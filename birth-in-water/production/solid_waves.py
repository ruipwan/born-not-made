"""Small-amplitude gravity-wave test with impermeable links at the project STL.

The fixed scene has no active pump, moving child, surface tension or viscosity.
The paired empty-domain control uses the same grid and initial displacement.
"""
import argparse
from pathlib import Path
import time

import numpy as np
from scipy import ndimage, sparse
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import factorized

TRIANGLE = np.dtype([('normal','<f4',3),('vertices','<f4',(3,3)),('attr','<u2')])

def registered_meshes(directory):
    parts = []
    for name,sign in [('head',1),('tail',-1)]:
        data = (directory/f'bnm_simple_{name}.stl').read_bytes()
        v = np.frombuffer(data, dtype=TRIANGLE,offset=84)['vertices'].astype(float)/1000
        xyz = v[:,:,[2,1,0]].copy()
        xyz[:,:,0] = sign*v[:,:,2] + (.004 if name=='tail' else 0)
        xyz[:,:,1] = -sign*v[:,:,1]
        parts.append(xyz)
    return np.concatenate(parts)

def shell_intersections(coords,triangles):
    """Flag each grid link traversed by at least one mesh triangle."""
    shape = tuple(map(len,coords))
    crossed = np.zeros((*shape,3),dtype=bool)
    for normal in range(3):
        u, v = (normal+1)%3, (normal+2)%3
        a, b, c = triangles[:,0],triangles[:,1],triangles[:,2]
        du,dv = b[:,u]-a[:,u], b[:,v]-a[:,v]
        eu,ev = c[:,u]-a[:,u], c[:,v]-a[:,v]
        area=du*ev-dv*eu
        lo,hi=triangles.min(axis=1),triangles.max(axis=1)
        for i,ui in enumerate(coords[u]):
            candidates=np.flatnonzero((lo[:,u]<=ui)&(hi[:,u]>=ui)&(np.abs(area)>1e-14))
            if not len(candidates):
                continue
            for j,vj in enumerate(coords[v]):
                ids=candidates[(lo[candidates,v]<=vj)&(hi[candidates,v]>=vj)]
                if not len(ids):
                    continue
                U,V=ui-a[ids,u],vj-a[ids,v]
                s=(U*ev[ids]-V*eu[ids])/area[ids]
                t=(du[ids]*V-dv[ids]*U)/area[ids]
                inside=(s>=-1e-9)&(t>=-1e-9)&(s+t<=1+1e-9)
                depth=a[ids,normal]+s*(b[ids,normal]-a[ids,normal])+t*(c[ids,normal]-a[ids,normal])
                links=np.searchsorted(coords[normal],depth[inside],side='right')-1
                links=links[(links>=0)&(links<shape[normal]-1)]
                index=[0,0,0,normal]
                index[normal],index[u],index[v]=links,i,j
                crossed[tuple(index)]=True
    return crossed

def conductance(coords, blocked):
    shape=tuple(map(len,coords))
    nodes=np.arange(np.prod(shape)).reshape(shape)
    spacing=np.array([c[1]-c[0] for c in coords])
    pairs, values=[],[]
    for axis,ds in enumerate(spacing):
        first=[slice(None)]*3;first[axis]=slice(None,-1)
        last=[slice(None)]*3;last[axis]=slice(1,None)
        start=nodes[tuple(first)]; end=nodes[tuple(last)]
        g=np.full(start.shape, np.prod(spacing)/ds**2)
        if axis!=2:  # Half cells on the bottom and free surface.
            g[:,:,(0,-1)] *= .5
        clear=~blocked[tuple(first)+(axis,)]
        pairs.append(np.column_stack((start[clear],end[clear])))
        values.append(g[clear])
    pairs=np.concatenate(pairs); values=np.concatenate(values)
    edges=sparse.coo_matrix((values,(pairs[:,0],pairs[:,1])),shape=(nodes.size,nodes.size)).tocsr()
    edges=edges+edges.T
    _,labels=connected_components(edges,directed=False)
    wet=labels==labels[nodes[0,0,-1]]
    surface=wet.copy() & (np.arange(nodes.size)%shape[2]==shape[2]-1)
    interior=np.flatnonzero(wet & ~surface); top=np.flatnonzero(surface)
    L=sparse.diags(np.asarray(edges.sum(axis=1)).ravel())-edges
    L=L.tocsr()
    ii=L[interior][:,interior].tocsc()
    si=L[top][:,interior].tocsr()
    ss=L[top][:,top].tocsr()
    solve=factorized(ii)
    def flux(phi):
        interior_phi=solve(-si.T@phi)
        return (ss@phi+si@interior_phi)/(spacing[0]*spacing[1])
    return flux, surface.reshape(shape)[:,:,-1], wet.reshape(shape)

def evolve(coords,crossed,seconds,kind):
    flux,surface,wet=conductance(coords,crossed)
    x,y,z=coords
    X,Y=np.meshgrid(x,y,indexing='ij')
    if kind=='mode':
        eta=np.cos(np.pi*(X+.67)/1.34)[surface]
    else:
        eta=np.exp(-((X-.445)**2+(Y+.035)**2)/(2*.047**2))[surface]
    eta-=eta.mean()
    eta*=.003/max(abs(eta))
    phi=np.zeros_like(eta)
    nearest=ndimage.distance_transform_edt(~surface,return_distances=False,return_indices=True)
    records=[]; energy=[]; volumes=[]
    dt=1/96
    for n in range(round(seconds/dt)+1):
        if n%4==0:
            full=np.zeros(surface.shape); full[surface]=eta
            records.append(full[tuple(nearest)].T.astype('float32'))
            q=flux(phi)
            energy.append(float(.5*(9.81*eta@eta+phi@q)*(x[1]-x[0])*(y[1]-y[0])))
            volumes.append(float(eta.sum()*(x[1]-x[0])*(y[1]-y[0])))
        if n==round(seconds/dt):
            break
        # Störmer-Verlet for the linear surface Hamiltonian.
        phi-=.5*dt*9.81*eta
        eta+=dt*flux(phi)
        phi-=.5*dt*9.81*eta
    return dict(x=x,y=y,z=z,frames=np.asarray(records),wet=wet,surface=surface,energy=energy,volume=volumes)

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('stls',type=Path); cli.add_argument('out',type=Path)
    cli.add_argument('--nx',type=int,default=80);cli.add_argument('--ny',type=int,default=46)
    cli.add_argument('--nz',type=int,default=20);cli.add_argument('--seconds',type=float,default=4.)
    cli.add_argument('--case',choices=['hull','empty','mode'],default='hull')
    args=cli.parse_args()
    x=(np.arange(args.nx)+.5)*1.34/args.nx-.67
    y=(np.arange(args.ny)+.5)*.76/args.ny-.38
    z=np.linspace(-.175,.10,args.nz)
    coords=(x,y,z)
    start=time.monotonic()
    blocked=shell_intersections(coords,registered_meshes(args.stls)) if args.case=='hull' else np.zeros((len(x),len(y),len(z),3),bool)
    print(args.case,'cut links',blocked.sum(),'grid',(len(x),len(y),len(z)),flush=True)
    result=evolve(coords,blocked,args.seconds,args.case)
    np.savez_compressed(args.out,**result)
    print('wet nodes',result['wet'].sum(),'wet surface',result['surface'].sum(),'elapsed',time.monotonic()-start,flush=True)

if __name__=='__main__':
    main()

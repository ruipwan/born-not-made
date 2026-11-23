import json, base64, numpy as np
D='../doublewall/'
J=json.load(open(D+'quilt.json')); A=json.load(open(D+'arm.json'))
AR=J['arm']
def b64f(s): return np.frombuffer(base64.b64decode(s),dtype=np.float32)
def b64u(s): return np.frombuffer(base64.b64decode(s),dtype=np.uint32)
PARTS={n:(b64f(p['p']).reshape(-1,3).astype(float), b64u(p['i'])) for n,p in A['parts'].items()}
def T(v): M=np.eye(4); M[:3,3]=v; return M
def Rx(a): c,s=np.cos(a),np.sin(a); M=np.eye(4); M[1,1]=c;M[1,2]=-s;M[2,1]=s;M[2,2]=c; return M
def Ry(a): c,s=np.cos(a),np.sin(a); M=np.eye(4); M[0,0]=c;M[0,2]=s;M[2,0]=-s;M[2,2]=c; return M
def Rz(a): c,s=np.cos(a),np.sin(a); M=np.eye(4); M[0,0]=c;M[0,1]=-s;M[1,0]=s;M[1,1]=c; return M
def about(p,a): p=np.array(p); return T(p)@Rx(a)@T(-p)
def rxv(v,t): c,s=np.cos(t),np.sin(t); return np.array([v[0],c*v[1]-s*v[2],s*v[1]+c*v[2]])
def part_mats(q):
    """local (arm.json frame) matrices of each part, given q=(q0,q1,q2); returns dict name->(M, uses_yaw)"""
    a=q[1]-AR['A_REST']; b=q[2]-AR['B_REST']; S=np.array(AR['S']); E=np.array(AR['E']); W=np.array(AR['W'])
    E2=S+rxv(E-S,a); W2=E2+rxv(W-E,b); dE=E2-E
    Lp=np.array(AR['O1'])-(E-S)
    m={'B_Fix':np.eye(4),'B_Rot':np.eye(4),'In_1':about(S,a),'Join':T(dE),'In_2':T(dE)@about(E,b),'EE':T(W2-W),'Out_1':about(Lp,a),'Out_2':T(dE)@about(AR['O2'],b)}
    return m,S,E2,W2
def world_parts(root,q):
    """root: 4x4 of the arm base frame (z up, x forward). Returns name->4x4 world, and joint points in world"""
    m,S,E2,W2=part_mats(q)
    base=root@Rz(np.pi/2); yb=base@Rz(q[0])
    out={n:(base if n=='B_Fix' else yb@M) for n,M in m.items()}
    j=[(yb@np.r_[p,1])[:3] for p in (S,E2,W2)]
    return out,j
def tool_head(root,q):
    rw=AR['SF']+AR['L1']*np.sin(q[1])+AR['L2']*np.cos(q[2]); zw=AR['SZ']+AR['L1']*np.cos(q[1])-AR['L2']*np.sin(q[2])
    r=rw+AR['STEM_F']; p=root@np.r_[r*np.cos(q[0]),r*np.sin(q[0]),zw+AR['HEAD_BOT'],1]
    return p[:3]
MODS={'M1':['B_Fix','B_Rot'],'M2':['In_1','Out_1'],'M3':['Join','In_2','Out_2'],'M4':['EE']}
def bounds(root,q,names=None):
    W,_=world_parts(root,q); pts=[]
    for n,M in W.items():
        if names and n not in names: continue
        v=PARTS[n][0]; pts.append((M@np.c_[v,np.ones(len(v))].T).T[:,:3])
    P=np.vstack(pts); return P.min(0),P.max(0)
def ik(tip,Ls,base,lim=True):
    """parent arm IK. tip: world tip of tool (length Ls). base: parent base point. returns q or None"""
    dx,dy=tip[0]-base[0],tip[1]-base[1]; q0=np.arctan2(dy,dx)
    r=np.hypot(dx,dy)-AR['STEM_F']; zw=tip[2]+Ls-base[2]-AR['HEAD_BOT']
    u=r-AR['SF']; v=zw-AR['SZ']; L1,L2=AR['L1'],AR['L2']; d=np.hypot(u,v)
    if d>L1+L2-1e-6 or d<abs(L1-L2)+1e-6: return None
    phi=np.arctan2(u,v); beta=np.arccos(np.clip((L1*L1+d*d-L2*L2)/(2*L1*d),-1,1))
    for q1 in (phi-beta,phi+beta):
        ex,ez=L1*np.sin(q1),L1*np.cos(q1); q2=np.arctan2(-(v-ez),u-ex)
        if not lim or (0<=q1<=np.radians(110) and 0<=q2<=np.radians(85) and abs(q0)<=np.radians(110)): return np.array([q0,q1,q2])
    return None

"""BNM_FRAMES=/tmp/rim-wave blender -b -P birth-in-water/production/rim_wave.py"""
import bpy,os,runpy,sys
import numpy as np
from pathlib import Path
base=Path(__file__).resolve().parent
sys.path.insert(0,str(base))
from wave_tank import WaveTank
state=runpy.run_path(str(base/'shell_plate.py'))
s,cam,aim=state['s'],state['cam'],state['aim']
cam.location=(.44,-.92,.34);aim(cam,(.235,-.025,.065))
cam.data.lens=72;cam.data.dof.focus_distance=.94;cam.data.dof.aperture_fstop=8
s.world.color=(.045,.055,.061)
for o in s.objects:
 if o.type=='LIGHT' and o.location.x>.6:
  o.location=(.50,.70,.56);aim(o,(.21,0,.08));o.data.energy=18;o.data.size=.55;o.data.size_y=.033
# Keep the broad fill softbox out of the front glass's mirror image. The
# narrow cross-light remains visible to glossy rays as a slope reference.
for lamp in s.objects:
 if lamp.type=='LIGHT' and lamp.location.x<0:lamp.visible_glossy=False
s.cycles.samples=int(os.getenv('BNM_SAMPLES','64'))
s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False
s.cycles.sample_clamp_indirect=1.4;s.cycles.sample_clamp_direct=3.2
s.render.use_persistent_data=True
s.render.resolution_x,s.render.resolution_y=960,540;s.render.resolution_percentage=int(os.getenv('BNM_SCALE','100'))
s.render.fps=24;s.frame_start=1;s.frame_end=int(os.getenv('BNM_COUNT','120'))
out=Path(os.getenv('BNM_FRAMES','/tmp/bnm-dispersive'));out.mkdir(exist_ok=True,parents=True)
s.render.filepath=str(out/'rim-');s.render.image_settings.file_format='PNG'
tank=WaveTank();gx,gy=np.meshgrid(tank.x,tank.y);ny,nx=gx.shape
coords=np.column_stack((gx.ravel(),gy.ravel(),np.full(nx*ny,.10))).astype('float32')
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
rim=[*range(nx),*[j*nx+nx-1 for j in range(1,ny)],*range(ny*nx-2,(ny-1)*nx-1,-1),*[j*nx for j in range(ny-2,0,-1)]]
bottom=coords[rim].copy();bottom[:,2]=-.175
coords=np.concatenate((coords,bottom));base_idx=nx*ny
for i,a in enumerate(rim):
 j=(i+1)%len(rim);faces.append((rim[j],a,base_idx+i,base_idx+j))
faces.append(tuple(reversed(range(base_idx,len(coords)))))
mesh=bpy.data.meshes.new('Bounded water');mesh.from_pydata(coords.tolist(),[],faces)
water=bpy.data.objects.new('Water',mesh);s.collection.objects.link(water)
def glass(name,ior,tint):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 surface=n.new('ShaderNodeBsdfGlass');surface.inputs['IOR'].default_value=ior;surface.inputs['Roughness'].default_value=.008;surface.inputs['Color'].default_value=(*tint,1)
 mix=n.new('ShaderNodeMixShader');l.new(n.new('ShaderNodeLightPath').outputs['Is Shadow Ray'],mix.inputs[0]);l.new(surface.outputs[0],mix.inputs[1]);l.new(n.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface']);return m
mesh.materials.append(glass('Water interface',1.333,(.97,.995,.997)))
for poly in list(mesh.polygons)[:(ny-1)*(nx-1)]:poly.use_smooth=True
wallmat=glass('Tank glass',1.49,(.99,1,1))
for loc,dim in [((0,.383,.03),(1.35,.005,.41)),((0,-.383,.03),(1.35,.005,.41)),((.673,0,.03),(.005,.771,.41)),((-.673,0,.03),(.005,.771,.41))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;o.data.materials.append(wallmat)
def move(scene):
 t=(scene.frame_current-1)/24
 coords[:base_idx,2]=.1 if os.getenv('BNM_CALM')=='1' else .1+tank.displacement(t).ravel()
 mesh.vertices.foreach_set('co',coords.ravel());mesh.update()
bpy.app.handlers.frame_change_pre.append(move)
if 'BNM_TEST_FRAME' in os.environ:
 s.frame_set(int(os.environ['BNM_TEST_FRAME']));s.render.filepath=str(out/f'proof-{s.frame_current:04d}.png');bpy.ops.render.render(write_still=True)
else:
 s.render.use_overwrite=False;bpy.ops.render.render(animation=True)

"""Render an optical rehearsal of a freely decaying surface wave around the project CAD.
BNM_FRAMES=/path blender -b -t 7 -P birth-in-water/production/waterline.py
"""
import bpy,runpy,os,math
from pathlib import Path
from mathutils import Vector
base=runpy.run_path(str(Path(__file__).with_name('shell_plate.py')))
s=base['s'];cam=base['cam'];aim=base['aim']
cam.location=(.88,-.96,.49);aim(cam,(.045,0,.024))
cam.data.lens=54;cam.data.dof.focus_distance=1.22;cam.data.dof.aperture_fstop=9
s.render.resolution_x,s.render.resolution_y=960,540
s.cycles.samples=48
s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False
s.cycles.sample_clamp_indirect=1.4; s.cycles.sample_clamp_direct=3.2
s.render.use_persistent_data=True
s.render.fps=24;s.frame_start=1;s.frame_end=240
out=Path(os.environ.get('BNM_FRAMES','/tmp/bnm-waterline'));out.mkdir(exist_ok=True,parents=True)
s.render.filepath=str(out/'waterline-');s.render.image_settings.file_format='PNG'
# Long, low ripples travel outwards from just ahead of the rim. Their slopes
# refract the shell and bend the strip-light highlights. This is a prescribed
# free surface, with neither a submerged propulsion solver nor modeled feedback.
nx,ny=201,141
xy=[(-1.35+2.7*i/(nx-1),-1.4+2.8*j/(ny-1)) for j in range(ny) for i in range(nx)]
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
mesh=bpy.data.meshes.new('Tank interface');mesh.from_pydata([(x,y,.10) for x,y in xy],[],faces);mesh.update()
o=bpy.data.objects.new('Water surface',mesh);s.collection.objects.link(o)
m=bpy.data.materials.new('Water and air interface');m.use_nodes=True
nodes=m.node_tree.nodes;glass=nodes.new('ShaderNodeBsdfGlass');glass.inputs['IOR'].default_value=1.333;glass.inputs['Roughness'].default_value=.009
links=m.node_tree.links; mix=nodes.new('ShaderNodeMixShader'); lightpath=nodes.new('ShaderNodeLightPath')
links.new(lightpath.outputs['Is Shadow Ray'],mix.inputs[0]);links.new(glass.outputs[0],mix.inputs[1]);links.new(nodes.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface']);mesh.materials.append(m)
for poly in mesh.polygons:poly.use_smooth=True
from array import array
samples=[(x,y,math.hypot(x-.32,y+.04)) for x,y in xy]
def surface_frame(scene):
 t=(scene.frame_current-1)/24
 coords=array('f')
 for x,y,r in samples:
  phase=r-.22*t
  envelope=math.exp(-((phase+.06)/.21)**2-.30*t)
  z=.10+.0042*envelope*math.cos(44*phase)+.0007*math.sin(12*x+8*y-1.3*t)
  coords.extend((x,y,z))
 mesh.vertices.foreach_set('co',coords);mesh.update()
bpy.app.handlers.frame_change_pre.append(surface_frame)
if 'BNM_TEST_FRAME' in os.environ:
 s.frame_set(int(os.environ['BNM_TEST_FRAME']));s.render.filepath=str(out/'proof.png');bpy.ops.render.render(write_still=True)
else:
 s.render.use_overwrite=False
 bpy.ops.render.render(animation=True)

"""From repository root: blender -b -P birth-in-water/production/shell_plate.py"""
import bpy, math
from pathlib import Path
from mathutils import Vector, Matrix
root = Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=48
s.cycles.use_denoising=False
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=1600,900,100
s.world=bpy.data.worlds.new('Room fill'); s.world.color=(.12,.16,.17)
def surface(name,color,rough,trans=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 for key,value in [('Base Color',(*color,1)),('Roughness',rough),('Transmission Weight',trans),('IOR',1.16)]:p.inputs[key].default_value=value
 return m
resin=surface('Milky shell under water',(.50,.68,.65),.24,.55)
for name,sign in [('head',1),('tail',-1)]:
 bpy.ops.wm.stl_import(filepath=str(root/f'simulator/simple/print/bnm_simple_{name}.stl'))
 obj=bpy.context.object
 # Print Z is the length axis. Both parts were laid on their docking face.
 mat=Matrix(((0,0,sign,0),(0,-sign,0,0),(1,0,0,0),(0,0,0,1)))
 obj.matrix_world=mat @ Matrix.Diagonal(Vector((.001,.001,.001,1)))
 obj.data.materials.append(resin)
 for poly in obj.data.polygons:poly.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.175))
bpy.context.object.data.materials.append(surface('Slate',(.042,.060,.064),.64))
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def strip(pos,power,color,size,other):
 l=bpy.data.lights.new('Softbox','AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=other;l.color=color
 o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.location=pos;aim(o,(0,0,0))
strip((.2,.65,.85),36,(.74,.95,1),.85,.12)
strip((.7,-.45,.32),9,(1,.83,.66),.48,.06)
strip((-.75,-.24,.6),16,(.63,.78,1),.52,.45)
bpy.ops.object.camera_add(location=(.75,-1.07,.29))
cam=bpy.context.object;aim(cam,(.035,0,-.015));cam.data.lens=58;cam.data.dof.use_dof=True;cam.data.dof.focus_distance=1.24;cam.data.dof.aperture_fstop=5.6;s.camera=cam
s.render.filepath=str(root/'birth-in-water/media/shell-plate.jpg');s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
if __name__ == "__main__":
 bpy.ops.render.render(write_still=True)

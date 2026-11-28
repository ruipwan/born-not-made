"""Sightline and light previsualisations. Paths for two extracted artist frames
are supplied in BNM_FILM_FRAME and BNM_DIGITAL_FRAME (see gallery-cut.md).
No photometry is calibrated. BNM_VIEW = entry, seated, crossing, or standing.
"""
import bpy,math,os,runpy
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2]
base=runpy.run_path(str(Path(__file__).with_name('shell_plate.py')))
s,cam,aim=base['s'],base['cam'],base['aim']
# Retain only the two print meshes and the camera from the scale study.
for obj in list(s.objects):
 if obj.type=='MESH' and obj.name.startswith('bnm_simple_'):
  # The +390 mm mouth faces the side bay; centre it at the release mark.
  obj.matrix_world=Matrix.Translation((3.89,3.96,1.02)) @ Matrix.Rotation(math.pi,4,'Z') @ obj.matrix_world
 elif obj!=cam:bpy.data.objects.remove(obj,do_unlink=True)
def mat(n,c,r=.48,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=r;bs.inputs['Metallic'].default_value=metal;return m
def cube(n,loc,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  b=o.modifiers.new('Eased edge','BEVEL');b.width=bevel;b.segments=2
 return o
def dielectric(n,ior,c):
 m=mat(n,c,.018);g=m.node_tree.nodes.get('Principled BSDF');g.inputs['Transmission Weight'].default_value=1;g.inputs['IOR'].default_value=ior
 # Transparent shadow paths approximate direct illumination through clear panes.
 nodes=m.node_tree.nodes;links=m.node_tree.links;mix=nodes.new('ShaderNodeMixShader')
 links.new(nodes.new('ShaderNodeLightPath').outputs['Is Shadow Ray'],mix.inputs[0]);links.new(g.outputs[0],mix.inputs[1]);links.new(nodes.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface']);return m
def light(n,loc,direction,power,col,width,height):
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=width;l.size_y=height;l.color=col;o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=loc;aim(o,direction)
wall=mat('Charcoal matte',(.056,.061,.059),.86);floor=mat('Honed concrete',(.16,.16,.15),.52)
wood=mat('Ebonised plywood',(.086,.064,.05),.44);metal=mat('Satin aluminium',(.24,.25,.24),.36,.75)
cube('North wall',(4,6.06,1.5),(8.2,.12,3),wall);cube('West wall',(-.06,3,1.5),(.12,6.1,3),wall)
cube('East wall',(8.06,3,1.5),(.12,6.1,3),wall);cube('Floor',(4,3,-.05),(8.2,6.2,.1),floor)
cube('Tank cabinet',(4,4.025,.34),(1.80,.65,.68),wood,.008)
cube('Cabinet top',(4,4.025,.673),(1.82,.67,.014),metal,.002)
glass=dielectric('Float glass',1.49,(.95,.99,.965))
for pos,dims in [((4,3.705,.96),(1.80,.009,.56)),((4,4.345,.96),(1.80,.009,.56)),((3.105,4.025,.96),(.009,.632,.56)),((4.895,4.025,.96),(.009,.632,.56))]:
 cube('Tank pane',pos,dims,glass,.001)
cube('Water to 1.13 m',(4,4.025,.909),(1.777,.627,.442),dielectric('Water',1.333,(.97,.995,.987)))
# The original stills kept just 0.25 m behind the tank. The revised service
# layout moves a shallower bench to the back wall, leaving a 1.02 m band.
service_layout=os.getenv('BNM_SERVICE_BENCH')=='1'
bench_y,depth=(5.67,.60) if service_layout else (5,.80)
cube('Reset worktop',(4,bench_y,.89),(2.6,depth,.07),wood,.006)
for x in [2.8,5.2]:
 for y in [bench_y-depth/2+.10,bench_y+depth/2-.10]:cube('Bench leg',(x,y,.435),(.04,.04,.87),metal)
def screen(n,centre,width,height,image_file):
 x,y,z=centre;cube(n+' surround',(x,y+.018,z),(width+.048,.035,height+.048),wall,.005)
 bpy.ops.mesh.primitive_plane_add(size=1,location=centre,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=n;o.scale=(width,height,1)
 m=bpy.data.materials.new(n);m.use_nodes=True;nodes=m.node_tree.nodes;l=m.node_tree.links
 img=nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(image_file)
 e=nodes.new('ShaderNodeEmission');e.inputs[1].default_value=1.65;l.new(img.outputs[0],e.inputs[0]);l.new(e.outputs[0],nodes.get('Material Output').inputs['Surface']);o.data.materials.append(m)
screen('Recorded film',(1.4,5.80,1.485),1.90,1.07,os.environ['BNM_FILM_FRAME'])
screen('Digital population',(6.975,5.80,1.46),1.45,.82,os.environ['BNM_DIGITAL_FRAME'])
side_screen=os.getenv('BNM_SIDE_SCREEN')=='1'
if side_screen:
 # Move the bright image out of the right tank pane as seen from the bay.
 screen_obj=bpy.data.objects['Digital population'];screen_obj.location=(7.88,4.85,1.46)
 screen_obj.rotation_euler.z=-math.pi/2
 back=bpy.data.objects['Digital population surround'];back.location=(7.90,4.85,1.46);back.rotation_euler.z=-math.pi/2
light('Tank grazing strip',(3.9,4.46,1.90),(3.7,3.9,.95),37,(.80,.91,1),1.0,.08)
light('Route spill',(2.0,.8,2.8),(3,2.8,0),75,(.99,.85,.68),2.4,1.1)
light('Worktop pool',(4.2,5.2,2.75),(4,5,.82),20,(1,.87,.7),1.1,.2)
light('Group fill',(7.2,2.8,2.6),(5.8,2.4,.9),30,(.8,.9,1),1.4,.5)
fabric=mat('Occlusion proxy',(.07,.077,.075),.93)
def ellipsoid(n,loc,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;o.data.materials.append(fabric)
 for p in o.data.polygons:p.use_smooth=True
def visitor(x,y):
 ellipsoid('Head proxy',(x,y,1.60),(.115,.12,.145))
 ellipsoid('Torso proxy',(x,y,1.11),(.21,.14,.40))
 for xx in [x-.09,x+.09]:ellipsoid('Leg proxy',(xx,y,.45),(.095,.115,.45))
view=os.getenv('BNM_VIEW','entry')
light_test=os.getenv('BNM_LIGHT_TEST')=='1'
if light_test:
 # Light entering through the surface can be sampled badly in forward path
 # tracing. A diffuse interior reference and cross-light are a design trial.
 cube('Trial liner',(4,4.025,.693),(1.765,.616,.008),mat('Pale neutral liner',(.42,.48,.44),.78))
 light('Hooded lateral fill',(3.0,4.26,1.58),(3.65,4.0,1.0),45,(.89,.96,1),.65,.12)

for x,y in [(4.45,2.9),(5.15,2.6),(5.9,2.9),(6.45,2.45)]:visitor(x,y)
if view=='crossing':visitor(3,3.15)
positions={'entry':((1.26,.29,1.53),(3.94,4.10,1.05),22),'seated':((2.55,2.45,1.12),(3.50,3.96,1.02),24),'crossing':((2.55,2.45,1.12),(3.50,3.96,1.02),24),'standing':((2.55,2.45,1.62),(3.50,3.96,1.02),24)}
cam.location,target,cam.data.lens=positions[view];aim(cam,target);cam.data.dof.use_dof=False
s.world.color=(.045,.044,.043);s.cycles.samples=32;s.cycles.sample_clamp_indirect=1.5;s.cycles.caustics_refractive=False
s.render.resolution_x,s.render.resolution_y=1120,630;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90
out=Path(os.getenv('BNM_VIEW_OUT','/tmp/bnm-gallery-views'));out.mkdir(exist_ok=True,parents=True)
s.render.filepath=str(out/(view+('-fill' if light_test else '')+('-side' if side_screen else '')+'.jpg'))
if __name__ == '__main__':
 bpy.ops.render.render(write_still=True)

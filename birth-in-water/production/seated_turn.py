"""Render a seated line-of-sight rehearsal in the proposed gallery.

Supply BNM_FILM_FRAME=.../film-001.jpg (return study, 37 s onwards, 12 fps)
and BNM_DIGITAL_FRAME (Water Beings still). Output uses BNM_VIEW_OUT.
For the 16-second gallery edition set BNM_VISIT_EDITION=gallery, BNM_FILM_FRAME
to the first of 192 frames sampled from gallery-projection-1080.mp4 at 45 s,
BNM_DIGITAL_FRAME to the corresponding Water Beings sequence starting at 7 s,
and BNM_STATUS_CARD and BNM_LABEL_TEXTURE to the rasterised exhibition sheets.
BNM_START and BNM_COUNT are inclusive first and last frame numbers.
Run from Blender in background mode.
"""
import math
import os
from pathlib import Path
import runpy
import bpy
from mathutils import Vector

os.environ.update(BNM_VIEW='seated', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1')
gallery = os.getenv('BNM_VISIT_EDITION') == 'gallery'
if gallery:
    os.environ['BNM_SERVICE_BENCH'] = '1'
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene, camera = room['s'], room['cam']
eye = camera.location.copy()
mouth = Vector((3.50, 3.96, 1.02))
film_x = float(os.getenv('BNM_FILM_WALL_X', '1.4'))
for name in ('Recorded film', 'Recorded film surround'):
    scene.objects[name].location.x += film_x - 1.4
screen = Vector((film_x, 5.80, 1.485))
# Fixed 3-degree heading east of north for the matched wall-position trial.
fixed_direction = Vector((math.sin(math.radians(3)), math.cos(math.radians(3)), .025))
fixed_rotation = fixed_direction.to_track_quat('-Z', 'Y')
fixed_seat = os.getenv('BNM_FIXED_SEAT') == '1'
initial = (mouth-eye).to_track_quat('-Z', 'Y')
terminal = (screen-eye).to_track_quat('-Z', 'Y')

# A fifth proxy moves toward the tank then stops in the viewing diagonal.
original = set(scene.objects)
room['visitor'](4.23, 3.15)
walker = [(o, o.location.copy()) for o in set(scene.objects)-original]
total = 192 if gallery else 120
for material in (['Recorded film', 'Digital population'] if gallery else ['Recorded film']):
    texture = next(n for n in bpy.data.materials[material].node_tree.nodes if n.type=='TEX_IMAGE')
    texture.image.source = 'SEQUENCE'
    texture.image_user.frame_start = 1
    texture.image_user.frame_duration = total
    texture.image_user.use_auto_refresh = True
if gallery:
    # The tank is paused. The sourced films on both walls continue at their
    # own times; the dark figure at the revised bench is a staff-position proxy.
    room['visitor'](4.0,4.85)
    status_height=float(os.getenv('BNM_STATUS_HEIGHT','1.09'))
    post_height=status_height-.11
    room['cube']('Pause card stand',(2.89,3.84,post_height/2),(.022,.022,post_height),room['metal'])
    room['cube']('Stand base',(2.89,3.84,.008),(.18,.16,.016),room['metal'])
    for label,location,rotation,dimensions,path in [
        ('Tank paused',(2.89,3.82,status_height),(math.pi/2,0,0),(.297,.210),os.environ['BNM_STATUS_CARD']),
        ('Film wall label',(7.992,1.95,1.35),(math.pi/2,0,-math.pi/2),(.297,.420),os.environ['BNM_LABEL_TEXTURE'])]:
        bpy.ops.mesh.primitive_plane_add(size=1,location=location,rotation=rotation)
        card=bpy.context.object;card.name=label;card.scale=(*dimensions,1)
        paper=room['mat'](label,(1,1,1),.93)
        tex=paper.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image=bpy.data.images.load(path)
        paper.node_tree.links.new(tex.outputs['Color'],paper.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
        card.data.materials.append(paper)
camera.rotation_mode = 'QUATERNION'

def ease(t):
    t = min(1, max(0, t))
    return t*t*(3-2*t)

def move(frame_scene):
    seconds = (frame_scene.frame_current-1)/12
    for obj, origin in walker:
        obj.location.x = origin.x - 1.23*ease((seconds-.25)/(1.75 if gallery else 2.25))
    fraction = .5 if os.getenv('BNM_MIDPOINT') == '1' else (ease((seconds-1.6)/1.95) if gallery else ease((seconds-2.8)/2.4))
    camera.rotation_quaternion = fixed_rotation if fixed_seat else initial.slerp(terminal, fraction)

bpy.app.handlers.frame_change_pre.append(move)
scene.frame_start = int(os.getenv('BNM_START','1'))
scene.frame_end = int(os.getenv('BNM_COUNT',str(total)))
scene.render.fps = 12
scene.render.resolution_x, scene.render.resolution_y = 768,432
scene.cycles.samples = 20 if gallery else 18
if gallery:
    scene.cycles.seed=37
    scene.cycles.use_animated_seed=False
scene.cycles.use_denoising = False
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(os.environ['BNM_VIEW_OUT'])/'bay-')
scene.render.use_overwrite=False
if 'BNM_TEST_FRAME' in os.environ:
    frame = int(os.environ['BNM_TEST_FRAME'])
    scene.frame_set(frame)
    scene.render.filepath = str(Path(os.environ['BNM_VIEW_OUT'])/f'proof-{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)

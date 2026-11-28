"""Render a seated line-of-sight rehearsal in the proposed gallery.

Supply BNM_FILM_FRAME=.../film-001.jpg (return study, 37 s onwards, 12 fps)
and BNM_DIGITAL_FRAME (Water Beings still). Output uses BNM_VIEW_OUT.
Run from Blender in background mode.
"""
import math
import os
from pathlib import Path
import runpy
import bpy
from mathutils import Vector

os.environ.update(BNM_VIEW='seated', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1')
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene, camera = room['s'], room['cam']
eye = camera.location.copy()
mouth = Vector((3.50, 3.96, 1.02))
screen = Vector((1.4, 5.80, 1.485))
initial = (mouth-eye).to_track_quat('-Z', 'Y')
terminal = (screen-eye).to_track_quat('-Z', 'Y')

# A fifth proxy moves toward the tank then stops in the viewing diagonal.
original = set(scene.objects)
room['visitor'](4.23, 3.15)
walker = [(o, o.location.copy()) for o in set(scene.objects)-original]
film_material = bpy.data.materials['Recorded film']
texture = next(node for node in film_material.node_tree.nodes if node.type=='TEX_IMAGE')
texture.image.source = 'SEQUENCE'
texture.image_user.frame_duration = 120
texture.image_user.use_auto_refresh = True
camera.rotation_mode = 'QUATERNION'

def ease(t):
    t = min(1, max(0, t))
    return t*t*(3-2*t)

def move(frame_scene):
    seconds = (frame_scene.frame_current-1)/12
    for obj, origin in walker:
        obj.location.x = origin.x - 1.23*ease((seconds-.25)/2.25)
    fraction = .5 if os.getenv('BNM_MIDPOINT') == '1' else ease((seconds-2.8)/2.4)
    camera.rotation_quaternion = initial.slerp(terminal, fraction)

bpy.app.handlers.frame_change_pre.append(move)
scene.frame_start, scene.frame_end = 1,120
scene.render.fps = 12
scene.render.resolution_x, scene.render.resolution_y = 768,432
scene.cycles.samples = 18
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

"""Compare four seconds of real Water Beings imagery in two modelled wall positions.

Pass BNM_DIGITAL_FRAME as the first eco-001.jpg of 64 source samples at 16 fps
and BNM_FILM_FRAME as the held documentary picture on the north wall.
BNM_SPILL_LAYOUT is north or east. BNM_BLACK_SCREEN=1 renders a matched unlit
screen control; BNM_TEST_FRAME selects a single still.
"""
import json
import os
from pathlib import Path
import runpy

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

side=os.environ['BNM_SPILL_LAYOUT']
if side not in ('north','east'):
    raise ValueError(side)
os.environ.update(BNM_VIEW='seated', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN=str(int(side=='east')), BNM_SERVICE_BENCH='1')
room=runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene,camera=room['s'],room['cam']
screen=bpy.data.materials['Digital population']
texture=next(n for n in screen.node_tree.nodes if n.type=='TEX_IMAGE')
texture.image.source='FILE' if os.getenv('BNM_HOLD_STILL')=='1' else 'SEQUENCE'
texture.image_user.frame_start=1
texture.image_user.frame_duration=64
texture.image_user.use_auto_refresh=True
route=os.getenv('BNM_SPILL_PATH','all')
surface=bpy.data.objects['Digital population']
if route in ('camera','glossy','transmission'):
    setattr(surface,'visible_'+route,False)
elif route!='all':
    raise ValueError(route)
black=os.getenv('BNM_BLACK_SCREEN')=='1'
if black:
    emit=next(n for n in screen.node_tree.nodes if n.type=='EMISSION')
    emit.inputs['Strength'].default_value=0
scene.render.fps=16
scene.frame_start,scene.frame_end=1,64
scene.render.resolution_x,scene.render.resolution_y=768,432
scene.cycles.samples=32
scene.cycles.seed=37
scene.cycles.use_animated_seed=False
scene.render.use_persistent_data=True
scene.render.use_overwrite=False
scene.render.image_settings.file_format='PNG'
out=Path(os.environ['BNM_VIEW_OUT'])
scene.render.filepath=str(out/'spill-')
# Corners of the physical front pane, in displayed pixel coordinates.
# This polygon isolates the projected silhouette of the pane from the wall.
bpy.context.view_layer.update()
def pixel(point):
    v=world_to_camera_view(scene,camera,Vector(point))
    return (round(v.x*768,3),round((1-v.y)*432,3))
points=[pixel((x,3.7005,z)) for x,z in ((3.1,.68),(4.9,.68),(4.9,1.24),(3.1,1.24))]
(out/'front-pane.json').write_text(json.dumps(points)+'\n')
if 'BNM_TEST_FRAME' in os.environ:
    fr=int(os.environ['BNM_TEST_FRAME']);scene.frame_set(fr)
    scene.render.filepath=str(out/f'{side}-{"black" if black else "lit"}-{fr}.png')
    if route!='all' or os.getenv('BNM_HOLD_STILL')=='1':
        scene.render.filepath=str(out/f'{side}-{route}-hold{os.getenv("BNM_HOLD_STILL","0")}-{fr}.png')
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)

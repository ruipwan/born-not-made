"""Comparison of the first reset bench and the revised plan. See room.py.
Run with BNM_SERVICE_BENCH=0 and =1, using gallery_views.py frame paths.
"""
import os
from pathlib import Path
import runpy
import bpy
os.environ.update(BNM_VIEW='seated',BNM_LIGHT_TEST='1',BNM_SIDE_SCREEN='1')
room=runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene,camera=room['s'],room['cam']
before=set(scene.objects)
room['visitor'](4.00,4.85)
apron=room['mat']('Operator proxy',(.32,.20,.11),.88)
for obj in set(scene.objects)-before:
    obj.data.materials.clear()
    obj.data.materials.append(apron)
camera.location=(5.68,3.96,2.68)
room['aim'](camera,(3.95,4.81,.81))
camera.data.lens=23
scene.cycles.samples=24
scene.render.resolution_x,scene.render.resolution_y=1024,576
scene.render.image_settings.file_format='PNG'
state='revised' if room['service_layout'] else 'first'
scene.render.filepath=str(Path(os.environ['BNM_VIEW_OUT'])/f'{state}.png')
bpy.ops.render.render(write_still=True)

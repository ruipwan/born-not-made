"""View the actual open-caption picture in the proposed room.

BNM_FILM_FRAME must be the 49.5 s frame from the open-caption exhibition MP4.
BNM_DIGITAL_FRAME and BNM_VIEW_OUT follow gallery_views.py. Set BNM_WALL_TRIAL
to seated, doorway, or side for the three reader and camera positions.
"""
import os
import runpy
from pathlib import Path

import bpy

os.environ.update(BNM_VIEW='seated', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1',
                  BNM_SERVICE_BENCH='1')
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
trial = os.environ['BNM_WALL_TRIAL']
eye, reader_x = {
    'seated': ((2.55, 2.45, 1.12), 1.95),
    'doorway': ((.45, .64, 1.50), 1.95),
    'side': ((2.55, 2.45, 1.12), 2.72),
}[trial]
room['visitor'](reader_x, 4.18)
room['cam'].location = eye
room['cam'].data.lens = 35
room['aim'](room['cam'], (1.40, 5.80, 1.485))
scene = room['s']
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.cycles.samples = 32
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(os.environ['BNM_VIEW_OUT'])/(trial+'.png'))
bpy.ops.render.render(write_still=True)

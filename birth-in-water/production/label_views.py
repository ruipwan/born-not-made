"""Observe the same printed A3 beside two dry visitor routes.

BNM_LABEL_SIDE=west or east, BNM_LABEL_EYE=door, bay, or reader,
BNM_LABEL_LIGHT=0 or 1. The texture is a raster of film-wall-label.pdf.
Gallery frame paths and BNM_VIEW_OUT follow gallery_views.py.
"""
import math
import os
from pathlib import Path
import runpy

import bpy

os.environ.update(BNM_VIEW='seated', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1', BNM_SERVICE_BENCH='1')
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
side, eye = os.environ['BNM_LABEL_SIDE'], os.environ['BNM_LABEL_EYE']
lit = os.environ['BNM_LABEL_LIGHT'] == '1'
cx, cy, facing = {'west': (.008, 4.70, 1), 'east': (7.992, 1.95, -1)}[side]
reader_x = cx+.792*facing
reader_y = cy
bpy.ops.mesh.primitive_plane_add(size=1, location=(cx,cy,1.35), rotation=(math.pi/2,0,facing*math.pi/2))
label = bpy.context.object
label.name = 'A3 film label on matte stock'
label.scale = (.297,.420,1)
paper = room['mat']('Uncoated label stock', (1,1,1), .93)
picture = paper.node_tree.nodes.new('ShaderNodeTexImage')
picture.image = bpy.data.images.load(os.environ['BNM_LABEL_TEXTURE'])
paper.node_tree.links.new(picture.outputs['Color'],paper.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
label.data.materials.append(paper)
if lit:
    spot = bpy.data.lights.new('Shielded reading spot', 'SPOT')
    spot.energy, spot.spot_size, spot.spot_blend = 5, math.radians(34), .35
    spot.shadow_soft_size = .035
    lamp = bpy.data.objects.new('Reading spot', spot)
    room['s'].collection.objects.link(lamp)
    lamp.location = (cx+.57*facing,cy,2.12)
    room['aim'](lamp,(cx,cy,1.35))
cam = room['cam']
if eye == 'reader':
    cam.location = (reader_x,reader_y,1.12)
    room['aim'](cam,(cx,cy,1.35))
    cam.data.lens=42
else:
    room['visitor'](reader_x,reader_y)
    cam.location = {'door': (.45,.64,1.50), 'bay': (2.55,2.45,1.12)}[eye]
    room['aim'](cam,(1.4,5.80,1.485))
    cam.data.lens = 35
scene=room['s']
scene.render.resolution_x, scene.render.resolution_y = 1440,900
scene.cycles.samples=32
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(Path(os.environ['BNM_VIEW_OUT'])/f'{side}-{eye}-{int(lit)}.png')
bpy.ops.render.render(write_still=True)

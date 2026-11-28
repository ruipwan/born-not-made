"""Compare an A4 printed pause notice at two positions in the proposed room.

BNM_STATUS_CARD is a raster of the first page of studies/tank-status.pdf.
Set BNM_STATUS_POSITION to cabinet or stand. Gallery frame paths and BNM_VIEW
have the same meaning as in gallery_views.py. BNM_VIEW_OUT holds the result.
"""
import math
import os
from pathlib import Path
import runpy
import bpy

os.environ.update(BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1')
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene = room['s']
position = os.environ['BNM_STATUS_POSITION']
if position == 'cabinet':
    centre = (3.36, 3.695, .52)
elif position == 'stand':
    centre = (2.89, 3.82, 1.09)
    room['cube']('Dry card stand', (2.89, 3.84, .49), (.022, .022, .98), room['metal'])
    room['cube']('Stand base', (2.89, 3.84, .008), (.18, .16, .016), room['metal'])
else:
    raise ValueError(position)
bpy.ops.mesh.primitive_plane_add(size=1, location=centre, rotation=(math.pi/2, 0, 0))
card = bpy.context.object
card.name = 'A4 printed card'
card.scale = (.297, .210, 1)
paper = room['mat']('Matte printed card', (1, 1, 1), .85)
texture = paper.node_tree.nodes.new('ShaderNodeTexImage')
texture.image = bpy.data.images.load(os.environ['BNM_STATUS_CARD'])
bsdf = paper.node_tree.nodes.get('Principled BSDF')
paper.node_tree.links.new(texture.outputs['Color'], bsdf.inputs['Base Color'])
card.data.materials.append(paper)
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.cycles.samples = 24
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(os.environ['BNM_VIEW_OUT'])/(position+'-'+room['view']+'.png'))
bpy.ops.render.render(write_still=True)

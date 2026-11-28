"""Render a temporary alignment target at the CAD mouth before installing the body.

The front pane remains in all views. BNM_VIEW_OUT receives one PNG per trial.
Supply gallery_views.py's two image sources as before.
"""
import os
import runpy
from pathlib import Path

import bpy

os.environ.update(BNM_VIEW='seated', BNM_SERVICE_BENCH='1', BNM_LIGHT_TEST='1', BNM_SIDE_SCREEN='1')
room = runpy.run_path(str(Path(__file__).with_name('gallery_views.py')))
scene, cam = room['s'], room['cam']
for obj in scene.objects:
    if obj.name.startswith('bnm_simple_'):
        obj.hide_render = True
# A matte square and a luminous reference point stand at the planned mouth.
target=(3.50,3.96,1.02)
board=room['mat']('Calibration square',(.76,.78,.77),.86)
room['cube']('Alignment target backing',(3.50,3.964,1.02),(.085,.005,.085),board)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=.008, location=target)
dot=bpy.context.object
material=bpy.data.materials.new('Red calibration point')
material.use_nodes=True
emit=material.node_tree.nodes.new('ShaderNodeEmission')
emit.inputs[0].default_value=(1.0,.003,.003,1)
emit.inputs[1].default_value=1.0
material.node_tree.links.new(emit.outputs[0],material.node_tree.nodes.get('Material Output').inputs['Surface'])
dot.data.materials.append(material)
water=scene.objects['Water to 1.13 m']
cam.data.lens=50
scene.render.resolution_x,scene.render.resolution_y=1280,720
scene.render.image_settings.file_format='PNG'
scene.cycles.samples=24
cover=room['cube']('Matte temporary surface flag',(4,4.025,1.134),
                  (1.772,.620,.003),room['mat']('Matte dark flag',(.003,.003,.003),.95))
for eye,z in [('seated',1.12),('standing',1.62)]:
    cam.location=(2.55,2.45,z)
    room['aim'](cam,target)
    for level in (('dry','filled','covered') if eye=='standing' else ('dry','filled')):
        if os.getenv('BNM_CONTROL_ONLY') and os.getenv('BNM_CONTROL_ONLY')!=f'{eye}-{level}':
            continue
        cover.hide_render=(level!='covered')
        water.hide_render=(level=='dry')
        scene.render.filepath=str(Path(os.environ['BNM_VIEW_OUT'])/f'{eye}-{level}.png')
        bpy.ops.render.render(write_still=True)

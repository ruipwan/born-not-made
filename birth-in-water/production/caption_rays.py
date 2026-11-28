"""Measure the coverage of bright caption pixels by a standing-room proxy.

Run with the 49.5 s frame of the open-caption exhibition film as the argument.
Coordinates describe the north-wall mock-up in gallery_views.py.
"""
from pathlib import Path
import sys

import numpy as np
from PIL import Image

picture = np.asarray(Image.open(Path(sys.argv[1])).convert('RGB'))
if picture.shape[:2] != (720,1280):
    raise ValueError('Expected the 1280 by 720 distribution picture')
sections = {'source': (48,32,500,29), 'lower caption': (392,628,491,61)}
trials = {'seated': ((2.55,2.45,1.12),1.95), 'doorway': ((.45,.64,1.50),1.95),
          'side': ((2.55,2.45,1.12),2.72)}
for section, (x,y,w,h) in sections.items():
    ink_y, ink_x = np.where(picture[y:y+h,x:x+w].min(axis=2) > 200)
    points = np.column_stack((.45 + (ink_x+x+.5)*1.90/1280,
                              np.full(len(ink_x),5.80),
                              2.02 - (ink_y+y+.5)*1.07/720))
    for trial, (eye,reader_x) in trials.items():
        rays = points - eye
        blocked = np.zeros(len(points),dtype=bool)
        for offset,z,radii in [(0,1.60,(.115,.12,.145)), (0,1.11,(.21,.14,.40)),
                               (-.09,.45,(.095,.115,.45)), (.09,.45,(.095,.115,.45))]:
            # Transform the finite eye-to-pixel segment to a unit sphere.
            directions = rays/radii
            origin = (np.asarray(eye) - (reader_x+offset,4.18,z))/radii
            nearest = np.clip(-(directions*origin).sum(1)/(directions**2).sum(1),0,1)
            blocked |= ((origin + directions*nearest[:,None])**2).sum(1) <= 1
        print(f'{section:13s} {trial:8s}  {blocked.sum():4d} / {len(points)}')

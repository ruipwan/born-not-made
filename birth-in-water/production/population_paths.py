"""Separate camera, glossy and transmission paths in the registered north-wall shot."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('renders',type=Path)
parser.add_argument('sheet',type=Path)
args=parser.parse_args()
p=args.renders
raw=p/'north/spill-0001.png'
definition={'all paths':raw,'camera hidden':p/'control/north-camera-hold0-1.png',
    'glossy hidden':p/'control/north-glossy-hold0-1.png',
    'transmission hidden':p/'control/north-transmission-hold0-1.png',
    'held source at 1':p/'control/north-all-hold1-1.png',
    'held source at 8':p/'control/north-all-hold1-8.png'}
def read(path):
    with Image.open(path) as im:return np.asarray(im.convert('RGB'),dtype='f4')
base=read(raw)
poly=Image.new('1',(768,432));ImageDraw.Draw(poly).polygon([tuple(v) for v in json.loads((p/'north/front-pane.json').read_text())],fill=1)
mask=np.asarray(poly,dtype=bool);y,x=np.indices(mask.shape)
regions={'upper right pane':mask&(x>=530)&(x<635)&(y<215),
         'direct image above rail':(x>=565)&(x<595)&(y>=122)&(y<146)}
with (p/'paths.csv').open('w') as f:
    writer=csv.writer(f,lineterminator='\n');writer.writerow(['diagnostic','region','pixels','mean_abs_difference_luma','fraction_difference_over_3'])
    for name,source in definition.items():
        change=abs((read(source)-base)@np.array([.2126,.7152,.0722]))
        for region,area in regions.items():
            writer.writerow([name,region,int(area.sum()),round(float(change[area].mean()),5),
                             round(float((change[area]>3).mean()),5)])
canvas=Image.new('RGB',(1110,275),'#e6ece4');text=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf',16)
for col,(key,title) in enumerate([('all paths','All paths'),('glossy hidden','Screen hidden from glossy rays'),
                                  ('transmission hidden','Screen hidden from transmission rays')]):
    with Image.open(definition[key]) as im:
        pic=im.convert('RGB').crop((490,112,675,232)).resize((370,240),Image.Resampling.LANCZOS)
    canvas.paste(pic,(col*370,0));text.text((col*370+9,247),title,font=font,fill='#1b3930')
canvas.save(args.sheet,quality=93)

"""Make a registered two-wall comparison from 64 matched Cycles frames per layout."""
import argparse
import csv
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image,ImageDraw,ImageFont

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('renders',type=Path,help='north/ and east/ hold raw spill-*.png, with finished pictures in cleaned/')
parser.add_argument('output',type=Path)
args=parser.parse_args()
p=args.renders
sides=('north','east')
poly=Image.new('1',(768,432))
corners=json.loads((p/'north/front-pane.json').read_text())
ImageDraw.Draw(poly).polygon([tuple(v) for v in corners],fill=1)
mask=np.asarray(poly,dtype=bool)
y,x=np.indices(mask.shape)
rois={'front pane':mask, 'upper right pane':mask&(x>=530)&(x<635)&(y<215),
      'centre of shell':(x>=421)&(x<473)&(y>=190)&(y<225)}
coeffs=np.array([.2126,.7152,.0722],dtype='f4')
def luma(path):
    with Image.open(path) as im:return np.asarray(im.convert('RGB'),dtype='f4')@coeffs

font_path='/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'
heading=ImageFont.truetype(font_path,23);small=ImageFont.truetype(font_path,17)
size=(1280,818)
scale=Image.Resampling.LANCZOS
target=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
    '-video_size','1280x818','-framerate','16','-i','-','-an','-c:v','libx264',
    '-pix_fmt','yuv420p','-preset','slow','-crf','18','-threads','3','-movflags','+faststart',
    str(args.output)],stdin=subprocess.PIPE)
first,previous={},{}
with (p/'motion.csv').open('w') as f:
    rows=csv.writer(f,lineterminator='\n')
    rows.writerow(['layout','frame','source_s','region','pixels','mean_luma_change_since_previous','mean_luma_change_since_first'])
    for i in range(1,65):
        canvas=Image.new('RGB',size,'#182b28')
        pen=ImageDraw.Draw(canvas)
        filename=f'spill-{i:04}.png'
        for col,side in enumerate(sides):
            raw=luma(p/side/filename)
            first.setdefault(side,raw)
            previous.setdefault(side,raw)
            for area,m in rois.items():
                rows.writerow([side,i,49+(i-1)/16,area,int(m.sum()),
                    round(float(np.abs(raw[m]-previous[side][m]).mean()),5),
                    round(float(np.abs(raw[m]-first[side][m]).mean()),5)])
            previous[side]=raw
            with Image.open(p/side/'cleaned'/filename) as img:
                img=img.convert('RGB')
                canvas.paste(img.resize((640,360),scale),(640*col,0))
                canvas.paste(img.crop((348,106,668,286)).resize((640,360),scale),(640*col,360))
            pen.text((640*col+14,729),side.capitalize()+' wall',font=heading,fill='#ecf0e6')
        pen.text((14,777),'Seated view above   /   Same tank detail below   /   Fixed shell and water   /   Moving digital recording',font=small,fill='#c3d6c9')
        pen.text((1110,777),f'{49+(i-1)/16:.2f} s',font=small,fill='#dbe6dd')
        target.stdin.write(canvas.tobytes())
target.stdin.close()
if target.wait():raise RuntimeError('Population wall comparison encode failed')

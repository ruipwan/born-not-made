"""Project an eight-second passage onto the proposed wall through a moving visitor.

Usage: projection_beam.py OUTPUT_DIR. Input footage is the distributed projection
master. The ray test uses a point lens and the room's head, torso and leg proxies.
"""
import argparse
import csv
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

wall_y, wall_width, wall_height = 5.80, 1.90, 1.07
wall_left, wall_top = .45, 2.02
lenses = {'standard': (1.4, 1.95, 2.02), 'short': (1.4, 4.10, 2.02)}
seated = (2.55, 2.45, 1.12)
body = [(0,1.60,.115,.12,.145), (0,1.11,.21,.14,.40),
        (-.09,.45,.095,.115,.45), (.09,.45,.095,.115,.45)]

def wall_grid(w, h):
    x = wall_left + (np.arange(w,dtype='f4')+.5)*wall_width/w
    z = wall_top - (np.arange(h,dtype='f4')+.5)*wall_height/h
    return x[None,:], z[:,None]

class Rays:
    def __init__(self, source, points, target_y=wall_y):
        self.source = np.array(source)
        x,z = points
        self.dx, self.dy, self.dz = x-source[0], target_y-source[1], z-source[2]

    def blocked(self, x, y, scale=1.):
        sx,sy,sz = self.source
        hits = np.zeros(np.broadcast_shapes(self.dx.shape,self.dz.shape),dtype=bool)
        for offset,mid,rx,ry,rz in body:
            rx,ry,rz = rx*scale, ry*scale, rz*scale
            a = (self.dx/rx)**2+(self.dy/ry)**2+(self.dz/rz)**2
            b = self.dx*(sx-x-offset*scale)/rx**2+self.dy*(sy-y)/ry**2+self.dz*(sz-mid*scale)/rz**2
            c = ((sx-x-offset*scale)/rx)**2+((sy-y)/ry)**2+((sz-mid*scale)/rz)**2-1
            # The lens and wall lie outside each ellipsoid. A hit requires both
            # an intersection and a closest point within the finite ray segment.
            hits |= (b*b >= a*c) & (b<0) & (-b<a)
        return hits

def measure_label(out, release):
    pix=np.asarray(Image.open(release).convert('RGB'))
    assert pix.shape==(720,1280,3)
    with (out/'beam-captions.csv').open('w') as f:
        rows=csv.writer(f,lineterminator='\n')
        rows.writerow(['reader_x_m','reader_y_m','height_m','area','count','standard_shadow','short_shadow','seated_occlusion'])
        for x,y,height in [(1.95,4.18,1.745),(1.4,4.18,1.745),(1.4,4.90,1.745),(1.4,4.90,1.90)]:
            for name,(px,py,w,h) in {'source': (48,32,500,29), 'lower':(392,628,491,61)}.items():
                iy,ix=np.where(pix[py:py+h,px:px+w].min(axis=2)>200)
                pts=(wall_left+(px+ix+.5)*wall_width/1280,wall_top-(py+iy+.5)*wall_height/720)
                hits=[Rays(loc,pts).blocked(x,y,height/1.745).sum() for loc in (*lenses.values(),seated)]
                rows.writerow([x,y,height,name,len(ix),*hits])

def render(out, movie):
    w,h=640,360
    points=wall_grid(w,h)
    beams=[Rays(lens,points) for lens in lenses.values()]
    source=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-ss','46','-i',str(movie),
        '-t','8','-an','-vf','fps=24,scale=640:360:flags=lanczos','-pix_fmt','rgb24',
        '-threads','1','-f','rawvideo','-'],stdout=subprocess.PIPE)
    target=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-video_size','1280x456','-framerate','24','-i','-','-an','-c:v','libx264',
        '-preset','slow','-crf','19','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',
        str(out/'beam-study.mp4')],stdin=subprocess.PIPE)
    font_dir=Path('/usr/share/fonts/truetype/open-sans')
    font=ImageFont.truetype(str(font_dir/'OpenSans-Regular.ttf'),23)
    small=ImageFont.truetype(str(font_dir/'OpenSans-Regular.ttf'),17)
    footer=Image.new('RGB',(1280,96),'#172825')
    pen=ImageDraw.Draw(footer)
    for offset,title in [(0,'3.85 m throw'),(640,'1.70 m throw')]:
        pen.text((offset+14,9),title,font=font,fill='#f0f1e8')
    pen.text((14,56),'Modelled shadow on the film wall    /    Same visitor and recorded picture',font=small,fill='#becfc4')
    # Simple display comparison. Unshadowed values retain the source contrast
    # above an assumed 2% white ambient floor. A blocked ray receives ambient only.
    codes=np.arange(256)/255
    linear=np.where(codes<=.04045,codes/12.92,((codes+.055)/1.055)**2.4)
    floor=.02
    forward=lambda l:np.where(l<=.0031308,12.92*l,1.055*l**(1/2.4)-.055)
    lit=np.uint8(255*forward(floor+(1-floor)*linear)+.5)
    dim=round(255*float(forward(floor)))
    with (out/'beam-motion.csv').open('w') as f:
        stats=csv.writer(f,lineterminator='\n')
        stats.writerow(['frame','film_s','reader_x_m','standard_shadow_pixels','short_shadow_pixels','total_wall_pixels'])
        for i in range(192):
            raw=source.stdout.read(w*h*3)
            if len(raw)!=w*h*3:raise RuntimeError(f'Missing source picture at {i}')
            pic=lit[np.frombuffer(raw,dtype='uint8').reshape(h,w,3)]
            t=i/24
            x=2.40-.40*np.clip(t-1,0,4)
            masks=[beam.blocked(x,4.18) for beam in beams]
            copies=[]
            for mask in masks:
                displayed=pic.copy()
                displayed[mask]=dim
                copies.append(displayed)
            frame=Image.new('RGB',(1280,456))
            frame.paste(Image.fromarray(np.concatenate(copies,axis=1)),(0,0))
            frame.paste(footer,(0,360))
            ImageDraw.Draw(frame).text((1085,416),f'Film   {46+t:05.2f} s',font=small,fill='#d5e2d7')
            target.stdin.write(frame.tobytes())
            stats.writerow([i,round(46+t,5),round(float(x),4),*[m.sum() for m in masks],w*h])
        target.stdin.close()
    if source.wait() or target.wait():raise RuntimeError('Projection study encode failed')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    parser.add_argument('release',type=Path,help='49.5 s frame from the 720p open-caption film')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    measure_label(args.output,args.release)
    render(args.output,Path(__file__).resolve().parents[1]/'media/gallery-projection-1080.mp4')

"""Measure a fixed seated eye with two film-wall positions, across a visitor crossing."""
import argparse
import csv
import io
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from projection_beam import Rays, seated, wall_height, wall_top, wall_width, wall_y

root = Path(__file__).resolve().parents[1]
group = ((4.45, 2.9), (5.15, 2.6), (5.9, 2.9), (6.45, 2.45), (4., 4.85))


def at_wall(cx, x, y):
    return cx - wall_width/2 + x*wall_width, wall_top - y*wall_height


def pause_card(x, z, eye_z, card_z):
    k = (3.82-seated[1])/(wall_y-seated[1])
    u = seated[0]+k*(x-seated[0]); v = eye_z+k*(z-eye_z)
    return (abs(u-2.89) <= .297/2) & (abs(v-card_z) <= .210/2)


def crossing(t):
    u = np.clip((t-.25)/1.75, 0, 1)
    return (4.23-1.23*u*u*(3-2*u), 3.15)


def measure(output, proof=None):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '49.5', '-i',
          str(root/'media/gallery-projection-1080.mp4'), '-frames:v', '1', '-c:v', 'png',
          '-f', 'image2pipe', '-'])
    frame = np.asarray(Image.open(io.BytesIO(data)).convert('RGB'))
    assert frame.shape == (1080, 1920, 3)
    if proof:
        # Native projection pixels. An opaque paper colour marks the eye rays
        # intersecting the A4 card in each of the two shifted-wall layouts.
        xx, yy = np.meshgrid(np.arange(550,1370), np.arange(922,1045))
        X, Z = at_wall(2.8,(xx+.5)/1920,(yy+.5)/1080)
        sheet = Image.new('RGB',(844,377),'#172823')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf',20)
        for n, height in enumerate((1.09,.90)):
            visible = frame[922:1045,550:1370].copy()
            visible[pause_card(X,Z,1.12,height)] = (207,201,183)
            y = n*182
            draw.text((12,y+8),f'Film 49.50 s   /   Card centre {height:.2f} m',font=font,fill='#edf0e6')
            sheet.paste(Image.fromarray(visible),(12,y+43))
        sheet.save(proof,quality=94)
    with output.open('w') as f:
        out = csv.writer(f, lineterminator='\n')
        out.writerow(['wall_centre_x_m','card_centre_z_m','eye_z_m','wall_to_mouth_angle_deg','area','walker_at_t_s',
                      'sample_count','walker_hits','other_people_hits','paper_hits','union_hits'])
        for cx,card_z in ((1.4,1.09),(2.8,1.09),(2.8,.90)):
            angle = math.degrees(math.atan2(3.5-seated[0], 3.96-seated[1])
                               - math.atan2(cx-seated[0], wall_y-seated[1]))
            for name, box in [('source',(48,25,870,120)),('lower',(550,922,1370,1045))]:
                x0,y0,x1,y1 = box
                py,px = np.where(frame[y0:y1,x0:x1].min(axis=2)>200)
                X,Z = at_wall(cx,(x0+px+.5)/1920,(y0+py+.5)/1080)
                for eye_z in (1., 1.12, 1.30, 1.62):
                    rays = Rays((seated[0],seated[1],eye_z),(X,Z))
                    others = np.logical_or.reduce([rays.blocked(x,y) for x,y in group])
                    paper = pause_card(X,Z,eye_z,card_z)
                    for t in (0, .75, 1.25, 1.75, 2., 4.5):
                        person = rays.blocked(*crossing(t))
                        out.writerow([cx,card_z,eye_z,round(angle,2),name,t,len(X),person.sum(),
                                      others.sum(),paper.sum(),(person|others|paper).sum()])


def read_pause_heading(output):
    with tempfile.TemporaryDirectory() as folder:
        name=Path(folder)/'card'
        subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','900','-singlefile',
                        '-png',str(root/'studies/tank-status.pdf'),str(name)],check=True)
        pixels=np.asarray(Image.open(name.with_suffix('.png')).convert('L'))
    assert pixels.shape==(637,900)
    py,px=np.where(pixels[108:196,33:630]<80)
    px,py=px+33,py+108
    with output.open('w') as f:
        out=csv.writer(f,lineterminator='\n')
        out.writerow(['eye_x_m','eye_y_m','eye_z_m','card_centre_z_m','downward_angle_deg',
                      'heading_ink_samples','max_hits_across_six_crossing_positions'])
        for eye in [(2.55,2.45,h) for h in (1.,1.12,1.30,1.62)]+[(1.26,.29,1.53)]:
            for h in (1.09,.90):
                x=2.89-.297/2+(px+.5)*.297/900
                z=h+.210/2-(py+.5)*.210/637
                rays=Rays(eye,(x,z),target_y=3.82)
                fixed=np.logical_or.reduce([rays.blocked(*pos) for pos in group])
                blocked=max((fixed|rays.blocked(*crossing(t))).sum() for t in (0,.75,1.25,1.75,2.,4.5))
                dip=math.degrees(math.atan2(eye[2]-h,math.hypot(2.89-eye[0],3.82-eye[1])))
                out.writerow([*eye,h,round(dip,2),len(px),blocked])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--proof',type=Path)
    parser.add_argument('--sign-counts',type=Path)
    args=parser.parse_args()
    measure(args.output,args.proof)
    if args.sign_counts:read_pause_heading(args.sign_counts)

"""Package six matched room-acoustic auditions with the same six seconds of film."""
import argparse
import csv
from pathlib import Path
import subprocess
import tempfile

from PIL import Image,ImageDraw,ImageFont

from room_acoustics import EARS,SOURCES

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('signals',type=Path,help='Output directory of room_acoustics.py')
parser.add_argument('output',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
font_dir=Path('/usr/share/fonts/truetype/open-sans')
def font(size):
    return ImageFont.truetype(str(font_dir/'OpenSans-Regular.ttf'),size)
serif=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',43)
ink='#f0f0e6';soft='#c7d7cd';mint='#82c5b4';amber='#e9b676'
station={'seat':'Seated bay','door':'Entrance','bench':'Service bench'}
with (args.signals/'positions.csv').open() as f:
    values={(r['speaker'],r['listener']):float(r['full_db_relative_to_seat']) for r in csv.DictReader(f)
            if r['reflection_amplitude']=='0.8' and r['order']=='36'}
def background(speaker,ear):
    image=Image.new('RGB',(1280,720),'#162724');pen=ImageDraw.Draw(image)
    pen.text((32,25),'BIRTH IN WATER',font=font(19),fill=soft)
    pen.text((30,62),'Listening from the '+{'seat':'seated bay','door':'entrance','bench':'service bench'}[ear],font=serif,fill=ink)
    pen.text((32,548),'Same six seconds of the exhibition film',font=font(22),fill=ink)
    pen.text((32,586),'Original picture   /   Modelled mono sound at the marked ear',font=font(19),fill=soft)
    pen.text((32,658),'8 × 6 × 3 m closed-room model    •    Each speaker matched at the seat',font=font(19),fill=soft)
    # Position axes match the printed plan, north up and east right.
    left,bottom,scale=807,480,50
    def xy(p):return (left+p[0]*scale,bottom-p[1]*scale)
    def box(x,y,w,h,fill):
        pen.rectangle([xy((x,y+h)),xy((x+w,y))],fill=fill)
    pen.rectangle([xy((0,6)),xy((8,0))],outline=soft,width=2)
    box(3.1,3.70,1.80,.65,'#5b837e');box(2.7,5.37,2.6,.60,'#6f7165')
    pen.line([xy((.45,5.8)),xy((2.35,5.8))],fill=mint,width=4)
    ax,ay=xy(SOURCES[speaker]);ex,ey=xy(EARS[ear])
    pen.line([(ax,ay),(ex,ey)],fill='#91a49b',width=2)
    pen.rectangle((ax-7,ay-7,ax+7,ay+7),fill=mint)
    pen.ellipse((ex-9,ey-9,ex+9,ey+9),fill=amber)
    pen.text((807,510),'Speaker   '+('film wall' if speaker=='wall' else 'beside the bay'),font=font(22),fill=mint)
    pen.text((807,547),'Ear   '+station[ear],font=font(22),fill=amber)
    value=values[(speaker,ear)]
    pen.text((807,592),f'{value:+.1f} dB relative to the seat',font=font(23),fill=ink)
    return image

def ff(*args):
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y',*map(str,args)],check=True)

with tempfile.TemporaryDirectory() as temp:
    p=Path(temp);chapters=';FFMETADATA1\ntitle=Listening from the room\nartist=Ruipeng Wang / Born, Not Made\n'
    cuts=[];audio=[]
    for i,(speaker,ear) in enumerate((s,e) for s in SOURCES for e in EARS):
        mark=p/f'{i}.png';background(speaker,ear).save(mark)
        ff('-threads','2','-ss','52','-t','6','-i',root/'media/gallery-projection-1080.mp4',
           '-loop','1','-framerate','30','-i',mark,'-t','6','-filter_complex_threads','2',
           '-filter_complex','[0:v]scale=704:396:flags=lanczos[v];[1:v][v]overlay=32:142:shortest=1',
           '-an','-c:v','libx264','-threads','3','-preset','medium','-crf','21','-pix_fmt','yuv420p',p/f'{i}.mp4')
        cuts.append(f"file '{i}.mp4'\n")
        audio.append(f"file '{(args.signals/f'{speaker}-{ear}.wav').resolve()}'\n")
        chapters+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={i*6000}\nEND={(i+1)*6000}\ntitle={speaker} speaker / {station[ear]}\n'
    (p/'picture.ffconcat').write_text(''.join(cuts));(p/'sound.ffconcat').write_text(''.join(audio))
    (p/'marks.txt').write_text(chapters)
    ff('-f','concat','-safe','0','-i',p/'picture.ffconcat','-f','concat','-safe','0','-i',p/'sound.ffconcat',
       '-f','ffmetadata','-i',p/'marks.txt','-map','0:v','-map','1:a','-map_metadata','2','-map_chapters','2',
       '-c:v','copy','-c:a','aac','-b:a','136k','-movflags','+faststart',args.output)

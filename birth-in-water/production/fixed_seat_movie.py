"""Assemble three consecutive six-second fixed-eye studies with source-time labels.

Usage: python fixed_seat_movie.py RENDER_ROOT OUTPUT.mp4
Each named layout folder contains clean/bay-0001.png through bay-0072.png.
"""
import argparse
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

layouts = [
    ('original', 'Original wall', '51.1° between film centre and tank mouth.'),
    ('nearer', 'Film moved 1.40 m', '27.9° between centres. The pause card covers part of the film.'),
    ('nearer-low', 'Same wall, card lowered 0.19 m', 'The lower caption clears the card at the tested seated mark.'),
]
font_dir = Path('/usr/share/fonts/truetype/open-sans')
label = ImageFont.truetype(str(font_dir/'OpenSans-Semibold.ttf'),25)
copy = ImageFont.truetype(str(font_dir/'OpenSans-Regular.ttf'),19)

def assemble(render_root, output):
    process = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-video_size','768x532','-framerate','12','-i','-','-an','-c:v','libx264','-threads','3',
        '-crf','18','-preset','slow','-pix_fmt','yuv420p','-metadata',
        'title=Birth in Water — three views from a fixed seat','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
    for name,title,note in layouts:
        for frame in range(1,73):
            canvas=Image.new('RGB',(768,532),'#172823')
            with Image.open(render_root/name/'clean'/f'bay-{frame:04}.png') as image:
                if image.size!=(768,432):raise ValueError('Unexpected camera raster')
                canvas.paste(image.convert('RGB'))
            pen=ImageDraw.Draw(canvas)
            pen.text((12,443),title,font=label,fill='#f4f1e6')
            pen.text((614,450),f'Film  {45+(frame-1)/12:05.2f} s',font=copy,fill='#c2d7c8')
            pen.text((12,491),note,font=copy,fill='#d7e2d6')
            process.stdin.write(canvas.tobytes())
    process.stdin.close()
    if process.wait():raise RuntimeError('Fixed-seat encode failed')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('render_root',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    assemble(args.render_root,args.output)

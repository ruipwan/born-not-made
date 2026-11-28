"""Assemble the completed 96-frame shell shot and 48-frame empty-water control.

Inputs are two directories of denoised rim-NNNN.png images. The output starts
with the 4 s fixed-hull shot. The following 4 s repeat a 2 s matched comparison.
Use --proof N to save a JPEG of the comparison layout at that source frame.
"""
import argparse
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser(description=__doc__)
for key in ('hull','empty','output'):
    parser.add_argument(key,type=Path)
parser.add_argument('--proof',type=int)
args=parser.parse_args()
font=ImageFont.truetype('DejaVuSans.ttf',23)
small=ImageFont.truetype('DejaVuSans.ttf',17)
size=(1152,720)
dark=(19,33,32)
white=(243,243,231)
muted=(185,205,196)
resample=Image.Resampling.LANCZOS

def source(folder, number):
    with Image.open(folder/f'rim-{number:04d}.png') as im:
        if im.size!=(768,432):
            raise ValueError(f'Unexpected size in {folder}, frame {number}')
        return im.convert('RGB')

def picture(number, compare):
    canvas=Image.new('RGB',size,dark)
    draw=ImageDraw.Draw(canvas)
    if compare:
        for column,(folder,label) in enumerate(((args.empty,'Empty-basin water field'),(args.hull,'Water field with the rigid shell'))):
            im=source(folder,number)
            x=576*column
            canvas.paste(im.resize((576,324),resample),(x,0))
            # The crop spans the slots cut into the upper rim at the waterline.
            canvas.paste(im.crop((240,79,624,295)).resize((576,324),resample),(x,324))
            draw.text((x+15,653),label,font=font,fill=white)
        legend='Same shell on camera   /   Whole frame above, rim detail below   /   Two seconds repeated twice'
    else:
        canvas.paste(source(args.hull,number).resize((1152,648),resample),(0,0))
        draw.text((15,653),'Water at the fixed shell',font=font,fill=white)
        legend='Project CAD   /   Modelled water and light   /   118 mm lens'
    draw.text((15,690),legend,font=small,fill=muted)
    draw.text((1065,690),f'{(number-1)/24:.2f} s',font=small,fill=white)
    return canvas

if args.proof:
    picture(args.proof,True).save(args.output,quality=92)
else:
    with subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                           '-video_size','1152x720','-framerate','24','-i','-','-an',
                           '-pix_fmt','yuv420p','-c:v','libx264','-crf','18','-preset','slow',
                           '-threads','2','-movflags','+faststart',str(args.output)],
                           stdin=subprocess.PIPE) as encoder:
        for i in range(192):
            compare=i>=96
            number=(i-96)%48+1 if compare else i+1
            encoder.stdin.write(picture(number,compare).tobytes())
        encoder.stdin.close()
        if encoder.wait()!=0:
            raise RuntimeError('Optical comparison encode failed')

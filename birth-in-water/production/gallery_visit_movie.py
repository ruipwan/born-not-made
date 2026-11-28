"""Make the 16 s seated visit from final-room renders and the film's local speaker."""
import argparse
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.io.wavfile import write
from scipy.signal import fftconvolve

from room_acoustics import EARS, RATE, SOURCES, impulse, level

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('pictures',type=Path,help='192 consecutive cleaned bay-NNNN.png pictures')
parser.add_argument('output',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
def programme(start,duration):
    out=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(root/'media/gallery-projection-1080.mp4'),
        '-t',str(duration),'-vn','-af','pan=mono|c0=0.5*FL+0.5*FR','-ar',str(RATE),'-f','f32le','-'])
    return np.frombuffer(out,dtype='<f4').astype('f8')
with tempfile.TemporaryDirectory() as temp:
    tmp=Path(temp)
    response=impulse(SOURCES['bay'],EARS['seat'],.80,36)
    signal=programme(43,18)
    heard=fftconvolve(signal,response)[:len(signal)]
    # Same level calibration interval as the six-station acoustic study.
    reference=slice(9*RATE,15*RATE)
    gain=10**((level(signal[reference])-level(heard[reference]))/20)
    actual=heard[2*RATE:18*RATE]*gain
    assert len(actual)==16*RATE and np.abs(actual).max()<1
    fade=np.linspace(0,1,round(.08*RATE))
    actual[:len(fade)]*=fade;actual[-len(fade):]*=fade[::-1]
    write(tmp/'bay.wav',RATE,np.int16(np.round(actual*32767)))
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-video_size','768x540','-framerate','12','-i','-','-i',str(tmp/'bay.wav'),'-map','0:v','-map','1:a',
        '-c:v','libx264','-threads','3','-crf','18','-preset','slow','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','128k','-metadata','title=Birth in Water — a seated visit during reset',
        '-metadata','artist=Ruipeng Wang / Born, Not Made','-movflags','+faststart',str(args.output)],stdin=subprocess.PIPE)
    fontfile='/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'
    face=ImageFont.truetype(fontfile,22);small=ImageFont.truetype(fontfile,17)
    for i in range(1,193):
        canvas=Image.new('RGB',(768,540),'#172824')
        with Image.open(args.pictures/f'bay-{i:04}.png') as scene:
            if scene.size!=(768,432):raise ValueError('Unexpected render size')
            canvas.paste(scene.convert('RGB'),(0,0))
        t=(i-1)/12
        text=ImageDraw.Draw(canvas)
        text.text((14,443),'Tank paused   /   Modelled seated visit',font=small,fill='#bbd2c0')
        text.text((616,443),f'Film  {45+t:05.2f} s',font=small,fill='#bbd2c0')
        if t<1.6:
            cue='The film score can be heard from the seated bay.'
        elif t<3.55:
            cue='A visitor crosses the opening. The seat stays still.'
        elif t<3.916:
            cue='North wall. The first prototype is on screen.'
        elif t<9:
            cue='A strip of water opens. A second tone enters.'
        elif t<15:
            cue='The smaller hull curves back. The lower tone holds.'
        else:
            cue='The film cuts to a second tank. The live tank is still paused.'
        text.text((14,483),cue,font=face,fill='#f1f1e7')
        enc.stdin.write(canvas.tobytes())
    enc.stdin.close()
    if enc.wait():raise RuntimeError('Seated-room encode failed')

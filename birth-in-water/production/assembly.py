"""Usage: python assembly.py WATER_BEINGS.mp4 FIRST_TANK_WITH_AUDIO.mp4 CREATIVE_AI_2026.mp4 output.mp4
Inputs are the artist's videos identified in the camera report. FFmpeg with libx264 required.
"""
from pathlib import Path
import subprocess as sp
import sys, tempfile
water,tank,second,out=sys.argv[1:]
def run(*args):
 sp.run(['ffmpeg','-nostdin','-v','error','-y',*map(str,args)],check=True)
with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 # No retiming. Use one continuous 36 s tank observation; cut only between source works.
 for n,(source,start,length,audio,grade) in enumerate([
  (water,7,7,False,'null'),(tank,1,36,True,'eq=contrast=1.025:brightness=0.009:saturation=0.87'),
  (second,23.85,5.15,False,'null'),(water,49,8,False,'null')]):
  inputs=['-ss',start,'-i',source]
  if not audio:inputs+=['-f','lavfi','-i','anullsrc=r=48000:cl=stereo']
  run(*inputs,'-t',length,'-map','0:v','-map',('0:a:0' if audio else '1:a:0'),'-vf',
      f'{grade},fps=30,scale=1280:720:flags=lanczos,setsar=1',
      '-af','aresample=48000,afade=t=in:d=0.12,afade=t=out:st='+str(length-.15)+':d=0.15',
      '-c:v','libx264','-preset','slow','-threads','4','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',p/f'{n}.mp4')
 (p/'edl').write_text(''.join(f"file '{n}.mp4'\n" for n in range(4)))
 run('-f','concat','-safe','0','-i',p/'edl','-c','copy','-movflags','+faststart',out)

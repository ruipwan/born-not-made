"""Finish a contiguous CG frame range. Input directory must contain all frames.
Usage: python pack_rushes.py oidnDenoise source_dir prefix count output.mp4 [wide]
"""
import sys,subprocess,tempfile
from pathlib import Path
from denoise_render import denoise
oidn,src,prefix,count,out,*opt=sys.argv[1:]
with tempfile.TemporaryDirectory() as td:
 d=Path(td)
 for num in range(1,int(count)+1):
  f=Path(src)/f'{prefix}{num:04d}.png'
  if not f.is_file():raise FileNotFoundError(f)
  denoise(oidn,f,d/f'frame-{num:04d}.png')
 vf='crop=810:456:105:0,scale=960:540:flags=lanczos' if opt==['wide'] else 'pad=ceil(iw/2)*2:ceil(ih/2)*2'
 subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','24','-i',str(d/'frame-%04d.png'),'-vf',vf,'-pix_fmt','yuv420p','-c:v','libx264','-threads','2','-preset','slow','-crf','20','-movflags','+faststart',out],check=True)

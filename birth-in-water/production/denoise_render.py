"""Denoise sRGB CG frames with Intel Open Image Denoise 2.5.1.
Usage: python denoise_render.py path/to/oidnDenoise input.png output.png
Photo and documentary sources do not pass through this process.
"""
import subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
import numpy as np
def denoise(oidn,source,output):
 raw=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32)/255
 h,w,_=raw.shape
 with tempfile.TemporaryDirectory() as d:
  a,b=Path(d)/'a.pfm',Path(d)/'b.pfm'
  with a.open('wb') as f:
   f.write(f'PF\n{w} {h}\n-1.0\n'.encode());raw[::-1].astype('<f4').tofile(f)
  subprocess.run([str(oidn),'--device','cpu','--ldr',str(a),'--srgb','-o',str(b),'--threads','2','-q','balanced','-v','0'],check=True,stdout=subprocess.DEVNULL)
  with b.open('rb') as f:
   assert f.readline().strip()==b'PF'
   width,height=map(int,f.readline().split());scale=float(f.readline())
   pixels=np.fromfile(f,dtype='<f4' if scale<0 else '>f4').reshape(height,width,3)[::-1]
  blend=np.clip(.96*pixels+.04*raw,0,1)
  Image.fromarray(np.uint8(255*blend+.5)).save(output)
if __name__=='__main__':denoise(*sys.argv[1:])

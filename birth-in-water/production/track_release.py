"""Track pale silhouettes in FIRST_TANK_WITH_AUDIO.mp4 at 10 Hz (image pixels only).
Usage: python track_release.py source.mp4 output.csv
"""
import csv,sys,subprocess
import numpy as np
from scipy import ndimage
w,h=480,270
proc=subprocess.Popen(['ffmpeg','-v','error','-i',sys.argv[1],'-vf',f'fps=10,scale={w}:{h}',
 '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
with open(sys.argv[2],'w') as target:
 writer=csv.writer(target);writer.writerow(['source_s','carrier_x_px','carrier_y_px','child_x_px','child_y_px','gap_px'])
 for n in range(400):
  raw=proc.stdout.read(w*h*3)
  if len(raw)!=w*h*3:break
  pix=np.frombuffer(raw,dtype=np.uint8).reshape(h,w,3).astype(float)
  mask=(pix.mean(2)>98)&((pix.max(2)-pix.min(2))<53)
  mask=ndimage.binary_closing(mask,iterations=2)
  regions,count=ndimage.label(mask);sizes=np.bincount(regions.ravel());sizes[0]=0
  order=np.argsort(sizes)[::-1];a=regions==order[0];cy,cx=ndimage.center_of_mass(a)
  row=[n/10,round(cx,1),round(cy,1)]
  if len(order)>1 and sizes[order[1]]>=220:
   b=regions==order[1];by,bx=ndimage.center_of_mass(b)
   row+=[round(bx,1),round(by,1),round(ndimage.distance_transform_edt(~a)[b].min(),1)]
  else:row+=['','','']
  writer.writerow(row)
if proc.wait()!=0:raise RuntimeError('Source decode failed')

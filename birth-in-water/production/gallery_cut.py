"""Exhibition edit from artist sources, see gallery-cut.md.
Usage: python gallery_cut.py media_directory output.mp4 [existing-gallery-picture.mp4]
The optional picture preserves an existing gallery edit while replacing its mix.
Expected: ecology.mp4, pump.mp4, pump-audio.mp4, interface.mp4,
overhead-4k.mp4, overhead-audio.mp4, second.mp4, score.wav, installation.webp.
"""
import sys,subprocess,tempfile
from pathlib import Path
src,out=Path(sys.argv[1]),Path(sys.argv[2]).resolve()
def run(*args):
 subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y',*map(str,args)],check=True)
with tempfile.TemporaryDirectory() as temp:
 tmp=Path(temp)
 # The framing changes at source 15.25 and 26.40 s but the overhead
 # record is continuous across those changes. Different experiments hard-cut.
 shots=[('ecology',7,8,'wide'),('pump',1,10.4,'wide'),('interface',14,5.6,'wide'),
 ('overhead-4k',1,14.25,'wide'),('overhead-4k',15.25,11.15,'detail'),
 ('overhead-4k',26.4,10.60,'wide'),('second',23.85,5.15,'wide'),
 ('installation',0,5,'still'),('ecology',49,9,'wide')]
 picture=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else tmp/'picture.mp4'
 if len(sys.argv)<=3:
  for i,(name,start,duration,framing) in enumerate(shots):
   inputs=['-loop','1','-framerate','30','-i',src/'installation.webp'] if framing=='still' else ['-threads','3','-ss',start,'-t',duration,'-i',src/(name+'.mp4')]
   filters=['crop=1440:810:1660:550'] if framing=='detail' else []
   filters+=['scale=1280:720:flags=lanczos','setsar=1','fps=30']
   if name=='overhead-4k':filters+=['eq=saturation=0.89:brightness=0.006:contrast=1.018']
   run(*inputs,'-t',duration,'-an','-vf',','.join(filters),'-pix_fmt','yuv420p','-c:v','libx264','-crf','27','-threads','3','-preset','slow',tmp/f'shot-{i}.mp4')
  (tmp/'list').write_text(''.join(f"file 'shot-{i}.mp4'\n" for i in range(len(shots))))
  run('-f','concat','-safe','0','-i',tmp/'list','-c','copy',tmp/'picture.mp4')
 # Use the authored resonances for the 36-second observational span. Keep the
 # bench sound synchronous and leave a quiet gap over the control-interface edit.
 import numpy as np
 from scipy.io.wavfile import write
 rate=48000
 total=sum(shot[2] for shot in shots)
 mix=np.zeros((round(total*rate),2),dtype=np.float32)
 for source,start,length,offset,gain,fade in [('pump-audio.mp4',1,10.4,8,.55,.16),('overhead-audio.mp4',1,36,24,1,.15),('score.wav',7,36,24,1,.8)]:
  raw=subprocess.check_output(['ffmpeg','-loglevel','error','-ss',str(start),'-t',str(length),'-i',str(src/source),'-vn','-ar',str(rate),'-ac','2','-f','f32le','-'])
  pcm=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
  env=np.linspace(0,1,round(fade*rate))[:,None]
  pcm[:len(env)]*=env;pcm[-len(env):]*=env[::-1]
  sample=round(offset*rate);mix[sample:sample+len(pcm)]+=pcm*gain
 write(tmp/'mix.wav',rate,np.int16(mix.clip(-1,1)*32767))
 run('-i',picture,'-i',tmp/'mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','96k','-movflags','+faststart',out)

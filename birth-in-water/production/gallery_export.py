"""Encode a distribution MP4 from the gallery_cut.py master.
Usage: python gallery_export.py master.mp4 output.mp4 [--open-captions]
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('master',type=Path);p.add_argument('output',type=Path);p.add_argument('--open-captions',action='store_true')
args=p.parse_args()
master=args.master.resolve();output=args.output.resolve();folder=Path(__file__).resolve().parent
filters='setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709'
if args.open_captions:filters='ass=gallery-captions.ass,'+filters
with tempfile.TemporaryDirectory(dir=output.parent) as temp:
 tmp=Path(temp)
 base=['ffmpeg','-loglevel','error','-y','-reinit_filter','0','-i',str(master),'-vf',filters,'-map','0:v','-c:v','libx264',
       '-threads','3','-preset','slow','-b:v','630k' if args.open_captions else '640k','-passlogfile',str(tmp/'pass')]
 subprocess.run(base+['-pass','1','-an','-f','null','-'],cwd=folder,check=True)
 subprocess.run(base+['-pass','2','-map','0:a','-c:a','copy','-movflags','+faststart',str(tmp/'film.mp4')],cwd=folder,check=True)
 (tmp/'film.mp4').replace(output)

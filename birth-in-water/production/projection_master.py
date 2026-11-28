"""Build the 1080p permanent-caption gallery copy from the original source pixels.

Usage: python projection_master.py media_directory reference_gallery.mp4 output.mp4
The released gallery file supplies the current exhibition sound mix at its original gain.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from gallery_shots import SHOTS

parser = argparse.ArgumentParser(description=__doc__)
for name in ('sources', 'reference', 'output'):
    parser.add_argument(name, type=Path)
args = parser.parse_args()
sources, reference, output = (path.resolve() for path in (args.sources, args.reference, args.output))
folder = Path(__file__).resolve().parent

def ffmpeg(arguments):
    subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', *map(str, arguments)], cwd=folder, check=True)

def stamp(label):
    print(datetime.now(timezone.utc).isoformat(), label, flush=True)

with TemporaryDirectory(dir=output.parent) as temp:
    scratch = Path(temp)
    for index, (name, start, duration, framing) in enumerate(SHOTS):
        if framing == 'still':
            inputs = ['-loop', '1', '-framerate', '30', '-i', sources/'installation.webp']
        else:
            inputs = ['-threads', '2', '-ss', start, '-t', duration, '-i', sources/f'{name}.mp4']
        filters = ['crop=1440:810:1660:550'] if framing == 'detail' else []
        filters += ['scale=1920:1080:flags=lanczos', 'setsar=1', 'fps=30']
        if name == 'overhead-4k':
            filters.append('eq=saturation=0.89:brightness=0.006:contrast=1.018')
        # Identical frame counts and time bases to the existing exhibition edit.
        ffmpeg([*inputs, '-t', duration, '-an', '-vf', ','.join(filters), '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264', '-crf', '15', '-preset', 'veryfast', '-threads', '3', scratch/f'{index}.mp4'])
        stamp(f'registered shot {index+1}: {name}')
    cuts = scratch/'cuts'
    cuts.write_text(''.join(f"file '{i}.mp4'\n" for i in range(len(SHOTS))))
    common = ['-f', 'concat', '-safe', '0', '-i', cuts, '-i', reference, '-map', '0:v:0',
              '-vf', 'ass=gallery-captions.ass,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709',
              '-c:v', 'libx264', '-b:v', '1120k', '-pix_fmt', 'yuv420p', '-preset', 'slow',
              '-threads', '3', '-passlogfile', scratch/'stats']
    ffmpeg([*common, '-pass', '1', '-an', '-f', 'null', '-'])
    stamp('completed analysis pass')
    ffmpeg([*common, '-pass', '2', '-map', '1:a:0', '-c:a', 'copy', '-movflags', '+faststart', scratch/'film.mp4'])
    (scratch/'film.mp4').replace(output)
    stamp('completed projection encode')

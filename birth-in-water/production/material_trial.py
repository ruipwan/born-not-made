"""Join Wang's two full workshop tests with their original framing and camera audio."""
import argparse
from fractions import Fraction
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('sources', type=Path, help='Directory with shell- and sponge-{video,audio}.mp4')
parser.add_argument('output', type=Path)
args = parser.parse_args()
serif = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
sans = '/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'
white, sage = '#f5f3ea', '#bbccc2'
side = 960

def plate(name, path):
    image = Image.new('RGBA', (side, side))
    pen = ImageDraw.Draw(image)
    def block(x, y, words, size, face=sans, color=white, leading=7):
        pen.multiline_text((x, y), words, font=ImageFont.truetype(face, size),
                           fill=color, spacing=leading, stroke_width=0)
    if name == 'shell':
        block(40, 32, 'BIRTH IN WATER', 22, color=sage)
        block(38, 72, 'Weight in water', 67, serif)
        block(40, 754, 'The printed shell', 47, serif)
        block(40, 823, 'Wang describes the shell resting on the pan floor.\nWater moves along its edge.', 32)
    else:
        block(575, 49, 'BIRTH IN WATER', 20, color=sage)
        block(570, 216, 'The floating\nsponge', 54, serif, leading=0)
        block(575, 404, 'The pump sits in a\nsponge. Follow the wire\nback to the hand.', 30, leading=10)
        block(575, 831, 'Ruipeng Wang\nWorkshop recordings, 2025', 19, color=sage)
    image.save(path)

def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', *map(str, args)], check=True)

with tempfile.TemporaryDirectory() as folder:
    tmp = Path(folder)
    seconds = []
    for name, width, height, x, y in [('shell', 960, 540, 0, 187), ('sponge', 540, 960, 0, 0)]:
        video = args.sources / f'{name}-video.mp4'
        label = tmp / f'{name}.png'
        plate(name, label)
        geometry = (f'[0:v]scale={width}:{height}:flags=lanczos,setsar=1,'
                    f'pad=960:960:{x}:{y}:color=0x172624[framed];'
                    '[framed][1:v]overlay=eof_action=repeat:format=yuv420')
        ffmpeg('-threads', 2, '-i', video, '-i', label, '-filter_complex_threads', 2,
               '-filter_complex', geometry, '-an', '-c:v', 'libx264', '-threads', 3,
               '-preset', 'slow', '-crf', 23, '-pix_fmt', 'yuv420p', '-video_track_timescale', 30000,
               tmp / f'{name}.mp4')
        rate, count = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=avg_frame_rate,nb_frames', '-of', 'csv=p=0',
                        tmp/f'{name}.mp4'], text=True).strip().split(',')
        seconds.append(float(int(count) / Fraction(rate)))
    # The concat demuxer reads the first file's duration in microseconds.
    # Specify the exact picture run to avoid a whole-millisecond rounding at the cut.
    listfile = tmp/'edits.ffconcat'
    listfile.write_text(f"ffconcat version 1.0\nfile shell.mp4\nduration {seconds[0]:.9f}\nfile sponge.mp4\n")
    sound = (f'[1:a]atrim=end={seconds[0]:.9f},asetpts=PTS-STARTPTS[a];'
             f'[2:a]atrim=end={seconds[1]:.9f},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[sound]')
    ffmpeg('-f', 'concat', '-safe', 0, '-i', listfile, '-i', args.sources/'shell-audio.mp4',
           '-i', args.sources/'sponge-audio.mp4', '-filter_complex', sound, '-map', '0:v',
           '-map', '[sound]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
           '-video_track_timescale', 30000, '-movflags', '+faststart', args.output)

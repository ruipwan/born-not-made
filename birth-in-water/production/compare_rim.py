"""Compare one second from each registered light test, at two scales."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont

baseline, raised, output = map(Path, sys.argv[1:])
font = ImageFont.truetype('DejaVuSans.ttf', 24)
small = ImageFont.truetype('DejaVuSans.ttf', 17)
with TemporaryDirectory() as temp:
    directory = Path(temp)
    for detail in (False, True):
        name = 'detail' if detail else 'wide'
        for frame in range(1, 25):
            canvas = Image.new('RGB', (1280,442), '#172222')
            draw = ImageDraw.Draw(canvas)
            for i, (folder, label) in enumerate(((baseline, 'First position   /   0.56 m'),
                                                  (raised, 'Raised strip   /   0.82 m'))):
                with Image.open(folder/f'rim-{frame:04}.png') as im:
                    assert im.size == (960,540)
                    if detail:
                        im = im.crop((469,250,949,520))
                    canvas.paste(im.resize((640,360), Image.Resampling.LANCZOS), (640*i,0))
                draw.text((640*i+14,370), label, font=font, fill='#f2f1e9')
            size = 'Matched crop' if detail else 'Full frame'
            draw.text((14,409),f'{size}    /    Model surface at 24 fps    /    One second repeated three times',
                      font=small, fill='#b5ceca')
            canvas.save(directory/f'{name}-{frame:02}.png')
    for index in range(144):
        name = 'wide' if index < 72 else 'detail'
        source = directory/f'{name}-{index%24+1:02}.png'
        (directory/f'output-{index+1:03}.png').symlink_to(source)
    subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number','1',
                    '-i',str(directory/'output-%03d.png'),'-frames:v','144','-pix_fmt','yuv420p',
                    '-c:v','libx264','-crf','18','-preset','slow','-threads','2',
                    '-movflags','+faststart',str(output)], check=True)

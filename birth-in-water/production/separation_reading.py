"""Read 27 consecutive camera frames across the exit in the first 4K tank take.

Usage: python separation_reading.py overhead-4k.mp4 birth-in-water/studies
Requires FFmpeg, NumPy, SciPy and Pillow.
"""
import argparse
import csv
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

# Width, minimum mean RGB, maximum channel spread, closing iterations.
RULES = [(480, 98, 53, 2), (960, 98, 53, 4), (960, 88, 53, 4),
         (960, 108, 53, 4), (960, 98, 43, 4), (960, 98, 63, 4),
         (960, 98, 53, 0)]
TILE = (720, 405)


def gap(image, width, brightness, spread, closing):
    rgb = np.asarray(image if width == 960 else image.resize((480, 270), Image.Resampling.BICUBIC))
    mask = (rgb.sum(2) > 3 * brightness) & (rgb.max(2) - rgb.min(2) < spread)
    if closing:
        mask = ndimage.binary_closing(mask, iterations=closing)
    labels, _ = ndimage.label(mask)
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    first, second = np.argsort(counts)[-2:][::-1]
    if counts[second] < 220 * (width / 480) ** 2:
        return ''
    left, right = labels == first, labels == second
    if ndimage.center_of_mass(left)[1] >= ndimage.center_of_mass(right)[1]:
        raise ValueError('Second patch is outside the expected side of the carrier')
    return round(ndimage.distance_transform_edt(~left)[right].min(), 2)


def make(source, output):
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        filters = ("[0:v]select='between(t,25.35,26.25)',showinfo,split=2[wide][detail];"
                   "[wide]scale=960:540[w];[detail]crop=1440:810:1660:550[d]")
        command = ['ffmpeg', '-hide_banner', '-v', 'info', '-threads', '3', '-ss', '24',
                   '-copyts', '-i', str(source), '-filter_complex_threads', '2', '-filter_complex', filters]
        for stream, name in [('[w]', 'wide'), ('[d]', 'detail')]:
            command += ['-map', stream, '-fps_mode', 'passthrough', '-threads', '2',
                        '-start_number', '0', str(temp / (name + '-%03d.png'))]
        log = subprocess.run(command, check=True, capture_output=True, text=True).stderr
        pts = re.findall(r'n:\s*\d+ pts:\s*\d+ pts_time:([\d.]+)', log)
        if len(pts) != 27:
            raise ValueError(f'Expected 27 consecutive pictures, found {len(pts)}')
        sheet = Image.new('RGB', (TILE[0] * 3, TILE[1] * 9))
        with (output / 'separation-samples.csv').open('w', newline='') as f:
            table = csv.writer(f, lineterminator='\n')
            table.writerow(['sample', 'source_pts_s', 'width_px', 'min_mean_rgb', 'max_channel_spread',
                            'closing_iterations', 'distance_px'])
            for i, timestamp in enumerate(pts):
                with Image.open(temp / f'wide-{i:03}.png') as wide:
                    for rule in RULES:
                        table.writerow([i, timestamp, *rule, gap(wide, *rule)])
                with Image.open(temp / f'detail-{i:03}.png') as detail:
                    tile = detail.convert('RGB').resize(TILE, Image.Resampling.LANCZOS)
                    sheet.paste(tile, ((i % 3) * TILE[0], (i // 3) * TILE[1]))
                    if i == 16:
                        tile.save(output / 'separation-still.jpg', quality=94)
        sheet.save(output / 'separation-frames.jpg', quality=92, subsampling=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    make(args.source, args.output)

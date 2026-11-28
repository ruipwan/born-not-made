"""Measure the angle of the carrier's upper silhouette in the first overhead take.

Usage: python carrier_edge.py overhead-4k.mp4 carrier-edge.csv
The camera looks down. Positive angles slope down toward image right.
"""
import csv
import subprocess
import sys
import numpy as np

WIDTH, HEIGHT = 960, 540
FIRST_SECOND = 22
BANDS = [(350, 465), (340, 445), (365, 465)]
THRESHOLDS = [80, 94, 108]


def fit_edge(image, band, threshold):
    x = np.arange(*band)
    bright = image[50:180, x] > threshold
    y = 50 + np.argmax(bright, axis=0)
    valid = bright.any(axis=0) & (y > 50)
    # The returning child can enter a few columns at the far edge of a band.
    # Start with a median of separated column pairs before refining the line.
    lag = 25
    paired = valid[lag:] & valid[:-lag]
    slope = np.median((y[lag:]-y[:-lag])[paired])/lag
    intercept = np.median((y - slope*x)[valid])
    keep = valid & (np.abs(y - slope*x - intercept) < 3)
    for _ in range(4):
        if keep.sum() < 20:
            raise ValueError('Insufficient continuous hull edge')
        slope, intercept = np.polyfit(x[keep], y[keep], 1)
        residual = np.abs(y - slope*x - intercept)
        keep = valid & (residual < 3)
    return np.degrees(np.arctan(slope)), np.median(residual[keep])


def measure(source, output):
    command = ['ffmpeg', '-v', 'error', '-threads', '2', '-ss', str(FIRST_SECOND),
               '-i', source, '-vf', 'fps=10,scale=960:540', '-pix_fmt', 'gray',
               '-f', 'rawvideo', '-']
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process, open(output, 'w') as target:
        writer = csv.writer(target)
        writer.writerow(['source_s', 'angle_deg', 'range_deg', 'median_error_px'])
        for frame, data in enumerate(iter(lambda: process.stdout.read(WIDTH*HEIGHT), b'')):
            image = np.frombuffer(data, np.uint8).reshape(HEIGHT, WIDTH)
            fits = [fit_edge(image, band, level) for band in BANDS for level in THRESHOLDS]
            angle, residual = fits[1]  # Reference band, middle threshold.
            span = np.ptp([value for value, _ in fits])
            writer.writerow([round(FIRST_SECOND + frame/10, 1), round(angle, 3),
                             round(span, 3), round(residual, 3)])
        if process.wait():
            raise RuntimeError('Source decode failed')


if __name__ == '__main__':
    measure(*sys.argv[1:])

"""Sample-accurate camera and composed signals for the gallery cut."""
import subprocess

import numpy as np

from gallery_shots import SHOTS

RATE = 48_000

def gallery_signals(source_dir, score_path=None):
    samples = round(sum(shot[2] for shot in SHOTS)*RATE)
    camera = np.zeros((samples,2),dtype=np.float32)
    score = np.zeros_like(camera)
    cues = [
        (camera, source_dir/'pump-audio.mp4', 1, 10.4, 8, .55, .16),
        (camera, source_dir/'overhead-audio.mp4', 1, 36, 24, 1, .15),
        (score, score_path or source_dir/'score.wav', 7, 36, 24, 1, .8),
    ]
    for dest, source, start, length, offset, gain, fade in cues:
        raw = subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-t',str(length),
                '-i',str(source),'-vn','-ar',str(RATE),'-ac','2','-f','f32le','-'])
        pcm = np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
        envelope = np.linspace(0,1,round(fade*RATE))[:,None]
        pcm[:len(envelope)] *= envelope
        pcm[-len(envelope):] *= envelope[::-1]
        first = round(offset*RATE)
        dest[first:first+len(pcm)] += pcm*gain
    return camera, score

def pcm16(signal):
    return np.int16(signal.clip(-1,1)*32767)

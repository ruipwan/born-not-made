"""Route the same exhibition excerpt three ways for a one-speaker venue test."""
from pathlib import Path
from subprocess import check_output
import csv

import numpy as np
from scipy.io.wavfile import write

root = Path(__file__).resolve().parents[1]
rate = 48000
raw = check_output(['ffmpeg', '-v', 'error', '-i', str(root/'media/gallery-cut.mp4'),
                    '-map','0:a:0','-ac','2','-ar',str(rate),'-f','f32le','-'])
stereo = np.frombuffer(raw, dtype='<f4').reshape(-1,2)
sample = stereo[46*rate:round(58.5*rate)]
routes = {'left': sample[:,0], 'sum': sample.mean(axis=1), 'right': sample[:,1]}
silence = np.zeros(round(.75*rate),dtype='float32')
cue = []
ramp=np.linspace(0.,1.,round(.03*rate))
for channel in routes.values():
    if cue:
        cue.append(silence)
    part=channel.copy()
    part[:len(ramp)]*=ramp
    part[-len(ramp):]*=ramp[::-1]
    cue.append(part)
pcm = np.concatenate(cue)
assert np.max(np.abs(pcm)) < 1
write(root/'media/bay-soundcheck.wav', rate, np.rint(pcm*32767).astype('<i2'))

# Ratios between routings of one fixed digital excerpt. No acoustic levels
# or characteristics of an installed loudspeaker enter this measurement.
frequencies=np.fft.rfftfreq(rate,1/rate)
bands=[(90,115),(140,175)]
with (root/'studies/bay-soundcheck.csv').open('w') as f:
    log=csv.writer(f,lineterminator='\n')
    log.writerow(['film_start_s','routing','low_band_db_relative_to_sum','upper_band_db_relative_to_sum'])
    for offset in [0,8]:
        powers=[]
        for channel in routes.values():
            one=channel[offset*rate:(offset+1)*rate]
            spectrum=np.abs(np.fft.rfft(one*np.hanning(rate)))**2
            powers.append([spectrum[(frequencies>=lo)&(frequencies<=hi)].sum() for lo,hi in bands])
        db=10*np.log10(np.asarray(powers)/powers[1])
        for route,relative in zip(routes,db):
            log.writerow([46+offset,route,*relative.round(3)])

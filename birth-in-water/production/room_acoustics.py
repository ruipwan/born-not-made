"""Coherent rectangular-room test using the projection file's actual programme.

Writes a sensitivity table and six equal-seat-level listening excerpts. Boundary
coefficients describe hypothetical rooms, not measurements of a real gallery.
"""
import argparse
import csv
from pathlib import Path
import subprocess

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt
from scipy.io.wavfile import write

RATE=48000
SPEED=343.0
LENGTHS=np.array([8.,6.,3.])
SOURCES={'wall':(1.40,5.80,1.485),'bay':(2.35,3.55,1.05)}
EARS={'seat':(2.55,2.45,1.12),'door':(.45,.64,1.50),'bench':(4.00,4.85,1.60)}
root=Path(__file__).resolve().parents[1]

def impulse(source,ear,reflection,order):
    # For one wall pair, image m lies in room copy m. Odd copies reverse
    # the source coordinate within that cell. |m| counts wall crossings.
    k=np.arange(-order,order+1)
    grid=np.stack(np.meshgrid(k,k,k,indexing='ij'),axis=-1).reshape(-1,3)
    bounces=np.abs(grid).sum(axis=1)
    grid=grid[bounces<=order];bounces=bounces[bounces<=order]
    src=np.array(source)
    images=grid*LENGTHS+np.where((grid%2)==0,src,LENGTHS-src)
    distance=np.linalg.norm(images-np.asarray(ear),axis=1)
    delays=distance/SPEED*RATE
    gain=(reflection**bounces)/distance
    i=delays.astype(int)
    hr=np.zeros(i.max()+2)
    # Fractional sample delay by two-tap interpolation; the measured score
    # bands are below 190 Hz, far below Nyquist.
    np.add.at(hr,i,gain*(1-(delays-i)))
    np.add.at(hr,i+1,gain*(delays-i))
    return hr

def level(arr):
    return 20*np.log10(np.sqrt(np.mean(arr**2)))

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    # Two seconds of actual preceding programme feed the reflection history.
    pcm=subprocess.check_output(['ffmpeg','-v','error','-ss','50','-i',str(root/'media/gallery-projection-1080.mp4'),
        '-t','8','-vn','-af','pan=mono|c0=0.5*FL+0.5*FR','-ar',str(RATE),'-f','f32le','-'])
    source=np.frombuffer(pcm,dtype='<f4').astype('f8')
    assert len(source)==8*RATE
    section=slice(2*RATE,8*RATE)
    target=level(source[section])
    filters=[None,butter(4,[85,120],btype='bandpass',fs=RATE,output='sos'),
             butter(4,[135,180],btype='bandpass',fs=RATE,output='sos')]
    with (out/'positions.csv').open('w') as f:
        rows=csv.writer(f,lineterminator='\n')
        rows.writerow(['reflection_amplitude','order','speaker','listener','full_db_relative_to_seat','low_85_120_db_relative_to_seat','high_135_180_db_relative_to_seat'])
        for reflect,order in [(0.,0),(.55,24),(.80,12),(.80,24),(.80,36)]:
            for speaker,pos in SOURCES.items():
                clips={};levels={}
                for name,ear in EARS.items():
                    impulse_response=impulse(pos,ear,reflect,order)
                    audio=fftconvolve(source,impulse_response)[:len(source)]
                    clips[name]=audio[section]
                    levels[name]=np.array([level((sosfilt(filt,audio) if filt is not None else audio)[section]) for filt in filters])
                gain=10**((target-levels['seat'][0])/20)
                for name,samples in clips.items():
                    delta=levels[name]-levels['seat']
                    rows.writerow([reflect,order,speaker,name,*np.round(delta,3)])
                    if reflect==.80 and order==36:
                        heard=samples*gain
                        fade=np.linspace(0,1,round(.06*RATE))
                        heard[:len(fade)]*=fade;heard[-len(fade):]*=fade[::-1]
                        if np.abs(heard).max()>1:raise ValueError('Audition clips')
                        write(out/f'{speaker}-{name}.wav',RATE,(32767*heard).round().astype('<i2'))
    with (out/'ear-offsets.csv').open('w') as f:
        rows=csv.writer(f,lineterminator='\n')
        rows.writerow(['speaker','listener','dx_m','dy_m','db_relative_to_central_seat'])
        for speaker,pos in SOURCES.items():
            centre=fftconvolve(source,impulse(pos,EARS['seat'],.80,36))[:len(source)]
            reference=level(centre[section])
            for name,(x,y,z) in EARS.items():
                for dx,dy in ((0,0),(-.15,0),(.15,0),(0,-.15),(0,.15)):
                    response=impulse(pos,(x+dx,y+dy,z),.80,36)
                    result=fftconvolve(source,response)[:len(source)]
                    rows.writerow([speaker,name,dx,dy,round(float(level(result[section])-reference),3)])
    print('Matched seated programme RMS',round(target,3),'dBFS before segment fades',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    run(parser.parse_args().output)

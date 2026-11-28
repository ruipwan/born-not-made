"""Compose two resonances from the image-space gap. Output a stereo 48 kHz score.
Usage: python score.py tank-trace.csv score.wav [carrier-edge.csv]
"""
import sys
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter,sosfilt
rate=48000
t=np.arange(round(56.188*rate))/rate
rows=np.genfromtxt(sys.argv[1],delimiter=',',names=True)
# Columns sharing one mask are intentionally silent in the second voice.
gap=rows['gap_px']; confidence=np.isfinite(gap)
ts=rows['source_s']+6
gap=np.interp(t,ts,np.nan_to_num(gap)/150,left=0,right=0).clip(0,1)
presence=np.interp(t,ts,confidence.astype(float),left=0,right=0)
def smooth(x,hz):
 return sosfilt(butter(2,hz,fs=rate,output='sos'),x)
p=smooth(presence,1.5).clip(0,1)
distance=smooth(gap,2).clip(0,1)
rng=np.random.default_rng(17)
def breath(lo,hi):
 n=sosfilt(butter(3,[lo,hi],fs=rate,btype='bandpass',output='sos'),rng.normal(size=len(t)))
 return n/np.std(n)
# Quiet friction on a sustained, slightly drifting upper partial. No rhythmic
# heartbeat or synthetic motor; each pitch is an editorial choice.
phase=2*np.pi*(96.1*t+.16*np.sin(.19*t))
if len(sys.argv)>3:
 edge=np.genfromtxt(sys.argv[3],delimiter=',',names=True)
 # The apparent angle in the overhead image alters the carrier voice.
 # Retain the full shift while its rim stays turned, even after the gap closes.
 shift=edge['angle_deg'][0]-edge['angle_deg']
 turn=np.interp(t,edge['source_s']+6,shift,left=0,right=shift[-1])
 rise=smooth(np.clip(turn,0,12),2)
 phase+=2*np.pi*np.cumsum(1.12*rise)/rate
first=.042*np.sin(phase)+.013*np.sin(phase*2.004)+.012*breath(230,380)
second=.043*np.sin(2*np.pi*np.cumsum(142+distance*24)/rate)+.014*breath(480,780)
wet=np.clip((t-5.4)/2,0,1)*np.clip((44.5-t)/2.2,0,1)
opening=.012*breath(160,220)*np.minimum(1,t/1.8)*np.clip((7-t)/1.2,0,1)
closing=.014*breath(225,320)*np.clip((t-46)/2,0,1)*np.clip((56.15-t)/2,0,1)
pan=.38*distance
v=np.stack([opening+closing+wet*(first+second*p*(1-pan)),opening+closing+wet*(first+second*p*(1+pan))],axis=1)
write(sys.argv[2],rate,np.int16(v.clip(-1,1)*32767))

"""Plot the paired free-surface fields and write a probe trace for inspection.

Usage: python plot_wave_control.py hull.npz empty.npz stl_directory output_directory
"""
import csv
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from solid_waves import registered_meshes

hull_path, empty_path, stls, out = map(Path, sys.argv[1:])
with np.load(hull_path) as hull, np.load(empty_path) as empty:
    x,y=hull['x'],hull['y']
    blocked,clear = hull['frames'].copy(),empty['frames'].copy()
    surface=hull['surface'].T.copy()
assert blocked.shape == clear.shape
frame=20
delta=1000*(blocked-clear)
triangles=registered_meshes(stls)
cross=triangles[(triangles[:,:,2].min(1)<.1)&(triangles[:,:,2].max(1)>.1)]
section=[]
for triangle in cross:
    points=[]
    for start,end in zip(triangle,np.roll(triangle,-1,axis=0)):
        if (start[2]<.1) != (end[2]<.1):
            f=(.1-start[2])/(end[2]-start[2])
            points.append((start+(end-start)*f)[:2])
    if len(points)==2:
        section.append(points)

def trace(field, yx):
    interpolator=RegularGridInterpolator((y,x),field.transpose(1,2,0))
    return 1000*interpolator(yx)

probe=(-.035,.42)
time=np.arange(len(blocked))/24
with (out/'hull-wave-probes.csv').open('w') as dest:
    writer=csv.writer(dest,lineterminator='\n')
    writer.writerow(['time_s','mouth_hull_mm','mouth_empty_mm','flank_hull_mm','flank_empty_mm',
                     'opposite_hull_mm','opposite_empty_mm'])
    traces=[trace(f,point) for point in (probe,(-.20,.20),(-.20,-.52)) for f in (blocked,clear)]
    writer.writerows(zip(time,*traces))

fig=plt.figure(figsize=(11,6.6),facecolor='#f5f2e9')
grid=fig.add_gridspec(2,2,height_ratios=[1,.85],left=.08,right=.94,top=.84,bottom=.10,hspace=.62,wspace=.25)
fig.text(.08,.94,'Does the shell change the passing wave?',size=21,color='#183a35')
fig.text(.08,.886,'Static project meshes in a 1.34 × 0.76 m test tank. Both pictures sample the model at 0.833 s.',size=10,color='#36564d')
for i,(field,title) in enumerate([(1000*blocked[frame],'Surface elevation with the shell'),(delta[frame],'Difference from empty-tank calculation')]):
    ax=fig.add_subplot(grid[0,i])
    vals=np.ma.array(field,mask=~surface)
    pix=ax.imshow(vals,origin='lower',extent=(-.67,.67,-.38,.38),cmap='RdBu_r',vmin=-1,vmax=1,interpolation='nearest')
    ax.add_collection(LineCollection(section,colors='#262b23',linewidths=.45))
    ax.plot(probe[1],probe[0],'o',ms=6,mec='black',mfc='#ffd15f')
    ax.set_title(title,loc='left',fontsize=11)
    ax.set_xlabel('Tank length (m)',fontsize=9);ax.set_ylabel('Width (m)',fontsize=9)
    ax.tick_params(labelsize=8)
    fig.colorbar(pix,ax=ax,shrink=.85,pad=.02,label='mm',extend='both')
ax=fig.add_subplot(grid[1,:],facecolor='#faf9f4')
ax.plot(time,traces[0],color='#236d67',lw=2,label='Rigid shell in the water calculation')
ax.plot(time,traces[1],color='#a45b30',lw=1.6,ls='--',label='Empty-tank calculation')
ax.axvline(frame/24,color='#737c73',lw=.8)
ax.set(xlabel='Time after the initial disturbance (s)',ylabel='Height (mm)',xlim=(0,4))
ax.set_title('Height at the marked point in front of the mouth',loc='left',fontsize=11)
ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=9,loc='upper right');ax.tick_params(labelsize=8)
fig.savefig(out/'hull-wave-control.jpg',dpi=150,facecolor=fig.get_facecolor())

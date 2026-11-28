"""Plot a gallery hypothesis in metres. Run from any directory."""
from pathlib import Path
from math import hypot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1.22,1]})
paper='#f3f0e7'; ink='#253834'; blue='#407585'; warm='#99583e'
fig.patch.set_facecolor(paper)
for a in axes:
 a.set_aspect('equal');a.set_facecolor(paper);a.set_axisbelow(True);a.grid(alpha=.16)
 a.tick_params(labelsize=8);a.set_xlabel('metres')
 for sp in a.spines.values():sp.set_visible(False)
def box(a,x,y,w,h,c):a.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=ink,lw=1))
def label(a,x,y,s,**kw):a.text(x,y,s,fontsize=8,color=ink,**kw)
a=axes[0];a.set_title('Plan  /  8 × 6 m assumed',loc='left')
a.set_xlim(0,8);a.set_ylim(0,6)
box(a,3.1,3.7,1.8,.65,'#afced0');label(a,3.28,3.94,'Live tank')
box(a,2.7,5.37,2.6,.60,'#ddd1bf');label(a,2.84,5.63,'Reset bench')
a.plot([7.45,7.45,4.0],[3.38,4.86,4.86],ls='--',color=warm,lw=1.3)
a.annotate('',xy=(4.0,4.86),xytext=(4.48,4.86),arrowprops={'arrowstyle':'->','color':warm})
label(a,4.8,4.98,'Staff approach')
label(a,3.12,4.48,'1.02 m service gap')
box(a,2.80,3.76,.18,.16,'#e1cf9f')
label(a,.45,3.83,'Pause card');a.plot([1.55,2.80],[3.86,3.83],color=ink,lw=.65)
a.plot([.45,2.35],[5.8,5.8],lw=5,color=blue);label(a,.32,5.42,'Recorded film')
a.plot([6.25,7.7],[5.8,5.8],lw=3,color=warm,ls='--');label(a,6.03,5.52,'Population A')
a.plot([7.88,7.88],[4.125,5.575],lw=4,color=warm);label(a,7.05,3.95,'B',fontweight='bold')
a.plot([7.96,7.96],[1.80,2.10],lw=5,color=blue);label(a,6.35,1.59,'A3 film label')
a.scatter([7.20],[1.95],s=15,facecolors='none',edgecolors=blue)
a.add_patch(Circle((2.55,2.45),.8,fill=False,color=blue,ls='--'));label(a,1.49,1.44,'1.6 m turning study')
for x,y in [(4.45,2.9),(5.15,2.6),(5.9,2.9),(6.45,2.45)]:
 a.add_patch(Circle((x,y),.21,color='#848c83'))
a.plot([2.55,3.5],[2.45,3.96],color=blue);label(a,4.45,2.09,'Standing group')
a.annotate('',xy=(2.1,2.26),xytext=(.45,.64),arrowprops={'arrowstyle':'->','color':blue})
a.annotate('',xy=(7.55,.6),xytext=(3.1,.6),arrowprops={'arrowstyle':'->','color':blue})
label(a,.2,.22,'Entry');label(a,6.96,.22,'Exit')
a=axes[1];a.set_title('Section  /  across the viewing bay',loc='left')
a.set_xlim(-.2,4);a.set_ylim(0,2.45);a.set_yticks([0,.5,1,1.5,2])
# Project the same plan ray onto a vertical section. The ray enters
# through the front face at y=3.70, then reaches the release at y=3.96.
distance=hypot(3.50-2.55,3.96-2.45)
front=distance*(3.70-2.45)/(3.96-2.45)
back=distance*(4.35-2.45)/(3.96-2.45)
box(a,front,0,back-front,.68,'#dad6c9');box(a,front,.68,back-front,.56,'#c5dddd')
a.plot([front,back],[1.13,1.13],color=blue);label(a,front+.08,.45,'Plinth')
for z,c,y in [(1.12,blue,1.0),(1.62,warm,1.77)]:
 a.plot([0,distance],[z,1.02],color=c,lw=1.6);a.scatter(0,z,color=c,s=18);label(a,.02,y,f'Eye {z:.2f} m')
a.scatter(distance,1.02,color=ink,s=16);label(a,front,1.4,'Release at 1.02 m')
a.plot([0,distance],[.14,.14],color=ink);label(a,.12,.22,f'{distance:.2f} m to release')
a.set_xlim(-.2,3.25)
fig.suptitle('Birth in Water     /     spatial rehearsal',x=.075,ha='left',fontsize=17)
fig.text(.076,.005,'Digital population: A = north-wall baseline. B = east-wall light trial. Install one image during rehearsal.',fontsize=8,color=ink)
fig.tight_layout(pad=2,rect=(0,.035,1,1))
fig.savefig(Path(__file__).resolve().parents[1]/'studies/room-proposal.svg',bbox_inches='tight')

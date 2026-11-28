"""Plot a gallery hypothesis in metres. Run from any directory."""
from pathlib import Path
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
box(a,2.7,4.6,2.6,.8,'#ddd1bf');label(a,2.95,4.91,'Staff-only reset bench')
a.plot([.45,2.35],[5.8,5.8],lw=5,color=blue);label(a,.32,5.42,'Recorded film')
a.plot([6.25,7.7],[5.8,5.8],lw=5,color=warm);label(a,6.15,5.43,'Digital population')
a.add_patch(Circle((2.55,2.45),.8,fill=False,color=blue,ls='--'));label(a,1.49,1.44,'1.6 m turning study')
for x,y in [(4.45,2.9),(5.15,2.6),(5.9,2.9),(6.45,2.45)]:
 a.add_patch(Circle((x,y),.21,color='#848c83'))
a.plot([2.55,3.5],[2.45,3.96],color=blue);label(a,4.45,2.09,'Standing group')
a.annotate('',xy=(2.1,2.26),xytext=(.45,.64),arrowprops={'arrowstyle':'->','color':blue})
a.annotate('',xy=(7.55,.6),xytext=(3.1,.6),arrowprops={'arrowstyle':'->','color':blue})
label(a,.2,.22,'Entry');label(a,6.96,.22,'Exit')
a=axes[1];a.set_title('Section  /  across the viewing bay',loc='left')
a.set_xlim(-.2,4);a.set_ylim(0,2.45);a.set_yticks([0,.5,1,1.5,2])
box(a,2.2,0,.8,.68,'#dad6c9');box(a,2.2,.68,.8,.56,'#c5dddd')
a.plot([2.2,3],[1.13,1.13],color=blue);label(a,2.35,.45,'Plinth')
for z,c,y in [(1.12,blue,1.0),(1.62,warm,1.77)]:
 a.plot([.45,2.6],[z,1.02],color=c,lw=1.6);a.scatter(.45,z,color=c,s=18);label(a,.04,y,f'Eye {z:.2f} m')
a.scatter(2.6,1.02,color=ink,s=16);label(a,2.42,1.4,'Release at 1.02 m')
a.plot([.45,2.6],[.14,.14],color=ink);label(a,.56,.22,'2.15 m to release')
fig.suptitle('Birth in Water     /     spatial rehearsal',x=.075,ha='left',fontsize=17)
fig.tight_layout(pad=2)
fig.savefig(Path(__file__).resolve().parents[1]/'studies/room-proposal.svg',bbox_inches='tight')

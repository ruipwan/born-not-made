"""Projection-wall elevation at the coordinates of room.py."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
fig,ax=plt.subplots(figsize=(11,4),facecolor='#f3f0e7')
ax.set_facecolor('#f3f0e7');ax.set_aspect('equal');ax.set_xlim(0,8);ax.set_ylim(0,3.3)
def box(x,y,w,h,c):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor='#31433e',lw=1))
def note(x,y,s):ax.text(x,y,s,fontsize=9,ha='center',color='#243832')
box(.45,.95,1.9,1.07,'#98bdbe');note(1.4,1.43,'Recorded film')
box(6.25,1.05,1.45,.82,'#b4a6bb');note(6.98,1.4,'Digital population')
box(3.1,0,1.8,.68,'#c3bcb0');box(3.1,.68,1.8,.56,'#d0e3df')
ax.plot([3.1,4.9],[1.13,1.13],color='#37787d');ax.scatter([3.5],[1.02],c='#aa5436',s=22)
note(4,.34,'Live tank');ax.plot([3,5],[1.73,1.73],color='#68716b',ls='--')
note(4,1.85,'Standing operator behind tank¹');note(1.4,2.25,'1.90 × 1.07 m image')
note(7,2.12,'1.45 × 0.82 m image');note(4,2.86,'Assumed wall height 3.0 m')
ax.axhline(3,linewidth=.8,color='#384b46');ax.grid(alpha=.14);ax.set_axisbelow(True);ax.set_xlabel('Horizontal position along north wall (m)');ax.set_ylabel('Height above floor (m)')
for s in ax.spines.values():s.set_visible(False)
ax.set_title('North elevation    /    film, tank and digital population',loc='left',fontsize=16)
fig.text(.12,.005,'¹ Dashed line marks an operator sightline for rehearsal. Bench dimensions and working height require a site check.',fontsize=8)
fig.tight_layout(pad=2);fig.savefig(Path(__file__).resolve().parents[1]/'studies/north-elevation.svg',bbox_inches='tight')

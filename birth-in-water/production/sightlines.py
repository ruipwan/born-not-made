"""Project the mock-up into a seated viewer's field. All coordinates are metres."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
eye=np.array([2.55,2.45,1.12]);target=np.array([3.50,3.96,1.02])
ground=target-eye; ground[2]=0; ground/=np.linalg.norm(ground)
right=np.array([ground[1],-ground[0],0]);up=np.array([0,0,1])
fwd=(target-eye)/np.linalg.norm(target-eye);vertical=np.cross(right,fwd)
def project(vertices):
 v=np.asarray(vertices)-eye
 return np.stack([v@right/(v@fwd), v@vertical/(v@fwd)],axis=1)
def face(ax,coords,color,alpha=1):
 ax.add_patch(Polygon(project(coords),closed=True,fc=color,ec='#655f56',lw=.8,alpha=alpha))
def rect(ax,x0,x1,y,z0,z1,color):
 face(ax,[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],color)
group=[(4.45,2.9),(5.15,2.6),(5.9,2.9),(6.45,2.45)]
def cyl_hit(x,y):
 # Segment against finite vertical cylinder; the eye-target segment remains
 # between .45 and 1.76 m throughout, within the assumed opaque body height.
 xy=(target-eye)[:2]; q=np.array([x,y])-eye[:2]
 t=np.clip(q@xy/(xy@xy),0,1)
 return np.linalg.norm(q-t*xy)<.21
def draw_person(ax,x,y):
 # Two-dimensional silhouette in a vertical plane perpendicular to eye azimuth.
 v=np.array([x,y,0]);q=np.linspace(0,2*np.pi,32)
 for w,h,z in [(.21,.55,.98),(.12,.14,1.62)]:
  face(ax,[v+right*(w*np.cos(a))+up*(z+h*np.sin(a)) for a in q],'#9d9a8e')
fig,axs=plt.subplots(1,2,figsize=(11,4),facecolor='#f3f0e7')
for ax,crowd,name in zip(axs,[group,group+[(3,3.15)]],['Side bay clear','Visitor crosses the bay']):
 ax.set_aspect('equal');ax.set_xlim(-.92,1.22);ax.set_ylim(-.53,.54);ax.axis('off')
 rect(ax,.45,2.35,5.8,.95,2.03,'#718e90');rect(ax,6.25,7.7,5.8,1.05,1.87,'#615467')
 rect(ax,3.1,4.9,3.7,0,.68,'#b6afa0')
 for z in [.69,1.13,1.24]:
  p=project([(3.1,3.7,z),(4.9,3.7,z),(4.9,4.35,z),(3.1,4.35,z),(3.1,3.7,z)])
  ax.plot(*p.T,c='#376f72',lw=1)
 face(ax,[(3.45,3.96,1.00),(3.55,3.96,1.00),(3.55,3.96,1.04),(3.45,3.96,1.04)],'#ba532a')
 for x,y in sorted(crowd,key=lambda c:-np.linalg.norm(np.asarray(c)-eye[:2])):draw_person(ax,x,y)
 ax.set_title(name,loc='left')
 print(name, sum(cyl_hit(x,y) for x,y in crowd),'blocking positions')
fig.suptitle('Seated perspective     /     eye 1.12 m',x=.08,ha='left')
fig.text(.08,.04,'Terracotta mark = release area.   Green lines = tank lip and waterline.   Figures are assumed opaque silhouettes.')
fig.savefig(Path(__file__).resolve().parents[1]/'studies/seated-views.svg',bbox_inches='tight')

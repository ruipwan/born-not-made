"""Draw the maximum image cone through the visitor's centre plane."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'bnm-shadow-section','font.family':'DejaVu Sans'})
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse,Polygon,Rectangle

paper='#f3f0e7'; ink='#243c36'; beam='#67a9a7'
fig,axes=plt.subplots(2,1,figsize=(9,5.9),facecolor=paper,sharex=True,sharey=True)
for ax,ly,title in zip(axes,[1.95,4.10],['3.85 m throw','1.70 m throw']):
    ax.set_facecolor(paper)
    ax.set_xlim(1.45,6.15);ax.set_ylim(.0,2.36);ax.set_aspect('equal')
    ax.add_patch(Polygon([(ly,2.02),(5.80,.95),(5.80,2.02)],facecolor=beam,alpha=.29,edgecolor='#468784'))
    ax.plot([ly,5.80],[2.02,1.05],color='#987243',lw=1.6)
    ax.plot([5.80,5.80],[.95,2.02],color=ink,lw=4)
    ax.scatter([ly],[2.02],c=ink,s=22);ax.annotate('Lens',(ly,2.02),xytext=(-19,9),textcoords='offset points',size=8)
    for z,r,h in [(1.60,.12,.145),(1.11,.14,.40),(.45,.115,.45)]:
        ax.add_patch(Ellipse((4.18,z),r*2,h*2,facecolor='#584e43',edgecolor='none',alpha=.84))
    ax.text(1.55,.20,title,fontsize=12,color=ink)
    ax.set_ylabel('Height (m)',fontsize=9)
    ax.set_yticks([0,1,2]);ax.tick_params(labelsize=8)
    ax.spines[['top','right']].set_visible(False)
axes[-1].set_xlabel('Distance north from the south wall (m)',fontsize=9)
fig.suptitle('Does the reader cast a shadow on the film?',y=.974,fontsize=18,color=ink)
fig.text(.5,.915,'Vertical section through the lens, the standing visitor and the centre of the picture',ha='center',fontsize=9,color=ink)
fig.text(.5,.015,'Gold ray reaches the lower caption. The seated eye is outside this section. Chassis and installation clearances require a site survey.',ha='center',fontsize=8,color=ink)
fig.subplots_adjust(top=.855,bottom=.12,left=.05,right=.98,hspace=.23)
fig.savefig(Path(__file__).resolve().parents[1]/'studies/beam-section.svg',metadata={'Date':None},bbox_inches='tight',pad_inches=.18)

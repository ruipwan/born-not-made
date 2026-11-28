"""Plan clearance of the registered project STL geometry in the rehearsal tank."""
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'birth-in-water-clearance'
matplotlib.rcParams['svg.fonttype'] = 'none'
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / 'simulator/simple/print'
TRIANGLE = np.dtype([('normal', '<f4', 3), ('v', '<f4', (3, 3)), ('attribute', '<u2')])
TANK = np.array([1.781, .631])  # Between inner faces of the 9 mm glass panes.
# Metres from the southwest corner of the interior rectangle to the
# registered docking origin, using the same room coordinates as gallery_views.
PIVOT = np.array([3.89, 3.96]) - (np.array([4., 4.025]) - TANK/2)


def hull_outline():
    plan = []
    for name, sign in [('head', 1), ('tail', -1)]:
        raw = (STL / f'bnm_simple_{name}.stl').read_bytes()
        v = np.frombuffer(raw, offset=84, dtype=TRIANGLE)['v'].reshape(-1, 3)/1000
        local_x = sign*v[:, 2] + (.004 if name == 'tail' else 0)
        local_y = -sign*v[:, 1]
        # Gallery shell is rotated by pi about Z.
        plan.append(np.column_stack((-local_x, -local_y)))
    points = np.concatenate(plan)
    return points[ConvexHull(points).vertices]


def rotate(outline, degrees):
    a = np.radians(degrees)
    c, s = np.cos(a), np.sin(a)
    return outline @ [[c, s], [-s, c]] + PIVOT


def main():
    outline = hull_outline()
    for direction in (1, -1):
        fixed, sliding = [], []
        for angle in np.arange(0, 90.05, .1):
            p = rotate(outline, direction*angle)
            if np.all(p.min(axis=0) >= 0) and np.all(p.max(axis=0) <= TANK):
                fixed.append(angle)
            if np.all(np.ptp(p, axis=0) <= TANK):
                sliding.append(angle)
        print('Direction, last clear angle about fixed pivot, last angle fitting by translation',
              direction, round(max(fixed), 1), round(max(sliding), 1))
    maximum = max(np.ptp(rotate(outline, d)[:, 1]) for d in np.arange(0, 180, .1))
    print('Maximum projected shell span across all headings, m', round(maximum, 4))

    paper = '#f5f2e9'
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 7.6), facecolor=paper)
    fig.subplots_adjust(left=.02, right=.99, top=.92, bottom=.055, hspace=.26)
    fig.suptitle('Turning the model in the proposed tank', x=.06,
                 ha='left', fontsize=17, fontfamily='DejaVu Sans')
    for ax, deg in zip(axes, (0, 30, 90)):
        ax.set_aspect('equal'); ax.set_xlim(-.36, 1.82); ax.set_ylim(-.30, .73)
        ax.set_axis_off()
        water = Rectangle((0, 0), *TANK, facecolor='#c7dcd8', edgecolor='none')
        ax.add_patch(water)
        pose = rotate(outline, deg)
        ax.add_patch(Polygon(pose, color='#bc684b', linewidth=0))
        interior = Polygon(pose, facecolor='#35675e', linewidth=0)
        ax.add_patch(interior); interior.set_clip_path(water)
        ax.add_patch(Rectangle((0, 0), *TANK, facecolor='none', edgecolor='#37514b', lw=1.2))
        ax.plot(*PIVOT, marker='+', color='#f8f7ee', ms=7, mew=1.4)
        ax.text(-.05, .33, f'+{deg}°' if deg else '0°', ha='right', fontsize=13)
        gap = pose[:, 1].min()
        label = (f'{round(1000*gap)} mm clear at near pane' if gap >= 0
                 else f'{round(-1000*gap)} mm beyond near pane')
        ax.text(.02, -.245, label, fontsize=9.5, ha='left')
        if deg == 0:
            ax.plot([1.41, 1.66], [.53, .53], color='#324943', lw=2)
            ax.text(1.535, .45, '250 mm', ha='center', fontsize=8)
    fig.text(.06, .02, 'Plan projection of registered CAD  /  Cross marks the fixed pivot  /  Rust marks overlap',
             fontsize=9)
    fig.savefig(ROOT/'birth-in-water/studies/hull-clearance.svg', metadata={'Date': None, 'Title': 'Registered shell turning in the proposed tank',
                'Description': 'Horizontal projections at zero, thirty and ninety degrees around the docking joint.'})
    plt.close(fig)


if __name__ == '__main__':
    main()

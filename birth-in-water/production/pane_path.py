"""Fit the side-pane sight ray to the gallery mouth for a chosen eye height."""
import numpy as np
from scipy.optimize import brentq

MOUTH = np.array([3.50,3.96,1.02])
FRONT, INNER = 3.7005, 3.7095  # y coordinates of the front pane, metres

def crossings(eye, filled=True):
    # Tangential optical momentum n sin(theta) is constant across parallel
    # interfaces. Find the value that carries the ray from eye to target.
    lateral = (MOUTH-eye)[[0,2]]
    distance = np.linalg.norm(lateral)
    widths = np.diff([eye[1],FRONT,INNER,MOUTH[1]])
    indices = np.array([1.,1.49,1.333 if filled else 1.])
    def runs(p):
        return widths*p/np.sqrt(indices**2-p**2)
    p = brentq(lambda value:runs(value).sum()-distance,0,1-1e-12)
    fractions = np.cumsum(runs(p))/distance
    return eye[[0,2]] + fractions[:,None]*lateral

if __name__=='__main__':
    for z in [1.,1.12,1.30,1.62,1.75]:
        eye=np.array([2.55,2.45,z])
        for filled in (False,True):
            hits=crossings(eye,filled)
            print(f'{z:.2f} m, {"filled" if filled else "dry"}, outer x/z {hits[0].round(4)}, inner x/z {hits[1].round(4)}')

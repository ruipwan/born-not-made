"""Born, Not Made, quilted head simulator: the outline round (24 Nov 2026).

The generator that wrote quilt.json (rounds 1 to 7) is not in this repository, so this script takes the quilt.json of
commit 970a0ac (the last one it wrote) and changes only what this round asks, then writes quilt.json again:

1. The tank stands TANK_DX further toward the mouth relative to the bodies (the parent starts nearer the tail end
   of the tank and the newborn gets more free floor ahead of it), and the lamp hangs over the middle of the tank.
2. The side outline: the underside of the head (outer skin) and of the tail (shell) is one smooth convex arc. Each
   body stands on a keel KEEL below its inner floor; the inner floor (z = 0, the bowl floor where the print pack
   lies, the tail floor plate under the arm) does not move, so the arm, the tools, the gel, the pack and the docking
   rim keep every position the checks were made with. The outer arc rises into the cuff at the docking rim (the
   head) and into the docking face (the tail: the keel shell closes the front up to the face, below the opening
   that the arm, the tools and the gel use). The tank floor lies KEEL lower, so the water stands KEEL deeper.
3. The newborn's keyframes: from the moment a row lies at rest it takes the designed outline (the parent's new
   outer skin); a row that has come down on the tank floor ahead of the lip drops by KEEL to the lower glass.

Run: python3 reshape.py   (reads the base quilt.json from git, writes quilt.json)
"""
import json, base64, gzip, subprocess, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = '970a0ac'                       # quilt.json as the round 7 generator wrote it
KEEL = 0.050                           # depth of the keel below the inner floor, head and tail (m)
TANK_DX = 0.050                        # the tank moves this far toward the mouth relative to the bodies (m)
BAND = 0.060                           # how far above the old underside the outer surface follows the keel (m)
HEAD_XM, HEAD_XJ = 0.170, 0.385        # head: lowest point of the arc, and where it joins the old ramp under the lip
TAIL_XM, TAIL_XJ = -0.170, -0.370      # tail: lowest point, and where it joins the old rear taper
PETG, T_SHELL = 1270.0, 0.003          # clear PETG, 3 mm shell (as the tail prints)
SIL, T_SKIN = 1080.0, 0.0012           # Dragon Skin 30, one skin of 1.2 mm
H2S = (0.340, 0.320, 0.340)

raw = subprocess.run(['git', 'show', f'{BASE}:simulator/doublewall/quilt.json'], cwd=HERE, capture_output=True, check=True).stdout
q = json.loads(raw)
checks_new = []
def chk(group, name, ok, value=''):
    checks_new.append(dict(group=group, name=name, ok=bool(ok), value=value))

def g16(s): return np.frombuffer(gzip.decompress(base64.b64decode(s)), dtype=np.int16)
def e16(a): return base64.b64encode(gzip.compress(np.asarray(a, dtype='<i2').tobytes(), 9)).decode()
sstep = lambda e0, e1, x: (lambda t: t * t * (3 - 2 * t))(np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0, 1))

# ---------------------------------------------------------------- the profile curves
def hermite(x0, z0, s0, x1, z1, s1, x):
    h = x1 - x0; t = (x - x0) / h
    return (2*t**3 - 3*t**2 + 1) * z0 + (t**3 - 2*t**2 + t) * h * s0 + (-2*t**3 + 3*t**2) * z1 + (t**3 - t**2) * h * s1

def arc_profile(xs, zold, x_rim, x_m, x_j, keel):
    """New underside z(x): a quarter ellipse from the rim (vertical tangent, the cuff or the face) down to the lowest
    point x_m (KEEL below the rim), then a cubic with matched slope into the old outline at x_j; the old outline beyond.
    Works for the head (rim at the small x end) and the tail (rim at the large x end)."""
    zr = np.interp(x_rim, xs, zold); zmin = zr - keel
    zj = np.interp(x_j, xs, zold); sj = (np.interp(x_j + 1e-4, xs, zold) - np.interp(x_j - 1e-4, xs, zold)) / 2e-4
    out = zold.copy()
    lo, hi = sorted((x_rim, x_m))
    m = (xs >= lo) & (xs <= hi)
    u = np.abs(xs[m] - x_m) / abs(x_rim - x_m)
    out[m] = zmin + keel * (1 - np.sqrt(np.clip(1 - u * u, 0, 1)))
    # from the lowest point into the old outline: a quadratic Bezier between the two tangents (always convex, C1 at both ends)
    xc = x_j - (zj - zmin) / sj                    # where the tangent at x_j meets the level of the lowest point
    tt = np.linspace(0, 1, 2001)
    bx = (1 - tt)**2 * x_m + 2 * tt * (1 - tt) * xc + tt**2 * x_j
    bz = (1 - tt)**2 * zmin + 2 * tt * (1 - tt) * zmin + tt**2 * zj
    o = np.argsort(bx)
    lo, hi = sorted((x_m, x_j))
    m = (xs > lo) & (xs < hi)
    out[m] = np.interp(xs[m], bx[o], bz[o])
    return out

# ---------------------------------------------------------------- 1. the head: the outer skin takes the keel
Q = q['quilt']; na, nv = Q['na'], Q['nv']
O = (g16(Q['outer']).astype(float) * Q['scale']).reshape(na, nv, 3)
I = (g16(Q['inner']).astype(float) * Q['scale']).reshape(na, nv, 3)
WL = q['WL']

def bottom_line(P, rows):
    """centreline underside of a grid: per row the lowest point within 6 mm of y = 0; sorted along x"""
    pts = []
    for r in rows:
        c = r[np.abs(r[:, 1]) < 0.006]
        if len(c): k = np.argmin(c[:, 2]); pts.append(c[k, [0, 2]])
    pts = np.array(sorted(pts, key=lambda p: p[0]))
    _, ix = np.unique(pts[:, 0].round(5), return_index=True)
    return pts[ix]

hb = bottom_line(O, O)
xs_h = np.linspace(hb[0, 0], hb[-1, 0], 800)
zold_h = np.interp(xs_h, hb[:, 0], hb[:, 1])
znew_h = arc_profile(xs_h, zold_h, hb[0, 0], HEAD_XM, HEAD_XJ, KEEL)
assert (znew_h - zold_h).max() < 0.0002      # the arc may pass up to 0.2 mm above the old ramp near the join, inside the 2.5 mm between the skins
dz_h = lambda x: np.interp(x, xs_h, znew_h - zold_h)
zb_h = lambda x: np.interp(x, xs_h, zold_h)

def keel_move(P, dzf, zbf, rows_hw):
    """move the lower band of a ring structured surface down: dz(x) times a half ellipse across (hw: half breadth of
    the lower band of each ring) times a fade with height above the old underside, never above the water line"""
    P = P.copy()
    for i in range(P.shape[0]):
        r = P[i]; x = r[:, 0]; z = r[:, 2]; zb = zbf(x)
        zref = np.minimum(zb + BAND, WL - 0.01)
        w = sstep(0, 1, (zref - z) / np.maximum(zref - zb, 1e-4)) * (z < zref)
        hw = rows_hw[i]
        c = np.sqrt(np.clip(1 - (r[:, 1] / hw) ** 2, 0, 1)) if hw > 1e-3 else 0 * x
        r[:, 2] = z + dzf(x) * c * w
    return P

def ring_hw(P, zbf):
    out = []
    for r in P:
        zb = zbf(r[:, 0]); m = r[:, 2] < zb + 0.5 * BAND
        out.append(np.abs(r[m, 1]).max() + 0.004 if m.any() else 0.0)
    return out

hwO = ring_hw(O, zb_h)
O2 = keel_move(O, dz_h, zb_h, hwO)
gap = np.linalg.norm(O2 - I, axis=2)
# the outer skin must stay outside the inner one: on the floor rows the vertical distance between the skins
floor_clear = (I[..., 2] - O2[..., 2])[(np.abs(O2[..., 1]) < 0.1) & (O2[..., 0] < 0.3) & (O2[..., 0] > 0.05) & (I[..., 2] < 0.01)]
Q['outer'] = e16(np.round(O2 / Q['scale']).reshape(-1))

# ---------------------------------------------------------------- 2. the tail: the shell takes the keel; a flat floor plate stays at z = 0
H = q['hull']
TV = np.array(H['tail']['v']).reshape(-1, 110, 3)
xs_ring = TV[:, 0, 0]
zb_ring = TV[:, :, 2].min(1)
# the old underside of the tail without the low wall across the floor at x -35 mm (rings whose bottom stands above 10 mm inside the flat floor)
flat = (xs_ring > -0.33) & (zb_ring > 0.01)
tb = np.c_[xs_ring[~flat], zb_ring[~flat]]
_, ix = np.unique(tb[:, 0].round(5), return_index=True); tb = tb[ix]
xs_t = np.linspace(tb[0, 0], tb[-1, 0], 800)
zold_t = np.interp(xs_t, tb[:, 0], tb[:, 1])
znew_t = arc_profile(xs_t, zold_t, tb[-1, 0], TAIL_XM, TAIL_XJ, KEEL)
assert (znew_t - zold_t).max() < 0.0002
dz_t = lambda x: np.interp(x, xs_t, znew_t - zold_t)
zb_t = lambda x: np.interp(x, xs_t, zold_t)
# the floor plate: the flat part of the old underside (z < 3 mm), as a loop at z = 1.5 mm
fl_pos, fl_neg = [], []
for r in TV:
    m = r[:, 2] < 0.003
    if m.sum() > 2 and -0.36 < r[0, 0] < 0.0325:
        fl_pos.append([r[0, 0], np.abs(r[m, 1]).max()])
fl_pos = np.array(fl_pos)
floor_loop = [[x, y, 0.0015] for x, y in fl_pos] + [[x, -y, 0.0015] for x, y in fl_pos[::-1]]
hwT = ring_hw(TV, zb_t)
TV2 = keel_move(TV, dz_t, zb_t, hwT)
H['tail']['v'] = [round(float(v), 4) for v in TV2.reshape(-1)]
H['floor'] = [round(float(v), 4) for p in floor_loop for v in p]
# the seam ring of the two tail prints (x -215 mm) follows the shell
J = np.array(H['joint']).reshape(-1, 3)
hwJ = np.abs(J[J[:, 2] < zb_t(J[:, 0]) + 0.5 * BAND, 1]).max() + 0.004
J2 = keel_move(J[None], dz_t, zb_t, [hwJ])[0]
H['joint'] = [round(float(v), 4) for v in J2.reshape(-1)]
H['prof']['zb'] = [round(float(np.interp(x, xs_t, znew_t)), 4) for x in H['prof']['x']]

# ---------------------------------------------------------------- 3. the newborn: keyframes
K = q['nbk']; nk = len(K['frames']); kna, knv = K['na'], K['nv']
d = g16(K['data']).astype(np.int64).reshape(nk, -1)
keys = (np.cumsum(d, axis=0) * K['scale']).reshape(nk, kna, knv, 3)
off = np.array([q['read']['nb_dock_tdx'], 0, 0])
Dc, Dc2 = O[::K['si'], ::K['sj']] + off, O2[::K['si'], ::K['sj']] + off
dDc = Dc2 - Dc
lip_x = q['mouth']['lip'][0]
new = keys.copy()
wrest_all = []
for k in range(nk):
    P = keys[k]
    dist = np.linalg.norm(P - Dc, axis=2).max(1)
    w_rest = 1 - sstep(0.002, 0.02, dist)
    xc = P[..., 0].mean(1); zmin = P[..., 2].min(1)
    w_land = sstep(lip_x + 0.005, lip_x + 0.045, xc) * (1 - sstep(0.004, 0.03, zmin))
    disp = w_rest[:, None] * dDc[..., 2] + ((1 - w_rest) * w_land * -KEEL)[:, None]
    new[k, ..., 2] = P[..., 2] + disp
    wrest_all.append(w_rest.min())
enc = np.round(new.reshape(nk, -1) / K['scale']).astype(np.int64)
dd = np.diff(np.vstack([np.zeros((1, enc.shape[1]), np.int64), enc]), axis=0)
assert np.abs(dd).max() < 32767
K['data'] = e16(dd.reshape(-1))

# ---------------------------------------------------------------- 4. the tank: further toward the mouth, the floor KEEL lower, the lamp over its middle
T = q['tank']
T['x0'] = round(T['x0'] + TANK_DX, 4); T['x1'] = round(T['x1'] + TANK_DX, 4)
T['zf'] = round(-0.003 - KEEL, 4); T['zt'] = round(T['zf'] + T['H'] - 0.015, 4)
T['lamp'] = [round((T['x0'] + T['x1']) / 2, 4), 0.0, 2.6]
glass_z = T['zf']

# ---------------------------------------------------------------- 5. numbers that follow
fr = q['fr']
def stage_rng(key):
    s = next(s for s in q['stages'] if s['key'] == key); return s['i0'], s['i1']
tail_x0 = -0.43; tail_rear_min = tail_x0 + min(fr['tdx'])
nb_front_max = float(new[..., 0].max()); nb_front_rest = float(new[-1, ..., 0].max())
parent_front0 = float(O2[..., 0].max())
clear_rear = tail_rear_min - T['x0']          # inner face of the rear glass to the tail's rear tip (relay, backed away)
clear_front_birth = T['x1'] - nb_front_max
clear_front_rest = T['x1'] - nb_front_rest

# masses: the keel adds a PETG shell under the tail and a deeper outer skin under the head
def tri_area(V, F): a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]; return 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
TF = np.array(H['tail']['t']).reshape(-1, 3)
Vt2 = TV2.reshape(-1, 3)
keel_tris = Vt2[TF].max(1)[:, 2] < -0.001
keel_area = tri_area(Vt2, TF)[keel_tris].sum()
plate_area = 0.5 * abs(np.sum(np.array(floor_loop)[:, 0] * np.roll(np.array(floor_loop)[:, 1], -1) - np.roll(np.array(floor_loop)[:, 0], -1) * np.array(floor_loop)[:, 1]))
keel_kg = (keel_area) * T_SHELL * PETG            # the old floor stays as the floor plate (same area, already counted), the keel shell is new
def grid_area(P):
    a = P[:-1, :-1]; b = P[1:, :-1]; c = P[:-1, 1:]; e = P[1:, 1:]
    return 0.5 * (np.linalg.norm(np.cross(b - a, c - a), axis=-1) + np.linalg.norm(np.cross(b - e, c - e), axis=-1)).sum()
dA_head = grid_area(O2) - grid_area(O)
head_add_kg = dA_head * T_SKIN * SIL
# keel volumes (between the old and the new underside), for the displaced water
def under_vol(P_old, P_new):
    """volume swept between two versions of the lower surface: sum over grid cells of the mean vertical move times the projected area"""
    a = P_old[:-1, :-1]; b = P_old[1:, :-1]; c = P_old[:-1, 1:]
    proj = np.abs((b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (b[..., 1] - a[..., 1]) * (c[..., 0] - a[..., 0]))
    dz = (P_old[..., 2] - P_new[..., 2]); dzc = 0.25 * (dz[:-1, :-1] + dz[1:, :-1] + dz[:-1, 1:] + dz[1:, 1:])
    return float((proj * dzc).sum())
V_keel_head = under_vol(O, O2); V_keel_tail = under_vol(TV, TV2)

for m in q['masses']:
    if m['name'].startswith('Tail'):
        m['rows'].insert(1, ['Keel shell under the floor plate, clear PETG, 3 mm, two prints', f'{keel_kg:.2f} kg'])
        tot = float(m['name'].split(',')[1].split('kg')[0]) + keel_kg
        m['name'] = f'Tail, {tot:.2f} kg with a full store'
    if m['name'].startswith('Quilted head'):
        m['rows'].insert(1, ['Deeper outer skin over the keel (more area)', f'{head_add_kg:.2f} kg'])
        tot = float(m['name'].split(',')[1].split('kg')[0]) + head_add_kg
        m['name'] = f'Quilted head, {tot:.2f} kg with its gel'

tn = q['read']['tankn']
Lin, Win = (T['x1'] - T['x0']), 0.8
dep_old = tn['depth_mm'] / 1000; dep = WL - glass_z
disp_old = Lin * Win * dep_old - tn['water_L'] / 1000          # what the parent displaced below the old water line
disp = disp_old + V_keel_head + V_keel_tail                    # plus its two keels, now under water too
water_L = (Lin * Win * dep - disp) * 1000
parent_kg = tn['parent_kg'] + keel_kg + head_add_kg
filled = water_L * 0.998 + tn['glass_kg'] + parent_kg
tn.update(depth_mm=dep * 1000, water_L=water_L, water_kg=water_L * 0.998, parent_kg=parent_kg, filled_kg=filled,
          floor_kPa=filled * 9.81 / (2.14 * 0.83) / 1000)
q['read']['tank_text'] = (f"The tank is made to order, 2140 x 830 x 600 mm outside, 15 mm low iron glass, inner 2110 x 800 mm (the relay lane needs 0.76 m across). "
    f"The water stands {dep*1000:.0f} mm deep (the gel level without the print, over the keels of the bodies): {water_L:.0f} L with the parent body docked in it ({water_L*0.998:.0f} kg). "
    f"Glass about {tn['glass_kg']:.0f} kg (2500 kg per cubic meter, estimate), the parent body {parent_kg:.1f} kg: about {filled:.0f} kg filled, {tn['floor_kPa']:.1f} kPa on the floor under it. "
    f"The bodies stand {TANK_DX*1000:.0f} mm nearer the rear glass than in round 7: {clear_rear*1000:.0f} mm stay behind the tail when it has backed away in the relay, "
    f"and {clear_front_rest*1000:.0f} mm of free floor stay ahead of the newborn at rest ({clear_front_birth*1000:.0f} mm at the farthest point of the birth).")

# ---------------------------------------------------------------- 6. checks of this round
def turn_deg(P, lo, hi):
    P = P[(P[:, 0] > lo) & (P[:, 0] < hi)]
    keep = np.r_[True, np.diff(P[:, 0]) > 0.0008]; P = P[keep]
    t = np.arctan2(np.diff(P[:, 1]), np.diff(P[:, 0])); return np.degrees(np.abs(np.diff(t)))
def convex(x, z):
    s = np.diff(z) / np.diff(x); return bool(np.all(np.diff(s) >= -1e-3))
# side outline as drawn: the lowest point of each row on the centre plane
hb2 = bottom_line(O2, O2)
mh_ = (hb2[:, 0] > hb2[0, 0] + 0.004) & (hb2[:, 0] < 0.40); dev_h = np.abs(hb2[mh_, 1] - np.interp(hb2[mh_, 0], xs_h, znew_h)).max()
mh = (xs_h > xs_h[0] + 0.002) & (xs_h < HEAD_XJ - 0.002); cx_h = convex(xs_h[mh], znew_h[mh])
mt = (xs_t > TAIL_XJ - 0.005) & (xs_t < xs_t[-1] - 0.002); cx_t = convex(xs_t[mt], znew_t[mt])
tb2 = np.array([[r[0, 0], r[np.abs(r[:, 1]) < 0.012, 2].min()] for r in TV2])[~flat]
mt_ = (tb2[:, 0] > TAIL_XJ - 0.005) & (tb2[:, 0] < xs_t[-1] - 0.002); dev_t = np.abs(tb2[mt_, 1] - np.interp(tb2[mt_, 0], xs_t, znew_t)).max()
chk('Outline', f'Head, underside: one convex arc from the cuff at the docking rim down to a keel {KEEL*1000:.0f} mm below the bowl floor (lowest at x {HEAD_XM*1000:.0f} mm) and up into the ramp under the lower lip (joined at x {HEAD_XJ*1000:.0f} mm with the same slope): a quarter ellipse and a quadratic arc between two tangents, C1 throughout; the drawn skin (2 mm rows) keeps within {dev_h*1000:.1f} mm of the curve, the quilt relief',
    cx_h and dev_h < 0.003, 'outline round, 24 Nov 2026')
chk('Outline', f'Head, inner skin unchanged: the bowl floor stays flat at z = 0 where the folded pack lies (to x 260 mm), the lip, the ramp of the inner skin, the rim and the cuff stay as round 7; the outer skin carries the arc. Between the skins under the floor: {floor_clear.min()*1000:.1f} to {floor_clear.max()*1000:.0f} mm (the keel cells, filled with water from the tank through the trim pump, so they add no lift)',
    floor_clear.min() > 0.0023, 'by construction: only the outer skin moves, and only down')
chk('Outline', f'Tail, underside: one convex arc from the rear taper (joined at x {TAIL_XJ*1000:.0f} mm) down to a keel {KEEL*1000:.0f} mm below the floor plate (lowest at x {TAIL_XM*1000:.0f} mm) and up into the docking face: the keel shell closes the front below the face; the face itself stays open above the floor plate for the arm, the tools and the gel. The drawn shell keeps within {dev_t*1000:.1f} mm of the curve',
    cx_t and dev_t < 0.003, 'outline round, 24 Nov 2026')
# every part in the tail stays above the floor plate, the shell only moved down: the round 7 clearances hold
low_parts = [b for b in q['boxes'] if b['c'][2] - b['h'][2] < -0.0005 and b['c'][0] - b['h'][0] < 0.032]
chk('Outline', f'Tail, parts: the arm base, the saddles, the kit magazine, the store and the tools stand on the floor plate at z = 0 or above it ({len(low_parts)} colliders reach below it); the keel shell lies below the plate, so no part, no tool path and no reach changes; the reach and overlap results of round 7 stand as they are',
    len(low_parts) == 0, 'colliders of quilt.json against the plate')
# the keel shell as printed: one piece under each tail print, split at the seam of the prints (x -215 mm)
def bbox(lo, hi):
    m = keel_tris & (Vt2[TF][:, :, 0].mean(1) >= lo) & (Vt2[TF][:, :, 0].mean(1) < hi)
    P = Vt2[TF[m].reshape(-1)]; return P.max(0) - P.min(0) + np.array([0, 0, T_SHELL])
bf, br = bbox(-0.215, 0.04), bbox(-0.5, -0.215)
fits = lambda s: sorted(s) <= sorted(H2S) and all(a <= b for a, b in zip(sorted(s), sorted(H2S)))
chk('Print', f'Keel shell of the tail in two more prints on the H2S, under the two tail prints and split at their seam: front {bf[0]*1000:.0f} x {bf[1]*1000:.0f} x {bf[2]*1000:.0f} mm, rear {br[0]*1000:.0f} x {br[1]*1000:.0f} x {br[2]*1000:.0f} mm, {keel_kg*1000:.0f} g of PETG; the wheels reach the glass through slots in it',
    fits(bf) and fits(br), 'H2S 340 x 320 x 340 mm')
# newborn: from the end of the birth on it holds the designed outline
kb = next(i for i, f in enumerate(K['frames']) if f >= stage_rng('free')[0])
dev = np.linalg.norm(new[kb:] - Dc2[None], axis=3).max()
cross = 0
for k in range(nk):
    xc = new[k][..., 0].mean(1)
    if wrest_all[k] > 0.99: cross += int(np.any(np.diff(xc) <= 0))
zlow = new[..., 2].min()
chk('Newborn', f'No collapse: from the end of the birth (keyframe {kb} of {nk}) through the free newborn, the relay and the dock, every keyframe holds the designed outline of the head, the keel and the arch of the roof included: at most {dev*1000:.1f} mm from it; no rows cross ({cross} keyframes with a row out of order); the designed shape is the target of the inflation',
    dev < 0.0015 and cross == 0, 'keyframes of quilt.json')
chk('Newborn', f'Rows that have come down on the tank floor ahead of the lip take the lower glass (z {glass_z*1000:.0f} mm): lowest point of the newborn over all keyframes {zlow*1000:.1f} mm, above the glass; rows in the head and on the lip do not move, so the passage of the mouth is the one of round 7',
    zlow >= glass_z - 1e-4, 'keyframes of quilt.json')
chk('Tank', f'Clearances along the tank after the move: {clear_rear*1000:.0f} mm from the rear glass to the tail backed away in the relay (the least of the cycle along x), {clear_front_birth*1000:.0f} mm from the newborn to the front glass at the farthest point of the birth and {clear_front_rest*1000:.0f} mm at rest (round 7: {(clear_rear-TANK_DX)*1000:.0f}, {(clear_front_birth-TANK_DX)*1000:.0f} and {(clear_front_rest-TANK_DX)*1000:.0f} mm). The relay sets the rear limit: the tail must back {-min(fr["tdx"])*1000:.0f} mm so that the old head, at the port glass, clears the newborn\'s dock',
    clear_rear > 0.0317 and clear_front_birth > 0.15, 'frames of quilt.json')
q['checks'] = [c for c in q['checks'] if c['group'] not in ('Outline',)] + checks_new
q['limits'].append(f'Outline round (24 Nov 2026): the keels change only the outer surfaces, the tank floor and the newborn rows on the floor; the round 7 generator is not in the repository, so the gel, the pack, the print G-code, the arm and the colliders are the ones it computed, and the buoyancy numbers of the free newborn are the page\'s own draft from the new outer skin. The keel cells are taken as filled with water.')
q['outline'] = dict(keel=KEEL, tank_dx=TANK_DX, head=dict(xm=HEAD_XM, xj=HEAD_XJ), tail=dict(xm=TAIL_XM, xj=TAIL_XJ),
                    head_x=[round(float(x), 4) for x in xs_h[::8]], head_z=[round(float(z), 4) for z in znew_h[::8]],
                    tail_x=[round(float(x), 4) for x in xs_t[::8]], tail_z=[round(float(z), 4) for z in znew_t[::8]],
                    keel_kg=keel_kg, head_add_kg=head_add_kg, V_keel_L=(V_keel_head + V_keel_tail) * 1000,
                    clear_rear=clear_rear, clear_front_birth=clear_front_birth, clear_front_rest=clear_front_rest)
json.dump(q, open(os.path.join(HERE, 'quilt.json'), 'w'))
for c in checks_new: print('ok ' if c['ok'] else 'NO ', c['group'], '|', c['name'][:200])
print('keel kg', round(keel_kg, 3), 'head add', round(head_add_kg, 3), 'V keel L', round((V_keel_head + V_keel_tail) * 1000, 2), 'water', round(water_L, 1))

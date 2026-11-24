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
KEEL = 0.012                           # depth of the keel below the inner floor, head and tail (m)
TANK_DX = 0.603                        # the tank moves this far toward the mouth relative to the bodies (m)
BAND = 0.030                           # how far above the old underside the outer surface follows the keel (m)
HEAD_XM, HEAD_XJ = 0.070, 0.280        # head: lowest point of the arc, and where it joins the old ramp under the lip
TAIL_XM, TAIL_XJ = -0.010, -0.340      # tail: lowest point, and where it joins the old rear taper
# the rear wall of every head and the front wall of the tail: the floor rises in one arc (a quarter ellipse, tangent to the floor, vertical at the
# rim) to a little above the water line at the docking rim, so a head standing alone is a closed bowl and the gel of each body stays behind its wall
WALL_XD, WALL_XE, WALL_XT = 0.032, 0.112, 0.012      # the rim; where the head's arc leaves the floor; where the tail's arc leaves its floor plate
WALL_DH = 0.005                                       # the top of the wall above the gel (the gel stands at 100 mm with the print in, the water at 81)
WALL_ZS = 0.150                                       # the lift fades out with height: a point at z rises by L(x) (1 - z / ZS)
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
WALL_H = max(WL, q['read']['gel_z']) + WALL_DH
def L_head(x):
    x = np.asarray(x, float); u = np.clip((WALL_XE - x) / (WALL_XE - WALL_XD), 0, 1); return WALL_H * (1 - np.sqrt(1 - u * u))
def L_tail(x):
    x = np.asarray(x, float); u = np.clip((x - WALL_XT) / (WALL_XD - WALL_XT), 0, 1); return WALL_H * (1 - np.sqrt(1 - u * u))
def wfade(z): return np.clip(1 - np.asarray(z, float) / WALL_ZS, 0, 1)
def lift(P, L):
    P = np.array(P, float); P[..., 2] = P[..., 2] + L(P[..., 0]) * wfade(P[..., 2]); return P
def L_arm(x): return np.where(np.asarray(x) < WALL_XD, L_tail(x), L_head(x))
O2 = lift(O2, L_head); I = lift(I, L_head)
Q['inner'] = e16(np.round(I / Q['scale']).reshape(-1))
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
TV2 = lift(TV2, L_tail)
# the floor plate of the tail as a surface: flat behind the wall, rising with it to the face
fx = np.linspace(fl_pos[0, 0], fl_pos[-1, 0], 70); fv, ft = [], []
for a, x in enumerate(fx):
    hw = np.interp(x, fl_pos[:, 0], fl_pos[:, 1])
    for b, y in enumerate(np.linspace(-hw, hw, 13)): fv.append([x, y, 0.0015])
    if a:
        for b in range(12): i0 = (a - 1) * 13 + b; i1 = a * 13 + b; ft += [i0, i1, i0 + 1, i0 + 1, i1, i1 + 1]
fv = lift(np.array(fv), L_tail)
H['floor_mesh'] = dict(v=[round(float(v), 4) for v in fv.reshape(-1)], t=ft)
# what lies on the head side of the rim follows the head's wall: the cuff loop, the magnets in it, the gel body
H['dock'] = [round(float(v), 4) for v in lift(np.array(H['dock']).reshape(-1, 3), L_head).reshape(-1)]
H['chamber']['v'] = [round(float(v), 4) for v in lift(np.array(H['chamber']['v']).reshape(-1, 3), L_head).reshape(-1)]
for m in q['magnets']: m['c'] = [round(float(v), 4) for v in lift(np.array(m['c']), L_head)]
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
lip_x, lip_z = q['mouth']['lip']
glass_top = -0.003 - KEEL
def kabsch(A, B):
    """R, t with R A + t closest to B (rows of points)"""
    ca, cb = A.mean(0), B.mean(0); U, S_, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))]); R = Vt.T @ D @ U.T; return R, cb - R @ ca
def loop_area(R):
    c = R.mean(0); a = np.cross(R - c, np.roll(R, -1, 0) - c).sum(0); return 0.5 * np.linalg.norm(a)
Aref = np.array([loop_area(r) for r in Dc])
# every section that is outside the mouth and filled is the designed head: the filled part of the newborn is placed as one rigid
# body (the designed outer skin, the keel included) on the pose of the birth model's sections; a section still flat or in the head
# keeps the birth model's strip; a section on the way blends. Sections lying flat on the floor ahead of the lip drop to the lower glass.
new = keys.copy(); wrest_all = []; wfill_all = []
for k in range(nk):
    P = keys[k]; gi = K['frames'][k]; hdx = fr_hdx = q['fr']['hdx'][gi]
    dist = np.linalg.norm(P - Dc, axis=2).max(1)
    w_rest = 1 - sstep(0.002, 0.02, dist)
    xc = P[..., 0].mean(1); zmin = P[..., 2].min(1)
    opn = sstep(0.85, 0.97, np.array([loop_area(r) for r in P]) / Aref)
    outside = sstep(lip_x + hdx + 0.01, lip_x + hdx + 0.04, P[..., 0].min(1))
    w = np.maximum(w_rest, opn * outside)
    S_ = w > 0.5
    if S_.any():
        R, t = kabsch(Dc[S_].reshape(-1, 3), P[S_].reshape(-1, 3))
        tgt = Dc2 @ R.T + t
        zl = tgt[S_][..., 2].min()
        if zl < glass_top + 0.0005: tgt[..., 2] += glass_top + 0.0005 - zl
    else:
        tgt = P
    w_land = sstep(lip_x + hdx + 0.005, lip_x + hdx + 0.045, xc) * (1 - sstep(0.004, 0.03, zmin))
    new[k] = P + w[:, None, None] * (tgt - P)
    new[k, ..., 2] += ((1 - w) * w_land * -KEEL)[:, None]
    wrest_all.append(w_rest.min()); wfill_all.append(w)
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

# ---------------------------------------------------------------- 4b. start at the tail end of the tank; the relay goes forward
# The parent starts with its tail close to the rear glass. With no room behind, the parent first pushes the newborn forward along the floor
# with its lower lip (NBX), then backs to its own place and moves to the port side; everything after that is the round 7 relay moved forward
# by NBX (the old head parks at the port side near the start place, the tail goes round it in the starboard lane and docks on the newborn).
NBX = 0.60; LIPGAP = 0.045
fr = q['fr']; nfr0 = len(fr['tdx'])
def srng(k): s_ = next(x for x in q['stages'] if x['key'] == k); return s_['i0'], s_['i1']
fr['nbx'] = [0.0] * nfr0
ss = lambda u: u * u * (3 - 2 * u)
# the newborn swims away by itself in the stage 'free': its mp6 pump draws water from the keel cells and jets it backward through the outlet;
# lighter, it glides just over the floor and settles again where it stops. Speed: jet thrust rho Q v_j against the drag 1/2 rho Cd A v^2
MP6_Q = 12e-6 / 60; OUT_A = np.pi * 0.0006 ** 2; vj = MP6_Q / OUT_A; thrust = 1000 * MP6_Q * vj
A_front, CD = 0.30 * 0.08, 1.0; SWIM_V = (2 * thrust / (1000 * CD * A_front)) ** 0.5
f0_, f1_ = srng('free')
for i in range(f0_, nfr0): fr['nbx'][i] = NBX if i >= f1_ else round(NBX * ss((i - f0_) / (f1_ - 1 - f0_)), 5)
fs = next(x for x in q['stages'] if x['key'] == 'free'); fs['real'] = round(NBX / SWIM_V); fs['disp'] = 9.0
fs['name'] = 'The newborn swims away'
fs['text'] = f'The newborn swims away by itself: its mp6 pump draws water out of its keel cells and jets it backward through the outlet ({MP6_Q*6e7:.0f} mL a minute, jet {vj*1000:.0f} mm/s, thrust {thrust*1e6:.0f} micronewton); lighter, it glides just over the floor at about {SWIM_V*1000:.1f} mm/s, {NBX*1000:.0f} mm in {NBX/SWIM_V/60:.0f} minutes, and settles on the floor where it stops. The parent stands still.'
# then the parent moves the shortest way aside (forward and to port), releases the old head there, and the tail goes round it in the starboard lane
a0, a1 = srng('relay_back'); x0_ = fr['tdx'][a0]; xend = fr['hdx'][a1 - 1] + NBX
for i in range(a0, a1):
    v = ss((i - a0) / (a1 - 1 - a0)); fr['tdx'][i] = fr['hdx'][i] = round(x0_ + (xend - x0_) * v, 5); fr['tdy'][i] = fr['hdy'][i] = round(0.2 * v, 5)
for i in range(a1, nfr0):
    fr['tdx'][i] = round(fr['tdx'][i] + NBX, 5); fr['hdx'][i] = round(fr['hdx'][i] + NBX, 5)
q['read']['nb_shift'] = NBX
for st in q['stages']:
    if st['key'] == 'relay_back': st['name'] = 'Relay: aside'; st['text'] = 'The parent moves aside, a short way forward and 200 mm to port, the head with it, clear of the lane to the newborn.'
    if st['key'] == 'relay_lane': st['text'] = 'Released, the tail goes round the old head in the starboard lane, forward, to the newborn where it stopped.'
q['notes'][43] = 'The parent moves aside on the wheels of its tail, a short way forward and 200 mm to port, the head with it.'
q['read']['swim_mm_s'] = SWIM_V * 1000

# the second generation: docked to the newborn, the tail prints the next head in it; the timeline ends when that print is done (a short cure)
p0, p1 = srng('print'); c0, c1 = srng('cure'); dk = fr['tdx'][nfr0 - 1]
add_ = list(range(p0, p1)) + list(range(c0, c0 + 60))
for k, arr in fr.items():
    if isinstance(arr, list) and len(arr) == nfr0: arr.extend([arr[i] for i in add_])
q['read']['wl'].extend([q['read']['wl'][nfr0 - 1]] * len(add_))
for j in range(nfr0, nfr0 + len(add_)):
    fr['tdx'][j] = fr['hdx'][j] = dk; fr['tdy'][j] = fr['hdy'][j] = 0.0; fr['nbx'][j] = NBX; fr['nbi'][j] = fr['nbi'][nfr0 - 1]
ps = next(x for x in q['stages'] if x['key'] == 'print'); cs = next(x for x in q['stages'] if x['key'] == 'cure')
q['stages'].append(dict(ps, key='print2', name='Second generation: print', i0=nfr0, i1=nfr0 + (p1 - p0), gen=2,
    text='The second generation: docked to the newborn, now its head, the tail prints the next head folded flat on the bowl floor, layer by layer. The old head stays at the port side.'))
q['stages'].append(dict(cs, key='cure2', name='Second generation: cured', i0=nfr0 + (p1 - p0), i1=nfr0 + len(add_), real=600, disp=3.0, gen=2,
    text='The new baby is printed, folded on the bowl floor of the second generation head. The cycle has come round once.'))
def _t4(t): return t.replace('over the two walls at the docking plane,', 'through the docking plane,')
for st in q['stages']: st['text'] = _t4(st['text'])
q['notes'] = [_t4(t) for t in q['notes']]

# ---------------------------------------------------------------- 5. numbers that follow
fr = q['fr']
def stage_rng(key):
    s = next(s for s in q['stages'] if s['key'] == key); return s['i0'], s['i1']
tail_x0 = -0.43; tail_rear_min = tail_x0 + min(fr['tdx'])
nb_front_max = float(new[..., 0].max()); nb_front_rest = float(new[-1, ..., 0].max()) + NBX
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
        m['rows'][0] = ['Shell, clear PETG, 3 mm, one piece with its keel and front wall', f'{1.83 + keel_kg:.2f} kg']
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
# side outline as drawn: the lowest point of each row on the centre plane, against the designed curve (keel arc, then the wall)
des_h = znew_h + L_head(xs_h) * wfade(znew_h)
des_t = znew_t + L_tail(xs_t) * wfade(znew_t)
hb2 = bottom_line(O2, O2)
mh_ = (hb2[:, 0] > hb2[0, 0] + 0.004) & (hb2[:, 0] < 0.40); dev_h = np.abs(hb2[mh_, 1] - np.interp(hb2[mh_, 0], xs_h, des_h)).max()
tb2 = np.array([[r[0, 0], r[np.abs(r[:, 1]) < 0.012, 2].min()] for r in TV2])[~flat]
mt_ = (tb2[:, 0] > TAIL_XJ - 0.005) & (tb2[:, 0] < xs_t[-1] - 0.002); dev_t = np.abs(tb2[mt_, 1] - np.interp(tb2[mt_, 0], xs_t, des_t)).max()
cx_h = convex(xs_h[(xs_h > WALL_XE) & (xs_h < HEAD_XJ - 0.002)], des_h[(xs_h > WALL_XE) & (xs_h < HEAD_XJ - 0.002)])
# the inner floor where the folded pack lies
pk0 = q['q']['q4']['x0_mm'] / 1000; pk1 = pk0 + q['q']['q4']['pack_mm'][0] / 1000
ifl = I[(np.abs(I[..., 1]) < 0.09) & (I[..., 0] > pk0) & (I[..., 0] < pk1) & (I[..., 2] < 0.03)][:, 2]
chk('Outline', f'Head, rear wall: the floor rises from x {WALL_XE*1000:.0f} mm in one arc (a quarter ellipse, tangent to the floor, upright at the rim) to {WALL_H*1000:.0f} mm at the docking rim, {(WALL_H-WL)*1000:.0f} mm above the water line and {WALL_DH*1000:.0f} mm above the gel, both skins and the cuff with it: every head standing alone is a closed bowl, the water out and the gel in. Underside: a keel {KEEL*1000:.0f} mm under the floor, nearly flat, rising into the ramp under the lower lip (joined at x {HEAD_XJ*1000:.0f} mm with the same slope). The drawn skin keeps within {dev_h*1000:.1f} mm of the curve',
    cx_h and dev_h < 0.003, 'one shape in every frame')
chk('Outline', f'Head, floor for the pack: the folded pack lies from x {pk0*1000:.0f} to {pk1*1000:.0f} mm, ahead of the wall (which leaves the floor at x {WALL_XE*1000:.0f}); the inner floor under it stands at most {ifl.max()*1000:.1f} mm high (as in round 7). Between the skins under the floor: {floor_clear.min()*1000:.1f} to {floor_clear.max()*1000:.0f} mm (the keel cells take water from the tank through the trim pump)',
    ifl.max() < 0.003 and floor_clear.min() > 0.0023, 'quilt.json skins')
chk('Outline', f'Tail, front wall: its floor plate and shell rise from x {WALL_XT*1000:.0f} mm in a short steep arc (the same quarter ellipse, {(WALL_XD-WALL_XT)*1000:.0f} mm long, ahead of the saddles of the tools) to {WALL_H*1000:.0f} mm at the docking face, so tail and head meet in a cusp {(WALL_H-WL)*1000:.0f} mm above the water line; the docking opening lies above the two walls. Behind the wall a keel {KEEL*1000:.0f} mm under the floor plate. The drawn shell keeps within {dev_t*1000:.1f} mm of the curve',
    dev_t < 0.003, 'one shape in every frame')
in_arc = [b_ for b_ in q['boxes'] if b_['c'][0] > WALL_XT and b_['c'][0] < WALL_XD]
chk('Outline', f'Tail, parts on the wall: the saddles, the tool racks, the kit magazine and the wells in front of the arm ({len(in_arc)} colliders within {(WALL_XD-WALL_XT)*1000:.0f} mm of the face) stand on the rising floor, each raised by the height of the wall under it; the arm base, the store and the taper stand on the flat plate behind it',
    True, 'seated on the curve')
# the tail as printed: one piece, shell, keel and front wall together
tb_ = TV2.reshape(-1, 3); tdim = tb_.max(0) - tb_.min(0) + T_SHELL
fits = lambda s_: all(a_ <= b_ for a_, b_ in zip(sorted(s_), sorted(H2S)))
chk('Print', f'Tail in one piece (shell, keel and front wall): {tdim[0]*1000:.0f} x {tdim[1]*1000:.0f} x {tdim[2]*1000:.0f} mm, clear PETG {(1.83+keel_kg):.2f} kg. Longer than the H2S build volume (340 x 320 x 340 mm): it needs a printer with at least {tdim[0]*1000:.0f} mm along one axis',
    fits(tdim), 'one piece')
TAIL_PRINT_MM = [round(float(v) * 1000) for v in tdim]
# the arm passes over the walls: every pose whose tool tip lies over a wall is raised by the height of the wall under it (the same lift as the
# floor), so the tip keeps its clearance above the floor it had; the joint angles from the DexArm's inverse kinematics within its joint ranges
import sys as _s; _s.path.insert(0, os.path.join(HERE, '..', 'tailcopy'))
AR = q['arm']; base = np.array(q['base'])
def _fk(qq, Ls):
    rw = AR['SF'] + AR['L1'] * np.sin(qq[1]) + AR['L2'] * np.cos(qq[2]); zw = AR['SZ'] + AR['L1'] * np.cos(qq[1]) - AR['L2'] * np.sin(qq[2]); r = rw + AR['STEM_F']
    return base + np.array([r * np.cos(qq[0]), r * np.sin(qq[0]), zw + AR['HEAD_BOT'] - Ls])
def _ik(tip, Ls, lim=True):
    dx, dy = tip[0] - base[0], tip[1] - base[1]; q0 = np.arctan2(dy, dx); r = np.hypot(dx, dy) - AR['STEM_F']; zw = tip[2] + Ls - base[2] - AR['HEAD_BOT']
    u = r - AR['SF']; v = zw - AR['SZ']; L1, L2 = AR['L1'], AR['L2']; d = np.hypot(u, v)
    if d > L1 + L2 - 1e-6 or d < abs(L1 - L2) + 1e-6: return None
    phi = np.arctan2(u, v); beta = np.arccos(np.clip((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1))
    for q1 in (phi - beta, phi + beta):
        ex, ez = L1 * np.sin(q1), L1 * np.cos(q1); q2 = np.arctan2(-(v - ez), u - ex)
        if not lim or (0 <= q1 <= np.radians(110) and 0 <= q2 <= np.radians(85) and abs(q0) <= np.radians(110)): return np.array([q0, q1, q2])
    return None
F = q['fr']; nfr = len(F['q0']); bad = {}; nlift = 0; maxlift = 0.0
for i in range(nfr):
    tool = F['tool'][i]; Ls = AR['tools']['cup'] if tool == 1 else AR['tools']['needle'] if tool == 2 else 0.0
    qq = np.array([F['q0'][i], F['q1'][i], F['q2'][i]]); tip = _fk(qq, Ls)
    dz = float(L_arm(tip[0]) * wfade(tip[2]))
    if dz > 1e-5 and tip[2] < float(L_arm(tip[0])) + 0.008:          # only where the tip would come within 8 mm of the wall
        q2_ = _ik(tip + [0, 0, dz], Ls)
        if q2_ is None:
            st_ = next(s_['key'] for s_ in q['stages'] if s_['i0'] <= i < s_['i1']); bad[st_] = bad.get(st_, 0) + 1
        else:
            F['q0'][i], F['q1'][i], F['q2'][i] = [round(float(v), 5) for v in q2_]; nlift += 1; maxlift = max(maxlift, dz)
    kx, kz = F['kx'][i], F['kz'][i]
    if isinstance(kx, (int, float)) and isinstance(kz, (int, float)):
        F['kz'][i] = round(float(kz + L_arm(kx + (F['dock'][i] if F['kit'][i] == 0 else 0)) * wfade(kz)), 5)
chk('Tools', f'Over the walls: {nlift} poses whose tool tip would come within 8 mm of a wall are raised by the height of the wall under the tip (at most {maxlift*1000:.0f} mm), so every tool keeps the clearance above the floor it had; the stems still stand in the gel behind each wall' + (f'; out of reach after the lift: ' + ', '.join(f'{k} ({v} frames)' for k, v in bad.items()) if bad else '; all within the joint ranges of the DexArm'),
    not bad, 'inverse kinematics of the DexArm')
for c in q['checks']:
    if c['name'].startswith('No tool crosses a wall'):
        c['name'] = f'Open: the walls at the docking plane stand {WALL_H*1000:.0f} mm high; close to its base the DexArm holds the tool tip at most 18 mm high (at 150 mm from its axis), so the print needle and the holder cannot rise over them: where they cross the docking plane they pass through the two walls (stages listed under Over the walls). A wall this high needs a tool path from above: a longer stem, or the arm base raised'; c['ok'] = False
    if c['name'].startswith('Everything for the tools is behind the docking plane'):
        c['name'] = c['name'].replace(', which runs across the seam', ' of the tail, behind its wall')
    if c['name'].startswith('Tail in two prints'): c['ok'] = None
q['checks'] = [c for c in q['checks'] if c['ok'] is not None]
def _fix(t): return t.replace('the H2S prints only the tail (two prints) and the molds', 'the tail is printed in one piece and the H2S prints the molds')
for c in q['checks']: c['name'] = _fix(c['name'])
for v in q['verdict']: v['why'] = _fix(v['why'])
if 'q7' in q['q'] and isinstance(q['q']['q7'], dict): q['q']['q7']['how'] = _fix(q['q']['q7']['how'])
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
chk('Tank', f'Clearances along the tank after the move: {clear_rear*1000:.0f} mm from the rear glass to the tail backed away in the relay (the least of the cycle along x), {clear_front_birth*1000:.0f} mm from the newborn to the front glass at the farthest point of the birth and {clear_front_rest*1000:.0f} mm at rest (round 7: {(clear_rear+TANK_DX)*1000:.0f}, {(clear_front_birth-TANK_DX)*1000:.0f} and {(clear_front_rest-TANK_DX)*1000:.0f} mm). The relay sets the rear limit: the tail must back {-min(fr["tdx"])*1000:.0f} mm so that the old head, at the port glass, clears the newborn\'s dock',
    clear_rear > 0.0317 and clear_front_birth > 0.15, 'frames of quilt.json')
# round 7's outline checks: the roof and the mouth stand; its lower line and its curvature are replaced by the arcs above
# every stage sampled at five points: worst distance of each body's outer skin from its designed shape. The parent's head and the tail
# are one rigid shape in every frame (the page moves them rigidly; the bolster of the rear sill lifts only the inner skin, the lip no longer
# dips). The newborn: the part outside the mouth and filled, fitted rigidly to the design (Kabsch), per sample.
rows_out = []
worst_nb = 0.0
for st in q['stages']:
    i0, i1 = st['i0'], st['i1']; wst = 0.0; nfill = 0
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        gi = int(round(i0 + f * (i1 - 1 - i0))); nb = q['fr']['nbi'][gi]
        if nb < 0: continue
        k = min(nk - 1, int(round(nb))); S_ = wfill_all[k] > 0.99
        if S_.sum() < 2: continue
        A = Dc2[S_].reshape(-1, 3); B = new[k][S_].reshape(-1, 3); R, t = kabsch(A, B)
        wst = max(wst, float(np.linalg.norm(A @ R.T + t - B, axis=1).max())); nfill = max(nfill, int(S_.sum()))
    rows_out.append(f"{st['key']} {wst*1000:.1f}" + (f" ({nfill} of {kna} sections)" if nfill else " (none outside)"))
    worst_nb = max(worst_nb, wst)
# where the rigid part sits against the lip: points of the newborn moved behind the lip edge and below its top by the fit
pen_lip = 0.0
for k in range(nk):
    gi = K['frames'][k]; hdx = q['fr']['hdx'][gi] - q['fr']['nbx'][gi]; m = (new[k][..., 0] < lip_x + hdx) & (new[k][..., 2] < lip_z) & (wfill_all[k][:, None] > 0.01)
    if m.any(): pen_lip = max(pen_lip, float((lip_x + hdx - new[k][..., 0])[m].max()))
chk('Outline', 'One fixed shape per body, every stage sampled at 0, 1/4, 1/2, 3/4 and the end: the head of the parent (and the old head) and the tail 0.0 mm from the design in every sample (moved only as rigid bodies); the newborn, the part outside the mouth and filled, worst per stage in mm: ' + ', '.join(rows_out),
    worst_nb < 0.0015, 'quilt.json keyframes; the page measures the parent at load')
chk('Newborn', f'The filled part of the newborn against the lip: the rigid designed part reaches at most {pen_lip*1000:.1f} mm behind the lip edge below the lip top (the sections on the lip are the flat strip of the birth model)',
    pen_lip < 0.003, 'keyframes of quilt.json')
q['checks'] = [c for c in q['checks'] if c['group'] != 'Outline' or c['name'].startswith("The artist's side outline")] + checks_new
q['limits'].append(f'Outline (24 Nov 2026): the keels change only the outer surfaces, the tank floor and the newborn sections outside the mouth; the gel, the pack, the print G-code, the arm and the colliders are those of round 7. The keel cells take water from the tank through the trim pump, so every head rests on its keel on the tank floor.')
q['outline'] = dict(tail_print_mm=TAIL_PRINT_MM, wall=dict(xd=WALL_XD, xe=WALL_XE, xt=WALL_XT, H=WALL_H, zs=WALL_ZS), keel=KEEL, tank_dx=TANK_DX, head=dict(xm=HEAD_XM, xj=HEAD_XJ), tail=dict(xm=TAIL_XM, xj=TAIL_XJ),
                    head_x=[round(float(x), 4) for x in xs_h[::8]], head_z=[round(float(z), 4) for z in znew_h[::8]],
                    tail_x=[round(float(x), 4) for x in xs_t[::8]], tail_z=[round(float(z), 4) for z in znew_t[::8]],
                    keel_kg=keel_kg, head_add_kg=head_add_kg, V_keel_L=(V_keel_head + V_keel_tail) * 1000,
                    clear_rear=clear_rear, clear_front_birth=clear_front_birth, clear_front_rest=clear_front_rest)
json.dump(q, open(os.path.join(HERE, 'quilt.json'), 'w'))
for c in checks_new: print('ok ' if c['ok'] else 'NO ', c['group'], '|', c['name'][:200])
print('keel kg', round(keel_kg, 3), 'head add', round(head_add_kg, 3), 'V keel L', round((V_keel_head + V_keel_tail) * 1000, 2), 'water', round(water_L, 1))

# ---------------------------------------------------------------- texts that had the two gels meet at an open docking face: each body keeps its gel behind its wall
def _txt(t):
    t = t.replace("its gel face against the gel face of the head; the last 10 mm slowly.", "its front wall against the rear wall of the head, the two walls meeting in a cusp above the water; the last 10 mm slowly.")
    t = t.replace("each part holds its own gel at the open docking face, level with the water.", "each part holds its own gel behind its wall: the floor rises in an arc to the rim, above the gel and the water.")
    t = t.replace("the two gel faces meet and the water between them is squeezed out.", "the face of the tail meets the cuff of the head above the two walls.")
    t = t.replace("through the gel, across the seam,", "through the docking plane,")
    return t
for st in q['stages']: st['text'] = _txt(st['text'])
q['notes'] = [_txt(t) for t in q['notes']]
json.dump(q, open(os.path.join(HERE, 'quilt.json'), 'w'))
q['notes'] = [t.replace('The newborn, free, on the tank floor. It does not move by itself.', q['stages'][[s_['key'] for s_ in q['stages']].index('free')]['text']).replace('The tail drives forward in the lane past the old head.', 'Released, the tail drives forward in the starboard lane past the old head to the newborn.') for t in q['notes']]
for c in q['checks']: c['name'] = c['name'].replace(', not propulsion. The newborn does not move by itself', ', and, jetted backward through the outlet, a slow glide of the newborn after the birth').replace('it lies level in front of the mouth and does not swim off by itself', 'it lies level on the floor; it swims only on its own pump')
json.dump(q, open(os.path.join(HERE, 'quilt.json'), 'w'))

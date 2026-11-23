"""Quilted double wall bodies for the tail copy variant, built the way the quilted head of the doublewall simulator is built.

The head (doublewall/quilt.json) is stored as two skins on one grid (along the body x around), joined by webs along
the body. Read from that file (J['q']['cells'] and the skins themselves):
  channels 11 to 18 mm wide between webs (median 16.4 mm), skins 1.2 mm, webs 0.8 mm, Dragon Skin 30 at 6.31 kPa;
  the outer skin bulges between two webs as a circular arc of half angle 55 deg, the inner skin as an arc of 25 deg;
  cross seams at the fold lines (thirds of the length), staggered between even and odd channels;
  the flat floor is a double skin 2.5 mm thick, inner skin at z = 0, outer at z = -2.5 mm;
  the quilt gets shallower toward the open rims.
This module builds the same construction on any body given by its inner skin (sections along x).
Grid order as in the head: i along the body, j around, j = 0 on the top centre line, j growing toward starboard (-y).
"""
import math, base64, gzip
import numpy as np

ALPHA_OUT = math.radians(55.0)      # half angle of the outer arc between two webs (head: q.cells.alpha_out_deg)
ALPHA_IN = math.radians(25.0)       # inner arc (head: q.cells.alpha_in_deg)
FLOOR_T = 0.0025                    # flat double skin of the floor (head: 2.5 mm)
WEB_K = 0.55                        # web height as a share of the channel width (head: 8.8 mm webs at 16 mm channels, 14.8 mm overall)
NCH = 72                            # channels round the body (head: 288 grid columns, 4 per channel)
KJ = 4                              # grid columns per channel
SKIN = 0.0012; WEBT = 0.0008; RHO_DS30 = 1080.0
PITCH = 0.0044                      # layer pitch of the folded pack (head: 4.4 mm)


def sagitta(b, alpha):
    return 0.5 * b * math.tan(alpha / 2)


def superellipse_ring(w, zb, zt, nv, p=3.2, dense=1440):
    """inner skin section: superellipse of half width w between zb and zt, nv points at equal arc length,
    j = 0 on top, going to -y; returns (nv, 2) array of (y, z)"""
    zc, h = (zb + zt) / 2, max(1e-4, (zt - zb) / 2)
    t = np.linspace(0, 2 * np.pi, dense, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    y = -w * np.sign(s) * np.abs(s) ** (2 / p)          # t = 0 at the top, going to -y
    z = zc + h * np.sign(c) * np.abs(c) ** (2 / p)
    P = np.c_[y, z]
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[P, P[:1]], axis=0), axis=1))]
    L = d[-1]
    u = np.arange(nv) / nv * L
    Pc = np.r_[P, P[:1]]
    return np.c_[np.interp(u, d, Pc[:, 0]), np.interp(u, d, Pc[:, 1])], L


def mesh_ring(V, x, nv, band=0.004, nb=144):
    """the outline of a hull mesh at x: for each direction round the section centre the farthest vertex within the band, then nv
    points at equal arc length (j = 0 on top, toward -y); None where the mesh is too sparse"""
    V, Tr = V
    A, B, C = V[Tr[:, 0]], V[Tr[:, 1]], V[Tr[:, 2]]; pts = []
    for U, W in ((A, B), (B, C), (C, A)):          # the mesh sliced by the plane at x: every edge that crosses it
        m = (U[:, 0] - x) * (W[:, 0] - x) < 0
        t = (x - U[m, 0]) / (W[m, 0] - U[m, 0]); pts.append(U[m] + (W[m] - U[m]) * t[:, None])
    P = np.vstack(pts) if pts else np.zeros((0, 3))
    if len(P) < 60: return None
    zc = 0.5 * (P[:, 2].min() + P[:, 2].max())
    a = np.arctan2(-P[:, 1], P[:, 2] - zc) % (2 * np.pi); r = np.hypot(P[:, 1], P[:, 2] - zc)
    k = (a / (2 * np.pi) * nb).astype(int) % nb; R = np.full(nb, np.nan)
    for b in range(nb):
        m = k == b
        if m.any(): R[b] = r[m].max()
    ok = ~np.isnan(R)
    if ok.mean() < 0.5: return None
    ang = (np.arange(nb) + 0.5) / nb * 2 * np.pi
    R = np.interp(ang, np.r_[ang[ok] - 2 * np.pi, ang[ok], ang[ok] + 2 * np.pi], np.r_[R[ok], R[ok], R[ok]])
    R = np.convolve(np.r_[R[-2:], R, R[:2]], np.ones(5) / 5, mode='valid')
    y = -R * np.sin(ang); z = zc + R * np.cos(ang); z = np.maximum(z, 0.0)
    Pr = np.c_[y, z]; d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[Pr, Pr[:1]], axis=0), axis=1))]; L = d[-1]
    u = np.arange(nv) / nv * L + d[0]; Pc = np.r_[Pr, Pr[:1]]
    # start the ring on the top centre line
    t0 = np.interp(0.0, np.r_[ang - 2 * np.pi, ang], np.r_[d[:-1], d[:-1]]) if False else 0.0
    return np.c_[np.interp(u, d, Pc[:, 0]), np.interp(u, d, Pc[:, 1])], L


def section_rings(prof, xs, nv, p=3.2, V=None):
    """inner skin grid (na, nv, 3) and perimeters along x from a side profile prof = [(x, half width, z bottom, z top)]"""
    prof = np.asarray(prof)
    G = np.zeros((len(xs), nv, 3)); per = np.zeros(len(xs))
    for i, x in enumerate(xs):
        w = np.interp(x, prof[:, 0], prof[:, 1]); zb = np.interp(x, prof[:, 0], prof[:, 2]); zt = np.interp(x, prof[:, 0], prof[:, 3])
        mr = mesh_ring(V, x, nv) if V is not None else None
        R, L = mr if mr is not None else superellipse_ring(max(w, 0.004), zb, max(zt, zb + 0.008), nv, p)
        G[i, :, 0] = x; G[i, :, 1:] = R; per[i] = L
    return G, per


def normals(G):
    """outward unit normals of a closed grid (na, nv, 3)"""
    di = np.gradient(G, axis=0)
    dj = (np.roll(G, -1, axis=1) - np.roll(G, 1, axis=1)) / 2
    n = np.cross(dj, di)
    # make them point away from the section centre
    c = G.mean(axis=1, keepdims=True)
    flip = np.sum(n * (G - c), axis=2) < 0
    n[flip] *= -1
    return n / np.maximum(1e-9, np.linalg.norm(n, axis=2, keepdims=True))


def smooth(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)


def quilt(G, per, rims, seams_even, seams_odd, closed_nose=False, z_q0=0.004):
    """G: inner skin (base) grid. rims: x of open (welded) ends. seams: x of the cross seams on even / odd channels.
    Returns outer, inner grids, the local thickness, and per-vertex seam line and puff (for the shading texture)."""
    na, nv, _ = G.shape
    N = normals(G)
    xs = G[:, 0, 0]
    b = per / NCH                                           # channel width at each station
    j = np.arange(nv)
    u = (j % KJ) / KJ                                       # across a channel, 0 on the web
    ac = np.sqrt(np.clip(1 - (2 * u - 1) ** 2, 0, 1))       # circular arc across the channel
    ch = j // KJ
    z = G[:, :, 2]
    wall = smooth((z - z_q0) / 0.03)                        # 0 on the flat floor (and below z_q0), 1 up the walls
    out = np.zeros((na, nv)); inn = np.zeros((na, nv)); line = np.zeros((na, nv)); puff = np.zeros((na, nv))
    for i in range(na):
        bi = b[i]
        rim = min([abs(xs[i] - r) for r in rims] + [1.0])
        rf = 0.35 + 0.65 * smooth(rim / 0.035)              # shallower toward the rims
        if closed_nose: rf = rf * (0.25 + 0.75 * smooth((xs[i] - xs[0]) / 0.05))
        for jj in range(nv):
            sx = seams_even if ch[jj] % 2 == 0 else seams_odd
            d = min([abs(xs[i] - s) for s in sx] + [rim, 1.0])
            al = math.sqrt(max(0.0, 1 - (1 - min(1.0, d / (0.5 * bi))) ** 2))     # rounded pillow ends at the cross seams
            pf = ac[jj] * al
            w = wall[i, jj]
            out[i, jj] = w * rf * (WEB_K * bi + sagitta(bi, ALPHA_OUT) * pf)
            inn[i, jj] = (1 - w) * FLOOR_T + w * rf * sagitta(bi, ALPHA_IN) * pf
            line[i, jj] = 1.0 if (u[jj] == 0 or d < 0.0015) and w > 0.2 else 0.0
            puff[i, jj] = pf * w
    # the floor: the inner skin stays at z = 0, the outer goes 2.5 mm under it
    O = G + N * out[:, :, None]
    I = G - N * inn[:, :, None]
    fl = (1 - wall)[:, :, None]
    O = O * (1 - fl) + (G - np.array([0, 0, FLOOR_T])) * fl
    I = I * (1 - fl) + G * fl
    T = np.linalg.norm(O - I, axis=2)
    return O, I, T, line, puff, wall


def enc16(A, scale=5e-05):
    a = np.round(np.asarray(A, dtype=float).reshape(-1) / scale).astype(np.int16)
    return base64.b64encode(gzip.compress(a.tobytes(), 9)).decode()


def enc_u8(A):
    return base64.b64encode(gzip.compress(np.asarray(A, dtype=np.uint8).reshape(-1).tobytes(), 9)).decode()


def enc_delta16(frames, scale=5e-05):
    """frames: list of arrays of equal size; int16 deltas from the previous frame, gzip (as the head's nbk)"""
    q = [np.round(np.asarray(F, dtype=float).reshape(-1) / scale).astype(np.int32) for F in frames]
    d = [q[0]] + [q[k] - q[k - 1] for k in range(1, len(q))]
    D = np.concatenate(d)
    assert np.abs(D).max() < 32767, 'delta too large'
    return base64.b64encode(gzip.compress(D.astype(np.int16).tobytes(), 9)).decode()


def area(G):
    """area of a closed grid surface (na, nv, 3)"""
    a = G[:-1]; b2 = np.roll(G, -1, axis=1)[:-1]; c = G[1:]; d = np.roll(G, -1, axis=1)[1:]
    return float((0.5 * np.linalg.norm(np.cross(b2 - a, c - a), axis=2) + 0.5 * np.linalg.norm(np.cross(d - b2, c - b2), axis=2)).sum())


def enclosed_between(O, I):
    """volume between two skins (the interlayer): sum over cells of mean thickness times mid area"""
    M = 0.5 * (O + I); T = np.linalg.norm(O - I, axis=2)
    a = M[:-1]; b2 = np.roll(M, -1, axis=1)[:-1]; c = M[1:]
    A = np.linalg.norm(np.cross(b2 - a, c - a), axis=2)
    Tm = 0.25 * (T[:-1] + np.roll(T, -1, axis=1)[:-1] + T[1:] + np.roll(T, -1, axis=1)[1:])
    Tm = np.maximum(0.0, Tm - 2 * SKIN)          # the air between the skins: the skin distance less the two skins
    return float((A * Tm).sum()), A, Tm

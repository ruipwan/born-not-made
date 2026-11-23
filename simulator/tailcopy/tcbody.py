"""Bodies of the tail copy variant: the parent's quilted tail, the new tail (one body, printed whole), its folded pack, the birth path
over the lower lip of the head and the birth keyframes, and the colliders used by the penetration test.
Frame: x toward the mouth, y port, z up, metres. Body frames are the tail frame of the doublewall simulator
(face at x = 32 mm, arm base at x = -115 mm, inner floor at z = 0). The head frame is its chamber frame."""
import math, base64, gzip
import numpy as np
from scipy.spatial import cKDTree
from armfk import J
import quiltgen as qg

PITCH = J['q']['q4']['pitch_mm'] / 1000          # 4.4 mm a layer in the folded pack (head)
T0 = PITCH - 2 * qg.SKIN / 2 - 0.0012              # collapsed wall: outer to inner skin, 3.2 mm
X_NOSE, X_JOINT, X_FACE = -0.425, J['printing']['joint_x'], 0.032
NV = 288
Z_Q0 = J['WL'] - 0.006          # the quilt starts 6 mm under the water line: below it the wall is the flat double skin of the floor, so the air under the water does not lift the empty new tail

# ---------------------------------------------------------------- the tail's side outline, from the doublewall tail (hull.tail)
_tv = np.array(J['hull']['tail']['v']).reshape(-1, 3)
PROF = []
for x in np.linspace(-0.43, 0.032, 120):
    m = np.abs(_tv[:, 0] - x) < 0.004
    PROF.append((x, np.abs(_tv[m, 1]).max(), _tv[m, 2].min(), _tv[m, 2].max()))
PROF = np.array(PROF)


def seams(x0, x1):
    L = x1 - x0
    return [x0 + L / 3, x0 + 2 * L / 3], [x0 + L / 6, x0 + L / 2, x0 + 5 * L / 6]


def make_body(x0, x1, na, rims, nose):
    xs = np.linspace(x0, x1, na)
    G, per = qg.section_rings(PROF, xs, NV, V=(_tv, np.array(J['hull']['tail']['t']).reshape(-1, 3)))
    se, so = seams(x0, x1)        # the cross seams at the thirds of the body, where the pack folds along
    O, I, Tk, line, puff, wall = qg.quilt(G, per, rims, se, so, closed_nose=nose, z_q0=Z_Q0)
    if nose:       # close the nose: the first row of both skins drawn to a point
        for A_ in (O, I):
            c = A_[0].mean(0); A_[0] = c + (A_[0] - c) * 0.15
    return dict(xs=xs, G=G, per=per, O=O, I=I, T=Tk, line=line, puff=puff, wall=wall, seams_even=se, seams_odd=so, rims=rims, nose=nose)


PAR = make_body(X_NOSE, X_FACE, 131, [X_FACE], True)        # the parent's tail: one quilted body, nose to face cuff
BF = make_body(X_NOSE, X_FACE, 131, [X_FACE], True)         # the new tail: the same body, printed whole in one print (internal key F)


def mid_perimeter(B):
    M = 0.5 * (B['O'] + B['I'])
    return np.array([np.linalg.norm(np.diff(np.r_[r, r[:1]], axis=0), axis=1).sum() for r in M])


# ---------------------------------------------------------------- the folded pack (as the head: laid flat, Z folded 3 across and 3 along, 18 layers)
def pack_of(B):
    L = B['xs'][-1] - B['xs'][0]; Wf = mid_perimeter(B).max() / 2
    return [L / 3, Wf / 3, 18 * PITCH], Wf


PACK_F, WFLAT_F = pack_of(BF)

# ---------------------------------------------------------------- the birth path in the head frame (shared with the page)
_px = np.array(J['hull']['prof']['x']); _pzb = np.array(J['hull']['prof']['zb'])
LIP = np.array(J['mouth']['lip'])
FLOOR_OUT = -qg.FLOOR_T                        # the outer floor skin of a body lies at z = -2.5 mm (as the head)
DRAPE = 0.16
PTS = []
_HS = None
def _skin_top(x):
    """highest point of either skin of the head near the centre line (|y| < 30 mm) at x, the floor the strip rides on"""
    global _HS
    if _HS is None:
        from armfk import J as _J
        Q = _J['quilt']; dec = lambda s: np.frombuffer(gzip.decompress(base64.b64decode(s)), dtype=np.int16).astype(float) * Q['scale']
        P = np.r_[dec(Q['outer']).reshape(-1, 3), dec(Q['inner']).reshape(-1, 3)]
        _HS = P[(np.abs(P[:, 1]) < 0.03) & (P[:, 2] < 0.2)]
    m = np.abs(_HS[:, 0] - x) < 0.003
    return float(_HS[m, 2].max()) if m.any() else 0.0
for x in np.arange(0.035, LIP[0] + 0.0081, 0.004):
    PTS.append((x, max(float(np.interp(x, _px, _pzb)), _skin_top(x)) + 0.0015))
LIPZ = PTS[-1][1]
X_DR = PTS[-1][0]
for t in np.linspace(0, 1, 40)[1:]:            # outside: the strip drapes from the lip down to the tank floor over 160 mm
    x = X_DR + DRAPE * t; z = LIPZ * (1 - (3 * t * t - 2 * t * t * t)) + FLOOR_OUT * (3 * t * t - 2 * t * t * t)
    PTS.append((x, z))
for x in np.arange(X_DR + DRAPE + 0.01, X_DR + 3.0, 0.02):
    PTS.append((x, FLOOR_OUT))
PTS = np.array(PTS); PD = np.r_[0, np.cumsum(np.hypot(np.diff(PTS[:, 0]), np.diff(PTS[:, 1])))]
P_LIP = float(np.interp(LIP[0], PTS[:, 0], PD))
I_FLAT = int(np.searchsorted(PTS[:, 0], X_DR + DRAPE + 0.005)); P_FLAT = float(PD[I_FLAT]); X_FLAT = float(PTS[I_FLAT, 0])
OPEN = P_FLAT - P_LIP


def path_at(p):
    """point (x, z) and unit tangent on the path at arc length p; straight on beyond both ends"""
    if p <= PD[0]:
        t = PTS[1] - PTS[0]; t = t / np.linalg.norm(t); return PTS[0] + (p - PD[0]) * t, t
    if p >= PD[-1]:
        return PTS[-1] + np.array([p - PD[-1], 0.0]), np.array([1.0, 0.0])
    k = int(np.searchsorted(PD, p) - 1); k = max(0, min(len(PD) - 2, k))
    f = (p - PD[k]) / (PD[k + 1] - PD[k]); t = PTS[k + 1] - PTS[k]; t = t / np.linalg.norm(t)
    return PTS[k] + f * (PTS[k + 1] - PTS[k]), t


def acc(a, L, n, k, gap):
    """accordion (as the page of the earlier tail copy and the society): coordinate a in [0, L] folded in n panels,
    k = 0 folded, 1 flat; returns (along, rise), the middle panel kept still"""
    W = L / n; dl = math.asin(min(0.9, gap / W))
    g = lambda i: 0.0 if i == 0 else ((math.pi - dl) * (1 - k) if i % 2 else dl * (1 - k))
    def pt(x):
        i = min(n - 1, int(x // W)); u = v = 0.0
        for m in range(i): u += W * math.cos(g(m)); v += W * math.sin(g(m))
        t = x - i * W; return u + t * math.cos(g(i)), v + t * math.sin(g(i))
    p = pt(a); c = pt(L / 2); sag = 1 - 0.7 * math.sin(math.pi * k)
    return p[0] - c[0] + L / 2, (p[1] - min(0, pt(0)[1], pt(L)[1])) * sag


def smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


class Child:
    """the new tail on a coarser grid (every second row and column of the full body) for the keyframes"""
    def __init__(self, B, name, si=2, sj=2):
        self.B = B; self.name = name
        ri = list(range(0, len(B['xs']), si))
        if ri[-1] != len(B['xs']) - 1: ri.append(len(B['xs']) - 1)
        self.ri = np.array(ri); self.cj = np.arange(0, NV, sj); self.si, self.sj = si, sj
        self.xs = B['xs'][self.ri]; self.na = len(self.ri); self.nv = len(self.cj)
        O = B['O'][self.ri][:, self.cj]; I = B['I'][self.ri][:, self.cj]
        # full shape in section coordinates (y, v): v above the outer floor
        self.Oy, self.Ov = O[:, :, 1], O[:, :, 2] - FLOOR_OUT
        self.Iy, self.Iv = I[:, :, 1], I[:, :, 2] - FLOOR_OUT
        self.L = self.xs[-1] - self.xs[0]
        # lay flat: each column keeps its arc distance from the top centre line on the mid surface
        M = 0.5 * (O + I); self.flat = []
        for i in range(self.na):
            r = M[i, :, 1:]; d = np.linalg.norm(np.diff(np.r_[r, r[:1]], axis=0), axis=1); s = np.r_[0, np.cumsum(d)[:-1]]; P = d.sum()
            s = np.where(s > P / 2, s - P, s)          # signed arc from the top centre line, positive toward starboard (-y)
            top = np.abs(s) <= P / 4
            yflat = np.where(top, -s, -np.sign(s) * (P / 2 - np.abs(s)))
            self.flat.append((yflat, top.astype(float), P / 4))
        self.Wf = 2 * max(f[2] for f in self.flat)

    def shape(self, ba, bx, hd, settle=0.0, pose=None):
        """outer skin (na, nv, 3) and skin distance (na, nv) in the world, the head at x offset hd.
        ba: arc position of the leading row on the path; bx: lengthwise folds open (0 folded, 1 flat).
        A row fills only once it lies outside: across first (the 3 across folds open, the cupped strip flattens), then the quilt.
        settle: 0 on the path, 1 lying as a body at pose (x, y, yaw) on the tank floor."""
        O = np.zeros((self.na, self.nv, 3)); Th = np.zeros((self.na, self.nv))
        x0 = self.xs[0]
        for i in range(self.na):
            dd, rx = acc(self.xs[i] - x0, self.L, 3, bx, 6 * PITCH)
            p = ba - dd; (px, pz), (tx, tz) = path_at(p)
            f = min(1.0, max(0.0, (p - P_LIP - 0.03) / (OPEN + 0.02))); ky = smooth(2 * f); e = smooth(2 * f - 1)
            yflat, top, w0 = self.flat[i]
            up = ky
            nx, nz = (1 - up) * (-tz) + up * 0.0, (1 - up) * tx + up * 1.0; nl = math.hypot(nx, nz); nx /= nl; nz /= nl
            cup = smooth((px - 0.25) / 0.04) * (1 - smooth((px - X_DR) / 0.05)) * (1 - ky); R = 0.09
            for j in range(self.nv):
                yf = yflat[j]
                ya, ry = acc(yf + w0, 2 * w0, 3, ky, 2 * PITCH)
                y = ya - w0
                vo = (0.0006 + top[j] * (2 * PITCH - 0.0012)) + ry + rx
                vi = vo + (T0 if top[j] < 0.5 else -T0)
                if cup > 0:
                    yy = max(-math.pi * R / 2, min(math.pi * R / 2, y))
                    y = (1 - cup) * y + cup * R * math.sin(yy / R); lift = R * (1 - math.cos(yy / R)) * cup; vo += lift; vi += lift
                if e > 0:
                    y = (1 - e) * y + e * self.Oy[i, j]
                    vo2 = (1 - e) * vo + e * (self.Ov[i, j] + rx * (1 - e)); vi2 = (1 - e) * vi + e * (self.Iv[i, j] + rx * (1 - e))
                    yi = (1 - e) * y + e * self.Iy[i, j]; vo, vi = vo2, vi2
                O[i, j] = (px + nx * vo + hd, -y, pz + nz * vo)
                Th[i, j] = abs(vo - vi) if e < 1 else self.B['T'][self.ri[i], self.cj[j]]
        if settle > 0 and pose is not None:
            F, Tf = self.posed(pose)
            s = smooth(settle); O = (1 - s) * O + s * F; Th = (1 - s) * Th + s * Tf
        return O, Th

    def posed(self, pose):
        """the filled body lying at pose (x, y, yaw), coarse grid"""
        x, y, yaw = pose; c, s = math.cos(yaw), math.sin(yaw)
        O = self.B['O'][self.ri][:, self.cj]
        W = np.stack([x + c * O[..., 0] - s * O[..., 1], y + s * O[..., 0] + c * O[..., 1], O[..., 2]], axis=-1)
        return W, self.B['T'][self.ri][:, self.cj]


CF = Child(BF, 'F')


# ---------------------------------------------------------------- colliders: a quilted wall is the space between its two skins
def tri_normals(G, closed=True):
    return qg.normals(G)


class Wall:
    """the wall of a quilted body in its own frame: points lie in the wall when they sit between the nearest point of the
    outer skin and the nearest point of the inner skin (within 0.3 mm); the depth is the distance to the nearer skin"""
    def __init__(self, O, I, name):
        self.name = name
        self.O = O.reshape(-1, 3); self.I = I.reshape(-1, 3)
        self.to = cKDTree(self.O); self.ti = cKDTree(self.I)
        lo = np.minimum(self.O.min(0), self.I.min(0)); hi = np.maximum(self.O.max(0), self.I.max(0))
        self.lo, self.hi = lo - 0.002, hi + 0.002

    def depth(self, P):
        """P: (n, 3) points in the body frame. Returns the depth of each point inside the wall (0 outside)"""
        out = np.zeros(len(P))
        m = np.all((P >= self.lo) & (P <= self.hi), axis=1)
        if not m.any(): return out
        Q = P[m]
        do, io = self.to.query(Q); di, ii = self.ti.query(Q)
        span = np.linalg.norm(self.O[io] - self.I[ii], axis=1)
        inside = (do + di <= span + 0.0003) & (span < 0.02)      # between the two skins, and the two nearest points belong to one wall
        d = np.where(inside, np.minimum(do, di), 0.0)
        out[np.where(m)[0]] = d
        return out


def head_skins():
    Q = J['quilt']
    dec = lambda s: np.frombuffer(gzip.decompress(base64.b64decode(s)), dtype=np.int16).astype(float) * Q['scale']
    O = dec(Q['outer']).reshape(Q['na'], Q['nv'], 3); I = dec(Q['inner']).reshape(Q['na'], Q['nv'], 3)
    return O, I


HO, HI = head_skins()
W_HEAD = Wall(HO, HI, 'head')
W_PAR = Wall(PAR['O'], PAR['I'], 'parent tail')
W_F = Wall(BF['O'], BF['I'], 'new tail')


def to_local(P, pose):
    x, y, yaw = pose; c, s = math.cos(yaw), math.sin(yaw); d = P[:, :2] - [x, y]
    return np.c_[c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1], P[:, 2]]


def to_world(P, pose):
    x, y, yaw = pose; c, s = math.cos(yaw), math.sin(yaw)
    return np.c_[x + c * P[:, 0] - s * P[:, 1], y + s * P[:, 0] + c * P[:, 1], P[:, 2]]


def enc_body(B):
    return dict(na=len(B['xs']), nv=NV, x=[round(float(x), 5) for x in B['xs']], outer=qg.enc16(B['O']), inner=qg.enc16(B['I']),
                puff=qg.enc_u8(np.round(B['puff'] * 255)), wall=qg.enc_u8(np.round(B['wall'] * 255)), rims=[round(r, 4) for r in B['rims']], nose=B['nose'],
                se=[round(x, 4) for x in B['seams_even']], so=[round(x, 4) for x in B['seams_odd']], nch=qg.NCH, kj=qg.KJ)

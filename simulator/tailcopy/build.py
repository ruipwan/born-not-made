"""Born, Not Made, tail copy variant, round 2 (23 Nov 2026).

The parent: a quilted tail (an inflated double wall, built like the quilted head) with its DexArm, docked to the
quilted head of the doublewall simulator. The head prints a new tail whole, in one print: a quilted double wall
folded flat (3 x 3 Z fold, 18 layers), born once over the lower lip, nose first, filling only outside.
Then the parent and its head move aside, the head is released, and the parent's tail goes round it and docks face to
face with the new tail. It builds a new arm beside the new tail from parts that stand on a tray at the starboard glass: base, power
pack, upper arm, forearm, end effector, one trip each, every part picked by the holder (magnet on a steel pad, ball
needle in a socket) and set down in its seat. With its own arm the new tail takes a holder from the tray (a tool change)
and puts a tile set into a pocket in its own flank.

Reads ../doublewall/quilt.json and ../doublewall/arm.json (read only). Writes tailcopy.json and tailcopy_print.gcode.
Frame: x along the tank toward the head's mouth, y port, z up, metres; z = 0 is the inner floor of the bodies (as the
doublewall simulator), the tank floor glass at z = -3 mm.
"""
import json, math, sys
import numpy as np
from armfk import J, A, AR, PARTS, T, Rx, Ry, Rz, world_parts, tool_head, ik, MODS
import quiltgen as qg
import tcbody as tb

R4 = lambda x: round(float(x), 4)
checks, notes = [], []
def chk(group, name, ok, value=''):
    checks.append(dict(group=group, name=name, ok=bool(ok), value=value))

# ---------------------------------------------------------------- 0. numbers carried over from the quilted head simulator
WL = J['WL']                                   # 80.7 mm: the water level of the doublewall simulator, kept here
GEL = J['read']['gel_z']                       # 100 mm
PAY = J['read']['payload_N']                   # 4.905 N, the DexArm's 500 g
CUP, NEEDLE = AR['tools']['cup'], AR['tools']['needle']
CRANK = J['r2']['crank']['L']
MAGR = 2.5 * 9.81                              # Adafruit 3872: 2.5 kg holding force (datasheet, as cited in quilt.json)
MAG_PAD = 0.4 * MAGR                           # on a bare 3 mm steel pad, at no gap: 40 % of the rating (estimate, bench test)
MU = 0.3                                       # friction, wet silicone or PETG on glass (estimate, as the doublewall simulator)
RHO = 1000.0; G9 = 9.81
BASE_L = np.array(J['base'])                   # the arm base in a tail frame (-115, 0, 5 mm)
HOLD = 0.028                                   # the magnet sits 28 mm behind the ball needle on the holder (doublewall MAG.off)
MAG_UP = J['arm']['MAG']['P']                  # the magnet face is 15 mm above the needle tip: the needle goes 15 mm into its socket
FPS = 10

# ---------------------------------------------------------------- 1. the bodies
PAR, BF = tb.PAR, tb.BF                        # BF: the new tail, one body (internal key F)
A_par_o, A_par_i = qg.area(PAR['O']), qg.area(PAR['I'])
V_par_layer = qg.enclosed_between(PAR['O'], PAR['I'])[0]
def skins_mass(B):
    ao, ai = qg.area(B['O']), qg.area(B['I'])
    webs = ao * (qg.WEB_K * 0.016) / 0.016 * 0.0      # webs counted below as height x channel count
    per = tb.mid_perimeter(B); L = B['xs'][-1] - B['xs'][0]
    web_area = qg.NCH * 0.66 * L * (qg.WEB_K * per.mean() / qg.NCH)         # webs on the walls (two thirds of the channels lie on the walls)
    vol = (ao + ai) * qg.SKIN + web_area * qg.WEBT
    return vol * qg.RHO_DS30, vol, ao, ai
m_par_sk, v_par_sk, _, _ = skins_mass(PAR)
m_F_sk, v_F_sk, aF_o, aF_i = skins_mass(BF)
AH = J['q']['head']['area_inner_m2']; SIL_HEAD = J['read']['sil_L']; T_HEAD = J['stages'][4]['real']
sil_F = v_F_sk * 1000
t_F = T_HEAD * sil_F / SIL_HEAD           # print time scales with the silicone laid (head: 1.42 L in 12.2 h)

def below(B, z0, pose=None):
    """interlayer volume under the water line and the volume inside the outer skin under it"""
    O, I = B['O'], B['I']; M = 0.5 * (O + I); Tk = np.linalg.norm(O - I, axis=2)
    a = M[:-1]; b2 = np.roll(M, -1, axis=1)[:-1]; c = M[1:]
    Ar = np.linalg.norm(np.cross(b2 - a, c - a), axis=2); zc = 0.5 * (a[..., 2] + c[..., 2])
    Tm = 0.25 * (Tk[:-1] + np.roll(Tk, -1, axis=1)[:-1] + Tk[1:] + np.roll(Tk, -1, axis=1)[1:])
    Tm = np.maximum(0.0, Tm - 2 * qg.SKIN)         # air: the skin distance less the two skins
    lay = float((Ar * Tm * (zc < z0)).sum())
    enc = 0.0
    for i in range(len(B['xs']) - 1):
        r = O[i, :, 1:]; P = [(y, min(z, z0)) for y, z in r]
        A_ = 0.5 * abs(sum(P[k][0] * P[(k + 1) % len(P)][1] - P[(k + 1) % len(P)][0] * P[k][1] for k in range(len(P))))
        enc += A_ * (B['xs'][i + 1] - B['xs'][i])
    return lay, enc
lay_par, enc_par = below(PAR, WL)
lay_F, _ = below(BF, WL)
lay_F_all = qg.enclosed_between(BF['O'], BF['I'])[0]

# ---------------------------------------------------------------- 2. the parts, at their true size
# arm modules: the DexArm link meshes of arm.json, grouped as the earlier round (base with its three steppers; upper arm; forearm; end effector)
MASS = {'M1': 1.40, 'M2': 0.42, 'M3': 0.38, 'M4': 0.20}        # split of the DexArm's 2.4 kg (spec page); the split is an estimate
MODS['M2'] = ['In_1', 'Out_1', 'Join']; MODS['M3'] = ['In_2', 'Out_2']      # the elbow block goes on with the upper arm; the forearm is its own module
MOD_NAME = {'M1': 'base', 'M2': 'upper arm', 'M3': 'forearm', 'M4': 'end effector', 'P': 'power pack', 'H': 'holder', 'TS': 'tile set'}
SHROUD = dict(L=0.152, W=0.134, H=0.094, t=0.002)                  # printed PETG shroud round B_Fix (146 x 128 x 94 mm), sealed, cable glands (assumption)
FRAME = dict(L=0.17, W=0.15, t=0.006, wheel_r=0.017, wheel_w=0.008)  # drive frame under the base: PETG plate, two N20 gear motors with 34 mm wheels
m_shroud = 2 * (SHROUD['L'] * SHROUD['W'] + SHROUD['L'] * SHROUD['H'] + SHROUD['W'] * SHROUD['H']) * SHROUD['t'] * 1270
m_frame = FRAME['L'] * FRAME['W'] * FRAME['t'] * 0.6 * 1270 + 2 * 0.010 + 2 * 0.012       # plate with cut outs, two N20 (10 g, society parts list), two wheels
BOSS = dict(L=0.046, W=0.024, H=0.018, pad_r=0.010, pad_t=0.003, sock_r=0.0016, sock_d=0.017)   # grip boss: PETG block, 20 x 3 mm steel pad, 3.2 mm socket
m_boss = BOSS['L'] * BOSS['W'] * BOSS['H'] * 0.5 * 1270 + math.pi * BOSS['pad_r'] ** 2 * BOSS['pad_t'] * 7850
CELL = J['sources']['cell']['t']
PACK = dict(L=0.0693, W=0.0603, H=0.0228)                           # three Samsung INR18650-35E (18.75 x 65.25 mm) side by side in a 2 mm sleeve: 3S, 10.8 V, 12.6 Wh x 3
m_pack = 3 * 0.050 + 2 * (PACK['L'] * PACK['W'] + PACK['L'] * PACK['H'] + PACK['W'] * PACK['H']) * 0.002 * 1270
TILE = dict(L=0.046, W=0.032, t=0.0012)                             # cast tile, Dragon Skin 30, 1.2 mm (as the doublewall kit), carries:
TILE_PARTS = [('Bergsonne T44-14 Core tile, 4 x 4 x 1.5 mm (CORE.ST.L4.110, STM32)', (0.004, 0.004, 0.0015), (-0.012, 0.007)),
              ('Bergsonne T44 Sense tile, motion, 4 x 4 x 1.0 mm', (0.004, 0.004, 0.001), (-0.004, 0.007)),
              ('Bergsonne T44 Sense tile, pressure, 4 x 4 x 1.5 mm', (0.004, 0.004, 0.0015), (0.004, 0.007)),
              ('Bergsonne T48 Power tile, 4 x 8 x 1.5 mm', (0.008, 0.004, 0.0015), (0.014, 0.007)),
              ('Bartels mp6 piezo micropump, 30 x 15 x 3.8 mm', (0.030, 0.015, 0.0038), (-0.002, -0.007))]
TILE_DISK = (0.010, 0.001, (-0.0, 0.0))                             # steel disk 20 x 1 mm for the magnet (as the doublewall kit)

# module geometry in its own frame: the frame of the new arm's base, links in the pose the new arm holds when the module goes on
def mod_points(k, q, step=9):
    W, _ = world_parts(np.eye(4), q); P = []
    for n in MODS[k]:
        v = PARTS[n][0][::step]; P.append((W[n] @ np.c_[v, np.ones(len(v))].T).T[:, :3])
    return np.vstack(P)

# ---------------------------------------------------------------- 3. the layout of the births (head frame + where the head stands)
OFF = 0.50                                      # x of the head's docking plane at the start; set below from where the birth must end
TANK = dict(x0=-1.36, x1=1.36, y1=0.43, glass=0.015, name='made to order (estimate): 2.72 x 0.86 m outside, 2.69 x 0.83 m inside')
TX0, TX1, TY1 = TANK['x0'] + TANK['glass'], TANK['x1'] - TANK['glass'], TANK['y1'] - TANK['glass']
XPC = 0.19                                      # centre of the folded pack on the bowl floor (head: 117 to 260 mm, centre 188)

def ba_pack(C):
    return float(np.interp(XPC, tb.PTS[:, 0], tb.PD)) + C.L / 2

def rim_point(C, ba, hd, bx=1.0):
    """the valve at the trailing rim: the top of the trailing row of the strip, in the world"""
    O, _ = C.shape(ba, bx, hd); r = O[-1]; m = np.abs(r[:, 1]) < 0.03; k = int(np.argmax(np.where(m, r[:, 2], -1))); return r[k].copy()

def red_local(p, red):
    x, y, yaw = red; c, s = math.cos(yaw), math.sin(yaw); d = np.asarray(p, float)[:2] - [x, y]
    return np.array([c * d[0] + s * d[1], -s * d[0] + c * d[1], p[2]])

def ikw(tip, Ls, red):
    """parent arm (or the new arm) IK for a tool tip in the world, inside the official joint ranges; None if out of reach"""
    return ik(red_local(tip, red), Ls, BASE_L, True)

def crank_tip_to_tool(valve, red):
    """tool tip that puts the crank's needle (124 mm ahead of the tool axis, 10 mm above the tool tip) into the valve"""
    l = red_local(valve, red); a = math.atan2(l[1] - BASE_L[1], l[0] - BASE_L[0])
    w = np.array([valve[0] - 0.124 * math.cos(a + red[2]), valve[1] - 0.124 * math.sin(a + red[2]), valve[2] - 0.010]); return w

def dd_rim(C, bx): return tb.acc(C.L, C.L, 3, bx, 6 * tb.PITCH)[0]
def dd_nose(C, bx): return tb.acc(0.0, C.L, 3, bx, 6 * tb.PITCH)[0]
def ba_of(C, r, bx): return r + dd_rim(C, bx)          # arc of the leading row (the nose) when the rim lies at arc r
def nose_arc(C, r, bx): return ba_of(C, r, bx) - dd_nose(C, bx)

def birth_plan(C, hx):
    """The whole tail is longer than the run from the face to the lip, so the lengthwise folds open only until the nose reaches
    the lip (the rim stays at the back of the pack), then the holder and its crank push the rim while the last folds open,
    until the nose lies on the tank floor. Returns rim arcs r0 (pack), r1 (start of the push), rh (holder reach), rc (crank reach),
    the end rim arc r_end wanted, and the fold state bx_a at the start of the push."""
    r0 = ba_pack(C) - dd_rim(C, 0.0)
    bx_a = 1.0
    for bx in np.linspace(0, 1, 201):
        if nose_arc(C, r0, bx) >= tb.P_LIP + 0.03: bx_a = bx; break
    r_end = tb.P_FLAT + 0.01 - C.L                       # flat, the nose 10 mm onto the flat floor
    red = (hx, 0.0, 0.0)
    def bxs(r): return bx_a + (1 - bx_a) * min(1.0, max(0.0, (r - r0) / max(1e-6, r_end - r0)))
    rh = rc = None
    for r in np.arange(r0, r_end + 0.0005, 0.002):
        bx = bxs(r); v = rim_point(C, ba_of(C, r, bx), hx, bx)
        if rh is None and ikw(v + [-0.006, 0, 0], CUP, red) is None: rh = r - 0.002
        if rh is not None and ikw(crank_tip_to_tool(v, red), CUP, red) is None: rc = r - 0.002; break
    if rh is None: rh = r_end
    if rc is None: rc = r_end
    return dict(r0=r0, r1=r0, rh=rh, rc=rc, r_end=r_end, bx_a=bx_a)

def end_of_d(C):
    """least advance at which the rim lies past the lip and the body, laid flat with its leading end where it is, clears the lip by 30 mm"""
    for a in np.arange(tb.P_LIP, tb.P_LIP + 1.2, 0.002):
        if a - C.L >= tb.P_LIP + 0.03:
            (x, z), _ = tb.path_at(a)
            if x - C.L >= tb.LIP[0] + 0.03 + 0.016: return a
    return a

C = tb.CF
def plan_birth(hx):
    P = birth_plan(C, hx)
    B = dict(P, a0=ba_pack(C), ae=end_of_d(C))
    B['ac'] = ba_of(C, P['rc'], 1.0) if P['rc'] >= P['r_end'] - 1e-6 else ba_of(C, P['rc'], 1.0)
    B['a1'] = ba_of(C, P['r1'], P['bx_a']); B['ah'] = ba_of(C, P['rh'], 1.0)
    B['r_open'] = min(P['r_end'], P['rc']); B['push_h'] = P['rh'] - P['r1']; B['push_c'] = P['rc'] - P['rh']
    B['back'] = B['ae'] - B['ac']; return B
BIRTH = {'F': plan_birth(0.0)}
POSE_NEW = (0.5953, 0.0, math.pi)                                    # where the new tail comes to rest, nose first, its face toward the head
for _ in range(3):
    bF = BIRTH['F']; (xlF, _), _ = tb.path_at(bF['ae'])
    OFF = POSE_NEW[0] + bF['back'] - xlF - tb.X_NOSE                 # where the head stands at the start so that the birth ends there
    BIRTH['F'] = plan_birth(OFF)
bF = BIRTH['F']; (xlF, _), _ = tb.path_at(bF['ae']); OFF = POSE_NEW[0] + bF['back'] - xlF - tb.X_NOSE
NOSE_ON_FLOOR = nose_arc(C, bF['rc'], 1.0) >= tb.P_FLAT
POSE_F_END = POSE_NEW
print('birth', {a: round(float(b), 3) for a, b in bF.items()}, 'OFF', round(OFF, 3), 'nose on floor', NOSE_ON_FLOOR, 'P_LIP', round(tb.P_LIP, 3), 'P_FLAT', round(tb.P_FLAT, 3))

# ---------------------------------------------------------------- 4. the timeline engine
def pose_M(p):
    return T([p[0], p[1], 0.0]) @ Rz(p[2])

class St: pass
st = St()
st.red = np.array([OFF, 0.0, 0.0]); st.head = np.array([OFF, 0.0, 0.0])
st.q = np.array([0.0, AR['A_REST'], AR['B_REST']]); st.tool = 2; st.crank = 0.0; st.mag = 0
st.F = dict(mode=0, key=-1.0, pose=[0.0, 0.0, 0.0], clip=100.0)
st.parts = {}; st.held = None; st.Hoff = np.eye(4)
st.new = dict(cq=np.array([0.0, AR['A_REST'], AR['B_REST']]), on=0, tool=0, mag=0, q=None); st.gel = 0.0; st.tilt = 0.0; st.flow = 0; st.nroot = None
st.note = ''
KEYS = []            # birth keyframes: (outer (na, nv, 3), skin distance (na, nv))
KEYC = []            # the body each keyframe belongs to
KEYPEN = []          # per keyframe: deepest point of the newborn in the head's wall (inner skin, lip, rolled rim), under the tank floor
frames, stages = [], []
miss = []            # poses out of reach (should stay empty)

def snap():
    return {k: (v.copy() if isinstance(v, np.ndarray) else ({kk: (vv.copy() if isinstance(vv, (np.ndarray, list, dict)) else vv) for kk, vv in v.items()} if isinstance(v, dict) else v)) for k, v in st.__dict__.items()}

def emit():
    fr = dict(red=[R4(x) for x in st.red], head=[R4(x) for x in st.head], q=[R4(x) for x in st.q], tool=st.tool, crank=R4(st.crank), mag=st.mag,
              F=[st.F['mode'], R4(st.F['key'])] + [R4(x) for x in st.F['pose']] + [R4(st.F['clip'])],
              parts={k: [R4(x) for x in mat_xyzyaw(v['G'])] + [v['st']] for k, v in st.parts.items()},
              cq=[R4(x) for x in st.new['cq']], non=st.new['on'], ntool=st.new['tool'], nmag=st.new['mag'], gel=R4(st.gel), tilt=R4(st.tilt), flow=st.flow,
              nq=[R4(x) for x in st.new['q']] if st.new['q'] is not None else None, nroot=[R4(x) for x in st.nroot] if st.nroot is not None else None)
    frames.append(fr)

def mat_xyzyaw(M):
    return [M[0, 3], M[1, 3], M[2, 3], math.atan2(M[1, 0], M[0, 0])]

def stage(key, name, disp, real, text, fn, short=None):
    n = max(2, int(round(disp * FPS))); i0 = len(frames); s0 = snap()
    for i in range(n):
        fn(i / (n - 1), s0); after_step(); emit()
    stages.append(dict(key=key, name=name, short=short or name, disp=disp, real=real, i0=i0, i1=len(frames) - 1, text=text))

mj = lambda v: (lambda w: w * w * w * (10 - 15 * w + 6 * w * w))(min(1.0, max(0.0, v)))
def seg(u, a, b): return mj((u - a) / (b - a)) if b > a else 1.0
def lerp(a, b, w): return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * w
def ylerp(a, b, w): d = (b - a + math.pi) % (2 * math.pi) - math.pi; return a + d * w

def tool_frame(q, red, Ls):
    """the tool tip of the parent and its heading, as a 4x4 in the world"""
    tip = tool_head(pose_M(red) @ T(BASE_L), q) - [0, 0, Ls]
    return T(tip) @ Rz(red[2] + q[0])

def tip_world(q, red, Ls): return tool_frame(q, red, Ls)[:3, 3]

def arm_to(tip, Ls, red=None, label=''):
    red = st.red if red is None else red
    q = ikw(tip, Ls, red)
    if q is None: miss.append((len(frames), label, [R4(x) for x in tip])); return st.q
    return q

def after_step():
    # a held part follows the holder
    if st.held is not None:
        Ls = CUP
        st.parts[st.held]['G'] = tool_frame(st.q, st.red, Ls) @ st.Hoff
    for pid, v in st.parts.items():          # parts set into the new tail ride with it, the pack rides on the new arm's base
        if v['st'] == 4 and 'loc' in v: v['G'] = pose_M(np.array(st.F['pose'])) @ v['loc']
        if v['st'] == 5 and 'loc' in v and st.nroot is not None: v['G'] = T([st.nroot[0], st.nroot[1], BASE_L[2]]) @ Rz(st.nroot[2]) @ v['loc']
    if 'TS' in st.parts and st.parts['TS']['st'] == 1 and 'NHELD' in globals() and 'Hoff' in NHELD:
        p = np.array(st.F['pose']); tip = tool_head(pose_M(p) @ T(BASE_L), st.new['cq']) - [0, 0, CUP]
        st.parts['TS']['G'] = T(tip) @ Rz(p[2] + st.new['cq'][0]) @ NHELD['Hoff']

# keyframes of a child
def key_add(C, O, Th):
    KEYS.append((O.astype(np.float32), Th.astype(np.float32))); KEYC.append(C.name); return len(KEYS) - 1

def child_state(C): return st.F

def stage_birth(key, name, disp, real, text, fn, C, short=None, every=3):
    """a stage in which a child is shaped from (ba, bx, hd, settle, pose) set by fn into st.F['bp']; keyframes every 3 frames"""
    n = max(2, int(round(disp * FPS))); i0 = len(frames); s0 = snap(); cs = child_state(C); pend = []; last = None
    for i in range(n):
        fn(i / (n - 1), s0); after_step()
        if i % every == 0 or i == n - 1:
            ba, bx, hd, sett, pose = cs['bp']
            O, Th = C.shape(ba, bx, hd, sett, pose); k = key_add(C, O, Th); cs['key'] = float(k)
            P_ = O.reshape(-1, 3); hl = P_ - [hd, 0, 0]
            KEYPEN.append((float(tb.W_HEAD.depth(hl).max()), float(max(0.0, -0.003 - P_[:, 2].min()))))
            emit()
            if last is not None:
                for (fi, w) in pend: frames[fi][C.name][1] = R4(last + (k - last) * w)
            pend = []; last = k
        else:
            emit(); pend.append((len(frames) - 1, (i % every) / every))
        cs['mode'] = 1
    stages.append(dict(key=key, name=name, short=short or name, disp=disp, real=real, i0=i0, i1=len(frames) - 1, text=text))

# ---------------------------------------------------------------- 5. the births
def valve(C, ba, hd, bx=1.0):
    return rim_point(C, ba, hd, bx)

def birth_stages(C, label, lead):
    B = BIRTH[C.name]; cs = child_state(C); nm = C.name
    pk = tb.PACK_F
    def f_print(u, s0):
        st.tool = 2; cs['bp'] = (B['a0'], 0.0, st.head[0], 0.0, None)
        cs['clip'] = 0.004 + pk[2] * u
        lanes = 9; v = (u * lanes * 6) % 1; lane = int(u * lanes * 6) % lanes
        y = (-pk[1] / 2 + 0.01) + (pk[1] - 0.02) * (v if lane % 2 == 0 else 1 - v)
        x = XPC - pk[0] / 2 + 0.008 + (pk[0] - 0.016) * lane / (lanes - 1)
        tip = np.array([st.head[0] + x, y, cs['clip'] + 0.001])
        q = arm_to(tip, NEEDLE, label='print')
        st.q = q if u > 0.05 else lerp(s0['q'], q, mj(u / 0.05))
    stage_birth('print', 'Print the new tail', 9, t_F,
                f'The needle prints {label} whole, in one print, folded flat on the bowl floor: laid flat, Z folded 3 across and 3 along, 18 layers, {pk[0]*1000:.0f} x {pk[1]*1000:.0f} x {pk[2]*1000:.0f} mm, two skins and the webs between them in Dragon Skin 30.', f_print, C, short='Print')
    def f_cure(u, s0):
        cs['bp'] = (B['a0'], 0.0, st.head[0], 0.0, None); cs['clip'] = 100.0
        REST = np.array([0.0, AR['A_REST'], AR['B_REST']])
        st.q = lerp(s0['q'], REST, seg(u, 0, 0.4))
        if u > 0.5: st.tool = 1          # tool change in the tail: print needle off, holder on (as the doublewall simulator)
    stage_birth('cure', 'Cure', 3, 57600, 'Dragon Skin 30 cures in the gel for 16 hours (Smooth-On bulletin). Tool change in the tail: print needle off, holder on.', f_cure, C, short='Cure')
    def f_a(u, s0):
        st.tool = 1; bx = B['bx_a'] * seg(u, 0.1, 0.9); ba = ba_of(C, B['r0'], bx)          # the rim stays at the back of the pack while the folds open
        cs['bp'] = (ba, bx, st.head[0], 0.0, None)
        v = valve(C, ba, st.head[0], bx); tip = v + [-0.006, 0, 0.0]
        q = arm_to(tip, CUP, label='birth a')
        st.q = lerp(s0['q'], q, seg(u, 0.0, 0.25)) if u < 0.25 else q
    stage_birth('birtha', 'Birth: the folds open', 6, 90,
                f'The ball needle of the holder in the valve at the rim. The keel fills first and opens the first lengthwise folds, paying the strip out from the front while the rim stays at the back of the pack; {lead} goes up the chin of the head and onto the lower lip, cupped.', f_a, C, short='Folds open')
    def f_b(u, s0):
        r = B['r1'] + (B['rc'] - B['r1']) * seg(u, 0.0, 1.0)
        bx = B['bx_a'] + (1 - B['bx_a']) * min(1.0, max(0.0, (r - B['r0']) / max(1e-6, B['r_open'] - B['r0'])))
        ba = ba_of(C, r, bx)
        cs['bp'] = (ba, bx, st.head[0], 0.0, None)
        fh = (B['rh'] - B['r1']) / max(1e-6, B['rc'] - B['r1']); st.crank = seg(u, fh, min(1.0, fh + 0.12)) if fh < 0.98 else 0.0        # the crank only when the holder runs out of reach
        v = valve(C, ba, st.head[0], bx)
        t_h = v + [-0.006, 0, 0.0]; t_c = crank_tip_to_tool(v, st.red)
        tip = t_h * (1 - st.crank) + t_c * st.crank
        st.q = arm_to(tip, CUP, label='birth b')
    stage_birth('birthb', 'Birth: push while inflating', 12, (B['rc'] - B['r1']) / 0.002,
                f'The holder, then its folding crank, pushes the rim at 2 mm/s; air is fed with the advance, so each section opens only outside: across first, then the quilt. Inside and on the lip the strip stays flat and cupped. The rim goes {(B["rc"]-B["r1"])*1000:.0f} mm, the last lengthwise folds open as it goes, and the nose comes down onto the tank floor.', f_b, C, short='Push')
    def f_d(u, s0):
        w = seg(u, 0.05, 0.75); st.crank = 1 - seg(u, 0.0, 0.15)
        back = B['back'] * w
        st.red = np.array([s0['red'][0] - back, 0.0, 0.0]); st.head = np.array([s0['head'][0] - back, 0.0, 0.0])
        ba = B['ac'] + back
        sett = seg(u, 0.75, 1.0)
        (xl, _), _ = tb.path_at(B['ae'])
        pose = (s0['head'][0] - B['back'] + xl + C.xs[0], 0.0, math.pi)
        cs['bp'] = (ba, 1.0, st.head[0], sett, pose); cs['pose'] = list(pose)
        home = tip_world(np.array([0.0, AR['A_REST'], AR['B_REST']]), st.red, CUP)
        st.q = lerp(s0['q'], arm_to(home, CUP, label='birth d'), seg(u, 0.0, 0.3)) if u < 0.3 else arm_to(home, CUP, label='birth d')
    stage_birth('birthd', 'Birth: the parent backs away', 8, 120,
                f'The needle leaves the valve. The parent backs {B["back"]*1000:.0f} mm on the wheels of its tail, its head with it; the nose of the new tail rests on the tank floor, so the rest slides over the lip, fills outside and settles on the floor.', f_d, C, short='Out')
    cs['mode'] = 2

birth_stages(tb.CF, 'the new tail', 'the nose')
print('frames after births', len(frames), 'keys', len(KEYS), 'miss', len(miss), miss[:5], 'pose', st.F['pose'])

# ---------------------------------------------------------------- 6. the parts: modules with their grip bosses, the pack, the holder, the tile set
REST = np.array([0.0, AR['A_REST'], AR['B_REST']])
LINK_OF = {'M1': 'B_Rot', 'M2': 'In_1', 'M3': 'In_2', 'M4': 'EE'}
def link_pts(n, step=1):
    return PARTS[n][0][::step]
def armW(q, root=np.eye(4)):
    W, _ = world_parts(root, q); return W
def module_pts(k, q, root=np.eye(4), step=7):
    W = armW(q, root); return np.vstack([(W[n] @ np.c_[link_pts(n, step), np.ones(len(link_pts(n, step)))].T).T[:, :3] for n in MODS[k]])

def boss_site(k, q_ref, others):
    """grip boss for module k: a 46 x 24 x 18 mm block with the pad on top, bonded to the module (module points close under or beside
    it), clear of every other module of the whole arm at rest, with the column the holder needs above the pad (90 x 90 mm, 130 mm
    tall) free of the module itself and of the modules on before it; the place nearest the module's middle wins"""
    W = armW(q_ref); n = LINK_OF[k]; Wl = W[n]
    P = module_pts(k, q_ref, step=2 if k in ('M3', 'M4') else 5); lo, hi = P.min(0), P.max(0); com = (lo + hi) / 2
    if k == 'M3':          # the forearm is taken at its middle, between elbow and wrist
        _, jp_ = world_parts(np.eye(4), q_ref); com = 0.5 * (jp_[1] + jp_[2])
    rest = [o for o in MODS if o != k]
    allo = np.vstack([module_pts(o, q_ref, step=7) for o in rest])
    col_obst = np.vstack([P] + [module_pts(o, q_ref, step=5) for o in others]) if others else P
    best = None
    for x in np.arange(lo[0] - 0.03, hi[0] + 0.031, 0.008):
        for y in np.arange(lo[1] - 0.04, hi[1] + 0.041, 0.008):
            for zp in np.arange(lo[2] + 0.02, hi[2] + 0.03, 0.008):
                blk = (np.abs(P[:, 0] - x) < 0.023) & (np.abs(P[:, 1] - y) < 0.012) & (P[:, 2] > zp - 0.018) & (P[:, 2] < zp + 0.0005)
                if blk.any(): continue                                         # the block may not sit inside the module
                near = (np.abs(P[:, 0] - x) < 0.027) & (np.abs(P[:, 1] - y) < 0.016) & (P[:, 2] > zp - 0.024) & (P[:, 2] < zp)
                if near.sum() < 4: continue                                    # something to bond to, under or beside the block
                if ((np.abs(allo[:, 0] - x) < 0.026) & (np.abs(allo[:, 1] - y) < 0.015) & (allo[:, 2] > zp - 0.02) & (allo[:, 2] < zp + 0.002)).any(): continue
                col = col_obst[(np.hypot(col_obst[:, 0] - x, col_obst[:, 1] - y) < 0.014) & (col_obst[:, 2] > zp + 0.001) & (col_obst[:, 2] < zp + 0.04)]
                if len(col): continue                                          # the magnet must come down onto the pad; the rest of the holder is tested in its real pose
                sc = math.hypot(x - com[0], y - com[1]) + 0.6 * abs(zp - com[2])
                if best is None or sc < best[0]: best = (sc, np.array([x, y, zp]))
    if best is None: return None
    pad = best[1]
    return n, np.linalg.inv(Wl) @ np.r_[pad, 1.0]      # pad top centre in the link frame (level in the pose q_ref, the pose it is handled in)

# the poses the new arm holds while each module goes on (searched below), and the bosses
BOSS_AT = {}
BOSS_AT['M1'] = boss_site('M1', REST, [])
# ---- where everything stands: the new tail, the parent docked face to face, the tray
PNEW = np.array(POSE_NEW); ROOT_NEW = pose_M(PNEW) @ T(BASE_L)
X_FACE_W = PNEW[0] - tb.X_FACE                                  # the new tail's face in the world (yaw pi)
RD = np.array([X_FACE_W - tb.X_FACE - 0.001, 0.0, 0.0])        # the parent docked face to face, 1 mm between the cuffs
XA, YA = 0.40, 0.17                                              # the new arm is put together on the floor beside the new tail's face, to port, its base axis here, facing the parent
ROOT_ASM = T([XA, YA, BASE_L[2]]) @ Rz(math.pi)
def stand(D, ys=0.0): return np.array([XA - D - BASE_L[0], ys, 0.0])   # the parent's pose, facing +x, its arm axis D behind the new arm's axis
RP = {}
TRAY = dict(y_in=-TY1, y_out=-0.300, top=0.030, x0=-0.17, x1=0.98)
PICK_Y = TRAY['y_out'] - 0.012 + tb.X_FACE                      # parent pose y when its face is 12 mm off the tray (yaw -90 deg)
PICK_YS = {}
def pick_pose(xp, pid=None): return np.array([xp, PICK_YS.get(pid, PICK_Y), -math.pi / 2])  # base axis at (xp, y + 0.115)

def pad_world(k, q, root, site=None):
    n, pl = site or BOSS_AT[k]; W = armW(q, root); return (W[n] @ pl)[:3], W[n]

def contact_tip(pad, heading):
    """tool tip at contact: the magnet face on the pad, the needle 28 mm ahead in its socket, 15 mm down"""
    return np.array([pad[0] + HOLD * math.cos(heading), pad[1] + HOLD * math.sin(heading), pad[2] - MAG_UP])

def solve_contact(pad, red, Ls=CUP):
    """the holder's heading follows the arm's base angle, so the socket direction and the contact tip are solved together"""
    h = red[2] + math.atan2(*(red_local(pad, red)[[1, 0]] - BASE_L[[1, 0]]))
    for _ in range(6):
        tip = contact_tip(pad, h); q = ikw(tip, Ls, red)
        if q is None: return None, None, h
        h = red[2] + q[0]
    return tip, q, h

# the new arm's join poses: its base turned and its joints held so that each module's pad is in reach of the parent, from above
_AS = {n: PARTS[n][0][::40] for n in PARTS}
_LB = {n: (PARTS[n][0].min(0) + 0.001, PARTS[n][0].max(0) - 0.001) for n in PARTS}
_MATE = {'M2': {'B_Rot'}, 'M3': {'Join', 'In_1', 'Out_1'}, 'M4': {'In_2', 'Out_2'}}
def _arm_world(root, q, skip=('B_Fix',)):
    W, _ = world_parts(root, q); return np.vstack([(M @ np.c_[_AS[n], np.ones(len(_AS[n]))].T).T[:, :3] for n, M in W.items() if n not in skip])
def _wall_hit(P, pose_par, pose_new):
    return max(tb.W_PAR.depth(tb.to_local(P, pose_par)).max(), tb.W_F.depth(tb.to_local(P, pose_new)).max())
def holder_hits(P, q, red, crank=0.0):
    """points of P inside the holder (head block, stem, magnet and its bracket, folded crank), the needle left out (it goes into the socket)"""
    M = np.linalg.inv(tool_frame(q, red, 0.0)); L = (M @ np.c_[P, np.ones(len(P))].T).T[:, :3]; x, y, z = L[:, 0], L[:, 1], L[:, 2]; m = 0.001
    hit = (np.abs(x) < 0.015 + m) & (np.abs(y) < 0.02 + m) & (z > -m) & (z < 0.052)
    hit |= (np.hypot(x, y) < 0.003 + m) & (z > -(CUP - 0.03)) & (z < 0)
    hit |= (np.hypot(x + HOLD, y) < 0.010 + m) & (z > -CUP + MAG_UP + 0.0005) & (z < -CUP + 0.033)
    hit |= (x > -HOLD - 0.002) & (x < 0) & (np.abs(y) < 0.004 + m) & (z > -CUP + 0.03) & (z < 0)
    hit |= (np.hypot(x - 0.004, y) < 0.004 + m) & (z > -0.03) & (z < 0.09)
    return int(hit.sum())
def _tool_world(q, red):
    """the holder sampled: stem, magnet ring, bracket, needle, folded crank"""
    tf = tool_frame(q, red, 0.0); P = [[0, 0, z] for z in np.linspace(-(CUP - 0.03), 0.052, 8)]
    P += [[-HOLD + 0.0105 * math.cos(a), 0.0105 * math.sin(a), z] for a in np.linspace(0, 2 * math.pi, 8, endpoint=False) for z in (-CUP + MAG_UP, -CUP + 0.03)]
    P += [[sx * 0.015, sy * 0.02, z] for sx in (-1, 1) for sy in (-1, 1) for z in (0.0, 0.052)] + [[0.004, 0, z] for z in np.linspace(-0.03, 0.09, 6)]
    P = np.array(P); return (tf @ np.c_[P, np.ones(len(P))].T).T[:, :3]
def _clear_of_parent(P, red):
    """everything of the new arm in front of the parent's face (its cuff at 32 mm, 6 mm kept)"""
    return tb.to_local(P, red)[:, 0].min() > tb.X_FACE + 0.006
HEAD_PARK = np.array([-0.70, 0.215, 0.0])           # where the relay leaves the old head, 33 mm from the port glass
_PAR_O = PAR['O'][::5, ::12].reshape(-1, 3); _HEAD_O = tb.HO[::8, ::12].reshape(-1, 3)
def _clear_of_head(red):
    """the parent's tail standing here clear of its old head, both ways, 3 mm kept"""
    a = float(tb.W_HEAD.depth(tb.to_local(tb.to_world(_PAR_O, red), HEAD_PARK)).max()); b = float(tb.W_PAR.depth(tb.to_local(tb.to_world(_HEAD_O, HEAD_PARK), red)).max())
    if max(a, b) > 0: return False
    P = tb.to_world(_PAR_O, red); H = tb.to_world(_HEAD_O, HEAD_PARK)
    from scipy.spatial import cKDTree as _K
    return float(_K(H).query(P)[0].min()) > 0.003
def best_stand(k, q, site, others):
    """where the parent stands to set module k (or the pack) in pose q: the pad in reach from above, its arm clear of its own wall,
    everything of the new arm in front of its face"""
    pad, _ = pad_world(k, q, ROOT_ASM, site) if k in MODS else (site, None)
    NA = np.vstack([module_pts(o, q, ROOT_ASM, step=11) for o in (others or ['M1'])])
    MP = module_pts(k, q, ROOT_ASM, step=11) if k in MODS else None
    for D, ys in [(D_, y_) for y_ in (0.0, 0.05, 0.1) for D_ in np.arange(0.24, 0.43, 0.01)]:
        red = stand(D, ys)
        if not _clear_of_head(red): continue
        if not _clear_of_parent(NA if MP is None else np.r_[NA, MP], red): continue
        tip, qq, h = solve_contact(pad, red)
        if tip is None or ikw(tip + [0, 0, 0.045], CUP, red) is None: continue
        if holder_hits(np.r_[NA, MP] if MP is not None else NA, qq, red): continue
        A_ = np.r_[_arm_world(pose_M(red) @ T(BASE_L), qq), _tool_world(qq, red)]
        if tb.W_PAR.depth(tb.to_local(A_, red)).max() > 0.0005: continue
        qa = ikw(tip + [0, 0, 0.045], CUP, red); bad = False
        Qs = [REST + (qa - REST) * w for w in np.linspace(0, 1, 9)]                  # from the rest pose to above the pad (joint space)
        Qs += [ikw(tip + [0, 0, 0.045 * w], CUP, red) for w in np.linspace(0, 1, 6)]   # down and up, straight
        for qw in Qs:
            if qw is None: bad = True; break
            P_ = np.r_[_arm_world(pose_M(red) @ T(BASE_L), qw), _tool_world(qw, red)]
            if tb.W_PAR.depth(tb.to_local(P_, red)).max() > 0.0003: bad = True; break
        if bad: continue
        return (D, ys), red
    return None
def find_qj(k, others):
    """search: the module's pad within the parent's reach from above (the parent may stand closer or farther), the parent's arm clear
    of its own wall, the module clear of the modules already on (the joint it clicks onto left out), joint ranges of the DexArm"""
    best = None
    sites = {} if k == 'M2' else {q2: boss_site(k, np.radians([0.0, 0.0, q2]), []) for q2 in range(0, 86, 10)}
    for q0 in range(-30, 31, 10):
        for q1 in range(0, 111, 10):
            for q2 in range(0, 86, 10):
                q = np.radians([q0, q1, q2])
                sc = abs(q0) * 0.3 + abs(q1 - REST[1] * 57.3) * 0.1 + abs(q2 - REST[2] * 57.3) * 0.05
                if best is not None and sc >= best[0]: continue
                if k == 'M2':
                    site = boss_site(k, q, others)
                else:
                    site = sites[q2]
                    if site is None: continue
                    n_, pl_ = site; Wq = armW(q); pd = (Wq[n_] @ pl_)[:3]
                    obst = np.vstack([module_pts(o, q, step=5) for o in others + [k]])
                    if ((np.hypot(obst[:, 0] - pd[0], obst[:, 1] - pd[1]) < 0.014) & (obst[:, 2] > pd[2] + 0.001) & (obst[:, 2] < pd[2] + 0.04)).any(): continue
                if site is None: continue
                MP = module_pts(k, q, ROOT_ASM, step=11)
                pz = pad_world(k, q, ROOT_ASM, site)[0][2]
                if pz - MP[:, 2].min() > 0.15: continue            # on the tray the pad must be low enough for the holder (cradle on the 30 mm plinth)
                W, _ = world_parts(ROOT_ASM, q); bad = False
                for o in others:
                    for n in MODS[o]:
                        if n in _MATE.get(k, set()): continue
                        L = (np.linalg.inv(W[n]) @ np.c_[MP, np.ones(len(MP))].T).T[:, :3]; lo, hi = _LB[n]
                        if (np.min(np.minimum(L - lo, hi - L), axis=1) > 0.0005).any(): bad = True; break
                    if bad: break
                if bad: continue
                bs = best_stand(k, q, site, others)
                if bs is None: continue
                best = (sc, q, site, bs)
    return best
QJ = {'M1': REST.copy()}
import time as _t, os as _os, hashlib as _h
_key = _h.md5(open('build.py', 'rb').read().split(b'# ---- the parts list')[0]).hexdigest()
_cache = json.load(open('qj_cache.json')) if _os.path.exists('qj_cache.json') else {}
for k, oth in (('M2', ['M1']), ('M3', ['M1', 'M2']), ('M4', ['M1', 'M2', 'M3'])):
    t0 = _t.time(); ck = _key + k
    if ck in _cache: b = (0, np.array(_cache[ck][0]), (_cache[ck][1], np.array(_cache[ck][2])), (tuple(_cache[ck][3]), stand(*_cache[ck][3])))
    else:
        b = find_qj(k, oth)
        if b: _cache[ck] = [list(map(float, b[1])), b[2][0], list(map(float, b[2][1])), [float(v) for v in b[3][0]]]; json.dump(_cache, open('qj_cache.json', 'w'))
    if b: RP[k] = b[3][1]
    if b: QJ[k] = b[1]; BOSS_AT[k] = b[2]
    else: QJ[k] = REST.copy(); BOSS_AT[k] = boss_site(k, REST, oth); print('no join pose for', k)
    print(k, 'join pose', np.degrees(QJ[k]).round(), round(_t.time() - t0, 1), 's')
print('QJ', {k: np.degrees(v).round() for k, v in QJ.items()})

# ---- the parts list
SEAT = {}                                                # where each part ends, as a world 4x4 of its own frame
SEAT['M1'] = ROOT_ASM.copy()
for k in ('M2', 'M3', 'M4'): SEAT[k] = ROOT_ASM.copy()
P_LOC = np.array([-0.002, 0.0, 0.045])                  # the power pack on a bracket at the front of the drive frame, 45 mm up, its cells across (the arm cannot reach lower so close to its base)
SEAT['P'] = ROOT_ASM @ T(P_LOC - BASE_L) @ Rz(math.pi / 2)          # on the bracket of the base's frame
P_ON_BASE = np.linalg.inv(ROOT_ASM) @ SEAT['P']
FRAME_C = np.array([0.005, 0.0])                        # the drive frame centre under B_Fix, in the module frame
BRACKET = dict(x0=0.080, x1=0.146, w=0.074, z=0.040, t=0.005)      # in the module frame (root at the base axis, 5 mm above the inner floor): a shelf in front of B_Fix
def frame_pts():
    g = np.mgrid[-1:1.01:0.5, -1:1.01:0.5, 0:1.01:1].reshape(3, -1).T
    br = np.mgrid[0:1.01:0.5, -1:1.01:0.5, 0:1.01:1].reshape(3, -1).T * [BRACKET['x1'] - BRACKET['x0'], BRACKET['w'] / 2, BRACKET['t']] + [BRACKET['x0'], 0, BRACKET['z'] - BRACKET['t']]
    return np.r_[g * [FRAME['L'] / 2, FRAME['W'] / 2, FRAME['t']] + [FRAME_C[0], FRAME_C[1], -FRAME['t']], [[FRAME_C[0], s * (FRAME['W'] / 2 + 0.005), -0.008] for s in (-1, 1)], br]
def part_frame_pts(pid):
    if pid == 'M1': return np.r_[module_pts('M1', QJ['M1']), frame_pts()]
    if pid in MODS: return module_pts(pid, QJ[pid])
    if pid == 'P':
        g = np.mgrid[-1:1.01:0.25, -1:1.01:0.25, 0:1.01:0.25].reshape(3, -1).T; return g * [PACK['L'] / 2, PACK['W'] / 2, PACK['H']]
    if pid == 'TS':
        g = np.mgrid[-1:1.01:0.25, -1:1.01:0.25, 0:1.01:0.5].reshape(3, -1).T; return g * [TILE['L'] / 2, TILE['W'] / 2, 0.005]
    if pid == 'H':
        g = np.mgrid[-1:1.01:0.5, -1:1.01:0.5, 0:1.01:0.1].reshape(3, -1).T; return g * [0.015, 0.02, 0.052] + [0, 0, 0.055]
LOADS = {}
def wet_base_N(bottom_z):
    """the base module in its sealed shroud: weight less buoyancy with the frame bottom at bottom_z"""
    sub = max(0.0, min(SHROUD['H'], WL - (bottom_z + FRAME['t'])))
    V = SHROUD['L'] * SHROUD['W'] * sub + FRAME['L'] * FRAME['W'] * FRAME['t'] * 0.6 * (1 if WL > bottom_z else 0)
    m = MASS['M1'] + m_shroud + m_frame + m_boss
    return (m - RHO * V) * G9, m, V
LIFT_M1 = 0.008
wet_M1_floor, mass_M1, V_M1 = wet_base_N(0.0)
wet_M1_lift, _, _ = wet_base_N(LIFT_M1)
LOADS['M1'] = wet_M1_lift
for k in ('M2', 'M3', 'M4'): LOADS[k] = (MASS[k] + m_boss) * G9        # carried in the air above the water (no buoyancy counted)
LOADS['P'] = (m_pack + m_boss) * G9
m_ts = TILE['L'] * TILE['W'] * TILE['t'] * qg.RHO_DS30 + 0.002 + 0.004 * 0.0004 + math.pi * 0.01 ** 2 * 0.001 * 7850     # tile, mp6 2 g, four tiles, disk
LOADS['TS'] = m_ts * G9
m_H = 0.0227 + 0.035                                              # the holder: Adafruit 3872 22.7 g, printed head and crank (estimate)
LOADS['H'] = m_H * G9

# ---------------------------------------------------------------- 7. the tray at the starboard glass: a printed plinth on the floor, a cradle for each part, the base in a floor bay
SLOT_X = {'M1': -0.02, 'P': 0.085, 'M2': 0.165, 'M3': 0.255, 'M4': 0.335, 'H': 0.64, 'TS': 0.78}
PAD_Y = {'M1': -0.372, 'P': -0.357, 'M2': -0.357, 'M3': -0.372, 'M4': -0.357, 'H': -0.357, 'TS': -0.357}
PICK_X = {'M1': 0.08, 'P': 0.08, 'M2': 0.12, 'M3': 0.13, 'M4': 0.20}
tray_items = []; TRAY_G = {}; HEAD_PICK = {}; HEAD_PLACE = {}; PLACE_TIP = {}; PICK_TIP = {}
def frame_bottom(pid, M):
    return (M @ np.c_[part_frame_pts(pid), np.ones(len(part_frame_pts(pid)))].T).T[:, 2].min()

def plan_part(pid):
    """heading of the holder at the seat and at the tray decide how the part stands on the tray"""
    if pid in MODS:
        n, pl = BOSS_AT[pid]; Wl = armW(QJ[pid])[n]; pad_l = (Wl @ pl)[:3]          # pad in the module frame
    else:
        pad_l = np.array([0.0, 0.0, (PACK['H'] if pid == 'P' else TILE['t'] + 0.001)])
    # at the seat
    padW = (SEAT[pid] @ np.r_[pad_l, 1])[:3]
    if pid not in RP:
        qq_ = QJ['M1']; bs = best_stand(pid, qq_ if pid in ('M1', 'P') else QJ[pid], padW if pid == 'P' else BOSS_AT.get(pid, BOSS_AT['M1']), [] if pid in ('M1', 'P') else [o for o in ('M1', 'M2', 'M3') if o < pid])
        RP[pid] = bs[1] if bs else stand(0.30, 0.1)
    tip, q, h = solve_contact(padW, RP[pid])
    if tip is None: print('no place contact', pid); tip, q, h = contact_tip(padW, 0.0), REST, 0.0
    beta = h - math.atan2(SEAT[pid][1, 0], SEAT[pid][0, 0])        # boss direction in the part frame
    # at the tray: the part on its cradle (the base on the glass in front of the plinth), inside the tray's depth where it can be,
    # the parent's face 12 mm off the nearest point of the part or the plinth
    padT = np.array([SLOT_X[pid], PAD_Y[pid], 0.0]); PICK_YS[pid] = PICK_Y
    for _ in range(5):
        red = pick_pose(PICK_X[pid], pid)
        tipT, qT, hT = solve_contact(np.r_[padT[:2], 0.15], red)
        psi = hT - beta
        G = T([padT[0], padT[1], 0]) @ Rz(psi) @ T(-np.array([pad_l[0], pad_l[1], 0]))
        floor = -0.003 if pid == 'M1' else TRAY['top'] + 0.004
        Pw = (G @ np.c_[part_frame_pts(pid), np.ones(len(part_frame_pts(pid)))].T).T[:, :3]
        G = T([0, 0, floor - Pw[:, 2].min()]) @ G
        Pw[:, 2] += floor - Pw[:, 2].min()
        if pid != 'M1':                                           # keep the part over the plinth (y between the glass and the plinth's front) where it fits
            lo_, hi_ = Pw[:, 1].min(), Pw[:, 1].max(); dy = 0.0
            if hi_ - lo_ < TRAY['y_out'] - TRAY['y_in'] - 0.012: dy = (TRAY['y_in'] + 0.006) - lo_ if lo_ < TRAY['y_in'] + 0.006 else ((TRAY['y_out'] - 0.006) - hi_ if hi_ > TRAY['y_out'] - 0.006 else 0.0)
            else: dy = (TRAY['y_in'] + 0.006) - lo_
            G = T([0, dy, 0]) @ G; Pw[:, 1] += dy
        else:                                                     # the base stands on the glass in a bay of the plinth, 6 mm off the glass
            dy = (TRAY['y_in'] + 0.006) - Pw[:, 1].min(); G = T([0, dy, 0]) @ G; Pw[:, 1] += dy
        padT = (G @ np.r_[pad_l, 1])[:3]
        PICK_YS[pid] = max(TRAY['y_out'], Pw[:, 1].max()) + 0.012 + tb.X_FACE
    tipT, qT, hT = solve_contact(padT, pick_pose(PICK_X[pid], pid))
    TRAY_G[pid] = G; HEAD_PICK[pid] = hT; HEAD_PLACE[pid] = h; PLACE_TIP[pid] = (tip, q); PICK_TIP[pid] = (tipT, qT)
    return pad_l, beta
PAD_L = {}; BETA = {}
for pid in ('M1', 'P', 'M2', 'M3', 'M4'):
    PAD_L[pid], BETA[pid] = plan_part(pid)
    print(pid, 'tray', np.round(mat_xyzyaw(TRAY_G[pid]), 3), 'pick y', round(PICK_YS[pid], 3), 'pick tip', None if PICK_TIP[pid][1] is None else np.round(PICK_TIP[pid][0], 3), 'place tip', np.round(PLACE_TIP[pid][0], 3), 'stand', np.round(RP[pid], 3))

# ---------------------------------------------------------------- 8. after the births: the relay, five trips to the tray, the new tail's own picks
def turn_about(axis, yaw):
    """pose of a tail whose base axis stays at axis (x, y) while it turns on its wheels to yaw"""
    c, s = math.cos(yaw), math.sin(yaw); return np.array([axis[0] - c * BASE_L[0] + s * BASE_L[1], axis[1] - s * BASE_L[0] - c * BASE_L[1], yaw])
def axis_of(p):
    c, s = math.cos(p[2]), math.sin(p[2]); return np.array([p[0] + c * BASE_L[0] - s * BASE_L[1], p[1] + s * BASE_L[0] + c * BASE_L[1]])
def bez(P, u):
    P = [np.asarray(p, float) for p in P]; a = (1 - u) ** 3; b = 3 * u * (1 - u) ** 2; c = 3 * u * u * (1 - u); d = u ** 3
    pt = a * P[0] + b * P[1] + c * P[2] + d * P[3]
    dv = 3 * (1 - u) ** 2 * (P[1] - P[0]) + 6 * u * (1 - u) * (P[2] - P[1]) + 3 * u * u * (P[3] - P[2]); return pt, dv
def bez_pose(P, u, reverse=False):
    pt, dv = bez(P, u); yaw = math.atan2(dv[1], dv[0]) + (math.pi if reverse else 0.0); return np.array([pt[0], pt[1], yaw])

HOME_Q = REST.copy()
def hold_tip_local(q, Ls=CUP):
    return tool_head(T(BASE_L), q) - [0, 0, Ls]

# ---- relay: the parent with its head backs away to port, releases the head, goes round it in the starboard lane
H_END = st.head.copy()
def f_relay(u, s0):
    h0 = np.array(s0['head']) + [-0.08, 0.0, 0.0]           # first straight back 80 mm, clear of the newborn's face, then the curve
    if u < 0.2: hp = lerp(s0['head'], h0, seg(u, 0.0, 0.2))
    else:
        P = [h0[:2], h0[:2] + [-0.30, 0.0], HEAD_PARK[:2] + [0.35, 0.0], HEAD_PARK[:2]]
        hp = bez_pose(P, seg(u, 0.2, 0.95), reverse=True)
    st.head = hp.copy(); st.red = hp.copy()
    st.q = lerp(s0['q'], HOME_Q, seg(u, 0, 0.2))
stage('relay', 'The parent and its head move aside', 8, 240, 'The parent backs its head away from the new tail and toward the port glass on the wheels of its tail, the head dragged on the floor (as the relay of the quilted head simulator).', f_relay, short='Aside')
def f_release(u, s0):
    st.tilt = seg(u, 0.0, 0.3) * (1 - seg(u, 0.75, 1.0))
    st.red = s0['red'] + np.array([-0.035 * seg(u, 0.3, 0.8), 0, 0])
stage('release', 'Tilt release', 3, 20, 'A cord tilts the nine magnets of the tail face on their hinged tabs; they peel off the steel disks of the head\'s cuff. The tail backs 35 mm. The old head stays at the port glass with its gel.', f_release, short='Release')
LANE_Y = -0.19
# the way round the old head, planned on the frames of the penetration test (dbg planner): the parent stands behind its old head,
# the head 30 mm from the port glass; one shunt (forward to starboard, back) gives the room to turn into the starboard lane
LANE_MOVES = [('s', -0.175), ('r', -0.30), ('s', 0.175), ('r', 0.20), ('s', -0.175), ('r', -0.65), ('s', None), ('r', 0.0)]
def _lane_prims(a):
    A = axis_of(a); h = 0.0; P = []
    for k, v in LANE_MOVES:
        if k == 'r': P.append(('r', A.copy(), h, v)); h = v
        else:
            d = v if v is not None else (LANE_Y - A[1]) / math.sin(h)
            B = A + d * np.array([math.cos(h), math.sin(h)]); P.append(('s', A.copy(), B.copy(), h)); A = B
    A3 = axis_of(np.array([0.215, 0.0, 0.0])); A2 = np.array([A3[0] - 0.45, LANE_Y])
    P.append(('s', A.copy(), A2, 0.0)); P.append(('b', A2, A3, 0.0))
    L = [abs(p[3] - p[2]) * 0.15 if p[0] == 'r' else float(np.linalg.norm(p[2] - p[1])) * (1.1 if p[0] == 'b' else 1.0) for p in P]
    return P, np.cumsum([0] + L) / sum(L)
def f_lane(u, s0):
    P, C = _lane_prims(np.array(s0['red']))
    w = seg(u, 0.02, 0.98); k = min(len(P) - 1, int(np.searchsorted(C, w, side='right') - 1)); t = mj((w - C[k]) / max(1e-9, C[k + 1] - C[k]))
    p = P[k]
    if p[0] == 'r': st.red = turn_about(p[1], p[2] + (p[3] - p[2]) * t)
    elif p[0] == 's': st.red = turn_about(p[1] + (p[2] - p[1]) * t, p[3])
    else:
        A2, A3 = p[1], p[2]; pa = bez_pose([A2, A2 + [0.18, 0], A3 - [0.18, 0], A3], t); st.red = turn_about(pa[:2], pa[2])
stage('lane', 'Round the old head', 10, 300, 'The tail backs 175 mm, shunts once to starboard (forward 175 mm, back 175 mm), turns into the starboard lane, drives past the old head and comes onto the centre line in front of the new tail. Nothing is between them now: the head that bore the new tail stands aside.', f_lane, short='Lane')
LANE_END = st.red.copy()

# ---- one trip: to the tray, pick, back, face to face, set down
def tip_path(a, b, w):
    return lerp(a, b, w)
def red_tip_local(q): return hold_tip_local(q)
def carry_q(pid, Hoff):
    """a holding pose for driving: the part in front of the face (clear of the parent's gel face, which fills the front 62 mm
    of the tail up to 100 mm), as low as the part allows, the turn as tight as possible"""
    best = None
    P = part_frame_pts(pid)
    for x in np.arange(0.06, 0.32, 0.004):
        for y in np.arange(-0.12, 0.121, 0.02):
            for z in np.arange(0.03, 0.30, 0.004):
                tip = np.array([x, y, z]); q = ik(tip, CUP, BASE_L)
                if q is None: continue
                M = T(tip) @ Rz(q[0]) @ Hoff; Q = (M @ np.c_[P, np.ones(len(P))].T).T[:, :3]
                if Q[:, 2].min() < 0.004: continue
                if pid == 'M1':
                    if Q[:, 2].min() > 0.006 + LIFT_M1 or Q[:, 0].min() < tb.X_FACE + 0.004: continue
                else:
                    if Q[:, 2].min() < J['read']['sill_z'] + 0.01 and Q[:, 0].min() < tb.X_FACE + 0.004: continue
                    if Q[:, 2].max() > 0.315 or np.abs(Q[:, 1]).max() > 0.13: continue
                r = np.hypot(Q[:, 0] - BASE_L[0], Q[:, 1]).max() + 0.2 * abs(y)
                if best is None or r < best[0]: best = (r, q, tip)
    return best

HELD_BY = {}
def set_part(pid, G, s=0):
    st.parts[pid] = dict(G=G.copy(), st=s)
for pid in ('M1', 'P', 'M2', 'M3', 'M4'): set_part(pid, TRAY_G[pid])

CUR = dict(pose=None)
CARRY_YT = {'M1': 0.10, 'M3': 0.0}                 # the base is carried low: it turns where it sweeps clear of the plinth
def trip(pid, first=False):
    label = MOD_NAME[pid]; xp = PICK_X[pid]; pk = pick_pose(xp, pid); ax = axis_of(pk)
    tipT, qT = PICK_TIP[pid]; tipP, qP = PLACE_TIP[pid]
    pad_l = PAD_L[pid]
    up = UP[pid]
    def f_pick(u, s0):
        a = s0['red']
        # drive: straight back (or on) along x to the turning point, turn to face the tray, drive in
        A = np.array([ax[0], axis_of(a)[1] if abs(a[2]) < 1e-3 else 0.0]); p_turn0 = turn_about(A, 0.0); p_turn1 = turn_about(A, -math.pi / 2)
        if u < 0.2: st.red = lerp(a, p_turn0, seg(u, 0.0, 0.2)); st.red[2] = 0.0
        elif u < 0.36: st.red = turn_about(A, -math.pi / 2 * seg(u, 0.2, 0.36))
        elif u < 0.5: st.red = lerp(p_turn1, pk, seg(u, 0.36, 0.5))
        else: st.red = pk.copy()
        # arm: home while driving, then over the pad, down to contact, magnet on, lift, back to the carry pose
        above = tipT + [0, 0, up]
        if u < 0.36: st.q = lerp(s0['q'], HOME_Q, seg(u, 0.0, 0.3))
        elif u < 0.55: st.q = lerp(HOME_Q, arm_to(above, CUP, pk, 'pick above ' + pid), seg(u, 0.4, 0.55))          # moves between holds in joint space, the approach and the lift straight
        elif u < 0.66: st.q = arm_to(lerp(above, tipT, seg(u, 0.55, 0.66)), CUP, pk, 'pick down ' + pid)
        elif u < 0.7: st.q = qT.copy(); st.mag = 1 if u > 0.68 else 0
        if 0.66 <= u < 0.7: st.mag = 1 if u > 0.675 else 0
        if u >= 0.7 and st.held is None:
            st.held = pid; st.Hoff = np.linalg.inv(tool_frame(qT, pk, CUP)) @ st.parts[pid]['G']; st.parts[pid]['st'] = 1; st.mag = 1
        if u >= 0.7:
            lift = (LIFT_M1 if pid == 'M1' else min(0.03, up))
            t_l = tipT + [0, 0, lift]
            st.q = arm_to(lerp(tipT, t_l, seg(u, 0.7, 0.85)), CUP, pk, 'lift ' + pid)
    def f_carry(u, s0):
        # back out along y to the turning point, turn to face +x, drive along x to the stand (and, if the turn had to be made
        # elsewhere, a turn, a short drive across and a turn back): every segment checked by the penetration test
        yt = CARRY_YT.get(pid, RP[pid][1]); A = np.array([ax[0], yt]); p_back = turn_about(A, -math.pi / 2)
        S = axis_of(RP[pid]); B = np.array([S[0], yt])
        if u < 0.2: st.red = lerp(s0['red'], p_back, seg(u, 0.0, 0.2)); st.q = s0['q'].copy(); return
        st.q = lerp(s0['q'], CARRY[pid][1], seg(u, 0.2, 0.32)) if u < 0.32 else CARRY[pid][1].copy()
        if u < 0.32: st.red = p_back.copy()
        elif u < 0.48: st.red = turn_about(A, -math.pi / 2 * (1 - seg(u, 0.32, 0.48)))
        elif abs(S[1] - yt) < 1e-6 or u < 0.72:
            w = seg(u, 0.48, 1.0 if abs(S[1] - yt) < 1e-6 else 0.72); st.red = turn_about(A + (B - A) * w, 0.0)
        else:
            h = math.copysign(math.pi / 2, S[1] - yt)
            if u < 0.8: st.red = turn_about(B, h * seg(u, 0.72, 0.8))
            elif u < 0.9: st.red = turn_about(B + (S - B) * seg(u, 0.8, 0.9), h)
            else: st.red = turn_about(S, h * (1 - seg(u, 0.9, 1.0)))
    def f_place(u, s0):
        RDp = RP[pid]; st.red = RDp.copy(); above = tipP + [0, 0, up]
        cq = CARRY[pid][1]; qa = arm_to(above, CUP, RDp, 'place above ' + pid)
        if u < 0.2: st.q = lerp(cq, HOME_Q, seg(u, 0.0, 0.2))                       # to the rest pose, then over the pad (the way the stand search tested)
        elif u < 0.4: st.q = lerp(HOME_Q, qa, seg(u, 0.2, 0.4))
        elif u < 0.55: st.q = arm_to(lerp(above, tipP, seg(u, 0.4, 0.55)), CUP, RDp, 'place down ' + pid)
        elif u < 0.62: st.q = qP.copy(); st.mag = 0 if u > 0.6 else 1
        if u >= 0.6 and st.held == pid:
            st.held = None; st.parts[pid]['G'] = SEAT[pid].copy(); st.parts[pid]['st'] = 3 if pid in MODS else 5; st.mag = 0
            if pid == 'P': st.parts[pid]['loc'] = P_ON_BASE.copy()
            if pid == 'M1': st.nroot = np.array([XA, YA, math.pi])
            if pid == 'P': st.new['on'] = 1
            if pid == 'M1': st.new['on'] = 0
        if u >= 0.62: st.q = arm_to(lerp(tipP, above, seg(u, 0.62, 0.75)), CUP, RDp, 'release ' + pid) if u < 0.75 else lerp(arm_to(above, CUP, RDp, 'release ' + pid), HOME_Q, seg(u, 0.75, 1.0))
        # the new arm holds the next join pose once it is powered
        # the new arm, once powered, waits folded up while the parent drives; it holds out the joint only when the parent stands by
        if st.new['on'] and pid in ('M2', 'M3', 'M4'): st.new['cq'] = lerp(s0['new']['cq'], QJ[pid], seg(u, 0.0, 0.18)) if u < 0.62 else lerp(QJ[pid], WAIT_Q, seg(u, 0.8, 1.0))
        elif st.new['on'] and pid == 'P': st.new['cq'] = lerp(s0['new']['cq'], WAIT_Q, seg(u, 0.8, 1.0))
    stage('pick' + pid, f'{label.capitalize()}: from the tray', 9, 300,
          PICK_TEXT[pid], f_pick, short=f'{label.capitalize()}: pick')
    stage('carry' + pid, f'{label.capitalize()}: carried to the plate', 6, 180,
          f'It backs out, turns on its wheels and drives to the assembly plate beside the new tail, the {label} held low in front of its face.', f_carry, short='Carry')
    stage('place' + pid, f'{label.capitalize()}: set down', 8, 240, PLACE_TEXT[pid], f_place, short=f'{label.capitalize()}: set')

PICK_TEXT = {
    'M1': 'It turns to the tray. The base stands in its floor bay on its drive frame, in its sealed shroud. The magnet lands on the steel pad of the grip boss on the turret, the ball needle enters the socket 28 mm ahead: the magnet holds, the needle keeps the base from turning. The base is lifted 12 mm, no more: at this depth the water carries most of it.',
    'P': 'The power pack (three 18650 cells in series in a sealed sleeve) stands in its cradle. Magnet on the pad, needle in the socket, lifted out of the cradle.',
    'M2': 'The upper arm with the elbow block lies in its cradle in the attitude it will go on. Magnet on the pad of its boss, needle in the socket; lifted clear of the cradle walls.',
    'M3': 'The forearm in its cradle, in the attitude it will go on. Magnet on the pad of its boss, needle in the socket; lifted.',
    'M4': 'The end effector with its rotary flange. Magnet on the pad, needle in the socket; lifted.'}
PLACE_TEXT = {
    'M1': 'The parent stands beside the assembly plate, a steel cast plate on the glass beside the new tail\'s face. It sets the base down on the plate: the two wheels of the frame drop into the plate\'s slots. Magnet off; the needle leaves the socket.',
    'P': 'The pack goes on the bracket at the front of the drive frame; its pads meet the pogo pins of the frame. The new arm has power.',
    'M2': 'The new arm holds its shoulder where the parent can reach. The upper arm goes down onto the shoulder pins and the latch clicks. Magnet off.',
    'M3': 'The new arm holds its upper arm out. The forearm goes down onto the elbow and clicks. Magnet off.',
    'M4': 'The end effector goes down onto the wrist and clicks. The new arm is whole.'}
def up_for(pid):
    tipT, qT = PICK_TIP[pid]; tipP, qP = PLACE_TIP[pid]; pk = pick_pose(PICK_X[pid], pid)
    for up in (0.045, 0.035, 0.025, 0.018, 0.012, 0.008):
        ok = all(ikw(tipT + [0, 0, up * w], CUP, pk) is not None and ikw(tipP + [0, 0, up * w], CUP, RP[pid]) is not None for w in np.linspace(0, 1, 7))
        if ok: return up
    return 0.008
UP = {p: up_for(p) for p in ('M1', 'P', 'M2', 'M3', 'M4')}
print('approach heights', UP)
WAIT_Q = np.array([0.0, 0.0, math.radians(85)])          # the new arm waits folded up (as it folds to drive), out of the parent's way
CARRY = {}
for pid in ('M1', 'P', 'M2', 'M3', 'M4'):
    tipT, qT = PICK_TIP[pid]
    Hoff = np.linalg.inv(tool_frame(qT, pick_pose(PICK_X[pid], pid), CUP)) @ TRAY_G[pid]
    CARRY[pid] = carry_q(pid, Hoff)
    print('carry', pid, None if CARRY[pid] is None else (round(CARRY[pid][0], 3), np.round(CARRY[pid][2], 3)))

for pid in ('M1', 'P', 'M2', 'M3', 'M4'):
    trip(pid)
import collections; print('frames after trips', len(frames), 'miss', len(miss), collections.Counter(m[1] for m in miss))

# ---- the parent leaves; the new arm wakes; the new tail turns to the tray and takes a holder and a tile set itself
def new_pose(): return np.array(st.F['pose'])
def set_new_pose(p):
    st.F['pose'] = list(p); a = axis_of(np.array(p)); st.nroot = np.array([a[0], a[1], p[2]])
def nik(tip_world, Ls, pose, label):
    q = ik(red_local(tip_world, pose), Ls, BASE_L, True)
    if q is None: miss.append((len(frames), label, [R4(x) for x in tip_world])); return st.new['cq']
    return q
def ntool_frame(q, pose, Ls):
    tip = tool_head(pose_M(pose) @ T(BASE_L), q) - [0, 0, Ls]; return T(tip) @ Rz(pose[2] + q[0])

FOLDQ = np.array([0.0, 0.0, math.radians(85)])
PARK0 = stand(0.335)
SEAT_ROOT = np.array([axis_of(PNEW)[0], axis_of(PNEW)[1], math.pi])
def f_fold(u, s0):
    st.red = lerp(s0['red'], PARK0, seg(u, 0.1, 0.7)); st.red[2] = 0.0; st.q = lerp(s0['q'], HOME_Q, seg(u, 0.0, 0.3))
    st.new['cq'] = lerp(s0['new']['cq'], FOLDQ, seg(u, 0.3, 1.0))
stage('fold', 'The new arm folds', 5, 60, 'The new arm is whole. Powered by its own pack it folds up; the parent backs away to give it room.', f_fold, short='Folds')
def f_drivein(u, s0):
    a = np.array(s0['nroot']); mid = np.array([SEAT_ROOT[0] - 0.30, 0.0])
    w = seg(u, 0.05, 0.95)
    if w < 0.55: p = bez_pose([a[:2], [a[0] + 0.10, a[1]], [mid[0] - 0.10, 0.0], mid], w / 0.55); st.nroot = np.array([p[0], p[1], p[2] + math.pi])
    else: st.nroot = np.array([mid[0] + (SEAT_ROOT[0] - mid[0]) * (w - 0.55) / 0.45, 0.0, math.pi])
stage('drivein', 'It drives into the new tail', 6, 120, 'On the two N20 wheels of its frame the new arm backs round and into the new tail through its open face: the wheels run in two slots of its floor down to the glass, and the frame\'s four pins click into the cast sockets of the floor where the base of a tail stands.', f_drivein, short='Drives in')
def f_dock(u, s0):
    st.red = lerp(s0['red'], RD, seg(u, 0.05, 0.95)); st.red[2] = 0.0
stage('dock', 'Face to face', 5, 120, 'The parent docks face to face with the new tail: the nine magnets of its face on the steel disks of the new tail\'s face cuff, as a tail docks to a head.', f_dock, short='Dock')
def f_ballast(u, s0):
    st.gel = seg(u, 0.1, 0.9); st.flow = 1 if 0.1 < u < 0.9 else 0
    st.new['cq'] = lerp(s0['new']['cq'], REST, seg(u, 0.0, 0.3))
stage('ballast', 'Gel ballast', 6, 1500, 'Docked, the parent pumps gel from the bottle outside the tank through its line into the new tail\'s circuits in place of their air (a relief valve lets the air out), at 0.1 L a minute: the body becomes heavy above the water line and holds down the frame of the new arm, pinned into its floor. Gel is the only ballast of a new body; no steel.', f_ballast, short='Ballast')
PARK = np.array([RD[0] - 0.30, 0.0, 0.0])
def f_leave(u, s0):
    st.red = lerp(RD, PARK, seg(u, 0.15, 0.8)); st.red[2] = 0.0; st.q = lerp(s0['q'], HOME_Q, seg(u, 0.0, 0.3))
stage('leave', 'Its own arm', 5, 120, 'The tilt release lets go and the parent backs 300 mm away. The new tail has a body, an arm, power and gel ballast; it has no tool and no sensors yet.', f_leave, short='Apart')

NAX = axis_of(np.array(POSE_NEW)); NEW_PICK = np.array([NAX[0], PICK_Y, -math.pi / 2])
# the holder for the new arm stands on a saddle on the tray, the tile set in its cradle; their pads face the way the new arm will come
H_HEAD = np.array([SLOT_X['H'], -0.357, TRAY['top'] + 0.062])           # the underside of the holder's head block, where the quick release takes it
def head_heading(p, pose):
    l = red_local(p, pose); return pose[2] + math.atan2(l[1] - BASE_L[1], l[0] - BASE_L[0])
PSI_H = head_heading(H_HEAD, NEW_PICK)
TRAY_G['H'] = T(H_HEAD) @ Rz(PSI_H)
TS_PAD = np.array([SLOT_X['TS'], -0.357, TRAY['top'] + 0.006 + TILE['t'] + 0.001])
def ts_contact(pose):
    h = head_heading(TS_PAD, pose)
    for _ in range(5):
        tip = contact_tip(TS_PAD, h); q = ik(red_local(tip, pose), CUP, BASE_L, True)
        if q is None: break
        h = pose[2] + q[0]
    return tip, q, h
TS_TIP, TS_Q, TS_H = ts_contact(NEW_PICK)
TRAY_G['TS'] = T(TS_PAD - [0, 0, TILE['t'] + 0.001]) @ Rz(TS_H)        # the disk at the tile's centre, the socket 28 mm ahead on the holder's heading
set_part('H', TRAY_G['H']); set_part('TS', TRAY_G['TS'])
# the pocket: a third skin printed on the inner skin of F's lower port flank, open toward the arm; its lower skin has a slot for the needle
NHELD = {}
def pk_pt(r, z=None, a=None):
    a = PK_A if a is None else a; z = PK_Z if z is None else z
    return np.array([BASE_L[0] + r * math.cos(a), BASE_L[1] + r * math.sin(a), z])
def wall_r(a, z):
    """where the ray from the arm's axis meets the new tail's inner skin at height z"""
    for r in np.arange(0.10, 0.30, 0.001):
        p = pk_pt(r, z, a); i = np.argmin(np.abs(BF['xs'] - p[0])); I = BF['I'][i]; m = np.abs(I[:, 2] - z) < 0.006
        if p[0] > tb.X_FACE - 0.003: return None
        if m.any() and abs(p[1]) > np.abs(I[m, 1]).max() - 0.001: return r
    return None
def tile_box_clear(a, r, z):
    """the tile (46 x 32 mm, long side along the ray) clear of the base housing, the frame's bracket and the pack, 5 mm kept"""
    c = pk_pt(r, z, a); ca, sa = math.cos(a), math.sin(a)
    pts = np.array([c + [ca * u - sa * v, sa * u + ca * v, w] for u in (-0.023, 0, 0.023) for v in (-0.016, 0, 0.016) for w in (0.0, 0.005)])
    for lo, hi in ((np.array([-0.188, -0.069, 0.0]), np.array([-0.032, 0.069, 0.104])), (np.array([-0.040, -0.042, 0.0]), np.array([0.036, 0.042, 0.073]))):
        if np.all((pts >= lo) & (pts <= hi), axis=1).any(): return False
    return np.hypot(pts[:, 0] - BASE_L[0], pts[:, 1]).min() > 0.112 or pts[:, 2].max() < 0.093
def tile_pts_local(a, r, z):
    c = pk_pt(r, z, a); ca, sa = math.cos(a), math.sin(a)
    hl, hw = TILE['L'] / 2 + 0.0005, TILE['W'] / 2 + 0.0005          # 0.5 mm kept round the tile (its heading at the pocket is the ray's: the base angle of the arm)
    return np.array([c + [ca * u - sa * v, sa * u + ca * v, w] for u in np.linspace(-hl, hl, 19) for v in np.linspace(-hw, hw, 13) for w in (0.0, 0.0025, 0.005)])
def pocket_gap(a, z, rw):
    """the gap kept between the tile's outer end and the wall: the least that keeps every point of the tile 0.3 mm out of the new tail's wall"""
    for g in np.arange(0.002, 0.030, 0.001):
        r_in = rw - TILE["L"] / 2 - g; r_lip = r_in - 0.016
        P = np.vstack([tile_pts_local(a, r_in, z)] + [tile_pts_local(a, r_lip, z + dz) for dz in (0.0, 0.003, 0.006, 0.009)])     # set in, and on the way down over the lip (9 mm)
        if float(tb.W_F.depth(P).max()) <= 0.0: return g
    return None
def pocket_ok(a, z):
    rw = wall_r(a, z)
    if rw is None: return None
    g = pocket_gap(a, z, rw)
    if g is None: return None
    r_in = rw - TILE["L"] / 2 - g; r_lip = r_in - 0.016
    if not (tile_box_clear(a, r_in, z) and tile_box_clear(a, r_lip, z)): return None
    zt = z + TILE['t'] + 0.001 - MAG_UP
    for r in (r_lip, r_in):
        for dz in (0.0, 0.008):
            tip = np.array([BASE_L[0] + (r + HOLD) * math.cos(a), BASE_L[1] + (r + HOLD) * math.sin(a), zt + dz])
            if ik(tip, CUP, BASE_L, True) is None: return None
    return rw, g
PK = None
for z_ in np.arange(0.03, 0.155, 0.01):
    for a_ in sorted([math.radians(d) for d in range(10, 81, 2)] + [-math.radians(d) for d in range(10, 81, 2)], key=abs):
        rg = pocket_ok(a_, z_)
        if rg is not None: PK = (a_, z_, rg[0], rg[1]); break
    if PK: break
print('pocket', None if PK is None else (round(math.degrees(PK[0])), round(PK[1], 3), round(PK[2], 3), PK[3]))
assert PK is not None, 'no pocket found'
PK_A, PK_Z, R_WALL, PK_GAP = PK
R_IN = R_WALL - TILE["L"] / 2 - PK_GAP; R_LIP = R_IN - 0.016
POCKET = dict(a=PK_A, z=PK_Z, r_lip=R_LIP, r_in=R_IN, r_wall=R_WALL, w=TILE['W'] + 0.008, h=0.007)
def drop_plan(pose):
    disk = np.array(pose_M(pose) @ np.r_[pk_pt(R_LIP, PK_Z + TILE['t'] + 0.001), 1])[:3]
    h = pose[2] + PK_A
    tip = contact_tip(disk, h); return tip, T(disk - [0, 0, TILE['t'] + 0.001]) @ Rz(h)
DROP_TIP, DROP_G = drop_plan(NEW_PICK)
_d = np.array(pose_M(NEW_PICK)[:3, :3] @ [math.cos(PK_A) * (R_IN - R_LIP), math.sin(PK_A) * (R_IN - R_LIP), 0]); SLIDE_TIP = DROP_TIP + _d
def f_turn_new(u, s0):
    p0 = np.array(s0['F']['pose']); A = NAX
    if u < 0.5: set_new_pose(turn_about(A, p0[2] + (math.pi / 2) * seg(u, 0.05, 0.5)))
    else: p1 = turn_about(A, p0[2] + math.pi / 2); p2 = NEW_PICK.copy(); p2[2] = p1[2]; set_new_pose(lerp(p1, p2, seg(u, 0.5, 0.95)))
stage('turnNew', 'The new tail turns to the tray', 6, 120, 'On the wheels of its drive frame, powered from its pack, the new tail turns on the spot and drives to the tray.', f_turn_new, short='To tray')
def f_selfH(u, s0):
    pose = new_pose(); above = H_HEAD + [0, 0, 0.04]
    qa = nik(above, 0.0, pose, 'new above holder'); qc = nik(H_HEAD, 0.0, pose, 'new on holder')
    if u < 0.4: st.new['cq'] = lerp(s0['new']['cq'], qa, seg(u, 0.0, 0.4))
    elif u < 0.6: st.new['cq'] = nik(lerp(above, H_HEAD, seg(u, 0.4, 0.6)), 0.0, pose, 'new down holder')
    elif u < 0.65: st.new['cq'] = qc
    if u >= 0.65 and st.new['tool'] == 0: st.new['tool'] = 1; st.parts['H']['st'] = 3
    if u >= 0.65: st.new['cq'] = nik(lerp(H_HEAD, above + [0, 0, 0.02], seg(u, 0.65, 0.9)), 0.0, pose, 'new lift holder')
stage('selfH', 'It takes a holder', 7, 90, 'Tool change, as the parent does it in its own tail: the bare quick release of the new arm comes down onto the holder standing in its saddle on the tray and clicks; the holder lifts out of the saddle. The new arm now has an electromagnet, a ball needle and a crank.', f_selfH, short='Holder')
def f_selfT(u, s0):
    pose = new_pose(); above = TS_TIP + [0, 0, 0.03]
    if u < 0.12: st.new['cq'] = lerp(s0['new']['cq'], nik(above, CUP, pose, 'new above tile'), seg(u, 0.0, 0.12))
    elif u < 0.2: st.new['cq'] = nik(lerp(above, TS_TIP, seg(u, 0.12, 0.2)), CUP, pose, 'new down tile')
    elif u < 0.24: st.new['cq'] = TS_Q.copy(); st.new['mag'] = 1 if u > 0.22 else 0
    if u >= 0.24 and st.parts['TS']['st'] == 0:
        st.parts['TS']['st'] = 1; st.new['mag'] = 1; NHELD['Hoff'] = np.linalg.inv(ntool_frame(TS_Q, pose, CUP)) @ st.parts['TS']['G']
    if 0.24 <= u < 0.64:
        via = np.array(pose_M(pose) @ np.r_[0.125, 0.05, 0.12, 1])[:3]
        if u < 0.3: st.new['cq'] = nik(lerp(TS_TIP, above, seg(u, 0.24, 0.3)), CUP, pose, 'new lift tile')
        elif u < 0.4: st.new['cq'] = lerp(nik(above, CUP, pose, 'new lift tile'), nik(via, CUP, pose, 'new via'), seg(u, 0.3, 0.4))
        elif u < 0.5: st.new['cq'] = lerp(nik(via, CUP, pose, 'new via'), nik(DROP_TIP + [0, 0, 0.008], CUP, pose, 'new above lip'), seg(u, 0.4, 0.5))
        elif u < 0.56: st.new['cq'] = nik(lerp(DROP_TIP + [0, 0, 0.008], DROP_TIP, seg(u, 0.5, 0.56)), CUP, pose, 'new down lip')
        else: st.new['cq'] = nik(lerp(DROP_TIP, SLIDE_TIP, seg(u, 0.56, 0.64)), CUP, pose, 'new slide in')
    if 0.64 <= u and st.parts['TS']['st'] == 1:
        if u > 0.66: st.new['mag'] = 0; st.parts['TS']['st'] = 4; st.parts['TS']['loc'] = np.linalg.inv(pose_M(new_pose())) @ st.parts['TS']['G']
    if u >= 0.66:
        if u < 0.76: st.new['cq'] = nik(lerp(SLIDE_TIP, SLIDE_TIP + [0, 0, 0.012], seg(u, 0.66, 0.76)), CUP, pose, 'new up')
        else: st.new['cq'] = lerp(nik(SLIDE_TIP + [0, 0, 0.012], CUP, pose, 'new up'), REST, seg(u, 0.76, 1.0))
stage('selfT', 'It puts a tile set into its own wall', 12, 240, f'Magnet on the steel disk of the tile set, the ball needle into the well of its cradle. The arm draws the tile into its own body over the pack and lays it on the lower skin of the pocket on the port flank, then slides it {(R_IN - R_LIP)*1000:.0f} mm in under the two lips of the pocket, the needle running in the slot of the lower skin. Magnet off; the magnet lifts out between the lips. A Core tile, two Sense tiles (motion, pressure), a Power tile and an mp6 pump, on one cast tile (after bergsonne.io/tiles and the quilted head kit).', f_selfT, short='Tile set')
def f_end(u, s0):
    a = np.array(s0['F']['pose']); b = a + [0, 0.12, 0]          # straight back along its own axis, heading kept
    set_new_pose(lerp(a, b, seg(u, 0.1, 0.8)))
stage('end', 'Two tails', 4, 60, 'The new tail backs away from the tray: one body born from the head, an arm the parent put together for it, power, gel ballast, a tool and a first set of sensors it took itself. The parent waits beside its old head.', f_end, short='Two tails')

# ---------------------------------------------------------------- 10. penetration test over every frame (as the quilted head simulator: sampled points against exact surfaces)
# A quilted wall is the space between its two skins (tcbody.Wall). Parts, cradles and the tray are boxes; the arm links are their mesh
# vertices; the tank is its glass. Designed contacts are left out and named: a part on its own cradle or seat at the moment of contact,
# a module and the joint it clicks onto, the tool's needle in a socket.
def tray_boxes():
    """the plinth along the glass, in two lengths either side of the bay where the base stands on the glass; the assembly plate on the floor"""
    B = []; Pw = (TRAY_G['M1'] @ np.c_[PART_S0['M1'], np.ones(len(PART_S0['M1']))].T).T[:, :3]; bx0, bx1 = Pw[:, 0].min() - 0.06, Pw[:, 0].max() + 0.06
    for a, b in ((TRAY['x0'], bx0), (bx1, TRAY['x1'])):
        B.append(('plinth', np.array([(a + b) / 2, (TRAY['y_in'] + TRAY['y_out']) / 2, TRAY['top'] / 2]), np.array([(b - a) / 2, (TRAY['y_out'] - TRAY['y_in']) / 2, TRAY['top'] / 2]), 0.0))
    # the assembly plate: tank furniture like the tray, 3 mm on the glass, with two slots for the wheels of the drive frame
    for yc, hw in ((0.0, 0.07), (0.105, 0.015), (-0.105, 0.015)):
        B.append(('assembly plate', np.array([XA + FRAME_C[0] * -1, YA + yc, -0.0015]), np.array([0.13, hw, 0.0015]), 0.0))
    return B
PART_S0 = {'M1': None}
def cradle_boxes():
    """a cradle under each part on the tray: a pocket 6 mm deep round the lowest 6 mm of the part, walls 4 mm thick"""
    out = {}
    for pid in ('P', 'M2', 'M3', 'M4', 'TS'):
        G = TRAY_G[pid]; P = (G @ np.c_[part_frame_pts(pid), np.ones(len(part_frame_pts(pid)))].T).T[:, :3]
        z0 = P[:, 2].min(); low = P[P[:, 2] < z0 + 0.006]; yaw = mat_xyzyaw(G)[3]; c, s = math.cos(yaw), math.sin(yaw)
        L = np.c_[c * low[:, 0] + s * low[:, 1], -s * low[:, 0] + c * low[:, 1]]; lo, hi = L.min(0), L.max(0); cc = (lo + hi) / 2; hw = (hi - lo) / 2
        ctr = np.array([c * cc[0] - s * cc[1], s * cc[0] + c * cc[1]])
        items = [('floor', np.r_[ctr, (TRAY['top'] + z0) / 2], np.r_[hw + 0.004, (z0 - TRAY['top']) / 2], yaw)]
        for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            off = np.array([sx * (hw[0] + 0.002 + 0.0005), sy * (hw[1] + 0.002 + 0.0005)]); h2 = np.array([0.002 if sx else hw[0] + 0.004, 0.002 if sy else hw[1] + 0.004])
            items.append(('wall', np.r_[ctr + [c * off[0] - s * off[1], s * off[0] + c * off[1]], z0 + 0.003], np.r_[h2, 0.003], yaw))
        out[pid] = items
    # the base's floor bay: two rails 3 mm high under the frame's skids
    G = TRAY_G['M1']; yaw = mat_xyzyaw(G)[3]; c, s = math.cos(yaw), math.sin(yaw); o = (G @ np.r_[FRAME_C[0], 0, 0, 1])[:2]
    out['M1'] = [('rail', np.r_[o + [-s * sy * 0.05, c * sy * 0.05], -0.0015], np.array([FRAME['L'] / 2, 0.006, 0.0015]), yaw) for sy in (-1, 1)]
    # the holder's saddle: two ledges under its head block
    G = TRAY_G['H']; yaw = mat_xyzyaw(G)[3]; c, s = math.cos(yaw), math.sin(yaw); o = G[:3, 3]
    out['H'] = [('ledge', o + [-s * sy * 0.026, c * sy * 0.026, -0.003], np.array([0.016, 0.006, 0.003]), yaw) for sy in (-1, 1)] + \
               [('post', o + [-s * sy * 0.026, c * sy * 0.026, -(o[2] - TRAY['top']) / 2 - 0.003], np.array([0.006, 0.006, (o[2] - TRAY['top']) / 2 - 0.003]), yaw) for sy in (-1, 1)]
    return out
PART_S0['M1'] = part_frame_pts('M1'); TRAYB = tray_boxes(); CRADLE = cradle_boxes()
def box_depth(P, c, h, yaw):
    cy, sy = math.cos(yaw), math.sin(yaw); d = P - c; L = np.c_[cy * d[:, 0] + sy * d[:, 1], -sy * d[:, 0] + cy * d[:, 1], d[:, 2]]
    pen = np.min(h - np.abs(L), axis=1); return np.maximum(pen, 0.0)
def pocket_boxes(pose):
    """the pocket in the new tail: lower skin with its slot (two strips), two lips over the tile's long edges; in the world"""
    out = []; Mp = pose_M(pose)
    for name, r0, r1, off, w, z0, t in (('lower skin', R_LIP - 0.03, R_WALL, -0.012, 0.010, PK_Z - 0.0012, 0.0012), ('lower skin', R_LIP - 0.03, R_WALL, 0.012, 0.010, PK_Z - 0.0012, 0.0012),
                                         ('lip', R_IN - TILE['L'] / 2 - 0.002, R_WALL, -(TILE['W'] / 2 + 0.002) + 0.002, 0.008, PK_Z + 0.007, 0.0012), ('lip', R_IN - TILE['L'] / 2 - 0.002, R_WALL, TILE['W'] / 2, 0.008, PK_Z + 0.007, 0.0012)):
        rm = (r0 + r1) / 2; c = pk_pt(rm, z0 + t / 2) + np.array([-math.sin(PK_A) * off, math.cos(PK_A) * off, 0])
        cw = (Mp @ np.r_[c, 1])[:3]; out.append((name, cw, np.array([(r1 - r0) / 2, w / 2, t / 2]), pose[2] + PK_A))
    return out

def tool_pts(q, red, tool, crank):
    """the holder (stem, magnet, needle, crank) or the print needle, sampled, in the world"""
    tf = tool_frame(q, red, 0.0); P = []
    if tool == 1:
        for z in np.linspace(-0.025, 0.0, 6): P.append([0, 0, z])                                  # stem from the head down
        for a in np.linspace(0, 2 * math.pi, 10, endpoint=False):
            for z in (-CUP + MAG_UP, -CUP + MAG_UP + 0.015): P.append([-HOLD + 0.0095 * math.cos(a), 0.0095 * math.sin(a), z])
        cr = crank
        for l in np.linspace(0, CRANK, 8):
            th = -math.pi / 2 * (1 - cr); P.append([0.004 + l * math.cos(th), 0, -0.03 - l * math.sin(th)])
    elif tool == 2:
        for z in np.linspace(-NEEDLE + 0.03, 0.0, 8): P.append([0, 0, z])
    P = np.array(P) if P else np.zeros((0, 3))
    return (tf @ np.c_[P, np.ones(len(P))].T).T[:, :3] if len(P) else P
def needle_pts(q, red, Ls=CUP):
    tf = tool_frame(q, red, Ls); P = np.array([[0, 0, z] for z in np.linspace(0, 0.03, 6)]); return (tf @ np.c_[P, np.ones(len(P))].T).T[:, :3]

ARM_S = {n: PARTS[n][0][::25] for n in PARTS}
def arm_pts(root, q, names=None, skip=('B_Fix',)):
    W, _ = world_parts(root, q); P = []
    for n, M in W.items():
        if (names and n not in names) or n in skip: continue
        v = ARM_S[n]; P.append((M @ np.c_[v, np.ones(len(v))].T).T[:, :3])
    return np.vstack(P)
PART_S = {pid: part_frame_pts(pid) for pid in ('M1', 'P', 'M2', 'M3', 'M4', 'TS', 'H')}
PAR_OUT = PAR['O'][::5, ::12].reshape(-1, 3); HEAD_OUT = tb.HO[::8, ::12].reshape(-1, 3); F_OUT = BF['O'][::4, ::12].reshape(-1, 3)
def glass_depth(P):
    return np.maximum.reduce([np.maximum(0, TX0 - P[:, 0]), np.maximum(0, P[:, 0] - TX1), np.maximum(0, np.abs(P[:, 1]) - TY1), np.maximum(0, -0.0031 - P[:, 2])])
def Gm(v): return T(v[:3]) @ Rz(v[3])
JOINT_MATE = {'M2': {'B_Rot'}, 'M3': {'Join', 'In_1', 'Out_1'}, 'M4': {'In_2', 'Out_2'}}
LINK_BOX = {n: (PARTS[n][0].min(0) + 0.001, PARTS[n][0].max(0) - 0.001) for n in PARTS}
def in_link_boxes(P, root, q, names):
    W, _ = world_parts(root, q); worst = 0.0
    for n in names:
        M = np.linalg.inv(W[n]); L = (M @ np.c_[P, np.ones(len(P))].T).T[:, :3]; lo, hi = LINK_BOX[n]
        d = np.min(np.minimum(L - lo, hi - L), axis=1); worst = max(worst, float(np.maximum(d, 0).max()) if len(d) else 0.0)
    return worst

W_PAR, W_HEAD, W_F = tb.W_PAR, tb.W_HEAD, tb.W_F
PAIRS = {}
def rec(name, v, fi):
    if name not in PAIRS or v > PAIRS[name][0]: PAIRS[name] = (v, fi)
    elif name not in PAIRS: PAIRS[name] = (0.0, -1)
PAIR_NAMES = ['newborn, inner skin, lip and rolled rim of the head', 'newborn, tank floor', 'parent arm and tool, the quilted wall of its own tail',
              'parent arm and tool, the head', 'parent arm, tool and held part, the walls of the new tail', 'held part, tray, cradles and saddle',
              'held module, the modules already on the new arm (the joint it clicks onto left out)', 'part, the parts already set down (pack, tile set)',
              'bodies, parts and arms, the tank glass and floor', 'parent tail, head and new tail, each other', 'new arm, holder and tile set, the new tail and its pocket']
for n in PAIR_NAMES: PAIRS[n] = (0.0, -1)
# keyframes: map each frame to the keyframes it shows
for fi, fr in enumerate(frames):
    for nm in ('F',):
        v = fr[nm]
        if v[0] == 1:
            k0 = int(math.floor(v[1])); k1 = min(len(KEYPEN) - 1, k0 + 1)
            rec(PAIR_NAMES[0], max(KEYPEN[k0][0], KEYPEN[k1][0]), fi); rec(PAIR_NAMES[1], max(KEYPEN[k0][1], KEYPEN[k1][1]), fi)
PEN = np.zeros(len(frames))
import os
FAST = os.environ.get('FAST')
for fi, fr in enumerate(frames):
    if FAST and fi % 10: fr['pen'] = 0.0; continue
    red = np.array(fr['red']); head = np.array(fr['head']); q = np.array(fr['q']); tool = fr['tool']
    worst = 0.0
    def R(i, v):
        global worst
        rec(PAIR_NAMES[i], v, fi); worst = max(worst, v)
    root = pose_M(red) @ T(BASE_L)
    A = arm_pts(root, q); A = np.r_[A, tool_pts(q, red, tool, fr['crank'])]
    R(2, float(W_PAR.depth(tb.to_local(A, red)).max()))
    R(3, float(W_HEAD.depth(tb.to_local(A, head)).max()))
    newp = np.array(fr['F'][2:5]) if fr['F'][0] == 2 else None
    held = [pid for pid, v in fr['parts'].items() if v[4] == 1]
    HP = np.zeros((0, 3))
    for pid in held:
        HP = (Gm(fr['parts'][pid]) @ np.c_[PART_S[pid], np.ones(len(PART_S[pid]))].T).T[:, :3]
    # new tail walls
    if newp is not None:
        Q = np.r_[A, HP]
        R(4, float(W_F.depth(tb.to_local(Q, newp)).max()))
    # held part vs tray, cradles, saddle (its own cradle counted too once it has left contact: the lift is vertical)
    if len(HP):
        d = 0.0
        for nm, c, h, yw in TRAYB: d = max(d, float(box_depth(HP, c, h, yw).max()))
        for pid2, items in CRADLE.items():
            for nm, c, h, yw in items: d = max(d, float(box_depth(HP, c, h, yw).max()))
        R(5, d)
        # held module vs the modules already on the new arm
        if held[0] in MODS and fr.get('nroot') is not None:
            nr = fr['nroot']; NR = T([nr[0], nr[1], BASE_L[2]]) @ Rz(nr[2])
            on = [k for k in ('M1', 'M2', 'M3') if fr['parts'].get(k, [0] * 5)[4] == 3 and k != held[0]]
            names = [n for k in on for n in MODS[k] if n not in JOINT_MATE.get(held[0], set())]
            if names: R(6, in_link_boxes(HP, NR, np.array(fr['cq']), names))
    # parts vs set down parts (pack, tile set as boxes)
    for pid in ('P', 'TS'):
        v = fr['parts'].get(pid)
        if v and v[4] in (2, 4, 5):
            G = Gm(v); c = G[:3, 3] + [0, 0, (PACK['H'] if pid == 'P' else 0.005) / 2]; h = np.array([PACK['L'] / 2, PACK['W'] / 2, PACK['H'] / 2]) if pid == 'P' else np.array([TILE['L'] / 2, TILE['W'] / 2, 0.0025])
            Q = np.r_[A, HP] if len(HP) else A
            R(7, float(box_depth(Q, c, h - 0.0005, v[3]).max()))
    # glass and floor: the bodies' outer skins, arms, parts
    G_ = [tb.to_world(PAR_OUT, red), tb.to_world(HEAD_OUT, head), A]
    if newp is not None: G_ += [tb.to_world(F_OUT, newp)]
    for pid, v in fr['parts'].items():
        if v[4] in (0, 1, 2, 4, 5): G_.append((Gm(v) @ np.c_[PART_S[pid][::3], np.ones(len(PART_S[pid][::3]))].T).T[:, :3])
    R(8, float(glass_depth(np.vstack(G_)).max()))
    # bodies against each other
    d = float(W_HEAD.depth(tb.to_local(tb.to_world(PAR_OUT, red), head)).max())
    d = max(d, float(W_PAR.depth(tb.to_local(tb.to_world(HEAD_OUT, head), red)).max()))
    if newp is not None:
        for Wb in (W_F,):
            d = max(d, float(Wb.depth(tb.to_local(tb.to_world(PAR_OUT, red), newp)).max()), float(Wb.depth(tb.to_local(tb.to_world(HEAD_OUT, head), newp)).max()))
        NO = tb.to_world(F_OUT, newp)
        d = max(d, float(W_PAR.depth(tb.to_local(NO, red)).max()), float(W_HEAD.depth(tb.to_local(NO, head)).max()))
    R(9, d)
    # the new arm in its own tail
    if fr.get('nroot') is not None and fr['parts'].get('M1', [0] * 5)[4] == 3:
        nr = fr['nroot']; NR = T([nr[0], nr[1], BASE_L[2]]) @ Rz(nr[2])
        on = [n for k in ('M1', 'M2', 'M3', 'M4') if fr['parts'].get(k, [0] * 5)[4] == 3 for n in MODS[k]]
        NA = arm_pts(NR, np.array(fr['cq']), on)
        d0 = float(W_PAR.depth(tb.to_local(NA, red)).max()); R(9, d0)
        R(8, float(glass_depth(NA).max()))
        Q = NA
        if fr['ntool'] == 1:
            Q = np.r_[Q, tool_pts(np.array(fr['cq']), newp, 1, 0.0)]
        d = float(W_F.depth(tb.to_local(Q, newp)).max())
        tsv = fr['parts'].get('TS')
        if tsv and tsv[4] in (1, 4):
            TP = (Gm(tsv) @ np.c_[PART_S['TS'], np.ones(len(PART_S['TS']))].T).T[:, :3]
            for nm, c, h, yw in pocket_boxes(newp): d = max(d, float(box_depth(TP, c, h - 0.0003, yw).max()))
            d = max(d, float(W_F.depth(tb.to_local(TP, newp)).max()))
        R(10, d)
    PEN[fi] = worst
    fr['pen'] = R4(worst)
PEN_MAX = float(PEN.max())
print('penetration', {k: (round(v[0] * 1000, 2), v[1]) for k, v in PAIRS.items()}, 'max', round(PEN_MAX * 1000, 2))

# ---------------------------------------------------------------- 11. masses, buoyancy, locomotion, ballast (estimates are marked)
FOLDQ_ = np.array([0.0, 0.0, math.radians(85)])
eq = J['equip']; m_store = sum(e['kg'] for e in eq if not e['name'].startswith('Silicone')) + sum(e['kg'] for e in eq if e['name'].startswith('Silicone'))
m_par_frame = 0.40 * 1.0                                        # printed PETG seat plate, rack posts and wheel brackets of the parent's tail (estimate)
m_par_wheels = 2 * (0.010 + 0.012)                              # two N20 gear motors and wheels, as the new tail's (estimate)
m_steel = 1.2                                                   # steel under the arm base of the parent's tail (allowed for the tail, the quilted head simulator)
gel_tail_L = J['q']['q2']['tail_gel_L']
m_par = m_par_sk + 2.4 + m_par_frame + m_par_wheels + m_steel + m_store + gel_tail_L
B_par = RHO * enc_par                                           # the tail is closed by its gel face: the water it keeps out under the water line
floor_par = (m_par - B_par) * G9
# the new tail, empty on the floor: its interlayer air under the water line lifts; its face is open, so water fills it
lay_new = lay_F
m_new_sk = m_F_sk
W_new_empty = (m_new_sk - RHO * v_F_sk - RHO * lay_new) * G9
W_F_free = W_new_empty
# the gel ballast: the parent fills the new tail's circuits with gel instead of air through its line (as the head's lip circuit takes gel at 9 kPa);
# the gel is denser than nothing, so above the water line it weighs, under it it is neutral
V_pan = lay_F_all - lay_F                                       # the circuits of the new tail above the water line
W_ballast = V_pan * 1000 * G9
m_links = MASS['M2'] + MASS['M3'] + MASS['M4']
def tip_moment(q, mods=('M2', 'M3', 'M4')):
    """moment of the links (in the air) about the base axis, from the centres of their meshes (mass spread by the split above)"""
    W, _ = world_parts(np.eye(4), q); mo = 0.0
    for k in mods:
        P = np.vstack([(W[n] @ np.c_[PARTS[n][0][::15], np.ones(len(PARTS[n][0][::15]))].T).T[:, :3] for n in MODS[k]]); c = P.mean(0)
        mo += MASS[k] * G9 * c[:2]
    return float(np.hypot(*mo))
M_tip_asm = max(tip_moment(QJ['M3'], ('M2',)), tip_moment(QJ['M4'], ('M2', 'M3')), tip_moment(QJ['M4'], ('M2', 'M3', 'M4')), tip_moment(FOLDQ_, ('M2', 'M3', 'M4')))
PLATE_STEEL = 4.0                                                 # kg of steel cast into the assembly plate: tank furniture like the tray, not part of any body
W_plate = PLATE_STEEL * (1 - 1 / 7.85) * G9
restore_asm = (W_plate + wet_M1_floor + LOADS['P']) * 0.12
poses_q = [REST] + [np.array(f['cq']) for f in frames if f['parts'].get('M4', [0] * 5)[4] == 3][::5]
M_tip = max(tip_moment(q) for q in poses_q)
LEVER = 0.10                                                     # the frame is pinned into four cast sockets of the new tail's floor; the body's weight acts at least 100 mm from the frame's edges (the body is 300 mm wide, its middle 100 mm behind the frame) (estimate)
W_base_floor = wet_M1_floor
W_new_full = W_new_empty + W_base_floor + W_ballast + LOADS['P'] + (m_links + m_boss * 3) * G9 + LOADS['TS'] + LOADS['H']
restore = (W_new_full - (m_links + m_boss * 3) * G9) * LEVER

# ---------------------------------------------------------------- 12. checks
chk('Bodies', f'The parent\'s tail is a quilted double wall from the first frame, built as the head is built: two skins joined by webs along the body, {qg.NCH} channels round it, the outer skin an arc of 55 degrees between two webs, the inner one of 25, the floor a flat double skin of {qg.FLOOR_T*1000:.1f} mm; cross seams at the thirds of the body, staggered. The inner skin follows the outer surface of the doublewall tail, so the arm, the tools and the store keep their places',
    True, f'{qg.area(PAR["O"]):.3f} m2 outer, {qg.area(PAR["I"]):.3f} m2 inner, up to {PAR["T"].max()*1000:.1f} mm thick (head: 14.8), {V_par_layer*1000:.1f} L of air between the skins')
_px = np.array(J['hull']['prof']['x']); _pz = np.array(J['hull']['prof']['zb'])
_fl = _px[(_px > 0.032) & (_pz < 0.001)]; FLAT0, FLAT1 = 0.032, float(_fl.max())       # the flat floor of the bowl, head frame
PK0, PK1 = XPC - tb.PACK_F[0] / 2, XPC + tb.PACK_F[0] / 2
LAY4 = 2 * 3 * 4; H4 = LAY4 * tb.PITCH
chk('Bodies', f'The new tail is one body, printed whole: the parent\'s tail copied, the same construction and the same outline, nose to face cuff', True,
    f'{aF_o:.3f} m2 outer, {aF_i:.3f} m2 inner, {sil_F:.2f} L of Dragon Skin 30')
chk('Fold', f'The whole tail folds as the head does (laid flat, Z folded 3 across and 3 along, 18 layers of {tb.PITCH*1000:.1f} mm): {tb.PACK_F[0]*1000:.0f} x {tb.PACK_F[1]*1000:.0f} x {tb.PACK_F[2]*1000:.1f} mm. It is {(tb.PACK_F[0]-0.143)*1000:.0f} mm longer than the head\'s own pack (143 x 194 x 79 mm), not taller: it lies on the flat floor of the bowl from {PK0*1000:.0f} to {PK1*1000:.0f} mm (the floor is flat from {FLAT0*1000:.0f} to {FLAT1*1000:.0f} mm). Folding 4 along to keep 143 mm would give {LAY4} layers, {H4*1000:.0f} mm, over the {J["q"]["q4"]["z_top_mm"]:.1f} mm under the needle',
    tb.PACK_F[1] <= 0.224 - 2 * 0.015 and FLAT0 + 0.01 <= PK0 and PK1 <= FLAT1 - 0.0 and tb.PACK_F[2] * 1000 <= J['q']['q4']['z_top_mm'],
    f'across: the 224 mm trough with 15 mm each side; height: {tb.PACK_F[2]*1000:.1f} mm under {J["q"]["q4"]["z_top_mm"]:.1f} mm; the needle reaches every lane of the print (no pose out of reach); the earlier round counted 21 layers by scaling the head\'s area onto its 143 x 194 mm footprint')
chk('Fold', f'Print time from the silicone laid, scaled from the head (1.42 L in {T_HEAD/3600:.1f} h): {t_F/3600:.1f} h for the whole tail', True, 'the toolpath of the quilt is not computed here; the G-code shown is schematic')
kp = [p[0] for p in KEYPEN]
chk('Birth', f'Birth by the method of the quilted head: the keel opens the lengthwise folds, the holder and then its folding crank push the rim, each row of the strip opens across and fills only once it lies outside; inside and on the lip the strip stays flat and cupped (radius 90 mm, as the head\'s strip). {len(KEYS)} keyframes of both skins from the script, each tested against the head\'s inner skin, lip and rolled rim: deepest overlap {max(kp)*1000:.2f} mm',
    max(kp) <= 0.001, 'kinematic, as the head\'s birth: rows move along a fixed path over the lip and are interpolated between flat, folded and filled; not solved as a membrane')
chk('Birth', f'Reach: the whole tail is {tb.CF.L*1000:.0f} mm long, longer than the run from the face to the lip, so the folds open only until the nose reaches the lip; then the holder pushes the rim {BIRTH["F"]["push_h"]*1000:.0f} mm and the crank {BIRTH["F"]["push_c"]*1000:.0f} mm more while the last folds open, and the nose comes down onto the tank floor ({"yes" if NOSE_ON_FLOOR else "no"}); then the parent backs {BIRTH["F"]["back"]*1000:.0f} mm on its wheels, the head with it, the nose resting on the floor',
    NOSE_ON_FLOOR and not [m for m in miss if m[1].startswith('birth')], 'every pose inside the DexArm\'s joint ranges')
# push per phase, the method of the quilted head simulator: the strip's weight up the ramp above the gel, gel drag on both faces
for nm, msk, C in (('F', m_F_sk, tb.CF),):
    per_m = msk / C.L; ramp = 0.074; th = math.radians(54)
    w_fold = tb.PACK_F[1]
    GEL_EXIT = tb.P_LIP - ramp                                   # the strip leaves the gel 74 mm of ramp before the lip
    xr = C.xs - C.xs[0]; Lg = 0.0
    for r_ in np.linspace(BIRTH['F']['r1'], BIRTH['F']['rc'], 25):     # the strip material still in the gel, the most over the push
        bx_ = BIRTH['F']['bx_a'] + (1 - BIRTH['F']['bx_a']) * min(1.0, max(0.0, (r_ - BIRTH['F']['r0']) / max(1e-6, BIRTH['F']['r_open'] - BIRTH['F']['r0'])))
        ba_ = ba_of(C, r_, bx_); p_ = np.array([ba_ - tb.acc(x, C.L, 3, bx_, 6 * tb.PITCH)[0] for x in xr])
        Lg = max(Lg, float(C.L * np.mean(p_ < GEL_EXIT)))
    Fp = per_m * ramp * G9 * (math.sin(th) + MU * math.cos(th)) + 2 * 25.0 * w_fold * Lg
    chk('Birth', f'Push on the rim: {per_m*ramp:.2f} kg of strip on the 74 mm of ramp above the gel at 54 degrees ({per_m*ramp*G9*(math.sin(th)+MU*math.cos(th)):.2f} N with friction 0.3), and gel drag at 25 Pa on both faces of the {Lg*1000:.0f} mm of strip still in the gel at the start of the push ({2*25*w_fold*Lg:.2f} N): {Fp:.2f} N of the {PAY:.2f} N payload',
        Fp < PAY, 'the numbers of the quilted head simulator\'s push check (where the head, heavier, fails at 5.29 N); estimate')
chk('Water', f'Water at {WL*1000:.1f} mm, the level of the quilted head simulator (the earlier round raised it to 270 mm, where the head floated and the hard tail lost its wheels). No part needs deep water here: the base, sealed, nearly floats at this depth and is lifted only {LIFT_M1*1000:.0f} mm; the other parts weigh less than the payload in air',
    True, f'base: {wet_M1_floor:.2f} N on the floor, {wet_M1_lift:.2f} N on the holder lifted {LIFT_M1*1000:.0f} mm')
chk('Water', f'The parent\'s tail on its wheels: {m_par:.2f} kg (quilted skins {m_par_sk:.2f}, DexArm 2.4, frame {m_par_frame:.2f}, store {m_store:.2f}, gel {gel_tail_L:.2f}, steel {m_steel:.1f}) against {B_par/1000*1000:.2f} kg of water kept out under the water line: {floor_par:.1f} N on the floor',
    floor_par > 5.0, f'traction at 0.3: {MU*floor_par:.1f} N; it drags the head ({5.0*MU:.1f} N in the quilted head simulator); air between its skins under the water line {lay_par*1000:.2f} L')
chk('Water', f'The new tail, empty, lies on the tank floor: {W_F_free:.2f} N on the floor (skins in Dragon Skin 30, SG 1.08, less the air between the skins under the water line)', W_F_free > 0, 'it does not float off; it does not move by itsels')
chk('New tail', f'The new arm\'s base, in its sealed shroud on its drive frame, {mass_M1:.2f} kg, displaces {V_M1*1000:.2f} L at this depth: only {wet_M1_floor:.2f} N on the floor. Its links reach out with up to {M_tip:.2f} N m, so the frame is pinned into four cast sockets printed into the new tail\'s floor and the body holds it down: with its circuits filled with gel ({V_pan*1000:.2f} L above the water line, {W_ballast:.1f} N) the body gives {restore:.2f} N m at a lever of {LEVER*1000:.0f} mm',
    restore >= 1.5 * M_tip, f'margin {restore/max(1e-6, M_tip):.2f} (wanted 1.5); gel is the only ballast, no steel in the new body; lever and sockets: estimate, bench test')
chk('New tail', f'While it is put together the new arm stands with its frame pinned into the latching sockets of the assembly plate (tank furniture, like the tray: {PLATE_STEEL:.0f} kg of steel cast in a printed plate, 3 mm over the glass, slots for the wheels). Its links lean out with up to {M_tip_asm:.2f} N m; plate, base and pack give {restore_asm:.2f} N m at 120 mm',
    restore_asm >= 1.5 * M_tip_asm, f'margin {restore_asm/max(1e-6, M_tip_asm):.2f} (wanted 1.5); latches: estimate, bench test')
chk('New tail', f'The finished new tail: {W_new_full:.1f} N on the floor ({W_new_empty:.1f} N of it the empty quilted body), traction {MU*W_new_full:.1f} N for its two N20 wheels', W_new_full > 0, 'rolling on the glass, no slip modelled')
held = {k: LOADS[k] for k in ('M1', 'P', 'M2', 'M3', 'M4', 'TS', 'H')}
chk('Parts', 'Every part at its true size: the DexArm in four modules from the link meshes of arm.json (base with its three steppers, upper arm with the elbow block, forearm, end effector); the pack of three Samsung INR18650-35E cells (18.75 x 65.25 mm); the tile set after bergsonne.io/tiles (T44 4 x 4 mm, T48 4 x 8 mm tiles) with the Bartels mp6 (30 x 15 x 3.8 mm); the holder as the parent\'s', True,
    'module masses are a split of the DexArm\'s 2.4 kg (estimate)')
chk('Parts', 'Loads on the holder: ' + ', '.join(f'{MOD_NAME[k]} {v:.2f} N' for k, v in held.items()) + f'; payload {PAY:.2f} N, the magnet on a bare 3 mm pad {MAG_PAD:.1f} N (40 % of the 2.5 kg rating, estimate)',
    max(held.values()) <= min(PAY, MAG_PAD), f'heaviest {max(held, key=held.get)}, margin {PAY/max(held.values()):.2f}')
chk('Parts', 'Every pick and every set down is a sequence: the holder comes over the part from a reachable direction, the magnet lands on the steel pad of the part\'s grip boss and the ball needle enters its socket 28 mm ahead (15 mm deep), magnet on, a straight vertical lift out of the cradle, a carry pose clear of the parent\'s gel face, the turn, the drive to its stand beside the assembly plate, a vertical descent onto the plate or joint, magnet off, a vertical lift. Moves between holds run in joint space inside the DexArm\'s ranges',
    len(miss) == 0, f'{len(miss)} poses out of reach')
chk('Parts', 'The holder has no wrist: its heading is the arm\'s base angle. So each part stands on the tray turned by the angle that brings it to its seat at the right heading (' + ', '.join(f'{MOD_NAME[k]} {math.degrees(mat_xyzyaw(TRAY_G[k])[3]):.0f} deg' for k in ('M1', 'P', 'M2', 'M3', 'M4')) + ')', True, 'computed from the heading at the tray and at the seat')
chk('Parts', 'The new arm, powered from its pack, holds each join pose: ' + ', '.join(f'for its {MOD_NAME[k]} {", ".join(f"{math.degrees(x):.0f}" for x in QJ[k])} deg' for k in ('M2', 'M3', 'M4')), True, 'searched: pad in reach from above, both arms and the module clear of every wall and of the modules already on')
chk('Parts', f'The tile set goes into a pocket of the new tail\'s port flank, a third skin printed with the tail on its inner skin, {POCKET["r_in"]*1000:.0f} mm from the arm\'s axis at {POCKET["z"]*1000:.0f} mm: the arm slides it in under the pocket\'s two lips, the needle in the slot of the lower skin', True,
    'the floor of the tail is out of the arm\'s reach (the DexArm reaches the floor only 230 mm or more from its axis)')
chk('Tank', f'Tank {TANK["name"]}: the birth needs {BIRTH["F"]["back"]:.2f} m of run behind the parent; the relay puts the head at the port glass and the tail goes round it; the parent turns on the spot to face the tray', True, 'glass clearance is part of the penetration test')
chk('Penetration', f'Per frame penetration test over {len(frames)} frames (bodies, arms, tools, parts, tray, cradles, saddle, pocket, glass): deepest overlap of any pair {PEN_MAX*1000:.2f} mm (limit 1 mm)', PEN_MAX <= 0.001,
    'points sampled from the skins and the arm meshes against the walls (the space between the two skins), boxes and the glass')

notes += [
    'The parent\'s tail is no longer a hard shell: it is a quilted double wall from the first frame, built like the head, with its inner skin where the shell\'s outer surface was. The DexArm stands on a printed seat plate on the floor skin; the store hangs on a printed rack on the same plate; two N20 wheels in slots of the floor skin drive it; 1.2 kg of steel on the plate (allowed for the parent, as in the quilted head simulator) gives the wheels their grip.',
    'The water stays at the level of the quilted head simulator (80.7 mm). The earlier round raised it to 270 mm so the parent could lift the base; here the base, in its sealed shroud, nearly floats at this depth and is lifted only 8 mm, so the head stays on the floor and the tails keep their wheels on the glass.',
    f'The new tail is printed whole, in one print, and born once: nose first over the lower lip, so that it comes to rest in front of the head with its open face toward it. The earlier round printed it in two halves; the whole tail fits the bowl folded 3 x 3 as the head does, {(tb.PACK_F[0]-0.143)*1000:.0f} mm longer than the head\'s own pack and no taller.',
    'The new arm is put together on an assembly plate on the glass beside the new tail\'s face, not inside it: docked face to face, the parent\'s holder could not reach the join poses over its floor without touching its walls. For each part the parent stands beside the plate at a place the script searched (the pad in reach from above, its arm and tool clear of its own wall on the way in and out). Five trips. Then the new arm drives itself into the new tail on its own wheels.',
    'The holder\'s heading is its base angle (no wrist): the parts stand on the tray turned so they arrive at their seats at the right heading.',
    'Each part carries a grip boss: a printed block with a 20 x 3 mm steel pad and a 3.2 mm socket 28 mm from it, placed by the script where the block bonds to the part, clears every other module and leaves the holder room above the pad.',
    'Ballast is gel: once the new arm is inside the new tail, the parent docks face to face and fills its circuits above the water line with gel through its line instead of air, as the head\'s lip circuit takes gel. The frame of the new arm is pinned into cast sockets printed into the new tail\'s floor, so the body holds the arm down. No steel in the new body.',
    'The quilt starts just under the water line: below it the walls are the flat double skin of the floor, so no air under the water lifts the bodies, and the new tail rests on the floor when it is born.',
    'The tile set is taken by the new tail itself, with the holder it took from the tray: Bergsonne style tiles (Core T44-14, Sense T44 motion and pressure, Power T48) and an mp6 pump on one cast tile, slid into a pocket of its own port flank.',
]
TEXT = dict(
    birth='The new tail is printed whole, in one print, folded flat on the bowl floor (laid flat, Z folded 3 across and 3 along, 18 layers), around nothing: it is born empty, nose first. (a) The ball needle of the holder sits in the valve at the rim; the keel fills first and opens the lengthwise folds until the nose lies on the lip, paying the strip out from the front while the rim stays at the back of the pack (the tail is longer than the run from the face to the lip). (b) The holder and then its folding crank push the rim at 2 mm/s while the last folds open and air is fed with the advance, until the nose lies on the tank floor; each row opens across and then fills only once it lies outside, past the lip. (d) The needle leaves; the parent backs away on its wheels with its head, the front of the newborn resting on the floor, and the rest slides over the lip and settles.',
    solved='Solved by the script: the two skins of every body (built as the head is built), the folded pack, the path over the lip from the head\'s own skins, the reach of every pose with the DexArm\'s kinematics and joint ranges, the join poses of the new arm, the grip bosses, the heading of every part on the tray, the penetration of every pair in every frame. Interpolated: the shape of a row between flat, folded and filled during a birth (kinematic, as the head\'s birth), the settling of the rear of a newborn onto the floor, the drives of the tails (kinematic, no slip). Estimated: module masses, magnet pull on a pad, friction, gel drag, the base shroud.',
    handover='The parent\'s tail leaves its head at the port glass and goes round it. For each part it turns on the spot to the tray at the starboard glass, takes the part with its holder, drives to its stand beside the assembly plate at the new tail\'s face and sets the part down: base, pack, upper arm, forearm, end effector. The new arm, powered by its pack, holds each joint where the next module goes on. Whole, it folds and drives itself into the new tail. The parent docks face to face with the new tail and fills its circuits with gel ballast, then backs away. The new tail turns to the tray and takes a holder and a tile set itself.')
SOURCES = [J['sources'][k] for k in ('dex', 'ds30', 'mag', 'magnet', 'cell', 'carbopol', 'gelpump')] + [
    dict(t='Bergsonne tiles (opened 23 Nov 2026): T44 packages 4.0 x 4.0 mm, 10 to 14 pads, 1.0 to 2.0 mm tall; T48 4.0 x 8.0 mm; 0.8 mm pad pitch; epoxy overmold; one I2C/I3C bus', u='https://bergsonne.io/tiles'),
    dict(t='Bartels mp6 micropump datasheet: 30 x 15 x 3.8 mm, 2 g', u='https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5561/mp6 micropumps.pdf'),
    dict(t='Rotrics DexArm link meshes (arm.json of the quilted head simulator)', u='../doublewall/arm.json'),
    dict(t='N20 gear motor, about 10 g (society parts list of this site; estimate)', u='')]
MASSES = [
    dict(name=f'Parent\'s tail, {m_par:.2f} kg', rows=[['Quilted skins and webs, Dragon Skin 30', f'{m_par_sk:.2f} kg'], ['Rotrics DexArm', '2.4 kg'], ['Seat plate, rack, wheels (estimate)', f'{m_par_frame + m_par_wheels:.2f} kg'], ['Store, pumps, battery, Pi (the quilted head simulator)', f'{m_store:.2f} kg'], ['Gel at its face', f'{gel_tail_L:.2f} kg'], ['Steel on the seat plate', f'{m_steel:.1f} kg'], ['Air between the skins', f'{V_par_layer*1000:.1f} L']],
         note=f'In {WL*1000:.1f} mm of water: {floor_par:.1f} N on the floor.'),
    dict(name='The new tail', rows=[['Skins and webs, Dragon Skin 30', f'{m_F_sk:.2f} kg, {sil_F:.2f} L'], ['Air between the skins', f'{lay_F_all*1000:.2f} L']], note=f'Free on the floor: {W_F_free:.2f} N.'),
    dict(name='Parts', rows=[[MOD_NAME[k], f'{(MASS[k] + m_boss + (m_shroud + m_frame if k == "M1" else 0)) * 1000:.0f} g'] for k in ('M1', 'M2', 'M3', 'M4')] + [['power pack', f'{(m_pack + m_boss)*1000:.0f} g'], ['tile set', f'{m_ts*1000:.1f} g'], ['holder', f'{m_H*1000:.0f} g'], ['gel in the new tail\'s circuits', f'{V_pan*1000:.2f} L']],
         note='DexArm split: estimate. Shroud, frame and bosses: printed PETG, from their volumes.')]

# ---------------------------------------------------------------- 13. what the page draws
def box_item(c, s, yaw=0.0, m='print', link=None, ro=6.4, g='box', axis=None, edge=1):
    it = dict(g=g, c=[R4(v) for v in c], s=[R4(v) for v in s], yaw=R4(yaw), m=m, ro=ro, edge=edge)
    if link: it['link'] = link
    if axis: it['axis'] = axis
    return it
def boss_items(pid):
    if pid in MODS:
        n, pl = BOSS_AT[pid]; Wl = armW(QJ[pid])[n]; pad = (Wl @ pl)[:3]; link = n
    else:
        pad = PAD_L[pid]; link = None
    b = BETA[pid]; c, s = math.cos(b), math.sin(b)
    blk = pad + [c * (HOLD / 2), s * (HOLD / 2), -(BOSS['H'] - BOSS['pad_t']) / 2 - BOSS['pad_t']]
    return [box_item(blk, [BOSS['L'], BOSS['W'], BOSS['H'] - BOSS['pad_t']], b, 'print', link),
            box_item(pad - [0, 0, BOSS['pad_t'] / 2], [BOSS['pad_r'], BOSS['pad_t']], 0, 'steel', link, g='cyl', axis='z', edge=0),
            box_item(pad + [c * HOLD, s * HOLD, 0.0002], [BOSS['sock_r'] + 0.001, 0.0004], 0, 'dark', link, g='cyl', axis='z', edge=0)]
PDATA = {}
for k in ('M1', 'M2', 'M3', 'M4'):
    its = boss_items(k)
    if k == 'M1':
        its += [box_item([FRAME_C[0], 0, -FRAME['t'] / 2], [FRAME['L'], FRAME['W'], FRAME['t']], 0, 'print', 'B_Fix'),
                box_item([0.005, 0, SHROUD['H'] / 2], [SHROUD['L'], SHROUD['W'], SHROUD['H']], 0, 'shroud', 'B_Fix', ro=6.2),
                box_item([(BRACKET['x0'] + BRACKET['x1']) / 2, 0, BRACKET['z'] - BRACKET['t'] / 2], [BRACKET['x1'] - BRACKET['x0'], BRACKET['w'], BRACKET['t']], 0, 'print', 'B_Fix')]
        its += [box_item([BRACKET['x1'] - 0.004, sy * (BRACKET['w'] / 2 - 0.004), BRACKET['z'] / 2 - 0.003], [0.006, 0.006, BRACKET['z'] - 0.006], 0, 'print', 'B_Fix') for sy in (-1, 1)]
        for sy in (-1, 1):
            its.append(box_item([FRAME_C[0], sy * (FRAME['W'] / 2 + 0.005), -0.008 + FRAME['wheel_r']], [FRAME['wheel_r'], FRAME['wheel_w']], 0, 'dark', 'B_Fix', g='cyl', axis='y', edge=0))
            its.append(box_item([FRAME_C[0] - 0.02, sy * (FRAME['W'] / 2 - 0.012), 0.006], [0.026, 0.012, 0.010], 0, 'chip', 'B_Fix'))          # N20 gear motor
            for sx in (-1, 1): its.append(box_item([FRAME_C[0] + sx * (FRAME['L'] / 2 - 0.012), sy * (FRAME['W'] / 2 - 0.012), -FRAME['t'] - 0.002], [0.003, 0.004], 0, 'dark', 'B_Fix', g='cyl', axis='z', edge=0))      # pins into the floor sockets
    PDATA[k] = dict(kind='mod', label=MOD_NAME[k], q=[R4(v) for v in QJ[k]], links=MODS[k], items=its, mass=MASS[k] + m_boss, load_N=LOADS[k],
                    dims={'M1': 'base 146 x 128 x 159 mm on a 170 x 150 mm drive frame', 'M2': 'upper arm with the elbow block, 150 mm between its joints', 'M3': 'forearm, 151 mm between its joints', 'M4': 'end effector with the rotary flange'}[k])
# pack: three cells across, in a sleeve
pk_items = boss_items('P') + [box_item([0, 0, PACK['H'] / 2], [PACK['L'], PACK['W'], PACK['H']], 0, 'shroud', ro=6.2)]
for j in (-1, 0, 1): pk_items.append(box_item([0, j * 0.01875, 0.002 + 0.009375], [0.009375, 0.06525], 0, 'cell', g='cyl', axis='x', edge=0))
PDATA['P'] = dict(kind='pack', label='power pack', items=pk_items, mass=m_pack + m_boss, load_N=LOADS['P'], dims='3 x 18650 cells in series, 69 x 60 x 23 mm')
ts_items = [box_item([0, 0, TILE['t'] / 2], [TILE['L'], TILE['W'], TILE['t']], 0, 'tile', edge=0), box_item([0, 0, TILE['t'] + 0.0005], [0.010, 0.001], 0, 'steel', g='cyl', axis='z', edge=0)]
for nm, sz, (dx, dy) in TILE_PARTS:
    ts_items.append(box_item([dx + (0.0 if 'mp6' in nm else 0.0), dy, TILE['t'] + sz[2] / 2], sz, 0, 'pump' if 'mp6' in nm else 'chip', edge=0))
PDATA['TS'] = dict(kind='tiles', label='tile set', items=ts_items, mass=m_ts, load_N=LOADS['TS'], dims='46 x 32 mm cast tile: Core, two Sense, Power tiles, mp6 pump')
PDATA['H'] = dict(kind='holder', label='holder', items=[], mass=m_H, load_N=LOADS['H'], dims='electromagnet 20 x 15 mm, ball needle, crank, as the parent\'s')
# the tray: plinth, cradles, base bay rails, saddle; in the world
titems = [box_item(c, 2 * h, yaw, 'tray', ro=5) for nm, c, h, yaw in TRAYB]
for pid, items in CRADLE.items():
    for nm, c, h, yaw in items: titems.append(box_item(c, 2 * h, yaw, 'tray' if nm != 'ledge' else 'print', ro=5.2))
G = TRAY_G['TS']; titems.append(box_item((G @ np.r_[HOLD, 0, -0.004, 1])[:3], [0.004, 0.008], 0, 'dark', g='cyl', axis='z', edge=0))          # the well for the needle under the tile
# the seats in the new tail, in its frame: the pocket (lower skin in two strips round the slot, two lips) and the floor slots for the wheels
fitems = []
for name, c, h, yaw in pocket_boxes(np.array([0.0, 0.0, 0.0])):
    fitems.append(box_item(c, 2 * h, yaw, 'seat', ro=9.0))
for sy in (-1, 1):
    fitems.append(box_item([BASE_L[0] + FRAME_C[0], sy * (FRAME['W'] / 2 + 0.005), -0.0012], [0.05, 0.014, 0.0026], 0, 'dark', ro=8.9, edge=0))
PARFRAME = [box_item([BASE_L[0] + 0.005 - 0.14, 0, 0.0025], [0.46, 0.15, 0.005], 0, 'print'),
            box_item([BASE_L[0], 0, 0.006], [0.15, 0.13, 0.002], 0, 'steel')]
for xp_ in (-0.36, -0.17):
    for sy in (-1, 1): PARFRAME.append(box_item([xp_, sy * 0.072, 0.13], [0.008, 0.008, 0.25], 0, 'print'))
PARFRAME.append(box_item([-0.265, 0.072, 0.252], [0.20, 0.008, 0.008], 0, 'print')); PARFRAME.append(box_item([-0.265, -0.072, 0.252], [0.20, 0.008, 0.008], 0, 'print'))
for sy in (-1, 1): PARFRAME.append(box_item([BASE_L[0], sy * 0.083, 0.017], [0.017, 0.008], 0, 'dark', g='cyl', axis='y', edge=0))
BALLAST = dict(L=V_pan * 1000)

# ---------------------------------------------------------------- 14. schematic G-code for the print (as the quilted head simulator shows its own)
Gc = ['; Born, Not Made, tail copy variant: the next tail, printed whole, folded flat in the gel of the head',
      '; SCHEMATIC: lanes across the footprint of each layer of the 3 x 3 Z fold, not the toolpath of the quilt',
      '; frame: X toward the mouth, Y port, Z up, mm, origin on the docking plane of the head', 'G21', 'G90', 'M82']
GL = {}
for which, P in (('F', tb.PACK_F),):
    GL[which] = len(Gc); Gc.append(f'; ---- the new tail, whole: {P[0]*1000:.0f} x {P[1]*1000:.0f} x {P[2]*1000:.1f} mm, 18 layers')
    x0 = XPC * 1000 - P[0] * 500; y0 = -P[1] * 500; E = 0.0
    for L_ in range(18):
        z = tb.PITCH * 1000 * (L_ + 0.5) + 0.5; Gc.append(f'; layer z {z:.2f}')
        for k in range(10):
            y = y0 + 4 + (P[1] * 1000 - 8) * k / 9; xa, xb = (x0 + 3, x0 + P[0] * 1000 - 3) if k % 2 == 0 else (x0 + P[0] * 1000 - 3, x0 + 3)
            E += abs(xb - xa) * 0.0186
            Gc.append(f'G0 X{xa:.2f} Y{y:.2f} Z{z:.2f} F1800'); Gc.append(f'G1 X{xb:.2f} Y{y:.2f} Z{z:.2f} E{E:.2f} F1200')
    GL[which + '_end'] = len(Gc) - 1
open('tailcopy_print.gcode', 'w').write('\n'.join(Gc) + '\n')

# ---------------------------------------------------------------- 15. write
def enc_keys(name):
    idx = [k for k, c in enumerate(KEYC) if c == name]
    O = [KEYS[k][0] for k in idx]; Th = [KEYS[k][1] for k in idx]
    C = tb.CF
    return dict(idx=idx, na=C.na, nv=C.nv, si=C.si, sj=C.sj, data=qg.enc_delta16(O), th=qg.enc_u8(np.clip(np.round(np.array(Th) * 10000), 0, 255)))
out = dict(
    about='Born, Not Made, tail copy variant, round 2 (23 Nov 2026). Frame: x along the tank toward the head\'s mouth at the start, y port, z up, metres; z = 0 the inner floor of the bodies, the tank floor glass at -3 mm.',
    water=WL, gel=GEL, off=OFF, tank=TANK,
    bodies=dict(par=tb.enc_body(PAR), F=tb.enc_body(BF)),
    keys=dict(F=enc_keys('F'), child=KEYC),
    path=dict(x=[R4(x) for x in tb.PTS[:, 0]], z=[R4(x) for x in tb.PTS[:, 1]], d=[R4(x) for x in tb.PD], lip=tb.P_LIP),
    birth={k: {a: R4(b) for a, b in v.items()} for k, v in BIRTH.items()}, pack=dict(F=[R4(x) for x in tb.PACK_F]),
    stages=stages, fps=FPS, fr=frames, checks=checks, notes=notes,
    read=dict(pen_max=PEN_MAX, payload_N=PAY, mag_pad_N=MAG_PAD, sil=dict(F=sil_F)), order=['M1', 'P', 'M2', 'M3', 'M4', 'H', 'TS'], parts=PDATA,
    tray=dict(items=titems, cx=R4(np.mean([SLOT_X[k] for k in SLOT_X])), y0=0.357), fseat=dict(items=fitems, pocket=[R4(x) for x in pk_pt(R_IN)[:2]]), parframe=PARFRAME, ballast=BALLAST,
    masses=MASSES, text=TEXT, asm=[XA, YA], sources=SOURCES, pairs=[dict(name=k, mm=R4(v[0] * 1000), frame=v[1]) for k, v in PAIRS.items()], gcode_lines=GL, newpose=[R4(x) for x in POSE_NEW],
)
out['tank']['inner_mm'] = [round((TX1 - TX0) * 1000), round(2 * TY1 * 1000), 585]
s_ = json.dumps(out, separators=(',', ':'))
open('tailcopy.json', 'w').write(s_)
import collections; print('miss', len(miss), collections.Counter(m[1] for m in miss))
print('wrote tailcopy.json', len(s_) // 1024, 'kB,', len(frames), 'frames,', sum(s['disp'] for s in stages), 's')
for c in checks: print(('PASS ' if c['ok'] else 'FAIL ') + c['group'] + ': ' + c['name'][:160] + ('  [' + c['value'][:120] + ']' if c['value'] else ''))

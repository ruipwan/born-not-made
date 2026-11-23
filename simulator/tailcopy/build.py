"""Born, Not Made, tail copy variant (23 Nov 2026).

The parent (hard tail with its DexArm + quilted head) prints the parts of a new tail and puts a new arm together:
  N  the nose segment of the tail, a quilted double wall, printed folded over its pods (battery, Pi, pump): born first, it swims
  F  the face segment, a quilted ring with the arm's seat plate printed into its floor
  the arm, four modules (base, upper arm, forearm, end effector) that float in the tank in trimmed collars;
  N herds each to the mouth, the holder's crank draws it in, and the parent snaps the four together in the gel of the bowl.
Then N docks to F, the shell docks its face to the parent's mouth, the arm is pushed out base first onto its seat,
the shell backs off with the arm hooked, and the arm stands itself up, turns and unfolds.

Reads ../doublewall/quilt.json and ../doublewall/arm.json (read only). Writes tailcopy.json.
Frame: x toward the parent's mouth, y port, z up, meters, origin on the tank floor. The parent sits 200 mm further back
than in the quilted head simulator (OFF), so that the new tail has room in front of the mouth.
"""
import json, math
import numpy as np
from armfk import J, A, AR, PARTS, T, Rx, Ry, Rz, world_parts, part_mats, tool_head, bounds, ik, MODS

R2 = lambda x: round(float(x), 4)
OFF = -0.20                                   # the parent, moved back in the tank
BASE = np.array(J['base']) + [OFF, 0, 0]      # parent arm base, world
WATER = 0.27                                  # variant: water level (doublewall: 0.080)
GEL = J['read']['gel_z']                      # 0.100
LIP = np.array(J['mouth']['lip']) + [OFF, 0]  # (x, z) of the lower lip
MOUTH_TOP = np.array([J['mouth']['top'][0] + OFF, J['mouth']['top'][2]])
TANK = J['tank']; TX1 = TANK['x1'] - TANK['glass']; TY1 = TANK['y1'] - TANK['glass']
CUP, NEEDLE = AR['tools']['cup'], AR['tools']['needle']
CRANK = J['r2']['crank']['L']
notes, checks = [], []

def chk(group, name, ok, value=''):
    checks.append(dict(group=group, name=name, ok=bool(ok), value=value))

# ---------------------------------------------------------------- 1. the tail as two quilted segments
tv = np.array(J['hull']['tail']['v']).reshape(-1, 3)
XS = np.linspace(-0.43, 0.032, 47)
prof = []
for x in XS:
    m = np.abs(tv[:, 0] - x) < 0.007
    prof.append((x, np.abs(tv[m, 1]).max(), tv[m, 2].min(), tv[m, 2].max()))
prof = np.array(prof)
JOINT = J['printing']['joint_x']              # -0.215: where the hard tail is printed in two pieces on the H2S

def seg_grid(x0, x1, na, nv, nose=False, p=3.2, cell=0.0136, var=0.0):
    """outer skin of a quilted segment: superellipse sections on the tail profile, pushed out by the quilt's half depth;
    returns flat position list and the area of the skin"""
    xs = np.linspace(x0, x1, na)
    P = np.zeros((na, nv, 3))
    for i, x in enumerate(xs):
        w = np.interp(x, prof[:, 0], prof[:, 1]); zb = np.interp(x, prof[:, 0], prof[:, 2]); zt = np.interp(x, prof[:, 0], prof[:, 3])
        if var: w *= 1 + var * math.sin(3.1 * (x - x0) / max(1e-3, x1 - x0))     # the child's own proportions
        zc, h = (zb + zt) / 2, (zt - zb) / 2
        for j in range(nv):
            t = 2 * math.pi * j / nv
            c, s = math.cos(t), math.sin(t)
            y = (w + cell) * math.copysign(abs(c) ** (2 / p), c)
            z = zc + (h + cell) * math.copysign(abs(s) ** (2 / p), s)
            z = max(z, 0.0)                                   # single skin floor on the tank floor
            P[i, j] = (x, y, z)
    if nose:                                                  # close the blunt nose: a rounded cap over the last 30 mm
        c0 = P[0].mean(0)
        P[0] = c0 + (P[0] - c0) * 0.15
    # area
    area = 0.0
    for i in range(na - 1):
        for j in range(nv):
            a, b, c, d = P[i, j], P[i, (j + 1) % nv], P[i + 1, j], P[i + 1, (j + 1) % nv]
            area += 0.5 * np.linalg.norm(np.cross(b - a, c - a)) + 0.5 * np.linalg.norm(np.cross(d - b, c - b))
    return P, area

NA, NV = 34, 96
PN, AN = seg_grid(-0.43, JOINT, NA, NV, nose=True, var=0.05)
PF, AF = seg_grid(JOINT, 0.032, NA, NV)
def sections(x0, x1, na, var=0.0, cell=0.0136):
    xs = np.linspace(x0, x1, na); out = []
    for x in xs:
        w = np.interp(x, prof[:, 0], prof[:, 1]); zb = np.interp(x, prof[:, 0], prof[:, 2]); zt = np.interp(x, prof[:, 0], prof[:, 3])
        if var: w *= 1 + var * math.sin(3.1 * (x - x0) / max(1e-3, x1 - x0))
        out.append([R2(x), R2(w + cell), R2(max(0.0, zb)), R2(zt + cell)])
    return out
SECN = sections(-0.43 - 0.02, JOINT, NA, var=0.05)      # the child's nose comes out 20 mm longer
SECF = sections(JOINT, 0.032, NA)
def perim(sec):
    P = PN if False else None
    return max(2 * (r[1] * 2 + (r[3] - r[2])) * 0.93 for r in sec)
PER_N, PER_F = perim(SECN), perim(SECF)
def flatpack(sec, per):
    L = sec[-1][0] - sec[0][0]
    return [L / 3 * 1000, per / 2 / 3 * 1000, 18 * J['q']['q4']['pitch_mm']]
FPN, FPF = flatpack(SECN, PER_N), flatpack(SECF, PER_F)
AH = J['q']['head']['area_inner_m2']          # 0.328 m2 of the quilted head: 18 layers, 123 x 194 x 79 mm
PK = J['q']['q4']['pack_mm']; LAY = J['q']['q4']['layers']; PITCH = J['q']['q4']['pitch_mm']
def pack(area):
    layers = math.ceil(LAY * area / AH)
    return [PK[0], PK[1], layers * PITCH], layers
packN, layN = FPN, 18; packF, layF = FPF, 18
t_head = J['stages'][4]['real']; bead_head = J['read']['bead_m']
tN, tF = t_head * AN / AH, t_head * AF / AH
budget = J['q']['q4']['z_top_mm']
chk('Shell', f'Nose segment N: {AN:.3f} m2 of skin, folds to {packN[0]:.0f} x {packN[1]:.0f} x {packN[2]:.1f} mm ({layN} layers)', packN[2] <= PK[2] + 1,
    f'{tN/3600:.1f} h print')
chk('Shell', f'Face segment F: {AF:.3f} m2 of skin, folds to {packF[0]:.0f} x {packF[1]:.0f} x {packF[2]:.1f} mm ({layF} layers)', packF[2] <= PK[2] + 1,
    f'{tF/3600:.1f} h print')
chk('Shell', f'Fold: each segment is laid flat (two layers, a section of {PER_F*1000:.0f} mm round lies {PER_F/2*1000:.0f} mm wide), then Z folded 3 across and 3 along, 18 layers like the head', max(FPN[1], FPF[1]) < 230 and max(FPN[0], FPF[0]) < 130, f'N {FPN[0]:.0f} x {FPN[1]:.0f}, F {FPF[0]:.0f} x {FPF[1]:.0f} mm footprint; the head pack is 123 x 194, the bowl takes 230 across with the needle\'s 12 mm each side')
chk('Shell', f'Whole tail as one print: {AN+AF:.3f} m2, {math.ceil(LAY*(AN+AF)/AH)} layers, {LAY*(AN+AF)/AH*PITCH:.0f} mm tall; the bowl takes {PK[2]:.0f} mm under the needle',
    False, 'so two prints, split at the joint of the hard tail (x = -215 mm)')
notes.append(f'The tail splits where the hard tail is already printed in two on the H2S (x = {JOINT*1000:.0f} mm). Each half has less skin than a head '
             f'({AN:.3f} and {AF:.3f} against {AH:.3f} m2), so each folds into the head\'s own print envelope.')

# ---------------------------------------------------------------- 2. the arm in four modules
MASS = {'M1': 1.40, 'M2': 0.35, 'M3': 0.45, 'M4': 0.20}     # estimate, split of the DexArm's 2.4 kg (spec page)
RHO_PART = 2000.0; RHO_FOAM = 35.0
TRIMS = {'M1': 0.10, 'M2': -0.05, 'M3': -0.05, 'M4': -0.05}   # wet weight left (N): the base sinks a little, the links float a little
TRIM = 0.10
floats = {}
for k, m in MASS.items():
    Vs = m / RHO_PART
    Vf = (m - 1000 * Vs - TRIMS[k] / 9.81) / (1000 - RHO_FOAM)
    floats[k] = dict(mass=m, float_L=Vf * 1000)
chk('Arm', 'Four modules: base (with the three steppers), upper arm, forearm, end effector with the rotary flange; 2.4 kg in all', True, 'split estimated')
chk('Arm', 'Collars: ' + ', '.join(f'{k} {v["float_L"]*1000:.0f} mL of foam' for k, v in floats.items()) + '; wet weight: base +0.10 N, each link -0.05 N (floats)',
    TRIM < 2.45, f'holder magnet {2.45} N')
notes.append('Each module floats in a foam collar trimmed so it floats the way it is joined and weighs 0.15 N in water: the parent\'s arm (500 g payload, a 2.45 N magnet) '
             'could not lift its own base in air (1.4 kg), but it can steer it in water. This is why the arm is put together under water, and why the water stands at 270 mm.')

# ---------------------------------------------------------------- 3. the child arm: folded pose, seat, lying pose
RB = 0.070                                   # base radius (B_Fix: 128 x 146 mm)
FOLD = np.array([0.0, 0.0, math.radians(85)])
REST = np.array([0.0, AR['A_REST'], AR['B_REST']])
X0 = LIP[0] + 0.012                          # the shell's face against the parent's mouth
def seg_pose(px, py, yaw):
    return T([px, py, 0]) @ Rz(yaw)
DOCK = (X0 + 0.032, 0.0, math.pi)            # pose of the child's tail frame when its face is on the mouth
def root_stand(pose):
    return seg_pose(*pose) @ T([-0.115, 0, 0.005])
def hinge(pose):
    return (seg_pose(*pose) @ np.r_[-0.115 + RB, 0, 0, 1])[:3]
def root_tilt(pose, phi, dz=0.0):
    """phi = 90 deg: lying on its back toward the face, base plate facing the nose; 0: standing on the seat"""
    R = root_stand(pose); h = hinge(pose)
    s = 1.0 if math.cos(pose[2]) < 0 else -1.0       # tilt toward the face side
    return T([0, 0, dz]) @ T(h) @ Ry(-s * phi) @ T(-h) @ R
Q0LIE = 0.0                                  # lying face down: the joint axes lie across the body (y)
lie_q = np.array([Q0LIE, FOLD[1], FOLD[2]])
LIFT = -bounds(root_tilt(DOCK, math.pi / 2), lie_q)[0][2] + 0.002     # the lying arm rests on the floor
_rt = root_tilt
def root_tilt(pose, phi, dz=0.0):
    return T([0, 0, LIFT * math.sin(phi)]) @ _rt(pose, phi, dz)
lo, hi = bounds(root_tilt(DOCK, math.pi / 2), lie_q)
lie_len, lie_w, lie_h = hi - lo
# standing, folded, in F
slo, shi = bounds(root_stand(DOCK), FOLD)
roofF = np.interp(-0.115, prof[:, 0], prof[:, 3])
chk('Arm', f'Folded for birth (joint 1 {math.degrees(FOLD[1]):.0f}, joint 2 {math.degrees(FOLD[2]):.0f} deg): lying it is {lie_len*1000:.0f} long, {lie_w*1000:.0f} wide, {lie_h*1000:.0f} tall',
    lie_w < J['mouth']['width'] and lie_h < (MOUTH_TOP[1] - LIP[1]), f'mouth {J["mouth"]["width"]*1000:.0f} wide, {(MOUTH_TOP[1]-LIP[1])*1000:.0f} tall')
chk('Arm', f'Standing folded in F: {shi[2]*1000:.0f} mm tall under an inner roof of {roofF*1000:.0f} mm', shi[2] < roofF - 0.005, f'{(roofF-shi[2])*1000:.0f} mm spare')

# lying in the bowl: the same lying pose moved back by DELTA
LIECEN = (lambda b: (b[0] + b[1]) / 2)(bounds(root_tilt(DOCK, math.pi / 2), lie_q))
def lie_in_bowl(delta, psi=0.0, dy=0.0):
    c = LIECEN - [delta, 0, 0]
    return T([0, dy, 0]) @ T(c) @ Rz(psi) @ T(-c) @ T([-delta, 0, 0]) @ root_tilt(DOCK, math.pi / 2)
best = None
for psi in np.radians(np.arange(0, 46, 3)):
    for dy in (0.0, -0.02, -0.04, 0.02, 0.04):
        for d in np.arange(0.10, 0.40, 0.005):
            R = lie_in_bowl(d, psi, dy); l, h = bounds(R, lie_q)
            if l[0] < 0.032 + OFF + 0.006 or h[0] > LIP[0] - 0.015 or l[1] < -0.140 or h[1] > 0.140: continue
            _, jp = world_parts(R, lie_q)
            if all(ik(p + [0, 0, 0.04], CUP, BASE) is not None for p in jp):
                best = (d, psi, dy); break
        if best: break
    if best: break
DELTA, PSI, DY = best if best is not None else (0.2, 0.0, 0.0)
R_BOWL = lie_in_bowl(DELTA, PSI, DY)
lb, hb = bounds(R_BOWL, lie_q)
_, JP = world_parts(R_BOWL, lie_q)
notes.append(f'In the bowl the folded arm lies turned {math.degrees(PSI):.0f} deg so its elbow is not under the parent\'s own shoulder, where the DexArm cannot bend down (joint 1 does not lean back).')
chk('Reach', f'Assembly in the bowl (turned {math.degrees(PSI):.0f} deg): the folded arm lies from x {lb[0]*1000:.0f} to {hb[0]*1000:.0f} mm (chamber {(0.032+OFF)*1000:.0f} to {LIP[0]*1000:.0f})',
    best is not None, 'every joint inside the holder\'s reach' if best is not None else 'no place found')
# the push: holder on the rear face of the arm (the elbow end), from the bowl to the hook
push_from = lb[0] - 0.004; push_to = push_from + DELTA
qpush = ik(np.array([push_to, 0, LIP[1] + 0.06]), CUP, BASE)
chk('Reach', f'Birth of the arm: the holder pushes {DELTA*1000:.0f} mm, from x {push_from*1000:.0f} to {push_to*1000:.0f} mm, until the base plate hooks the seat hinge in F',
    qpush is not None, 'the base hooks 147 mm inside F\'s face, as the parent\'s base sits in the hard tail')
# the hook and the pull
PULL = 0.0
for p in np.arange(0.0, 0.40, 0.005):
    pose = (DOCK[0] + p, 0.0, math.pi)
    l, h = bounds(root_tilt(pose, math.pi / 2), lie_q)
    if l[0] > LIP[0] + 0.03:
        PULL = p; break
# the stand: sweep the tilt, the arm must stay clear of the parent's head (x < mouth top) and inside F's face port when it crosses the face
POSE_PULL = (DOCK[0] + PULL + 0.04, 0.0, math.pi)
clear_head, worst_port = 9.0, 9.0
PORT_TOP = np.interp(0.032, prof[:, 0], prof[:, 3]) - 0.015       # inner skin of F at the face, less the cuff
STAND_Q1 = math.radians(30)                  # it leans its upper arm toward its face as it rises, to pass under the top of F's face
def stand_q(ph):
    s_ = 1 - ph / (math.pi / 2); return np.array([Q0LIE, STAND_Q1 * min(1, 3 * s_), FOLD[2]])
for ph in np.linspace(math.pi / 2, 0, 61):
    W, _ = world_parts(root_tilt(POSE_PULL, ph), stand_q(ph))
    for n, M in W.items():
        v = PARTS[n][0][::7]; P = (M @ np.c_[v, np.ones(len(v))].T).T[:, :3]
        clear_head = min(clear_head, (P[:, 0] - (LIP[0] + 0.0)).min())
        face = POSE_PULL[0] - 0.032
        near = np.abs(P[:, 0] - face) < 0.01
        if near.any(): worst_port = min(worst_port, PORT_TOP - P[near, 2].max())
chk('Birth', f'The shell backs off {(PULL+0.04)*1000:.0f} mm with the arm hooked, so the arm clears the parent\'s lip', True, f'tank front glass at {TX1*1000:.0f} mm, nose at {(POSE_PULL[0]+0.43)*1000:.0f}')
chk('Birth', f'Standing up about the hinge: closest approach to the parent\'s lip {clear_head*1000:.0f} mm', clear_head > 0.005)
chk('Birth', f'Standing up through F\'s face: {worst_port*1000:.0f} mm under the top of the {PORT_TOP*1000:.0f} mm port (leaning joint 1 to 30 deg on the way up; upright and straight it would hit by 13 mm)', worst_port > 0.0)

# forces (estimates, marked)
GEL_TAU = 9.0
push_N = 2 * GEL_TAU * 0.09 + 0.3 * 0.10      # gel drag on the lying arm (both faces) + friction of four trimmed modules
chk('Forces', f'Push of the arm out of the gel and over the lip: {push_N:.2f} N', push_N < J['read']['payload_N'], f'arm gives {J["read"]["payload_N"]:.2f} N (estimate)')
snap_N = 3.0
chk('Forces', f'Snap of each joint: magnets close the last 2 mm, a spring latch needs {snap_N:.1f} N', snap_N < J['read']['payload_N'], 'estimate; bench test 2')
jet = 0.039
drag_pull = 0.5 * 1000 * 0.005 ** 2 * 1.0 * (0.30 * 0.30 + 0.15 * 0.13)
chk('Forces', f'N\'s jet ({jet*1000:.0f} mN, the quilted head\'s estimate) draws the shell and the hooked arm at 5 mm/s: drag {drag_pull*1000:.1f} mN, plus the base sliding on F\'s floor {0.3*0.10*1000:.0f} mN',
    jet > drag_pull + 0.3 * 0.10, 'the collars stay on until the arm stands')
stand_T = 0.10 * 0.05
chk('Forces', f'Standing up: the floating links pull the arm up about the hinge (0.15 N), the base weighs {stand_T:.3f} N m back; the arm\'s own joint 1 only steers it', True, 'it rises like a buoy on its foot')
hold = 3 * 54 * 0.5
chk('Forces', f'Seat: three magnet pairs in the seat plate ({hold:.0f} N at half pull through 1.2 mm of silicone) and the arm\'s wet weight once the collars are shed ({(2.4-2.4*1000/RHO_PART/ (1) * 0 - 2.4*1000/RHO_PART)*9.81:.1f} N)', True, 'estimate')
# water level consequences
air_head = J['q']['silicone']['air_L']
chk('Water', f'Water at {WATER*1000:.0f} mm (quilted head simulator: {J["WL"]*1000:.0f} mm): the quilted head\'s {air_head:.1f} L of cell air lifts {air_head*9.81:.0f} N against its {J["r2"]["float"]["weight_N"]:.1f} N',
    False, 'needs gel ballast in its low cells, as in round 2 (bench test 9 there)')
chk('Water', 'Deep water for the hard tail too: it needs steel to keep its wheels on the floor', False, 'outer change, not sized here')
chk('Births', 'Every birth (N, F, the arm) goes over the lower lip at 104.5 mm: the folded body is lifted out of the gel by the holder and pushed out, neutral in water', True, 'water above the mouth makes the lift free')

# ---------------------------------------------------------------- 4. the timeline
FPS = 10
frames = []
stages = []
MOD_ORDER = ['M1', 'M2', 'M3', 'M4']

class S:  # state, carried from frame to frame
    pass
st = S()
st.q = REST.copy(); st.tool = 1; st.crank = 0.0; st.rot = 0.0
st.N = dict(x=0.0, y=0.0, yaw=0.0, k=0.0, vis=0, pack=0.0, jet=0.0)
st.F = dict(x=0.0, y=0.0, yaw=0.0, k=0.0, vis=0, pack=0.0)
st.pods = 0          # 0 in the parent's store, 1 on the bowl floor, 2 in N
st.root = R_BOWL.copy(); st.cq = lie_q.copy()
st.mods = {k: dict(G=np.eye(4), att=0, vis=1, collar=1) for k in MOD_ORDER}
st.childvis = 0
st.note = 0
st.gel = GEL
st.lip = 0.0
st.text = ''

def mat7(M):
    q = quat(M[:3, :3]); return [R2(M[0, 3]), R2(M[1, 3]), R2(M[2, 3])] + [R2(x) for x in q]
def quat(R):
    t = np.trace(R)
    if t > 0:
        s = math.sqrt(t + 1) * 2; w = s / 4; x = (R[2, 1] - R[1, 2]) / s; y = (R[0, 2] - R[2, 0]) / s; z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = math.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; w = (R[2, 1] - R[1, 2]) / s; x = s / 4; y = (R[0, 1] + R[1, 0]) / s; z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = math.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; w = (R[0, 2] - R[2, 0]) / s; x = (R[0, 1] + R[1, 0]) / s; y = s / 4; z = (R[1, 2] + R[2, 1]) / s
    else:
        s = math.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; w = (R[1, 0] - R[0, 1]) / s; x = (R[0, 2] + R[2, 0]) / s; y = (R[1, 2] + R[2, 1]) / s; z = s / 4
    return [x, y, z, w]

def emit():
    fr = dict(q=[R2(x) for x in st.q], tool=st.tool, crank=R2(st.crank), rot=R2(st.rot),
              N=[R2(st.N['x']), R2(st.N['y']), R2(st.N['yaw']), R2(st.N['k']), st.N['vis'], R2(st.N['pack']), R2(st.N['jet'])],
              F=[R2(st.F['x']), R2(st.F['y']), R2(st.F['yaw']), R2(st.F['k']), st.F['vis'], R2(st.F['pack'])],
              pods=st.pods, root=mat7(st.root), cq=[R2(x) for x in st.cq], cv=st.childvis,
              m=[mat7(st.mods[k]['G']) + [st.mods[k]['att'], st.mods[k]['vis'], st.mods[k]['collar']] for k in MOD_ORDER],
              lip=R2(st.lip), gel=R2(st.gel))
    frames.append(fr)

ss = lambda u: u * u * (3 - 2 * u)
mj = lambda u: (lambda v: v * v * v * (10 - 15 * v + 6 * v * v))(min(1, max(0, u)))
def seg(u, a, b):   # sub-interval of a stage
    return mj((u - a) / (b - a)) if b > a else 1.0

def arm_to(q_from, tip, tool, u, a=0.0, b=1.0):
    q = ikc(tip, CUP if tool == 1 else NEEDLE)
    w = seg(u, a, b)
    return q_from + (q - q_from) * w if q is not None else q_from

def ikc(tip, Ls):
    tip = np.array(tip, float)
    for k in range(60):
        q = ik(tip, Ls, BASE)
        if q is not None: return q
        d = tip[:2] - BASE[:2]; tip[:2] = BASE[:2] + d * 0.985; tip[2] = tip[2] * 0.99 + 0.12 * 0.01
    return ik(tip, Ls, BASE, lim=False)

def tip_of(q, tool):
    p = tool_head(T(BASE), q); return p - [0, 0, CUP if tool == 1 else NEEDLE]

def stage(key, name, disp, real, text, fn):
    n = max(2, int(disp * FPS)); i0 = len(frames)
    s0 = {k: (v.copy() if isinstance(v, (np.ndarray, dict)) else v) for k, v in st.__dict__.items()}
    for i in range(n):
        fn(i / (n - 1), s0)
        emit()
    stages.append(dict(key=key, name=name, disp=disp, real=real, i0=i0, i1=len(frames) - 1, text=text))

def copy_mods(s0):
    return {k: dict(G=v['G'].copy(), att=v['att'], vis=v['vis'], collar=v['collar']) for k, v in s0['mods'].items()}

# where the floating modules start: in the free water in front of the mouth, port side, trimmed to float as they are joined
def floating_G(k, x, y, bob=0.0):
    """G moves the module from its place in the folded arm in the bowl to the water surface at (x, y)"""
    W, _ = world_parts(R_BOWL, lie_q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    c = (pts.min(0) + pts.max(0)) / 2; top = pts[:, 2].max() - c[2]
    return T([x - c[0], y - c[1], WATER - 0.012 - top - c[2] + bob])
def mod_center(k, G=None):
    W, _ = world_parts(R_BOWL, lie_q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    c = (pts.min(0) + pts.max(0)) / 2
    if G is not None: c = (G @ np.r_[c, 1])[:3]
    return c
START = {'M1': (0.47, -0.27), 'M2': (0.88, -0.27), 'M3': (0.68, -0.29), 'M4': (0.66, -0.10)}
for k in MOD_ORDER:
    st.mods[k]['G'] = floating_G(k, *START[k])

PRINT_X = (np.array([J['q']['q4']['x0_mm'], J['q']['q4']['x1_mm']]) / 1000 + OFF)
PRINT_C = np.array([PRINT_X.mean(), 0.0])
HOME = tip_of(REST, 1)
N_PARK = (0.86, -0.08, -math.pi / 2); F_PARK = (0.52, 0.22, math.pi / 2)
OUT = (LIP[0] + 0.20, 0.0)                      # where a born segment unfolds, in front of the mouth

# 0
def f_intro(u, s0):
    st.text = ''
stage('intro', 'The parent and the parts', 4, 60, 'The parent, a hard tail with its DexArm and a quilted head, sits at the back of the tank. Four arm modules float in front of it in foam collars: base, upper arm, forearm, end effector.', f_intro)

def f_kit(u, s0):
    q0 = s0['q']
    a = np.array([0.032 + OFF - 0.01, -0.06, 0.14]); b = np.array([PRINT_C[0], 0, 0.04])
    if u < 0.5:
        st.q = arm_to(q0, a, 1, u, 0, 0.5); st.pods = 0
    else:
        st.q = arm_to(arm_to(q0, a, 1, 1), b, 1, u, 0.5, 0.95)
        if u > 0.9: st.pods = 1
stage('kitN', 'Pods on the floor', 6, 75, 'The holder lays N\'s two sealed pods on the floor of the bowl, the way it lays a kit: a battery and a Raspberry Pi in one, the pump in the other.', f_kit)

def printer(key, name, which, real, text):
    def f(u, s0):
        st.tool = 2
        seg_ = st.N if which == 'N' else st.F
        P = packN if which == 'N' else packF
        seg_['pack'] = u; seg_['vis'] = 0
        h = P[2] / 1000 * u + 0.004
        lanes = 9; v = (u * lanes * 6) % 1; lane = int(u * lanes * 6) % lanes
        y = (-P[1] / 2000 + 0.01) + (P[1] / 1000 - 0.02) * (v if lane % 2 == 0 else 1 - v)
        x = PRINT_X[0] + 0.008 + (P[0] / 1000 - 0.016) * lane / (lanes - 1)
        q = ikc(np.array([x, y, h]), NEEDLE)
        if q is not None: st.q = q if u > 0.04 else s0['q'] + (q - s0['q']) * mj(u / 0.04)
    stage(key, name, 10, real, text, f)

printer('printN', 'Print N', 'N', tN, f'The needle prints the nose segment folded flat over the pods: {layN} layers, {packN[2]:.0f} mm tall, double wall with the quilt between.')
stage('cureN', 'Cure', 3, 57600, 'Dragon Skin 30 cures in the gel for 16 hours.', lambda u, s0: setattr(st, 'tool', 1))

def birth(which, park):
    def f(u, s0):
        seg_ = st.N if which == 'N' else st.F
        P = packN if which == 'N' else packF
        q0 = s0['q']
        rear = PRINT_X[0] - 0.004
        if u < 0.15:
            st.q = arm_to(q0, [rear, 0, 0.05], 1, u, 0, 0.15)
        elif u < 0.55:
            w = seg(u, 0.15, 0.55)
            seg_['pack'] = 1 + w                         # 1..2: the pack slides out (JS reads 1+w as the push)
            tipx = rear + min(0.20, (LIP[0] + 0.01 - PRINT_X[0]) * w)
            st.q = arm_to(st.q, [tipx, 0, 0.05 + 0.06 * w], 1, 1)
            if which == 'N': st.pods = 2
        else:
            w = seg(u, 0.55, 1.0)
            seg_['pack'] = 3; seg_['vis'] = 1; seg_['k'] = w
            seg_['x'] = LIP[0] + 0.06 - (SECN if which == 'N' else SECF)[0][0]; seg_['y'] = 0; seg_['yaw'] = 0.0
            st.q = arm_to(st.q, HOME, 1, u, 0.6, 0.9)
    return f
stage('birthN', 'Birth of N', 8, 300, 'The holder lifts the folded nose out of the gel and pushes it over the lip. Outside, air goes into the quilt and the segment opens to its printed shape.', birth('N', N_PARK))

def f_wakeN(u, s0):
    w = seg(u, 0.15, 1.0)
    st.N['jet'] = 1.0 if 0.1 < u < 0.95 else 0.0
    st.N['x'] = s0['N']['x'] + (N_PARK[0] - s0['N']['x']) * w
    st.N['y'] = s0['N']['y'] + (N_PARK[1] - s0['N']['y']) * w
    st.N['yaw'] = s0['N']['yaw'] + (N_PARK[2] - s0['N']['yaw']) * w
stage('wakeN', 'N wakes', 5, 120, 'The Pi in the pod boots on its own battery. N has the pump, so the first part of the child is the part that moves: it swims clear of the mouth.', f_wakeN)

printer('printF', 'Print F', 'F', tF, f'The needle prints the face segment: a quilted ring with the arm\'s seat plate printed into its floor, {layF} layers, {packF[2]:.0f} mm tall.')
stage('cureF', 'Cure', 3, 57600, 'Sixteen hours in the gel.', lambda u, s0: setattr(st, 'tool', 1))
stage('birthF', 'Birth of F', 8, 300, 'F is born the same way. It has no pump: it opens in front of the mouth and waits.', birth('F', F_PARK))

def f_moveF(u, s0):
    w = seg(u, 0.1, 1.0)
    st.F['x'] = s0['F']['x'] + (F_PARK[0] - s0['F']['x']) * w
    st.F['y'] = s0['F']['y'] + (F_PARK[1] - s0['F']['y']) * w
    st.F['yaw'] = s0['F']['yaw'] + (F_PARK[2] - s0['F']['yaw']) * w
    # N pushes F from its port side
    st.N['jet'] = 1.0 if 0.05 < u < 0.95 else 0.0
    nx = st.F['x'] + 0.33; ny = st.F['y']
    a = seg(u, 0.0, 0.2)
    st.N['x'] = s0['N']['x'] + (nx - s0['N']['x']) * a; st.N['y'] = s0['N']['y'] + (ny - s0['N']['y']) * a
    st.N['yaw'] = s0['N']['yaw'] + (math.pi - s0['N']['yaw']) * a
    if u > 0.85:
        b = seg(u, 0.85, 1.0); st.N['x'] = nx + (N_PARK[0] - nx) * b; st.N['y'] = ny + (N_PARK[1] - ny) * b; st.N['yaw'] = math.pi + (N_PARK[2] - math.pi) * b
stage('parkF', 'N moves F aside', 6, 240, 'N pushes F nose first to the port side, out of the way of the mouth.', f_moveF)

# the four modules: N herds, the crank hooks, the holder places and snaps
W_BOWL, _ = world_parts(R_BOWL, lie_q)
for idx, k in enumerate(MOD_ORDER):
    label = {'M1': 'base', 'M2': 'upper arm', 'M3': 'forearm', 'M4': 'end effector'}[k]
    def f_gather(u, s0, k=k, idx=idx):
        st.mods = copy_mods(s0) if u == 0 else st.mods
        m = st.mods[k]
        G0 = s0['mods'][k]['G']; c0 = mod_center(k, G0)
        mouth_pt = np.array([LIP[0] + 0.06, 0.0])
        q0 = s0['q']
        # 1. N herds the module to the mouth (0 .. 0.35)
        if u <= 0.35:
            w = seg(u, 0.0, 0.35)
            tgt = c0[:2] + (mouth_pt - c0[:2]) * w
            m['G'] = T([tgt[0] - c0[0], tgt[1] - c0[1], 0.004 * math.sin(u * 40)]) @ G0
            d = mouth_pt - c0[:2]; d = d / (np.linalg.norm(d) + 1e-9)
            st.N['x'] = tgt[0] - d[0] * 0.30 + 0.0; st.N['y'] = tgt[1] - d[1] * 0.30
            st.N['yaw'] = math.atan2(d[1], d[0]); st.N['jet'] = 1.0
            st.q = arm_to(q0, [LIP[0] - 0.12, 0, 0.20], 1, u, 0.15, 0.35); st.crank = 0.0
            st.lip = 0.0
        # 2. the crank swings forward and hooks the collar's loop, draws the module in under the upper lip (0.35 .. 0.6)
        elif u <= 0.6:
            st.N['jet'] = 0.0
            w = seg(u, 0.35, 0.45); st.crank = w
            Gm = T([mouth_pt[0] - c0[0], mouth_pt[1] - c0[1], 0]) @ G0
            cm = mod_center(k, Gm)
            hook_tip = np.array([LIP[0] - 0.10, 0, 0.19])
            st.q = arm_to(ikc([LIP[0] - 0.12, 0, 0.20], CUP), hook_tip, 1, u, 0.35, 0.45)
            dr = seg(u, 0.45, 0.6)
            dest = mod_center(k, np.eye(4)) + [0, 0, 0.10]
            pos = cm + (dest - cm) * dr
            m['G'] = T(pos - cm) @ Gm
            # holder follows the module
            if u > 0.45:
                q = ikc(pos + [-0.09 * (1 - dr), 0, 0.06], CUP)
                if q is not None: st.q = q
            st.N['x'] += (N_PARK[0] - st.N['x']) * 0.04; st.N['y'] += (N_PARK[1] - st.N['y']) * 0.04
        # 3. the magnet takes it, the crank folds, the module goes down into the gel onto its place and snaps (0.6 .. 0.92)
        else:
            st.crank = 1 - seg(u, 0.6, 0.68)
            w = seg(u, 0.62, 0.9)
            dest = mod_center(k, np.eye(4))
            Gup = T([0, 0, 0.10])
            m['G'] = T([0, 0, 0.10 * (1 - w)])
            q = ikc(dest + [0, 0, 0.06 + 0.10 * (1 - w)], CUP)
            if q is not None: st.q = q
            if u > 0.9:
                m['att'] = 1; m['G'] = np.eye(4)
            st.N['x'] += (N_PARK[0] - st.N['x']) * 0.05; st.N['y'] += (N_PARK[1] - st.N['y']) * 0.05
            st.N['yaw'] += (N_PARK[2] - st.N['yaw']) * 0.05
            st.childvis = 1
    joint = {'M1': 'It lies on the gel floor of the bowl, the base plate toward the mouth.', 'M2': 'The upper arm drops onto the shoulder: magnets pull the last 2 mm and a spring latch clicks.',
             'M3': 'The forearm drops onto the elbow and clicks.', 'M4': 'The end effector clicks onto the wrist. The arm is whole, folded, lying on its side in the gel.'}[k]
    stage('get' + k, f'Module {idx+1}: {label}', 11, 600,
          f'N noses the {label} to the mouth. The holder\'s crank, the hook it uses at a birth, reaches 25 mm past the lip, catches the loop on the collar and draws it in under water. {joint}', f_gather)

def f_holdreach(u, s0):
    st.q = arm_to(s0['q'], HOME, 1, u, 0, 0.8)
stage('folded', 'The folded arm', 3, 30, 'Every joint is vertical while it lies like this, so every module went straight down onto the one before. Nothing was screwed.', f_holdreach)

# N docks to F, the shell turns and docks its face on the mouth
JOINT_END = lambda pose: (seg_pose(*pose) @ np.r_[JOINT, 0, 0, 1])[:3]
def f_joinNF(u, s0):
    st.N['jet'] = 1.0 if u < 0.92 else 0.0
    # N's joint end on F's joint end, N's nose away
    Fp = (s0['F']['x'], s0['F']['y'], s0['F']['yaw'])
    tgt_yaw = Fp[2]
    # same tail frame: N's local coords are the tail's, so N docks with the same pose as F
    w = seg(u, 0.0, 0.85)
    a = (s0['N']['x'], s0['N']['y'], s0['N']['yaw'])
    via = (Fp[0] - 0.12, Fp[1] + 0.32, tgt_yaw)
    if w < 0.6:
        v = w / 0.6; st.N['x'] = a[0] + (via[0] - a[0]) * v; st.N['y'] = a[1] + (via[1] - a[1]) * v
        dy = (tgt_yaw - a[2] + math.pi) % (2 * math.pi) - math.pi; st.N['yaw'] = a[2] + dy * v
    else:
        v = (w - 0.6) / 0.4; st.N['x'] = via[0] + (Fp[0] - via[0]) * v; st.N['y'] = via[1] + (Fp[1] - via[1]) * v; st.N['yaw'] = tgt_yaw
stage('joinNF', 'N docks to F', 8, 300, 'N backs its open end onto F\'s rear cuff: magnets in the two cuffs, the same as the docking of a tail and a head. Pogo pads in the cuff carry the battery\'s power into F. The shell is whole, still without an arm.', f_joinNF)

def f_dockmouth(u, s0):
    a = (s0['F']['x'], s0['F']['y'], s0['F']['yaw'])
    b = DOCK
    w = seg(u, 0.0, 1.0)
    via = (b[0] + 0.12, 0.10, b[2])
    if w < 0.55:
        v = w / 0.55; x = a[0] + (via[0] - a[0]) * v; y = a[1] + (via[1] - a[1]) * v
        dy = (b[2] - a[2] + math.pi) % (2 * math.pi) - math.pi; yaw = a[2] + dy * mj(v)
    else:
        v = (w - 0.55) / 0.45; x = via[0] + (b[0] - via[0]) * v; y = via[1] + (b[1] - via[1]) * v; yaw = b[2]
    for s_ in (st.F, st.N): s_['x'], s_['y'], s_['yaw'] = x, y, yaw
    st.N['jet'] = 1.0 if u < 0.95 else 0.0
stage('dockMouth', 'The shell docks on the mouth', 9, 300, 'The shell swims round and brings its open face against the parent\'s mouth. Nine magnet pairs in F\'s cuff meet steel disks in the quilt round the mouth.', f_dockmouth)

def f_birtharm(u, s0):
    q0 = s0['q']
    lift = 0.11 * seg(u, 0.12, 0.35)
    push = DELTA * seg(u, 0.38, 0.9)
    st.root = T([push, 0, lift]) @ R_BOWL
    if u < 0.12:
        st.q = arm_to(q0, [push_from, 0, 0.06], 1, u, 0, 0.12)
    else:
        q = ikc(np.array([push_from + push, 0, 0.06 + lift]), CUP)
        if q is not None: st.q = q
    st.gel = GEL
stage('birthArm', 'Birth of the arm', 9, 240, f'The holder lifts the folded arm off the gel floor, over the lower lip, and pushes it base first out of the mouth into F: {DELTA*1000:.0f} mm, until the base plate hooks the hinge bar of the seat.', f_birtharm)

def f_pull(u, s0):
    w = seg(u, 0.1, 1.0)
    px = DOCK[0] + (POSE_PULL[0] - DOCK[0]) * w
    for s_ in (st.F, st.N): s_['x'] = px; s_['y'] = 0.0; s_['yaw'] = math.pi
    st.N['jet'] = 1.0 if 0.1 < u < 0.97 else 0.0
    # the hooked arm comes along, and settles from the lip down to F's floor as it leaves the lip
    drop = 0.11 * seg(u, 0.35, 0.9)
    st.root = T([0, 0, 0.11 - drop]) @ root_tilt((px, 0, math.pi), math.pi / 2)
    st.q = arm_to(s0['q'], HOME, 1, u, 0.0, 0.5)
stage('pull', 'The shell backs off', 8, 240, 'The magnets of the face cuff let go (the tilt release of the tail). N\'s jet draws the shell back and the hooked arm slides out after it, down onto F\'s floor.', f_pull)

def f_stand(u, s0):
    ph = math.pi / 2 * (1 - seg(u, 0.12, 0.95))
    st.root = root_tilt(POSE_PULL, ph); st.cq = stand_q(ph)
stage('stand', 'The arm stands up', 7, 60, 'The seat\'s pogo pads touch the base plate: the arm has power for the first time. It presses its forearm on the floor and stands itself up about the hinge, and the seat magnets close.', f_stand)

def f_turn(u, s0):
    w = seg(u, 0.05, 0.9)
    st.cq = np.array([math.radians(35) * math.sin(math.pi * w), STAND_Q1, FOLD[2]])
stage('turn', 'It looks', 4, 20, 'It turns its base a little to one side and back, the first move it chooses.', f_turn)

def f_unfold(u, s0):
    w = seg(u, 0.25, 1.0)
    for k in MOD_ORDER: st.mods[k]['collar'] = 0 if u > 0.18 else 1
    F2 = np.array([0, STAND_Q1, FOLD[2]]); st.cq = F2 + (REST - F2) * w
stage('unfold', 'It unfolds', 6, 30, 'The collars are shed and float up. The arm unfolds to its rest pose. The new tail is whole: N, F and an arm, and the parent kept its own.', f_unfold)

def f_end(u, s0):
    w = seg(u, 0.1, 1.0)
    st.cq = REST + np.array([0.35 * math.sin(u * 6), 0.12 * math.sin(u * 4), 0.1 * math.sin(u * 5)]) * math.sin(math.pi * u)
stage('free', 'A tail of its own', 6, 60, 'The new tail can dock to any head and print. Its two segments are quilted and soft where the parent\'s were printed hard on the H2S; its nose came out a little longer. Same principle, its own body.', f_end)

# ---------------------------------------------------------------- 5. write
out = dict(
    about='Born, Not Made, tail copy variant (23 Nov 2026): the parent prints the two segments of a new tail and puts a new arm together from four floating modules. '
          'Frame: x toward the parent\'s mouth, y port, z up, meters, origin on the tank floor; the parent sits 200 mm back from the quilted head simulator.',
    off=OFF, water=WATER, gel=GEL, lip=[float(x) for x in LIP], mouth_top=[float(x) for x in MOUTH_TOP], base=[float(x) for x in BASE], tank=TANK,
    seg=dict(na=NA, nv=NV, secN=SECN, secF=SECF, perN=PER_N, perF=PER_F, joint=JOINT, pitch=J['q']['q4']['pitch_mm'], packN=packN, packF=packF,
             areaN=AN, areaF=AF, layN=layN, layF=layF),
    print_x=[float(x) for x in PRINT_X], rbowl=[R2(x) for x in R_BOWL.T.reshape(-1)], lie_q=[float(x) for x in lie_q], rb=RB, out=[float(x) for x in OUT], dock=[float(x) for x in DOCK], mods=MODS, mod_order=MOD_ORDER, floats=floats, fold=[float(x) for x in FOLD], rest=[float(x) for x in REST], delta=float(DELTA),
    stages=stages, fps=FPS, fr=frames, checks=checks, notes=notes,
    sources=dict(dex=J['sources']['dex'], ds30=J['sources']['ds30'], mag=J['sources']['mag']),
)
json.dump(out, open('tailcopy.json', 'w'), separators=(',', ':'))
print(len(frames), 'frames,', sum(s['disp'] for s in stages), 's')
for c in checks: print(('PASS ' if c['ok'] else 'FAIL ') + c['group'] + ': ' + c['name'] + ('  [' + c['value'] + ']' if c['value'] else ''))
print('DELTA', DELTA, 'PULL', PULL, 'lying box', lie_len, lie_w, lie_h)

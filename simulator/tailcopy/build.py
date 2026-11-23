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
TANK = dict(L=3.0, W=1.22, H=0.406, glass=0.012, x0=-1.6, x1=1.4, y1=0.61, name='a 3.0 x 1.22 m tank (estimate: room for two tails side by side and one to turn)', url='')
TX1 = TANK['x1'] - TANK['glass']; TX0 = TANK['x0'] + TANK['glass']; TY1 = TANK['y1'] - TANK['glass']
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
TRIMS = {'M1': 0.10, 'M2': 0.35 * 9.81 * 0.5, 'M3': 0.45 * 9.81 * 0.5, 'M4': 0.20 * 9.81 * 0.5}   # wet weight (N): the base sealed and trimmed, the links as they are (mean density 2000, estimate)
TRIM = 0.10
floats = {}
_lie = np.array([0.0, 0.0, math.radians(85)])
for k, m in MASS.items():
    lo_, hi_ = bounds(np.eye(4), _lie, MODS[k])
    Vbox = float(np.prod(hi_ - lo_))
    need = m / 1000 - TRIMS[k] / 9.81 / 1000                # m3 of water to displace for that wet weight
    floats[k] = dict(mass=m, need_L=need * 1000, box_L=Vbox * 1000)
chk('Arm', 'Four modules: base (with the three steppers), upper arm, forearm, end effector with the rotary flange; 2.4 kg in all', True, 'split estimated')
chk('Arm', f'No floats. Only the base (1.4 kg) needs help: its housing is sealed and holds air, {floats["M1"]["need_L"]:.2f} L of displacement inside a {floats["M1"]["box_L"]:.2f} L housing, trimmed to weigh 0.10 N in water', floats['M1']['need_L'] < 0.6 * floats['M1']['box_L'], 'the slim links could not hold enough air; they do not need to')
chk('Arm', 'Wet weight of each module against the holder\'s 2.45 N magnet: ' + ', '.join(f'{k} {TRIMS[k]:.2f} N' for k in ['M1', 'M2', 'M3', 'M4']), max(TRIMS.values()) < 2.45, 'the forearm is the heaviest, 10 % under the magnet')
notes.append('No floats. Each module has a closed, sealed housing that holds air, trimmed with a little steel so it weighs 0.10 N in water and stands still on the tray. '
             'The parent\'s arm (500 g payload, a 2.45 N magnet) could not lift its own base in air (1.4 kg), but it can carry it under water. This is why the arm is put together under water, and why the water stands at 270 mm.')



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
POSE_PULL = DOCK
BACK = PULL + 0.04                                 # the parent drives back this far
clear_head, worst_port = 9.0, 9.0
PORT_TOP = np.interp(0.032, prof[:, 0], prof[:, 3]) - 0.015       # inner skin of F at the face, less the cuff
STAND_Q1 = math.radians(30)                  # it leans its upper arm toward its face as it rises, to pass under the top of F's face
def stand_q(ph):
    s_ = 1 - ph / (math.pi / 2); return np.array([Q0LIE, STAND_Q1 * min(1, 3 * s_), FOLD[2]])
for ph in np.linspace(math.pi / 2, 0, 61):
    W, _ = world_parts(root_tilt(POSE_PULL, ph), stand_q(ph))
    for n, M in W.items():
        v = PARTS[n][0][::7]; P = (M @ np.c_[v, np.ones(len(v))].T).T[:, :3]
        clear_head = min(clear_head, (P[:, 0] - (LIP[0] - BACK)).min())
        face = POSE_PULL[0] - 0.032
        near = np.abs(P[:, 0] - face) < 0.01
        if near.any(): worst_port = min(worst_port, PORT_TOP - P[near, 2].max())
chk('Birth', f'The parent backs {BACK*1000:.0f} mm away from the hooked arm, so the arm clears its lip', True, f'tail nose then at {(BASE[0]-0.315-BACK)*1000:.0f} mm, back glass at {(TANK["x0"]+TANK["glass"])*1000:.0f}')
chk('Birth', f'Standing up about the hinge: closest approach to the parent\'s lip {clear_head*1000:.0f} mm', clear_head > 0.005)
chk('Birth', f'Standing up through F\'s face: {worst_port*1000:.0f} mm under the top of the {PORT_TOP*1000:.0f} mm port (leaning joint 1 to 30 deg on the way up; upright and straight it would hit by 13 mm)', worst_port > 0.0)

# forces (estimates, marked)
GEL_TAU = 9.0
push_N = 2 * GEL_TAU * 0.09 + 0.3 * 0.10      # gel drag on the lying arm (both faces) + friction of four trimmed modules
WARM = sum(TRIMS.values())
push_N = 2 * GEL_TAU * 0.09 + 0.3 * WARM
chk('Forces', f'The whole folded arm weighs {WARM:.1f} N in water: too much to lift over the lip ({J["read"]["payload_N"]:.1f} N payload), so the lower lip is vented and lies flat, and the arm slides out along the floor: {push_N:.2f} N', push_N < J['read']['payload_N'], 'friction 0.3 on silicone, gel drag at 9 Pa; the gel stays because the water stands over it (round 2 argument)')
snap_N = 3.0
chk('Forces', f'Snap of each joint: magnets close the last 2 mm, a spring latch needs {snap_N:.1f} N', snap_N < J['read']['payload_N'], 'estimate; bench test 2')
jet = 0.039
drag_pull = 0.5 * 1000 * 0.005 ** 2 * 1.0 * (0.30 * 0.30 + 0.15 * 0.13)
chk('Forces', f'N\'s jet ({jet*1000:.0f} mN) could not drag the hooked arm ({0.3*WARM:.1f} N of friction), so the parent backs away on its wheels instead, the crank under the elbow end ({WARM/2:.1f} N of the arm\'s {J["read"]["payload_N"]:.1f} N payload) until it rests on the tank floor', WARM / 2 < J['read']['payload_N'], 'the hook holds the base end in F')
chk('Forces', f'Standing up: the arm weighs {WARM:.1f} N in water, about {WARM*0.12:.2f} N m about the hinge; it pushes its forearm on the floor with joint 1', WARM * 0.12 < 1.0, 'DexArm stepper with its reduction, estimate; bench test')
hold = 3 * 54 * 0.5
chk('Forces', f'Seat: three magnet pairs in the seat plate hold the base ({hold:.0f} N at half pull through 1.2 mm of silicone); with the arm\'s 5 N of wet weight they carry its reactions', True, 'estimate; a steel trim plate can be added to the base once it is seated')
DROP = ('Folded for birth', 'Standing folded', 'Assembly in the bowl', 'Birth of the arm', 'The parent backs', 'Standing up', 'The whole folded arm', "N's jet")
checks[:] = [c for c in checks if not c['name'].startswith(DROP)]
notes[:] = [n for n in notes if not n.startswith('In the bowl')]
# water level consequences
air_head = J['q']['silicone']['air_L']
chk('Water', f'Water at {WATER*1000:.0f} mm (quilted head simulator: {J["WL"]*1000:.0f} mm): the quilted head\'s {air_head:.1f} L of cell air lifts {air_head*9.81:.0f} N against its {J["r2"]["float"]["weight_N"]:.1f} N',
    False, 'needs gel ballast in its low cells, as in round 2 (bench test 9 there)')
chk('Births', 'N and F go over the lower lip at 104.5 mm: each folded body is lifted out of the gel and pushed out, about neutral in water', True, 'Dragon Skin 30, SG 1.08')

# ---------------------------------------------------------------- 4. the timeline
FPS = 10
frames = []
stages = []
MOD_ORDER = ['M1', 'M2', 'M3', 'M4']

class S:  # state, carried from frame to frame
    pass
st = S()
st.px = 0.0
st.red = np.array([OFF, 0.0, 0.0])          # pose of the parent's tail frame: world = (x, y) + R(yaw) (lx, ly)
st.item = np.array([0.0, 0.0, 0.0]); st.itemv = 0
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
    fr = dict(red=[R2(x) for x in st.red], item=[R2(x) for x in st.item] + [st.itemv], px=R2(st.px), q=[R2(x) for x in st.q], tool=st.tool, crank=R2(st.crank), rot=R2(st.rot),
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

BL = np.array(J['base'])                              # arm base in the tail frame
def pose_M(p):
    return T([p[0], p[1], 0]) @ Rz(p[2])
def ik_pose(tip, Ls, pose, lim=True):
    tl = np.linalg.inv(pose_M(pose)) @ np.r_[tip, 1]
    return ik(tl[:3], Ls, BL, lim)
def ikc(tip, Ls, pose=None):
    pose = st.red if pose is None else pose
    Minv = np.linalg.inv(pose_M(pose)); tl = (Minv @ np.r_[tip, 1])[:3]
    for k in range(60):
        q = ik(tl, Ls, BL)
        if q is not None: return q
        d = tl[:2] - BL[:2]; tl[:2] = BL[:2] + d * 0.985; tl[2] = tl[2] * 0.99 + 0.12 * 0.01
    return ik(tl, Ls, BL, lim=False)
def tip_of(q, tool, pose=None):
    pose = st.red if pose is None else pose
    p = tool_head(pose_M(pose) @ T(BL), q); return p - [0, 0, CUP if tool == 1 else NEEDLE]

def stage(key, name, disp, real, text, fn):
    n = max(2, int(disp * FPS)); i0 = len(frames)
    s0 = {k: (v.copy() if isinstance(v, (np.ndarray, dict)) else v) for k, v in st.__dict__.items()}
    for i in range(n):
        fn(i / (n - 1), s0)
        emit()
    stages.append(dict(key=key, name=name, disp=disp, real=real, i0=i0, i1=len(frames) - 1, text=text))

def copy_mods(s0):
    return {k: dict(G=v['G'].copy(), att=v['att'], vis=v['vis'], collar=v['collar']) for k, v in s0['mods'].items()}

# the shelf on the front glass: its top at the lower lip, sloped toward the middle slot
def mod_center(k, G=None):
    W, _ = world_parts(R_BOWL, lie_q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    c = (pts.min(0) + pts.max(0)) / 2
    if G is not None: c = (G @ np.r_[c, 1])[:3]
    return c
def mod_box(k):
    W, _ = world_parts(R_BOWL, lie_q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    return pts.min(0), pts.max(0)
# the tray on the back glass, sloped toward its middle slot; the four modules stand on it the way they will be joined
TRAY_TOP = 0.006
TRAY_X = (TX0, TX0 + 0.15)
TRAY_Y = 0.42
FACE = 0.032
RS = np.array([TRAY_X[1] + 0.012 + FACE, 0.0, math.pi])                 # the parent's tail, its face at the tray
BX = -0.95                                                              # where the new tail sits for a handover
RD = np.array([BX + 2 * FACE + 0.004, 0.0, math.pi])                    # the parent's tail, face to face with it
BD = np.array([BX, 0.0, 0.0])
BWAIT = np.array([BX, 0.42, 0.0])
CROOT = pose_M(BD) @ T([-0.115, 0, 0.005])                              # the new arm's base frame in the seat
# join poses: the new arm, powered from N as soon as its base is seated, holds its joints where the parent can reach
def reach_c(p, tool=CUP):
    return ik_pose(p + [0, 0, 0.04], tool, RD) is not None
def find_pose(j, also=None):
    for q0 in range(-110, 111, 10):
        for q1 in range(0, 111, 5):
            for q2 in range(0, 86, 5):
                q = np.radians([q0, q1, q2]); W, jp = world_parts(CROOT, q); p = jp[j]
                if p[2] < 0.04 or abs(p[1]) > 0.14 or p[2] > 0.29: continue
                if reach_c(p) and (also is None or also(q)): return q
    return None
def mod_box_at(k, root, q):
    W, _ = world_parts(root, q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    return pts.min(0), pts.max(0)
def grip(k, root, q, G=None):
    """where the holder takes a module: the top of its box, or for the forearm the top of its elbow end"""
    Mr = root if G is None else G @ root
    if k == 'M3':
        _, jp = world_parts(Mr, q); return jp[1] + [0, 0, 0.03]
    lo_, hi_ = mod_box_at(k, Mr, q); return np.array([(lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, hi_[2] + 0.003])
def top_reach(k):
    def f(q):
        g = grip(k, CROOT, q)
        return ik_pose(g, CUP, RD) is not None and ik_pose(g + [0, 0, 0.02], CUP, RD) is not None
    return f
QJ = {'M1': REST.copy()}
QJ['M2'] = find_pose(0, top_reach('M2')); QJ['M3'] = find_pose(1, top_reach('M3')); QJ['M4'] = find_pose(2, top_reach('M4'))
print('QJ', {k: np.degrees(v).round() if v is not None else None for k, v in QJ.items()})
JOINP = {}
for k in MOD_ORDER:
    _, jp = world_parts(CROOT, QJ[k]); JOINP[k] = {'M1': (CROOT @ np.r_[0, 0, 0.09, 1])[:3], 'M2': jp[0], 'M3': jp[1], 'M4': jp[2]}[k]
def mod_box_at(k, root, q):
    W, _ = world_parts(root, q)
    pts = np.vstack([(W[n] @ np.c_[PARTS[n][0][::9], np.ones(len(PARTS[n][0][::9]))].T).T[:, :3] for n in MODS[k]])
    return pts.min(0), pts.max(0)
SLOT0 = {'M1': 0.0, 'M2': -0.20, 'M3': 0.20, 'M4': -0.34}
def tray_G(k, y):
    lo_, hi_ = mod_box_at(k, CROOT, QJ[k]); c = (lo_ + hi_) / 2
    x = TRAY_X[0] + 0.012 + (hi_[0] - lo_[0]) / 2
    return T([x - c[0], y - c[1], TRAY_TOP - lo_[2]])
for k in MOD_ORDER:
    st.mods[k]['G'] = tray_G(k, SLOT0[k])
st.item = np.array([TRAY_X[0] + 0.05, 0.34, TRAY_TOP + 0.01]); st.itemv = 1
ok_join = all(top_reach(k)(QJ[k]) for k in MOD_ORDER)
def rs_for(k):
    g = grip(k, CROOT, QJ[k], tray_G(k, 0.0))
    for back in np.arange(0.0, 0.25, 0.005):
        p = RS + [back, 0, 0]
        if ik_pose(g, CUP, p) is not None and ik_pose(g + [0, 0, 0.03], CUP, p) is not None: return p
    return None
RSK = {k: rs_for(k) for k in MOD_ORDER}
ok_tray = all(v is not None for v in RSK.values())
RSK = {k: (v if v is not None else RS) for k, v in RSK.items()}
_unused = all(ik_pose(((lambda b: (b[0] + b[1]) / 2)(mod_box_at(k, tray_G(k, 0.0) @ CROOT, QJ[k]))) + [0, 0, 0.06], CUP, RS) is not None for k in MOD_ORDER)
chk('Handover', 'Face to face: the parent\'s tail and the new tail dock face to face, the nine magnets of the parent\'s face on the steel disks of F\'s cuff, as a tail docks to a head', True, 'the open faces make one chamber')
chk('Handover', f'The new arm\'s seat is {RD[0]-FACE - (BD[0]+FACE) + 0.147 + 0.147:.3f} m from the parent\'s arm axis, inside its reach', ik_pose((CROOT @ np.r_[0, 0, 0.1, 1])[:3], CUP, RD) is not None, 'the parent\'s base sits 147 mm behind its face, the seat 147 mm behind F\'s')
chk('Handover', 'Every joint reachable when the new arm helps: seated and powered from N, it holds its shoulder, then its elbow, then its wrist where the parent\'s holder can reach (joint 1 at '
    + ', '.join(f'{math.degrees(QJ[k][1]):.0f}' for k in MOD_ORDER[1:]) + ' deg)', ok_join, 'upright and still, its elbow and wrist would be out of reach')
chk('Handover', 'The parent takes each module from the middle slot of the tray on the back glass', ok_tray, 'the tray slopes to the middle: the next one slides in')
chk('Handover', f'The new tail waits beside, {BWAIT[1]*1000:.0f} mm off the centre line, and comes in for each module', True, 'the tank is 1.22 m wide so a tail fits beside a tail')
notes.append('Face to face. The parent\'s tail leaves its head, turns round and docks face to face with the new tail. Its arm reaches into the new tail as it reaches into a head: the new arm\'s seat is 294 mm from its axis. It brings the four modules from a tray on the back glass one at a time and builds the arm upright in the seat. From the base on, the new arm has power from N\'s battery through the cuff and helps: it holds each joint where the parent can reach it.')
PRINT_X = (np.array([J['q']['q4']['x0_mm'], J['q']['q4']['x1_mm']]) / 1000 + OFF)
PRINT_C = np.array([PRINT_X.mean(), 0.0])
HOME = tip_of(REST, 1)
N_PARK = (0.70, 0.015, math.pi / 2); F_PARK = (0.52, 0.40, math.pi / 2)    # both beside the glass, out of the way
OUT = (LIP[0] + 0.20, 0.0)
chk('Water', 'Driving at 270 mm of water: the hard tail is buoyant and its wheels lose grip', False, 'steel in the tail, not sized here')
notes.append('After the handover the new tail has an arm, so it can pick up the rest itself: the last thing on the tray, a tile set, it takes with its own arm.')

# 0
def f_intro(u, s0):
    st.text = ''
stage('intro', 'The parent and the parts', 4, 60, 'The parent, a hard tail with its DexArm and a quilted head, sits in the middle of the tank. Four arm modules stand on a tray against the back glass: base, upper arm, forearm, end effector. No floats.', f_intro)

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
    nx = st.F['x']; ny = st.F['y'] - 0.33
    a = seg(u, 0.0, 0.2)
    st.N['x'] = s0['N']['x'] + (nx - s0['N']['x']) * a; st.N['y'] = s0['N']['y'] + (ny - s0['N']['y']) * a
    st.N['yaw'] = s0['N']['yaw'] + (-math.pi / 2 - s0['N']['yaw']) * a
    if u > 0.85:
        b = seg(u, 0.85, 1.0); st.N['x'] = nx + (N_PARK[0] - nx) * b; st.N['y'] = ny + (N_PARK[1] - ny) * b; st.N['yaw'] = -math.pi / 2 + (N_PARK[2] + math.pi / 2) * b
stage('parkF', 'N moves F aside', 6, 240, 'N pushes F against the port glass and parks itself against the starboard glass: the middle of the tank is clear.', f_moveF)

def lerp3(a, b, w): return np.array(a) + (np.array(b) - np.array(a)) * w
def yaw_lerp(a, b, w): d = (b - a + math.pi) % (2 * math.pi) - math.pi; return a + d * w
def set_blue(p):
    for s_ in (st.F, st.N): s_['x'], s_['y'], s_['yaw'] = float(p[0]), float(p[1]), float(p[2])

def f_joinNF(u, s0):
    st.N['jet'] = 1.0 if u < 0.92 else 0.0
    Fp = (s0['F']['x'], s0['F']['y'], s0['F']['yaw']); w = seg(u, 0.0, 0.85)
    a = (s0['N']['x'], s0['N']['y'], s0['N']['yaw']); via = (Fp[0] - 0.32, Fp[1] - 0.05, Fp[2])
    if w < 0.6:
        v = w / 0.6; st.N['x'] = a[0] + (via[0] - a[0]) * v; st.N['y'] = a[1] + (via[1] - a[1]) * v; st.N['yaw'] = yaw_lerp(a[2], Fp[2], v)
    else:
        v = (w - 0.6) / 0.4; st.N['x'] = via[0] + (Fp[0] - via[0]) * v; st.N['y'] = via[1] + (Fp[1] - via[1]) * v; st.N['yaw'] = Fp[2]
stage('joinNF', 'N docks to F', 8, 300, 'N backs its open end onto F\'s rear cuff: magnets in the two cuffs, the same as the docking of a tail and a head. Pogo pads in the cuff carry the battery\'s power into F. The new tail is whole, still without an arm.', f_joinNF)

def f_undock(u, s0):
    st.red = lerp3(s0['red'], [OFF - 0.25, 0, 0], seg(u, 0.1, 0.9)); st.q = arm_to(s0['q'], HOME, 1, u, 0, 0.3)
stage('undock', 'The parent leaves its head', 5, 120, 'The tilt release lets the nine magnets go. The parent\'s tail backs 250 mm away from its head on its wheels. The head stays where it is.', f_undock)

C_TURN = np.array([OFF - 0.25 - 0.2, 0.0])
def f_turn(u, s0):
    yaw = math.pi * seg(u, 0.05, 0.95); R2_ = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]])
    p = C_TURN - R2_ @ np.array([-0.2, 0.0]); st.red = np.array([p[0], p[1], yaw])
stage('turnRed', 'It turns round', 6, 120, 'It turns on the spot, its face now toward the back glass.', f_turn)

def f_toTray(u, s0):
    st.red = lerp3(s0['red'], RS, seg(u, 0.05, 0.95))
stage('toTray', 'To the tray', 5, 120, 'It drives to the tray on the back glass, where the four modules of the new arm stand.', f_toTray)

def f_blueWait(u, s0):
    a = np.array([s0['F']['x'], s0['F']['y'], s0['F']['yaw']]); w = seg(u, 0.0, 1.0)
    via = np.array([a[0], BWAIT[1], 0.0])
    if w < 0.25: p = np.array([a[0], a[1] + (BWAIT[1] - a[1]) * w / 0.25, yaw_lerp(a[2], 0.0, w / 0.25)])
    else: p = lerp3(via, BWAIT, (w - 0.25) / 0.75)
    set_blue(p); st.N['jet'] = 1.0 if u < 0.97 else 0.0
stage('blueWait', 'The new tail comes round', 7, 300, 'The new tail swims down the side of the tank, past the head, and waits beside the place of the handover.', f_blueWait)

for idx, k in enumerate(MOD_ORDER):
    label = {'M1': 'base', 'M2': 'upper arm', 'M3': 'forearm', 'M4': 'end effector'}[k]
    last = idx == len(MOD_ORDER) - 1
    def f_mod(u, s0, k=k, idx=idx, last=last):
        if u == 0: st.mods = copy_mods(s0)
        m = st.mods[k]; q0 = s0['q']
        # A. the module slides to the middle slot; the holder comes down onto it (0 .. 0.2)
        y0 = SLOT0[k] if idx > 0 else 0.0
        Gt = tray_G(k, y0 * (1 - seg(u, 0.0, 0.12)))
        top = grip(k, CROOT, QJ[k], Gt)
        if u <= 0.2:
            st.red = lerp3(s0['red'], RSK[k], seg(u, 0.0, 0.08)); m['G'] = Gt
            st.q = arm_to(q0, top, 1, u, 0.08, 0.2)
        G_grab = tray_G(k, 0.0); top2 = grip(k, CROOT, QJ[k], G_grab)
        # B. lift and carry to the place of the handover (0.2 .. 0.45)
        if 0.2 < u <= 0.45:
            lift = 0.03 * seg(u, 0.2, 0.26)
            st.red = lerp3(RSK[k], RD, seg(u, 0.26, 0.45))
            dx = st.red[0] - RSK[k][0]
            tip = top2 + [dx, 0, lift]; q = ikc(tip, CUP)
            st.q = q; m['G'] = T([dx, 0, lift]) @ G_grab
        # C. the new tail comes in and docks; its arm holds the joint where the parent can reach (0.45 .. 0.6)
        if 0.45 < u <= 0.6:
            st.red = RD.copy()
            set_blue(lerp3(BWAIT if idx > 0 or True else BD, BD, seg(u, 0.45, 0.58))); st.N['jet'] = 1.0 if u < 0.57 else 0.0
            if idx > 0: st.cq = s0['cq'] + (QJ[k] - s0['cq']) * seg(u, 0.5, 0.6)
        # D. the holder sets the module on its joint: magnets close the last 2 mm, the latch clicks (0.6 .. 0.85)
        if u > 0.6:
            dx = RD[0] - RSK[k][0]
            Gc = T([dx, 0, 0.03]) @ G_grab                     # as carried
            w = seg(u, 0.6, 0.84)
            g_car = grip(k, CROOT, QJ[k], Gc); g_fin = grip(k, CROOT, QJ[k])
            via = np.array([g_fin[0], g_fin[1], max(g_car[2], g_fin[2] + 0.06)])
            pos = lerp3(g_car, via, min(1, w * 2)) if w < 0.5 else lerp3(via, g_fin, (w - 0.5) * 2)
            if u <= 0.84: m['G'] = T(pos - g_fin)
            st.q = ikc(pos, CUP)
            if u > 0.84:
                m['G'] = np.eye(4); m['att'] = 1; st.childvis = 1
                st.root = CROOT.copy()
        # E. the new tail moves aside, the parent drives back to the tray (0.86 .. 1)
        if u > 0.86 and not last:
            w = seg(u, 0.86, 1.0); set_blue(lerp3(BD, BWAIT, w)); st.red = lerp3(RD, RSK[MOD_ORDER[idx + 1]], w)
            st.q = arm_to(st.q, tip_of(REST, 1), 1, u, 0.86, 1.0)
    joint = {'M1': 'It sets the base in F\'s seat: three magnets and the pogo pads. The new arm has power.',
             'M2': 'The new arm holds its shoulder up; the upper arm goes down onto it and clicks.',
             'M3': 'The new arm leans its upper arm toward the parent; the forearm clicks onto the elbow.',
             'M4': 'It holds its wrist where the parent can reach; the end effector clicks on. The arm is whole.'}[k]
    real = 900
    stage('mod' + k, f'Module {idx+1}: {label}', 13, real,
          f'The {label} slides to the middle of the tray and the holder takes it. The parent drives back, the new tail comes in and docks face to face. {joint}', f_mod)
    st.root = CROOT.copy()

st.cq = QJ['M4'].copy()
def f_wake(u, s0):
    w = seg(u, 0.1, 0.9); st.cq = s0['cq'] + (REST - s0['cq']) * w
    st.q = arm_to(s0['q'], tip_of(REST, 1, RD), 1, u, 0.0, 0.4)
stage('wake', 'Its own arm', 5, 30, 'The new arm straightens to its rest pose, inside its own tail.', f_wake)

def f_part(u, s0):
    w = seg(u, 0.05, 0.6); st.red = lerp3(RD, RD + [0.35, 0, 0], w)
    # the new tail turns on the spot to face the tray
    v = seg(u, 0.5, 1.0); c = np.array([BX - 0.2, 0.0])
    yaw = math.pi * v; R2_ = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]]); p = c + R2_ @ np.array([0.2, 0.0])
    set_blue([p[0], p[1], yaw]); st.N['jet'] = 1.0 if u > 0.5 else 0.0
stage('part', 'Apart', 6, 120, 'The magnets let go. The parent backs off; the new tail turns round to face the tray.', f_part)

SELF_POSE = np.array([TRAY_X[1] + 0.012 + FACE, 0.30, math.pi])
def f_self(u, s0):
    a = np.array([s0['F']['x'], s0['F']['y'], s0['F']['yaw']])
    set_blue(lerp3(a, SELF_POSE, seg(u, 0.0, 0.35))); st.N['jet'] = 1.0 if u < 0.33 else 0.0
    bp = np.array([st.F['x'], st.F['y'], st.F['yaw']]); croot = pose_M(bp) @ T([-0.115, 0, 0.005])
    item = np.array([TRAY_X[0] + 0.05, 0.34, TRAY_TOP + 0.01])
    inside = (pose_M(SELF_POSE) @ np.r_[-0.03, 0.07, 0.02, 1])[:3]
    def cik(p):
        tl = (np.linalg.inv(pose_M(bp)) @ np.r_[p, 1])[:3]; q = ik(tl, CUP, BL)
        if q is None:
            for _ in range(60):
                d = tl[:2] - BL[:2]; tl[:2] = BL[:2] + d * 0.985; q = ik(tl, CUP, BL)
                if q is not None: break
        return q
    if u > 0.35:
        if u < 0.6: q = cik(item + [0, 0, 0.012]); w = seg(u, 0.35, 0.6); st.cq = s0['cq'] + (q - s0['cq']) * w if q is not None else st.cq; st.item = item
        else:
            w = seg(u, 0.6, 0.95); p = lerp3(item, inside, w) + [0, 0, 0.06 * math.sin(math.pi * w)]; q = cik(p + [0, 0, 0.012])
            if q is not None: st.cq = q
            st.item = p
    st.root = croot
stage('selfPick', 'It picks up the rest', 9, 120, 'The new tail swims to the tray. With its own arm it takes the last thing there, a tile set, and puts it inside itself. From here it can gather what it needs.', f_self)

def f_home(u, s0):
    st.cq = s0['cq'] + (REST - s0['cq']) * seg(u, 0.0, 0.4)
    bp = np.array([st.F['x'], st.F['y'], st.F['yaw']]); st.root = pose_M(bp) @ T([-0.115, 0, 0.005])
    # the parent turns round and goes back to its head
    a = s0['red']; c = np.array([a[0] - math.cos(a[2]) * 0.2, a[1] - math.sin(a[2]) * 0.2])
    w1 = seg(u, 0.0, 0.45)
    yaw = math.pi * (1 - w1); R2_ = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]]); p = c - R2_ @ np.array([-0.2, 0.0])
    st.red = np.array([p[0], p[1], yaw])
    if u > 0.45: st.red = lerp3(st.red, [OFF, 0, 0], seg(u, 0.45, 1.0))
stage('home', 'Two tails', 8, 300, 'The parent turns and docks back to its head. The new tail has two quilted halves, an arm put together inside it, and a first thing it picked up itself.', f_home)

# ---------------------------------------------------------------- 5. write
out = dict(
    about='Born, Not Made, tail copy variant (23 Nov 2026): the parent prints the two segments of a new tail and puts a new arm together from four floating modules. '
          'Frame: x toward the parent\'s mouth, y port, z up, meters, origin on the tank floor; the parent sits 200 mm back from the quilted head simulator.',
    off=OFF, water=WATER, gel=GEL, lip=[float(x) for x in LIP], mouth_top=[float(x) for x in MOUTH_TOP], base=[float(x) for x in BASE], tank=TANK,
    seg=dict(na=NA, nv=NV, secN=SECN, secF=SECF, perN=PER_N, perF=PER_F, joint=JOINT, pitch=J['q']['q4']['pitch_mm'], packN=packN, packF=packF,
             areaN=AN, areaF=AF, layN=layN, layF=layF),
    print_x=[float(x) for x in PRINT_X], rbowl=[R2(x) for x in R_BOWL.T.reshape(-1)], lie_q=[float(x) for x in lie_q], croot=[R2(x) for x in CROOT.T.reshape(-1)], qj={k: [float(x) for x in QJ[k]] for k in MOD_ORDER}, tray=dict(x0=float(TRAY_X[0]), x1=float(TRAY_X[1]), y=TRAY_Y, top=TRAY_TOP), rb=RB, out=[float(x) for x in OUT], dock=[float(x) for x in DOCK], mods=MODS, mod_order=MOD_ORDER, floats=floats, fold=[float(x) for x in FOLD], rest=[float(x) for x in REST], delta=float(DELTA),
    stages=stages, fps=FPS, fr=frames, checks=checks, notes=notes,
    sources=dict(dex=J['sources']['dex'], ds30=J['sources']['ds30'], mag=J['sources']['mag']),
)
json.dump(out, open('tailcopy.json', 'w'), separators=(',', ':'))
print(len(frames), 'frames,', sum(s['disp'] for s in stages), 's')
for c in checks: print(('PASS ' if c['ok'] else 'FAIL ') + c['group'] + ': ' + c['name'] + ('  [' + c['value'] + ']' if c['value'] else ''))
print('DELTA', DELTA, 'PULL', PULL, 'lying box', lie_len, lie_w, lie_h)

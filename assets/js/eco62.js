/* RealMan ECO62 for the two 3D views (Build and Simulator).
   Chain: official URDF (simulator/eco62.json). Meshes: one per link, link local frames, metres (simulator/eco62_glb.txt, base64 GLB).
   Layout: the R25 note. The arm hangs upside down under the tip of a flat telescopic top boom, foot turned 180 degrees, and the whole
   system is 1.25 times the DexArm design. All lengths in this file are real metres in the tail frame of the scaled system
   (scene coordinate times S), so a view that keeps the scene at the DexArm size draws the arm group at 1 / S. */
(function (G) {
  "use strict";
  const S = 1.25;
  /* ---- 4 x 4 matrices as row major arrays of 16 ---- */
  const I4 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  function mul(a, b) { const o = new Array(16); for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) o[4 * r + c] = a[4 * r] * b[c] + a[4 * r + 1] * b[4 + c] + a[4 * r + 2] * b[8 + c] + a[4 * r + 3] * b[12 + c]; return o; }
  const tr = (x, y, z) => [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z, 0, 0, 0, 1];
  const rx = (t) => { const c = Math.cos(t), s = Math.sin(t); return [1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1]; };
  const ry = (t) => { const c = Math.cos(t), s = Math.sin(t); return [c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1]; };
  const rz = (t) => { const c = Math.cos(t), s = Math.sin(t); return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; };
  const rpy = (r, p, y) => mul(rz(y), mul(ry(p), rx(r)));                    // URDF fixed axis roll, pitch, yaw
  function raxis(ax, t) { if (ax[2] === 1 && !ax[0] && !ax[1]) return rz(t); if (ax[0] === 1) return rx(t); if (ax[1] === 1) return ry(t); return rz(t * Math.sign(ax[2] || 1)); }

  let META = null, ORG = null, LIM = null;
  function setMeta(m) { META = m; ORG = m.joints.map((j) => mul(tr(j.xyz[0], j.xyz[1], j.xyz[2]), rpy(j.rpy[0], j.rpy[1], j.rpy[2]))); LIM = m.joints.map((j) => [j.lower, j.upper]); }

  /* ---- layout (real metres, tail frame of the scaled system) ---- */
  const LAYOUT = {
    S,
    boomZ: [0.124, 0.144],          // flat top boom 80 x 20, underside and top; passes under the top of the hatch
    boomW: 0.080,
    seat: 0.008,                    // seat plate between the boom tip and the foot
    homeX: -0.920,                  // foot axis with the boom home, arm folded inside the tail
    gain: 1.30,                     // foot travel per metre of the DexArm boom command (three stages reach further than the low carriage)
    tool: 0.150,                    // flange to nozzle tip
    stage: 0.44,                    // length of one boom stage
  };
  const footX = (boom) => LAYOUT.homeX + LAYOUT.gain * boom * S;         // boom: the simulator's boom command, scene metres
  /* foot frame: hanging (z down), turned 180 degrees about the vertical on the boom tip */
  function baseM(boom) { return mul(tr(footX(boom), 0, LAYOUT.boomZ[0] - LAYOUT.seat), mul(rx(Math.PI), rz(Math.PI))); }

  /* ---- forward kinematics: link frames in the tail frame; [0] base_link ... [6] link_6, [7] nozzle tip ---- */
  function fk(q, B) {
    const out = [B]; let M = B;
    for (let i = 0; i < 6; i++) { M = mul(mul(M, ORG[i]), raxis(META.joints[i].axis, q[i])); out.push(M); }
    out.push(mul(M, tr(0, 0, LAYOUT.tool))); return out;
  }
  const tipOf = (F) => { const T = F[7]; return [T[3], T[7], T[11], T[2], T[6], T[10]]; };     // position, tool axis

  /* ---- inverse kinematics: damped least squares on the nozzle position and on the tool axis pointing down ----
     target: [x, y, z] real metres, tail frame. q0: previous joints (continuity). Joint limits from the URDF are respected by clamping.
     returns { q, err (m), tilt (rad off vertical), lim: [joint numbers on a limit], ok } */
  const WO = 0.12;                  // metres per radian: weight of the axis error against the position error
  function errVec(F, target) { const t = tipOf(F); const a = [t[3], t[4], t[5]]; return [target[0] - t[0], target[1] - t[1], target[2] - t[2], -WO * a[0], -WO * a[1], WO * (-1 - a[2])]; }   // zero only with the tool axis straight down
  function solve6(A, b) {
    const n = 6, M = A.map((r, i) => r.concat(b[i]));
    for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; const t = M[c]; M[c] = M[p]; M[p] = t; const d = M[c][c] || 1e-12;
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c] / d; if (f) for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; } }
    return M.map((r, i) => r[n] / (r[i] || 1e-12));
  }
  function ik(target, q0, B, opt) {
    const o = opt || {}, iters = o.iters || 10, lam2 = o.lambda2 || 4e-4, h = 1e-5; let q = q0.slice();
    for (let it = 0; it < iters; it++) {
      const F = fk(q, B), e = errVec(F, target); if (Math.hypot(e[0], e[1], e[2]) < 2e-5 && Math.hypot(e[3], e[4], e[5]) < 2e-5) break;
      const J = []; for (let r = 0; r < 6; r++) J.push(new Array(6));
      for (let j = 0; j < 6; j++) { const qq = q.slice(); qq[j] += h; const e2 = errVec(fk(qq, B), target); for (let r = 0; r < 6; r++) J[r][j] = -(e2[r] - e[r]) / h; }
      const A = []; for (let r = 0; r < 6; r++) { A.push(new Array(6)); for (let c = 0; c < 6; c++) { let s = 0; for (let k = 0; k < 6; k++) s += J[r][k] * J[c][k]; A[r][c] = s + (r === c ? lam2 : 0); } }
      const y = solve6(A, e);
      for (let j = 0; j < 6; j++) { let d = 0; for (let r = 0; r < 6; r++) d += J[r][j] * y[r]; d = Math.max(-0.25, Math.min(0.25, d)); q[j] = Math.max(LIM[j][0], Math.min(LIM[j][1], q[j] + d)); }
    }
    const t = tipOf(fk(q, B)), err = Math.hypot(target[0] - t[0], target[1] - t[1], target[2] - t[2]), tilt = Math.acos(Math.max(-1, Math.min(1, -t[5])));
    const lim = []; for (let j = 0; j < 6; j++) if (q[j] - LIM[j][0] < 2e-3 || LIM[j][1] - q[j] < 2e-3) lim.push(j + 1);
    return { q, err, tilt, lim, ok: err < 0.002 && tilt < 0.035 && !lim.length };
  }
  /* plain note for a pose that is not met, or "" */
  function note(r) {
    if (!r || r.ok) return "";
    const p = [];
    if (r.err >= 0.002) p.push(`out of reach by ${(r.err * 1000).toFixed(0)} mm`);
    if (r.tilt >= 0.035) p.push(`tool ${(r.tilt * 180 / Math.PI).toFixed(0)} deg off vertical`);
    if (r.lim.length) p.push(`joint ${r.lim.join(" and ")} at the limit`);
    return "ECO62 clamped: " + p.join(", ");
  }
  const FOLD = [0, -2.2019, 0.6109, 1.6251, -1.5708, 0];          // passage pose: folded flat under the boom
  const SEED = [-0.19, -2.39, 1.87, -1.05, -1.5708, 0];   // start of the first solve: elbow up toward the bow, wrist leading, tool down

  /* ---- three.js side (needs THREE and THREE.GLTFLoader) ---- */
  const toM4 = (a) => { const m = new THREE.Matrix4(); m.set(...a); return m; };
  /* non indexed geometry with normals smoothed only across edges flatter than the crease angle; keeps vertex colours */
  function creased(geo, deg) {
    const g = geo.index ? geo.toNonIndexed() : geo.clone(), P = g.attributes.position.array, n = P.length / 9, cosT = Math.cos((deg || 38) * Math.PI / 180);
    const fn = new Float32Array(n * 3), map = new Map(), N = new Float32Array(P.length);
    for (let f = 0; f < n; f++) { const i = 9 * f, ux = P[i + 3] - P[i], uy = P[i + 4] - P[i + 1], uz = P[i + 5] - P[i + 2], vx = P[i + 6] - P[i], vy = P[i + 7] - P[i + 1], vz = P[i + 8] - P[i + 2];
      const x = uy * vz - uz * vy, y = uz * vx - ux * vz, z = ux * vy - uy * vx; fn[3 * f] = x; fn[3 * f + 1] = y; fn[3 * f + 2] = z;      // area weighted
      for (let k = 0; k < 3; k++) { const key = Math.round(P[i + 3 * k] * 2e5) + "," + Math.round(P[i + 3 * k + 1] * 2e5) + "," + Math.round(P[i + 3 * k + 2] * 2e5); let a = map.get(key); if (!a) map.set(key, (a = [])); a.push(f); } }
    const keyOf = (i) => Math.round(P[i] * 2e5) + "," + Math.round(P[i + 1] * 2e5) + "," + Math.round(P[i + 2] * 2e5);
    for (let f = 0; f < n; f++) { const ax = fn[3 * f], ay = fn[3 * f + 1], az = fn[3 * f + 2], al = Math.hypot(ax, ay, az) || 1;
      for (let k = 0; k < 3; k++) { const i = 9 * f + 3 * k; let x = 0, y = 0, z = 0;
        for (const g2 of map.get(keyOf(i))) { const bx = fn[3 * g2], by = fn[3 * g2 + 1], bz = fn[3 * g2 + 2], bl = Math.hypot(bx, by, bz) || 1; if ((ax * bx + ay * by + az * bz) / (al * bl) >= cosT) { x += bx; y += by; z += bz; } }
        const l = Math.hypot(x, y, z) || 1; N[i] = x / l; N[i + 1] = y / l; N[i + 2] = z / l; } }
    g.setAttribute("normal", new THREE.BufferAttribute(N, 3)); return g;
  }
  /* the real colours are toned toward the white clay of the views: white shell, a quiet orange, dark joints */
  function tone(geo) {
    const c = geo.attributes.color; if (!c) return geo; const a = new Float32Array(c.count * 3);
    for (let i = 0; i < c.count; i++) { let r = c.getX(i), g = c.getY(i), b = c.getZ(i);
      if (r > 1 || g > 1 || b > 1) { r /= 255; g /= 255; b /= 255; }
      let o;
      if (r > 0.9 && g > 0.35 && g < 0.65 && b < 0.2) o = [0.93, 0.45, 0.17];             // orange slabs
      else if (r + g + b < 0.5) o = [0.16, 0.165, 0.18];                                    // black joints and display
      else if (b > r + 0.2) o = [0.36, 0.47, 0.62];                                          // blue port panel
      else if (r > 0.85) o = [0.93, 0.93, 0.915];                                            // white shell
      else o = [r * 0.9, g * 0.9, b * 0.9];
      a[3 * i] = o[0]; a[3 * i + 1] = o[1]; a[3 * i + 2] = o[2]; }
    const attr = new THREE.BufferAttribute(a, 3); geo.setAttribute("color", attr);
    for (let i = 0; i < a.length; i++) a[i] = a[i] <= 0.04045 ? a[i] / 12.92 : Math.pow((a[i] + 0.055) / 1.055, 2.4);        // sRGB to linear, as vertex colours are used
    return geo;
  }
  let loading = null;
  /* load(base): base = path of the simulator folder, with the trailing slash. Resolves to { meta, geo: { link name: geometry } } */
  function load(base) {
    if (loading) return loading;
    loading = (async () => {
      const [meta, b64] = await Promise.all([fetch(base + "eco62.json").then((r) => r.json()), fetch(base + "eco62_glb.txt").then((r) => r.text())]);
      setMeta(meta);
      const bin = Uint8Array.from(atob(b64.trim()), (c) => c.charCodeAt(0));
      const gltf = await new Promise((res, rej) => new THREE.GLTFLoader().parse(bin.buffer, "", res, rej));
      const geo = {}; gltf.scene.traverse((o) => { if (o.isMesh) geo[o.name.replace(/\.\d+$/, "")] = tone(creased(o.geometry, 38)); });
      for (const ln of meta.links) if (!geo[ln]) throw new Error("ECO62 mesh missing: " + ln);
      return { meta, geo };
    })();
    loading.catch(() => { loading = null; });
    return loading;
  }
  /* tool on the flange (link_6 frame, +z out of the flange): valve block, print tube, needle. Returns [{ geo, pos, kind }] */
  function toolShapes() {
    const L = LAYOUT.tool, cyl = (r0, r1, len) => { const g = new THREE.CylinderGeometry(r1, r0, len, 20); g.rotateX(Math.PI / 2); return g; };
    return [
      { geo: new THREE.BoxGeometry(0.044, 0.044, 0.032), pos: [0, 0, 0.016], kind: "block" },
      { geo: cyl(0.011, 0.009, L - 0.032 - 0.038), pos: [0, 0, 0.032 + (L - 0.070) / 2], kind: "tube" },
      { geo: cyl(0.0035, 0.0012, 0.038), pos: [0, 0, L - 0.019], kind: "needle" },
    ];
  }
  /* three boom stages for the simulator's boom command: [{ x0, x1, w, z0, z1 }], real metres; the outer stage is fixed in the tail and sticks out of the rear */
  function boomStages(boom) {
    const lead = 0.055, L = LAYOUT.stage, tip0 = footX(0) + lead, ext = Math.max(0, footX(boom) + lead - tip0), [z0, z1] = LAYOUT.boomZ, w = LAYOUT.boomW;
    return [{ x0: tip0 - L, x1: tip0, w, z0, z1 }, { x0: tip0 - L + 0.02 + ext / 2, x1: tip0 + ext / 2, w: w - 0.010, z0: z0 + 0.003, z1: z1 - 0.003 }, { x0: tip0 - L + 0.04 + ext, x1: tip0 + ext, w: w - 0.020, z0: z0 + 0.006, z1: z1 - 0.006 }];
  }
  const KEY = "bnm-arm";
  const getArm = () => { try { return localStorage.getItem(KEY) === "eco62" ? "eco62" : "dexarm"; } catch (e) { return "dexarm"; } };
  const setArm = (v) => { try { localStorage.setItem(KEY, v === "eco62" ? "eco62" : "dexarm"); } catch (e) {} };
  const STATUS = "The ECO62 version is built, but the targets are not all met (64 collision frames at 10 mm clearance, 57 frames above datasheet joint speed), and the DexArm version remains the only one that passes every check.";

  G.ECO62 = { S, LAYOUT, FOLD, SEED, setMeta, footX, baseM, fk, tipOf, ik, note, toM4, creased, load, toolShapes, boomStages, getArm, setArm, STATUS, get meta() { return META; }, get limits() { return LIM; }, mul, tr, rx, ry, rz };
})(typeof window !== "undefined" ? window : globalThis);

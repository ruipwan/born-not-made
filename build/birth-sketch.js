/* Overdamped one-dimensional comparison. SI units throughout; this function
   does not run the finite element solver or include the earlier gel breakout. */
const BirthSketch = (() => {
  const sleeveLength = 0.08;
  const exit = 0.17;
  const pulsePeriod = 9;
  const referenceCurve = [[0, 54], [20, 172], [50, 220], [100, 265], [150, 297], [250, 346], [365, 385]];
  function canalRadius(s, throat) {
    if (s < -0.16) return 0.2;
    if (s >= 0.16) return 0.22;
    if (s >= 0 && s <= sleeveLength) return throat;
    const u = s < 0 ? -s / 0.16 : (s - sleeveLength) / 0.08;
    const outside = s < 0 ? 0.2 : 0.22;
    return throat + (outside - throat) * u * u * (3 - 2 * u);
  }
  function extensionFraction(pressure, curve = referenceCurve) {
    if (pressure <= curve[0][0]) return 0;
    const span = curve[curve.length - 1][1] - curve[0][1];
    for (let i = 1; i < curve.length; i++) {
      const [p0, l0] = curve[i - 1], [p1, l1] = curve[i];
      if (pressure <= p1) return (l0 + (l1 - l0) * (pressure - p0) / (p1 - p0) - curve[0][1]) / span;
    }
    return 1;
  }
  function normalForce(run, throat, p) {
    const ds = run.L / 40;
    let total = 0;
    for (let i = 0; i < 40; i++) {
      const radius = canalRadius(run.B + (i + 0.5) * ds, throat);
      total += p.kappa * Math.max(0, p.ro - radius) * ds;
    }
    return total;
  }
  function initial(method, p) {
    const length = p.n * p.pf;
    return {m: method, B: -0.06 - length, L: length, v: 0, born: null, stuck: 0,
      Fmax: 0, hist: [], held: method.key === "grow", sealed: false};
  }
  function step(run, input, p, time, dt) {
    if (run.born !== null) return;
    const pulse = Math.max(0, Math.sin(2 * Math.PI * time / pulsePeriod)) ** 4;
    const tip = run.B + run.L;
    run.sealed = p.ro > input.rt && tip >= 0 && run.B < sleeveLength;
    const contact = normalForce(run, input.rt, p);
    const gelLength = Math.max(0, Math.min(run.L, -0.16 - run.B));
    const gelDrag = input.ty * 2 * Math.PI * p.ro * gelLength;
    let friction = (run.v > 1e-4 ? 2 / 3 : 1) * input.mu * contact;
    if (run.m.key === "evert") friction *= 0.1; // illustrative rolling liner
    const resistance = friction + gelDrag + p.climb;
    const growthForce = input.pb * p.Aeff;
    const before = run.L;
    if ((run.held || input.inf) && growthForce > resistance) {
      const fraction = extensionFraction(input.pb, p.curve);
      const target = p.n * (p.pf + (p.pd - p.pf) * fraction);
      run.L = Math.max(before, Math.min(target, before + dt * p.Q / p.Aeff));
    }
    const outside = Math.max(0, run.B + run.L - Math.max(run.B, 0.16));
    const buoyancy = 1000 * 9.81 * Math.PI * p.ro ** 2 * outside * 0.85 * Math.sin(20.8 * Math.PI / 180);
    let drive = buoyancy;
    if (run.m.key === "womb" && run.sealed) drive += input.pw * pulse * p.Aseal;
    if (run.m.key === "evert") drive += input.pw * pulse * Math.PI * input.rt ** 2;
    if (run.m.key === "arm") drive += p.armF;
    if (run.held) {
      drive = growthForce; // reaction at the heel; a fixed tail cannot clear the exit
    } else {
      run.v = Math.max(0, (drive - resistance) / p.c);
      run.B += run.v * dt;
    }
    run.stuck = (run.v > 1e-6 || run.L > before) ? 0 : run.stuck + dt;
    run.Fmax = Math.max(run.Fmax, drive);
    if (run.B >= exit) run.born = time;
    if (!run.hist.length || time - run.hist[run.hist.length - 1][0] >= 0.25) {
      run.hist.push([time, drive, resistance]);
    }
  }
  return {initial, step, canalRadius};
})();

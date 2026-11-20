const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const read = name => fs.readFileSync(path.join(__dirname, '..', name), 'utf8');
const data = JSON.parse(read('simulator/stage3.json'));
const near = (x, y, tolerance) => assert.ok(Math.abs(x - y) <= tolerance, `${x} differs from ${y}`);
const element = () => ({children: [], appendChild(el) { this.children.push(el); }, style: {}});
const document = {querySelector: element, createElement: element, querySelectorAll: () => []};
const context = vm.createContext({
  console, performance, atob, URL, TextDecoder, document,
  fetch: async file => new Response(read('simulator/' + file)),
});
const run = code => vm.runInContext(code, context);
before(async () => {
  run('window = self = globalThis;');
  for (const name of ['assets/vendor/three-r147/three.min.js', 'assets/vendor/three-r147/GLTFLoader.js', 'assets/js/eco62.js']) run(read(name));
  const script = read('simulator/index.html').match(/<script>([\s\S]*?)<\/script>/)[1];
  run(script.slice(0, script.indexOf('(async function main()')));
  run('R3 = {scene: new THREE.Scene(), host: document.createElement("div")}; for (const k of ["vessel","tail","arm","baby"]) R3[k] = new THREE.Group();');
  await run('loadAll()');
});
function arm(name) {
  context.armName = name;
  run('ARM.sel = armName; ECOV.on = armName === "eco62"; buildStages();');
}
function state(key, seconds) {
  context.key = key; context.seconds = seconds;
  return JSON.parse(run('JSON.stringify((() => {const s = TL.stages.find(s => s.k === key); return evalState(s.d0 + s.disp * seconds / s.real, 0);})())'));
}
test('the production loaders assemble a smooth upper hull, both robot arms and a six-story folded baby', () => {
  assert.equal(run('ECOV.ready'), true);
  assert.ok(run('Object.keys(ARM.parts).length') >= 7);
  assert.equal(run('PARTS.shell.children.length'), 0);
  assert.equal(run('PARTS.shell.material.wireframe'), false);
  assert.equal(run('BB.lam.length'), 6);
  near(run('babyGeo([0,0,0,0,0,0]).L'), data.body.len_folded, 1e-7);
  near(run('babyGeo([1,1,1,1,1,1]).L'), data.body.len_deployed, 1e-7);
});
test('actual print moves reproduce the exported print time, deposited volume and last layer', () => {
  arm('dexarm');
  assert.equal(run('GC.layers'), 59);
  near(run('GC.total'), data.print.total_s, 0.20);
  near(run('GC.pts.at(-1).ext / 1000'), data.print.silicone_ml, 0.01);
  assert.equal(state('kit', 1).babyVis, false);
  assert.equal(state('kit', 1).layer, -1);
  assert.equal(state('cure', 1).layer + 1, data.print.layers);
});
test('both birth runs replay each recorded push sample and begin rising at release', () => {
  for (const name of ['dexarm','eco62']) {
    arm(name);
    const record = data.birth[name], rise = data.newborn[name].rise;
    for (const row of record.track) {
      const s = state('birth', row[0]);
      near(s.xe,row[1],1e-8); near(s.bV,row[3],1e-5); near(s.bp,row[4],1e-5); near(s.F,row[7],1e-7);
    }
    assert.ok(!state('birth',record.t_release-0.01).released);
    assert.equal(state('birth',record.t_release+0.01).released,true);
    const atFour = state('birth',record.t_release+4);
    assert.ok(atFour.babyZ > data.z_axis);
    near(state('birth',record.t_release+6-0.0001).babyZ,state('float',0).babyZ,1e-5);
    near(state('float',rise.at(-1)[0]-6-0.0001).babyZ,rise.at(-1)[1],1e-5);
  }
});
test('ECO62 reports the actual forward-kinematic tip when a target is outside its workspace', () => {
  arm('eco62');
  run('const sample=evalState(0,0); ARM.target=[2,0,0]; applyState(sample,0);');
  assert.ok(run('ARM.err')>500);
  near(run('ARM.err'),run('ECOV.res.err * 1000'),1e-6);
});
test('DexArm can reach every recorded print waypoint within one hundredth of a millimetre in the model', () => {
  const worst = run(`(() => {
    let q = [0, 0.6, 0.5], worst = 0;
    for (const p of GC.pts) {
      if (p.kind !== 1) continue;
      const target = [p.x, p.y, p.z], base = railX(target);
      q = KIN.solve(target, q, base);
      const tip = KIN.tip(q, base);
      worst = Math.max(worst, 1000 * Math.hypot(...tip.map((value,i) => value-target[i])));
    }
    return worst;
  })()`);
  assert.ok(worst < 0.01, `worst model tip error was ${worst} mm`);
});
test('the GPU-free side view can draw all replay stages with finite coordinates', () => {
  let shapes = 0;
  const method = (...args) => {
    assert.ok(args.every(Number.isFinite), 'non-finite canvas coordinate');
    shapes++;
  };
  context.canvasContext = {
    canvas: {width: 960, height: 600}, setTransform: method, fillRect: method, beginPath: method,
    lineTo: method, moveTo: method, closePath: method, fill: method, stroke: method,
    save: method, restore: method, clip: method, arc: method,
  };
  arm('dexarm');
  run(`R3.profile = canvasContext; R3.host.clientWidth = 960; R3.host.clientHeight = 600;
    for (const stage of TL.stages) {
      const s=evalState(stage.d0+stage.disp/2,0); applyState(s,0); drawSideView(s);
    }`);
  assert.ok(shapes > 10000);
});

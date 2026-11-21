const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const read = file => fs.readFileSync(path.join(__dirname,'..',file),'utf8');
const data = file => JSON.parse(read(file));
const reference = data('simulator/old_/stage2/birth_fe.json');
const physics = data('build/data/physics.json');
const trace = vm.runInNewContext(read('assets/js/birth-trace.js')+'\nBirthTrace');
const sketch = vm.runInNewContext(read('build/birth-sketch.js')+'\nBirthSketch');
const near = (actual,expected,tolerance) => assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} vs ${expected}`);
const {t:times,s_tail:tail} = reference.series;

test('all recorded pressure and position samples return their stored values', () => {
  for (const key of ['p_b','p_w','s_tail','s_nose','V_b_L','push_N']) {
    const values = reference.series[key];
    times.forEach((time,i) => assert.equal(trace.at(times,values,time),values[i]));
    assert.equal(trace.at(times,values,-1),values[0]);
    assert.equal(trace.at(times,values,500),values.at(-1));
  }
  const i = times.indexOf(400.01), values = reference.series.p_w;
  assert.equal(values[i],644);
  near(trace.at(times,values,(times[i]+times[i+1])/2),(values[i]+values[i+1])/2,1e-8);
});

test('the recorded tail crosses the exit at the reported time', () => {
  const i = tail.findIndex(s => s >= reference.s_end);
  const u = (reference.s_end-tail[i-1])/(tail[i]-tail[i-1]);
  const crossing = times[i-1]+u*(times[i]-times[i-1]);
  near(crossing,reference.t_born_s,0.05);
  assert.equal(reference.slip_t.filter(t => t <= reference.t_born_s).length,37);
  assert.equal(reference.frames.nodes,reference.nb+reference.ns);
  assert.equal(Buffer.from(reference.frames.b64,'base64').length,reference.frames.t.length*reference.frames.nodes*2*2);
});

test('twelve comparison cases distinguish computed exits, extrapolations and no exit', () => {
  const cases = data('build/data/birth_sim.json').cases;
  assert.equal(cases.length,12);
  for (const kind of ['no_exit','extrapolated','completed']) assert.equal(cases.filter(c=>c.exit_result===kind).length,4);
  for (const c of cases) assert.equal(c.exit_result==='extrapolated',/extrapolated/.test(c.notes));
  const solved = cases.find(c=>c.name==='(c) growth, then gel chamber pulses, sleeve r 80 (tighter)');
  assert.equal(solved.exit_result,'completed');
  assert.equal(Math.round(reference.t_born_s),solved.time_s);
});

const p = {n:6,pf:.009,pd:.385/6,ro:.105,riF:.055,riD:.069,Aeff:.0237,Aseal:.0346,
  Q:3/60000,kappa:25000,armF:4.9,climb:1.2,c:1000,curve:physics.fold.params.L_vs_p_DS10};
const input = {pw:0,pb:0,mu:.6,rt:.08,ty:50,inf:true};
function simulate(key, inputs, duration) {
  const run=sketch.initial({key},p);
  for (let i=1;i<=Math.round(duration/.025);i++) sketch.step(run,inputs,p,i*.025,.025);
  return run;
}
test('at zero pressure the three passive lanes stay in place and maintain folded length', () => {
  for (const key of ['womb','grow','evert']) {
    const r=simulate(key,input,40);
    near(r.L,p.n*p.pf,1e-12); near(r.B,-.06-p.n*p.pf,1e-12);
    assert.equal(r.Fmax,0); assert.equal(r.born,null);
  }
  assert.equal(simulate('arm',input,.025).Fmax,p.armF);
});
test('external pressure cannot push an unsealed baby and growth alone retains its heel', () => {
  const r=simulate('womb',{...input,pw:2000,inf:false},40);
  assert.equal(r.Fmax,0); assert.equal(r.sealed,false);
  const grown=simulate('grow',{...input,pb:1000},350);
  assert.ok(grown.L>p.n*p.pf); assert.ok(grown.L<=p.n*p.pd);
  near(grown.B,-.06-p.n*p.pf,1e-12); assert.equal(grown.born,null);
});
test('with a seal the pulse force follows pressure times area', () => {
  const run=sketch.initial({key:'womb'},p);
  run.B=-.025;
  sketch.step(run,{...input,pw:1000,inf:false},p,2.25,.025);
  assert.ok(run.sealed); near(run.Fmax,1000*p.Aseal,1e-10);
});

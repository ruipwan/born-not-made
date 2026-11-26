// A composed motion score. Time and distance select a choreography, not a model of animal behaviour.
const TAU = Math.PI * 2;
const duration = 26;
const chapterStarts = [0, 7.5, 16.5];
const chapterFrames = [3.8, 12, 22];
const clamp = (value, low = 0, high = 1) => Math.min(high, Math.max(low, value));
const mix = (a, b, amount) => a + (b - a) * amount;
const ease = value => { const t = clamp(value); return t * t * (3 - 2 * t); };
const ramp = (time, a, b) => ease((time - a) / (b - a));
const doubleBeat = time => {
  const p = ((time % 3.2) + 3.2) % 3.2;
  return Math.exp(-Math.pow((p - .33) / .15, 2)) + .77 * Math.exp(-Math.pow((p - .98) / .17, 2));
};
const descriptions = [
  'The new body repeats the double contraction of the parent on the left. One gesture makes the passage.',
  'From close by, a long turn crosses the water. The young body follows it with a slight delay.',
  'A second child slips free. It carries the slow turn forward, with a wider arc. The older double contraction falls away.'
];
const distantDescriptions = [
  descriptions[0],
  'The neighbor turns at the far edge. The young body keeps its double contraction and drifts along its own course.',
  'A second child slips free. One contraction returns at a longer interval. The neighbor’s turn stays at the far edge.'
];

function addStyles() {
  const url = new URL('./relation.css', import.meta.url).href;
  if (Array.from(document.styleSheets).some(sheet => sheet.href === url)) return;
  if (document.querySelector('link[data-relation-score]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = url;
  link.dataset.relationScore = '';
  document.head.append(link);
}

function waterPlate(width, height) {
  const surface = document.createElement('canvas');
  surface.width = Math.ceil(width);
  surface.height = Math.ceil(height);
  const c = surface.getContext('2d');
  c.fillStyle = '#111111';
  c.fillRect(0, 0, width, height);
  const light = c.createRadialGradient(width * .52, height * .48, 0, width * .52, height * .48, width * .55);
  light.addColorStop(0, '#232323');
  light.addColorStop(.64, '#171717');
  light.addColorStop(1, '#0d0d0d');
  c.fillStyle = light;
  c.fillRect(0, 0, width, height);
  let seed = 87;
  const noise = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  // Narrow grazing light intermittently catches the water surface.
  for (let i = 0; i < 120; i++) {
    const x = width * noise(), y = height * noise();
    const len = width * (.015 + noise() * .14), curve = height * (.008 + noise() * .015);
    const alpha = (.016 + .06 * noise()) * (1 - Math.abs(.48 - x / width));
    const glow = c.createLinearGradient(x, y, x + len, y);
    glow.addColorStop(0, 'transparent');
    glow.addColorStop(.64, 'rgba(255,255,255,' + alpha + ')');
    glow.addColorStop(1, 'transparent');
    c.strokeStyle = glow;
    c.lineWidth = .65;
    c.beginPath();
    c.moveTo(x, y);
    c.bezierCurveTo(x + len * .26, y - curve, x + len * .53, y + curve * .45, x + len, y - curve * .34);
    c.stroke();
  }
  return surface;
}

function shape(s) {
  const profile = Math.pow(Math.max(0, Math.sin(Math.PI * s)), .64);
  return {
    breadth: profile * (1.08 - .16 * s) * (1 + .035 * Math.sin(s * TAU * 11)),
    center: Math.sin(s * TAU) * .115 + (s - .5) * .12
  };
}

function edge(radius, breadth, s, side) {
  const section = shape(s);
  return [(2 * s - 1) * radius, (section.center + side * section.breadth) * breadth];
}

function hullPath(c, radius, breadth) {
  c.beginPath();
  for (let i = 0; i <= 90; i++) {
    const [x, y] = edge(radius, breadth, i / 90, -1);
    if (i === 0) c.moveTo(x, y);
    else c.lineTo(x, y);
  }
  for (let i = 90; i >= 0; i--) c.lineTo(...edge(radius, breadth, i / 90, 1));
  c.closePath();
}

function membrane(c, x, y, radius, angle, pulse, light, seed) {
  if (radius < 2) return;
  c.save();
  c.translate(x, y);
  c.rotate(angle);
  const r = radius * (1 - .035 * pulse);
  const breadth = r * (.36 + .035 * pulse);
  c.translate(0, breadth * .32);
  c.scale(1, 1.05);
  hullPath(c, r, breadth);
  c.fillStyle = 'rgba(0,0,0,.5)';
  c.fill();
  c.scale(1, 1 / 1.05);
  c.translate(0, -breadth * .32);
  hullPath(c, r, breadth);
  const skin = c.createLinearGradient(0, -breadth, 0, breadth);
  skin.addColorStop(0, '#838383');
  skin.addColorStop(.15, '#d4d4d4');
  skin.addColorStop(.34, '#858585');
  skin.addColorStop(.54, '#414141');
  skin.addColorStop(.82, '#777777');
  skin.addColorStop(1, '#222222');
  c.globalAlpha = light;
  c.fillStyle = skin;
  c.fill();
  c.strokeStyle = 'rgba(240,240,240,.66)';
  c.lineWidth = Math.max(.7, r * .008);
  c.stroke();
  c.save();
  c.clip();
  // The opaque motor sits under the translucent membrane. Folds cross it in front.
  c.fillStyle = 'rgba(15,15,15,.56)';
  c.beginPath();
  c.ellipse(-r * .09, breadth * .1, r * .23, breadth * .29, -.11, 0, TAU);
  c.fill();
  for (let i = 0; i < 16; i++) {
    const s = (i + .3) / 16;
    const a = edge(r, breadth, s, -1), b = edge(r, breadth, Math.min(.998, s + .032), 1);
    const swell = Math.sin(s * Math.PI);
    const turn = r * (.08 + .025 * Math.sin(seed + i * .29)) * swell;
    const ridgeX = a[0] + turn;
    const ridgeY = (a[1] + b[1]) * .5 - breadth * .18;
    c.beginPath();
    c.moveTo(...a);
    c.quadraticCurveTo(ridgeX + .01 * r, ridgeY - breadth * .26, ridgeX, ridgeY);
    c.quadraticCurveTo(ridgeX - .008 * r, ridgeY + breadth * .35, ...b);
    c.lineTo(b[0] + r * .05 * swell, b[1]);
    c.quadraticCurveTo(ridgeX + r * .07, ridgeY, a[0] + .055 * r * swell, a[1]);
    c.closePath();
    const bevel = c.createLinearGradient(a[0], 0, a[0] + Math.max(r * .14, 1), 0);
    bevel.addColorStop(0, 'rgba(5,5,5,.5)');
    bevel.addColorStop(.39, 'rgba(40,40,40,.12)');
    bevel.addColorStop(.75, 'rgba(248,248,248,.78)');
    bevel.addColorStop(1, 'rgba(90,90,90,.24)');
    c.fillStyle = bevel;
    c.fill();
    c.beginPath();
    c.moveTo(...a);
    c.quadraticCurveTo(ridgeX, ridgeY - breadth * .22, ridgeX, ridgeY);
    c.strokeStyle = 'rgba(255,255,255,.55)';
    c.lineWidth = Math.max(.45, .007 * r);
    c.stroke();
  }
  c.restore();
  c.restore();
}

function wake(c, x, y, radius, angle, time, strength) {
  c.save();
  c.translate(x, y);
  c.rotate(angle);
  c.lineWidth = Math.max(.6, radius * .009);
  for (let i = 0; i < 4; i++) {
    const cycle = (time * .16 + i * .25) % 1;
    const reach = radius * (.58 + 1.7 * cycle);
    for (const side of [-1, 1]) {
      c.beginPath();
      c.moveTo(-radius * .48 - reach * .25, side * radius * (.1 + .3 * cycle));
      c.bezierCurveTo(-radius * .55 - reach * .5, side * reach * .42, -radius * .5 - reach * .77, side * reach * .52, -radius * .76 - reach, side * reach * (.61 + .05 * side));
      c.strokeStyle = 'rgba(217,217,217,' + (.18 * strength * Math.sin(cycle * Math.PI)) + ')';
      c.stroke();
    }
  }
  c.restore();
}

function makePainter(canvas) {
  const c = canvas.getContext('2d');
  let backdrop, previousKey;
  return (time, nearby) => {
    const width = canvas.clientWidth, height = canvas.clientHeight;
    if (!c || !width || !height) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const key = [width, height, dpr].join('/');
    if (key !== previousKey) {
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      backdrop = waterPlate(width, height);
      previousKey = key;
    }
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.drawImage(backdrop, 0, 0, width, height);
    const unit = Math.min(width * .089, height * .219);
    const leave = ramp(time, 0, 6.8), meet = ramp(time, 7.5, 13.5), after = ramp(time, 16.4, 25.8);
    const youngPulse = doubleBeat(time - .5) * (nearby ? 1 - .84 * meet : 1);
    const parentX = width * (.206 - .03 * leave);
    const parentY = height * (.447 + .018 * Math.sin(time * .27));
    const parentAngle = -.17 + .024 * Math.sin(time * .23);
    const youngX = width * (.23 + .211 * leave + .062 * meet + .057 * after);
    const youngY = height * (.426 + .151 * leave + (nearby ? -.037 : .09) * meet + .064 * after + (nearby ? .072 * meet * Math.sin(time * .68 - 1.1) : .007 * Math.sin(time)));
    const youngAngle = .27 - .14 * leave + (nearby ? .64 * meet * Math.cos(time * .68 - 1.1) : .09 * Math.sin(time * .35));
    const neighX = width * (.866 + (nearby ? -.168 : .004) * meet + .013 * Math.cos(time * .68));
    const neighY = height * (.299 + (nearby ? .025 : -.128) * meet + .045 * Math.sin(time * .68));
    const neighAngle = .07 + .63 * Math.cos(time * .68);
    const nextX = youngX + width * (.005 + .162 * after);
    const nextY = youngY + height * (.005 + .117 * after + (nearby ? .052 * after * Math.sin(time * .54) : 0));
    const nextAngle = .21 + (nearby ? .55 * Math.cos(time * .54) : .025 * Math.sin(time * .31));
    const youngR = unit * (.33 + .215 * leave + .085 * meet);
    const nextR = unit * .39 * ramp(time, 16.5, 20.9);
    const secondBeat = nearby ? 0 : Math.exp(-Math.pow(((time - 16) % 3.8 - .75) / .23, 2));
    const young = [youngX, youngY, youngR, youngAngle, youngPulse, .91, .45];
    const next = [nextX, nextY, nextR, nextAngle, secondBeat, .84, 1.5];
    const parent = [parentX, parentY, unit, parentAngle, doubleBeat(time) * (1 - leave * .6), .95, .74];
    const neighbor = [neighX, neighY, unit * .72, neighAngle, 0, .73, 2.3];
    [neighbor, young, parent, next].forEach(body => {
      if (body[2] > 1) wake(c, ...body.slice(0, 4), time + body[6], .55 + .56 * body[4]);
    });
    [neighbor, next, young, parent].forEach(body => membrane(c, ...body));
    const font = clamp(width / 83, 10, 13);
    c.font = '400 ' + font + 'px ui-monospace, monospace';
    c.textAlign = 'center';
    const notes = [
      [parentX, parentY + unit * .66 + font, 'Parent'],
      [neighX, Math.max(font * 1.8, neighY - unit * .62), 'Neighbor']
    ];
    if (time > 3) notes.push([youngX, youngY + youngR * .72 + font, time >= chapterStarts[2] ? 'New parent' : 'Child']);
    if (time > 20) notes.push([nextX, nextY + nextR * .92 + font, 'Next child']);
    c.fillStyle = '#c1c1c1';
    for (const [x, y, label] of notes) c.fillText(label, x, y);
  };
}

export function mountRelation(container) {
  addStyles();
  const section = document.createElement('div');
  section.className = 'relation-study';
  section.innerHTML = `
    <p class="rs-score">Choreographed study · Three generations</p>
    <div class="rs-stage"><canvas role="img" aria-label="Three generations of folded bodies at the water surface. The adjacent text describes their movements."></canvas></div>
    <div class="rs-moments">
      <div class="rs-steps" role="group" aria-label="Moment in the score">
        <button type="button" data-rs-step="0"><span class="rs-name">First birth</span></button>
        <button type="button" data-rs-step="1"><span class="rs-name">Encounter</span></button>
        <button type="button" data-rs-step="2"><span class="rs-name">Second birth</span></button>
      </div>
      <button class="rs-play" type="button">Play score</button>
    </div>
    <div class="rs-interactions">
      <p class="rs-question">Where does the neighbor go?</p>
      <div class="rs-choice" role="group" aria-label="Neighbor’s distance">
        <button type="button" data-rs-near="1"><span class="rs-name">Stay nearby</span></button>
        <button type="button" data-rs-near="0"><span class="rs-name">Keep a distance</span></button>
      </div>
    </div>
    <p class="rs-caption" role="status" aria-live="polite"></p>`;
  container.append(section);
  const steps = [...section.querySelectorAll('[data-rs-step]')];
  const choices = [...section.querySelectorAll('[data-rs-near]')];
  const play = section.querySelector('.rs-play');
  const caption = section.querySelector('.rs-caption');
  const canvas = section.querySelector('canvas');
  const paint = makePainter(canvas);
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let time = motion.matches ? chapterFrames[0] : 0;
  let playing = !motion.matches;
  let near = true, active = true, onScreen = false, raf = 0, lastFrame = null, lastCaption;

  function update() {
    const chapter = time >= chapterStarts[2] ? 2 : time >= chapterStarts[1] ? 1 : 0;
    steps.forEach((button, i) => button.setAttribute('aria-pressed', String(i === chapter)));
    choices.forEach(button => button.setAttribute('aria-pressed', String((button.dataset.rsNear === '1') === near)));
    const description = (near ? descriptions : distantDescriptions)[chapter];
    if (description !== lastCaption) { caption.textContent = description; lastCaption = description; }
    play.textContent = playing ? 'Pause' : time >= duration ? 'Replay' : 'Play score';
    paint(time, near);
  }
  function frame(now) {
    if (lastFrame !== null && now - lastFrame < 1000 / 30) { raf = requestAnimationFrame(frame); return; }
    if (lastFrame !== null) time = Math.min(duration, time + (now - lastFrame) / 1000);
    lastFrame = now;
    if (time >= duration) playing = false;
    update();
    raf = playing ? requestAnimationFrame(frame) : 0;
  }
  function schedule() {
    cancelAnimationFrame(raf);
    raf = 0;
    lastFrame = null;
    update();
    if (playing && active && onScreen && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function click(event) {
    const button = event.target.closest('button');
    if (!button) return;
    if (button === play) {
      if (time >= duration) time = 0;
      playing = !playing;
    } else if ('rsStep' in button.dataset) {
      const step = Number(button.dataset.rsStep);
      time = playing ? chapterStarts[step] : chapterFrames[step];
    } else {
      const nextNear = button.dataset.rsNear === '1';
      if (near !== nextNear || time < chapterStarts[1]) {
        near = nextNear;
        time = playing ? chapterStarts[1] : chapterFrames[1];
      }
    }
    schedule();
  }
  function preference() {
    if (motion.matches) { playing = false; if (time < .01) time = chapterFrames[0]; schedule(); }
  }
  const intersection = new IntersectionObserver(([entry]) => { onScreen = entry.isIntersecting; schedule(); });
  const resize = new ResizeObserver(() => paint(time, near));
  intersection.observe(canvas);
  resize.observe(canvas);
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', preference);
  section.addEventListener('click', click);
  update();
  return {
    setActive(value) { active = Boolean(value); schedule(); },
    destroy() {
      active = false; playing = false; cancelAnimationFrame(raf);
      intersection.disconnect(); resize.disconnect();
      motion.removeEventListener('change', preference);
      document.removeEventListener('visibilitychange', schedule);
      section.removeEventListener('click', click);
      section.remove();
    }
  };
}

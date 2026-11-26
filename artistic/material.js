// Print Then Breathe. A cinematic longitudinal section of the proposed S8 body.
// Coordinates are composition units. Motion is a staged interpretation of the
// four design states, not a forward dynamics or buoyancy solver.
const W = 1024;
const H = 540;
const TAU = Math.PI * 2;
const clamp = (x, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = (a, b, x) => {
  const f = clamp((x - a) / (b - a));
  return f * f * (3 - 2 * f);
};
const gray = (n, alpha = 1) => `rgba(${n},${n},${n},${alpha})`;

function layer(width, height) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return canvas;
}

function gradient(ctx, x0, y0, x1, y1, stops) {
  const paint = ctx.createLinearGradient(x0, y0, x1, y1);
  stops.forEach(([at, color]) => paint.addColorStop(at, color));
  return paint;
}

function path(ctx, d, fill, stroke, lineWidth = 1) {
  const shape = new Path2D(d);
  if (fill) { ctx.fillStyle = fill; ctx.fill(shape); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lineWidth; ctx.stroke(shape); }
}

function ellipse(ctx, x, y, rx, ry, fill, stroke, weight = 1) {
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, 0, 0, TAU);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = weight; ctx.stroke(); }
}

function line(ctx, points, color, weight) {
  ctx.beginPath();
  ctx.moveTo(...points[0]);
  for (let i = 1; i < points.length; i++) ctx.lineTo(...points[i]);
  ctx.strokeStyle = color;
  ctx.lineWidth = weight;
  ctx.stroke();
}

function randomSource(seed) {
  return () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

// Upper/lower half shells meet at the pointed bow. The stern is intentionally
// interrupted between its two moving lids, so the child can clear the section.
const hull = 'M96 289 C210 193 322 94 463 67 C555 49 649 62 699 128 C725 162 736 194 739 223 L709 234 C704 193 679 153 636 123 C580 86 506 83 437 101 C311 132 220 207 121 289 C221 368 340 424 456 425 C557 429 643 391 682 334 Q694 317 698 302 L732 305 C716 369 670 416 606 444 C480 497 313 460 202 391 C161 366 122 327 96 289 Z';
const interior = 'M105 289 C232 176 345 90 490 80 C597 67 686 113 716 203 C725 240 724 291 705 331 C663 425 546 465 412 442 C285 423 180 352 105 289Z';
const basin = 'M142 298 Q375 275 670 294 Q691 296 697 302 C670 379 569 420 453 419 C349 418 235 364 142 298Z';

function drawBackground(ctx) {
  ctx.fillStyle = gradient(ctx, 0, 0, 0, H, [
    [0, '#0a0a0a'], [.38, '#191919'], [.53, '#1d1d1d'], [.55, '#303030'], [.6, '#202020'], [1, '#0c0c0c']
  ]);
  ctx.fillRect(0, 0, W, H);
  const softbox = ctx.createRadialGradient(449, 193, 25, 449, 193, 600);
  softbox.addColorStop(0, gray(125, .14));
  softbox.addColorStop(.6, gray(97, .055));
  softbox.addColorStop(1, gray(0, .22));
  ctx.fillStyle = softbox;
  ctx.fillRect(0, 0, W, H);
  const rng = randomSource(2103);
  for (let i = 0; i < 610; i++) {
    const y = 287 + Math.pow(rng(), 1.6) * 253;
    const x = rng() * W;
    const span = 2 + rng() ** 3 * (11 + (y - 287) * .32);
    const value = rng() > .42 ? 219 : 5;
    line(ctx, [[x, y], [x + span * .44, y - rng() * .75], [x + span, y]], gray(value, .017 + rng() * .085), .4 + rng() * .8);
  }
  for (let i = 0; i < 250; i++) {
    const x = rng() * W, y = 299 + rng() * 241;
    ellipse(ctx, x, y, .2 + rng() * .7, .35 + rng() * .55, gray(222, .03 + rng() * .18));
  }
  const shade = ctx.createRadialGradient(465, 469, 3, 465, 469, 250);
  shade.addColorStop(0, gray(0, .56)); shade.addColorStop(1, gray(0, 0));
  ctx.save(); ctx.translate(0, 364); ctx.scale(1, .23); ctx.fillStyle = shade;
  ctx.fillRect(170, 160, 620, 620); ctx.restore();
}

// Reflections are evaluated once on the concave interior surface. The profile
// comes from the section outline so a highlight also bends at the pointed bow.
function innerWall() {
  const surface = layer(W,H), surfaceCtx = surface.getContext('2d');
  surfaceCtx.fill(new Path2D(interior));
  const pixels=surfaceCtx.getImageData(0,0,W,H), data=pixels.data;
  const noise=randomSource(5519);
  for (let x=104;x<728;x++) {
    let top=60, bottom=454;
    while (top<bottom && data[(top*W+x)*4+3]===0) top++;
    while (bottom>top && data[(bottom*W+x)*4+3]===0) bottom--;
    const half=Math.max(1,(bottom-top)*.5);
    const u=(x-104)/624;
    for (let y=top;y<=bottom;y++) {
      const v=(y-top)/half-1;
      const nz=Math.sqrt(Math.max(0,1-v*v));
      const shadow = .82+.18*Math.sin(u*Math.PI);
      const strip = Math.exp(-((v+.67-.20*Math.sin(u*5.4))**2)/.022);
      const ambient = 21+22*(1-u)+22*(1-nz)**2+17*strip*shadow;
      const reflectedSky = 17*Math.exp(-((v+.1+.44*(u-.4))**2)/.15)*(1-u);
      const fine = (noise()-.5)*4;
      const val = Math.round(ambient + reflectedSky + fine);
      const k=(y*W+x)*4;
      data[k]=data[k+1]=data[k+2]=val;
    }
  }
  surfaceCtx.putImageData(pixels,0,0);
  return surface;
}

function drawVessel(ctx) {
  const cavityLight = gradient(ctx, 150, 100, 630, 407, [
    [0, '#626262'], [.35, '#414141'], [.63, '#272727'], [1, '#121212']
  ]);
  path(ctx, interior, cavityLight);
  ctx.drawImage(innerWall(),0,0);
  ctx.save();
  ctx.clip(new Path2D(interior));
  // The aft opening can see through both the cutaway and the water beyond.
  const opening = new Path2D('M695 178 Q736 179 760 200 L767 331 L685 327 Q713 266 695 178Z');
  ctx.save(); ctx.clip(opening);
  ctx.fillStyle = gradient(ctx, 0, 180, 0, 335, [[0, '#232323'], [.70, '#282828'], [.72, '#383838'], [1, '#252525']]);
  ctx.fillRect(680, 170, 90, 171);
  ctx.restore();
  // Ribs on the far wall turn into the darker side of the section.
  for (let k = 0; k < 9; k++) {
    const x = 165 + 59 * k;
    path(ctx, `M${x} 74 Q${x-64} 229 ${x-20} 412`, null, gray(237, .048), 1.15);
    path(ctx, `M${x+1.7} 74 Q${x-62} 229 ${x-18} 412`, null, gray(0, .075), 1.9);
  }
  // The section reveals one of the two reservoir bays. It is behind the arm.
  path(ctx, 'M287 182 Q337 138 392 127 L414 132 L407 178 Q349 185 291 220Z',
    gradient(ctx, 290, 140, 412, 211, [[0, '#282828'], [.37, '#6a6a6a'], [.6, '#424242'], [1, '#232323']]), gray(150, .5), 1.2);
  path(ctx, 'M292 183 Q339 145 387 133 M301 191 Q348 155 397 143', null, gray(222, .36), .9);
  path(ctx, 'M389 159 C417 161 442 155 461 128', null, '#202020', 5.8);
  path(ctx, 'M389 158 C417 160 442 154 461 127', null, '#999999', 1.1);
  const drain = 'M484 117 Q548 111 566 156 Q574 183 574 254 Q574 263 580 266';
  path(ctx,drain,null,gray(16,.82),4.6);
  path(ctx,drain,null,gray(163,.67),1.6);
  // Bolted bilge plates and low sealed component housings sit beneath the bath.
  path(ctx, 'M285 360 Q398 406 528 399 L569 411 Q423 458 285 377Z', '#252525', '#636363', 1);
  for (let i = 0; i < 7; i++) {
    const x = 360 + i * 23, y = 401 + Math.sin(i / 6 * Math.PI) * 4;
    path(ctx, `M${x} ${y} l16 2 7 -3 -1 8 -8 4 -15 -2Z`, gray(83 - i * 2), gray(116, .6), .8);
  }
  const gel = gradient(ctx, 0, 283, 0, 427, [[0, gray(225, .28)], [.12, gray(201, .14)], [.65, gray(167, .11)], [1, gray(211, .28)]]);
  path(ctx, basin, gel, gray(196, .39), 1.2);
  path(ctx, 'M142 298 Q381 310 686 297 Q673 292 640 291 Q344 278 142 298Z',
    gradient(ctx, 0, 283, 0, 305, [[0, gray(197, .2)], [.7, gray(203, .15)], [1, gray(239, .44)]]));
  const rng = randomSource(8021);
  ctx.save(); ctx.clip(new Path2D(basin));
  // Soft overhead reflections break into narrow caustics at the bilge.
  for(let i=0;i<21;i++){
    const x=220+i*16+rng()*10, y=400+rng()*20;
    path(ctx,`M${x-44} ${y-17} Q${x-6} ${y-8} ${x+5} ${y-3} T${x+56} ${y+2}`,
      null,gray(224,.055+rng()*.15),.65+rng()*1.2);
  }
  for (let i = 0; i < 220; i++) {
    const x = 144 + rng() * 550, y = 292 + rng() * 125, r = rng() ** 4 * 1.8 + .16;
    ellipse(ctx, x, y, r, r * 1.08, gray(35, .25), gray(230, rng() * .30), .6);
  }
  ctx.restore(); ctx.restore();
  const shellLight = gradient(ctx, 210, 62, 496, 462, [
    [0, '#676767'], [.12, '#cdcdcd'], [.27, '#b8b8b8'], [.43, '#5b5b5b'],
    [.53, '#373737'], [.65, '#909090'], [.79, '#616161'], [1, '#282828']
  ]);
  path(ctx, hull, shellLight, gray(201, .66), 1.1);
  ctx.save(); ctx.clip(new Path2D(hull));
  // Grazing light follows the crown and the submerged shell’s turning surface.
  ctx.lineCap = 'round';
  for (let i = 0; i < 20; i++) {
    path(ctx, `M91 ${288+i*.75} Q402 ${-29+i*.9} 611 ${76+i*1.05} Q699 ${102+i} 741 223`, null, gray(247, .024), 1.4);
    path(ctx, `M100 293 Q312 ${496-i*.95} 521 ${461-i*.85} Q672 ${445-i*.7} 734 313`, null, gray(232, .035), 1);
  }
  ctx.restore();
  path(ctx, 'M101 286 C209 195 336 81 477 64 Q574 49 635 78', null, gray(243, .81), 1.6);
  path(ctx, 'M129 298 Q333 464 502 428 Q654 406 698 304', null, gray(4, .67), 4);
  path(ctx, 'M130 300 Q336 464 502 430 Q655 408 700 304', null, gray(217, .63), 1.15);
  // A small flange at the roof is a visible reference point for the moving arm.
  path(ctx, 'M451 95 L506 89 L521 98 L519 106 L464 113 L451 106Z', '#636363', '#b6b6b6', 1);
}

function drawDoor(ctx, opened) {
  // Each curved lid translates inward, then slides along its own inner rail.
  ctx.save();
  ctx.translate(-18 * opened, -46 * opened); ctx.translate(720, 194); ctx.rotate(-.38 * opened); ctx.translate(-720, -194);
  path(ctx, 'M675 111 Q739 150 742 246 L738 268 L727 270 Q728 171 668 127Z',
    gradient(ctx, 672, 130, 742, 257, [[0,'#999999'],[.4,'#d2d2d2'],[.56,'#727272'],[1,'#343434']]), '#a0a0a0', 1.3);
  path(ctx, 'M682 124 Q737 165 738 257', null, gray(236, .63), 1.1);
  ctx.restore();
  ctx.save();
  ctx.translate(-10 * opened, 38 * opened); ctx.translate(718, 332); ctx.rotate(.39 * opened); ctx.translate(-718, -332);
  path(ctx, 'M737 270 L742 268 Q746 328 701 381 L685 370 Q722 329 727 272Z',
    gradient(ctx, 681, 371, 748, 271, [[0,'#3c3c3c'],[.35,'#858585'],[.8,'#a3a3a3'],[1,'#535353']]), '#8d8d8d', 1.1);
  path(ctx, 'M733 277 Q732 329 699 366', null, gray(240, .44), 1);
  ctx.restore();
}

function joint(ctx, x, y, r) {
  const metal = ctx.createRadialGradient(x - r * .28, y - r * .45, .1, x, y, r);
  metal.addColorStop(0, '#d4d4d4'); metal.addColorStop(.63, '#868686');
  metal.addColorStop(.78, '#505050'); metal.addColorStop(.92, '#373737'); metal.addColorStop(1, '#b4b4b4');
  ellipse(ctx, x + 3, y + 3, r + 2, r + 1, gray(5, .6));
  ellipse(ctx, x, y, r, r, metal, '#303030', 1.2);
  ellipse(ctx, x, y, r * .48, r * .48, '#424242', '#d3d3d3', .9);
  ellipse(ctx, x - .4, y - .5, r * .17, r * .17, '#c1c1c1');
  for (let j = 0; j < 4; j++) {
    const a = .61 + j * Math.PI / 2;
    ellipse(ctx, x + r * .7 * Math.cos(a), y + r * .7 * Math.sin(a), 1, 1, '#242424');
  }
}

function armLink(ctx, a, b, width) {
  const dx = b.x-a.x, dy = b.y-a.y, len = Math.hypot(dx, dy);
  ctx.save(); ctx.translate(a.x, a.y); ctx.rotate(Math.atan2(dy, dx));
  const w = width, l = len;
  const shape = `M1 ${-w*.49} Q14 ${-w*.78} 32 ${-w*.5} L${l-25} ${-w*.31} L${l-8} ${-w*.52} L${l+1} ${-w*.23} L${l-1} ${w*.44} L${l-19} ${w*.64} L${l-33} ${w*.38} L23 ${w*.52} Q6 ${w*.76} 1 ${w*.49}Z`;
  path(ctx, shape, gradient(ctx, 0, -w * .7, 0, w*.8, [[0,'#f1f1f1'],[.18,'#d8d8d8'],[.49,'#c2c2c2'],[.71,'#9e9e9e'],[.76,'#656565'],[1,'#434343']]), '#232323', 1.5);
  path(ctx, `M25 ${-w*.27} Q${l*.4} ${-w*.14} ${l-29} ${-w*.15} L${l-38} ${w*.07} L32 ${w*.15}Z`, '#464646', '#dfdfdf', .6);
  line(ctx, [[28,-w*.4],[l-29,-w*.23]], gray(250,.8), .8);
  ctx.restore();
}

function drawCore(ctx, x, y, scale, opacity) {
  ctx.save(); ctx.globalAlpha = opacity; ctx.translate(x, y); ctx.scale(scale, scale);
  ctx.rotate(-.045);
  path(ctx, 'M-33 -7 L11 -10 L27 -4 L27 9 L-19 13 L-33 8Z', '#333333', '#d2d2d2', 1);
  path(ctx, 'M-33 -7 L10 -12 L26 -7 L-18 -2Z', '#808080', '#cecece', .8);
  for (let j = 0; j < 8; j++) {
    line(ctx, [[-24+j*5,3],[-21+j*5,5],[-18+j*5,4]], '#bcbcbc', .7);
  }
  path(ctx, 'M-20 -10 L-18 -17 L-5 -17 L-3 -11 L-6 -7 L-18 -6Z', '#242424', '#acacac', .8);
  ctx.fillStyle = gradient(ctx, 0, -15, 0, 3, [[0,'#272727'],[.25,'#cecece'],[.48,'#a9a9a9'],[.8,'#454545'],[1,'#252525']]);
  ctx.fillRect(0, -15, 23, 15);
  ellipse(ctx, 23, -7.5, 3.2, 7.5, '#707070', '#c8c8c8', 1);
  line(ctx, [[25,-7],[32,-7]], '#d9d9d9', 2);
  ellipse(ctx, -26, 1, 2.1, 1.8, '#222222', '#ededed', .8);
  path(ctx, 'M-9 -13 C-8 -27 12 -26 10 -13', null, '#c8c8c8', 1.7);
  ctx.restore();
}

const skinFrames = new Map();

// A surface of revolution with corrugated meridians. Local unfolding changes
// the spacing/depth of folds. Normals and a reflected strip light shade each pixel.
function membrane(inflation) {
  const phase = Math.round(inflation * 48);
  if (skinFrames.has(phase)) return skinFrames.get(phase);
  const f = phase / 48, sx = 61 + 17*f, sy = 31 + 13*f;
  const cell = layer(344, 224), ctx = cell.getContext('2d');
  const data = ctx.createImageData(cell.width, cell.height), p = data.data;
  const profile = u => {
    const base = Math.max(0, 1-u*u) ** .59;
    const local = ease(-1.0, .8, 2.4*f - u - 1.1);
    const amplitude = .18 - .138 * local;
    const ripple = Math.cos(6.25*Math.PI*u + .72*Math.sin(2.6*u) - .38);
    return base * (1 - amplitude * (.5 + .5*ripple)) * (1 + .055*u);
  };
  for (let ix = 0; ix < cell.width; ix++) {
    const x = (ix - cell.width/2) * .5, u = x/sx;
    if (Math.abs(u) >= 1) continue;
    const radius = sy*profile(u);
    const gradientX = (profile(u + .001) - profile(u - .001)) * sy/(.002*sx);
    for (let iy = 0; iy < cell.height; iy++) {
      const v = ((iy-cell.height/2)*.5 - 1.6*Math.sin(2*u+.4)) / radius;
      if (Math.abs(v) >= 1) continue;
      const z = Math.sqrt(1-v*v);
      const il = 1/Math.sqrt(gradientX*gradientX + 1);
      const nx = -gradientX*il, ny = v*il, nz = z*il;
      const diffuse = Math.max(0, -.48*nx - .7*ny + .52*nz);
      const soft = Math.exp(-((ny + .48)**2/.037 + (nx+.26)**2/.8));
      const strip = Math.exp(-((ny+.72+.09*Math.sin(u*7))**2/.0038 + (nx+.26)**2/.52));
      const edge = (1 - nz)**3.7;
      const transmission = Math.exp(-((ny-.62)**2/.13 + nx*nx/1.55));
      const pore = (Math.sin(ix*12.8+iy*1.4)*Math.cos(iy*5.7+ix*.8))*1.5;
      const luminance = clamp(41 + 130*diffuse + 41*soft + 39*strip + 65*edge + 31*transmission + pore, 0, 254);
      const idx = (iy*cell.width + ix)*4;
      p[idx] = p[idx+1] = p[idx+2] = luminance;
      p[idx+3] = Math.floor((.81 + .17*edge) * 255 * clamp((1-Math.abs(v))*radius*2.5));
    }
  }
  ctx.putImageData(data, 0, 0);
  skinFrames.set(phase, cell);
  return cell;
}

function stateAt(t) {
  const deposited = ease(.17, .53, t);
  const inflate = .67 * ease(.62, .76, t) + .33 * ease(.78, .90, t);
  const carrierTravel = ease(.73, .915, t);
  const independent = ease(.926, 1, t);
  const x = 468 + carrierTravel * 363 + independent * 61;
  const y = 328 - ease(.61, .73, t)*46 - carrierTravel*37 + independent*39;
  const r = 31 + inflate*13;
  const pass = deposited * TAU * 6;
  const printY = 32 - 64*deposited;
  const pathRX = 59*Math.sqrt(Math.max(0, 1 - (printY/33)**2));
  const nozzleX = x + Math.cos(pass)*pathRX;
  const nozzleY = y + printY + Math.sin(pass)*3;
  const approach = ease(.025,.16,t);
  const toPort = ease(.51,.58,t);
  const release = ease(.925,.988,t);
  const tx = lerp(lerp(lerp(554,nozzleX,approach), x+4, toPort), 557, release);
  const ty = lerp(lerp(lerp(219,nozzleY,approach), y-r+3,toPort), 162, release);
  const load=ease(.005,.13,t);
  const door=Math.max(1-ease(.079,.158,t),ease(.70,.79,t)*(1-ease(.93,1,t)));
  return {t, x, y, r, deposited, inflate, nozzleX, nozzleY, tx, ty, carrierTravel, independent,door,load};
}

function drawChild(ctx, s) {
  // The core follows the stern opening into the gel before fabrication starts.
  const coreX=s.x+344*(1-s.load);
  const coreY=s.y-72*(1-s.load*s.load*s.load);
  if (s.load<1) {
    const retreat=ease(.076,.13,s.t);
    ctx.save();ctx.globalAlpha=1-retreat;
    const endX=coreX+30+210*retreat,endY=coreY-5-25*retreat;
    path(ctx,`M1028 227 Q${endX+125} ${endY-11} ${endX+12} ${endY-3} L${endX} ${endY+2}`,null,'#7a7a7a',2.7);
    path(ctx,`M1028 232 Q${endX+124} ${endY-3} ${endX+12} ${endY+3} L${endX} ${endY+5}`,null,'#b6b6b6',1.2);
    ctx.restore();
  }
  drawCore(ctx, coreX, coreY, 1, 1);
  if (s.deposited <= 0) return;
  const skin = membrane(s.inflate);
  const top = s.y + 34 - 72*s.deposited - Math.max(0, s.r-31);
  ctx.save();
  ctx.beginPath(); ctx.rect(s.x-91, top, 182, 130); ctx.clip();
  ctx.drawImage(skin, s.x-86, s.y-56, 172, 112);
  ctx.restore();
  if(s.deposited>.94){
    const valveY=s.y-s.r+3;
    ctx.save();ctx.globalAlpha=ease(.94,1,s.deposited);
    path(ctx,`M${s.x+1} ${valveY+6} L${s.x+1.5} ${valveY+1} Q${s.x+4} ${valveY-1} ${s.x+6.5} ${valveY+1} L${s.x+8} ${valveY+6}Z`,
      '#6b6b6b',gray(220,.75),.7);
    ctx.restore();
  }
  if (s.t>.548 && s.t<.638) {
    const drain=ease(.548,.638,s.t);
    const level=-19+42*drain;
    const extent=48*Math.sqrt(Math.max(0,1-(level/25)**2));
    const opacity=Math.sin(Math.PI*drain);
    ctx.beginPath();ctx.ellipse(s.x,s.y+level,extent,2.0,0,0,TAU);
    ctx.strokeStyle=gray(230,.53*opacity);ctx.lineWidth=1.05;ctx.stroke();
    const stream=gradient(ctx,0,266,0,295,[[0,gray(186,.72*opacity)],[1,gray(219,.28*opacity)]]);
    path(ctx,'M580 266 Q583 269 583 282 Q583 291 586 294',null,stream,1.8);
    ripples(ctx,586,294,opacity*.66,drain);
  }
  // A small feedstock meniscus at the advancing print front makes the
  // deposited material and the end effector share a single visible point.
  if (s.deposited > .03 && s.deposited < .98) {
    const dy = (32 - 64*s.deposited) / 33;
    const span = 58*Math.sqrt(Math.max(0,1-dy*dy));
    ctx.beginPath(); ctx.ellipse(s.x, s.nozzleY, span, 3.1, 0, 0, Math.PI);
    ctx.strokeStyle=gray(232,.72); ctx.lineWidth=1.4; ctx.stroke();
    ellipse(ctx, s.nozzleX, s.nozzleY, 2.5, 1.5, '#e9e9e9');
  }
}

function drawArm(ctx, s) {
  const mount = {x:486, y:119};
  // The same connector changes use. It rotates towards the valve before carry.
  const tilt = .10 + .29*s.carrierTravel - .35*ease(.925,.985,s.t);
  const tip = {x:s.tx, y:s.ty};
  const wrist = {x:tip.x-56*Math.sin(tilt), y:tip.y-56*Math.cos(tilt)};
  const dx = wrist.x-mount.x, dy = wrist.y-mount.y;
  const distance = Math.max(.01,Math.hypot(dx,dy));
  const a = 154, b = 179;
  const along = (a*a-b*b+distance*distance)/(2*distance);
  // Foreshorten the out-of-plane elbow when reaching to the forward side of
  // the gel, keeping the joint and the delivery hose inside the roof.
  const yaw = .43 + .57*ease(-40,110,dx);
  const transverse = yaw*Math.sqrt(Math.max(0,a*a-along*along));
  const elbow = {x:mount.x+(dx*along-dy*transverse)/distance, y:mount.y+(dy*along+dx*transverse)/distance};
  const hose=`M477 108 Q${elbow.x-37} ${elbow.y+3} ${elbow.x-10} ${elbow.y+16} Q${wrist.x-31} ${wrist.y+26} ${wrist.x-5} ${wrist.y}`;
  path(ctx,hose,null,'#171717',4.7);
  path(ctx,hose,null,'#939393',1.35);
  armLink(ctx, mount, elbow, 24);
  armLink(ctx, elbow, wrist, 20);
  joint(ctx, mount.x,mount.y,16);
  joint(ctx, elbow.x,elbow.y,13.5);
  joint(ctx, wrist.x,wrist.y,9.3);
  ctx.save();
  ctx.translate(wrist.x,wrist.y);
  ctx.rotate(-tilt);
  path(ctx, 'M-7 2 L7 2 L8 14 L5 17 L-4 17 L-8 13Z', '#b7b7b7', '#404040', 1.1);
  path(ctx, 'M-5 16 L5 16 L5.6 34 L2.5 38 L-2 38 L-5.5 35Z',
    gradient(ctx,-6,0,6,0,[[0,'#5d5d5d'],[.32,'#e5e5e5'],[.62,'#afafaf'],[1,'#535353']]), '#404040', .8);
  line(ctx,[[-5,19],[-9,15],[-10,10]],'#c6c6c6',2.1);
  line(ctx,[[0,37],[0,56]],'#ededed',1.4);
  line(ctx,[[1.1,38],[1.1,55]],'#707070',.65);
  ctx.restore();
}

function ripples(ctx, cx, cy, energy, phase) {
  if (energy < .005) return;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(1,.105);
  for (let i=0;i<8;i++) {
    const r = ((i + phase) / 8)*143 + 4;
    ctx.beginPath(); ctx.ellipse(0,0,r,r,0,.07*Math.PI,.94*Math.PI);
    ctx.strokeStyle=gray(227,.24*energy*(1-r/159)); ctx.lineWidth=3.4; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0,0,r,r,0,1.05*Math.PI,1.65*Math.PI);
    ctx.strokeStyle=gray(223,.19*energy*(1-r/159)); ctx.lineWidth=2.2; ctx.stroke();
  }
  ctx.restore();
}

export function createMaterialScene(canvas) {
  const ctx = canvas.getContext('2d', {alpha:false});
  if (!ctx) throw new Error('A 2D canvas is required to display the material study.');
  const background = layer(W*1.5, H*1.5);
  const bg = background.getContext('2d');
  bg.scale(1.5, 1.5); drawBackground(bg);
  const body = layer(W*1.5, H*1.5);
  const boat = body.getContext('2d');
  boat.scale(1.5, 1.5); drawVessel(boat);
  let time = 0, disposed = false;
  function draw() {
    if (disposed) return;
    const w = canvas.width, h = canvas.height;
    const scale = Math.min(w/W, h/H);
    if (!scale) return;
    ctx.setTransform(1,0,0,1,0,0);
    ctx.fillStyle='#101010'; ctx.fillRect(0,0,w,h);
    ctx.drawImage(background,0,0,w,h);
    ctx.setTransform(scale,0,0,scale,(w-W*scale)/2,(h-H*scale)/2);
    const s=stateAt(time);
    // The close view follows the material, then gives the child space at exit.
    const close = ease(.11,.33,time)*(1-ease(.65,.87,time));
    ctx.translate(W*.5,H*.5);
    ctx.scale(1+.30*close,1+.30*close);
    ctx.translate(-lerp(W*.5,469,close),-lerp(H*.5,289,close));
    ctx.drawImage(background,0,0,W,H);
    // A small displacement at release is visible against the fixed waterline.
    const bob = Math.sin(time*TAU*1.6)*1.15;
    ctx.save(); ctx.translate(0,bob);
    ctx.translate(456,290); ctx.rotate(.008*Math.sin(time*Math.PI)*s.carrierTravel); ctx.translate(-456,-290);
    ctx.drawImage(body,0,0,W,H);
    drawDoor(ctx,s.door);
    drawChild(ctx,s);
    drawArm(ctx,s);
    ctx.restore();
    const shimmer = (Math.sin(time*TAU*2.1)+1)*.5;
    path(ctx,`M0 289 Q49 ${291+shimmer} 105 289 M734 289 Q875 ${287-shimmer} 1024 289`,null,gray(216,.25),.8);
    ripples(ctx,123,292,.48,.1+time);
    ripples(ctx,749,291,.32 + .35*s.carrierTravel,.4+time);
    ripples(ctx,s.x,s.y+19,s.independent,1-time);
  }
  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.round(rect.width*dpr), height = Math.round(rect.height*dpr);
    if (canvas.width !== width || canvas.height !== height) { canvas.width=width; canvas.height=height; }
    draw();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(canvas); resize();
  return {
    setProgress(fraction) { if (Number.isFinite(fraction)) time=clamp(fraction); draw(); },
    destroy() { disposed=true; observer.disconnect(); }
  };
}

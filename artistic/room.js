// A stage model: dimensions are in metres; time and stock are rehearsal units.
const TAU=Math.PI*2;
const clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n));
const mix=(a,b,t)=>a+(b-a)*t;
const smooth=(a,b,t)=>{ const k=clamp((t-a)/(b-a));return k*k*(3-2*k); };
const blend=(a,b,t)=>a.map((v,i)=>mix(v,b[i],t));
const gray=(v,a=1)=>`rgba(${v},${v},${v},${a})`;
const length=v=>Math.hypot(...v);
const unit=v=>v.map(x=>x/length(v));
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const STUDIES=[
  {name:'Witness', prompt:'Take a position beside the water.', actions:['At the copper strip','Across the tank']},
  {name:'A stranger', prompt:'Place a second body in the water after release.', actions:['Bring the neighbor near','Keep the neighbor distant']},
  {name:'The night shift', prompt:'Who supplies the next birth after the gallery closes?', actions:['Wait one cycle','Replenish the reservoir']}
];
const initialNotice=[
  'Two visitors face the same tank. One can reach the copper strip. The other can see the gap at the stern.',
  'The newborn has entered the water. Another soft body is resting by the far wall of the tank.',
  'Cycle 0. Two portions remain. Each portion includes silicone and an assembled motor core. A refill occupies one rehearsal cycle.'
];
const directions=['witness','stranger','night-shift'];

function camera(eye,aim,fov,width,height) {
  const f=unit(aim.map((v,i)=>v-eye[i])), right=unit(cross([0,1,0],f)), up=cross(f,right);
  const focal=height/(2*Math.tan(fov*Math.PI/360));
  return p=>{
    const delta=p.map((v,i)=>v-eye[i]),d=dot(delta,f);
    return [width*.5+focal*dot(delta,right)/Math.max(.06,d),height*.50-focal*dot(delta,up)/Math.max(.06,d),d];
  };
}

function line(ctx,points,color,weight=1) {
  ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));
  ctx.strokeStyle=color;ctx.lineWidth=weight;ctx.stroke();
}
function poly(ctx,points,fill,stroke=null,weight=1) {
  ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();
  if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=weight;ctx.stroke();}
}
function ellipse(ctx,x,y,rx,ry,fill,stroke=null,weight=1){
  if(rx<=0||ry<=0)return;
  ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,TAU);
  if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=weight;ctx.stroke();}
}
function gradient(ctx,x0,y0,x1,y1,stops){
  const g=ctx.createLinearGradient(x0,y0,x1,y1);stops.forEach(([n,v])=>g.addColorStop(n,v));return g;
}
function worldLine(ctx,P,pts,color,width) {line(ctx,pts.map(P),color,width);}
function worldPoly(ctx,P,pts,fill,stroke,width) {poly(ctx,pts.map(P),fill,stroke,width);}
function randomGenerator(seed) {return ()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};}

function roomShell(ctx,P,mode) {
  ctx.fillStyle='#151515';ctx.fillRect(0,0,2400,500);
  const night=mode===2;
  worldPoly(ctx,P,[[-20,0,7],[17,0,7],[17,6,7],[-20,6,7]],
    gradient(ctx,0,0,40,350,[[0,night?'#151515':'#252525'],[.53,night?'#333333':'#444444'],[1,night?'#242424':'#333333']]));
  worldPoly(ctx,P,[[7,0,-15],[7,0,7],[7,6,7],[7,6,-15]],
    gradient(ctx,0,0,960,0,[[0,'#141414'],[.8,night?'#262626':'#353535'],[1,'#242424']]));
  worldPoly(ctx,P,[[-24,0,-11],[22,0,-11],[22,0,7],[-24,0,7]],
    gradient(ctx,0,209,120,500,[[0,night?'#282828':'#383838'],[.34,night?'#353535':'#4d4d4d'],[1,night?'#181818':'#282828']]));
  // Expansion joints and distant skirting give the eye a stable room scale.
  for(let x=-9;x<=9;x+=1.6)worldLine(ctx,P,[[x,.006,-3],[x,.006,7]],gray(80,.52),.7);
  for(let z=-2;z<7;z+=1.6)worldLine(ctx,P,[[-8,.006,z],[7,.006,z]],gray(86,.56),.8);
  worldLine(ctx,P,[[-12,.06,7],[7,.06,7],[7,.06,-8]],'#171717',2);
  for(let x=-8;x<=7;x+=2.2)worldLine(ctx,P,[[x,.12,7],[x,5,7]],gray(124,.16),.75);
  const cx=1.4;
  worldPoly(ctx,P,[[cx-3,.06,6.98],[cx+2.8,.06,6.98],[cx+2.8,3.83,6.98],[cx-3,3.83,6.98]],
    gradient(ctx,470,80,610,315,[[0,gray(191,.022)],[.58,gray(220,.061)],[1,gray(210,.11)]]));
  // The floor catches secondary light under the glass. A soft reflection of
  // the surface is legible even after visitors have left for the night.
  const patch=P([.19,.015,-.05]),patchEdge=P([1.85,.015,-.05]);
  const breadth=Math.abs(patchEdge[0]-patch[0]);
  ctx.save();ctx.translate(patch[0],patch[1]);ctx.scale(1,.40);
  const pool=ctx.createRadialGradient(0,0,.1,0,0,breadth*1.37);
  pool.addColorStop(0,gray(198,night?.12:.095));pool.addColorStop(.55,gray(166,.041));pool.addColorStop(1,gray(181,0));
  ctx.fillStyle=pool;ctx.fillRect(-breadth*1.4,-breadth*1.4,breadth*2.8,breadth*2.8);ctx.restore();
  const rand=randomGenerator(1908);
  for(let i=0;i<160;i++){
    const x=rand()*960,y=250+rand()*250;
    line(ctx,[[x,y],[x+rand()*2.4,y+.2]],gray(190,.02+rand()*.055),.65);
  }
}

function projection(ctx,P,t,mode,pulse) {
  if(mode===2)return;
  const gain=mode===1?.38:.62+.30*pulse;
  for(let i=0;i<33;i++) {
    const pts=[];
    for(let j=0;j<=64;j++){
      const x=-2.45+j*.092;
      const base=.35+i*.046;
      const y=base + .097*Math.sin(x*2.9+i*.29+t*.92) + .083*Math.cos(x*4.6-i*.19-t*.68)
        + .058*Math.sin(x*7.3+i*.44+t*.78) + .10*Math.sin(x*3.6+i*.46-t*.76)*Math.sin(.45*x+i*.2);
      pts.push(P([x,y,6.965]));
    }
    const value=.10+.15*(.5+.5*Math.sin(i*3.7));
    line(ctx,pts,gray(230,value*gain),i%4===0?1.7:.74);
  }
}

function person(ctx,P,x,z,height,turn,reach) {
  const foot=P([x,.012,z]),head=P([x,height,z]), h=foot[1]-head[1];if(h<=0)return;
  ctx.save();ctx.translate(foot[0],foot[1]);ctx.scale(h/160,h/160);
  const g=gradient(ctx,-12,-105,16,-99,[[0,'#1b1b1b'],[.66,'#282828'],[.96,'#424242'],[1,'#606060']]);
  ellipse(ctx,6,1,20,3,gray(8,.54));
  ctx.scale(turn,1);
  const draw=(d,fill,stroke,w)=>{const p=new Path2D(d);ctx.fillStyle=fill;ctx.fill(p);if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=w;ctx.stroke(p);}};
  draw('M-10 -74 Q-10 -52 -7 -34 L-11 -6 L-6 -4 L-2 -33 L4 -61 L1 -75Z','#181818',null);
  draw('M-7 -7 L-11 -5 Q-16 -5 -16 -2 L-3 -2 L-3 -6Z','#141414');
  draw('M-4 -78 L10 -80 Q14 -56 8 -35 L10 -7 L4 -5 L0 -34 L-4 -55Z',g,'#353535',.7);
  draw('M4 -7 L10 -8 L13 -4 L19 -3 Q20 -1 18 0 L3 -1Z','#1a1a1a');
  draw('M-6 -137 L3 -138 L5 -125 L13 -122 Q17 -108 12 -91 L13 -75 Q1 -70 -13 -75 L-14 -87 L-11 -118Z',g,'#505050',.65);
  draw('M-6 -137 Q-12 -143 -10 -151 Q-9 -161 0 -161 Q9 -162 10 -154 L10 -149 L13 -146 L10 -145 Q11 -138 5 -137 L3 -132Z','#292929','#626262',.68);
  draw('M-10 -149 Q-12 -159 -4 -162 Q4 -166 9 -158 L11 -153 L5 -154 L1 -151 L-4 -148 L-6 -141Z','#1a1a1a');
  const pose=reach?'M8 -120 Q15 -120 17 -111 L23 -98 L36 -95 L40 -91 L36 -89 L19 -92 Q14 -97 9 -105 L6 -112Z':
    'M8 -121 Q16 -119 16 -108 L17 -89 L20 -78 Q20 -74 17 -73 L14 -77 L10 -88 L7 -104Z';
  draw(pose,g,'#4a4a4a',.7);
  line(ctx,[[-9,-95],[-7,-86],[-8,-78]],gray(90,.46),.7);
  ctx.restore();
}

const water=.99, bottom=.56, top=1.13, left=-1.66,right=1.66, back=.73,front=-.73;

function tank(ctx,P,t,glow) {
  const project=(a,b,c,d,fill,stroke,w)=>worldPoly(ctx,P,[a,b,c,d],fill,stroke,w);
  // Slender exhibition plinth. The legs, their shadows and a rear witness
  // are drawn independently of the change in the visitor's viewpoint.
  worldPoly(ctx,P,[[-1.57,.01,-.57],[1.67,.01,-.57],[2.47,.01,.18],[-.76,.01,.29]],gray(0,.21));
  for(const [x,z] of [[left+.12,back-.1],[right-.12,back-.1],[left+.12,front+.1],[right-.12,front+.1]]){
    project([x-.031,0,z],[x+.031,0,z],[x+.031,bottom,z],[x-.031,bottom,z],'#272727','#858585',.55);
    worldLine(ctx,P,[[x-.03,.05,z],[x-.03,.53,z]],'#b3b3b3',.8);
  }
  project([left,bottom-.06,front],[right,bottom-.06,front],[right,bottom,front],[left,bottom,front],'#555555','#949494',.7);
  project([left,bottom-.06,back],[right,bottom-.06,back],[right,bottom,back],[left,bottom,back],'#333333','#878787',.6);
  project([left,bottom,back],[right,bottom,back],[right,top,back],[left,top,back],gray(166,.08),gray(202,.62),.9);
  project([left,bottom,front],[left,bottom,back],[left,top,back],[left,top,front],gray(216,.10),gray(206,.72),1);
  project([left,water,front],[right,water,front],[right,water,back],[left,water,back],
    gradient(ctx,300,200,620,340,[[0,gray(224,.35)],[.4,gray(161,.24)],[.7,gray(229,.43)],[1,gray(134,.32)]]),gray(238,.56),.75);
  const rand=randomGenerator(140);
  for(let i=0;i<76;i++){
    const x=mix(left+.05,right-.22,rand()), z=mix(front+.04,back-.04,rand());
    const span=.03+rand()*.17;
    worldLine(ctx,P,[[x,water+.001,z],[x+span/2,water+.003,z+Math.sin(t+i)*.012],[x+span,water+.001,z]],
      gray(224,.12+rand()*.22),.55);
  }
  const strip=[[left+.09,.99,front-.013],[left+.52,.99,front-.013],[left+.52,1.081,front-.013],[left+.09,1.081,front-.013]];
  worldPoly(ctx,P,strip,gray(112+Math.round(120*glow)),gray(238,.67),1);
}

function frontGlass(ctx,P){
  worldPoly(ctx,P,[[left,bottom,front],[right,bottom,front],[right,top,front],[left,top,front]],
    gradient(ctx,420,207,500,349,[[0,gray(204,.025)],[.7,gray(232,.055)],[1,gray(166,.15)]]),gray(203,.70),.9);
  for(const z of [back,front]){
    worldLine(ctx,P,[[left,top+.004,z],[right,top+.004,z]],gray(230,.82),1.25);
    worldLine(ctx,P,[[left,water,z],[right,water,z]],gray(224,.44),.7);
  }
  worldLine(ctx,P,[[right,top,front],[right,top,back],[right,bottom,back],[right,bottom,front]],gray(224,.70),1);
}

function wave(ctx,P,x,z,rad,alpha,t){
  for(let n=0;n<3;n++){
    const d=rad*(.45+.25*n), pts=[];
    for(let k=0;k<=44;k++){
      const a=k/44*TAU;
      const zz=z+Math.sin(a)*d*.59;const xx=x+Math.cos(a)*d;
      if(xx<left+.02||xx>right-.02||zz<front+.02||zz>back-.02){
        if(pts.length>1)line(ctx,pts,gray(230,alpha*(1-n*.20)),.76);
        pts.length=0;continue;
      }
      pts.push(P([xx,water+.003,zz+Math.sin(2*a+t)*.006]));
    }
    if(pts.length>1)line(ctx,pts,gray(230,alpha*(1-n*.20)),.76);
  }
}

function specimen(ctx,P,x,z,size,isParent,phase,heading=0) {
  const c=P([x,water+.038,z]), edge=P([x+size,water+.038,z]);const rx=Math.abs(edge[0]-c[0]);
  if(rx<1)return;
  const ry=rx*(isParent?.49:.65);ctx.save();ctx.translate(c[0],c[1]);
  ctx.rotate((edge[1]-c[1])/Math.max(1,rx)*.50+heading);
  ellipse(ctx,3,ry*.52,rx*1.07,ry*.48,gray(12,.32));
  const shell=gradient(ctx,-rx*.65,-ry,rx*.36,ry,[[0,'#e9e9e9'],[.19,'#c5c5c5'],[.36,'#929292'],[.59,'#777777'],[.74,'#4c4c4c'],[1,'#303030']]);
  ctx.beginPath();
  if(isParent){
    ctx.moveTo(-rx,ry*.02);ctx.bezierCurveTo(-rx*.38,-ry*.85,rx*.09,-ry*1.32,rx*.61,-ry*.72);
    ctx.bezierCurveTo(rx*1.25,-ry*.08,rx*1.08,ry*.83,rx*.52,ry*.91);ctx.bezierCurveTo(0,ry*1.16,-rx*.6,ry*.58,-rx,ry*.02);
    ctx.closePath();ctx.fillStyle=shell;ctx.fill();ctx.strokeStyle=gray(236,.79);ctx.lineWidth=.85;ctx.stroke();
    ctx.beginPath();ctx.ellipse(rx*.68,-ry*.10,rx*.16,ry*.68,-.25,Math.PI*1.37,Math.PI*2.45);ctx.strokeStyle='#525252';ctx.lineWidth=1;ctx.stroke();
  }else{
    ellipse(ctx,0,0,rx,ry,shell,gray(227,.72),.8);
    for(let i=-2;i<=2;i++){
      const xx=i*rx*.31,hh=ry*Math.sqrt(1-(xx/rx)**2);
      ctx.beginPath();ctx.moveTo(xx-1,-hh*.87);ctx.quadraticCurveTo(xx+rx*.22+Math.sin(phase)*.45,-hh*.03,xx,hh*.86);
      ctx.strokeStyle=gray(44,.59);ctx.lineWidth=Math.max(.8,rx*.077);ctx.stroke();
    }
  }ctx.restore();
}

function bottle(ctx,P,stock,lit) {
  const x=2.0,z=.05;
  worldPoly(ctx,P,[[x-.26,.31,z-.23],[x+.26,.31,z-.23],[x+.26,.31,z+.23],[x-.26,.31,z+.23]],'#363636','#6e6e6e',.85);
  for(const dx of [-.21,.21])worldLine(ctx,P,[[x+dx,.02,z-.13],[x+dx,.31,z-.13]],'#929292',1.4);
  const base=P([x,.32,z]), cap=P([x,.89,z]);const hh=base[1]-cap[1], ww=hh*.28;
  ctx.save();ctx.translate(base[0],base[1]);
  const d=`M${-ww*.72} 0 Q${-ww} -1 ${-ww} ${-hh*.11} L${-ww} ${-hh*.72} Q${-ww*.93} ${-hh*.81} ${-ww*.4} ${-hh*.87} L${-ww*.4} ${-hh*.96} L${ww*.4} ${-hh*.96} L${ww*.4} ${-hh*.87} Q${ww*.96} ${-hh*.81} ${ww} ${-hh*.72} L${ww} ${-hh*.10} Q${ww} 0 ${ww*.7} 0Z`;
  const jar=new Path2D(d);ctx.fillStyle='#393939';ctx.fill(jar);
  ctx.save();ctx.clip(jar);const fluid=hh*(.018+.665*stock/2);
  ctx.fillStyle=gradient(ctx,-ww,0,ww,0,[[0,'#686868'],[.25,'#b5b5b5'],[.75,'#939393'],[1,'#636363']]);
  ctx.fillRect(-ww,-fluid,2*ww,fluid);line(ctx,[[-ww,-fluid],[ww,-fluid]],'#e2e2e2',1);
  ctx.restore();ctx.strokeStyle=lit?'#e1e1e1':'#9d9d9d';ctx.lineWidth=1;ctx.stroke(jar);
  ctx.fillStyle='#bdbdbd';ctx.fillRect(-ww*.52,-hh,ww*1.04,hh*.06);
  for(let i=1;i<=2;i++){const y=-hh*(.018+.665*i/2);line(ctx,[[-ww*.82,y],[-ww*.36,y]],'#dcdcdc',.85);}
  ctx.restore();
  const start=P([x,.90,z]),end=P([right-.04,top,0]);
  ctx.beginPath();ctx.moveTo(...start.slice(0,2));ctx.bezierCurveTo(start[0]-4,start[1]-23,end[0]+19,end[1]-16,end[0],end[1]);ctx.strokeStyle='#b4b4b4';ctx.lineWidth=1.5;ctx.stroke();
}

export function mountRoom(container,{direction='witness'}={}) {
  const doc=container.ownerDocument;
  container.classList.add('rehearsal');
  container.innerHTML=`<div class="room-selection" role="group" aria-label="Choose a rehearsal"></div>
    <div class="room-stage"><canvas role="img" aria-label="A modeled gallery with a waist-high water tank and two visitors"></canvas></div>
    <div class="room-console"><div class="room-choices"><p class="room-prompt"></p><div class="room-actions" role="group" aria-label="Rehearsal actions"></div></div>
    <div class="room-readout"><p class="room-result" role="status" aria-live="polite" aria-atomic="true"></p><button type="button" class="room-reset">Restart this rehearsal</button></div></div>`;
  const select=container.querySelector('.room-selection'), controls=container.querySelector('.room-actions');
  const result=container.querySelector('.room-result'),prompt=container.querySelector('.room-prompt');
  const canvas=container.querySelector('canvas'),ctx=canvas.getContext('2d',{alpha:false});
  let mode=0,choice=-1,portion=2,prevPortion=2,cycles=0,releases=0,outcome='idle',initialMode=true;
  let lastBody=false,prediction=-1,judged=false;
  let active=true,disposed=false,raf=0,elapsed=0,previous=0,clock=0,run=0;
  let cameraStart=[-2.62,1.59,-4.27],eyeNow=[...cameraStart], startAim=[.03,.95,.18],aimNow=[...startAim],startFov=43,fovNow=43;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const modeButtons=STUDIES.map((study,index)=>{
    const button=doc.createElement('button');button.type='button';button.textContent=study.name;
    button.addEventListener('click',()=>{if(index!==mode)reset(index);});select.append(button);return button;
  });
  function focusFor(){
    if(mode===0 && choice===0)return {eye:[-2.18,1.63,-2.44],aim:[-.78,1.0,-.28],fov:42};
    if(mode===0 && choice===1)return {eye:[2.76,1.60,-2.60],aim:[.39,1.04,.06],fov:39};
    if(mode===1)return {eye:[-.79,2.65,-3.93],aim:[.06,.86,.04],fov:39};
    if(mode===2)return {eye:[2.94,1.59,-3.37],aim:[.74,.83,-.02],fov:41};
    return {eye:[-2.62,1.59,-4.27],aim:[.03,.95,.18],fov:43};
  }
  function render(){
    if(disposed||!ctx||!canvas.width||!canvas.height)return;
    const target=focusFor(),cameraMix=smooth(0,.90,elapsed);
    eyeNow=blend(cameraStart,target.eye,cameraMix);aimNow=blend(startAim,target.aim,cameraMix);fovNow=mix(startFov,target.fov,cameraMix);
    const width=canvas.width,height=canvas.height;
    const aspect=width/height;
    const viewHeight=500,viewWidth=viewHeight*aspect;
    const P=camera(eyeNow,aimNow,fovNow*(aspect<1.55?1.17:1),viewWidth,viewHeight);
    const scale=height/viewHeight;
    ctx.setTransform(scale,0,0,scale,0,0);ctx.clearRect(0,0,viewWidth,viewHeight);
    roomShell(ctx,P,mode);
    const phase=elapsed;
    const pulse=mode===0 && choice===0&&!judged?Math.max(0,1-(phase%1.05)*5)**2:0;
    projection(ctx,P,clock,mode,pulse);
    if(mode===2){
      if(outcome==='refill')person(ctx,P,2.32,.86,1.68,-1,true);
    } else {
      person(ctx,P,1.92,1.57,1.68,-1,false);
      if(mode===1)person(ctx,P,-2.26,.10,1.75,1,false);
    }
    tank(ctx,P,clock,pulse);
    const gate=(mode===0?choice>=0:mode===2&&outcome==='birth');
    const part=gate?smooth(.28,mode===0?2.86:1.74,phase):mode===1?1:0;
    const parentX=-.49, parentZ=.02, kidX=mode===1?.16:.03+.62*part;
    const childTurn=mode===1&&prediction>=0?smooth(.2,1.30,phase):0;
    const neighborTurn=mode===1&&prediction>=0?smooth(.93,2.30,phase):0;
    const kidZ=mode===1?-.13-.19*childTurn:.02-.13*part;
    if(mode===0||mode===2){wave(ctx,P,parentX,.04,.42+.15*pulse,.29+.24*pulse,clock);}
    if(mode===0&&choice===0&&!judged){
      const rings=(phase%1.05)/1.05;
      wave(ctx,P,-1.36,-.58,.12+.59*rings,.54*(1-rings),clock);
    }
    specimen(ctx,P,parentX,parentZ,.48,true,clock);
    if(part>.15||mode===1) {
      specimen(ctx,P,kidX,kidZ,.135,false,clock,-.64*childTurn);
      wave(ctx,P,kidX,kidZ,.20+.13*part,.57,clock);
    }
    if(mode===0&&choice>=0&&elapsed<2.86){
      const tip=P([kidX-.045,water+.080,kidZ]),base=P([-.18,water+.16,parentZ]);
      ctx.beginPath();ctx.moveTo(base[0],base[1]);ctx.quadraticCurveTo(mix(base[0],tip[0],.65),Math.min(base[1],tip[1])-6,tip[0],tip[1]);
      ctx.strokeStyle=gray(224,.89);ctx.lineWidth=1.6;ctx.stroke();
    }
    if(mode===2&&lastBody&&outcome!=='birth'){
      ctx.save();ctx.globalAlpha=.36;specimen(ctx,P,.72,-.11,.135,false,0);ctx.restore();
      wave(ctx,P,.72,-.11,.37,.24,0);
    }
    if(mode===1) {
      const target=choice===0?[.62,.07]:[1.32,.42];
      const k=prediction>=0?1:choice>=0?smooth(.12,1.75,phase):0;
      const x=mix(1.26,target[0],k),z=mix(.41,target[1],k)-.22*neighborTurn;
      specimen(ctx,P,x,z,.19,false,clock*.82,-.64*neighborTurn);
      const waveRadius=choice===0?.24+.25*k:.23;
      wave(ctx,P,x,z,waveRadius,.66,clock+.7);
      if(choice===0&&k>.38){
        // Interference moves across the narrow region where the two wakes meet.
        for(let j=0;j<4;j++){
          const x0=.26+j*.066;
          worldLine(ctx,P,[[x0,water+.008,-.22],[x0+.032,water+.008,-.07],[x0-.010,water+.008,.06]],gray(234,.42*k),.95);
        }
      }
    }
    frontGlass(ctx,P);bottle(ctx,P,mix(prevPortion,portion,smooth(.13,1.3,phase)),mode===2);
    if(mode===2){
      // The keeper supplies the prefabricated electronic cores as well as the
      // fluid shown by the meniscus: inventory is staged in paired portions.
      for(let i=0;i<portion;i++){
        const a=P([1.87+.16*i,.34,-.23]),b=P([1.98+.16*i,.36,-.20]);
        const sz=Math.max(4,Math.abs(b[0]-a[0]));
        ctx.fillStyle='#888';ctx.fillRect(a[0]-3,a[1]-sz*.36,sz,sz*.52);
        line(ctx,[[a[0]-3,a[1]-sz*.38],[a[0]+sz-2,a[1]-sz*.38]],'#dedede',.9);
      }
    }
    if(mode===0&&choice!==0)person(ctx,P,-1.93,-.98,1.72,1,true);
    if(mode===2&&outcome==='empty')wave(ctx,P,-1.45,-.57,.31,.33,0);
    // A broad falloff gives the far side of the room depth without hiding the work.
    const v=ctx.createRadialGradient(viewWidth*.49,viewHeight*.49,viewHeight*.39,viewWidth*.49,viewHeight*.49,viewWidth*.72);
    v.addColorStop(0,'transparent');v.addColorStop(1,gray(0,.47));ctx.fillStyle=v;ctx.fillRect(0,0,viewWidth,viewHeight);
  }
  function cancel(){if(raf)cancelAnimationFrame(raf);raf=0;previous=0;}
  function tick(now){
    raf=0;if(!active||disposed)return;
    const dt=previous?Math.min(.065,(now-previous)/1000):0;previous=now;
    elapsed=Math.min(run,elapsed+dt);clock+=dt;render();
    if(elapsed<run)raf=requestAnimationFrame(tick);else previous=0;
  }
  function startMotion(duration) {
    cancel();cameraStart=[...eyeNow];startAim=[...aimNow];startFov=fovNow;
    run=duration;elapsed=reduced.matches?(mode===0&&choice===0?.9:run):0;
    render();if(active&&!reduced.matches)raf=requestAnimationFrame(tick);
  }
  function describe(message){
    result.textContent=message;
    canvas.setAttribute('aria-label',STUDIES[mode].name+'. '+message);
  }
  function buttonFor(label,handle){
    const b=doc.createElement('button');b.type='button';b.textContent=label;
    b.addEventListener('click',handle);controls.append(b);return b;
  }
  function showChoices(){
    controls.replaceChildren();prompt.textContent=STUDIES[mode].prompt;
    STUDIES[mode].actions.forEach((label,i)=>{
      const b=buttonFor(label,()=>act(i));
      if(mode!==2)b.setAttribute('aria-pressed',String(i===choice));
    });
  }
  function offerLaterStill(){
    if(!reduced.matches||mode!==0||choice!==0||judged||controls.children.length>1)return;
    const advance=buttonFor('View the next still',()=>{
      elapsed=3.34;clock=3.34;
      describe('A later still. The parent and child occupy different positions in the tank. Decide whether support has ended.');
      advance.remove();controls.firstElementChild.focus({preventScroll:true});render();
    });
  }
  function act(index) {
    choice=index;initialMode=false;prevPortion=portion;judged=false;prediction=-1;
    [...controls.children].forEach((b,i)=>{if(mode!==2)b.setAttribute('aria-pressed',String(i===index));});
    if(mode===0) {
      if(index===0){
        describe('You are touching the strip. Short waves cross the tank. The parent is still carrying the child.');
        prompt.textContent='Lift your finger when you think the child is swimming alone.';
        controls.replaceChildren();
        const lift=buttonFor('Lift my finger',()=>{
          if(judged)return;judged=true;
          const supported=elapsed<2.86;
          describe(supported?'You lifted while the connector still supported the child. The child had begun to travel before the arm withdrew.':
            'You lifted after the connector withdrew. A strip of water now separates the child from its parent.');
          showChoices();controls.firstElementChild.focus({preventScroll:true});render();
        });
        lift.focus({preventScroll:true});
        offerLaterStill();
      }else{
        describe('From across the tank, watch the thin connector above the child. A strip of water opens only after the parent lets go.');
      }
    } else if(mode===1) {
      if(index===0){
        describe('A neighbor moves alongside the child. Both wakes are visible as the child starts a small turn.');
        controls.replaceChildren();prompt.textContent='Which body will carry the turn across the water?';
        ['The child alone','The neighbor too'].forEach((label,i)=>buttonFor(label,()=>{
          prediction=i;initialMode=false;
          describe(i===1?'You anticipated the second turn. The child turns first. A moment later the neighbor turns, and the two wakes cross.':
            'Watch the far body. After the child turns, its neighbor takes up the same turn. The wakes cross between them.');
          showChoices();controls.firstElementChild.focus({preventScroll:true});startMotion(2.75);
        }));
        controls.firstElementChild.focus({preventScroll:true});
      }else describe('The neighbor holds near the far wall. Two separate wakes fade, leaving still water between the bodies.');
    } else {
      cycles++;
      if(index===1){portion=2;outcome='refill';
        describe(prevPortion===2?
          `Cycle ${cycles}. The keeper checks a full reservoir and two motor cores. The service cycle adds no stock. Stock remains 2 of 2. Releases so far: ${releases}.`:
          `Cycle ${cycles}. A keeper replenishes silicone and supplies assembled motor cores. That takes the full cycle. Stock is now 2 of 2. Releases so far: ${releases}.`);
      }else if(portion>0){portion--;releases++;outcome='birth';
        lastBody=true;
        describe(`Cycle ${cycles}. One child leaves the stern. ${portion} of 2 portions remain. Releases so far: ${releases}.`);
      }else{outcome='empty';
        describe(`Cycle ${cycles}. A pulse arrives at the empty tank. Stock is 0 of 2. No child emerges. Releases so far: ${releases}.`);
      }
    }
    startMotion(mode===0?4.75:2.45);
  }
  function reset(index){
    cancel();mode=index;choice=-1;portion=prevPortion=2;cycles=releases=0;outcome='idle';clock=0;initialMode=true;lastBody=false;prediction=-1;judged=false;
    modeButtons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===mode)));
    showChoices();
    describe(initialNotice[index]);const pose=focusFor();
    cameraStart=eyeNow=[...pose.eye];startAim=aimNow=[...pose.aim];startFov=fovNow=pose.fov;elapsed=run=2.45;render();
  }
  function size(){
    const rect=canvas.getBoundingClientRect();if(rect.width<1||rect.height<1)return;
    const device=Math.min(1.5,window.devicePixelRatio||1);
    const w=Math.round(rect.width*device),h=Math.round(rect.height*device);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}render();
  }
  function motionPref(){
    if(reduced.matches){cancel();elapsed=mode===0&&choice===0&&!judged?.9:run;offerLaterStill();render();}
    else if(mode===0&&choice===0&&!judged){controls.querySelector('button:nth-child(2)')?.remove();if(active&&elapsed<run){cancel();raf=requestAnimationFrame(tick);}}
  }
  container.querySelector('.room-reset').addEventListener('click',()=>reset(mode));
  const observer=new ResizeObserver(size);observer.observe(canvas);
  reduced.addEventListener('change',motionPref);
  reset(Math.max(0,directions.indexOf(direction)));size();
  return {
    setActive(value){active=Boolean(value);cancel();if(active&&elapsed<run&&!initialMode&&!reduced.matches)raf=requestAnimationFrame(tick);},
    getDirection(){return directions[mode];},
    seek(seconds){cancel();elapsed=clamp(seconds,0,run);clock=elapsed;render();},
    destroy(){disposed=true;cancel();observer.disconnect();reduced.removeEventListener('change',motionPref);container.replaceChildren();container.classList.remove('rehearsal');}
  };
}

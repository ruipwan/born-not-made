/* Diagrams for the inheritance page. Each canvas loops on its own and only runs while on screen.
   Shapes follow the lineage diagram: head = gel, brain and parts in a double wall; tail = the arm, the part that reproduces. */
(function(){
const DOCK=.032, HK=1.3, TK=.62;
const COL=[[232,163,61],[63,193,171],[156,136,242],[239,111,134]];
const col=(o,a)=>'rgba('+COL[o].join(',')+','+Math.min(1,Math.max(0,a))+')';
const ink=a=>'rgba(236,235,230,'+Math.min(1,Math.max(0,a))+')';
const clamp=x=>Math.min(1,Math.max(0,x)), lerp=(a,b,u)=>a+(b-a)*u;
const ease=(t,a,b)=>{const x=clamp((t-a)/(b-a));return x*x*(3-2*x)};
const mono='ui-monospace, "JetBrains Mono", Menlo, monospace';
function text(c,s,x,y,size,a,font,align,track){c.save();c.textAlign=align||'left';c.fillStyle=ink(a);c.font=size+'px '+(font||'Arial');if(track&&'letterSpacing' in c)c.letterSpacing=track+'px';c.fillText(s,x,y);c.restore()}
function wrap(c,s,x,y,w,size,a,lh){c.save();c.font=size+'px Arial';const words=s.split(' ');let line='',yy=y;for(const wd of words){const t=line?line+' '+wd:wd;if(c.measureText(t).width>w&&line){text(c,line,x,yy,size,a);line=wd;yy+=lh}else line=t}text(c,line,x,yy,size,a);c.restore();return yy}
function rng(seed){return()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

// head: X0 = back face, Yb = floor, s = px per meter; o: l,h,crown,mx,mz,flip
function headMap(X0,Yb,s,o){const l=o.l||1,h=o.h||1,mx=o.mx||1,mz=o.mz||1,cr=o.crown||0,f=o.flip?-1:1;
  return (x,z)=>[X0+f*(x-DOCK)*HK*l*s*mx, Yb-(z*h+cr*Math.sin(Math.PI*clamp((x-DOCK)/.3))*(z>.2?1:0))*s*mz]}
function headPath(m){const P=new Path2D();
  P.moveTo(...m(DOCK,.06));P.lineTo(...m(DOCK,.29));
  P.bezierCurveTo(...m(DOCK,.345),...m(.06,.36),...m(.12,.36));
  P.bezierCurveTo(...m(.19,.36),...m(.25,.345),...m(.295,.325));
  P.bezierCurveTo(...m(.335,.30),...m(.37,.22),...m(.36,.15));
  P.bezierCurveTo(...m(.345,.075),...m(.27,0),...m(.16,0));
  P.lineTo(...m(.09,0));P.bezierCurveTo(...m(.05,0),...m(DOCK,.015),...m(DOCK,.06));P.closePath();return P}
function mouth(c,m,a){const [ax,ay]=m(.295,.325),[bx,by]=m(.36,.15),L=Math.hypot(bx-ax,by-ay)/2,w=Math.abs(m(.33,0)[0]-m(.3,0)[0]);
  c.strokeStyle=ink(.55*a);c.lineWidth=1;c.beginPath();c.ellipse((ax+bx)/2-w*.1,(ay+by)/2,L*.98,Math.max(2,w*.9),Math.atan2(by-ay,bx-ax),0,7);c.stroke()}
function drawHead(c,m,a,fill){const P=headPath(m);c.fillStyle=ink((fill??.05)*a);c.fill(P);c.strokeStyle=ink(.8*a);c.lineWidth=1.4;c.stroke(P);mouth(c,m,a);return P}
function tailMap(Xd,Yb,s,flip){const f=flip?-1:1;return (x,z)=>[Xd+f*(x-DOCK)*TK*s,Yb-z*s]}
function tailPath(t){const P=new Path2D();
  P.moveTo(...t(DOCK,.33));P.lineTo(...t(-.12,.33));
  P.bezierCurveTo(...t(-.27,.33),...t(-.42,.25),...t(-.44,.14));
  P.bezierCurveTo(...t(-.455,.05),...t(-.40,0),...t(-.32,0));
  P.lineTo(...t(DOCK,0));P.closePath();return P}
function drawTail(c,t,a){const P=tailPath(t);c.fillStyle=ink(.035*a);c.fill(P);c.strokeStyle=ink(.6*a);c.lineWidth=1.3;c.stroke(P);return P}
// two link arm from the tail's base; elbow kept under the roof
function arm(c,t,s,tip,a,segs){
  const B=t(-.115,.2),F=t(-.115,.005),L=.33*s;let [dx,dy]=[tip[0]-B[0],tip[1]-B[1]],d=Math.hypot(dx,dy);
  if(d>2*L-1){tip=[B[0]+dx/d*(2*L-1),B[1]+dy/d*(2*L-1)];dx=tip[0]-B[0];dy=tip[1]-B[1];d=2*L-1}
  const an=Math.atan2(dy,dx),b=Math.acos(clamp(d/(2*L))),up=dx>=0?-1:1;
  let E=[B[0]+L*Math.cos(an+up*b),B[1]+L*Math.sin(an+up*b)];E[1]=Math.max(E[1],t(0,.31)[1]);
  const pts=[F,B,E,tip],n=segs??3;
  c.strokeStyle=ink(.75*a);c.lineWidth=2;c.beginPath();c.moveTo(...pts[0]);for(let i=1;i<=n;i++)c.lineTo(...pts[i]);c.stroke();
  if(n>=3){c.fillStyle=ink(.9*a);c.beginPath();c.arc(tip[0],tip[1],2.6,0,7);c.fill()}
  return {B,E,tip};
}
// points inside a head, in head coordinates
function spots(seed,n){const R=rng(seed),o=[];for(let i=0;i<n;i++){const x=.06+R()*.24,lo=x<.19?.03:.03+.15*Math.pow((x-.19)/.11,1.3),hi=.32-.06*Math.pow((x-.05)/.25,2);o.push([x,lo+R()*(hi-lo)])}return o}

/* Each canvas plays on its own. Earlier this froze on one still frame when the system asked for reduced motion
   (macOS "Reduce motion"), which made the diagrams look like pictures. Now every canvas always plays, and has
   the same speed for everyone. Time advances only while the canvas is on screen; if no IntersectionObserver report ever
   arrives (some nested frames), it plays anyway. Returns a small control: play(), pause(), seek(t), playing, t. */
function loop(canvas,W,H,dur,draw){
  const c=canvas.getContext('2d');let t=0,last=performance.now(),vis=true,run=true;
  const rate=1, fix=new URLSearchParams(location.search).get('dt');if(fix!==null){t=+fix;run=false}
  if('IntersectionObserver' in window)new IntersectionObserver(e=>{vis=e[e.length-1].isIntersecting;last=performance.now()}).observe(canvas);
  function size(){const r=Math.min(2,devicePixelRatio||1),w=Math.round(canvas.clientWidth*r);if(w&&canvas.width!==w){canvas.width=w;canvas.height=Math.round(w*H/W)}}
  const api={get t(){return t},get playing(){return run},dur,onframe:null,
    play(){run=true;last=performance.now()},pause(){run=false},seek(v){t=Math.min(dur-1e-3,Math.max(0,+v||0))}};
  function tick(now){size();
    if(vis&&run&&!document.hidden){t=(t+Math.min(.1,Math.max(0,(now-last)/1000))*rate)%dur}
    last=now;
    if(vis){c.setTransform(canvas.width/W,0,0,canvas.height/H,0,0);c.fillStyle='#000';c.fillRect(0,0,W,H);const d=draw(c,t);if(d&&canvas.getAttribute('aria-label')!==d)canvas.setAttribute('aria-label',d);if(api.onframe)api.onframe(t)}
    requestAnimationFrame(tick)}
  requestAnimationFrame(tick);return api;
}

/* 1 · Copy, update, "birth" */
(function(){
  const cv=document.getElementById('d-why');if(!cv)return;
  const W=1600,H=780,S=300,X=300,DX=200,DUR=15;
  const SP=spots(7,16), rows=[150,390,630];
  const SHAPES=[{l:1,h:1,crown:0},{l:1.1,h:.9,crown:.026},{l:.9,h:1.08,crown:-.02},{l:1.05,h:.95,crown:.032}];
  function dots(c,m,o,n,a,from){for(let i=0;i<n&&i<SP.length;i++){const [x,y]=m(...SP[i]);c.fillStyle=col(o,a);c.beginPath();c.arc(x,y,2.4,0,7);c.fill()}}
  function rings(c,m,cols,a){cols.forEach((o,i)=>{const [x,y]=m(...SP[(i*5+3)%SP.length]);c.strokeStyle=col(o,a);c.lineWidth=1.6;c.beginPath();c.arc(x,y,5.5,0,7);c.stroke();c.fillStyle=col(o,a);c.beginPath();c.arc(x,y,2,0,7);c.fill()})}
  loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);
    // labels
    [['Copy','More of the same. Every copy is the first one again.'],
     ['Update','The new version replaces the old. Only one is left.'],
     ['“Birth”','Both stay. The newborn is formed inside, inherits part of what the older one knows, learns the rest, and differs in body.']]
    .forEach(([h,d],i)=>{text(c,h,64,rows[i]-40,30,.95,'Georgia');wrap(c,d,64,rows[i]-8,190,13.5,.6,19)});
    c.strokeStyle=ink(.08);c.lineWidth=1;[270,510].forEach(y=>{c.beginPath();c.moveTo(64,y);c.lineTo(W-64,y);c.stroke()});
    // copy: identical bodies, identical memory
    for(let i=0;i<6;i++){const ti=i*1.8;if(t<ti)continue;const a=ease(t,ti,ti+.5)*fade,Yb=rows[0]+70,m=headMap(X+i*DX-(1-a)*30,Yb,S,{});drawHead(c,m,a);dots(c,m,0,16,.9*a)}
    // update: one place, the version changes, the old one is gone
    {const v=Math.min(3,Math.floor(t/3.5)),f=ease(t,v*3.5,v*3.5+.6),Yb=rows[1]+70;
     if(v>0&&f<1){const m=headMap(X,Yb,S,{});c.globalAlpha=1-f;drawHead(c,m,1);dots(c,m,v-1,16,.9);c.globalAlpha=1}
     const m=headMap(X,Yb,S,{});c.globalAlpha=(v?f:1)*fade;drawHead(c,m,1);dots(c,m,v,16,.9);text(c,'v'+(v+1),X+70,Yb+30,14,.8,mono,'center');c.globalAlpha=1;
     for(let k=0;k<v;k++){text(c,'v'+(k+1),X+DX+k*60,Yb-50,13,.3,mono);c.strokeStyle=ink(.3);c.beginPath();c.moveTo(X+DX+k*60-2,Yb-54);c.lineTo(X+DX+k*60+20,Yb-54);c.stroke()}
     if(v)text(c,'gone',X+DX,Yb-28,11,.3,mono,'left',1.2)}
    // birth: each one from the one before, each different; colors are where its memory came from
    {const Yb=rows[2]+70;const comp=[[0],[0,0,0],[0,1,1],[0,1,2,2]];
     for(let k=0;k<4;k++){
       const tb=k?k*3.2-1.4:-9, a=k?ease(t,tb,tb+1.4):1;if(t<tb)continue;
       const sh=SHAPES[k], par=k?headMap(X+(k-1)*DX,Yb,S,SHAPES[k-1]):null;
       let X0=X+k*DX,Y=Yb,mx=1,mz=1;
       if(k&&a<1){const [px]=par(.2,0),[ex]=par(.42,0);X0=lerp(px-20,X+k*DX,a);mx=lerp(.45,1,a);mz=lerp(.3,1,a);Y=Yb-30*Math.sin(Math.PI*a)}
       const m=headMap(X0,Y,S,{...sh,mx,mz});c.globalAlpha=fade;drawHead(c,m,1);
       const own=Math.min(16,Math.floor(Math.max(0,t-tb-1.4)*3)+(k?0:16));
       if(k)rings(c,m,comp[k],.95*a);
       for(let i=0;i<own;i++){const [x,y]=m(...SP[(i*7+k*3)%SP.length]);c.fillStyle=col(k,.9);c.beginPath();c.arc(x+(k%2?3:-3),y+(k>1?4:0),2.4,0,7);c.fill()}
       text(c,['I','II','III','IV'][k],X0+70,Yb+30,18,.85*a,'Georgia','center');c.globalAlpha=1;
     }}
    return 'Copy makes more of the same. Update replaces the old. Birth keeps both, and the newborn differs.';
  });
})();

/* 2 · Head and tail: a still from the quilted head simulator (simulator/doublewall, print stage), every part labelled.
   Names and figures come from simulator/doublewall/quilt.json (kit, equip, masses), which keeps the first hand source of each. */
(function(){
  const cv=document.getElementById('d-body');if(!cv)return;
  const W=1600,H=900,DUR=16,IX=262,IY=205,IS=1080/1908;
  const img=new Image();img.src='body-section.jpg?v=6';
  const P=(x,y)=>[IX+x*IS,IY+y*IS], IW=1908*IS, IH=838*IS;
  // [anchor in the image, side, label x or y, title, line]
  const LB=[
    [[445,262],'left',95,'Air pump','A cordless tire inflator, 75 x 60 x 32 mm. Fills the cells of the newborn at birth.'],
    [[330,365],'left',215,'Brain and battery','Raspberry Pi 5, 85 x 56 mm. Nine 18650 cells, 10.8 V, 113 Wh.'],
    [[175,490],'left',350,'Piston stepper','A small stepper and screw drive both pistons of the store.'],
    [[300,470],'left',475,'Silicone store','Two printed cartridges, part A and part B, 370 mL each, mixed at the needle.'],
    [[445,500],'left',615,'Gel pump','Peristaltic, up to 100 mL a minute, with a 90 mL gel reservoir for top ups.'],
    [[860,230],'top',560,'Arm','Rotrics DexArm, four axes. Its mainboard holds the motor drivers for the arm and the piston stepper.'],
    [[1380,120],'top',900,'Quilted double wall','Two skins of Dragon Skin 30, 1.2 mm, webs of 0.8 mm, air in the cells.'],
    [[1760,300],'right',95,'Mouth','The newborn leaves here, inflating on the way.'],
    [[1500,700],'right',260,'Gel','A shallow layer in the lower head, 5.2 kg.'],
    [[1330,650],'right',400,'The next body','Printed folded flat in 18 layers, 143 x 194 x 79 mm; its pod adds about 23 mm.'],
    [[920,470],'bottom',300,'Tools','In saddles on the tail wall: a magnet holder that picks up parts, and the printing needle.'],
    [[680,600],'bottom',560,'Steel plate','Under the arm base. With the relay steel, 1.9 kg that keeps the tail upright.'],
    [[985,420],'bottom',820,'Docks from behind','Gel face to gel face. The tail moves on to the next head.']];
  const LW=200;
  loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);
    if(img.complete&&img.naturalWidth){c.drawImage(img,IX,IY,IW,IH);
      const E=60,edges=[[IX,0,IX+E,0,IX,IY,E,IH],[IX+IW,0,IX+IW-E,0,IX+IW-E,IY,E,IH],[0,IY,0,IY+E,IX,IY,IW,E],[0,IY+IH,0,IY+IH-E,IX,IY+IH-E,IW,E]];
      for(const [x0,y0,x1,y1,rx,ry,rw,rh] of edges){const gr=c.createLinearGradient(x0,y0,x1,y1);gr.addColorStop(0,'#000');gr.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=gr;c.fillRect(rx,ry,rw,rh)}}
    LB.forEach(([an,side,q,h,body],i)=>{
      const a=ease(t,.4+i*.55,.9+i*.55)*fade;if(a<=0)return;
      const [ax,ay]=P(...an);let tx,ty,pts;
      if(side==='left'){tx=24;ty=q;pts=[[ax,ay],[IX-14,ty+6],[tx+LW+8,ty+6]]}
      else if(side==='right'){tx=W-24-LW;ty=q;pts=[[ax,ay],[IX+IW+14,ty+6],[tx-8,ty+6]]}
      else if(side==='top'){tx=q;ty=40;pts=[[ax,ay],[ax,ty+66],[tx,ty+66]]}
      else {tx=q;ty=IY+IH+42;pts=[[ax,ay],[ax,ty-20],[tx,ty-20]]}
      c.save();c.globalAlpha=a;
      c.strokeStyle=ink(.4);c.lineWidth=1;c.beginPath();c.moveTo(...pts[0]);for(const p of pts.slice(1))c.lineTo(...p);c.stroke();
      c.fillStyle=ink(.95);c.beginPath();c.arc(ax,ay,3.2,0,7);c.fill();c.strokeStyle='#000';c.lineWidth=1.5;c.stroke();
      text(c,h,tx,ty,15,.95);wrap(c,body,tx,ty+19,side==='bottom'?240:(side==='top'?320:LW),12,.6,16);
      c.restore();
    });
    return 'A still of the quilted head simulator with every part named: in the tail the air pump, a Raspberry Pi 5 and its battery, the silicone store and its piston stepper, the gel pump, the arm with its motor drivers, the tools and the steel plate; in the head the quilted double wall, the gel, the next body and the mouth.';
  });
})();

/* 3 · How a part gets into the wall. First the kit is composed on one plate (top view, 3.5 px to the mm), then the plate is potted into one pod,
   then the pod goes into the wall (side section, 2.8 px to the mm; skins and beads drawn about twice their thickness so they read).
   Parts and numbers: Raspberry Pi 5 mechanical drawing and documentation (raspberrypi.com), TI DRV8833 datasheet SLVSAR1E,
   Pololu S13V30F5 product page, the AITIAO 3 to 4.5 V pump as recorded in build/data/components.json (no maker sheet exists),
   the 18650 cell as in simulator/doublewall/quilt.json. Sensor breakout sizes are assumed. */
(function(){
  const cv=document.getElementById('d-wall');if(!cv)return;
  const W=1600,H=860,TC=34,DUR=TC+36;
  /* ---------- the plate, top view, mm ---------- */
  const K=3.5,OX=470,OY=196, P=(x,y)=>[OX+x*K,OY+y*K];
  const PL={w:152,h:84};
  const PART={
    pumpA:{x:0,y:3,w:42.6,h:23.9}, pumpB:{x:0,y:30,w:42.6,h:23.9},
    drv:{x:47,y:4,w:14,h:12}, pi:{x:64,y:0,w:85,h:56},
    cell:{x:0,y:62,w:65.25,h:18.75}, reg:{x:69,y:60,w:22.9,h:22.9},
    imu:{x:96,y:60,w:20,h:18}, mic:{x:119,y:60,w:14,h:14}, amp:{x:136,y:60,w:14,h:14},
    ghost:{x:158,y:60,w:20,h:18}};
  // GPIO header: 2 x 20 at 2.54 mm, starting 7.1 mm from the left edge of the Pi; even pins on the outer row
  const pin=n=>{const col=Math.floor((n-1)/2),x=PART.pi.x+7.1+1.27+col*2.54,y=PART.pi.y+(n%2?4.77:2.23);return [x,y]};
  const cen=p=>[p.x+p.w/2,p.y+p.h/2];
  function rectMM(c,p,dx,dy,a,fill){const [x,y]=P(p.x+dx,p.y+dy);c.save();c.globalAlpha*=a;c.fillStyle=fill||'#000';c.strokeStyle=ink(.85);c.lineWidth=1.2;c.beginPath();c.roundRect(x,y,p.w*K,p.h*K,3);c.fill();c.stroke();c.restore()}
  function piBoard(c,a){const p=PART.pi;rectMM(c,p,0,0,a,'#060606');c.save();c.globalAlpha*=a;c.strokeStyle=ink(.5);c.lineWidth=1;
    const R=(x,y,w,h)=>{const [X,Y]=P(p.x+x,p.y+y);c.strokeRect(X,Y,w*K,h*K)};
    R(7.1,0.9,50.8,5.1);                       // 40 pin header
    c.fillStyle=ink(.45);for(let n=1;n<=40;n++){const [x,y]=P(...pin(n));c.fillRect(x-1,y-1,2,2)}
    R(24,14,14,14);R(46,14,8,8);                // SoC, RP1
    R(70.5,2,17.5,14);R(70.5,20,17.5,14);R(67,37,21,16); // USB, USB, Ethernet, 3 mm over the edge
    R(7.2,52,8,5);R(22.8,53,6,3.5);R(36.2,53,6,3.5);         // USB C, micro HDMI x2
    R(44,38,3,12);R(51,38,3,12);                // two MIPI connectors
    R(-0.5,20,3,14);                            // PCIe connector
    [[3.5,3.5],[61.5,3.5],[3.5,52.5],[61.5,52.5]].forEach(([x,y])=>{const [X,Y]=P(p.x+x,p.y+y);c.beginPath();c.arc(X,Y,1.35*K,0,7);c.stroke()});
    c.restore()}
  function pump(c,p,dx,dy,a){rectMM(c,p,dx,dy,a);c.save();c.globalAlpha*=a;c.strokeStyle=ink(.6);c.lineWidth=1;
    const [nx,ny]=P(p.x+dx-6,p.y+dy+p.h/2-2.5);c.strokeRect(nx,ny,6*K,5*K);                 // outlet nozzle
    const [ix,iy]=P(p.x+dx+28,p.y+dy+p.h/2);c.beginPath();c.arc(ix,iy,4*K,0,7);c.stroke();   // inlet, underneath
    c.restore()}
  function small(c,p,dx,dy,a,chip){rectMM(c,p,dx,dy,a);if(chip){c.save();c.globalAlpha*=a;c.strokeStyle=ink(.55);const [x,y]=P(p.x+dx+p.w/2-2.5,p.y+dy+p.h/2-2.2);c.strokeRect(x,y,5*K,4.4*K);c.restore()}}
  function cell(c,p,dx,dy,a){const [x,y]=P(p.x+dx,p.y+dy);c.save();c.globalAlpha*=a;c.fillStyle='#000';c.strokeStyle=ink(.85);c.lineWidth=1.2;c.beginPath();c.roundRect(x,y,p.w*K,p.h*K,p.h*K/2);c.fill();c.stroke();
    c.strokeStyle=ink(.5);c.beginPath();c.moveTo(x+(p.w-2)*K,y+4);c.lineTo(x+(p.w-2)*K,y+p.h*K-4);c.stroke();c.restore()}
  /* wires: kind 0 signal, 1 power, 2 water; slack 1 = long lead, 0 = short lead on the plate */
  function wire(c,pts,kind,u,slack,a){if(u<=0)return;const Q=pts.map(q=>P(...q));c.save();c.globalAlpha*=a;
    c.strokeStyle=kind===0?col(1,.95):kind===1?col(0,.95):col(2,.95);c.lineWidth=kind===1?2.6:1.5;if(kind===2)c.setLineDash([6,5]);
    // sample a smooth path through the points, bowed out by the slack, and draw the first fraction u
    const S=[];for(let i=0;i<Q.length-1;i++){const [x0,y0]=Q[i],[x1,y1]=Q[i+1],dx=x1-x0,dy=y1-y0,L=Math.hypot(dx,dy)||1,nx=-dy/L,ny=dx/L,b=slack*Math.min(22,L*.18);
      for(let k=0;k<=20;k++){const s=k/20,w=Math.sin(Math.PI*s)*b;S.push([x0+dx*s+nx*w,y0+dy*s+ny*w])}}
    let tot=0;for(let i=1;i<S.length;i++)tot+=Math.hypot(S[i][0]-S[i-1][0],S[i][1]-S[i-1][1]);let lim=tot*u,acc=0;
    c.beginPath();c.moveTo(...S[0]);for(let i=1;i<S.length;i++){const d=Math.hypot(S[i][0]-S[i-1][0],S[i][1]-S[i-1][1]);if(acc+d>lim){const f=(lim-acc)/d;c.lineTo(S[i-1][0]+(S[i][0]-S[i-1][0])*f,S[i-1][1]+(S[i][1]-S[i-1][1])*f);break}acc+=d;c.lineTo(...S[i])}c.stroke();c.restore()}
  function lab(c,s,x,y,ax,ay,a,align){c.save();c.globalAlpha*=a;if(ax!==undefined){c.strokeStyle=ink(.35);c.lineWidth=1;c.beginPath();c.moveTo(ax,ay);c.lineTo(align==='right'?x+6:x-6,y-4);c.stroke();c.fillStyle=ink(.8);c.beginPath();c.arc(ax,ay,2.2,0,7);c.fill()}
    text(c,s,x,y,11,.75,mono,align||'left',1.1);c.restore()}
  const fly=(t,t0,t1,dist)=>(1-ease(t,t0,t1))*dist;
  function compose(c,t){
    const plate=ease(t,23,24.5), slack=1-ease(t,24.5,27), pot=ease(t,27,29.5), cap=ease(t,29.5,30.5);
    // plate: aluminum carrier, all parts on top
    if(plate>0){c.save();c.globalAlpha*=plate;const [x,y]=P(-1,-1);c.fillStyle='rgba(255,255,255,.05)';c.strokeStyle=ink(.55);c.lineWidth=1.2;c.setLineDash([2,4]);c.fillRect(x,y,(PL.w+2)*K,(PL.h+2)*K);c.strokeRect(x,y,(PL.w+2)*K,(PL.h+2)*K);c.restore()}
    // a: the Pi 5 alone
    piBoard(c,ease(t,.2,1.4));
    // b: sensors beside the Pi, one I2C chain and one I2S pair
    const sA=ease(t,4.5,6),sB=ease(t,5.5,7),sC=ease(t,6,7.5);
    small(c,PART.imu,fly(t,4.5,6,60),0,sA,true);small(c,PART.mic,fly(t,5.5,7,60),0,sB,true);small(c,PART.amp,fly(t,6,7.5,60),0,sC,true);
    if(sC>0){c.save();c.globalAlpha*=sC;c.strokeStyle=ink(.7);const [x,y]=P(PART.amp.x+PART.amp.w/2,PART.amp.y+PART.amp.h+5);c.beginPath();c.arc(x+fly(t,6,7.5,60)*K,y,5*K,0,7);c.stroke();c.restore()}
    const g=ease(t,8.5,9.5)*(1-ease(t,26,27.5));if(g>0){c.save();c.globalAlpha*=g;const [x,y]=P(PART.ghost.x,PART.ghost.y);c.strokeStyle=ink(.5);c.setLineDash([4,4]);c.strokeRect(x,y,PART.ghost.w*K,PART.ghost.h*K);c.restore()}
    // the free connector blinks: the bus goes on
    if(t>8.5&&t<27){const on=(Math.floor(t*2.5)%2)===0;const [x,y]=P(PART.imu.x+PART.imu.w-1.5,PART.imu.y+4);c.fillStyle=col(1,on?.95:.25);c.fillRect(x-4,y,8,12)}
    wire(c,[pin(3),[pin(3)[0],22],[94,22],[94,66],[PART.imu.x,66]],0,ease(t,6.5,8),slack,1);                       // I2C, GPIO 2 and 3, with 3.3 V and ground
    wire(c,[pin(12),[pin(12)[0],30],[126,30],[126,PART.mic.y]],0,ease(t,7,8.5),slack,1);                                // I2S to the microphone
    wire(c,[pin(40),[pin(40)[0],34],[143,34],[143,PART.amp.y]],0,ease(t,7.3,8.8),slack,1);                              // I2S to the amplifier
    wire(c,[[PART.imu.x+PART.imu.w,64],[PART.ghost.x,64]],0,ease(t,8.6,9.6),0,.6*(1-ease(t,26,27.5)));
    // c: driver, two PWM lines, then the pumps
    const d=ease(t,11,12.5);small(c,PART.drv,0,-fly(t,11,12.5,40),d,true);
    wire(c,[pin(32),[pin(32)[0],-6],[56,-6],[56,PART.drv.y]],0,ease(t,12.5,14),slack,1);
    wire(c,[pin(33),[pin(33)[0],9],[60,9],[60,10]],0,ease(t,12.8,14.2),slack,1);
    pump(c,PART.pumpA,-fly(t,13.5,15,70),0,ease(t,13.5,15));pump(c,PART.pumpB,-fly(t,14,15.5,70),0,ease(t,14,15.5));
    wire(c,[[PART.drv.x,8],[42.6,10]],1,ease(t,15,16),slack,1);wire(c,[[PART.drv.x,13],[47,40],[42.6,40]],1,ease(t,15.3,16.3),slack,1);
    // water: in under each pump, out at the nozzle
    [PART.pumpA,PART.pumpB].forEach((p,i)=>{const yy=p.y+p.h/2;wire(c,[[-6,yy],[-20,yy]],2,ease(t,16+i*.3,17+i*.3),0,1);wire(c,[[28,yy+9],[28,yy+16]],2,ease(t,16.3+i*.3,17.3+i*.3),0,i?0:1)});
    // d: cell and regulator; 5 V to the Pi, the cell straight to the driver
    cell(c,PART.cell,-fly(t,18,19.5,60),0,ease(t,18,19.5));small(c,PART.reg,0,fly(t,18.5,20,40),ease(t,18.5,20),true);
    wire(c,[[65.25,71],[PART.reg.x,71]],1,ease(t,19.8,20.6),slack,1);
    wire(c,[[PART.reg.x+PART.reg.w/2,PART.reg.y],[80,40],[pin(4)[0],40],pin(4)],1,ease(t,20.3,21.6),slack,1);
    wire(c,[[30,62],[30,58],[54,58],[54,PART.drv.y+PART.drv.h]],1,ease(t,20.8,22),slack,1);
    // e: potted into one pod, flange of holes, four capped tubes, metal face
    if(pot>0){c.save();const [x,y]=P(-2-1*pot,-2-1*pot),w=(PL.w+4+2*pot)*K,h=(PL.h+4+2*pot)*K;c.globalAlpha*=pot;c.fillStyle='rgba(225,235,238,.14)';c.strokeStyle=ink(.9);c.lineWidth=1.5;c.beginPath();c.roundRect(x,y,w,h,14);c.fill();c.stroke();
      const [fx,fy]=P(-6,-6),fw=(PL.w+12)*K,fh=(PL.h+12)*K;c.strokeStyle=ink(.6);c.beginPath();c.roundRect(fx,fy,fw,fh,18);c.stroke();
      c.fillStyle=ink(.6);const n=[Math.round(fw/26),Math.round(fh/26)];for(let i=0;i<n[0];i++){const xx=fx+(i+.5)*fw/n[0];[fy+7,fy+fh-7].forEach(yy=>{c.beginPath();c.arc(xx,yy,2.2,0,7);c.fill()})}
      for(let i=1;i<n[1]-1;i++){const yy=fy+(i+.5)*fh/n[1];[fx+7,fx+fw-7].forEach(xx=>{c.beginPath();c.arc(xx,yy,2.2,0,7);c.fill()})}c.restore()}
    if(cap>0)[PART.pumpA,PART.pumpB].forEach(p=>{[[-3,p.y+p.h/2],[28,p.y+p.h/2]].forEach(([x,y])=>{const [X,Y]=P(x,y);c.save();c.globalAlpha*=cap;c.fillStyle=col(2,.9);c.beginPath();c.arc(X,Y,7,0,7);c.fill();c.strokeStyle=ink(.9);c.lineWidth=1.2;c.stroke();c.restore()})});
    // labels: each part once, with its real name
    const L=(s,x,y,a,ax,ay,al)=>lab(c,s,x,y,ax,ay,a,al);
    const la=ease(t,1,2)*(1-ease(t,TC-1.2,TC-.4));
    {const [ax,ay]=P(PART.pi.x+80,PART.pi.y+10);L('RASPBERRY PI 5, 85 X 56 MM',1040,150,la,ax,ay)}
    {const [ax,ay]=P(PART.pi.x+30,PART.pi.y+1);L('40 PIN GPIO HEADER',1040,176,la*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.pi.x+52,PART.pi.y+44);L('2 X MIPI, CAMERA OR DISPLAY',1040,520,la*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.pi.x+1,PART.pi.y+27);L('PCIE',600,150,la*(1-pot)*(1-ease(t,11,12)),ax,ay,'right')}
    {const [ax,ay]=P(PART.imu.x+10,PART.imu.y+18);L('IMU, I2C, STEMMA QT',1040,560,ease(t,6,7)*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.mic.x+7,PART.mic.y+14);L('I2S MICROPHONE',1040,585,ease(t,7,8)*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.amp.x+7,PART.amp.y+17);L('I2S AMPLIFIER AND SPEAKER',1040,610,ease(t,7.5,8.5)*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.ghost.x+20,PART.ghost.y+4);L('NEXT SENSOR, SAME FOUR WIRES',1100,470,g*(1-pot),ax,ay)}
    {const [ax,ay]=P(PART.drv.x+7,PART.drv.y);L('DRV8833 DUAL H BRIDGE',430,150,d*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(PART.pumpA.x+20,PART.pumpA.y);L('WATER PUMP A, 3 TO 4.5 V, 0.18 A',430,180,ease(t,14,15)*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(PART.pumpB.x+20,PART.pumpB.y+PART.pumpB.h);L('WATER PUMP B',430,420,ease(t,14.5,15.5)*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(PART.cell.x+20,PART.cell.y+PART.cell.h);L('18650 CELL, 3.6 V, 3500 MAH',430,560,ease(t,18.5,19.5)*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(PART.reg.x+11,PART.reg.y+PART.reg.h);L('5 V REGULATOR, 3 A',700,600,ease(t,19,20)*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(pin(32)[0],-6);L('PWM, GPIO 12 AND 13',700,140,ease(t,13,14)*(1-pot)*(1-ease(t,17,18)),ax,ay,'right')}
    {const [ax,ay]=P(94,30);L('I2C, GPIO 2 AND 3',780,130,ease(t,7,8)*(1-pot)*(1-ease(t,12,13)),ax,ay,'right')}
    {const [ax,ay]=P(140,34);L('I2S, GPIO 18 TO 21',1040,128,ease(t,7.5,8.5)*(1-pot)*(1-ease(t,12,13)),ax,ay)}
    {const [ax,ay]=P(pin(4)[0],40);L('5 V INTO GPIO PINS 2 AND 4',1040,200,ease(t,21,22)*(1-pot),ax,ay)}
    {const [ax,ay]=P(-20,PART.pumpA.y+PART.pumpA.h/2);L('WATER OUT',300,250,ease(t,16.5,17.5)*(1-pot),ax,ay,'right')}
    {const [ax,ay]=P(-6,-6);L('ONE POD, FLANGE OF HOLES',430,120,pot*(1-ease(t,TC-1.2,TC-.4)),ax,ay,'right')}
    {const [ax,ay]=P(-3,PART.pumpA.y+PART.pumpA.h/2);L('FOUR CAPPED TUBES, WATER IN AND OUT',430,640,cap*(1-ease(t,TC-1.2,TC-.4)),ax,ay,'right')}
    {const [ax,ay]=P(PL.w,PL.h);L('ALUMINUM CARRIER, FACE TO THE OUTER SKIN',1040,660,plate*(1-ease(t,TC-1.2,TC-.4)),ax,ay)}
    // f: one piece
    const f=ease(t,30.5,31.5)*(1-ease(t,TC-.8,TC));if(f>0){c.save();c.globalAlpha*=f;c.font='34px Georgia';c.fillStyle=ink(.95);c.textAlign='center';c.fillText('One piece, one grab.',OX+PL.w*K/2,OY+PL.h*K+120);c.restore();
      text(c,'156 x 88 x 27 MM, ABOUT 0.5 KG',OX+PL.w*K/2,OY+PL.h*K+150,11,.7*f,mono,'center',1.2)}
  }
  /* ---------- the wall, side section ---------- */
  const S=2.8, X0=560, X1=1570, LB=640, SK=6, LT=LB-SK, GS=230;      // px per mm, patch, lower skin bottom and top, gel surface
  const PX=1060, PLEN=156, PHT=26.2, FL=164;                          // pod: 156 x 88 x 26.2 mm, flange 164 mm
  const PW=PLEN*S/2, PHh=PHT*S, FW=FL*S/2, PB=LT-6, PT=PB-PHh-4;      // pod half width px, pod height px, flange half width, pod bottom and top
  const RIM=FW+10, WEBS=[];for(let k=0;k<6;k++){const d=RIM+24+k*18*S;if(PX+d<X1-4)WEBS.push(PX-d<X0+4?null:PX-d,PX+d)}
  const WB=WEBS.filter(x=>x!==null).sort((a,b)=>a-b), UT=LT-SK-3;
  const MAG={x:14,w:FW*2+24,y:250,h:400}, MSP=125;
  function podSide(c,x,y,a,cut){ // x center, y bottom (flange underside)
    c.save();c.globalAlpha*=a;c.fillStyle='#000';c.strokeStyle=ink(.85);c.lineWidth=1.3;
    c.beginPath();c.rect(x-FW,y-4,2*FW,4);c.fill();c.stroke();                      // flange
    c.fillStyle='#000';c.strokeStyle=ink(.55);for(let i=0;i<16;i++){const hx=x-FW+6+i*(2*FW-12)/15;if(Math.abs(hx-x)<PW-4)continue;c.fillRect(hx-2,y-4,4,4);c.strokeRect(hx-2,y-4,4,4)}
    c.fillStyle='rgba(225,235,238,.08)';c.strokeStyle=ink(.85);c.beginPath();c.roundRect(x-PW,y-4-PHh,2*PW,PHh,6);c.fill();c.stroke();
    c.fillStyle=ink(.5);c.fillRect(x-PW+6,y-4-PHh+5,2*PW-12,1.5*S);                  // aluminum face, up
    c.strokeStyle=ink(.4);c.lineWidth=1;const top=y-4-PHh+5+1.5*S;
    c.strokeRect(x-PW+6,top,42.6*S,22.7*S);                                         // pumps, side by side, one seen
    c.strokeRect(x-PW+6+65*S,top,85*S,1.6*S);c.strokeRect(x-PW+6+65*S+60*S,top+1.6*S,22*S,14*S);c.strokeRect(x-PW+6+65*S+8*S,top+1.6*S,51*S,6*S); // Pi 5 board, jacks, header (hanging)
    c.beginPath();c.roundRect(x-PW+6+47*S,top+2,18*S,18.75*S,18.75*S/2);c.stroke();                                 // the 18650, seen end on
    c.fillStyle=ink(.85);c.fillRect(x-10*S,y-4-PHh-1*S,20*S,1*S);                    // steel disk for the magnet
    [x-PW+14,x-PW+30].forEach(px=>{c.strokeStyle=ink(.85);c.lineWidth=1.3;c.beginPath();c.moveTo(px-3,y-4-PHh);c.lineTo(px-3,y-4-PHh-22);c.moveTo(px+3,y-4-PHh);c.lineTo(px+3,y-4-PHh-22);c.stroke();c.fillStyle=col(2,.9);c.fillRect(px-5,y-4-PHh-27,10,6)});
    c.restore()}
  function needle(c,x,y,a){c.save();c.globalAlpha*=a;c.strokeStyle=ink(.85);c.fillStyle='#000';c.lineWidth=1.3;
    c.beginPath();c.moveTo(x-9,y-190);c.lineTo(x+9,y-190);c.lineTo(x+9,y-40);c.lineTo(x+2,y);c.lineTo(x-2,y);c.lineTo(x-9,y-40);c.closePath();c.fill();c.stroke();
    c.strokeStyle=ink(.3);c.beginPath();c.moveTo(x,y-190);c.lineTo(x,-10);c.stroke();c.restore()}
  function holder(c,x,y,a,on){c.save();c.globalAlpha*=a;c.strokeStyle=ink(.85);c.fillStyle='#000';c.lineWidth=1.3;
    c.beginPath();c.rect(x-5,y-150,10,108);c.fill();c.stroke();c.beginPath();c.rect(x-10*S,y-15*S,20*S,15*S);c.fill();c.stroke();
    if(on){c.fillStyle=col(0,.9);c.fillRect(x-10*S+4,y-5,20*S-8,3)}
    c.strokeStyle=ink(.3);c.beginPath();c.moveTo(x,y-150);c.lineTo(x,-10);c.stroke();c.restore()}
  function tag(c,s,x,y,ax,ay,a,align){c.save();c.globalAlpha*=a;if(ax!==undefined){c.strokeStyle=ink(.35);c.lineWidth=1;c.font='11px '+mono;const tw=c.measureText(s).width+s.length*1.2,left=align==='right'?x-tw:x,ex=ax<left?left-6:ax>left+tw?left+tw+6:ax;c.beginPath();c.moveTo(ax,ay);c.lineTo(ex,ax>=left&&ax<=left+tw?y+4:y-4);c.stroke();c.fillStyle=ink(.8);c.beginPath();c.arc(ax,ay,2.2,0,7);c.fill()}
    text(c,s,x,y,11,.6,mono,align||'left',1.2);c.restore()}
  const STEPS=[
    [0,4.5,'1 · The brain','A Raspberry Pi 5: 40 pin header, two MIPI connectors, USB, PCIe. It needs 5 V and draws about 0.8 A.','Board 85 x 56 mm. Typical draw of the bare board 800 mA (Raspberry Pi documentation).'],
    [4.5,11,'2 · Sensors on one bus','Sensors sit beside the Pi. The IMU chains on I2C with four wire STEMMA QT leads; microphone and speaker share I2S.','A new sensor plugs into the free connector: same bus, same board. The camera would take a MIPI connector.'],
    [11,18,'3 · A driver for the pumps','A GPIO pin is a 3.3 V signal of a few milliamps; each pump draws 0.18 A. A driver is needed.','The DRV8833 switches the cell to the two pumps; GPIO 12 and 13 set each speed by PWM. Run one harder to steer.'],
    [18,23,'4 · Power','One 18650 cell. A 5 V regulator feeds the Pi; the pumps run straight from the cell through the driver.','Pi 4.0 W / 0.9 + pumps 1.3 W = 5.8 W; 12.6 Wh / 5.8 W = about 2.2 h with both pumps on.'],
    [23,30.5,'5 · One plate, one pod','Every part sits on one aluminum plate, every lead is short and soldered. The plate is cast into one silicone pod.','No wire runs in the print: the wires are inside the pod. Only water crosses the skin, through four capped tubes.'],
    [30.5,TC,'6 · One piece','One piece, one grab for the arm.','156 x 88 x 27 mm with the flange of holes, about 0.5 kg.'],
    [TC+0,TC+5.5,'7 · Lower skin','The needle prints the lower skin, the webs and a low rim.','The rim is tapered. It will center the pod, so a small error at the tool change does no harm.'],
    [TC+5.5,TC+8.5,'8 · A bed','Into the rim goes a bed of fresh silicone, so no gel stays there.','Gel left in the rim would stay as a film and stop the bond. The bed pushes the gel out first.'],
    [TC+8.5,TC+10.5,'Tool change','Tool change in the tail: the needle off, the magnet holder on.',''],
    [TC+10.5,TC+17.5,'9 · The pod','The holder takes the pod from the dry magazine and presses the pod into the wet bed, metal face up.','Bed and gel squeeze out at the rim and rise through the flange holes.'],
    [TC+17.5,TC+19.5,'Tool change','Tool change: the holder off, the needle back on.',''],
    [TC+19.5,TC+26,'10 · The cover','Wet on wet, the needle prints around the pod, over the pod, then the upper skin.','The pod is 27 mm tall; the flat wall is 3.4 mm. The pod is a thick island in the wall.'],
    [TC+26,DUR,'11 · Cured, then “birth”','After the cure the pod is a solid island between the two skins. Air fills the cells around it.','16 hours of cure. Only the four capped tubes cross the skin. Data by radio; charging is still open.']];
  function wall(c,T){const t=T-TC;
    // gel, tail and dock
    c.fillStyle='rgba(255,255,255,.025)';c.fillRect(X0-40,GS,W-X0+40,LB+40-GS);
    c.strokeStyle=ink(.25);c.lineWidth=1;c.beginPath();for(let x=X0-40;x<=W;x+=10){const y=GS+1.2*Math.sin(x*.02+t*.7);x>X0-40?c.lineTo(x,y):c.moveTo(x,y)}c.stroke();
    c.setLineDash([4,6]);c.beginPath();c.moveTo(X0-40,GS-30);c.lineTo(X0-40,LB+40);c.stroke();c.setLineDash([]);
    text(c,'TAIL',X0-56,GS-14,11,.5,mono,'right',1.2);text(c,'HEAD',X0-24,GS-14,11,.5,mono,'left',1.2);
    tag(c,'GEL, CARBOPOL',W-30,GS+30,undefined,undefined,1,'right');
    c.strokeStyle=ink(.6);c.lineWidth=1.2;c.beginPath();c.moveTo(MAG.x,MAG.y);c.lineTo(MAG.x,MAG.y+MAG.h);c.lineTo(MAG.x+MAG.w,MAG.y+MAG.h);c.lineTo(MAG.x+MAG.w,MAG.y);c.stroke();
    text(c,'MAGAZINE, DRY, IN THE TAIL',MAG.x,MAG.y-50,11,.6,mono,'left',1.2);
    const MC=MAG.x+MAG.w/2, slot=k=>MAG.y+MAG.h-8-k*MSP;
    const taken=t>=12.2&&t<DUR-TC-.6;for(let k=0;k<(taken?2:3);k++)podSide(c,MC,slot(k),1);
    const sk=ease(t,.3,3.2),rim=ease(t,4.2,5.5),bed=ease(t,5.8,8.2),inflate=ease(t,27,30),cell=lerp(3,3+5.5*S*2,inflate),wet=1-ease(t,26,27.6),FR=a=>'rgba(250,246,226,'+a+')';
    // lower skin as beads, laid behind the needle
    const xs=lerp(X0,X1,sk);if(sk>0){for(let x=X0+3;x<=xs;x+=6){const nw=clamp(1-(xs-x)/160);c.fillStyle=nw>0&&wet>0?FR(.18+.5*nw*wet):ink(.16+.1*wet);c.beginPath();c.arc(x,LB-SK/2,3.2,0,7);c.fill()}c.strokeStyle=ink(.8);c.lineWidth=1;c.strokeRect(X0,LT,xs-X0,SK)}
    WB.forEach((x,i)=>{const a=ease(t,3.2+i*.12,3.45+i*.12);if(a<=0)return;const h=Math.max(cell*a,2);c.fillStyle=a<1?FR(.6):ink(.16+.1*wet);c.fillRect(x-2,LT-h,4,h);c.strokeStyle=ink(.8);c.strokeRect(x-2,LT-h,4,h)});
    if(rim>0){c.globalAlpha=rim;c.fillStyle=ink(.16);c.strokeStyle=ink(.8);[-1,1].forEach(s=>{c.beginPath();c.moveTo(PX+s*(RIM-4),LT);c.lineTo(PX+s*(RIM+2),LT-14);c.lineTo(PX+s*(RIM+8),LT-14);c.lineTo(PX+s*(RIM+4),LT);c.closePath();c.fill();c.stroke()});c.globalAlpha=1}
    if(bed>0){const rows=bed*2;for(let r=0;r<Math.ceil(rows);r++){const f=Math.min(1,rows-r),y=LT-3-r*4.5,xe=r%2?PX+RIM-6-2*(RIM-6)*f:PX-RIM+6+2*(RIM-6)*f;
        for(let x=PX-RIM+6;x<=PX+RIM-6;x+=6){if(r%2?x<xe:x>xe)continue;c.fillStyle=FR(t<19.5?.32+.25*(r===Math.ceil(rows)-1&&bed<1):.18+.2*wet);c.beginPath();c.arc(x,y,3,0,7);c.fill()}}
      const g=Math.sin(Math.PI*clamp((t-5.8)/2.6));if(g>0){c.strokeStyle=ink(.55*g);c.lineWidth=1.2;[-1,1].forEach(s2=>{const x=PX+s2*(RIM-20),y=LT-16;c.beginPath();c.moveTo(x,y+10);c.quadraticCurveTo(x+s2*24,y-14-10*g,x+s2*50,y-6);c.stroke();c.beginPath();c.moveTo(x+s2*50,y-6);c.lineTo(x+s2*42,y-12);c.moveTo(x+s2*50,y-6);c.lineTo(x+s2*40,y-2);c.stroke()});
        text(c,'GEL PUSHED OUT',PX,LT-60,11,.6*g,mono,'center',1.2)}}
    const sq=ease(t,14.4,15.6);if(sq>0){[-1,1].forEach(s=>{c.fillStyle=ink(.3);c.beginPath();c.ellipse(PX+s*(RIM+5),LT-16,7*sq,5*sq,0,0,7);c.fill()})}
    // the tool
    let tool='needle',tx=PX,ty=LT,on=false,carry=false;const zz=(u,x0,x1,n)=>lerp(x0,x1,Math.abs((u*n%2)-1));
    const top=[MC,slot(2)-4-PHh-1*S],seat=[PX,PB-4-PHh-1*S],away=[MC,60];
    if(t<3.2){tx=xs;ty=LB-2}
    else if(t<4.4){const i=Math.min(WB.length-1,Math.floor((t-3.2)/.12));tx=WB[i];ty=LT-4}
    else if(t<5.5){tx=t<4.85?PX-RIM-3:PX+RIM+3;ty=LT-14}
    else if(t<8.5){tx=zz(bed,PX-RIM+8,PX+RIM-8,4);ty=LT-4-5*bed}
    else if(t<10.5){const u=(t-8.5)/2;tool=u<.5?'needle':'holder';const v=u<.5?ease(u,0,.5):1-ease(u,.5,1);const from=u<.5?[PX,LT-10]:[MC,MAG.y-70];tx=lerp(from[0],away[0],v);ty=lerp(from[1],away[1]+60,v)}
    else if(t<17.5){tool='holder';
      if(t<12){tx=top[0];ty=lerp(MAG.y-70,top[1],ease(t,10.5,11.8))}
      else if(t<12.4){tx=top[0];ty=top[1];on=t>=12.1;carry=on}
      else if(t<15.6){on=true;carry=true;const u=ease(t,12.4,14.2),d=ease(t,14.2,15.6);tx=lerp(top[0],seat[0],u);ty=t<14.2?lerp(top[1],seat[1]-40,u)-70*Math.sin(Math.PI*u):lerp(seat[1]-40,seat[1],d)}
      else if(t<16.1){tx=PX;ty=seat[1];on=false}
      else{tx=PX;ty=lerp(seat[1],seat[1]-110,ease(t,16.1,17.4))}}
    else if(t<19.5){const u=(t-17.5)/2;tool=u<.5?'holder':'needle';const v=u<.5?ease(u,0,.5):1-ease(u,.5,1);const from=u<.5?[PX,seat[1]-110]:[PX-PW-20,LT-20];tx=lerp(from[0],MC,v);ty=lerp(from[1],60,v)}
    else if(t<26){const u=ease(t,19.5,23.5),w=ease(t,23.5,25.8);if(t<23.5){tx=zz(u,PX-PW-16,PX+PW+16,12);ty=lerp(LT-10,PT-6,u)}else{tx=w<.5?lerp(PX-RIM-12,WB[0],w*2):lerp(PX+RIM+12,WB[WB.length-1],(w-.5)*2);ty=UT}}
    else tool='none';
    const placed=t>=15.6;if(placed)podSide(c,PX,PB,1);if(carry)podSide(c,tx,ty+4+PHh+1*S,1);
    // the cover, from the bottom up, then the upper skin outward
    const cov=ease(t,19.5,23.5),us=ease(t,23.5,25.8);
    if(cov>0){const tp=lerp(LT,PT-10,cov);c.save();c.beginPath();c.rect(0,tp,W,H);c.clip();const L2=PW+16;
      const Pp=new Path2D();Pp.moveTo(PX-RIM-10,LT);Pp.lineTo(PX-L2,PT+10);Pp.quadraticCurveTo(PX-L2,PT-10,PX-L2+20,PT-10);Pp.lineTo(PX+L2-20,PT-10);Pp.quadraticCurveTo(PX+L2,PT-10,PX+L2,PT+10);Pp.lineTo(PX+RIM+10,LT);Pp.closePath();
      c.fillStyle=wet>0?FR(.1+.14*wet):ink(.13);c.fill(Pp);c.save();c.clip(Pp);c.strokeStyle=ink(.2);c.lineWidth=1;for(let y=LT-4;y>PT-14;y-=4.5){c.beginPath();c.moveTo(PX-L2-20,y);c.lineTo(PX+L2+20,y);c.stroke()}c.restore();
      c.strokeStyle=ink(.8);c.lineWidth=1;c.stroke(Pp);c.restore();podSide(c,PX,PB,.3*cov)}
    if(us>0){c.fillStyle=wet>0?FR(.16+.3*wet):ink(.16);c.strokeStyle=ink(.8);c.lineWidth=1;const xl=lerp(PX-RIM-10,WB[0],us),xr=lerp(PX+RIM+10,WB[WB.length-1],us),yb=LT-cell;
      const seg=(xa,xb)=>{const Pq=new Path2D();const pts=[xa,...WB.filter(x=>x>xa&&x<xb),xb];Pq.moveTo(xa,yb);for(let i=1;i<pts.length;i++){const m=(pts[i-1]+pts[i])/2;Pq.quadraticCurveTo(m,yb-5.5*S*2*inflate,pts[i],yb)}
        Pq.lineTo(xb,yb-SK);for(let i=pts.length-1;i>0;i--){const m=(pts[i-1]+pts[i])/2;Pq.quadraticCurveTo(m,yb-SK-5.5*S*2*inflate,pts[i-1],yb-SK)}Pq.closePath();c.fill(Pq);c.stroke(Pq)};
      seg(xl,PX-RIM-10);seg(PX+RIM+10,xr)}
    if(inflate>0)tag(c,'CELL, AIR',W-30,LT-cell-70,WB[WB.length-2]+20,LT-cell/2,inflate,'right');
    if(tool==='needle'){needle(c,tx,ty,1);const pr=(t<5.5)||(t>5.8&&t<8.3)||(t>19.5&&t<25.8);if(pr){c.fillStyle=FR(.95);c.beginPath();c.arc(tx,ty,3.4,0,7);c.fill();c.strokeStyle=FR(.35);c.lineWidth=1;c.beginPath();c.arc(tx,ty,8+3*Math.sin(t*12),0,7);c.stroke()}}
    else if(tool==='holder')holder(c,tx,ty,1,on);
    tag(c,'LOWER SKIN, 1.2 MM',W-30,LB+30,X1-60,LB-3,sk,'right');
    tag(c,'WEB, 0.8 MM',X0+20,LB+30,WB[1],LT-2,ease(t,3.5,4.4)*(1-inflate),'left');
    tag(c,'RIM',PX-RIM-120,LT-70,PX-RIM-2,LT-10,rim*(1-ease(t,19.5,20.5)),'right');
    tag(c,'FRESH BED',PX+RIM+60,LT-70,PX+RIM-30,LT-4,bed*(1-ease(t,10.5,11.5)),'left');
    tag(c,'POD, METAL FACE UP',PX+RIM+60,PT-30,PX+PW-10,PT+10,ease(t,15.6,16.2)*(1-ease(t,19.5,20)),'left');
    tag(c,'CAPPED TUBES',PX-PW-140,PT-60,PX-PW+14,PT-22,ease(t,16,16.6)*(1-ease(t,27,27.5)),'right');
    tag(c,'COVER',PX+RIM+60,PT-30,PX+PW+10,PT+20,ease(t,20,20.6)*(1-ease(t,27,27.5)),'left');
    tag(c,'UPPER SKIN',X0+30,LT-cell-56,X0+60,LT-cell-4,us,'left');
    if(t>=26)text(c,'16 HOURS LATER',W-30,GS+60,11,.6*ease(t,26,26.5),mono,'right',1.2);
  }
  function legend(c){const x=W-260,y=36;[[0,'SIGNAL'],[1,'POWER'],[2,'WATER']].forEach(([k,s],i)=>{const yy=y+i*18;c.save();c.strokeStyle=k===0?col(1,.95):k===1?col(0,.95):col(2,.95);c.lineWidth=k===1?2.6:1.5;if(k===2)c.setLineDash([6,5]);c.beginPath();c.moveTo(x,yy);c.lineTo(x+36,yy);c.stroke();c.restore();text(c,s,x+46,yy+4,11,.6,mono,'left',1.2)})}
  const ctl=loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);c.globalAlpha=fade;
    if(t<TC){c.globalAlpha=fade*(1-ease(t,TC-.6,TC));compose(c,t)}else{c.globalAlpha=fade*ease(t,TC,TC+.6);wall(c,t)}
    c.globalAlpha=fade;legend(c);
    const St=STEPS.find(s=>t>=s[0]&&t<s[1])||STEPS[STEPS.length-1];
    text(c,St[2].toUpperCase(),64,H-112,12,.55,mono,'left',1.6);
    c.save();c.font='26px Georgia';const w=c.measureText(St[3]).width;c.restore();
    text(c,St[3],64,H-74,Math.min(26,26*1470/w),.95,'Georgia');
    if(St[4])text(c,St[4],64,H-40,14,.6);
    c.globalAlpha=1;return St[2]+'. '+St[3]+' '+St[4];
  });
  // play, pause and scrub under the canvas; step marks on the slider
  const pb=document.getElementById('wplay'),sk=document.getElementById('wseek'),tm=document.getElementById('wtime'),dl=document.getElementById('wsteps');
  if(pb&&sk){const lab2=s=>Math.floor(s/60)+':'+String(Math.floor(s)%60).padStart(2,'0');sk.max=DUR;
    if(dl){dl.innerHTML=STEPS.map(s=>'<option value="'+s[0]+'"></option>').join('')}
    ctl.onframe=t=>{sk.value=t;if(tm)tm.textContent=lab2(t)+' / '+lab2(DUR);const p=ctl.playing?'Pause':'Play';if(pb.textContent!==p)pb.textContent=p};
    pb.onclick=()=>ctl.playing?ctl.pause():ctl.play();sk.oninput=()=>{ctl.pause();ctl.seek(sk.value)}}
})();

/* 4 · The tail copies itself */
(function(){
  const cv=document.getElementById('d-tail');if(!cv)return;
  const W=1600,H=700,S=520,Yb=500,HX=430,XN=1010,DUR=22;
  const MOD=['base','upper arm','forearm','end'];
  loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);c.globalAlpha=fade;
    // the tank edge with arm modules waiting on it
    const TR=[1110,250];c.strokeStyle=ink(.3);c.beginPath();c.moveTo(TR[0]-30,TR[1]);c.lineTo(TR[0]+330,TR[1]);c.stroke();
    text(c,'TANK EDGE',TR[0]+330,TR[1]+18,10,.4,mono,'right',1.2);
    const mh=m=>{const H=headMap(HX,Yb,S,{});return H};const hm=mh();
    drawHead(c,hm,1);
    // phases
    const pr=clamp((t-1)/4), out=ease(t,5,7), turn=ease(t,7,8.5), undock=ease(t,8.5,10.5), back=ease(t,17.5,19.5);
    // new tail body
    let nb=null;
    if(t>=1){
      if(t<5){ // printed folded in the gel
        const [fx,fy]=hm(.08,.005);const tm=tailMap(fx+.29*S*.35,fy,S*.35);c.save();c.beginPath();c.rect(0,fy-.33*S*.35*pr,W,H);c.clip();c.globalAlpha*=fade;drawTail(c,tm,1);c.restore();
        c.strokeStyle=ink(.5);c.beginPath();c.moveTo(fx,fy-.33*S*.35*pr);c.lineTo(fx+.3*S*.35,fy-.33*S*.35*pr);c.stroke();
      }else{
        const s=lerp(.35,1,ease(t,5.6,7)),[mx]=hm(.42,0);
        let Xd=t<7?lerp(hm(.08,0)[0]+.29*S*.35,mx+.29*S,out):lerp(mx+.29*S,XN+ (1-turn)*0,turn);
        let lift=t<7?40*Math.sin(Math.PI*out):0;
        // turning around: squeeze to zero width and open the other way
        const fl=turn<.5?1-2*turn:2*turn-1, flip=turn>=.5;
        const tm=(x,z)=>{const base=tailMap(0,0,S*s,flip)(x,z);return [Xd+base[0]*fl+(flip?(-.29*S*0):0),Yb-lift+base[1]]};
        if(t>=8.5){nb=(x,z)=>{const b=tailMap(XN,Yb,S,true)(x,z);return b}}
        drawTail(c,t>=8.5?nb:tm,1);
      }
    }
    // the parent tail: docked, then leaves its head to meet the new one, then returns
    const XP=XN-8;
    let Xp=lerp(HX,XP,undock);if(t>17.5)Xp=lerp(XP,HX,back);
    const pt=tailMap(Xp,Yb,S);drawTail(c,pt,1);
    // modules: the parent picks each from the edge and sets it in the new tail
    let tip=pt(-.02,.12), built=0, carry=null;
    for(let i=0;i<4;i++){const a0=10.5+i*1.6;if(t>a0+1.6)built=i+1;
      if(t>=a0&&t<a0+1.6){const u=(t-a0)/1.6,src=[TR[0]+i*80,TR[1]-6],dst=nb?nb(-.115,.2):[XN,Yb];
        tip=u<.45?[lerp(pt(-.02,.12)[0],src[0],ease(u,0,.45)),lerp(pt(-.02,.12)[1],src[1],ease(u,0,.45))]:[lerp(src[0],dst[0],ease(u,.5,1)),lerp(src[1],dst[1],ease(u,.5,1))];
        if(u>=.45)carry={p:tip,i}}}
    for(let i=0;i<4;i++){if(i<built||(carry&&carry.i===i))continue;const x=TR[0]+i*80;c.fillStyle=ink(.75);c.fillRect(x-10,TR[1]-16,20,14);text(c,MOD[i].toUpperCase(),x,TR[1]-24,9,.5,mono,'center',1)}
    // last thing on the edge: a tile set, taken by the new tail itself
    const own=ease(t,19,20.5);
    if(t<20.3){const x=TR[0]+320;c.fillStyle=col(3,1);c.fillRect(x-7,TR[1]-14,14,12);text(c,'TILES',x,TR[1]-24,9,.5,mono,'center',1)}
    if(t>=8.5&&t<17.5&&t<10.5){tip=pt(-.02,.12)}
    arm(c,pt,S,tip,1);
    if(carry){c.fillStyle=ink(.85);c.fillRect(carry.p[0]-9,carry.p[1]-6,18,12)}
    if(nb){
      const segs=Math.min(3,built===0?0:built===1?1:built===2?2:3);
      let ntip=nb(-.02,.12);
      if(t>=19&&t<21){const u=ease(t,19,20),v=ease(t,20,20.8),src=[TR[0]+320,TR[1]-8],dst=nb(-.2,.1);ntip=t<20?[lerp(ntip[0],src[0],u),lerp(ntip[1],src[1],u)]:[lerp(src[0],dst[0],v),lerp(src[1],dst[1],v)];if(t>=20.3){c.fillStyle=col(3,1);c.fillRect(ntip[0]-7,ntip[1]-6,14,12)}}
      if(built>=4){arm(c,nb,S,ntip,1,3)}else if(segs){arm(c,nb,S,nb(-.02,.12),1,segs)}
      if(t>=20.8){const [x,y]=nb(-.2,.1);c.fillStyle=col(3,1);c.fillRect(x-7,y-6,14,12)}
    }
    // caption
    let cap;
    if(t<5)cap='The arm prints a tail shell in the gel, not a head.';
    else if(t<8.5)cap='Born through the mouth, the shell inflates into an empty tail and turns round.';
    else if(t<10.5)cap='The tail that printed it leaves its head and meets the new tail face to face.';
    else if(t<17.5)cap='It hands over the arm piece by piece. Each joint is powered as soon as it is in.';
    else cap='The new tail takes its last part by itself. Tails are no longer a fixed number.';
    text(c,cap,64,H-60,30,.95,'Georgia');
    c.globalAlpha=1;return cap;
  });
})();
})();

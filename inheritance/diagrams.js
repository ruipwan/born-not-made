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
    [[1330,650],'right',400,'The next body','Printed folded flat in 18 layers, 143 x 194 x 79 mm.'],
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

/* 3 · How a part gets into the wall. Close up section of the wall being printed flat in the gel, 8 px to the mm.
   Method from the sources listed under the canvas: a tapered rim, a bed of fresh silicone, the pod pressed in wet (Valentine 2017,
   Wehner 2016), the cover printed wet on wet within the pot life of Dragon Skin 30 (Smooth-On bulletin). */
(function(){
  const cv=document.getElementById('d-wall');if(!cv)return;
  const W=1600,H=800,DUR=34;
  const X0=380,X1=1560,LB=600,LT=590,UT=572,PX=960,PH=120,PT=522,PB=578; // lower skin bottom/top, upper skin top, pod half width, pod top/bottom
  const WEBS=[383,470,560,650,1270,1360,1450,1537], MAG={x:40,w:280,y:210,h:340}, MSP=108;
  const GS=130; // gel surface
  function pod(c,x,y,a,ports){ // x = center, y = bottom
    c.save();c.globalAlpha*=a;
    c.fillStyle='#000';c.strokeStyle=ink(.85);c.lineWidth=1.3;
    c.beginPath();c.roundRect(x-PH,y-56,2*PH,48,8);c.fill();c.stroke();
    // flange with holes, the lock for the fresh silicone
    c.beginPath();c.rect(x-PH-12,y-8,2*PH+24,8);c.fill();c.stroke();
    c.fillStyle='#000';c.strokeStyle=ink(.6);[-1,1].forEach(s=>[0,1].forEach(k=>{const hx=x+s*(PH+2-k*20)-4;c.fillRect(hx,y-7,8,6);c.strokeRect(hx,y-7,8,6)}));
    // the parts inside, faint
    c.strokeStyle=ink(.35);c.lineWidth=1;c.strokeRect(x-PH+16,y-46,92,28);c.strokeRect(x-PH+120,y-42,46,20);c.strokeRect(x+60,y-44,44,24);
    if(ports){c.strokeStyle=ink(.85);c.lineWidth=1.3;[x+70,x+94].forEach(px=>{c.beginPath();c.moveTo(px-4,y-56);c.lineTo(px-4,y-104);c.moveTo(px+4,y-56);c.lineTo(px+4,y-104);c.stroke();c.fillStyle=ink(.85);c.fillRect(px-6,y-110,12,6)})}
    c.restore();
  }
  function needle(c,x,y,a){c.save();c.globalAlpha*=a;c.strokeStyle=ink(.85);c.fillStyle='#000';c.lineWidth=1.3;
    c.beginPath();c.moveTo(x-9,y-190);c.lineTo(x+9,y-190);c.lineTo(x+9,y-40);c.lineTo(x+2,y);c.lineTo(x-2,y);c.lineTo(x-9,y-40);c.closePath();c.fill();c.stroke();
    c.strokeStyle=ink(.3);c.beginPath();c.moveTo(x,y-190);c.lineTo(x,-10);c.stroke();c.restore()}
  function holder(c,x,y,a,on){c.save();c.globalAlpha*=a;c.strokeStyle=ink(.85);c.fillStyle='#000';c.lineWidth=1.3;
    c.beginPath();c.rect(x-5,y-170,10,130);c.fill();c.stroke();c.beginPath();c.rect(x-40,y-40,80,40);c.fill();c.stroke();
    if(on){c.fillStyle=ink(.85);c.fillRect(x-30,y-6,60,4)}
    c.strokeStyle=ink(.3);c.beginPath();c.moveTo(x,y-170);c.lineTo(x,-10);c.stroke();c.restore()}
  function tag(c,s,x,y,ax,ay,a,align){c.save();c.globalAlpha*=a;if(ax!==undefined){c.strokeStyle=ink(.35);c.lineWidth=1;c.font='11px '+mono;const tw=c.measureText(s).width+s.length*1.2,left=align==='right'?x-tw:x,ex=ax<left?left-6:ax>left+tw?left+tw+6:ax;c.beginPath();c.moveTo(ax,ay);c.lineTo(ex,ax>=left&&ax<=left+tw?y+4:y-4);c.stroke();c.fillStyle=ink(.8);c.beginPath();c.arc(ax,ay,2.2,0,7);c.fill()}
    text(c,s,x,y,11,.6,mono,align||'left',1.2);c.restore()}
  const STEPS=[
    [0,5.5,'1 · Lower skin','The needle prints the lower skin, the webs and a low rim.','The rim is tapered. It will center the pod, so a small error at the tool change does no harm.'],
    [5.5,8.5,'2 · A bed','Into the rim goes a bed of fresh silicone, so no gel stays there.','Gel left in the rim would stay as a film and stop the bond. The bed pushes the gel out first.'],
    [8.5,10.5,'Tool change','Tool change in the tail: the needle off, the magnet holder on.',''],
    [10.5,17.5,'3 · The pod','The holder brings a sealed pod from the dry magazine and presses the pod into the wet bed.','The pod is cast in Dragon Skin 30 beforehand, with a flange full of holes. Bed and gel squeeze out at the rim.'],
    [17.5,19.5,'Tool change','Tool change: the holder off, the needle back on.',''],
    [19.5,26,'4 · The cover','Wet on wet, the needle prints around the pod, over the pod, then the upper skin.','All within the 45 minutes of pot life of Dragon Skin 30, so bed, flange holes and cover cure as one.'],
    [26,DUR,'5 · Cured, then “birth”','After the cure the pod is a solid island between the two skins. Air fills the cells around it.','16 hours of cure. No wire crosses the skin: Bluetooth from the controller, charging by a coil through the skin. A pump pod adds two capped ports.']];
  const ctl=loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);c.globalAlpha=fade;
    // gel, tail and dock
    c.fillStyle='rgba(255,255,255,.025)';c.fillRect(X0-40,GS,W-X0+40,LB+40-GS);
    c.strokeStyle=ink(.25);c.lineWidth=1;c.beginPath();for(let x=X0-40;x<=W;x+=10){const y=GS+1.2*Math.sin(x*.02+t*.7);x>X0-40?c.lineTo(x,y):c.moveTo(x,y)}c.stroke();
    c.setLineDash([4,6]);c.beginPath();c.moveTo(X0-40,GS-30);c.lineTo(X0-40,LB+40);c.stroke();c.setLineDash([]);
    text(c,'TAIL',X0-56,GS-14,11,.5,mono,'right',1.2);text(c,'HEAD',X0-24,GS-14,11,.5,mono,'left',1.2);
    tag(c,'GEL, CARBOPOL',W-30,GS+30,undefined,undefined,1,'right');
    // magazine, dry, in the tail
    c.strokeStyle=ink(.6);c.lineWidth=1.2;c.beginPath();c.moveTo(MAG.x,MAG.y);c.lineTo(MAG.x,MAG.y+MAG.h);c.lineTo(MAG.x+MAG.w,MAG.y+MAG.h);c.lineTo(MAG.x+MAG.w,MAG.y);c.stroke();
    text(c,'MAGAZINE, DRY',MAG.x,MAG.y-62,11,.6,mono,'left',1.2);text(c,'IN THE TAIL',MAG.x,MAG.y-46,11,.6,mono,'left',1.2);
    const taken=t>=12.2&&t<DUR-.6;
    for(let k=0;k<(taken?2:3);k++)pod(c,MAG.x+MAG.w/2,MAG.y+MAG.h-8-k*MSP,1,true);
    // the wall: lower skin and webs and rim
    const sk=ease(t,.3,3.2), wb=ease(t,3.2,4.4), rim=ease(t,4.2,5.5), bed=ease(t,5.8,8.2);
    const inflate=ease(t,27,30), cell=lerp(8,64,inflate);
    c.fillStyle=ink(.16);c.strokeStyle=ink(.8);c.lineWidth=1;
    // fresh silicone is glossy and brighter; it turns matte in the cure
    const wet=1-ease(t,26,27.6), FR=a=>'rgba(250,246,226,'+a+')';
    // lower skin as beads in section, laid one by one behind the needle tip
    const xs=lerp(X0,X1,sk);if(sk>0){for(let x=X0+5;x<=xs;x+=10){const nw=clamp(1-(xs-x)/160);c.fillStyle=nw>0&&wet>0?FR(.18+.5*nw*wet):ink(.16+.1*wet);c.beginPath();c.arc(x,LB-5,5.4,0,7);c.fill()}
      c.strokeStyle=ink(.8);c.strokeRect(X0,LT,xs-X0,LB-LT)}
    WEBS.forEach((x,i)=>{const a=ease(t,3.2+i*.15,3.5+i*.15);if(a<=0)return;const h=Math.max(cell*a,2);c.fillStyle=a<1?FR(.6):ink(.16+.1*wet);c.fillRect(x-3,LT-h,6,h);c.strokeStyle=ink(.8);c.strokeRect(x-3,LT-h,6,h)});
    if(rim>0){c.globalAlpha=fade*rim;[-1,1].forEach(s=>{c.beginPath();c.moveTo(PX+s*136,LT);c.lineTo(PX+s*146,LT-32);c.lineTo(PX+s*154,LT-32);c.lineTo(PX+s*144,LT);c.closePath();c.fill();c.stroke()});c.globalAlpha=fade}
    if(bed>0){const rows=bed*3;for(let r=0;r<Math.ceil(rows);r++){const f=Math.min(1,rows-r),y=LT-3-r*5.3,xe=r%2?PX+132-264*f:PX-132+264*f;
        for(let x=PX-131;x<=PX+131;x+=8){if(r%2?x<xe:x>xe)continue;c.fillStyle=FR(t<19.5?.32+.25*(r===Math.ceil(rows)-1&&bed<1):.18+.2*wet);c.beginPath();c.arc(x,y,4,0,7);c.fill()}}
      // the gel in the rim is pushed out over the edge
      const g=Math.sin(Math.PI*clamp((t-5.8)/2.6));if(g>0){c.strokeStyle=ink(.55*g);c.lineWidth=1.2;[-1,1].forEach(s2=>{const x=PX+s2*120,y=LT-30;c.beginPath();c.moveTo(x,y+14);c.quadraticCurveTo(x+s2*20,y-14-10*g,x+s2*48,y-6);c.stroke();c.beginPath();c.moveTo(x+s2*48,y-6);c.lineTo(x+s2*40,y-12);c.moveTo(x+s2*48,y-6);c.lineTo(x+s2*38,y-2);c.stroke()});
        text(c,'GEL PUSHED OUT',PX,LT-70,11,.6*g,mono,'center',1.2)}}
    // squeeze out at the rim when the pod goes in
    const sq=ease(t,14.4,15.6);
    if(sq>0&&t<19.5+3){[-1,1].forEach(s=>{c.fillStyle=ink(.3);c.beginPath();c.ellipse(PX+s*150,LT-34,7*sq,5*sq,0,0,7);c.fill()})}
    // the tool: position and kind
    let tool='needle',tx=PX,ty=LT,on=false,carry=false;
    const zz=(u,x0,x1,n)=>lerp(x0,x1,Math.abs((u*n%2)-1));
    if(t<3.2){tx=lerp(X0,X1,sk);ty=LB-2}
    else if(t<4.4){const i=Math.min(WEBS.length-1,Math.floor((t-3.2)/.15));tx=WEBS[i];ty=LT-8}
    else if(t<5.5){tx=t<4.85?PX-150:PX+150;ty=LT-30}
    else if(t<8.5){tx=zz(bed,PX-128,PX+128,6);ty=LT-16*bed}
    else if(t<10.5){const u=(t-8.5)/2,away=[MAG.x+MAG.w/2,-40];tool=u<.5?'needle':'holder';const v=u<.5?ease(u,0,.5):1-ease(u,.5,1);
      const from=u<.5?[PX,LT-16]:[MAG.x+MAG.w/2,MAG.y-60];tx=lerp(from[0],away[0],v);ty=lerp(from[1],away[1]+100,v)}
    else if(t<17.5){tool='holder';const top=[MAG.x+MAG.w/2,MAG.y+MAG.h-8-2*MSP-56],seat=[PX,PT];
      if(t<12){tx=top[0];ty=lerp(MAG.y-60,top[1],ease(t,10.5,11.8))}
      else if(t<12.4){tx=top[0];ty=top[1];on=t>=12.1;carry=on}
      else if(t<15.6){on=true;carry=true;const u=ease(t,12.4,14.2),d=ease(t,14.2,15.6);tx=lerp(top[0],seat[0],u);ty=t<14.2?lerp(top[1],PT-60,u)-80*Math.sin(Math.PI*u):lerp(PT-60,PT,d)}
      else if(t<16.1){tx=PX;ty=PT;on=false}
      else{tx=PX;ty=lerp(PT,PT-130,ease(t,16.1,17.4))}}
    else if(t<19.5){const u=(t-17.5)/2;tool=u<.5?'holder':'needle';const v=u<.5?ease(u,0,.5):1-ease(u,.5,1);
      const from=u<.5?[PX,PT-130]:[PX-170,LT-20];tx=lerp(from[0],MAG.x+MAG.w/2,v);ty=lerp(from[1],60,v)}
    else if(t<26){const u=ease(t,19.5,23.5),w=ease(t,23.5,25.8);
      if(t<23.5){tx=zz(u,PX-168,PX+168,10);ty=lerp(LT-20,PT-18,u)}else{tx=w<.5?lerp(PX-170,WEBS[0],w*2):lerp(PX+170,WEBS[WEBS.length-1],(w-.5)*2);ty=UT}}
    else{tool='none'}
    // the pod in the wall, once placed
    const placed=t>=15.6;
    if(placed)pod(c,PX,PB,1,true);
    if(carry){pod(c,tx,ty+56,1,true)}
    // the cover, printed from the bottom up, and the upper skin outward
    const cov=ease(t,19.5,23.5), us=ease(t,23.5,25.8);
    if(cov>0){const top=lerp(LT,PT-16,cov);c.save();c.beginPath();c.rect(0,top,W,H);c.clip();
      const P=new Path2D();P.moveTo(PX-170,LT);P.lineTo(PX-170,PT+4);P.quadraticCurveTo(PX-170,PT-16,PX-140,PT-16);P.lineTo(PX+140,PT-16);P.quadraticCurveTo(PX+170,PT-16,PX+170,PT+4);P.lineTo(PX+170,LT);P.closePath();
      c.fillStyle=wet>0?FR(.1+.14*wet):ink(.13);c.fill(P);c.save();c.clip(P);c.strokeStyle=ink(.22);c.lineWidth=1;for(let y=LT-5;y>PT-20;y-=5.3){c.beginPath();c.moveTo(PX-172,y);c.lineTo(PX+172,y);c.stroke()}c.restore();
      c.strokeStyle=ink(.8);c.lineWidth=1;c.stroke(P);c.restore();pod(c,PX,PB,.25*cov,true)}
    if(us>0){c.fillStyle=wet>0?FR(.16+.3*wet):ink(.16);c.strokeStyle=ink(.8);c.lineWidth=1;
      const xl=lerp(PX-170,WEBS[0],us),xr=lerp(PX+170,WEBS[WEBS.length-1],us),yb=LT-cell;
      // upper skin: flat while printed, cells bulge when inflated
      const seg=(xa,xb)=>{const P=new Path2D();const pts=[xa,...WEBS.filter(x=>x>xa&&x<xb),xb];P.moveTo(xa,yb);
        for(let i=1;i<pts.length;i++){const m=(pts[i-1]+pts[i])/2;P.quadraticCurveTo(m,yb-26*inflate,pts[i],yb)}
        P.lineTo(xb,yb-10);for(let i=pts.length-1;i>0;i--){const m=(pts[i-1]+pts[i])/2;P.quadraticCurveTo(m,yb-10-26*inflate,pts[i-1],yb-10)}P.closePath();c.fill(P);c.stroke(P)};
      seg(xl,PX-170);seg(PX+170,xr)}
    // cells and links after "birth"
    if(inflate>0){tag(c,'CELL, AIR',1010+320,LT-cell-70,1315,LT-cell/2,inflate);
      const r=ease(t,29.5,31);if(r>0)for(let k=0;k<3;k++){c.strokeStyle=ink(.5*r*(1-((t*0.8+k/3)%1)));c.lineWidth=1;c.beginPath();c.arc(PX-40,PT-16,30+((t*0.8+k/3)%1)*70,-Math.PI*.85,-Math.PI*.15);c.stroke()}}
    // the tool
    if(tool==='needle'){needle(c,tx,ty,1);const pr=(t<5.5)||(t>5.8&&t<8.3)||(t>19.5&&t<25.8);if(pr){c.fillStyle=FR(.95);c.beginPath();c.arc(tx,ty,3.4,0,7);c.fill();c.strokeStyle=FR(.35);c.lineWidth=1;c.beginPath();c.arc(tx,ty,8+3*Math.sin(t*12),0,7);c.stroke()}}else if(tool==='holder')holder(c,tx,ty,1,on);
    // tags
    tag(c,'LOWER SKIN, 1.2 MM',W-30,LB+30,X1-60,LB-5,sk,'right');
    tag(c,'WEB',WEBS[5]-60,LB+30,WEBS[5],LT-4,wb*(1-inflate),'right');
    tag(c,'RIM',PX-260,LT-70,PX-150,LT-24,rim*(1-ease(t,19.5,20.5)),'right');
    tag(c,'FRESH BED',PX+300,LT-70,PX+100,LT-8,bed*(1-ease(t,10.5,11.5)),'left');
    tag(c,'POD',PX+300,PT-70,PX+PH,PT+20,ease(t,15.6,16.2)*(1-ease(t,19.5,20)),'left');
    tag(c,'FLANGE HOLES',PX+300,PT-40,PX+PH-4,PB-4,ease(t,15.8,16.4)*(1-ease(t,19.5,20)),'left');
    tag(c,'CAPPED PORTS, PUMP POD',PX+300,PT-110,PX+94,PB-110,ease(t,16,16.6)*(1-ease(t,27,27.5)),'left');
    tag(c,'COVER',PX-300,PT-40,PX-150,PT+20,ease(t,20,20.6)*(1-ease(t,27,27.5)),'right');
    tag(c,'UPPER SKIN',X0+120,LT-cell-56,X0+80,LT-cell-4,us,'left');
    if(t>=26){text(c,'16 HOURS LATER',W-30,GS+60,11,.6*ease(t,26,26.5),mono,'right',1.2)}
    // caption
    const S=STEPS.find(s=>t>=s[0]&&t<s[1])||STEPS[STEPS.length-1];
    text(c,S[2].toUpperCase(),64,H-104,12,.55,mono,'left',1.6);
    c.save();c.font='26px Georgia';const w=c.measureText(S[3]).width;c.restore();
    text(c,S[3],64,H-68,Math.min(26,26*1470/w),.95,'Georgia');
    if(S[4])text(c,S[4],64,H-36,14,.6);
    c.globalAlpha=1;return S[2]+'. '+S[3]+' '+S[4];
  });
  // play, pause and scrub under the canvas
  const pb=document.getElementById('wplay'),sk=document.getElementById('wseek'),tm=document.getElementById('wtime');
  if(pb&&sk){const lab=s=>Math.floor(s/60)+':'+String(Math.floor(s)%60).padStart(2,'0');sk.max=DUR;
    ctl.onframe=t=>{sk.value=t;if(tm)tm.textContent=lab(t)+' / '+lab(DUR);const p=ctl.playing?'Pause':'Play';if(pb.textContent!==p)pb.textContent=p};
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

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

function loop(canvas,W,H,dur,draw){
  const c=canvas.getContext('2d');let t=0,last=performance.now(),vis=false;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches, fix=new URLSearchParams(location.search).get('dt');if(fix!==null)t=+fix;
  new IntersectionObserver(e=>{vis=e[0].isIntersecting;last=performance.now()}).observe(canvas);
  function size(){const r=Math.min(2,devicePixelRatio||1),w=Math.round(canvas.clientWidth*r);if(w&&canvas.width!==w){canvas.width=w;canvas.height=Math.round(w*H/W)}}
  function tick(now){if(vis||t===0||fix!==null){size();if(fix===null){if(!reduce&&vis)t=Math.max(0,t+(now-last)/1000)%dur;if(reduce)t=dur*.92}last=now;
    c.setTransform(canvas.width/W,0,0,canvas.height/H,0,0);c.fillStyle='#000';c.fillRect(0,0,W,H);const d=draw(c,t);if(d&&canvas.getAttribute('aria-label')!==d)canvas.setAttribute('aria-label',d)}
    else last=now;requestAnimationFrame(tick)}
  requestAnimationFrame(tick);
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

/* 2 · Head and tail: a still from the quilted head simulator (simulator/doublewall, print stage), labels on top */
(function(){
  const cv=document.getElementById('d-body');if(!cv)return;
  const W=1600,H=900,DUR=14,IX=150,IY=175,IS=1300/1908;
  const img=new Image();img.src='body-section.jpg?v=2';
  const P=(x,y)=>[IX+x*IS,IY+y*IS];
  const LB=[ // anchor in the image, label x, top or bottom, title, line
    [[860,230],330,'top','Arm','The only part not in the wall. It prints, and picks up parts.'],
    [[1380,120],760,'top','Quilted double wall','Brain, battery, pump, motor and sensors, sealed between two skins.'],
    [[1760,300],1200,'top','Mouth','The newborn leaves here, inflating on the way.'],
    [[380,380],150,'bottom','Tail','Reproduces. Holds the arm and its tools.'],
    [[985,420],520,'bottom','Docks from behind','Gel face to gel face. It moves on to the next head.'],
    [[1240,690],880,'bottom','The next body','Printed folded flat in the gel, its parts set in first.'],
    [[1560,640],1220,'bottom','Gel','A shallow layer held by the lower part of the head.']];
  loop(cv,W,H,DUR,(c,t)=>{
    const fade=1-ease(t,DUR-.6,DUR);
    const iw=1908*IS,ih=838*IS;
    if(img.complete&&img.naturalWidth){c.drawImage(img,IX,IY,iw,ih);
      // soften the frame so the still sits in the page
      const E=70,edges=[[IX,0,IX+E,0,IX,IY,E,ih],[IX+iw,0,IX+iw-E,0,IX+iw-E,IY,E,ih],[0,IY,0,IY+E,IX,IY,iw,E],[0,IY+ih,0,IY+ih-E,IX,IY+ih-E,iw,E]];
      for(const [x0,y0,x1,y1,rx,ry,rw,rh] of edges){const gr=c.createLinearGradient(x0,y0,x1,y1);gr.addColorStop(0,'#000');gr.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=gr;c.fillRect(rx,ry,rw,rh)}}
    LB.forEach(([an,x,side,h,body],i)=>{
      const a=ease(t,.6+i*.9,1.2+i*.9)*fade;if(a<=0)return;
      const [ax,ay]=P(...an), y=side==='top'?70:IY+838*IS+45;
      c.save();c.globalAlpha=a;
      c.strokeStyle=ink(.45);c.lineWidth=1;c.beginPath();c.moveTo(ax,ay);c.lineTo(ax,side==='top'?y+48:y-22);c.lineTo(x,side==='top'?y+48:y-22);c.stroke();
      c.fillStyle=ink(.95);c.beginPath();c.arc(ax,ay,3.5,0,7);c.fill();c.strokeStyle='#000';c.lineWidth=1.5;c.stroke();
      text(c,h,x,y,16,.95);wrap(c,body,x,y+20,300,13,.6,17);
      c.restore();
    });
    return 'A still of the quilted head simulator: tail with the arm, head with the quilted double wall, gel, the next body printed in it, and the mouth.';
  });
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

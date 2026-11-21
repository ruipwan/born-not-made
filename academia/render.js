(function(){
"use strict";
const items=window.ACADEMIA_REFERENCES||[];
const grid=document.getElementById("grid");
const count=document.getElementById("count");
const empty=document.getElementById("empty");
const esc=(s)=>String(s??"").replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const link=(url,title)=>'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(title)+' <span aria-hidden="true">↗</span></a>';
const safeImage=(url)=>/^https:\/\//.test(url||"")?url:"";
let tier="all",kind="all",query="";
function card(e){
 const src=safeImage(e.image);
 return '<article class="research-card" data-tier="'+esc(e.tier)+'" data-kind="'+esc(e.kind)+'" data-search="'+esc([e.school,e.lab,e.people,e.work,e.focus,e.relation,e.tags.join(" ")].join(" ").toLowerCase())+'">'+
 '<a class="research-image'+(src?"":" image-missing")+'" href="'+esc(e.workUrl)+'" target="_blank" rel="noopener noreferrer" aria-label="Open original research work: '+esc(e.work)+'">'+
 (src?'<img loading="lazy" decoding="async" src="'+esc(src)+'" alt="'+esc(e.work+" — "+e.credit)+'">':"")+
 '<span class="image-placeholder"><span>'+String(e.id).padStart(2,"0")+'</span><b>'+esc(e.school)+'</b><small>'+esc(e.focus)+'</small></span>'+
 '<span class="image-annotation">'+esc(e.work)+' ↗</span></a>'+
 '<div class="card-body"><div class="card-label"><span>'+(e.tier==="top"?"LEADING RESEARCH ENVIRONMENT":"SPECIALIST EXCEPTION")+'</span><span>'+(e.kind==="art"?"ART PRACTICE":e.kind==="robotics"?"ROBOTICS / HRI":"MATERIAL / MAKING")+'</span></div>'+
 '<h2>'+esc(e.school)+'</h2><p class="lab">'+esc(e.lab)+'</p><p class="people">'+esc(e.people)+'</p>'+
 '<p class="focus">'+esc(e.focus)+'</p><p class="why">'+esc(e.relation)+'</p>'+
 '<div class="tags">'+e.tags.map((t)=>'<span>'+esc(t)+'</span>').join("")+'</div>'+
 '<p class="status"><strong>Doctoral pathway</strong>'+esc(e.status)+'</p>'+
 '<div class="links">'+link(e.workUrl,"Work / project")+link(e.researchUrl,"Research")+link(e.phdUrl,"PhD route")+'</div>'+
 '<p class="credit">Image / source: '+esc(e.credit)+'</p></div></article>';
}
grid.innerHTML=items.map(card).join("\n");
const cards=Array.from(grid.children);
const main=document.querySelector("main");
let lastHeight=0;
function reportHeight(){
 if(window.parent===window || !main)return;
 const height=Math.ceil(main.getBoundingClientRect().height);
 if(height<=0 || height===lastHeight)return;
 lastHeight=height;
 try{window.parent.postMessage({bnm:"academia-height",h:height},window.location.origin)}catch(e){}
}
function apply(){
 let n=0;
 cards.forEach((el)=>{
 const visible=(tier==="all"||el.dataset.tier===tier)&&(kind==="all"||el.dataset.kind===kind)&&(!query||el.dataset.search.includes(query));
 el.hidden=!visible;if(visible)n++;
 });
 count.textContent=n+" / "+cards.length+" references";
 empty.classList.toggle("on",!n);
 requestAnimationFrame(reportHeight);
}
function setup(id,attr,update){
 document.querySelectorAll("#"+id+" button").forEach((b)=>{
 b.addEventListener("click",()=>{
 update(b.dataset[attr]);
 document.querySelectorAll("#"+id+" button").forEach((x)=>x.setAttribute("aria-pressed",String(x===b)));
 apply();
 });
 });
}
setup("tierFilters","tier",(x)=>tier=x);
setup("kindFilters","kind",(x)=>kind=x);
document.getElementById("q").addEventListener("input",(e)=>{query=e.target.value.trim().toLowerCase();apply();});
grid.querySelectorAll("img").forEach((img)=>{
 img.addEventListener("load",reportHeight);
 img.addEventListener("error",()=>{img.hidden=true;img.parentElement.classList.add("image-missing");reportHeight();});
 if(img.complete&&img.naturalWidth===0){img.hidden=true;img.parentElement.classList.add("image-missing");}
});
window.addEventListener("load",reportHeight);
window.addEventListener("resize",reportHeight);
if(window.ResizeObserver)new ResizeObserver(reportHeight).observe(main);
apply();
})();

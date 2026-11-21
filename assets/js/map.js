/* Born, Not Made: the map.
   One trunk: a robot gives birth to another.
   One branch per tab leaves the trunk and comes back. Hover a branch to find it, click to open the tab.
   Mount: <div id="bnm-map" data-mode="hero"></div>. Plain SVG, no libraries, no motion. */
(() => {
"use strict";

const NS = "http://www.w3.org/2000/svg";
const ALIAS = { trunk: "work", branches: "ideas", questions: "ideas", early: "prototypes", log: "process" };

// u: where the phrase sits along the trunk, 0 left, 1 right
const TRUNK = [
  { key: "mother", text: "A robot", u: 0.14, main: true },
  { key: "birth", text: "gives birth to", u: 0.46, verb: true },
  { key: "baby", text: "another", u: 0.8, main: true },
];

// u0, u1: where the branch leaves and rejoins the trunk. side 1 above, -1 below. a: height as a share of the half height.
const BRANCHES = [
  { tab: "ideas", label: "Ideas", side: 1, u0: 0.0, u1: 0.46, a: 0.84, shape: "sin" },
  { tab: "culture", label: "Culture", side: -1, u0: 0.14, u1: 0.46, a: 0.5, shape: "cos" },
  { tab: "prototypes", label: "Prototypes", side: 1, u0: 0.27, u1: 0.62, a: 0.52, shape: "cos" },
  { tab: "build", label: "Build", side: -1, u0: 0.30, u1: 0.72, a: 0.88, shape: "sin" },
  { tab: "simulator", label: "Simulator", side: 1, u0: 0.47, u1: 0.8, a: 0.76, shape: "sin" },
  { tab: "society", label: "Society", side: -1, u0: 0.56, u1: 0.86, a: 0.52, shape: "cos" },
  { tab: "process", label: "Process", side: 1, u0: 0.66, u1: 1.0, a: 0.5, shape: "cos" },
  { tab: "voices", label: "Voices", side: -1, u0: 0.8, u1: 1.0, a: 0.82, shape: "sin" },
];

function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function cssVar(n, f) { try { return getComputedStyle(document.documentElement).getPropertyValue(n).trim() || f; } catch (e) { return f; } }
let mctx = null;
function measure(text, font) { if (!mctx) mctx = document.createElement("canvas").getContext("2d"); mctx.font = font; return mctx.measureText(text).width; }
function currentTab() { const h = location.hash.slice(1); return ALIAS[h] || h || "work"; }
const cultureLive = () => !!document.getElementById("culture");

function curvePath(b, x0, x1, yT, A) {
  const N = 120, f = b.shape === "cos" ? (t) => (1 - Math.cos(2 * Math.PI * t)) / 2 : (t) => Math.sin(Math.PI * t);
  let d = "";
  for (let i = 0; i <= N; i++) { const t = i / N; d += (i ? "L" : "M") + (x0 + (x1 - x0) * t).toFixed(1) + " " + (yT - b.side * A * f(t)).toFixed(1); }
  return d;
}

function draw(host, svg) {
  const W = Math.round(host.clientWidth);
  svg.replaceChildren();
  if (!W) return;
  const phone = W < 640, H = phone ? 280 : W < 900 ? 320 : 360;
  host.style.height = H + "px";
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  const yT = Math.round(H / 2) + 0.5, pad = 2, serif = cssVar("--serif", "Georgia, serif");
  const base = phone ? { mother: 15, birth: 13, baby: 15 } : W < 900 ? { mother: 18, birth: 15, baby: 18 } : { mother: 20, birth: 16, baby: 20 };

  // place the phrases, shrinking until they fit
  let P = null;
  for (let scale = 1, it = 0; it < 12; it++, scale *= 0.94) {
    let x = pad;
    P = TRUNK.map((p) => { const size = base[p.key] * scale; return { ...p, size, wd: measure(p.text, (p.verb ? "italic 400 " : p.main ? "500 " : "400 ") + size + "px " + serif) + 2 }; });
    for (const p of P) { p.x = Math.max(pad + p.u * (W - 2 * pad), x + p.wd / 2); x = p.x + p.wd / 2 + (phone ? 16 : 30); }
    const lastP = P[P.length - 1];
    if (lastP.x + lastP.wd / 2 <= W - pad - 8) break;
  }
  const by = Object.fromEntries(P.map((p) => [p.key, p]));
  const anchors = [[0, pad], [0.14, by.mother.x], [0.46, by.birth.x], [0.8, by.baby.x], [1, W - pad]];
  const X = (u) => { for (let i = 1; i < anchors.length; i++) if (u <= anchors[i][0]) { const [u0, a0] = anchors[i - 1], [u1, a1] = anchors[i]; return a0 + ((a1 - a0) * (u - u0)) / (u1 - u0); } return W - pad; };
  const AU = (yT - (phone ? 22 : 28)) * (phone ? 0.8 : 1), labelPx = phone ? 13 : 15;
  const here = currentTab(), live = cultureLive();

  const gBr = el("g", { class: "bnm-branches" }, svg);
  for (const b of BRANCHES) {
    const coming = b.tab === "culture" && !live;
    const x0 = X(b.u0), x1 = X(b.u1), A = b.a * AU, d = curvePath(b, x0, x1, yT, A);
    const g = el("g", { class: "bnm-br" + (coming ? " bnm-coming" : "") + (here === b.tab ? " bnm-here" : ""), "data-tab": b.tab }, gBr);
    el("path", { class: "bnm-line", d }, g);
    if (!coming) el("path", { class: "bnm-hit", d }, g);
    const ay = yT - b.side * A, off = 12;
    const lab = el("text", { class: "bnm-label", x: ((x0 + x1) / 2).toFixed(1), y: (b.side > 0 ? ay - off : ay + off + labelPx * 0.72).toFixed(1), "text-anchor": "middle", "font-size": labelPx }, g);
    lab.textContent = coming ? b.label + " (soon)" : b.label;
    if (!coming) {
      g.addEventListener("click", () => { location.hash = b.tab; });
      g.addEventListener("pointerenter", () => { svg.classList.add("bnm-has-hot"); g.classList.add("bnm-hot"); });
      g.addEventListener("pointerleave", () => { svg.classList.remove("bnm-has-hot"); g.classList.remove("bnm-hot"); });
    }
  }

  const gT = el("g", { class: "bnm-trunk" }, svg);
  el("path", { class: "bnm-trunkline", d: "M" + pad + " " + yT + "H" + (W - pad) }, gT);
  for (const p of P) {   // a plain ground under each phrase, so no line shows through the gaps between words
    el("rect", { class: "bnm-ground", x: (p.x - p.wd / 2 - 8).toFixed(1), y: (yT - p.size * 0.7).toFixed(1), width: (p.wd + 16).toFixed(1), height: (p.size * 1.4).toFixed(1) }, gT);
    const t = el("text", { class: "bnm-phrase" + (p.main ? " bnm-main" : "") + (p.verb ? " bnm-verb" : ""), x: p.x.toFixed(1), y: yT, dy: "0.32em", "text-anchor": "middle", "font-size": p.size.toFixed(2) }, gT);
    t.textContent = p.text;
  }
  gT.addEventListener("click", () => { location.hash = "work"; });
}

function setup(host) {
  if (host.__bnm) return; host.__bnm = 1;
  host.classList.add("bnm-map");
  const svg = el("svg", { class: "bnm-svg", role: "img", focusable: "false",
    "aria-label": "Map of the site. One line: a robot gives birth to another. Branches: " + BRANCHES.map((b) => b.label).join(", ") + "." }, host);
  const nav = document.createElement("nav"); nav.className = "bnm-sr"; nav.setAttribute("aria-label", "Tabs of the site");
  const ul = document.createElement("ul");
  for (const [href, text] of [["#work", "The Work"], ...BRANCHES.map((b) => ["#" + b.tab, b.label])]) {
    const li = document.createElement("li"), a = document.createElement("a"); a.href = href; a.textContent = text; li.appendChild(a); ul.appendChild(li);
  }
  nav.appendChild(ul); host.appendChild(nav);
  let w = 0;
  const redraw = () => { const nw = Math.round(host.clientWidth); if (nw !== w) { w = nw; draw(host, svg); } };
  if ("ResizeObserver" in window) new ResizeObserver(redraw).observe(host); else addEventListener("resize", redraw);
  addEventListener("hashchange", () => { const h = currentTab(); svg.querySelectorAll(".bnm-br").forEach((g) => g.classList.toggle("bnm-here", g.dataset.tab === h)); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => draw(host, svg));
  draw(host, svg);
}

function start() { document.querySelectorAll("#bnm-map, .bnm-map, [data-bnm-map]").forEach(setup); }
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();

/* Born, Not Made: the living map.
   One trunk runs through the work: not a copy, born, not made, born is a relation.
   One branch per tab leaves the trunk and comes back, like sine and cosine waves.
   Words on each branch are read from that tab's own content at load and sized by how often they occur.
   Rings spread from "born is a relation"; the number of voices sets how often a ring is born.

   Mount:  <div id="bnm-map" data-mode="hero"></div>     (top of The Work)
           <div class="bnm-map" data-mode="strip"></div> (footer, every tab)
   Plain SVG and JavaScript, no libraries. Nothing is stored beyond the page session. */
(() => {
"use strict";

const NS = "http://www.w3.org/2000/svg", XL = "http://www.w3.org/1999/xlink";
const SCRIPT = document.currentScript;
const ROOT = (() => { try { return new URL("../../", SCRIPT.src).href; } catch (e) { return new URL("./", location.href).href; } })();
const REPO = "ruipwan/born-not-made";
const API = "https://api.github.com/repos/" + REPO + "/issues?labels=voice&state=open&per_page=100";
const RM = matchMedia("(prefers-reduced-motion: reduce)");
const ALIAS = { trunk: "work", branches: "ideas", questions: "ideas", early: "prototypes", log: "process" };

/* ------------------------------------------------------------------ the trunk */
// u: where the phrase sits along the trunk, 0 at the far left, 1 at the far right.
const TRUNK = [
  { key: "copy", text: "copy", u: 0, faint: true },
  { key: "not", text: "Not a copy", u: 0.15 },
  { key: "born", text: "Born, Not Made", u: 0.45, main: true },
  { key: "rel", text: "Born is a relation", u: 0.78 },
];

/* ------------------------------------------------------------------ the branches
   u0, u1: where the branch leaves and rejoins the trunk. side 1 above, -1 below.
   a: height as a share of the half height. shape: "sin" leaves at an angle, "cos" leaves tangent.
   terms: candidate words chosen from the tab's real content. "shown=pattern/pattern", a trailing *
   matches any ending (pleat* finds pleats, pleated); otherwise a plain s or es is allowed.        */
const BRANCHES = [
  { tab: "ideas", label: "Ideas", side: 1, u0: 0.03, u1: 0.45, a: 0.84, shape: "sin",
    terms: ["womb", "matrix", "mater", "mold=mold/mould", "cyberfeminism=cyberfemin*", "VNS Matrix", "Sadie Plant", "hospitality", "Aristarkhova",
      "matricentric", "mothering", "gestation", "surrogacy", "Mosuo", "matrilineal", "kinship", "kin", "ectogenesis", "Haldane", "Biobag",
      "artificial womb", "labor=labor/labour", "robota", "Čapek=Čapek/Capek", "hysteria", "hystera", "garbha", "子宫", "uterus",
      "weaving", "seahorse*", "budding", "jellyfish", "ammonite", "sanctum", "fathers", "O'Reilly", "Sophie Lewis", "Daedalus", "sacred"] },
  { tab: "culture", label: "Culture", side: -1, u0: 0.15, u1: 0.45, a: 0.5, shape: "cos",
    terms: ["Blade Runner", "begotten", "Nicene Creed", "Frankenstein", "golem", "Pygmalion", "Galatea", "Pinocchio", "Astro Boy",
      "Ghost in the Shell", "Evangelion", "Nüwa=Nüwa/Nuwa/女娲", "Ex Machina", "Lem", "Ted Chiang", "myth*", "anime", "manga",
      "film*", "games", "novel*", "Shelley", "replicant*", "Genesis", "Prometheus", "Talos", "automaton=automat*", "ritual*"] },
  { tab: "prototypes", label: "Prototypes", side: 1, u0: 0.27, u1: 0.62, a: 0.52, shape: "cos",
    terms: ["water muscle", "pump", "tank", "shell", "water jet", "TPU", "bag", "syringe", "XIAO", "battery", "touch loop", "phone",
      "WiFi=wifi/wi-fi", "resin", "foaming filament", "silicone", "gel bath", "swims=swim*", "inflatable", "buoyancy", "floats=float*",
      "LiPo", "rigid", "lid", "slider", "capacitive", "sponge", "thrust", "glass tank", "cavity", "wheels", "sensor"] },
  { tab: "build", label: "Build", side: -1, u0: 0.30, u1: 0.72, a: 0.88, shape: "sin",
    terms: ["gel", "silicone", "bellows", "sleeve", "valve", "DexArm", "magnets=magnet*", "pleats=pleat*", "origami", "Kresling", "Yoshimura",
      "creases=crease*", "Demaine", "pressure", "tether", "canal", "bore", "nozzle", "Carbopol", "Ecoflex", "Dragon Skin", "Sorta-Clear",
      "PDMS", "friction", "cure=cure/cured/curing", "needle", "hoop", "tail", "dock=dock*", "duckbill", "capsule", "seal=seal/seals/sealed",
      "cartridge", "mixer", "resin", "boom", "servo", "ballast", "stopcock", "thrusters=thruster*", "bead", "tolerance"] },
  { tab: "simulator", label: "Simulator", side: 1, u0: 0.47, u1: 0.78, a: 0.76, shape: "sin",
    terms: ["signal", "memory", "G-code=G-code/gcode", "genome", "drift", "inherited=inherit*", "Blender", "kinematics", "layer", "nozzle",
      "agent", "voice", "pressure", "light", "rhythm", "distance", "trace", "tide", "pump", "egg", "amniotic", "umbilical", "canal", "valve",
      "breathes=breath*", "random", "likeness", "viewport", "timeline", "spring", "fluid", "sound", "core"] },
  { tab: "society", label: "Society", side: -1, u0: 0.56, u1: 0.86, a: 0.52, shape: "cos",
    terms: ["water", "relations=relation*", "memory", "inheritance=inherit*", "drift", "gestation", "signal", "generations=generation*",
      "population", "diversity", "energy", "selected=select*", "seed", "trace", "bears=bear/bears", "feeds", "travels=travel*", "scale",
      "conditions", "carrying=carry*", "swells=swell*"] },
  { tab: "process", label: "Process", side: 1, u0: 0.66, u1: 0.99, a: 0.5, shape: "cos",
    terms: ["arm", "gel", "tail", "valve", "SO-ARM101=SO-ARM101/SO-101", "DexArm", "ECO62", "boom", "syringe", "shell", "muscle",
      "docks=dock*", "needle", "lid", "NaOH", "vacuum", "Carbopol", "EpiKure", "crosslinker", "offspring", "origami", "petals=petal*",
      "lobes=lobe*", "door", "render=render*", "film", "NeurIPS", "ALIFE", "hackathon", "test=test/tests/tested", "decision*",
      "idea", "design", "resin", "bubbles=bubble*", "umbilical", "ring", "reversals=reversal*", "options=option*"] },
  { tab: "voices", label: "Voices", side: -1, u0: 0.78, u1: 1.0, a: 0.82, shape: "sin", voices: true },
];

/* stopwords for words taken straight from the voices */
const STOP = new Set(("a about above after again against all also am an and any are aren't as at be because been before being below between both but by " +
  "can can't cannot could couldn't did didn't do does doesn't doing don't down during each even ever every few for from further get gets got had hadn't has " +
  "hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its " +
  "itself just let's like lot lots many may me might more most much must mustn't my myself no nor not now of off on once one ones only or other ought our " +
  "ours ourselves out over own really same shall shan't she she'd she'll she's should shouldn't so some something such than that that's the their theirs " +
  "them themselves then there there's these they they'd they'll they're they've thing things this those though through to too under until up upon us very " +
  "was wasn't way we we'd we'll we're we've were weren't what what's when when's where where's which while who who's whom why why's will with won't would " +
  "wouldn't yet you you'd you'll you're you've your yours yourself yourselves im ive dont doesnt didnt cant wont isnt also still maybe perhaps quite " +
  "的 了 是 在 和 也 就 都 而 及 与 着 或 一个 我 你 他 她 它 我们 你们 他们 她们 这 那 这个 那个 有 没有 不 会 能 要 吗 呢 吧 啊 很 还 又 被 把 让 给 对 从 到 说").split(" "));

/* ------------------------------------------------------------------ helpers */
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function cssVar(n, f) { try { return getComputedStyle(document.documentElement).getPropertyValue(n).trim() || f; } catch (e) { return f; } }
const isWide = (ch) => ch.codePointAt(0) > 0x2e80;
function monoWidth(s, px) { let w = 0; for (const ch of s) w += isWide(ch) ? 1 : 0.6; return w * px; }
let mctx = null;
function measure(text, font) { if (!mctx) mctx = document.createElement("canvas").getContext("2d"); mctx.font = font; return mctx.measureText(text).width; }
function currentTab() { const h = location.hash.slice(1); return ALIAS[h] || h || "work"; }

/* candidate term to a counting pattern */
function compileTerm(spec) {
  const eq = spec.indexOf("=");
  const shown = (eq > 0 ? spec.slice(0, eq) : spec.replace(/\*$/, "")).normalize("NFC");
  const pats = (eq > 0 ? spec.slice(eq + 1) : spec).split("/").map((p) => {
    p = p.normalize("NFC");
    const pre = p.endsWith("*"); if (pre) p = p.slice(0, -1);
    const body = p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "[\\s-]+").replace(/'/g, "['’]");
    if (/[㐀-鿿]/.test(p)) return body;
    return "(?<![\\p{L}\\p{N}])" + body + (pre ? "[\\p{L}\\p{N}]*" : "(?:s|es)?") + "(?![\\p{L}\\p{N}])";
  });
  return { w: shown, re: new RegExp(pats.join("|"), "giu") };
}
function countTerms(text, specs) {
  text = text.normalize("NFC");
  return specs.map((s, i) => { const t = compileTerm(s); const m = text.match(t.re); return { w: t.w, c: m ? m.length : 0, i }; })
    .filter((t) => t.c > 0).sort((a, b) => b.c - a.c || a.i - b.i);
}

/* top words of free text, for the voices */
function topWords(texts) {
  const counts = new Map();
  let order = 0;
  const seg = typeof Intl !== "undefined" && Intl.Segmenter ? new Intl.Segmenter("en", { granularity: "word" }) : null;
  for (let text of texts) {
    text = String(text || "").normalize("NFC").replace(/https?:\/\/\S+/g, " ").replace(/[`*_#>[\]()~|]/g, " ");
    const toks = [];
    if (seg) { for (const s of seg.segment(text)) if (s.isWordLike) toks.push(s.segment); }
    else toks.push(...(text.match(/[\p{L}\p{N}][\p{L}\p{N}'’]*/gu) || []));
    for (let t of toks) {
      t = t.toLowerCase().replace(/’/g, "'").replace(/'s$/, "");
      if (/^\p{N}+$/u.test(t) || STOP.has(t)) continue;
      const cjk = /[㐀-鿿]/.test(t);
      if (cjk ? t.length < 2 : t.length < 3) continue;
      const c = counts.get(t); if (c) c.c++; else counts.set(t, { w: t, c: 1, i: order++ });
    }
  }
  for (const [k, v] of counts) {   // fold a plain plural into its singular when both occur
    const base = k.endsWith("es") && counts.has(k.slice(0, -2)) ? k.slice(0, -2) : k.endsWith("s") && counts.has(k.slice(0, -1)) ? k.slice(0, -1) : null;
    if (base && base !== k) { counts.get(base).c += v.c; counts.delete(k); }
  }
  return [...counts.values()].sort((a, b) => b.c - a.c || a.i - b.i).slice(0, 40);
}

/* ------------------------------------------------------------------ reading the site */
async function getText(path) { try { const r = await fetch(ROOT + path, { cache: "no-cache" }); return r.ok ? await r.text() : null; } catch (e) { return null; } }
async function getJSON(path) { const t = await getText(path); if (t == null) return null; try { return JSON.parse(t); } catch (e) { return null; } }
function proseLiterals(code) {   // plain sentences kept in a page's scripts (labels, notes written by the page)
  const out = [], re = /"((?:[^"\\\n]|\\.){12,400})"|'((?:[^'\\\n]|\\.){12,400})'|`([^`]{12,800})`/g;
  let m;
  while ((m = re.exec(code))) {
    const s = m[1] || m[2] || m[3];
    if (/[{};=<>]|https?:|\$\{|=>/.test(s) || (s.match(/[A-Za-z]{2,}\s/g) || []).length < 3) continue;
    out.push(s);
  }
  return out.join(" ");
}
function htmlText(src) {
  if (!src) return null;
  const doc = new DOMParser().parseFromString(src, "text/html");
  const lits = [];
  doc.querySelectorAll("script").forEach((s) => { if (!s.src) lits.push(proseLiterals(s.textContent)); s.remove(); });
  doc.querySelectorAll("style,noscript,template,header,nav").forEach((s) => s.remove());
  return (doc.body ? doc.body.textContent : "") + " " + lits.join(" ");
}
function jsonText(j) {
  if (j == null) return null;
  const out = [];
  (function walk(x) {
    if (typeof x === "string") { if (!/^(https?:|mailto:|media\/|\.\.?\/|data:)/.test(x)) out.push(x); }
    else if (Array.isArray(x)) x.forEach(walk);
    else if (x && typeof x === "object") for (const k in x) walk(x[k]);
  })(j);
  return out.join(" ");
}
let rootDoc = null;
async function sectionText(id) {
  let sec = document.getElementById(id);
  if (!sec && !document.getElementById("work")) {   // the map is on another page: read the sections from the home page
    rootDoc = rootDoc || getText("index.html").then((t) => (t ? new DOMParser().parseFromString(t, "text/html") : null));
    const d = await rootDoc; sec = d && d.getElementById(id);
  }
  if (!sec) return null;
  const c = sec.cloneNode(true);
  c.querySelectorAll(".bnm-map,#bnm-map,[data-bnm-map],script,style,iframe,video").forEach((n) => n.remove());
  return c.textContent;
}
function voiceWords(v) {
  let w = String(v.words || "");
  if (!w && !v.sketch && v.title) w = String(v.title).replace(/^\s*\[voice\]\s*/i, "");
  return w.replace(/^>[ \t]?.*\n?/, "");   // a first quoted line is the site's own question being answered
}
function issueWords(i) {
  const t = String(i.body || "").replace(/\r\n?/g, "\n");
  const m = /^###[ \t]+Words[ \t]*$/im.exec(t);
  let w = t;
  if (m) { const rest = t.slice(m.index + m[0].length); const n = /^###[ \t]+(Topic|Sketch|How to call you)[ \t]*$/im.exec(rest); w = n ? rest.slice(0, n.index) : rest; }
  w = w.replace(/bnm-sketch-v1:[A-Za-z0-9_-]+/g, " ").replace(/_No response_/g, " ").trim();
  return voiceWords({ words: w, title: i.title, sketch: /bnm-sketch-v1:/.test(t) });
}
const notHidden = (labels) => !(labels || []).some((l) => (typeof l === "string" ? l : l && l.name) === "hidden");
async function loadVoices() {
  const rec = await getJSON("voices/data/voices.json");
  const list = rec && (Array.isArray(rec) ? rec : Array.isArray(rec.voices) ? rec.voices : null);
  const built = rec && (Array.isArray(rec) ? rec.length > 0 : !!rec.generated_at);
  if (list && built) return list.filter((v) => v && !v.hidden).map(voiceWords);
  try {   // the record is not built yet: ask GitHub, as the Voices page does (reuse that page's fresh copy if there is one)
    const c = JSON.parse(localStorage.getItem("bnm-voices-api-v1") || "null");
    if (c && Array.isArray(c.voices) && Date.now() - c.t < 10 * 60 * 1000) return c.voices.filter((v) => v && !v.hidden).map(voiceWords);
  } catch (e) { /* no stored copy */ }
  try {
    const r = await fetch(API, { headers: { Accept: "application/vnd.github+json" } });
    if (!r.ok) return null;
    const j = await r.json();
    return Array.isArray(j) ? j.filter((i) => i && !i.pull_request && notHidden(i.labels)).map(issueWords) : null;
  } catch (e) { return null; }
}
async function loadAll() {
  const join = (parts, need) => { const ok = parts.slice(need).some((p) => p != null); return ok ? parts.filter((p) => p != null).join(" \n ") : null; };
  const [work, ideas, culture, protoHead, early, buildHead, build, comps, phys, simHead, sim, socHead, soc, procHead, log, voices] = await Promise.all([
    sectionText("work"), sectionText("ideas"), sectionText("culture"),
    sectionText("prototypes"), getText("early/index.html").then(htmlText),
    sectionText("build"), getText("build/index.html").then(htmlText), getJSON("build/data/components.json").then(jsonText), getJSON("build/data/physics.json").then(jsonText),
    sectionText("simulator"), getText("simulator/index.html").then(htmlText),
    sectionText("society"), getText("society/index.html").then(htmlText),
    sectionText("process"), getJSON("log/data/log.json").then(jsonText),
    loadVoices(),
  ]);
  const text = {
    work, ideas, culture,
    prototypes: join([protoHead, early], 1),
    build: join([buildHead, build, comps, phys], 1),
    simulator: join([simHead, sim], 1),
    society: join([socHead, soc], 1),
    process: join([procHead, log], 1),
  };
  const terms = {};
  for (const b of BRANCHES) terms[b.tab] = b.voices ? (voices ? topWords(voices) : null) : text[b.tab] ? countTerms(text[b.tab], b.terms) : null;
  const workTerms = work ? countTerms(work, ["mother", "baby", "gel", "water", "womb", "print*", "kinship", "memory", "species", "artificial life",
    "soft robotics", "amniotic", "belly", "origami", "inheritance=inherit*", "umbilical", "reproduction=reproduc*", "relation*"]) : null;
  return { terms, workTerms, voices: voices ? voices.length : 0, voicesOk: !!voices, culture: culture != null };
}
let dataP = null;
const loadOnce = () => dataP || (dataP = loadAll().catch(() => ({ terms: {}, voices: 0, voicesOk: false, culture: !!document.getElementById("culture") })));

/* ------------------------------------------------------------------ geometry */
function curve(b, x0, x1, yT, A) {
  const N = 180, xs = new Float64Array(N + 1), ys = new Float64Array(N + 1), ss = new Float64Array(N + 1);
  const f = b.shape === "cos" ? (t) => (1 - Math.cos(2 * Math.PI * t)) / 2 : (t) => Math.sin(Math.PI * t);
  for (let i = 0; i <= N; i++) {
    const t = i / N; xs[i] = x0 + (x1 - x0) * t; ys[i] = yT - b.side * A * f(t);
    ss[i] = i ? ss[i - 1] + Math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) : 0;
  }
  let d = "M" + xs[0].toFixed(1) + " " + ys[0].toFixed(1);
  for (let i = 1; i <= N; i++) d += "L" + xs[i].toFixed(1) + " " + ys[i].toFixed(1);
  const yAt = (x) => { const t = (x - x0) / (x1 - x0); return t <= 0 || t >= 1 ? yT : yT - b.side * A * f(t); };
  const at = (s) => {   // point at arc length s
    let lo = 0, hi = N; while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (ss[mid] < s) lo = mid; else hi = mid; }
    const k = ss[hi] - ss[lo] ? (s - ss[lo]) / (ss[hi] - ss[lo]) : 0; return [lerp(xs[lo], xs[hi], k), lerp(ys[lo], ys[hi], k)];
  };
  const sAtX = (x) => { const i = clamp(Math.round(((x - x0) / (x1 - x0)) * N), 0, N); return ss[i]; };
  return { xs, ys, ss, L: ss[N], d, yAt, at, sAtX, x0, x1, A };
}

/* ------------------------------------------------------------------ one mount */
const mounts = [];
let uid = 0;

function setup(host) {
  if (host.__bnm) return;
  const m = { el: host, mode: host.dataset.mode === "strip" ? "strip" : "hero", id: "bnm" + uid++, data: null, L: null, w: 0,
    rings: [], since: 0, alpha: 0, conv: [], visible: true };
  host.__bnm = m;
  host.classList.add("bnm-map");
  host.setAttribute("data-mode", m.mode);
  m.svg = el("svg", { class: "bnm-svg", role: "img", focusable: "false" }, host);
  m.list = document.createElement("nav"); m.list.className = "bnm-sr"; m.list.setAttribute("aria-label", "Tabs of the site");
  host.appendChild(m.list);
  mounts.push(m);
  writeList(m);
  if ("ResizeObserver" in window) new ResizeObserver(() => { const w = Math.round(host.clientWidth); if (w && w !== m.w) { layout(m); render(m); } }).observe(host);
  else addEventListener("resize", () => { layout(m); render(m); });
  if ("IntersectionObserver" in window) new IntersectionObserver((es) => { for (const e of es) m.visible = e.isIntersecting; if (m.visible) kick(); }).observe(host);
  layout(m); render(m);
}

function writeList(m) {
  const d = m.data, ul = document.createElement("ul");
  const words = (list, n) => (list && list.length ? ": " + list.slice(0, n).map((t) => t.w).join(", ") : "");
  const li = (href, text) => { const l = document.createElement("li"); if (href) { const a = document.createElement("a"); a.href = href; a.textContent = text; l.appendChild(a); } else l.textContent = text; ul.appendChild(l); };
  li("#work", "The Work: not a copy, born, not made, born is a relation" + (d && d.workTerms && d.workTerms.length ? ". Often: " + d.workTerms.slice(0, 5).map((t) => t.w).join(", ") : ""));
  for (const b of BRANCHES) {
    const coming = b.tab === "culture" && !(d ? d.culture : document.getElementById("culture"));
    if (coming) { li(null, "Culture, coming soon"); continue; }
    let extra = d ? words(d.terms[b.tab], 5) : "";
    if (b.voices && d) extra = ": " + (d.voices === 1 ? "1 voice so far" : d.voices + " voices so far") + (d.terms.voices && d.terms.voices.length ? ", often " + d.terms.voices.slice(0, 4).map((t) => t.w).join(", ") : "");
    li("#" + b.tab, b.label + extra);
  }
  m.list.replaceChildren(ul);
  const shown = BRANCHES.filter((b) => !(b.tab === "culture" && !(d ? d.culture : document.getElementById("culture")))).map((b) => b.label);
  m.svg.setAttribute("aria-label", "A living map of the site. One line runs through the work: not a copy, then born, not made, then born is a relation. " +
    "Branches leave the line and return to it: " + shown.slice(0, -1).join(", ") + " and " + shown[shown.length - 1] + "." +
    (shown.includes("Culture") ? "" : " Culture is coming.") + " Words on each branch come from that tab and grow with how often they appear. Rings spread from born is a relation.");
}

/* layout: everything that depends on width */
function layout(m) {
  const W = Math.round(m.el.clientWidth);
  m.w = W;
  if (!W) { m.L = null; return; }
  const strip = m.mode === "strip", phone = W < 640;
  const H = strip ? 120 : phone ? 300 : W < 900 ? 340 : 380;
  m.el.style.height = H + "px";
  const yT = Math.round(H / 2) + 0.5, pad = phone ? 2 : 6;
  const serif = cssVar("--serif", '"Newsreader", Georgia, serif');
  const base = strip ? (phone ? { copy: 11, not: 12, born: 14.5, rel: 12.5 } : { copy: 13, not: 15, born: 18.5, rel: 16 })
    : phone ? { copy: 12, not: 14, born: 18, rel: 15 } : W < 900 ? { copy: 15, not: 18, born: 25, rel: 20 } : { copy: 17, not: 21, born: 30, rel: 23 };
  const gapMin = phone ? 18 : strip ? 22 : 34;
  let scale = 1, P = null, dropCopy = false;
  for (let it = 0; it < 12; it++) {   // place the phrases in order, push apart, shrink until they fit
    const list = TRUNK.filter((p) => !(dropCopy && p.faint)).map((p) => {
      const size = base[p.key] * scale, font = (p.faint ? "italic 400 " : p.main ? "500 " : "400 ") + size + "px " + serif;
      return { ...p, size, wd: measure(p.text, font) + 2 };
    });
    let x = pad;
    for (const p of list) {
      const target = p.faint ? pad + p.wd / 2 : pad + p.u * (W - 2 * pad);
      p.x = Math.max(target, x + p.wd / 2); x = p.x + p.wd / 2 + gapMin;
    }
    const over = list[list.length - 1].x + list[list.length - 1].wd / 2 - (W - pad - (phone ? 4 : 18));
    if (over <= 0) { P = list; break; }
    if (!dropCopy && (phone || scale <= 0.82)) { dropCopy = true; scale = 1; } else scale *= 0.95;
    P = list;
  }
  const byKey = Object.fromEntries(P.map((p) => [p.key, p]));
  const xL = pad, xR = W - pad;
  const anchors = [[0, xL], [0.15, byKey.not.x], [0.45, byKey.born.x], [0.78, byKey.rel.x], [1, xR]];
  const X = (u) => { for (let i = 1; i < anchors.length; i++) if (u <= anchors[i][0]) { const [u0, a0] = anchors[i - 1], [u1, a1] = anchors[i]; return a0 + ((a1 - a0) * (u - u0)) / (u1 - u0); } return xR; };
  const AU = (yT - (strip ? 15 : phone ? 24 : 30)) * (phone && !strip ? 0.74 : 1);   // phones: branches stacked tighter, so the arcs stay readable
  const br = BRANCHES.map((b) => ({ b, c: curve(b, X(b.u0), X(b.u1), yT, b.a * AU), cross: [] }));
  for (let i = 0; i < br.length; i++) for (let j = i + 1; j < br.length; j++) {   // where two branches on one side cross
    const A = br[i], B = br[j];
    if (A.b.side !== B.b.side) continue;
    const lo = Math.max(A.c.x0, B.c.x0) + 1, hi = Math.min(A.c.x1, B.c.x1) - 1;
    let prev = null;
    for (let x = lo; x <= hi; x += 1.5) {
      const d = A.c.yAt(x) - B.c.yAt(x);
      if (prev != null && Math.sign(d) !== Math.sign(prev) && d !== 0) { A.cross.push(A.c.sAtX(x)); B.cross.push(B.c.sAtX(x)); }
      prev = d;
    }
  }
  const rel = byKey.rel;
  m.L = { W, H, yT, strip, phone, P, byKey, br, X, xL, xR,
    rc: [rel.x, yT], r0: 6, rv: strip ? 11 : phone ? 9 : 15, rmax: strip ? W * 0.42 : phone ? W * 1.05 : Math.min(W * 0.78, 1000), rop: strip ? 0.15 : 0.18,
    fs: phone ? [10, 12.5] : W < 900 ? [9.5, 13] : [10, 14.5], v: phone ? 6 : 8.5, minOff: phone ? 17 : 30, F: phone ? 22 : 40,
    budget: phone ? 12 : 24, slope: Math.tan(((phone ? 50 : 40) * Math.PI) / 180), labelPx: strip ? (phone ? 8.5 : 9.5) : phone ? 9 : 10 };
}

/* render: rebuild the SVG for the current layout and data */
function render(m) {
  const L = m.L, svg = m.svg;
  for (const c of m.conv) for (const w of c.words) w.el.remove();
  m.conv = []; m.rings = [];
  svg.replaceChildren();
  if (!L) return;
  svg.setAttribute("viewBox", "0 0 " + L.W + " " + L.H);
  svg.setAttribute("width", L.W); svg.setAttribute("height", L.H);
  const id = m.id, d = m.data;
  const defs = el("defs", null, svg);
  // rings fade out softly toward the edges instead of being cut by them
  const fade = el("radialGradient", { id: id + "-rf", cx: 0.5, cy: 0.5, r: 0.5 }, defs);
  [[0, 1], [0.7, 1], [1, 0]].forEach(([o, op]) => el("stop", { offset: o, "stop-color": "#fff", "stop-opacity": op }, fade));
  const mask = el("mask", { id: id + "-rm", maskUnits: "userSpaceOnUse", x: 0, y: 0, width: L.W, height: L.H }, defs);
  el("rect", { x: 0, y: 0, width: L.W, height: L.H, fill: "url(#" + id + "-rf)" }, mask);
  m.gRings = el("g", { class: "bnm-rings", "aria-hidden": "true", mask: "url(#" + id + "-rm)" }, svg);
  const gBr = el("g", { class: "bnm-branches" }, svg);
  const gTrunk = el("g", { class: "bnm-trunk" }, svg);
  const here = currentTab();
  const cultureLive = d ? d.culture : !!document.getElementById("culture");

  /* branches */
  m.br = []; m.labels = [];
  for (const R of L.br) {
    const b = R.b, coming = b.tab === "culture" && !cultureLive;
    const g = el("g", { class: "bnm-br" + (coming ? " bnm-coming" : "") + (here === b.tab ? " bnm-here" : ""), "data-tab": b.tab }, gBr);
    const pid = id + "-" + b.tab;
    el("path", { id: pid, class: "bnm-line", d: R.c.d }, g);
    if (!coming) el("path", { class: "bnm-hit", d: R.c.d }, g);
    const words = el("g", { class: "bnm-words" }, g);
    // the label sits just outside the top of the arc
    const ax = (R.c.x0 + R.c.x1) / 2, ay = L.yT - b.side * R.c.A, off = L.strip ? 7 : 15;
    const lab = el("text", { class: "bnm-label", x: ax.toFixed(1), y: (b.side > 0 ? ay - off : ay + off + L.labelPx * 0.72).toFixed(1), "text-anchor": "middle", "font-size": L.labelPx }, g);
    lab.textContent = b.label;
    if (coming) { const t = el("tspan", { class: "bnm-soon", dx: "0.6em" }, lab); t.textContent = "soon"; }
    const lw = ((b.label.length + (coming ? 7.6 : 0)) * 0.74 * L.labelPx) / 2, ly = +lab.getAttribute("y");
    m.labels.push({ tab: b.tab, cx: ax, cy: ly - L.labelPx * 0.36, hw: lw + 3, hh: L.labelPx * 0.5 + 3 });
    if (!coming) {
      g.addEventListener("click", () => { location.hash = b.tab; });
      g.addEventListener("pointerenter", () => { svg.classList.add("bnm-has-hot"); g.classList.add("bnm-hot"); });
      g.addEventListener("pointerleave", () => { svg.classList.remove("bnm-has-hot"); g.classList.remove("bnm-hot"); });
    }
    m.br.push({ R, g, words, pid, coming });
  }

  /* trunk: a line from copy to the far edge, the phrases sitting on it */
  const P = L.P, first = P[0], last = P[P.length - 1];
  const xs = first.faint ? first.x + first.wd / 2 + 4 : L.xL;
  const gid = id + "-tg", notP = L.byKey.not;
  const grad = el("linearGradient", { id: gid, gradientUnits: "userSpaceOnUse", x1: xs, y1: L.yT, x2: L.W, y2: L.yT }, defs);
  const off = (x) => clamp((x - xs) / (L.W - xs), 0, 1).toFixed(4);
  [[0, 0.1], [off(notP.x - notP.wd / 2), 1], [off(last.x + last.wd / 2 + 40), 1], [1, 0.12]].forEach(([o, op]) => el("stop", { offset: o, "stop-color": "var(--gel, #2f6fa8)", "stop-opacity": op }, grad));
  el("path", { class: "bnm-trunkline", d: "M" + xs.toFixed(1) + " " + L.yT + "H" + L.W, stroke: "url(#" + gid + ")" }, gTrunk);
  el("path", { class: "bnm-hit", d: "M" + xs.toFixed(1) + " " + L.yT + "H" + L.W }, gTrunk);
  for (const p of P) {
    const t = el("text", { class: "bnm-phrase" + (p.faint ? " bnm-faint" : "") + (p.main ? " bnm-main" : ""), x: p.x.toFixed(1), y: L.yT, dy: "0.32em", "text-anchor": "middle", "font-size": p.size.toFixed(2) }, gTrunk);
    t.textContent = p.text;
  }
  gTrunk.addEventListener("click", () => { location.hash = "work"; });
  if (here === "work" && L.strip) gTrunk.classList.add("bnm-here");

  /* rings already spreading, so the first frame is not empty */
  const iv = ringInterval(m);
  for (let age = 3; L.r0 + L.rv * age < L.rmax; age += iv) m.rings.push({ age, el: null });
  m.since = 0;

  if (d && !L.strip) fillWords(m);
  step(m, 0);
}

function ringInterval(m) {
  const n = m.data ? m.data.voices : 0;
  return n > 0 ? clamp(9 / (1 + 0.85 * Math.log(1 + n)), 2.2, 9) : 9;
}

/* words: one slow conveyor per branch */
function fillWords(m) {
  const L = m.L, d = m.data;
  m.on = new Set();
  const live = [];
  for (const B of m.br) {
    if (B.coming) continue;
    const terms = d.terms[B.R.b.tab];
    const c = B.R.c, n = c.ss.length - 1;
    const ok = (i) => { const j = Math.min(n, i + 1), k = Math.max(0, i - 1); return Math.abs(c.ys[i] - L.yT) >= L.minOff && Math.abs((c.ys[j] - c.ys[k]) / (c.xs[j] - c.xs[k])) <= L.slope; };
    let ia = 0, ib = n;
    while (ia < ib && !ok(ia)) ia++;
    while (ib > ia && !ok(ib)) ib--;
    const sa = c.ss[ia], sb = c.ss[ib];
    if (B.R.b.voices && (!terms || !terms.length)) {   // no voices yet: a quiet invitation under the label instead of words
      const b = B.R.b, lab = B.g.querySelector(".bnm-label"), px = L.fs[0] + 2.5, text = "leave a voice";
      const wd = measure(text, "italic 400 " + px + "px " + cssVar("--serif", "Georgia, serif"));
      const ax = clamp((c.x0 + c.x1) / 2, L.xL + wd / 2 + 2, L.xR - wd / 2 - 2), ly = +lab.getAttribute("y");
      const t = el("text", { class: "bnm-w bnm-invite", x: ax.toFixed(1), y: (b.side < 0 ? ly + px + 5 : ly - L.labelPx - 6).toFixed(1), "text-anchor": "middle", "font-size": px.toFixed(1) }, B.words);
      t.textContent = text;
      m.conv.push({ still: t, words: [] });
      continue;
    }
    if (sb - sa < 50 || !terms || !terms.length) continue;
    live.push({ B, terms, sa, sb, len: sb - sa });
  }
  // how many words each branch shows: by the room it has, 3 to 7 (fewer on phones), within one budget
  const total = live.reduce((s, x) => s + x.len, 0) || 1;
  for (const x of live) x.k = L.phone ? clamp(Math.round(x.len / 95), 1, 2) : clamp(Math.round((x.len / total) * L.budget), 3, 7);
  let sum = live.reduce((s, x) => s + x.k, 0);
  while (sum > L.budget) { const big = live.filter((x) => x.k > (L.phone ? 1 : 3)).sort((a, b) => b.k - a.k)[0]; if (!big) break; big.k--; sum--; }
  for (const x of live) {
    const top = x.terms[0].c, den = Math.log(Math.max(top, 6));
    const terms = x.terms.map((t, i) => {
      const r = t.c > 1 ? clamp(Math.log(t.c) / den, 0, 1) : 0, size = lerp(L.fs[0], L.fs[1], r);
      const weight = 1 + Math.log(t.c);
      return { w: t.w, key: t.w.toLowerCase(), c: t.c, size, op: 0.52 + 0.43 * r, wd: monoWidth(t.w, size) + 4, weight, pass: 0.5 / weight + i * 1e-6 };
    });
    const conv = { B: x.B, terms, on: m.on, words: [], sa: x.sa, sb: x.sb, F: Math.min(L.F, x.len / 4), v: L.v, cross: x.B.R.cross };
    // the first picks fill the window, centred; then the stream keeps their spacing
    const firsts = [];
    for (let i = 0; i < x.k; i++) { const t = peek(conv); if (!t) break; take(conv, t); firsts.push(t); }
    const widths = firsts.reduce((s, t) => s + t.wd, 0);
    conv.gap = clamp((x.len - conv.F - widths) / Math.max(1, firsts.length), 22, 220);
    let span = widths + conv.gap * (firsts.length - 1);
    while (firsts.length > 1 && span > x.len - conv.F * 1.2) { const t = firsts.pop(); conv.on.delete(t.key); t.pass -= 1 / t.weight; span = firsts.reduce((s, q) => s + q.wd, 0) + conv.gap * (firsts.length - 1); }
    const row = [];   // from the back of the window to the front: ... 4, 2, 1, 3, 5 ...
    firsts.forEach((t, i) => { if (i % 2) row.unshift(t); else row.push(t); });
    const pos = []; let acc = 0;
    for (const t of row) { pos.push(acc + t.wd / 2); acc += t.wd + conv.gap; }
    const lo = x.sa + conv.F * 0.6, hi = x.sb - conv.F * 0.6, total = acc - conv.gap;
    const shift = clamp((x.sa + x.sb) / 2 - pos[row.indexOf(firsts[0])], lo, hi - total);
    for (let i = row.length - 1; i >= 0; i--) spawn(m, conv, row[i], shift + pos[i]);
    m.conv.push(conv);
  }
  m.alpha = RM.matches ? 1 : m.alpha;
}
function peek(conv) { let best = null; for (const t of conv.terms) if (!conv.on.has(t.key) && (!best || t.pass < best.pass)) best = t; return best; }
function take(conv, t) { conv.on.add(t.key); t.pass += 1 / t.weight; }
function spawn(m, conv, t, s) {
  // a halo copy under the ink copy: on a curve each glyph is painted on its own, so a stroke on the ink would cover its neighbour
  const B = conv.B, g = el("g", { class: "bnm-wg", opacity: 0 }, B.words), tps = [];
  for (const cls of ["bnm-halo", "bnm-w"]) {
    const text = el("text", { class: cls, dy: "0.34em", "text-anchor": "middle", "font-size": t.size.toFixed(2) }, g);
    if (cls === "bnm-w") text.setAttribute("data-count", t.c);
    const tp = el("textPath", { href: "#" + B.pid, startOffset: s.toFixed(2) }, text);
    tp.setAttributeNS(XL, "xlink:href", "#" + B.pid);
    tp.textContent = t.w;
    tps.push(tp);
  }
  conv.words.push({ t, s, el: g, tps });   // words[0] leads; the newest is last
}

/* ------------------------------------------------------------------ motion */
function step(m, dt) {
  const L = m.L; if (!L) return;
  if (m.data) m.alpha = Math.min(1, m.alpha + dt / 1.4);
  if (RM.matches) m.alpha = m.data ? 1 : 0;
  // rings
  m.since += dt;
  const iv = ringInterval(m);
  if (dt && m.since >= iv) { m.since = 0; m.rings.push({ age: 0, el: null }); }
  const keep = [];
  for (const r of m.rings) {
    r.age += dt;
    const rad = L.r0 + L.rv * r.age;
    if (rad > L.rmax) { if (r.el) r.el.remove(); continue; }
    if (!r.el) r.el = el("circle", { class: "bnm-ring", cx: L.rc[0].toFixed(1), cy: L.rc[1] }, m.gRings);
    const k = 1 - rad / L.rmax;
    r.el.setAttribute("r", rad.toFixed(2));
    r.el.setAttribute("opacity", (L.rop * Math.pow(k, 1.6) * Math.min(1, r.age / 2)).toFixed(3));
    keep.push(r);
  }
  m.rings = keep;
  // words
  for (const c of m.conv) {
    if (c.still) { c.still.setAttribute("fill-opacity", (0.62 * m.alpha).toFixed(3)); continue; }
    for (const w of c.words) w.s += c.v * dt;
    while (c.words.length && c.words[0].s > c.sb + 1) { const w = c.words.shift(); w.el.remove(); c.on.delete(w.t.key); }
    if (dt) {
      const tail = c.words[c.words.length - 1], t = peek(c);
      if (t) {
        const s = tail ? tail.s - tail.t.wd / 2 - c.gap - t.wd / 2 : c.sa;
        if (s >= c.sa - 1) { take(c, t); spawn(m, c, t, Math.min(s, c.sa)); }
      }
    }
    for (const w of c.words) {
      let o = w.t.op * m.alpha * sstep(c.sa, c.sa + c.F, w.s) * (1 - sstep(c.sb - c.F, c.sb, w.s));
      for (const x of c.cross) { const dd = Math.abs(w.s - x); o *= sstep(w.t.wd / 2 + 2, w.t.wd / 2 + 30, dd); }
      if (o > 0.01) {   // and where the word would pass under another branch's label
        const [px, py] = c.B.R.c.at(w.s);
        for (const lb of m.labels) {
          if (lb.tab === c.B.R.b.tab) continue;
          const dd = Math.hypot(Math.max(0, Math.abs(px - lb.cx) - lb.hw), Math.max(0, Math.abs(py - lb.cy) - lb.hh));
          o *= sstep(0, 18, dd - w.t.wd / 2);
        }
      }
      const so = w.s.toFixed(2); w.tps[0].setAttribute("startOffset", so); w.tps[1].setAttribute("startOffset", so);
      w.el.setAttribute("opacity", o.toFixed(3));
    }
  }
}
let raf = 0, last = 0;
function frame(t) {
  raf = 0;
  const dt = last ? Math.min(0.1, (t - last) / 1000) : 0; last = t;
  let any = false;
  for (const m of mounts) if (m.L && m.visible && m.el.offsetParent !== null) { step(m, dt); any = true; }
  if (any && !RM.matches && !document.hidden) raf = requestAnimationFrame(frame); else last = 0;
}
function kick() { if (!raf && !RM.matches) raf = requestAnimationFrame(frame); }

/* ------------------------------------------------------------------ start */
function start() {
  document.querySelectorAll("#bnm-map, .bnm-map, [data-bnm-map]").forEach(setup);
  if (!mounts.length) return;
  kick();
  addEventListener("hashchange", () => {
    const h = currentTab();
    for (const m of mounts) {
      if (m.br) for (const B of m.br) B.g.classList.toggle("bnm-here", B.R.b.tab === h);
      const tr = m.svg.querySelector(".bnm-trunk"); if (tr) tr.classList.toggle("bnm-here", h === "work" && m.mode === "strip");
    }
    kick();
  });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) kick(); });
  RM.addEventListener && RM.addEventListener("change", () => { for (const m of mounts) { render(m); } kick(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { for (const m of mounts) { layout(m); render(m); } });
  const go = () => loadOnce().then((d) => { for (const m of mounts) { m.data = d; writeList(m); render(m); } kick(); });
  if ("requestIdleCallback" in window) requestIdleCallback(go, { timeout: 1200 }); else setTimeout(go, 200);
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();

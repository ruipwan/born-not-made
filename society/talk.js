/* Society, the dialogue model. No model is called: every line is composed here from the speaker's own state.

   After "Raised by many" (Ruipeng Wang, Cognitive Agents 2026), where every body is one agent that knows only who it is,
   what it remembers and where it is now, talks in turns with whoever is near, and at a full window compacts and bears.
   Kept from that work: an agent's knowledge is only its own readings and what it was told; a body in words (its traits
   named); talk in turns between two that meet, with the relation named; a store that fills with talk and, once full,
   is compacted at a birth; what is let go is dealt to the newborn as traces, with one note; everything from one seed.
   Changed: no language model. A line is a template filled from a fact, and a fact changes what the listener knows.

   A fact: { u: its own number, o: the number of the first reading it copies, k: "light" | "flow" | "crowd" | "body" |
   "fade" | "trace", p: place 0..8, v: value, t: seconds, src: who first read it, hops: times passed on, ... } */
(function (root) {
"use strict";
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const TRAITS = ["speed", "sense", "light", "memory", "endurance"];
const PLACES = ["the north west corner", "the north side", "the north east corner", "the west side", "the middle", "the east side", "the south west corner", "the south side", "the south east corner"];
// "in the middle", "in the north west corner", "on the east side"
const AT = PLACES.map((p) => (/side$/.test(p) ? "on " : "in ") + p);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const fmt = (t) => { const m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ":" + String(s).padStart(2, "0"); };
const pct = (e) => Math.round(clamp(e, 0, 1) * 100) + " percent";
const numWord = (n) => ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][n] || String(n);
function RNG(seed) { let a = seed >>> 0; return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const hash = (s) => { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
// one of several wordings, fixed by what is said and who says it, so the same fact from the same body reads the same
const pick = (list, salt) => list[hash(salt) % list.length];
let UID = 1;
const fact = (o) => { const f = Object.assign({ u: UID++, hops: 0 }, o); if (f.o === undefined) f.o = f.u; return f; };
const copyOf = (f) => Object.assign({}, f, { u: UID++, hops: f.hops + 1 });

/* ---------- values in words ---------- */
const lightWord = (v) => v < 0.18 ? "dark" : v < 0.45 ? "dim" : v < 0.75 ? "fair" : "bright";
const flowWord = (v) => v < 0.15 ? "still" : v < 0.45 ? "slow" : v < 0.75 ? "pulling" : "hard";
const crowdWord = (n) => n < 1 ? "empty" : n < 3 ? "quiet" : n < 5 ? "busy" : "crowded";
const wordOf = (f) => f.k === "light" ? lightWord(f.v) : f.k === "flow" ? flowWord(f.v) : crowdWord(f.v);
const band = (f) => f.k === "light" ? (f.v < 0.18 ? 0 : f.v < 0.45 ? 1 : f.v < 0.75 ? 2 : 3) : f.k === "flow" ? (f.v < 0.15 ? 0 : f.v < 0.45 ? 1 : f.v < 0.75 ? 2 : 3) : (f.v < 1 ? 0 : f.v < 3 ? 1 : f.v < 5 ? 2 : 3);
// a body in words, as "Raised by many" names a body's genes
const TRAIT_WORDS = { speed: ["slow and wide", "steady", "quick", "narrow and fast"], sense: ["short in reach", "of middling reach", "long in reach", "feeling far"], light: ["without a lamp", "with a faint lamp", "with a lamp", "with a strong lamp"],
  memory: ["holding few traces", "holding some traces", "holding many traces", "holding a long record"], endurance: ["quick to drain", "of middling charge", "slow to drain", "lasting"] };
const traitWord = (k, v) => TRAIT_WORDS[k][v < 0.25 ? 0 : v < 0.5 ? 1 : v < 0.75 ? 2 : 3];
function bodyText(D) { const o = TRAITS.map((k) => [k, D[k]]).sort((a, b) => b[1] - a[1]); return traitWord(o[0][0], o[0][1]) + ", " + traitWord(o[1][0], o[1][1]) + ", " + traitWord(o[4][0], o[4][1]); }

/* ---------- a fact in words ---------- */
function obsText(f, salt, third) {
  const p = PLACES[f.p], P = cap(p), at = AT[f.p], s = salt + ":" + f.o;
  if (f.k === "light") { const b = band(f);
    let t = b === 0 ? pick([`No light ${at}.`, `${P} is dark.`, `The lamps over ${p} are low.`], s) : b === 1 ? pick([`Light is thin ${at}.`, `Only a little light ${at}.`], s)
      : b === 2 ? pick([`Fair light ${at}.`, `${P} has some light.`], s) : pick([`Light is strong ${at}.`, `${P} is bright.`, `Good light ${at}.`], s);
    if (f.hops === 0 && f.e !== undefined && ((b === 0 && f.e < 0.5) || (b === 3 && f.e > 0.5))) t += b === 0 ? ` Charge fell to ${pct(f.e)}.` : ` Charge rose to ${pct(f.e)}.`;
    return t; }
  if (f.k === "flow") { const b = band(f);
    return b === 0 ? pick([`The water is still ${at}.`, `No stream ${at}.`], s) : b === 1 ? pick([`A slow stream ${at}.`, `The water moves a little ${at}.`], s)
      : b === 2 ? pick([`The stream pulls ${at}.`, `${P} pulls sideways.`], s) : pick([`The stream runs hard ${at}.`, `Hard water ${at}.`], s); }
  if (f.k === "crowd") { const n = Math.round(f.v);
    return n < 1 ? pick([`${P} is empty.`, `No other body ${at}.`], s) : n === 1 ? `One other body ${at}.` : n < 5 ? pick([`${cap(numWord(n))} bodies share ${p}.`, `${cap(numWord(n))} bodies ${at}.`], s) : `${P} is crowded, ${numWord(n)} bodies. Little light for each.`; }
  if (f.k === "fade") return `#${f.who} faded ${at}. ${FADE_WHY[f.why] || FADE_WHY.old}`;
  if (f.k === "trace") return `A trace from generation ${f.g}: ${f.txt}`;
  if (f.k === "body") return bodyLine(f, salt, third || f.hops > 0);
  return "";
}
const FADE_WHY = { dark: "Charge ran out in the dark.", flow: "The stream took the charge.", crowd: "Too many shared the light.", old: "The body was old." };
// how a body fared: which trait fell short (sg 1) or held (sg 0), with the number that shows it
function bodyLine(f, salt, third) {
  const p = PLACES[f.p], at = AT[f.p], s = salt + ":" + f.o, me = third ? "#" + f.src : "this body", Me = third ? "#" + f.src : "This body";
  if (f.sg > 0) switch (f.ax) {
    case "speed": return pick([`${Me} is too slow for the stream ${at}. Carried ${numWord(clamp(f.n, 1, 10))} ${f.n === 1 ? "time" : "times"}.`, `The stream ${at} turned ${me} round. Too wide, too slow.`], s);
    case "sense": return pick([`${Me} searched ${Math.round(f.n)} seconds for light and does not feel far.`, `Light was near ${p} and ${me} passed by. Short reach.`], s);
    case "light": return pick([`${Me} lost the way in the dark ${at}. No lamp in ${me}.`, `In the dark ${at} ${me} feels nothing.`], s);
    case "memory": return pick([`${Me} forgot the way to ${p}. Too few traces fit.`, `The way to ${p} dropped out. ${Me} holds too little.`], s);
    default: return pick([`Charge is at ${pct(f.e)}. ${Me} drains fast.`, `Charge does not last between pools. ${Me} is down to ${pct(f.e)}.`], s); }
  switch (f.ax) {
    case "speed": return pick([`The narrow shape of ${me} cuts the water well.`, `${Me} swims well. Charge at ${pct(f.e)}.`], s);
    case "sense": return pick([`${Me} feels light from far off.`, `${Me} found light at once. The reach is long enough.`], s);
    case "light": return pick([`The lamp in ${me} shows the way in the dark.`, `${Me} keeps the way by lamp. Charge at ${pct(f.e)}.`], s);
    case "memory": return pick([`${Me} still holds every way to light.`, `Nothing lost yet. The record fits in ${me}.`], s);
    default: return pick([`Charge at ${pct(f.e)} after ${fmt(f.n)}. ${Me} lasts.`, `${Me} holds. Charge at ${pct(f.e)}.`], s); }
}
const REQUEST = { speed: "Make the next body narrower and faster.", sense: "Give the next body a longer reach.", light: "Put a lamp in the next body.", memory: "Give the next body more room for traces.", endurance: "Make the next body slower to drain." };
const GAIN = { speed: "narrower and faster", sense: "longer in reach", light: "brighter", memory: "roomier for traces", endurance: "slower to drain" };
const LOSS = { speed: "wider", sense: "shorter in reach", light: "dimmer", memory: "lighter in traces", endurance: "smaller" };
// a trace: a fact cut down to a few words, as a memory handed on
const traceText = (f) => f.k === "light" || f.k === "flow" || f.k === "crowd" ? `${PLACES[f.p]} was ${wordOf(f)} at ${fmt(f.t)}.` : f.k === "fade" ? `#${f.who} faded ${AT[f.p]} at ${fmt(f.t)}.` : f.k === "body" ? (f.sg > 0 ? `a body fell short in ${f.ax === "endurance" ? "charge" : f.ax} at ${fmt(f.t)}.` : `a body held well at ${fmt(f.t)}.`) : f.txt;

/* ---------- the store of a tailed one ---------- */
function Store() { return { lines: [], info: 0, topics: new Set(), speakers: new Set(), since: 0, total: 0, gist: [] }; }
// take a fact in. Returns what it was to the store: new, changed, known; and how much it added.
function take(S, f, from, t) {
  let kind = "new", prev = null, add = 1, first = false;
  if (S.lines.some((l) => l.o === f.o)) { prev = S.lines.find((l) => l.o === f.o); return { kind: "known", prev, add: 0, first }; }
  if (f.k === "light" || f.k === "flow" || f.k === "crowd") {
    first = !S.lines.some((l) => l.p === f.p && (l.k === "light" || l.k === "flow" || l.k === "crowd"));
    prev = S.lines.filter((l) => l.k === f.k && l.p === f.p).sort((a, b) => b.t - a.t)[0] || null;
    if (prev && prev.t > f.t) return { kind: "known", prev, add: 0.05, first };
    if (prev) { if (band(prev) !== band(f) && Math.abs(prev.v - f.v) > (f.k === "crowd" ? 1.5 : 0.22)) kind = "changed"; else if (f.t - prev.t > 50) { kind = "new"; add = 0.5; } else { kind = "known"; add = 0.15; }
      if (kind !== "known") S.lines.splice(S.lines.indexOf(prev), 1); }
  } else if (f.k === "body") { prev = S.lines.find((l) => l.k === "body" && l.src === f.src && l.ax === f.ax && f.t - l.t < 45); if (prev) { kind = "known"; add = 0.1; } }
  else if (f.k === "trace") { prev = S.lines.find((l) => l.k === "trace" && l.txt === f.txt); if (prev) { kind = "known"; add = 0.05; } else add = 0.6; }
  if (f.hops > 0) add *= 0.7;
  if (kind !== "known") { S.lines.push(Object.assign({}, f, { got: t, from })); if (S.lines.length > 18) S.lines.shift(); S.topics.add(f.k); }
  if (from !== null && from !== undefined) S.speakers.add(from);
  S.info += add; S.total += add;
  return { kind, prev, add, first };
}
// enough, and of enough kinds, from enough speakers. A tailed one with no one to ask starts from its own place alone.
function ready(S, need, alone) { return alone ? S.info >= Math.min(need, 3) && S.topics.size >= 2 : S.info >= need && S.topics.size >= 3 && S.speakers.size >= 2; }
const fresh = (l, t) => Math.exp(-(t - l.t) / 150);
// what the store says the next body should be: a pull on each trait, 0 none to 1 strong
function pressures(S, t) {
  const P = { speed: 0, sense: 0, light: 0, memory: 0, endurance: 0 }, W = { speed: 0.6, sense: 0.6, light: 0.6, memory: 0.6, endurance: 0.6 };
  const add = (k, v, w) => { P[k] += v * w; W[k] += w; };
  for (const l of S.lines) { const w = fresh(l, t);
    if (l.k === "flow") add("speed", clamp((l.v - 0.2) / 0.6, 0, 1), w);
    else if (l.k === "light") { add("light", clamp((0.5 - l.v) / 0.4, 0, 1), w); add("sense", clamp((0.45 - l.v) / 0.45, 0, 1), 0.6 * w); }
    else if (l.k === "crowd") add("endurance", clamp((l.v - 2) / 4, 0, 1), 0.8 * w);
    else if (l.k === "body") add(l.ax, l.sg > 0 ? 1 : 0, 2.2 * w);
    else if (l.k === "fade") { if (l.why === "old") continue; const ax = l.why === "dark" ? "light" : l.why === "flow" ? "speed" : "endurance"; add(ax, 1, 2.6 * w); if (l.why === "dark") add("sense", 0.8, 1.2 * w); }
    else if (l.k === "trace") add("memory", 0.55, 0.5 * w); }
  for (const k of TRAITS) P[k] = P[k] / W[k];
  return P;
}
// the next design. The store names a target: the one budget of traits shared out in proportion to the pulls. The line's last design moves
// part of the way there, with a little chance. All traits share the budget, so no body is best at everything.
const BUDGET = 2.3;
function compose(D, P, mut, rnd) {
  const N = {}; let sum = 0; for (const k of TRAITS) sum += P[k] + 0.1;
  for (const k of TRAITS) { const target = clamp(BUDGET * (P[k] + 0.1) / sum, 0.04, 1), g = (rnd() + rnd() + rnd() - 1.5) * 2; N[k] = clamp(D[k] + 0.55 * (target - D[k]) + mut * g, 0.04, 1); }
  sum = 0; for (const k of TRAITS) sum += N[k]; if (sum > BUDGET) for (const k of TRAITS) N[k] = clamp(N[k] * BUDGET / sum, 0.04, 1);
  return N;
}
function describe(D0, D1) {
  const d = TRAITS.map((k) => [k, D1[k] - D0[k]]).sort((a, b) => b[1] - a[1]), up = d.filter((x) => x[1] > 0.05).slice(0, 2).map((x) => GAIN[x[0]]), dn = d[d.length - 1];
  if (!up.length) return dn[1] < -0.08 ? `${LOSS[dn[0]]}, otherwise like the last` : "much like the last";
  return up.join(", ") + (dn[1] < -0.1 ? `, and ${LOSS[dn[0]]}` : "");
}
// at a birth the store is compacted: a short gist stays, the rest is dealt to the newborn as traces, with one note
function note(S, t) {
  const L = S.lines.filter((l) => l.k === "light").sort((a, b) => b.v * fresh(b, t) - a.v * fresh(a, t))[0], F = S.lines.filter((l) => l.k === "flow" && l.v > 0.5).sort((a, b) => b.v - a.v)[0], Dk = S.lines.filter((l) => l.k === "light" && l.v < 0.2).sort((a, b) => b.t - a.t)[0];
  const out = [], facts = [];
  if (L && L.v > 0.45) { out.push(`Light is ${AT[L.p]}.`); facts.push(L); }
  if (F) { out.push(`Stay out of the stream ${AT[F.p]}.`); facts.push(F); }
  else if (Dk && (!L || Dk.p !== L.p)) { out.push(`${cap(PLACES[Dk.p])} is dark.`); facts.push(Dk); }
  if (!out.length) out.push("Little is known. Read the water and come back.");
  return { text: out.join(" "), facts };
}
function deal(S, n, salt) { const pool = S.lines.filter((l) => l.k !== "trace"), out = []; if (!pool.length) return out;
  const start = hash(salt) % pool.length; for (let i = 0; i < Math.min(n, pool.length); i++) out.push(pool[(start + i * 2) % pool.length]); return [...new Set(out)]; }
function compact(S, t) { const keep = S.lines.slice().sort((a, b) => (b.k === "light" || b.k === "flow" ? 1 : 0) * fresh(b, t) - (a.k === "light" || a.k === "flow" ? 1 : 0) * fresh(a, t)).slice(0, 5);
  S.gist = keep.map(traceText); S.lines = keep; S.info = 0; S.topics = new Set(); S.speakers = new Set(); S.since = t; }

/* ---------- memory of a body without a tail ---------- */
function remember(a, f) {
  if (a.mem.some((m) => m.o === f.o)) return false;
  if (f.k === "light" || f.k === "flow" || f.k === "crowd") { const i = a.mem.findIndex((m) => m.k === f.k && m.p === f.p); if (i >= 0) { if (a.mem[i].t >= f.t) return false; a.mem.splice(i, 1); } }
  a.mem.push(f);
  while (a.mem.length > a.memCap) { // the oldest goes; a dropped way to light is felt later
    let j = 0; for (let i = 1; i < a.mem.length; i++) if (a.mem[i].t < a.mem[j].t) j = i; const d = a.mem.splice(j, 1)[0]; a.forgot = (a.forgot || 0) + 1; if (d.k === "light" && d.v > 0.6) a.lostWay = d.p; }
  return true;
}
// how much a fact is worth saying: its own readings first, then the strong and the new
const weight = (f, t) => (f.hops === 0 ? 1 : 0.55) * (f.k === "body" || f.k === "fade" ? 1.2 : f.k === "trace" ? 0.5 : 0.6 + Math.abs(band(f) - 1.5) / 3) * Math.exp(-(t - f.t) / 120);
function untold(a, to, t, filter) { const told = a.told.get(to.id) || new Set(); let best = null, bw = 0; for (const f of a.mem) { if (told.has(f.o) || (filter && !filter(f))) continue; if (f.src === to.id) continue; const w = weight(f, t); if (w > bw) { bw = w; best = f; } } return best; }
const mark = (a, to, f) => { let s = a.told.get(to.id); if (!s) a.told.set(to.id, (s = new Set())); s.add(f.o); };
// how the body fares, read off its own state: the trait that fell short most, or the one that held
function selfReport(a, t, p) {
  const c = [["speed", a.carried >= 2 ? a.carried / 2 : 0, a.carried], ["sense", a.searched > 25 ? a.searched / 30 : 0, a.searched], ["light", a.lostDark > 0 ? 1 + a.lostDark : 0, a.lostDark], ["memory", a.lostN > 0 ? 0.8 + a.lostN / 2 : 0, a.lostN], ["endurance", a.E / a.cap < 0.35 ? 1.2 : 0, 0]].sort((x, y) => y[1] - x[1]);
  if (c[0][1] > 0) return fact({ k: "body", ax: c[0][0], sg: 1, n: c[0][2], e: a.E / a.cap, p: c[0][0] === "memory" && a.lostWay !== undefined ? a.lostWay : a.hardP !== undefined && c[0][0] !== "endurance" ? a.hardP : p, t, src: a.id });
  const best = TRAITS.slice().sort((x, y) => a.D[y] - a.D[x])[0];
  return fact({ k: "body", ax: a.E / a.cap > 0.6 && t - a.born > 60 ? "endurance" : best, sg: 0, n: t - a.born, e: a.E / a.cap, p, t, src: a.id });
}
const relation = (a, b) => a.tailed && b.tailed ? "tailed" : b.tailed ? (a.line === b.id ? "bearer" : "other bearer") : a.tailed ? (b.line === a.id ? "offspring" : "of another line") : a.line === b.line ? (a.gen === b.gen ? "same generation" : "same line") : "another line";
const hail = (a, b) => { const r = relation(a, b);
  return r === "bearer" ? `#${b.id}.` : r === "other bearer" ? `#${b.id}. #${a.id} here, of #${a.line}'s line.` : r === "same generation" ? `#${b.id}, same generation.` : r === "same line" ? `#${b.id}, generation ${b.gen} of this line.` : r === "another line" ? `#${b.id}, of #${b.line}'s line.` : `#${b.id}.`; };

/* ---------- a conversation: two agents, a few turns. Each turn one says one thing, and the saying changes the listener ---------- */
function Convo(a, b, t) { return { a, b, n: 0, t0: t, next: a, plan: null, done: false, said: [] }; }
// world: { t, place(agent) -> place index, need, alone(tailed) -> bool, brightest(agent) -> fact or null, unknown(tailed) -> place index or -1 }
function turn(C, W) {
  const sp = C.next, li = sp === C.a ? C.b : C.a, t = W.t, salt = sp.id + ":" + li.id + ":" + C.n; let text = "", kind = "say", f = null;
  const end = () => { C.done = true; };
  const tellTo = (who, ff) => { mark(sp, who, ff); if (who.tailed) return take(who.store, ff.hops === 0 && ff.src === sp.id ? ff : copyOf(ff), sp.id, t); remember(who, copyOf(ff)); mark(who, sp, ff); return null; };
  if (!sp.tailed && li.tailed) {          // a body reports to a tailed one
    if (C.n === 0) { f = untold(sp, li, t); if (f) { C.res = tellTo(li, f); text = hail(sp, li) + " " + (f.hops ? `Word from #${f.src}: ` : "") + obsText(f, salt); } else { text = hail(sp, li) + " Nothing new to tell."; C.res = null; } kind = "report"; }
    else if (C.n === 2) { if (C.asked) { f = selfReport(sp, t, W.place(sp)); remember(sp, f); C.res = tellTo(li, f); text = obsText(f, salt) + (f.sg > 0 ? " " + REQUEST[f.ax] : ""); sp.carried = 0; sp.searched = 0; sp.lostDark = 0; sp.forgot = 0; sp.lostN = 0; kind = "body"; }
      else { f = untold(sp, li, t); if (f) { C.res = tellTo(li, f); text = (f.hops ? `Word from #${f.src}: ` : "") + obsText(f, salt); kind = "report"; } else { f = selfReport(sp, t, W.place(sp)); remember(sp, f); C.res = tellTo(li, f); text = obsText(f, salt) + (f.sg > 0 ? " " + REQUEST[f.ax] : ""); sp.carried = 0; sp.searched = 0; sp.lostDark = 0; sp.forgot = 0; sp.lostN = 0; kind = "body"; } } }
    else if (C.n === 4) { if (sp.E / sp.cap < 0.5) { text = pick(["Where is light now?", "Charge is low. Where is light?"], salt); C.q = "light"; kind = "ask"; } else if (C.order !== undefined) { text = pick(["Going.", `Going to ${PLACES[C.order]}.`], salt); sp.goalP = C.order; sp.goalWhy = "sent"; end(); } else { text = "Going back out."; end(); } }
    else { text = C.order !== undefined ? `Going to ${PLACES[C.order]}.` : "Going."; if (C.order !== undefined) { sp.goalP = C.order; sp.goalWhy = "sent"; } end(); }
  } else if (sp.tailed && !li.tailed) {   // the tailed one answers
    const S = sp.store, r = C.res, left = Math.max(0, Math.ceil(W.need - S.info));
    if (C.q === "light") { const b = W.brightest(sp); C.q = null;
      if (b) { text = b.src === sp.id ? `Light holds here ${AT[b.p]}.` : `Light holds ${AT[b.p]}, by word of #${b.src} at ${fmt(b.t)}.`; remember(li, copyOf(b)); li.goalP = b.p; li.goalWhy = "light"; } else text = "No word of light yet.";
      kind = "answer"; end(); }
    else { const lf = C.lastF;
      if (!r) text = pick(["Then stay near and feed.", "Nothing kept."], salt);
      else if (r.kind === "known") text = r.prev && r.prev.from !== undefined && r.prev.from !== null && r.prev.from !== li.id ? `Known. #${r.prev.from} brought the same.` : pick(["Known. The store has that line.", "The store has that line."], salt);
      else if (r.kind === "changed") text = `Changed, then. ${cap(PLACES[lf.p])} was ${wordOf(r.prev)} at ${fmt(r.prev.t)}.`;
      else if (lf && lf.k === "body") text = lf.sg > 0 ? pick(["Kept for the next body.", "Kept. The next body will answer that."], salt) : pick(["Kept. That shape stays.", "Good. That shape stays."], salt);
      else if (lf && lf.k === "fade") text = "Kept. The next body will answer that.";
      else text = r.first ? `Kept. First word of ${PLACES[lf.p]}.` : pick(["Kept.", `Kept, line ${S.lines.length}.`], salt);
      kind = "ack";
      if (C.n === 1) { if (!sp.busy && left > 0 && r && r.kind !== "known") text += left === 1 ? " One more and the next generation starts." : ""; text += " " + pick(["How does the body fare?", "How does that shape hold?"], salt); C.asked = true; }
      else if (C.n === 3) { const u = W.unknown(sp); if (li.E / li.cap >= 0.5 && u >= 0) { text += " " + (S.lines.some((l) => l.p === u && l.k !== "trace") ? `The last word of ${PLACES[u]} is old. Read ${PLACES[u]} again.` : `No word of ${PLACES[u]} yet. Go and read ${PLACES[u]}.`); C.order = u; kind = "send"; } } }
  } else if (!sp.tailed && !li.tailed) {  // two bodies pass word to each other
    if (C.q === "light") { C.q = null; const b = sp.mem.filter((m) => m.k === "light" && m.v > 0.5).sort((x, y) => y.v * Math.exp(-(t - y.t) / 150) - x.v * Math.exp(-(t - x.t) / 150))[0];
      if (b) { text = b.hops ? `Light ${AT[b.p]}, by word of #${b.src} at ${fmt(b.t)}.` : `Light ${AT[b.p]} at ${fmt(b.t)}.`; remember(li, copyOf(b)); mark(sp, li, b); li.goalP = b.p; li.goalWhy = "light"; } else text = "No word of light here either."; kind = "answer"; end(); }
    else { f = untold(sp, li, t);
      if (C.n >= 2 && sp.E / sp.cap < 0.45 && !C.askedL) { text = pick(["Where is light now?", "Charge is low. Where is light?"], salt); C.q = "light"; C.askedL = true; kind = "ask"; }
      else if (f) { tellTo(li, f); text = (C.n === 0 ? hail(sp, li) + " " : "") + (f.hops ? `Word from #${f.src}: ` : "") + obsText(f, salt); kind = "report"; if (C.n >= 3) end(); }
      else { text = C.n === 0 ? hail(sp, li) + " Nothing new to tell." : pick(["Nothing more.", "That is all here."], salt); if (C.n >= 1) end(); } }
  } else {                                 // two tailed ones: each gives the other the strongest line of its store
    f = sp.store.lines.filter((l) => l.k !== "trace" && !(sp.told.get(li.id) || new Set()).has(l.o)).sort((x, y) => weight(y, t) - weight(x, t))[0];
    if (f) { mark(sp, li, f); const r = take(li.store, copyOf(f), sp.id, t); text = (C.n === 0 ? `#${li.id}. ` : "") + (f.src !== sp.id ? `From #${f.src}: ` : "Read here: ") + obsText(f, salt, true); kind = "report"; C.res = r; }
    else text = (C.n === 0 ? `#${li.id}. ` : "") + "Nothing new on this side.";
    if (C.n >= 1) end();
  }
  C.lastF = f; C.n++; C.next = li; C.said.push({ from: sp.id, to: li.id, text, kind, t });
  if (C.n >= 7) C.done = true;
  return { from: sp, to: li, text, kind, fact: f };
}

const API = { TRAITS, PLACES, AT, RNG, hash, pick, fact, copyOf, fmt, cap, lightWord, flowWord, crowdWord, wordOf, band, traitWord, bodyText, obsText, bodyLine, traceText, Store, take, ready, pressures, compose, describe, note, deal, compact, remember, untold, mark, selfReport, relation, hail, Convo, turn, GAIN, REQUEST, FADE_WHY };
if (typeof module !== "undefined" && module.exports) module.exports = API; else root.TALK = API;
})(typeof window !== "undefined" ? window : globalThis);

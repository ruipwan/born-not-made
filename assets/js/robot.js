/* One robot body, drawn as an outline: a soft spindle, each printed to its own shape from a seed. Nothing else. */
window.bnmRobot = function (seed) {
  let a = (Math.abs(Math.round(seed)) * 7 + 3) >>> 0;
  const r = () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const p = 0.45 + 0.25 * r(), bulge = (r() - 0.5) * 0.7, waist = r() < 0.3 ? 0.05 + 0.06 * r() : 0, lobe = 0.015 + 0.02 * r(), k = 2 + Math.floor(r() * 2), ph = r() * 6.283;
  const B = 31, N = 90, top = [], bot = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, uu = Math.min(1, Math.max(0, u - bulge * u * (1 - u) * 2));
    const e = Math.pow(Math.max(0, 1 - Math.pow(2 * uu - 1, 2)), p) * (1 - waist * Math.exp(-Math.pow((u - 0.5) / 0.13, 2))) * (1 + lobe * Math.cos(k * 3.1416 * u + ph));
    top.push((2 + 96 * u).toFixed(1) + " " + (33 - B * e).toFixed(1)); bot.push((2 + 96 * u).toFixed(1) + " " + (33 + B * e).toFixed(1));
  }
  const NS = "http://www.w3.org/2000/svg", svg = document.createElementNS(NS, "svg"), path = document.createElementNS(NS, "path");
  svg.setAttribute("viewBox", "0 0 100 66"); svg.setAttribute("preserveAspectRatio", "none"); svg.setAttribute("class", "bot"); svg.setAttribute("aria-hidden", "true");
  path.setAttribute("class", "shell"); path.setAttribute("d", "M" + top.join("L") + "L" + bot.reverse().join("L") + "Z"); svg.appendChild(path);
  return svg;
};

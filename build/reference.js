/* Inspect the archived Stage 2 finite element run. */
async function renderReference() {
  const panel = document.getElementById("referenceTrace");
  const record = await getJSON("../simulator/old_/stage2/birth_fe.json");
  if (!record) {
    panel.textContent = "The reference trace could not load. Reload to try again.";
    return;
  }
  const series = record.series, times = series.t;
  const slider = panel.querySelector("input"), timeLabel = panel.querySelector("output");
  const chart = panel.querySelector("svg"), ns = "http://www.w3.org/2000/svg";
  const left = 55, right = 748, top = 12, bottom = 163;
  const x = t => left + (right - left) * t / record.t_end_s;
  const y = p => bottom - (bottom - top) * (p + 250) / 1750;
  function element(name, attrs, content) {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    if (content !== undefined) node.textContent = content;
    chart.append(node);
    return node;
  }
  for (const p of [0, 500, 1000, 1500]) {
    element("line", {x1:left, x2:right, y1:y(p), y2:y(p), stroke:"#48515b", "stroke-width":0.8});
    element("text", {x:left-10, y:y(p)+5, "text-anchor":"end"}, (p/1000).toFixed(1));
  }
  for (const t of [0, 100, 200, 300, 400]) element("text", {x:x(t), y:189, "text-anchor":"middle"}, t+" s");
  for (const [channel, color] of [["p_b","#e6bc83"],["p_w","#94c9ee"]]) {
    const points = times.map((t,i) => x(t).toFixed(2)+","+y(series[channel][i]).toFixed(2)).join(" ");
    element("polyline", {points, fill:"none", stroke:color, "stroke-width":1.8, "stroke-linejoin":"round"});
  }
  const cursor = element("line", {y1:top, y2:bottom, stroke:"#f5f3ed", "stroke-width":1.3});
  slider.max = Math.ceil(record.t_end_s * 100) / 100;
  function inspect(time) {
    const t = Math.max(0, Math.min(record.t_end_s,time));
    slider.value = t.toFixed(2);
    timeLabel.value = t.toFixed(2) + " s";
    cursor.setAttribute("x1", x(t)); cursor.setAttribute("x2", x(t));
    const value = key => BirthTrace.at(times, series[key], t);
    panel.querySelector("[data-womb]").textContent = (value("p_w")/1000).toFixed(3)+" kPa";
    panel.querySelector("[data-baby]").textContent = (value("p_b")/1000).toFixed(3)+" kPa";
    panel.querySelector("[data-tail]").textContent = (value("s_tail")*1000).toFixed(1)+" mm";
    panel.querySelector("[data-slips]").textContent = record.slip_t.filter(event => event <= t).length+" / "+record.n_slips;
  }
  slider.addEventListener("input", () => inspect(Number(slider.value)));
  const events = {start:times[0],growth:record.t_growth_s,slip:record.slip_t[0],exit:record.t_born_s};
  for (const button of panel.querySelectorAll("button[data-event]")) {
    button.addEventListener("click", () => inspect(events[button.dataset.event]));
    button.disabled = false;
  }
  slider.disabled = false;
  inspect(record.t_born_s);
}

export const windowLength = 360;
const filmDuration = 79.15;
const recordedGap = 48.9;

export const visits = [
  { label: 'Seated bay', start: 25, end: 75 },
  { label: 'Silent, no-touch visit', start: 46, end: 82 },
  { label: 'Three visitors together', start: 108, end: 158 },
  { label: 'Arrival during service', start: 205, end: 305 },
];

export function rehearse({ demo, reset, pause, cleared, filmPhase }) {
  const tank = [];
  function add(start, end, state) {
    if (end > start) tank.push({ start, end, state });
  }
  function staffed(start, end) {
    for (let t = start; t < end; t += demo + reset) {
      add(t, Math.min(t + demo, end), 'staffed');
      add(Math.min(t + demo, end), Math.min(t + demo + reset, end), 'reset');
    }
  }
  if (pause === null) {
    staffed(0, windowLength);
  } else {
    staffed(0, pause);
    const back = cleared === null ? windowLength : cleared;
    add(pause, back, 'paused');
    staffed(back, windowLength);
  }
  const gaps = [];
  const first = ((recordedGap - filmPhase) % filmDuration + filmDuration) % filmDuration;
  for (let t = first; t < windowLength; t += filmDuration) gaps.push(t);
  return { tank, gaps };
}

export function encounter(visit, { tank, gaps }) {
  const durations = { staffed: 0, reset: 0, paused: 0 };
  for (const span of tank) {
    durations[span.state] += Math.max(0, Math.min(visit.end, span.end) - Math.max(visit.start, span.start));
  }
  return {
    ...durations,
    film: gaps.filter(t => t >= visit.start && t < visit.end),
  };
}

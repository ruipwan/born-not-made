const embedded = window !== window.parent;
document.documentElement.classList.toggle('embedded', embedded);

const film = document.querySelector('#film-player');
const hero = document.querySelector('#film');
const screen = document.querySelector('#screen');
const watch = document.querySelector('#watch');
const closeFilm = document.querySelector('#close-film');
watch.addEventListener('click', event => {
  event.preventDefault();
  stopStudy();
  screen.hidden = false;
  hero.classList.add('is-playing');
  film.focus({ preventScroll: true });
  film.play().catch(() => { /* Native controls remain available. */ });
});
function closePlayer() {
  film.pause();
  hero.classList.remove('is-playing');
  screen.hidden = true;
  watch.focus({ preventScroll: true });
}
closeFilm.addEventListener('click', closePlayer);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !screen.hidden && !document.fullscreenElement) closePlayer();
});

const canvas = document.querySelector('#material-canvas');
const scrub = document.querySelector('#scrub');
const motion = document.querySelector('#motion');
const clock = document.querySelector('#time');
const caption = document.querySelector('#phase-caption');
const phaseButtons = [...document.querySelectorAll('[data-phase]')];
const phases = [
  { start: 0, mark: .075, text: 'The motor and electronics enter as one assembled core. They are already there when the parent begins to print.' },
  { start: .17, mark: .37, text: 'The white arm traces a narrow path in the gel. Each new line leaves a fold around the electronic core.' },
  { start: .52, mark: .68, text: 'The tool stays coupled. Gel is drawn back and air enters the shell. The narrow folds begin to open while the wider ones remain creased.' },
  { start: .74, mark: .91, text: 'The two rear lids slide apart. The arm carries the child through, then withdraws outside the hull. For the first time the water takes the whole load.' }
];
let progress = phases[0].mark;
let scene;
let relation;
let previousPhase = -1;
let active = true;
let frame = 0;
let lastTime = 0;
let materialInView = false;
let relationInView = false;
const duration = 34;

function updateStudy(next) {
  progress = Math.min(1, Math.max(0, next));
  scene?.setProgress(progress);
  scrub.value = String(Math.round(progress * 1000));
  clock.textContent = '00:' + String(Math.floor(duration * progress)).padStart(2, '0');
  const index = phases.findLastIndex(phase => progress >= phase.start);
  if (index !== previousPhase) {
    previousPhase = index;
    phaseButtons.forEach((button, position) => button.setAttribute('aria-pressed', String(position === index)));
    caption.textContent = phases[index].text;
  }
  scrub.setAttribute('aria-valuetext', phaseButtons[index].textContent + ', ' + clock.textContent);
}
function stopStudy() {
  cancelAnimationFrame(frame);
  frame = 0;
  lastTime = 0;
  motion.innerHTML = '<span aria-hidden="true">▶</span> Play';
  motion.setAttribute('aria-label', 'Play material study');
}
function advance(timestamp) {
  if (lastTime) updateStudy(progress + (timestamp - lastTime) / (duration * 1000));
  lastTime = timestamp;
  if (progress >= 1) { stopStudy(); return; }
  frame = requestAnimationFrame(advance);
}
motion.addEventListener('click', () => {
  if (frame) { stopStudy(); return; }
  if (progress >= .999) updateStudy(0);
  film.pause();
  motion.innerHTML = '<span aria-hidden="true">Ⅱ</span> Pause';
  motion.setAttribute('aria-label', 'Pause material study');
  frame = requestAnimationFrame(advance);
});
scrub.addEventListener('input', () => { stopStudy(); updateStudy(Number(scrub.value) / 1000); });
phaseButtons.forEach((button, index) => button.addEventListener('click', () => {
  stopStudy();
  updateStudy(phases[index].mark);
}));
updateStudy(progress);

function syncPlayback() {
  const visible = active && !document.hidden;
  if (!visible) film.pause();
  if (!visible || !materialInView) stopStudy();
  relation?.setActive(visible && relationInView);
}
if (embedded) {
  window.addEventListener('message', event => {
    if (event.origin !== location.origin || event.source !== window.parent ||
        event.data?.bnm !== 'artistic-visible') return;
    active = event.data.active === true;
    syncPlayback();
  });
  const reportSize = () => {
    window.parent.postMessage({ bnm: 'artistic-height', height: Math.ceil(document.body.getBoundingClientRect().height) }, location.origin);
  };
  new ResizeObserver(reportSize).observe(document.body);
  reportSize();
}
document.addEventListener('visibilitychange', syncPlayback);
window.addEventListener('pagehide', () => { film.pause(); stopStudy(); relation?.setActive(false); });
window.addEventListener('pageshow', syncPlayback);
const observers = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (entry.target === canvas) materialInView = entry.isIntersecting;
    else relationInView = entry.isIntersecting;
  }
  syncPlayback();
});
observers.observe(canvas);
const score = document.querySelector('#relation-score');
observers.observe(score);
import('./material.js').then(({ createMaterialScene }) => {
  scene = createMaterialScene(canvas);
  scene.setProgress(progress);
}).catch(() => {
  canvas.replaceWith(Object.assign(document.createElement('p'), {textContent: 'The cutaway could not load. Select the stages below to read the sequence.'}));
  motion.disabled = true;
  scrub.disabled = true;
});
import('./relation.js').then(({ mountRelation }) => {
  relation = mountRelation(score);
  syncPlayback();
}).catch(() => {
  score.textContent = 'The relation study could not load. Its references on social learning are in the field notes below.';
});

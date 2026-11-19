/* Born, Not Made: sections fade and rise 12 px as they enter the viewport, once. Nothing else moves. */
(function () {
  var d = document.documentElement;
  var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (still || !("IntersectionObserver" in window)) return;
  var SEL = ".hero, .tabhead, .intro, .block, .cu-group, .kept, .record, .end, .open, .conv-q, .conv-list, .controls, .layout, .meet, .composer, .glance, .doc section, .conv-f";
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
  function scan(root) {
    (root || document).querySelectorAll(SEL).forEach(function (el) {
      if (el.__rv) return; el.__rv = 1; el.classList.add("rv"); io.observe(el);
    });
  }
  d.classList.add("org-js");
  scan();
  /* content that arrives later (conversations, voices, log) */
  var q = 0; new MutationObserver(function () { if (q) return; q = requestAnimationFrame(function () { q = 0; scan(); }); }).observe(document.body, { childList: true, subtree: true });
  /* safety: never leave anything hidden if the observer is slow */
  setTimeout(function () { document.querySelectorAll(".rv:not(.in)").forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) el.classList.add("in"); }); }, 1800);
})();

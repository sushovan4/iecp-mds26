// Opener: the scale r is driven by clicks. Invisible step fragments
//   <span class="fragment anim-step" data-frame="k" data-r="0.7"></span>
// set the target radius of frame k (the k-th svg.opener-anim); each change
// tweens the balls, the cursor, the drawn-in profile and the readouts.
// Review hook: ?opener_r=0.45 freezes every frame at that r.
(function () {
  var TWEEN = 650;
  function setup(svg, k) {
    return {
      svg: svg, k: k, r: 0, from: 0, to: 0, t0: 0,
      sc: +svg.dataset.scale, rmax: +svg.dataset.rmax, x0: +svg.dataset.x0, x1: +svg.dataset.x1,
      dchi: svg.dataset.dchi.split(',').map(Number),
      balls: svg.querySelectorAll('circle.ball'),
      prog: svg.querySelector('rect.prog'),
      cursor: svg.querySelector('line.cursor'),
      cdot: svg.querySelector('circle.cdot'),
      rlabel: svg.querySelector('text.rlabel'),
      dlabel: svg.querySelector('text.dlabel')
    };
  }
  function draw(a, r) {
    a.r = r;
    var rp = (r * a.sc).toFixed(2);
    for (var i = 0; i < a.balls.length; i++) a.balls[i].setAttribute('r', rp);
    var x = a.x0 + (a.x1 - a.x0) * r / a.rmax;
    a.prog.setAttribute('width', Math.max(0, x - a.x0 + 2).toFixed(1));
    a.cursor.setAttribute('x1', x.toFixed(1)); a.cursor.setAttribute('x2', x.toFixed(1));
    var idx = Math.min(a.dchi.length - 1, Math.round(r / a.rmax * (a.dchi.length - 1)));
    var v = a.dchi[idx], c = a.cdot.dataset;
    a.cdot.setAttribute('cx', x.toFixed(1));
    a.cdot.setAttribute('cy', (+c.cy0 - (v - +c.vmin) * +c.cyscale).toFixed(1));
    a.rlabel.textContent = 'r = ' + r.toFixed(2);
    a.dlabel.textContent = 'Δχ = ' + v;
  }
  function start() {
    var svgs = document.querySelectorAll('svg.opener-anim');
    if (!svgs.length) return;
    var anims = Array.prototype.map.call(svgs, function (s, i) { return setup(s, i + 1); });
    var slide = svgs[0].closest('section');
    var fixed = new URLSearchParams(location.search).get('opener_r');
    if (fixed !== null) { anims.forEach(function (a) { draw(a, Math.min(+fixed, a.rmax)); }); return; }
    function target(a) {
      var r = 0;
      slide.querySelectorAll('.anim-step[data-frame="' + a.k + '"]').forEach(function (s) {
        if (s.classList.contains('visible')) r = Math.max(r, +s.dataset.r);
      });
      return r;
    }
    function retarget(instant) {
      var now = performance.now();
      anims.forEach(function (a) {
        var t = target(a);
        if (instant) { a.to = t; draw(a, t); return; }
        if (t !== a.to) { a.from = a.r; a.to = t; a.t0 = now; }
      });
    }
    function tick(now) {
      anims.forEach(function (a) {
        if (a.r === a.to) return;
        var u = Math.min(1, (now - a.t0) / TWEEN), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
        draw(a, u >= 1 ? a.to : a.from + (a.to - a.from) * e);
      });
      requestAnimationFrame(tick);
    }
    Reveal.on('fragmentshown', function () { retarget(false); });
    Reveal.on('fragmenthidden', function () { retarget(false); });
    Reveal.on('slidechanged', function (ev) { if (ev.currentSlide === slide) retarget(true); });
    anims.forEach(function (a) { draw(a, 0); });
    retarget(true);
    requestAnimationFrame(tick);
  }
  function boot() { if (Reveal.isReady()) start(); else Reveal.on('ready', start); }
  if (window.Reveal && Reveal.on) boot(); else window.addEventListener('load', boot);
})();

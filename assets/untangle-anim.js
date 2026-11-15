// Disentanglement cartoon: clicks step the layer. Invisible step fragments
//   <span class="fragment untangle-step" data-layer="3"></span>
// set the target layer; the spiral points tween (unwind, then pull apart), and the
// small quotient chart fills in to the layer reached.
// Review hook: ?untangle_layer=4 freezes the cartoon at that layer.
(function () {
  var TWEEN = 1100;
  function start() {
    var svg = document.querySelector('svg.untangle-anim');
    if (!svg) return;
    var slide = svg.closest('section');
    var U = svg.dataset.u.split(',').map(Number), D = svg.dataset.d.split(',').map(Number);
    var Q = svg.dataset.q.split(','), turns = +svg.dataset.turns;
    var sc = +svg.dataset.sc, cx = +svg.dataset.cx, cy = +svg.dataset.cy;
    var pts = Array.prototype.map.call(svg.querySelectorAll('circle.pt'), function (e) {
      return { e: e, c: +e.dataset.c, t: +e.dataset.t, jx: +e.dataset.jx, jy: +e.dataset.jy };
    });
    var dots = svg.querySelectorAll('.qdot, .qseg');
    var arms = svg.querySelectorAll('path.arm'), TT = [];
    for (var a = 0; a < 160; a++) TT.push(0.12 + 0.88 * a / 159);
    var llabel = svg.querySelector('text.llabel'), qlabel = svg.querySelector('text.qlabel');
    var L = 1, from = 1, to = 1, t0 = 0;

    function draw(l) {
      L = l;
      var k = Math.min(3, Math.floor(l - 1)), f = l - 1 - k;
      var u = U[k] + (U[k + 1] - U[k]) * f, d = D[k] + (D[k + 1] - D[k]) * f;
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i], th = (1 - u) * turns * Math.PI * p.t + (p.c ? Math.PI : 0);
        var x = p.t * Math.cos(th) + p.jx + (p.c ? -d : d), y = p.t * Math.sin(th) + p.jy;
        p.e.setAttribute('cx', (cx + x * sc).toFixed(1));
        p.e.setAttribute('cy', (cy - y * sc).toFixed(1));
      }
      arms.forEach(function (e) {
        var c = +e.dataset.c, dd = 'M';
        TT.forEach(function (t, j) {
          var th = (1 - u) * turns * Math.PI * t + (c ? Math.PI : 0);
          dd += (j ? ' L ' : ' ') + (cx + (t * Math.cos(th) + (c ? -d : d)) * sc).toFixed(1) + ' ' + (cy - t * Math.sin(th) * sc).toFixed(1);
        });
        e.setAttribute('d', dd);
      });
      var shown = Math.round(l);
      llabel.textContent = 'layer ' + shown;
      qlabel.textContent = 'Ê = ' + Q[shown - 1];
      dots.forEach(function (e) { e.setAttribute('opacity', +e.dataset.layer <= shown ? 1 : 0); });
    }
    function target() {
      var l = 1;
      slide.querySelectorAll('.untangle-step').forEach(function (s) {
        if (s.classList.contains('visible')) l = Math.max(l, +s.dataset.layer);
      });
      return l;
    }
    function retarget(instant) {
      var l = target();
      if (instant) { to = l; draw(l); return; }
      if (l !== to) { from = L; to = l; t0 = performance.now(); }
    }
    function tick(now) {
      if (L !== to) {
        var u = Math.min(1, (now - t0) / TWEEN), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
        draw(u >= 1 ? to : from + (to - from) * e);
      }
      requestAnimationFrame(tick);
    }
    var fixed = new URLSearchParams(location.search).get('untangle_layer');
    if (fixed !== null) { draw(+fixed); return; }
    Reveal.on('fragmentshown', function () { retarget(false); });
    Reveal.on('fragmenthidden', function () { retarget(false); });
    Reveal.on('slidechanged', function (ev) { if (ev.currentSlide === slide) retarget(true); });
    retarget(true);
    requestAnimationFrame(tick);
  }
  function boot() { if (Reveal.isReady()) start(); else Reveal.on('ready', start); }
  if (window.Reveal && Reveal.on) boot(); else window.addEventListener('load', boot);
})();

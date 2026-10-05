// Broadsheet title-block injector—masthead, edition line, seal, byline,
// speaker notes, and floating pull-quote. Customize the marked sections
// for each talk; leave the structural scaffolding intact.

(function () {
  // ============================================================
  // CUSTOMIZE PER TALK—title-block content
  // ============================================================
  var ARXIV_URL = 'https://arxiv.org/abs/2608.06180';

  // Eyebrow/kicker shown above the (long, registered) title—the human hook,
  // e.g. 'Same or Different?'. Empty string disables it.
  var KICKER = '';

  var GAZETTE = {
    volume:   'Vol. I',
    issue:    'No. VI',
    name:     'The Topology Gazette',         // REPLACE with venue-flavored gazette name
    edition:  'Salt Lake City Edition',
  };

  var COAUTHORS = [
    'Kazuhiro Kawamura',
    'Atish Mitra',
  ];

  var EDITION_LINE = {
    field:    'Applied Topology · Euler Calculus · Inference',
    venue:    { text: 'SIAM MDS26 · Minisymposium MS8, Topological Descriptors in Data Analysis',
                href: 'https://meetings.siam.org/sess/dsp_talk.cfm?p=159636' },
  };

  var PULLQUOTE = {
    body:    'A barcode describes one cloud. The question is how several meet, and at what scale.',
    attrib:  'a dispatch on overlaps',
  };

  // Speaker notes for the title slide (HTML; presenter-only).
  // Inline `::: {.notes}` at the top of the .qmd would create a phantom
  // empty slide, so we inject the title's notes here instead.
  var TITLE_NOTES_HTML =
    '<p>Thank you, Brittany and Atish, for the invitation. This is joint work with Kazuhiro Kawamura and Atish Mitra.</p>' +
    '<p>The question: given several point clouds, how much do they interact topologically, and at what scale? ' +
    'The answer is an integer-valued curve, the Euler characteristic of the overlap of their ball unions. ' +
    'Three parts: why this curve, and why it is the canonical one; how cheap and how stable it is; ' +
    'and what it certifies, on monsoons and on trained classifiers.</p>';

  // ============================================================
  // STRUCTURAL SCAFFOLDING—usually no edits needed below
  // ============================================================

  function makePlate(cls, label, svg, href) {
    var el = href ? document.createElement('a') : document.createElement('figure');
    el.className = cls;
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('data-plate', label);
    if (href) { el.href = href; el.target = '_blank'; el.rel = 'noopener'; }
    el.innerHTML = svg;
    return el;
  }

  function makeEdition(items) {
    var line = document.createElement('div');
    line.className = 'edition-line';
    items.forEach(function (item) {
      if (!item) return;
      var s = document.createElement('span');
      if (typeof item === 'string') {
        s.textContent = item;
      } else {
        var a = document.createElement('a');
        a.href = item.href; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = item.text;
        s.appendChild(a);
      }
      line.appendChild(s);
    });
    return line;
  }

  // QR of arXiv:2608.06180 (qrcode, error correction M; one unit square per dark module).
  var ARXIV_QR_SVG = '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 31 31" class="qr-code" role="img" aria-label="QR code: arXiv:2608.06180" shape-rendering="crispEdges"><path fill="currentColor" d="M0 0h1v1h-1zM1 0h1v1h-1zM2 0h1v1h-1zM3 0h1v1h-1zM4 0h1v1h-1zM5 0h1v1h-1zM6 0h1v1h-1zM9 0h1v1h-1zM11 0h1v1h-1zM13 0h1v1h-1zM16 0h1v1h-1zM19 0h1v1h-1zM20 0h1v1h-1zM22 0h1v1h-1zM23 0h1v1h-1zM24 0h1v1h-1zM25 0h1v1h-1zM26 0h1v1h-1zM27 0h1v1h-1zM28 0h1v1h-1zM0 1h1v1h-1zM6 1h1v1h-1zM10 1h1v1h-1zM12 1h1v1h-1zM13 1h1v1h-1zM14 1h1v1h-1zM15 1h1v1h-1zM20 1h1v1h-1zM22 1h1v1h-1zM28 1h1v1h-1zM0 2h1v1h-1zM2 2h1v1h-1zM3 2h1v1h-1zM4 2h1v1h-1zM6 2h1v1h-1zM9 2h1v1h-1zM12 2h1v1h-1zM13 2h1v1h-1zM16 2h1v1h-1zM17 2h1v1h-1zM18 2h1v1h-1zM19 2h1v1h-1zM20 2h1v1h-1zM22 2h1v1h-1zM24 2h1v1h-1zM25 2h1v1h-1zM26 2h1v1h-1zM28 2h1v1h-1zM0 3h1v1h-1zM2 3h1v1h-1zM3 3h1v1h-1zM4 3h1v1h-1zM6 3h1v1h-1zM9 3h1v1h-1zM10 3h1v1h-1zM11 3h1v1h-1zM12 3h1v1h-1zM13 3h1v1h-1zM14 3h1v1h-1zM15 3h1v1h-1zM22 3h1v1h-1zM24 3h1v1h-1zM25 3h1v1h-1zM26 3h1v1h-1zM28 3h1v1h-1zM0 4h1v1h-1zM2 4h1v1h-1zM3 4h1v1h-1zM4 4h1v1h-1zM6 4h1v1h-1zM9 4h1v1h-1zM10 4h1v1h-1zM12 4h1v1h-1zM13 4h1v1h-1zM14 4h1v1h-1zM16 4h1v1h-1zM20 4h1v1h-1zM22 4h1v1h-1zM24 4h1v1h-1zM25 4h1v1h-1zM26 4h1v1h-1zM28 4h1v1h-1zM0 5h1v1h-1zM6 5h1v1h-1zM8 5h1v1h-1zM9 5h1v1h-1zM11 5h1v1h-1zM13 5h1v1h-1zM14 5h1v1h-1zM17 5h1v1h-1zM18 5h1v1h-1zM19 5h1v1h-1zM22 5h1v1h-1zM28 5h1v1h-1zM0 6h1v1h-1zM1 6h1v1h-1zM2 6h1v1h-1zM3 6h1v1h-1zM4 6h1v1h-1zM5 6h1v1h-1zM6 6h1v1h-1zM8 6h1v1h-1zM10 6h1v1h-1zM12 6h1v1h-1zM14 6h1v1h-1zM16 6h1v1h-1zM18 6h1v1h-1zM20 6h1v1h-1zM22 6h1v1h-1zM23 6h1v1h-1zM24 6h1v1h-1zM25 6h1v1h-1zM26 6h1v1h-1zM27 6h1v1h-1zM28 6h1v1h-1zM9 7h1v1h-1zM10 7h1v1h-1zM11 7h1v1h-1zM12 7h1v1h-1zM14 7h1v1h-1zM17 7h1v1h-1zM19 7h1v1h-1zM0 8h1v1h-1zM3 8h1v1h-1zM5 8h1v1h-1zM6 8h1v1h-1zM8 8h1v1h-1zM15 8h1v1h-1zM18 8h1v1h-1zM20 8h1v1h-1zM21 8h1v1h-1zM23 8h1v1h-1zM1 9h1v1h-1zM4 9h1v1h-1zM5 9h1v1h-1zM10 9h1v1h-1zM11 9h1v1h-1zM14 9h1v1h-1zM15 9h1v1h-1zM17 9h1v1h-1zM18 9h1v1h-1zM20 9h1v1h-1zM22 9h1v1h-1zM25 9h1v1h-1zM28 9h1v1h-1zM0 10h1v1h-1zM2 10h1v1h-1zM4 10h1v1h-1zM5 10h1v1h-1zM6 10h1v1h-1zM7 10h1v1h-1zM9 10h1v1h-1zM11 10h1v1h-1zM16 10h1v1h-1zM18 10h1v1h-1zM19 10h1v1h-1zM20 10h1v1h-1zM21 10h1v1h-1zM23 10h1v1h-1zM24 10h1v1h-1zM25 10h1v1h-1zM26 10h1v1h-1zM27 10h1v1h-1zM0 11h1v1h-1zM1 11h1v1h-1zM4 11h1v1h-1zM5 11h1v1h-1zM7 11h1v1h-1zM8 11h1v1h-1zM9 11h1v1h-1zM14 11h1v1h-1zM15 11h1v1h-1zM20 11h1v1h-1zM21 11h1v1h-1zM22 11h1v1h-1zM24 11h1v1h-1zM26 11h1v1h-1zM27 11h1v1h-1zM0 12h1v1h-1zM1 12h1v1h-1zM2 12h1v1h-1zM3 12h1v1h-1zM4 12h1v1h-1zM5 12h1v1h-1zM6 12h1v1h-1zM7 12h1v1h-1zM8 12h1v1h-1zM9 12h1v1h-1zM10 12h1v1h-1zM11 12h1v1h-1zM12 12h1v1h-1zM16 12h1v1h-1zM17 12h1v1h-1zM18 12h1v1h-1zM20 12h1v1h-1zM22 12h1v1h-1zM25 12h1v1h-1zM27 12h1v1h-1zM28 12h1v1h-1zM3 13h1v1h-1zM10 13h1v1h-1zM11 13h1v1h-1zM15 13h1v1h-1zM18 13h1v1h-1zM19 13h1v1h-1zM20 13h1v1h-1zM21 13h1v1h-1zM2 14h1v1h-1zM3 14h1v1h-1zM5 14h1v1h-1zM6 14h1v1h-1zM7 14h1v1h-1zM8 14h1v1h-1zM9 14h1v1h-1zM10 14h1v1h-1zM11 14h1v1h-1zM12 14h1v1h-1zM15 14h1v1h-1zM16 14h1v1h-1zM17 14h1v1h-1zM18 14h1v1h-1zM20 14h1v1h-1zM21 14h1v1h-1zM23 14h1v1h-1zM24 14h1v1h-1zM25 14h1v1h-1zM26 14h1v1h-1zM27 14h1v1h-1zM28 14h1v1h-1zM1 15h1v1h-1zM4 15h1v1h-1zM5 15h1v1h-1zM7 15h1v1h-1zM9 15h1v1h-1zM13 15h1v1h-1zM14 15h1v1h-1zM16 15h1v1h-1zM17 15h1v1h-1zM19 15h1v1h-1zM21 15h1v1h-1zM22 15h1v1h-1zM23 15h1v1h-1zM24 15h1v1h-1zM25 15h1v1h-1zM27 15h1v1h-1zM2 16h1v1h-1zM3 16h1v1h-1zM5 16h1v1h-1zM6 16h1v1h-1zM8 16h1v1h-1zM9 16h1v1h-1zM10 16h1v1h-1zM13 16h1v1h-1zM14 16h1v1h-1zM15 16h1v1h-1zM17 16h1v1h-1zM18 16h1v1h-1zM19 16h1v1h-1zM20 16h1v1h-1zM21 16h1v1h-1zM23 16h1v1h-1zM27 16h1v1h-1zM1 17h1v1h-1zM4 17h1v1h-1zM7 17h1v1h-1zM10 17h1v1h-1zM11 17h1v1h-1zM12 17h1v1h-1zM15 17h1v1h-1zM17 17h1v1h-1zM21 17h1v1h-1zM22 17h1v1h-1zM23 17h1v1h-1zM25 17h1v1h-1zM28 17h1v1h-1zM0 18h1v1h-1zM2 18h1v1h-1zM3 18h1v1h-1zM4 18h1v1h-1zM6 18h1v1h-1zM7 18h1v1h-1zM9 18h1v1h-1zM11 18h1v1h-1zM12 18h1v1h-1zM13 18h1v1h-1zM16 18h1v1h-1zM17 18h1v1h-1zM21 18h1v1h-1zM27 18h1v1h-1zM28 18h1v1h-1zM2 19h1v1h-1zM3 19h1v1h-1zM5 19h1v1h-1zM8 19h1v1h-1zM9 19h1v1h-1zM10 19h1v1h-1zM12 19h1v1h-1zM13 19h1v1h-1zM15 19h1v1h-1zM16 19h1v1h-1zM17 19h1v1h-1zM19 19h1v1h-1zM20 19h1v1h-1zM23 19h1v1h-1zM27 19h1v1h-1zM28 19h1v1h-1zM0 20h1v1h-1zM6 20h1v1h-1zM9 20h1v1h-1zM12 20h1v1h-1zM14 20h1v1h-1zM18 20h1v1h-1zM19 20h1v1h-1zM20 20h1v1h-1zM21 20h1v1h-1zM22 20h1v1h-1zM23 20h1v1h-1zM24 20h1v1h-1zM26 20h1v1h-1zM8 21h1v1h-1zM9 21h1v1h-1zM11 21h1v1h-1zM13 21h1v1h-1zM17 21h1v1h-1zM18 21h1v1h-1zM19 21h1v1h-1zM20 21h1v1h-1zM24 21h1v1h-1zM26 21h1v1h-1zM27 21h1v1h-1zM28 21h1v1h-1zM0 22h1v1h-1zM1 22h1v1h-1zM2 22h1v1h-1zM3 22h1v1h-1zM4 22h1v1h-1zM5 22h1v1h-1zM6 22h1v1h-1zM10 22h1v1h-1zM13 22h1v1h-1zM14 22h1v1h-1zM18 22h1v1h-1zM20 22h1v1h-1zM22 22h1v1h-1zM24 22h1v1h-1zM27 22h1v1h-1zM0 23h1v1h-1zM6 23h1v1h-1zM8 23h1v1h-1zM10 23h1v1h-1zM11 23h1v1h-1zM13 23h1v1h-1zM15 23h1v1h-1zM19 23h1v1h-1zM20 23h1v1h-1zM24 23h1v1h-1zM25 23h1v1h-1zM26 23h1v1h-1zM27 23h1v1h-1zM0 24h1v1h-1zM2 24h1v1h-1zM3 24h1v1h-1zM4 24h1v1h-1zM6 24h1v1h-1zM9 24h1v1h-1zM11 24h1v1h-1zM12 24h1v1h-1zM14 24h1v1h-1zM15 24h1v1h-1zM17 24h1v1h-1zM18 24h1v1h-1zM20 24h1v1h-1zM21 24h1v1h-1zM22 24h1v1h-1zM23 24h1v1h-1zM24 24h1v1h-1zM28 24h1v1h-1zM0 25h1v1h-1zM2 25h1v1h-1zM3 25h1v1h-1zM4 25h1v1h-1zM6 25h1v1h-1zM8 25h1v1h-1zM10 25h1v1h-1zM11 25h1v1h-1zM14 25h1v1h-1zM16 25h1v1h-1zM17 25h1v1h-1zM18 25h1v1h-1zM19 25h1v1h-1zM20 25h1v1h-1zM22 25h1v1h-1zM24 25h1v1h-1zM25 25h1v1h-1zM26 25h1v1h-1zM27 25h1v1h-1zM0 26h1v1h-1zM2 26h1v1h-1zM3 26h1v1h-1zM4 26h1v1h-1zM6 26h1v1h-1zM9 26h1v1h-1zM12 26h1v1h-1zM13 26h1v1h-1zM14 26h1v1h-1zM19 26h1v1h-1zM21 26h1v1h-1zM24 26h1v1h-1zM25 26h1v1h-1zM26 26h1v1h-1zM28 26h1v1h-1zM0 27h1v1h-1zM6 27h1v1h-1zM9 27h1v1h-1zM11 27h1v1h-1zM15 27h1v1h-1zM17 27h1v1h-1zM19 27h1v1h-1zM20 27h1v1h-1zM21 27h1v1h-1zM27 27h1v1h-1zM0 28h1v1h-1zM1 28h1v1h-1zM2 28h1v1h-1zM3 28h1v1h-1zM4 28h1v1h-1zM5 28h1v1h-1zM6 28h1v1h-1zM8 28h1v1h-1zM11 28h1v1h-1zM12 28h1v1h-1zM14 28h1v1h-1zM16 28h1v1h-1zM17 28h1v1h-1zM18 28h1v1h-1zM20 28h1v1h-1zM22 28h1v1h-1zM24 28h1v1h-1zM25 28h1v1h-1zM27 28h1v1h-1z"/></svg>';

  // Placeholder QR: finder patterns and a caption, no data modules. Swap for
  // a real QR of ARXIV_URL once the preprint is posted.
  var QR_PLACEHOLDER_SVG =
    '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" class="qr-code qr-placeholder" role="img" aria-label="QR code placeholder">' +
      '<g fill="none" stroke="currentColor" stroke-width="28">' +
        '<rect x="74" y="74" width="140" height="140"/><rect x="386" y="74" width="140" height="140"/><rect x="74" y="386" width="140" height="140"/>' +
      '</g>' +
      '<g fill="currentColor"><rect x="116" y="116" width="56" height="56"/><rect x="428" y="116" width="56" height="56"/><rect x="116" y="428" width="56" height="56"/></g>' +
      '<g fill="currentColor" opacity="0.18"><rect x="260" y="74" width="28" height="28"/><rect x="316" y="102" width="28" height="28"/><rect x="260" y="158" width="28" height="28"/><rect x="316" y="214" width="28" height="28"/>' +
        '<rect x="74" y="260" width="28" height="28"/><rect x="158" y="316" width="28" height="28"/><rect x="214" y="260" width="28" height="28"/><rect x="498" y="316" width="28" height="28"/><rect x="442" y="260" width="28" height="28"/></g>' +
      '<text x="357" y="420" text-anchor="middle" font-family="Alegreya SC, EB Garamond, Georgia, serif" font-size="46" letter-spacing="4" fill="currentColor">arXiv</text>' +
      '<text x="357" y="478" text-anchor="middle" font-family="EB Garamond, Georgia, serif" font-style="italic" font-size="36" fill="currentColor" opacity="0.8">October 2026</text>' +
    '</svg>';

  // Decorative placeholder SVGs for the left/right title-block "landmark plates".
  // Replace with talk-relevant figures (a thumbnail diagram, QR code, etc.)
  // when you want them; the broadsheet aesthetic also works without them.
  // A plate can also be an external file: '<img src="assets/title-plate.svg?v=STAMP" alt="">'
  // (list it under `resources:` and bump STAMP when it changes; see README, Caching).
  // Before the preprint is posted, RIGHT_PLATE_SVG = QR_PLACEHOLDER_SVG.
  var LEFT_PLATE_SVG  = '<img src="assets/title-plate.svg?v=202610050700" alt="">';
  var RIGHT_PLATE_SVG = ARXIV_QR_SVG;

  // Wax seal—initials inside a serif circle. Customize the textPaths
  // (top/bottom band) and inner monogram for your name.
  var SEAL_SVG =
    '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" class="wax-seal" viewBox="0 0 80 80" role="img" aria-label="Author seal">' +
      '<defs>' +
        '<style>' +
          '.seal-ring { stroke: currentColor; fill: none; stroke-width: 1.3; }' +
          '.seal-inner { stroke: currentColor; fill: none; stroke-width: 0.45; }' +
          '.seal-mark { fill: currentColor; stroke: none; }' +
          '.seal-mono { font-family: "EB Garamond", Georgia, serif; font-weight: 700; font-size: 14px; fill: currentColor; }' +
          '.seal-band { font-family: "Alegreya SC", "EB Garamond", Georgia, serif; font-size: 4.6px; letter-spacing: 0.22em; fill: currentColor; }' +
        '</style>' +
        '<path id="seal-top" d="M 11 40 A 29 29 0 0 1 69 40" />' +
        '<path id="seal-bottom" d="M 11 40 A 29 29 0 0 0 69 40" />' +
      '</defs>' +
      '<circle class="seal-ring" cx="40" cy="40" r="36" />' +
      '<circle class="seal-inner" cx="40" cy="40" r="33" />' +
      '<circle class="seal-inner" cx="40" cy="40" r="22" />' +
      '<text class="seal-band"><textPath href="#seal-top" startOffset="50%" text-anchor="middle">SVSHOVAN MAJHI</textPath></text>' +
      '<text class="seal-band"><textPath href="#seal-bottom" startOffset="50%" text-anchor="middle">· ANNO MMXXVI ·</textPath></text>' +
      // tetrahedral monogram mark (a nod to simplices) + Bengali signature
      '<g>' +
        '<polygon class="seal-mark" opacity="0.16" points="35,33 40,24 40,41" />' +
        '<polygon class="seal-mark" opacity="0.16" points="40,24 45,33 40,41" />' +
        '<g stroke="currentColor" fill="none" stroke-width="0.55">' +
          '<line x1="35" y1="33" x2="40" y2="24" /><line x1="40" y1="24" x2="45" y2="33" />' +
          '<line x1="35" y1="33" x2="40" y2="41" /><line x1="45" y1="33" x2="40" y2="41" />' +
          '<line x1="40" y1="24" x2="40" y2="41" /><line x1="35" y1="33" x2="45" y2="33" />' +
        '</g>' +
      '</g>' +
      '<text class="seal-mono" x="40" y="51" text-anchor="middle" style="font-family: \'Noto Serif Bengali\', \'Bengali Sangam MN\', \'Kalpurush\', serif; font-size: 12px;">সুশোভন</text>' +
    '</svg>';

  function inject() {
    var tb = document.querySelector('.quarto-title-block');
    if (!tb || tb.querySelector('.masthead')) return;

    var titleEl    = tb.querySelector('h1.title');
    var subtitleEl = tb.querySelector('.subtitle');
    var authorEl   = tb.querySelector('.quarto-title-author-name, .author');
    var dateEl     = tb.querySelector('p.date, .date');

    var author = authorEl ? authorEl.textContent.trim() : '';
    var date   = dateEl   ? dateEl.textContent.trim()   : '';

    var volBadge = document.createElement('div');
    volBadge.className = 'edition-badge title-volume';
    volBadge.innerHTML =
      '<span>' + GAZETTE.volume  + '</span>' +
      '<span>' + GAZETTE.issue   + '</span>' +
      '<span>' + GAZETTE.name    + '</span>' +
      '<span>' + GAZETTE.edition + '</span>';

    var seal = document.createElement('div');
    seal.className = 'title-seal';
    seal.setAttribute('aria-hidden', 'true');
    seal.innerHTML = SEAL_SVG;

    var masthead = document.createElement('header');
    masthead.className = 'masthead';

    var row = document.createElement('div');
    row.className = 'masthead-row';

    var left  = makePlate('landmark-plate left',  'I',   LEFT_PLATE_SVG);
    var right = makePlate('landmark-plate right qr-plate', 'III', RIGHT_PLATE_SVG, ARXIV_URL);

    var text = document.createElement('div');
    text.className = 'masthead-text';
    if (KICKER) {
      var kicker = document.createElement('p');
      kicker.className = 'masthead-kicker';
      kicker.textContent = KICKER;
      text.appendChild(kicker);
    }
    if (titleEl)    text.appendChild(titleEl);
    if (subtitleEl) text.appendChild(subtitleEl);

    if (COAUTHORS.length > 0) {
      var byline = document.createElement('p');
      byline.className = 'masthead-byline';
      var names = COAUTHORS.map(function (n) {
        return '<span class="byline-name">' + n + '</span>';
      }).join(' · ');
      byline.innerHTML = '<span class="byline-label">with</span> ' + names;
      text.appendChild(byline);
    }

    row.appendChild(left);
    row.appendChild(text);
    row.appendChild(right);
    masthead.appendChild(row);

    masthead.appendChild(makeEdition([
      author,
      EDITION_LINE.field,
      EDITION_LINE.venue,
      date,
    ]));

    var auths = tb.querySelector('.quarto-title-authors');
    if (auths)  auths.style.display  = 'none';
    if (dateEl) dateEl.style.display = 'none';

    tb.insertBefore(masthead, tb.firstChild);
    tb.insertBefore(volBadge, masthead);
    tb.appendChild(seal);

    var notes = document.createElement('aside');
    notes.className = 'notes';
    notes.innerHTML = TITLE_NOTES_HTML;
    tb.appendChild(notes);

    var quote = document.createElement('aside');
    quote.className = 'title-pullquote';
    quote.innerHTML =
      '<blockquote>' + PULLQUOTE.body + '</blockquote>' +
      '<div class="attribution">' + PULLQUOTE.attrib + '</div>';
    tb.appendChild(quote);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();

// Toggle a "finis" class on .reveal while the colophon slide is showing, so the
// theme can drop the running footer and page number on the back page. Quarto
// strips data-state from headings, so we drive it from Reveal's slide events.
// (Quarto also keeps only the first line of include-after-body `text:`, so extra
// deck JS like this lives appended here rather than as a second <script>.)
(function () {
  function hook() {
    if (typeof Reveal === 'undefined' || !Reveal.on) { setTimeout(hook, 100); return; }
    function update() {
      var cur = Reveal.getCurrentSlide();
      var isColophon = !!(cur && cur.classList && cur.classList.contains('colophon'));
      var r = document.querySelector('.reveal');
      if (r) r.classList.toggle('finis', isColophon);
    }
    Reveal.on('slidechanged', update);
    Reveal.on('ready', update);
    update();
  }
  hook();
})();

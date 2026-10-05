// Broadsheet title-block injector—masthead, edition line, seal, byline,
// speaker notes, and floating pull-quote. Customize the marked sections
// for each talk; leave the structural scaffolding intact.

(function () {
  // ============================================================
  // CUSTOMIZE PER TALK—title-block content
  // ============================================================
  var ARXIV_URL = 'https://arxiv.org/abs/0000.00000';   // REPLACE with paper URL or '#'

  // Eyebrow/kicker shown above the (long, registered) title—the human hook,
  // e.g. 'Same or Different?'. Empty string disables it.
  var KICKER = '';

  var GAZETTE = {
    volume:   'Vol. I',
    issue:    'No. I',
    name:     'The Topology Gazette',         // REPLACE with venue-flavored gazette name
    edition:  'Workshop Edition',             // REPLACE with edition tag
  };

  var COAUTHORS = [
    // REPLACE with co-author names (or leave [] for solo talks)
    // 'Co-Author One',
    // 'Co-Author Two',
  ];

  var EDITION_LINE = {
    field:    'Field · Subfield · Lens',      // REPLACE
    venue:    { text: 'Venue, Institution',   // REPLACE
                href: '#' },
  };

  var PULLQUOTE = {
    body:    'A one-line punch quote, italic, anchored bottom-right.',  // REPLACE
    attrib:  'a topological dispatch',                                  // REPLACE
  };

  // Speaker notes for the title slide (HTML; presenter-only).
  // Inline `::: {.notes}` at the top of the .qmd would create a phantom
  // empty slide, so we inject the title's notes here instead.
  var TITLE_NOTES_HTML =
    '<p>REPLACE with opening notes — greet the audience, name the talk, name co-authors, ' +
    'pitch the headline in 2–3 sentences, list the section roadmap.</p>';

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
  var LEFT_PLATE_SVG  = '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600"></svg>';
  var RIGHT_PLATE_SVG = '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600"></svg>';

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
      '<text class="seal-band"><textPath href="#seal-top" startOffset="50%" text-anchor="middle">AUTHOR NAME</textPath></text>' +    // REPLACE
      '<text class="seal-band"><textPath href="#seal-bottom" startOffset="50%" text-anchor="middle">· ANNO MMXXVI ·</textPath></text>' +
      '<text class="seal-mono" x="40" y="46" text-anchor="middle">AN</text>' +    // REPLACE initials
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

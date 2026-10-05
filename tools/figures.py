"""Figures and section plates for the IECP talk (SIAM MDS26).

Run from the repository root:  python3 tools/figures.py
Every profile is computed, not drawn: Delta chi is evaluated with the
intersection_ecp package of ~/GitHub/mixup-ecp, and the classifier figures are
re-plotted from that repository's results files, in the deck's palette.
"""

import json
import math
import os
import random
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

MIXUP = os.path.expanduser("~/GitHub/mixup-ecp")
sys.path.insert(0, MIXUP)
sys.path.insert(0, os.path.join(MIXUP, "disentangle"))

OX, INK, SEPIA, PENCIL, RULE, PAPER, PAPER_SOFT = (
    "#6c1d1a", "#2b211a", "#57473a", "#8c7d6a", "#c8b894", "#f5efde", "#ede5cf")
SERIF = "EB Garamond, Georgia, serif"
CAPS = "Alegreya SC, EB Garamond, Georgia, serif"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

plt.rcParams.update({
    "font.family": ["EB Garamond", "Georgia", "serif"],
    "svg.fonttype": "none",           # keep text as text: the browser sets it
    "font.size": 13,
    "axes.edgecolor": SEPIA, "axes.labelcolor": SEPIA, "text.color": INK,
    "xtick.color": SEPIA, "ytick.color": SEPIA,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": "none", "axes.facecolor": "none",
    "savefig.facecolor": "none", "legend.frameon": False,
})


# --------------------------------------------------------------------------
# svg helpers
# --------------------------------------------------------------------------
def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def poly(points, **attrs):
    pts = " ".join(f"{f(x)},{f(y)}" for x, y in points)
    return f'<polygon points="{pts}"{_attrs(attrs)}/>'


def line(p, q, **attrs):
    return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" '
            f'y2="{f(q[1])}"{_attrs(attrs)}/>')


def circle(p, r, **attrs):
    return f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r)}"{_attrs(attrs)}/>'


def text(p, s, size=14, italic=True, fill=INK, anchor="middle", caps=False,
         spacing=None, weight=None):
    fam = CAPS if caps else SERIF
    style = ' font-style="italic"' if italic and not caps else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{f(p[0])}" y="{f(p[1])}" fill="{fill}" font-family="{fam}"'
            f' font-size="{size}"{style}{ls}{w} text-anchor="{anchor}">{s}</text>')


def _attrs(attrs):
    return "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}">\n' + "\n".join(body) + "\n</svg>\n")


def complex_layers(pts, edges, tris, fill=OX, fill_opacity=0.16, edge=OX,
                   edge_w=0.8, edge_opacity=0.55, pt_r=2.4, pt_fill=INK):
    """Shadow (union of triangle hulls, flat tint via group opacity), edges, points."""
    out = [f'<g opacity="{fill_opacity}" fill="{fill}" stroke="none">']
    out += [poly([pts[i], pts[j], pts[k]]) for i, j, k in tris]
    out += ["</g>", f'<g stroke="{edge}" stroke-width="{edge_w}" '
            f'opacity="{edge_opacity}" stroke-linecap="round">']
    out += [line(pts[i], pts[j]) for i, j in edges]
    out += ["</g>", f'<g fill="{pt_fill}" stroke="none">']
    out += [circle(p, pt_r) for p in pts]
    out.append("</g>")
    return out


def fleurons():
    petal = ('<path d="M 0 -8 Q 5 -3 0 0 Q -5 -3 0 -8 Z"/>'
             '<path d="M 0 8  Q 5 3  0 0 Q -5 3  0 8  Z"/>'
             '<path d="M -8 0 Q -3 -5 0 0 Q -3 5 -8 0 Z"/>'
             '<path d="M 8 0  Q 3 -5  0 0 Q 3 5  8 0  Z"/>'
             '<circle cx="0" cy="0" r="2.0"/>')
    out = [f'<g fill="{RULE}" stroke="none">']
    for x, y in [(52, 52), (668, 52), (52, 348), (668, 348)]:
        out.append(f'<g transform="translate({x}, {y}) scale(0.9)">{petal}</g>')
    out.append("</g>")
    return out


def plate(title, deck, caption, art, label):
    body = [f'<rect x="36" y="36" width="648" height="328" fill="none" '
            f'stroke="{RULE}" stroke-width="0.6"/>',
            text((360, 68), title, 16, caps=True, fill=OX, spacing=4, weight=500),
            text((360, 92), deck, 13, fill=SEPIA),
            line((120, 104), (600, 104), stroke=RULE, stroke_width=0.5)]
    body += art
    body += fleurons()
    body.append(text((360, 356), caption, 11, caps=True, fill=SEPIA, spacing=3))
    return svg(720, 400, body, label)


def write(name, content):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(content)
    print("wrote", name)


# --------------------------------------------------------------------------
# computed figures (matplotlib, text kept as text)
# --------------------------------------------------------------------------
import intersection_ecp as iecp


def _save(fig, name):
    fig.savefig(os.path.join(OUT, name), format="svg", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("wrote", name)


def _blob(rng, c, sd, n):
    return rng.normal(c, sd, (n, 2))


def _ring(rng, c, R, w, n):
    a = rng.uniform(0, 2 * np.pi, n)
    rr = R + rng.uniform(-w, w, n)
    return np.c_[c[0] + rr * np.cos(a), c[1] + rr * np.sin(a)]


def _offsets(ax, P, r, color, alpha=0.13):
    for p in P:
        ax.add_patch(Circle(p, r, color=color, alpha=alpha, lw=0))
    ax.scatter(P[:, 0], P[:, 1], s=5, color=color, zorder=3, lw=0)


def _union_mask(P, r, xs, ys):
    gx, gy = np.meshgrid(xs, ys)
    m = np.zeros(gx.shape, bool)
    for p in P:
        m |= (gx - p[0]) ** 2 + (gy - p[1]) ** 2 <= r * r
    return m


def _draw_overlap(ax, X, Y, r, lim=2.6):
    """The two ball unions, light, and their intersection, solid oxblood."""
    from matplotlib.colors import ListedColormap
    xs = np.linspace(-lim, lim, 520); ys = np.linspace(-lim * 0.9, lim * 0.9, 470)
    mx, my = _union_mask(X, r, xs, ys), _union_mask(Y, r, xs, ys)
    img = np.full(mx.shape, 0)
    img[mx] = 1; img[my] = 2; img[mx & my] = 3
    cmap = ListedColormap([(0, 0, 0, 0), (0.42, 0.11, 0.10, 0.18), (0.17, 0.13, 0.10, 0.16), (0.42, 0.11, 0.10, 0.92)])
    ax.imshow(img, extent=(xs[0], xs[-1], ys[0], ys[-1]), origin="lower", cmap=cmap, vmin=0, vmax=3,
              interpolation="nearest")
    ax.scatter(X[:, 0], X[:, 1], s=4, color=OX, zorder=3, lw=0)
    ax.scatter(Y[:, 0], Y[:, 1], s=4, color=INK, zorder=3, lw=0)


def fig_trio():
    """Separated, overlapping, encircling: offsets at one scale, and the profiles."""
    rng = np.random.default_rng(3)
    configs = [
        ("separated", _blob(rng, (-1.5, 0), 0.32, 70), _blob(rng, (1.5, 0), 0.32, 70)),
        ("overlapping", _blob(rng, (-0.45, 0), 0.32, 70), _blob(rng, (0.45, 0), 0.32, 70)),
        ("encircling", _ring(rng, (0, 0), 1.55, 0.12, 110), _blob(rng, (0, 0), 0.30, 70)),
    ]
    r_grid = np.linspace(0, 1.2, 241)
    r_show = 0.7
    fig = plt.figure(figsize=(10.5, 5.9))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 0.9], hspace=0.28, wspace=0.08)
    styles = {"separated": (PENCIL, "--"), "overlapping": (OX, "-"), "encircling": (INK, "-.")}
    axp = fig.add_subplot(gs[1, :])
    for j, (name, X, Y) in enumerate(configs):
        ax = fig.add_subplot(gs[0, j])
        _draw_overlap(ax, X, Y, r_show)
        ax.set_xlim(-2.6, 2.6); ax.set_ylim(-2.3, 2.3); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(name, fontsize=15, style="italic", color=SEPIA)
        d = iecp.intersection_profile([X, Y], r_grid)
        v = int(iecp.intersection_profile([X, Y], np.array([r_show]))[0])
        meet = iecp.first_interaction_scale([X, Y]) <= r_show
        note = rf"$\Delta\chi = {v}$" + (", yet they meet" if (meet and v == 0) else "")
        ax.text(0, -2.55, note, ha="center", va="top", fontsize=14, color=OX if (meet and v == 0) else INK)
        col, ls = styles[name]
        axp.step(r_grid, d, where="post", color=col, ls=ls, lw=1.6, label=name)
    axp.axvline(r_show, color=RULE, lw=1)
    top = axp.get_ylim()[1]
    axp.text(r_show + 0.01, top * 0.9, "the scale above", fontsize=11, color=PENCIL, style="italic")
    axp.annotate("encircling: the overlap is an annulus, $\\chi = 0$", xy=(0.95, 0.05), xytext=(0.78, top * 0.45),
                 fontsize=11.5, color=OX, style="italic", arrowprops=dict(arrowstyle="-", color=OX, lw=0.8))
    axp.text(0.075, top * 0.97, "many small lenses", fontsize=11, color=PENCIL, style="italic", va="top")
    axp.set_xlabel("scale $r$", fontsize=13)
    axp.set_ylabel(r"$\Delta\chi(r)$", fontsize=14)
    axp.legend(fontsize=12, loc="upper right")
    _save(fig, "trio.svg")


def fig_stability():
    """Two crossing rings and a Hausdorff perturbation: equal off critical scales."""
    rng = np.random.default_rng(7)
    X = _ring(rng, (-0.7, 0), 1.25, 0.05, 140)
    Y = _ring(rng, (0.7, 0), 1.25, 0.05, 140)
    eps = 0.03
    def jiggle(P):
        a = rng.uniform(0, 2 * np.pi, len(P)); s = eps * np.sqrt(rng.uniform(0, 1, len(P)))
        return P + np.c_[s * np.cos(a), s * np.sin(a)]
    Xp, Yp = jiggle(X), jiggle(Y)
    r_grid = np.linspace(0, 0.75, 751)
    d = iecp.intersection_profile([X, Y], r_grid)
    dp = iecp.intersection_profile([Xp, Yp], r_grid)
    fig, ax = plt.subplots(figsize=(8.2, 3.3))
    diff = d != dp
    ax.fill_between(r_grid, -1, 1 + max(d.max(), dp.max()), where=diff, color=RULE, alpha=0.55, lw=0, step="post")
    ax.step(r_grid, d, where="post", color=OX, lw=1.7, label="two crossing rings")
    ax.step(r_grid, dp, where="post", color=INK, lw=1.1, ls="--", label="every point moved by at most $\\epsilon$")
    ax.set_ylim(-0.5, max(d.max(), dp.max()) + 1)
    ax.set_xlabel("scale $r$"); ax.set_ylabel(r"$\Delta\chi(r)$")
    ax.legend(fontsize=12, loc="upper right")
    ax.text(0.99, 0.66, "shaded: where the two differ", transform=ax.transAxes, fontsize=11, color=PENCIL, style="italic", ha="right")
    ins = fig.add_axes([0.33, 0.52, 0.17, 0.42])
    ins.scatter(X[:, 0], X[:, 1], s=2, color=OX, lw=0); ins.scatter(Y[:, 0], Y[:, 1], s=2, color=INK, lw=0)
    ins.set_aspect("equal"); ins.axis("off")
    print("  stability: profiles differ on", round(diff.mean() * 100, 1), "% of the grid; max value", d.max())
    _save(fig, "stability.svg")


def _e2_finals():
    from experiments.common import CONFIGS, checkpoint_epochs
    base = os.path.join(MIXUP, "disentangle", "results", "measure")
    finals = {}
    for c in [c for c in CONFIGS if c.tag == "e2"]:
        e = checkpoint_epochs(c)[-1]
        p = os.path.join(base, f"{c.name}_epoch{e}.json")
        if os.path.exists(p):
            finals[c.name] = json.load(open(p))
    return finals


def _arch(name):
    a = "ViT-Tiny" if "vit8" in name else "ResNet-56"
    return a + (", CIFAR-100 subset" if "cifar100s" in name else ", CIFAR-10")


def fig_depth():
    finals = _e2_finals()
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    cols = {"ResNet-56, CIFAR-10": OX, "ResNet-56, CIFAR-100 subset": SEPIA, "ViT-Tiny, CIFAR-10": INK}
    marks = {"ResNet-56, CIFAR-10": "o", "ResNet-56, CIFAR-100 subset": "s", "ViT-Tiny, CIFAR-10": "^"}
    for name, rec in finals.items():
        L = list(rec["layers"])
        ys = [np.mean([p["quotient"] for p in rec["layers"][l]["pairs"].values()]) for l in L]
        lab = _arch(name)
        ax.plot(range(len(L)), ys, marker=marks[lab], color=cols[lab], lw=1.6, ms=6, label=lab)
        print("  depth:", lab, [round(y, 2) for y in ys])
    ax.axhline(1, color=RULE, lw=1, ls=":")
    ax.text(4.05, 1.0, "exchangeable", fontsize=11, color=PENCIL, va="center", style="italic")
    ax.set_xticks(range(5)); ax.set_xticklabels(["stem", "stage 1", "stage 2", "stage 3", "penultimate"], fontsize=12)
    ax.set_xlabel("depth  (ResNet stage / ViT block 2, 4, 6, 8)")
    ax.set_ylabel(r"mean pairwise quotient $\widehat E_\ell$")
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=11, loc="lower left")
    _save(fig, "depth.svg")


def fig_triples():
    from itertools import combinations
    finals = _e2_finals()
    rows = []
    for name, rec in finals.items():
        for layer, trips in rec.get("triples", {}).items():
            pairs = rec["layers"][layer]["pairs"]
            # all 120 triples per layer (the paper's full scan): the escalated
            # quotient where the triple was escalated, the screening one otherwise
            for t in trips:
                cs = sorted(map(int, t["triple"].split(",")))
                pq = [pairs[f"{a},{b}"]["quotient"] for a, b in combinations(cs, 2) if f"{a},{b}" in pairs]
                if pq and max(pq) > 0:
                    rows.append((name, layer, t.get("headline_quotient", t["quotient"]) / max(pq)))
    cells = {}
    for n, l, v in rows:
        cells.setdefault((n, l), []).append(v)
    for k in [k for k in cells if k[1] == "penult" and (k[0], "stage3") in cells]:
        del cells[k]
    order = ["stem", "stage1", "stage2", "stage3", "block2", "block4", "block6", "block8", "penult"]
    keys = sorted(cells, key=lambda k: ("vit" in k[0], "cifar100s" not in k[0], order.index(k[1]) if k[1] in order else 99))
    null = json.load(open(os.path.join(MIXUP, "disentangle", "results", "dominance_null.json")))
    meds = [c["median_ratio"] for c in null["gauss"] + null["shuffle"]]
    allv = np.concatenate([cells[k] for k in keys])
    print(f"  triples: {len(allv)} triple-layer values in {len(keys)} cells, at or below 1: {int(np.sum(allv <= 1))} ({np.mean(allv <= 1):.3f}), median {np.median(allv):.3f}; null medians {min(meds):.2f}-{max(meds):.2f}")
    fig, ax = plt.subplots(figsize=(9.6, 3.7))
    ax.axhspan(min(meds), max(meds), color=RULE, alpha=0.45, lw=0)
    ax.text(len(keys) - 0.4, max(meds) + 0.02, "null-floor medians", fontsize=11, ha="right", color=PENCIL, style="italic")
    ax.axhline(1.0, color=SEPIA, lw=0.8, ls=":")
    rng = np.random.default_rng(0)
    groups = []
    for x, k in enumerate(keys):
        v = np.array(cells[k])
        col = INK if "vit" in k[0] else (SEPIA if "cifar100s" in k[0] else OX)
        ax.scatter(x + rng.uniform(-0.2, 0.2, len(v)), v, s=6, color=col, alpha=0.35, lw=0)
        ax.plot([x - 0.27, x + 0.27], [np.median(v)] * 2, color=INK, lw=1.8)
        g = _arch(k[0])
        if not groups or groups[-1][0] != g:
            groups.append([g, x, x])
        groups[-1][2] = x
    top = ax.get_ylim()[1]
    for g, a, b in groups:
        ax.text((a + b) / 2, top + 0.02, g, fontsize=11.5, ha="center", va="bottom", color=SEPIA, style="italic")
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([k[1].replace("stage", "stage ").replace("block", "block ").replace("penult", "penult.") for k in keys],
                       fontsize=10.5, rotation=40, ha="right")
    ax.set_ylabel("triple / strongest pair")
    _save(fig, "triples.svg")


# --------------------------------------------------------------------------
# section plates and the title plate
# --------------------------------------------------------------------------
def _poly_path(xs, ys, sx, sy, x0, y0):
    return " ".join(f"{'M' if i == 0 else 'L'} {f(x0 + sx * x)} {f(y0 - sy * y)}" for i, (x, y) in enumerate(zip(xs, ys)))


def plate_i():
    """Two ball unions and their lens, the overlap Euler calculus counts."""
    art = ['<defs><clipPath id="cA"><circle cx="320" cy="215" r="78"/></clipPath></defs>',
           circle((320, 215), 78, fill=OX, fill_opacity=0.10, stroke=OX, stroke_width=1.2),
           circle((410, 215), 78, fill=INK, fill_opacity=0.08, stroke=INK, stroke_width=1.2),
           '<g clip-path="url(#cA)">' + circle((410, 215), 78, fill=OX, fill_opacity=0.75) + '</g>',
           text((365, 222), "χ = 1", 15, fill=PAPER, italic=True),
           text((262, 222), "A", 18, fill=OX), text((468, 222), "B", 18, fill=INK)]
    write("section-i-plate.svg", plate(
        "EULER CALCULUS", "— the overlap of the ball unions, counted by Euler —",
        "— TWO BALL UNIONS AND THEIR OVERLAP —", art, "Section I plate"))


def plate_ii():
    """The profile as a running sum: two step curves, equal off critical scales."""
    rng = np.random.default_rng(7)
    X = _ring(rng, (-0.7, 0), 1.25, 0.05, 140); Y = _ring(rng, (0.7, 0), 1.25, 0.05, 140)
    r = np.linspace(0.0, 0.72, 361)
    d = iecp.intersection_profile([X, Y], r)
    xs, ys = [], []
    for i in range(len(r)):
        if i and d[i] != d[i - 1]:
            xs.append(r[i]); ys.append(d[i - 1])
        xs.append(r[i]); ys.append(d[i])
    art = [line((150, 300), (590, 300), stroke=RULE, stroke_width=0.8),
           f'<path d="{_poly_path(xs, ys, 600, 26, 150, 300)}" fill="none" stroke="{OX}" stroke-width="1.6"/>']
    write("section-ii-plate.svg", plate(
        "COMPUTATION AND STABILITY", "— a running sum over sorted simplices —",
        "— EQUAL OFF THE CRITICAL SCALES —", art, "Section II plate"))


def plate_iii():
    """An observed profile below its permutation band: certified separation."""
    rng = np.random.default_rng(11)
    X = _blob(rng, (-0.55, 0), 0.4, 60); Y = _blob(rng, (0.55, 0), 0.4, 60)
    r = np.linspace(0, 0.5, 101)
    d = iecp.intersection_profile([X, Y], r)
    Z = np.r_[X, Y]; perms = []
    for _ in range(99):
        idx = rng.permutation(len(Z))
        perms.append(iecp.intersection_profile([Z[idx[:60]], Z[idx[60:]]], r))
    perms = np.array(perms)
    lo, hi = np.percentile(perms, 5, axis=0), np.percentile(perms, 95, axis=0)
    sx, sy, x0, y0 = 860, 190 / max(hi.max(), d.max(), 1), 150, 300
    band = [(x0 + sx * a, y0 - sy * b) for a, b in zip(r, hi)] + [(x0 + sx * a, y0 - sy * b) for a, b in zip(r[::-1], lo[::-1])]
    art = [poly(band, fill=RULE, fill_opacity=0.55, stroke="none"),
           line((150, 300), (590, 300), stroke=RULE, stroke_width=0.8),
           f'<path d="{_poly_path(r, d, sx, sy, x0, y0)}" fill="none" stroke="{OX}" stroke-width="1.6"/>']
    write("section-iii-plate.svg", plate(
        "CERTIFIED INTERACTION", "— the observed profile against its permutation band —",
        "— EVERY NUMBER CARRIES A TEST —", art, "Section III plate"))


def title_plate():
    rng = np.random.default_rng(3)
    X = _ring(rng, (0, 0), 1.55, 0.12, 110); Y = _blob(rng, (0, 0), 0.30, 70)
    fig, ax = plt.subplots(figsize=(3, 3))
    _draw_overlap(ax, X, Y, 0.7)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-2.4, 2.4); ax.set_aspect("equal"); ax.axis("off")
    _save(fig, "title-plate.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_trio()
    fig_stability()
    fig_depth()
    fig_triples()
    plate_i()
    plate_ii()
    plate_iii()
    title_plate()

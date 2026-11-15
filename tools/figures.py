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
import gudhi as gd
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
from intersection_ecp import core as iecp_core


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


def fig_reading():
    """'Reading a profile': the three configurations of fig_trio, with the four readings
    numbered on the computed curves: first contact, the small-scale burst, the plateau,
    and a zero after contact."""
    rng = np.random.default_rng(3)
    configs = [
        ("separated", _blob(rng, (-1.5, 0), 0.32, 70), _blob(rng, (1.5, 0), 0.32, 70)),
        ("overlapping", _blob(rng, (-0.45, 0), 0.32, 70), _blob(rng, (0.45, 0), 0.32, 70)),
        ("encircling", _ring(rng, (0, 0), 1.55, 0.12, 110), _blob(rng, (0, 0), 0.30, 70)),
    ]
    r_grid = np.linspace(0, 1.2, 481)
    r_show = 0.7
    fig = plt.figure(figsize=(8.6, 6.0))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.05], hspace=0.3, wspace=0.06)
    styles = {"separated": (PENCIL, "--"), "overlapping": (OX, "-"), "encircling": (INK, "-.")}
    axp = fig.add_subplot(gs[1, :])
    prof, rstar = {}, {}
    for j, (name, X, Y) in enumerate(configs):
        ax = fig.add_subplot(gs[0, j])
        _draw_overlap(ax, X, Y, r_show, lim=3.1)
        ax.set_xlim(-3.05, 3.05); ax.set_ylim(-2.45, 2.45); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(name, fontsize=15, style="italic", color=SEPIA)
        prof[name] = iecp.intersection_profile([X, Y], r_grid)
        rstar[name] = iecp.first_interaction_scale([X, Y])
        col, ls = styles[name]
        axp.step(r_grid, prof[name], where="post", color=col, ls=ls, lw=1.6, label=name)
    axp.axvline(r_show, color=RULE, lw=1)
    axp.text(r_show + 0.01, axp.get_ylim()[1] * 0.93, "scale shown above", fontsize=10.5, color=PENCIL, style="italic", va="top")

    def badge(n, xy, off):
        axp.annotate(str(n), xy=xy, xytext=off, textcoords="offset points", ha="center", va="center", fontsize=12,
                     color=OX, bbox=dict(boxstyle="circle,pad=0.25", fc=PAPER, ec=OX, lw=1),
                     arrowprops=dict(arrowstyle="-", color=OX, lw=0.8, shrinkA=0, shrinkB=2))
    d_ov, d_en = prof["overlapping"], prof["encircling"]
    small = r_grid < 0.25
    i_peak = int(np.argmax(np.where(small, d_ov, -99)))
    after = np.flatnonzero((r_grid > rstar["encircling"]) & (d_en == 0))
    r_zero = r_grid[after[after.size // 2]] if after.size else 1.0
    badge(1, (rstar["separated"], 1), (0, 26))
    badge(2, (r_grid[i_peak], d_ov[i_peak]), (22, 6))
    badge(3, (0.3, 1), (0, 26))
    badge(4, (r_zero, 0), (0, -26))
    axp.set_ylim(-1.6, axp.get_ylim()[1])
    axp.set_xlabel("scale $r$", fontsize=13)
    axp.set_ylabel(r"$\Delta\chi(r)$", fontsize=14)
    axp.legend(fontsize=11.5, loc="upper right", bbox_to_anchor=(1.0, 0.8))
    print(f"  reading: r* separated {rstar['separated']:.3f}, burst peak {d_ov[i_peak]} at r={r_grid[i_peak]:.3f}, "
          f"encircling r* {rstar['encircling']:.3f}, zero marked at r={r_zero:.3f}, value there {int(d_en[np.searchsorted(r_grid, r_zero)])}")
    _save(fig, "reading.svg")


def fig_stability():
    """Two crossing rings and a Hausdorff perturbation: equal off critical scales. Two frames on
    identical axes: stability-1.svg (the rings and their profile), stability-2.svg (adds the moved
    rings, their profile, and the strips where the two differ); stability.svg = frame 2."""
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
    diff = d != dp
    top = max(d.max(), dp.max())
    # exact L1 and a certified bar count: evaluate both profiles on every interval between
    # entry radii of the six Alpha complexes; each bar moves the profile by at most 2 in total,
    # so N >= TV/2 and the theorem's bound 2 eps (N + N') >= eps (TV + TV').
    from scipy.spatial.distance import directed_hausdorff
    def _ev(A, B):
        ev = set()
        for P in (A, B, np.r_[A, B]):
            ev |= {np.sqrt(f_) for _, f_ in gd.AlphaComplex(points=P, precision="exact").create_simplex_tree().get_filtration()}
        return ev
    E = np.array(sorted(_ev(X, Y) | _ev(Xp, Yp) | {0.0}))
    mid = np.r_[(E[:-1] + E[1:]) / 2, E[-1] + 1.0]
    de, dpe = iecp.intersection_profile([X, Y], mid), iecp.intersection_profile([Xp, Yp], mid)
    L1 = float((np.abs(de - dpe) * np.r_[np.diff(E), 0.0]).sum())
    eps_h = max(max(directed_hausdorff(A, B)[0], directed_hausdorff(B, A)[0]) for A, B in ((X, Xp), (Y, Yp)))
    TV = np.abs(np.diff(np.r_[0, de])).sum() + np.abs(np.diff(np.r_[0, dpe])).sum()
    bound = eps_h * TV
    print(f"  stability numbers: eps {eps_h:.4f}, L1 {L1:.4f}, N+N' >= {TV // 2}, bound >= {bound:.2f}")
    for frame in (1, 2):
        fig, ax = plt.subplots(figsize=(8.2, 3.3))
        if frame == 2:
            ax.fill_between(r_grid, -1, 1 + top, where=diff, color=RULE, alpha=0.55, lw=0, step="post")
        ax.step(r_grid, d, where="post", color=OX, lw=1.7, label="two crossing rings")
        # frame 1 draws the moved profile invisibly, so the legend box is the same in both frames
        ax.step(r_grid, dp, where="post", color=INK if frame == 2 else "none", lw=1.1, ls="--",
                label="every point moved by at most $\\epsilon$")
        ax.set_xlim(-0.0375, 0.7875); ax.set_ylim(-0.5, top + 1)
        ax.set_xlabel("scale $r$"); ax.set_ylabel(r"$\Delta\chi(r)$")
        leg = ax.legend(fontsize=12, loc="upper right")
        if frame == 1:
            leg.get_texts()[1].set_color("none"); leg.legend_handles[1].set_color("none")
        if frame == 2:
            ax.text(0.99, 0.66, "shaded: where the two differ", transform=ax.transAxes, fontsize=11, color=PENCIL, style="italic", ha="right")
        # the numbers, exact over all event radii (computed below); invisible in frame 1 to keep the bounding box
        ax.text(0.99, 0.555, f"ε = {eps_h:.2f}:  L¹ = {L1:.2f},  bound 2ε(N + N′) ≥ {bound:.1f}",
                transform=ax.transAxes, fontsize=12, color=OX if frame == 2 else "none", ha="right", style="italic")
        for k, (A, B, lab) in enumerate(((X, Y, "the rings"), (Xp, Yp, "moved by $\\leq\\epsilon$"))):
            ghost = k == 1 and frame == 1          # drawn invisibly so both frames share one bounding box
            ins = fig.add_axes([0.262 + 0.118 * k, 0.53, 0.12, 0.36])
            ins.scatter(A[:, 0], A[:, 1], s=2, color="none" if ghost else OX, lw=0)
            ins.scatter(B[:, 0], B[:, 1], s=2, color="none" if ghost else INK, lw=0)
            ins.set_aspect("equal"); ins.axis("off")
            ins.set_title(lab, fontsize=10, color="none" if ghost else PENCIL, style="italic", pad=1)
        _save(fig, f"stability-{frame}.svg")
        if frame == 2:
            _save(fig, "stability.svg")
    print("  stability: profiles differ on", round(diff.mean() * 100, 1), "% of the grid; max value", d.max())


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
    fig, ax = plt.subplots(figsize=(6.0, 2.92))
    cols = {"ResNet-56, CIFAR-10": OX, "ResNet-56, CIFAR-100 subset": SEPIA, "ViT-Tiny, CIFAR-10": INK}
    marks = {"ResNet-56, CIFAR-10": "o", "ResNet-56, CIFAR-100 subset": "s", "ViT-Tiny, CIFAR-10": "^"}
    for name, rec in finals.items():
        L = list(rec["layers"])
        ys = [np.mean([p["quotient"] for p in rec["layers"][l]["pairs"].values()]) for l in L]
        lab = _arch(name)
        ax.plot(range(len(L)), ys, marker=marks[lab], color=cols[lab], lw=1.6, ms=6, label=lab)
        print("  depth:", lab, [round(y, 2) for y in ys])
    ax.axhline(1, color=RULE, lw=1, ls=":")
    ax.text(4.05, 1.0, "random labels", fontsize=11, color=PENCIL, va="center", style="italic")
    ax.set_xticks(range(5))
    ax.set_xticklabels(["1", "2", "3", "4", "5"], fontsize=11.5)
    ax.set_xlabel("layer, from input (left) to the last before the output (right)")
    ax.set_ylabel(r"mean pairwise quotient $\widehat E_\ell$")
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, handlelength=1.6, columnspacing=1.2)
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


def _bars(P):
    import gudhi
    st = gudhi.AlphaComplex(points=P).create_simplex_tree()
    st.compute_persistence()
    return [(d, np.sqrt(b), np.sqrt(e) if np.isfinite(e) else np.inf) for d, (b, e) in st.persistence()]


def _draw_barcode(ax, bars, rmax, ref=None, min_len=(0.15, 0.1)):
    """Long H0 bars (merges) in sepia and H1 bars in oxblood, one label per degree;
    bars absent from ref (the barcode of X alone) are drawn bold."""
    keep = [b for b in bars if b[0] <= 1 and (min(b[2], rmax) - b[1]) > min_len[b[0]]]
    keep.sort(key=lambda b: (b[0], b[1], -min(b[2], rmax)))
    key = lambda d, b, e: (d, round(b, 2), round(e, 2) if np.isfinite(e) else e)
    refset = {key(*x) for x in (ref or [])}
    rows = {0: [], 1: []}
    for y, (d, b, e) in enumerate(keep):
        new = ref is not None and key(d, b, e) not in refset
        ax.plot([b, min(e, rmax)], [y, y], color=OX if d == 1 else SEPIA, lw=4 if new else 1.8,
                solid_capstyle="butt")
        rows[d].append(y)
    for dgr, ys in rows.items():
        if ys:
            ax.text(-0.04, np.mean(ys), f"$H_{dgr}$", ha="right", va="center", fontsize=11, color=PENCIL)
    ax.set_xlim(-0.16, rmax); ax.set_ylim(-0.8, max(len(keep), 2) - 0.2)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)


def fig_approach():
    """A blob Y approaches a ring X: barcode of X, barcode of X u Y, and the overlap profile."""
    rng = np.random.default_rng(5)
    X = _ring(rng, (0, 0), 1.5, 0.1, 120)
    Yb = _blob(rng, (0, 0), 0.28, 60)
    rmax, r_show = 1.6, 0.42
    r = np.linspace(0, rmax, 321)
    bx = _bars(X)
    frames = [("far apart", (4.3, 0)), ("touching", (2.55, 0)), ("inside the hole", (0, 0))]
    for i, (label, c) in enumerate(frames, 1):
        Y = Yb + np.array(c)
        bu = _bars(np.r_[X, Y])
        d = iecp.intersection_profile([X, Y], r)
        fig = plt.figure(figsize=(11, 3.9))
        gs = fig.add_gridspec(3, 2, width_ratios=[1.35, 1.5], hspace=0.75, wspace=0.08)
        ax = fig.add_subplot(gs[:, 0])
        _draw_overlap(ax, X, Y, r_show, lim=5.0)
        ax.set_xlim(-2.2, 5.0); ax.set_ylim(-2.3, 2.3); ax.set_aspect("equal"); ax.axis("off")
        ax.text(-1.95, 1.75, "$X$", color=OX, fontsize=16); ax.text(c[0] + 0.5, c[1] + 0.5, "$Y$", color=INK, fontsize=16)
        ax.set_title(label, fontsize=15, style="italic", color=SEPIA)
        a1 = fig.add_subplot(gs[0, 1]); _draw_barcode(a1, bx, rmax)
        a1.set_title("barcode of $X$", fontsize=12, loc="left", color=SEPIA)
        a2 = fig.add_subplot(gs[1, 1]); _draw_barcode(a2, bu, rmax, ref=bx)
        a2.set_title(r"barcode of $X\cup Y$  (bold: not in $X$'s)", fontsize=12, loc="left", color=SEPIA)
        a3 = fig.add_subplot(gs[2, 1])
        a3.step(r, d, where="post", color=OX, lw=1.6)
        a3.set_xlim(-0.12, rmax); a3.set_ylim(-0.5, 7)
        a3.set_title(r"the overlap: $\Delta\chi(r)$", fontsize=12, loc="left", color=SEPIA)
        a3.set_xlabel("scale $r$", fontsize=11)
        for a in (a1, a2, a3):
            a.tick_params(labelsize=10)
        _save(fig, f"approach-{i}.svg")


def _signed_births(P):
    """(birth radius, sign) of every simplex of the Alpha complex of P."""
    import gudhi
    st = gudhi.AlphaComplex(points=P, precision="fast").create_simplex_tree()
    out = [(np.sqrt(max(v, 0.0)), (-1) ** (len(s) - 1)) for s, v in st.get_filtration()]
    return np.array(out)


def fig_sweep():
    """Theorem 3 in a picture: chi_X + chi_Y against chi_{X u Y}; the gap is Delta chi.

    The ring and blob of the opener's last frame.  Each Euler characteristic
    curve is a running sum of signs over the Alpha complex's simplices in birth
    order; the strip shows those signs for X u Y.
    """
    rng = np.random.default_rng(5)
    X = _ring(rng, (0, 0), 1.5, 0.1, 120)
    Y = _blob(rng, (0, 0), 0.28, 60)
    rmax = 1.6
    r = np.linspace(0, rmax, 641)
    cx, cy = iecp_core.ecc_alpha(X, r), iecp_core.ecc_alpha(Y, r)
    cu = iecp_core.ecc_alpha(np.r_[X, Y], r)
    d = cx + cy - cu
    assert np.array_equal(d, iecp.intersection_profile([X, Y], r))
    sb = _signed_births(np.r_[X, Y])
    sb = sb[sb[:, 0] > 0]                       # vertices are all born at 0

    fig = plt.figure(figsize=(7.0, 4.1))
    gs = fig.add_gridspec(3, 2, width_ratios=[0.9, 3.0], height_ratios=[2.1, 0.42, 1.25],
                          hspace=0.16, wspace=0.1)
    ins = fig.add_subplot(gs[:2, 0])
    ins.scatter(X[:, 0], X[:, 1], s=3, color=OX, lw=0); ins.scatter(Y[:, 0], Y[:, 1], s=3, color=INK, lw=0)
    ins.text(-1.55, 1.45, "$X$", color=OX, fontsize=15); ins.text(0.0, -0.95, "$Y$", color=INK, fontsize=15, ha="center")
    ins.set_xlim(-1.8, 1.8); ins.set_ylim(-1.8, 1.8); ins.set_aspect("equal"); ins.axis("off")

    top = 9
    a1 = fig.add_subplot(gs[0, 1])
    a1.fill_between(r, cx + cy, cu, step="post", color=OX, alpha=0.22, lw=0)
    a1.step(r, cx + cy, where="post", color=OX, lw=1.6, label=r"$\chi_X+\chi_Y$")
    a1.step(r, cu, where="post", color=INK, lw=1.2, ls="--", label=r"$\chi_{X\cup Y}$")
    a1.set_ylim(-6, top); a1.set_xlim(0, rmax)
    a1.legend(fontsize=12, loc="lower right")
    a1.annotate(f"both start at $|X|+|Y|={len(X) + len(Y)}$", xy=(0.14, top - 0.3), xytext=(0.62, 6.2),
                fontsize=11, color=PENCIL, style="italic", va="center",
                arrowprops=dict(arrowstyle="-", color=PENCIL, lw=0.7))
    a1.text(0.555, -5.2, "loops in the gap", fontsize=11, color=OX, style="italic", ha="left", va="bottom")
    a1.text(1.42, 2.6, "the ring fills", fontsize=11, color=OX, style="italic", ha="left", va="bottom")
    a1.tick_params(labelbottom=False, labelsize=10)
    a1.set_ylabel(r"$\chi$", fontsize=13)

    a2 = fig.add_subplot(gs[1, 1], sharex=a1)
    up, dn = sb[sb[:, 1] > 0, 0], sb[sb[:, 1] < 0, 0]
    a2.vlines(up, 0, 1, color=SEPIA, lw=0.35, alpha=0.7)
    a2.vlines(dn, -1, 0, color=OX, lw=0.35, alpha=0.7)
    a2.axhline(0, color=RULE, lw=0.6)
    a2.set_ylim(-1.15, 1.15); a2.set_yticks([])
    for s in ("left", "bottom"):
        a2.spines[s].set_visible(False)
    a2.tick_params(bottom=False, labelbottom=False)
    a2.text(rmax, 0.55, "triangles $+1$", fontsize=10.5, color=SEPIA, style="italic", ha="right", va="center")
    a2.text(rmax, -0.55, "edges $-1$", fontsize=10.5, color=OX, style="italic", ha="right", va="center")
    a2.set_ylabel("entry radii", fontsize=11, rotation=0, ha="right", va="center", color=PENCIL)

    a3 = fig.add_subplot(gs[2, 1], sharex=a1)
    a3.fill_between(r, 0, d, step="post", color=OX, alpha=0.22, lw=0)
    a3.step(r, d, where="post", color=OX, lw=1.6)
    a3.set_ylim(-0.8, max(d.max(), 1) + 1.5)
    a3.set_ylabel(r"$\Delta\chi$", fontsize=13)
    a3.set_xlabel("scale $r$", fontsize=12)
    a3.tick_params(labelsize=10)
    a3.text(0.012, a3.get_ylim()[1] - 0.3, "the gap above", fontsize=11, color=PENCIL, style="italic", va="top")
    print("  sweep:", len(sb), "simplices of positive birth; max Delta chi", d.max())
    _save(fig, "sweep.svg")


def fig_permtest():
    """Proposition 3 in a picture: the observed profile against its relabelings,
    and the statistic against its permutation distribution."""
    rng = np.random.default_rng(11)
    X = _blob(rng, (-0.6, 0), 0.4, 60); Y = _blob(rng, (0.6, 0), 0.4, 60)
    r = iecp_core.default_r_grid([X, Y], num=200)
    B = 999
    Z = np.r_[X, Y]
    cache = {(0, 1): iecp_core.ecc_alpha(Z, r)}
    d = iecp.intersection_profile([X, Y], r, _cache=dict(cache))
    T = iecp.profile_stat(d, r, "int")
    prof, Tp = [], np.empty(B)
    for b in range(B):
        idx = rng.permutation(len(Z))
        dp = iecp.intersection_profile([Z[idx[:60]], Z[idx[60:]]], r, _cache=dict(cache))
        prof.append(dp); Tp[b] = iecp.profile_stat(dp, r, "int")
    prof = np.array(prof)
    p_down = (1 + np.sum(Tp <= T)) / (1 + B)
    E = T / Tp.mean()
    lo, hi = np.percentile(prof, 5, axis=0), np.percentile(prof, 95, axis=0)
    med = np.median(prof, axis=0)

    fig = plt.figure(figsize=(7.0, 3.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.7, 1.0], wspace=0.28)
    a1 = fig.add_subplot(gs[0, 0])
    a1.fill_between(r, lo, hi, step="post", color=RULE, alpha=0.6, lw=0, label="relabelings, 5–95%")
    a1.step(r, med, where="post", color=SEPIA, lw=0.9, ls=":", label="relabelings, median")
    a1.step(r, d, where="post", color=OX, lw=1.7, label="observed")
    a1.set_xlim(0, r[-1]); a1.set_ylim(-1.5, hi.max() + 2)
    a1.set_xlabel("scale $r$", fontsize=12); a1.set_ylabel(r"$\Delta\chi(r)$", fontsize=13)
    a1.legend(fontsize=11, loc="upper right")
    a1.tick_params(labelsize=10)
    ins = fig.add_axes([0.42, 0.24, 0.15, 0.3])
    ins.scatter(X[:, 0], X[:, 1], s=2.5, color=OX, lw=0); ins.scatter(Y[:, 0], Y[:, 1], s=2.5, color=INK, lw=0)
    ins.set_aspect("equal"); ins.axis("off")

    a2 = fig.add_subplot(gs[0, 1])
    a2.hist(Tp, bins=32, color=RULE, edgecolor=PAPER, lw=0.4)
    a2.axvline(T, color=OX, lw=1.8)
    a2.axvline(Tp.mean(), color=SEPIA, lw=0.9, ls=":")
    ytop = a2.get_ylim()[1]
    a2.annotate("observed", (T, ytop * 0.98), xytext=(5, 0), textcoords="offset points", color=OX, fontsize=11, style="italic", va="top")
    a2.text(Tp.mean(), ytop * 1.02, r"$\overline{\Phi}_B$", color=SEPIA, fontsize=11, ha="center", va="bottom")
    pstr = f"{p_down:.3f}" if p_down >= 0.001 else "0.001"
    a2.text(0.1, 0.62, rf"$\widehat E = {E:.2f}$" + "\n" + rf"$p_{{\downarrow}} = {pstr}$" + "\n" + rf"$B = {B}$",
            transform=a2.transAxes, ha="left", va="top", fontsize=12.5, color=INK, linespacing=1.5)
    a2.set_xlabel(r"$\Phi = \int|\Delta\chi|\,dr$", fontsize=12)
    a2.set_yticks([]); a2.spines["left"].set_visible(False)
    a2.tick_params(labelsize=10)
    print(f"  permtest: T={T:.4f} null mean={Tp.mean():.4f} E={E:.3f} p_down={p_down:.4f} min Tp={Tp.min():.4f}")
    _save(fig, "permtest.svg")


def fig_memo():
    """Memorization (arXiv:2610.00251): the measured profiles of two CIFAR-10 DDPMs,
    generations against training images and against held-out images, re-plotted
    from mixup-ecp/disentangle/results/genmem in the deck's palette."""
    gm = os.path.join(MIXUP, "disentangle", "results", "genmem")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9))
    fig.subplots_adjust(wspace=0.32)
    for ax, (name, lab) in zip(axes, (("memo200", "memorizer, 200 training images"),
                                      ("full50k", "control, 50,000 training images"))):
        d = json.load(open(os.path.join(gm, f"{name}_full_measure.json")))
        g = np.array(d["r_grid"]); tr = np.array(d["dchi_tr"]); ho = np.array(d["dchi_ho"]); r0 = d["r0"]
        ax.axvspan(0, r0, color=RULE, alpha=0.35, lw=0)
        ax.plot(g, tr, color=OX, lw=1.6, label=r"$\Delta\chi(r;G,T)$, training")
        ax.plot(g, ho, color=INK, lw=1.1, ls="--", label=r"$\Delta\chi(r;G,H)$, held out")
        i = int(np.searchsorted(g, r0))
        ax.scatter([r0, r0], [tr[i], ho[i]], s=22, color=[OX, INK], zorder=4, lw=0)
        ax.text(0.97, 0.6, f"at $r_0$: {tr[i]} vs {ho[i]}", transform=ax.transAxes, fontsize=12,
                color=OX, ha="right", va="center")
        ax.text(r0 * 0.5, 0.04, "$r_0$", transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                fontsize=11, color=SEPIA)
        ax.set_xlim(0, g[-1] * 0.6)
        ax.set_title(lab, fontsize=12, style="italic", color=SEPIA)
        ax.set_xlabel("scale $r$", fontsize=11)
        ax.tick_params(labelsize=10)
        print(f"  memo: {name} r0={r0:.3f} at r0: {tr[i]} vs {ho[i]}")
    axes[0].set_ylabel(r"$\Delta\chi$  (overlap components)", fontsize=11)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=10.5, loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=2, handlelength=1.6)
    _save(fig, "memo.svg")


def fig_remains():
    """'What remains': the opener's ring X and blob Y.
    remains-annulus.svg: their overlap at r = s = 0.9, an annulus (beta_0 = beta_1 = 1, chi = 0).
    remains-surface.svg: the two-scale profile Delta chi(r, s), X at scale r and Y at scale s,
    by inclusion-exclusion with a weighted Alpha complex for the union term (the larger-scale
    cloud carries weight max^2 - min^2, evaluated at min); its diagonal is the talk's profile."""
    from matplotlib.colors import ListedColormap, BoundaryNorm
    rng = np.random.default_rng(5)
    X = _ring(rng, (0, 0), 1.5, 0.1, 120)
    Y = _blob(rng, (0, 0), 0.28, 60)
    rq = 0.9

    fig, ax = plt.subplots(figsize=(2.6, 2.6))
    _draw_overlap(ax, X, Y, rq, lim=2.4)
    ax.set_xlim(-2.4, 2.4); ax.set_ylim(-2.4, 2.4); ax.set_aspect("equal"); ax.axis("off")
    ax.text(-1.75, 1.75, "$X$", color=OX, fontsize=14); ax.text(0.25, 0.2, "$Y$", color=INK, fontsize=13)
    ax.text(0, -2.55, r"$r=s=0.9$: $\beta_0=\beta_1=1$, $\chi=0$", ha="center", va="top", fontsize=12, color=OX)
    d = int(iecp.intersection_profile([X, Y], np.array([rq]))[0])
    assert d == 0, d
    _save(fig, "remains-annulus.svg")

    g = np.linspace(0.02, 1.6, 100)
    cx, cy = iecp_core.ecc_alpha(X, g), iecp_core.ecc_alpha(Y, g)
    P, nX, nY = np.r_[X, Y], len(X), len(Y)
    D = np.zeros((len(g), len(g)), int)          # D[i, j] = Delta chi(X at g[i], Y at g[j])
    for i, r in enumerate(g):
        for j, t in enumerate(g):
            if t >= r:
                w, at = np.r_[np.zeros(nX), np.full(nY, t * t - r * r)], r
            else:
                w, at = np.r_[np.full(nX, r * r - t * t), np.zeros(nY)], t
            D[i, j] = cx[i] + cy[j] - iecp_core.ecc_alpha(P, np.array([at]), weights=w)[0]
    assert np.array_equal(np.diag(D), iecp.intersection_profile([X, Y], g))
    bounds = [-100, -0.5, 0.5, 1.5, 3.5, 7.5, 1000]
    cmap = ListedColormap([SEPIA, PAPER_SOFT, "#e3c3bb", "#c98a80", "#9c4a42", OX])
    fig, ax = plt.subplots(figsize=(3.6, 3.1))
    m = ax.pcolormesh(g, g, D.T, cmap=cmap, norm=BoundaryNorm(bounds, cmap.N), shading="nearest", rasterized=True)
    ax.plot(g, g, color=INK, lw=1.0, ls="--")
    ax.text(1.0, 1.42, "the diagonal\nof this talk", fontsize=10, color=INK, style="italic", ha="center", va="center")
    ax.scatter([rq], [rq], s=26, color=OX, zorder=4, edgecolor=PAPER, lw=0.8)
    ax.text(0.72, 1.12, "$\\chi=0$, yet\nthey meet", fontsize=10.5, color=SEPIA, style="italic", ha="center", va="center")
    ax.text(1.5, 0.55, "ring\nfills", fontsize=10, color=SEPIA, style="italic", ha="center")
    ax.set_xlabel("$r$, scale of the ring $X$", fontsize=11); ax.set_ylabel("$s$, scale of the blob $Y$", fontsize=11)
    ax.set_xlim(g[0], g[-1]); ax.set_ylim(g[0], g[-1]); ax.set_aspect("equal")
    ax.tick_params(labelsize=9.5)
    cb = fig.colorbar(m, ax=ax, ticks=[-1, 0, 1, 2.5, 5.5, 9], fraction=0.045, pad=0.03)
    cb.ax.set_yticklabels(["< 0", "0", "1", "2–3", "4–7", "≥ 8"], fontsize=9)
    cb.outline.set_visible(False)
    cb.set_label(r"$\Delta\chi(r,s)$", fontsize=11)
    print("  remains: surface range", D.min(), D.max(), "; zero cells", int((D == 0).mean() * 100), "%")
    _save(fig, "remains-surface.svg")


def fig_profile_chi():
    """'The profile': three overlaps from the opener, labelled pieces minus holes."""
    rng = np.random.default_rng(5)
    X = _ring(rng, (0, 0), 1.5, 0.1, 120)
    Yb = _blob(rng, (0, 0), 0.28, 60)
    cases = [((2.55, 0), 0.3, (-1.95, 3.3), "1 piece"), ((0, 0), 0.45, (-2.4, 2.4), "4 pieces"),
             ((0, 0), 0.7, (-2.4, 2.4), "1 piece, 1 hole")]
    widths = [c[2][1] - c[2][0] for c in cases]
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 2.85), gridspec_kw=dict(width_ratios=widths, wspace=0.06))
    for ax, (c, r, xl, lab) in zip(axes, cases):
        Y = Yb + np.array(c)
        _draw_overlap(ax, X, Y, r, lim=3.4)
        ax.set_xlim(*xl); ax.set_ylim(-2.4, 2.4); ax.set_aspect("equal"); ax.axis("off")
        d = int(iecp.intersection_profile([X, Y], np.array([r]))[0])
        ax.text(np.mean(xl), -2.55, f"{lab}:  " + rf"$\chi = {d}$", ha="center", va="top", fontsize=14, color=OX)
        ax.text(np.mean(xl), 2.5, f"$r = {r}$", ha="center", va="bottom", fontsize=12, color=SEPIA, style="italic")
        print(f"  profile-chi: {lab} at r={r}: Delta chi = {d}")
    _save(fig, "profile-chi.svg")


# --------------------------------------------------------------------------
# the opener, animated: balls grow, a cursor sweeps the image barcode and the profile
# --------------------------------------------------------------------------
def _image_barcode(X, Y):
    """Image persistence of H_*(U(X;r)) -> H_*(U(X u Y;r)) on the chromatic Alpha filtration
    (chalc; filtration values are ball radii). Also returns X's own barcode for comparison."""
    import chalc.sixpack as sixpack
    P = np.r_[X, Y]
    d = sixpack.compute(P.T, [0] * len(X) + [1] * len(Y), sixpack.SubsetInclusion({0}),
                        filtration_algorithm="alpha", max_diagram_dimension=1)
    im0, im1 = d.get_matrix("im", [0, 1]); dom1 = d.get_matrix("dom", 1)
    return im0, im1, dom1


def fig_opener():
    """Three frames of the opener (Y far apart, touching, inside X's hole). Each is an inline SVG
    driven by assets/opener-anim.js: the balls grow with r, a cursor sweeps the image barcode
    of X inside X u Y, and the profile is drawn in as r grows. Written as assets/opener-k.md."""
    rng = np.random.default_rng(5)
    X = _ring(rng, (0, 0), 1.5, 0.1, 120)
    Yb = _blob(rng, (0, 0), 0.28, 60)
    RMAX, W, H = 1.6, 1180, 446
    LX0, LX1, LY0, LY1 = 10, 470, 34, 414                      # left panel, pixels
    xmin, xmax = -2.4, 5.6; sc = (LX1 - LX0) / (xmax - xmin); ymid = (LY0 + LY1) / 2
    px = lambda p: (LX0 + (p[0] - xmin) * sc, ymid - p[1] * sc)
    RX0, RX1 = 575, 1150; rx = lambda r: RX0 + (RX1 - RX0) * r / RMAX
    BT, BB = 62, 205                                            # barcode band
    CT, CB = 262, 382                                           # profile band
    grid = np.round(np.linspace(0, RMAX, 321), 4)
    frames = [("far apart", (4.3, 0)), ("touching", (2.55, 0)), ("inside the hole", (0, 0))]
    for k, (label, c) in enumerate(frames, 1):
        Y = Yb + np.array(c)
        d = iecp.intersection_profile([X, Y], grid)
        im0, im1, dom1 = _image_barcode(X, Y)
        vmin, vmax = -1, 7; cy = lambda v: CB - (v - vmin) * (CB - CT) / (vmax - vmin)
        o = [f'<svg class="opener-anim" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'data-scale="{sc:.4f}" data-rmax="{RMAX}" data-x0="{RX0}" data-x1="{RX1}" '
             f'data-dchi="{",".join(str(int(v)) for v in d)}" role="img" '
             f'aria-label="Opener, {label}: balls growing with r, the image barcode of X inside X union Y, and the profile">',
             f'<defs><clipPath id="op{k}-panel"><rect x="{LX0}" y="{LY0}" width="{LX1 - LX0}" height="{LY1 - LY0}"/></clipPath>',
             f'<clipPath id="op{k}-ux">'] + [f'<circle class="ball" cx="{px(p)[0]:.1f}" cy="{px(p)[1]:.1f}" r="0"/>' for p in X] + [
             '</clipPath>',
             f'<clipPath id="op{k}-prog"><rect class="prog" x="{RX0 - 2}" y="{CT - 10}" width="0" height="{CB - CT + 20}"/></clipPath></defs>']
        # left panel: growing unions, their overlap, the points
        o += [f'<g clip-path="url(#op{k}-panel)">',
              f'<g fill="{OX}" opacity="0.17">'] + [f'<circle class="ball" cx="{px(p)[0]:.1f}" cy="{px(p)[1]:.1f}" r="0"/>' for p in X] + ['</g>',
              f'<g fill="{INK}" opacity="0.14">'] + [f'<circle class="ball" cx="{px(p)[0]:.1f}" cy="{px(p)[1]:.1f}" r="0"/>' for p in Y] + ['</g>',
              f'<g fill="{OX}" opacity="0.88" clip-path="url(#op{k}-ux)">'] + [f'<circle class="ball" cx="{px(p)[0]:.1f}" cy="{px(p)[1]:.1f}" r="0"/>' for p in Y] + ['</g>',
              f'<g fill="{OX}">'] + [circle(px(p), 1.9) for p in X] + ['</g>',
              f'<g fill="{INK}">'] + [circle(px(p), 1.9) for p in Y] + ['</g>', '</g>']
        o += [text((px((-1.95, 1.75))[0], px((-1.95, 1.75))[1]), "X", 25, fill=OX),
              text((px((c[0] + 0.62, c[1] + 0.5))[0], px((c[0] + 0.62, c[1] + 0.5))[1]), "Y", 25, fill=INK),
              text((LX0 + (LX1 - LX0) / 2, 24), label, 24, fill=SEPIA),
              f'<text class="rlabel" x="{LX0 + 8}" y="{LY1 - 8}" fill="{INK}" font-family="{SERIF}" font-size="24" font-style="italic">r = 0.00</text>']
        # right top: image barcode of X inside X u Y
        o += [text((RX0, BT - 26), "X's features inside X ∪ Y", 21, fill=SEPIA, anchor="start", italic=True),
              text((RX1, BT - 26), "image of H(X) → H(X ∪ Y)", 16, fill=PENCIL, anchor="end", italic=True)]
        keep0 = sorted([b for b in im0 if min(b[1], RMAX) - b[0] > 0.12], key=lambda b: -min(b[1], 9))
        keep1 = [b for b in im1 if min(b[1], RMAX) - b[0] > 0.05]
        rows = len(keep1) + len(keep0) + (1 if len(keep1) else 0); step = (BB - BT) / max(rows, 1)
        yrow = BT + step / 2
        for b in keep1:
            ghost = [g for g in dom1 if abs(g[0] - b[0]) < 1e-6 and abs(g[1] - b[1]) > 1e-3]
            if ghost:
                g = ghost[0]
                o.append(line((rx(g[0]), yrow), (rx(min(g[1], RMAX)), yrow), stroke=OX, stroke_width=1.2,
                              stroke_dasharray="5 4", opacity=0.55))
                o.append(text((rx(min(g[1], RMAX)) + 6, yrow + 5), f"X alone: {g[1]:.2f}", 16, fill=PENCIL, anchor="start"))
                o.append(text((rx(min(b[1], RMAX)) + 6, yrow - 7), f"in X ∪ Y: {b[1]:.2f}", 16, fill=OX, anchor="start"))
            o.append(line((rx(b[0]), yrow), (rx(min(b[1], RMAX)), yrow), stroke=OX, stroke_width=4.5, stroke_linecap="butt"))
            yrow += step
        o.append(text((RX0 - 14, BT + step * (len(keep1) / 2) + 5), "H₁", 18, fill=PENCIL, anchor="end"))
        y0 = yrow + (step if len(keep1) else 0)
        yrow = y0
        for b in keep0:
            o.append(line((rx(b[0]), yrow), (rx(min(b[1], RMAX)), yrow), stroke=SEPIA, stroke_width=3, stroke_linecap="butt"))
            yrow += step
        o.append(text((RX0 - 14, (y0 + yrow - step) / 2 + 5), "H₀", 18, fill=PENCIL, anchor="end"))
        # right bottom: the profile, drawn in as r grows
        pts = []
        for i in range(len(grid)):
            if i and d[i] != d[i - 1]:
                pts.append((rx(grid[i]), cy(d[i - 1])))
            pts.append((rx(grid[i]), cy(d[i])))
        path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        o += [text((RX0, CT - 18), "the overlap: Δχ(r)", 21, fill=SEPIA, anchor="start", italic=True),
              line((RX0, cy(0)), (RX1, cy(0)), stroke=RULE, stroke_width=0.8),
              f'<path d="{path}" fill="none" stroke="{RULE}" stroke-width="1.3"/>',
              f'<path d="{path}" fill="none" stroke="{OX}" stroke-width="2.2" clip-path="url(#op{k}-prog)"/>',
              line((RX0, CB + 6), (RX1, CB + 6), stroke=SEPIA, stroke_width=0.8)]
        for v in (0, 5):
            o.append(text((RX0 - 10, cy(v) + 5), str(v), 16, fill=PENCIL, anchor="end", italic=False))
        for t in (0, 0.4, 0.8, 1.2, 1.6):
            o += [line((rx(t), CB + 6), (rx(t), CB + 11), stroke=SEPIA, stroke_width=0.8),
                  text((rx(t), CB + 27), f"{t:.1f}", 16, fill=SEPIA, italic=False)]
        o.append(text(((RX0 + RX1) / 2, CB + 52), "scale r", 18, fill=SEPIA))
        # the cursor and the readout
        o += [f'<line class="cursor" x1="{RX0}" y1="{BT - 12}" x2="{RX0}" y2="{CB + 6}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>',
              f'<circle class="cdot" cx="{RX0}" cy="{cy(0):.1f}" r="4.5" fill="{OX}" data-cy0="{CB}" data-cyscale="{(CB - CT) / (vmax - vmin):.4f}" data-vmin="{vmin}"/>',
              f'<text class="dlabel" x="{RX1}" y="{CT - 18}" fill="{OX}" font-family="{SERIF}" font-size="23" font-style="italic" text-anchor="end">Δχ = 0</text>',
              '</svg>']
        with open(os.path.join(OUT, f"opener-{k}.md"), "w") as fh:
            fh.write("```{=html}\n" + "\n".join(o) + "\n```\n")
        print(f"  opener {k} ({label}): image H1 {np.round(im1[(im1[:,1]-im1[:,0])>0.05],3).tolist()}, max dchi {d.max()}")


# --------------------------------------------------------------------------
# Proposition 2: the overlap is a union of lenses; its nerve has a simplex per common point
# --------------------------------------------------------------------------
def fig_nerve():
    """Two points of X, three of Y, radius t = 0.62. Left: the balls and the five lenses
    B(x,t) n B(y,t) whose union is the overlap. Right: their nerve, one vertex per lens, a
    simplex per common point. Four lenses share the centre: a 3-simplex, 2^4 - 1 = 15 faces.
    The fifth lens is apart: chi(overlap) = 1 + 1 = 2. Written as assets/nerve.svg."""
    import itertools
    X = np.array([[-0.55, 0.0], [0.55, 0.05]]); Y = np.array([[0.0, 0.55], [0.05, -0.5], [1.35, 0.4]]); t = 0.62
    L = [(i, j) for i in range(2) for j in range(3) if np.linalg.norm(X[i] - Y[j]) <= 2 * t]
    gx, gy = np.meshgrid(np.linspace(-1.3, 2.1, 680), np.linspace(-1.2, 1.2, 480)); G = np.c_[gx.ravel(), gy.ravel()]
    inl = np.stack([(np.linalg.norm(G - X[i], axis=1) <= t) & (np.linalg.norm(G - Y[j], axis=1) <= t) for i, j in L], 1)
    cent = np.array([G[inl[:, a]].mean(0) for a in range(len(L))])
    simp = {k: [c for c in itertools.combinations(range(len(L)), k) if inl[:, list(c)].all(1).any()] for k in (2, 3, 4)}
    W, H = 600, 214
    sc = 66.0; ox, oy = 95, 95
    P = lambda q: (ox + q[0] * sc, oy - q[1] * sc)
    o = ['<defs><clipPath id="nv-ux">'] + [circle(P(x), t * sc) for x in X] + ['</clipPath></defs>',
         f'<g fill="{OX}" opacity="0.13">'] + [circle(P(x), t * sc) for x in X] + ['</g>',
         f'<g fill="{INK}" opacity="0.10">'] + [circle(P(y), t * sc) for y in Y] + ['</g>',
         f'<g fill="{OX}" opacity="0.80" clip-path="url(#nv-ux)">'] + [circle(P(y), t * sc) for y in Y] + ['</g>']
    o += [circle(P(x), 3.2, fill=OX) for x in X] + [circle(P(y), 3.2, fill=INK) for y in Y]
    o += [text((P(X[0])[0] - 34, P(X[0])[1] - 40), "X", 24, fill=OX),
          text((P(Y[2])[0] + 34, P(Y[2])[1] - 32), "Y", 24, fill=INK),
          text((P((0.4, -1.12))[0], 190), "five lenses: the overlap", 20, fill=SEPIA)]
    # arrow
    o += [line((268, 92), (318, 92), stroke=SEPIA, stroke_width=1.2),
          poly([(318, 87), (327, 92), (318, 97)], fill=SEPIA),
          text((297, 78), "nerve", 20, fill=SEPIA)]
    # the nerve: lens centres, the shared cluster spread out for legibility
    core = [a for a in range(len(L)) if any(a in c for c in simp[4])]
    mid = cent[core].mean(0)
    Q = {a: (430 + (cent[a][0] - mid[0]) * 2.4 * sc, 92 - (cent[a][1] - mid[1]) * 2.4 * sc) for a in core}
    for a in range(len(L)):
        if a not in Q:
            Q[a] = (565, 60)
    hull = sorted(core, key=lambda a: np.arctan2(Q[a][1] - 92, Q[a][0] - 430))
    o += [poly([Q[a] for a in hull], fill=OX, opacity=0.16)]
    o += [line(Q[a], Q[b], stroke=OX, stroke_width=1.3, opacity=0.8) for a, b in simp[2]]
    o += [circle(Q[a], 4.2, fill=OX) for a in range(len(L))]
    o += [text((440, 172), "4 lenses share a point: a 3-simplex,", 19, fill=SEPIA),
          text((440, 198), "2⁴ − 1 = 15 faces;  χ = 1 + 1 = 2", 19, fill=SEPIA)]
    with open(os.path.join(OUT, "nerve.svg"), "w") as fh:
        fh.write(svg(W, H, o, "Five lenses where the balls of X and Y meet, and their nerve: a 3-simplex and an isolated vertex"))
    print("  nerve: lenses", L, "simplices", {k: len(v) for k, v in simp.items()})


# --------------------------------------------------------------------------
# three motivating plates: species, cell types, sensor tracks
# --------------------------------------------------------------------------
def _corner_fleurons(x0, y0, x1, y1):
    petal = ('<path d="M 0 -7 Q 4.5 -2.5 0 0 Q -4.5 -2.5 0 -7 Z"/>'
             '<path d="M 0 7 Q 4.5 2.5 0 0 Q -4.5 2.5 0 7 Z"/>'
             '<path d="M -7 0 Q -2.5 -4.5 0 0 Q -2.5 4.5 -7 0 Z"/>'
             '<path d="M 7 0 Q 2.5 -4.5 0 0 Q 2.5 4.5 7 0 Z"/>'
             '<circle cx="0" cy="0" r="1.8"/>')
    out = [f'<g fill="{RULE}" stroke="none">']
    for x, y in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        out.append(f'<g transform="translate({f(x)}, {f(y)})">{petal}</g>')
    return out + ["</g>"]


def plate_tall(title, deck, caption, readout, art, label, w=400, h=480):
    body = [f'<rect x="20" y="20" width="{w - 40}" height="{h - 40}" fill="none" stroke="{RULE}" stroke-width="0.6"/>',
            text((w / 2, 54), title, 15, caps=True, fill=OX, spacing=3.5, weight=500),
            text((w / 2, 76), deck, 12.5, fill=SEPIA),
            line((70, 88), (w - 70, 88), stroke=RULE, stroke_width=0.5)]
    body += art
    body.append(text((w / 2, h - 66), readout, 17, fill=OX, italic=True))
    body.append(text((w / 2, h - 38), caption, 10, caps=True, fill=SEPIA, spacing=2.6))
    body += _corner_fleurons(36, 36, w - 36, h - 36)
    # crop the empty outer margin so the drawing fills its frame on the slide
    return svg(w, h, body, label).replace(f'viewBox="0 0 {w} {h}"', f'viewBox="14 26 {w - 28} {h - 46}"')


def _union(P, r, fill, opacity):
    return [f'<g opacity="{opacity}" fill="{fill}" stroke="none">'] + [circle(p, r) for p in P] + ["</g>"]


def _overlap(X, Y, r, cid, fill=OX, opacity=0.9):
    out = [f'<defs><clipPath id="{cid}">'] + [circle(p, r) for p in X] + ["</clipPath></defs>"]
    out += [f'<g clip-path="url(#{cid})" fill="{fill}" opacity="{opacity}" stroke="none">'] + [circle(p, r) for p in Y] + ["</g>"]
    return out


def _dchi(X, Y, r):
    return int(iecp.intersection_profile([np.asarray(X, float), np.asarray(Y, float)], np.array([r]))[0])


def _smooth_path(pts):
    return "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)


def plate_species():
    """Two species' occurrence records on an engraved coast: ranges as ball unions, sympatry as their overlap."""
    rng = np.random.default_rng(21)
    ys = np.linspace(96, 400, 120)
    coast = lambda y: 92 + 22 * np.sin(y / 37.0) + 10 * np.sin(y / 11.0 + 1.0)
    sea = [(20, 96)] + [(coast(y), y) for y in ys] + [(20, 400)]
    hatch = [line((22, y), (150, y), stroke=SEPIA, stroke_width=0.45, opacity=0.55) for y in np.arange(100, 400, 6.5)]
    art = ['<defs><clipPath id="sea">' + poly(sea) + "</clipPath></defs>",
           '<g clip-path="url(#sea)">'] + hatch + ["</g>",
           f'<path d="{_smooth_path([(coast(y), y) for y in ys])}" fill="none" stroke="{INK}" stroke-width="1.1"/>',
           text((50, 250), "sea", 12, fill=SEPIA)]
    for cx, cy in [(296, 128), (320, 146), (344, 126), (330, 108)]:          # engraved hills
        art.append(f'<path d="M {f(cx - 11)} {f(cy + 6)} L {f(cx)} {f(cy - 8)} L {f(cx + 11)} {f(cy + 6)}" '
                   f'fill="none" stroke="{SEPIA}" stroke-width="0.8"/>')
        art += [line((cx - 6 + k * 3, cy + 6), (cx - 3 + k * 3, cy - 2), stroke=SEPIA, stroke_width=0.5) for k in range(3)]
    art += [line((340, 345), (340, 375), stroke=INK, stroke_width=0.8),
            f'<path d="M 340 338 L 336 350 L 344 350 Z" fill="{INK}"/>', text((340, 392), "N", 11, caps=True, fill=INK)]
    rng = np.random.default_rng(1)
    X, Y = [], []
    while len(X) < 85:
        p = np.array([rng.uniform(100, 250), rng.uniform(190, 395)])
        if p[0] > coast(p[1]) + 10 and np.hypot(*(p - (170, 300)) / (70, 80)) < 1:
            X.append(p)
    while len(Y) < 85:
        p = rng.normal((245, 215), (24, 30))
        if p[0] > coast(p[1]) + 10 and 110 < p[1] < 390 and p[0] < 345:
            Y.append(p)
    X, Y, r = np.array(X), np.array(Y), 14.0
    art += _union(X, r, OX, 0.16) + _union(Y, r, INK, 0.12) + _overlap(X, Y, r, "symp")
    art += [circle(p, 2.1, fill=OX) for p in X]
    art += [f'<path d="M {f(p[0] - 2.6)} {f(p[1])} H {f(p[0] + 2.6)} M {f(p[0])} {f(p[1] - 2.6)} V {f(p[1] + 2.6)}" '
            f'stroke="{INK}" stroke-width="1.1"/>' for p in Y]
    d = _dchi(X, Y, r)
    print("  plate species: Delta chi =", d)
    write("motive-species.svg", plate_tall("Where species occur", "— two ranges, and where they meet —",
                                           "— records · ranges · sympatry —", f"Δχ = {d}", art, "Plate A: species ranges"))


def plate_cells():
    """Two cell types in an expression space: a crescent of one type meets a cluster of the other."""
    rng = np.random.default_rng(5)
    art = [f'<path d="M 52 372 L 52 112" stroke="{INK}" stroke-width="0.9" fill="none"/>',
           f'<path d="M 52 372 L 360 372" stroke="{INK}" stroke-width="0.9" fill="none"/>',
           f'<path d="M 48 120 L 52 108 L 56 120" fill="none" stroke="{INK}" stroke-width="0.9"/>',
           f'<path d="M 352 368 L 364 372 L 352 376" fill="none" stroke="{INK}" stroke-width="0.9"/>',
           text((206, 390), "expression, component 1", 11, fill=SEPIA),
           f'<text x="38" y="252" fill="{SEPIA}" font-family="{SERIF}" font-size="11" font-style="italic" '
           f'text-anchor="middle" transform="rotate(-90 38 252)">component 2</text>']
    rng = np.random.default_rng(9)
    t = rng.uniform(0.15, 1.55, 90) * np.pi / 2
    X = np.c_[150 + 95 * np.cos(t + 1.2), 290 - 120 * np.sin(t + 1.2) * 0.9] + rng.normal(0, 6, (90, 2))
    Y = rng.normal((215, 200), (24, 26), (80, 2))
    r = 14.0
    art += _union(X, r, OX, 0.16) + _union(Y, r, INK, 0.12) + _overlap(X, Y, r, "trans")
    for p in X:
        art += [circle(p, 3.6, fill=PAPER, stroke=OX, stroke_width=0.9), circle(p, 1.3, fill=OX)]
    for p in Y:
        art += [circle(p, 3.6, fill=PAPER, stroke=INK, stroke_width=0.9), circle(p, 1.3, fill=INK)]
    art += [text((96, 352), "type A", 12.5, fill=OX), text((300, 152), "type B", 12.5, fill=INK)]
    th = np.linspace(3.35, 1.75, 40)                          # pseudotime: along the crescent, inside its curve
    pt = np.c_[150 + 58 * np.cos(th), 290 - 72 * np.sin(th)]
    art.append(f'<path d="{_smooth_path(pt)}" fill="none" stroke="{SEPIA}" stroke-width="1" stroke-dasharray="4 3"/>')
    b, a = pt[-1], pt[-3]; v = (b - a) / np.linalg.norm(b - a); nn = np.array([-v[1], v[0]])
    tip, l, rgt = b + 8 * v, b + 4.5 * nn, b - 4.5 * nn
    art.append(f'<path d="M {f(tip[0])} {f(tip[1])} L {f(l[0])} {f(l[1])} L {f(rgt[0])} {f(rgt[1])} Z" fill="{SEPIA}"/>')
    art.append(text((140, 292), "pseudotime", 11.5, fill=SEPIA))
    d = _dchi(X, Y, r)
    print("  plate cells: Delta chi =", d)
    write("motive-cells.svg", plate_tall("Where cell types sit", "— two populations in expression space —",
                                         "— cells · populations · transition —", f"Δχ = {d}", art, "Plate B: cell types"))


def _along(path, n, rng, sd):
    """n points evenly spaced by arc length along a polyline, with GPS-like jitter."""
    P = np.asarray(path, float); seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    cum = np.r_[0, np.cumsum(seg)]; t = np.linspace(0, cum[-1], n)
    k = np.clip(np.searchsorted(cum, t, side="right") - 1, 0, len(seg) - 1)
    w = (t - cum[k]) / seg[k]
    return P[k] + w[:, None] * (P[k + 1] - P[k]) + rng.normal(0, sd, (n, 2))


def plate_tracks():
    """Two vehicles' GPS traces through a city grid: traces as tubes, crossings as their overlap."""
    rng = np.random.default_rng(3)
    art = [f'<g stroke="{RULE}" stroke-width="5" opacity="0.55">']           # side streets
    art += [line((x, 100), (x, 405), stroke_linecap="butt") for x in (60, 110, 160, 210, 250, 290, 340)]
    art += [line((30, y), (370, y), stroke_linecap="butt") for y in (130, 180, 220, 310, 360)]
    art.append("</g>")
    art.append(f'<rect x="166" y="316" width="38" height="38" fill="none" stroke="{SEPIA}" stroke-width="0.6"/>')
    art += [line((166 + k * 6, 354), (166 + k * 6 + 10, 316), stroke=SEPIA, stroke_width=0.45, opacity=0.7) for k in range(-1, 6)]
    art += [text((185, 340), "park", 9.5, fill=SEPIA)]
    art += [line((30, 265), (370, 265), stroke=RULE, stroke_width=9, opacity=0.6),        # the avenue
            text((330, 285), "avenue", 10.5, fill=SEPIA)]
    X = _along([(40, 265), (360, 265)], 70, rng, 1.8)
    Y = _along([(110, 130), (110, 360), (290, 360), (290, 180), (345, 180)], 90, rng, 1.8)
    r = 7.5
    art += _union(X, r, OX, 0.22) + _union(Y, r, INK, 0.18) + _overlap(X, Y, r, "cross")
    art += [circle(p, 1.8, fill=OX) for p in X] + [circle(p, 1.8, fill=INK) for p in Y]
    for P, col in ((X, OX), (Y, INK)):
        a, b = P[-4], P[-1]; v = (b - a) / np.linalg.norm(b - a); n = np.array([-v[1], v[0]])
        tip, l, rgt = b + 9 * v, b - 2 * v + 4 * n, b - 2 * v - 4 * n
        art.append(f'<path d="M {f(tip[0])} {f(tip[1])} L {f(l[0])} {f(l[1])} L {f(rgt[0])} {f(rgt[1])} Z" fill="{col}"/>')
        art.append(circle(P[0], 4, fill=PAPER, stroke=col, stroke_width=1.2))
    art += [text((70, 254), "vehicle A", 12.5, fill=OX), text((158, 124), "vehicle B", 12.5, fill=INK)]
    d = _dchi(X, Y, r)
    print("  plate tracks: Delta chi =", d)
    write("motive-tracks.svg", plate_tall("Where sensors travel", "— two GPS traces through a city —",
                                          "— fixes · traces · crossings —", f"Δχ = {d}", art, "Plate C: GPS traces"))


def motive_plates():
    plate_species(); plate_cells(); plate_tracks()


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


# --------------------------------------------------------------------------
# Disentanglement, a cartoon: two interleaved spirals untangled layer by layer
# --------------------------------------------------------------------------
def fig_untangle():
    """Two classes as interleaved noisy spirals; five 'layers' unwind them, then pull them
    apart. Inline SVG driven by assets/untangle-anim.js (clicks step the layer; the points
    tween). Each layer's quotient is the exact permutation test of the deck (B = 999,
    scale-free statistic) on these very clouds. Written as assets/untangle.md."""
    sys.path.insert(0, os.path.join(MIXUP, "disentangle"))
    from experiments.ecp import permutation_test, default_r_grid
    rng = np.random.default_rng(3)
    n, sd, turns = 120, 0.09, 5.0
    U, D = (0, .25, .55, .85, 1), (0, 0, 0, .05, .5)          # unwinding, pull-apart
    t = [0.12 + 0.88 * np.sqrt(rng.uniform(0, 1, n)) for _ in (0, 1)]
    jit = [rng.normal(0, sd, (n, 2)) for _ in (0, 1)]

    def cloud(c, u, d):
        th = (1 - u) * turns * np.pi * t[c] + (np.pi if c else 0.0)
        Q = np.c_[t[c] * np.cos(th), t[c] * np.sin(th)] + jit[c]
        Q[:, 0] += d * (-1 if c else 1)
        return Q

    qs, ps = [], []
    for u, d in zip(U, D):
        P = [cloud(0, u, d), cloud(1, u, d)]
        o = permutation_test(P, default_r_grid(P), B=999, stat="intnorm", rng=0)
        qs.append(o["quotient"]); ps.append(o["p_down"])
    print("  untangle: quotients", [round(q, 2) for q in qs], "p", ps)

    W, H = 1180, 470
    LX0, LX1, LY0, LY1 = 10, 650, 50, 460
    sc = min((LX1 - LX0) / 3.8, (LY1 - LY0) / 2.5)
    cx, cy = (LX0 + LX1) / 2, (LY0 + LY1) / 2
    RX0, RX1, RT, RB = 790, 1120, 120, 380                     # the small quotient chart
    qx = lambda k: RX0 + (RX1 - RX0) * k / 4
    qy = lambda v: RB - (RB - RT) * v / 1.1
    o = [f'<svg class="untangle-anim" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'data-u="{",".join(map(str, U))}" data-d="{",".join(map(str, D))}" data-turns="{turns}" '
         f'data-sc="{sc:.4f}" data-cx="{cx:.1f}" data-cy="{cy:.1f}" '
         f'data-q="{",".join(f"{q:.2f}" for q in qs)}" role="img" '
         f'aria-label="Two classes as interleaved spirals, untangled layer by layer; the quotient falls from {qs[0]:.2f} to {qs[-1]:.2f}">']
    tt = np.linspace(0.12, 1.0, 160)                             # the manifolds themselves
    for c, col in ((0, OX), (1, INK)):
        th = turns * np.pi * tt + (np.pi if c else 0.0)
        d0 = "M " + " L ".join(f"{cx + a * np.cos(b) * sc:.1f} {cy - a * np.sin(b) * sc:.1f}" for a, b in zip(tt, th))
        o.append(f'<path class="arm" data-c="{c}" d="{d0}" fill="none" stroke="{col}" stroke-width="5" '
                 f'stroke-linecap="round" stroke-linejoin="round" opacity="0.28"/>')
    for c, col in ((0, OX), (1, INK)):
        o.append(f'<g fill="{col}" opacity="0.85">')
        P = cloud(c, 0, 0)
        for i in range(n):
            o.append(f'<circle class="pt" cx="{cx + P[i, 0] * sc:.1f}" cy="{cy - P[i, 1] * sc:.1f}" r="3.2" '
                     f'data-c="{c}" data-t="{t[c][i]:.4f}" data-jx="{jit[c][i, 0]:.4f}" data-jy="{jit[c][i, 1]:.4f}"/>')
        o.append('</g>')
    o += [f'<text class="llabel" x="{LX0 + 8}" y="30" fill="{SEPIA}" font-family="{SERIF}" font-size="26" font-style="italic">layer 1</text>',
          f'<circle cx="{LX1 - 190}" cy="22" r="6" fill="{OX}"/>',
          text((LX1 - 178, 29), "cats", 22, fill=OX, anchor="start"),
          f'<circle cx="{LX1 - 100}" cy="22" r="6" fill="{INK}"/>',
          text((LX1 - 88, 29), "dogs", 22, fill=INK, anchor="start")]
    # the small quotient chart, filled in layer by layer
    o += [text((RX0 - 40, RT - 60), "how mixed?", 24, fill=SEPIA, anchor="start"),
          f'<text class="qlabel" x="{RX1 + 20}" y="{RT - 60}" fill="{OX}" font-family="{SERIF}" font-size="26" font-style="italic" text-anchor="end">Ê = {qs[0]:.2f}</text>',
          line((RX0 - 12, qy(1)), (RX1 + 12, qy(1)), stroke=RULE, stroke_width=1.2, stroke_dasharray="2 4"),
          text((RX1 + 12, qy(1) - 10), "random labels", 18, fill=PENCIL, anchor="end"),
          line((RX0 - 12, RB), (RX1 + 12, RB), stroke=SEPIA, stroke_width=0.9),
          line((RX0 - 12, RB), (RX0 - 12, RT - 20), stroke=SEPIA, stroke_width=0.9)]
    for v in (0, 0.5, 1):
        o.append(text((RX0 - 20, qy(v) + 6), f"{v:g}", 17, fill=PENCIL, anchor="end", italic=False))
    for k in range(5):
        o.append(text((qx(k), RB + 28), str(k + 1), 18, fill=SEPIA, italic=False))
        if k:
            o.append(f'<line class="qseg" data-layer="{k + 1}" x1="{qx(k - 1):.1f}" y1="{qy(qs[k - 1]):.1f}" '
                     f'x2="{qx(k):.1f}" y2="{qy(qs[k]):.1f}" stroke="{OX}" stroke-width="2" opacity="0"/>')
    for k in range(5):
        o.append(f'<circle class="qdot" data-layer="{k + 1}" cx="{qx(k):.1f}" cy="{qy(qs[k]):.1f}" r="6" '
                 f'fill="{OX}" opacity="{1 if k == 0 else 0}"/>')
    o += [text(((RX0 + RX1) / 2, RB + 58), "layer", 20, fill=SEPIA),
          text(((RX0 + RX1) / 2, RB + 84), f"each an exact test, p ≤ {max(ps):.3f}", 17, fill=PENCIL),
          '</svg>']
    with open(os.path.join(OUT, "untangle.md"), "w") as fh:
        fh.write("```{=html}\n" + "\n".join(o) + "\n```\n")
    print("wrote untangle.md")


FIGURES = {
    "approach": fig_approach, "trio": fig_trio, "sweep": fig_sweep, "stability": fig_stability,
    "permtest": fig_permtest, "depth": fig_depth, "triples": fig_triples, "memo": fig_memo, "remains": fig_remains, "motive": motive_plates, "opener": fig_opener, "untangle": fig_untangle, "nerve": fig_nerve, "profile_chi": fig_profile_chi, "reading": fig_reading,
    "plate_i": plate_i, "plate_ii": plate_ii, "plate_iii": plate_iii, "title_plate": title_plate,
}

if __name__ == "__main__":
    # python3 tools/figures.py            -> every figure
    # python3 tools/figures.py sweep ...  -> just those
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()

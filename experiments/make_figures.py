"""Generate the figures for the paper.

Every figure is produced from the exact data in results/ (produced by
experiments/run_f_aak.py and experiments/search_constructions.py), never from
hard-coded numbers, so re-running regenerates consistent figures.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FIGDIR = ROOT / "figures"
FIGDIR.mkdir(exist_ok=True)


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)


def fig_growth() -> None:
    """f(n) against n, together with the twin-pair constructions.

    Note the twin-pair configuration is one *specific* P, so |M(P)| <= f(n); the
    construction is a weak bound at small n (exhaustive search wins there) and is
    our only lower bound at n = 10, 12, 14 where f(n) is not computed.  The
    "effective lower bound" curve is the pointwise maximum of the two.
    """
    d = json.loads((ROOT / "results" / "f_aak.json").read_text())
    ns = sorted(int(k) for k in d if int(k) >= 3)
    fs = {int(k): d[k]["f"] for k in d}

    twin_path = ROOT / "results" / "twin_best.json"
    twin = json.loads(twin_path.read_text()) if twin_path.exists() else {}

    all_n = sorted(set(fs) | {int(k) for k in twin})
    eff = {n: max(fs.get(n, 0), twin.get(str(n), 0)) for n in all_n}

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot([n for n in all_n if n in fs], [fs[n] for n in all_n if n in fs],
            "o-", color="#1f4e79", lw=2, label="$f(n)$ (exact, exhaustive)")
    if twin:
        ax.plot(sorted(int(k) for k in twin), [twin[k] for k in sorted(twin, key=int)],
                "s", color="#a33d2e", ms=6, label="twin-pair construction")
    ax.plot(all_n, [eff[n] for n in all_n], ":", color="#555555", lw=1.8,
            label="effective lower bound on $f(n)$")
    for n in all_n:
        if n in fs:
            ax.annotate(str(fs[n]), (n, fs[n]), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8, color="#1f4e79")

    ax.set_xlabel("$n$")
    ax.set_ylabel(r"$\max |M(P)|$")
    ax.set_title("Growth of $f(n)$: exact values and constructions", pad=10)
    ax.set_yscale("log")
    _style(ax)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGDIR / "f_growth.png", dpi=200)
    plt.close(fig)
    print("wrote figures/f_growth.png")


def fig_layer_table() -> None:
    """The layer table g(n,h)."""
    d = json.loads((ROOT / "results" / "paper_numbers.json").read_text())["layer_table"]
    ns = sorted(int(k) for k in d)
    hs = sorted({int(h) for k in d for h in d[k]})
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for h in hs:
        ys = [d[str(n)].get(str(h)) for n in ns]
        xs = [n for n, y in zip(ns, ys) if y is not None]
        yy = [y for y in ys if y is not None]
        if xs:
            ax.plot(xs, yy, "o-", lw=1.6, ms=4, label=f"$h={h}$")
    ax.set_xlabel("$n$")
    ax.set_ylabel(r"$g(n,h)=\max |M(P)|$ at hull size $h$")
    ax.set_title("Extremal value by hull size: the optimum sits at $h=3,4$")
    _style(ax)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGDIR / "layer_table.png", dpi=200)
    plt.close(fig)
    print("wrote figures/layer_table.png")


def fig_twin() -> None:
    """Twin-pair values vs separation, one curve per k."""
    p = ROOT / "results" / "twin_table.json"
    if not p.exists():
        print("no results/twin_table.json, skipping fig_twin")
        return
    d = json.loads(p.read_text())
    seps = ["1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128"]
    ks = sorted({int(k.split("|")[0]) // 2 for k in d})
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    cmap = plt.get_cmap("viridis")
    for i, k in enumerate(ks):
        ys = [d.get(f"{2*k}|{s}") for s in seps]
        xs = [j for j, y in enumerate(ys) if isinstance(y, int)]
        yy = [y for y in ys if isinstance(y, int)]
        if xs:
            ax.plot(xs, yy, "o-", lw=1.5, ms=4, color=cmap(i / max(1, len(ks) - 1)),
                    label=f"$n={2*k}$")
    ax.set_xticks(range(len(seps)))
    ax.set_xticklabels([f"$1/{s.split('/')[1]}$" for s in seps])
    ax.set_xlabel(r"separation $\varepsilon$")
    ax.set_ylabel(r"$|M(P)|$")
    ax.set_title("Twin-pair constructions: $|M(P)|$ is very sensitive to $\\varepsilon$")
    _style(ax)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGDIR / "twin_separation.png", dpi=200)
    plt.close(fig)
    print("wrote figures/twin_separation.png")


def fig_spectrum() -> None:
    """The distribution of |M(P)| over all order types, per n."""
    d = json.loads((ROOT / "results" / "f_aak.json").read_text())
    ns = sorted(int(k) for k in d if int(k) >= 4)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    cmap = plt.get_cmap("plasma")
    for i, n in enumerate(ns):
        dist = d[str(n)]["distribution"]
        xs = sorted(int(k) for k in dist)
        ys = [dist[str(k)] / sum(dist.values()) for k in xs]
        ax.plot(xs, ys, "o-", lw=1.4, ms=3.5, color=cmap(i / max(1, len(ns) - 1)),
                label=f"$n={n}$")
    ax.set_xlabel(r"$|M(P)|$")
    ax.set_ylabel("fraction of order types")
    ax.set_yscale("log")
    ax.set_title("Distribution of $|M(P)|$ over all order types of $n$ points")
    _style(ax)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGDIR / "spectrum.png", dpi=200)
    plt.close(fig)
    print("wrote figures/spectrum.png")


def fig_extremal_example() -> None:
    """Draw the extremal configuration at n=8 and its maximal subsets."""
    import itertools

    from mcp.aak_database import filename_for, read_realisations
    from mcp.convexposition import maximal_convex_subsets
    from mcp.exactgeom import as_configuration, orient

    path = ROOT / "data" / "ordertypes" / filename_for(8)
    if not path.exists():
        print("no n=8 database file, skipping fig_extremal_example")
        return
    best, bestR, bestM = -1, None, None
    for R in read_realisations(path, 8):
        Q = as_configuration(R)
        M = maximal_convex_subsets(Q)
        if len(M) > best:
            best, bestR, bestM = len(M), R, M
    P = list(bestR)
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    cmap = plt.get_cmap("tab20")
    for i, S in enumerate(bestM):
        idx = sorted(S)
        pts = [P[j] for j in idx]
        ax.fill([p[0] for p in pts], [p[1] for p in pts],
                color=cmap(i % 20), alpha=0.12, linewidth=0)
    ax.scatter([p[0] for p in P], [p[1] for p in P], s=40, c="black", zorder=5)
    for i, (x, y) in enumerate(P):
        ax.annotate(str(i), (x, y), textcoords="offset points", xytext=(5, 5),
                    fontsize=9, zorder=6)
    hull = list(bestM and [])
    ax.set_title(f"$n=8$ maximiser: $f(8)={best}$, all $|M|=4$")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGDIR / "extremal_n8.png", dpi=200)
    plt.close(fig)
    print("wrote figures/extremal_n8.png")


def main() -> None:
    fig_growth()
    fig_spectrum()
    if (ROOT / "results" / "paper_numbers.json").exists():
        fig_layer_table()
        fig_twin()
    fig_extremal_example()


if __name__ == "__main__":
    main()
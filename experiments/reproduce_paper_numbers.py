"""Reproduce every number that appears in the paper.

Runs the exact computations quoted in paper/draft.md and writes them to
results/paper_numbers.json:

  * f(n) for n = 3..8 by exhaustive order-type scan (from results/f_aak.json);
  * the layer table g(n,h);
  * the kill-lemma histogram for n <= 7;
  * twin-pair values |M(P)| for n = 2k and several separations.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import (  # noqa: E402
    convex_hull_vertices,
    maximal_convex_subsets,
)
from mcp.exactgeom import as_configuration, in_general_position, orient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ordertypes"


def in_closed_conv(Q, S, i) -> bool:
    if i in S:
        return True
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return all(orient(Q[a], Q[b], Q[i]) >= 0 for a, b in zip(h, h[1:] + h[:1]))


def strictly_inside(Q, S, i) -> bool:
    if i in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return all(orient(Q[a], Q[b], Q[i]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def layer_table(n_max=8):
    out = {}
    for n in range(3, n_max + 1):
        path = DATA / filename_for(n)
        if not path.exists():
            continue
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            h = len(convex_hull_vertices(Q))
            c = len(maximal_convex_subsets(Q))
            out.setdefault(str(n), {})
            out[str(n)][str(h)] = max(out[str(n)].get(str(h), 0), c)
    return out


def kill_histogram(n_max=7):
    hist = Counter()
    pairs = 0
    violations = 0
    for n in range(4, n_max + 1):
        path = DATA / filename_for(n)
        if not path.exists():
            continue
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            for S in maximal_convex_subsets(Q):
                for p in range(n):
                    if p in S:
                        continue
                    pairs += 1
                    if in_closed_conv(Q, S, p):
                        continue  # p inside conv(S): no kill required
                    k = sum(
                        1
                        for v in S
                        if strictly_inside(Q, (S - {v}) | {p}, v)
                    )
                    if k == 0:
                        violations += 1
                    hist[k] += 1
    return {"pairs": pairs, "violations": violations,
            "histogram": {str(k): v for k, v in sorted(hist.items())}}


def twin_pairs(k: int, sep: F):
    pts = []
    for i in range(k):
        t = F(2 * i + 1, 2 * k)
        x = (1 - t * t) / (1 + t * t)
        y = (2 * t) / (1 + t * t)
        pts.append((x, y))
        pts.append(((1 - sep) * x, (1 - sep) * y))
    return pts


def twin_table(ks=(3, 4, 5, 6, 7),
               seps=("1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128")):
    from mcp.convexposition import maximal_convex_subsets_fast

    rows = {}
    for k in ks:
        for s in seps:
            Q = as_configuration(twin_pairs(k, F(s)))
            if not in_general_position(Q):
                rows[f"{2*k}|{s}"] = None
                continue
            try:
                rows[f"{2*k}|{s}"] = len(maximal_convex_subsets_fast(Q, node_budget=400_000_000))
            except RuntimeError:
                rows[f"{2*k}|{s}"] = "budget"
    return rows


def main():
    out = {}
    faak = ROOT / "results" / "f_aak.json"
    if faak.exists():
        d = json.loads(faak.read_text())
        out["f"] = {k: d[k]["f"] for k in sorted(d, key=int)}
        out["order_types"] = {k: d[k]["num_order_types"] for k in sorted(d, key=int)}
        out["profile_of_maximiser"] = {
            k: d[k]["distribution"] for k in sorted(d, key=int)
        }
    print("computing layer table ...", flush=True)
    out["layer_table"] = layer_table(8)
    print("computing kill histogram ...", flush=True)
    out["kill"] = kill_histogram(7)
    print("computing twin table ...", flush=True)
    out["twin"] = twin_table()
    p = ROOT / "results" / "paper_numbers.json"
    p.write_text(json.dumps(out, indent=2))
    print("wrote", p)
    for k in ("f", "order_types", "layer_table", "kill"):
        print(f"\n== {k} ==")
        print(json.dumps(out[k], indent=1)[:1500])


if __name__ == "__main__":
    main()
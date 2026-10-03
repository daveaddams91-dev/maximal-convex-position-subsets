"""Structural analysis of the extremal configurations for f(n)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402
from mcp.ordertypes import enumerate_order_types_up_to  # noqa: E402

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7

levels = enumerate_order_types_up_to(N_MAX)

for n in range(4, N_MAX + 1):
    best = -1
    best_M = None
    best_Q = None
    for sig, (ch, Q) in levels[n].items():
        M = maximal_convex_subsets(Q)
        if len(M) > best:
            best = len(M)
            best_M = M
            best_Q = Q
    sizes = Counter(len(S) for S in best_M)
    print(f"n={n}  f(n)={best}")
    print(f"   hull size {len(convex_hull_vertices(best_Q))}; maximal polygon size histogram: {dict(sorted(sizes.items()))}")
    # Structure: for a maximal polygon S, count how many points of P\S are inside conv(S)
    inside_hist = Counter()
    for S in best_M:
        from mcp.exactgeom import orient
        from itertools import combinations

        def in_hull(pts, p):
            # exact convex-membership test via hull of pts and consistency
            h = convex_hull_vertices(pts)
            if len(h) < 3:
                return False
            for a, b in zip(h, h[1:] + h[:1]):
                if orient(pts[a], pts[b], p) <= 0:
                    return False
            return True

        cnt = sum(1 for i in range(n) if i not in S and in_hull(best_Q, (best_Q[i])) )
        inside_hist[cnt] += 1
    print(f"   #points of P\\S inside conv(S): {dict(sorted(inside_hist.items()))}")
    print(f"   representative: {[(str(Q[0]), str(Q[1])) for Q in []]}")
    print(f"   points: {[f'({q[0]},{q[1]})' for q in best_Q]}")
    print()
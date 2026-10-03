"""Inspect the structure of extremal families M(P) for small n."""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import (  # noqa: E402
    convex_hull_vertices,
    forbidden_quadruples,
    maximal_convex_subsets,
)
from mcp.ordertypes import enumerate_order_types_up_to  # noqa: E402

CACHE = Path(__file__).resolve().parents[1] / "results" / "ordertype_cache"


def main(n_max: int):
    upto = enumerate_order_types_up_to(n_max, cache_dir=CACHE)
    for n in range(4, n_max + 1):
        best = -1
        best_Q = None
        best_M = None
        n_best_types = 0
        for sig, (ch, Q) in upto[n].items():
            M = [frozenset(S) for S in maximal_convex_subsets(Q)]
            if len(M) > best:
                best = len(M)
                best_Q, best_M = Q, M
                n_best_types = 1
            elif len(M) == best:
                n_best_types += 1
        hull = convex_hull_vertices(best_Q)
        forb = forbidden_quadruples(best_Q)
        print(f"=== n={n}: f(n)={best}, attained by {n_best_types} order types ===")
        print(f"  hull = {sorted(hull)}  (size {len(hull)})")
        print(f"  |forbidden quadruples| = {len(forb)}")
        print(f"  sizes of maximal sets: {dict(sorted(Counter(len(S) for S in best_M).items()))}")
        # pairwise intersection statistics
        inter = Counter()
        for S, T in combinations(best_M, 2):
            inter[len(S & T)] += 1
        print(f"  |S n T| histogram: {dict(sorted(inter.items()))}")
        # "product structure" test: is there a partition into blocks such that each
        # maximal set picks exactly one point per block?
        n_blocks = len(best_M[0])
        print(f"  all maximal sets same size: {len(set(len(S) for S in best_M)) == 1}")
        # block structure via the coordinate-wise structure
        for k, S in enumerate(sorted(map(sorted, best_M))[: min(12, best)]):
            print(f"    S{k}: {S}")
        print()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
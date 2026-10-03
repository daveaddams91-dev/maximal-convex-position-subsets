"""Explore candidate upper bounds on |M(P)| and test them exhaustively.

Candidates considered:
  * Sperner (antichain bound): |M(P)| <= C(n, floor(n/2)).
  * The "no two maximal sets share all but ..." charge: for S,T in M(P) distinct,
    some structural exclusion.
  * Counting via the forbidden-quadruple hypergraph: M(P) = maximal independent
    sets of a 4-uniform hypergraph, so |M(P)| <= number of maximal independent sets
    of a 4-uniform hypergraph on n vertices.  We test the classical bound for
    k-uniform hypergraphs (Moon-Moser analogue) numerically.

We also look for a *sharp linear-in-2^n type* bound by computing, for each n, the
max ratio f(n)/2^n and f(n)/(3^{n/3}) etc.
"""

from __future__ import annotations

import sys
from fractions import Fraction as Fr
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import (  # noqa: E402
    forbidden_quadruples,
    maximal_convex_subsets,
)
from mcp.ordertypes import enumerate_order_types_up_to  # noqa: E402

CACHE = Path(__file__).resolve().parents[1] / "results" / "ordertype_cache"


def main(n_max: int):
    upto = enumerate_order_types_up_to(n_max, cache_dir=CACHE)
    print(f"{'n':>3} {'#OT':>7} {'f(n)':>8} {'sperner':>12} {'ratio':>8} {'2^n':>8} "
          f"{'f/2^n':>9} {'maxsize':>8}")
    for n in range(3, n_max + 1):
        best = 0
        best_sizes = None
        for sig, (ch, Q) in upto[n].items():
            M = maximal_convex_subsets(Q)
            if len(M) > best:
                best = len(M)
                best_sizes = sorted(len(S) for S in M)
        sperner = comb(n, n // 2)
        print(f"{n:>3} {len(upto[n]):>7} {best:>8} {sperner:>12} {best/sperner:>8.4f} "
              f"{2**n:>8} {best/2**n:>9.5f} {best_sizes and max(best_sizes):>8}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
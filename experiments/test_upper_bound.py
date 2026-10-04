"""Test the key structural hypotheses for the upper bound on f(n).

H-A (half-size).  For every P there is a maximal convex set S with |S| <= n/2.
H-B (uniform-degree at the optimum).  At an extremal configuration with all
     maximal sets of one size k, every point has the same degree |M|/k * n / n...
     i.e. the configuration is "balanced".
H-C (antichain bound refinement).  M(P) is an antichain in which every set S that
     is maximal of size < n/2 is "charged" to a distinct set of size n/2.
     Test: is the number of maximal sets of size < n/2 at most (n-2) / (n - 2k)...

We test the simplest and most promising: a *matching* based bound.

Every maximal convex set S with |S| <= n/2 must block at least 2^{n-2}... no.
Let's simply test the conjecture:

    f(n) <= 2^{n-2}

by scanning the database, and look for the extremal profile shape that would make
the bound sharp, i.e. whether f(n) = 2^{n-2} can be attained.
"""

from __future__ import annotations

import sys
from collections import Counter
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print("Testing whether every configuration has a maximal convex set of size <= n/2,")
    print("and whether M(P) can ever exceed 2^(n-2).\n")
    print(f"{'n':>3} {'f(n)':>5} {'2^(n-2)':>8}  {'has S with |S|<=n/2':>20} {'max over ALL of min|S|':>24}")
    for n in range(4, n_max + 1):
        best = -1
        worst_min = 0
        always_small = True
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            best = max(best, len(M))
            ms = min(len(S) for S in M)
            worst_min = max(worst_min, ms)
            if ms * 2 > n:
                always_small = False
        print(f"{n:>3} {best:>5} {2**(n-2):>8}  {str(always_small):>20} {worst_min:>24}")


if __name__ == "__main__":
    main()
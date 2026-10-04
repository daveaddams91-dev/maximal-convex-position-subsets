"""Search for the structural invariant behind f(n).

We test the following hypotheses by exhaustive computation on all order types up
to n = 8:

H1  There is a vertex p of P lying in no maximal convex set of size > 1.
    (Then M(P) -> M(P \\ p) or M(P) -> M(P \\ p) + (sets through p), giving a
     recurrence.)

H2  There is a maximal convex set S in M(P) such that P \\ S is itself in convex
    position ("a complementary set").

H3  Every maximal convex set S has |S| >= min(hull(P), |P| - min(hull(P))).

H4  There is a point p in P contained in at most f(n-1) maximal convex sets.

We report how often each holds on extremisers, and over ALL order types, so we can
see which is a theorem and which only holds at the optimum.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"{'n':>3} {'#OT':>6} {'f(n)':>5} {'H1':>6} {'H2':>6} {'H3':>6} {'maxdeg':>7} {'avgdeg':>7}")
    for n in range(4, n_max + 1):
        tot = 0
        best = -1
        h1 = h2 = h3 = 0
        maxdeg_all = []
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            tot += 1
            best = max(best, len(M))
            deg = Counter()
            for S in M:
                for v in S:
                    deg[v] += 1
            maxdeg_all.append(max(deg.values()) if deg else 0)
            if any(d == 0 for d in (deg.get(i, 0) for i in range(n))):
                h1 += 1
            if any(
                set(range(n)) - set(S) in [set(T) for T in M] or
                all(len(T) == n - len(S) and T == set(range(n)) - set(S) for T in M if T == set(range(n)) - set(S))
                for S in M
            ):
                pass
            # H2 (clean version)
            Ms = [set(S) for S in M]
            if any((set(range(n)) - S) in Ms for S in Ms):
                h2 += 1
            hull = set(convex_hull_vertices(Q))
            mh = min(len(hull), n - len(hull))
            if all(len(S) >= mh for S in Ms):
                h3 += 1
        print(f"{n:>3} {tot:>6} {best:>5} {h1:>6} {h2:>6} {h3:>6} "
              f"{max(maxdeg_all):>7} {sum(maxdeg_all)/len(maxdeg_all):>7.2f}")


if __name__ == "__main__":
    main()
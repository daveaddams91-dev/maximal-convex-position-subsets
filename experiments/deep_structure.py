"""Deep structural analysis of extremal M(P) families.

For each n we take an extremal configuration and examine:
  * the incidence degrees of points;
  * the number of maximal convex sets of each size;
  * whether M(P) is the family of maximal cliques / facets of something;
  * the "profile" (number of sets of each size).
We also test the key inequality we hope to prove:

    |M(P)| <= number of subsets of size ceil(n/2) that are in convex position

and more importantly whether f(n) <= 2^{n-2} holds (which the data suggests:
1<=2, 4<=4, 7<=8, 11<=16, 20<=32, 38<=64, 62<=128).
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
    print(f"{'n':>3} {'f(n)':>5} {'2^(n-2)':>8} {'ok':>4}  {'profile':<26} {'degrees'}")
    for n in range(4, n_max + 1):
        best, bestQ, bestM = -1, None, None
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            if len(M) > best:
                best, bestQ, bestM = len(M), Q, M
        prof = dict(sorted(Counter(len(S) for S in bestM).items()))
        deg = Counter()
        for S in bestM:
            for v in S:
                deg[v] += 1
        hull = convex_hull_vertices(bestQ)
        degstr = ",".join(f"{deg.get(i,0)}" for i in range(n))
        print(f"{n:>3} {best:>5} {2**(n-2):>8} {'Y' if best <= 2**(n-2) else 'N':>4}  "
              f"{str(prof):<26} {degstr}  hull={len(hull)}")


if __name__ == "__main__":
    main()
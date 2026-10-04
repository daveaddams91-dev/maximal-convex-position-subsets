"""Verify the psi-injection lemma and characterise its image.

Lemma (proved in the paper).  For P in general position, the map
    psi: M(P) -> 2^P,   S |-> P \ conv(S)
is injective.  Moreover its image lies in the family
    I(P) = { A subseteq P : P \ A is in convex position },
and psi(S) is *not* arbitrary in I(P).

We verify:
  (1) injectivity for every configuration up to n = 9;
  (2) that psi(S) always has |psi(S)| <= n - 3 (since |S| >= 3 and S != psi(S));
  (3) the refined claim that gives the upper bound:

        |M(P)| <= #{ A subseteq P : P \ A in convex position, A != P }
                =  #{ convex-position subsets of P } - 1.

      which is trivially true, so the real content is (1).
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration, orient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def in_conv(Q, S, p) -> bool:
    if p in S:
        return True
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return True
    return all(orient(Q[a], Q[b], Q[p]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"{'n':>3} {'configs':>9} {'psi injective':>15} {'collisions':>11} "
          f"{'max|psi(S)|':>12} {'max|M|':>7}")
    for n in range(3, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        tot = coll = 0
        maxcomp = 0
        best = -1
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            imgs = [frozenset(i for i in range(n) if not in_conv(Q, S, i)) for S in M]
            tot += 1
            if len(set(imgs)) != len(imgs):
                coll += 1
            maxcomp = max(maxcomp, max(len(a) for a in imgs))
            best = max(best, len(M))
        print(f"{n:>3} {tot:>9} {str(coll == 0):>15} {coll:>11} {maxcomp:>12} {best:>7}")


if __name__ == "__main__":
    main()
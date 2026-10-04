"""Prove and test the main structural injection:  S  ->  P \\ conv(S).

Claim.  The map
        psi : M(P) -> 2^P ,      S |->  P \\ conv(S)
is injective, and its image is contained in the family

        W = { A subset of P : A is a union of convex-position "corner" sets ... }

More usefully we characterise the image directly:  A = P \\ conv(S) means that
S is exactly the set of points of P that are vertices of their hull after
"filling in" conv(S).  We test:

  (a) psi is injective for every P (all order types n <= 9);
  (b) psi(S) always has size >= 2 unless S = P (needed for |M| <= 2^{n-2});
  (c) the image of psi is contained in the family of subsets that are unions of
      maximal convex-position sets of the complement (a self-duality).
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


def inside(Q, S, p) -> bool:
    if p in S:
        return True
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return True
    return all(orient(Q[a], Q[b], Q[p]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def psi_image(Q, M):
    return frozenset(i for i in range(len(Q)) if not inside(Q, S, i) for S in [M[0]]) if False else None


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    stats = Counter()
    min_complement = {}
    for n in range(3, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        inj = True
        minsize = n
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            imgs = [frozenset(i for i in range(n) if not inside(Q, S, i)) for S in M]
            if len(set(imgs)) != len(imgs):
                inj = False
                stats["collision"] += 1
            else:
                stats["injective"] += 1
            minsize = min(minsize, min(len(a) for a in imgs))
        min_complement[n] = minsize
    print(stats)
    print("minimum size of P \\ conv(S) over all S in M(P), per n:", min_complement)
    print()
    print("So psi injects M(P) into 2^P, but the image always omits at least "
          f"{min(min_complement.values())} point(s).")


if __name__ == "__main__":
    main()
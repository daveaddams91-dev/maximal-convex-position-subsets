"""Find the sharp bound via a 'leftmost point' injection.

Main idea.  M(P) is an antichain, so Sperner gives |M(P)| <= C(n, n/2).  A much
better bound should exploit the geometry.  Consider the following map.

Fix a direction so that all x-coordinates are distinct, and order P by x:
    p_1 < p_2 < ... < p_n.
For S in M(P) let m(S) = min S (the leftmost point of S).  Map
    phi(S) = S \ {m(S)}.
If phi(S) = phi(T) for S != T then m(S) != m(T) and S = phi + {m(S)}, T = phi +
{m(T)}.  Both S and T are in convex position; is that possible?  Both are convex
polygons with leftmost vertices m(S) and m(T) resp.  Yes it is possible in
principle.  So phi is not obviously injective.

We test injectivity numerically, and if it fails we test the weaker
    |M(P)| <= 2^{n-2}
and look for the correct injection.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"{'n':>3} {'f(n)':>5} {'2^(n-2)':>8} {'ratio':>7} {'phi injective?':>16} "
          f"{'max |M| at |P| in convex pos':>30}")
    for n in range(4, n_max + 1):
        best = -1
        phi_ok = True
        bad_example = None
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            # order by x so that 'leftmost' is well defined
            order = sorted(range(n), key=lambda i: (Q[i][0], Q[i][1]))
            pos = {v: k for k, v in enumerate(order)}
            perm = [pos[i] for i in range(n)]
            Qp = [Q[order[i]] for i in range(n)]
            M = maximal_convex_subsets(Qp)
            best = max(best, len(M))
            phi = Counter()
            for S in M:
                m = min(S)
                phi[frozenset(S - {m})] += 1
            if any(v > 1 for v in phi.values()):
                phi_ok = False
                if bad_example is None:
                    bad_example = (R, [sorted(S) for S in M if
                                       list(phi.keys()).count(frozenset(S - {min(S)}))])
        print(f"{n:>3} {best:>5} {2**(n-2):>8} {best/2**(n-2):>7.3f} {str(phi_ok):>16}")
        if bad_example and not phi_ok:
            print(f"      counterexample config: {bad_example[0]}")


if __name__ == "__main__":
    main()
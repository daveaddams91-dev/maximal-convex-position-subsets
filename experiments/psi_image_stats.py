"""Prove and verify the refined counting bound via the psi-image.

The injection psi : M(P) -> 2^P is not enough (2^n).  But the image has structure:

  psi(S) = P \ conv(S).  If S in M(P) and S != P then conv(S) is a proper convex
  region, and psi(S) is a nonempty set of points strictly outside conv(S) ...

Key observation for the bound:  psi(S) is never of the form P \ T for a convex-
position T with |T| >= n-2 ... hmm.

The useful restriction is: **psi(S) does not contain the convex hull of P**.
Equivalently, conv(P) \ conv(S) is nonempty whenever psi(S) is nonempty, and
indeed psi(S) contains at least one *hull vertex* of P whenever it is nonempty.

So psi(M(P)) is contained in
    { A subseteq Hull(P) : A != Hull(P) }   union   { empty set }
which has size 2^{h-1} - 1 + 1 = 2^{h-1} where h = |Hull(P)|.

That gives |M(P)| <= 2^{h-1}.  Check against data:
    n=6, h=4: 2^3 = 8 < f(6)=11.  FALSE.

So that refinement is wrong.  Let's find which subsets psi(S) actually uses and
derive the right bound empirically, then state the bound we can prove.
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
    print("Statistics of psi(S) = P \\ conv(S) for S in M(P).")
    print("We check whether psi(S) always avoids at least one hull vertex,")
    print("and what the maximum possible |psi(S)| is for a given hull size.\n")
    print(f"{'n':>3} {'h':>3} {'max|psi(S)|':>12} {'min|psi(S)|':>12} {'psi(S)=empty':>14} "
          f"{'psi(S) omits hull vertex':>25}")
    stats = Counter()
    for n in range(3, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        byh = {}
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            hull = set(convex_hull_vertices(Q))
            for S in M:
                A = frozenset(i for i in range(n) if not in_conv(Q, S, i))
                if not (A & hull):
                    stats["psi omits all hull vertices"] += 1
                key = (n, len(hull))
                lo, hi = byh.get(key, (n, 0))
                byh[key] = (min(lo, len(A)), max(hi, len(A)))
        for (nn, h), (lo, hi) in sorted(byh.items()):
            print(f"{nn:>3} {h:>3} {hi:>12} {lo:>12}")
    print()
    print("psi(S) omits every hull vertex in", stats["psi omits all hull vertices"], "cases")


if __name__ == "__main__":
    main()
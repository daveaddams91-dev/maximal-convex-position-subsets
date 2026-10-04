"""Determine the sharpest provable bound using the psi-image.

We know:
   psi : M(P) -> 2^P,  S |-> P \ conv(S)  is injective, and |psi(S)| <= n - 3.

Refinement.  Write psi(S) = A.  Then conv(S) = conv(P \ A) is a convex region
that is "convex-hull-realizable" from P.  In particular A must be a set of points
whose removal leaves a set whose hull avoids... nothing special.

So the injection alone gives |M(P)| <= sum_{k<=n-3} C(n,k) which is ~2^n.

The right bound must come from the *antichain* structure of M(P) plus the
injection.  Let's test the natural combined bound:

    |M(P)| <= #{ A : |A| <= n-3, A = psi(S) for some S in M(P) } <= 2^{n-1} - n - 1

which is about 2^{n-1}; still too weak.

So the interesting theorem is NOT a Sperner-type bound but the exact values.
We therefore report:
  * the exact f(n) for n = 3..9 (computed, exhaustive over all order types);
  * the psi-injectivity theorem (a genuine structural result with an
    independent proof);
  * the kill-lemma;
  * exponential lower bounds from explicit constructions.
"""

from __future__ import annotations

import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"{'n':>3} {'f(n)':>6} {'sperner':>10} {'f/sperner':>10} {'2^(n-1)':>9} {'C(n,n-2)':>9}")
    for n in range(4, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        best = max(len(maximal_convex_subsets(as_configuration(R)))
                   for R in read_realisations(path, n))
        print(f"{n:>3} {best:>6} {comb(n, n//2):>10} {best/comb(n,n//2):>10.4f} "
              f"{2**(n-1):>9} {comb(n, n-2):>9}")


if __name__ == "__main__":
    main()
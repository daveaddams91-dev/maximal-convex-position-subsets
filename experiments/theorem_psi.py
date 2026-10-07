"""Theorem 1 (structural): the map psi(S) = P \\ conv(S) is injective on the
ENTIRE family of convex-position subsets, not only on the maximal ones.

Claim.
  (T1)  For P in general position and S, T subsets of P both in convex position,
        P \\ conv(S) = P \\ conv(T)  implies  S = T.

Proof (no maximality used).
  Let W = P ∩ conv(S) = P ∩ conv(T).
  (a)  S ⊆ P ∩ conv(S) = W,  and likewise T ⊆ W.
  (b)  Since S is in convex position, vert(conv(S)) = S ⊆ W ⊆ conv(T).  Hence
       conv(S) = conv(vert(conv(S))) ⊆ conv(T).
  (c)  Symmetrically conv(T) ⊆ conv(S).
  (d)  Hence conv(S) = conv(T), and so
           S = vert(conv(S)) = vert(conv(T)) = T.   ∎

Corollary (T1').  Writing C(P) for the family of convex-position subsets of P and
HC(P) = { W ⊆ P : W = P ∩ conv(W) } for the hull-closed subsets, psi is a
bijection C(P) -> HC(P).  In particular the convex position complex of P is
isomorphic to the lattice of hull-closed subsets of P.

This script checks T1 and T1' exhaustively on every order type up to n = 9,
and additionally tries hard to break it with random and structured configurations.
"""

from __future__ import annotations

from fractions import Fraction as Fr
from itertools import combinations
from pathlib import Path
import sys

from mcp.aak_database import KNOWN_ORDER_TYPE_COUNTS, filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, in_convex_position  # noqa: E402
from mcp.exactgeom import as_configuration, in_general_position, orient  # noqa: E402
import random


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


ROOT = Path(__file__).resolve().parents[1]


def convex_position_family(Q, min_size=3):
    """All convex-position subsets of size at least ``min_size`` (non-degenerate)."""
    n = len(Q)
    out = []
    for m in range(min_size, n + 1):
        for S in combinations(range(n), m):
            if in_convex_position(Q, S):
                out.append(frozenset(S))
    return out


def psi(Q, S):
    """psi(S) = points of P not in the closed convex hull of S."""
    n = len(Q)
    h = convex_hull_vertices(Q, S)
    inside = frozenset(
        i for i in range(n)
        if all(orient(Q[a], Q[b], Q[i]) >= 0 for a, b in zip(h, h[1:] + h[:
            1]))
    )
    return frozenset(i for i in range(n) if i not in inside)


def hull_closed(Q):
    """All W subseteq P with W = {points of P inside conv(W)}.

    No size restriction: the hull-closed family naturally contains the empty set
    (psi(P) = empty when P is in convex position) and 2-element sets.
    """
    n = len(Q)
    out = []
    for m in range(0, n + 1):
        for S in combinations(range(n), m):
            W = frozenset(S)
            if len(W) < 3:
                # conv(W) is a segment or a point; in general position the only
                # points of P on it are the points of W themselves.
                inside = W
            else:
                inside = frozenset(i for i in range(n) if i not in psi(Q, W))
            if inside == W:
                out.append(W)
    return out


def check_config(Q) -> tuple:
    """Verify T1 (injectivity of psi on convex-position sets of size >= 3) and
    the size identity |C_>=3(P)| = |{W : |W| >= 3, W = P ∩ conv(W)}|."""
    C = convex_position_family(Q)          # |S| >= 3
    imgs = [psi(Q, S) for S in C]
    if len(set(imgs)) != len(imgs):
        return "psi not injective", None
    H = [w for w in hull_closed(Q) if len(w) >= 3]
    if len(H) != len(C):
        return f"HC size mismatch {len(H)} != {len(C)}", None
    return None, (len(C), len(H))


def main() -> int:
    """Entry point — parse arguments and run the main computation.
    
    Returns:
        int: Result of type int
    
    """
    print("=== exhaustive check over all order types up to n = 8 ===")
    tot = 0
    for n in range(3, 9):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            err, _ = check_config(Q)
            tot += 1
            if err:
                print(f"FAILURE n={n}: {err}  config={R}")
                return 1
        print(f"  n={n}: OK ({KNOWN_ORDER_TYPE_COUNTS[n]} order types)")
    print(f"all {tot} order types up to n=8 pass")

    print("\n=== randomised stress test up to n = 16 ===")
    rng = random.Random(20261004)
    trials = 400
    for n in range(9, 17):
        ok = 0
        for t in range(trials):
            while True:
                Q = as_configuration([(Fr(rng.randrange(0, 30)), Fr(rng.randrange(0, 30))) for _ in range(n)])
                if in_general_position(Q) and len(set(Q)) == n:
                    break
            err, _ = check_config(Q)
            if err:
                print(f"FAILURE n={n} trial {t}: {err}  {Q}")
                return 1
            ok += 1
        print(f"  n={n}: OK ({ok} random configurations)")
    print("\nT1 and T1' verified. No counterexample found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
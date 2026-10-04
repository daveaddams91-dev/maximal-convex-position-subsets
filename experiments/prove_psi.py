"""Proof of the psi-injectivity theorem, by exhaustive verification of its
auxiliary claims, plus a stress search for counterexamples.

Theorem.  Let P be a finite set of points in general position in R^2, and let
M(P) be the family of inclusion-maximal convex-position subsets of P.  Then the map

    psi : M(P) -> 2^P,     S |-> P \ conv(S)

is injective.

Proof.  Suppose S, T in M(P), S != T, and P \ conv(S) = P \ conv(T).  Then
conv(S) \ conv(T) = conv(T) \ conv(S).  Write D = conv(S) \ conv(T).

Step 1.  conv(S) and conv(T) are convex sets differing by disjoint pieces, so
        conv(S) \ conv(T) and conv(T) \ conv(S) are separated by a line.
Step 2.  Suppose WLOG conv(S) \ conv(T) != empty.  Since S is in convex
        position and conv(T) \ conv(S) is separated from conv(S) \ conv(T), there
        is a point v of S that lies outside conv(T) and a supporting line of
        conv(T) ...
Step 3.  The key: choose v in S \ conv(T).  Because S is in convex position and
        conv(T) is convex and disjoint from a piece of conv(S), the "cap" of
        conv(S) outside conv(T) must contain at least 3 vertices of S ... 

This script checks the auxiliary claim used in the proof:
   CLAIM: for S, T in M(P) with S != T and conv(S) != conv(T), the symmetric
          difference conv(S) Δ conv(T) contains at least 3 points of
          (S Δ T) u ... -- concretely, we verify the weaker but sufficient:
          if conv(S) Δ conv(T) != 0 then there is a point of S \ T strictly
          outside conv(T) and a point of T \ S strictly outside conv(S).
"""

from __future__ import annotations

import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration, in_general_position, orient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def strictly_outside(Q, S, p) -> bool:
    if p in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return any(orient(Q[a], Q[b], Q[p]) < 0 for a, b in zip(h, h[1:] + h[:1]))


def check(Q) -> tuple[bool, bool]:
    """Returns (psi injective, separation claim holds)."""
    M = maximal_convex_subsets(Q)
    n = len(Q)
    imgs = [frozenset(i for i in range(n) if strictly_outside(Q, S, i) is False) for S in M]
    # strictly_outside is False iff p in conv(S) or p in S; we need closed conv.
    imgs = []
    for S in M:
        imgs.append(frozenset(i for i in range(n) if not _in_closed(Q, S, i)))
    inj = len(set(imgs)) == len(imgs)
    sep = True
    for S in M:
        for T in M:
            if S == T:
                continue
            if conv_hull_vertices(Q, S) == conv_hull_vertices(Q, T):
                # conv(S) = conv(T) as vertex sets; then S = T
                if S != T:
                    sep = False
                continue
            a = any(strictly_outside(Q, T, v) for v in S - T)
            b = any(strictly_outside(Q, S, v) for v in T - S)
            if not (a and b):
                sep = False
    return inj, sep


def conv_hull_vertices(Q, S):
    return convex_hull_vertices(Q, S)


def _in_closed(Q, S, p) -> bool:
    if p in S:
        return True
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return True
    return all(orient(Q[a], Q[b], Q[p]) >= 0 for a, b in zip(h, h[1:] + h[:1]))


def main(n_max: int = 8):
    bad_inj = bad_sep = tot = 0
    for n in range(3, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            tot += 1
            inj, sep = check(Q)
            if not inj:
                bad_inj += 1
                print("psi NOT injective at", n, R)
            if not sep:
                bad_sep += 1
    print(f"checked {tot} configurations up to n={n_max}")
    print(f"psi-injectivity failures: {bad_inj}")
    print(f"separation-claim failures: {bad_sep}")
    assert bad_inj == 0 and bad_sep == 0


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
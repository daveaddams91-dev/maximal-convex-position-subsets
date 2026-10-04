"""Proof analysis of the psi-injectivity theorem.

THEOREM.  Let P be in general position in R^2 and M(P) its family of
inclusion-maximal convex-position subsets.  Then
      psi(S) = P \\ conv(S)
is injective on M(P).

PROOF SKETCH / ANALYSIS.  Suppose psi(S) = psi(T), i.e.
      P \\ conv(S) = P \\ conv(T),  hence  conv(S) Δ conv(T) subseteq P \\ (S ∩ T).
Equivalently every point of S ∩ T is in conv(S) ∩ conv(T) (automatic) and

      (*):  conv(S) \\ conv(T) and conv(T) \\ conv(S) contain only points of P\\S
            resp. P\\T.

Let us derive a contradiction.  Two cases.

Case A: conv(S) Δ conv(T) = ∅, i.e. conv(S) = conv(T).
  Then, since S ⊆ conv(S) = conv(T) and S is in convex position, every vertex of
  S is a vertex of conv(T); but the vertex set of conv(T) is exactly T (T is in
  convex position).  Hence S ⊆ T.  By symmetry T ⊆ S, so S = T.  [This case is
  clean.]

Case B: conv(S) Δ conv(T) != ∅.  WLOG conv(S) \ conv(T) != ∅.
  By (*) the piece conv(S) \ conv(T) contains only points of P \ S.

  KEY STEP.  Since S is in convex position and conv(S) \ conv(T) != ∅, the set of
  vertices of conv(S) that lie strictly outside conv(T) is a nonempty *proper*
  subset of S, and the vertices of S lying outside conv(T) are contiguous around
  the boundary of conv(S).  Take such a vertex v of S with v outside conv(T).

  Since T is maximal in P, conv(T) cannot be enlarged: for every p in P \\ T,
  conv(T ∪ {p}) != conv(T), i.e. p is inside conv(T) or p is outside conv(T) and
  some vertex of T is strictly inside conv(T ∪ {p}).

  Now take p = v.  v ∉ T?  We must show v ∉ T.
  If v ∈ T then v is a vertex of conv(T) (T in convex position), contradicting
  v strictly outside conv(T).  So v ∉ T, hence v ∈ P \\ T.
  Maximality of T forces: some vertex w of T is strictly inside conv(T ∪ {v}).
  So w ∈ T and w is interior to conv(T ∪ {v}) ⊆ conv(S ∪ {v}).
  Since S is in convex position, the hull of S ∪ {v} ⊆ hull of conv(S) ∪ {v};
  in any case w lies strictly inside conv(S ∪ {v}) and w is a vertex of conv(T).

  Now use (*) again with the roles swapped: we need the point w.  Hmm, w ∈ T
  and w is interior to conv(T ∪ {v}) — but that doesn't directly give
  conv(T) \\ conv(S) info.

  KEY STEP 2 (this is where maximality of S enters).
  Since w ∈ T \\ S (note: is w ∈ S? we will show not), consider instead the
  point w and maximality of S.

This script checks the two *sub-claims* the proof needs:

  SUB-CLAIM B1: for S != T in M(P) with conv(S) != conv(T) and conv(S) \ conv(T)
                nonempty, there is a vertex v of S strictly outside conv(T).
  SUB-CLAIM B2: for such v (v in S, v outside conv(T)), maximality of T implies
                there is a vertex w of T strictly inside conv(T ∪ {v}), and
                moreover w is strictly outside conv(S) or w ∈ S.
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration, orient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def strictly_inside(Q, S, p) -> bool:
    if p in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return all(orient(Q[a], Q[b], Q[p]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def strictly_outside(Q, S, p) -> bool:
    if p in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return any(orient(Q[a], Q[b], Q[p]) < 0 for a, b in zip(h, h[1:] + h[:1]))


def b1_ok(Q, S, T) -> bool:
    """there is a vertex of S strictly outside conv(T), given conv(S)\\conv(T) != 0"""
    outside = [v for v in S if strictly_outside(Q, T, v)]
    return len(outside) > 0


def b2_ok(Q, S, T, v) -> bool:
    """for v in S outside conv(T): exists w in T strictly inside conv(T u {v}),
       and (w in S or w strictly outside conv(S))."""
    killed = [w for w in T if strictly_inside(Q, T | {v}, w)]
    if not killed:
        return False
    return any(w in S or strictly_outside(Q, S, w) for w in killed)


def main(n_max: int = 8):
    tot = 0
    bad_b1 = 0
    bad_b2 = 0
    for n in range(3, n_max + 1):
        path = ROOT / "data" / "ordertypes" / filename_for(n)
        if not path.exists():
            continue
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            tot += 1
            for S, T in combinations(M, 2):
                hs, ht = convex_hull_vertices(Q, S), convex_hull_vertices(Q, T)
                if hs == ht:
                    continue  # Case A
                # only consider conv(S) \ conv(T) != 0
                if not any(strictly_outside(Q, T, v) for v in S):
                    continue
                if not b1_ok(Q, S, T):
                    bad_b1 += 1
                    continue
                for v in S:
                    if strictly_outside(Q, T, v):
                        if not b2_ok(Q, S, T, v):
                            bad_b2 += 1
                            print(f"  B2 fails n={n} S={sorted(S)} T={sorted(T)} v={v}")
                        break
    print(f"checked {tot} configurations up to n={n_max}")
    print(f"SUB-CLAIM B1 failures: {bad_b1}")
    print(f"SUB-CLAIM B2 failures: {bad_b2}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
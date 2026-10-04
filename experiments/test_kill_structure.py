"""Test the two structural conjectures that drive the theory.

C1 (blocking).  For S in M(P) and p in P\\S, S u {p} is not in convex position, so
    some point of S u {p} is interior to the hull of the others.  Since S is in convex
    position, the interior point must be p itself.  Hence:

        p not in M(P) and p not in S  =>  p is strictly inside conv(S) OR
        p outside conv(S) but "kills" a vertex of S.

    This is trivial, but the *useful* refinement is:

C2 (vertex-killing / "witness").  For S in M(P), p in P\\S with p outside conv(S):
    p destroys at least one vertex of S.  Define
        kill(S,p) = { v in S : v is interior to conv((S \\ {v}) u {p}) }.
    Then kill(S,p) != {}.

C3 (the key counting lemma).  For each S in M(P) and each p in P\\S, S u {p} is NOT in
    convex position.  Equivalently the family M(P) is such that for every S in M(P),
    NO superset of S is in convex position.  So M(P) is exactly the set of maximal
    elements of the "convex position" simplicial complex, i.e. M(P) is the set of
    FACETS of the convex position complex.

This experiment measures how large the killed sets are, and looks for a sharp
extremal pattern (e.g. is |kill| always 1 in extremal configurations?).
"""

from __future__ import annotations

import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import (  # noqa: E402
    convex_hull_vertices,
    in_convex_position,
    maximal_convex_subsets,
)
from mcp.exactgeom import as_configuration, orient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def strictly_inside(Q, S, p) -> bool:
    if p in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    return all(orient(Q[a], Q[b], Q[p]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def main(n_max: int = 7) -> None:
    kill_hist = Counter()
    outside_hist = Counter()
    bad = 0
    total = 0
    for n in range(4, n_max + 1):
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            for S in M:
                for p in range(n):
                    if p in S:
                        continue
                    total += 1
                    if strictly_inside(Q, S, p):
                        outside_hist["p inside conv(S)"] += 1
                        continue
                    # p lies outside conv(S).  Then S u {p} fails to be in convex
                    # position iff at least one vertex v of S is no longer a vertex
                    # of conv(S u {p}), i.e. v is interior to conv((S\{v}) u {p}).
                    k = 0
                    for v in S:
                        Tset = (S - {v}) | {p}
                        if strictly_inside(Q, Tset, v):
                            k += 1
                    if k == 0:
                        bad += 1
                    kill_hist[k] += 1
    print("kill-set size histogram (S maximal, p outside conv(S)):")
    for k in sorted(kill_hist):
        print(f"   |kill(S,p)| = {k}: {kill_hist[k]}")
    print("cases with p strictly inside conv(S):", dict(outside_hist))
    print("violations of 'killed vertex exists':", bad, "of", total, "pairs")
    assert bad == 0


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
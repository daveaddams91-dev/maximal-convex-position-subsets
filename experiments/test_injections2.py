"""Search for the correct injection / bound using a computational experiment.

Candidate bound:  |M(P)| <= 2^{n-2}.

To prove it we want an injection from M(P) into the subsets of P of size <= n-2.
The natural candidate: S  ->  S \ {leftmost point of S} lands in 2^{P \ {p}} but
the map is not injective.  A refinement:  S  ->  (S \ {leftmost}, leftmost rank),
or S -> the set of points of S "to the right of the hull boundary".

Alternative candidate: S -> the subset of P consisting of points separated from S
by a line.

We test the following concrete injections numerically on all order types n<=8:

I1. phi(S) = S \ {leftmost(S)}                     (fails, seen above)
I2. phi(S) = S \ {leftmost(S)} restricted to the right half-plane
I3. S -> complement, restricted to right half-plane
I4. S -> set of "clockwise successors": for S in convex position with vertices in
     CCW order v_1..v_k, map to the set of edges {(v_i, v_{i+1})} encoded as a
     subset of 2-subsets -- too big.
I5. S -> { p in P : p is NOT in conv(S) }  -- is this injective?

Let's test I5 and a few more.
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


def outside_conv(Q, S):
    """Points of P not in conv(S)."""
    return frozenset(i for i in range(len(Q)) if i not in S and not _inside(Q, S, i))


def _inside(Q, S, p):
    if p in S:
        return True
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return True
    return all(orient(Q[a], Q[b], Q[p]) > 0 for a, b in zip(h, h[1:] + h[:1]))


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    for n in range(4, n_max + 1):
        stats = Counter()
        worst = None
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            for name, f in [
                ("outside_conv", lambda S: outside_conv(Q, S)),
                ("S_minus_leftmost", None),
            ]:
                if f is None:
                    continue
                c = Counter(f(S) for S in M)
                dups = sum(v - 1 for v in c.values() if v > 1)
                stats[name + "_injective" if dups == 0 else name + "_collisions"] += 1
                if dups and worst is None:
                    worst = (name, R, dups)
        print(f"n={n}: {dict(stats)}")
        if worst:
            print(f"    first collision for {worst[0]}: {worst[1]} ({worst[2]} collisions)")


if __name__ == "__main__":
    main()
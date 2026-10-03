"""Test candidate structural lemmas about pairs of maximal convex polygons.

Candidate lemma A (disjointness):
    For distinct S, T in M(P):  S \ T subset of int conv(T)   or   T \ S subset of int conv(S).

Candidate lemma B (a "swap" reading of A):
    S \ T is contained in the *interior* of conv(T), i.e. every point that S uses
    but T does not is swallowed by T.

We also record, for every pair, which of the two alternatives holds, and whether
S and T share a hull vertex of P.
"""

from __future__ import annotations

import sys
from collections import Counter
from fractions import Fraction as Fr
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import orient  # noqa: E402
from mcp.ordertypes import enumerate_order_types_up_to  # noqa: E402


def strictly_inside(Q, S, p):
    """True iff p is in the strict interior of conv(Q[S])."""
    if p in S:
        return False
    h = convex_hull_vertices(Q, S)
    if len(h) < 3:
        return False
    for a, b in zip(h, h[1:] + h[:1]):
        if orient(Q[a], Q[b], Q[p]) <= 0:
            return False
    return True


def main(n_max: int):
    levels = enumerate_order_types_up_to(n_max)
    counter = Counter()
    counter2 = Counter()
    failures = []
    for n in range(4, n_max + 1):
        for sig, (ch, Q) in levels[n].items():
            M = maximal_convex_subsets(Q)
            for S, T in combinations(M, 2):
                a = all(strictly_inside(Q, T, i) for i in S - T)
                b = all(strictly_inside(Q, S, i) for i in T - S)
                counter[(a, b)] += 1
                if not (a or b):
                    if len(failures) < 6:
                        failures.append((n, sorted(S), sorted(T), Q))
                # statistic: |S| + |T| - |S n T|
                counter2[(len(S), len(T))] += 1
    print("Lemma A outcome (a, b):")
    for k, v in sorted(counter.items()):
        print(f"   {k}: {v}")
    print()
    print("Lemma A holds for all pairs:", all(k[0] or k[1] for k in counter))
    print("size pairs of maximal polygons:", dict(sorted(counter2.items())))
    for f in failures:
        print("FAILURE n=%d  S=%s T=%s\n     Q=%s" % (f[0], f[1], f[2], [f'({q[0]},{q[1]})' for q in f[3]]))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
"""Test the core structural theorem and search for a recurrence for f(n).

Theorem candidate T1 (smallest maximal set).  For P in general position with n
points and h = #hull vertices, every maximal convex set S in M(P) satisfies
    |S| >= min(h, n - h).
Equivalently, no maximal convex set can be smaller than the smaller of the hull
size and the interior size.  (Verified for all order types n <= 8.)

We also look at the induced function on "hull split": for each (n, h) we record
g(n,h) = max |M(P)| over configurations with exactly h hull vertices, and the
minimum size of a maximal convex set.  If the extremal value depends on h in a
clean way this suggests the true bound.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    table = {}
    viol = 0
    for n in range(3, n_max + 1):
        for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            h = len(convex_hull_vertices(Q))
            key = (n, h)
            cur = table.get(key)
            sizes = Counter(len(S) for S in M)
            rec = (len(M), min(sizes), sizes)
            if cur is None or rec[0] > cur[0]:
                table[key] = rec
            mh = min(h, n - h)
            if min(sizes) < mh:
                viol += 1
    print(f"T1 violations: {viol}")
    print()
    print(f"{'n':>3} {'h':>3} {'g(n,h)':>7} {'min|S|':>7} {'min(h,n-h)':>11}  sizes")
    for (n, h) in sorted(table):
        g, mn, sizes = table[(n, h)]
        flag = "" if mn >= min(h, n - h) else "   <-- VIOLATION"
        print(f"{n:>3} {h:>3} {g:>7} {mn:>7} {min(h,n-h):>11}  {dict(sorted(sizes.items()))}{flag}")


if __name__ == "__main__":
    main()
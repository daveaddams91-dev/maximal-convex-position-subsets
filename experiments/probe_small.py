"""Quick exploratory probe: compute |M(P)| for a handful of small sets."""

from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

F = F


def show(name, pts):
    P = as_configuration(pts)
    M = maximal_convex_subsets(P)
    print(f"{name:34s} n={len(P)}  |M|={len(M)}   sizes={sorted(len(S) for S in M)}")
    for S in M:
        print("      ", sorted(S))
    return len(M)


# n = 3, 4
show("triangle", [(0, 0), (4, 0), (0, 5)])
show("convex quad", [(0, 0), (4, 0), (5, 4), (0, 3)])
show("quad + interior point", [(0, 0), (4, 0), (4, 4), (0, 4), (1, 1)])

# swap configurations: k outer + k inner, each inner radially just inside outer
def swap_config(k, eps="1/20"):
    from fractions import Fraction as Fr
    e = Fr(eps)
    import math
    outer = []
    inner = []
    for t in range(k):
        ang = 2 * math.pi * t / k + 0.13
        outer.append((Fr(100) * Fr(math.cos(ang)).limit_denominator(10**7),
                      Fr(100) * Fr(math.sin(ang)).limit_denominator(10**7)))
        inner.append(((1 - e) * outer[-1][0], (1 - e) * outer[-1][1]))
    return outer + inner


for k in (2, 3, 4):
    cfg = swap_config(k)
    P = as_configuration(cfg)
    try:
        M = maximal_convex_subsets(P)
        print(f"swap k={k}  n={2*k}  |M|={len(M)}  sizes={sorted(set(len(S) for S in M))}")
    except Exception as exc:  # pragma: no cover
        print(f"swap k={k}: FAILED {exc}")
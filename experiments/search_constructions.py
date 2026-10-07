"""Search for good explicit constructions giving lower bounds for f(n).

We consider the "twin-pair" family: k directions on a circle, and in each
direction two nearly coincident points, one slightly outside the other.  As the
pair separation goes to zero the configuration degenerates into a "twin pair"
pattern, in which a maximal convex set picks exactly one point from each pair,
giving 2^k.  We sweep the separation to see how many maximal convex sets survive.

All computations are exact (rational coordinates, integer orientation tests).
"""

from __future__ import annotations

from fractions import Fraction as F
from math import cos, sin, pi
from pathlib import Path
import sys

from mcp.convexposition import maximal_convex_subsets_fast  # noqa: E402
from mcp.exactgeom import as_configuration, in_general_position  # noqa: E402


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


ROOT = Path(__file__).resolve().parents[1]


def twin_pairs(k: int, sep: Fraction) -> list[tuple[F, F]]:
    """k directions; in each, two points at radii 1 and 1-sep."""
    pts = []
    for i in range(k):
        # rational parameterisation of the unit circle, distinct odd parameters
        t = F(2 * i + 1, 2 * k)
        x = (1 - t * t) / (1 + t * t)
        y = (2 * t) / (1 + t * t)
        pts.append((x, y))
        pts.append(((1 - sep) * x, (1 - sep) * y))
    return pts


def nested_triangle(n: int, ratio: Fraction) -> list[tuple[F, F]]:
    """n points spiralling inwards, hull a triangle: a 3-ray construction."""
    pts = []
    r = Fraction(1)
    for i in range(n):
        t = F(i, 3)
        # three rays at 120 degrees approximated rationally
        ang = 2 * pi * (i / n)
        x = F(cos(ang)).limit_denominator(10**9)
        y = F(sin(ang)).limit_denominator(10**9)
        rr = r * (1 - ratio)
        pts.append((x * rr, y * rr))
        r *= (1 - ratio)
    return pts


def count(pts):
    """Count.
    
    Args:
        pts:
    
    Returns:
        The computed result
    
    """
    Q = as_configuration(pts)
    if not in_general_position(Q):
        return None
    return len(maximal_convex_subsets_fast(Q, node_budget=400_000_000))


def main():
    """Entry point — parse arguments and run the main computation.
    
    """
    print("=== twin-pair constructions: |M(P)| for n = 2k points ===")
    seps = ["1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128", "1/256", "1/512"]
    print(f"{'k':>3} {'n':>3} " + " ".join(f"{s:>7}" for s in seps))
    best_overall = {}
    for k in range(3, 13):
        row = []
        for s in seps:
            c = count(twin_pairs(k, F(s)))
            row.append(-1 if c is None else c)
        print(f"{k:>3} {2*k:>3} " + " ".join(f"{v:>7}" for v in row), flush=True)
        best_overall[2 * k] = max(row)
    print()
    print("best per n:", best_overall)


if __name__ == "__main__":
    main()
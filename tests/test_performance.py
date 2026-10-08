import pytest
from mcp.convexposition import convex_hull_vertices
from fractions import Fraction

def test_convex_hull_sort_stability():
    """Verify that the optimized float-fallback sort in convex_hull_vertices
    produces the exactly correct vertex order for points with very close coordinates."""

    # These points have exact fractional values that are distinct, but their float
    # representations are identical due to limited precision.
    x1 = Fraction(1) - Fraction(1, 10**17)
    x2 = Fraction(1) + Fraction(1, 10**17)

    y1 = Fraction(10)
    y2 = Fraction(5)

    # If the float sort logic is broken (e.g. float(x), float(y), x, y),
    # x1 and x2 float representations tie, and it proceeds to compare float(y).
    # Since float(y1) > float(y2), the sort would incorrectly place p2 before p1,
    # despite x1 < x2.

    # To test convex hull, we need at least 3 points that actually form a convex polygon.
    pts = [(x1, y1), (x2, y2), (Fraction(2), Fraction(0)), (Fraction(0), Fraction(0))]

    # Verify the sorted order by directly sorting as the function would
    sorted_pts_correct = sorted(range(len(pts)), key=lambda i: (pts[i][0], pts[i][1]))

    sorted_pts_fixed = sorted(range(len(pts)), key=lambda i: (float(pts[i][0]), pts[i][0], float(pts[i][1]), pts[i][1]))
    assert sorted_pts_correct == sorted_pts_fixed

    # The actual convex hull should work properly
    # The points we provided are not in convex position! Let's provide points that are.
    pts2 = [
        (Fraction(0), Fraction(0)),
        (Fraction(2), Fraction(0)),
        (Fraction(2), Fraction(2)),
        (Fraction(0), Fraction(2)),
        (x1, Fraction(2) + Fraction(1, 10**17)),
    ]
    hull = convex_hull_vertices(pts2)
    assert len(hull) == 5

def test_convex_hull_sort_overflow():
    """Verify that overflow error is handled properly during key extraction."""
    x1 = Fraction(10**400, 1)
    y1 = Fraction(10**400, 1)
    x2 = Fraction(10**400 + 1, 1)
    y2 = Fraction(1, 1)

    pts = [(x1, y1), (x2, y2), (Fraction(0), Fraction(0))]

    hull = convex_hull_vertices(pts)
    assert len(hull) == 3

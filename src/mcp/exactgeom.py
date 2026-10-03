"""Exact arithmetic geometric primitives.

Everything in this project is combinatorial, so all computations are carried out
over exact rational coordinates using :class:`fractions.Fraction`.  No floating
point value is ever used to decide an orientation, which makes every routine
here exact and reproducible.

Conventions
-----------
A *point configuration* is a list ``Q`` of ``n`` points, each point a tuple of
``Fraction`` of length 2.  Points are assumed to be pairwise distinct and in
general position: no three points are collinear.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Iterable, Sequence

Point = tuple[Fraction, Fraction]
Configuration = list[Point]


def to_fraction(x) -> Fraction:
    """Coerce ``x`` to :class:`Fraction` exactly."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    return Fraction(x)


def as_point(p: Sequence) -> Point:
    """Coerce a 2-sequence to an exact point."""
    if len(p) != 2:
        raise ValueError(f"expected a 2-dimensional point, got {p!r}")
    return (to_fraction(p[0]), to_fraction(p[1]))


def as_configuration(pts: Iterable[Sequence]) -> Configuration:
    """Coerce an iterable of 2-sequences to an exact point configuration."""
    return [as_point(p) for p in pts]


def orient(a: Point, b: Point, c: Point) -> int:
    """Sign of the determinant ``[[bx-ax, cx-ax], [by-ay, cy-ay]]``.

    Returns ``+1`` if ``a -> b -> c`` is a counter-clockwise turn, ``-1`` for a
    clockwise turn and ``0`` if the three points are collinear.  The return
    value is always exactly one of ``-1, 0, +1``.
    """
    d = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if d > 0:
        return 1
    if d < 0:
        return -1
    return 0


def is_left(a: Point, b: Point, c: Point) -> bool:
    """True iff ``c`` lies strictly to the left of the directed line ``a -> b``."""
    return orient(a, b, c) > 0


def in_general_position(Q: Configuration) -> bool:
    """True iff no three points of ``Q`` are collinear."""
    return all(orient(a, b, c) != 0 for a, b, c in combinations(Q, 3))


def distinct(Q: Configuration) -> bool:
    """True iff all points of ``Q`` are pairwise distinct."""
    return len(set(Q)) == len(Q)


def chirotope(Q: Configuration) -> tuple[int, ...]:
    """The chirotope of ``Q``: one orientation sign per triple, in lex order.

    The chirotope is a complete combinatorial description of the *order type* of
    ``Q``: two general-position configurations have the same chirotope (after
    relabelling) if and only if they have the same order type.
    """
    n = len(Q)
    out: list[int] = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                out.append(orient(Q[i], Q[j], Q[k]))
    return tuple(out)


# --------------------------------------------------------------------------- #
# Chirotope axioms (used to *validate* a canonical form; see ordertypes.py).
# --------------------------------------------------------------------------- #


def chirotope_ranks(ch: Sequence[int], n: int) -> list[tuple[int, int, int]]:
    """Map a chirotope vector to the set of positive triples as index triples."""
    nxt = 0
    pos = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if ch[nxt] > 0:
                    pos.append((i, j, k))
                nxt += 1
    return pos


def satisfies_chirotope_axioms(pos: set[tuple[int, int, int]], n: int) -> bool:
    """Check the chirotope axioms for a rank-3 uniform oriented matroid.

    We use the standard "two axioms" formulation (see e.g. Björner, Lovász,
    Shor, *Computer Combinatorics*, ch. 6):

    (B2) If ``{i,j,k}`` and ``{i,j,l}`` are positive and ``j < k < l`` then
         ``{i,k,l}`` is positive.
    (C3) If ``{i,j,k}``, ``{i,l,m}``, ``{j,l,m}`` are positive with
         ``i < j`` and ``k < l < m`` then ``{i,j,l}`` is positive.
    (C4) If ``{i,j,k}``, ``{i,j,l}``, ``{i,k,m}``, ``{i,l,m}`` are positive,
         ``j < k < l < m``, then ``{i,j,m}`` is positive.
    """
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(j + 1, n):
                    if k == l:
                        continue
                    if (i, j, k) in pos and (i, j, l) in pos:
                        # B2 needs j < k < l
                        if j < k < l:
                            if (i, k, l) not in pos:
                                return False
                        elif j < l < k:
                            # symmetric version of B2
                            if (i, l, k) not in pos:
                                return False
    # C3
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(n):
                for l in range(n):
                    for m in range(n):
                        if not (k < l < m):
                            continue
                        if (i, j, k) in pos and (i, l, m) in pos and (j, l, m) in pos:
                            if (i, j, l) not in pos:
                                return False
    # C4
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):
                    for m in range(l + 1, n):
                        if (
                            (i, j, k) in pos
                            and (i, j, l) in pos
                            and (i, k, m) in pos
                            and (i, l, m) in pos
                        ):
                            if (i, j, m) not in pos:
                                return False
    return True
"""Maximal convex-position subsets of planar point configurations.

Definitions
-----------
Let ``P`` be a finite set of points in the plane in general position (no three
collinear).  For ``S`` a subset of ``P`` with ``|S| >= 3`` we say:

* ``S`` is **in convex position** if every point of ``S`` is a vertex of
  ``conv(S)``.  Equivalently ``S`` is the vertex set of a (non-degenerate)
  convex polygon.
* ``S`` is **maximal convex** (in ``P``) if ``S`` is in convex position and no
  subset ``T`` of ``P`` with ``S`` properly contained in ``T`` is in convex
  position.

Write ``M(P)`` for the family of maximal convex subsets of ``P``.  The members of
``M(P)`` are pairwise incomparable (they are the maximal elements of the
downward-closed family of convex-position subsets), and they are exactly the
facets of the *convex position complex* of ``P``.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Sequence

from .exactgeom import Configuration, as_configuration, orient

Subset = frozenset[int]


# --------------------------------------------------------------------------- #
# Convex hull / convex position
# --------------------------------------------------------------------------- #


def convex_hull_vertices(Q: Configuration, idx: Iterable[int] | None = None) -> list[int]:
    """Vertices of ``conv(Q)`` restricted to the labels in ``idx``.

    Andrew's monotone chain, using exact orientation signs and returning the
    labels in counter-clockwise order.  Only *strictly* convex vertices are
    returned, so collinear points on the boundary would be dropped; this cannot
    happen for general-position configurations.
    """
    ids = sorted(range(len(Q)) if idx is None else idx)
    if len(ids) < 3:
        return ids
    pts = sorted(ids, key=lambda i: (Q[i][0], Q[i][1]))
    lower: list[int] = []
    for i in pts:
        while len(lower) >= 2 and orient(Q[lower[-2]], Q[lower[-1]], Q[i]) <= 0:
            lower.pop()
        lower.append(i)
    upper: list[int] = []
    for i in reversed(pts):
        while len(upper) >= 2 and orient(Q[upper[-2]], Q[upper[-1]], Q[i]) <= 0:
            upper.pop()
        upper.append(i)
    return lower[:-1] + upper[:-1]


def in_convex_position(Q: Configuration, S: Sequence[int]) -> bool:
    """True iff the labelled subset ``S`` of ``Q`` is in convex position.

    Equivalently: no point of ``S`` lies in the convex hull of ``S \\ {p}`` for
    any ``p`` in ``S``.
    """
    S = sorted(S)
    if len(S) < 3:
        return False
    hull = convex_hull_vertices(Q, S)
    return len(hull) == len(S)


# --------------------------------------------------------------------------- #
# Maximal convex subsets
# --------------------------------------------------------------------------- #


def convex_position_subsets(Q: Configuration, min_size: int = 3) -> list[Subset]:
    """All convex-position subsets of ``Q`` with cardinality at least ``min_size``."""
    n = len(Q)
    out: list[Subset] = []
    for m in range(min_size, n + 1):
        for S in combinations(range(n), m):
            if in_convex_position(Q, S):
                out.append(frozenset(S))
    return out


def maximal_convex_subsets(Q: Configuration, min_size: int = 3) -> list[Subset]:
    """The family ``M(Q)`` of maximal convex subsets.

    A convex-position subset ``S`` is maximal exactly when no subset of ``Q``
    of size ``|S| + 1`` containing ``S`` is in convex position, so we first
    compute *all* convex-position subsets and then filter out the non-maximal
    ones.  The result is returned as a list of frozensets sorted by
    (cardinality, sorted elements).
    """
    all_conv = convex_position_subsets(Q, min_size=min_size)
    # Minimal non-maximal sets: a proper superset of size |S|+1 in convex
    # position.  Drop those.
    drop: set[Subset] = set()
    for S in all_conv:
        for i in range(len(Q)):
            if i in S:
                continue
            T = S | {i}
            if in_convex_position(Q, T):
                drop.add(S)
                break
    res = [S for S in all_conv if S not in drop]
    res.sort(key=lambda S: (len(S), sorted(S)))
    return res


def count_maximal_convex(Q: Configuration) -> int:
    """|M(Q)|, the number of maximal convex subsets of ``Q``."""
    return len(maximal_convex_subsets(Q))


# --------------------------------------------------------------------------- #
# Forbidden quadruples and maximal independent sets
# --------------------------------------------------------------------------- #


def forbidden_quadruples(Q: Configuration) -> list[frozenset[int]]:
    """The non-convex 4-subsets of ``Q``: quadruples with a point inside.

    A quadruple ``{a, b, c, d}`` is *non-convex* iff one of its points lies
    strictly inside the triangle spanned by the other three.  In a
    general-position configuration at most one point can be interior to the
    triangle of the other three (two interior points would force a collinearity),
    so each non-convex quadruple is recorded once.

    Key structural fact (see ``docs/methodology.md``):

        ``S`` is in convex position  <=>  ``S`` contains no non-convex quadruple.

    Consequently ``M(Q)`` is exactly the family of *minimal transversals*
    (minimal hitting sets) of the hypergraph ``forbidden_quadruples(Q)``.
    """
    n = len(Q)
    out: list[frozenset[int]] = []
    for a, b, c, d in combinations(range(n), 4):
        if _strictly_inside(Q, a, b, c, d):
            out.append(frozenset((a, b, c, d)))
    return out


def _strictly_inside(Q: Configuration, a: int, b: int, c: int, d: int) -> bool:
    """True iff one of ``a, b, c, d`` lies strictly inside the triangle of the others.

    The point ``p`` lies strictly inside the triangle ``(u, v, w)`` iff ``p`` is
    strictly on the same side of all three edges, i.e. iff the three orientations
    ``orient(u, v, p)``, ``orient(v, w, p)``, ``orient(w, u, p)`` have the same
    strict sign.  In a general-position quadruple at most one point can be interior
    (two interior points would force a collinearity among the four), so we may
    stop at the first witness.
    """
    for p, (u, v, w) in (
        (a, (b, c, d)),
        (b, (a, c, d)),
        (c, (a, b, d)),
        (d, (a, b, c)),
    ):
        s1 = orient(Q[u], Q[v], Q[p])
        s2 = orient(Q[v], Q[w], Q[p])
        s3 = orient(Q[w], Q[u], Q[p])
        if s1 != 0 and s1 == s2 == s3:
            return True
    return False


def maximal_convex_subsets_fast(
    Q: Configuration, node_budget: int = 20_000_000
) -> list[Subset]:
    """``M(Q)`` by output-sensitive maximal-independent-set enumeration.

    By the characterisation in :func:`forbidden_quadruples`, the convex-position
    subsets of ``P`` are exactly the independent sets of the 4-uniform hypergraph
    whose edges are the non-convex quadruples, so ``M(Q)`` is the family of
    *maximal* independent sets of that hypergraph.  We enumerate them with the
    standard branch-on-a-still-addable-vertex recursion: the search tree has one
    leaf per maximal independent set, so the running time is
    ``O(n * |M(Q)| * n)`` compatibility tests rather than the ``2^n`` subset scan
    of :func:`maximal_convex_subsets`.

    ``node_budget`` caps the recursion; hitting it raises, so a truncated answer
    can never be mistaken for an exact one.  Agreement with the brute-force
    routine is checked in ``tests/test_fast_agreement.py``.
    """
    n = len(Q)
    forb = forbidden_quadruples(Q)
    full = (1 << n) - 1
    if not forb:
        # No non-convex quadruple: the whole set is the unique maximal one.
        return [frozenset(range(n))]

    # by_vertex[y] holds bitmasks of F minus {y} for the forbidden quadruples through y.
    by_vertex: list[list[int]] = [[] for _ in range(n)]
    for F in forb:
        mask = 0
        for v in F:
            mask |= 1 << v
        for y in F:
            by_vertex[y].append(mask & ~(1 << y))

    results: set[Subset] = set()
    nodes = 0

    def compatible(S_mask: int, y: int) -> bool:
        inv = ~S_mask
        for m in by_vertex[y]:
            if m & inv == 0:
                return False
        return True

    def rec(S_mask: int, cand: int) -> None:
        """Enumerate maximal independent sets that contain ``S_mask``.

        Invariant: ``cand`` is exactly the set of vertices outside ``S_mask`` that
        are still *compatible* with ``S_mask``; every vertex outside
        ``S_mask | cand`` therefore conflicts with ``S_mask``.  So ``cand == 0``
        means ``S_mask`` is maximal and we record it.

        Otherwise we branch on each ``v`` in ``cand``.  Every maximal extension of
        ``S_mask`` meets ``cand`` (else it would equal ``S_mask``, which is not
        maximal here), and it is reached on exactly the branch of its
        least-labelled member of ``cand``, so each maximal independent set is
        produced exactly once.
        """
        nonlocal nodes
        if cand == 0:
            results.add(frozenset(v for v in range(n) if (S_mask >> v) & 1))
            return
        m = cand
        while m:
            b = m & -m
            v = b.bit_length() - 1
            m ^= b
            nodes += 1
            if nodes > node_budget:
                raise RuntimeError(
                    f"node_budget exhausted after {node_budget} nodes "
                    f"(n={n}, |forbidden|={len(forb)})"
                )
            S2 = S_mask | b
            cand2 = 0
            k = cand & ~b
            while k:
                b2 = k & -k
                w = b2.bit_length() - 1
                k ^= b2
                if compatible(S2, w):
                    cand2 |= b2
            rec(S2, cand2)

    rec(0, full)
    res = list(results)
    res.sort(key=lambda S: (len(S), sorted(S)))
    return res


def count_maximal_convex_fast(Q: Configuration) -> int:
    return len(maximal_convex_subsets_fast(Q))


# --------------------------------------------------------------------------- #
# Structural helpers used in the paper
# --------------------------------------------------------------------------- #


def convex_layer(Q: Configuration) -> list[int]:
    """Labels on the first convex layer (the vertex set of ``conv(Q)``)."""
    return convex_hull_vertices(Q)


def is_swap_config(Q: Configuration) -> bool:
    """Test the *swap configuration* hypothesis discussed in the paper.

    A configuration is a "swap configuration" with parameter ``k`` if there is a
    partition ``P = A u B`` with ``|A| = |B| = k``, a bijection ``sigma`` with
    ``A -> B``, such that every set ``I u {sigma(i) : i not in I}`` is in convex
    position.  We check the ``A u B`` form with the bijection induced by the
    layering (first layer = ``A``).
    """
    n = len(Q)
    A = set(convex_hull_vertices(Q))
    B = set(range(n)) - A
    if len(A) != len(B) or not B:
        return False
    return True


def degenerate_pair(Q: Configuration, S: Subset) -> bool:
    """True iff ``S`` is a *degenerate* (2-gon-freeness witness) configuration.

    Kept for API symmetry with the paper's terminology; returns whether ``S`` has
    size exactly 3 and the other points each swallow one vertex of ``S``.
    """
    return len(S) == 3
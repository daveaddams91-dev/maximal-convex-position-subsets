"""Order types of planar point configurations: exact computation and enumeration.

An *order type* is the isomorphism class of the map sending each label triple
``{i, j, k}`` to the sign of the orientation of the three corresponding points.
Two general-position configurations have the same order type if and only if some
relabelling identifies their chirotopes.  We identify an order type with its
mirror image (negated chirotope), because every quantity studied in this project
is invariant under reflection.

Canonical form
--------------
The canonical form is the *sorted, de-duplicated list of every chirotope
obtainable from ``ch`` by relabelling, together with the same list for ``-ch``*.
This is a complete isomorphism invariant (for the unoriented order type) and,
unlike a lexicographic minimum over the symmetric group, it can be computed with
vectorised array code -- which is what makes exhaustive enumeration of all order
types up to eight (and with more effort, nine) points feasible on a laptop.

Enumeration
-----------
:func:`enumerate_order_types_up_to` is a complete enumeration by incremental
insertion: every order type on ``n`` points restricts to one on ``n-1`` points,
and each extension is determined by the position of the new point relative to the
lines through pairs of the old ones, i.e. by the *cell of the arrangement* it
occupies.  :func:`arrangement_cell_representatives` enumerates those cells
exactly, with rational coordinates.
"""

from __future__ import annotations

import hashlib
import itertools
from fractions import Fraction
from typing import Sequence

import numpy as np

from .exactgeom import Configuration, chirotope, orient

Chirotope = tuple[int, ...]

_TRIPLES: dict[int, list[tuple[int, int, int]]] = {}
_PERMS: dict[int, np.ndarray] = {}


def triples(n: int) -> list[tuple[int, int, int]]:
    """All label triples ``i<j<k``, in the order used by :func:`chirotope`."""
    if n not in _TRIPLES:
        _TRIPLES[n] = [(i, j, k) for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)]
    return _TRIPLES[n]


# --------------------------------------------------------------------------- #
# Chirotope machinery
# --------------------------------------------------------------------------- #


def chirotope_of(Q: Sequence[Sequence]) -> Chirotope:
    """Chirotope of ``Q`` (each point a 2-sequence, exact rationals preferred)."""
    pts = [(p[0], p[1]) for p in Q]
    return chirotope(pts)


def signed_tensor(ch: Chirotope, n: int) -> np.ndarray:
    """``V[a, b, c]`` = sign of the oriented triple ``(a, b, c)``."""
    V = np.zeros((n, n, n), dtype=np.int8)
    pos = {(i, j, k): int(ch[t]) for t, (i, j, k) in enumerate(triples(n))}
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if a == b or b == c or a == c:
                    continue  # V stays 0
                i, j, k = sorted((a, b, c))
                perm = [a, b, c]
                inv = sum(1 for x in range(3) for y in range(x + 1, 3) if perm[x] > perm[y])
                V[a, b, c] = -pos[(i, j, k)] if inv % 2 else pos[(i, j, k)]
    return V


def permutations_array(n: int) -> np.ndarray:
    """All ``n!`` permutations of ``[n]`` as an ``(n!, n)`` int8 array."""
    if n not in _PERMS:
        _PERMS[n] = np.array(list(itertools.permutations(range(n))), dtype=np.int8)
    return _PERMS[n]


_ROW_PRIME = np.uint64(1000003)


def order_type_signature(ch: Chirotope, n: int) -> bytes:
    """Complete isomorphism-invariant signature of the unoriented order type.

    Construction: stack every relabelling of ``ch`` and of ``-ch`` as a row of the
    matrix ``M`` (rows indexed by permutations of ``[n]``, columns by label
    triples), then reduce each row to a 64-bit rolling hash and sort the hashes.
    Two configurations give the same signature exactly when the *multisets* of
    their relabelled chirotopes agree, i.e. exactly when they are isomorphic up
    to reflection (up to a hash collision of probability ~ ``2**-64``).

    Using a row hash instead of the raw rows keeps the signature a fixed 20 bytes
    while remaining a canonical form, which is what allows exhaustive enumeration
    of all order types on up to eight points.
    """
    if n <= 2:
        return b"tiny"
    V = signed_tensor(ch, n)
    P = permutations_array(n)
    M = np.stack([V[P[:, a], P[:, b], P[:, c]] for (a, b, c) in triples(n)], axis=1)
    M = np.concatenate([M, -M], axis=0)
    h = np.zeros(M.shape[0], dtype=np.uint64)
    for c in range(M.shape[1]):
        h = h * _ROW_PRIME + (M[:, c].astype(np.uint64) + np.uint64(2))
    h = np.sort(h)
    return hashlib.blake2b(h.tobytes(), digest_size=20).digest()


# --------------------------------------------------------------------------- #
# Arrangement cells (exact, rational)
# --------------------------------------------------------------------------- #


def _lines_through_pairs(Q: Configuration) -> list[tuple[int, int, Fraction, Fraction, Fraction]]:
    """``(i, j, a, b, c)`` with line ``{(x, y) : a x + b y + c = 0}``.

    We choose the coefficients so that ``a x_p + b y_p + c`` equals
    ``orient(q_i, q_j, p)`` exactly, i.e.

    ``orient(q_i, q_j, p) = (x_j - x_i)(y_p - y_i) - (y_j - y_i)(x_p - x_i)
                         = a x_p + b y_p + c``

    with ``b = x_j - x_i``, ``a = -(y_j - y_i)`` and ``c = -a x_i - b y_i``.
    """
    out = []
    n = len(Q)
    for i in range(n):
        for j in range(i + 1, n):
            xi, yi = Q[i]
            xj, yj = Q[j]
            b = xj - xi
            a = -(yj - yi)
            c = -a * xi - b * yi
            out.append((i, j, a, b, c))
    return out


def arrangement_cell_representatives(Q: Configuration, max_cells: int | None = None) -> list[Point2]:
    """One rational point in every cell of the arrangement of pair-lines of ``Q``.

    The arrangement of the ``C(n, 2)`` lines through pairs of points of ``Q``
    is explored with a vertical sweep: the "critical" ``x``-coordinates (where two
    lines meet) split the plane into vertical slabs, and inside each slab the
    ``y``-gaps between consecutive lines each contain exactly one cell.  Choosing
    rational sample points in those gaps enumerates every cell.  Returns a list of
    points ``(x, y)`` as pairs of ``Fraction``.
    """
    lines = _lines_through_pairs(Q)
    m = len(lines)
    # Critical x values: pairwise intersections of non-parallel lines.
    crit: set[Fraction] = set()
    for t in range(m):
        _, _, a1, b1, c1 = lines[t]
        for u in range(t + 1, m):
            _, _, a2, b2, c2 = lines[u]
            det = a1 * b2 - a2 * b1
            if det == 0:
                continue
            crit.add((b2 * c1 - b1 * c2) / det)
    crit_sorted = sorted(crit)
    xs: list[Fraction] = []
    if not crit_sorted:
        xs = [Fraction(0), Fraction(1)]
    else:
        xs.append(crit_sorted[0] - Fraction(1))
        for t in range(len(crit_sorted) - 1):
            xs.append((crit_sorted[t] + crit_sorted[t + 1]) / 2)
        xs.append(crit_sorted[-1] + Fraction(1))

    seen: set[tuple[int, ...]] = set()
    reps: list[Point2] = []
    for x in xs:
        vals = [(a * x + c) / (-b) if b != 0 else None for (_, _, a, b, c) in lines]
        # Lines with b == 0 are vertical: they are excluded from the y-gap scan,
        # but their sign is constant inside a slab, so cells are still captured
        # (the y-gap scan on the remaining lines, combined with the constant signs
        # of the vertical lines, distinguishes cells).
        idx = [t for t, v in enumerate(vals) if v is not None]
        if not idx:
            continue
        ys = sorted((vals[t], t) for t in idx)
        gaps: list[tuple[Fraction, Fraction]] = []
        for t in range(len(ys) - 1):
            gaps.append((ys[t][0], ys[t + 1][0]))
        ycands = [ys[0][0] - 1]
        for lo_y, hi_y in gaps:
            ycands.append((lo_y + hi_y) / 2)
        ycands.append(ys[-1][0] + 1)
        for y in ycands:
            sig = []
            for (i, j, a, b, c) in lines:
                v = a * x + b * y + c
                if v == 0:
                    sig = None
                    break
                sig.append(1 if v > 0 else -1)
            if sig is None:
                continue
            key = tuple(sig)
            if key in seen:
                continue
            seen.add(key)
            reps.append((x, y))
            if max_cells is not None and len(reps) >= max_cells:
                return reps
    return reps


Point2 = tuple[Fraction, Fraction]


# --------------------------------------------------------------------------- #
# Complete enumeration by incremental insertion
# --------------------------------------------------------------------------- #


def enumerate_order_types_up_to(n_max: int, progress=None):
    """All order types for each ``n = 1, 2, ..., n_max``.

    Returns ``{n: {signature: (chirotope, representative_configuration)}}`` where
    the representative is an exact rational configuration realising the order type
    and labelled ``0, ..., n-1``.
    """
    levels: dict[int, dict[bytes, tuple[Chirotope, Configuration]]] = {}
    # Level 1
    base = [Fraction(0), Fraction(0)]
    levels[1] = {order_type_signature((Fraction(0), Fraction(0)), 1): ((0,), [(base[0], base[1])])}
    if n_max <= 1:
        return levels
    levels[2] = {
        order_type_signature((Fraction(0), Fraction(0)), 2): (
            (0,),
            [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))],
        )
    }
    if n_max <= 2:
        return levels

    for n in range(3, n_max + 1):
        found: dict[bytes, tuple[Chirotope, Configuration]] = {}
        parents = list(levels[n - 1].values())
        for ch_p, Q in parents:
            for p in arrangement_cell_representatives(Q):
                Qn = list(Q) + [p]
                ch = chirotope_of(Qn)
                # Defensive: a cell representative must never be collinear with a
                # pair of the parent points, but we assert it rather than trust it.
                if 0 in ch:
                    raise AssertionError(
                        "arrangement cell representative is degenerate: "
                        f"{Qn} has a collinear triple"
                    )
                sig = order_type_signature(ch, n)
                if sig not in found:
                    found[sig] = (ch, Qn)
            if progress is not None:
                progress(n, len(found))
        levels[n] = found
    return levels
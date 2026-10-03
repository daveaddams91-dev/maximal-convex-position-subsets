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
import pickle
import time
from fractions import Fraction
from pathlib import Path
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


def _generic_rotation(Q: Configuration) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """A rational rotation ``(x,y) -> (u x - v y, v x + u y)`` making y-coordinates distinct.

    Rotation preserves the arrangement's combinatorics, so this is free.  We need
    ``v (x_i - x_j) + u (y_i - y_j) != 0`` for all pairs, i.e. the ratio
    ``-(y_i - y_j)/(x_i - x_j)`` must not equal ``v/u`` whenever the denominator is
    nonzero.  We scan a short deterministic list of ``(u, v)``.
    """
    n = len(Q)
    if n < 2:
        z = Fraction(1)
        return (z, Fraction(0), Fraction(0), z)
    for u in range(0, n + 2):
        for v in range(0, n + 2):
            if u == 0 and v == 0:
                continue
            ok = True
            for i in range(n):
                for j in range(i + 1, n):
                    dy = Q[j][1] - Q[i][1]
                    dx = Q[j][0] - Q[i][0]
                    if v * dx + u * dy == 0:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                # det = u^2 + v^2 must be nonzero for invertibility.
                det = u * u + v * v
                if det:
                    return (Fraction(u), Fraction(v), Fraction(v), Fraction(u))
    raise AssertionError("no generic rotation found; configuration is degenerate")


def _unrotate(p: Point2, rot: tuple[Fraction, Fraction, Fraction, Fraction]) -> Point2:
    """Inverse of the rational rotation ``(x,y) -> (u x - v y, v x + u y)``."""
    u, v = rot[0], rot[1]
    det = u * u + v * v
    x, y = p
    xr = u * x + v * y
    yr = -v * x + u * y
    return (xr / det, yr / det)


def arrangement_cell_representatives(Q: Configuration, max_cells: int | None = None) -> list[Point2]:
    """One rational point in every cell of the arrangement of pair-lines of ``Q``.

    The arrangement of the ``C(n, 2)`` lines through pairs of points of ``Q`` is
    explored with a vertical sweep: the critical ``x``-coordinates (where two
    non-parallel lines meet) split the plane into vertical slabs, and inside each
    slab every ``y``-gap between consecutive lines contains exactly one cell.

    To make the sweep total we first apply a *generic rational shear*
    ``(x, y) -> (x + t y, y)``, which sends every pair-line to a non-vertical line
    unless the pair has equal ``y``-coordinates, so we first rotate the
    configuration by a rational rotation whose cosine and sine avoid the finitely
    many bad values.  Both operations are unimodular on the arrangement's
    combinatorics, so no cell is lost or gained; the returned points are mapped
    back to the original coordinates.

    Returns a list of points ``(x, y)`` as pairs of ``Fraction``.
    """
    lines = _lines_through_pairs(Q)
    m = len(lines)
    n = len(Q)

    # A rational rotation by an angle with cos = u/|.| , sin = v/|.| chosen so that
    # no two points share a y-coordinate afterwards.  We try a short deterministic
    # list of (u, v) pairs and take the first that works.
    rot = _generic_rotation(Q)
    Qr = [((rot[0] * x - rot[1] * y), (rot[2] * x + rot[3] * y)) for (x, y) in Q]
    lines = _lines_through_pairs(Qr)

    # Critical x values: where two non-parallel lines meet, i.e. where the vertical
    # order of the lines changes.  Solving a1 x + b1 y + c1 = a2 x + b2 y + c2 = 0
    # gives x = (b1 c2 - b2 c1) / (a1 b2 - a2 b1).
    crit: set[Fraction] = set()
    for t in range(m):
        _, _, a1, b1, c1 = lines[t]
        for u in range(t + 1, m):
            _, _, a2, b2, c2 = lines[u]
            det = a1 * b2 - a2 * b1
            if det == 0:
                continue  # parallel: never meet, no critical x
            crit.add((b1 * c2 - b2 * c1) / det)
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
        ys = sorted((-(a * x + c) / b, t) for (t, (_, _, a, b, c)) in enumerate(lines) if b != 0)
        if not ys:
            continue
        ycands = [ys[0][0] - 1]
        for t in range(len(ys) - 1):
            ycands.append((ys[t][0] + ys[t + 1][0]) / 2)
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
            # Map the sample point back through the inverse rotation.
            reps.append(_unrotate((x, y), rot))
            if max_cells is not None and len(reps) >= max_cells:
                return reps
    return reps


Point2 = tuple[Fraction, Fraction]


# --------------------------------------------------------------------------- #
# Complete enumeration by incremental insertion
# --------------------------------------------------------------------------- #


def enumerate_order_types_up_to(n_max: int, progress=None, cache_dir=None):
    """All order types for each ``n = 1, 2, ..., n_max``.

    Returns ``{n: {signature: (chirotope, representative_configuration)}}`` where
    the representative is an exact rational configuration realising the order type
    and labelled ``0, ..., n-1``.

    ``cache_dir``, if given, stores each level as a pickle so that repeated runs
    (or the continuation to a larger ``n_max``) do not repeat earlier levels.
    """
    levels: dict[int, dict[bytes, tuple[Chirotope, Configuration]]] = {}
    if cache_dir is not None:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
    for n in range(1, n_max + 1):
        path = Path(cache_dir) / f"ordertypes_n{n}.pkl" if cache_dir is not None else None
        if path is not None and path.exists():
            with path.open("rb") as fh:
                levels[n] = pickle.load(fh)
            if progress is not None:
                progress(n, len(levels[n]), cached=True)
            continue
        if n <= 2:
            levels[n] = _trivial_level(n)
            continue
        prev = levels[n - 1]
        found: dict[bytes, tuple[Chirotope, Configuration]] = {}
        t0 = time.time()
        for k, (ch_p, Q) in enumerate(prev.values()):
            for p in arrangement_cell_representatives(Q):
                Qn = list(Q) + [p]
                ch = chirotope_of(Qn)
                # Defensive: a cell representative must never be collinear with a
                # pair of the parent points, but we assert it rather than trust it.
                if 0 in ch:
                    raise AssertionError(
                        f"arrangement cell representative is degenerate: {Qn}"
                    )
                sig = order_type_signature(ch, n)
                if sig not in found:
                    found[sig] = (ch, Qn)
            if progress is not None and k % 50 == 0:
                progress(n, len(found), cached=False)
        levels[n] = found
        if progress is not None:
            progress(n, len(found), cached=False, elapsed=time.time() - t0)
        if path is not None:
            tmp = path.with_suffix(".tmp")
            with tmp.open("wb") as fh:
                pickle.dump(found, fh)
            tmp.replace(path)
    return levels


def _trivial_level(n: int) -> dict[bytes, tuple[Chirotope, Configuration]]:
    z, o = Fraction(0), Fraction(1)
    if n == 1:
        return {b"tiny": ((0,), [(z, z)])}
    return {b"tiny": ((0,), [(z, z), (o, z)])}
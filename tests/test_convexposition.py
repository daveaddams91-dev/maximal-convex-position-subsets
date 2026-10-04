"""Tests for the definition-level behaviour of M(P).

These are the tests that would catch a *mathematical* error rather than a coding
error: they check that maximal convex subsets are what Definition 2.2 says, that
the two algorithms agree, and that the small exact values are the ones claimed in
the paper.
"""

from __future__ import annotations

import random
import sys
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import (  # noqa: E402
    convex_hull_vertices,
    forbidden_quadruples,
    in_convex_position,
    maximal_convex_subsets,
    maximal_convex_subsets_fast,
)
from mcp.exactgeom import as_configuration, in_general_position, orient  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data" / "ordertypes"


def rand_cfg(n, rng, scale=10):
    while True:
        Q = as_configuration(
            [(F(rng.randrange(0, scale)), F(rng.randrange(0, scale))) for _ in range(n)]
        )
        if len(set(Q)) == n and in_general_position(Q):
            return Q


# --------------------------------------------------------------------------- #
# Definition-level properties
# --------------------------------------------------------------------------- #


def test_maximality_matches_definition() -> None:
    """Every S returned is convex position and cannot be enlarged; every convex
    subset is contained in a returned set."""
    rng = random.Random(1)
    for n in range(4, 10):
        for _ in range(40):
            Q = rand_cfg(n, rng)
            M = maximal_convex_subsets(Q)
            for S in M:
                assert in_convex_position(Q, S)
                # not enlargeable
                for p in range(n):
                    if p not in S:
                        assert not in_convex_position(Q, S | {p}), (
                            f"S={sorted(S)} should have been extendable by {p}"
                        )
            # every convex-position subset is contained in some member of M
            covered = [frozenset(S) for S in M]
            for m in range(3, n + 1):
                for T in combinations(range(n), m):
                    if in_convex_position(Q, T):
                        assert any(frozenset(T) <= S for S in covered), (
                            f"convex subset {sorted(T)} not covered by any maximal set"
                        )
    print("maximality matches Definition 2.2: OK")


def test_M_is_an_antichain() -> None:
    rng = random.Random(2)
    for n in range(4, 10):
        for _ in range(40):
            Q = rand_cfg(n, rng)
            M = maximal_convex_subsets(Q)
            for S, T in combinations(M, 2):
                assert not (S <= T) and not (T <= S), f"{sorted(S)} and {sorted(T)} comparable"


def test_convex_position_set_gives_one_family() -> None:
    """Lemma 4.1 of the paper: if P is in convex position then M(P) = {P}."""
    # A regular pentagon and a regular hexagon, given exactly on the unit circle by
    # the rational parameterisation t -> ((1-t^2)/(1+t^2), 2t/(1+t^2)).
    for k in (5, 6):
        pts = []
        for i in range(k):
            t = F(2 * i + 1, 2 * k)
            pts.append(((1 - t * t) / (1 + t * t), (2 * t) / (1 + t * t)))
        Q = as_configuration(pts)
        assert in_general_position(Q)
        assert len(convex_hull_vertices(Q)) == len(Q), "expected P in convex position"
        assert maximal_convex_subsets(Q) == [frozenset(range(k))], (
            f"P in convex position but |M(P)| != 1"
        )
    print("P in convex position gives M(P) = {P}: OK")


def test_forbidden_quadruples_characterisation() -> None:
    """S in convex position  <=>  S contains no forbidden quadruple."""
    rng = random.Random(3)
    for n in range(4, 11):
        for _ in range(30):
            Q = rand_cfg(n, rng)
            forb = forbidden_quadruples(Q)
            for m in range(3, n + 1):
                for T in combinations(range(n), m):
                    S = frozenset(T)
                    has_forbidden = any(f <= S for f in forb)
                    assert in_convex_position(Q, S) == (not has_forbidden), (
                        f"n={n} S={sorted(S)} forbidden={sorted(f for f in forb if f <= S)}"
                    )
    print("forbidden-quadruple characterisation: OK")


def test_psi_injective_on_convex_position_sets() -> None:
    """Theorem 3.1 of the paper."""
    rng = random.Random(4)
    for n in range(4, 13):
        for _ in range(30):
            Q = rand_cfg(n, rng)
            imgs = []
            for m in range(3, n + 1):
                for T in combinations(range(n), m):
                    S = frozenset(T)
                    if in_convex_position(Q, S):
                        h = convex_hull_vertices(Q, S)
                        inside = frozenset(
                            i
                            for i in range(n)
                            if all(
                                orient(Q[a], Q[b], Q[i]) >= 0
                                for a, b in zip(h, h[1:] + h[:1])
                            )
                        )
                        imgs.append(frozenset(range(n)) - inside)
            assert len(set(imgs)) == len(imgs), f"psi not injective at n={n}"
    print("psi injectivity (Theorem 3.1): OK")


def test_kill_lemma() -> None:
    """Lemma 4.1 of the paper."""
    rng = random.Random(5)
    checked = 0
    for n in range(4, 12):
        for _ in range(20):
            Q = rand_cfg(n, rng)
            for S in maximal_convex_subsets(Q):
                for p in range(n):
                    if p in S:
                        continue
                    h = convex_hull_vertices(Q, S)
                    if all(orient(Q[a], Q[b], Q[p]) >= 0 for a, b in zip(h, h[1:] + h[:1])):
                        continue  # p inside conv(S)
                    checked += 1
                    killed = False
                    for v in S:
                        T = (S - {v}) | {p}
                        hv = convex_hull_vertices(Q, T)
                        if all(orient(Q[a], Q[b], Q[v]) > 0 for a, b in zip(hv, hv[1:] + hv[:1])):
                            killed = True
                            break
                    assert killed, f"kill lemma failed n={n} S={sorted(S)} p={p}"
    print(f"kill lemma: OK ({checked} pairs checked)")


# --------------------------------------------------------------------------- #
# Regression cases: the exact small values
# --------------------------------------------------------------------------- #

KNOWN_F = {3: 1, 4: 4, 5: 7, 6: 11, 7: 20, 8: 38}


def test_known_small_values() -> None:
    """f(n) for n = 3..8, verified over all order types if the database is present."""
    from mcp.aak_database import filename_for, read_realisations

    for n, expected in KNOWN_F.items():
        path = DATA / filename_for(n)
        if not path.exists():
            print(f"  n={n}: database file missing, skipping")
            continue
        best = max(
            len(maximal_convex_subsets(as_configuration(R)))
            for R in read_realisations(path, n)
        )
        assert best == expected, f"f({n}) = {best}, expected {expected}"
        print(f"  f({n}) = {best}  OK")


def test_fast_matches_brute_force_small() -> None:
    for n in range(3, 9):
        rng = random.Random(100 + n)
        for _ in range(20):
            Q = rand_cfg(n, rng, scale=9)
            assert set(maximal_convex_subsets_fast(Q)) == set(maximal_convex_subsets(Q))


if __name__ == "__main__":
    test_maximality_matches_definition()
    test_M_is_an_antichain()
    test_convex_position_set_gives_one_family()
    test_forbidden_quadruples_characterisation()
    test_psi_injective_on_convex_position_sets()
    test_kill_lemma()
    test_known_small_values()
    test_fast_matches_brute_force_small()
    print("\nall convex-position tests passed")
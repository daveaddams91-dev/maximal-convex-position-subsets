"""Unit tests: exact geometry primitives and arrangement cells."""

from __future__ import annotations

import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.exactgeom import in_general_position, orient  # noqa: E402
from mcp.ordertypes import _lines_through_pairs, arrangement_cell_representatives  # noqa: E402


def test_line_equation_matches_orient() -> None:
    rng = random.Random(12345)
    for _ in range(200):
        n = rng.choice([3, 4, 5])
        Q = []
        while len(Q) < n:
            p = (Fr(rng.randrange(-6, 7)), Fr(rng.randrange(-6, 7)))
            if p not in Q:
                Q.append(p)
        lines = _lines_through_pairs(Q)
        for _ in range(30):
            x = Fr(rng.randrange(-20, 21))
            y = Fr(rng.randrange(-20, 21))
            for (i, j, a, b, c) in lines:
                got = a * x + b * y + c
                want = orient(Q[i], Q[j], (x, y))
                assert (got > 0) == (want > 0) and (got < 0) == (want < 0) and (got == 0) == (want == 0), (
                    f"line sign mismatch on {Q[i]},{Q[j]},p={x},{y}: {got} vs {want}"
                )


def test_cell_representatives_are_in_general_position_and_distinct_cells() -> None:
    rng = random.Random(999)
    for _ in range(60):
        n = rng.choice([3, 4, 5, 6])
        while True:
            Q = []
            for _ in range(n):
                p = (Fr(rng.randrange(0, 12)), Fr(rng.randrange(0, 12)))
                if p not in Q:
                    Q.append(p)
            if in_general_position(Q):
                break
        reps = arrangement_cell_representatives(Q)
        assert reps, "no cells found"
        lines = _lines_through_pairs(Q)
        keys = set()
        for p in reps:
            Qn = Q + [p]
            assert in_general_position(Qn), f"degenerate cell rep {p} for {Q}"
            key = tuple(
                1 if (a * p[0] + b * p[1] + c) > 0 else -1 for (_, _, a, b, c) in lines
            )
            assert key not in keys, "duplicate cell returned"
            keys.add(key)


if __name__ == "__main__":
    test_line_equation_matches_orient()
    print("test_line_equation_matches_orient OK")
    test_cell_representatives_are_in_general_position_and_distinct_cells()
    print("test_cell_representatives... OK")
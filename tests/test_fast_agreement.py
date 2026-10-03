"""Cross-check the fast maximal-independent-set routine against the brute force."""

from __future__ import annotations

import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import (  # noqa: E402
    maximal_convex_subsets,
    maximal_convex_subsets_fast,
)
from mcp.exactgeom import in_general_position  # noqa: E402


def rand_cfg(n, rng, scale=8):
    while True:
        Q = []
        for _ in range(n):
            p = (Fr(rng.randrange(0, scale)), Fr(rng.randrange(0, scale)))
            if p not in Q:
                Q.append(p)
        if in_general_position(Q):
            return Q


def main(n_max=9, trials=300):
    rng = random.Random(7)
    for n in range(4, n_max + 1):
        for _ in range(trials):
            Q = rand_cfg(n, rng)
            a = set(maximal_convex_subsets(Q))
            b = set(maximal_convex_subsets_fast(Q))
            assert a == b, (
                f"mismatch n={n}: brute={sorted(map(sorted,a))} fast={sorted(map(sorted,b))} Q={Q}"
            )
        print(f"n={n}: brute force and fast routine agree on {trials} random configurations")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
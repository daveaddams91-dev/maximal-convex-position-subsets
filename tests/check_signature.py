"""Sanity check: the order-type signature must be invariant under relabelling."""

from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.ordertypes import chirotope_of, order_type_signature  # noqa: E402


def rand_cfg(n, rng, scale=10):
    return [(Fr(rng.randrange(0, scale)), Fr(rng.randrange(0, scale))) for _ in range(n)]


def main():
    rng = random.Random(0)
    bad = 0
    for n in (4, 5, 6):
        for _ in range(200):
            # distinct x-coordinates to make collinearity unlikely, then verify
            while True:
                cfg = rand_cfg(n, rng, 25)
                if len(set(cfg)) == n:
                    break
            from mcp.exactgeom import in_general_position

            if not in_general_position(cfg):
                continue
            ch = chirotope_of(cfg)
            sig = order_type_signature(ch, n)
            for perm in itertools.permutations(range(n)):
                cfg2 = [cfg[perm[i]] for i in range(n)]
                sig2 = order_type_signature(chirotope_of(cfg2), n)
                if sig != sig2:
                    bad += 1
                    print("MISMATCH", n, perm)
                    break
            # reflection
            cfg3 = [(x, -y) for (x, y) in cfg]
            if order_type_signature(chirotope_of(cfg3), n) != sig:
                print("REFLECTION MISMATCH", n)
                bad += 1
    print("done, mismatches:", bad)
    assert bad == 0, "signature is not invariant"


if __name__ == "__main__":
    main()
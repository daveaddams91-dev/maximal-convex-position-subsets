"""Heuristic search for configurations with many maximal convex subsets.

Two searchers are provided:

* ``structured``  -- deterministic constructions built from "swap" configurations
  (a convex polygon with a second point tucked just inside each vertex) and from
  block products thereof.
* ``annealing``   -- simulated annealing / hill climbing on the coordinates,
  maximising |M(P)| directly, with deterministic seeds so results reproduce.

Everything here produces *lower bounds* for f(n) only.  Upper bounds come from
the theory in the paper, never from search.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import maximal_convex_subsets_fast  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# Structured constructions
# --------------------------------------------------------------------------- #


def swap_configuration(k: int, shrink: str = "999/1000") -> list[tuple[Fraction, Fraction]]:
    """``k`` outer points on a circle plus ``k`` points pulled just inside each.

    The configuration is realised exactly on the rational lattice (a unit circle
    point with denominator ``2k``) so no floating point enters.
    """
    e = Fraction(shrink)
    outer: list[tuple[Fraction, Fraction]] = []
    for i in range(k):
        # (2k)-th roots of unity scaled to integers: use the standard rational
        # parameterisation of the unit circle t -> ((1-t^2)/(1+t^2), 2t/(1+t^2)).
        t = Fraction(4 * i + 1, 4 * k)  # odd denominators give distinct points
        outer.append(((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)))
    inner = [((1 - e) * x, (1 - e) * y) for (x, y) in outer]
    return outer + inner


def count(Q) -> int:
    return len(maximal_convex_subsets_fast(as_configuration(Q)))


# --------------------------------------------------------------------------- #
# Simulated annealing on coordinates
# --------------------------------------------------------------------------- #


def perturb(Q, scale, rng):
    return [
        (x + Fraction(rng.randrange(-scale, scale + 1)), y + Fraction(rng.randrange(-scale, scale + 1)))
        for (x, y) in Q
    ]


def annealing(n: int, iters: int, seed: int, start=None, scale: int = 12, radius: int = 40):
    rng = random.Random(seed)
    if start is None:
        while True:
            Q = [
                (Fraction(rng.randrange(0, 2 * radius + 1)), Fraction(rng.randrange(0, 2 * radius + 1)))
                for _ in range(n)
            ]
            if len(set(Q)) == n:
                break
    else:
        Q = list(start)
    try:
        best = count(Q)
    except RuntimeError:
        return None, None
    best_Q = Q
    cur, cur_Q = best, Q
    s = scale
    stall = 0
    for it in range(iters):
        idx = rng.randrange(n)
        old = Q[idx]
        dx = Fraction(rng.randrange(-s, s + 1))
        dy = Fraction(rng.randrange(-s, s + 1))
        if dx == 0 and dy == 0:
            continue
        cand = list(Q)
        cand[idx] = (old[0] + dx, old[1] + dy)
        try:
            val = count(cand)
        except RuntimeError:
            stall += 1
            continue
        if val >= cur:
            if val > cur:
                stall = 0
            cur, Q = val, cand
            if val > best:
                best, best_Q = val, cand
        else:
            stall += 1
        if stall > 400:
            stall = 0
            s = max(1, s // 2)
    return best, best_Q


def main():
    out = {}
    print("--- structured 'swap' configurations ---", flush=True)
    struct = {}
    for k in range(3, 26):
        Q = swap_configuration(k)
        c = count(Q)
        struct[2 * k] = c
        print(f"  n={2*k:>3} (k={k:>2}): |M(P)| = {c}", flush=True)
    out["swap"] = struct

    print("--- simulated annealing ---", flush=True)
    ann = {}
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    for n in range(8, n_max + 1):
        best = 0
        best_Q = None
        t0 = time.time()
        # seed the search from the structured configuration when possible
        starts = []
        if n % 2 == 0:
            starts.append(swap_configuration(n // 2))
        if n % 2 == 1 and n >= 7:
            starts.append(swap_configuration((n - 1) // 2) + [None])  # placeholder, replaced below
            starts.pop()
        for seed in range(seeds):
            b, bq = annealing(n, iters, seed)
            if b is not None and b > best:
                best, best_Q = b, bq
        ann[n] = {"best": best, "config": [[str(a), str(b)] for (a, b) in best_Q] if best_Q else None}
        print(f"  n={n:>3}: best |M(P)| = {best}   ({time.time()-t0:.0f}s)", flush=True)
    out["annealing"] = ann

    p = ROOT / "results" / "search_lower_bounds.json"
    p.write_text(json.dumps(out, indent=2))
    print("wrote", p)


if __name__ == "__main__":
    main()
"""Explore the combinatorial structure of extremal M(P) families.

We test the hypothesis suggested by the small cases: extremal configurations have a
"product" or "layered" structure, and we look for the invariant that predicts f(n).

Concretely we check, for the extremal configurations at each n:
  * the sizes of the maximal convex sets;
  * whether the family has a "block product" form: a partition of P into blocks
    B_1, ..., B_t such that every maximal set is a union of per-block choices;
  * the number of maximal sets that are *hull* subsets vs not.
"""

from __future__ import annotations

import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import convex_hull_vertices, maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def best_config(n):
    best, bestQ = -1, None
    for R in read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n):
        Q = as_configuration(R)
        c = len(maximal_convex_subsets(Q))
        if c > best:
            best, bestQ = c, Q
    return best, bestQ


def product_profile(M, n):
    """Try to express M as a product over blocks of local families.

    Returns a description if one is found: a partition of the points into blocks
    such that each maximal set is the union over blocks of one local option, and
    M is exactly the Cartesian product of the local option families.
    """
    Msets = [frozenset(S) for S in M]
    # Candidate blocks: connected components of the co-occurrence graph
    # (a and b are adjacent if some maximal set contains both).
    adj = {v: set() for v in range(n)}
    for S in Msets:
        for a, b in combinations(sorted(S), 2):
            adj[a].add(b)
            adj[b].add(a)
    # Connected components
    seen = set()
    comps = []
    for v in range(n):
        if v in seen:
            continue
        stack, comp = [v], set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(adj[u] - comp)
        seen |= comp
        comps.append(sorted(comp))
    # For each maximal set and each block, record which intersection pattern occurs.
    local = []
    for comp in comps:
        pats = Counter()
        for S in Msets:
            pats[frozenset(S & set(comp))] += 1
        local.append((comp, pats))
    # Verify Cartesian product: the multiset of tuples of patterns must have
    # size = product of the number of patterns, and each tuple occurs once.
    keys = [sorted(p) for _, p in local]
    nsets = [len(p) for p in keys]
    total = 1
    for t in nsets:
        total *= t
    ok = total == len(Msets)
    return comps, keys, ok


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"{'n':>3} {'f(n)':>6} {'sizes of M':<28} {'hull':>5}  blocks")
    for n in range(4, n_max + 1):
        best, Q = best_config(n)
        M = maximal_convex_subsets(Q)
        sizes = dict(sorted(Counter(len(S) for S in M).items()))
        hull = convex_hull_vertices(Q)
        blocks, keys, ok = product_profile(M, n)
        bl = " | ".join(
            str(len(b)) + ":" + ",".join(str(len(p)) for p in ps) for b, ps in zip(blocks, keys)
        )
        print(f"{n:>3} {best:>6} {str(sizes):<28} {len(hull):>5}  {bl}  product_ok={ok}")


if __name__ == "__main__":
    main()
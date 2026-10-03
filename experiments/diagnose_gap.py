"""Diagnose the gap between our order-type enumeration and the AAK database.

Our incremental-insertion enumeration found 3288 order types of 8 points where
the classical (and AAK) count is 3315.  We locate the missing types by scanning
the AAK realisations, computing each one's signature, and checking which of them
is absent from our enumerated level.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402
from mcp.ordertypes import chirotope_of, enumerate_order_types_up_to, order_type_signature  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "ordertype_cache"


def main() -> None:
    n = 8
    upto = enumerate_order_types_up_to(n, cache_dir=CACHE)
    mine = set(upto[n].keys())
    print(f"our enumeration: {len(mine)} order types of {n} points")

    missing = []
    for idx, R in enumerate(read_realisations(ROOT / "data" / "ordertypes" / filename_for(n), n)):
        Q = as_configuration(R)
        sig = order_type_signature(chirotope_of(Q), n)
        if sig not in mine:
            missing.append((idx, [[int(x), int(y)] for (x, y) in R]))
    print(f"AAK types missing from our enumeration: {len(missing)}")
    for idx, R in missing[:10]:
        print(f"  index {idx}: {R}")

    # How many parent order types do the missing types have whose extension is
    # reachable only via a cell we failed to sample?
    if missing:
        from mcp.ordertypes import arrangement_cell_representatives
        from mcp.exactgeom import as_point

        Q = as_configuration(missing[0][1])
        parents = {}
        for k in range(n):
            sub = [i for i in range(n) if i != k]
            subQ = as_configuration([Q[i] for i in sub])
            ch = chirotope_of(subQ)
            sig = order_type_signature(ch, n - 1)
            parents[sig] = (k, subQ)
        present = [parents[s] for s in parents if s in set(upto[n - 1].keys())]
        print(f"  missing type's {n}-1 point sub-configurations found at level {n-1}: "
              f"{len(present)} of {len(parents)}")
        for k, subQ in present:
            cells = arrangement_cell_representatives(subQ)
            print(f"    deleting label {k}: arrangement of {len(subQ)} points has "
                  f"{len(cells)} cells")


if __name__ == "__main__":
    main()
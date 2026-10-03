"""Re-derive level 8 from level 7 with the fixed sampler and compare to AAK."""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import read_realisations  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402
from mcp.ordertypes import (  # noqa: E402
    arrangement_cell_representatives,
    chirotope_of,
    enumerate_order_types_up_to,
    order_type_signature,
)

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "ordertype_cache"


def main() -> None:
    upto = enumerate_order_types_up_to(7, cache_dir=CACHE)
    new: set[bytes] = set()
    t0 = time.time()
    for k, (s, (ch, Q)) in enumerate(upto[7].items()):
        for p in arrangement_cell_representatives(Q):
            cand = list(Q) + [p]
            c = chirotope_of(cand)
            if 0 in c:
                raise SystemExit("degenerate cell representative encountered")
            new.add(order_type_signature(c, 8))
        if k % 25 == 0:
            print(f"  parent {k}/135, found {len(new)}  {time.time()-t0:.0f}s", flush=True)
    print(f"regenerated {len(new)} order types of 8 points ({time.time()-t0:.0f}s)")

    aak = set()
    for R in read_realisations(ROOT / "data" / "ordertypes" / "otypes08.b08", 8):
        aak.add(order_type_signature(chirotope_of(as_configuration(R)), 8))
    print(f"AAK: {len(aak)}")
    print(f"ours - AAK: {len(new - aak)}   AAK - ours: {len(aak - new)}")


if __name__ == "__main__":
    main()
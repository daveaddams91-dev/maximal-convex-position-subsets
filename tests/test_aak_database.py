"""Validate the AAK order-type database reader."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import (  # noqa: E402
    KNOWN_ORDER_TYPE_COUNTS,
    count_realisations,
    filename_for,
    read_realisations,
)
from mcp.exactgeom import as_configuration, in_general_position  # noqa: E402
from mcp.ordertypes import chirotope_of, order_type_signature  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data" / "ordertypes"


def main(n_max: int = 8) -> None:
    for n in range(3, n_max + 1):
        path = DATA / filename_for(n)
        if not path.exists():
            print(f"n={n}: {path.name} not present, skipping")
            continue
        recs = count_realisations(path, n)
        sigs = set()
        bad = dup_x = 0
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            if not in_general_position(Q):
                bad += 1
            if len({x for x, _ in Q}) < n or len({y for _, y in Q}) < n:
                dup_x += 1
            sigs.add(order_type_signature(chirotope_of(Q), n))
        exp = KNOWN_ORDER_TYPE_COUNTS[n]
        ok = recs == exp and len(sigs) == exp and bad == 0 and dup_x == 0
        print(
            f"n={n}: records={recs} (expected {exp}), distinct order types={len(sigs)} "
            f"(expected {exp}), degenerate={bad}, repeated coords={dup_x}  -> {'OK' if ok else 'MISMATCH'}"
        )
        assert ok, f"database validation failed for n={n}"


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
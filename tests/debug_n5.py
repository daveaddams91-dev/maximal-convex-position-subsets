"""Debug the order type enumeration at n=5."""

from __future__ import annotations

import sys
from fractions import Fraction as Fr
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.exactgeom import in_general_position, orient  # noqa: E402
from mcp.ordertypes import (  # noqa: E402
    arrangement_cell_representatives,
    chirotope_of,
    enumerate_order_types_up_to,
    order_type_signature,
)

levels = enumerate_order_types_up_to(5)
for n in range(3, 6):
    print(f"n={n}: {len(levels[n])} order types")

print()
print("--- representatives at n=4 ---")
for sig, (ch, Q) in levels[4].items():
    print("  ", Q, ch)

print()
print("--- n=5 candidates ---")
for sig, (ch, Q) in levels[5].items():
    n = 5
    zeros = [t for t in ch if t == 0]
    gp = in_general_position(Q)
    print("  gp:", gp, "zeros:", len(zeros), Q)
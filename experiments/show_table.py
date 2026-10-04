"""Print the exact table of f(n) computed from the AAK order-type database."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    d = json.loads((ROOT / "results" / "f_aak.json").read_text())
    print(f"{'n':>3} {'f(n)':>8} {'order types':>14}")
    for k in sorted(d, key=int):
        v = d[k]
        print(f"{k:>3} {v['f']:>8} {v['num_order_types']:>14}")


if __name__ == "__main__":
    main()
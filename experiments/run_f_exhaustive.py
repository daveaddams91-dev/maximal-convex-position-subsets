"""Exhaustive computation of f(n) = max |M(P)| over all order types of n points."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.convexposition import maximal_convex_subsets  # noqa: E402
from mcp.ordertypes import enumerate_order_types_up_to  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main(n_max: int, out: Path) -> None:
    t0 = time.time()
    upto = enumerate_order_types_up_to(n_max, progress=lambda n, c: None)
    for n in range(1, n_max + 1):
        print(f"[{time.time()-t0:7.1f}s] n={n}: {len(upto[n])} order types", flush=True)
    levels = upto

    results = {}
    best = {}
    for n in range(3, n_max + 1):
        best_count = -1
        best_reps = []
        counts = {}
        for sig, (ch, Q) in levels[n].items():
            c = len(maximal_convex_subsets(Q))
            counts[c] = counts.get(c, 0) + 1
            if c > best_count:
                best_count = c
                best_reps = [[int(Q[i][0]), int(Q[i][1])] if (Q[i][0].denominator == 1 and Q[i][1].denominator == 1) else [str(Q[i][0]), str(Q[i][1])] for i in range(n)]
        best[n] = best_count
        results[str(n)] = {
            "num_order_types": len(levels[n]),
            "f": best_count,
            "distribution": {str(k): v for k, v in sorted(counts.items())},
            "extremal_representative": best_reps,
        }
        print(f"n={n}: f(n) = {best_count}   (distribution {dict(sorted(counts.items()))})", flush=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print("wrote", out, f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    main(n_max, ROOT / "results" / "f_exhaustive.json")
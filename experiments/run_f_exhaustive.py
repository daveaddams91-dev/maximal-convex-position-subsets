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
CACHE = ROOT / "results" / "ordertype_cache"


def config_to_json(Q):
    out = []
    for (x, y) in Q:
        out.append([str(x), str(y)])
    return out


def main(n_max: int, out_name: str) -> None:
    t0 = time.time()

    def progress(n, count, cached, elapsed=None):
        tag = "cached" if cached else f"{elapsed:.0f}s" if elapsed else "..."
        print(f"    [n={n}] {count} order types ({tag})  t={time.time()-t0:.1f}s", flush=True)

    upto = enumerate_order_types_up_to(n_max, progress=progress, cache_dir=CACHE)

    results = {}
    for n in range(3, n_max + 1):
        best = -1
        best_reps = []
        counts = {}
        best_M = None
        for sig, (ch, Q) in upto[n].items():
            M = maximal_convex_subsets(Q)
            c = len(M)
            counts[c] = counts.get(c, 0) + 1
            if c > best:
                best = c
                best_reps = config_to_json(Q)
                best_M = sorted(sorted(S) for S in M)
        results[str(n)] = {
            "num_order_types": len(upto[n]),
            "f": best,
            "distribution": {str(k): v for k, v in sorted(counts.items())},
            "extremal_representative": best_reps,
            "extremal_family": best_M,
        }
        print(f"n={n}: f(n) = {best}   (order types: {len(upto[n])})", flush=True)

    out = ROOT / "results" / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print("wrote", out, f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    name = sys.argv[2] if len(sys.argv) > 2 else "f_exhaustive.json"
    main(n_max, name)
"""Compute f(n) = max |M(P)| by scanning the AAK order-type database.

For each stored realisation we compute |M(P)| and record the distribution and the
maximising configurations.  This is exact: the database contains exactly one
realisation per order type, and |M(P)| depends only on the order type.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.aak_database import filename_for, read_realisations  # noqa: E402
from mcp.convexposition import maximal_convex_subsets  # noqa: E402
from mcp.exactgeom import as_configuration  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ordertypes"


def main(n_max: int, out_name: str) -> None:
    results_path = ROOT / "results" / out_name
    results = json.loads(results_path.read_text()) if results_path.exists() else {}
    for n in range(3, n_max + 1):
        path = DATA / filename_for(n)
        if not path.exists():
            print(f"n={n}: {path.name} missing, skipping")
            continue
        if str(n) in results:
            print(f"n={n}: cached f(n)={results[str(n)]['f']}")
            continue
        t0 = time.time()
        best = -1
        best_cfgs = []
        dist = Counter()
        count = 0
        for R in read_realisations(path, n):
            Q = as_configuration(R)
            M = maximal_convex_subsets(Q)
            c = len(M)
            dist[c] += 1
            if c > best:
                best = c
                best_cfgs = [[list(R[0]), list(R[1])] for R in [R]]
            elif c == best and len(best_cfgs) < 5:
                best_cfgs.append([[int(x), int(y)] for (x, y) in R])
            count += 1
            if count % 50000 == 0:
                print(f"    n={n}: {count} scanned, best={best}, {time.time()-t0:.0f}s", flush=True)
        results[str(n)] = {
            "f": best,
            "num_order_types": count,
            "distribution": {str(k): v for k, v in sorted(dist.items())},
            "extremal_examples": best_cfgs[:5],
        }
        results_path.write_text(json.dumps(results, indent=2))
        print(f"n={n}: f(n) = {best}  over {count} order types  ({time.time()-t0:.0f}s)", flush=True)
    print("wrote", results_path)


if __name__ == "__main__":
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    name = sys.argv[2] if len(sys.argv) > 2 else "f_aak.json"
    main(n_max, name)
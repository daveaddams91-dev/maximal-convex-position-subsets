"""Reader for the Aichholzer--Aurenhammer--Krasser order-type database.

The format is documented in the database's ``readme.txt``:

* no header, no delimiters;
* for each of the order types of ``n`` points, the coordinates are stored in the
  order ``x_1, y_1, x_2, y_2, ..., x_n, y_n``;
* coordinates are **unsigned** integers, one byte each for ``n <= 8`` (``.b08``)
  and two bytes each for ``n = 9, 10`` (``.b16``, low byte first);
* exactly one representative per order type is stored, with a reflected pair
  contributing a single representative.

Because ``|M(P)|`` depends only on the order type of ``P``, one realisation per
order type suffices.  ``tests/test_aak_database.py`` checks the record count,
general position, and that the realised order types are pairwise distinct and
count exactly as expected.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterator

KNOWN_ORDER_TYPE_COUNTS = {
    3: 1,
    4: 2,
    5: 3,
    6: 16,
    7: 135,
    8: 3315,
    9: 158817,
    10: 14309547,
    11: 2334512907,
}


def width_for(n: int) -> int:
    """Bytes per coordinate in the published files."""
    return 1 if n <= 8 else 2


def record_size(n: int) -> int:
    return 2 * n * width_for(n)


def read_realisations(path: str | Path, n: int) -> Iterator[list[tuple[int, int]]]:
    """Yield each stored realisation as a list of ``n`` unsigned integer ``(x, y)`` pairs."""
    path = Path(path)
    raw = path.read_bytes()
    size = record_size(n)
    if len(raw) % size != 0:
        raise ValueError(
            f"{path}: file length {len(raw)} is not a multiple of the record size {size} "
            f"for n={n}"
        )
    fmt = ("<%dB" if width_for(n) == 1 else "<%dH") % (2 * n)
    for off in range(0, len(raw), size):
        v = struct.unpack_from(fmt, raw, off)
        yield [(v[2 * i], v[2 * i + 1]) for i in range(n)]


def count_realisations(path: str | Path, n: int) -> int:
    return Path(path).stat().st_size // record_size(n)


def filename_for(n: int) -> str:
    return f"otypes{n:02d}.b08" if n <= 8 else f"otypes{n:02d}.b16"
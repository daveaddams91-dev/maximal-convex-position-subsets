# Methodology: exactness, validation, and known bugs

This document records how every number in the paper is produced, what is verified,
and what is *not* verified.  It is intended to be read alongside the code.

## 1. Exactness

Every geometric predicate is an orientation sign of **rational** coordinates.
The only numeric type used for geometry is `fractions.Fraction`; the return type
of `mcp.exactgeom.orient` is one of `-1, 0, +1`.  No floating-point value ever
decides an orientation.  Floating point appears in exactly one place — the
rational parameterisation of the unit circle in the twin-pair construction uses
`math.cos`/`math.pi` only to *choose* angles, after which everything is converted
to `Fraction`; and those experiments are cross-checked against exact brute force.

Order-type signatures use NumPy, but only for integer/reduction arithmetic on the
chirotope (`uint64` rolling hash), never for geometry.

## 2. Two independent implementations of `M(P)`

| routine | method | cost | verified against |
|---|---|---|---|
| `maximal_convex_subsets` | brute force over all `2^n` subsets, hull by monotone chain | `O(2^n n log n)` | — |
| `maximal_convex_subsets_fast` | maximal independent sets of the forbidden-quadruple hypergraph | exponential in `|M(P)|` | the brute force, on 300 random configurations for each `n = 4..12` |

The second routine raises `RuntimeError` if its node budget is exhausted, so a
truncated answer can never be silently mistaken for an exact one.

## 3. Order types

### 3.1 The external database (used for the reported values)

`mcp/aak_database.py` reads the Aichholzer–Aurenhammer–Krasser database.  The
format, from section B of that database's `readme.txt`, is:

* no header, no delimiters;
* for each order type, coordinates in the order `x_1, y_1, x_2, y_2, ..., x_n, y_n`;
* **unsigned** integers; one byte for `n <= 8`, two bytes (low byte first) for
  `n = 9, 10`.

Validation (`tests/test_aak_database.py`), for `n <= 8`:

* record count equals the classical number of order types
  (`1, 2, 3, 16, 135, 3315`);
* the number of *distinct* order types realised equals the same counts;
* every realisation is in general position;
* no two points share an `x` or a `y` coordinate.

Getting this format wrong twice is instructive: reading the coordinates as
*signed*, and reading them as *split* (`x_1..x_n, y_1..y_n`) rather than
*interleaved*, both produce plausible-looking but wrong point sets that pass a
naive "is it in general position" check.  The count check catches both.

### 3.2 Our own enumerator (used as a cross-check)

`enumerate_order_types_up_to` enumerates all order types by incremental
insertion: every order type on `n` points restricts to one on `n-1` points, and
the extension is determined by the cell of the arrangement of pair-lines
occupied by the new point.  Cells are enumerated by a vertical sweep with exact
rational sample points.

Validation: it reproduces the classical counts `1, 1, 1, 2, 3, 16, 135` for
`n = 1..7`, i.e. **3313 of 3315** for `n = 8`.  Two defects were found and are
documented in the paper:

1. the intersection abscissa was computed as `(b2*c1 - b1*c2)/det` instead of
   `(b1*c2 - b2*c1)/det`, which sampled the wrong vertical slabs (3288 -> 3313
   once fixed);
2. the gap scan excluded vertical pair-lines, so configurations containing pairs
   with equal `x` lost cells.  A generic rational rotation before the sweep fixes
   the combinatorics; this is implemented but the full `n = 8` run was not
   repeated afterwards.

**We therefore do not claim our own enumerator is complete at `n = 8`.**  All
reported exact values come from the database scan.

### 3.3 Order-type signature

`order_type_signature` is a complete isomorphism invariant of the *unoriented*
order type: it stacks every relabelling of the chirotope and of its negation,
reduces each row to a 64-bit rolling hash, sorts the hashes, and returns a
BLAKE2b digest.  Two configurations give the same signature iff they are
isomorphic up to reflection (up to a `2^-64` hash collision).
`tests/check_signature.py` verifies invariance under all relabellings and under
reflection for random configurations with `n = 4, 5, 6`.

## 4. Verifying the theorems

| statement | script | scope of check |
|---|---|---|
| Theorem 3.1 (duality) | `experiments/theorem_psi.py` | all 3472 order types with `n <= 8`; 400 random configurations for each `n = 9..16` |
| Corollary 3.2 | `experiments/theorem_psi.py` | same |
| Lemma 4.1 (kill lemma) | `experiments/test_kill_structure.py` | 6126 pairs `(S, p)` with `n <= 7` |
| Proposition 4.4 / Table 6.3 | `experiments/test_theorem_t1.py` | all order types `n <= 8` |
| Table 6.2 (f values) | `experiments/run_f_aak.py` | all order types `n = 3..9` |
| Table 7.1 (twin pairs) | `experiments/search_constructions.py` | exact evaluation of each configuration |

`experiments/reproduce_paper_numbers.py` recomputes every number quoted in the
paper and writes `results/paper_numbers.json`.

## 5. Falsified statements

We record these because they were part of the research process and are
informative:

* **"Every maximal convex subset has `|S| >= min(h, n-h)` where `h` is the hull
  size."**  False: 1292 violations for `n <= 8`; the maximum of `|M(P)|` lives at
  `h = 3` or `4`, not near `n/2`.
* **`S -> S \ {leftmost point of S}` is injective.**  False already at `n = 4`.
* **Our own first cut of `forbidden_quadruples`** used a cyclic-orientation test
  that is correct only when the labelling is in cyclic order; it mislabelled
  convex quadruples.  Fixed by using a direct interior test.
* **`S -> P \ conv(S)` injective on subsets of size `< 3`.**  False (`n = 3`
  counterexample: the empty set and `P` both map to the empty set).  Theorem 3.1
  is stated for `|S| >= 3`.

## 6. Reproducing

```bash
make fetch-data      # download the order-type database (needs network)
make test            # fast correctness tests
make numbers         # recompute every number in the paper (slow)
make figures         # regenerate figures
```

Seeds: the randomised stress tests use fixed seeds (`20261004`, `7`, `999`,
`12345`), so results are reproducible.
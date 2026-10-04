# v1.0.0

Initial release of an honest computational-structural study of the number of
**inclusion-maximal convex-position subsets** of a planar point set.

This release is a **preprint**. It has not been peer reviewed and is not
submitted anywhere.

---

## Research question

For a finite point set `P` in general position in the plane, a subset `S ⊆ P` is
*in convex position* if every point of `S` is a vertex of `conv(S)`, and is a
*maximal convex subset* if no proper superset of `S` inside `P` is in convex
position. Writing

```
M(P) = { maximal convex-position subsets of P }
f(n) = max { |M(P)| : P has n points in general position }
```

we ask how fast `f(n)` grows.

This is a **third** extremal question, distinct from two neighbours:
* the **minimum** number of convex subsets is Erdős Problem 838 (exact values to
  `n ≤ 11` by Savova, 2026);
* the number of **empty** convex polygons ("holes") is a large literature.

As far as we could determine, the extremal count of *maximal* convex-position
subsets does not appear to have been studied. We searched zbMATH Open, Crossref,
OpenAlex, arXiv and MathOverflow under many phrasings; see §7 of the paper.

## Main theorem

**Duality.** For `P` in general position and `S, T ⊆ P` in convex position with
`|S|, |T| ≥ 3`,

```
P \ conv(S) = P \ conv(T)   ⟹   S = T.
```

Maximality is *not* used in the proof. Consequently the map `ψ(S) = P \ conv(S)`
is a bijection from the family of convex-position subsets onto the family of
*hull-closed* subsets `W ⊆ P` with `W = P ∩ conv(W)`. In particular two distinct
maximal convex subsets are always distinguished by their hull as a subset of `P`.

**Kill lemma.** If `S ∈ M(P)`, `p ∈ P \ S` and `p ∉ conv(S)`, then `p` destroys at
least one vertex of `S`.

## Main computational contribution

Exact values of `f(n)`, exhaustive over **all** order types of `n` points:

| n | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| f(n) | 1 | 4 | 7 | 11 | 20 | 38 | 62 |

computed by scanning the Aichholzer–Aurenhammer–Krasser order-type database
(1, 2, 3, 16, 135, 3315 and 158 817 order types respectively).

Also measured: the maximum of `|M(P)|` at fixed hull size `h` (the optimum sits
at `h = 3` or `4`, and `|M(P)| = 1` when `P` is in convex position); the
distribution of `|M(P)|` over all order types; and explicit twin-pair
configurations.

## Reproducing

```bash
make install
make fetch-data      # third-party order-type database, ~6 MB, network required
make test            # 10 tests
make numbers         # recompute every number in the paper (~5 h for n = 9)
make figures
make paper           # requires pdflatex or tectonic
```

The single command behind the main table is

```bash
python experiments/run_f_aak.py 9 f_aak.json
```

All geometry is exact: orientation predicates use `fractions.Fraction` only, and
no floating-point value ever decides an orientation. All randomised components
use fixed seeds.

## Known limitations

These are stated in full in §8 of the paper and in `README.md`.

1. **The upper bound is Sperner's.** We prove `f(n) ≤ C(n, ⌊n/2⌋)` and do not
   improve it. The conjecture `f(n) = 2^{Θ(n)}` is **unproved in both
   directions**: we have no upper bound better than Sperner and no construction we
   can prove beats `2^{n/2}`.
2. **Exact values stop at `n = 9`.** `f(10)` needs a scan of 14 309 547 order
   types (~572 MB); extrapolating our timings this would take ~19 days.
3. **Our own order-type enumerator is incomplete at `n = 8`** (3313 of 3315
   types). The reported values come from the external database, which we
   validated but did not produce. Two bugs in our enumerator are documented in
   §5.4 of the paper rather than hidden.
4. **Explicit constructions give no asymptotic lower bound.** The twin-pair
   constructions are *weaker* than exhaustive search at small `n` (best value 14
   at `n = 8`, versus `f(8) = 38`), so they do not support `f(n) ≥ 2^{n/2}`.
5. **Novelty is not established.** We did not find prior work on `f`, but our
   search could not reach MathSciNet or Google Scholar. We claim only "we did
   not find a prior result", never "this is the first".
6. **The layer-profile observation is verified only for `n ≤ 8`** and may not
   persist.
7. **Five of our own conjectures were refuted by our own data** and are reported
   as such in `docs/mathematical_notes.md`, including the expectation that twin
   pairs give `2^{n/2}`.

## Third-party data

`data/ordertypes/` is **not** redistributed in this repository. It is the
point-set order-type database of O. Aichholzer, F. Aurenhammer and H. Krasser
(Graz University of Technology), used under the terms stated on their
distribution page. Run `make fetch-data` to obtain it. The MIT licence in
`LICENSE` covers the code in this repository only.
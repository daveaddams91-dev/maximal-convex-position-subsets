# Maximal Convex-Position Subsets of Planar Point Sets

**How many inclusion-maximal subsets of an $n$-point set can lie in convex position?**

For a finite set $P\subset\mathbb{R}^2$ in general position, a subset $S\subseteq P$ is in
**convex position** if every point of $S$ is a vertex of $\operatorname{conv}(S)$, and is
**maximal convex** if no proper superset of $S$ inside $P$ is in convex position. Writing
$M(P)$ for the family of maximal convex subsets and

$$f(n)=\max\{|M(P)|:\ P\subset\mathbb{R}^2,\ |P|=n,\ P \text{ in general position}\},$$

this repository computes $f$ exactly for small $n$, proves a duality theorem governing the
structure of $M(P)$, and gives explicit configurations with exponentially many maximal convex
subsets.

---

## TL;DR

- **Exact values** (exhaustive over *all* order types of $n$ points):
  $f(3)=1,\ f(4)=4,\ f(5)=7,\ f(6)=11,\ f(7)=20,\ f(8)=38,\ f(9)=62$.
- **Main theorem.** The map $\psi(S)=P\setminus\operatorname{conv}(S)$ is **injective on the
  entire family** of convex-position subsets — maximality is not used — and identifies it with
  the lattice of hull-closed subsets $W\subseteq P$ satisfying $W=P\cap\operatorname{conv}(W)$.
- **Kill lemma.** If $S\in M(P)$ and $p\in P\setminus S$ lies outside $\operatorname{conv}(S)$,
  then $p$ destroys at least one vertex of $S$.
- **Sensitivity.** On fixed $n=14$ points, $|M(P)|$ ranges over $34,\dots,121$ as a single
  rational separation parameter varies.
- **Conjecture.** $f(n)=2^{\Theta(n)}$. We prove only the Sperner bound
  $f(n)\le\binom{n}{\lfloor n/2\rfloor}$ and give no construction beating $2^{n/2}$ —
  our explicit twin-pair constructions are *weaker* than exhaustive search already at $n=8$.

---

## Research question

Maximising the number of convex $k$-gons for a fixed $k$ is trivial: it is $\binom{n}{k}$,
attained when $P$ is in convex position. Counting *all* convex subsets of a given $P$ is
well studied (Mitchell–Rote–Sundaram–Woeginger, 1995). The **minimum** number of convex
subsets is Erdős Problem 838 (exact values to $n\le 11$ by Savova, 2026).

The quantity studied here is a third one: the **maximum** number of convex subsets that
**cannot be enlarged**. It is an order-type invariant, and it is genuinely different — for
$P$ in convex position, $|M(P)|=1$ while the total count of convex subsets is $2^{\Theta(n)}$.

## Main result

**Theorem (duality).** Let $P$ be in general position and $S,T\subseteq P$ be in convex
position with $|S|,|T|\ge 3$. Then

$$P\setminus\operatorname{conv}(S)=P\setminus\operatorname{conv}(T)\ \Longrightarrow\ S=T.$$

*Proof.* Set $W=P\cap\operatorname{conv}(S)=P\cap\operatorname{conv}(T)$. Since
$S\subseteq\operatorname{conv}(S)$ we get $S\subseteq W$, likewise $T\subseteq W$. As
$S$ is in convex position, $\operatorname{vert}(S)=S$, so $\operatorname{conv}(S)
=\operatorname{conv}(\operatorname{vert}(S))\subseteq\operatorname{conv}(T)$. By symmetry
$\operatorname{conv}(T)\subseteq\operatorname{conv}(S)$, hence $\operatorname{conv}(S)
=\operatorname{conv}(T)$ and $S=T$. $\square$

The hypothesis that $S$ and $T$ are *maximal* is never used: the theorem holds for the whole
family $\mathcal{C}(P)$ of convex-position subsets. Consequently $\psi$ is a bijection from
$\mathcal{C}(P)$ onto the hull-closed subsets, so $|\mathcal{C}(P)|=|\{W\subseteq P:
W=P\cap\operatorname{conv}(W)\}|$.

**Corollary.** Two distinct maximal convex subsets are always distinguished by their hull
*as a subset of $P$*.

## Why this is interesting

$M(P)$ is an antichain (any subset of a convex-position set is in convex position), so
Sperner gives $|M(P)|\le\binom{n}{\lfloor n/2\rfloor}$. The duality theorem says that
$M(P)$ is not merely an antichain but the facet set of a complex that is *isomorphic to a
lattice of closed sets* — a rigidity that a bare antichain bound does not see, and that
explains why $|M(P)|$ is so sensitive to the order type (Table 7.1 of the paper shows
$|M(P)|$ ranging from 34 to 121 on 14 points purely as a rational separation parameter
varies).

The extremal configurations are themselves striking: at $n=6$ and $n=8$ every maximal
convex subset has the same size ($n/2$) and **every point of $P$ lies in the same number
of maximal subsets** — perfectly balanced.

## Repository structure

```
maximal-convex-position-subsets/
├── README.md
├── LICENSE                     MIT (see note on third-party data)
├── Makefile                    fetch-data / test / numbers / figures / paper
├── pyproject.toml
├── docs/
│   ├── methodology.md          exactness, validation, and the bugs we found
│   └── mathematical_notes.md   development notes, rejected conjectures
├── src/mcp/
│   ├── exactgeom.py            exact rational orientation primitives
│   ├── convexposition.py       convex hull, convex position, M(P), two algorithms
│   ├── ordertypes.py           chirotopes, canonical signatures, cell enumeration
│   └── aak_database.py         reader for the AAK order-type database
├── tests/
│   ├── test_exactgeom.py       line equations and cell representatives
│   ├── test_fast_agreement.py  brute force vs. output-sensitive enumeration
│   ├── test_aak_database.py    database format validation
│   ├── check_signature.py      order-type signature invariance
│   └── test_convexposition.py  definitions, edge cases, regression cases
├── experiments/
│   ├── run_f_aak.py            exact f(n) from the order-type database
│   ├── theorem_psi.py          verification of the duality theorem
│   ├── test_kill_structure.py  verification of the kill lemma
│   ├── search_constructions.py twin-pair constructions
│   ├── reproduce_paper_numbers.py  recompute every quoted number
│   └── make_figures.py         figures, generated from results/
├── results/                    computed data (JSON) and logs
├── figures/                    generated PNG figures
└── paper/
    └── main.tex                the paper (LaTeX, self-contained)
```

## Reproducing the results

```bash
make install      # pip install -e ".[dev,plots]"
make fetch-data   # download the order-type database (~6 MB; needs network)
make test         # fast correctness tests
make numbers      # recompute every number in the paper (slow: ~5 h for n=9)
make figures      # regenerate figures from results/
```

The single command that reproduces the main experimental result is

```bash
python experiments/run_f_aak.py 9 f_aak.json
```

All randomised components use fixed seeds, so results are deterministic.

### Third-party data

`data/ordertypes/` contains the point-set order-type database of Aichholzer, Aurenhammer
and Krasser (Graz University of Technology), obtained from their distribution page. **It is
not covered by this repository's MIT licence and is not redistributed here**; see `LICENSE`
and `docs/methodology.md` §3.1. We use it to obtain one realisation per order type; all
geometry computed from it is exact.

If `make` is unavailable, fetch it directly:

```bash
mkdir -p data/ordertypes
BASE=http://www.ist.tugraz.at/staff/aichholzer/research/rp/triangulations/ordertypes/data
for n in 03 04 05 06 07 08 09; do
  curl -fsSL -o data/ordertypes/otypes$n.b08 $BASE/otypes$n.b08
done
python tests/test_aak_database.py 8     # validates the reader
```

The test suite passes with or without the database; the database-dependent tests skip
gracefully when the files are absent.

## Examples

```python
from fractions import Fraction as F
from mcp import as_configuration, maximal_convex_subsets

# Four points, one inside the triangle of the other three.
P = as_configuration([(0, 0), (4, 0), (0, 4), (1, 1)])
M = maximal_convex_subsets(P)
print(len(M))                       # 4
print(sorted(sorted(S) for S in M))  # [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]

# P in convex position: the only maximal convex subset is P itself.
P = as_configuration([(0, 0), (4, 0), (4, 4), (0, 4), (2, 3)])
print(len(maximal_convex_subsets(P)))  # 1
```

## Limitations

We state these plainly, because they bound what the results are worth.

1. **The upper bound is Sperner's.** We prove
   $f(n)\le\binom{n}{\lfloor n/2\rfloor}$ and do not improve it. The conjecture
   $f(n)=2^{\Theta(n)}$ is unproved; we give a lower bound of $2^{n/2}$ from twin pairs and no
   matching upper bound.
2. **Exact values stop at $n=9$.** $f(10)$ needs a scan of $14\,309\,547$ order types
   ($\approx 572$ MB of data); we did not run it.
3. **Our own order-type enumerator is incomplete at $n=8$** ($3313$ of $3315$ types). The
   reported values come from the external database, which we validated thoroughly but did
   not produce. Two bugs in our enumerator are documented rather than hidden.
4. **Constructions give no asymptotic lower bound.** The twin-pair constructions are *weaker*
   than exhaustive search at small $n$ (best value 14 at $n=8$, versus $f(8)=38$), so they
   do not support $f(n)\ge 2^{n/2}$. We have no construction we can prove beats $2^{n/2}$.
5. **Novelty is not established.** We did not find prior work on $f$, but our search could
   not reach MathSciNet or Google Scholar. We claim only that "we did not find a prior
   result", never "this is the first".
6. **The layer-profile observation (optimum at hull size 3 or 4) is verified only for
   $n\le 8$** and may not persist.
7. **Two of our own initial conjectures were refuted by our own data** and are reported as
   such: the bound $|S|\ge\min(h,n-h)$ on maximal subsets, and the expectation that
   twin pairs give $2^{n/2}$.

## Related work

- Rote–Woeginger–Zhu–Wang (1991); Rote–Woeginger (1992); Mitchell–Rote–Sundaram–Woeginger
  (1995): counting convex polygons in a **given** point set.
- Huemer–Oliveros–Pérez-Lantero–Torra–Vogtenhuber (2022): linear identities among counts of
  convex $k$-gons by interior-point count.
- Erdős Problem 838 / Savova (2026): the **minimum** number of convex subsets.
- Bárány–Valtr (2004), Pinchasi–Radičić–Sharir (2006), Bae (2022), Suk (2017):
  **empty** convex polygons (holes) — a different notion from ours.
- Aichholzer–Aurenhammer–Krasser (2002, 2001, 2007): the order-type database used for the
  exact computations.

## Citation

```bibtex
@misc{maximalconvex2026,
  title  = {On the Extremal Number of Maximal Convex-Position Subsets
            of a Planar Point Set},
  note   = {Preprint},
  year   = {2026},
  url    = {https://github.com/daveaddams91-dev/maximal-convex-position-subsets}
}
```

## Licence

MIT — see `LICENSE`. The order-type database under `data/ordertypes/` has separate terms.
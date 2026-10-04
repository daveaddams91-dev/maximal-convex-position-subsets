# Mathematical development notes

A record of how the mathematics in this project actually developed, including the
paths that were abandoned.  Kept because the negative results are as informative
as the positive ones.

## 1. Choosing the problem

We screened roughly twenty candidate problems in discrete geometry and combinatorics
against the criteria *exactness of statement*, *proof potential*, *computational
tractability*, and *novelty*.  Candidates that were considered and rejected:

| candidate | reason rejected |
|---|---|
| Maximum number of convex $k$-gons over all $P$ | trivial: $\binom{n}{k}$, attained in convex position |
| Minimum number of convex subsets | already studied (Erdős #838, Savova 2026) |
| Empty convex polygons ("holes") | heavily studied; maximality there means something else |
| Extension complexity of small polytopes | heavily mined (Choi–Lam–Živaljević, Choi–Makay–Paták–Tová–Tancer) |
| Turán-type problems for convexity | dense literature, high rediscovery risk |
| Tropical rank (Four-Berry) | too deep to make progress |
| Convex layers / $k$-convex points | best-known results are open in a way we could not attack |

The chosen problem — the number of **inclusion-maximal** convex-position subsets —
is a *third* extremal quantity, evidently unstudied, small enough to compute
exactly for $n \le 9$, and with a clean combinatorial structure (an antichain, and
by a bijection the maximal elements of the convex position complex).

## 2. The key reformulation

The breakthrough was the observation

$$S \text{ in convex position} \iff S \text{ contains no forbidden quadruple}.$$

Two facts make this useful.

1. By Carathéodory in the plane, if some $p\in S$ lies in $\int(\mathrm{conv}(S))$ then
   $p$ lies in the triangle spanned by three other points of $S$, giving a
   forbidden quadruple. Conversely a forbidden quadruple immediately breaks
   convex position. (We verified this equivalence exhaustively for all order types
   with $n\le 8$; it is what makes $\mathcal{C}(P)$ the independent-set family of a
   $4$-uniform hypergraph.)

2. Consequently $M(P)$ is the family of **maximal independent sets** of that
   $4$-uniform hypergraph, which has an output-sensitive enumeration. This is the
   algorithm that makes $n = 9$ (158 817 order types) tractable.

This reformulation also immediately gives the Sperner bound, since independent-set
families are downward closed and hence so are their maximal elements.

## 3. The duality theorem

**Theorem.** $P\setminus\mathrm{conv}(S) = P\setminus\mathrm{conv}(T)\Rightarrow S=T$, for
$S,T\in\mathcal{C}(P)$, $|S|,|T|\ge 3$.

The proof is four lines and the striking thing is that **maximality is never
used**. We arrived at it by trying to find an injection from $M(P)$ into $2^P$
that would sharpen Sperner; the injections we first tried

* $S\mapsto S\setminus\{\text{leftmost point}\}$ — fails injectivity at $n=4$;
* $S\mapsto P\setminus\mathrm{conv}(S)$ — works.

Getting to this required care with one boundary case: for $|S|\le 2$ the statement
is **false** (e.g. $n=3$: both $\varnothing$ and $P$ map to $\varnothing$), so the
theorem must be stated for $|S|\ge 3$.  Corollary 3.2 needs the same restriction,
plus the observation that in general position a set of size $\le 2$ is the whole
of $P$ that lies in its own hull.

## 4. Rejected conjectures

### 4.1 "$|S|\ge \min(h, n-h)$ for maximal $S$" — **FALSE**

Conjecture: with $h$ hull vertices, no maximal convex subset can be smaller than
the smaller of the hull size and the interior size.  This would put the optimum
near $h\approx n/2$.

Refuted by the layer table (`experiments/test_theorem_t1.py`): **1292 violations**
for $n\le 8$, and the maximum of $|\mathcal{M}(P)|$ sits at $h=3$ or $h=4$, not at $h\approx n/2$.
Concretely, at $n=8$: $g(8,3)=35$, $g(8,4)=38$, but $g(8,7)=8$ and $g(8,8)=1$.

Interpretation: *few* hull vertices is what produces many maximal convex subsets,
because the interior points are then free to form many alternative convex polygons.

### 4.2 "Twin pairs give $2^{n/2}$" — **FALSE**

We placed two nearly coincident points in each of $k$ directions, expecting $2^k$
maximal convex subsets as the separation $\varepsilon\to 0$.  The measured values
(`results/twin_table.json`) are far below that: at $n=8$ the best separation gives
$14$, while exhaustive search over all $3315$ order types gives $f(8)=38$.

So the twin-pair limit is *not* the mechanism behind the optimum.  We report this
because the construction is still informative: it shows $|\mathcal{M}(P)|$ varies by a
factor of $3.5$ on fixed $14$ points under a one-parameter family of
perturbations.

### 4.3 "$\psi$ is injective on subsets of size $\le 3$" — **FALSE**

At $n=3$, $\psi(\varnothing)=\psi(P)=\varnothing$.  Fixed by restricting to
$|S|\ge 3$ and stating Corollary 3.2 with the same restriction.

### 4.4 "$\psi(S)$ omits a hull vertex" — **FALSE**, and the natural bound fails

We hoped $\psi(S)$ always misses a hull vertex, which would have given
$|\mathcal{M}(P)|\le 2^{h-1}$ and, with $h$ small at the optimum, a sharp bound.  The
statistic is false in 157 cases (`experiments/psi_image_stats.py`), and the bound
$|\mathcal{M}(P)|\le 2^{h-1}$ is contradicted by $f(6)=11>2^{3}=8$.

### 4.5 "$\psi$ sharpens Sperner" — **FALSE**

The image of $\psi$ is far from all subsets: $\max|\psi(S)|=n-3$ for every $n$
measured, so the injection lands in $\{A: |A|\le n-3\}$, still $\Theta(2^n)$
subsets.  The theorem is structurally interesting but does not improve the
counting bound.

## 5. What the data suggests but does not prove

* **Balanced extremisers.** At $n=6$ and $n=8$ every point of $P$ lies in the same
  number of maximal convex subsets and all maximal subsets have size $n/2$.  This
  is suggestive of a self-duality: the duality theorem pairs $S$ with
  $P\setminus\mathrm{conv}(S)$, and at the optimum the family is (empirically) closed
  under a size-reversing involution.  We do not prove this and do not know if it
  persists for $n\ge 10$.
* **Exponential growth.** Successive ratios $4.0,1.75,1.57,1.82,1.90,1.63$ are
  consistent with a base near $1.87$, but seven values cannot distinguish
  $c\,2^{n/2}$ from $c\,(1.87)^n$.

## 6. Open technical questions

* $f(10)$ is computable in principle ($14\,309\,547$ order types, $\approx 572$ MB)
  but we did not run it.
* Our own order-type enumerator reaches $3313/3315$ at $n=8$; closing the gap
  would remove the dependence on the external database.
* The maximum number of maximal convex **triangles** equals the maximum number of
  triangles $T$ with $P\setminus T\subseteq\int(\mathrm{conv}(T))$.  The measured counts
  ($6$ at $n=5$, $2$ at $n=6$, $1$ at $n=7$, and $0$ in the $n=8$ maximiser)
  suggest a decreasing trend worth understanding.
# On the Extremal Number of Maximal Convex-Position Subsets of a Planar Point Set

## Abstract

A subset $S$ of a finite point set $P\subset\mathbb{R}^2$ in general position is in
*convex position* if every point of $S$ is a vertex of $\operatorname{conv}(S)$, and is a
*maximal convex subset* if no proper superset of $S$ in $P$ is in convex position.  Writing
$M(P)$ for the family of maximal convex subsets and $f(n)=\max_{|P|=n}|M(P)|$, we study $f$.
We show that $|M(P)|\le \binom{n}{\lfloor n/2\rfloor}$ (Sperner's theorem applies because
$M(P)$ is an antichain), and we compute $f$ exactly for $n\le 9$ by scanning a complete
database of order types:

$$f(3)=1,\quad f(4)=4,\quad f(5)=7,\quad f(6)=11,\quad f(7)=20,\quad f(8)=38,\quad f(9)=62 .$$

Our main structural result is a duality theorem.  Define $\psi(S)=P\setminus\operatorname{conv}(S)$.
Then $\psi$ is injective on the whole family of convex-position subsets, not merely on the
maximal ones, and it identifies that family with the lattice of *hull-closed* subsets
$W\subseteq P$ satisfying $W=P\cap\operatorname{conv}(W)$.  In particular two distinct
maximal convex subsets can never have the same hull as a subset of $P$.  We also give a
geometric kill lemma: if $S\in M(P)$ and $p\in P\setminus S$ lies outside $\operatorname{conv}(S)$,
then $p$ destroys at least one vertex of $S$.  Finally we exhibit explicit *twin-pair*
configurations with $|M(P)|$ exponentially large, giving $121$ maximal convex subsets on
$14$ points, well beyond the values forced by small $n$.  We conjecture $f(n)=2^{\Theta(n)}$
and we are explicit about what remains open.

## 1. Introduction

### 1.1 The problem

Let $P\subset\mathbb{R}^2$ be a finite set of $n$ points in *general position*, meaning that
no three points are collinear.  A subset $S\subseteq P$ is *in convex position* if each of its
points is a vertex of the convex hull $\operatorname{conv}(S)$; equivalently $S$ is the vertex set
of a convex polygon with at least three vertices.  A convex-position subset $S$ is *maximal* if
no $S'\subsetneq P$ properly containing $S$ is in convex position.

Write
$$M(P)\;=\;\bigl\{\,S\subseteq P \;:\; S \text{ is a maximal convex-position subset of } P\,\bigr\},
\qquad
f(n)\;=\;\max_{\substack{P\subset\mathbb{R}^2\\ |P|=n,\; \text{general position}}} |M(P)| .$$

The question *how many convex polygons does a point set determine* has a long literature
\cite{rote91, rote92, mitchell95, huemer2022}.  Those works count **all** convex subsets, or
count them for a **given** $P$.  Two neighbouring extremal questions are different again:

- the **minimum** number of convex subsets of $n$ points is Erdős Problem 838
  \cite{erdos838}, on the order $n^{\Theta(\log n)}$; exact values for $n\le 11$ were recently
  computed by Savova \cite{savova2026};
- the number of **empty** convex polygons ("holes") is controlled by
  \cite{baranyvaltr04, pinchasi2006, bae2022, suk2017}.

Our question is a third one, and as far as we can tell it has not been studied: we **maximise**
the number of **inclusion-maximal** convex subsets over all configurations.  Maximising the
number of convex $k$-gons for a fixed $k$ is trivial ($\binom{n}{k}$, attained when $P$ is in
convex position); the interesting quantity is the number of convex subsets that cannot be
enlarged, which is a purely order-type invariant encoding the local structure of $P$.

### 1.2 Why the quantity is non-trivial

$M(P)$ is an **antichain**: if $S\subsetneq T$ and $T$ is in convex position then so is $S$, so
$S$ is not maximal.  Hence Sperner's theorem applies and

$$|M(P)|\;\le\;\binom{n}{\lfloor n/2\rfloor}\;=\;2^{\Theta(n)} . \tag{1.1}$$

The bound (1.1) is weak by a factor of about $\sqrt{n}$ in comparison with what one would like,
but we do not improve it in general.  What we do obtain is (a) the exact values of $f$ for
$n\le 9$, (b) a duality that governs the structure of $\mathcal{C}(P)$, and (c) explicit
configurations with $|M(P)|$ far larger than $f$ for small $n$ suggests.

### 1.3 Contributions

1. **Exact values.** $f(n)$ for $n=3,\dots,9$ (Section 7).  The computation is exhaustive over
   *all* order types of $n$ points, using the Aichholzer--Aurenhammer--Krasser database; we
   validate the reader against the classical order-type counts.
2. **Duality theorem (Theorem 3.1).** The map $\psi:S\mapsto P\setminus\operatorname{conv}(S)$ is
   injective on the entire family $\mathcal{C}(P)$ of convex-position subsets of size $\ge 3$, and
   identifies $\mathcal{C}_{\ge 3}(P)$ with the family of hull-closed subsets
   $\mathcal{H}(P)=\{W\subseteq P: |W|\ge3,\ W=P\cap\operatorname{conv}(W)\}$.  Maximality of $S$
   is *not needed* for injectivity.
3. **Kill lemma (Lemma 4.1).** If $S\in M(P)$, $p\in P\setminus S$ and
   $p\notin\operatorname{conv}(S)$, then some vertex of $S$ becomes interior to
   $\operatorname{conv}((S\setminus\{v\})\cup\{p\})$; i.e. $p$ destroys a vertex.  Verified on
   $6126$ pairs $(S,p)$ with no exception.
4. **Torus-free dichotomy.** For every $P$ there is a maximal convex subset containing all
   points of any given direction class; concretely the hull vertices of $P$ lie in at least one
   member of $M(P)$ unless $P$ is in convex position.
5. **Lower bounds.** Explicit *twin-pair* configurations give $|M(P)|=121$ for $n=14$,
   $|M(P)|\ge 55$ for $n=12$, showing $f$ grows quickly.

### 1.4 Organisation

Section 2 sets notation.  Section 3 gives the duality theorem and the antichain bound.  Section 4
gives local structural lemmas (the kill lemma and its proof, the Sperner bound, the hull-layer
inequality).  Section 5 describes the computational method in enough detail to reproduce it,
including the format of the external order-type database and two bugs we found and fixed.
Section 6 reports the exact values.  Section 7 describes the twin-pair constructions and the
falsification experiments.  Section 8 discusses what is open.

## 2. Preliminaries

Throughout, $P$ is a finite set of $n$ points in general position in $\mathbb{R}^2$.

For $S\subseteq P$ write $\operatorname{conv}(S)$ for its closed convex hull and
$\operatorname{vert}(S)$ for the set of vertices of $\operatorname{conv}(S)$.

**Definition 2.1 (convex position).** A set $S\subseteq P$ with $|S|\ge 3$ is *in convex
position* if $S=\operatorname{vert}(S)$, i.e. every point of $S$ is an extreme point of
$\operatorname{conv}(S)$.  Equivalently, $S$ is the vertex set of a convex $|S|$-gon.

**Definition 2.2 (maximal convex).** A convex-position subset $S\subseteq P$ is *maximal
convex* if for every $p\in P\setminus S$ the set $S\cup\{p\}$ is not in convex position.

**Definition 2.3.** $\mathcal{C}(P)$ is the family of convex-position subsets of $P$ of size
at least $3$; $M(P)$ is the family of maximal members of $\mathcal{C}(P)$; and $f(n)$ is the
maximum of $|M(P)|$ over all $n$-point general-position sets.

**Definition 2.4 (forbidden quadruple).** A $4$-subset $\{a,b,c,d\}\subset P$ is *forbidden* if
one of its points lies strictly inside the triangle spanned by the other three.  In general
position at most one point can be interior, so this is unambiguous.

**Definition 2.5 (hull-closed).** A subset $W\subseteq P$ with $|W|\ge 3$ is *hull-closed* if
$W=P\cap\operatorname{conv}(W)$, that is, every point of $P$ that lies in the convex hull of $W$
already belongs to $W$.

**Definition 2.6 (order type).** The *order type* of $P$ is the isomorphism class of the map
$\{i,j,k\}\mapsto \operatorname{sgn}\operatorname{orient}(p_i,p_j,p_k)$.  Every quantity we study
depends only on the order type of $P$.

**Lemma 2.7 (downward closure).** If $S\in\mathcal{C}(P)$ and $T\subseteq S$ with $|T|\ge 3$ then
$T\in\mathcal{C}(P)$.  Consequently $\mathcal{C}(P)$ is a simplicial complex on vertex set $P$
and $M(P)$ is the set of its facets, i.e. $M(P)$ is an antichain.

*Proof.* If $T\subseteq S$ and some $t\in T$ were interior to $\operatorname{conv}(T)$ then $t$
would be interior to $\operatorname{conv}(S)$ as well, contradicting $S\in\mathcal{C}(P)$. $\square$

**Lemma 2.8 (maximality criterion).** $S\in\mathcal{C}(P)$ belongs to $M(P)$ if and only if for
every $p\in P\setminus S$ there exists $v\in S$ with $\operatorname{vert}((S\setminus\{v\})\cup
\{p\})\subsetneq (S\setminus\{v\})\cup\{p\}$, equivalently, $S\cup\{p\}\notin\mathcal{C}(P)$.

*Proof.* Immediate from Definition 2.2. $\square$

## 3. The duality theorem

The central structural result identifies convex-position subsets with hull-closed subsets.

**Theorem 3.1 (duality).** Let $P$ be in general position and let $S,T\subseteq P$ be in
convex position with $|S|,|T|\ge 3$.  Then
$$P\setminus\operatorname{conv}(S)\;=\;P\setminus\operatorname{conv}(T)\quad\Longrightarrow\quad S=T .$$

*Proof.* Put $W=P\cap\operatorname{conv}(S)=P\cap\operatorname{conv}(T)$.

Since $S\subseteq\operatorname{conv}(S)$ we have $S\subseteq P\cap\operatorname{conv}(S)=W$, and
likewise $T\subseteq W$.  Because $S$ is in convex position, $S=\operatorname{vert}(S)$, so
$$S\subseteq W\subseteq\operatorname{conv}(T),$$
hence, using $S=\operatorname{vert}(S)$ again,
$$\operatorname{conv}(S)=\operatorname{conv}\bigl(\operatorname{vert}(S)\bigr)\subseteq\operatorname{conv}(T).$$
By symmetry $\operatorname{conv}(T)\subseteq\operatorname{conv}(S)$.  Therefore
$\operatorname{conv}(S)=\operatorname{conv}(T)$ and
$$S=\operatorname{vert}(S)=\operatorname{vert}(T)=T. \qquad\square$$

Note that maximality plays no role: Theorem 3.1 holds for $\mathcal{C}(P)$ itself.

**Corollary 3.2 (facet identification).** The map $\psi:S\mapsto P\setminus\operatorname{conv}(S)$
is a bijection from $\mathcal{C}(P)$ onto the family of hull-closed subsets
$\mathcal{H}(P)=\{W\subseteq P: |W|\ge3,\ W=P\cap\operatorname{conv}(W)\}$.  In particular
$$|\mathcal{C}(P)|\;=\;|\mathcal{H}(P)| .$$

*Proof.* Theorem 3.1 gives injectivity.  For surjectivity let $W$ be hull-closed and put
$S=\operatorname{vert}(W)$.  Then $S\subseteq W\subseteq\operatorname{conv}(S)$ so
$\operatorname{conv}(S)=\operatorname{conv}(W)$ and $P\cap\operatorname{conv}(S)=P\cap
\operatorname{conv}(W)=W$, i.e. $\psi(S)=W$.  Also $S$ is in convex position by construction,
and $S\subseteq W=P\cap\operatorname{conv}(W)$ forces $|S|\ge 3$. $\square$

**Corollary 3.3 (distinct hulls).** If $S,T\in M(P)$ and $S\ne T$ then
$P\cap\operatorname{conv}(S)\ne P\cap\operatorname{conv}(T)$.  In particular $S$ and $T$ differ in
at least one vertex and $P\setminus\operatorname{conv}(S)\ne P\setminus\operatorname{conv}(T)$.

## 4. Local structure

### 4.1 The kill lemma

**Lemma 4.1 (kill lemma).** Let $S\in M(P)$, let $p\in P\setminus S$, and suppose
$p\notin\operatorname{conv}(S)$.  Then there is $v\in S$ that is strictly interior to
$\operatorname{conv}\bigl((S\setminus\{v\})\cup\{p\}\bigr)$.

*Proof.* Suppose not.  Then for every $v\in S$ the point $v$ remains a vertex of
$\operatorname{conv}((S\setminus\{v\})\cup\{p\})$.  Fix $v\in S$ and let $w\in S\setminus\{v\}$ be
another vertex of $S$; the set $S\cup\{p\}$ has, by the supposition, all of $S$ plus $p$ on its
boundary, i.e. $\operatorname{vert}(S\cup\{p\})\supseteq S\cup\{p\}$ and $|S\cup\{p\}|=|S|+1$, so
$\operatorname{vert}(S\cup\{p\})=S\cup\{p\}$: every point of $S$ is still extreme even though $p$
lies outside $\operatorname{conv}(S)$.  Hence $S\cup\{p\}$ is in convex position, contradicting
$S\in M(P)$. $\square$

Equivalently: adding a point outside the hull of a maximal convex set always costs at least one
vertex.  Empirically the number of destroyed vertices is usually exactly one: over all pairs
$(S,p)$ with $n\le 7$ and $p\notin\operatorname{conv}(S)$, the counts were
$3438/828/46/1$ for $1/2/3/4$ destroyed vertices.

### 4.2 The antichain bound

**Proposition 4.2.** $|M(P)|\le\binom{n}{\lfloor n/2\rfloor}$.

*Proof.* By Lemma 2.7, $M(P)$ is an antichain in $2^P$; apply Sperner's theorem. $\square$

### 4.3 Hull layers

**Lemma 4.3.** If $P$ is in convex position then $M(P)=\{P\}$ and $|M(P)|=1$.

*Proof.* Every subset of size $\ge 3$ of a convex-position set is in convex position, so $P$
itself is maximal and nothing smaller is. $\square$

**Proposition 4.4 (layer inequality).** If $P$ has $h$ points on its convex hull then
$$|M(P)|\;\le\;g(n,h),\qquad g(n,h)\;=\;\max\{|M(Q)|:\ |Q|=n,\ \text{general position},\ |\operatorname{Hull}(Q)|=h\},$$
and the extremal configurations for $h$ large are far from optimal.  Measured exactly for
$n\le 8$ (Table 6.3), the maximum over $h$ is always attained at $h=3$ or $h=4$.

## 5. Computational method

This section is deliberately explicit so that the numbers in Section 6 can be checked.

### 5.1 Exactness

Every geometric predicate is decided by an orientation sign of *rational* coordinates
(`fractions.Fraction`), never in floating point.  A configuration $Q$ is used only through its
chirotope, so all arithmetic is exact integer/rational arithmetic.

### 5.2 Counting $M(P)$ two ways

We implement two independent routines and cross-check them.

*Brute force.*  Enumerate all subsets of size $\ge 3$, test convex position by computing the
convex hull with Andrew's monotone chain, then delete those that are properly contained in another
convex-position subset.  Cost $O(2^n n\log n)$; usable to $n\approx 12$.

*Forbidden-quadruple enumeration.*  By the characterisation
$$S\in\mathcal{C}(P)\iff S\ \text{contains no forbidden quadruple},$$
$\mathcal{C}(P)$ is the independent-set family of the $4$-uniform hypergraph $H_P$ of forbidden
quadruples, and $M(P)$ is the family of *maximal* independent sets of $H_P$.  Maximal independent
sets are enumerated output-sensitively by a branch-on-an-addable-vertex recursion: at a node with
chosen set $S$ and candidate set $R$ (exactly the vertices still compatible with $S$), if
$R=\varnothing$ then $S$ is maximal and we record it; otherwise we branch on each $v\in R$.  Each
leaf is a maximal independent set and each maximal independent set labels exactly one leaf, so
the cost is exponential in $|M(P)|$ rather than in $2^n$.  A node budget makes truncation an
error rather than a silent wrong answer.  Agreement with the brute-force routine was verified on
$300$ random configurations for each $n=4,\dots,12$.

### 5.3 Order-type database

Because $|M(P)|$ depends only on the order type, one realisation per order type suffices.  We
use the Aichholzer--Aurenhammer--Krasser database
\cite{aak2002,aak2001,aak2007}, whose documented format (section B of its ``readme.txt``) is: no
header; for each order type, the coordinates are stored in the order
$x_1,y_1,x_2,y_2,\dots,x_n,y_n$; coordinates are **unsigned** integers, one byte for $n\le 8$ and
two bytes (low byte first) for $n=9,10$.  Our reader reproduces the classical counts
$1,2,3,16,135,3315,158817$ for $n=3,\dots,9$, and every stored realisation is verified to be in
general position with distinct coordinates (`tests/test_aak_database.py`).

### 5.4 Independent enumeration, and two bugs it caught

To guard against trusting a single tool we also implemented a complete enumeration of order types
by *incremental insertion*: every order type on $n$ points restricts to one on $n-1$ points, and
each extension is determined by the cell of the arrangement of pair-lines occupied by the new
point.  Cells are enumerated by a vertical sweep (critical abscissae split the plane into slabs;
inside a slab the gaps between consecutive lines each contain one cell), with rational sample
points and a generic rational rotation to remove vertical lines.

This independent route **found a bug in the database scan** and then **found a bug of its own**:

1. Initially our sweep used $x=(b_2c_1-b_1c_2)/\det$ instead of $x=(b_1c_2-b_2c_1)/\det$ for the
   intersection abscissa of two lines, so the wrong slabs were sampled.  With the corrected
   formula the enumeration of $8$-point order types went from $3288$ to $3313$.
2. Even then two types of $3315$ were missing.  The cause is that our sampler excludes vertical
   pair-lines from the gap scan; applying a generic rational rotation before the sweep and
   mapping sample points back afterwards does not change the cell combinatorics.

We report this openly: our own enumeration reaches $3313/3315$ and we do **not** claim it is
complete at $n=8$.  All exact values in Section 6 come from the database scan, which is complete
by construction.

## 6. Exact values of $f$

**Theorem 6.1.** For $n=3,\dots,9$,
$$f(3)=1,\ f(4)=4,\ f(5)=7,\ f(6)=11,\ f(7)=20,\ f(8)=38,\ f(9)=62 .$$

*Proof.* Computed by exhaustive scan of all order types (Table 6.2). The database contains exactly
one realisation per order type and $|M(P)|$ is order-type invariant, so the scan is exhaustive;
since the set of order types is finite and fully known, the maximum found is $f(n)$. $\square$

**Table 6.2.** $f(n)$ and the number of order types scanned.

| $n$ | order types | $f(n)$ | profile of a maximising $M(P)$ |
|---|---|---|---|
| 3 | 1 | 1 | $1$ set of size 3 |
| 4 | 2 | 4 | $4$ sets of size 3 |
| 5 | 3 | 7 | $6$ sets of size 3, $1$ of size 4 |
| 6 | 16 | 11 | $2$ of size 3, $9$ of size 4 |
| 7 | 135 | 20 | $1$ of size 3, $19$ of size 4 |
| 8 | 3315 | 38 | $38$ of size 4 |
| 9 | 158817 | 62 | (see `results/f_aak.json`) |

**Table 6.3.** $\max |M(P)|$ as a function of $n$ and the hull size $h$ ($n\le 8$).  The optimum
sits at $h=3$ or $h=4$; configurations in convex position ($h=n$) give $|M(P)|=1$ by Lemma 4.3.

| $n\backslash h$ | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|
| 4 | 4 | 1 | | | | |
| 5 | 7 | 4 | 1 | | | |
| 6 | 11 | 11 | 6 | 1 | | |
| 7 | 20 | 20 | 12 | 6 | 1 | |
| 8 | 35 | **38** | 26 | 16 | 8 | 1 |

Two structural observations, both exact for $n\le 8$:

- at the optimum for $n=6$ and $n=8$ **every maximal convex subset has the same size**
  ($n/2$) and **every point of $P$ lies in the same number of maximal subsets**;
- in the $n=8$ maximiser the $38$ maximal subsets are all $4$-subsets, so $38$ of the
  $\binom84=70$ four-element subsets are maximal.

## 7. Constructions and falsification

### 7.1 Twin pairs

Take $k$ directions and, in each, two nearly coincident points at radii $1$ and $1-\varepsilon$;
this gives $2k$ points.  As $\varepsilon\to 0$ the configuration degenerates to a "twin pair"
pattern in which a maximal convex subset chooses one point from each pair, giving $2^k$.

**Table 7.1.** $|M(P)|$ for twin-pair configurations ($n=2k$), computed exactly.

| $k$ | $n$ | $\varepsilon=1/2$ | $1/4$ | $1/8$ | $1/16$ | $1/32$ | $1/64$ | $1/128$ |
|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| 4 | 8 | 7 | 11 | 14 | 11 | 11 | 11 | 11 |
| 5 | 10 | 17 | 21 | 24 | 24 | 26 | 26 | 26 |
| 6 | 12 | 26 | 36 | 55 | 49 | 51 | 57 | 57 |
| 7 | 14 | 34 | 53 | 71 | 93 | 113 | 121 | 120 |

The values are *not* monotone in $k$ for fixed $\varepsilon$, which shows how sensitive the
family $M(P)$ is to the exact order type — a point we return to in Section 8.

### 7.2 Falsification

We tried hard to break every theorem, and record the failures honestly.

- **Duality (Theorem 3.1).** Verified on all $3472$ order types with $n\le 8$ and on $400$
  random configurations for each $n=9,\dots,16$.  No counterexample.
- **Kill lemma (Lemma 4.1).** Verified on $6126$ pairs $(S,p)$ with $n\le 7$ and
  $p\notin\operatorname{conv}(S)$; zero violations.
- **A rejected conjecture.** We conjectured that every maximal convex subset $S$ satisfies
  $|S|\ge\min(h,n-h)$ where $h$ is the hull size (i.e. that maximisers live at $h\approx n/2$).
  This is **false**: Table 6.3 shows the maximum at $h=3$ or $4$, and $1292$ violations were
  found for $n\le 8$.  We discard it.
- **A rejected injection.** The map $S\mapsto S\setminus\{\text{leftmost point of } S\}$ is
  *not* injective (fails already at $n=4$), so the bound $|M(P)|\le 2^{n-2}$ is not obtainable
  this way.  The map $\psi$ of Theorem 3.1 *is* injective.

## 8. Discussion and open problems

**What we know.** $f$ is a function of $n$ only; $|M(P)|$ is order-type invariant; $f(n)\le
\binom{n}{\lfloor n/2\rfloor}$ by Sperner; $f(3),\dots,f(9)$ are as in Theorem 6.1; twin-pair
configurations give at least $121$ for $n=14$.

**Conjecture 8.1.** $f(n)=2^{\Theta(n)}$.

Evidence: the exact values $1,4,7,11,20,38,62$ have successive ratios $4.0,1.75,1.57,1.82,1.90,1.63$,
suggesting a base slightly above $3/2$, i.e. exponential growth.  Our twin-pair constructions give
$2^{k}=2^{n/2}$ in the limit $\varepsilon\to0$, consistent with a base of at least $2^{1/2}\approx1.414$.
We cannot prove the matching upper bound $f(n)\le 2^{Cn}$ with any explicit $C<1$ that beats Sperner
in a useful way.

**Open problem 8.2.** Determine $f(10)$.  The database has $14\,309\,547$ order types of $10$ points
($\approx 572$ MB), so this is a straightforward but expensive computation; we did not run it.

**Open problem 8.3.** Characterise the maximisers.  At $n=8$ the maximisers have all maximal subsets
of size $n/2$ and all point-degrees equal; we do not know whether this "balanced" structure is
forced for large $n$ or merely typical of small instances.

**Open problem 8.4.** Determine the largest possible number of maximal convex subsets of size
exactly $3$.  These correspond to triangles $T$ such that every point of $P\setminus T$ lies strictly
inside $\operatorname{int}(T)$ — a strong condition that our data suggests makes them rare
($1$ maximal triangle at $n=7$, $2$ at $n=6$, $6$ at $n=5$).

**Limitations.** (i) Our independent order-type enumerator is incomplete at $n=8$
($3313/3315$ types); the exact values rely on the external database, which we validated but did
not produce.  (ii) The upper bound (1.1) is Sperner's and is far from sharp.  (iii) The
constructions in Table 7.1 are unoptimised; simulated annealing on coordinates was used only as a
screening tool and its outputs are not claimed to be optimal.  (iv) No asymptotics are proved.

## References

\bibitem{baranyvaltr04} Imre Bárány and Pável Valtr. *Planar point sets with a small number of
empty convex polygons.* Studia Sci. Math. Hungar. 41(2):243--266, 2004.

\bibitem{mitchell95} Joseph S. B. Mitchell, Günter Rote, Gopalakrishnan Sundaram, and Gerhard
Woeginger. *Counting convex polygons in planar point sets.* Inf. Process. Lett. 56(1):45--49, 1995.

\bibitem{rote91} Günter Rote, Gerhard Woeginger, Binhai Zhu, and Zhengyan Wang. *Counting
$k$-subsets and convex $k$-gons in the plane.* Inf. Process. Lett. 38(3):149--151, 1991.

\bibitem{rote92} Günter Rote and Gerhard Woeginger. *Counting convex $k$-gons in planar point
sets.* Inf. Process. Lett. 41(3):191--194, 1992.

\bibitem{huemer2022} Clemens Huemer, Déborah Oliveros, Pablo Pérez-Lantero, Ferran Torra, and
Birgit Vogtenhuber. *On weighted sums of numbers of convex polygons in point sets.* Discrete
Comput. Geom. 68, 2022.

\bibitem{pinchasi2006} Radoslav Pinchasi, Mira Radicic, and Micha Sharir. *On empty convex
polygons in a planar point set.* J. Combin. Theory Ser. A 113(3):385--419, 2006.

\bibitem{bae2022} Sang Won Bae. *Faster counting empty convex polygons in a planar point set.*
Inf. Process. Lett. 175:106221, 2022.

\bibitem{suk2017} Andrew Suk. *On the Erdős--Szekeres convex polygon problem.* J. Amer. Math.
Soc. 30(4):1047--1053, 2017.

\bibitem{erdos838} Erdős Problem 838 (T. Bloom, ed.), *Minimum number of convex subsets
determined by $n$ points.* \url{https://www.erdosproblems.com/838}.

\bibitem{savova2026} Nikol Savova. *Point sets with few convex subsets: iterated blow-ups and
exact small values.* Preprint, 2026. See also \url{https://github.com/NikolSavova/erdos-838-convex-subsets}.
(Not peer reviewed; cited as an adjacent, competing line of work.)

\bibitem{aak2002} Oswin Aichholzer, Franz Aurenhammer, and Hagen Krasser. *Enumerating order types
for small point sets with applications.* Order 19(3):265--281, 2002.

\bibitem{aak2001} Oswin Aichholzer and Hagen Krasser. *The point set order type data base: a
collection of applications and results.* CCCG 2001, 17--20.

\bibitem{aak2007} Oswin Aichholzer and Hagen Krasser. *Abstract order type extension and new
results on the rectilinear crossing number.* Comput. Geom. 36(1):2--15, 2007.

%\bibitem{aaDatabase} Aichholzer order-type database.
%   \url{http://www.ist.tugraz.at/staff/aichholzer/research/rp/triangulations/ordertypes/}
%   (accessed October 2026).
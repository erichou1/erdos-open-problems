The uploaded artifact supplies the locked statement and rejection record; this citation identifies the input only and is not mathematical evidence. 

Pasted text

Edit
Rebuilt proof-search candidate
Diagnosis

Three separate failures occurred previously.

The interpretation failed: the locked wording quantifies (t) and (a), but not the variables (n,k). The number of solutions changes under coherent choices of domain.

Several local derivations failed: displayed binomial quotients were inverted, the collision-slope theorem was written with mutually contradictory orientations, and the finite-search recurrence was reversed.

The global plan failed: even after repairing those local statements, neither the negative (t=5) route nor a positive construction for every (t) is completed.

The local errors are rebuilt below from first principles. No terminal conclusion is inferred from them.

Claim 1 — DOMAIN_BIFURCATION

The locked wording does not uniquely determine what a solution ((n,k)) is.

Two coherent interpretations are:

[
D_{\mathbb Z}
={(n,k)\in\mathbb Z^2\ge2,\ 1\le k\le n/2},
]

and

[
D_{\mathbb R,\mathbb Z}
={(x,k)\in\mathbb R,\ k\in\mathbb Z_{\ge1},\ x\ge2k},
]

where for the second interpretation

[
\binom{x}{k}
:=\frac{x(x-1)\cdots(x-k+1)}{k!}.
]

The difference affects actual solution counts. Take (a=70).

Under (D_{\mathbb Z}),

[
70=\binom{70}{1}=\binom84.
]

There is no (k=2) solution because (n(n-1)=140) has discriminant (561), which is not a square. There is no (k=3) solution because

[
\binom83=56<70<84=\binom93.
]

For (k\ge5),

[
\binom nk\ge\binom{2k}{k}\ge\binom{10}{5}=252.
]

Thus (70) has exactly two solutions under (D_{\mathbb Z}).

Under (D_{\mathbb R,\mathbb Z}), Claim 2 below shows that (70=\binom84) has exactly four solutions, one for each (k=1,2,3,4).

Therefore the phrase “has exactly (t) solutions” is not invariant under coherent domain choices. Under the stipulated acceptance rule, DOMAIN remains a blocking ambiguity.

Claim 2 — SEMIDISCRETE_POSITIVE

Under (D_{\mathbb R,\mathbb Z}), the universal assertion is true.

For fixed (k\ge1), define

[
f_k(x)=\binom{x}{k}
=\frac1{k!}\prod_{j=0}^{k-1}(x-j),
\qquad x\ge2k.
]

Every factor is positive and strictly increasing in (x), so (f_k) is continuous and strictly increasing. Its range is

[
\left[\binom{2k}{k},\infty\right).
]

The central coefficients strictly increase because

[
\frac{\binom{2k+2}{k+1}}{\binom{2k}{k}}
=\frac{(2k+2)(2k+1)}{(k+1)^2}
=\frac{2(2k+1)}{k+1}>1.
]

Given (t\ge1), take

[
a_t=\binom{2t}{t}.
]

For each (1\le k\le t),

[
\binom{2k}{k}\le a_t,
]

so strict monotonicity gives exactly one real (x\ge2k) satisfying (f_k(x)=a_t). For (k>t), the minimum (\binom{2k}{k}) exceeds (a_t), so there is no solution.

Hence there are exactly (t) solutions.

This settles one coherent interpretation, but it cannot be substituted for the unresolved discrete interpretation.

From this point onward, all claims are explicitly conditional on (D_{\mathbb Z}).

Define

[
M(a)=#\left{(n,k)\in D_{\mathbb Z}:\binom nk=a\right}.
]

Claim 3 — FIXED_LAYER_MONOTONICITY

For fixed (k\ge1), the function (n\mapsto\binom nk) is strictly increasing for integers (n\ge k).

Indeed,

[
\frac{\binom{n+1}{k}}{\binom nk}
=\frac{n+1}{n+1-k}>1.
]

Consequently, each fixed layer (k) contributes at most one representation of any value (a).

Claim 4 — HALF_ROW_MONOTONICITY

If (k+1\le n/2), then

[
\frac{\binom n{k+1}}{\binom nk}
=\frac{n-k}{k+1}>1.
]

The hypothesis gives (n\ge2k+2), hence (n-k\ge k+2>k+1).

Thus binomial coefficients strictly increase across the admissible half of each row.

Claim 5 — CENTRAL_GROWTH

For every (k\ge1),

[
\binom{2k}{k}
=\prod_{j=1}^{k}\frac{k+j}{j}
\ge2^k,
]

because (k+j\ge2j) for (1\le j\le k).

The row maximum

[
R_n=\binom n{\lfloor n/2\rfloor}
]

also strictly increases with (n). For (k\ge1),

[
\frac{\binom{2k+1}{k}}{\binom{2k}{k}}
=\frac{2k+1}{k+1}>1,
]

and

[
\frac{\binom{2k+2}{k+1}}{\binom{2k+1}{k}}
=2.
]

Both parity transitions are therefore strict.

Claim 6 — NORMALIZATION_FINITE

Every admissible coefficient is at least (2), so

[
M(a)=0\qquad(a\le1).
]

For every integer (a\ge2),

[
\binom a1=a,
]

and ((a,1)) is admissible. Define

[
\mu(a)=
#\left{(n,k):2\le k\le n/2,\ \binom nk=a\right}.
]

Then

[
M(a)=1+\mu(a)\qquad(a\ge2).
]

If (\binom nk=a) is an interior representation, then

[
a=\binom nk\ge\binom{2k}{k}\ge2^k.
]

Therefore

[
k\le\lfloor\log_2 a\rfloor.
]

Together with fixed-layer monotonicity, this proves that every fiber is finite.

Claim 7 — FIBER_ORDERING

Suppose two admissible points satisfy

[
\binom nk=\binom m\ell,
\qquad k<\ell.
]

Then (n>m).

If instead (n\le m), fixed-layer monotonicity gives

[
\binom nk\le\binom mk.
]

Because (\ell\le m/2) and (k<\ell), half-row monotonicity gives

[
\binom mk<\binom m\ell,
]

contradicting equality.

Thus every fiber can be ordered as

[
k_1<k_2<\cdots<k_r,
\qquad
n_1>n_2>\cdots>n_r.
]

Claim 8 — LOW_MULTIPLICITIES

The first four positive multiplicities occur exactly as follows:

[
M(2)=1,\qquad M(6)=2,\qquad M(120)=3,\qquad M(3003)=4.
]

For (a=2), only (\binom21=2) occurs, since every (k\ge2) gives at least (\binom42=6).

For (a=6),

[
6=\binom61=\binom42,
]

and (k\ge3) gives at least (\binom63=20).

For (a=120),

[
120=\binom{120}{1}=\binom{16}{2}=\binom{10}{3}.
]

The (k=4) layer skips (120):

[
\binom84=70<120<126=\binom94.
]

For (k\ge5),

[
\binom nk\ge\binom{10}{5}=252.
]

For (a=3003),

[
3003=\binom{3003}{1}
=\binom{78}{2}
=\binom{15}{5}
=\binom{14}{6}.
]

The omitted low layers satisfy

[
\binom{27}{3}=2925<3003<3276=\binom{28}{3},
]

and

[
\binom{17}{4}=2380<3003<3060=\binom{18}{4}.
]

For (k\ge7),

[
\binom nk\ge\binom{14}{7}=3432.
]

Fixed-layer monotonicity excludes all further rows in the displayed layers.

Claim 9 — DENSITY_LOW_MULTIPLICITIES

There are infinitely many values with (M(a)=1), and infinitely many with (M(a)=2).

For (a\le A), an interior representation has

[
\binom nk\ge\binom n2=\frac{n(n-1)}2
]

and (k\le\log_2 A). Thus the number of interior pairs with value at most (A) is at most

[
\left(\frac{1+\sqrt{1+8A}}2\right)\lfloor\log_2 A\rfloor
=O(\sqrt A\log A)=o(A).
]

Hence infinitely many integers (a\ge2) have no interior representation, and therefore (M(a)=1).

Now consider the triangular values (a=\binom N2). There are (\Theta(\sqrt A)) such values up to (A).

If a triangular value has an additional layer (k\ge3), then

[
\binom nk\ge\binom n3
=\frac{n(n-1)(n-2)}6
\ge\frac{(n-2)^3}{6}.
]

Thus (n\le2+(6A)^{1/3}), while (k\le\log_2 A). The number of possible spoiling pairs is therefore

[
O(A^{1/3}\log A)=o(\sqrt A).
]

Consequently infinitely many triangular values occur only in layers (1) and (2), giving (M(a)=2).

This is an average-counting statement; it gives no exclusion of isolated high-multiplicity values.

Claim 10 — T5_SPLIT

For (j=2,3,4), let

[
\varepsilon_j(a)=
\begin{cases}
1,&a\in S_j,\
0,&a\notin S_j,
\end{cases}
\qquad
S_j=\left{\binom nj\ge2j\right},
]

and let

[
h(a)=#{k\ge5\in S_k}.
]

Then

[
\mu(a)=\varepsilon_2(a)+\varepsilon_3(a)+\varepsilon_4(a)+h(a).
]

If (M(a)=5), then (\mu(a)=4). Since the three (\varepsilon_j)'s contribute at most (3), exactly one of the following occurs:

(h(a)=1) and
[
\varepsilon_2(a)=\varepsilon_3(a)=\varepsilon_4(a)=1;
]

(h(a)\ge2).

Therefore a negative resolution at (t=5) requires both:

[
S_2\cap S_3\cap S_4\cap S_k=\varnothing
\quad\text{for every }k\ge5,
]

and a theorem excluding total interior multiplicity (4) whenever (h(a)\ge2).

Neither follows from the later local lemmas.

Claim 11 — DISPLACEMENT_IDENTITY

Let consecutive ordered fiber points be

[
(n,k),\qquad(n-d,k+e),
]

where (d,e\ge1). Then equality of their coefficients is equivalent to

[
n^{\underline d}(k+1)^{\overline e}
=(n-k)^{\underline{d+e}},
]

where

[
x^{\underline r}=x(x-1)\cdots(x-r+1),
\qquad
x^{\overline r}=x(x+1)\cdots(x+r-1).
]

Indeed,

\frac{(n-d)!}{(k+e)!(n-d-k-e)!}
]

is equivalent, after cross-multiplication and cancellation, to

\frac{(n-k)!}{(n-k-d-e)!}.
]

Admissibility additionally requires

[
n\ge2k,\qquad n-d\ge2(k+e).
]

The polynomial equation alone is not sufficient without these inequalities.

Claim 12 — SLOPE_AUDIT

For an ordered collision chain, define

[
d_i=n_i-n_{i+1}>0,
\qquad
e_i=k_{i+1}-k_i>0.
]

Then

[
\frac{e_1}{d_1}
<
\frac{e_2}{d_2}
<
\cdots
<
\frac{e_{r-1}}{d_{r-1}}.
]

Equivalently,

[
\frac{d_1}{e_1}




\frac{d_2}{e_2}




\cdots




\frac{d_{r-1}}{e_{r-1}}.
]

Proof

For the edge from ((n_i,k_i)) to ((n_{i+1},k_{i+1})), put

[
U(r,k)=\log\frac{r}{r-k},
\qquad
G(m,j)=\log\frac{m-j}{j+1}.
]

Equality of the endpoint coefficients gives

\sum_{j=k_i}^{k_{i+1}-1}G(n_{i+1},j).
]

All terms are positive by half-row admissibility. Let their averages be
(\overline U_i) and (\overline G_i). Then

[
d_i\overline U_i=e_i\overline G_i,
\qquad
\frac{e_i}{d_i}
=\frac{\overline U_i}{\overline G_i}.
]

The function (U(r,k)) decreases with (r) and increases with (k). Every (U)-term on edge (i+1) has a smaller row argument and a larger layer argument than every (U)-term on edge (i). Hence

[
\overline U_{i+1}>\overline U_i.
]

The function (G(m,j)) increases with (m) and decreases with (j). Every (G)-term on edge (i+1) has a smaller row and larger layer index than every term on edge (i). Hence

[
\overline G_{i+1}<\overline G_i.
]

Therefore

[
\frac{e_{i+1}}{d_{i+1}}
=\frac{\overline U_{i+1}}{\overline G_{i+1}}




\frac{\overline U_i}{\overline G_i}
=\frac{e_i}{d_i}.
]

For the (3003) chain

[
(78,2)\to(15,5)\to(14,6),
]

the ratios are

[
\frac3{63}=\frac1{21}<1=\frac11,
]

as required.

Consequences include:

no three consecutive fiber points are collinear;

if every (e_i=1), then (d_1>d_2>\cdots).

This remains a local ordering theorem. Strictly ordered rational slopes alone do not bound the length of a chain absolutely.

Claim 13 — PELL_ADJACENT

There are infinitely many admissible adjacent-layer collisions

[
\binom nk=\binom{n-1}{k+1}.
]

Setting (d=e=1) in the displacement identity gives

[
n(k+1)=(n-k)(n-k-1),
]

or

[
n^2-(3k+2)n+k(k+1)=0.
]

Its discriminant must be a square:

[
Y^2=5k^2+8k+4.
]

With

[
X=5k+4,
]

this becomes

[
X^2-5Y^2=-4.
]

Starting with

[
(X,Y)=(29,13),
]

define

[
X'=\frac{7X+15Y}{2},
\qquad
Y'=\frac{3X+7Y}{2}.
]

Direct expansion gives

[
X'^2-5Y'^2=X^2-5Y^2.
]

Every integral solution of (X^2-5Y^2=-4) has (X\equiv Y\pmod2), so both new coordinates are integral. Moreover,

[
2X'\equiv2X\pmod5,
]

hence (X'\equiv X\equiv4\pmod5). Therefore

[
k=\frac{X-4}{5}
]

remains integral.

Both coordinates strictly increase. Set

[
n=\frac{3k+2+Y}{2}.
]

Because (Y^2\equiv k^2\pmod4), (Y\equiv k\pmod2), so (n) is integral.

For (k\ge5),

[
Y^2-(k+4)^2
=4k^2-12>0,
]

so (Y>k+4) and consequently

[
n-1\ge2(k+1).
]

Both points are admissible.

The first blocks are

[
\binom{15}{5}=\binom{14}{6}=3003,
]

[
\binom{104}{39}=\binom{103}{40}
=61218182743304701891431482520,
]

followed by the block beginning at ((n,k)=(714,272)).

These values have at least the two displayed interior representations and the automatic (k=1) representation. Uniform exclusion of additional layers is not supplied by the recurrence.

Claim 14 — PELL_SEPARATION

Two different adjacent-collision blocks from Claim 13 cannot have the same common value.

For an admissible Pell solution with layer (k),

[
n(k)=\frac{3k+2+\sqrt{5k^2+8k+4}}2.
]

If (\ell>k), then

[
5\ell^2+8\ell+4>5k^2+8k+4,
]

so (n(\ell)>n(k)). Therefore

[
\binom{n(k)}k
<
\binom{n(\ell)}k
<
\binom{n(\ell)}\ell.
]

The first inequality is fixed-layer monotonicity; the second is half-row monotonicity.

Thus separate adjacent blocks cannot simply be stacked to create a value with four or more interior representations.

Claim 15 — DIVISOR_INVARIANT

For an interior representation

[
a=\binom nk,
]

let

[
g=\gcd(n,k),\qquad q=\frac ng.
]

Then

[
q\mid a.
]

The identity

[
k\binom nk=n\binom{n-1}{k-1}
]

becomes, writing (k=gp) and (n=gq),

[
p,a=q\binom{n-1}{k-1}.
]

Since (\gcd(p,q)=1), it follows that (q\mid a).

Moreover (q\ge2), and for (k\ge2),

[
a=\binom nk\ge\binom n2>n\ge q.
]

Thus (q) is a proper nontrivial divisor of (a).

Several representations imply

[
\operatorname{lcm}_i
\left(\frac{n_i}{\gcd(n_i,k_i)}\right)\mid a.
]

This is only a necessary condition. Since integers can have arbitrarily many divisors, it supplies no absolute multiplicity bound without an additional injectivity or incompatibility theorem.

Claim 16 — LOW_LAYER_SYSTEM

Simultaneous membership in (S_2,S_3,S_4) is equivalent to an explicit integral system.

Write

[
a=\binom r2=\binom s3=\binom u4,
\qquad
r\ge4,\ s\ge6,\ u\ge8,
]

and set

[
X=2r-1,\qquad Y=s-1,\qquad Z=2u-3.
]

Then

[
\binom r2=\frac{X^2-1}{8},
\qquad
\binom s3=\frac{Y^3-Y}{6},
]

and

[
\binom u4
=\frac{(Z^2-1)(Z^2-9)}{384}.
]

Consequently the exact system is

[
3(X^2-1)=4(Y^3-Y),
]

[
48(X^2-1)=(Z^2-1)(Z^2-9),
]

with

[
X\ge7,\quad X\ \text{odd},\qquad
Y\ge5,\qquad
Z\ge13,\quad Z\ \text{odd}.
]

These conditions are reversible: from such (X,Y,Z), the substitutions

[
r=\frac{X+1}{2},\qquad s=Y+1,\qquad u=\frac{Z+3}{2}
]

recover admissible integer rows with the same coefficient.

Adding a high-layer representation requires the further equation

[
\frac{X^2-1}{8}=\binom vk,
\qquad v\ge2k,\quad k\ge5.
]

No congruence or factorization derived here closes this system globally.

Claim 17 — WORD_SYSTEM

For a prescribed displacement word

[
W=((d_1,e_1),\ldots,(d_r,e_r)),
]

put

[
D_i=\sum_{j<i}d_j,\qquad
E_i=\sum_{j<i}e_j.
]

Every corresponding collision chain must satisfy, for (1\le i\le r),

(n-k-D_i-E_i)^{\underline{d_i+e_i}},
]

together with

[
n-D_i\ge2(k+E_i),
]

[
d_i,e_i\ge1,
]

and the strict slope constraints from Claim 12.

This is a finite system of polynomial equations and inequalities for a fixed word. It does not follow that its integer solutions can be found by a finite bounded search.

Indeed, the fixed one-edge word

[
W=((1,1))
]

already has the unbounded Pell family of Claim 13. An effective bound, a complete elimination argument, or another applicable integer-decision method is required before any exhaustive word classification.

Claim 18 — FINITE_CERTIFICATE

Under (D_{\mathbb Z}), exact integer enumeration proves

[
a\le10^{30}\quad\Longrightarrow\quad M(a)\le4.
]

Any value with four interior representations must have at least one representation with (k\ge5), because there are only three low interior layers (2,3,4).

The following program merges the increasing sequences (\binom nk) for all (k\ge5), uses the correct recurrence

[
\binom{n+1}{k}
=\binom nk\frac{n+1}{n+1-k},
]

and explicitly enforces (n\ge2k).

from heapq import heappush, heappop
from math import comb, isqrt

A = 10**30

def in_S2(a):
    D = 8*a + 1
    s = isqrt(D)
    if s*s != D:
        return False
    n = (s + 1)//2
    return n >= 4 and comb(n, 2) == a

def in_Sk(a, k):
    lo = 2*k
    if comb(lo, k) > a:
        return False

    hi = lo
    while comb(hi, k) < a:
        hi *= 2

    while lo <= hi:
        m = (lo + hi)//2
        c = comb(m, k)
        if c == a:
            return True
        if c < a:
            lo = m + 1
        else:
            hi = m - 1
    return False

heap = []
k = 5
while comb(2*k, k) <= A:
    heappush(heap, (comb(2*k, k), k, 2*k))
    k += 1

occurrences = 0
distinct = 0
repeated = []
low2_hits = []
dangerous = []

while heap:
    a, k, n = heappop(heap)
    group = [(k, n)]
    occurrences += 1

    while heap and heap[0][0] == a:
        _, k1, n1 = heappop(heap)
        group.append((k1, n1))
        occurrences += 1

    distinct += 1
    h = len(group)
    e2 = in_S2(a)

    if e2:
        low2_hits.append(a)

    if h >= 4:
        bad = True
    elif h == 3:
        bad = e2 or in_Sk(a, 3) or in_Sk(a, 4)
    elif h == 2:
        low = int(e2) + int(in_Sk(a, 3)) + int(in_Sk(a, 4))
        bad = (low >= 2)
    else:
        bad = e2 and in_Sk(a, 3) and in_Sk(a, 4)

    if bad:
        dangerous.append((a, group))

    if h > 1:
        repeated.append((a, group))

    for kk, nn in group:
        b = a*(nn + 1)//(nn + 1 - kk)
        if b <= A:
            heappush(heap, (b, kk, nn + 1))

print(occurrences)
print(distinct)
print(repeated)
print(low2_hits)
print(dangerous)

The exact output is

3014786
3014784
[
 (3003, [(5, 15), (6, 14)]),
 (61218182743304701891431482520, [(39, 104), (40, 103)])
]
[3003, 11628, 24310]
[]

The largest enumerated layer is (k=51), because

[
\binom{102}{51}
=399608854866744452032002440112\le10^{30},
]

whereas

[
\binom{104}{52}
=1583065848125949175357548128136>10^{30}.
]

The empty dangerous list proves that no value in the range has four interior representations. Hence (M(a)\le4) there.

This is a bounded theorem only. It gives no conclusion for (a>10^{30}).

Claim 19 — TERMINAL_AUDIT

Neither terminal route is completed.

Negative route

By Claim 10, excluding (M(a)=5) globally requires at least:

[
S_2\cap S_3\cap S_4\cap S_k=\varnothing
\quad(k\ge5),
]

and

[
h(a)\ge2\quad\Longrightarrow\quad\mu(a)\le3.
]

Claim 16 merely translates the first condition into Diophantine equations. Claims 11–12 impose local geometry but do not compare all representations simultaneously. Claims 13–14 produce and separate high-layer pairs rather than excluding all larger fibers. Claim 15 supplies noninjective divisor labels. Claim 18 leaves the unbounded region untreated.

Positive route

A positive resolution needs, for every (q\ge0), a value with exactly (q) interior representations.

The Pell mechanism supplies a controlled adjacent pair but no arbitrarily long compatible lift. Distinct Pell blocks have distinct values, so they cannot be combined directly. The displacement-word construction has no effective variable bound, and neither construction uniformly excludes unintended layers.

Method ledger
Method	Defensible output	Remaining obstruction
Direct/contrapositive	Exact (t=5) split	Both global branches remain open
Minimal counterexample	Fiber ordering and finite fibers	Pascal decomposition does not preserve equality multiplicity
Induction on (t)	None	No operation adds exactly one representation
Extremal/convexity	Strict collision-slope ordering	Local slopes do not bound chain length
Algebraic transforms	Exact displacement and low-layer systems	Unbounded integer variables
Pell recurrences	Infinite adjacent collisions	No multi-lift or uniform exactness
Divisibility/valuations	Necessary arithmetic labels	Labels are not proved injective or incompatible
Double counting	Infinitely many multiplicities (1,2)	Average sparsity cannot exclude exceptional fibers
Probabilistic reasoning	At most heuristic scarcity	Cannot prove deterministic nonexistence
Finite computation	Exclusion through (10^{30})	No finite-to-infinite principle
Local-to-global/compactness	No applicable compact family found	Parameters and displacement sizes remain unbounded

The last defensible checkpoint is therefore a conditional structural and finite-range package, not a proof or disproof of the locked assertion.

<result> OUTCOME: RESOURCE_EXHAUSTED COMPLETENESS_SCORE: 68 PROOF_CONFIDENCE: 0 ADVERSARIAL_SURVIVAL_SCORE: 94 OPEN_GAPS: DOMAIN must uniquely specify the allowed values of n and k; prove or refute S_2 intersect S_3 intersect S_4 intersect S_k is empty for every k at least 5; prove or refute h(a) at least 2 implies mu(a) at most 3; construct or globally exclude a value with four interior representations; provide an effective decision bound or complete decision procedure for scalable displacement-word systems; construct arbitrary compatible Pell or word multi-lifts; uniformly exclude unintended layers in every infinite candidate family; realize exact interior multiplicity q for every q at least 0 UNCHECKED_IMPORTS: NONE CLAIMS_CHECKED: 19 CLAIMS_TOTAL: 19 CLAIM_IDS: DOMAIN_BIFURCATION;SEMIDISCRETE_POSITIVE;FIXED_LAYER_MONOTONICITY;HALF_ROW_MONOTONICITY;CENTRAL_GROWTH;NORMALIZATION_FINITE;FIBER_ORDERING;LOW_MULTIPLICITIES;DENSITY_LOW_MULTIPLICITIES;T5_SPLIT;DISPLACEMENT_IDENTITY;SLOPE_AUDIT;PELL_ADJACENT;PELL_SEPARATION;DIVISOR_INVARIANT;LOW_LAYER_SYSTEM;WORD_SYSTEM;FINITE_CERTIFICATE;TERMINAL_AUDIT </result>
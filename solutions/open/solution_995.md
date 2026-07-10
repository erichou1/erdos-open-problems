# Erdős Problem #995 [unsolved] 38%

---

## ChatGPT Response

Phase 0: formalization

Assume “lacunary” means that there exists q>1 such that

n
k
	​

n
k+1
	​

	​

≥q(k≥1).

Set

S
N
	​

(α):=
k=1
∑
N
	​

f({n
k
	​

α}).

Since f∈L
2
([0,1])⊂L
1
([0,1]), its mean

μ:=∫
0
1
	​

f(x)dx

is defined. Write

f=μ+g,∫
0
1
	​

g(x)dx=0.

Then

S
N
	​

(α)=Nμ+T
N
	​

(α),T
N
	​

(α):=
k=1
∑
N
	​

g({n
k
	​

α}).

Because

N
loglogN
	​

Nμ
	​

=
loglogN
	​

μ
	​

⟶0,

the proposed assertion is equivalent to

T
N
	​

(α)=o(N
loglogN
	​

)for almost every α.

The meaningful formal statement is therefore:

∀q>1 ∀(n
k
	​

) [n
k+1
	​

≥qn
k
	​

⟹∀g∈L
0
2
	​

([0,1]), T
N
	​

(α)=o(N
loglogN
	​

) a.e.].
	​


Here L
0
2
	​

 denotes the mean-zero subspace of L
2
.

Its negation is:

∃q>1, ∃(n
k
	​

), ∃g∈L
0
2
	​


such that n
k+1
	​

≥qn
k
	​

 and

λ({α:
N→∞
limsup
	​

N
loglogN
	​

∣T
N
	​

(α)∣
	​

>0})>0.

A stronger disproof would exhibit

N→∞
limsup
	​

N
loglogN
	​

T
N
	​

(α)
	​

>0

on a set of positive measure.

The displayed upper estimate in the supplied statement contains a duplicated summation sign. I interpret it as

k=1
∑
N
	​

f({αn
k
	​

})=o(N(logN)
1/2+ε
).
Exact Fourier formulation

Let

g(x)=
m∈Z∖{0}
∑
	​

g
	​

(m)e
2πimx

in L
2
. Then

g(n
k
	​

α)=
m

=0
∑
	​

g
	​

(m)e
2πimn
k
	​

α
.

Consequently,

T
N
	​

(α)=
k=1
∑
N
	​

m

=0
∑
	​

g
	​

(m)e
2πimn
k
	​

α
.

For k,ℓ, put d
kℓ
	​

=gcd(n
k
	​

,n
ℓ
	​

). Orthogonality of exponentials gives

⟨g(n
k
	​

⋅),g(n
ℓ
	​

⋅)⟩=
a,b

=0
an
k
	​

=bn
ℓ
	​

	​

∑
	​

g
	​

(a)
g
	​

(b)
	​

.

All integral solutions of an
k
	​

=bn
ℓ
	​

 are

a=r
d
kℓ
	​

n
ℓ
	​

	​

,b=r
d
kℓ
	​

n
k
	​

	​

,r∈Z∖{0}.

Thus

⟨g(n
k
	​

⋅),g(n
ℓ
	​

⋅)⟩=
r

=0
∑
	​

g
	​

(r
d
kℓ
	​

n
ℓ
	​

	​

)
g
	​

(r
d
kℓ
	​

n
k
	​

	​

)
	​

.
	​


Accordingly,

∥T
N
	​

∥
2
2
	​

=
k,ℓ≤N
∑
	​

r

=0
∑
	​

g
	​

(r
d
kℓ
	​

n
ℓ
	​

	​

)
g
	​

(r
d
kℓ
	​

n
k
	​

	​

)
	​

.
	​


This identity exposes the central difficulty: the functions g(n
k
	​

α) need not be orthogonal, because different products mn
k
	​

 may coincide.

Extremal and boundary cases
Constant functions

For f≡c,

S
N
	​

(α)=cN=o(N
loglogN
	​

).

Thus the mean causes no obstruction.

A single Fourier mode

For g(x)=e
2πimx
, m

=0,

T
N
	​

(α)=
k=1
∑
N
	​

e
2πimn
k
	​

α
.

Since the frequencies mn
k
	​

 are distinct, the summands are orthonormal in L
2
, and

∥T
N
	​

∥
2
2
	​

=N.

Standard dyadic maximal estimates for orthogonal functions then give a bound much smaller than N
loglogN
	​

.

Fixed trigonometric polynomials

This case can be settled completely.

Lemma 1: orthogonal decomposition for trigonometric polynomials

Let

p(x)=
0<∣m∣≤d
∑
	​

c
m
	​

e
2πimx

have mean zero. Choose an integer L such that

q
L
>d.

For each residue class r∈{1,…,L}, consider

p(n
r+jL
	​

α),j≥0.

These functions are pairwise orthogonal.

Proof

Suppose two Fourier frequencies from distinct terms coincide:

an
r+jL
	​

=bn
r+j
′
L
	​

,0<∣a∣,∣b∣≤d,j
′
>j.

Taking absolute values gives

n
r+jL
	​

n
r+j
′
L
	​

	​

=
∣b∣
∣a∣
	​

≤d.

Lacunarity gives

n
r+jL
	​

n
r+j
′
L
	​

	​

≥q
L(j
′
−j)
≥q
L
>d,

a contradiction. Hence the Fourier supports of distinct terms in the same residue class are disjoint. Therefore the terms are orthogonal. □

Lemma 2: almost-everywhere polynomial bound

For every mean-zero trigonometric polynomial p and every δ>0,

k=1
∑
N
	​

p(n
k
	​

α)=O
p,q,δ
	​

(N
1/2
(logN)
3/2+δ
)

for almost every α.

Proof

For each residue class modulo L, Lemma 1 gives an orthogonal sequence X
j
	​

 with

∥X
j
	​

∥
2
	​

=∥p∥
2
	​

.

For an orthogonal family X
1
	​

,…,X
M
	​

, the dyadic decomposition of intervals yields the Rademacher–Menshov estimate

∫
0
1
	​

1≤m≤M
max
	​

	​

j=1
∑
m
	​

X
j
	​

(α)
	​

2
dα≤C(1+log
2
	​

M)
2
j=1
∑
M
	​

∥X
j
	​

∥
2
2
	​

.

Here the right side is at most

CM(logM)
2
∥p∥
2
2
	​

.

At M=2
s
, Chebyshev’s inequality gives

λ{
m≤2
s
max
	​

	​

j=1
∑
m
	​

X
j
	​

	​

>2
s/2
s
3/2+δ
}≤
s
1+2δ
C
	​

.

The right side is summable in s. Borel–Cantelli therefore gives, for almost every α,

m≤2
s
max
	​

	​

j=1
∑
m
	​

X
j
	​

(α)
	​

=O
α
	​

(2
s/2
s
3/2+δ
).

Summing over the finitely many residue classes proves

k=1
∑
N
	​

p(n
k
	​

α)=O
p,q,δ
	​

(N
1/2
(logN)
3/2+δ
).

□

In particular,

k=1
∑
N
	​

p(n
k
	​

α)=o(N
loglogN
	​

)

almost everywhere.

Why ordinary L
2
-approximation does not close the argument

Choose a trigonometric polynomial p and write

g=p+r.

The polynomial part is harmless. For the remainder,

R
N
	​

(α):=
k=1
∑
N
	​

r(n
k
	​

α),

the triangle inequality gives

∣R
N
	​

(α)∣≤
k=1
∑
N
	​

∣r(n
k
	​

α)∣.

Since multiplication by n
k
	​

 preserves Lebesgue measure,

∫
0
1
	​

∣r(n
k
	​

α)∣dα=∥r∥
1
	​

.

Hence

∫
0
1
	​

k=1
∑
N
	​

∣r(n
k
	​

α)∣dα=N∥r∥
1
	​

.

Markov’s inequality consequently gives

λ{∣R
N
	​

∣>εN
loglogN
	​

}≤
ε
loglogN
	​

∥r∥
1
	​

	​

.

At geometric values N=2
j
, this becomes approximately

logj
	​

∥r∥
1
	​

	​

,

whose sum diverges. Thus a fixed L
2
-small remainder cannot be discarded by this argument.

Allowing p to depend on N introduces another difficulty: its degree may increase so rapidly that the number L of orthogonal residue classes, satisfying q
L
>degp, also increases. The constants in the polynomial maximal estimate can then overwhelm the desired normalization.

This is not merely a cosmetic defect. It is exactly the place where arbitrary slow decay of the Fourier tail can enter.

Twelve independent approaches
1. Direct Fourier orthogonalization

Separate each Fourier mode and group terms whose products mn
k
	​

 coincide.

Verified gain: finite Fourier support is controlled.

Failure: infinitely many Fourier modes may create arbitrarily large collision classes.

2. Contradiction from positive-measure exceptional sets

Assume

∣T
N
	​

∣≥cN
loglogN
	​


infinitely often on a positive-measure set and integrate.

Failure: large values can occur on sets whose measures tend to zero but whose limsup still has positive measure. A second-moment estimate without summability does not exclude this.

3. Constructive counterexample by nested spikes

Choose g as a sum of large functions supported on tiny sets and choose n
k
	​

 so many dilates hit the same spikes.

Obstacle: preserving g∈L
2
 while obtaining blocks of size N
loglogN
	​

 on a non-null limsup set requires a sharp balance between amplitude, support measure, and recurrence.

4. Induction over Fourier truncations

Prove the estimate successively for truncations g
≤d
j
	​

	​

.

Obstacle: the exceptional-set estimates depend on d
j
	​

, while no universal rate is available for

∥g−g
≤d
j
	​

	​

∥
2
	​

→0.
5. Transfinite or well-ordered decomposition

Decompose Fourier support into collision components ordered by scale.

Failure: the support is countable, so ordinary induction suffices; transfinite indexing creates no new quantitative estimate.

6. Cardinal arithmetic

Count solutions of

an
k
	​

=bn
ℓ
	​

.

Verified fact: for fixed bounded a,b, only boundedly many relative index gaps are possible.

Failure: a,b range over the entire Fourier support and can be arbitrarily large.

7. Diagonalization

Construct g with Fourier mass on frequencies adapted to increasingly long blocks of the sequence.

Potential: this is compatible with strong correlations.

Obstacle: an L
2
 coefficient budget requires square summability, while the desired block contribution is nearly linear times 
loglogN
	​

.

8. Compactness

Approximate the unit ball of L
2
 by finite-dimensional subsets.

Failure: the L
2
 unit ball is not compact in norm. Weak compactness does not preserve almost-everywhere maximal estimates.

9. Density and Borel–Cantelli

Estimate measures of exceptional events at a sparse sequence N
j
	​

.

Failure: choosing N
j
	​

 sparse enough for summability leaves intervals [N
j
	​

,N
j+1
	​

] too large to interpolate using only triangle inequalities.

10. Reflection to arithmetic structure

Split pairs (k,ℓ) according to

min(n
k
	​

,n
ℓ
	​

)
gcd(n
k
	​

,n
ℓ
	​

)
	​

.

Gain: small gcd forces Fourier coefficients far into the tail.

Obstacle: divisibility chains such as n
k
	​

∣n
k+1
	​

 have maximal gcd and must be handled differently.

11. Auxiliary collision graph

Create a graph with vertices (m,k) and edges whenever

mn
k
	​

=m
′
n
k
′
	​

.

Each connected component corresponds to one resulting Fourier frequency.

Gain: the sum becomes an orthogonal sum over components.

Obstacle: a component can contain one vertex for each k, for example when n
k
	​

∣M and m=M/n
k
	​

. Lacunarity alone does not bound component size.

12. Counterexample search in divisibility chains

Take n
k
	​

=b
k
. Then

g(b
k
α)

is an orbit under the map x↦bx(mod1).

For this special sequence, g∈L
1
, and the pointwise ergodic theorem for the measure-preserving map x↦bx(mod1) gives

N
1
	​

k=1
∑
N
	​

g(b
k
α)⟶0

almost everywhere for mean-zero g. Hence

T
N
	​

=o(N),

which is stronger than the proposed estimate.

Thus a counterexample cannot arise merely from a fixed geometric progression. It would have to exploit nonstationarity in the ratios n
k+1
	​

/n
k
	​

.

Shared verified theorem pool
Theorem A

The mean term is negligible at the proposed scale:

N∫f=o(N
loglogN
	​

).
Theorem B

For every fixed trigonometric polynomial p,

k≤N
∑
	​

(p(n
k
	​

α)−∫p)=O(N
1/2
(logN)
3/2+δ
)

almost everywhere.

Theorem C

For n
k
	​

=b
k
,

k≤N
∑
	​

f(b
k
α)=N∫f+o(N)

almost everywhere.

Theorem D

For arbitrary g∈L
0
2
	​

, the covariance is exactly

⟨g(n
k
	​

⋅),g(n
ℓ
	​

⋅)⟩=
r

=0
∑
	​

g
	​

(r
d
kℓ
	​

n
ℓ
	​

	​

)
g
	​

(r
d
kℓ
	​

n
k
	​

	​

)
	​

.

No theorem above supplies a summable maximal estimate uniformly over the L
2
 unit ball.

Strongest unresolved target

A sufficient result would be a maximal inequality of the form

λ{
M≤N
max
	​

	​

k=1
∑
M
	​

g(n
k
	​

α)
	​

>tN}≤
t
2
Φ
g
	​

(N)
	​


where

j=1
∑
∞
	​

logj
Φ
g
	​

(2
j
)
	​

<∞.

Neither the elementary L
2
 estimate nor Fourier truncation establishes such summability. The trivial estimate

∥T
N
	​

∥
2
	​

≤N∥g∥
2
	​


would only yield probabilities of order 1/loglogN, which are not summable along geometric N.

Conversely, a disproof requires constructing g∈L
2
 and a lacunary sequence such that coherent Fourier collisions yield contributions of order

N
loglogN
	​


infinitely often on a set of positive measure. The collision graph shows how coherence could occur, but the square-summability of the Fourier coefficients prevents the present construction from reaching that scale.

No argument developed above proves the universal assertion, and no construction developed above violates it.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100
Confidence applies to the formal reductions, Fourier identities, polynomial case, and identification of the unresolved quantitative step—not to the truth or falsity of the proposed universal estimate.

COMPLETENESS_SCORE: 38/100

ADVERSARIAL_SURVIVAL_SCORE: 91/100 for the verified partial results; 0/100 for any claimed resolution, since none is claimed.

RESOURCE_USAGE: approximately 100% of the available response budget; 12 principal strategies explored; 4 verified lemmas/theorems retained; 8 unsuccessful proof routes; 3 counterexample frameworks examined.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

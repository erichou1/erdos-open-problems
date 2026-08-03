# Erdős Problem #1062 [unsolved] 25%

---

## ChatGPT Response

0. Formalization

For n∈N, write

[n]={1,2,…,n}.

Call A⊆[n] admissible when

∀a,b,c∈A,(a,b,c pairwise distinct)⟹¬(a∣b ∧ a∣c).

Define

f(n)=max{∣A∣:A⊆[n] is admissible}.

The maximum exists because [n] has finitely many subsets.

Quantifier structure

The admissibility condition is

∀a∈A,∣{b∈A:b

=a, a∣b}∣≤1.

Thus every selected integer has at most one selected strict multiple.

The extremal assertion f(n)≥k means

∃A⊆[n](∣A∣≥k ∧ ∀a∈A, ∣{b∈A:a∣b, b>a}∣≤1).

Its negation is

∀A⊆[n],∣A∣≥k⟹∃a,b,c∈A

with a,b,c distinct and a∣b, a∣c.

Equivalent integer-program formulation

For d∈[n], introduce x
d
	​

∈{0,1}, where x
d
	​

=1 means d∈A. Then

f(n)=max
d=1
∑
n
	​

x
d
	​


subject to

x
a
	​

+x
b
	​

+x
c
	​

≤2

whenever a,b,c∈[n] are distinct and a∣b, a∣c.

Equivalently, for each a,

x
a
	​

=1⟹
j≥2
ja≤n
	​

∑
	​

x
ja
	​

≤1.
Symmetry and invariance

There is no nontrivial translation symmetry because divisibility is not translation invariant.

There is a partial scaling symmetry: if A⊆[m] is admissible and q≥1, then

qA={qa:a∈A}⊆[qm]

is admissible, since

qa∣qb⟺a∣b.

This scaling does not by itself give an additive or superadditive relation for f.

1. Basic structural lemmas
Lemma 1: Chain bound

Let

d
1
	​

∣d
2
	​

∣⋯∣d
r
	​


be distinct integers. An admissible set contains at most two members of this chain.

Proof

Suppose A contained three members d
i
	​

,d
j
	​

,d
k
	​

 with i<j<k. Then

d
i
	​

∣d
j
	​

,d
i
	​

∣d
k
	​

,

and the three integers are distinct. This violates admissibility. Hence the intersection has size at most two. □

The converse is false: meeting every divisibility chain in at most two points is not sufficient. For example, the configuration

{a,2a,3a}

violates admissibility even though 2a and 3a are incomparable.

Lemma 2: Monotonicity
f(n)≤f(n+1)≤f(n)+1.
Proof

Every admissible subset of [n] remains admissible in [n+1], giving the first inequality.

If A⊆[n+1] is admissible, then A∩[n] is admissible and has size at least ∣A∣−1. Therefore

∣A∣−1≤f(n),

so ∣A∣≤f(n)+1. Maximizing over A gives the second inequality. □

2. Verified lower bound
Theorem 3

For every n≥1,

f(n)≥n−⌊
3
n
	​

⌋=⌈
3
2n
	​

⌉.
Proof

Set

A
n
	​

={⌊
3
n
	​

⌋+1,…,n}.

Its cardinality is

∣A
n
	​

∣=n−⌊
3
n
	​

⌋=⌈
3
2n
	​

⌉.

Take a∈A
n
	​

. Since a>n/3, we have

3a>n.

Every strict positive multiple of a is one of

2a,3a,4a,….

Among these, only 2a can possibly lie in [n], because every multiple ka with k≥3 exceeds n. Thus a has at most one strict multiple in A
n
	​

.

Therefore no a∈A
n
	​

 divides two distinct other elements of A
n
	​

, so A
n
	​

 is admissible. □

Boundary verification

For n=3m, the set is

{m+1,…,3m}

and has 2m elements.

For n=3m+1, it has 2m+1 elements.

For n=3m+2, it has 2m+2 elements.

These equal ⌈2n/3⌉ in all three residue classes.

3. A first-principles upper bound

Every positive integer has a unique representation

r2
j
,

where r is odd and j≥0. For each odd r≤n, define the dyadic chain

C
r
	​

={r,2r,4r,…}∩[n].

The chains C
r
	​

 partition [n].

By Lemma 1, an admissible set contains at most two elements from each C
r
	​

. That observation alone overcounts chains of length one, so we calculate more precisely.

Lemma 4

For every admissible A⊆[n], there is an injection

A↪{⌊n/4⌋+1,…,n}.
Proof

Fix an odd r, and list its chain increasingly:

C
r
	​

={r,2r,…,2
t
r},2
t
r≤n<2
t+1
r.

The two largest elements are 2
t
r and, when t≥1, 2
t−1
r.

We have

2
t
r>
2
n
	​

,

because otherwise 2
t+1
r≤n, contradicting maximality of t. Similarly, when t≥1,

2
t−1
r>
4
n
	​

.

By Lemma 1,

∣A∩C
r
	​

∣≤2.

Map the members of A∩C
r
	​

, in increasing order, to the corresponding number of largest positions in C
r
	​

: one selected member maps to the largest chain element; two selected members map to the two largest chain elements.

Every image is greater than n/4. Different dyadic chains are disjoint, so images originating in different chains are different. Within one chain, the assigned images are also different. Hence the resulting map is injective. □

Theorem 5

For every n≥1,

f(n)≤n−⌊
4
n
	​

⌋.

Consequently,

n
f(n)
	​

≤
4
3
	​

+O(
n
1
	​

).
Proof

By Lemma 4, every admissible A⊆[n] injects into the set of integers exceeding n/4, whose cardinality is

n−⌊
4
n
	​

⌋.

Therefore the same quantity bounds ∣A∣, and hence bounds f(n). □

Combining the verified bounds gives

⌈
3
2n
	​

⌉≤f(n)≤n−⌊
4
n
	​

⌋
	​

.

Thus

3
2
	​

≤
n→∞
liminf
	​

n
f(n)
	​

≤
n→∞
limsup
	​

n
f(n)
	​

≤
4
3
	​

.
4. Why the dyadic bound cannot settle the problem

The dyadic-chain argument uses only configurations

a,2a,4a.

It does not exploit branching configurations such as

a,2a,3a,

which are forbidden even though 2a and 3a lie in different dyadic chains.

A sharper upper bound must therefore coordinate different dyadic chains. For example, whenever

3a≤n,

the triple

{a,2a,3a}

imposes

x
a
	​

+x
2a
	​

+x
3a
	​

≤2.

Likewise,

x
a
	​

+x
2a
	​

+x
5a
	​

≤2,x
a
	​

+x
3a
	​

+x
5a
	​

≤2

whenever the displayed integers lie in [n].

These inequalities overlap heavily. Simply summing them does not yield a valid sharp density bound unless the multiplicity with which each variable occurs is controlled.

5. Multiplicative-component formulation

Every positive integer admits a unique factorization

m=u2
α
3
β
,

where gcd(u,6)=1 and α,β≥0.

For each u coprime to 6, define

P
u
	​

(n)={u2
α
3
β
≤n:α,β≥0}.

These sets partition [n]. Inside P
u
	​

(n), divisibility corresponds to coordinatewise comparison:

u2
α
3
β
∣u2
γ
3
δ
⟺α≤γ and β≤δ.

Therefore the restriction of an admissible set to P
u
	​

(n) is a subset of a finite lattice region in N
2
 satisfying:

No selected lattice point has two selected points weakly northeast of it.

This formulation captures both chain and branching obstructions. However, it is still incomplete for the original problem because divisibility may also multiply by primes other than 2 and 3, connecting different P
u
	​

(n). Consequently, optimizing independently on the P
u
	​

(n) does not produce a valid exact decomposition.

A complete multiplicative decomposition would require fixing the part of an integer coprime to every prime, which leaves only the integer 1 and therefore gives no useful finite-dimensional separation.

6. Limit and irrationality

The elementary properties proved above do not establish that

n→∞
lim
	​

n
f(n)
	​


exists.

Monotonicity of f(n) is insufficient: a nondecreasing integer-valued sequence with increments at most one can still have a normalized ratio that oscillates.

A standard route to limit existence would be a sufficiently strong approximate additivity relation such as

f(m+n)≥f(m)+f(n)−o(m+n)

or a corresponding approximate subadditivity relation. Divisibility across adjacent intervals prevents an immediate construction of this kind: after translating an admissible set, divisibility relations are not preserved, and after scaling two sets into separate ranges, cross-divisibility may still occur.

Therefore, from the deductions established here, none of the following has been proved:

n→∞
lim
	​

n
f(n)
	​

 exists;
n→∞
lim
	​

n
f(n)
	​

 is rational;
n→∞
lim
	​

n
f(n)
	​

 is irrational.

In particular, proving irrationality logically requires first proving existence of the limit.

7. Adversarial verification
Lower-bound attack

Potential failure: an element a>n/3 might divide two larger elements not equal to 2a.

This is impossible because any strict multiple is ka with integer k≥2, and every k≥3 gives ka>n. Thus at most 2a remains.

Upper-bound attack

Potential failure: the injection replaces selected elements by other elements and might identify two images.

It cannot identify images from different chains because the dyadic chains partition [n]. It cannot identify images within one chain because at most two selected elements are assigned to two distinct top positions.

Potential failure: the second-largest chain element might be at most n/4.

If 2
t−1
r≤n/4, then

2
t+1
r≤n,

contradicting that 2
t
r was the largest chain element not exceeding n.

Thus the upper bound survives these attacks.

Quantifier check

The proof controls every a∈A, not merely the smallest element of A. The upper bound applies to every admissible A⊆[n], so maximizing yields a bound on f(n).

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 99/100 for the displayed elementary bounds.

COMPLETENESS_SCORE: 25/100. The construction and the bound f(n)≤n−⌊n/4⌋ are rigorous, but the exact asymptotic density, existence of the limit, and irrationality question remain undecided by this reasoning.

ADVERSARIAL_SURVIVAL_SCORE: 97/100 for the proved lemmas and bounds.

RESOURCE_USAGE: Approximately 90% of the allocated response budget; several structural approaches examined, including interval construction, dyadic-chain decomposition, integer programming, multiplicative lattice decomposition, approximate additivity, and overlapping forbidden-triple inequalities.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

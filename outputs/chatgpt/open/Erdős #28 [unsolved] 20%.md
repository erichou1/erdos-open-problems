# Erdős Problem #28 [unsolved] 20%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

0. Formalization

Let N={1,2,3,…}. If instead 0∈N, only finitely many boundary terms change, so the target limsup is unaffected.

Define

r
A
	​

(n)=(1
A
	​

∗1
A
	​

)(n)=
m∈Z
∑
	​

1
A
	​

(m)1
A
	​

(n−m).

Thus r
A
	​

(n) counts ordered representations n=a+b with a,b∈A. If unordered representations are used instead, the two counts differ by at most a factor of 2 plus diagonal terms, so unboundedness is equivalent.

Target theorem

For every A⊆N,

(∃N
0
	​

 ∀n≥N
0
	​

, r
A
	​

(n)≥1)⟹(∀M∈N ∃n∈N, r
A
	​

(n)≥M).

Equivalently,

A+A is cofinite⟹
n→∞
limsup
	​

r
A
	​

(n)=∞.
Negation

The negation is the existence of A⊆N, N
0
	​

∈N, and K∈N such that

∀n≥N
0
	​

,r
A
	​

(n)≥1,

but

∀n,r
A
	​

(n)≤K.

So a counterexample would be an eventually complete additive basis of order 2 with uniformly bounded representation function.

Contrapositive

The target is equivalent to

(
n
sup
	​

r
A
	​

(n)<∞)⟹(infinitely many n satisfy r
A
	​

(n)=0).
Counting function

Let

A(N)=∣A∩[1,N]∣.

The first rigid consequence is:

A(N)=Θ(
N
	​

)

for any hypothetical bounded counterexample.

Indeed, suppose r
A
	​

(n)≤K for all n, and r
A
	​

(n)≥1 for all n≥N
0
	​

.

For the lower bound, every n∈[N
0
	​

,N] has at least one representation n=a+b, and necessarily a,b≤N. Hence

A(N)
2
≥N−N
0
	​

+1,

so

A(N)≥
N−N
0
	​

+1
	​

.

For the upper bound, every ordered pair (a,b)∈A(⌊N/2⌋)
2
 has a+b≤N. Therefore

A(⌊N/2⌋)
2
≤
n≤N
∑
	​

r
A
	​

(n)≤KN.

Thus, for M=⌊N/2⌋,

A(M)
2
≤2KM+O(1),

so

A(M)≪
K
	​

M
	​

.

Therefore any counterexample must live exactly at square-root density.

1. Equivalent formulations
Formulation 1: bounded representation obstruction

The theorem says there is no A⊆N satisfying simultaneously

1≤r
A
	​

(n)≤K

for all sufficiently large n.

Formulation 2: finite interval form

For every N, let A
N
	​

=A∩[1,N]. If A+A is cofinite, then for all large N,

[N
0
	​

,N]⊆A
N
	​

+A
N
	​

.

The theorem asks whether this eventual interval-covering forces arbitrarily high collision multiplicity among the sums a+b.

Formulation 3: pair-to-sum map

Consider the map

ϕ:A×A→N,ϕ(a,b)=a+b.

The hypothesis says ϕ(A×A) misses only finitely many integers. The desired conclusion says that the fiber sizes

∣ϕ
−1
(n)∣

are unbounded.

The negation says there is a map ϕ whose image is cofinite and whose fibers are uniformly bounded.

Formulation 4: generating function form

Let

F(z)=
a∈A
∑
	​

z
a
.

Then

F(z)
2
=
n≥2
∑
	​

r
A
	​

(n)z
n
.

The hypothesis says the coefficients of F(z)
2
 are eventually positive. The negation says those coefficients are eventually positive but uniformly bounded.

This gives

1−z
z
N
0
	​

	​

⪯F(z)
2
⪯K
1−z
z
2
	​

,

coefficientwise after ignoring finitely many initial terms.

This implies only the already verified scale

F(r)≍(1−r)
−1/2

as r↑1, not a contradiction by itself.

2. Extremal cases and invariants
Finite A

Impossible. If A is finite, then A+A is finite, so it cannot contain all sufficiently large integers.

Positive-density A

If

A(N)≫N

along an infinite sequence, then

n≤2N
∑
	​

r
A
	​

(n)≥A(N)
2
≫N
2
.

Since there are only 2N possible sums up to 2N, some r
A
	​

(n)≫N. Hence the conclusion holds.

More generally, if

N
	​

A(N)
	​

→∞

along some sequence, then

n≤2N
max
	​

r
A
	​

(n)≥
2N
A(N)
2
	​

→∞.

So any counterexample must satisfy

A(N)=O(
N
	​

).

Combined with cofinite covering,

A(N)≫
N
	​

.

Thus the only possible obstruction is exactly square-root growth.

Translation invariance

Replacing A by A+t shifts A+A by 2t. Cofiniteness is preserved, and

r
A+t
	​

(n)=r
A
	​

(n−2t).

Thus unboundedness of r
A
	​

 is invariant under translation.

Finite modification

Adding or deleting finitely many elements changes each r
A
	​

(n) by at most O(1). Therefore infinite limsup versus finite limsup is unchanged.

3. Twelve independent strategies
Strategy 1: Direct counting

Try to prove that covering every large integer requires more than O(N) pairs below N.

Verified result: only gives

A(N)
2
≥N−O(1).

Obstacle: bounded representations allow exactly O(N) pairs, so counting alone is compatible.

Status: insufficient.

Strategy 2: Average representation

Use

n≤2N
max
	​

r
A
	​

(n)≥
2N
A(N)
2
	​

.

This proves unboundedness if A(N)/
N
	​

→∞.

Obstacle: a counterexample may have A(N)≍
N
	​

.

Status: conditional only.

Strategy 3: Contradiction from bounded fibers

Assume

1≤r
A
	​

(n)≤K

eventually. Attempt to show incompatible structural constraints.

Verified consequences:

A(N)=Θ(
N
	​

),

and

n≤N
∑
	​

r
A
	​

(n)=Θ(N).

Obstacle: these are mutually compatible.

Status: no contradiction.

Strategy 4: Generating functions

Let

F(z)=
a∈A
∑
	​

z
a
.

Then F(z)
2
 has eventually positive bounded coefficients.

From the hypothesis,

F(r)
2
≫
1−r
1
	​

,

and from bounded representations,

F(r)
2
≪
K
	​

1−r
1
	​

.

So

F(r)≍(1−r)
−1/2
.

Obstacle: this matches the square-root counting scale and does not contradict positivity.

Status: no contradiction.

Strategy 5: Energy method

Define additive energy up to N:

E(N)=
n≤2N
∑
	​

r
A
N
	​

	​

(n)
2
.

If r
A
	​

(n)≤K, then

E(N)≤K
n≤2N
∑
	​

r
A
N
	​

	​

(n)=KA(N)
2
≪N.

Cauchy gives

E(N)≥
2N
A(N)
4
	​

.

Since A(N)
2
≍N, this only gives

E(N)≫N.

Thus

E(N)≍N.

Obstacle: again compatible.

Status: insufficient.

Strategy 6: Dyadic decomposition

Let

B
j
	​

=A∩(2
j−1
,2
j
].

Then

∣B
1
	​

∣+⋯+∣B
m
	​

∣≍2
m/2
.

Covering [2
m
,2
m+1
] requires sums from layer pairs B
i
	​

+B
j
	​

 with i,j≤m+1.

Obstacle: the number of available cross-layer pairs is of the same order as the number of integers to cover.

Status: no contradiction from first-order layer counting.

Strategy 7: Diagonalization

Try to construct an integer n missed by all sums a+b, assuming r
A
	​

≤K.

Obstacle: cofinite coverage explicitly prevents such n, so one must exploit bounded multiplicity to force a missed value. Direct diagonal exclusion does not produce enough forbidden residues.

Status: failed.

Strategy 8: Modular obstruction

Reduce A modulo q. Since A+A contains all large integers, for every modulus q,

Amodq+Amodq=Z/qZ.

Thus A must be an additive basis modulo every q.

Obstacle: this condition is weak. A set of roughly 
q
	​

 residues can cover Z/qZ by sums.

Status: no contradiction.

Strategy 9: Compactness

Assume bounded counterexamples exist. Extract local limits of shifted sets

A−t
j
	​

.

One hopes to obtain a bi-infinite set B⊆Z with

1≤r
B
	​

(n)≤K

for all n∈Z.

Obstacle: compactness can produce local limits, but passing global representation bounds and full coverage simultaneously requires careful control of both positive and negative directions.

Status: unresolved reduction, not a proof.

Strategy 10: Induction on intervals

Try to show that if [N
0
	​

,N]⊆A+A with bounded multiplicity, then extending coverage to [N,2N] forces too many new elements.

Obstacle: adding about 
N
	​

 new elements in each dyadic scale is numerically sufficient to create about N new sums.

Status: inconclusive.

Strategy 11: Graph model

Choose one representation

n=a
n
	​

+b
n
	​


for every sufficiently large n. This gives a graph on vertex set A, with an edge labeled n.

Bounded r
A
	​

(n) says each label has bounded multiplicity.

Obstacle: graph sparsity and label uniqueness do not contradict the existence of one edge per large label.

Status: structural but incomplete.

Strategy 12: Counterexample search

Try to recursively build A with bounded representations and eventual coverage.

At stage N, add elements to cover currently missing sums while avoiding too many repeated sums.

Obstacle: local construction may keep representations bounded for a long time. The difficulty is forcing eventual global failure.

Status: no finite obstruction found.

4. Verified theorem pool
Lemma 1: Cofinite coverage forces lower square-root growth

Assume A+A contains all integers n≥N
0
	​

. Then for all N≥N
0
	​

,

A(N)
2
≥N−N
0
	​

+1.

Proof: For every n∈[N
0
	​

,N], choose a,b∈A with a+b=n. Since a,b≥1, both a,b≤n−1≤N. Hence each such n is the sum of a pair from A∩[1,N]. There are A(N)
2
 ordered pairs available, so

A(N)
2
≥N−N
0
	​

+1.

No boundedness assumption is used.

Lemma 2: Bounded representation forces upper square-root growth

Assume r
A
	​

(n)≤K for all n. Then

A(N)≤
2KN+O(1)
	​

.

Proof: Every ordered pair (a,b)∈(A∩[1,N])
2
 has sum at most 2N. Therefore

A(N)
2
≤
n≤2N
∑
	​

r
A
	​

(n)≤2KN.

Thus

A(N)≤
2K
	​

N
	​

.
Lemma 3: Super-square-root growth implies unbounded representations

If

N→∞
limsup
	​

N
	​

A(N)
	​

=∞,

then

n→∞
limsup
	​

r
A
	​

(n)=∞.

Proof: For every N,

n≤2N
∑
	​

r
A
	​

(n)≥A(N)
2
.

Therefore

n≤2N
max
	​

r
A
	​

(n)≥
2N
A(N)
2
	​

.

If A(N)/
N
	​

 is unbounded along a subsequence, the right-hand side is unbounded along that subsequence.

Lemma 4: Any bounded counterexample has exact square-root order

If A+A is cofinite and r
A
	​

(n)≤K for all n, then

c
N
	​

≤A(N)≤C
K
	​

N
	​


for all sufficiently large N.

This follows directly from Lemmas 1 and 2.

5. Primary gap

The entire problem is now equivalent to eliminating the following possibility:

There exists A⊆N, constants N
0
	​

,K, and constants 0<c<C<∞, such that

c
N
	​

≤A(N)≤C
N
	​

,
r
A
	​

(n)≥1(n≥N
0
	​

),

and

r
A
	​

(n)≤K(n≥1).

All elementary first-order counting identities are consistent with this hypothetical configuration. Therefore a proof must use structure beyond total pair counts.

6. Branch exploration
Branch A: energy contradiction

Assume 1≤r
A
	​

(n)≤K eventually.

For A
N
	​

=A∩[1,N], define

r
N
	​

(n)=∣{(a,b)∈A
N
2
	​

:a+b=n}∣.

Then

n
∑
	​

r
N
	​

(n)=A(N)
2
≍N.

Also

n
∑
	​

r
N
	​

(n)
2
≤K
n
∑
	​

r
N
	​

(n)≪
K
	​

N.

By Cauchy,

n
∑
	​

r
N
	​

(n)
2
≥
∣{n:r
N
	​

(n)>0}∣
(∑
n
	​

r
N
	​

(n))
2
	​

≥
2N
A(N)
4
	​

≍N.

Thus

n
∑
	​

r
N
	​

(n)
2
≍N.

No contradiction appears: lower and upper bounds match.

Branch A failed.

Branch B: dyadic layer pressure

Let

b
j
	​

=∣A∩(2
j−1
,2
j
]∣.

Since

A(2
m
)≍2
m/2
,

we have

j≤m
∑
	​

b
j
	​

≍2
m/2
.

The interval [2
m
,2
m+1
] has length 2
m
. It must be covered by sums of elements from layers B
i
	​

+B
j
	​

 with i,j≤m+1.

The total number of available ordered pairs from earlier layers is

(
j≤m+1
∑
	​

b
j
	​

)
2
≍2
m
.

Again, this is exactly the required order of magnitude. Bounded multiplicity imposes that these pairs must be distributed almost injectively over sums, but this near-injectivity is not impossible by counting alone.

Branch B failed.

Branch C: modular density

For every modulus q, define

A
q
	​

={amodq:a∈A}.

Since A+A contains all sufficiently large integers, every residue class modulo q is eventually represented. Hence

A
q
	​

+A
q
	​

=Z/qZ.

Therefore

∣A
q
	​

∣
2
≥q,

so

∣A
q
	​

∣≥
q
	​

.

This matches the global lower density. No contradiction follows.

Branch C failed.

7. Adversarial check of all verified claims
Check Lemma 1

Possible hidden issue: Could a representation n=a+b use a>N?

No, because a,b≥1, so a<n≤N. Thus both are ≤N−1. Lemma 1 survives.

Check Lemma 2

Possible hidden issue: Does ∑
n≤2N
	​

r
A
	​

(n) count pairs with elements greater than N?

Yes, but that only makes the sum larger. We only need

A(N)
2
≤
n≤2N
∑
	​

r
A
	​

(n).

If r
A
	​

(n)≤K, then

n≤2N
∑
	​

r
A
	​

(n)≤2KN.

Lemma 2 survives.

Check Lemma 3

Possible hidden issue: Does averaging over n≤2N miss pairs with sum >2N?

Pairs from A∩[1,N] have sum at most 2N, so no. Lemma 3 survives.

Check Branch A

Energy bounds match. No contradiction was proved. Correctly rejected.

Check Branch B

Dyadic counting gives the right scale but not contradiction. Correctly rejected.

Check Branch C

Modular surjectivity is necessary but too weak. Correctly rejected.

8. Dependency graph

Verified dependencies:

Cofinite A+A⟹A(N)≫
N
	​

.
n
sup
	​

r
A
	​

(n)<∞⟹A(N)≪
N
	​

.

Therefore,

counterexample⟹A(N)=Θ(
N
	​

).

Also,

A(N)/
N
	​

 unbounded⟹limsupr
A
	​

(n)=∞.

Unresolved dependency:

A(N)=Θ(
N
	​

)+A+A cofinite+r
A
	​

(n)≤K

has not been contradicted by the methods above.

9. Final state

RESOURCE_EXHAUSTED

I did not obtain a proof or disproof of the original statement from first principles within this response. The strongest rigorously established conclusion is:

A+A cofinite and 
n
sup
	​

r
A
	​

(n)<∞⟹A(N)=Θ(
N
	​

).

Thus every possible counterexample must have square-root density and almost perfectly efficient additive covering. Counting, averaging, energy, modular, dyadic, graph, compactness, and direct diagonal attempts did not eliminate that possibility.

PROOF_CONFIDENCE: 100 for the verified lemmas; 0 for a proof of the original statement.

COMPLETENESS_SCORE: 20.

ADVERSARIAL_SURVIVAL_SCORE: 90 for the partial deductions; no complete proof was produced.

RESOURCE_USAGE: approximately 12 branches considered, 4 verified lemmas generated, 8 failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

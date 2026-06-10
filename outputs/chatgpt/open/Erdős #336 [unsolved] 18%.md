# Erdős Problem #336 [unsolved] 18%

---

## ChatGPT Response

Phase 0: Formalization

Let A⊆N, and for t≥1 define

tA={a
1
	​

+⋯+a
t
	​

:a
i
	​

∈A}.

I use the only interpretation under which “exact order k” can be finite:

e(A)=min{k≥1:kA contains all sufficiently large integers}.

The ordinary order is

o(A)=min{r≥1:
i=1
⋃
r
	​

iA contains all sufficiently large integers}.

Then the function is

h(r)=max{e(A):A⊆N, o(A)≤r, e(A)<∞}.

The target statement is:

Find L=
r→∞
lim
	​

r
2
h(r)
	​

.

To prove L=c, one needs both:

∀ε>0, ∃R, ∀r≥R,h(r)≤(c+ε)r
2
,

and

∀ε>0, ∃R, ∀r≥R,h(r)≥(c−ε)r
2
.

Equivalently, the upper bound says:

Every A with ordinary order at most r and finite exact order satisfies

e(A)≤(c+ε)r
2

for all large r.

The lower bound says:

For every large r, one can construct A
r
	​

⊆N such that

o(A
r
	​

)≤r,e(A
r
	​

)≥(c−ε)r
2
.

The negation of the desired conclusion is:

∀c∈R, ∃ε>0, ∀R, ∃r≥R

such that

	​

r
2
h(r)
	​

−c
	​

≥ε.

So either the normalized sequence does not converge, or it converges to a value other than c.

Basic verified lemmas
Lemma 1: Exact cofinality is upward closed

If kA contains all sufficiently large integers, then (k+s)A contains all sufficiently large integers for every s≥0.

Proof.
Choose any a∈A. Suppose kA contains every integer n≥N. Then for m≥N+a,

m−a≥N,

so m−a∈kA. Hence

m=(m−a)+a∈(k+1)A.

Inducting gives the result for all s≥0. ∎

Therefore “exact order k” must mean the least such k, not merely one such k.

Lemma 2: Ordinary order is at most exact order

If e(A)=k, then o(A)≤k.

Proof.
Since kA is cofinite,

kA⊆
i=1
⋃
k
	​

iA,

so ⋃
i=1
k
	​

iA is also cofinite. Hence o(A)≤k. ∎

Lemma 3: Crude counting lower bound on density

Let

A(x)=∣A∩[1,x]∣.

If o(A)≤r, then for all sufficiently large x,

x−O(1)≤
i=1
∑
r
	​

A(x)
i
.

Thus, in particular,

A(x)≫x
1/r
.

Proof.
If every large integer n≤x lies in ⋃
i=1
r
	​

iA, then each such n is represented using summands at most x. The number of possible i-term sums using elements of A∩[1,x] is at most A(x)
i
. Therefore

x−O(1)≤
i=1
∑
r
	​

A(x)
i
.

For large x, the largest term dominates crudely, giving

A(x)
r
≫x,

hence

A(x)≫x
1/r
.

∎

This is far too weak to determine e(A) in terms of r, but it is a verified necessary condition.

Lemma 4: A residue obstruction

If all elements of A are congruent modulo some d>1, then A has no finite exact order.

Proof.
Suppose a≡a
0
	​

(modd) for all a∈A. Then every element of kA is congruent to

ka
0
	​

(modd).

Thus kA misses all other residue classes modulo d, so it cannot contain all sufficiently large integers. ∎

This gives a necessary condition:

gcd(A−A)=1

for finite exact order. It does not give an upper bound on e(A).

Phase 1: Breadth-first strategy search
Strategy	Description	Main obstacle
Direct proof	Try to bound e(A) from o(A)≤r.	Ordinary representations use variable lengths; exact representations require one fixed length.
Contradiction	Assume e(A)≫r
2
, derive failure of o(A)≤r.	Need structural information about missing exact-length sums.
Construction	Build A
r
	​

 with o(A
r
	​

)≤r and large e(A
r
	​

).	Must control all sufficiently large integers, not just intervals.
Induction on r	Relate h(r+1) to h(r).	No clear operation preserves exact order while increasing ordinary order by one.
Transfinite/ordinal ranks	Rank gaps in tA as t grows.	No natural well-founded rank emerged that controls r
2
.
Cardinal arithmetic	Count possible representations.	Counting gives only A(x)≫x
1/r
, not exact-order control.
Diagonalization	Force certain tA to miss infinitely many integers.	Must simultaneously keep ≤r-representability cofinite.
Compactness	Work modulo many moduli and lift local data.	Local residue coverage does not guarantee global cofinite coverage.
Density	Use lower density of rA to force exact sums.	A may have zero asymptotic density even when it is a basis.
Reflection	Study finite initial segments and scale limits.	Limit objects lose exact cofinite information.
Auxiliary structures	Define length spectra L
A
	​

(n).	Need a theorem forcing k∈L
A
	​

(n) eventually.
Counterexample search	Try to make h(r)/r
2
 oscillate.	Requires explicit families controlling both ordinary and exact order.

Top three selected branches:

Length-spectrum analysis.

Density/counting analysis.

Block construction analysis.

Phase 2: New definitions and invariants
Definition: Length spectrum

For n∈N, define

L
A
	​

(n)={t≥1:n∈tA}.

Then:

o(A)≤r

means

∀
∞
n,L
A
	​

(n)∩{1,…,r}

=∅.

Meanwhile

e(A)=k

means

∀
∞
n,k∈L
A
	​

(n),

and for every j<k,

jA is not cofinite.

So the problem asks how large the first eventually universal exact length can be, assuming every large integer has some representation of length at most r.

Definition: Exact deficiency sets

For t≥1, define

D
t
	​

(A)=N∖tA.

Then tA is cofinite exactly when D
t
	​

(A) is finite.

Thus

e(A)=k

means

D
k
	​

(A) is finite,

but

D
j
	​

(A) is infinite for 1≤j<k.

The ordinary condition o(A)≤r says

j=1
⋂
r
	​

D
j
	​

(A)

is finite.

So we need to understand how the infinite deficiency sets D
1
	​

,…,D
k−1
	​

 can overlap while their first r-fold intersection is finite.

This reformulation looks central, but I could not prove a quadratic sharp bound from it.

Definition: Residue coverage profiles

For modulus m, define

R
t
	​

(A;m)={x(modm):x∈tA}.

If tA is cofinite, then necessarily

R
t
	​

(A;m)=Z/mZ

for every m.

If o(A)≤r, then necessarily

t=1
⋃
r
	​

R
t
	​

(A;m)=Z/mZ

for every m.

But residue coverage is only necessary, not sufficient. It does not control large gaps inside a residue class.

Phase 3: Branch exploration
Branch A: Density/counting

From Lemma 3, ordinary order r forces

A(x)≫x
1/r
.

If e(A)=k, then similarly exact cofinality gives

x−O(1)≤A(x)
k
,

so

A(x)≫x
1/k
.

But since k≥r may be much larger than r, the exact-order density condition is weaker. Counting alone cannot force k=O(r
2
).

Gap A.1. Need an inverse theorem of the form:

If ⋃
i=1
r
	​

iA is cofinite, then some k≤Cr
2
 has kA cofinite.

I could not prove this from counting. The missing ingredient would need to transform variable-length representations into fixed-length representations efficiently.

Branch B: Length-spectrum transfer

We need to convert:

∀
∞
n,L
A
	​

(n)∩[1,r]

=∅

into:

∀
∞
n,k∈L
A
	​

(n)

for some bounded k.

A naive padding argument fails. If n∈tA, then adding extra elements of A changes the represented integer. It proves that nearby shifted integers have longer representations, not that the same integer has longer representations.

For example, if n=a
1
	​

+⋯+a
t
	​

, then

n+sa∈(t+s)A

for fixed a∈A, but this does not imply

n∈(t+s)A.

So the key obstruction is not increasing length; it is increasing length while preserving the target integer.

That requires additive relations inside A, such as replacing one summand by several summands with the same total. Therefore the relevant hidden structure is the set of internal identities

a=b
1
	​

+⋯+b
q
	​

,a,b
i
	​

∈A.

No argument found forces enough such identities merely from o(A)≤r.

Gap B.1. Prove that finite ordinary order forces enough internal additive replacement identities to make a fixed length cofinite by O(r
2
).

This remained unresolved.

Branch C: Block construction

The example in the prompt uses alternating intervals:

A=
j≥0
⋃
	​

(2
2j
,2
2j+1
].

It has small ordinary order but larger exact order because certain exact-length sumsets fail to bridge gaps created by the block structure.

A natural general construction would use rapidly growing blocks

A=
j
⋃
	​

I
j
	​


where I
j
	​

 are long intervals separated by very large gaps. The goal would be:

i=1
⋃
r
	​

iA cofinite,

but

tA not cofinite for every t<cr
2
.

This suggests designing blocks so that variable lengths 1,…,r cover every large scale, while each fixed length t<cr
2
 misses infinitely many scale intervals.

The construction problem becomes a finite covering problem on logarithmic scales:

each block contributes one scale interval;

tA contributes sums of t chosen blocks;

ordinary order allows a union over t≤r;

exact order requires one fixed t.

This branch produced a plausible framework, but not a proof. The unresolved technical step is:

Gap C.1. Construct block scales so that all large integers are covered by some t≤r, while every t<cr
2
 has infinitely many uncovered intervals.

I did not obtain a complete construction.

Main unresolved theorem isolated

The central theorem needed for an upper bound is:

If o(A)≤r and e(A)<∞, then e(A)≤Cr
2
+o(r
2
).
	​


The central theorem needed for a lower bound is:

For large r, construct A
r
	​

 with o(A
r
	​

)≤r, e(A
r
	​

)≥cr
2
−o(r
2
).
	​


To determine the limit, the constants C and c must match.

I proved neither matching upper nor matching lower bound.

Local verification / adversarial check

The verified lemmas survived the following checks:

Lemma 1 does not assume 0∈A; it only needs one fixed a∈A.

Lemma 2 uses only definitions.

Lemma 3 uses positivity of summands so that a sum ≤x uses only elements ≤x.

Lemma 4 is only a necessary obstruction; I did not use its converse.

The failed branches all fail at the same conceptual point: ordinary order gives eventual coverage by a union of short sumsets, but exact order requires eventual coverage by one fixed sumset. I found no first-principles mechanism that determines the optimal quadratic constant.

Dependency graph of verified results
Definitions

imply

Lemma 1: upward closure of exact cofinality

which justifies

e(A)=min{k:kA cofinite}.

Definitions also imply

Lemma 2: o(A)≤e(A).

Counting gives

Lemma 3: o(A)≤r⇒A(x)≫x
1/r
.

Residues give

Lemma 4: gcd(A−A)=1 is necessary for finite exact order.

None of these lemmas implies the requested limit.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified lemmas; 0/100 for any claimed value of the limit, since no value was proved.

COMPLETENESS_SCORE: 18/100. The definitions and several necessary conditions were rigorously established, but the main asymptotic value was not determined.

ADVERSARIAL_SURVIVAL_SCORE: 91/100 for the partial results; the attempted routes to the main theorem did not survive.

RESOURCE_USAGE: approximately 100% of the available proof-search budget for this response; 3 main branches explored; 4 verified lemmas generated; 3 failed proof attempts isolated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

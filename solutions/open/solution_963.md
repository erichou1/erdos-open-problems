# Erdős Problem #963 [unsolved] 45%

---

## ChatGPT Response

Formalization

For a finite set A⊂R, define

d(A):=max{∣B∣:B⊆A, B is dissociated}.

A finite set B⊂R is dissociated precisely when

b∈B
∑
	​

ε
b
	​

b=0,ε
b
	​

∈{−1,0,1},

implies that every ε
b
	​

=0. Indeed, a nonzero such relation is equivalent, after separating positive and negative coefficients, to two distinct subsets of B having the same sum.

The extremal function is therefore

f(n)=
A⊂R
∣A∣=n
	​

min
	​

d(A).

The proposed assertion is

∀n≥1f(n)≥⌊log
2
	​

n⌋.

Its negation is

∃n≥1 ∃A⊂R,∣A∣=n,d(A)<⌊log
2
	​

n⌋.

Equivalently, the proposed assertion says that every set of at least 2
k
 distinct real numbers contains a dissociated k-element subset.

Verified lower bound

Let A⊂R be finite, and let B⊆A be a maximal dissociated subset under inclusion. Write m=∣B∣.

For every a∈A∖B, maximality says that B∪{a} is not dissociated. Hence there are coefficients

ε∈{−1,1},(ε
b
	​

)
b∈B
	​

∈{−1,0,1}
B

such that

εa+
b∈B
∑
	​

ε
b
	​

b=0.

Consequently,

a=
b∈B
∑
	​

δ
b
	​

b

for some δ
b
	​

∈{−1,0,1}.

The same representation also covers a∈B, and 0, when present, is represented by the zero vector. Thus

A⊆{
b∈B
∑
	​

δ
b
	​

b:δ
b
	​

∈{−1,0,1}}.

There are at most 3
m
 coefficient vectors, so

∣A∣≤3
m
.

Therefore

d(A)≥⌈log
3
	​

∣A∣⌉,

and hence

f(n)≥⌈log
3
	​

n⌉.
	​


This is the maximal-dissociated-set greedy argument.

Verified upper bound

Take

A={1,2,…,n}.

Suppose B⊆A is dissociated and ∣B∣=m. Its 2
m
 subset sums are distinct integers. Every such sum lies between 0 and

b∈B
∑
	​

b≤mn.

There are only mn+1 integers in this interval. Therefore

2
m
≤mn+1.

Consequently,

f(n)≤max{m∈N:2
m
≤mn+1}.
	​


In particular,

f(n)≤log
2
	​

n+log
2
	​

log
2
	​

n+O(1).

For example, for all sufficiently large n,

f(n)≤log
2
	​

n+log
2
	​

log
2
	​

n+2.

Thus the rigorously established scale is

log
3
	​

n ≲ f(n) ≤ log
2
	​

n+log
2
	​

log
2
	​

n+O(1).
	​

Why the straightforward strengthening fails

The greedy proof only gives

A⊆Span
{−1,0,1}
	​

(B),

whose crude cardinality is 3
∣B∣
. To prove the proposed binary bound by this method, one would need an additional structural argument reducing the number of possible representations from 3
∣B∣
 to approximately 2
∣B∣
.

That reduction does not follow merely from maximality. An element outside B may require both positive and negative coefficients in its representation, and there is no verified injection from A into the 2
∣B∣
 ordinary subset sums of B.

Several natural alternatives also encounter a precise obstruction:

Translation is not harmless: dissociativity is not invariant under replacing every a by a−c, because subset sums of different cardinalities acquire different multiples of c.

Distinct 2-adic valuations prove dissociativity for the differences a−c, but not automatically for the original elements a.

Linear independence modulo 2 implies dissociativity, but reduction modulo 2 need not be injective on A, and the resulting rank can be much smaller than log
2
	​

∣A∣.

No proof that overcomes these obstructions, and no construction violating the proposed inequality, has been established here.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 98/100 for the displayed lower and upper bounds.

COMPLETENESS_SCORE: 45/100 for the original question. The log
3
	​

n lower bound and near-log
2
	​

n upper bound are proved, but the assertion

f(n)≥⌊log
2
	​

n⌋

has neither been proved nor disproved.

ADVERSARIAL_SURVIVAL_SCORE: 96/100 for the verified statements.

RESOURCE_USAGE: Approximately 90% of the available reasoning budget; multiple direct, maximality, counting, modular, valuation, translation, and recursive-partition approaches examined; two complete lemmas established; several attempted strengthenings rejected because of explicit translation or coefficient-sum gaps.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

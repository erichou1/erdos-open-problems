# Erdős Problem #247 [unsolved] 28%

---

## ChatGPT Response

Formal statement.

Let A={a
1
	​

<a
2
	​

<⋯}⊂N
≥1
	​

, and define

α
A
	​

=
n=1
∑
∞
	​

2
−a
n
	​

.

The assertion is

∀A⊂N
≥1
	​

 infinite,(
n→∞
limsup
	​

n
a
n
	​

	​

=∞)⟹α
A
	​

 is transcendental.

Equivalently, with

A(N)=∣A∩[1,N]∣,

the hypothesis is

N→∞
liminf
	​

N
A(N)
	​

=0.

Indeed, if N=a
n
	​

, then A(N)=n, so A(N)/N=n/a
n
	​

. Conversely, if A(N
j
	​

)/N
j
	​

→0, then with m
j
	​

=A(N
j
	​

), one has a
m
j
	​

+1
	​

>N
j
	​

, hence

m
j
	​

+1
a
m
j
	​

+1
	​

	​

≥
A(N
j
	​

)+1
N
j
	​

	​

→∞.

So the problem is exactly:

Does every binary number whose set of 1-digits has lower density 0 have to be transcendental?
	​


Negation.

There exists an infinite A⊂N with

N→∞
liminf
	​

N
A(N)
	​

=0

and a nonzero polynomial P∈Z[x] such that

P(α
A
	​

)=0.

Contrapositive form.

If α∈(0,1) is algebraic and its binary expansion has infinitely many 1’s, then its set of 1-digit positions must have positive lower density:

∃c>0 ∃N
0
	​

 ∀N≥N
0
	​

,A
α
	​

(N)≥cN.

This contrapositive is much stronger than what follows from elementary Diophantine approximation.

Verified partial theorem: large relative gaps imply transcendence

Define gaps by

g
n
	​

=a
n+1
	​

−a
n
	​

.

A stronger sufficient condition is

n→∞
limsup
	​

a
n
	​

a
n+1
	​

	​

=∞.

Under this stronger condition, α
A
	​

 is transcendental.

Proof.

Let

s
n
	​

=
k=1
∑
n
	​

2
−a
k
	​

=
2
a
n
	​

p
n
	​

	​

,

where p
n
	​

∈Z is odd because the last binary digit included is at position a
n
	​

. The tail satisfies

0<α
A
	​

−s
n
	​

=
k=n+1
∑
∞
	​

2
−a
k
	​

≤
m=a
n+1
	​

∑
∞
	​

2
−m
=2
1−a
n+1
	​

.

Assume α
A
	​

 is algebraic of degree d≥2. Liouville’s inequality says that for some constant C(α)>0,

	​

α
A
	​

−
q
p
	​

	​

>C(α)q
−d

for every rational p/q

=α
A
	​

. Applying this to s
n
	​

=p
n
	​

/2
a
n
	​

, with q=2
a
n
	​

, gives

∣α
A
	​

−s
n
	​

∣>C(α)2
−da
n
	​

.

But if a
n+1
	​

/a
n
	​

 is arbitrarily large, then for infinitely many n,

2
1−a
n+1
	​

<C(α)2
−da
n
	​

,

contradicting the upper tail bound.

If d=1, then α
A
	​

 is rational. A rational binary expansion is eventually periodic. Since A is infinite, eventual periodicity would force the gaps between consecutive 1-digits to be bounded. But a
n+1
	​

/a
n
	​

→∞ along a subsequence implies g
n
	​

→∞ along a subsequence, contradiction.

Therefore the stronger relative-gap condition proves transcendence.

This does not solve the original problem, because

limsup
n
a
n
	​

	​

=∞

does not imply large relative gaps. For example,

a
n
	​

=⌈nlog(n+1)⌉

has

n
a
n
	​

	​

→∞,

but

a
n
	​

a
n+1
	​

	​

→1.

So simple rational-approximation arguments cannot settle the stated problem.

Twelve independent strategies and outcomes
Strategy	Core idea	Verified outcome	Obstruction
Direct approximation	Approximate by binary truncations s
n
	​

	Works if a
n+1
	​

/a
n
	​

 is unbounded	Original hypothesis allows a
n+1
	​

/a
n
	​

→1
Contradiction via minimal polynomial	Use P(s
n
	​

)

=0 and denominator 2
da
n
	​

	Again requires a
n+1
	​

>da
n
	​

+O(1)	Same relative-gap obstruction
Induction on algebraic degree	Try to rule out degree 1,2,…	Degree 1 ruled out if gaps unbounded	No mechanism for degree 2+ under mere lower density 0
Cardinality of supports	Expand powers α
k
; supports lie in kA	Useful if A(N)
k
=o(N)	Lower density 0 gives only A(N)=o(N), not A(N)
k
=o(N)
Sumset sparsity	Study A+A+⋯+A	Promising under much stronger sparsity	A(N)=N/logN still gives lower density 0, but kA can be large
Carry analysis	Track binary carries in P(α)	Needs strong control of digit-support convolution	Carries can propagate through dense sumsets
Diagonal construction	Try to build algebraic α with sparse 1-digits	Algebraic numbers are dense in intervals	Density alone does not ensure meeting infinitely many digit constraints
Topological argument	Numbers with lower-density-zero 1-set form a large set	The set is dense by appending long zero blocks	A large topological set may avoid all algebraic numbers
Compactness	Build nested dyadic cylinders with sparse prefixes	Produces real numbers with sparse prefixes	Does not ensure algebraicity
Transfinite/choice construction	Attempt to select algebraic points through constraints	No constructive preservation of algebraicity	Countability of algebraics blocks generic arguments
Reflection/local-to-global	Sparse prefixes might force repeated blocks	True combinatorially	Repetition alone does not contradict algebraicity without stronger Diophantine input
Counterexample search	Seek quadratic or algebraic sparse binary expansion	No explicit construction obtained	Binary digits of algebraic numbers are not controlled by the algebraic equation in a direct finite way

Top three by expected value were:

Diophantine approximation from truncations.

Polynomial expansion and sumset sparsity.

Counterexample construction through nested binary cylinders.

Only the first gives a complete theorem, but only under a stronger hypothesis.

Primary unresolved gap

The original problem reduces to the following digit-density theorem:

If α∈(0,1) is algebraic irrational, then its binary 1-positions cannot have lower density 0.
	​


I attacked this gap through the mechanisms above. Every elementary route I could verify either needs relative gaps,

a
n+1
	​

≥(d+ε)a
n
	​


infinitely often, or needs stronger counting sparsity such as

A(N)
d
=o(N)

along infinitely many N. The stated hypothesis gives neither.

A model obstruction is

A(N)∼
logN
N
	​

.

Then A(N)/N→0, but for every fixed d≥2,

A(N)
d
∼
(logN)
d
N
d
	​

,

which is far larger than N. Thus d-fold additive combinations of A may be dense enough that polynomial relations cannot be contradicted by a simple support-counting argument.

Verified dependency graph

Definitions:

A,A(N),α
A
	​

,s
n
	​

,g
n
	​

.

Verified lemmas:

limsupa
n
	​

/n=∞⟺liminfA(N)/N=0.

For truncations,

0<α
A
	​

−s
n
	​

≤2
1−a
n+1
	​

.

Liouville lower bound for algebraic irrational α of degree d:

∃C>0 ∀p/q

=α,∣α−p/q∣>Cq
−d
.

Therefore,

limsup
a
n
	​

a
n+1
	​

	​

=∞⟹α
A
	​

 is transcendental.

Unresolved original implication:

limsup
n
a
n
	​

	​

=∞⟹α
A
	​

 is transcendental.

No proof or disproof of this implication was obtained from the verified deductions above.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100
COMPLETENESS_SCORE: 28/100
ADVERSARIAL_SURVIVAL_SCORE: 84/100

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; 12 strategies considered; 4 verified lemmas generated; 3 main branches explored; 2 failed proof frameworks identified; no complete proof or disproof of the original statement obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

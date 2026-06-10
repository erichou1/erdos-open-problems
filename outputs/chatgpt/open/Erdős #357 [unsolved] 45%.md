# Erdős Problem #357 [unsolved] 45%

---

## ChatGPT Response

Phase 0: Formalization

Let n∈Z
≥1
	​

. A sequence

1≤a
1
	​

<a
2
	​

<⋯<a
k
	​

≤n

is admissible if all interval sums

S(u,v)=
i=u
∑
v
	​

a
i
	​

,1≤u≤v≤k

are pairwise distinct.

Define

f(n)=max{k: there exists an admissible a
1
	​

<⋯<a
k
	​

≤n}.

The question is whether

f(n)=o(n),

i.e.

∀ε>0 ∃N ∀n≥N,f(n)<εn.

The negation is

∃ε>0 ∀N ∃n≥N,f(n)≥εn.

Equivalently, define prefix sums

P
0
	​

=0,P
j
	​

=a
1
	​

+⋯+a
j
	​

.

Then

S(u,v)=P
v
	​

−P
u−1
	​

.

Thus admissibility is equivalent to:

P
j
	​

−P
i
	​

(0≤i<j≤k)

are all distinct. So {P
0
	​

,…,P
k
	​

} is a set with all positive differences distinct, with the extra constraint that consecutive gaps

P
i
	​

−P
i−1
	​

=a
i
	​


are strictly increasing and at most n.

Immediate invariants:

#{S(u,v)}=
2
k(k+1)
	​

.

Also

1≤S(u,v)≤P
k
	​

≤kn.

Therefore

2
k(k+1)
	​

≤kn,

which only gives

k≤2n−1.

Since a
1
	​

<⋯<a
k
	​

≤n, we also have the trivial sharper bound

k≤n.

So f(n)≤n, but this does not imply f(n)=o(n).

Breadth-first strategy scan

I tested the following proof directions.

Strategy	Result
Direct counting of all interval sums	Gives only k≤n.
Prefix-difference formulation	Useful, but alone gives only Golomb-ruler-type counting.
Count interval sums ≤X	Gives a nontrivial linear upper-bound constant, not o(n).
Harmonic sum over reciprocals of interval sums	Gives another nontrivial constant bound, weaker than the X-counting method.
Dense-block contradiction	Works only when density exceeds a fixed constant.
Induction on k	No monotone recurrence strong enough was found.
Modular collision forcing	No modulus gave unavoidable exact equality.
Diagonalization from finite positive density to infinite positive density	Fails because sequences may drift upward by translation-like behavior.
Construction by large shift a
i
	​

=Q+b
i
	​

	Gives f(n)≫
n
	​

.
Attempted linear construction	No verified construction found.
Attempted o(n) upper bound by density of difference sets	Reduces to unresolved packing of disjoint difference layers.
Compactness/reflection argument	Fails because the first terms need not remain bounded.

The strongest fully verified deductions I obtained are:

f(n)≫
n
	​


and

n→∞
limsup
	​

n
f(n)
	​

≤1−e
−1
.

This is not enough to decide whether f(n)=o(n).

Verified lower bound: f(n)≫
n
	​


Let k≥1, and choose

Q>k
2
.

Define

a
i
	​

=Q+i,1≤i≤k.

Then a
1
	​

<⋯<a
k
	​

. An interval of length d=v−u+1 has sum

S(u,v)=dQ+
2
d(u+v)
	​

.

Suppose

S(u,v)=S(u
′
,v
′
).

Let

d=v−u+1,d
′
=v
′
−u
′
+1.

Then

(d−d
′
)Q=
2
d
′
(u
′
+v
′
)−d(u+v)
	​

.

The right-hand side has absolute value <k
2
, because d,d
′
≤k and u+v,u
′
+v
′
≤2k. Since Q>k
2
, the only possibility is

d=d
′
.

Then

d(u+v)=d(u
′
+v
′
),

so

u+v=u
′
+v
′
.

The pair (d,u+v) uniquely determines (u,v). Hence

(u,v)=(u
′
,v
′
).

Thus all interval sums are distinct.

The largest term is

a
k
	​

=Q+k.

Taking Q=k
2
+1, the construction fits inside [1,n] whenever

k
2
+k+1≤n.

Therefore

f(n)≥(1−o(1))
n
	​

.

So f(n) is at least of order 
n
	​

.

Verified upper bound from small-sum counting

For an admissible sequence, define

N(X)=#{(u,v):1≤u≤v≤k, S(u,v)≤X}.

Because all interval sums are distinct positive integers,

N(X)≤X.

Now compare a
i
	​

 with the componentwise largest possible increasing sequence of length k in [1,n]:

b
i
	​

=n−k+i.

Since a
i
	​

≤b
i
	​

, every interval sum of the a
i
	​

's is at most the corresponding interval sum of the b
i
	​

's. Therefore, if an interval sum in the b
i
	​

-sequence is ≤X, then the corresponding interval sum in the a
i
	​

-sequence is also ≤X. Hence

N
a
	​

(X)≥N
b
	​

(X).

So every admissible sequence must satisfy

N
b
	​

(X)≤X

for all X.

Now suppose along some subsequence n→∞,

k∼δn

for some fixed 0<δ<1. Put

α=1−δ.

For the extremal comparison sequence

b
i
	​

=n−k+i∼(α+i/n)n.

Scale interval length by y=ℓ/n and starting position by s=u/n. The sum of a block of scaled length y starting at scaled position s is asymptotically

n
2
(y(α+s)+
2
y
2
	​

).

Let

X=tn
2
.

Then the normalized number of intervals with sum ≤X tends to the area

F
δ
	​

(t)=meas{(s,y):0≤y≤δ, 0≤s≤δ−y, y(α+s)+
2
y
2
	​

≤t}.

The necessary inequality N
b
	​

(X)≤X becomes

F
δ
	​

(t)≤t

for every fixed t>0.

Now take t→0
+
. A direct scaling calculation gives

t→0
+
lim
	​

t
F
δ
	​

(t)
	​

=log
1−δ
1
	​

.

Therefore admissibility forces

log
1−δ
1
	​

≤1.

Equivalently,

1−δ
1
	​

≤e,

so

δ≤1−e
−1
.

Thus

n→∞
limsup
	​

n
f(n)
	​

≤1−e
−1
.
	​


Numerically,

1−e
−1
≈0.632.

This proves a genuine linear-density obstruction, but it still does not prove f(n)=o(n).

Gap node: prove or disprove f(n)=o(n)

The remaining target is:

∀ε>0,f(n)<εn

for all sufficiently large n, or else construct some fixed c>0 and infinitely many admissible sequences with

k≥cn.

I attacked this gap in two directions.

Gap attack A: strengthen the small-sum method

The small-sum method proves only

limsup
n
f(n)
	​

≤1−e
−1
.

To prove o(n), one would need an inequality forcing

δ=0.

But the comparison sequence b
i
	​

=n−k+i shows that the crude small-sum count cannot do this: for small positive δ, the area ratio satisfies

log
1−δ
1
	​

<1.

So this entire method cannot prove f(n)=o(n) without adding new information beyond interval-sum sizes.

Gap attack B: construct positive-density examples

The simple large-shift construction gives

f(n)≫
n
	​

,

but not linear growth.

A natural attempt is to take

a
i
	​

=Q+i

with smaller Q, but then collisions can occur because

dQ+
2
d(u+v)
	​


may equal

d
′
Q+
2
d
′
(u
′
+v
′
)
	​


for d

=d
′
. Taking Q>k
2
 prevents this, but then n≳k
2
, giving only k≲
n
	​

.

Thus this construction cannot disprove f(n)=o(n).

Gap attack C: prefix-difference packing

In prefix form, define

D
ℓ
	​

={P
i+ℓ
	​

−P
i
	​

:0≤i≤k−ℓ}.

Admissibility says the sets D
1
	​

,…,D
k
	​

 are pairwise disjoint.

For fixed ℓ, D
ℓ
	​

 is strictly increasing. Its size is

∣D
ℓ
	​

∣=k−ℓ+1.

Also every element of D
ℓ
	​

 is a sum of ℓ consecutive a
i
	​

's. Since a
i
	​

≤n,

D
ℓ
	​

⊆[1,ℓn].

This gives

ℓ≤L
∑
	​

∣D
ℓ
	​

∣≤Ln,

hence roughly

Lk≲Ln,

which again gives only k≲n. The disjointness of the D
ℓ
	​

's is not enough by itself.

To improve this, one would need a theorem saying that convexity of the prefix sequence P
i
	​

 forces many overlaps among the D
ℓ
	​

's when k has positive density in n. I did not obtain such a theorem from first principles.

Dependency graph of verified results
Lemma 1: Prefix-difference equivalence

Assumptions:

P
j
	​

=
i=1
∑
j
	​

a
i
	​

.

Conclusion:

S(u,v)=P
v
	​

−P
u−1
	​

.

Admissibility is equivalent to all positive differences P
j
	​

−P
i
	​

 being distinct.

Dependencies: definitions only.

Lemma 2: Trivial counting upper bound

Assumptions:

a
i
	​

≤n,k terms.

Conclusion:

k≤n.

Dependencies: strict increasing positive integers in [1,n].

Lemma 3: Large-shift construction

Assumptions:

Q>k
2
,a
i
	​

=Q+i.

Conclusion:

All interval sums are distinct.

Dependencies: explicit algebraic comparison of interval sums.

Corollary 4: Square-root lower bound

Assumptions:

k
2
+k+1≤n.

Conclusion:

f(n)≥k.

Hence

f(n)≥(1−o(1))
n
	​

.

Dependencies: Lemma 3.

Lemma 5: Small-sum counting obstruction

Assumptions:

a
1
	​

<⋯<a
k
	​

≤n

is admissible.

Conclusion:

For every X,

N(X)≤X.

Dependencies: distinctness of positive integer interval sums.

Lemma 6: Componentwise maximal comparison

Assumptions:

a
1
	​

<⋯<a
k
	​

≤n.

Conclusion:

a
i
	​

≤n−k+i.

Dependencies: strict increase and a
k
	​

≤n.

Corollary 7: Linear-density upper obstruction

Assumptions:

k/n→δ.

Conclusion:

δ≤1−e
−1
.

Dependencies: Lemmas 5 and 6 plus the scaled-area calculation.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100

COMPLETENESS_SCORE: 45/100

ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; 12 strategies scanned; 7 verified lemmas/corollaries generated; 3 main failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

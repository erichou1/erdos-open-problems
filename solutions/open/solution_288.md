# Erdős Problem #288 [unsolved] 25%

---

## ChatGPT Response

Phase 0: Formalization

Let an interval mean a nonempty finite integer interval

I=[a,b]
Z
	​

:={a,a+1,…,b},1≤a≤b.

Define

H([a,b])=
n=a
∑
b
	​

n
1
	​

.

The statement is:

There are finitely many ordered pairs (I
1
	​

,I
2
	​

) such that H(I
1
	​

)+H(I
2
	​

)∈N.
	​


Equivalently, since pairs of intervals are indexed by quadruples (a,b,c,d)∈N
4
 with a≤b, c≤d, the statement is

∃B∈N ∀a≤b, c≤d:H([a,b])+H([c,d])∈N⟹b≤B, d≤B.

The negation is

∀B∈N ∃a≤b, c≤d:max(b,d)>BandH([a,b])+H([c,d])∈N.

The coefficient reformulation is useful. For two intervals I
1
	​

,I
2
	​

, define

m
n
	​

=1
n∈I
1
	​

	​

+1
n∈I
2
	​

	​

∈{0,1,2}.

Then

H(I
1
	​

)+H(I
2
	​

)=
n≥1
∑
	​

n
m
n
	​

	​

,

where only finitely many m
n
	​

 are nonzero. The sequence (m
n
	​

) has a rigid shape: it is the sum of two interval-indicator functions, so its support is either one interval or two intervals, and the value 2 occurs exactly on the overlap I
1
	​

∩I
2
	​

.

Symmetry:

(I
1
	​

,I
2
	​

)↔(I
2
	​

,I
1
	​

)

does not change the sum, so ordered-pair finiteness and unordered-pair finiteness differ only by a factor of at most 2.

Boundary cases:

If both intervals are singletons, say I
1
	​

={a}, I
2
	​

={c}, then

a
1
	​

+
c
1
	​

∈N.

Since 
a
1
	​

+
c
1
	​

≤2, the only possibilities are integer 1 or 2. Directly,

a
1
	​

+
c
1
	​

=2

forces a=c=1, and

a
1
	​

+
c
1
	​

=1

gives

a+c=ac⟺(a−1)(c−1)=1,

so a=c=2. Thus the singleton-singleton solutions are exactly

({1},{1}),({2},{2}).

The given example is

H([3,6])+H([20,20])=
3
1
	​

+
4
1
	​

+
5
1
	​

+
6
1
	​

+
20
1
	​

=1.
Verified theorem pool
Lemma 1: p-adic uniqueness obstruction

Let p be prime and let x
1
	​

,…,x
r
	​

∈Q. Suppose there is a unique index j such that

ν
p
	​

(x
j
	​

)<ν
p
	​

(x
i
	​

)(i

=j),

and suppose also ν
p
	​

(x
j
	​

)<0. Then

x
1
	​

+⋯+x
r
	​

∈
/
Z.

Proof.

Write t=ν
p
	​

(x
j
	​

). Then x
j
	​

=p
t
u, where ν
p
	​

(u)=0. For i

=j, since valuations are integral on Q
×
,

ν
p
	​

(x
i
	​

)≥t+1,

so x
i
	​

=p
t
py
i
	​

 for some y
i
	​

∈Q with ν
p
	​

(y
i
	​

)≥0. Hence

i
∑
	​

x
i
	​

=p
t
	​

u+p
i

=j
∑
	​

y
i
	​

	​

.

The term u has p-adic valuation 0, while p∑y
i
	​

 has valuation at least 1. Therefore the parenthesized expression has valuation 0, so the whole sum has p-adic valuation t<0. An integer cannot have negative p-adic valuation. Therefore the sum is not an integer. ∎

Lemma 2: Necessary local balancing condition

For a candidate solution

n
∑
	​

n
m
n
	​

	​

∈Z,m
n
	​

∈{0,1,2},

define

λ
p
	​

(n)=ν
p
	​

(n)−ν
p
	​

(m
n
	​

)

for each n with m
n
	​


=0. Then for every prime p, the maximum positive value of λ
p
	​

(n) cannot be attained at exactly one n.

Equivalently, if there exists a prime p and a unique n
0
	​

 such that

λ
p
	​

(n
0
	​

)>λ
p
	​

(n)for all n

=n
0
	​


and λ
p
	​

(n
0
	​

)>0, then the reciprocal sum is not an integer.

Proof.

The term m
n
	​

/n has p-adic valuation

ν
p
	​

(
n
m
n
	​

	​

)=ν
p
	​

(m
n
	​

)−ν
p
	​

(n)=−λ
p
	​

(n).

A unique positive maximum of λ
p
	​

(n) is therefore a unique negative minimum of the p-adic valuation of the terms. Lemma 1 applies. ∎

For odd p, since m
n
	​

∈{1,2} and p∤m
n
	​

, this says:

For every odd prime p, the largest ν
p
	​

(n) among supported n must occur at least twice, unless it is 0.
	​


For p=2, coefficient 2 matters:

λ
2
	​

(n)={
ν
2
	​

(n),
ν
2
	​

(n)−1,
	​

m
n
	​

=1,
m
n
	​

=2.
	​


So overlap can cancel one power of 2.

Lemma 3: Single interval harmonic sums

For a single interval I=[a,b], H(I)∈Z if and only if I={1}.

Proof.

If I={1}, then H(I)=1.

If I={a} with a>1, then H(I)=1/a∈
/
Z.

Now assume b>a. Let

r=
a≤n≤b
max
	​

ν
2
	​

(n).

There is a unique n
0
	​

∈[a,b] with ν
2
	​

(n
0
	​

)=r. Indeed, if two distinct integers u<v in the interval had ν
2
	​

(u)=ν
2
	​

(v)=r, then they would be odd multiples of 2
r
. Between two such odd multiples lies an even multiple of 2
r
, hence a multiple of 2
r+1
, contradicting maximality of r.

Thus among the terms 1/n, the term 1/n
0
	​

 has unique minimal 2-adic valuation. By Lemma 1, H(I)∈
/
Z. ∎

Immediate consequence: if one of the intervals is {1}, then the other interval must also be {1}. Indeed,

1+H(I)∈Z⟺H(I)∈Z⟺I={1}.
Lemma 4: Equal-interval case

If I
1
	​

=I
2
	​

=I, then

2H(I)∈Z

only for

I={1},I={2},I=[1,2].

Proof.

Let I=[a,b]. The sum is

2H(I)=
n=a
∑
b
	​

n
2
	​

.

Let r=max
n∈I
	​

ν
2
	​

(n), attained uniquely by the same argument as in Lemma 3. The term 2/n
0
	​

 has 2-adic valuation

ν
2
	​

(2/n
0
	​

)=1−r.

If r≥2, this is negative and uniquely minimal, so Lemma 1 forbids integrality.

Thus r≤1, so the interval contains no multiple of 4. Therefore its length is at most 3.

Check lengths.

Length 1: I={a}. Then 2/a∈Z gives a=1 or a=2.

Length 2: I=[a,a+1]. Then

2H(I)=2(
a
1
	​

+
a+1
1
	​

)=
a(a+1)
2(2a+1)
	​

.

For a=1, this equals 3. For a=2, it equals 5/3. For a≥3, direct evaluation gives a positive noninteger; in particular for a≥4, it is <1, and for a=3, it is 7/6. Hence only a=1.

Length 3: I=[a,a+2]. If a≥4, then

2H(I)≤2(
4
1
	​

+
5
1
	​

+
6
1
	​

)<2,

and direct checking of small a gives

2H([1,3])=
3
11
	​

,2H([2,4])=
6
13
	​

,2H([3,5])=
30
47
	​

.

None is an integer. Therefore the only equal-interval solutions are

I={1},{2},[1,2].

∎

Phase 1: Twelve independent strategies
Strategy	Description	Main obstruction
Direct p-adic proof	Find a prime p with a unique lowest p-adic term.	Known example has perfect local balancing: 3,6 balance p=3, 5,20 balance p=5, 4,20 balance p=2.
Contradiction via maximal endpoint	Let N=max(I
1
	​

∪I
2
	​

); force some prime-power divisor of N to be unmatched.	If every prime-power divisor of N is small, intervals may extend downward enough to match them.
Induction on N	Assume no larger endpoint solutions below N, remove or pair N.	Removing N changes the interval shape and destroys the two-interval structure.
Singleton reduction	Study H([a,b])+1/m∈Z.	This already contains the example and remains resistant to the same local balancing issue.
Denominator analysis	Write H([a,b])=A/D; require another interval to have fractional part −A/D.	Denominators of harmonic intervals have heavy cancellation and are hard to control exactly.
Archimedean bounds	Use log-type estimates for interval sums.	Approximate size does not prevent exact integrality.
Prime-gap obstruction	Any supported odd prime power q>N/2 is fatal.	Need guaranteed prime powers inside arbitrary candidate intervals; this becomes a prime-distribution problem.
Dyadic structure	Use uniqueness of maximal 2-adic valuation.	Overlap coefficient 2 shifts the 2-adic depth by one and can remove the obstruction.
Graph matching	For each prime p, match maximal p-adic-depth terms.	A global contradiction from local matchings is not forced by current lemmas.
Minimal counterexample	Assume a smallest endpoint counterexample to finiteness and derive rigidity.	Minimality does not prevent every local obstruction from being paired.
Compactness/limit argument	If infinitely many exist, rescale endpoints and pass to limiting interval ratios.	Integrality is exact arithmetic; limiting real intervals lose denominator data.
Auxiliary invariant	Invent a rank measuring unmatched prime-power depth.	Rank decreases are not guaranteed under interval overlap.

The highest-value branches are:

p-adic witness branch.

Maximal-endpoint divisor branch.

Singleton-complement branch.

Phase 2: New structures
Definition: support profile

For a pair (I
1
	​

,I
2
	​

), define

S={n:m
n
	​

>0}.

The profile is the finite function

m:S→{1,2}.

The sum is

R(S,m)=
n∈S
∑
	​

n
m
n
	​

	​

.
Definition: p-depth

For each prime p,

d
p
	​

(n)=ν
p
	​

(n)−ν
p
	​

(m
n
	​

).

A term n is p-critical if d
p
	​

(n) is positive and maximal among S.

Lemma 2 says:

Every p-critical level must contain at least two elements.
	​

Definition: local witness

A prime p is a local witness against integrality if the set

{n∈S:d
p
	​

(n)=
t∈S
max
	​

d
p
	​

(t)}

has exactly one element and the maximum is positive.

If a local witness exists, the pair is not a solution.

Thus the main finiteness statement would follow from the following stronger statement:

∃B ∀(I
1
	​

,I
2
	​

), maxS>B⟹there exists a local witness.

This is a genuine reduction but not a proof. It is the main unresolved gap.

Call this statement W.

Phase 3: Parallel exploration
Branch A: Prove the local witness theorem W

Target:

∃B ∀(I
1
	​

,I
2
	​

), maxS>B⟹∃p local witness.

Verified progress:

If q=p
r
 is an odd prime power and q>N/2, where N=maxS, then any supported multiple of q is exactly q. Hence if q∈S, then q is uniquely p-critical, so integrality is impossible.

Therefore:

A solution cannot contain an odd prime power q>N/2.
	​


More generally, if an odd prime power q=p
r
 divides some supported n, and no other supported integer is divisible by q, then the pair is impossible.

Obstacle:

This does not force a contradiction unless one proves that every sufficiently large two-interval support must contain such an unmatched odd prime power. Current deductions do not establish that.

GAP_NODE A:

Every sufficiently large two-interval support contains an unmatched odd prime power.

Attacks tried:

Use the largest endpoint N.
Failure: N may have only small prime-power divisors.

Use primes in the top interval.
Failure: no first-principles guarantee here that the top interval contains a prime-power witness.

Use all prime factors of all endpoints.
Failure: every such divisor can in principle be matched elsewhere.

Use 2-adic depth.
Failure: coefficient 2 on overlaps can shift the obstruction.

Status: unresolved.

Branch B: Maximal endpoint divisor matching

Let

N=maxS.

Suppose N∈S. If the pair is a solution, then for every odd prime power p
r
∥N that gives maximal p-adic depth, there must be another supported m

=N divisible by p
r
.

Thus every maximal odd prime-power divisor of N must be “shadowed” by a second supported multiple.

If p
r
>N/2, this is impossible. Therefore every odd prime-power divisor of N that is maximal in the support must satisfy

p
r
≤N/2.

This implies that any large endpoint N in a solution must be arithmetically non-isolated: its large prime-power divisors must already occur elsewhere in the two intervals.

Obstacle:

Numbers such as highly composite or smooth integers can have all prime-power divisors small. The argument gives strong restrictions on N, but not a bound for N.

GAP_NODE B:

Show that no arbitrarily large N can satisfy all required divisor-shadowing conditions inside two intervals.

Attacks:

Product of required shadows.
Failure: one shadow can match several prime powers.

Distance lower bounds.
If m<N and p
r
∣m,N, then N−m is a positive multiple of p
r
, so m≤N−p
r
.
Failure: if all p
r
 are small, this gives weak distance.

Two-interval geometry.
Since there are only two intervals, perhaps many shadows must lie in the same interval.
Failure: current counting does not exceed available interval capacity.

Endpoint overlap.
If N lies in the overlap, m
N
	​

=2, helping only at p=2.
Failure: odd prime conditions remain but still may be matched.

Status: unresolved.

Branch C: Singleton-complement branch

Assume

I
2
	​

={m}.

Then the condition is

H([a,b])+
m
1
	​

=k∈N.

Equivalently,

H([a,b])=k−
m
1
	​

.

If H([a,b])<1, then necessarily k=1, so

H([a,b])=1−
m
1
	​

=
m
m−1
	​

.

The example is

H([3,6])=
20
19
	​

.

Thus the singleton case asks when a harmonic interval has fractional complement exactly one reciprocal.

Verified obstruction:

For every odd prime p, the maximal p-adic order among

[a,b]∪{m}

must occur at least twice.

For p=2, if m∈[a,b], then the coefficient of 1/m is 2, shifting the 2-adic depth of m downward by 1. If m∈
/
[a,b], no such shift occurs.

Obstacle:

The singleton m can serve as a simultaneous shadow for multiple prime powers in the interval. In the example, m=20 simultaneously balances the 2
2
-depth of 4 and the 5-depth of 5.

GAP_NODE C:

Show that only finitely many intervals [a,b] have H([a,b]) equal to an integer minus one reciprocal.

Attacks:

Denominator of H([a,b]).
Failure: cancellation can make the denominator much smaller than lcm(a,…,b).

Unique 2-adic maximum.
Failure: m can match the maximum, as 20 matches 4.

Odd prime maximum.
Failure: m can match odd prime powers too.

Size estimate.
Failure: H([a,b])≈log(b/a) does not control exact fractional complement.

Status: unresolved.

Phase 4: Referee attack on the strongest available route

The strongest route is:

large solution⟹large two-interval support⟹local p-adic witness⟹nonintegrality.

The final implication is proved by Lemma 1.

The unresolved implication is:

large two-interval support⟹local p-adic witness.

Adversarial counterpressure:

The example

[3,6]+{20}

shows that local witness hunting can fail in a nontrivial way:

For p=2, the maximal depth is shared by 4 and 20.

For p=3, the maximal depth is shared by 3 and 6.

For p=5, the maximal depth is shared by 5 and 20.

Thus a solution can build a small matching network among denominators. Any proof must show that such matching networks cannot persist at arbitrarily large scale.

No current deduction proves that.

Formal dependency graph

Verified:

Lemma 1⇒Lemma 2⇒local necessary conditions.

Verified:

Lemma 1+unique maximal 2-adic valuation on one interval⇒Lemma 3.

Verified:

Lemma 2+short case checking⇒Lemma 4.

Unresolved:

W:∃B ∀(I
1
	​

,I
2
	​

), maxS>B⟹∃p local witness.

If W were proved, the original statement would follow immediately. But W itself remains unproved here.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 95/100 for the verified lemmas above.

COMPLETENESS_SCORE: 25/100 for the original problem.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the local p-adic obstruction; 35/100 for the attempted global finiteness route.

RESOURCE_USAGE: approximately 100% of this response’s reasoning budget; 3 main branches explored; 4 verified lemmas generated; 3 major unresolved gap nodes identified.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

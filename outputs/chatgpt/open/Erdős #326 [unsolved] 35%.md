# Erdős Problem #326 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.

The target statement is

∃c>0 ∀n≥2 ∀k∈{1,…,n−1} ∃d∈Z
>0
	​


such that

d∣B(n,k),cn<d≤n.

By symmetry,

(
k
n
	​

)=(
n−k
n
	​

),

it is enough to consider

1≤k≤n/2.

The negation is

∀c>0 ∃n≥2 ∃k∈[1,n−1] ∀d∣(
k
n
	​

),
d≤n⟹d≤cn.

Equivalently, if

M(n,k)=max{d:d∣(
k
n
	​

), d≤n},

then the negation is

1≤k<n
inf
	​

n
M(n,k)
	​

=0.

So the problem is exactly to decide whether

1≤k<n
inf
	​

n
1
	​

d∣(
k
n
	​

)
d≤n
	​

max
	​

d

is positive.

Basic verified lemmas
Lemma 1: symmetry reduction

Because

(
k
n
	​

)=(
n−k
n
	​

),

it suffices to prove the claim for

1≤k≤n/2.

No information is lost.

Lemma 2: a universal divisor from n

For all 1≤k<n,

gcd(n,k)
n
	​

∣(
k
n
	​

).

Proof.

Let g=gcd(n,k), n=gn
0
	​

, k=gk
0
	​

, so gcd(n
0
	​

,k
0
	​

)=1. From

(
k
n
	​

)=
k
n
	​

(
k−1
n−1
	​

)

we get

k(
k
n
	​

)=n(
k−1
n−1
	​

).

Dividing by g,

k
0
	​

(
k
n
	​

)=n
0
	​

(
k−1
n−1
	​

).

Since gcd(k
0
	​

,n
0
	​

)=1, we have

k
0
	​

∣(
k−1
n−1
	​

).

Thus for some integer E,

(
k−1
n−1
	​

)=k
0
	​

E.

Therefore

(
k
n
	​

)=
gk
0
	​

gn
0
	​

	​

⋅k
0
	​

E=n
0
	​

E.

Hence

gcd(n,k)
n
	​

=n
0
	​

∣(
k
n
	​

).

This gives

M(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

So the problem is already solved in the range k≤C, with constant 1/C. The unresolved difficulty is the regime

k→∞,k=o(n).
Lemma 3: quotient-divisor family

For every 1≤j≤k,

D
j
	​

(n,k):=
gcd((
j
n
	​

),(
j
k
	​

))
(
j
n
	​

)
	​


divides

(
k
n
	​

).

Proof.

Use the identity

(
k
n
	​

)(
j
k
	​

)=(
j
n
	​

)(
k−j
n−j
	​

).

Let

A=(
j
n
	​

),B=(
j
k
	​

),g=gcd(A,B).

Then

A∣(
k
n
	​

)B.

Write A=gA
0
	​

, B=gB
0
	​

, with gcd(A
0
	​

,B
0
	​

)=1. Then

gA
0
	​

∣(
k
n
	​

)⋅gB
0
	​

,

so

A
0
	​

∣(
k
n
	​

)B
0
	​

.

Since gcd(A
0
	​

,B
0
	​

)=1,

A
0
	​

∣(
k
n
	​

).

Thus

D
j
	​

(n,k)=A
0
	​

∣(
k
n
	​

).

Also,

D
j
	​

(n,k)≥
(
j
k
	​

)
(
j
n
	​

)
	​

=
i=0
∏
j−1
	​

k−i
n−i
	​

≥(
k
n
	​

)
j
.

This creates many divisors of (
k
n
	​

), but it does not by itself guarantee one in (cn,n], because the divisors D
j
	​

 may jump from far below n to far above n.

This is the first central obstruction.

Main hard regime

After Lemma 2, small k is handled.

After any theorem giving a prime divisor >k, the range k≥cn would be handled, because a prime divisor p>k≥cn would itself lie in (cn,n].

Thus the essential unresolved region is

1≪k≪n.

In that range:

gcd(n,k)
n
	​

≥
k
n
	​


is too small compared to n, while a divisor merely >k is also too small compared to n.

So one needs either:

many medium divisors combine to size ≍n,

or

one large composite divisor survives denominator cancellation.
Twelve strategy scan

Direct divisor from n.
Gives n/gcd(n,k)∣(
k
n
	​

).
Works for bounded k.
Fails for k→∞.

Large-prime strategy.
Try to force a prime divisor p>cn.
Works if a numerator term contains a prime >cn not cancelled by k!.
Fails for short intervals (n−k,n] when k=o(n).

Prime >k strategy.
A divisor >k would help only when k≫n.
Fails in k=o(n).

Use D
j
	​

(n,k).
We have many divisors

D
j
	​

(n,k)∣(
k
n
	​

).

Lower bound

D
j
	​

(n,k)≥(n/k)
j
.

Promising, but jumps are uncontrolled.

Lattice-of-divisors strategy.
Let L
j
	​

=lcm(D
1
	​

,…,D
j
	​

).
Then L
j
	​

∣(
k
n
	​

).
Need prove some divisor of some L
j
	​

 lands in (cn,n].
Gap: no uniform divisor-density theorem proved for these L
j
	​

.

Greedy prime-packing.
Factor (
k
n
	​

), multiply prime factors until crossing cn.
If the crossing product remains ≤n, done.
Gap: a large prime factor may cause a jump over n.

Minimal divisor above n.
Let m be the smallest divisor of (
k
n
	​

) exceeding n.
Then m/p≤n for every prime p∣m.
To prove m/p>cn, one needs p<1/c, impossible uniformly.

Smoothness obstruction search.
Try to construct n,k such that every divisor ≤n is o(n).
This would require divisor sparsity similar to high powers of primes.
No construction derived from binomial structure.

Induction on k.
Use

(
k
n
	​

)=
k
n
	​

(
k−1
n−1
	​

).

Lemma 2 follows, but induction does not preserve the desired divisor interval.

Induction on n.
Pascal identity gives additive, not multiplicative, control:

(
k
n
	​

)=(
k
n−1
	​

)+(
k−1
n−1
	​

).

Divisibility is not inherited.

Contradiction via maximal divisor M(n,k).
Assume M(n,k)≤cn.
Then all divisors ≤n are small.
Need force a divisor in (cn,n] from known divisors D
j
	​

.
Gap remains divisor-density.

Counterexample construction by CRT.
Try to make each numerator term n−k+i highly divisible by denominator factors.
CRT can force many cancellations, but it also often creates individual large quotients near n.
No counterexample obtained.

Top three viable branches were:

D
j
	​

-divisor family,prime-packing,counterexample construction.
Branch A: D
j
	​

-divisor family

We have verified:

D
j
	​

(n,k)∣(
k
n
	​

),

and

D
j
	​

(n,k)≥(
k
n
	​

)
j
.

Let

R=
k
n
	​

.

In the hard range 1≪k≪n, we have R→∞. Choosing

j≈
logR
logn
	​


forces

D
j
	​

(n,k)≳n.

If one could prove that some divisor of D
j
	​

(n,k) lies in (cn,n], the problem would be solved.

But this requires a uniform divisor-density statement for numbers of the form

gcd((
j
n
	​

),(
j
k
	​

))
(
j
n
	​

)
	​

.

No proof was obtained.

Gap node A

Prove:

∃c>0 ∀n,k,j,D
j
	​

(n,k)>n⟹∃d∣D
j
	​

(n,k), cn<d≤n.

This is false for arbitrary integers D
j
	​

, so the special binomial-quotient structure is essential. I did not derive enough structure to prove it.

Branch B: prime-packing

Let

(
k
n
	​

)=
i
∏
	​

p
i
	​


with primes repeated according to multiplicity.

If there is a prime factor

p
i
	​

>cn,

then done.

Otherwise all prime factors are ≤cn. Greedily multiplying small prime factors can produce a divisor above cn, but it may exceed n. To control this, one needs either:

p
i
	​

≤C

for the crossing prime, or a way to replace the jump by another combination.

No such uniform replacement argument was obtained.

Gap node B

Prove a divisor-packing lemma specific to binomial coefficients:

(
k
n
	​

) has enough small and medium prime factors to pack a divisor into (cn,n].

I could prove neither this nor its negation.

Branch C: counterexample search

To disprove the statement, one would need a sequence (n
r
	​

,k
r
	​

) such that

n
r
	​

M(n
r
	​

,k
r
	​

)
	​

→0.

The strongest immediate obstruction to such a construction is Lemma 2:

M(n,k)≥
gcd(n,k)
n
	​

.

Thus any counterexample sequence must have

gcd(n
r
	​

,k
r
	​

)→∞.

Since gcd(n,k)≤k, one also needs

k
r
	​

→∞.

Additionally, if one has any surviving large prime divisor p≫n, impossible because every prime divisor of (
k
n
	​

) is at most n; but if p≫cn, then the desired divisor already exists. Therefore a counterexample must avoid all prime divisors in (cn,n] and must also prevent composite products from landing there.

This requires extreme divisor sparsity.

No explicit construction was obtained.

Verified partial theorem

For every fixed K≥1, if

1≤k≤K,

then

(
k
n
	​

)

has a divisor d≤n satisfying

d≥
K
n
	​

.

Indeed,

d=
gcd(n,k)
n
	​


works because

gcd(n,k)≤k≤K.

Thus the original statement is verified for bounded k, with constant 1/K.

Also, any theorem proving that (
k
n
	​

) has a prime divisor >k would verify the original statement in the proportional regime

k≥cn.

The unresolved core is precisely

K≪k≪n.
Dependency graph

Verified:

(
k
n
	​

)=(
n−k
n
	​

)
gcd(n,k)
n
	​

∣(
k
n
	​

)
D
j
	​

(n,k)=
gcd((
j
n
	​

),(
j
k
	​

))
(
j
n
	​

)
	​

∣(
k
n
	​

)
D
j
	​

(n,k)≥(n/k)
j

Unresolved:

D
j
	​

(n,k)>n⇒∃d∣D
j
	​

(n,k), cn<d≤n.

Unresolved:

(
k
n
	​

) has uniformly dense enough divisors below n.

Unresolved:

∃(n
r
	​

,k
r
	​

) with M(n
r
	​

,k
r
	​

)/n
r
	​

→0.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 91/100 for the verified lemmas; no proof of the original statement was obtained.

COMPLETENESS_SCORE: 35/100.

ADVERSARIAL_SURVIVAL_SCORE: 82/100 for the partial results; 0/100 for the unresolved main claim.

RESOURCE_USAGE: approximately 100% of available reasoning budget; 3 main branches explored; 4 verified lemmas generated; 3 failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

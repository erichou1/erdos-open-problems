# Erdős Problem #329 [unsolved] 35%

---

## ChatGPT Response

Formal statement.

Let

B(n,k)=(
k
n
	​

),1≤k<n.

The target assertion is:

∃c>0 ∀n∈Z
≥2
	​

 ∀k∈{1,…,n−1} ∃d∈Z
≥1
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

so it is enough to consider

1≤k≤n/2.

Negation:

∀c>0 ∃n>k≥1

such that every divisor d∣(
k
n
	​

) with d≤n satisfies

d≤cn.

Equivalently, if

D(n,k)=max{d:d∣(
k
n
	​

), d≤n},

the target is

1≤k<n
inf
	​

n
D(n,k)
	​

>0.

A complete proof would need a uniform lower bound for D(n,k)/n.

Several verified divisibility facts follow from first principles.

First,

k(
k
n
	​

)=n(
k−1
n−1
	​

).

Let g=gcd(n,k). Then

g
n
	​

∣(
k
n
	​

).

Indeed, writing n=gn
0
	​

, k=gk
0
	​

, with gcd(n
0
	​

,k
0
	​

)=1, the identity gives

gk
0
	​

(
k
n
	​

)=gn
0
	​

(
k−1
n−1
	​

),

hence

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

)=1, we get n
0
	​

∣(
k
n
	​

). Thus

gcd(n,k)
n
	​

∣(
k
n
	​

).

This proves the desired statement whenever gcd(n,k) is bounded. In particular, for fixed K, all k≤K are handled with c=1/K, because

gcd(n,k)
n
	​

≥
k
n
	​

≥
K
n
	​

.

Second, for any subset S⊆{0,1,…,k−1}, define

P
S
	​

=
i∈S
∏
	​

(n−i).

Then

gcd(P
S
	​

,k!)
P
S
	​

	​

∣(
k
n
	​

).

Proof: write

(
k
n
	​

)=
k!
P
S
	​

P
S
c
	​

	​

.

Let h=gcd(P
S
	​

,k!), so P
S
	​

=hP
S
′
	​

, k!=hk
′
, and gcd(P
S
′
	​

,k
′
)=1. Since (
k
n
	​

) is an integer,

k
′
∣P
S
′
	​

P
S
c
	​

.

Because gcd(P
S
′
	​

,k
′
)=1, it follows that

k
′
∣P
S
c
	​

.

Therefore

(
k
n
	​

)=P
S
′
	​

⋅
k
′
P
S
c
	​

	​

,

so

P
S
′
	​

=
gcd(P
S
	​

,k!)
P
S
	​

	​

∣(
k
n
	​

).

The one-element case gives

gcd(n−i,k!)
n−i
	​

∣(
k
n
	​

).

Since k≤n/2, each n−i≥n−k+1>n/2. Thus, if for some i,

gcd(n−i,k!)≤H,

then

(
k
n
	​

)

has a divisor at least

H
n/2
	​

=
2H
n
	​

.

So the problem would follow from a uniform bound on

0≤i<k
min
	​

gcd(n−i,k!),

but that bound is false in this naive form. For example, one can arrange intervals of length k in which every member shares a nontrivial factor with k!. Thus this line alone does not solve the problem.

Third, if there is a prime p such that

n−k<p≤n

and

p>k,

then p∣(
k
n
	​

). This is because p divides exactly one numerator factor in

(
k
n
	​

)=
k!
n(n−1)⋯(n−k+1)
	​

,

and p∤k!. Since k≤n/2, every prime p>n−k automatically satisfies p>k. Therefore, a prime in (n−k,n] gives a divisor close to n.

This handles many cases, but not all: for small or moderately growing k, the interval (n−k,n] may contain no prime.

I explored the following independent strategies.

Direct use of n/gcd(n,k).
Works when gcd(n,k) is uniformly bounded. Fails when n and k have large common divisor.

Single numerator factor after cancellation by k!.
Gives divisors

gcd(n−i,k!)
n−i
	​

.

Works if some top factor has small gcd with k!. Fails because all top factors may share moderately large factors with k!.

Subset-product divisors.
For every S,

gcd(∏
i∈S
	​

(n−i),k!)
∏
i∈S
	​

(n−i)
	​

∣(
k
n
	​

).

This is strong, but I did not obtain a uniform method for selecting S so that the resulting divisor lands in (cn,n].

Prime in the top interval.
If (n−k,n] contains a prime, we are done with a very strong divisor. This fails for prime gaps or constructed composite runs.

Minimal divisor above n.
If an integer M has a divisor above n, take the least such divisor and divide by a prime factor. This gives some divisor below n, but the lower bound can collapse to O(
n
	​

), not cn. So it is insufficient.

General divisor-density lemma.
A possible route is to prove that the divisor set of (
k
n
	​

) is multiplicatively dense near n. I could not prove this from the available first-principles tools.

Induction on k.
The recurrence

(
k
n
	​

)=
k
n−k+1
	​

(
k−1
n
	​

)

does not preserve divisibility of large divisors in a controllable way.

Induction on n.
Pascal’s identity gives addition, not divisibility, so it does not directly preserve divisor information.

Reduction by g=gcd(n,k).
The divisor n/g is always present. One would like to multiply it by a divisor of the quotient (
k
n
	​

)/(n/g) lying near g, but I did not prove such a quotient-divisor theorem.

Cyclic group action.
A cyclic action on k-subsets gives the divisor n/gcd(n,k), but I did not extract stronger divisibility near n.

p-adic valuation approach.
Legendre-type valuations might allow construction of a divisor near n, but I did not complete a uniform selection argument for prime powers.

Counterexample search.
The negation would require constructing infinitely many (n,k) for which all divisors ≤n are o(n). The obvious constructions with long composite intervals do not suffice because composite residual factors can combine to form large divisors.

The main unresolved gap became:

GAP:

Given the verified family of divisors

gcd(P
S
	​

,k!)
P
S
	​

	​

∣(
k
n
	​

),

prove or disprove that for some absolute c>0, at least one such divisor, or one divisor generated from them, lies in

(cn,n].

I attacked this gap by attempting:

S={i},∣S∣=2,∣S∣=r,

minimal crossing arguments, prime-factor extraction, and gcd-distribution estimates. Each approach either proved only special cases or reduced to another unproved uniform divisor-density statement.

I did not obtain a complete proof or a complete disproof.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the stated divisibility lemmas; 0 for a complete solution of the original problem.

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 85 for the verified lemmas; incomplete for the global theorem.

RESOURCE_USAGE: approximately 100% of the available reasoning budget; 12 strategies explored; 3 main lemmas generated; several failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

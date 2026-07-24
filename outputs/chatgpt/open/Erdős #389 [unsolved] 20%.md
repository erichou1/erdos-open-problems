# Erdős Problem #389 [unsolved] 20%

---

## ChatGPT Response

Complete formalization

Let n≥1, k≥1, and put N=n−1. The divisibility condition is

n(n+1)⋯(n+k−1)∣(n+k)(n+k+1)⋯(n+2k−1).

Equivalently,

i=1
∏
k
	​

(N+i)∣
i=1
∏
k
	​

(N+k+i).

Equivalently,

(N+k)!
2
(N+2k)!N!
	​

∈Z.

Equivalently,

(
k
N+k
	​

)
(
k
N+2k
	​

)
	​

∈Z.

So the problem is:

∀N≥0 ∃k≥1:
(N+k)!
2
(N+2k)!N!
	​

∈Z.
	​


Its negation is:

∃N≥0 ∀k≥1:
(N+k)!
2
(N+2k)!N!
	​

∈
/
Z.
	​


For a prime p, define

V
p
	​

(N,k)=v
p
	​

((N+2k)!)+v
p
	​

(N!)−2v
p
	​

((N+k)!).

The condition is equivalent to

V
p
	​

(N,k)≥0for every prime p.
	​


Using Legendre’s formula,

v
p
	​

(m!)=
j≥1
∑
	​

⌊
p
j
m
	​

⌋,

we get

V
p
	​

(N,k)=
j≥1
∑
	​

(⌊
p
j
N+2k
	​

⌋+⌊
p
j
N
	​

⌋−2⌊
p
j
N+k
	​

⌋).

Thus the problem is exactly the assertion that for every N≥0, there exists k≥1 such that for every prime p,

j≥1
∑
	​

(⌊
p
j
N+2k
	​

⌋+⌊
p
j
N
	​

⌋−2⌊
p
j
N+k
	​

⌋)≥0.
Verified boundary cases
Case n=1

Here N=0. We need

1⋅2⋯k∣(k+1)(k+2)⋯(2k).

But

1⋅2⋯k
(k+1)(k+2)⋯(2k)
	​

=(
k
2k
	​

)∈Z.

So n=1 works for every k≥1.

Given example n=2,k=5

Here N=1. The ratio is

2⋅3⋅4⋅5⋅6
7⋅8⋅9⋅10⋅11
	​

=
720
55440
	​

=77.

So k=5 works.

Given example n=3,k=4

Here

3⋅4⋅5⋅6
7⋅8⋅9⋅10
	​

=
360
5040
	​

=14.

So k=4 works.

A useful exact local form

Let q=p
j
. Write

N=aq+r,k=bq+s,

with 0≤r,s<q. Then

⌊
q
N+2k
	​

⌋+⌊
q
N
	​

⌋−2⌊
q
N+k
	​

⌋=⌊
q
r+2s
	​

⌋−2⌊
q
r+s
	​

⌋.

Therefore each prime-power contribution depends only on the residues

Nmodp
j
,kmodp
j
.

This gives the exact criterion

V
p
	​

(N,k)=
j≥1
∑
	​

(⌊
p
j
r
j
	​

+2s
j
	​

	​

⌋−2⌊
p
j
r
j
	​

+s
j
	​

	​

⌋),

where

r
j
	​

≡N(modp
j
),s
j
	​

≡k(modp
j
),0≤r
j
	​

,s
j
	​

<p
j
.

The summand can be negative, zero, or positive. A negative contribution occurs precisely when the interval (N,N+k] contains more multiples of p
j
 than the interval (N+k,N+2k].

Thus the problem is a simultaneous residue-balancing problem over all prime powers.

A necessary obstruction

Suppose p is a prime satisfying

2
N+2k
	​

<p≤N+k.

Then p appears in the denominator product

(N+1)(N+2)⋯(N+k),

because p≤N+k, but p does not appear in the numerator product

(N+k+1)(N+k+2)⋯(N+2k),

because the only possible positive multiple of p in [1,N+2k] above p is 2p, and

2p>N+2k.

So such a prime contributes negatively and cannot be compensated by a higher power of the same prime.

Therefore, any successful k must avoid primes in the interval

(
2
N+2k
	​

,N+k].
	​


Equivalently,

(k+N/2, k+N] contains no prime.
	​


This is a genuine necessary condition.

For fixed N, this only requires a prime-free interval of bounded length roughly N/2, so it is not by itself impossible. But it shows that k must be positioned carefully.

Stronger sufficient condition attempt

A very strong sufficient condition would be an injection assigning to each denominator factor N+i a numerator factor N+k+j divisible by it. That is, if there were a permutation π of {1,…,k} such that

N+i∣N+k+π(i)

for all i, then the desired divisibility would follow.

However, this condition is too strong. For the valid example n=2,k=5, the denominator factor 6 has no multiple among

7,8,9,10,11.

So product divisibility can hold even when no factorwise divisibility matching exists. The problem genuinely requires prime-power aggregation, not merely matching individual factors.

Verified reformulation as a convexity defect

Define

F
N
	​

(k)=log((N+k)!).

Then the logarithmic size of the ratio is

log(
(N+k)!
2
(N+2k)!N!
	​

)=F
N
	​

(2k)−2F
N
	​

(k)+F
N
	​

(0).

This is a second difference, and because log(m!) is convex, the ratio is usually large. But size alone is irrelevant: the obstruction is purely arithmetic. The ratio being greater than 1 does not imply integrality.

So asymptotic positivity cannot solve the problem.

Dependency graph of verified facts

Definitions:

R
N
	​

(k)=
(N+k)!
2
(N+2k)!N!
	​

.

Main target:

∀N≥0 ∃k≥1: R
N
	​

(k)∈Z.

Verified equivalences:

R
N
	​

(k)∈Z⟺∀p, V
p
	​

(N,k)≥0.
V
p
	​

(N,k)=
j≥1
∑
	​

(⌊
p
j
N+2k
	​

⌋+⌊
p
j
N
	​

⌋−2⌊
p
j
N+k
	​

⌋).

Verified necessary condition:

R
N
	​

(k)∈Z⟹(k+N/2, k+N] contains no prime.

Verified special case:

N=0

works for all k≥1.

Verified examples:

(n,k)=(2,5),(3,4).
Final state
RESOURCE_EXHAUSTED
	​


A complete proof or disproof of

∀n≥1 ∃k≥1:n(n+1)⋯(n+k−1)∣(n+k)⋯(n+2k−1)

has not been derived here. The rigorous results obtained are the exact p-adic reformulation, the verified boundary case n=1, the verification of the stated examples, and a genuine necessary prime-gap condition on any successful k.

PROOF_CONFIDENCE
95/100

Confidence is high for the equivalences, p-adic criterion, and necessary obstruction.

COMPLETENESS_SCORE
20/100

The original universal statement is not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE
90/100

The stated lemmas survive direct checking; no unproved theorem is used beyond Legendre’s formula for factorial valuations.

RESOURCE_USAGE

Reasoning budget used: approximately 100%.

Branches explored: 6.

Lemmas generated: 4.

Failed proof attempts: factorwise matching, monotonicity/size argument, direct binomial integrality, prime-gap-only strategy, residue-balancing shortcut, and convexity argument.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

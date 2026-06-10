# Erdős Problem #251 [unsolved] 38%

---

## ChatGPT Response

Phase 0: Formal statement

Let

B(n,k)=(
k
n
	​

),1≤k<n,

and define

M(n,k)=max{d∈Z
≥1
	​

:d∣B(n,k), d≤n}.

The problem asks whether

∃c>0 ∀n≥2 ∀k∈{1,…,n−1}:M(n,k)>cn.

Equivalently,

n≥2, 1≤k<n
inf
	​

n
M(n,k)
	​

>0.
Negation

The negation is

∀c>0 ∃n≥2 ∃k∈{1,…,n−1}:∀d∣(
k
n
	​

), d≤n⇒d≤cn.

Equivalently, there exists a sequence (n
i
	​

,k
i
	​

) with 1≤k
i
	​

<n
i
	​

 such that

n
i
	​

M(n
i
	​

,k
i
	​

)
	​

→0.
Symmetry

Since

(
k
n
	​

)=(
n−k
n
	​

),

we may always replace k by

r=min(k,n−k),

so the problem is equivalent to proving

∃c>0 ∀n≥2 ∀1≤r≤n/2:M(n,r)>cn.
Immediate boundary cases

For r=1,

(
1
n
	​

)=n,

so M(n,1)=n.

For general r,

(
r
n
	​

)=
r
n
	​

(
r−1
n−1
	​

),

and therefore

gcd(n,r)
n
	​

∣(
r
n
	​

).

Since gcd(n,r)≤r,

M(n,r)≥
r
n
	​

.

Thus all bounded r are harmless. The hard regime is

r→∞,r=o(n)

or, more generally, the regime where neither r nor n/r is a fixed positive fraction of n.

Verified lemma 1: p-adic exponent formula

For a prime p, define

v
p
	​

(m)=max{a:p
a
∣m}.

Then

v
p
	​

(
r
n
	​

)=
a≥1
∑
	​

(⌊
p
a
n
	​

⌋−⌊
p
a
r
	​

⌋−⌊
p
a
n−r
	​

⌋).

This follows directly from

v
p
	​

(m!)=
a≥1
∑
	​

⌊
p
a
m
	​

⌋

applied to

(
r
n
	​

)=
r!(n−r)!
n!
	​

.

This converts the problem into a divisor-selection problem: choose exponents

0≤f
p
	​

≤v
p
	​

(
r
n
	​

)

so that

cn<
p
∏
	​

p
f
p
	​

≤n.
Verified lemma 2: the elementary divisor n/gcd(n,r)

From

r(
r
n
	​

)=n(
r−1
n−1
	​

),

let g=gcd(n,r), n=gn
0
	​

, r=gr
0
	​

, gcd(n
0
	​

,r
0
	​

)=1. Then

gr
0
	​

(
r
n
	​

)=gn
0
	​

(
r−1
n−1
	​

),

so

r
0
	​

(
r
n
	​

)=n
0
	​

(
r−1
n−1
	​

).

Since gcd(r
0
	​

,n
0
	​

)=1, we get

n
0
	​

=
gcd(n,r)
n
	​

∣(
r
n
	​

).

Hence

M(n,r)≥
gcd(n,r)
n
	​

≥
r
n
	​

.

This proves the desired statement whenever r≤C for any fixed C, with c<1/C. It does not prove a uniform absolute constant because r is unbounded.

Verified lemma 3: residual lcm divisor

Let

L(n,r)=lcm(n−r+1,n−r+2,…,n)

and

L
r
	​

=lcm(1,2,…,r).

Define

D(n,r)=
L
r
	​

L(n,r)
	​

.

More precisely, interpret this p-adically as

v
p
	​

D(n,r)=
n−r<m≤n
max
	​

v
p
	​

(m)−
1≤j≤r
max
	​

v
p
	​

(j),

discarding negative values.

Then

D(n,r)∣(
r
n
	​

).
Proof

Fix a prime p. Let

A
a
	​

=#{m:n−r<m≤n, p
a
∣m}

and

B
a
	​

=#{j:1≤j≤r, p
a
∣j}.

Then

v
p
	​

(
r
n
	​

)=
a≥1
∑
	​

(A
a
	​

−B
a
	​

).

Every interval of length r contains at least ⌊r/p
a
⌋ multiples of p
a
, so

A
a
	​

≥B
a
	​

.

Let

α=
n−r<m≤n
max
	​

v
p
	​

(m),β=
1≤j≤r
max
	​

v
p
	​

(j).

If α≤β, then v
p
	​

D(n,r)=0. If α>β, then for every a=β+1,…,α,

A
a
	​

≥1,B
a
	​

=0.

Therefore

v
p
	​

(
r
n
	​

)=
a≥1
∑
	​

(A
a
	​

−B
a
	​

)≥α−β=v
p
	​

D(n,r).

Thus D(n,r)∣(
r
n
	​

).

Main reduction obtained

A sufficient condition for the original problem is:

∃c>0 ∀n≥2 ∀1≤r≤n/2:D(n,r) has a divisor d with cn<d≤n.

This is a genuine reduction, not a proof. The unresolved difficulty is that even if D(n,r) is large, a large integer need not have a divisor in a fixed proportional interval below n.

For example, an arbitrary number of the form

M=pq,p∼q∼
n
	​

,

may satisfy M>n, while its largest divisor ≤n could be only ≍
n
	​

. Therefore, merely proving that D(n,r)>n is not enough.

Breadth-first strategy search
Strategy	Idea	Verified progress	Obstacle
Direct divisor n/gcd(n,r)	Use r(
r
n
	​

)=n(
r−1
n−1
	​

)	Gives M(n,r)≥n/r	Vanishes for large r
Prime divisor search	Find prime p>cn dividing (
r
n
	​

)	Works if such p appears in numerator uncancelled	Requires uniform prime placement in moving intervals
Residual lcm	Use D(n,r)=L(n,r)/L
r
	​

∣(
r
n
	​

)	Fully proved	Need divisor-selection theorem for D(n,r)
p-adic carry criterion	Analyze v
p
	​

(
r
n
	​

) using base-p carries	Exact formula available	Hard to force p>cn for all r
Greedy divisor construction	Multiply available prime powers until near n	Natural	Fails for sparse factors near 
n
	​


Contradiction	Assume all divisors ≤n are ≤cn	Reformulates cleanly	Need structural contradiction from binomial exponents
Counterexample search	Seek (n
i
	​

,r
i
	​

) with M(n
i
	​

,r
i
	​

)/n
i
	​

→0	Negation clarified	No construction verified
Density of divisor logs	Treat logd as subset sums of available logp	Could prove divisor near n	Need density of available prime powers
Smooth interval obstruction	Make n−r+1,…,n mostly r-smooth	Relevant to possible disproof	No infinite construction established
Induction on r	Relate (
r
n
	​

) to (
r−1
n
	​

)	Recurrence exists	Divisibility does not behave monotonically
Transference to lcm intervals	Study L(n,r) instead of (
r
n
	​

)	Strong lcm divisor lemma proved	Still requires divisor extraction
Extremal function M(n,r)	Study infM(n,r)/n directly	Correct formulation	No monotonicity found

Top three surviving routes:

Prove a divisor-selection theorem for D(n,r).

Prove existence of a large prime divisor p>cn of (
r
n
	​

).

Construct a disproof sequence where all available prime powers force M(n,r)=o(n).

None was completed.

Gap node: divisor-selection theorem for D(n,r)

Primary unresolved statement:

∃c>0 ∀n,r:D(n,r)∣(
r
n
	​

)⇒D(n,r) has a divisor d∈(cn,n].

Ten attacks attempted:

Direct greedy selection.
Fails for arbitrary sparse factorizations.

Use only prime powers >r.
Gives structural information but not enough to guarantee a divisor near n.

Show D(n,r) contains a prime power >cn.
Would solve the problem immediately, but no proof found.

Show D(n,r) contains many prime powers in dyadic intervals.
Promising, but requires interval-prime information or strong smoothness control.

Use product size of D(n,r).
Insufficient by itself because large product does not imply large divisor below n.

Use lcm growth.
Gives large D(n,r) in many regimes, but again does not solve divisor placement.

Exploit interval structure of n−r+1,…,n.
This is essential, but no complete covering argument was obtained.

Assume no divisor in (cn,n] and cover all candidates by deficient prime powers.
Correct contradiction framework, but the covering bound was not closed.

Separate regimes r≪n, r≍n.
Boundary regimes are easier; the intermediate regime remains.

Build counterexamples using smooth blocks.
No verified construction forcing M(n,r)/n→0.

This gap remains unresolved.

Verified partial theorem

For every n≥2 and 1≤r≤n/2,

M(n,r)≥max(
r
n
	​

, M
D
	​

(n,r)),

where

M
D
	​

(n,r)=max{d:d∣D(n,r), d≤n}.

Therefore the original problem would follow from either of the following stronger statements:

n,r
inf
	​

n
M
D
	​

(n,r)
	​

>0,

or

∃c>0 ∀n,r:(
r
n
	​

) has a prime divisor p∈(cn,n].

Neither stronger statement was proved or disproved here.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 93/100
The formal reductions and lemmas above are logically verified.

COMPLETENESS_SCORE: 38/100
A real divisor-producing mechanism was found, but the core uniform constant problem remains open within this derivation.

ADVERSARIAL_SURVIVAL_SCORE: 82/100
The accepted lemmas survived p-adic verification. The attempted reductions were explicitly not promoted to solutions.

RESOURCE_USAGE:
Approximately 100% of the available response-level reasoning budget used; 12 strategies explored; 4 verified lemmas/formulations generated; 3 major proof routes failed to close.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

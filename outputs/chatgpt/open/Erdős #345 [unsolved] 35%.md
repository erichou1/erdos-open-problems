# Erdős Problem #345 [unsolved] 35%

---

## ChatGPT Response

Formal statement

Let

B(n,k)=(
k
n
	​

),1≤k<n.

Define

D(n,k)=max{d∈Z
≥1
	​

:d∣B(n,k), d≤n}.

The problem asks whether

∃c>0 ∀n≥2 ∀k∈{1,…,n−1},D(n,k)>cn.

By symmetry (
k
n
	​

)=(
n−k
n
	​

), it is enough to consider

1≤k≤n/2.

The negation is

∀c>0 ∃n≥2 ∃1≤k<nsuch that∀d∣(
k
n
	​

), d≤n⇒d≤cn.

Equivalently,

n≥2, 1≤k<n
inf
	​

n
D(n,k)
	​

=0.

So a proof needs a uniform positive lower bound for D(n,k)/n. A disproof needs a sequence (n
i
	​

,k
i
	​

) such that every divisor of (
k
i
	​

n
i
	​

	​

) below n
i
	​

 is o(n
i
	​

).

Verified elementary facts
Lemma 1: the standard divisor n/gcd(n,k)

Let g=gcd(n,k). Then

g
n
	​

∣(
k
n
	​

).

Proof:

k(
k
n
	​

)=n(
k−1
n−1
	​

).

Write n=gn
0
	​

, k=gk
0
	​

, with gcd(n
0
	​

,k
0
	​

)=1. Then

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

)=1, we get

n
0
	​

=
gcd(n,k)
n
	​

∣(
k
n
	​

).

Thus

D(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

This proves the easy bound mentioned in the statement, but it does not give an absolute constant because k can grow with n.

Lemma 2: an interval-lcm divisor

Let

L
1
	​

=lcm(n−k+1,n−k+2,…,n),
L
0
	​

=lcm(1,2,…,k).

Then

L
0
	​

L
1
	​

	​

∣(
k
n
	​

).

First, L
0
	​

∣L
1
	​

, because every block of k consecutive integers contains a multiple of each r∈{1,…,k}.

Now fix a prime p. Let

a=
0≤j<k
max
	​

v
p
	​

(n−j),s=
1≤r≤k
max
	​

v
p
	​

(r)=⌊log
p
	​

k⌋.

Then

v
p
	​

(L
1
	​

/L
0
	​

)=a−s.

If a≤s, there is nothing to prove. Suppose a>s. For every e≤s, a block of k consecutive integers contains at least ⌊k/p
e
⌋ multiples of p
e
. Therefore the contribution to

v
p
	​

(
k
n
	​

)=
e≥1
∑
	​

(#{m∈[n−k+1,n]:p
e
∣m}−⌊
p
e
k
	​

⌋)

from e≤s is nonnegative. For every s<e≤a, the denominator contributes 0, while the numerator contributes at least 1. Hence

v
p
	​

(
k
n
	​

)≥a−s=v
p
	​

(L
1
	​

/L
0
	​

).

Since this holds for every prime p,

L
0
	​

L
1
	​

	​

∣(
k
n
	​

).

This is a genuinely useful divisor source, stronger than Lemma 1 in many cases.

Reformulation after Lemma 2

A sufficient theorem would be:

∃c>0 ∀1≤k≤n/2,
lcm(1,…,k)
lcm(n−k+1,…,n)
	​

 has a divisor in (cn,n].

Call this statement S(c).

If S(c) holds, then the original problem is proved with the same c, because the lcm quotient divides (
k
n
	​

).

This is a reduction, not a solution. The remaining theorem S(c) still needs proof.

Strategy search

I considered the following independent approaches.

Strategy	Target	Obstacle
Direct use of n/gcd(n,k)	Works when gcd(n,k) is bounded	Fails when gcd(n,k) grows
Symmetry k↔n−k	Reduces to k≤n/2	Still leaves all medium k
Prime divisor >k	Would give d>cn when k>cn	Does not handle k=o(n)
Interval-lcm quotient	Produces large structured divisor of (
k
n
	​

)	Need divisor-placement theorem for lcm quotient
Greedy divisor construction	Try to build divisor just below n	General greedy lemma is false for arbitrary integers
p-adic valuation control	Track exact prime powers surviving cancellation	Hard to convert valuations into a divisor in (cn,n]
Cyclic group action on k-subsets	Reproves n/gcd(n,k)∣(
k
n
	​

)	No constant bound
Induction on k	Use (
k
n
	​

)=(
k−1
n
	​

)
k
n−k+1
	​

	Division by k can destroy useful divisors
Induction on n	Use Pascal recurrence	Additive recurrence gives weak divisibility information
Counterexample construction by CRT	Try forcing all large candidates not to divide	Hard because composite divisors can appear unexpectedly
Density/smoothness approach	Use large nonsmooth parts of top interval	Needs strong control of smooth blocks
Stronger theorem D(n,k)>n/2	Computationally plausible in small ranges	No proof from verified lemmas
Main unresolved gap

The strongest verified path is:

lcm(1,…,k)
lcm(n−k+1,…,n)
	​

∣(
k
n
	​

).

So the central unresolved target is:

∃c>0 ∀1≤k≤n/2,Q(n,k):=
lcm(1,…,k)
lcm(n−k+1,…,n)
	​

 has a divisor in (cn,n].
	​


I could not prove or disprove this target from first principles within the available reasoning budget.

Several tempting sublemmas fail in general. For example, the following general statement is false:

If an integer N has many prime factors below n, then N must have a divisor in (cn,n].

Arbitrary products can have large multiplicative gaps among divisors. Therefore one must exploit the special lcm-interval structure of Q(n,k), not just its size.

Verified special cases
k=1
(
1
n
	​

)=n,

so D(n,1)=n.

k=2
(
2
n
	​

)=
2
n(n−1)
	​

.

If n is odd, then n∣(
2
n
	​

), so D(n,2)=n.

If n is even, then

(
2
n
	​

)=
2
n
	​

(n−1),

so n−1∣(
2
n
	​

). Hence

D(n,2)≥n−1.

For n≥4,

n−1≥
4
3
	​

n.

Thus k=2 satisfies the desired property with c=3/4.

Bounded k

For fixed k, Lemma 2 often gives divisors very close to n, but proving a uniform statement over all fixed k simultaneously still requires control over cancellation by lcm(1,…,k). I did not complete that proof.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas above; 0 for the original statement as a completed theorem.

COMPLETENESS_SCORE: 35. The main structural reductions and divisibility lemmas are established, but the central constant-gap divisor theorem remains unresolved.

ADVERSARIAL_SURVIVAL_SCORE: 85 for Lemma 1 and Lemma 2. The broader proof attempt does not survive because the lcm-divisor-placement gap remains open inside this session.

RESOURCE_USAGE: approximately 90% of the available reasoning effort; 12 strategies generated; 2 verified lemmas; 1 main unresolved gap; several false auxiliary routes rejected.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

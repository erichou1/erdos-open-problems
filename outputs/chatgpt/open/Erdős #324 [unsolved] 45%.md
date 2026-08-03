# Erdős Problem #324 [unsolved] 45%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Phase 0: Complete formalization
Formal statement

We seek to decide:

∃c>0 ∀n,k∈Z,1≤k<n⟹∃d∈Z

such that

d∣(
k
n
	​

),cn<d≤n.

Equivalently:

∃c>0 ∀n≥2 ∀k∈{1,…,n−1},Div((
k
n
	​

))∩(cn,n]

=∅.
Quantifier structure

The constant c must be chosen once and for all, independent of both n and k.

The divisor d may depend on n,k.

Negation

The negation is:

∀c>0 ∃n>k≥1

such that every divisor d∣(
k
n
	​

) satisfies

d≤cnord>n.

Equivalently, for every c>0, there is a binomial coefficient whose divisors avoid the whole interval (cn,n].

Symmetry
(
k
n
	​

)=(
n−k
n
	​

).

So it is enough to study

1≤k≤
2
n
	​

.

If a divisor exists for k, the same divisor works for n−k.

Immediate divisor

Using

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

),

write g=gcd(n,k), n=gn
1
	​

, k=gk
1
	​

, gcd(n
1
	​

,k
1
	​

)=1. Since

(
k
n
	​

)=
k
1
	​

n
1
	​

	​

(
k−1
n−1
	​

)

is an integer and gcd(n
1
	​

,k
1
	​

)=1, we get

k
1
	​

∣(
k−1
n−1
	​

),

hence

gcd(n,k)
n
	​

∣(
k
n
	​

).
	​


Therefore (
k
n
	​

) always has a divisor in

[
k
n
	​

,n].

This proves the desired result whenever k≤1/c, but not uniformly for large k.

Stronger immediate divisor

For every prime p,

v
p
	​

((
k
n
	​

))=v
p
	​

(n)+v
p
	​

((n−1)⋯(n−k+1))−v
p
	​

(k!).

Thus

v
p
	​

((
k
n
	​

))≥max(0,v
p
	​

(n)−v
p
	​

(k!)).

Hence

gcd(n,k!)
n
	​

∣(
k
n
	​

).
	​


This improves the trivial divisor in some cases, but it still gives only

k!
n
	​


in the worst case, which is not enough for an absolute constant.

Phase 1: Breadth-first proof search

I explored the following independent strategies.

Strategy	Main idea	Obstacle
Direct divisor from n	Use n/gcd(n,k!)∣(
k
n
	​

)	Fails when n is very k!-smooth
Symmetry	Reduce to k≤n/2	Still leaves k growing with n
Prime divisor strategy	Prove (
k
n
	​

) has a prime factor >ck, then handle k≫n	Does not handle k=o(n)
Greedy divisor packing	Take largest divisor ≤n	General integer argument only gives ≫
n
	​

, not cn
Smooth/rough factor split	Separate small and large prime factors of (
k
n
	​

)	Small-prime valuations can vanish simultaneously for chosen n
LCM of numerator interval	Compare (
k
n
	​

) with lcm(n−k+1,…,n)	LCM has large divisors, but they need not survive division by the quotient
Quotient L/(
k
n
	​

)	Let L=lcm(n−k+1,…,n); then L/(
k
n
	​

)∣k!	Need a uniform bound on gcd(a,L/(
k
n
	​

)) for some interval element a, unresolved
Induction on k	Use recurrence (
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

)	Divisors can be destroyed by division by k
Induction on n	Relate (
k
n
	​

) to row n−1	Same cancellation obstruction
Contradiction via maximal divisor	Suppose largest divisor D≤n satisfies D≤cn	This forces remaining prime factors >n/D, but no contradiction follows
Counterexample construction	Try to force all divisors below cn or above n	No explicit construction obtained
Covering congruences	Make numerator terms highly divisible by small primes	Large surviving prime factors still tend to create divisors near n

The most promising route was the LCM quotient route.

Phase 2: Main partial structure discovered

Let

A
i
	​

=n−k+i,1≤i≤k,

so the numerator interval is

n−k+1,n−k+2,…,n.

Let

L=lcm(n−k+1,…,n).

Since

(
k
n
	​

)=
k!
A
1
	​

A
2
	​

⋯A
k
	​

	​

,

and since for every prime p,

v
p
	​

(A
1
	​

⋯A
k
	​

)−v
p
	​

(L)≤v
p
	​

(k!),

we get

L
A
1
	​

A
2
	​

⋯A
k
	​

	​

∣k!.

Therefore

(
k
n
	​

)=
M
L
	​


for some integer

M∣k!.

Thus every divisor of L which is sufficiently divisible by M produces a divisor of (
k
n
	​

).

For each interval element a∈[n−k+1,n],

gcd(a,M)
a
	​

∣(
k
n
	​

).

So if one could prove the following lemma, the original problem would be solved.

GAP NODE 1

For all 1≤k≤n/2, with

M=
(
k
n
	​

)
lcm(n−k+1,…,n)
	​

,

there exists a∈[n−k+1,n] such that

gcd(a,M)≤C

for some absolute constant C.

Indeed, then

d=
gcd(a,M)
a
	​


would satisfy

d∣(
k
n
	​

),d≤a≤n,

and because a≥n−k+1≥n/2,

d≥
C
n/2
	​

=
2C
n
	​

.

So the original theorem would follow with

c=
2C
1
	​

.

However, I was not able to prove this gap node from first principles.

Phase 3: Verification of the reduction

The reduction itself is valid.

For each prime p, write

e
i
	​

=v
p
	​

(A
i
	​

),E=
i
max
	​

e
i
	​

,S=
i
∑
	​

e
i
	​

.

Then

v
p
	​

(L)=E,

and

v
p
	​

((
k
n
	​

))=S−v
p
	​

(k!).

Thus

v
p
	​

(M)=v
p
	​

(L)−v
p
	​

((
k
n
	​

))=E−S+v
p
	​

(k!).

Since S−E≤v
p
	​

(k!), this is nonnegative, and therefore M is an integer.

Also,

v
p
	​

(M)≤v
p
	​

(k!),

so

M∣k!.

For a=A
j
	​

, since a∣L=M(
k
n
	​

), we have

gcd(a,M)
a
	​

∣(
k
n
	​

).

This part is fully verified.

Phase 4: Failed proof attempt for GAP NODE 1

I tried to prove a stronger statement:

∃a∈[n−k+1,n]gcd(a,M)≤2.

This would give

d≥
2
n−k+1
	​

>
4
n
	​


for k<n/2, hence c=1/4.

The obstruction is that M∣k!, so its prime factors are at most k, but an interval of length k can be heavily covered by small prime divisibility. One would need to show that the special structure of

M=
(
k
n
	​

)
L
	​


prevents such a covering from forcing every a to have large gcd(a,M).

I could verify the algebraic structure of M, but I could not prove the necessary covering lemma.

Phase 5: Counterexample search framework

To disprove the statement, one would need to construct, for every c>0, some n,k such that

Div((
k
n
	​

))∩(cn,n]=∅.

Equivalently, if D(n,k) is the largest divisor of (
k
n
	​

) not exceeding n, then one would need

1≤k<n
inf
	​

n
D(n,k)
	​

=0.

The trivial divisor gives

D(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

So any counterexample sequence must have

k→∞.

By symmetry, one may assume

k≤n/2.

Thus a counterexample sequence would need

k→∞,k≤n/2,

and all divisors of (
k
n
	​

) below n would have to remain o(n).

I did not obtain such a construction.

Dependency graph of verified results
Lemma 1
gcd(n,k)
n
	​

∣(
k
n
	​

).

Dependencies: identity (
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

Status: proved.

Lemma 2
gcd(n,k!)
n
	​

∣(
k
n
	​

).

Dependencies: p-adic valuation formula.

Status: proved.

Lemma 3

Let

L=lcm(n−k+1,…,n).

Then

(
k
n
	​

)∣L,

and

M=
(
k
n
	​

)
L
	​

∣k!.

Status: proved.

Lemma 4

For each a∈[n−k+1,n],

gcd(a,M)
a
	​

∣(
k
n
	​

).

Status: proved.

Unresolved primary target

Prove or disprove that there is an absolute C such that some a∈[n−k+1,n] satisfies

gcd(a,M)≤C.

Status: unresolved.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified reductions and lemmas.

COMPLETENESS_SCORE: 45/100. A promising reduction was obtained, but the central uniform bound remains unproved.

ADVERSARIAL_SURVIVAL_SCORE: 80/100 for the verified algebraic parts; 0/100 for the unresolved gap, since it was not proved.

RESOURCE_USAGE: approximately 100% of the available reasoning budget; 12 strategies explored; 4 verified lemmas generated; 1 main unresolved gap isolated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

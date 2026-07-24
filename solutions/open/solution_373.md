# Erdős Problem #373 [unsolved] 18%

---

## ChatGPT Response

Formal statement.

Let

S={(n,k,a
1
	​

,…,a
k
	​

)∈N
k+2
:n−1>a
1
	​

≥a
2
	​

≥⋯≥a
k
	​

≥2, n!=
i=1
∏
k
	​

a
i
	​

!}.

Target theorem:

∣S∣<∞.

Since for fixed n, each a
i
	​

≤n−2 and 2
k
∣∏a
i
	​

!=n!, we have

k≤v
2
	​

(n!)<n.

So for each fixed n, only finitely many tuples are possible. Therefore the theorem is equivalent to:

∃N ∀n>N, there is no solution with largest factor a
1
	​

<n−1.

Negation:

∀N ∃n>N ∃k≥1 ∃a
1
	​

≥⋯≥a
k
	​

≥2

such that

n−1>a
1
	​

,n!=
i=1
∏
k
	​

a
i
	​

!.

Contrapositive form:

If solutions exist for arbitrarily large n, then there is an infinite sequence

n
j
	​

→∞

with corresponding nonincreasing factorial decompositions satisfying the equation.

Set

A=a
1
	​

,d=n−A.

Then d≥2, A≤n−2, and after cancelling A!,

t=A+1
∏
n
	​

t=
i=2
∏
k
	​

a
i
	​

!.
(1)

This is the main reduced equation, but it is not a solution.

For every prime p,

v
p
	​

(n!)=
i=1
∑
k
	​

v
p
	​

(a
i
	​

!),

where

v
p
	​

(m!)=
r≥1
∑
	​

⌊
p
r
m
	​

⌋.

Equivalently,

v
p
	​

(
t=A+1
∏
n
	​

t)=
i=2
∑
k
	​

v
p
	​

(a
i
	​

!).
(2)

Immediate invariant:

No prime lies in (A,n].
Indeed, if p∈(A,n], then p∣n! but p∤a
i
	​

! for every i, contradiction.

By Bertrand’s postulate, for n>2 there is a prime p∈(n/2,n). Since no prime may lie in (A,n], this forces

A>
2
n
	​

.
(3)

Thus every solution satisfies

2≤d<n/2.

For primes p>A/2, and n large enough so that p
2
>n, equation (2) becomes

#{i≥2:a
i
	​

≥p}=⌊
p
n
	​

⌋−⌊
p
A
	​

⌋.

Since p>A/2, ⌊A/p⌋=1, so

#{i≥2:a
i
	​

≥p}=⌊
p
n
	​

⌋−1.
(4)

Because A>n/2, this only gives strong information for primes p∈(A/2,A], essentially the range p>n/4. It does not propagate deeply enough by itself.

Twelve proof strategies were examined.

Strategy	Core idea	Result
Direct p-adic proof	Use prime valuations to force impossible multiplicities	Gives (2), (3), (4), but no contradiction
Contradiction via prime-free interval	Infinite solutions force (A,n] prime-free	Only gives d bounded by a prime gap after A, insufficient
Log-size proof	Show RHS factorials must be too large	Needs many large a
i
	​

; only partially forced
Induction on n	Relate a solution at n to smaller factorial products	No monotone descent found
Induction on d=n−A	Treat short interval products	Works only for very small d, not uniform
Transfinite/ordering descent	Order solutions lexicographically and seek minimal counterexample	Minimal object gives no contradiction
Cardinal arithmetic	Use finiteness per n; reduce to bounding n	Correct but needs main bound
Diagonalization	Force incompatible prime constraints over many p	Constraint too sparse without prime-density input
Compactness	Treat valuation vectors as infinite integer sequences	Produces limiting constraints, no contradiction
Density argument	Many primes should lie in useful intervals	Requires prime-distribution input not derivable here
Reflection/scaling	Approximate a
j
	​

∼n/j from large primes	Exact only in limited ranges
Counterexample construction	Try to build infinite families from prime-free intervals	No construction found, but obstruction not decisive

Main verified lemmas.

Lemma 1. For every solution, no prime belongs to (A,n].

Proof. If p∈(A,n], then p∣n!. But every a
i
	​

≤A<p, so no a
i
	​

! is divisible by p. Contradiction.

Lemma 2. For every solution with n>2,

A>
2
n
	​

.

Proof. Bertrand’s postulate gives a prime p∈(n/2,n). By Lemma 1, p≤A. Hence A>n/2.

Lemma 3. For every prime p>A/2 with p
2
>n,

#{i≥2:a
i
	​

≥p}=⌊
p
n
	​

⌋−1.

Proof. Since p
2
>n,

v
p
	​

(m!)=⌊
p
m
	​

⌋

for all m≤n. Equation (2) gives

i=2
∑
k
	​

⌊
p
a
i
	​

	​

⌋=⌊
p
n
	​

⌋−⌊
p
A
	​

⌋.

Because p>A/2 and a
i
	​

≤A, each ⌊a
i
	​

/p⌋∈{0,1}, and ⌊A/p⌋=1. Therefore the left side is exactly #{i≥2:a
i
	​

≥p}, proving the claim.

This gives useful local information but does not force global finiteness.

A tempting false route was rejected:

One might try to use primes p∈(n/2
r+1
,n/2
r
) and claim that v
p
	​

(a
i
	​

!) is just an indicator of a
i
	​

≥p. That is false. Even when p
2
>n, one still has

v
p
	​

(a
i
	​

!)=⌊
p
a
i
	​

	​

⌋,

not merely 0 or 1. Multiples 2p,3p,… inside a
i
	​

! still contribute. This destroys the apparent logarithmic contradiction.

Primary unresolved gap.

To prove finiteness from the verified material, one would need a theorem of the following kind:

There exists N such that for every n>N, if A<n−1 and (A,n] contains no prime, then the interval product

(A+1)(A+2)⋯n

cannot be written as a product of factorials all ≤A!.

Equivalently, one needs to rule out solutions to

t=A+1
∏
n
	​

t=
i=2
∏
k
	​

a
i
	​

!

under

n/2<A≤n−2,a
i
	​

≤A.

I attacked this gap through valuation constraints, logarithmic lower bounds, prime-free interval structure, and attempts to force many large a
i
	​

. None produced a complete contradiction using only first-principles deductions available in this session.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified lemmas; 0/100 for the original finiteness theorem, since no proof was completed.

COMPLETENESS_SCORE: 18/100.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the partial deductions; the main proof attempt did not survive because the dyadic-prime argument contained the rejected valuation error.

RESOURCE_USAGE: approximately 100% of the available proof-search budget for this response; 12 strategies examined; 3 verified lemmas generated; 1 major failed proof attempt identified and destroyed.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

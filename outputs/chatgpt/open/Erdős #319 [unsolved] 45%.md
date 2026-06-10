# Erdős Problem #319 [unsolved] 45%

---

## ChatGPT Response

Formal statement

For N≥1, define F(N) to be the largest integer k such that there exist

A⊆{1,…,N},δ:A→{−1,1},

with ∣A∣=k, satisfying

n∈A
∑
	​

n
δ
n
	​

	​

=0

and, for every nonempty proper subset A
′
⊊A,

n∈A
′
∑
	​

n
δ
n
	​

	​


=0.

Equivalently, writing

P={n∈A:δ
n
	​

=1},M={n∈A:δ
n
	​

=−1},

we need

p∈P
∑
	​

p
1
	​

=
m∈M
∑
	​

m
1
	​

,

and no proper nonempty pair P
′
⊆P, M
′
⊆M, other than the full pair (P,M), has

p∈P
′
∑
	​

p
1
	​

=
m∈M
′
∑
	​

m
1
	​

.

Thus A is a minimal signed zero relation among the reciprocals {1,…,1/N}.

The asymptotic candidate suggested by the displayed construction is

F(N)
=
?
(1−
e
1
	​

+o(1))N.

I can verify the lower bound from the stated Croot input, but I do not obtain a matching upper bound from first-principles reasoning.

Verified lower bound

Assume the stated input theorem:

There exists

B⊆[(
e
1
	​

−o(1))N, N]

such that

b∈B
∑
	​

b
1
	​

=1.

Let

A=B∪{1},

with

δ
1
	​

=1,δ
b
	​

=−1(b∈B).

Then

n∈A
∑
	​

n
δ
n
	​

	​

=1−
b∈B
∑
	​

b
1
	​

=0.

Now check minimality. If A
′
⊆A is nonempty and has signed sum 0, then either 1∈
/
A
′
 or 1∈A
′
.

If 1∈
/
A
′
, then

n∈A
′
∑
	​

n
δ
n
	​

	​

=−
n∈A
′
∑
	​

n
1
	​

<0,

so it cannot be zero.

If 1∈A
′
, then zero sum forces

1−
b∈A
′
∩B
∑
	​

b
1
	​

=0,

so

b∈A
′
∩B
∑
	​

b
1
	​

=1.

But since every term 1/b is positive and the full set B already has sum 1, the only subset of B with sum 1 is B itself. Hence A
′
∩B=B, so A
′
=A. Therefore no nonempty proper A
′
⊊A has zero signed sum.

Thus

F(N)≥∣A∣=∣B∣+1.

The full interval

I
N
	​

=[(
e
1
	​

−o(1))N, N]

has reciprocal sum

n∈I
N
	​

∑
	​

n
1
	​

=1+o(1).

Since B⊆I
N
	​

 and ∑
b∈B
	​

1/b=1, the complement I
N
	​

∖B has reciprocal sum o(1). Every element of I
N
	​

 is ≤N, so every reciprocal is at least 1/N. Hence

∣I
N
	​

∖B∣≤o(N).

Therefore

∣B∣=∣I
N
	​

∣−o(N)=(1−
e
1
	​

+o(1))N,

and so

F(N)≥(1−
e
1
	​

+o(1))N.
	​


This part is proved, assuming the stated Croot-type input.

Structural necessary condition

Let A,δ be any admissible configuration, and let

L=lcm(A).

Multiplying the zero relation by L,

n∈A
∑
	​

δ
n
	​

n
L
	​

=0.

Fix a prime p. Let

α=
n∈A
max
	​

v
p
	​

(n).

Consider the terms with maximal p-adic valuation:

T
p
	​

={n∈A:v
p
	​

(n)=α}.

Modulo p, every term with v
p
	​

(n)<α vanishes, while the terms in T
p
	​

 survive. Therefore

n∈T
p
	​

∑
	​

δ
n
	​

(
p
α
n
	​

)
−1
≡0(modp).

In particular, T
p
	​

 cannot have size 1. Hence:

For every prime p, at least two elements of A attain the maximal p-adic valuation.
	​


Immediate consequence: if p>N/2, then p∈
/
A, because p would be the unique element of [N] divisible by p.

More generally, an element of A cannot possess a prime-power divisibility feature that no other element of A shares at the same maximal p-adic level.

This is a real obstruction, but it is too weak to yield the density upper bound (1−1/e)N. It excludes many isolated large-prime configurations, but not a positive proportion of all integers.

Failed upper-bound routes

A matching upper bound would require proving

F(N)≤(1−
e
1
	​

+o(1))N.

I tried the following approaches from first principles:

Strategy	Result
Harmonic-size bound	Fails: minimal relations can have both sides with sum >1, so the lower-bound construction is not forced.
Smallest denominator analysis	Gives local balancing constraints but no global density loss.
p-adic maximal-layer obstruction	Proves the top-layer lemma above, but does not force ≥N/e missing elements.
Large-prime exclusion	Excludes primes >N/2, and some similar sparse classes, only o(N) elements.
Induction on N	No monotone removal step preserves minimality.
Induction on lcm(A)	The p-adic descent does not produce a smaller admissible relation.
Subset-sum cardinality	The rational denominator space is exponentially large enough that counting subset sums gives no contradiction.
Circuit interpretation	A is a minimal signed circuit, but the ambient rational span alone gives no useful rank bound.
Interval-density argument	Proves the lower bound cleanly, but gives no converse.
Counterexample search to singleton-side structure	Small examples show minimal relations need not have one side equal to {1}.
Modular reductions modulo primes	Produce many necessary congruences but no linear-density upper bound.
Compactness-style reformulation	Gives no finite obstruction strong enough for the asymptotic claim.

The main unresolved gap is:

Gap:Show that every minimal signed reciprocal relation in [N] omits at least (
e
1
	​

−o(1))N integers.

I was unable to prove this from the available assumptions.

Verified conclusion

The rigorously established result is

F(N)≥(1−
e
1
	​

+o(1))N.
	​


I do not have a first-principles proof of the matching upper bound, nor a construction beating it.

Therefore the exact asymptotic size is not resolved by the reasoning completed here.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100
COMPLETENESS_SCORE: 45/100
ADVERSARIAL_SURVIVAL_SCORE: 80/100
RESOURCE_USAGE: about 85% of the available reasoning budget; 12 strategies explored; 3 verified lemmas; multiple failed upper-bound attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

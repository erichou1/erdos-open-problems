# Erdős Problem #68 [unsolved] 35%

---

## ChatGPT Response

Formal statement

Let

d
n
	​

=n!−1,S=
n=2
∑
∞
	​

d
n
	​

1
	​

.

The target statement is

S∈
/
Q.

Equivalently,

∀a∈Z∀b∈Z
>0
	​

,S

=
b
a
	​

.

Negation:

∃a∈Z, ∃b∈Z
>0
	​

such thatS=
b
a
	​

.

Since d
2
	​

=1,

S=1+
n=3
∑
∞
	​

n!−1
1
	​

,

so irrationality of S is equivalent to irrationality of

R=
n=3
∑
∞
	​

n!−1
1
	​

.

The series converges because for n≥3,

n!−1≥
2
n!
	​

,

so

0<
n!−1
1
	​

≤
n!
2
	​

,

and ∑1/n! converges.

A useful equivalent formulation is:

S∈
/
Q⟺∀M≥1, M!S∈
/
Z.

Indeed, if S=a/b, then for every M≥b, b∣M!, so M!S∈Z. Conversely, if M!S∈Z for some M, then S∈Q.

Basic verified identities

For every n≥2,

n!−1
1
	​

=
1−1/n!
1/n!
	​

=
k≥1
∑
	​

(n!)
k
1
	​

.

Thus

S=
n≥2
∑
	​

k≥1
∑
	​

(n!)
k
1
	​

.

This is valid because all terms are positive and the original series converges.

Also, every prime divisor of d
n
	​

=n!−1 is >n.
If p≤n, then p∣n!, hence

n!−1≡−1(modp),

so p∤n!−1.

For consecutive denominators,

gcd(d
n
	​

,d
n+1
	​

)=1.

Proof:

d
n+1
	​

=(n+1)!−1=(n+1)n!−1.

Modulo d
n
	​

=n!−1, we have n!≡1, hence

d
n+1
	​

≡n+1−1=n(modd
n
	​

).

Therefore

gcd(d
n
	​

,d
n+1
	​

)=gcd(d
n
	​

,n).

But d
n
	​

=n!−1≡−1(modn), so gcd(d
n
	​

,n)=1. Hence

gcd(d
n
	​

,d
n+1
	​

)=1.
Breadth-first strategy search

I tested the following proof frameworks.

Strategy	Idea	Obstacle
Direct tail bound	Clear first N terms and force the remaining tail into (0,1)	Clearing denominators grows too fast
Contradiction via S=a/b	Multiply by common denominators	Same denominator-growth obstruction
Factorial-base criterion	Prove M!S∈
/
Z for all M	Fractional part of M!S is hard to isolate
Double-series truncation	Use ∑
n,k
	​

(n!)
−k
 and truncate terms whose denominators divide M!	Omitted terms are still too large relative to the denominator
Prime isolation	Find a prime dividing exactly one n!−1	Existence of enough isolated primes is unproved here
p-adic obstruction	Use primes dividing n!−1	Infinite real convergence does not imply usable p-adic convergence
Induction on tails	Study T
N
	​

=∑
n>N
	​

1/(n!−1)	No closed recurrence preserving rationality contradiction
Diagonalization	Construct incompatible rational approximations	No verified incompatible diagonal condition found
Compactness-style argument	Model rationality through finite truncations	Finite data do not force global contradiction
Density/modular arguments	Study residues of m! modulo primes dividing n!−1	Residue sets may contain multiple collisions
Auxiliary invariant	Track denominator-clearing complexity	Produces obstruction, not proof
Counterexample search	Try to construct rationality mechanism	No construction found

The strongest verified obstruction is that the most obvious irrationality proof by clearing a finite prefix cannot work.

Let

L
N
	​

=lcm(d
2
	​

,d
3
	​

,…,d
N
	​

).

If S=a/b, then

bL
N
	​

S−bL
N
	​

n=2
∑
N
	​

d
n
	​

1
	​

=bL
N
	​

n>N
∑
	​

d
n
	​

1
	​


would be an integer. A standard approach would try to show

0<bL
N
	​

n>N
∑
	​

d
n
	​

1
	​

<1.

But L
N
	​

 is already too large. Since d
N−1
	​

 and d
N
	​

 are coprime,

d
N−1
	​

d
N
	​

∣L
N
	​

.

Also,

n>N
∑
	​

d
n
	​

1
	​

>
d
N+1
	​

1
	​

.

Therefore

L
N
	​

n>N
∑
	​

d
n
	​

1
	​

>
d
N+1
	​

d
N−1
	​

d
N
	​

	​

.

For N≥5,

d
N−1
	​

d
N
	​

>d
N+1
	​

.

Indeed, writing a=(N−1)!, this inequality becomes

(a−1)(Na−1)>(N+1)Na−1,

or

Na
2
−(N+1)
2
a+2>0,

which holds for N≥5 because a=(N−1)! is already large enough.

Thus

L
N
	​

n>N
∑
	​

d
n
	​

1
	​

>1

for N≥5, so the elementary “clear prefix and bound tail below 1” method fails structurally.

Main unresolved target

The cleanest equivalent theorem remains:

∀M≥1,M!S∈
/
Z.
	​


Several attacks on this target were tried.

Attack 1: choose M so many d
n
	​

∣M!

If d
n
	​

≤M, then d
n
	​

∣M!. Thus all terms with n!−1≤M become integral after multiplying by M!.

Let

r(M)=max{n:n!−1≤M}.

Then

M!S=integer+M!
n>r(M)
∑
	​

n!−1
1
	​

.

A contradiction would follow if the second term were always strictly between two consecutive integers, but it is generally large and complicated. No verified nonintegrality criterion was obtained.

Attack 2: use the double expansion

Because

S=
n≥2
∑
	​

k≥1
∑
	​

(n!)
k
1
	​

,

one can multiply by M!. Whenever

(n!)
k
∣M!,

that term becomes integral. The remaining terms are

(n!)
k
∤M!
∑
	​

(n!)
k
M!
	​

.

The hope is that the nonintegral remainder is small. This fails for many choices of M: moderate n and large k leave many terms whose total size is not controlled sharply enough.

Attack 3: prime-divisor isolation

Every prime divisor of n!−1 exceeds n. If one could prove that infinitely many d
n
	​

 have a prime divisor p that does not divide any other d
m
	​

, then that prime might isolate the n-th summand.

But this requires a new theorem of the form:

∃
∞
n ∃pp∣n!−1andp∤m!−1 for all m

=n.

I did not prove this. Moreover, even if such primes exist, converting that into a real irrationality proof requires care, because an infinite sum of rationals with denominators prime to p can converge in the real topology to a rational whose denominator is divisible by p. So the naïve p-adic argument is invalid without an additional convergence or denominator-control lemma.

Attack 4: recurrence on tails

Let

T
N
	​

=
n>N
∑
	​

n!−1
1
	​

.

Then

T
N−1
	​

=
N!−1
1
	​

+T
N
	​

.

If S∈Q, then every T
N
	​

∈Q. The hope is to show that this infinite rational tail recurrence is impossible.

The crude bounds are

(N+1)!−1
1
	​

<T
N
	​

<
(N+1)!
3
	​


for large N. These bounds are too weak to force rational impossibility.

Verified theorem pool

The following facts were rigorously established from the problem statement.

Lemma 1. The series S converges.

Lemma 2.

n!−1
1
	​

=
k≥1
∑
	​

(n!)
k
1
	​

.

Lemma 3.

S∈
/
Q⟺∀M≥1, M!S∈
/
Z.

Lemma 4. Every prime divisor of n!−1 is >n.

Lemma 5.

gcd(n!−1,(n+1)!−1)=1.

Lemma 6. The ordinary finite-prefix denominator-clearing method cannot prove irrationality, because for N≥5,

L
N
	​

n>N
∑
	​

n!−1
1
	​

>1.

No lemma in the verified theorem pool proves S∈
/
Q.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 95/100 for the verified lemmas above.

COMPLETENESS_SCORE: 35/100. The formal reductions and obstructions are rigorous, but the original irrationality statement is not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 85/100. The accepted lemmas survived local checks; the rejected strategies were not promoted to proofs.

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; 12 strategies considered; 6 verified lemmas generated; 4 main proof attempts failed.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

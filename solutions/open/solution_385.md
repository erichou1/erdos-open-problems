# Erdős Problem #385 [unsolved] 35%

---

## ChatGPT Response

Formalization

Let

F(n,k)=max{d∈Z
≥1
	​

:d∣(
k
n
	​

), d≤n}.

The problem asks whether

∃c>0 ∀n≥2 ∀1≤k<n,F(n,k)>cn.

Because (
k
n
	​

)=(
n−k
n
	​

), it is enough to consider

1≤k≤
2
n
	​

.

The negation is:

∀c>0 ∃n≥2 ∃1≤k<n

such that every divisor d∣(
k
n
	​

) with d≤n satisfies

d≤cn.

Equivalently,

n≥2, 1≤k<n
inf
	​

n
F(n,k)
	​

=0.

So the target is to prove or disprove

n,k
inf
	​

n
F(n,k)
	​

>0.
Verified reductions and lemmas
Lemma 1: symmetry reduction

It suffices to prove the assertion for 1≤k≤n/2, since

(
k
n
	​

)=(
n−k
n
	​

).

So if a divisor exists for (n,min(k,n−k)), the same divisor works for (n,k).

Lemma 2: a universal divisor from n

For every 1≤k<n,

gcd(n,k)
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

Let g=gcd(n,k). Then

g
k
	​

(
k
n
	​

)=
g
n
	​

(
k−1
n−1
	​

).

Since gcd(k/g,n/g)=1, it follows that n/g∣(
k
n
	​

).

Therefore, if

gcd(n,k)≤R,

then

(
k
n
	​

)

has a divisor at least n/R. Thus the problem is only difficult when gcd(n,k) can be large.

Lemma 3: a divisor from any numerator factor

Let

L
k
	​

=lcm(1,2,…,k).

For every

t∈{n−k+1,n−k+2,…,n},

the integer

gcd(t,L
k
	​

)
t
	​


divides (
k
n
	​

).

Proof: Write v
p
	​

(x) for the exponent of a prime p in x. Let

B
p
	​

=max{b:p
b
≤k}=v
p
	​

(L
k
	​

).

If p
a
∣t with a>B
p
	​

, then p
a
>k. The denominator k! contains no factor p
a
 coming from a single denominator term, so the excess p
a−B
p
	​

 cannot be fully canceled. Hence

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

(t)−v
p
	​

(L
k
	​

)).

Multiplying over all primes gives

gcd(t,L
k
	​

)
t
	​

∣(
k
n
	​

).

Thus, if for some t∈[n−k+1,n],

gcd(t,L
k
	​

)
t
	​

>cn,

then the desired divisor exists.

This proves the original claim in all cases where at least one numerator factor has a sufficiently large part not already contained in L
k
	​

.

Lemma 4: terminal block divisors

For every 1≤r≤k, define

A
r
	​

=(n−k+1)(n−k+2)⋯(n−k+r),

and

B
r
	​

=k(k−1)⋯(k−r+1).

Then

gcd(A
r
	​

,B
r
	​

)
A
r
	​

	​

∣(
k
n
	​

).

Proof:

(
k
n
	​

)=
k(k−1)⋯(k−r+1)
(n−k+1)(n−k+2)⋯(n−k+r)
	​

(
k−r
n
	​

).

Since (
k
n
	​

) is an integer, the reduced numerator

A
r
	​

/gcd(A
r
	​

,B
r
	​

)

divides (
k
n
	​

).

This gives a family of explicit divisors, but I did not obtain a proof that one of their divisors always lies in (cn,n] for an absolute c>0.

Boundary cases
Case k=1
(
1
n
	​

)=n,

so d=n works.

Case k=2
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

).

If n is even, then

n−1∣(
2
n
	​

).

Thus F(n,2)≥n−1.

Fixed k

For fixed k, Lemma 3 gives

gcd(n,L
k
	​

)
n
	​

∣(
k
n
	​

).

Since gcd(n,L
k
	​

)≤L
k
	​

, we get

F(n,k)≥
L
k
	​

n
	​

.

So for each fixed k, a constant c
k
	​

=1/L
k
	​

 works. The unresolved part is uniformity in k.

Main obstruction reached

The proof reduces to showing a uniform lower bound for divisors obtained from the numerator interval

[n−k+1,n].

A sufficient statement would be:

∃c>0 ∀n≥2 ∀1≤k≤n/2, ∃t∈[n−k+1,n]

such that

gcd(t,L
k
	​

)
t
	​

>cn.

This would prove the original problem by Lemma 3.

However, this sufficient statement is stronger than what is needed and is not established by the lemmas above. The original divisor may be a product of several smaller surviving parts, not necessarily the surviving part of one numerator factor.

So the verified work gives substantial reductions but not a complete proof or disproof of the original statement.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the stated lemmas; 0 for the unresolved original assertion.

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 90 for the verified reductions; not applicable to the full theorem because no complete proof was obtained.

RESOURCE_USAGE: about 80% of the available reasoning budget; 4 main divisor mechanisms isolated; 0 complete proof attempts survived full verification.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

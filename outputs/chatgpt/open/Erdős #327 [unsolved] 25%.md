# Erdős Problem #327 [unsolved] 25%

---

## ChatGPT Response

Phase 0: Formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.

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

so it is enough to study

m=min(k,n−k),1≤m≤n/2.

The target statement is:

∃c>0 ∀n≥2 ∀1≤k<n ∃d∈Z:d∣(
k
n
	​

),cn<d≤n.

Equivalent extremal form:

n≥2, 1≤k<n
inf
	​

n
1
	​

max{d≤n:d∣(
k
n
	​

)}>0.

Negation:

∀c>0 ∃n≥2, 1≤k<n

such that every divisor d≤n of (
k
n
	​

) satisfies

d≤cn.

So a disproof would require a sequence (n
j
	​

,k
j
	​

) for which the largest divisor of (
k
j
	​

n
j
	​

	​

) not exceeding n
j
	​

 is o(n
j
	​

).

Verified elementary lemmas
Lemma 1: The standard divisor

For all 1≤k<n,

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

Let g=gcd(n,k), n=gn
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

)=1. Then

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

so

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

This proves the weaker bound

(
k
n
	​

) has a divisor in [
k
n
	​

,n].

But this alone cannot give an absolute c, because k is unbounded.

Lemma 2: A family of guaranteed divisors

For every 1≤r≤k, the reduced numerator of

(
r
k
	​

)
(
r
n
	​

)
	​


divides (
k
n
	​

).

Proof:

Use

(
k
n
	​

)(
r
k
	​

)=(
r
n
	​

)(
k−r
n−r
	​

).

Let

A=(
r
n
	​

),B=(
r
k
	​

),h=gcd(A,B).

Then

B(
k
n
	​

)=A(
k−r
n−r
	​

).

Writing A=hA
0
	​

, B=hB
0
	​

, with gcd(A
0
	​

,B
0
	​

)=1, gives

B
0
	​

(
k
n
	​

)=A
0
	​

(
k−r
n−r
	​

).

Hence

A
0
	​

∣(
k
n
	​

).

So every reduced numerator

A
0
	​

=
gcd((
r
n
	​

),(
r
k
	​

))
(
r
n
	​

)
	​


is a divisor of (
k
n
	​

).

This creates many candidate divisors, but I did not obtain a proof that one of their divisors must always lie in (cn,n] for some absolute c>0.

Lemma 3: Divisor-selection lemma

Let N be an integer and let D∣N. Suppose D>n, and every prime factor of D is at most R. Then N has a divisor d satisfying

R
n
	​

<d≤n.

Proof:

Factor D into prime factors with multiplicity:

D=q
1
	​

q
2
	​

⋯q
s
	​

,q
i
	​

≤R.

Multiply the q
i
	​

’s one by one until the partial product first exceeds n. Let

Q
j
	​

=q
1
	​

⋯q
j
	​

>n

be minimal. Then

Q
j−1
	​

≤n,

and since Q
j
	​

=Q
j−1
	​

q
j
	​

≤Q
j−1
	​

R,

Q
j−1
	​

>
R
n
	​

.

Also Q
j−1
	​

∣D∣N. Thus d=Q
j−1
	​

 works.

This would prove the desired theorem with c=1/R if one could always construct a divisor D>n of (
k
n
	​

) whose prime factors are bounded by an absolute constant R. I could not prove such a construction.

Strategy search

I tested the following proof directions.

1. Direct use of n/gcd(n,k)

Works when gcd(n,k) is bounded. Fails in the hard case where k shares a large divisor with n, for example k∣n.

2. Prime divisor strategy

If (
k
n
	​

) has a prime divisor p>cn, then we are done. This handles cases where a sufficiently large prime appears, but I could not prove that such a prime must always exist.

3. Product-of-small-primes strategy

If enough small prime-power divisibility is forced, Lemma 3 gives a divisor near n. The obstruction is that binomial coefficients can have very small p-adic valuation for fixed small primes.

4. Reduced numerator strategy

The divisors

gcd((
r
n
	​

),(
r
k
	​

))
(
r
n
	​

)
	​


are guaranteed. However, they can jump from much smaller than n to much larger than n, and I could not prove that their internal divisors always hit (cn,n].

5. Counterexample construction

To disprove the statement, one would need to force every divisor d≤n of (
k
n
	​

) to be o(n). That requires controlling all subset-products of prime powers in (
k
n
	​

), not just preventing large prime factors. I found no construction that achieves this.

Main unresolved gap

The central unresolved statement is:

∃c>0 ∀n,k ∃d∣(
k
n
	​

),cn<d≤n.

The verified lemmas reduce the problem to proving one of the following stronger sufficient statements:

There is an absolute R such that (
k
n
	​

) always has a divisor D>n all of whose prime factors are ≤R.

There is an absolute c>0 such that one of the reduced numerators

gcd((
r
n
	​

),(
r
k
	​

))
(
r
n
	​

)
	​


has a divisor in (cn,n].

There is an absolute c>0 such that either (
k
n
	​

) has a prime divisor >cn, or its small-prime part is large enough to force a divisor in (cn,n].

I could not prove or disprove any of these sufficient statements within the available reasoning budget.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the stated lemmas; 0 for the original theorem as a solved claim.

COMPLETENESS_SCORE: 25

ADVERSARIAL_SURVIVAL_SCORE: 85 for the verified reductions; not applicable to a full proof, since no full proof was obtained.

RESOURCE_USAGE: approximately 100% of available reasoning budget; 12 strategies considered; 3 verified lemmas generated; multiple failed proof attempts; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

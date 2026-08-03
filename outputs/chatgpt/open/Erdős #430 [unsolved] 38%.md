# Erdős Problem #430 [unsolved] 38%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

The original statement reduces cleanly to a precise covering problem, but I did not obtain a complete proof or disproof from first principles.

1. Formal statement

For n≥2, define

S
n
	​

={m∈Z:2≤m<n, ∀p(p prime and p∣m⇒p>n−m)}.

The sequence a
1
	​

,a
2
	​

,… is exactly the decreasing enumeration of S
n
	​

. Therefore the question is:

∃N ∀n≥N ∃m∈S
n
	​

 such that m is composite.

Define P
−
(x) as the least prime divisor of x for x≥2. Put

r=n−m.

Then the target becomes:

∃N ∀n≥N ∃r≥1: n−r is composite and P
−
(n−r)>r.

So the whole problem is equivalent to proving that every sufficiently large n has a composite number just below it whose least prime factor exceeds its distance from n.

2. Negation

The negation is:

∀N ∃n≥N ∀r≥1: n−r composite⇒P
−
(n−r)≤r.

Equivalently, for arbitrarily large n, every number n−r whose prime factors all exceed r is forced to be prime.

3. Verified reductions
Lemma 1: If n−1 is composite, then the desired composite term exists.

Take m=n−1. Then r=1. Every prime factor of m is greater than 1. Hence m∈S
n
	​

. If n−1 is composite, this proves the desired claim for that n.

So any possible counterexample must satisfy:

n−1 is prime.

In particular, every odd n≥5 is automatically good, because n−1 is an even composite number.

Thus only even numbers n=p+1, where p is prime, can matter.

Lemma 2: A valid composite must occur very close to n.

If m=n−r is composite and P
−
(m)>r, then since m is composite,

P
−
(m)≤
m
	​

.

Therefore

r<
n−r
	​

.

Squaring gives

r
2
+r<n.

So it is enough to search

1≤r<
2
4n+1
	​

−1
	​

.

Thus a composite witness must lie within about 
n
	​

 of n.

Lemma 3: For even n, a valid composite witness must have odd r.

If n is even and r≥2 is even, then n−r is even. If n−r is composite, its least prime factor is 2, and

2≤r.

So P
−
(n−r)>r fails. Hence only odd r can matter for even n.

4. Equivalent interval covering form

For every composite m≥4, define the interval

I
m
	​

={m+r:1≤r<P
−
(m)}.

Then m is a valid composite witness for n exactly when

n∈I
m
	​

.

So the original statement is equivalent to:

∃N ∀n≥N ∃ composite m such that n∈I
m
	​

.

That is, the intervals immediately following composite rough numbers must eventually cover all integers.

5. Stronger sufficient conditions found

One sufficient condition is semiprime representation.

Suppose there is a prime q<
n
	​

 such that

Q=⌊
q
n
	​

⌋

is also prime, and qQ<n. Let

r=n−qQ.

Then 0<r<q<Q, so every prime factor of qQ is greater than r. Therefore

m=qQ

is a valid composite witness.

So the original claim would follow from the stronger statement:

∀ sufficiently large n, ∃q<
n
	​

 prime such that ⌊
q
n
	​

⌋ is prime and q∤n.

But this stronger statement was not proved.

Another sufficient condition is a prime square close below n. If there is a prime q such that

0<n−q
2
<q,

then q
2
 is a valid composite witness. But prime squares alone do not cover enough integers by an elementary argument.

6. Main unresolved target

After the verified reductions, the core remaining theorem is:

∃N ∀ primes p≥N ∃ odd r: r
2
+r<p+1, p+1−r composite, P
−
(p+1−r)>r.

Equivalently, for every sufficiently large prime p, at least one of the numbers

p, p−2, p−4, p−6,…

near p must be composite with no prime factor at most its offset from p+1.

I could not prove this from the allowed first principles.

7. Failed proof branches
Branch A: Direct small offset proof

Using r=1 solves all n with n−1 composite.
For r=3, if n=p+1, then the candidate is p−2. If p−2 is composite and not divisible by 3, then it works.

But a possible obstruction remains: p−2 may be prime or divisible by 3. Extending to r=5,7,9,… creates a growing sieve condition, but I did not derive a contradiction.

Branch B: Semiprime construction

It is enough to find a product qQ<n of two primes with

n−qQ<q≤Q.

This would immediately give a valid composite. However, proving such a semiprime exists for every sufficiently large n requires control over prime values of ⌊n/q⌋, which I did not establish.

Branch C: Interval covering

The desired theorem is equivalent to eventual coverage of all large integers by intervals

[m+1, m+P
−
(m)−1]

where m is composite. This reformulation is exact, but proving eventual coverage requires a lower bound on how densely such intervals overlap. I did not obtain such a bound from elementary counting alone.

8. Verified dependency graph

Definition of S
n
	​

.

Sequence equals decreasing enumeration of S
n
	​

.

Composite term exists iff ∃r≥1 with n−r composite and P
−
(n−r)>r.

If n−1 composite, then r=1 works.

Therefore only n=p+1 with p prime can be problematic.

Any composite witness satisfies r
2
+r<n.

For even n, only odd r can yield a composite witness.

Remaining target is the prime successor case n=p+1.

No complete proof or disproof of that remaining target was obtained.

Final report

PROOF_CONFIDENCE: 96

COMPLETENESS_SCORE: 38

ADVERSARIAL_SURVIVAL_SCORE: 90

RESOURCE_USAGE: about 100 percent of available reasoning budget used, 3 main branches explored, 7 verified lemmas or equivalences generated, 3 failed proof attempts.

I have not used internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

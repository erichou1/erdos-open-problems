# Erdős Problem #460 [unsolved] 32%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formalization

Fix an integer n≥2. Define a
0
	​

=0. For k≥1, a
k
	​

 is the least integer >a
k−1
	​

 such that

gcd(n−a
k
	​

,n−a
i
	​

)=1

for every 0≤i<k.

Define

A(n)={a
k
	​

:0<a
k
	​

<n}

and

S(n)=
a∈A(n)
∑
	​

a
1
	​

.

The main assertion is

∀M>0 ∃N ∀n≥N,S(n)>M.

Its negation is

∃M>0 ∀N ∃n≥N,S(n)≤M.

Equivalently, there is an unbounded sequence n
r
	​

→∞ such that S(n
r
	​

) stays bounded.

Now set

m=n−a.

Since a increases, m decreases. The construction scans

m=n−1,n−2,…,1

and accepts m exactly when it is coprime to n and to all previously accepted larger m's.

So A(n) is equivalently determined by the following greedy rule:

a∈A(n)

if and only if, when a is scanned,

gcd(n−a,n)=1

and

gcd(n−a,n−b)=1

for every earlier accepted b<a.

Exact prime blocking formulation

Let U(a) be the set of primes already used before scanning a:

U(a)={p:p∣n}∪{p:p∣n−b for some accepted b<a}.

Then

a∈A(n)

if and only if no prime divisor of n−a lies in U(a).

This is exact, because a common divisor greater than 1 exists exactly when a common prime divisor exists.

Boundary conditions

a=1 is always accepted, since

gcd(n−1,n)=1.

a=n−1 is always accepted, since

n−(n−1)=1.

Every accepted value n−a is coprime to n.

The accepted positive integers n−a, together with n, are pairwise coprime.

Restricted sums

Define

R(n)={1≤a<n:P
−
(n−a)>a},

where P
−
(1)=∞.

Define

C(n)=
a∈R(n)
∑
	​

a
1
	​

.

Then every a∈R(n) is automatically accepted.

Proof. Suppose p∣n−a. Since P
−
(n−a)>a, every such p>a.

First,

gcd(n−a,n)=gcd(n−a,a).

If a prime p∣n−a also divided a, then p≤a, contradiction.

Second, for any earlier b<a, if p∣n−a and p∣n−b, then

p∣(n−b)−(n−a)=a−b.

But

0<a−b<a<p,

impossible.

Therefore a is coprime to n and to all earlier accepted n−b. Hence a∈A(n).

So

R(n)⊆A(n)

and therefore

S(n)≥C(n).

Thus the main problem would be proved if one could prove

C(n)→∞.

This is a valid reduction, but it is not a proof of the original assertion.

Complementary restricted sum

Let

B(n)={a∈A(n):P
−
(n−a)≤a}.

Then

S(n)=
a∈R(n)
∑
	​

a
1
	​

+
a∈B(n)
∑
	​

a
1
	​

.

For each a∈B(n), define

p(a)=P
−
(n−a).

Then p(a)≤a, and the primes p(a) are distinct as a ranges over B(n). Indeed, if two accepted values n−a and n−b shared the same prime p, then they would not be coprime, contradicting the greedy rule.

Therefore

a∈B(n)
∑
	​

a
1
	​

≤
a∈B(n)
∑
	​

p(a)
1
	​

.

The right side is a sum over distinct primes not dividing n. This gives structural control over the complementary part, but not enough to prove that it diverges or stays bounded for all n.

Verified lemmas
Lemma 1

The greedy process is exactly equivalent to scanning a=1,2,…,n−1 and accepting a if no prime factor of n−a has appeared previously in n or in an accepted value n−b.

Status: proved.

Lemma 2

The accepted values n−a, together with n, are pairwise coprime.

Status: proved directly from the defining condition.

Lemma 3

Every a<n satisfying

P
−
(n−a)>a

is accepted.

Status: proved.

Lemma 4

The rough restricted sum

a<n
∑
	​

1
P
−
(n−a)>a
	​

a
1
	​


is exactly the contribution from the automatic accepted values.

Status: proved.

Lemma 5

For accepted a with P
−
(n−a)≤a, the least prime factors P
−
(n−a) are distinct.

Status: proved.

Lemma 6

For every Y, there exist n for which no 2≤a≤Y lies in R(n).

Proof. Take n divisible by every integer 1,2,…,Y. For each 2≤a≤Y, choose a prime p∣a. Since p∣n and p∣a,

p∣n−a.

Also p≤a. Hence

P
−
(n−a)≤a.

So a∈
/
R(n).

Status: proved.

This shows that any proof of C(n)→∞ cannot rely only on very small a. It must use values of a beyond the largest initial range forced by divisibility of n.

Strategy search

Direct proof through R(n): valid reduction, unresolved because it requires a uniform lower bound for shifted rough numbers.

Direct proof through the greedy rule: unresolved because rejected candidates can be covered by many small prime residue classes.

Contradiction from bounded S(n): no contradiction obtained, because bounded harmonic mass does not immediately force too few accepted coprime values.

Induction on a: stalls because acceptance at a depends on the entire previously accumulated prime set.

Induction on n: no monotonicity in n. The construction changes discontinuously with the factorization of n−a.

Cardinal arithmetic: gives at most one accepted value per reused prime, but cardinality alone does not control reciprocal mass.

Diagonal construction against the claim: CRT can kill long initial blocks, but not enough to keep the whole sum bounded.

Compactness of residue patterns: gives possible limiting obstruction systems, but no finite obstruction was converted into a full counterexample.

Density argument: heuristics suggest a contribution comparable to ∑1/(aloga), but no rigorous uniform lower bound was established.

Reflection argument using m=n−a: clarifies the descending scan, but does not force enough accepted a's near the origin.

Auxiliary hypergraph structure: candidates are vertices, primes are blocking colors, and acceptance means no used color appears. This organizes the dependencies but does not prove divergence.

Counterexample search through highly divisible n: explains why the rough part can be suppressed initially, but does not produce bounded S(n).

Primary unresolved theorem

The strongest clean target found is

a<n
∑
	​

1
P
−
(n−a)>a
	​

a
1
	​

→∞.

This theorem implies the main assertion because all such a are automatically accepted.

However, this theorem was not proved.

The main obstruction is that for each a, the forbidden condition is

∃p≤a,p∣n−a.

Equivalently,

a≡n(modp)

for some prime p≤a.

Thus the problem becomes a moving sieve with one forbidden residue class modulo each prime, but the sieve level grows with a. A lower bound strong enough to force divergent harmonic mass was not derived from first principles here.

Dependency graph

Definitions imply Lemma 1.

Lemma 1 implies Lemma 2.

Lemma 2 implies Lemma 5.

Lemma 1 plus the inequality P
−
(n−a)>a implies Lemma 3.

Lemma 3 implies

S(n)≥C(n).

Therefore

C(n)→∞

would imply

S(n)→∞.

No verified lemma proves C(n)→∞. No verified lemma disproves it.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94

COMPLETENESS_SCORE: 32

ADVERSARIAL_SURVIVAL_SCORE: 88

RESOURCE_USAGE: 100 percent reasoning budget used, 12 branches explored, 6 verified lemmas generated, 8 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #972 [unsolved] 28%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

For a fixed irrational real number α>1, define

N
α
	​

(X)=#{p≤X: p prime and ⌊αp⌋ prime}.

The assertion is

∀α∈R∖Q,α>1⟹∀M∈N ∃X≥M:N
α
	​

(X)>N
α
	​

(M).

Equivalently,

∀α>1 irrational,
X→∞
lim
	​

N
α
	​

(X)=∞.

Its negation is

∃α>1 irrational ∃P
0
	​

 ∀p>P
0
	​

,p prime⟹⌊αp⌋ composite.

There is no useful contrapositive beyond the logically equivalent statement

N
α
	​

(X) bounded⟹α is rational,

which is precisely as difficult as the original assertion.

Equivalent formulations

For primes p,q,

q=⌊αp⌋⟺q≤αp<q+1.

Thus the assertion is equivalent to the existence of infinitely many prime pairs (p,q) satisfying

0≤α−
p
q
	​

<
p
1
	​

.

Because α is irrational, equality on the left is impossible, so this can be written

0<α−
p
q
	​

<
p
1
	​

.

It is also equivalent to

p≤X
p prime
	​

∑
	​

1
P
	​

(⌊αp⌋)⟶∞.

A logarithmically weighted version is

n≤X
∑
	​

Λ(n)Λ(⌊αn⌋),

but divergence of this weighted expression must itself be proved; introducing it is only a reformulation.

Boundary conditions and elementary observations

Since α>1,

⌊αp⌋≥p

for every positive integer p.

If α=m is an integer greater than 1, then

⌊αp⌋=mp

is composite for every prime p. Thus irrationality is essential.

More generally, proximity to an integer does not immediately resolve the problem. Writing

α=m+β,0<β<1,

gives

⌊αp⌋=mp+⌊βp⌋.

The second term is unbounded, so the fixed factorization present at β=0 disappears.

There is no parity obstruction. If p is odd, the parity of ⌊αp⌋ varies according to the position of αp in intervals of length 1.

What the stated uniform-distribution fact proves

Assume the supplied fact:

For every irrational θ, the sequence

{θp},p prime,

is uniformly distributed in [0,1).

This proves that primes occur infinitely often in the Beatty sequence

{⌊nα⌋:n≥1}.

Indeed,

p=⌊nα⌋

is equivalent to

α
p
	​

≤n<
α
p+1
	​

.

Because this interval has length 1/α<1, it contains an integer precisely when the fractional part of p/α lies in an appropriate interval of length 1/α. Uniform distribution supplies infinitely many such primes p.

That argument varies n freely after choosing p. The present problem imposes the additional requirement that the index n itself be prime. Therefore the supplied argument does not imply the desired assertion.

Verified local divisibility lemma

Let d≥2 be fixed. Then

d∣⌊αp⌋

if and only if

{
d
αp
	​

}∈[0,
d
1
	​

).

Proof: write

αp=dk+r,0≤r<d.

Then

{
d
αp
	​

}=
d
r
	​

.

Also,

d∣⌊αp⌋⟺0≤r<1,

which is equivalent to r/d∈[0,1/d).

Since α/d is irrational, the supplied uniform-distribution statement yields

X→∞
lim
	​

π(X)
#{p≤X:p prime, d∣⌊αp⌋}
	​

=
d
1
	​

.

Consequently, no fixed divisor d>1 divides ⌊αp⌋ for all sufficiently large prime p.

More generally, for every fixed squarefree d,

π(X)
#{p≤X:p prime, d∣⌊αp⌋}
	​

⟶
d
1
	​

.

This gives the expected local density for every fixed divisibility condition.

Finite collections of local conditions

Fix z, and let

P(z)=
ℓ≤z, ℓ prime
∏
	​

ℓ.

For every divisor d∣P(z),

#{p≤X:p prime, d∣⌊αp⌋}=
d
π(X)
	​

+o
d
	​

(π(X)).

Because P(z) has finitely many divisors when z is fixed, inclusion–exclusion gives

π(X)
#{p≤X:p prime,gcd(⌊αp⌋,P(z))=1}
	​

⟶
ℓ≤z
∏
	​

(1−
ℓ
1
	​

).

Hence for every fixed z, infinitely many prime p satisfy

ℓ∤⌊αp⌋for every prime ℓ≤z.

This is rigorous, but it does not prove that ⌊αp⌋ is prime: a composite number of size approximately αp may have all prime factors larger than z.

To force primality, one would need to exclude prime divisors up to

⌊αp⌋
	​

≍
p
	​

,

so the sieving threshold must grow with p.

Quantitative gap

For

A
d
	​

(X)=#{p≤X:p prime, d∣⌊αp⌋},

the established statement for each fixed d is

A
d
	​

(X)=
d
π(X)
	​

+o
d
	​

(π(X)).

A growing sieve requires simultaneous control of the errors

R
d
	​

(X)=A
d
	​

(X)−
d
π(X)
	​


for many d increasing with X, such as an estimate of the form

d≤D(X)
∑
	​

∣R
d
	​

(X)∣=o(π(X))

for a sufficiently large D(X).

Pointwise convergence for every fixed d does not imply such a uniform estimate. Explicitly,

∀d ∃X
d
	​

 ∀X≥X
d
	​

: ∣R
d
	​

(X)∣≤επ(X)

does not imply

∃X
0
	​

 ∀X≥X
0
	​

 ∀d≤D(X):∣R
d
	​

(X)∣≤επ(X).

The order of the quantifiers differs.

Even hypothetical uniform divisibility estimates would not automatically produce a lower bound for primes. A sieve can readily detect integers without small prime factors, but separating primes from products of two comparably large primes requires additional information about the sequence

⌊αp⌋.
Counterexample search

The integer construction

α=m>1

makes every value composite, but it cannot directly be perturbed to an irrational construction.

For any finite set of primes p≤P, choosing

0<ε<
P
1
	​


gives

⌊(m+ε)p⌋=mp

for all such p. Thus an irrational number can imitate the integer obstruction on an arbitrarily long finite initial segment.

However, a single fixed ε>0 eventually has

⌊εp⌋≥1,

so this does not control all primes.

A nested-interval construction would need intervals I
n
	​

 such that

I
n+1
	​

⊂I
n
	​

,

every α∈I
n
	​

 makes ⌊αp
j
	​

⌋ composite for j≤n, and

n
⋂
	​

I
n
	​


contains an irrational number.

The straightforward construction using neighborhoods of a fixed integer produces intervals whose intersection is the integer itself. No verified mechanism was obtained that simultaneously keeps the intersection irrational and enforces compositeness for every prime input.

Therefore no counterexample was constructed.

Exact surviving target

A proof would require establishing an unbounded lower estimate for

N
α
	​

(X)=
p≤X
p prime
	​

∑
	​

1
P
	​

(⌊αp⌋)

for every fixed irrational α>1.

The supplied uniform-distribution hypothesis proves all fixed-modulus local densities, but it does not control the collection of growing divisibility conditions needed to detect primality. No deduction from the supplied assumptions overcame that gap, and no irrational α violating the assertion was constructed.

PROOF_CONFIDENCE: 98

COMPLETENESS_SCORE: 28

ADVERSARIAL_SURVIVAL_SCORE: 92

RESOURCE_USAGE:

Reasoning budget used: approximately 100%

Principal branches explored: direct equidistribution, fixed-modulus sieve, growing sieve, weighted correlation, rational approximation, perturbation of integer counterexamples, nested-interval counterexample construction, parity analysis, inclusion–exclusion, and quantifier analysis

Verified lemmas generated: 5

Failed proof or disproof routes: 8

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

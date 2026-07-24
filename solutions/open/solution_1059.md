# Erdős Problem #1059 [unsolved] 18%

---

## ChatGPT Response

Formalization

Let P denote the primes, and let “composite” mean a positive integer greater than 1 that is not prime.

For a prime p, define

L(p):=max{k∈N:k!<p}.

The assertion is

∀N∈N ∃p∈P,p>Nand∀k∈{1,…,L(p)}, p−k! is composite.
(T)

Equivalently, for infinitely many pairs (l,p),

l!<p≤(l+1)!,p∈P,p−k! composite for every 1≤k≤l.
(1)

For l≥2, p≤(l+1)! can be replaced by p<(l+1)!, since (l+1)! is not prime.

Negation

The negation of (T) is

∃N∈N ∀p∈P,p>N⟹∃k≥1: k!<p and p−k! is not composite.

Because p−k! is a positive integer, “not composite” means that it is either 1 or prime. Thus the negation is

∃N ∀p>N, p∈P,∃k≤L(p): p−k!∈{1}∪P.
(2)
Boundary observations

For every odd prime p>3,

p−1!=p−1

is even and greater than 2, hence composite. Thus the k=1 condition is automatic.

For k≥2, k! is even, so p−k! is odd. Consequently, parity supplies no factor for any of the genuinely difficult conditions.

If l!<p<(l+1)!, the number of conditions is exactly l. Elementary estimates give

2
l−1
≤l!<p,

and therefore

l<1+log
2
	​

p.
Verified finite congruence construction

Fix l≥1. Choose distinct primes

q
1
	​

,…,q
l
	​

>l.

The simultaneous congruences

a≡k!(modq
k
	​

),1≤k≤l,
(3)

have a solution a modulo

M=
k=1
∏
l
	​

q
k
	​


by the Chinese remainder theorem.

Moreover,

gcd(a,M)=1.

Indeed, for each k, q
k
	​

>l≥k, so q
k
	​

∤k!. From a≡k!(modq
k
	​

), it follows that q
k
	​

∤a.

Every integer

n=a+tM

then satisfies

q
k
	​

∣n−k!(1≤k≤l).

For sufficiently large t,

n−k!>q
k
	​

,

so every n−k! is composite. Hence:

For every fixed l, there are infinitely many integers n for which all n−k!, 1≤k≤l, are composite.

This does not prove the required assertion, because two additional conditions must be met simultaneously:

n must be prime,l!<n<(l+1)!.
(4)

The construction above gives a residue class with modulus M, but it supplies neither a prime in that class nor a prime below (l+1)!.

There is also a quantitative obstruction to the naive choice of distinct q
k
	​

. Since q
k
	​

>l,

M=
k=1
∏
l
	​

q
k
	​

>l
l
.

For l≥3,

(l+1)!<(l+1)
l+1
,

while M is already comparable on the logarithmic scale to the entire factorial interval. More decisively, choosing one independent modulus for every k gives no mechanism ensuring that the least positive representative, much less a prime representative, lies between l! and (l+1)!.

Structural obstruction to reusing a divisor for adjacent factorials

Suppose a prime q>l divided both

n−k!andn−(k+1)!

for some 1≤k<l. Subtracting gives

q∣(k+1)!−k!=k⋅k!.

But all prime divisors of k⋅k! are at most k≤l<q, which is impossible. Therefore:

No prime q>l can certify two adjacent differences.
	​

(5)

Thus any CRT construction using prime divisors larger than l needs distinct certifying primes for adjacent indices. This prevents the most direct attempt to compress all congruences into a very small modulus.

Other examined frameworks

The following approaches did not yield a complete argument:

Choosing p near l! gives no uniform factorization of p−k!.

Taking a prime divisor of a specially constructed integer does not transfer divisibility to p−k!.

An infinite CRT construction produces a profinite residue, not an ordinary integer satisfying infinitely many independent congruences.

Induction from one suitable prime to a larger one introduces new factorial differences not controlled by the inductive hypothesis.

A counting argument requires an upper bound for primes of the forms k!+q strong enough to leave a prime avoiding all such representations; no such bound was derived from elementary principles.

A covering-congruence construction must use divisors exceeding the corresponding k, since any prime q≤k divides k! and would force q∣p.

The proposed stronger integer statement does not immediately imply the prime statement: an integer all of whose prime factors exceed l may still be a product of several such primes.

The finite CRT lemma establishes arbitrarily long finite patterns among integers, but the simultaneous primality and factorial-window requirements remain unproved. No counterexample mechanism proving finiteness was obtained either.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100
Confidence that the verified partial statements and the conclusion that no proof or disproof has been established here are logically correct.

COMPLETENESS_SCORE: 18/100
The formalization and several structural lemmas are complete, but the infinitude assertion is neither proved nor disproved.

ADVERSARIAL_SURVIVAL_SCORE: 91/100
The stated lemmas survive the indicated boundary, quantifier, and divisibility checks; none establishes the main theorem.

RESOURCE_USAGE:
Approximately 100% of the allocated response-level reasoning budget; more than 12 conceptual branches examined; 3 verified auxiliary lemmas isolated; multiple unsuccessful construction, induction, counting, and congruence attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

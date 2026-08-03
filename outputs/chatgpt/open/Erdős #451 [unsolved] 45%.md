# Erdős Problem #451 [unsolved] 45%

---

## ChatGPT Response

Phase 0. Formalization

Let k∈Z
≥1
	​

. Define

P
k
	​

={p:p is prime and k<p<2k}.

For an integer n>2k, define

Q
k
	​

(n)=
1≤i≤k
∏
	​

(n−i).

The required integer n
k
	​

 is the least n>2k such that no prime p∈P
k
	​

 divides Q
k
	​

(n).

Equivalently,

n
k
	​

=min{n∈Z:n>2k, ∀p∈P
k
	​

, ∀i∈{1,…,k}, p∤n−i}.

Since p>k, the residues 1,…,k are distinct modulo p. Therefore

p∣Q
k
	​

(n)

if and only if

nmodp∈{1,…,k}.

So the exact modular condition is

∀p∈P
k
	​

,nmodp∈
/
{1,…,k}.

For each p∈P
k
	​

, the allowed residue classes modulo p are

0,k+1,k+2,…,p−1,

so there are exactly p−k allowed classes modulo p.

The negation is

∃p∈P
k
	​

, ∃i∈{1,…,k}n≡i(modp).

Thus n fails precisely when it lies within k steps after a multiple of some prime p∈(k,2k).

Equivalent interval formulation

Let

B
k
	​

={mp:m∈Z
≥1
	​

, p∈P
k
	​

}.

Then n fails exactly when

n∈[b+1,b+k]

for some b∈B
k
	​

.

Therefore n
k
	​

 is the first integer >2k not covered by the intervals

[b+1,b+k]b∈B
k
	​

.

This is the cleanest exact reformulation.

Exact recursive characterization

Define

F
k
	​

(C)=max({2k}∪{b+k:b∈B
k
	​

, b≤C}).

Start with

C
0
	​

=2k,C
t+1
	​

=F
k
	​

(C
t
	​

).

Then C
t
	​

 is nondecreasing. It stabilizes because a valid n exists, as shown below. Let its stable value be C
∞
	​

. Then

n
k
	​

=C
∞
	​

+1.
	​


Proof.

Assume all integers n with 2k<n≤C
t
	​

 fail. If b∈B
k
	​

 and b≤C
t
	​

, then every integer in [b+1,b+k] fails. Hence all integers up to F
k
	​

(C
t
	​

)=C
t+1
	​

 fail. By induction, every n≤C
∞
	​

 with n>2k fails.

Now suppose C
∞
	​

+1 failed. Then there would exist b∈B
k
	​

 such that

C
∞
	​

+1∈[b+1,b+k].

That implies

b≤C
∞
	​


and

b+k≥C
∞
	​

+1.

But then F
k
	​

(C
∞
	​

)≥C
∞
	​

+1, contradicting stability. Therefore C
∞
	​

+1 is valid, and it is the first valid integer.

So the exact problem is a covering problem by intervals following multiples of primes in (k,2k).

Proven upper bound

Let

M
k
	​

=
p∈P
k
	​

∏
	​

p.

If P
k
	​

=∅, then there is no forbidden prime, so

n
k
	​

=2k+1.

Otherwise choose the least multiple N of M
k
	​

 with N>2k. Then

N≤2k+M
k
	​

.

For every p∈P
k
	​

,

N≡0(modp).

Since 1≤i≤k<p,

N−i

≡0(modp).

So no p∈P
k
	​

 divides Q
k
	​

(N). Hence

n
k
	​

≤2k+M
k
	​

.
	​


Now every prime p∈(k,2k) divides the binomial coefficient

(
k
2k
	​

)

because p appears in the numerator product (k+1)(k+2)⋯(2k), but does not appear in k!. Therefore

M
k
	​

≤(
k
2k
	​

).

Also,

(
k
2k
	​

)≤
j=0
∑
2k
	​

(
j
2k
	​

)=2
2k
=4
k
.

Thus

n
k
	​

≤2k+4
k
.
	​


This proves the elementary exponential upper bound.

Proven lower bound from first multiples

Assume P
k
	​


=∅. Let

p
max
	​

(k)=maxP
k
	​

.

Every prime p∈P
k
	​

 itself lies in B
k
	​

, so the intervals

[p+1,p+k]

are all forbidden intervals.

Because all primes in P
k
	​

 lie between k and 2k, these intervals overlap or touch across the prime range. In particular, all integers

2k+1≤n≤p
max
	​

(k)+k

fail. Therefore

n
k
	​

≥p
max
	​

(k)+k+1
	​


whenever P
k
	​


=∅.

Since p
max
	​

(k)<2k, this only gives a lower bound below 3k+1, but it is rigorous and follows directly from the first layer of multiples.

Density heuristic, not a proof

The residue formulation gives an expected valid density over one full modulus M
k
	​

:

δ
k
	​

=
p∈P
k
	​

∏
	​

p
p−k
	​

=
p∈P
k
	​

∏
	​

(1−
p
k
	​

).

If one models these residue restrictions as roughly independent and uses the approximation that primes near size k have density about 1/logk, then

logδ
k
	​

≈
logk
k
	​

∫
1
2
	​

log(1−
t
1
	​

)dt.

Compute the integral:

∫
1
2
	​

log(1−
t
1
	​

)dt=∫
1
2
	​

(log(t−1)−logt)dt=−2log2.

So the heuristic density is

δ
k
	​

≈exp(−
logk
2(log2)k
	​

).

The expected first survivor is about

n
k
	​

≈exp(
logk
2(log2)k
	​

).
	​


This heuristic is subexponential in k, but larger than every fixed power k
d
. It is not proved here because it depends on distribution and independence assumptions that were not derived from the formal statement alone.

Final rigorous estimate obtained

The fully verified bounds are

p
max
	​

(k)+k+1≤n
k
	​

≤2k+4
k
	​


when P
k
	​


=∅, and

n
k
	​

=2k+1
	​


when P
k
	​

=∅.

The exact characterization is

n
k
	​

=C
∞
	​

+1
	​


where C
∞
	​

 is the stable value of

C
0
	​

=2k,C
t+1
	​

=max({2k}∪{b+k:b∈B
k
	​

, b≤C
t
	​

}).

The plausible asymptotic scale suggested by the residue density model is

n
k
	​

≈exp(
logk
2(log2)k
	​

),
	​


but that estimate is heuristic, not a proof.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92

COMPLETENESS_SCORE: 45

ADVERSARIAL_SURVIVAL_SCORE: 82

RESOURCE_USAGE: approximately 85 percent of available reasoning budget, 3 main branches explored, 6 lemmas generated, 2 failed attempts to convert the density model into a proof.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

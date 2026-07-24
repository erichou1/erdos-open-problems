# Erdős Problem #387 [unsolved] 35%

---

## ChatGPT Response

Complete formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.

The question asks whether

∃c>0 ∀n≥2 ∀k∈{1,…,n−1} ∃d∈Z
>0
	​


such that

d∣(
k
n
	​

)andcn<d≤n.

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

so it is enough to consider

m=min(k,n−k),1≤m≤n/2.

The target becomes:

∃c>0 ∀n≥2 ∀1≤m≤n/2 ∃d∣(
m
n
	​

)withcn<d≤n.

The negation is:

∀c>0 ∃n≥2 ∃1≤m≤n/2

such that every divisor d∣(
m
n
	​

) satisfying d≤n also satisfies

d≤cn.

Equivalently, if

D(n,m)=max{d:d∣(
m
n
	​

), d≤n},

then the problem asks whether

n≥2, 1≤m≤n/2
inf
	​

n
D(n,m)
	​

>0.

Thus the whole problem is the positivity of the normalized maximal small divisor

ρ(n,m)=
n
D(n,m)
	​

.
Verified elementary facts
Lemma 1: endpoint divisor

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

Since

gcd(
g
k
	​

,
g
n
	​

)=1,

we get

g
n
	​

∣(
k
n
	​

).

Therefore

D(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

This proves the weaker bound

D(n,k)≥
k
n
	​

.

It is not enough for an absolute constant, because when k∼
n
	​

, this gives only D(n,k)≥
n
	​

, hence

n
D(n,k)
	​

≥
n
	​

1
	​

→0.

So this lemma alone cannot solve the problem.

Lemma 2: large-prime divisor when m is linearly large

Using the Sylvester–Schur principle in the following exact form:

If x+1,x+2,…,x+m are m consecutive integers all exceeding m, then their product has a prime divisor p>m.

Apply this to

n−m+1,n−m+2,…,n.

Since m≤n/2, every term is >m. Hence

(n−m+1)⋯n

has a prime divisor p>m. Because p>m, this prime cannot divide m!. Therefore

p∣(
m
n
	​

).

Also p≤n, since p divides one of the numerator factors. Hence

D(n,m)≥p>m.

Therefore, whenever

m≥αn,

we get

D(n,m)>αn.

So the desired result is proved in the range

m≫n.

The hard range is

m=o(n),

especially the transition regime

m≈n
θ
,0<θ<1.
Lemma 3: small fixed m is harmless

For fixed m, the endpoint-divisor bound gives

D(n,m)≥
m
n
	​

.

Thus for each fixed M, if

1≤m≤M,

then

D(n,m)≥
M
n
	​

.

So bounded m causes no obstruction. The unresolved range is where

m→∞andm=o(n).
Equivalent divisor formulation

For 1≤m≤n/2,

(
m
n
	​

)=
m!
(n−m+1)(n−m+2)⋯n
	​

.

A number d∈(n/2,n] dividing (
m
n
	​

) would be especially strong. In fact computationally and heuristically one is led to the stronger possible statement:

∃a∈{n−m+1,…,n}such thata∣(
m
n
	​

).

If true, this would prove the original problem with

c=
2
1
	​

,

because every numerator factor satisfies

a≥n−m+1>n/2.

This stronger statement is equivalent to saying that for some numerator factor a,

m!∣
b=n−m+1
b

=a
	​

∏
n
	​

b.

In p-adic form, define

E
p
	​

=v
p
	​

(m!),N
p
	​

=
j=0
∑
m−1
	​

v
p
	​

(n−j),S
p
	​

=N
p
	​

−E
p
	​

=v
p
	​

(
m
n
	​

).

Then a∣(
m
n
	​

) is equivalent to

v
p
	​

(a)≤S
p
	​


for every prime p. Thus the stronger c=1/2 theorem would follow if one could always find a numerator factor whose p-adic valuation is never larger than the surplus S
p
	​

.

That is a clean reformulation, but it does not by itself prove the statement.

Strategy search

I tested the following independent routes logically.

1. Direct endpoint divisibility

Use

gcd(n,m)
n
	​

∣(
m
n
	​

).

Works for m bounded, fails for m→∞.

2. Sylvester–Schur large prime

Gives a prime divisor

p>m.

Works when m≥cn, fails when m=o(n).

3. Combine endpoint divisor and Sylvester prime

We have divisors roughly

m
n
	​

and>m.

Their maximum is at least

max(m,
m
n
	​

).

But the minimum of this expression occurs near m=
n
	​

, where it is only 
n
	​

, not a positive fraction of n. So this does not prove the theorem.

4. Try to force a numerator factor to divide (
m
n
	​

)

This would prove c=1/2. The condition becomes

m!∣
b

=a
∏
	​

b.

The p-adic surplus reformulation is exact, but I did not obtain a proof that an admissible a always exists.

5. Pair denominator factors with numerator factors

If one could assign denominator factors 1,2,…,m to numerator factors so that one numerator factor remains uncancelled, then that remaining factor would divide (
m
n
	​

). But a full divisibility matching can fail. For example, the interval

5,6,7,8

with m=4 has no perfect matching i∣a
i
	​

 using all i=1,2,3,4, even though

7∣(
4
8
	​

).

So matching is too strong.

6. Prime-power surplus covering

For each prime p, define the surplus

S
p
	​

=v
p
	​

(
m
n
	​

).

A numerator term a is bad for p if

v
p
	​

(a)>S
p
	​

.

A term divides (
m
n
	​

) iff it is bad for no prime. The problem becomes showing that the union of bad sets does not cover the whole numerator interval. I did not find a complete covering argument.

7. Greedy divisor construction from prime factors

Let D be the largest divisor of (
m
n
	​

) at most n. If D≤cn, then every unused prime factor p of (
m
n
	​

)/D must satisfy

pD>n,

so

p>
D
n
	​

≥
c
1
	​

.

Thus D saturates all small prime factors. This gives structural information, but I did not obtain a contradiction.

8. Use many primes >m

Applying large-prime arguments to related binomial coefficients suggests that (
m
n
	​

) often has many prime divisors >m. However, products of several medium-sized primes can still skip the interval (cn,n]. For example, two primes near 
n
	​

 can have divisors only near 1,
n
	​

,n. This approach did not close the divisor-placement gap.

9. Smooth/rough factor split

Write each numerator factor as

a=s(a)r(a),

where s(a) is composed of primes ≤m and r(a) uses primes >m. Large r(a) would immediately give useful divisors. But proving that the rough parts contain a subset product in (cn,n] requires stronger control than the elementary estimates provide.

10. Induction on m

Using

(
m
n
	​

)=
m
n
	​

(
m−1
n−1
	​

)

gives divisibility information, but the factor m in the denominator can destroy divisors inherited from (
m−1
n−1
	​

). I did not obtain a clean induction invariant.

11. Cyclic action on m-subsets

The cyclic group of order n acting on m-subsets gives the divisor

gcd(n,m)
n
	​

∣(
m
n
	​

).

This recovers Lemma 1 but does not produce a constant fraction of n in the difficult range.

12. Counterexample construction

To disprove the statement, one would need a sequence (n
j
	​

,m
j
	​

) such that

D(n
j
	​

,m
j
	​

)=o(n
j
	​

).

The natural obstruction regime is

m
j
	​

→∞,m
j
	​

=o(n
j
	​

),

especially m
j
	​

≈
n
j
	​

	​

. However, the elementary constructions I tested symbolically do not force all divisors ≤n to stay sublinear.

Verified partial conclusion

The following is rigorously established from the elementary arguments above:

D(n,m)≥max(
m
n
	​

,m)

for all 1≤m≤n/2.

Indeed,

D(n,m)≥
m
n
	​


by Lemma 1, and

D(n,m)>m

by Sylvester–Schur.

Therefore

D(n,m)≥
n
	​


for all m, because

max(m,
m
n
	​

)≥
n
	​

.

So every binomial coefficient (
k
n
	​

) has a divisor d≤n satisfying

d≥
n
	​

.

But this is far weaker than the desired

d≥cn.

The remaining gap is precisely the improvement

n
	​

⟶cn.

I did not obtain a proof or disproof of that strengthening from the allowed elementary deductions.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas above.

COMPLETENESS_SCORE: 35, because the main constant-fraction statement was not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 95 for the partial results; the proposed stronger c=1/2 route remains unproved.

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; 12 branches explored; 3 verified lemmas generated; multiple failed proof attempts identified.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

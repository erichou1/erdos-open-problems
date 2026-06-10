# Erdős Problem #208 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Complete formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.
Formal statement

The target theorem is

∃c>0 ∀n∈N ∀k∈N(1≤k<n⟹∃d∈N:d∣(
k
n
	​

) ∧ cn<d≤n).
Quantifier structure
∃c>0∀n≥2∀k∈{1,…,n−1}∃d.

The constant c must be independent of both n and k.

Negation

The negation is

∀c>0 ∃n≥2 ∃k∈{1,…,n−1}∀d∈N,(d∣(
k
n
	​

) ∧ d≤n)⟹d≤cn.

Equivalently, if

D(n,k)=max{d≤n:d∣(
k
n
	​

)},

then the target is

∃c>0 ∀n,k,D(n,k)>cn,

and the negation is

1≤k<n
inf
	​

n
D(n,k)
	​

=0.
Symmetry

Since

(
k
n
	​

)=(
n−k
n
	​

),

we may always replace k by n−k. Therefore it is enough to study

1≤k≤
2
n
	​

.
Boundary cases

If k=1, then

(
1
n
	​

)=n,

so d=n works for every c<1.

If k=2,

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
If n is even, then n−1∣(
2
n
	​

).
Thus for k=2, there is always a divisor >n/2.

The case n=4,k=2 gives

(
2
4
	​

)=6,

whose divisors ≤4 are 1,2,3. Thus no divisor lies in (3,4]. Therefore no universal result with c≥3/4 can hold using a strict lower endpoint.

So the best possible constant, if the strongest pattern were true, would have to satisfy

c<
4
3
	​

.
Verified lemmas
Lemma 1: The elementary divisor n/gcd(n,k)

Let g=gcd(n,k). Then

g
n
	​

∣(
k
n
	​

).
Proof

We use

(
k
n
	​

)=
k
n
	​

(
k−1
n−1
	​

).

Write

n=gn
′
,k=gk
′
,gcd(n
′
,k
′
)=1.

Then

(
k
n
	​

)=
k
′
n
′
	​

(
k−1
n−1
	​

).

Since (
k
n
	​

) is an integer and gcd(n
′
,k
′
)=1, we must have

k
′
∣(
k−1
n−1
	​

).

Therefore

(
k
n
	​

)=n
′
⋅
k
′
1
	​

(
k−1
n−1
	​

),

so

n
′
=
gcd(n,k)
n
	​

∣(
k
n
	​

).

Thus

D(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

This proves the easy lower bound

D(n,k)≥
k
n
	​

.

This alone does not prove the desired theorem, because k may grow with n.

Lemma 2: p-adic criterion

For a prime p,

v
p
	​

((
k
n
	​

))=
a≥1
∑
	​

(⌊
p
a
n
	​

⌋−⌊
p
a
k
	​

⌋−⌊
p
a
n−k
	​

⌋).

Each summand is 0 or 1. Hence p
a
 contributes to (
k
n
	​

) exactly when the interval

(n−k,n]

contains more multiples of p
a
 than the interval

[1,k].

This gives a precise divisibility test for any proposed divisor d≤n.

Lemma 3: Rough parts of the top interval divide the binomial coefficient

Assume

1≤k≤
2
n
	​

.

For each

m∈{n−k+1,…,n},

write

m=s
m
	​

r
m
	​

,

where every prime divisor of s
m
	​

 is ≤k, and every prime divisor of r
m
	​

 is >k.

Then

R:=
m=n−k+1
∏
n
	​

r
m
	​


divides

(
k
n
	​

).
Proof

The numerator of (
k
n
	​

) is

m=n−k+1
∏
n
	​

m=(∏s
m
	​

)(∏r
m
	​

).

The denominator k! has no prime factor >k. Therefore no prime factor of any r
m
	​

 can be canceled by the denominator.

Also, if a prime p>k divided two distinct numbers in the interval (n−k,n], their difference would be a positive multiple of p, but the difference is <k<p, impossible. Thus the r
m
	​

 are pairwise coprime.

Therefore all r
m
	​

 survive in the binomial coefficient, and

R∣(
k
n
	​

).

This is a useful structural lemma, but it does not by itself produce a divisor in (cn,n]. It creates a subset-product problem among the r
m
	​

.

Phase 1: Breadth-first search of strategies

I generated the following independent approaches.

Strategy	Idea	Obstacle
Direct proof with n/gcd(n,k)	Use Lemma 1	Only gives n/k, not constant times n
Strengthen to D(n,k)>n/2	Empirically plausible and would imply result	No proof found
Prove divisor in (n−k,n]	Would imply >n/2 after symmetry	False in given examples
Prove divisor in (n−Ck
A
,n]	Handles small k	Does not cover k growing like n
α

Prime divisor approach	Find prime p>cn dividing (
k
n
	​

)	Fails when all guaranteed primes are only O(k)
Product of large primes	Use primes >k from top interval	Becomes hard subset-product problem
Smooth/rough factorization	Split top interval into k-smooth and k-rough parts	Need uniform divisor-density lemma
Maximal divisor D(n,k)	Study obstruction D≤cn	Gives constraints but no contradiction
Cardinal/logarithmic subset sums	Work with logarithms of available prime factors	Needs a dense subset-sum theorem not proved
Induction on n or k	Use Pascal or multiplicative recurrences	Divisibility does not behave well under addition
Cyclic group action	n/gcd(n,k) arises from necklace orbits	Recovers Lemma 1 only
Counterexample construction	Try to force all divisors ≤n to be o(n)	No explicit construction found

Top three after ranking:

Rough/smooth factorization.

Maximal divisor obstruction.

Attempted strengthening D(n,k)>n/2.

Phase 2: New definitions and invariants
Definition: largest admissible divisor
D(n,k)=max{d≤n:d∣(
k
n
	​

)}.

Target:

n,k
inf
	​

n
D(n,k)
	​

>0.
Definition: k-rough part of the top interval

For m∈(n−k,n], define

r
k
	​

(m)=
p
a
∥m
p>k
	​

∏
	​

p
a
.

Then

m=n−k+1
∏
n
	​

r
k
	​

(m)∣(
k
n
	​

).
Definition: k-smooth residual quotient

Let

s
k
	​

(m)=
r
k
	​

(m)
m
	​

.

Then

(
k
n
	​

)=(∏r
k
	​

(m))⋅
k!
∏s
k
	​

(m)
	​

.

The second factor is an integer.

Definition: divisor-density obstruction

For a finite set of pairwise coprime integers a
1
	​

,…,a
t
	​

, define

M
X
	​

(a
1
	​

,…,a
t
	​

)=max{
i∈I
∏
	​

a
i
	​

:
i∈I
∏
	​

a
i
	​

≤X}.

A possible route would be to prove a uniform lower bound

M
n
	​

(r
k
	​

(n−k+1),…,r
k
	​

(n))≫n.

This would imply the target theorem.

But I could not prove such a bound from first principles.

Phase 3: Parallel exploration
Branch A: Try to prove the stronger statement D(n,k)>n/2
Target

Prove

∀n,k,D(n,k)>
2
n
	​

.

This would imply the original statement with every c<1/2.

Verified special cases

For k=1, D(n,1)=n.

For k=2, D(n,2)>n/2.

For k=3, one can verify by residue classes that a divisor >n/2 always exists, but I did not complete a clean uniform proof for all residue classes without expanding into many cases.

Obstruction

The statement

∃m∈(n−k,n]m∣(
k
n
	​

)

is false in general. Therefore the divisor >n/2, if it exists, may be a nontrivial product of prime powers drawn from several numerator terms.

That turns the problem into a subset-product problem inside the factorization of (
k
n
	​

).

Gap node A1

Prove:

Among the prime-power factors of (
k
n
	​

) there is a subproduct in (n/2,n].

I tried the following attacks:

Greedy multiplication by prime factors.

Greedy multiplication by prime powers.

Logarithmic subset sums.

Pairwise coprime rough parts.

Smooth part adjustment.

Maximal divisor contradiction.

Induction on k.

Induction on n.

Splitting k≤
n
	​

, k>
n
	​

.

Separating small and large primes.

None produced a complete proof.

Branch A remains unresolved.

Branch B: Use the divisor n/gcd(n,k) and amplify it

Lemma 1 gives

d
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

Let

g=gcd(n,k).

If g is bounded, then d
0
	​

≫n, and we are done.

The hard case is

g→∞.

To improve Lemma 1, one would need to find a divisor t of

n/g
(
k
n
	​

)
	​


with

cg<t≤g.

Then

d=d
0
	​

t

would satisfy

cn<d≤n.
Gap node B1

Prove:

n/gcd(n,k)
(
k
n
	​

)
	​


has a divisor in (cgcd(n,k),gcd(n,k)], for some absolute c>0.

This would imply the original theorem.

Attacks attempted

Express residual through (
k−1
n−1
	​

).

Use k/g∣(
k−1
n−1
	​

).

Try to identify a binomial coefficient inside the quotient.

Apply induction to (n−1,k−1).

Use p-adic valuation comparison.

Study only primes dividing g.

Try to prove the quotient contains the full g-part.

Search for counterexamples where the quotient is coprime to large parts of g.

Use cyclic group actions.

Use divisor-density of the quotient.

The main obstruction is that the quotient does not have a clean binomial form. I could not prove the required divisor amplification.

Branch B remains unresolved.

Branch C: Maximal-divisor obstruction

Let

D=D(n,k)=max{d≤n:d∣(
k
n
	​

)}.

Assume toward contradiction that

D≤cn.

Then for every prime p such that p∣(
k
n
	​

)/D, maximality of D implies

Dp>n.

Therefore

p>
D
n
	​

≥
c
1
	​

.

So every prime factor ≤1/c of (
k
n
	​

) must already occur fully inside D.

Thus

p≤1/c
∏
	​

p
v
p
	​

((
k
n
	​

))
∣D.

If one could prove

p≤1/c
∏
	​

p
v
p
	​

((
k
n
	​

))
>cn

for all sufficiently difficult cases, then contradiction would follow.

Obstruction

This lower bound is false in trivial cases such as k=1, where the binomial coefficient may have no small prime factors. Those cases are handled by Lemma 1, but the mixed cases remain difficult.

One needs a dichotomy:

Either

gcd(n,k)
n
	​

>cn,

or the small-prime part of (
k
n
	​

) is >cn.

I could not prove such a dichotomy.

Branch C remains unresolved.

Phase 4: Local verification of accepted lemmas
Lemma 1 attack

Claim:

gcd(n,k)
n
	​

∣(
k
n
	​

).

Possible failure point: assuming k
′
∣(
k−1
n−1
	​

).

But since

(
k
n
	​

)=
k
′
n
′
	​

(
k−1
n−1
	​

)

is an integer and gcd(n
′
,k
′
)=1, Euclid’s lemma gives

k
′
∣(
k−1
n−1
	​

).

No gap.

Lemma 1 survives.

Lemma 2 attack

This is Legendre’s formula applied to

(
k
n
	​

)=
k!(n−k)!
n!
	​

.

For each prime p,

v
p
	​

(m!)=
a≥1
∑
	​

⌊
p
a
m
	​

⌋.

Substitution gives the stated formula.

No gap.

Lemma 2 survives.

Lemma 3 attack

Possible issue: A prime p>k could divide two top interval terms.

But if p∣m
1
	​

,m
2
	​

, then p∣∣m
1
	​

−m
2
	​

∣. Since

0<∣m
1
	​

−m
2
	​

∣<k<p,

impossible.

Possible issue: denominator k! cancels a prime >k.

Impossible, since every prime divisor of k! is ≤k.

Lemma 3 survives.

Dependency graph of verified results
Legendre formula⇒Lemma 2.
(
k
n
	​

)=
k
n
	​

(
k−1
n−1
	​

)⇒Lemma 1.
Top interval factorization+denominator primes ≤k⇒Lemma 3.

None of the verified lemmas alone implies the main theorem.

Exact unresolved core

The strongest unresolved formulation reached is:

Does there exist c>0 such that every divisor set of (
k
n
	​

) contains an element in (cn,n]?
	​


The most concrete technical gap is the following subset-product statement.

Let

r
m
	​

=r
k
	​

(m)

be the k-rough part of each m∈(n−k,n]. Since

∏r
m
	​

∣(
k
n
	​

),

it would be enough to prove that some subset product of the r
m
	​

, possibly multiplied by a controlled divisor of the smooth residual factor, lies in (cn,n].

I could not prove that.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas; 0 for the unresolved main theorem.

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 90 for the partial lemmas; 20 for the overall attempted proof program.

RESOURCE_USAGE: approximately 100% of this response’s reasoning budget used; 3 main branches explored; 3 verified lemmas generated; 3 major failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

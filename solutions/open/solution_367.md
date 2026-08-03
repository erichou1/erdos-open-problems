# Erdős Problem #367 [unsolved] 35%

---

## ChatGPT Response

Formal statement

Let

B(n,k)=(
k
n
	​

),1≤k<n.

Define

D(n,k)=max{d∈Z
≥1
	​

:d∣B(n,k), d≤n}.

The problem asks whether

∃c>0 ∀n≥2 ∀k∈{1,…,n−1}:D(n,k)>cn.

Equivalently,

n≥2, 1≤k<n
inf
	​

n
D(n,k)
	​

>0.

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

1≤k≤
2
n
	​

.

The negation is

∀c>0 ∃n≥2 ∃k<n

such that every divisor d∣(
k
n
	​

) with d≤n satisfies

d≤cn.

Equivalently, there is a sequence (n
j
	​

,k
j
	​

) with

n
j
	​

D(n
j
	​

,k
j
	​

)
	​

→0.
Verified theorem pool
Lemma 1: the elementary divisor

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

Let g=gcd(n,k), n=gn
0
	​

, k=gk
0
	​

, gcd(n
0
	​

,k
0
	​

)=1. Then

(
k
n
	​

)=
k
0
	​

n
0
	​

	​

(
k−1
n−1
	​

).

Since the left side is an integer and gcd(n
0
	​

,k
0
	​

)=1, we have k
0
	​

∣(
k−1
n−1
	​

), hence n
0
	​

=n/gcd(n,k)∣(
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

So the problem is immediately solved for bounded k. The hard regime must have k→∞.

Lemma 2: subset cancellation divisor

Let

I={n−k+1,n−k+2,…,n}.

For any subset S⊆I, define

P
S
	​

=
m∈S
∏
	​

m.

Then

gcd(P
S
	​

,k!)
P
S
	​

	​

∣(
k
n
	​

).

Proof: Write

(
k
n
	​

)=
k!
P
S
	​

R
	​


where R is the product of the numerator terms not in S. Let

g=gcd(P
S
	​

,k!),P
S
	​

=gP
′
,k!=gK
′
,

so gcd(P
′
,K
′
)=1. Then

(
k
n
	​

)=
K
′
P
′
R
	​

.

Since (
k
n
	​

)∈Z and gcd(P
′
,K
′
)=1, we get K
′
∣R. Hence

(
k
n
	​

)=P
′
⋅
K
′
R
	​

,

so P
′
=P
S
	​

/gcd(P
S
	​

,k!)∣(
k
n
	​

).

This gives many explicit divisors, including each singleton divisor

gcd(m,k!)
m
	​

∣(
k
n
	​

),n−k+1≤m≤n.
Lemma 3: lcm quotient divisor

Let

L=lcm(n−k+1,…,n),M=lcm(1,…,k).

Then

M∣L

and

M
L
	​

∣(
k
n
	​

).

Proof: Fix a prime p. Let

α=
1≤i≤k
max
	​

v
p
	​

(i),β=
n−k+1≤m≤n
max
	​

v
p
	​

(m).

Because every block of k consecutive integers contains a multiple of every prime power p
a
≤k, we have β≥α, so M∣L.

Now we need to show

β−α≤v
p
	​

((
k
n
	​

)).

Write

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

(#{m∈[n−k+1,n]:p
a
∣m}−#{i∈[1,k]:p
a
∣i}).

For each a≤α, the interval of length k contains at least ⌊k/p
a
⌋ multiples of p
a
, matching the count in [1,k]. For α<a≤β, the denominator contributes zero multiples of p
a
, while the numerator contributes at least one. Thus the total excess valuation is at least β−α. Therefore

v
p
	​

(L/M)≤v
p
	​

((
k
n
	​

))

for every prime p, proving L/M∣(
k
n
	​

).

Extremal and boundary cases

For k=1,

(
1
n
	​

)=n,

so D(n,1)=n.

For k=n−1,

(
n−1
n
	​

)=n,

so again D(n,n−1)=n.

For k=2,

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

). If n is even, then n−1∣(
2
n
	​

). Hence

D(n,2)>
2
n
	​

.

Thus any counterexample sequence must have

k→∞,n−k→∞.
Reformulation through the maximal divisor

Let

B=(
k
n
	​

),D=D(n,k).

Assume, for contradiction against a candidate c, that

D≤cn.

Set

y=
D
n
	​

.

Then

D=
y
n
	​

.

From Lemma 1,

D≥
k
n
	​

,

so

y≤k.

If D≤n/2, then y≥2.

Now use maximality of D. If p is a prime such that

v
p
	​

(D)<v
p
	​

(B),

then Dp∣B. Since D was the largest divisor of B not exceeding n, we must have

Dp>n.

Therefore

p>
D
n
	​

=y.

So:

Every prime p≤y occurs in D with its full exponent from B.
	​


Equivalently, if a counterexample sequence has D(n
j
	​

,k
j
	​

)/n
j
	​

→0, then y
j
	​

=n
j
	​

/D(n
j
	​

,k
j
	​

)→∞, and the maximal divisor D(n
j
	​

,k
j
	​

) contains the entire y
j
	​

-smooth part of (
k
j
	​

n
j
	​

	​

).

This is a strong necessary condition for counterexamples.

Twelve independent strategies
Strategy	Core idea	Verified progress	Obstacle
Direct divisor construction	Use n/gcd(n,k), singleton divisors, subset divisors	Lemmas 1 and 2	Does not force a uniform fraction of n
Maximal-divisor contradiction	Let D be largest divisor ≤n; show D≫n	Full small-prime containment proved	Need global lower bound from smooth part
LCM structure	Use L/M∣(
k
n
	​

)	Lemma 3 proved	L/M may still lack a divisor near n
Prime-divisor route	Force a prime divisor >cn	Works in some dense regimes	Requires control of primes/multiples in short intervals
Subset-product route	Use many divisors P
S
	​

/gcd(P
S
	​

,k!)	Divisibility proved	Need a subset landing inside (cn,n]
Induction on k	Relate (
k
n
	​

) to (
k−1
n−1
	​

)	Identities available	Divisibility is not preserved cleanly
Induction on n	Use Pascal-type recurrences	Structural identities available	Additive identities do not preserve divisors
p-adic valuation route	Use Legendre valuation formula	Exact valuations available	Lower bounds are irregular because of carries/floor terms
Smooth/rough decomposition	Split (
k
n
	​

) into small-prime and large-prime parts	Necessary condition proved	Need divisor-packing theorem for mixed parts
Density of divisors	Show divisors of (
k
n
	​

) are multiplicatively dense near n	Works for smooth integers	Large primes create gaps
Counterexample construction	Try to force all divisors ≤n below cn	Necessary conditions derived	Binomial structure resists simple construction
Auxiliary lcm graph	Model denominator cancellation as a matching problem	Lemma 2 is first step	Matching must preserve divisor size, not only integrality

Top three by expected value:

Maximal-divisor contradiction.

Subset-product construction.

Smooth/rough decomposition.

Branch A: maximal-divisor contradiction

Target:

∃c>0D(n,k)>cnfor all n,k.

Assume the negation. Then there are (n
j
	​

,k
j
	​

) with

n
j
	​

D
j
	​

	​

→0.

Set

y
j
	​

=
D
j
	​

n
j
	​

	​

→∞.

By Lemma 1,

D
j
	​

≥
k
j
	​

n
j
	​

	​

,

so

y
j
	​

≤k
j
	​

.

Thus k
j
	​

→∞.

By maximality of D
j
	​

, every prime p≤y
j
	​

 occurs in D
j
	​

 with full exponent from (
k
j
	​

n
j
	​

	​

). Therefore the y
j
	​

-smooth part of (
k
j
	​

n
j
	​

	​

) is at most

D
j
	​

=
y
j
	​

n
j
	​

	​

.

So a counterexample sequence must satisfy:

p≤y
j
	​

∏
	​

p
v
p
	​

((
k
j
	​

n
j
	​

	​

))
≤
y
j
	​

n
j
	​

	​

.

This is a strong structural constraint.

GAP_NODE A

Prove that for some absolute C,

p≤y
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
>
y
n
	​


whenever 2≤y≤k, except when another divisor of (
k
n
	​

) already lies in (cn,n].

Attempts:

Direct Legendre lower bound: fails because v
p
	​

(
k
n
	​

) can vanish for many small p.

Carry-count formulation: exact but irregular.

Average over primes p≤y: insufficient without distribution input.

Use only p=2: fails when (
k
n
	​

) is odd.

Use product over prime powers: same obstruction.

Pair numerator and denominator terms: gives Lemma 2 but not a uniform-size divisor.

Use lcm quotient: gives Lemma 3 but not enough.

Search for contradiction from y≤k: not sufficient alone.

Try to force a rough prime >y into (cn,n]: fails when rough primes cluster below cn.

Try to combine rough primes with the y-smooth part: becomes a divisor-packing problem still unresolved.

Branch A does not close.

Branch B: subset-product construction

By Lemma 2, for every S⊆[n−k+1,n],

Q
S
	​

=
gcd(∏
m∈S
	​

m,k!)
∏
m∈S
	​

m
	​


divides (
k
n
	​

).

If one can prove that for some absolute c>0 there always exists S with

cn<Q
S
	​

≤n,

then the problem is solved.

Singletons give

Q
{m}
	​

=
gcd(m,k!)
m
	​

.

If for some m∈[n−k+1,n],

gcd(m,k!)<
cn
m
	​

,

then Q
{m}
	​

>cn, and since Q
{m}
	​

≤m≤n, we are done.

Thus a counterexample must force

gcd(m,k!)≥
cn
m
	​


for every m∈[n−k+1,n].

If c→0, this says every one of the last k numerator terms must have a very large divisor supported only on primes ≤k. That is restrictive.

GAP_NODE B

Show that not all k consecutive integers near n can have enough k!-supported part to prevent every Q
S
	​

 from landing in (cn,n].

Attacks:

Use product over all singleton lower bounds: gives a large product but not a single divisor.

Greedy multiply Q
{m}
	​

: overshoot can jump past n.

Use minimal subset with Q
S
	​

>cn: overshoot not controlled.

Use prime-factor ordering: large prime factors create gaps.

Use smoothness estimates: would need unproved distribution input.

Use exact p-adic budget of k!: promising but incomplete.

Pair terms sharing denominator factors: matching problem unresolved.

Use consecutive structure modulo prime powers: gives Lemma 3 only.

Try dyadic target intervals (n/2,n], (n/4,n/2], etc.: no closure.

Try induction on subset size: quotient Q
S
	​

 is not monotone enough.

Branch B does not close.

Branch C: lcm quotient

We have proved

Q=
lcm(1,…,k)
lcm(n−k+1,…,n)
	​

∣(
k
n
	​

).

If Q has a divisor in (cn,n], then we are done.

This route succeeds in many structural cases, especially when the interval [n−k+1,n] contains large prime powers or primes whose contribution is not canceled by lcm(1,…,k).

But Q records only maximal prime-power excess. It discards multiplicity. The full binomial coefficient may contain useful additional small factors that Q misses.

GAP_NODE C

Prove that either Q itself has a divisor in (cn,n], or the multiplicity discarded by the lcm quotient supplies enough small factors to combine with a divisor of Q.

Attacks:

Largest divisor of Q≤n: can be too small.

Multiply by discarded small-prime part: promising but no uniform packing lemma.

Use prime powers exceeding k: not enough when residual prime base is small.

Use lcm quotient recursively on smaller intervals: no clear invariant.

Use Q∣B and maximal divisor D: folds back into Branch A.

Separate Q-rough and Q-smooth components: unresolved packing.

Use interval length k to bound missing multiplicity: partial only.

Compare L/M with n: Q may be much larger than n.

Compare L/M with n/k: too weak.

Try to force a divisor of Q in every dyadic interval: false for general Q, not proved for this Q.

Branch C does not close.

Dependency graph of verified results

Definitions:

B(n,k)=(
k
n
	​

),D(n,k)=max{d∣B(n,k):d≤n}.

Verified lemmas:

Symmetry:

B(n,k)=B(n,n−k).

Elementary divisor:

gcd(n,k)
n
	​

∣B(n,k).

Lower bound:

D(n,k)≥
k
n
	​

.

Subset cancellation:

gcd(P
S
	​

,k!)
P
S
	​

	​

∣B(n,k).

Lcm quotient:

lcm(1,…,k)
lcm(n−k+1,…,n)
	​

∣B(n,k).

Maximal-divisor smooth containment:
If D=D(n,k), y=n/D, and D≤n/2, then every prime p≤y occurs in D with its full exponent from B(n,k).

Unresolved primary target:

n,k
inf
	​

n
D(n,k)
	​

>0.

No verified theorem in the dependency graph proves this final target.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas; 0 for the unresolved original statement.

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 90 for the partial results; the full proof was not obtained.

RESOURCE_USAGE: approximately 90% of the available reasoning budget; 3 main branches explored; 6 verified lemmas generated; 3 major failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning presented here was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

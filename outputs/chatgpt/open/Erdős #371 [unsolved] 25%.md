# Erdős Problem #371 [unsolved] 25%

---

## ChatGPT Response

Phase 0: complete formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.

Define

D(n,k)=max{d∈N:d∣B(n,k), d≤n}.

The problem is exactly:

∃c>0 ∀n≥2 ∀k∈{1,…,n−1}:D(n,k)>cn.

Equivalently,

n≥2, 1≤k<n
inf
	​

n
D(n,k)
	​

>0.

Negation:

∀c>0 ∃n≥2 ∃1≤k<n:∀d∣(
k
n
	​

), d≤n⇒d≤cn.

Equivalently,

n,k
inf
	​

n
D(n,k)
	​

=0.

Symmetry:

(
k
n
	​

)=(
n−k
n
	​

),

so it suffices to study

1≤k≤n/2.

Boundary cases:

k=1:(
1
n
	​

)=n,D(n,1)=n.
k=2:(
2
n
	​

)=
2
n(n−1)
	​

.

If n is odd, n∣(
2
n
	​

). If n is even, n−1∣(
2
n
	​

). Thus

D(n,2)≥n−1.

The hard regime is therefore neither very small k nor k extremely close to n, but intermediate k, especially after symmetry 3≤k≤n/2.

Verified divisor structure

Write

P(n,k)=
a=n−k+1
∏
n
	​

a.

Then

(
k
n
	​

)=
k!
P(n,k)
	​

.

For each top factor a∈[n−k+1,n], define its residual core

q
a
	​

=
gcd(a,k!)
a
	​

.
Lemma 1: each q
a
	​

 divides (
k
n
	​

)

Fix a∈[n−k+1,n]. Since a∣P(n,k), and (
k
n
	​

)=P(n,k)/k!, for every prime p,

v
p
	​

(q
a
	​

)=max{v
p
	​

(a)−v
p
	​

(k!),0}.

Also

v
p
	​

((
k
n
	​

))=v
p
	​

(P(n,k))−v
p
	​

(k!)≥v
p
	​

(a)−v
p
	​

(k!).

Therefore

v
p
	​

(q
a
	​

)≤v
p
	​

((
k
n
	​

))

for every prime p. Hence

q
a
	​

∣(
k
n
	​

).

So every top factor contributes a canonical divisor of the binomial coefficient.

Lemma 2: the q
a
	​

 are pairwise coprime

Take distinct

a,b∈[n−k+1,n].

Then

0<∣a−b∣<k.

Suppose a prime p divides both q
a
	​

 and q
b
	​

. Then

v
p
	​

(a)>v
p
	​

(k!),v
p
	​

(b)>v
p
	​

(k!).

Hence

p
v
p
	​

(k!)+1
∣a,p
v
p
	​

(k!)+1
∣b,

so

p
v
p
	​

(k!)+1
∣∣a−b∣.

But p
v
p
	​

(k!)+1
>k. Indeed, if p
t
≤k<p
t+1
, then p
t
 appears among the factors of k!, so

v
p
	​

(k!)≥t,

and therefore

p
v
p
	​

(k!)+1
≥p
t+1
>k.

Thus p
v
p
	​

(k!)+1
∣∣a−b∣ is impossible because

0<∣a−b∣<k.

Therefore no prime divides both q
a
	​

 and q
b
	​

, so

gcd(q
a
	​

,q
b
	​

)=1.
Corollary 3: every product of distinct residual cores divides (
k
n
	​

)

Because the q
a
	​

 are pairwise coprime and each divides (
k
n
	​

), for every subset

S⊆{n−k+1,…,n},

we have

a∈S
∏
	​

q
a
	​

∣(
k
n
	​

).

Thus the problem becomes partly a subset-product problem: can one always choose residual core factors, or prime factors of those cores, whose product lies in (cn,n]?

Breadth-first strategy search

I considered the following independent routes.

Strategy	Target	Obstacle
Direct large-prime proof	Find a prime divisor p>cn of (
k
n
	​

)	Top interval may contain no such prime
Top-core proof	Show some q
a
	​

>cn	Equivalent to forcing gcd(a,k!)<1/c; false in general by congruence obstructions
Subset-product proof	Use pairwise coprime q
a
	​

 to build d∈(cn,n]	General subset-product statement is false without extra structure
Prime-factor subset proof	Split each q
a
	​

 into primes and greedily approximate n	Large gaps can occur if all available primes are near cn
Induction on k	Relate (
k
n
	​

) to (
k−1
n
	​

)	Divisibility is not monotone in k
Induction on n	Use Pascal recurrence	Addition destroys divisor control
Contradiction	Assume all divisors ≤n are ≤cn	Need classify the divisor lattice of (
k
n
	​

), difficult
Smoothness obstruction	If no divisor near n, force strong smoothness	Smoothness alone does not prevent divisor gaps
Density of divisors	Show many divisors force one near n	Divisor count does not guarantee local density
Cardinal arithmetic	Bound number of forbidden subset products	Multiplicative overlaps are too structured
Auxiliary graph	Vertices are residual prime factors, edges represent products ≤n	Need lower bound on reachable product interval
Counterexample construction	Force every top factor to have a large divisor from k!	Must also control all remaining prime factors of (
k
n
	​

), not just top cores

The best verified structure is Lemma 2: the residual cores are pairwise coprime. This is nontrivial and useful, but it does not by itself solve the original problem.

Main proof attempt from residual cores

Let

Q={q
a
	​

:n−k+1≤a≤n}.

Every subproduct of elements of Q divides (
k
n
	​

).

If there exists a with

cn<q
a
	​

≤n,

then the problem is solved.

So the difficult case is

q
a
	​

≤cn

for every a∈[n−k+1,n].

Since

q
a
	​

=
gcd(a,k!)
a
	​


and a>n−k, when k≤n/2 we have

a>n/2.

Thus q
a
	​

≤cn implies

gcd(a,k!)≥
cn
a
	​

>
2c
1
	​

.

So every top factor must share a moderately large part with k!.

This suggests a contradiction if c is tiny. However, that contradiction does not follow automatically. One can arrange long intervals where every integer has a nontrivial common factor with k!, so merely forcing

gcd(a,k!)>
2c
1
	​


is not enough.

The next hope is subset products.

Suppose q
a
1
	​

	​

,…,q
a
r
	​

	​

≤cn. If some subproduct lies in (cn,n], we are done. The pairwise coprimality guarantees that such a subproduct divides (
k
n
	​

).

But the following abstract obstruction blocks the argument:

Take numbers x
1
	​

,x
2
	​

≤cn with

x
1
	​

x
2
	​

>n.

Then neither x
1
	​

 nor x
2
	​

 lies above cn, while their product already exceeds n. Thus no subset product lies in (cn,n]. This shows that pairwise coprimality alone is insufficient.

Therefore one needs additional structure from the fact that the q
a
	​

 arise from consecutive integers after removing gcd(a,k!). I was not able to prove the needed strengthening.

Counterexample search framework

To disprove the statement, one would need:

For every M, find n,k such that every divisor d≤n of (
k
n
	​

) satisfies

d≤
M
n
	​

.

A natural attempted construction is:

Choose k large.

Force each top factor a=n−j to be divisible by some modulus m
j
	​

≥M with m
j
	​

∣k!.

Then

q
a
	​

=
gcd(a,k!)
a
	​

≤
m
j
	​

a
	​

≤
M
n
	​

.

This prevents individual residual cores from entering (n/M,n].

But this is not enough. Even if all individual q
a
	​

≤n/M, products of prime factors from different q
a
	​

’s may still land in

(n/M,n].

To complete a disproof, one would have to control the entire divisor lattice of

(
k
n
	​

),

not just the canonical residual cores. I did not obtain such a construction.

Verified dependency graph

Definitions:

B(n,k)=(
k
n
	​

),D(n,k)=max{d≤n:d∣B(n,k)}.

Verified lemmas:

Symmetry

B(n,k)=B(n,n−k).

Top-core divisibility

q
a
	​

=
gcd(a,k!)
a
	​

∣B(n,k).

Top-core coprimality

For distinct a,b∈[n−k+1,n],

gcd(q
a
	​

,q
b
	​

)=1.

Subset-core divisibility

For every subset S,

a∈S
∏
	​

q
a
	​

∣B(n,k).

Unresolved primary gap:

Does the prime-factor multiset of the pairwise coprime q
a
	​

 always contain a subproduct in (cn,n]?

Unresolved counterexample gap:

Can one force all divisors ≤n of B(n,k) below cn for arbitrarily small c?

Neither gap was closed.

RESOURCE_EXHAUSTED

I did not obtain a complete proof or a complete disproof within the available reasoning budget.

PROOF_CONFIDENCE: 92/100 for the verified lemmas above.

COMPLETENESS_SCORE: 25/100. The formal structure and several useful divisor lemmas were established, but the central subset-product/divisor-density gap remains unresolved.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the local lemmas; 0/100 for the full theorem because no complete proof was produced.

RESOURCE_USAGE: approximately 100% of available reasoning budget used; 3 major branches explored; 4 verified lemmas generated; 2 main failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

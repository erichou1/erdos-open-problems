# Erdős Problem #404 [unsolved] 55%

---

## ChatGPT Response

Formalization

Let v
p
	​

(x) be the exponent of p in x, and define

F(a,p)=supv
p
	​

(
i=1
∑
n
	​

a
i
	​

!),

where the supremum is over all finite strictly increasing sequences

a=a
1
	​

<a
2
	​

<⋯<a
n
	​

.

The question asks for which (a,p) the quantity F(a,p) is finite. If finite, then

f(a,p)=F(a,p).

The unbounded alternative is

∀K≥1 ∃a=a
1
	​

<⋯<a
n
	​

such thatp
K
∣
i=1
∑
n
	​

a
i
	​

!.

Equivalently, writing s=v
p
	​

(a!),

i=1
∑
n
	​

a
i
	​

!=a!(1+
i=2
∑
n
	​

a!
a
i
	​

!
	​

),

so

F(a,p)=s+supv
p
	​

(1+
m>a
∑
	​

ε
m
	​

(a+1)(a+2)⋯m),

where each ε
m
	​

∈{0,1} and only finitely many ε
m
	​

 are nonzero.

Exact p-adic reformulation

For fixed a,p, define

X
a
	​

={(ε
m
	​

)
m≥a
	​

:ε
a
	​

=1, ε
m
	​

∈{0,1}}.

Since v
p
	​

(m!)→∞, the series

Φ(ε)=
m=a
∑
∞
	​

ε
m
	​

m!

converges in Z
p
	​

.

Then:

F(a,p)=∞

if and only if there exists ε∈X
a
	​

 such that

Φ(ε)=0in Z
p
	​

.
Proof

Suppose F(a,p)=∞. Then for every K there is a finite subset S
K
	​

⊆{a,a+1,…}, with a∈S
K
	​

, such that

m∈S
K
	​

∑
	​

m!≡0(modp
K
).

Represent S
K
	​

 by its characteristic sequence ε
(K)
∈X
a
	​

. Since X
a
	​

 is compact by diagonal subsequence extraction, choose a subsequential limit ε. For fixed K, all terms m! with v
p
	​

(m!)≥K vanish modulo p
K
, so the congruence modulo p
K
 depends on only finitely many coordinates. Hence

Φ(ε)≡0(modp
K
)

for every K. Therefore Φ(ε)=0 in Z
p
	​

.

Conversely, if Φ(ε)=0, let

a=b
1
	​

<b
2
	​

<b
3
	​

<⋯

be the selected indices. The finite partial sums

S
N
	​

=
i=1
∑
N
	​

b
i
	​

!

satisfy

S
N
	​

=−
i>N
∑
	​

b
i
	​

!

in Z
p
	​

. Since v
p
	​

(b
i
	​

!)→∞, the right-hand side tends to 0 p-adically. Therefore

v
p
	​

(S
N
	​

)→∞.

Thus the second question is equivalent to asking whether there exists at least one pair (a,p) with F(a,p)=∞.

Immediate finite cases

Let s=v
p
	​

(a!). If K≤s, then p
K
∣a!, so F(a,p)≥s.

To get divisibility by p
s+1
, after dividing by p
s
, only those m! with

v
p
	​

(m!)=s

matter modulo p. Hence:

F(a,p)=s

whenever no subset T of

{m≥a:v
p
	​

(m!)=s}

with a∈T satisfies

m∈T
∑
	​

p
s
m!
	​

≡0(modp).

This gives a complete first-digit obstruction.

For example, if a=p−1, then (p−1)!

≡0(modp), while every m! with m≥p is divisible by p. Therefore every allowed sum is congruent to (p−1)!

≡0(modp), so

f(p−1,p)=0.

In particular,

f(1,2)=0,f(2,3)=0,f(4,5)=0.

More generally, for a<p, divisibility by p is possible exactly when there is a subset

T⊆{a,a+1,…,p−1},a∈T,

such that

m∈T
∑
	​

m!≡0(modp).

If no such subset exists, then f(a,p)=0.

Finite computation criterion

For each K, let M
K
	​

 be the least integer such that

v
p
	​

(M
K
	​

!)≥K.

Then

F(a,p)≥K

if and only if there exists a subset

T⊆{a,a+1,…,M
K
	​

−1},a∈T,

such that

m∈T
∑
	​

m!≡0(modp
K
).

This is exact because all m! with m≥M
K
	​

 vanish modulo p
K
.

Thus every finite-level question is decidable by finite subset-sum modulo p
K
. The obstruction is not finite-level verification; it is deciding whether the congruences persist for all K.

Conclusion

RESOURCE_EXHAUSTED

A complete classification of all pairs (a,p) was not derived from first principles here. What is rigorously established is the exact equivalence:

F(a,p)=∞⟺∃(ε
m
	​

)
m≥a
	​

∈{0,1}
N
 with ε
a
	​

=1 and 
m=a
∑
∞
	​

ε
m
	​

m!=0 in Z
p
	​

.

Consequently, the existence of a prime p and an infinite sequence

a
1
	​

<a
2
	​

<⋯

with

v
p
	​

(
i≤k
∑
	​

a
i
	​

!)→∞

is exactly equivalent to the existence of at least one pair (a
1
	​

,p) for which f(a
1
	​

,p) is infinite.

PROOF_CONFIDENCE: 95
COMPLETENESS_SCORE: 55
ADVERSARIAL_SURVIVAL_SCORE: 90
RESOURCE_USAGE: approximately 80%; several reductions and obstruction criteria established; no complete global classification obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

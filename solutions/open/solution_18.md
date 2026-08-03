# Erdős Problem #18 [unsolved] 28%

---

## ChatGPT Response

Phase 0: Formalization

Let

D(m)={d∈Z
≥1
	​

:d∣m}.

For N∈[0,m−1], define

β
m
	​

(N)=min{∣A∣:A⊆D(m), 
d∈A
∑
	​

d=N},

with β
m
	​

(N)=∞ if no such A exists. Then m is practical exactly when

∀N∈{1,…,m−1},β
m
	​

(N)<∞.

For practical m,

h(m)=
1≤N<m
max
	​

β
m
	​

(N).

The three target statements are:

P
1
	​

:∃C>0 such that infinitely many practical m satisfy h(m)<(loglogm)
C
.
P
2
	​

:h(n!)<n
o(1)
.

Equivalently,

∀ε>0, ∃n
0
	​

, ∀n≥n
0
	​

,h(n!)<n
ε
.
P
3
	​

:∃C>0,∃n
0
	​

,∀n≥n
0
	​

,h(n!)<(logn)
C
.

Immediate implication:

P
3
	​

⇒P
2
	​

.

Also, since

log(n!)=nlogn+O(n),

we have

loglog(n!)=logn+O(loglogn).

Thus

P
3
	​

⇒P
1
	​


by taking m=n!.

Negations:

¬P
1
	​

:∀C>0,∃M
C
	​

,∀ practical m≥M
C
	​

,h(m)≥(loglogm)
C
.
¬P
2
	​

:∃ε>0,∀n
0
	​

,∃n≥n
0
	​

,h(n!)≥n
ε
.
¬P
3
	​

:∀C>0,∀n
0
	​

,∃n≥n
0
	​

,h(n!)≥(logn)
C
.

The reciprocal formulation is useful. If d∣m, write d=m/a, where a∣m. Then

N=
d∈A
∑
	​

d

is equivalent to

m
N
	​

=
a∈B
∑
	​

a
1
	​

,

where B⊆D(m). Thus h(m) is the maximal number of unit fractions with denominators dividing m needed to represent every rational N/m, 1≤N<m.

Verified theorem pool
Lemma 1: Product subadditivity

If a,b are practical, then ab is practical and

h(ab)≤h(a)+h(b).

Proof.
Let 0≤N<ab. Write

N=aq+r,0≤r<a,0≤q<b.

Since a is practical, r is a sum of at most h(a) distinct divisors of a. Since b is practical, q is a sum of at most h(b) distinct divisors of b:

r=
u∈U
∑
	​

u,q=
v∈V
∑
	​

v.

Then

N=
u∈U
∑
	​

u+
v∈V
∑
	​

av.

Each u∣a∣ab. Each av∣ab because v∣b. Also u<a whenever u appears in a representation of r<a, while av≥a, so the two collections are disjoint. Hence N is represented by at most h(a)+h(b) distinct divisors of ab. ∎

Lemma 2: Factorials are practical and satisfy Erdős-type bound

For every n≥2,

h(n!)≤n−1.

Proof.
Base case: 2!=2. The only N with 1≤N<2 is N=1, represented by the divisor 1. Thus h(2!)=1.

Assume h((n−1)!)≤n−2. Let 0≤N<n!. Write

N=nQ+r,0≤r<n,0≤Q<(n−1)!.

By induction,

Q=
d∈A
∑
	​

d

with A⊆D((n−1)!) and ∣A∣≤n−2. Then

nQ=
d∈A
∑
	​

nd,

and each nd∣n!. If r=0, this is enough. If 1≤r<n, then r∣n!, since every integer 1≤r≤n divides n!. Also r<n≤nd for every d≥1, so r is distinct from all nd. Therefore

N=r+
d∈A
∑
	​

nd

uses at most n−1 distinct divisors of n!. ∎

This proves the basic upper bound

h(n!)≤n−1.

It does not prove either h(n!)<n
o(1)
 or h(n!)<(logn)
O(1)
.

Lemma 3: Counting lower bound

Let m be practical and let D=d(m)=∣D(m)∣. If k=h(m), then

m≤
j=0
∑
k
	​

(
j
D
	​

).

In particular, if 1≤k≤D,

logm≤klog(
k
eD
	​

)+O(1).

Proof.
Every N∈{0,1,…,m−1} must be represented by some subset of D(m) of size at most k. There are at most

j=0
∑
k
	​

(
j
D
	​

)

such subsets. Different subsets may have the same sum, so this is only an upper bound for possible sums. Therefore it must be at least m. The binomial estimate gives the logarithmic inequality. ∎

Lemma 4: Divisor count of n!

There exists an absolute constant C
0
	​

 such that

d(n!)≤exp(C
0
	​

logn
n
	​

)

for all sufficiently large n.

Proof sketch with checked dependencies.

Write

d(n!)=
p≤n
∏
	​

(v
p
	​

(n!)+1).

For each prime p≤n,

v
p
	​

(n!)=
j≥1
∑
	​

⌊
p
j
n
	​

⌋≤
p−1
n
	​

.

Also

log(t+1)≤
r=1
∑
t
	​

r
1
	​

.

Thus

logd(n!)≤
r=1
∑
n
	​

r
1
	​

#{p≤n:v
p
	​

(n!)≥r}.

If v
p
	​

(n!)≥r, then p≤n/r+1. Hence

logd(n!)≤
r=1
∑
n
	​

r
π(n/r+1)
	​

.

Using the elementary Chebyshev-type bound

π(x)≪
logx
x
	​

,

which follows from the fact that every prime p∈(x,2x] divides (
⌊x⌋
2⌊x⌋
	​

), one obtains

r=1
∑
n
	​

r
π(n/r+1)
	​

≪
logn
n
	​

.

Therefore

logd(n!)≪
logn
n
	​

.

∎

Corollary 5: Universal lower bound for h(n!)

There exists c>0 such that for all sufficiently large n,

h(n!)≥c(logn)
2
.

Proof.
Let k=h(n!), D=d(n!). From Lemma 3,

log(n!)≤klog(
k
eD
	​

)+O(1)≤k(1+logD)+O(1).

By Lemma 4,

1+logD≪
logn
n
	​

.

Also

log(n!)≥c
1
	​

nlogn

for large n. Therefore

c
1
	​

nlogn≪k
logn
n
	​

,

so

k≫(logn)
2
.

Thus

h(n!)≥c(logn)
2
.

∎

This does not disprove the polylogarithmic possibility. It only shows that if

h(n!)<(logn)
C

is true, then necessarily C≥2 up to constants.

Phase 1: Breadth-first strategy search

I generated the following independent routes.

Strategy	Description	Obstacle	Status
Direct factorial expansion	Use N=nQ+r recursively	Gives only h(n!)≤n−1	Verified but weak
Block factorial expansion	Split N=AQ+r with large A∣n!	Need short representations for all r<A	Gap
Product subadditivity	Factor m=ab, use h(ab)≤h(a)+h(b)	Need practical factors with tiny total h	Verified tool, no full solution
Counting lower bound	Compare m to number of small subset sums	Gives lower bound only	Verified
Reciprocal/Egyptian form	Represent N/m as ∑1/a
i
	​

	Need uniform short expansions with a
i
	​

∣m	Gap
Greedy divisor approximation	Repeatedly subtract a large divisor d≤N	Need strong density of divisors of n!	Gap
Modular residue compression	Represent residues mod A cheaply	Need uniform residue basis modulo large A	Gap
Random subset-sum covering	Use many divisors of n! as random coins	Coverage of every residue is not guaranteed	Gap
Induction on prime exponents	Build n! by adding prime powers	Local increase in h too large	Weak
Transfinite/ordinal induction	Not naturally suited; all objects finite	No benefit found	Discarded
Diagonal lower bound	Try to construct N avoiding all k-term sums	Counting only reaches (logn)
2
	Verified obstruction only
Auxiliary divisor graph	Vertices divisors, edges encode usable sums	Connectivity does not imply short additive diameter	Gap

Top three after ranking:

Block factorial expansion.

Reciprocal/Egyptian formulation.

Random or pseudorandom divisor subset covering.

None produced a complete proof.

Phase 2: New definitions and invariants
1. Residue cost

For a∣m, define

R
m
	​

(a)=
0≤r<a
max
	​

min{∣A∣:A⊆D(m), 
d∈A
∑
	​

d=r, d<a}.

If R
m
	​

(a) is small, then residues modulo a are cheap.

Consequence: if a∣m and m/a is practical, then

h(m)≤R
m
	​

(a)+h(m/a).

This generalizes the proof of Lemma 1.

For m=n!, choosing a=n gives R
n!
	​

(n)=1, recovering

h(n!)≤h((n−1)!)+1.

To improve n−1, one needs large a with

R
n!
	​

(a)≪loga/logn.

This is the main unresolved bottleneck.

2. Divisor entropy

Define

E(m)=
logm
logd(m)
	​

.

The counting lower bound says roughly

h(m)≳
E(m)
1
	​


up to logarithmic factors.

For m=n!,

E(n!)≍
(logn)
2
1
	​


at the level needed for the lower bound, hence

h(n!)≳(logn)
2
.

Thus a polylogarithmic upper bound would be close to the counting barrier.

3. Reciprocal basis cost

Define

ε
m
	​

(N)=min{k:
m
N
	​

=
i=1
∑
k
	​

a
i
	​

1
	​

, a
i
	​

∣m, a
i
	​

 distinct}.

Then

h(m)=
1≤N<m
max
	​

ε
m
	​

(N).

For m=n!, this becomes:

Every rational N/n!∈(0,1) should be expressible as a short Egyptian fraction whose denominators all divide n!.

The factorial digit proof gives length at most n−1. A polylogarithmic theorem would require a radically more compressed Egyptian-fraction expansion.

Phase 3: Parallel exploration
Branch A: Direct factorial induction

Verified recurrence:

h(n!)≤h((n−1)!)+1.

This gives

h(n!)≤n−1.

Attempted strengthening: choose a block

A=(n−t+1)(n−t+2)⋯n

and write

N=AQ+r.

Then Q<(n−t)!. If every r<A could be represented using o(t) divisors of n!, one would obtain

h(n!)≤h((n−t)!)+o(t).

Iterating with large t could lead to sublinear or even polylogarithmic bounds.

Gap node:

Prove R
n!
	​

(A)=o(t) for some large factorial block A.
	​


Attack attempts:

Count available divisors below A.
There are many, but counting does not force interval coverage.

Use greedy subtraction inside [0,A).
Requires dense divisors below A, not established.

Use modular representations.
Need short subset sums realizing every residue modulo A.

Use recursive internal factorial digits.
Gives R
n!
	​

(A)≤t, no improvement.

Use divisors containing primes outside the block.
Helps density but no uniform covering proof emerged.

Status: unresolved.

Branch B: Product decomposition

Lemma 1 gives

h(ab)≤h(a)+h(b)

for practical a,b.

Thus, if

n!=m
1
	​

m
2
	​

⋯m
s
	​


with all m
i
	​

 practical, then

h(n!)≤
i=1
∑
s
	​

h(m
i
	​

).

A route to h(n!)<(logn)
C
 would be:

s≤(logn)
C
1
	​

,h(m
i
	​

)≤(logn)
C
2
	​

.

Gap node:

Factor n! into few practical factors of small h.
	​


Obstacle: small primes, especially powers of 2, occur in n! with exponent ≍n. Any factorization into lcm-like practical layers appears to require many layers unless each layer absorbs a large amount of 2-adic valuation while keeping h small. No verified construction achieved this.

Status: unresolved.

Branch C: Counting obstruction

For m=n!, we proved

h(n!)≥c(logn)
2
.

So a bound

h(n!)<(logn)
C

cannot hold with C<2 in the strongest asymptotic sense.

This branch cannot disprove h(n!)<n
o(1)
, because

(logn)
2
=n
o(1)
.

It also cannot disprove

h(n!)<(logn)
C

for some C≥2.

Status: verified lower bound, no disproof.

Gap recursion on the main unresolved target

Primary target:

T:∃C, h(n!)<(logn)
C
.

Equivalent additive form:

∀N<n!,N=
i=1
∑
(logn)
C
	​

d
i
	​

,

where the d
i
	​

∣n! are distinct.

Equivalent reciprocal form:

∀N<n!,
n!
N
	​

=
i=1
∑
(logn)
C
	​

a
i
	​

1
	​

,

where a
i
	​

∣n! are distinct.

Ten attack paths:

Direct proof: compress factorial digits.
Failed at residue compression.

Contradiction: assume no short representation.
Counting does not isolate a forbidden N.

Stronger theorem: every interval of length L contains many divisor sums.
No proof obtained.

Weaker theorem sufficient for P
2
	​

: prove h(n!)≤exp(o(logn)).
No route beyond O(n) obtained.

Equivalent formulation: Egyptian fractions with denominators dividing n!.
Reformulation useful, but no uniform short expansion proved.

Auxiliary structure: divisor-sum graph.
Short graph diameter would imply the result; diameter bound not proved.

New invariant: residue cost R
m
	​

(a).
Cleanly identifies the needed improvement, but R
m
	​

(a) remains unbounded beyond trivial estimates.

Counterexample search: try to force large h(n!).
Counting gives only Ω((logn)
2
).

Extremal N: examine N=n!−1, n!/2−1, sparse residues.
No lower bound stronger than counting obtained.

Recursive decomposition: split n! into practical factors.
Product subadditivity is verified, but no efficient factorization was found.

No attack completed T or its negation.

Formal dependency graph

Verified results:

Definition of h(m).
Dependencies: none.

Reciprocal formulation.
Dependencies: divisor bijection d=m/a.

Product subadditivity h(ab)≤h(a)+h(b).
Dependencies: Euclidean division N=aq+r, practicality of a,b.

Factorial recurrence h(n!)≤h((n−1)!)+1.
Dependencies: induction, fact that every 1≤r≤n divides n!.

Factorial upper bound h(n!)≤n−1.
Dependencies: factorial recurrence.

Counting lower bound.
Dependencies: number of subsets of size ≤k.

Divisor-count bound for n!.
Dependencies: v
p
	​

(n!)≤n/(p−1), elementary prime-counting bound.

Lower bound h(n!)≫(logn)
2
.
Dependencies: counting lower bound and divisor-count bound.

Unresolved nodes:

R
n!
	​

(a)≪(logn)
C

for large useful a∣n!.

h(n!)<n
o(1)
.
h(n!)<(logn)
C
.
∃
∞
m practical with h(m)<(loglogm)
C
.
Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 88/100
COMPLETENESS_SCORE: 28/100
ADVERSARIAL_SURVIVAL_SCORE: 82/100

RESOURCE_USAGE: approximately 100% of this response’s reasoning budget; 3 main branches explored; 8 verified lemmas/corollaries generated; 6 failed proof-improvement attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

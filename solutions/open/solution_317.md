# Erdős Problem #317 [unsolved] 35%

---

## ChatGPT Response

0. Complete formalization

Let

L
n
	​

=[1,2,…,n],A
n
	​

={
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

:δ
k
	​

∈{−1,0,1}}⊂Z.

Then every signed reciprocal sum has the form

k=1
∑
n
	​

k
δ
k
	​

	​

=
L
n
	​

N
	​

,N∈A
n
	​

.

Define

λ
n
	​

=min{∣N∣:N∈A
n
	​

, N

=0}.

Then the two questions become:

Q1

Does there exist c>0 such that for every n≥1,

λ
n
	​

<
2
n
cL
n
	​

	​

?

Equivalently,

0<
δ
min
	​

	​

k=1
∑
n
	​

k
δ
k
	​

	​

	​

<
2
n
c
	​

.
Q2

Since every nonzero sum is at least 1/L
n
	​

, the strict inequality

	​

k=1
∑
n
	​

k
δ
k
	​

	​

	​

>
L
n
	​

1
	​


for every nonzero signed sum is equivalent to

λ
n
	​

≥2.

Thus Q2 asks:

∃n
0
	​

 ∀n≥n
0
	​

,±1∈
/
A
n
	​

.

Its negation is:

∀n
0
	​

 ∃n≥n
0
	​

 ∃δ
k
	​

∈{−1,0,1}such that
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

=±1.
1. Basic verified lemmas
Lemma 1: denominator lemma

For every n and every choice of δ
k
	​

,

k=1
∑
n
	​

k
δ
k
	​

	​

∈
L
n
	​

1
	​

Z.

Therefore every nonzero signed sum satisfies

	​

k=1
∑
n
	​

k
δ
k
	​

	​

	​

≥
L
n
	​

1
	​

.

Proof. Since k∣L
n
	​

, each L
n
	​

/k is an integer. Hence

L
n
	​

k=1
∑
n
	​

k
δ
k
	​

	​

=
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

∈Z.

If the sum is nonzero, its numerator is a nonzero integer, so its absolute value is at least 1/L
n
	​

. ∎

Lemma 2: strictness is exactly the ±1 numerator problem

For fixed n,

	​

k=1
∑
n
	​

k
δ
k
	​

	​

	​

>
L
n
	​

1
	​


for every nonzero signed sum if and only if

±1∈
/
A
n
	​

.

Proof. By Lemma 1, every nonzero signed sum is ∣N∣/L
n
	​

 with N∈Z∖{0}. Equality with 1/L
n
	​

 occurs exactly when ∣N∣=1. ∎

Lemma 3: prime-window congruence obstruction

Let p≤n be prime, and let p
a
≤n<p
a+1
. Put q=p
a
. For

N=
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

,

one has

N≡
q
L
n
	​

	​

m≤n/q
p∤m
	​

∑
	​

δ
qm
	​

m
−1
(modp).

Here m
−1
 denotes the inverse of m modulo p.

Proof. Write k=p
b
m, where p∤m. Since v
p
	​

(L
n
	​

)=a,

v
p
	​

(
k
L
n
	​

	​

)=a−b.

Modulo p, the term L
n
	​

/k vanishes unless a−b=0, i.e. unless b=a. Thus only k=qm with p∤m survive modulo p. For such k,

k
L
n
	​

	​

=
qm
L
n
	​

	​

=
q
L
n
	​

	​

⋅m
−1
(modp),

because m is invertible modulo p. ∎

Corollary 4: large-prime obstruction to equality

If p is prime and

2
n
	​

<p≤n,

then the congruence simplifies to

N≡δ
p
	​

p
L
n
	​

	​

(modp).

Therefore, if N=±1, then necessarily

p
L
n
	​

	​

≡±1(modp).

Hence if there exists a prime p∈(n/2,n] such that

p
L
n
	​

	​


≡±1(modp),

then ±1∈
/
A
n
	​

, so the strict inequality in Q2 holds for that n.

Proof. Since p>n/2, the only multiple of p not exceeding n is p itself. Lemma 3 gives

N≡δ
p
	​

L
n
	​

/p(modp).

If N=±1, then δ
p
	​


=0, so δ
p
	​

=±1. Thus L
n
	​

/p≡±1(modp). ∎

This proves a real obstruction, but not the full second claim, because it remains unresolved whether such a “bad” prime must exist for all sufficiently large n.

2. Formal breadth-first strategy search

I tested the following independent proof directions.

Strategy	Target	Hidden assumption exposed	Status
Direct denominator argument	Q2	Strictness requires ruling out numerator ±1, not just denominator divisibility	Gives Lemmas 1–2 only
Modular obstruction using primes p>n/2	Q2	Need existence of a bad prime	Gives Corollary 4; gap remains
Modular obstruction using all prime powers	Q2/Q1	Congruences become coupled across qm terms	Gives Lemma 3; no closure
Pigeonhole on 2
n
 subset sums	Q1	Need many distinct subset sums in bounded interval	Fails at collision control
Random sign concentration	Q1	Many sign sums are bounded, but may collide	Reduces to anti-collision gap
Antichain bound on collisions	Q1	Sperner-type bounds are too weak	Gives only 
n
	​

-scale distinctness
CRT sieve over large primes	Q1/Q2	Need lower bounds for least allowed CRT residues	Promising but unresolved
Induction on n	Q1/Q2	L
n
	​

 changes discontinuously at prime powers	No monotone invariant found
Transfinite induction	Formal completeness	No transfinite structure naturally appears	No useful output
Diagonalization over coefficient vectors	Q1	Needs controlled separation among rational sums	Rephrases same gap
Compactness/density	Q1	Finite-dimensional rational lattice dominates	No compact limiting proof found
Counterexample construction for Q2	Q2 negation	Need infinitely many exact ±1/L
n
	​

 identities	No recursive identity found
Auxiliary smooth/rough decomposition	Q1/Q2	Rough denominators are congruence-controlled; smooth part still large	Partial structure only
Reflection via δ↦−δ	Both	Symmetry gives pairs but not small nonzero sums	Only symmetry invariant

Top three surviving branches:

Branch A: try to prove Q1 using random signs plus anti-collision.

Branch B: try to prove Q2 using large-prime congruence obstructions.

Branch C: try to disprove Q1 using CRT restrictions from large primes.

3. Branch A: attempt toward Q1

Take pure signs ε
k
	​

∈{−1,1}, and define

X(ε)=
k=1
∑
n
	​

k
ε
k
	​

	​

.

If two distinct sign vectors ε,ε
′
 satisfy

0<∣X(ε)−X(ε
′
)∣<
2
n
2c
	​

,

then

2
X(ε)−X(ε
′
)
	​

=
k=1
∑
n
	​

k
δ
k
	​

	​

,δ
k
	​

=
2
ε
k
	​

−ε
k
′
	​

	​

∈{−1,0,1},

and Q1 follows.

The random-sign variance satisfies

VarX=
k=1
∑
n
	​

k
2
1
	​

≤1+∫
1
∞
	​

x
2
dx
	​

=2.

Thus many sign sums lie in a fixed bounded interval. For example, by Chebyshev,

#{ε:∣X(ε)∣≤4}≥
8
7
	​

2
n
.

If these central values contained ≫2
n
 distinct real numbers, then two distinct values would be separated by O(2
−n
), proving Q1.

The unresolved primary theorem is therefore:

Gap A:#{X(ε):ε∈{−1,1}
n
, ∣X(ε)∣≤4}≥α2
n

for some absolute α>0.

I could not prove Gap A.

The obvious antichain argument is insufficient. Indeed, if two sign vectors give the same value, then the corresponding subsets form an antichain under inclusion, because adding positive reciprocals strictly increases the sum. Thus each fiber has size at most the largest Boolean antichain. But that only gives a lower bound of order roughly 
n
	​

 for the number of distinct values in the central interval, far below the ≍2
n
 distinctness needed for Q1.

So Branch A reduces Q1 to a strong arithmetic anti-collision statement and does not solve it.

4. Branch B: attempt toward Q2

By Lemma 2, Q2 is equivalent to eventual nonexistence of

N=
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

=±1.

Corollary 4 gives a clean sufficient condition:

∃p∈(n/2,n] prime with L
n
	​

/p

≡±1(modp)⟹±1∈
/
A
n
	​

.

Thus a possible route to Q2 is:

Gap B:For all sufficiently large n, there exists a prime p∈(n/2,n] such that L
n
	​

/p

≡±1(modp).

I attacked Gap B by considering the structure

L
n
	​

/p=
q
a
≤n
q

=p
	​

∏
	​

q
a
(modp).

The obstruction is that the residue L
n
	​

/pmodp depends on all prime powers up to n, not only on primes in (n/2,n]. Even if one knows that a prime exists in (n/2,n], this does not force the residue to avoid ±1.

A stronger all-large-primes contradiction was also attempted. Let

P
n
	​

={p prime:n/2<p≤n},M
n
	​

=
p∈P
n
	​

∏
	​

p.

For p∈P
n
	​

, write

B
n
	​

=
q
a
≤n
q∈
/
P
n
	​

	​

∏
	​

q
a
.

Then

L
n
	​

/p≡B
n
	​

r∈P
n
	​

r

=p
	​

∏
	​

r(modp).

If every large prime were “good,” then for each p∈P
n
	​

,

B
n
	​

r∈P
n
	​

r

=p
	​

∏
	​

r≡±1(modp).

This resembles a derivative condition for the polynomial

F(x)=
p∈P
n
	​

∏
	​

(x−p),

because

F
′
(p)=
r∈P
n
	​

r

=p
	​

∏
	​

(p−r)≡(−1)
∣P
n
	​

∣−1
r∈P
n
	​

r

=p
	​

∏
	​

r(modp).

Thus the all-good condition becomes

B
n
	​

F
′
(p)≡±1(modp)

for every p∈P
n
	​

. I found no contradiction from this alone.

Therefore Branch B proves a strong sufficient local obstruction but does not prove that the obstruction occurs eventually.

5. Branch C: CRT sieve toward disproving Q1

Let

N=
k=1
∑
n
	​

δ
k
	​

k
L
n
	​

	​

.

For every prime p∈(n/2,n],

N≡δ
p
	​

p
L
n
	​

	​

(modp).

Hence

Nmodp∈{0,
p
L
n
	​

	​

,−
p
L
n
	​

	​

}.

Let

M
n
	​

=
p prime
n/2<p≤n
	​

∏
	​

p.

Then NmodM
n
	​

 must lie in at most

3
∣P
n
	​

∣

allowed residue classes modulo M
n
	​

.

This gives a rigorous necessary condition for small numerators N. If one could prove that every nonzero allowed CRT class has least absolute representative much larger than L
n
	​

/2
n
, then Q1 would be false.

The unresolved primary theorem is:

Gap C:
0

=r∈R
n
	​

∣r∣
M
n
	​

	​

 least
	​

min
	​

∣r∣≫
2
n
L
n
	​

	​


for the allowed residue set R
n
	​

 coming from the large-prime congruences.

I could not prove Gap C. Counting alone is insufficient: although the allowed residue set is sparse modulo M
n
	​

, sparsity does not rule out one exceptionally small representative.

6. Gap recursion
GAP A: central distinctness of random sign sums

Target:

#{X(ε):∣X(ε)∣≤4}≫2
n
.

Attacks attempted:

Direct injectivity: false in general because rational reciprocal relations exist.

Antichain bound: too weak.

Fiber-size improvement using denominators: no uniform exponential saving proved.

Prime-denominator isolation: gives only 2
π(n)−π(n/2)
-scale independent choices, far too small.

Smooth/rough splitting: rough part controlled, smooth part causes collisions.

Fourier anti-concentration: requires bounds on products ∏cos(t/k); no complete bound obtained.

Modular lifting: rephrases into numerator residue collision.

Induction on n: fails at prime powers where L
n
	​

 changes.

Stronger theorem: all fibers are e
o(n)
; plausible route but unproved here.

Counterexample search: no construction showing fibers are exponentially large enough to kill Q1.

Status: unresolved.

GAP B: existence of a bad large prime

Target:

∃p∈(n/2,n]L
n
	​

/p

≡±1(modp)

eventually.

Attacks attempted:

Direct use of existence of primes in (n/2,n]: insufficient.

Largest prime p≤n: residue may equal 1 in some cases, so not reliable.

Smallest prime p>n/2: no forced residue obstruction found.

Product over all large primes: gives derivative-like congruences, no contradiction.

Pairwise comparison of two good primes: no contradiction.

Wilson-type factorial comparison: L
n
	​

 is not (p−1)!, so factorial congruences do not transfer cleanly.

Prime-power decomposition: exact but not decisive.

Induction over intervals between prime powers: residue changes nonlocally.

Stronger theorem: positive density of bad large primes; no proof obtained.

Counterexample construction: no infinite family of all-good intervals obtained.

Status: unresolved.

GAP C: least representative of the CRT allowed set

Target:

0

=r∈R
n
	​

min
	​

∣r∣≫L
n
	​

/2
n
.

Attacks attempted:

Counting allowed residues: insufficient because one small residue may exist.

Random-residue heuristic: not proof.

Product lower bound from large primes: only gives sparsity modulo M
n
	​

.

Add smaller prime intervals: increases restrictions but also increases coefficient coupling.

Recursive sieve over p∈(n/(j+1),n/j]: promising but not closed.

Smooth-number decomposition: needs strong control of smooth denominator contributions.

Direct lower bound on numerator divisibility: false, since the global gcd of {L
n
	​

/k} is 1.

Geometry of numbers: lattice has too many structured short directions.

Stronger theorem: no allowed CRT residue below L
n
	​

/2
n
; unproved.

Counterexample search: no explicit small allowed CRT representative constructed or ruled out.

Status: unresolved.

7. Verified dependency graph

The following statements are proved:

Definition of L
n
	​

,A
n
	​

,λ
n
	​

⇓
Lemma 1: signed sums lie in L
n
−1
	​

Z
⇓
Lemma 2: Q2 strictness ⟺±1∈
/
A
n
	​

⇓
Lemma 3: prime-power congruence
⇓
Corollary 4: bad large prime excludes equality ∣S∣=1/L
n
	​

.

No proof of Q1 or Q2 follows from the verified graph without one of the unresolved gap nodes.

8. Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified lemmas and reductions.

COMPLETENESS_SCORE: 35/100. The denominator and congruence structure is rigorously established, but neither original question is fully proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the local lemmas; 0/100 for the unresolved global claims, since they remain gaps.

RESOURCE_USAGE: approximately 100% of the allocated reasoning pass; 3 main branches explored; 4 proved lemmas/corollaries; 3 primary gap nodes generated; 30 gap attacks attempted; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

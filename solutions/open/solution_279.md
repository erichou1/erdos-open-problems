# Erdős Problem #279 [unsolved] 38%

---

## ChatGPT Response

Phase 0: Formalization

Let k≥3 be fixed. For each prime p, choose a representative

α
p
	​

∈{0,1,…,p−1}.

The target statement is:

∃(α
p
	​

)
p
	​

 ∃N
0
	​

 ∀n≥N
0
	​

 ∃p∈P ∃t∈Z
≥k
	​

n=α
p
	​

+tp.

Equivalently,

∃(α
p
	​

)
p
	​

 ∃N
0
	​

 ∀n≥N
0
	​

 ∃p∈Pn≡α
p
	​

(modp)and
p
n−α
p
	​

	​

≥k.

The exact admissibility condition for p to cover n is

p≤
k
n−α
p
	​

	​

.

Since 0≤α
p
	​

<p, a necessary condition is

p≤
k
n
	​

.

Thus this is not merely an infinite covering by residue classes. For each n, only primes p≲n/k are available.

Negation

The negation is:

∃k≥3 ∀(α
p
	​

)
p
	​

 ∀N
0
	​

 ∃n≥N
0
	​


such that for every prime p,

n

≡α
p
	​

(modp)

or else

p
n−α
p
	​

	​

<k.

Equivalently, for every residue assignment, there are arbitrarily large n avoiding every active congruence class

α
p
	​

(modp)

among primes satisfying

p≤
k
n−α
p
	​

	​

.
Immediate invariants and boundary checks

Finite-prime obstruction.
No finite set of primes can cover all sufficiently large integers.
If S is finite, then by CRT there is a residue class modulo

Q
S
	​

=
p∈S
∏
	​

p

avoiding every chosen class α
p
	​

modp. That class contains infinitely many integers.

Monotonicity in k.
If a construction works for some k, it automatically works for every k
′
≤k. Larger k is harder because fewer primes are eligible for each n.

The prime 2.
Choosing α
2
	​

=1 covers all sufficiently large odd integers, because every odd n≥2k+1 satisfies

n=1+t⋅2,t=
2
n−1
	​

≥k.

So the main difficulty may be reduced to covering sufficiently large even integers.

Zero-class heuristic.
If for all odd primes p one chose α
p
	​

=0, then every sufficiently large even integer with an odd prime factor p≤n/k would be covered. Since every non-power-of-two even integer has an odd prime factor at most 
n
	​

, this covers all sufficiently large even integers except powers of two, provided

n
	​

≤
k
n
	​

,

i.e.

n≥k
2
.

Thus the assignment

α
2
	​

=1,α
p
	​

=0(p odd)

covers every sufficiently large integer except powers of two.

This last observation is important: the whole problem becomes plausible because one residue choice nearly works, but the powers of two force us to disturb some zero-classes, and those disturbances create new exceptional multiplicative families.

Phase 1: Breadth-first strategy search
Strategy	Description	Hidden assumption	Obstacle	Confidence
Direct covering	Construct α
p
	​

 explicitly.	Exceptional sets remain controllable.	Disturbing α
p
	​

=0 creates new exceptions.	Medium
Contradiction	Assume every assignment misses infinitely many n.	Local sieve lower bounds strong enough.	CRT gives global gaps but not local gaps near n∼kp.	Low
Construction from zero-classes	Use α
2
	​

=1, α
p
	​

=0, then repair powers of two.	Repairs do not create too many new gaps.	Repair primes become nonzero and stop covering multiples.	Medium-high
Induction on exceptional semigroup	Enumerate new exceptions caused by repaired primes.	Sparse semigroup can be fully repaired.	Need a uniform domination argument.	Medium
Transfinite/recursive construction	Build residues in stages, preserving already covered intervals.	Future primes do not affect earlier coverage.	Must respect p≤(n−α
p
	​

)/k.	Medium
Cardinal arithmetic	Compare number of exceptions with number of available primes.	Counting suffices for assignment.	Congruence compatibility matters.	Medium
Diagonalization	Choose residues to kill the j-th currently uncovered integer.	Later changes do not uncover earlier integers.	Must choose primes too large to affect old range but small enough to cover target.	Medium
Compactness	Prove every finite interval can be covered compatibly, then pass to a limit.	Finite compatibility has compactness.	Eligibility condition depends on size of n.	Low-medium
Density argument	Random residues cover almost all integers.	Almost all can be upgraded to all.	Sparse exceptional integers may persist forever.	Low
Reflection/block argument	Cover intervals [N
j
	​

,N
j+1
	​

] using primes ≤N
j
	​

/k.	Enough unused primes remain.	Prime budget versus local exception count.	Medium
Auxiliary structure	Invent an exception graph or rank to manage cascades.	Rank decreases under repair.	Need a well-founded rank.	Medium
Counterexample search	Try to force infinitely many uncovered n.	A universal obstruction exists.	The zero-class construction leaves only powers of two, so obstruction must be delicate.	Low

Top three branches:

Branch A: zero-class construction plus repair of powers of two.

Branch B: staged interval construction with protection of previous intervals.

Branch C: contradiction via local sieve lower bound.

Phase 2: New definitions and invariants
Definition 1: Active coverage

For an assignment α=(α
p
	​

), say that p actively covers n if

n≡α
p
	​

(modp)

and

n≥kp+α
p
	​

.

The active covering set of n is

C
α
	​

(n)={p∈P:n≡α
p
	​

(modp), n≥kp+α
p
	​

}.

The target is

∃α ∃N
0
	​

 ∀n≥N
0
	​

,C
α
	​

(n)

=∅.
Definition 2: Zero-prime and exceptional prime

Call an odd prime p a zero-prime if

α
p
	​

=0.

Call p exceptional if

α
p
	​


=0.

With α
2
	​

=1, zero-primes cover large even integers having at least one sufficiently small zero-prime divisor.

Definition 3: Exceptional semigroup

Given a set E of exceptional odd primes, define

S(E)=
⎩
⎨
⎧
	​

2
m
q∈F
∏
	​

q
e
q
	​

:m≥0, F⊂E finite, e
q
	​

≥0
⎭
⎬
⎫
	​

.

If every odd prime outside E is assigned residue 0, then every sufficiently large even integer outside S(E) is covered by a zero-prime divisor.

So the problem reduces to covering sufficiently large elements of S(E) by exceptional congruence classes.

Lemma 1: Zero-class near-solution

Let

α
2
	​

=1,α
p
	​

=0(p odd).

Then every sufficiently large integer except powers of two is covered.

Proof

Odd n are covered by p=2.

Let n be even and not a power of two. Then n=2
r
m with m>1 odd. Let q be the least prime divisor of m. Then q is odd and

q≤
m
	​

≤
n
	​

.

If n≥k
2
, then

n
	​

≤
k
n
	​

.

Since α
q
	​

=0,

n≡0(modq).

Also

n=0+tq,t=
q
n
	​

≥k.

Thus q actively covers n. ∎

Attempted repair of powers of two

We need cover all sufficiently large

n=2
m
.

If we choose an odd prime q and set

α
q
	​

≡2
c
(modq),

then q covers those powers 2
m
 with

2
m
≡2
c
(modq).

If 2 has multiplicative order d
q
	​

 modulo q, this means

m≡c(modd
q
	​

).

So repairing powers of two becomes a covering problem for exponent classes mmodd
q
	​

.

A useful elementary covering of positive integers is

N={m:m≡0(mod2)}∪
s≥1
⋃
	​

{m:m≡2
s
−1(mod2
s+1
)}.

Indeed, if m is even, it lies in the first class. If m is odd, write

m+1=2
s
u

with u odd. Then

m≡2
s
−1(mod2
s+1
).

For each s≥0, every prime divisor q
s
	​

 of the Fermat number

F
s
	​

=2
2
s
+1

satisfies

2
2
s
≡−1(modq
s
	​

),

hence

2
2
s+1
≡1(modq
s
	​

).

So the order of 2modq
s
	​

 is exactly 2
s+1
, provided q
s
	​

 is odd, which it is.

Thus one can choose primes q
s
	​

∣F
s
	​

 and set

α
q
s
	​

	​

≡2
2
s
−1
(modq
s
	​

).

This covers powers 2
m
 in the exponent class

m≡2
s
−1(mod2
s+1
).

Together with s=0, this covers all powers of two.

New obstruction created by the repair

The previous repair makes infinitely many odd primes exceptional. Let

E={q
s
	​

:s≥0}.

All odd primes outside E remain zero-primes. Therefore every sufficiently large even integer with an odd prime divisor outside E is still covered.

But integers of the form

2
m
q∈F
∏
	​

q
e
q
	​


with all odd prime factors in E are no longer automatically covered by zero-primes.

Thus repairing powers of two creates the larger exceptional semigroup S(E).

The original powers of two are only the first layer. The repair creates second-layer exceptions such as

q
s
	​

2
m
,

then third-layer exceptions such as

q
s
	​

q
t
	​

2
m
,

and so on.

This is the main unresolved gap.

Phase 3: Parallel exploration
Branch A: Exceptional semigroup repair
Goal

Construct an infinite exceptional set E and residues α
q
	​


=0 for q∈E such that every sufficiently large element of

S(E)

is covered by some exceptional prime.

Candidate plan

Enumerate elements of S(E) and assign fresh exceptional primes to cover them.

For a target integer n, if there exists an unused prime q≤n/k with q∤n, then setting

α
q
	​

≡n(modq)

covers n.

Difficulty

Adding q to E creates new exceptional integers divisible only by primes in the enlarged set E. Thus the target set grows while we are trying to cover it.

Required theorem

A sufficient theorem would be:

Sparse exceptional repair theorem.
There exists an infinite set E of odd primes and a bijective or injective assignment of sufficiently large elements of S(E) to primes q∈E, with q≤n/k and q∤n, such that every sufficiently large n∈S(E) is assigned to some covering prime.

This theorem would finish the problem, because non-S(E) even integers are covered by zero-primes and odd integers are covered by 2.

Attack on the theorem

A counting condition is necessary:

∣S(E)∩[1,N]∣≲∣{q∈E:q≤N/k}∣

if every exceptional integer is covered individually.

But S(E) contains many products of primes in E, so this inequality is not automatic.

If E is extremely sparse, then S(E) may be sparse enough. For example, if the primes of E grow doubly exponentially, then the number of products below N can be subpolynomial in N. However, individual coverage of all powers 2
m
≤N already requires roughly logN exceptional primes up to N/k, so E cannot be too sparse.

This branch remains unresolved.

Branch B: Protected interval construction
Goal

Construct residues in stages while preserving already covered intervals.

Suppose all integers up to M
j
	​

 are covered. Primes

p>
k
M
j
	​

	​


cannot actively cover any n≤M
j
	​

, because

kp>M
j
	​

≥n.

Therefore their residues can still be chosen freely without disturbing coverage up to M
j
	​

.

This suggests a stage construction:

M
1
	​

<M
2
	​

<⋯

where at stage j, choose residues for primes in

(
k
M
j−1
	​

	​

,
k
M
j
	​

	​

]

to cover the new interval

(M
j−1
	​

,M
j
	​

].
Difficulty

For n near M
j−1
	​

, only primes

p≤
k
n
	​


are eligible. Very few newly available primes may satisfy

k
M
j−1
	​

	​

<p≤
k
n
	​

.

Thus the left edge of each new interval is hard to cover using only fresh primes.

Possible repair

Use overlap: at stage j, cover not merely the next interval but a future interval

[L
j
	​

,M
j
	​

]

with

L
j
	​

≫M
j−1
	​

,

so that many fresh primes are eligible for every n∈[L
j
	​

,M
j
	​

].

But then one must ensure no gaps between already covered intervals and future covered intervals.

This creates a technical block-covering lemma.

Required theorem

A sufficient theorem would be:

Moving block-covering lemma.
For fixed k≥3, there exist increasing intervals I
j
	​

=[U
j
	​

,U
j+1
	​

] and disjoint prime blocks P
j
	​

, with every p∈P
j
	​

 satisfying kp≤U
j
	​

, such that residues modulo primes in P
j
	​

, together with earlier choices, cover every integer in I
j
	​

.

This would prove the original statement.

Status

The theorem is plausible but not verified. The difficulty is proving a deterministic block-covering statement strong enough to cover every integer, not merely almost every integer.

Branch B unresolved.

Branch C: Contradiction through local sieve lower bounds
Goal

Show that for every assignment (α
p
	​

), there are arbitrarily large n avoiding all active classes.

A natural attempt is to fix x and examine integers avoiding

α
p
	​

(modp)

for all primes p≤x.

By CRT, modulo

Q
x
	​

=
p≤x
∏
	​

p,

the number of residue classes avoiding all forbidden classes is

p≤x
∏
	​

(p−1).

So the avoiding proportion modulo Q
x
	​

 is

p≤x
∏
	​

(1−
p
1
	​

).

This is positive for every finite x.

Why this does not disprove the statement

The period Q
x
	​

 is enormous. Positivity modulo Q
x
	​

 does not guarantee an avoiding integer in a short interval such as

[kx,kx+Cx].

The problem is local: for n∼kx, the active primes are roughly those p≤x. One would need a lower bound for sifted integers in intervals of length comparable to x, uniformly over arbitrary forbidden residue classes.

Such a lower bound is false in this generality if the forbidden classes are chosen specifically to cover a short interval.

Therefore the CRT argument does not yield a contradiction.

Branch C fails as a disproof.

Shared theorem pool
Lemma 2: Finite assignments cannot cover a tail

Let S be a finite set of primes and choose residues α
p
	​

modp for p∈S. Then infinitely many integers avoid all these residue classes.

Proof

Let

Q=
p∈S
∏
	​

p.

For each p∈S, exclude one residue class modulo p. There remains at least one allowed residue modulo each p. By CRT, there exists rmodQ satisfying

r

≡α
p
	​

(modp)

for every p∈S. Then all integers

r+ℓQ

avoid every class. Infinitely many such integers exist. ∎

Lemma 3: The zero-class assignment misses exactly powers of two eventually

Let

α
2
	​

=1,α
p
	​

=0(p odd).

Then every integer n≥k
2
 that is not a power of two is covered.

Proof

If n is odd and large enough, p=2 covers it.

If n is even but not a power of two, then n has an odd prime divisor. Let q be the least odd prime divisor. Then

q≤
n
	​

≤
k
n
	​


for n≥k
2
. Since q∣n,

n≡0(modq).

Thus q covers n with

t=
q
n
	​

≥k.

∎

Lemma 4: Powers of two can be covered at the cost of infinitely many nonzero odd primes

There exists an infinite set E of odd primes and residues α
q
	​


=0 for q∈E such that every sufficiently large power of two is covered by some q∈E.

Proof

Use the covering

N={m:m≡0(mod2)}∪
s≥1
⋃
	​

{m:m≡2
s
−1(mod2
s+1
)}.

For each s≥0, choose an odd prime divisor q
s
	​

 of

F
s
	​

=2
2
s
+1.

Then

2
2
s
≡−1(modq
s
	​

),

so the order of 2modq
s
	​

 is exactly 2
s+1
.

Set

α
q
s
	​

	​

≡2
2
s
−1
(modq
s
	​

).

Then q
s
	​

 covers 2
m
 whenever

m≡2
s
−1(mod2
s+1
).

These exponent classes cover all positive integers m. For sufficiently large m, the inequality

2
m
≥kq
s
	​

+α
q
s
	​

	​


also holds. Therefore every sufficiently large power of two is covered. ∎

Attack on Lemma 4 as a full solution

Lemma 4 does not solve the original problem.

Once α
q
s
	​

	​


=0, the prime q
s
	​

 no longer covers its multiples through the zero class. Thus integers whose odd prime divisors all lie among the q
s
	​

 may become uncovered.

Example shape:

n=2
m
q
s
	​

.

This integer is not necessarily covered by q
s
	​

, because

n≡0(modq
s
	​

)

but

α
q
s
	​

	​


=0.

If all other odd prime divisors of n also lie in E, then no zero-prime divisor covers n.

Therefore the proof must cover not only powers of two but the whole exceptional semigroup S(E). That remains unresolved.

Deep execution attempt on Branch A

The strongest current route is:

Set α
2
	​

=1.

Set α
p
	​

=0 for most odd primes.

Select a sparse infinite exceptional set E.

Assign nonzero residues to primes in E.

Prove every sufficiently large element of S(E) is covered by an exceptional prime.

The problem becomes:

∃E⊆P
odd
	​

∃(α
q
	​

)
q∈E
	​

∃N
0
	​

∀n∈S(E), n≥N
0
	​

,∃q∈E:n≡α
q
	​

(modq), n≥kq+α
q
	​

.

This is a self-referential covering problem.

A naive individual assignment would enumerate large n∈S(E), choose a fresh prime q≤n/k, and set

α
q
	​

≡n(modq).

But adding q to E enlarges S(E), creating new targets. To make this work, one needs a growth invariant ensuring the number of newly created targets below N remains smaller than the number of fresh available primes below N/k.

A possible invariant is:

∣S(E)∩[1,N]∣≤
10
1
	​

π(N/k)

for all large N.

But this invariant is difficult to preserve, because every new exceptional prime q creates the infinite family

q2
m
, q
2
2
m
, qq
′
2
m
,…

inside S(E).

If E grows too quickly, S(E) becomes too dense. If E grows too slowly, there are not enough exceptional primes to cover powers of two and other base families.

This is the central unresolved balancing problem.

Local verification and adversarial checks
Check 1: Did the zero-class lemma silently assume p≤n/k?

No. It explicitly uses

q≤
n
	​

≤n/k

for n≥k
2
.

Check 2: Did the power-of-two repair preserve coverage of non-powers?

No. It does not. This failure was identified. The exceptional semigroup S(E) is the exact obstruction.

Check 3: Can the CRT finite-complement argument disprove the statement?

No. It only gives avoiding residue classes modulo a huge period. It does not guarantee avoiding integers in the short moving windows relevant to p≤n/k.

Check 4: Is the staged interval construction already a proof?

No. It requires a block-covering lemma not proved here.

Check 5: Is almost-all coverage enough?

No. The original statement requires every sufficiently large integer. Sparse exceptional sequences such as powers of two cannot be ignored.

Dependency graph of verified results
Formalization
⇓
Lemma 2: finite primes cannot cover a tail
Lemma 3: zero-class assignment covers all but powers of two
Lemma 4: powers of two can be repaired by nonzero exceptional primes
⇓
Unresolved: exceptional semigroup covering

No verified theorem currently proves or disproves the original statement.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified lemmas and reductions.

COMPLETENESS_SCORE: 38/100. The formalization and several strong partial reductions are rigorous, but the central exceptional-semigroup covering problem remains unresolved.

ADVERSARIAL_SURVIVAL_SCORE: 78/100. The main candidate proof was attacked and the obstruction was identified rather than hidden.

RESOURCE_USAGE: approximately 100% of the available response budget; 3 main branches explored; 4 verified lemmas generated; 2 failed proof attempts isolated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #213 [unsolved] 28%

---

## ChatGPT Response

Phase 0: Complete formalization

Let

B(n,k)=(
k
n
	​

),1≤k<n.

The target statement is

∃c>0 ∀n∈N ∀k∈N(1≤k<n⇒∃d∈N:d∣B(n,k), cn<d≤n).

Define

D(n,k)=max{d∈N:d∣B(n,k), d≤n}.

Then the problem is equivalent to

1≤k<n
inf
	​

n
D(n,k)
	​

>0.

Negation:

∀c>0 ∃n ∃k, 1≤k<n,∀d∣B(n,k),d≤cn or d>n.

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

Boundary cases:

k=1: B(n,1)=n, so d=n.

k=2: B(n,2)=n(n−1)/2. If n is odd, n∣B(n,2). If n is even, n−1∣B(n,2).

More generally, for fixed k≤K, the divisor n/gcd(n,k) gives D(n,k)≥n/K. Thus every bounded k-range is harmless.

The difficulty is therefore the regime

k→∞,k≤n/2,

especially when k=o(n), because the elementary divisor n/gcd(n,k) may be only n/k, not a fixed fraction of n.

Verified theorem pool
Lemma 1: Reduced falling-factorial divisors

For 1≤r≤k, define

(n)
r
	​

=n(n−1)⋯(n−r+1),(k)
r
	​

=k(k−1)⋯(k−r+1).

Let

g
r
	​

=gcd((n)
r
	​

,(k)
r
	​

).

Then

g
r
	​

(n)
r
	​

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
(k)
r
	​

(n)
r
	​

	​

(
k−r
n−r
	​

).

Write

(n)
r
	​

=g
r
	​

A,(k)
r
	​

=g
r
	​

B,gcd(A,B)=1.

Then

(
k
n
	​

)=
B
A
	​

(
k−r
n−r
	​

).

Since (
k
n
	​

) is an integer and gcd(A,B)=1, we must have

B∣(
k−r
n−r
	​

).

Therefore

(
k
n
	​

)=A⋅
B
(
k−r
n−r
	​

)
	​

,

so

A=
g
r
	​

(n)
r
	​

	​

∣(
k
n
	​

).

For r=1, this gives

gcd(n,k)
n
	​

∣(
k
n
	​

),

and since gcd(n,k)≤k,

gcd(n,k)
n
	​

≥
k
n
	​

.

This proves the elementary fact that (
k
n
	​

) always has a divisor in [n/k,n].

Lemma 2: Prime-multiple criterion

Let p be prime with p>k. If the interval

(n−k,n]

contains a multiple of p, then

p∣(
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
k!
(n−k+1)(n−k+2)⋯n
	​

.

Since p>k, p∤k!. If some numerator term is divisible by p, then p survives in (
k
n
	​

).

Thus, if additionally

p>cn,

then p itself is a divisor in (cn,n].

So one sufficient condition for the desired theorem is:

∃c>0 ∀n,k≤n/2, ∃ prime p>cn with a multiple in (n−k,n].

This condition is strong and was not proved.

Lemma 3: Large prime-power residual from one numerator term

Let

L
k
	​

=lcm(1,2,…,k).

For each 0≤i≤k−1, define

R
i
	​

=
gcd(n−i,L
k
	​

)
n−i
	​

.

Then

R
i
	​

∣(
k
n
	​

).

Proof:

Fix a prime p. Let v
p
	​

(x) be the exponent of p in x. We need to show

v
p
	​

(R
i
	​

)≤v
p
	​

(
k
n
	​

).

Now

v
p
	​

(R
i
	​

)=max(0, v
p
	​

(n−i)−v
p
	​

(L
k
	​

)).

Also

v
p
	​

(L
k
	​

)=
1≤j≤k
max
	​

v
p
	​

(j)=⌊log
p
	​

k⌋.

For every exponent a>v
p
	​

(L
k
	​

), we have p
a
>k. Therefore k! contributes no factor divisible by p
a
. If p
a
∣n−i, then one numerator term contributes such a factor, and it cannot be cancelled by the denominator. Hence every prime-power level of n−i above L
k
	​

 survives in (
k
n
	​

).

Thus R
i
	​

∣(
k
n
	​

).

Therefore, if for some absolute c>0 one could prove that for every n,k,

0≤i≤k−1
max
	​

gcd(n−i,L
k
	​

)
n−i
	​

>cn,

then the problem would be solved.

This is a genuine gap, not a proof.

Phase 1: Breadth-first strategy search
Strategy	Description	Obstacle
Direct divisor n/gcd(n,k)	Gives divisor ≥n/k.	Fails when k is unbounded.
Prime divisor strategy	Find prime p>cn surviving from numerator.	Requires uniform prime/multiple control in short intervals.
Falling-factorial strategy	Use (n)
r
	​

/gcd((n)
r
	​

,(k)
r
	​

)∣(
k
n
	​

).	Divisors may jump from ≤cn to >n.
LCM residual strategy	Use R
i
	​

=(n−i)/gcd(n−i,L
k
	​

).	Need prove one R
i
	​

 is linear in n.
Contradiction	Assume all divisors ≤n are ≤cn.	Hard to force a divisor into the forbidden gap.
Construction/counterexample	Try to make every numerator term highly cancellable by k!.	Still must control all composite divisors of the binomial coefficient.
Induction on n	Relate (
k
n
	​

) to (
k
n−1
	​

) or (
k−1
n−1
	​

).	Divisibility between adjacent rows is not monotone.
Induction on k	Use (
k
n
	​

)=
k
n−k+1
	​

(
k−1
n
	​

).	Division by k can destroy the desired divisor.
Cardinal/divisor-count	Show many divisors, force one into (cn,n].	Divisor count does not imply location.
Diagonalization over c	For every c, try to build n,k avoiding the interval.	Needs exact control of all divisors, not just numerator terms.
Compactness/CRT	Prescribe divisibility of n−i by small factors.	Local congruences do not determine global divisor structure of (
k
n
	​

).
Cancellation hypergraph	Model denominator prime powers matched to numerator prime powers.	Need a bounded-load matching theorem; none was derived.

Top three branches selected:

LCM residual branch.

Falling-factorial divisor branch.

Prime-multiple branch.

Phase 2–5: Parallel exploration
Branch A: LCM residual branch

We have a verified divisor

R
i
	​

=
gcd(n−i,L
k
	​

)
n−i
	​

∣(
k
n
	​

),0≤i≤k−1.

Since R
i
	​

≤n, the target would follow if

∃c>0∀n,k
i
max
	​

R
i
	​

>cn.

Equivalently,

∃c>0∀n,k∃i∈[0,k−1]gcd(n−i,L
k
	​

)<
cn
n−i
	​

.

Since n−i∼n when k≤n/2, this roughly asks for some n−i whose L
k
	​

-part is bounded by an absolute constant.

GAP_NODE A

Prove:

∃C>0∀n,k≤n/2∃0≤i<k:gcd(n−i,L
k
	​

)≤C.

This would imply the theorem with c≈1/C.

Attack attempts:

Direct proof: False-looking. By congruence choices, one can force many consecutive values n−i to have prescribed common factors with L
k
	​

.

Contradiction: Assuming every gcd(n−i,L
k
	​

)>C does not contradict size, because L
k
	​

 is enormous.

Stronger theorem: Require one n−i coprime to L
k
	​

. This is much too strong.

Weaker theorem: Require one residual R
i
	​

>cn, not bounded gcd. Still unresolved.

Auxiliary invariant: Let s
i
	​

=gcd(n−i,L
k
	​

). Need bound min
i
	​

s
i
	​

. No uniform bound derived.

Density argument: Among k consecutive integers, many avoid any fixed prime, but not all small primes simultaneously.

CRT obstruction: Finite systems can force divisibility patterns across a finite interval.

Extremal configuration: Choose n so that n−i is divisible by a chosen small factor a
i
	​

≤k. This weakens any naive gcd bound.

Recursive decomposition: Factor L
k
	​

 into prime powers. Still no uniform survivor.

Counterexample search: No explicit full counterexample to the original theorem was produced, only an obstruction to this sufficient condition.

Conclusion of Branch A:

The LCM residual lemma is valid, but the required uniform residual lower bound was not proved.

Branch B: Falling-factorial divisor branch

For each r≤k,

A
r
	​

=
gcd((n)
r
	​

,(k)
r
	​

)
(n)
r
	​

	​

∣(
k
n
	​

).

If for some r,

cn<A
r
	​

≤n,

we are done.

Lower bound:

A
r
	​

≥
(k)
r
	​

(n)
r
	​

	​

=
j=0
∏
r−1
	​

k−j
n−j
	​

.

For k≤n/2, every factor satisfies

k−j
n−j
	​

≥
k
n
	​

≥2.

So A
r
	​

 grows at least exponentially in r. In particular, A
r
	​

 eventually exceeds n for moderately large r.

The natural idea is to choose the first r for which A
r
	​

>cn. But this fails as a proof because A
r
	​

 may jump directly from ≤cn to >n.

GAP_NODE B

Prove:

∃c>0∀n,k≤n/2∃r≤k:cn<A
r
	​

≤n.

Attack attempts:

Monotonicity: A
r
	​

 is not obviously monotone because gcd cancellation changes irregularly.

Use lower bound only: (n)
r
	​

/(k)
r
	​

 is rational and does not control the reduced numerator tightly enough.

Minimal crossing: Let r be minimal with A
r
	​

>cn. Need A
r
	​

≤n, but no jump bound was proved.

Prime factor jump control: If every prime factor of A
r
	​

 were ≤1/c, jumps would be controlled. This is false in general.

Divisor-subset rescue: Even if A
r
	​

>n, perhaps some divisor of A
r
	​

 lies in (cn,n]. This is plausible but unproved.

Abstract counterexample to naive subset lemma: An integer with prime factors just below cn can have no divisor in (cn,n] except those primes themselves; products may exceed n. Thus general divisor-density is insufficient.

Use consecutive structure: A
r
	​

 comes from consecutive numbers, not arbitrary integers. No complete exploitation found.

Use r=2: Gives divisor at least n(n−1)/k(k−1), useful only when k≲
n
	​

.

Use variable r: Handles ranges heuristically but not uniformly.

Recursive reduction: The remaining claim becomes a divisor-location theorem for reduced falling factorials, not simpler than the original.

Conclusion of Branch B:

The falling-factorial divisibility lemma is strong, but I did not prove a uniform interval-hit result for the divisors A
r
	​

.

Branch C: Prime-multiple branch

If there exists a prime

p>cn

such that some multiple of p lies in

(n−k,n],

then p∣(
k
n
	​

), and the theorem follows.

For k comparable to n, this is plausible because the numerator interval is long. For k=o(n), it becomes a short-interval prime/multiple question.

GAP_NODE C

Prove:

∃c>0∀n,k≤n/2∃p>cn prime such that (n−k,n] contains a multiple of p.

Attack attempts:

Direct prime in interval: A prime in (n−k,n] would work, but such a prime need not exist by elementary interval reasoning.

Prime divisor of one numerator term: Need one n−i to have a prime factor >cn. Not proved.

Large composite divisor: Even if no large prime exists, products of medium primes may work. This leaves prime-only branch.

Contradiction using smoothness: If all numerator terms are cn-smooth, no contradiction was derived.

Average size: Terms are near n, but large size alone does not force a prime factor >cn.

Pairwise coprimality: Consecutive numbers have limited gcds, but this does not force a large prime factor.

Use denominator bound: Since k! has no primes >k, primes >k survive. But if k≪n, primes >k may still be far below cn.

Strengthen to many primes >k: Not proved.

Combine primes >k: Products may overshoot n, and no subset-product interval theorem was proved.

Recursive local factorization: Reduces to controlling large prime factors of short intervals, unresolved internally.

Conclusion of Branch C:

A prime-divisor proof was not completed.

Verified partial consequences

The following statements were rigorously established.

Partial result 1

For all n,k,

(
k
n
	​

)

has a divisor in

[
k
n
	​

,n].

This follows from

gcd(n,k)
n
	​

∣(
k
n
	​

).
Partial result 2

For every fixed K, if 1≤k≤K, then

(
k
n
	​

)

has a divisor in

[
K
n
	​

,n].

So bounded k is fully controlled.

Partial result 3

If there exists 0≤i<k such that

gcd(n−i,L
k
	​

)
n−i
	​

>cn,

then the desired divisor exists.

Partial result 4

If there exists a prime p>cn with a multiple in (n−k,n], then the desired divisor exists.

Adversarial verification

The following possible proof failures were checked.

Assuming the conclusion: No accepted lemma assumes existence of a divisor in (cn,n].

Quantifier error: The unresolved part is exactly the uniform existence of one absolute c.

Hidden theorem use: No external prime-gap, smooth-number, Sylvester-type, or literature-status theorem was accepted.

Reduction cheat: Each reduction was promoted to a GAP_NODE and attacked.

Cardinal arithmetic: No divisor-count argument was accepted as location control.

Composite-divisor gap: The main unresolved difficulty is not merely finding large prime factors; composite divisors may matter.

False divisor-density lemma: The tempting claim that every large integer with small prime factors has a divisor in (cn,n] is false in that generality.

Finite computation: No numerical evidence was used as proof.

Dependency graph

Verified results:

Lemma 1⇒
gcd(n,k)
n
	​

∣(
k
n
	​

)⇒D(n,k)≥
k
n
	​

.
Lemma 2⇒prime multiple in (n−k,n] gives divisor.
Lemma 3⇒R
i
	​

=
gcd(n−i,L
k
	​

)
n−i
	​

∣(
k
n
	​

).

Unresolved primary theorem:

∃c>0∀n,kD(n,k)>cn.

Unresolved sufficient statements:

∃c>0∀n,k∃i: R
i
	​

>cn.
∃c>0∀n,k∃r: cn<
gcd((n)
r
	​

,(k)
r
	​

)
(n)
r
	​

	​

≤n.
∃c>0∀n,k∃p>cn prime surviving in (
k
n
	​

).

None of these sufficient statements was proved or disproved.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified lemmas and reductions.

COMPLETENESS_SCORE: 28/100 for the original problem.

ADVERSARIAL_SURVIVAL_SCORE: 82/100 for the partial results; no complete proof survived because the central uniform divisor-location gap remains unresolved.

RESOURCE_USAGE: approximately 100% of the allocated reasoning budget; 3 main branches explored; 4 verified lemmas/partial consequences generated; 3 major GAP_NODEs recursively attacked; no proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

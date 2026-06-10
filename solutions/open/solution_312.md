# Erdős Problem #312 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Formalization

Let a finite multiset A be encoded by multiplicities

m
A
	​

(n)∈N,n≥1,

with finite support. For a submultiset S⊆A, write 0≤s(n)≤m
A
	​

(n), and define

W(S)=
n≥1
∑
	​

n
s(n)
	​

,W(A)=
n≥1
∑
	​

n
m
A
	​

(n)
	​

.

The clean strengthened target is:

∃c>0 ∀K>1 ∀A,W(A)>K⟹∃S⊆A:1−e
−cK
<W(S)≤1.

This stronger form implies the version with “A sufficiently large.”

Define the best attainable reciprocal sum below 1:

M(A)=max{W(S):S⊆A, W(S)≤1}.

The desired conclusion is

M(A)>1−e
−cK
.

Equivalently, with deficit

d(A)=1−M(A),

the desired conclusion is

d(A)<e
−cK
.

The negation of the strengthened statement is:

∀c>0 ∃K>1 ∃A,W(A)>K

such that

∀S⊆A,W(S)≤1−e
−cK
orW(S)>1.

Equivalently,

d(A)≥e
−cK
.

Useful boundary cases:

If A contains at least n copies of n, then choosing exactly those n copies gives

W(S)=n⋅
n
1
	​

=1,

so the conclusion holds exactly.

Thus any counterexample must satisfy, for every n,

m
A
	​

(n)<n

unless exact sum 1 is already present through a more complicated combination.

A basic invariant is the deficit of a maximal submultiset S with W(S)≤1. If

W(S)=1−d,

then every unused element 1/n must satisfy

n
1
	​

>d,

because otherwise S∪{n} would still have reciprocal sum at most 1, contradicting maximality.

Phase 1: Strategy search

I considered these independent routes.

Strategy	Idea	Obstacle
Direct greedy	Take maximal S≤1, bound the remaining mass	Gives only polynomial deficit
Contradiction	Assume d≥e
−cK
, force too much mass in small denominators	Needs strong bounded-denominator lemma
Construction	Try to build counterexamples with large total and large gap	Natural constructions shrink the gap very fast
Induction on K	Repeatedly reduce the deficit	Large terms may be unusable for small deficits
Induction on denominator bound	Prove bounded-denominator avoiding sets have small mass	Threshold changes under induction
Cardinal arithmetic	Count multiplicities m(n)<n	Too weak: gives O(1/d), not O(log(1/d))
Diagonalization	Force many subset sums near 1 by pigeonhole	Subset-sum collisions are hard to control
Compactness	Pass to extremal bad multisets	Existence is plausible, but structure remains difficult
Density argument	Show subset sums are dense near 1	Needs a quantitative density theorem
Reflection/replacement	Replace part of a maximal S by unused elements	Promising but needs coverage of subset sums of S
Auxiliary structure	Track forbidden intervals around subset sums	Produces a central gap lemma
Counterexample search	Use denominators with modular obstructions	No robust counterexample found

The three most useful branches were:

Greedy maximal-subset bounds.

Bounded-denominator reduction.

Replacement/forbidden-interval structure.

Branch A: Verified greedy bound

Let S⊆A maximize W(S)≤1. Write

W(S)=1−d.

If d=0, then W(S)=1, and the desired conclusion holds. So assume d>0.

By maximality, every unused element 1/n∈A∖S satisfies

n
1
	​

>d,

hence

n<
d
1
	​

.

Let R=A∖S. If R contained n copies of some denominator n, then those n copies alone would give sum 1, contradicting d>0. Therefore

m
R
	​

(n)≤n−1.

Since all denominators in R satisfy n<1/d,

W(R)=
n<1/d
∑
	​

n
m
R
	​

(n)
	​

≤
n<1/d
∑
	​

n
n−1
	​

<
n<1/d
∑
	​

1<
d
1
	​

.

On the other hand,

W(R)=W(A)−W(S)>K−(1−d)=K−1+d.

Thus

K−1+d<
d
1
	​

.

Equivalently,

d
2
+(K−1)d−1<0.

So

d<
2
(K−1)
2
+4
	​

−(K−1)
	​

.

For large K, this is approximately

d<
K−1
1
	​

.

So the verified greedy argument proves only a polynomial-scale conclusion:

M(A)>1−O(
K
1
	​

).

This does not prove the desired exponential bound.

Sanity check:

No hidden theorem was used. The only ingredients were maximality of S, the exact identity n⋅
n
1
	​

=1, and the multiplicity bound m
R
	​

(n)≤n−1. The quantifier scope is correct: the argument applies to every finite multiset A with W(A)>K.

Branch B: Bounded-denominator reduction

Let

δ=e
−cK
.

Suppose all elements with denominator n≥1/δ have total reciprocal mass >1. Since each such term is at most δ, the greedy algorithm applied only to those terms gives a submultiset S with

1−δ<W(S)≤1.

Therefore, in a counterexample, the large-denominator part must have total mass at most 1.

Hence the bounded-denominator part

A
≤1/δ
	​

={n∈A:n<1/δ}

must satisfy

W(A
≤1/δ
	​

)>K−1.

So the exponential theorem would follow from the following bounded-denominator lemma.

GAP NODE 1

For some absolute constant C, prove:

If B is a finite multiset of positive integers with all denominators n≤M, and no submultiset T⊆B satisfies

1−
M
1
	​

<W(T)≤1,

then

W(B)≤ClogM.

Indeed, taking M≈e
cK
, this would give

K−1<W(B)≤ClogM≈CcK.

Choosing c<1/C would contradict K−1>CcK for large enough K, proving the desired exponential bound.

This reduction is valid, but it is not a proof. The unresolved statement is exactly the logarithmic bounded-denominator lemma.

Branch C: Replacement structure around a maximal subset

Let S be maximal with

W(S)=1−d.

Let R=A∖S. For any q copies of some denominator n from R, suppose there were a submultiset U⊆S such that

0≤
n
q
	​

−W(U)<d.

Then replacing U by those q copies gives

W(S)−W(U)+
n
q
	​

=1−d−W(U)+
n
q
	​

.

The new deficit is

d+W(U)−
n
q
	​

.

If

0≤
n
q
	​

−W(U)<d,

then

0<d+W(U)−
n
q
	​

≤d,

so the new sum lies in

[1−d,1].

If the inequality is strict enough, it improves S, contradicting maximality or producing a forbidden near-1 subset.

Thus the unused part R is constrained by forbidden intervals around the subset sums of S:

n
q
	​

∈
/
W(P(S))+(0,d)

for all usable q,n.

This is a strong structural obstruction. To finish the proof, one would need to show that if W(R) is large, then some fraction q/n forced by R must fall into one of those forbidden intervals. That becomes a quantitative subset-sum covering problem.

GAP NODE 2

Prove that the subset sums of a maximal S with W(S)=1−d cover enough of [0,1] at scale d to force a replacement whenever W(R)≫log(1/d).

I attacked this in several ways:

Direct density of subset sums of S: insufficient because S may have few elements.

Dyadic decomposition of S: gives scale information but not interval coverage.

Pigeonhole on subset sums: gives close signed differences, not necessarily positive usable replacements.

Modular denominator analysis: promising for bounded denominators, but requires controlling collisions.

Induction on d
−1
: threshold changes after removing elements.

Entropy lower bounds: need distinct subset sums, which can collapse because of unit-fraction identities.

Greedy coverage lemma: works for arbitrary small terms, but fails when remaining terms are larger than the current deficit.

Compression by denominator divisibility: works for composite denominators but fails on primes.

Extremal multiset analysis: suggests logarithmic mass may be true, but does not yield a proof.

Replacement graph between S and R: gives a natural auxiliary structure, but I did not close the covering estimate.

No attack completed GAP NODE 2.

Verified theorem obtained

The following weaker statement is fully proved:

For every finite multiset A of positive integers with

W(A)>K>1,

there exists S⊆A such that

1−
2
(K−1)
2
+4
	​

−(K−1)
	​

<W(S)≤1.

Equivalently, for large K,

W(S)>1−O(
K
1
	​

).

This is not the requested exponential bound.

Dependency graph

Verified:

Definition of M(A), d(A).

Maximal-subset lemma: unused elements have reciprocal value >d(A).

Multiplicity lemma: if d(A)>0, then no denominator n can occur n times in the unused part.

Greedy polynomial bound:

d(A)<
2
(K−1)
2
+4
	​

−(K−1)
	​

.

Unresolved:

Logarithmic bounded-denominator lemma.

Quantitative replacement-covering lemma.

Exponential deficit bound.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified polynomial bound.

COMPLETENESS_SCORE: 35/100 for the original exponential problem.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the verified lemmas; 0/100 for the unresolved exponential claim, because no proof was completed.

RESOURCE_USAGE: about 80% of available reasoning budget used; 12 strategies generated; 4 verified lemmas; 3 major failed proof attempts; 2 primary unresolved gap nodes.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #953 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Formalization

For r>0, write

B
r
	​

:={x∈R
2
:∣x∣<r},

and define the extremal quantity

M(r):=sup{m
2
	​

(A):A⊆B
r
	​

 measurable and (∀a,b∈A)[a

=b⇒∣a−b∣∈
/
Z]}.

Here m
2
	​

 is two-dimensional Lebesgue measure.

Since distinct points have positive distance, the condition is equivalently

(A−A)∩{x∈R
2
:∣x∣∈N}=∅.
Quantifier structure

The desired extremal statement asks for bounds on

A
sup
	​

m
2
	​

(A),

where A ranges over all measurable subsets of B
r
	​

 satisfying

∀a∈A∀b∈A,a=b ∨ ∀n∈N, ∣a−b∣

=n.
Negation of admissibility

A measurable A⊂B
r
	​

 is not admissible exactly when

∃a,b∈A∃n∈Nsuch thata

=b,∣a−b∣=n.
Equivalent translation formulation

For every n∈N and every unit vector u∈S
1
,

A∩(A+nu)=∅.

Indeed, a point in this intersection gives two points of A differing by the vector nu, and conversely every pair at distance n determines such a unit vector.

Immediate invariances

The admissibility condition is invariant under:

translations;

rotations;

reflections;

passage to measurable subsets.

It is not invariant under arbitrary scaling, because the forbidden set of distances is specifically N.

Boundary cases

If 0<r≤
2
1
	​

, then any two points of B
r
	​

 are at distance strictly less than 2r≤1. Therefore B
r
	​

 itself is admissible, and hence

M(r)=πr
2
(0<r≤
2
1
	​

).

For general r,

M(r)≤m
2
	​

(B
r
	​

)=πr
2
.
A one-dimensional fiber lemma
Lemma

Let E⊂R be measurable and suppose

x,y∈E,x

=y⟹x−y∈
/
Z.

Then

m
1
	​

(E)≤1.
Proof

For each k∈Z, define

E
k
	​

:=(E∩[k,k+1))−k⊂[0,1).

We claim that the sets E
k
	​

 are pairwise disjoint.

Suppose z∈E
j
	​

∩E
k
	​

. Then

z+j∈E,z+k∈E.

Their difference is

(z+j)−(z+k)=j−k∈Z.

If j

=k, these are distinct points of E at integer distance, contradicting the hypothesis. Thus j=k, proving pairwise disjointness.

Translation invariance and countable additivity of Lebesgue measure give

m
1
	​

(E)=
k∈Z
∑
	​

m
1
	​

(E∩[k,k+1))=
k∈Z
∑
	​

m
1
	​

(E
k
	​

).

Since the E
k
	​

 are pairwise disjoint subsets of [0,1),

k∈Z
∑
	​

m
1
	​

(E
k
	​

)=m
1
	​

(
k∈Z
⋃
	​

E
k
	​

)≤1.

Therefore m
1
	​

(E)≤1. □

Adversarial check

The proof uses exact integer differences, not merely positive integer differences. If j−k<0, its absolute value is a positive integer, so the original distance condition still forbids the pair.

The half-open partition [k,k+1) ensures that boundary points are assigned uniquely.

No boundedness assumption on E is required.

Linear upper bound
Theorem

For every r>0,

M(r)≤2r.

Consequently,

M(r)≤min{πr
2
,2r}.
Proof

Let A⊂B
r
	​

 be measurable and admissible.

Choose orthonormal coordinates (s,t), and for each t∈R define the horizontal fiber

A
t
	​

:={s∈R:(s,t)∈A}.

For almost every t, the set A
t
	​

 is measurable.

If s
1
	​

,s
2
	​

∈A
t
	​

 and s
1
	​


=s
2
	​

, then

∣(s
1
	​

,t)−(s
2
	​

,t)∣=∣s
1
	​

−s
2
	​

∣.

Therefore s
1
	​

−s
2
	​

 cannot be a nonzero integer. The fiber lemma gives

m
1
	​

(A
t
	​

)≤1

for almost every t.

Moreover, A⊂B
r
	​

 implies A
t
	​

=∅ whenever ∣t∣≥r. By Fubini–Tonelli,

m
2
	​

(A)=∫
R
	​

m
1
	​

(A
t
	​

)dt=∫
−r
r
	​

m
1
	​

(A
t
	​

)dt≤∫
−r
r
	​

1dt=2r.

Taking the supremum over admissible A proves the assertion. □

Dependency graph
No integer Euclidean distances⟹no integer differences inside any line fiber
⟹m
1
	​

(A
t
	​

)≤1
⟹m
2
	​

(A)=∫m
1
	​

(A
t
	​

)dt≤2r.
Sanity check

The conclusion was not assumed.

The fiber condition follows because collinear Euclidean distance equals the absolute coordinate difference.

The exceptional null set of nonmeasurable fibers does not affect Fubini’s integral.

The transverse parameter occupies an interval of length 2r, not an area of order r
2
.

No compactness, choice, or unstated regularity hypothesis is used.

Elementary lower bound
Proposition

For every r>0,

M(r)≥πmin{r,
2
1
	​

}
2
.
Proof

Put

ρ:=min{r,
2
1
	​

}

and take

A=B
ρ
	​

.

Because the disk is open, any two points a,b∈B
ρ
	​

 satisfy

∣a−b∣<2ρ≤1.

Thus distinct points of A have distance strictly between 0 and 1, and therefore cannot have integer distance. Hence A is admissible and

m
2
	​

(A)=πρ
2
.

□

Combining the verified estimates,

πmin{r,
2
1
	​

}
2
≤M(r)≤min{πr
2
,2r}.
	​


In particular,

M(r)=πr
2
for 0<r≤
2
1
	​

,

while for large r,

4
π
	​

≤M(r)≤2r.
Breadth-first strategy search
1. Direct fiber decomposition

Idea: Restrict A to parallel lines and apply a one-dimensional modular argument.

Outcome: Successfully proves M(r)≤2r.

Obstacle to sharpness: It uses only pairs lying on the same parallel line and discards all cross-fiber restrictions.

2. Translation packing

For every unit vector u, the sets

A, A+u, A+2u,…

are pairwise disjoint whenever their translation indices differ by an integer.

Inside a containing strip of length O(r+N), this reproduces a linear estimate after letting N grow.

Outcome: Equivalent in strength to the fiber argument.

Obstacle: Translations along one direction again use only a one-dimensional part of the distance condition.

3. Polar decomposition

Write points as (ρ,θ). On a fixed ray, two points have distance ∣ρ
1
	​

−ρ
2
	​

∣, so each radial fiber has measure at most 1.

The area formula would give

m
2
	​

(A)=∫
0
2π
	​

∫
A
θ
	​

	​

ρdρdθ.

Although m
1
	​

(A
θ
	​

)≤1, the weighted integral can be as large as r on each ray, yielding at best O(r), with an inferior constant.

Obstacle: The radial weight ρ.

4. Fourier autocorrelation

For every n∈N and u∈S
1
,

∫
R
2
	​

1
A
	​

(x)1
A
	​

(x+nu)dx=0.

Averaging over u gives circular autocorrelation identities. Formally, these involve the multipliers J
0
	​

(2πn∣ξ∣).

Potential: Simultaneously uses all directions and all forbidden integers.

Unresolved issue: A pointwise or averaged lower bound for a suitable finite linear combination of the oscillatory multipliers strong enough to control ∥1
A
	​

∥
1
	​

 was not established.

5. Distance-energy method

Define the distance measure

ν(E)=m
2
	​

×m
2
	​

{(a,b)∈A
2
:∣a−b∣∈E}.

Admissibility says

ν({n})=0(n∈N).

Obstacle: For a general measurable set, the distance distribution can already assign zero mass to every singleton without imposing a strong restriction. Exact zero at isolated radii is not directly controlled by ordinary L
1
 estimates.

6. Unit-cell decomposition

Partition the plane into unit squares. Within each horizontal line, translates modulo one must be disjoint.

Outcome: Repackages the fiber proof.

Possible extension: Couple several rotated unit-square decompositions.

Gap: No verified inequality combining multiple directions without overcounting was obtained.

7. Multiple-direction tomography

For every unit vector u, each line parallel to u contains at most one unit of one-dimensional measure from A.

This gives a family of X-ray inequalities:

∫
R
	​

m
1
	​

(A∩(tu
⊥
+Ru))dt≤2r.

Every individual direction gives the same area bound.

Obstacle: These are not independent inequalities; their left sides all equal m
2
	​

(A). Averaging them does not improve the estimate.

8. Induction on annuli

Decompose

B
r
	​

=
k
⋃
	​

{k≤∣x∣<k+1}.

Attempt to bound interactions between separated annuli.

Obstacle: Radial separation does not determine Euclidean distance because angular separation can vary continuously.

9. Compactness and finite distance graphs

Discretize B
r
	​

 into small cells and connect cells whenever some pair of their points can be at an integer distance.

Obstacle: “Some pair” produces too many edges, while “every pair” produces too few. Exact-distance avoidance is unstable under coarse discretization unless quantitative neighborhoods of the integers are forbidden.

10. Random construction

Take many small disks centered at selected points, requiring every center-to-center distance to stay farther than twice the disk radius from every integer.

Obstacle: Among N centers there are (
2
N
	​

) constraints. A naive random selection forces the disk radius to shrink too quickly, and the resulting total area does not grow.

11. Curve thickening

Place A in a thin neighborhood of a curve whose chord lengths avoid integers.

Obstacle: A connected curve of large diameter has a continuous chord-length image and therefore ordinarily realizes many integer values. A disconnected curve family avoids this continuity argument but reintroduces many pairwise constraints.

12. Modular distance coding

Assign points labels based on one or more coordinates modulo 1, attempting to choose a large label class on which integer Euclidean distances are impossible.

Obstacle: Integer Euclidean distance does not imply an integer difference in either coordinate. A single modular coordinate detects only collinear forbidden pairs.

Three strongest branches after verification

Fiber/modular decomposition: complete, yields M(r)≤2r.

Fourier circular autocorrelation: structurally uses the entire condition, but lacks a verified coercive multiplier inequality.

Geometric separated-component construction: potentially yields growing lower bounds, but no construction with rigorously controlled neighborhoods of all integer distances was completed.

The second and third branches contain unresolved primary targets:

Target F:derive a coercive inequality from all circular autocorrelation zeros;
Target C:construct a planar measurable set of unbounded area whose distance set avoids N.

Repeated attacks through finite Fourier combinations, annular decompositions, randomized centers, curve neighborhoods, and modular coordinate systems did not produce a complete proof of a sharper upper bound or a growing lower-bound construction from the stated assumptions alone.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 99/100 for the displayed upper bound, elementary lower bound, and exact result for r≤
2
1
	​

.

COMPLETENESS_SCORE: 35/100. The extremal quantity was formalized and rigorous general bounds were proved, but its large-r order was not determined.

ADVERSARIAL_SURVIVAL_SCORE: 97/100 for the proved statements.

RESOURCE_USAGE: Approximately 100% of the allocated reasoning budget; 12 principal strategies examined; 3 verified lemmas/theorems generated; 8 materially distinct incomplete approaches retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

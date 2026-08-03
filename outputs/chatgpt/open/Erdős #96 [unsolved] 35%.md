# Erdős Problem #96 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Complete formalization

Let P={p
1
	​

,…,p
n
	​

}⊂R
2
.
Assume the points are the vertices of a convex polygon, meaning every point of P is an extreme point of conv(P).

Define the unit-distance graph

G
1
	​

(P)=(P,E
1
	​

),E
1
	​

={{p
i
	​

,p
j
	​

}:i

=j, ∣p
i
	​

−p
j
	​

∣=1}.

The target statement is:

∃C>0 ∀n∈N ∀P⊂R
2
,(P convex position, ∣P∣=n)⇒∣E
1
	​

(P)∣≤Cn.

Equivalently,

P convex,∣P∣=n
sup
	​

∣E
1
	​

(P)∣=O(n).

The negation is:

∀C>0 ∃n∈N ∃P⊂R
2

such that P is in convex position, ∣P∣=n, and

∣E
1
	​

(P)∣>Cn.

A contrapositive form for a fixed constant C would be:

∣E
1
	​

(P)∣>Cn⇒P is not a convex n-point set.

But since C is existential, the useful negation is the superlinear family formulation above.

The core object is therefore the number of unit chords among the vertices of a convex n-gon.

Immediate verified observations
Observation 1: The problem is equivalent to bounding average unit degree

Let

d
1
	​

(p)=∣{q∈P:q

=p, ∣p−q∣=1}∣.

Then

p∈P
∑
	​

d
1
	​

(p)=2∣E
1
	​

(P)∣.

So the desired theorem is equivalent to

p∈P
∑
	​

d
1
	​

(p)=O(n).
Observation 2: Bounded maximum degree is false

There exist convex n-point sets where one vertex has unit degree n−1.

Construction: take

p
0
	​

=(0,0),

and choose p
1
	​

,…,p
n−1
	​

 on a circular arc of radius 1 centered at p
0
	​

, contained in an angle <π. Then all p
i
	​

 lie on the unit circle around p
0
	​

, so

∣p
0
	​

−p
i
	​

∣=1

for all i≥1. Choosing the arc strictly convex and shorter than a semicircle makes all points vertices of the convex hull. Hence

d
1
	​

(p
0
	​

)=n−1.

Therefore any proof based on showing d
1
	​

(p)≤C for every vertex is impossible.

Observation 3: A general incidence bound gives only O(n
3/2
)

For each p∈P, let C
p
	​

 be the circle of radius 1 centered at p. A unit distance {p,q} corresponds to two incidences:

q∈C
p
	​

,p∈C
q
	​

.

Let

I=∣{(p,q)∈P
2
:p

=q, ∣p−q∣=1}∣=2∣E
1
	​

(P)∣.

For each q∈P, let

r(q)=∣{p∈P:q∈C
p
	​

}∣.

Then

I=
q∈P
∑
	​

r(q).

Two distinct unit circles intersect in at most two points. Therefore

q∈P
∑
	​

(
2
r(q)
	​

)≤2(
2
n
	​

).

Thus

q
∑
	​

r(q)(r(q)−1)≤2n(n−1).

Also,

q
∑
	​

r(q)
2
=
q
∑
	​

r(q)(r(q)−1)+
q
∑
	​

r(q)≤2n(n−1)+I.

By Cauchy-Schwarz,

I
2
≤n
q
∑
	​

r(q)
2
≤n(2n(n−1)+I).

So

I=O(n
3/2
),

hence

∣E
1
	​

(P)∣=O(n
3/2
).

This uses no convexity. It is rigorously verified but far from the desired O(n).

Phase 1: Breadth-first strategy search

I considered the following independent routes.

Strategy	Description	Obstacle
Direct degree bound	Show average unit degree is bounded	Equivalent to target; no local bound possible
Minimal counterexample	Assume smallest convex P with too many unit edges	Need removable vertex with controlled lost edges
Induction	Remove a low unit-degree vertex	Requires bounded degeneracy; unproved
High-degree fan analysis	Large degree forces neighbors onto a unit circle arc	Need control of overlap among many fans
Incidence geometry	Count incidences between points and unit circles	Gives only O(n
3/2
) directly
Forbidden subgraph	Unit-distance graph has no K
2,3
	​

	Too weak for linearity
Convex adjacency matrix	Put vertices in cyclic order and study unit-distance matrix	Need strong forbidden pattern beyond K
2,3
	​


Crossing-chord analysis	Study pairs of crossing unit chords	Crossing unit chords exist; need global packing
Diagonalization	Construct many unit edges by recursive adversarial placement	No superlinear convex construction found
Compactness / limiting curve	Replace polygon by convex curve with many unit chords	Needs discrete-to-continuous transfer
Density argument	Find a dense block of unit chords, then contradict convexity	Dense blocks can be fan-like and locally consistent
Reflection / circle intersections	Reflect points across unit-circle constraints	Common-neighbor control gives only quadratic-pair bounds
Auxiliary shadows	Assign each unit edge to a private interval of boundary vertices	Promising but unproved
Stronger g(x)-sum bound	Prove ∑
x
	​

g(x)=O(n)	Strictly stronger; no derivation found

Top three routes by expected value:

High-degree fan / private-shadow decomposition.

Convex adjacency matrix forbidden-pattern approach.

Induction via bounded degeneracy or weak degeneracy.

Phase 2: New definitions and invariants
Definition: unit neighbor set

For p∈P,

N
1
	​

(p)={q∈P:q

=p, ∣p−q∣=1}.

Then

d
1
	​

(p)=∣N
1
	​

(p)∣.
Definition: unit fan

A vertex p is called a unit fan center if d
1
	​

(p) is large. Its fan is the set N
1
	​

(p), lying on the circle C
p
	​

.

Fan examples show one vertex can support linearly many unit distances, so the problem is not to rule out fans. The real target is to show that many large fans cannot coexist without forcing overlap or nonconvexity.

Definition: cyclic shadow

Fix the cyclic order

p
1
	​

,p
2
	​

,…,p
n
	​


around the convex hull. For a vertex p
i
	​

, define the shadow S(p
i
	​

) to be the smallest cyclic interval containing all vertices of N
1
	​

(p
i
	​

).

If one could prove

p∈P
∑
	​

∣S(p)∣=O(n),

then since

d
1
	​

(p)≤∣S(p)∣,

we would get

p
∑
	​

d
1
	​

(p)=O(n).

But this shadow bound is not established. It becomes a primary gap.

Phase 3: Parallel exploration
Branch A: Fan-shadow approach

Goal:

p
∑
	​

d
1
	​

(p)=O(n)

by showing that high-degree fans require mostly private boundary intervals.

Candidate lemma:

There exists an absolute constant K such that every vertex v∈P has a shadow S(v), and every polygon vertex lies in at most K large shadows.

If true, then

v
∑
	​

d
1
	​

(v)≤
v
∑
	​

∣S(v)∣≤Kn,

which proves the theorem.

Attack on lemma: two nearby fan centers cannot share many actual unit neighbors, because two unit circles meet in at most two points. However, their shadows may overlap heavily even if their actual unit-neighbor sets do not overlap. I found no contradiction from shadow overlap alone.

Status: unresolved.

Branch B: Convex adjacency matrix

Split the polygon into two boundary chains A and B. Define a 0-1 matrix

M
ij
	​

=1⟺∣a
i
	​

−b
j
	​

∣=1.

The total number of unit distances between the two chains is the number of ones in M. If convexity forced M to avoid a sufficiently strong pattern, then a linear bound might follow.

Verified weak fact: since two points have at most two common unit neighbors, M cannot contain a 2×3 all-one submatrix, nor a 3×2 all-one submatrix.

But this only implies approximately O(n
3/2
), not O(n). To obtain O(n), one would need a stronger convex-order forbidden pattern.

Candidate missing lemma:

In the unit-distance matrix induced by two convex chains, long alternating staircases of ones are impossible.

Attack: crossing unit chords and nested unit chords both exist in convex polygons. Local forbiddenness is insufficient. No complete global obstruction was derived.

Status: unresolved.

Branch C: Inductive low-degree approach

If every convex unit-distance graph had a vertex of unit degree at most D, then induction would prove

∣E
1
	​

(P)∣≤Dn.

Indeed, remove such a vertex v. The remaining n−1 points are still in convex position or at least have a convex-position subset after deletion, and at most D unit edges are lost. Then

e(n)≤e(n−1)+D,

so

e(n)≤Dn.

Primary gap:

Does every convex n-point set have a vertex incident to O(1) unit edges?

The fan construction does not disprove this, because although one vertex has degree n−1, most other vertices in that construction have small degree. But I found no proof that every convex configuration has a bounded-degree vertex.

Status: unresolved.

Phase 4: Verified theorem pool
Lemma 1: High maximum degree is possible

There are convex n-point sets with

p∈P
max
	​

d
1
	​

(p)=n−1.

Verified by the circular-arc fan construction above.

Lemma 2: Unit-distance graphs have no K
2,3
	​


Suppose two distinct vertices a,b∈P had three common unit neighbors x,y,z. Then

∣a−x∣=∣a−y∣=∣a−z∣=1

and

∣b−x∣=∣b−y∣=∣b−z∣=1.

Thus x,y,z all lie in

C
a
	​

∩C
b
	​

,

where C
a
	​

,C
b
	​

 are two distinct unit circles. Two distinct circles intersect in at most two points. Contradiction.

Therefore the unit-distance graph contains no K
2,3
	​

.

Lemma 3: General unit-distance bound O(n
3/2
)

For any n-point set in the plane,

∣E
1
	​

(P)∣=O(n
3/2
).

Proof given above by incidence counting. Convexity was unused.

Phase 5: Deep execution of the most promising branch

The best branch was the fan-shadow approach.

The desired proof would be:

For each vertex p, the unit neighbors N
1
	​

(p) lie on the unit circle C
p
	​

.

Since P is in convex position, these neighbors appear in cyclic order around the polygon.

A large set N
1
	​

(p) therefore creates a visible fan from p.

If many vertices had large fans, their unit circles would impose many repeated circle intersections.

Because two unit circles intersect at at most two points, large overlaps are impossible.

Therefore high-degree contributions are almost disjoint.

Hence

p
∑
	​

d
1
	​

(p)=O(n).

The failure occurs at step 4-to-5.

The obstruction is precise:

Circle-intersection control bounds common unit neighbors.

The desired charging argument needs control over overlapping cyclic regions or interleaving fan intervals.

Two fan shadows can overlap heavily without the corresponding unit-neighbor sets sharing many vertices.

Thus the available verified fact

∣N
1
	​

(p)∩N
1
	​

(q)∣≤2

does not imply

∣S(p)∩S(q)∣=O(1).

The missing statement is:

Large fan shadows cannot overlap too much in a convex polygon.
	​


I attempted the following attacks on this gap:

Direct geometric proof using convexity of boundary chains.

Contradiction from two overlapping large shadows.

Stronger theorem: shadows have bounded multiplicity.

Weaker theorem: only high-degree shadows have bounded multiplicity.

Reformulation using radial functions from each vertex.

Reformulation using support lines and polar angle order.

Circle-intersection counting among fan centers.

Extremal example search with several large fans.

Matrix version using rows as fan centers and columns as shadow vertices.

Decomposition into short and long unit chords.

None produced a complete proof. Several reduce back to needing a new convex-order lemma stronger than the two-circle intersection bound.

Adversarial referee check
Attack 1: Does the O(n
3/2
) incidence proof accidentally prove O(n)?

No. The only structural input is that two unit circles intersect in at most two points. That gives a K
2,3
	​

-free graph. Such information is insufficient for a linear edge bound in general.

So the incidence proof cannot be upgraded without extra convexity input.

Attack 2: Can one prove the theorem by bounding every degree?

No. The circular-arc fan gives a convex n-point set with one vertex of degree n−1. Therefore any proof requiring

d
1
	​

(p)=O(1)

for every p is invalid.

Attack 3: Can induction work by removing a bounded-degree vertex?

Possibly, but I did not prove the needed bounded-degeneracy statement. It remains a primary unresolved gap.

Attack 4: Can one prove bounded overlap of unit-neighbor sets?

Yes, but only weakly:

∣N
1
	​

(p)∩N
1
	​

(q)∣≤2.

This is insufficient because total edge count depends on

p
∑
	​

∣N
1
	​

(p)∣,

and pairwise intersection control alone gives only quadratic or n
3/2
-type bounds, not linear bounds.

Dependency graph of verified results
two circles meet in at most two points

implies

unit-distance graph is K
2,3
	​

-free

implies

∣E
1
	​

(P)∣=O(n
3/2
).

Separately,

circular-arc fan construction

implies

p
max
	​

d
1
	​

(p) can be n−1.

No verified chain obtained

∣E
1
	​

(P)∣=O(n).
Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 0/100 for the original O(n) statement, because no complete proof was obtained.

COMPLETENESS_SCORE: 35/100. The formalization, several reductions, the fan obstruction, the K
2,3
	​

-free property, and the O(n
3/2
) bound were rigorously established, but the central linear bound was not.

ADVERSARIAL_SURVIVAL_SCORE: 80/100 for the verified partial lemmas; 0/100 for the full target theorem.

RESOURCE_USAGE: approximately 100% of the current reasoning budget; 3 main branches explored; 3 verified lemmas generated; 4 failed proof attempts isolated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

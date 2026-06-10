# Erdős Problem #86 [unsolved] 45%

---

## ChatGPT Response

Phase 0: Deconstruction
Objects

Let

V(Q
n
	​

)={0,1}
n
.

Two vertices x,y are adjacent when they differ in exactly one coordinate. Let e
i
	​

 denote the vector flipping coordinate i. The edge in direction i based at x with x
i
	​

=0 is

{x,x+e
i
	​

}.

The number of edges is

∣E(Q
n
	​

)∣=n2
n−1
.

A C
4
	​

 in Q
n
	​

 is exactly the boundary of a 2-dimensional face: choose two distinct coordinates i,j and fix the other n−2 coordinates. The four vertices form a square.

Let

f(n)=max{∣E(H)∣:H⊆Q
n
	​

, H contains no C
4
	​

}.

The target statement is

f(n)≤(
2
1
	​

+o(1))n2
n−1
.

Equivalently, if

d
n
	​

:=
n2
n−1
f(n)
	​

,

then the target is

n→∞
limsup
	​

d
n
	​

≤
2
1
	​

.

Since a construction below gives d
n
	​

≥1/2, the target is equivalent to

n→∞
lim
	​

d
n
	​

=
2
1
	​

.
Quantifier structure

The desired assertion is:

∀ε>0 ∃N ∀n≥N ∀H⊆Q
n
	​

,

if

∣E(H)∣≥(
2
1
	​

+ε)n2
n−1
,

then H contains a C
4
	​

.

The negation is:

∃ε>0 ∀N ∃n≥N ∃H⊆Q
n
	​


such that

∣E(H)∣≥(
2
1
	​

+ε)n2
n−1

and H contains no C
4
	​

.

So a disproof would require a fixed positive excess ε occurring for infinitely many dimensions.

Contrapositive

For every fixed ε>0, if H⊆Q
n
	​

 is C
4
	​

-free for all sufficiently large n, then

∣E(H)∣<(
2
1
	​

+ε)n2
n−1
.
Equivalent formulations
1. Edge-density formulation

Let

d(H)=
n2
n−1
∣E(H)∣
	​

.

The target is:

H⊆Q
n
	​

, C
4
	​


⊂H
sup
	​

d(H)→
2
1
	​

.
2. Missing-edge hitting formulation

Let

M:=E(Q
n
	​

)∖E(H).

Then H is C
4
	​

-free iff M intersects every 2-dimensional face of Q
n
	​

. Thus the problem is equivalent to proving that every edge set hitting all 2-faces has size

∣M∣≥(
2
1
	​

−o(1))n2
n−1
.

So f(n)≤(1/2+o(1))∣E(Q
n
	​

)∣ is equivalent to:

τ
2
	​

(Q
n
	​

)≥(
2
1
	​

−o(1))∣E(Q
n
	​

)∣,

where τ
2
	​

(Q
n
	​

) is the minimum number of edges meeting every square face.

3. Direction-support formulation

For each coordinate i, define

A
i
	​

⊆{0,1}
[n]∖{i}

by placing a point u∈A
i
	​

 when the corresponding i-direction edge is selected.

Let

α
i
	​

:=
2
n−1
∣A
i
	​

∣
	​

.

Then

∣E(H)∣=
i=1
∑
n
	​

∣A
i
	​

∣,

and

d(H)=
n
1
	​

i=1
∑
n
	​

α
i
	​

.

For i

=j, define the j-parallel-pair shadow of A
i
	​

:

P
j
	​

(A
i
	​

)={z∈{0,1}
[n]∖{i,j}
: z∪{j=0}∈A
i
	​

, z∪{j=1}∈A
i
	​

}.

The C
4
	​

-free condition is exactly

P
j
	​

(A
i
	​

)∩P
i
	​

(A
j
	​

)=∅

for every i

=j.

This is one of the cleanest exact reformulations.

Extremal cases and basic constructions
n=1

There is no C
4
	​

, so

f(1)=1.
n=2

The whole graph Q
2
	​

 is one C
4
	​

. A C
4
	​

-free subgraph has at most 3 edges, so

f(2)=3.

Thus

d
2
	​

=
4
3
	​

.
Universal lower bound f(n)≥
2
1
	​

n2
n−1

Define H
⋆
	​

⊆Q
n
	​

 as follows. For an edge in direction i, based at x with x
i
	​

=0, include the edge iff

r

=i
∑
	​

x
r
	​

≡0(mod2).

For each fixed direction i, exactly half of the i-edges are selected, so

∣E(H
⋆
	​

)∣=
2
1
	​

n2
n−1
.

Now consider a square in directions i,j, with all other coordinates fixed. Let

s=
r

=i,j
∑
	​

x
r
	​

(mod2).

The two i-edges are selected according to s+j, so exactly one of them is selected. The two j-edges are selected according to s+i, so exactly one of them is selected. Therefore every square has exactly two selected edges, hence no square is fully selected. Thus

f(n)≥
2
1
	​

n2
n−1
.

So the desired upper bound, if true, is asymptotically sharp.

Phase 1: Breadth-first strategy generation
Strategy	Description	Hidden assumption	Obstacle	Confidence	Expected value
Direct face counting	Count incidences between selected edges and square faces	That local face constraints suffice	Gives only 3/4 density	High	Medium
Vertex-pair counting	Count selected adjacent direction pairs at vertices	Pair constraints force density near 1/2	Gives only 1/
2
	​

 density	High	Medium
Direction shadows	Use P
j
	​

(A
i
	​

)∩P
i
	​

(A
j
	​

)=∅	Shadows are large when α
i
	​

>1/2	Lower bounds too weak	Medium	High
Missing-edge transversal	Study edge sets hitting every square	Minimum transversal near half	Local lower bound gives only quarter	Medium	High
Induction on n	Split Q
n
	​

 into two Q
n−1
	​

 layers plus matching	Intersection of dense layers has small independence number	No strong independence bound available	Medium	High
Finite-subcube averaging	Relate d
n
	​

 to d
k
	​

 for fixed k	Finite d
k
	​

→1/2 can be proved	This is essentially equivalent to the target	High	High
Compactness	If excess persists, pass to an infinite local limit	Infinite local object violates a mass-transport inequality	Need such an inequality	Low	Medium
Spectral/Fourier	Represent edge indicators as coordinate-invariant functions	No-full-square condition gives strong Fourier restriction	Only weak pairwise restrictions found	Low	Medium
Entropy	Bound entropy of local square patterns	Local pattern constraints imply global density bound	Local constraints allow density 3/4	Low	Medium
Diagonalization	Construct an infinite counterexample from finite dense examples	Dense finite examples are mutually compatible	Compatibility not guaranteed	Low	Medium
Transfinite induction	Treat dimension growth through ordinal-indexed limits	Infinite cube has a useful well-ordering structure	Original parameter is finite; no natural transfinite step found	Very low	Low
Auxiliary structure invention	Introduce pair-loads, shadows, transversal defects	New invariant closes the gap	No invariant found strong enough	Medium	High

Top three selected branches:

Direction-shadow / pair-load method.

Inductive layer decomposition.

Missing-edge transversal method.

Phase 2: New definitions and invariants
Definition 1: Direction density

For each direction i,

α
i
	​

=
2
n−1
∣A
i
	​

∣
	​

.

Then

d(H)=
n
1
	​

i
∑
	​

α
i
	​

.

Motivation: a C
4
	​

 always involves two directions, so edge distribution by direction is natural.

Definition 2: Parallel-pair shadow

For i

=j,

P
j
	​

(A
i
	​

)={z: both i-edges above z in the j-direction are selected}.

Motivation: a square in directions i,j is fully selected exactly when both the i-parallel pair and the j-parallel pair are selected.

Consequence:

H is C
4
	​

-free⟺P
j
	​

(A
i
	​

)∩P
i
	​

(A
j
	​

)=∅

for all i

=j.

Definition 3: Missing-edge transversal

Let

M=E(Q
n
	​

)∖E(H).

Then M is a square-transversal:

∀ 2-face F,M∩E(F)

=∅.

Motivation: proving H has at most half the edges is equivalent to proving that every square-transversal has at least half the edges.

Definition 4: Local pair-load

For a vertex v, let

d
H
	​

(v)=∣{i:v∼v+e
i
	​

 and vv+e
i
	​

∈E(H)}∣.

The number of selected adjacent edge-pairs at v is

(
2
d
H
	​

(v)
	​

).

Motivation: each pair of selected incident edges at v occupies one corner of a square.

Definition 5: Subcube extremal density

Let

d
n
	​

=
n2
n−1
f(n)
	​

.

The target is

d
n
	​

→
2
1
	​

.

Motivation: random restriction to lower-dimensional subcubes gives exact monotonicity.

Phase 3: Verified theorem pool
Lemma 1: Every C
4
	​

 in Q
n
	​

 is a 2-face

Take a 4-cycle

v
0
	​

v
1
	​

v
2
	​

v
3
	​

v
0
	​

.

Each edge flips one coordinate. Let the flipped coordinates around the cycle be

a,b,c,d.

Returning to v
0
	​

 means every coordinate is flipped an even number of times. Since the cycle has length 4 and no repeated edge, the flips must be

i,j,i,j

with i

=j. Thus the cycle lies in the 2-dimensional face spanned by coordinates i,j.

So forbidding C
4
	​

 is exactly forbidding fully selected 2-faces.

SANITY CHECK: No hidden theorem used. This follows directly from coordinate parity.

Lemma 2: Face-counting gives
f(n)≤
4
3
	​

n2
n−1
.

There are

(
2
n
	​

)2
n−2

2-faces.

Each selected edge lies in exactly n−1 2-faces.

If H is C
4
	​

-free, every 2-face contains at most 3 selected edges. Therefore

∣E(H)∣(n−1)≤3(
2
n
	​

)2
n−2
.

Since

3(
2
n
	​

)2
n−2
=3
2
n(n−1)
	​

2
n−2
=3n(n−1)2
n−3
,

we get

∣E(H)∣≤3n2
n−3
=
4
3
	​

n2
n−1
.

So

d
n
	​

≤
4
3
	​

.

SANITY CHECK: This proves only 3/4, not the desired 1/2+o(1).

Lemma 3: Direction-shadow disjointness

For i

=j,

P
j
	​

(A
i
	​

)∩P
i
	​

(A
j
	​

)=∅.

Proof: if some base point z belongs to both sets, then in the square spanned by i,j over z, both i-parallel edges and both j-parallel edges are selected. Hence all four boundary edges are selected, giving a C
4
	​

. Conversely, if a C
4
	​

 exists in directions i,j, its base point lies in both shadows.

SANITY CHECK: Exact equivalence, no loss.

Lemma 4: Internal-shadow lower bound

Let A⊆Q
m
	​

 have density

α=
2
m
∣A∣
	​

.

Let I(A) be the number of edges of Q
m
	​

 with both endpoints in A. Then

I(A)≥m(2α−1)2
m−1

whenever α≥1/2.

Proof: Let ∂A be the edge boundary between A and its complement. Since every vertex of A
c
 has degree m,

∣∂A∣≤m∣A
c
∣=m(1−α)2
m
.

Also

m∣A∣=2I(A)+∣∂A∣.

Therefore

2I(A)=mα2
m
−∣∂A∣≥mα2
m
−m(1−α)2
m
=m(2α−1)2
m
.

Hence

I(A)≥m(2α−1)2
m−1
.

SANITY CHECK: This is valid but crude. It only uses the trivial boundary upper bound.

Applied to A
i
	​

⊆Q
n−1
	​

, this gives a lower bound on

j

=i
∑
	​

∣P
j
	​

(A
i
	​

)∣.

Together with shadow disjointness, it recovers only the 3/4 upper bound, not the desired 1/2.

Lemma 5: Vertex-pair counting gives
f(n)≤(
2
	​

1
	​

+O(
n
1
	​

))n2
n−1
.

Let H⊆Q
n
	​

 be C
4
	​

-free.

Split vertices into even and odd parity classes:

V
0
	​

={x:∣x∣≡0(mod2)},V
1
	​

={x:∣x∣≡1(mod2)}.

Each has size 2
n−1
.

Fix a parity class V
ρ
	​

. For a vertex v∈V
ρ
	​

, let S
v
	​

⊆[n] be the set of directions of selected edges incident to v. Then

∣S
v
	​

∣=d
H
	​

(v).

For every unordered coordinate pair {i,j}, say that v is (i,j)-active if

i,j∈S
v
	​

.

Now v and v+e
i
	​

+e
j
	​

 are opposite vertices of the same square. If both were (i,j)-active, then all four edges of that square would be selected, giving a C
4
	​

. Hence inside one parity class, for each fixed {i,j}, at most one endpoint of each pair

{v,v+e
i
	​

+e
j
	​

}

can be active.

The vertices of V
ρ
	​

 are partitioned into

2
n−2

such pairs, so for each {i,j},

∣{v∈V
ρ
	​

:{i,j}⊆S
v
	​

}∣≤2
n−2
.

Summing over all (
2
n
	​

) coordinate pairs,

v∈V
ρ
	​

∑
	​

(
2
d
H
	​

(v)
	​

)≤(
2
n
	​

)2
n−2
.

Now

v∈V
ρ
	​

∑
	​

d
H
	​

(v)=∣E(H)∣,

because every edge has exactly one endpoint in V
ρ
	​

. Let

d=
n2
n−1
∣E(H)∣
	​

.

Then the average degree inside each parity class is

2
n−1
∣E(H)∣
	​

=dn.

By convexity of x↦(
2
x
	​

),

2
n−1
(
2
dn
	​

)≤(
2
n
	​

)2
n−2
.

Canceling 2
n−2
,

2(
2
dn
	​

)≤(
2
n
	​

).

Thus

dn(dn−1)≤
2
n(n−1)
	​

.

Solving for d,

d≤
2n
1+
1+2n(n−1)
	​

	​

=
2
	​

1
	​

+O(
n
1
	​

).

Therefore

f(n)≤(
2
	​

1
	​

+O(
n
1
	​

))n2
n−1
.

SANITY CHECK: This is a genuine improvement over 3/4, but still far above 1/2. No conclusion about the target follows.

Lemma 6: Subcube monotonicity

For k≤n,

d
n
	​

≤d
k
	​

.

Proof: Let H⊆Q
n
	​

 be C
4
	​

-free with density d(H). Choose a random k-dimensional subcube by choosing k coordinates and fixing the remaining n−k coordinates.

Every selected edge of H lies in

(
k−1
n−1
	​

)

different k-subcubes, because its direction must be included and we choose k−1 additional directions.

The total number of k-subcubes is

(
k
n
	​

)2
n−k
.

Thus the expected number of selected edges in the random k-subcube is

∣E(H)∣
(
k
n
	​

)2
n−k
(
k−1
n−1
	​

)
	​

=∣E(H)∣
n2
n−k
k
	​

.

Dividing by the number k2
k−1
 of edges in Q
k
	​

, the expected density is

n2
n−1
∣E(H)∣
	​

=d(H).

Therefore some k-subcube has selected-edge density at least d(H). Since subcubes of a C
4
	​

-free graph are C
4
	​

-free,

d(H)≤d
k
	​

.

Taking H extremal in Q
n
	​

,

d
n
	​

≤d
k
	​

.

In particular, d
n
	​

 is nonincreasing in n, and since d
n
	​

≥1/2, the limit

n→∞
lim
	​

d
n
	​


exists and is at least 1/2.

SANITY CHECK: This is rigorous. It reduces the target to proving that the monotone limit is 1/2, but does not itself identify the limit.

Phase 4: Three parallel branches
Branch A: Direction-shadow method

We have exact sets A
i
	​

⊆Q
n−1
	​

 and exact constraints

P
j
	​

(A
i
	​

)∩P
i
	​

(A
j
	​

)=∅.

Let

B
ij
	​

:=∣P
j
	​

(A
i
	​

)∣.

Then for every unordered pair {i,j},

B
ij
	​

+B
ji
	​

≤2
n−2
.

Summing,

i

=j
∑
	​

B
ij
	​

≤(
2
n
	​

)2
n−2
.

But

j

=i
∑
	​

B
ij
	​

=I(A
i
	​

),

the number of internal edges of A
i
	​

⊆Q
n−1
	​

. Lemma 4 gives

I(A
i
	​

)≥(n−1)(2α
i
	​

−1)2
n−2

for α
i
	​

≥1/2.

Therefore

i
∑
	​

(n−1)(2α
i
	​

−1)
+
	​

2
n−2
≤(
2
n
	​

)2
n−2
.

Canceling,

i
∑
	​

(2α
i
	​

−1)
+
	​

≤
2
n
	​

.

This permits

α
i
	​

=
4
3
	​


for every i. Therefore the shadow method in this raw form cannot prove density 1/2+o(1).

Gap node A

Need a stronger inequality than

I(A
i
	​

)≥(n−1)(2α
i
	​

−1)2
n−2
.

The required strengthening would need to exploit not merely the size of each A
i
	​

, but the mutual consistency among all A
i
	​

’s.

Attack attempts:

Use sharper edge-isoperimetry for A
i
	​

.
Obstacle: a set of density 1/2+ε can have internal-edge density only O(ε), so this cannot force 1/2.

Use triple-coordinate shadows.
Obstacle: C
4
	​

-freeness is a 2-dimensional condition; triple shadows introduce many variables without immediate forbidden intersections.

Use correlation among A
i
	​

,A
j
	​

,A
k
	​

.
Obstacle: pairwise disjointness does not directly imply a strong global packing bound.

Branch A produces useful exact reformulations but no proof of the target.

Branch B: Induction by splitting Q
n
	​


Write Q
n
	​

 as two copies of Q
n−1
	​

, called layer 0 and layer 1, plus the perfect matching between corresponding vertices.

Let

H
0
	​

,H
1
	​

⊆Q
n−1
	​


be the selected edges inside the two layers, and let

S⊆V(Q
n−1
	​

)

be the set of matching edges selected between the two layers.

A square using the new dimension and some old direction corresponds to an edge uv∈Q
n−1
	​

. The four square edges are:

uv in layer 0,

uv in layer 1,

matching edge at u,

matching edge at v.

Therefore, if uv∈H
0
	​

∩H
1
	​

, then u and v cannot both belong to S. Hence

S

is an independent set in the graph

G:=H
0
	​

∩H
1
	​

.

Thus

∣E(H)∣=∣E(H
0
	​

)∣+∣E(H
1
	​

)∣+∣S∣,

with

∣S∣≤α(G),

where α(G) is the independence number of G.

This gives the exact recursive inequality

f(n)≤2f(n−1)+maxα(G),

where G ranges over possible intersections of two C
4
	​

-free subgraphs of Q
n−1
	​

.

The crude bound

∣S∣≤2
n−1

gives only

f(n)≤2f(n−1)+2
n−1
,

which is too weak.

A stronger attempt: if both H
0
	​

 and H
1
	​

 are dense, then their intersection has many edges:

∣E(H
0
	​

∩H
1
	​

)∣≥∣E(H
0
	​

)∣+∣E(H
1
	​

)∣−∣E(Q
n−1
	​

)∣.

If both layers have density >1/2+ε, then G has Ω(εn2
n
) edges.

But a graph can have many edges and still have a large independent set, especially when maximum degree is only n−1. A lower bound on edges does not give a useful upper bound on independence.

Gap node B

Need a theorem of the form:

If G⊆Q
n−1
	​

 arises as the intersection of two dense C
4
	​

-free subgraphs, then

α(G)≤(
2
1
	​

−o(1))2
n−1
.

Attack attempts:

Use ordinary edge density of G.
Fails: edge density alone does not upper-bound independence strongly.

Use G’s inherited C
4
	​

-free structure.
Insufficient: C
4
	​

-free graphs may still have large independent sets.

Use expansion of Q
n−1
	​

.
Needs a statement connecting cube expansion with the special intersection structure. No such statement has been derived.

Branch B gives an exact recurrence but leaves a major unresolved independence bound.

Branch C: Missing-edge transversal method

Let

M=E(Q
n
	​

)∖E(H).

The condition is:

∀ square F,M∩F

=∅.

For each direction i, let M
i
	​

 be the set of missing i-edges, with density

β
i
	​

=
2
n−1
∣M
i
	​

∣
	​

.

Then

n2
n−1
∣M∣
	​

=
n
1
	​

i
∑
	​

β
i
	​

.

The target becomes:

n
1
	​

i
∑
	​

β
i
	​

≥
2
1
	​

−o(1).

For a pair i,j, average over all ij-squares. In every such square, at least one of the four edges is missing. The average number of missing i-edges in such a square is 2β
i
	​

, and similarly for direction j. Hence

2β
i
	​

+2β
j
	​

≥1,

so

β
i
	​

+β
j
	​

≥
2
1
	​

.

Summing over all unordered pairs,

(n−1)
i
∑
	​

β
i
	​

≥(
2
n
	​

)
2
1
	​

,

so

n
1
	​

i
∑
	​

β
i
	​

≥
4
1
	​

.

This recovers only the trivial 3/4 upper bound for H.

Exact-one transversal obstruction search

If a missing-edge set M met every square in exactly one edge, then

∣M∣=
4
1
	​

n2
n−1
,

and its complement would be C
4
	​

-free with density 3/4. Such a structure would strongly disprove the target if it existed in infinitely many dimensions.

Let m
i
	​

(x)∈{0,1} indicate whether the i-edge based at x is missing. Exact-one would require, for every i<j and every fixed base z,

m
i
	​

(z,j=0)+m
i
	​

(z,j=1)+m
j
	​

(z,i=0)+m
j
	​

(z,i=1)=1.

Modulo 2 this becomes

D
j
	​

m
i
	​

+D
i
	​

m
j
	​

=1.

This parity equation alone is not contradictory; it is weaker than exact-one over the integers. The integer condition is much stronger because it forbids the value 3 as well as 0,2,4.

Gap node C

Need prove that square-transversals have density at least 1/2−o(1).

Attack attempts:

Pairwise direction inequalities.
Gives only 1/4.

Exact-one contradiction.
No general contradiction derived.

Stability from near-1/4 transversals.
Would need to show that a near-perfect square transversal cannot persist in large dimension. No proof obtained.

Cohomological parity method.
Mod-2 equations are too weak because hitting a square means “at least one,” not “oddly many.”

Branch C reformulates the problem cleanly but does not close the gap.

Phase 5: Highest-value execution attempt

The strongest verified global statement obtained is Lemma 6:

d
n
	​

≤d
k
	​

(k≤n).

Therefore d
n
	​

 is nonincreasing and bounded below by 1/2, so

L:=
n→∞
lim
	​

d
n
	​


exists and satisfies

2
1
	​

≤L≤
2
	​

1
	​

.

The original theorem is exactly the assertion

L=
2
1
	​

.

Suppose, toward contradiction, that

L>
2
1
	​

.

Then there exists ε>0 such that

d
n
	​

≥
2
1
	​

+ε

for every n.

Equivalently, for every n, there is a C
4
	​

-free H
n
	​

⊆Q
n
	​

 with density at least 1/2+ε.

By subcube monotonicity, this assumption is internally consistent with all finite restrictions: every smaller dimension k must also satisfy

d
k
	​

≥
2
1
	​

+ε.

So contradiction cannot come from a single fixed low-dimensional obstruction unless one proves

d
k
	​

<
2
1
	​

+ε

for some k.

Thus the target is equivalent to:

∀ε>0 ∃kd
k
	​

<
2
1
	​

+ε.

This is a finite-certification formulation.

Attempted contradiction using vertex-pair counting

If d
n
	​

≥1/2+ε, then average degree in each parity class is

dn≥(
2
1
	​

+ε)n.

The number of active direction-pairs in one parity class is at least

2
n−1
(
2
dn
	​

).

The no-C
4
	​

 condition allows at most

(
2
n
	​

)2
n−2
.

This requires

2
n−1
(
2
dn
	​

)≤(
2
n
	​

)2
n−2
.

Asymptotically this says

d
2
≤
2
1
	​

,

so

d≤
2
	​

1
	​

.

But for d=1/2+ε, this is still allowed for every

ε<
2
	​

1
	​

−
2
1
	​

.

Thus this contradiction attempt fails.

Attempted contradiction using missing-edge density

If d
n
	​

≥1/2+ε, then missing density is

1−d
n
	​

≤
2
1
	​

−ε.

A square-transversal of density below 1/2 is therefore required. Pairwise inequalities only force density at least 1/4, so they do not contradict this.

Attempted contradiction using layer induction

If H
n
	​

 has density 1/2+ε, then on average the two (n−1)-layers and the matching together have excess density. The exact obstruction is the independent set S in the layer-intersection graph G=H
0
	​

∩H
1
	​

. To force a contradiction, one needs a uniform upper bound on α(G). No such bound was derived from the available hypotheses.

Formal dependency graph

Verified results:

Lemma 1: C
4
	​

’s are exactly 2-faces.
Dependencies: definition of Q
n
	​

.

Lemma 2: f(n)≤
4
3
	​

n2
n−1
.
Dependencies: Lemma 1, face-edge incidence count.

Lemma 3: Direction-shadow disjointness.
Dependencies: Lemma 1, definition of A
i
	​

, P
j
	​

(A
i
	​

).

Lemma 4: Internal-shadow lower bound.
Dependencies: elementary edge-boundary counting in Q
m
	​

.

Lemma 5: f(n)≤(1/
2
	​

+O(1/n))n2
n−1
.
Dependencies: Lemma 1, parity-class pair counting, Jensen convexity.

Lemma 6: d
n
	​

≤d
k
	​

 for k≤n.
Dependencies: random subcube averaging.

Lower bound: f(n)≥
2
1
	​

n2
n−1
.
Dependencies: explicit parity construction.

Established interval:

2
1
	​

≤
n→∞
lim
	​

d
n
	​

≤
2
	​

1
	​

.

Unresolved target:

n→∞
lim
	​

d
n
	​

=
2
1
	​

.

The unresolved step is not a minor algebraic gap; it requires a new inequality stronger than all local pair-counting and face-counting constraints derived above.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96 / 100

COMPLETENESS_SCORE: 45 / 100

ADVERSARIAL_SURVIVAL_SCORE: 88 / 100

RESOURCE_USAGE:

Reasoning budget used: approximately 100%.

Branches explored: 3 primary branches, 12 initial strategies.

Lemmas generated: 6 verified lemmas plus one explicit lower-bound construction.

Failed proof attempts: direction-shadow strengthening, layer-induction closure, missing-edge transversal closure, vertex-pair contradiction.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

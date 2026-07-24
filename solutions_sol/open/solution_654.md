# Erdős Problem #654 [unsolved] 38%

---

## ChatGPT Response

I treat the geometric construction asserted in the supplied statement as part of the problem’s assumptions, but I do not use any external references or literature information. 

Pasted text

Phase 0: Formalization
1. Objects and extremal function

Assume throughout that the x
i
	​

 are distinct.

For a finite set S⊂R
2
 and x∈S, define

D
S
	​

(x)={∥x−y∥:y∈S∖{x}},d
S
	​

(x)=∣D
S
	​

(x)∣.

Let A
n
	​

 be the family of all n-point sets S⊂R
2
 such that no circle contains four points of S. Then

F(S)=
x∈S
max
	​

d
S
	​

(x),f(n)=
S∈A
n
	​

min
	​

F(S).

The minimum exists because F(S) is an integer between 1 and n−1, and A
n
	​


=∅.

2. Quantifier structures

The strong proposed lower bound means

∀ε>0∃N∀n≥N:f(n)>(1−ε)n.
(A)

Its negation is

∃ε>0∀N∃n≥N:f(n)≤(1−ε)n.
(¬A)

The weaker proposed lower bound means

∃c>0∃N∀n≥N:f(n)>(
3
1
	​

+c)n.
(B)

Its negation is

∀c>0∀N∃n≥N:f(n)≤(
3
1
	​

+c)n.
(¬B)

The construction asserted in the problem statement gives admissible examples satisfying

F(S)≤
4
3
	​

n.

Consequently, for the values of n supplied by that construction,

f(n)≤
4
3
	​

n,

which directly contradicts (A). Thus the (1−o(1))n proposal is disproved by an assumption already contained in the problem statement.

The remaining target is (B).

3. Distance multiplicities

For x∈S, every distance class

C
r
	​

(x)={y∈S∖{x}:∥x−y∥=r}

has size at most 3. Indeed, four members of C
r
	​

(x) would be four points of S on the circle of radius r centered at x.

Let a
k
	​

(x) denote the number of distance classes from x having exactly k points, for k=1,2,3. Then

a
1
	​

(x)+2a
2
	​

(x)+3a
3
	​

(x)=n−1,
(1)

and

d
S
	​

(x)=a
1
	​

(x)+a
2
	​

(x)+a
3
	​

(x).
(2)

Eliminating a
3
	​

(x),

d
S
	​

(x)=
3
n−1
	​

+
3
2a
1
	​

(x)+a
2
	​

(x)
	​

.
	​

(3)

This gives the trivial bound

f(n)≥⌈
3
n−1
	​

⌉.
	​

(4)

It also identifies the exact obstruction.

To prove (B), it is enough to prove that there is a constant c>0 such that every sufficiently large admissible S contains x satisfying

2a
1
	​

(x)+a
2
	​

(x)>3cn+1.
(5)

Thus one must force a linear weighted number of singleton and doubleton distance classes at one point.

4. Global counting formulation

Set

A
k
	​

=
x∈S
∑
	​

a
k
	​

(x),T=A
3
	​

.

Summing (1) and (2),

A
1
	​

+2A
2
	​

+3T=n(n−1),
(6)

and

x∈S
∑
	​

d
S
	​

(x)=A
1
	​

+A
2
	​

+T.
(7)

Therefore

3
x∈S
∑
	​

d
S
	​

(x)−n(n−1)=2A
1
	​

+A
2
	​

.
(8)

In particular,

F(S)≥
3
n−1
	​

+
3n
2A
1
	​

+A
2
	​

	​

.
(9)

Since

2A
1
	​

+A
2
	​

≥
2
1
	​

(A
1
	​

+2A
2
	​

)=
2
1
	​

(n(n−1)−3T),

we obtain the useful conditional estimate

F(S)≥
3
n−1
	​

+
6n
n(n−1)−3T
	​

.
	​

(10)

Consequently, a bound of the form

T≤(
3
1
	​

−δ)n
2
(11)

for some fixed δ>0 would imply

F(S)≥(
3
1
	​

+
2
δ
	​

−o(1))n.
(12)

So a central equivalent sufficient target is:

Show that a positive proportion of the theoretically possible centered three-point distance classes must be absent.

5. Equivalent radius-graph formulation

For every occurring distance r>0, define

G
r
	​

=(S,E
r
	​

),xy∈E
r
	​

⟺∥x−y∥=r.

The no-four-on-a-circle condition implies

Δ(G
r
	​

)≤3.
(13)

Moreover:

a
1
	​

(x) counts the radii r with deg
G
r
	​

	​

(x)=1;

a
2
	​

(x) counts the radii r with deg
G
r
	​

	​

(x)=2;

a
3
	​

(x) counts the radii r with deg
G
r
	​

	​

(x)=3.

Hence

T=
r
∑
	​

∣{x∈S:deg
G
r
	​

	​

(x)=3}∣.
(14)

A counterexample to (B) would therefore have the following structure: at every vertex, almost all incident edges of K
n
	​

 would belong to radius graphs in which that vertex has degree exactly 3.

6. Negation in structural form

Suppose (B) is false. Then for every η>0, there are arbitrarily large admissible sets S such that

2a
1
	​

(x)+a
2
	​

(x)≤ηnfor every x∈S.
(15)

Since

a
1
	​

(x)+2a
2
	​

(x)≤2(2a
1
	​

(x)+a
2
	​

(x)),

only O(ηn) of the n−1 other points can belong to non-triple classes at x. Thus almost every ordered pair (x,y) would have the property that y belongs to a three-point distance class centered at x.

This is the precise configuration that must either be constructed or contradicted.

7. Boundary cases and symmetries

The problem is invariant under:

relabeling;

translations;

rotations and reflections;

uniform scaling.

Small values include

f(1)=0,f(2)=1,f(3)=1.

Also,

f(4)=2.

For the upper bound, take the center of an equilateral triangle together with its three vertices. The center has one distance, while each triangle vertex has two.

For the lower bound, if every point of a four-point set had only one distance to the other three, all six pairwise distances would be equal, which is impossible for four points in R
2
.

Phase 1: Breadth-first strategy search
Rank	Strategy	Core idea	Hidden assumption or obstacle	Assessment
1	Radius-graph decomposition	Study the graphs G
r
	​

 of each distance and force many degree-1 or degree-2 occurrences	Cubic unit-distance components are locally possible	Highest expected value
2	Centered-triple counting	Bound T=∑a
3
	​

(x) below 
3
1
	​

n
2
 by a fixed proportion	Elementary uniqueness gives only weak bounds	High expected value
3	Perpendicular-bisector structure	Count isosceles configurations and classify repeated bisectors	Pair classes may concentrate along two lines	High structural value
4	Contradiction from near equality	Assume every vertex is almost partitioned into triples and derive rigid global structure	Requires a global compatibility theorem	Moderate
5	Direct multiplicity counting	Use class sizes at most 3	Gives exactly the known 1/3 coefficient	Verified but exhausted
6	Geometric construction	Attempt configurations with nearly all classes of size 3	Equalities are highly coupled and unstable under perturbation	Moderate for disproof search
7	Density/incidence bounds	Count incidences of points with perpendicular bisectors or centered circles	Collinear concentrations defeat naive incidence estimates	Moderate-low
8	Induction by deleting points	Remove an extremal point and apply a bound to the remaining set	Reinserted points can occupy existing classes, so gains do not add	Low
9	Compactness	Pass to limiting configurations with extremal multiplicity patterns	Coincidences and distance equalities are not uniformly separated	Low
10	Diagonalization	Compare the triple partitions centered at different vertices	Pairwise compatibility does not immediately create a forbidden circle	Low
11	Cardinal arithmetic	Use divisibility and parity of cubic radius graphs	At most gives residue-class or additive information	Low
12	Transfinite induction	Well-order configurations or equality patterns	The problem is finite and supplies no monotone ordinal invariant	Negligible

The top three strategies are developed below.

Phase 2: Auxiliary structures
Definition 1: Weighted defect

Define

e(x)=2a
1
	​

(x)+a
2
	​

(x).

Then

d
S
	​

(x)=
3
n−1+e(x)
	​

.
(16)

The desired improvement is exactly a linear lower bound on max
x
	​

e(x).

Definition 2: Saturated ordered pair

An ordered pair (x,y), x

=y, is saturated when the distance class from x containing y has size 3.

The number of saturated ordered pairs originating at x is 3a
3
	​

(x).

The number of nonsaturated ordered pairs originating at x is

u(x)=a
1
	​

(x)+2a
2
	​

(x).
(17)

The two defects satisfy

2
1
	​

u(x)≤e(x)≤2u(x).
(18)

Thus proving that some vertex has linearly many nonsaturated outgoing pairs would settle the weaker conjecture.

Definition 3: Centered triple

A centered triple is a pair

(x;{a,b,c})

such that

∥x−a∥=∥x−b∥=∥x−c∥.

Each size-3 distance class gives one centered triple.

Definition 4: Bisector multiplicity

For a line ℓ, let

w(ℓ)=∣{{a,b}⊂S:ℓ is the perpendicular bisector of ab}∣.

Isosceles triangles with apex in S∩ℓ and bases counted by w(ℓ) contribute

∣S∩ℓ∣w(ℓ)

apex-base incidences.

Phase 3A: Centered-triple branch
Lemma 1: A triple has at most one prescribed center

For three noncollinear points a,b,c, there is at most one point x satisfying

∥x−a∥=∥x−b∥=∥x−c∥.
Proof

Such an x belongs to the perpendicular bisectors of both ab and ac. These two nonparallel lines meet in exactly one point.

The outer points of a centered triple are automatically noncollinear, since a line meets a circle in at most two points. ∎

This gives

T≤(
3
n
	​

),

but that is far weaker than the local bound

T≤
3
n(n−1)
	​

.

So uniqueness alone does not produce a positive proportional saving.

Lemma 2: A four-point set has at most two centered vertices

Let Q={a,b,c,d}⊂R
2
. At most two vertices of Q can be equidistant from the other three.

Proof

Suppose a,b,c all have this property.

From a,

ab=ac=ad.

From b,

ba=bc=bd.

Because ab=ba, the five distances

ab,ac,ad,bc,bd

are equal. From the condition at c,

cd=ca,

so all six distances are equal.

But three mutually equidistant points form an equilateral triangle. There are exactly two points in the plane at the same prescribed distance from two fixed vertices, and those two points are at distance 
3
	​

 times the prescribed distance from each other. Hence four mutually equidistant points cannot lie in R
2
. ∎

This local incompatibility is genuine, but summing it over four-subsets gives only

T≤2(
4
n
	​

),

which is again much weaker than O(n
2
).

Branch status

To obtain a positive c, one needs a new inequality of the form

T≤(
3
1
	​

−δ)n
2
.

Neither uniqueness of circumcenters nor four-point incompatibility approaches the required scale.

Phase 3B: Radius-graph branch

For each distance r, the graph G
r
	​

 has maximum degree 3. A triple class is exactly a degree-3 occurrence.

If every point achieved the trivial lower bound exactly, then every nonzero degree in every G
r
	​

 would have to equal 3. Thus every G
r
	​

 would be a disjoint union of cubic components and isolated vertices.

More generally, a hypothetical asymptotic counterexample to (B) would decompose almost all edges of K
n
	​

 into radius graphs which are almost cubic at almost every incident vertex.

This suggests the target:

Prove that in any planar Euclidean realization satisfying the circle condition, the total number of degree-1 and degree-2 vertex-radius incidences is Ω(n
2
).

Such a theorem would immediately settle (B), by (8)–(10).

However, maximum degree 3 alone is insufficient. Cubic graphs are combinatorially possible, and cubic unit-distance configurations can occur locally. For example, take two congruent equilateral triangles, one obtained from the other by a generic translation vector whose length equals the triangle side length. Each vertex then has its two triangle neighbors and its translated counterpart at the same distance. For generic translation direction, accidental additional equalities and concyclic quadruples are avoided.

Thus the required theorem must use interactions between different radius graphs, not only the geometry of a single G
r
	​

.

Shared-edge compatibility

If xy∈E
r
	​

 and both endpoints have degree 3 in G
r
	​

, then xy belongs simultaneously to:

a three-point radius class centered at x;

a three-point radius class centered at y.

Consequently, in a near-extremal configuration, almost every edge would connect two degree-3 vertices in its radius graph.

No contradiction was derived from this condition. The two triples containing a shared edge may use four unrelated additional vertices, so local saturation need not close into a forbidden four-point configuration.

Branch status

The branch isolates a strong structural statement, but no valid argument forces a positive density of noncubic incidences.

Phase 3C: Perpendicular-bisector branch

Equal distances

∥x−a∥=∥x−b∥

mean that x lies on the perpendicular bisector of ab. Thus pair classes can be studied through point-line incidences.

The following rigidity property follows from the no-four-on-a-circle condition.

Lemma 3: Repeated perpendicular bisectors are collinear and concentric

Suppose two distinct unordered pairs {a,b} and {c,d} have the same perpendicular bisector ℓ. Then either the four points are concyclic, or the two segments have the same midpoint and all four points are collinear on the line perpendicular to ℓ.

Therefore, under the hypothesis of the problem, the latter alternative must hold.

Proof

The pairs are disjoint: reflection in ℓ maps one endpoint of a pair to the other, so two distinct pairs sharing an endpoint cannot have the same perpendicular bisector.

Choose coordinates in which ℓ is the y-axis. Write

a=(u,p),b=(−u,p),

and

c=(v,q),d=(−v,q),

where u,v>0.

If p

=q, choose z∈R satisfying

u
2
+(p−z)
2
=v
2
+(q−z)
2
.

This is a linear equation in z, so it has a solution. The circle centered at (0,z) through a then also passes through b,c,d. Hence the four points are concyclic.

Thus the no-four-on-a-circle condition forces p=q. All four points then lie on the horizontal line y=p, and both pairs have midpoint (0,p). ∎

Consequence

High bisector multiplicity can occur only in a cross-type configuration:

many symmetric pairs lie on one line and have a common midpoint;

their common perpendicular bisector is another line;

many possible isosceles apices may lie on that perpendicular line.

This demonstrates why a naive incidence bound cannot settle the question. A single line can contain many points and simultaneously be the perpendicular bisector of many pairs without producing four concyclic points, provided all those pairs are collinear with a common midpoint.

Such configurations naturally create many distance classes of multiplicity 2. They therefore explain why two-line constructions can substantially lower the number of distinct distances, but they do not produce multiplicity 3, which is required to approach the 1/3 coefficient.

Branch status

The bisector lemma sharply classifies the main degeneracy for doubleton classes. It does not bound the number of centered triple classes, so it cannot by itself establish a fixed c>0.

Phase 4: Adversarial verification
Failed claim 1: Diameter endpoints improve the bound

A tempting claim is that a diameter endpoint cannot have three farthest neighbors. This is false.

Take a point x and three points on a short arc of a circle centered at x. All three are at the same distance D from x, while their pairwise distances can all be strictly less than D. Hence D remains the diameter of the four-point set.

The three outer points lie on one circle, but x, being its center, does not lie on that circle. Thus there need not be a forbidden concyclic quadruple.

Therefore no improvement from

⌈
3
n−1
	​

⌉

to ⌈n/3⌉ follows from diameter considerations.

Failed claim 2: A centered triple creates a longer chord

It is also false that three points on a circle of radius r must contain a pair at distance at least 
3
	​

r. They may all lie on an arbitrarily short arc, making all three mutual distances arbitrarily small compared with r.

Thus an attempted increasing-length orientation of centered triples is invalid.

Failed claim 3: Circumcenter uniqueness gives a useful global bound

Although each outer triple has at most one center, the resulting estimate

T≤(
3
n
	​

)

is cubic, while the relevant extremal scale is n
2
. It supplies no proportional saving over n(n−1)/3.

Failed claim 4: Generic perturbation preserves constructions

Generic perturbation removes unwanted concyclic quadruples, but it also destroys desired equal-distance relations. Therefore one cannot begin with a highly symmetric few-distance set and perturb it while assuming its distance multiplicities remain intact.

Failed claim 5: Induction accumulates local gains

Applying a bound to S∖{x} and adding x back does not necessarily add a new distance at the inductively selected point. The new point can occupy an existing distance class. Consequently, the obvious induction has no monotone gain.

Verified theorem pool
Theorem 1: Multiplicity bound

Every distance class centered at a point of S has size at most 3.

Dependency: no four points on a circle.

Theorem 2: Exact defect identity

For every x∈S,

d
S
	​

(x)=
3
n−1
	​

+
3
2a
1
	​

(x)+a
2
	​

(x)
	​

.

Dependency: Theorem 1 and the partition of S∖{x} into distance classes.

Corollary 3: Universal lower bound
f(n)≥⌈
3
n−1
	​

⌉.
Theorem 4: Global triple-count criterion

If every admissible n-point set satisfies

x
∑
	​

a
3
	​

(x)≤(
3
1
	​

−δ)n
2
,

then

f(n)≥(
3
1
	​

+
2
δ
	​

−o(1))n.

Dependency: Equations (6)–(10).

Theorem 5: Repeated-bisector classification

Two distinct pairs with the same perpendicular bisector either produce four concyclic points or are collinear symmetric pairs with the same midpoint.

Theorem 6: At most two centered vertices in a four-set

A four-point subset of the plane has at most two vertices equidistant from the other three.

Theorem 7: Strong asymptotic proposal fails under the supplied construction premise

The asserted examples with

F(S)≤
4
3
	​

n

imply that

f(n)>(1−o(1))n

is false.

Exact unresolved gap

The surviving target is

∃δ>0∀S∈A
n
	​

 sufficiently large:
x∈S
∑
	​

a
3
	​

(x)≤(
3
1
	​

−δ)n
2
,

or some weaker statement that directly forces

x
max
	​

(2a
1
	​

(x)+a
2
	​

(x))=Ω(n).

The explored local geometric restrictions do not imply this. Specifically:

centered triples are unique when their outer triple is fixed, but there are Θ(n
3
) possible outer triples;

a four-set has at most two centers, but there are Θ(n
4
) four-sets;

individual radius graphs may be cubic;

perpendicular-bisector rigidity controls pair classes rather than triple classes;

clustering on short arcs defeats diameter and length-monotonicity arguments.

Therefore no positive constant c has been established, and no construction approaching the 1/3 coefficient has been produced.

Final bounds obtained

Based only on the definitions and the construction assertion supplied in the problem statement,

⌈
3
n−1
	​

⌉≤f(n)≤
4
3
	​

n
	​


for the sizes covered by the asserted upper construction.

The proposed bound

f(n)>(1−o(1))n

is disproved.

The existence of a fixed c>0 such that

f(n)>(
3
1
	​

+c)n

for all sufficiently large n was neither proved nor disproved.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 98/100 for the verified lemmas and conclusions.

COMPLETENESS_SCORE: 38/100. The strong proposal is settled from the supplied premise, and the weaker problem is reduced to precise structural targets, but no positive c is obtained.

ADVERSARIAL_SURVIVAL_SCORE: 95/100. Two initially promising geometric claims were explicitly destroyed by short-arc counterexamples and removed from the theorem pool.

RESOURCE_USAGE: Approximately 100% of the allocated proof search; 12 strategies considered, 3 main branches developed, 7 verified results recorded, and 5 failed proof mechanisms isolated.

I have not used WiFi, internet search, web search, external databases, or literature-status information. All mathematical reasoning was derived from the user-supplied problem statement, explicit definitions, and deductions performed within this session.

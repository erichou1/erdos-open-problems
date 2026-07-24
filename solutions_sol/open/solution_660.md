# Erdős Problem #660 [unsolved] 22%

---

## ChatGPT Response

0. Formalization

Let X={x
1
	​

,…,x
n
	​

}⊂R
3
 be precisely the set of vertices of the three-dimensional polytope convX. Define

Δ(X)={∥x
i
	​

−x
j
	​

∥:1≤i<j≤n},D(X)=∣Δ(X)∣.

The requested assertion is

∀ε>0 ∃N
ε
	​

 ∀n≥N
ε
	​

 ∀X,D(X)≥(1−ε)
2
n
	​

.

Its negation is:

∃ε
0
	​

>0and arbitrarily large nfor which there is XwithD(X)≤(1−ε
0
	​

)
2
n
	​

.

Equivalently, one asks whether

n→∞
liminf
	​

X⊂R
3
∣X∣=n, X in convex position
	​

min
	​

n
D(X)
	​

≥
2
1
	​

.

The task and its restrictions are those in the uploaded statement. 

Pasted text

The quantity D(X) is invariant under Euclidean similarities, but not under arbitrary affine transformations.

Every subset of X remains in convex position: if x∈X, then x∈
/
conv(X∖{x}), so the same remains true after deleting other points. Also, no three points of X are collinear, since the middle point of three collinear points would not be extreme.

1. Sharpness of the proposed constant

Let y
1
	​

,…,y
m
	​

 be the vertices of a regular m-gon in the plane z=0, with circumradius 1, and let

a=(0,0,h),h>0.

The set

X
m
	​

={y
1
	​

,…,y
m
	​

,a}

is the vertex set of a convex pyramid.

The distances between base vertices are

2sin
m
πk
	​

,1≤k≤⌊
2
m
	​

⌋,

and are mutually distinct. All apex-to-base distances equal

1+h
2
	​

.

Choosing h so this value is not one of the finitely many base distances gives

D(X
m
	​

)=⌊
2
m
	​

⌋+1.

Since n=m+1,

D(X
m
	​

)=
2
n
	​

+O(1).

Thus the coefficient 1/2, if valid, cannot be replaced by any larger asymptotic coefficient.

2. A verified unconditional bound

Choose three noncollinear vertices a,b,c on one face of the polyhedron. Let

P=aff{a,b,c}.

All vertices lie in one closed half-space bounded by P.

Define, for x∈X∖{a,b,c},

Φ(x)=(∥x−a∥,∥x−b∥,∥x−c∥).
Lemma 1

The map Φ is injective.

Proof

Suppose Φ(x)=Φ(y). Subtracting the squared-distance equations gives

(x−y)⋅(b−a)=0,(x−y)⋅(c−a)=0.

Hence x−y is perpendicular to P. The three equal distances determine the same orthogonal projection onto P and equal absolute distances from P. Thus x and y are either equal or mirror images across P.

Both lie in the same closed half-space bounded by P, so the mirror-image alternative is impossible unless both lie on P, in which case they are again equal. Therefore x=y. □

Each coordinate of Φ(x) belongs to Δ(X), so there are at most D(X)
3
 possible triples. Consequently,

n−3≤D(X)
3
,

and hence

D(X)≥(n−3)
1/3
	​

.

This does not approach the proposed linear bound, but it is a fully verified consequence of convexity.

3. Local multiplicity formulation

For v∈X, let

d(v)=∣{∥v−x∥:x∈X∖{v}}∣.

Plainly,

d(v)≤D(X).

For every distance r occurring from v, define

A
v,r
	​

={x∈X∖{v}:∥x−v∥=r},a
v,r
	​

=∣A
v,r
	​

∣.

Thus

r
∑
	​

a
v,r
	​

=n−1.

Define the multiplicity beyond two by

E(v)=
r
∑
	​

(a
v,r
	​

−2)
+
	​

.

Since

n−1−E(v)=
r
∑
	​

min(a
v,r
	​

,2)≤2d(v),

we have

d(v)≥
2
n−1−E(v)
	​

.

Therefore the desired conclusion would follow from the geometric assertion

v∈X
min
	​

E(v)=o(n).

More importantly, a fixed-factor counterexample would force the reverse behavior at every vertex. If

D(X)≤(1−ε)
2
n
	​

,

then for every v∈X,

E(v)≥n−1−2d(v)≥n−1−2D(X)≥εn−1.

Thus:

Every fixed-factor counterexample must have E(v)≥εn−O(1) for every vertex v.
	​


In particular, every vertex would be the center of linearly many repeated-radius configurations.

For a group of a≥3 equidistant neighbors, one can choose at least

⌊
3
a
	​

⌋≥
3
a−2
	​


pairwise disjoint triples. Hence every vertex in such a counterexample would be the center of at least

3
εn−O(1)
	​


neighbor-disjoint equidistant triples.

4. Why counting equidistant triples is insufficient

For three distinct vertices b,c,d, the locus

{z:∥z−b∥=∥z−c∥=∥z−d∥}

is a line: it is the intersection of the perpendicular-bisector planes of bc and bd. The points b,c,d are noncollinear, so these planes are distinct.

Because X has no three collinear vertices, at most two vertices of X can be equidistant from b,c,d.

Therefore, if

Q=
v∈X
∑
	​

r
∑
	​

(
3
a
v,r
	​

	​

),

then

Q≤2(
3
n
	​

).

On the other hand,

(
3
a
	​

)≥a−2(a≥3),

so a hypothetical fixed-factor counterexample gives only

Q≥
v
∑
	​

E(v)≥εn
2
−O(n).

The resulting inequalities are compatible:

εn
2
−O(n)≤Q≤
3
n
3
	​

+O(n
2
).

Thus this counting approach misses the required contradiction by a factor of order n.

5. Equal-distance graphs

For each r∈Δ(X), define the graph

G
r
	​

=(X,{{x,y}:∥x−y∥=r}).

Write

e
r
	​

=∣E(G
r
	​

)∣,v
r
	​

=∣{x:deg
G
r
	​

	​

(x)>0}∣.

Then

r
∑
	​

e
r
	​

=(
2
n
	​

)

and

x∈X
∑
	​

d(x)=
r
∑
	​

v
r
	​

.

Consequently, if one could prove

r
∑
	​

v
r
	​

≥(
2
1
	​

−o(1))n
2
,

then some vertex would satisfy

d(x)≥(
2
1
	​

−o(1))n,

and the desired conclusion would follow.

Equivalently,

r
∑
	​

v
r
	​

=(
2
n
	​

)−
r
∑
	​

(e
r
	​

−v
r
	​

).

Thus the sufficient structural estimate is

r
∑
	​

(e
r
	​

−v
r
	​

)=o(n
2
).
	​


Conversely, if

D(X)≤(1−ε)
2
n
	​

,

then

r
∑
	​

v
r
	​

≤nD(X)≤(1−ε)
2
n
2
	​

,

so

r
∑
	​

(e
r
	​

−v
r
	​

)≥(
2
n
	​

)−(1−ε)
2
n
2
	​

=
2
εn
2
	​

−O(n).

Let c
r
	​

 be the number of nontrivial connected components of G
r
	​

, and let

β
r
	​

=e
r
	​

−v
r
	​

+c
r
	​


be its cycle-space dimension. Since c
r
	​

≥0,

r
∑
	​

β
r
	​

≥
r
∑
	​

(e
r
	​

−v
r
	​

).

Hence every fixed-factor counterexample must satisfy

r
∑
	​

β
r
	​

=Ω
ε
	​

(n
2
).
	​


In words: its equal-distance graphs must collectively contain quadratically many independent cycles.

This is a strong necessary condition. The pyramid, bipyramid, regular polygon, and ordinary prism constructions have only O(n) total cycle excess.

6. A classwise bound cannot prove the result

A tempting claim is that every fixed-distance graph should satisfy

e
r
	​

≤n+o(n).

This is false.

Take a regular m-gonal prism with vertices

T
i
	​

=(cos
m
2πi
	​

,sin
m
2πi
	​

,
2
h
	​

),
B
i
	​

=(cos
m
2πi
	​

,sin
m
2πi
	​

,−
2
h
	​

),i∈Z/mZ.

Let

c
k
	​

=2sin
m
πk
	​


be the chord length of angular offset k, and choose

h
2
=c
2
2
	​

−c
1
2
	​

>0.

Set L=c
2
	​

. For m≥7:

T
i
	​

T
i±2
	​

 and B
i
	​

B
i±2
	​

 have length L, giving 2m edges.

T
i
	​

B
i±1
	​

 also have length L, since

∥T
i
	​

−B
i±1
	​

∥
2
=h
2
+c
1
2
	​

=c
2
2
	​

,

giving another 2m edges.

Thus, with n=2m,

e
L
	​

=4m=2n.

So even an arbitrarily large convex polyhedron can have a distance occurring 2n times. Any successful argument must control the aggregate excess over all distance classes, not each class separately.

7. Distance-energy formulation

Let

M
r
	​

=e
r
	​


be the number of unordered pairs at distance r, and define the distance energy

E(X)=
r
∑
	​

M
r
2
	​

.

Since

r
∑
	​

M
r
	​

=(
2
n
	​

),

Cauchy–Schwarz gives

(
2
n
	​

)
2
≤D(X)E(X).

Therefore,

D(X)≥
E(X)
(
2
n
	​

)
2
	​

.

The desired result would follow from

E(X)≤(
2
1
	​

+o(1))n
3
.
	​


Indeed, that estimate gives

D(X)≥
(1/2+o(1))n
3
(1+o(1))n
4
/4
	​

=(
2
1
	​

−o(1))n.

Conversely, a counterexample with

D(X)≤(1−ε)
2
n
	​


would force

E(X)≥
D(X)
(
2
n
	​

)
2
	​

≥(
2(1−ε)
1
	​

−o(1))n
3
.

The regular-pyramid construction has

E(X)=(
2
1
	​

+o(1))n
3
,

so the coefficient in this proposed energy inequality would be sharp.

No derivation of that energy bound was obtained.

8. Isosceles-count formulation

For v∈X, let

I(v)=
r
∑
	​

a
v,r
	​

(a
v,r
	​

−1),

the number of ordered pairs (x,y) of distinct vertices satisfying

∥v−x∥=∥v−y∥.

Because

r
∑
	​

a
v,r
2
	​

=n−1+I(v),

Cauchy–Schwarz gives

(n−1)
2
=(
r
∑
	​

a
v,r
	​

)
2
≤d(v)
r
∑
	​

a
v,r
2
	​

=d(v)(n−1+I(v)).

Hence

d(v)≥
n−1+I(v)
(n−1)
2
	​

.

Thus the proposed result would follow from

v∈X
min
	​

I(v)≤(1+o(1))n.
	​


A fixed-factor counterexample would violate this at every vertex. Indeed,

I(v)≥
d(v)
(n−1)
2
	​

−(n−1)≥
D(X)
(n−1)
2
	​

−(n−1).

If D(X)≤(1−ε)n/2, then

I(v)≥(
1−ε
1+ε
	​

)n−O
ε
	​

(1)

for every v.

This gives another sharply formulated geometric target:

Show that every sufficiently large three-dimensional convex-position set has a vertex that is the apex of at most (1+o(1))n ordered isosceles triangles.

The triple-center counting argument above is too weak to establish this.

9. Search branches and their verified outcomes
Strategy	Outcome
One center, at most two vertices per radius	False: a pyramid apex can be equidistant from all base vertices.
Every fixed-distance graph has at most n+o(n) edges	False: the thin-prism construction gives 2n.
Bound all isosceles triangles by averaging	Insufficient: bipyramidal examples concentrate quadratically many at a few vertices.
Find a vertex with E(v)=o(n)	Sufficient and natural, but not established.
Bound total cycle excess of equal-distance graphs	Sufficient; a counterexample requires Ω(n
2
) cycle rank. No upper bound proved.
Distance-energy estimate	A sharp sufficient condition, but no proof obtained.
Induction by deleting distance-redundant vertices	Produces a distance-realizing core of at most 2D vertices, but does not bound the number of additional convex vertices.
Projection to a plane	No argument ensures that a projection retains n−o(n) projected hull vertices.
Diameter peeling	Repeated diameters can occur on linearly many disjoint pairs, so strict descent fails.
Polynomial interpolation in squared distances	Gives polynomial, rather than linear, bounds; the face-coordinate argument yields D≥(n−3)
1/3
.
Compactness	A limiting measure loses exact equality information, since the number of distance values grows with n.
Symmetry and reflection	Explains the pyramid/prism extremizers heuristically, but few distances were not shown to force sufficient global symmetry.
Transfinite induction	Inapplicable: all objects and parameters are finite.
Diagonalization/cardinal arithmetic	Supplies no additional constraint beyond the finite counts above.
Counterexample construction using several rotational layers	Generic inter-layer distances create additional linear families of values; no construction below the n/2 scale was found.
10. Dependency graph of verified results
Convexity⟹
⎩
⎨
⎧
	​

subsets remain in convex position,
no three vertices are collinear,
all vertices lie on one side of a face plane.
	​


From the face-plane property:

n−3≤D
3
.

From local multiplicities:

D≤(1−ε)
2
n
	​

⟹E(v)≥εn−O(1)∀v.

From equal-distance graphs:

D≤(1−ε)
2
n
	​

⟹
r
∑
	​

β
r
	​

=Ω
ε
	​

(n
2
).

From Cauchy–Schwarz:

E(X)≤(
2
1
	​

+o(1))n
3
⟹D(X)≥(
2
1
	​

−o(1))n.

Also:

v
min
	​

I(v)≤(1+o(1))n⟹D(X)≥(
2
1
	​

−o(1))n.

None of the two sufficient geometric estimates was proved, and no construction violating the requested asymptotic inequality was obtained.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the explicitly proved lemmas and counterexamples to intermediate claims.

COMPLETENESS_SCORE: 22/100. The original asymptotic assertion is neither proved nor disproved.

ADVERSARIAL_SURVIVAL_SCORE: 91/100 for the retained partial results; several initially plausible stronger lemmas were destroyed by explicit pyramid and prism configurations.

RESOURCE_USAGE: 15 principal branches explored; 8 verified lemmas or reformulations retained; 9 proof routes rejected or shown insufficient.

No Wi-Fi, internet search, external database, or literature-status information was used. The only retrieved material was the user-supplied problem statement itself; all mathematical deductions above were made from that statement and elementary arguments.

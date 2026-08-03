1. Logical defect in the immutable statement

Let

Δ(X,Y):={∥x−y∥:x∈X, y∈Y},D(X,Y):=∣Δ(X,Y)∣.

There are two unresolved interpretation issues.

Repetitions

The statement does not explicitly require the indexed points to be distinct.

If repetitions are allowed, take

x
1
	​

=⋯=x
n
	​

=(0,0),y
1
	​

=⋯=y
n
	​

=(1,0).

Then D(X,Y)=1, and

1=o(
logn
	​

n
	​

).

Thus the literal tuple interpretation is immediately affirmative.

The later phrase “any 2n points” strongly suggests the intended version is instead:

∣X∣=∣Y∣=n,X∩Y=∅.
(D)

There is also an intermediate interpretation where X and Y are individually sets but may overlap. These variants are not formally equivalent.

Asymptotic quantifiers

The precise intended assertion should be

∀ε>0 ∃N ∀n≥N ∃X
n
	​

,Y
n
	​

D(X
n
	​

,Y
n
	​

)≤ε
logn
	​

n
	​

.
(1)

Equivalently, defining

F
2
	​

(n):=
∣X∣=∣Y∣=n
X∩Y=∅
	​

min
	​

D(X,Y),

the question is whether

F
2
	​

(n)=o(
logn
	​

n
	​

).
(2)

Because distinctness is not stated, the immutable wording has no unique nontrivial interpretation. Everything below concerns the strongest version (D).

2. Verified dimensional boundary cases
One dimension

For A,B⊂R, ∣A∣=∣B∣=n, the difference set satisfies

∣A−B∣≥2n−1.

Indeed, after ordering the sets, one obtains a strictly increasing chain of 2n−1 differences using one extreme point from each set.

Passing from signed differences to absolute differences identifies at most z and −z. Hence

D(A,B)≥n.

Equality is attained with

A={0,2,…,2n−2},B={1,3,…,2n−1},

whose cross-distances are 1,3,…,2n−1. Therefore

F
1
	​

(n)=n.
Three dimensions

The R
3
 side question has an elementary affirmative construction, even with all 2n points distinct.

Let

m=⌈(2n)
1/3
⌉

and choose any 2n distinct points from

{0,1,…,m−1}
3
.

Partition them into X and Y, each of size n.

Every squared cross-distance is an integer between 1 and

3(m−1)
2
.

Consequently,

D(X,Y)≤3(m−1)
2
=O(n
2/3
).

But

n/
logn
	​

n
2/3
	​

=
n
1/3
logn
	​

	​

⟶0.

Thus the three-dimensional analogue satisfies the desired little-o estimate.

More generally, the integer-grid construction in R
d
 gives

F
d
	​

(n)=O(n
2/d
),

so every d≥3 satisfies the displayed target. Dimension 2 is the critical case.

3. The standard planar benchmark

Let

R
2
	​

(T):=
	​

{k≤T:k=a
2
+b
2
 for some a,b∈Z}
	​

.

The exact auxiliary counting theorem is:

There is an absolute C such that, for every T≥3,

R
2
	​

(T)≤C
logT
	​

T
	​

.
(3)

Take M=⌈
2n
	​

⌉, choose 2n distinct points from an M×M integer grid, and split them into X,Y. Then

D(X,Y)≤R
2
	​

(2(M−1)
2
)=O(
logn
	​

n
	​

).
(4)

Therefore the problem asks for a genuine vanishing-factor improvement over the planar lattice scale, not merely a constant-factor improvement.

4. Equivalent structural formulations

Squaring distances does not change their number. Write

S:={∥x−y∥
2
:x∈X, y∈Y},∣S∣=D.

Several exact reformulations are useful.

Circle-cover formulation

For every x∈X,

Y⊆
s∈S
⋃
	​

{z:∥z−x∥
2
=s}.
(5)

Thus the same set of D radii, centered at each of n different points, must cover Y.

The symmetric statement holds after interchanging X and Y.

Distance-matrix formulation

The squared-distance matrix

M
ij
	​

=∥x
i
	​

−y
j
	​

∥
2

has entries in the alphabet S and satisfies

M
ij
	​

=∥x
i
	​

∥
2
+∥y
j
	​

∥
2
−2x
i
	​

⋅y
j
	​

.
(6)

Hence

rank
R
	​

M≤4.
(7)

So the problem asks for a highly repetitive D-symbol matrix of rank at most 4, subject to the additional nonlinear Euclidean-realizability conditions.

Radial difference-set formulation

Let

X−Y={x−y:x∈X,y∈Y}.

Then

D(X,Y)=∣{∥z∥:z∈X−Y}∣.
(8)

Since R
2
 is torsion-free,

∣X−Y∣≥2n−1.
(9)

Thus an affirmative construction must place many distinct difference vectors on the same circles about the origin. The square lattice achieves an average radial collapse of order 
logn
	​

; the problem asks for an unbounded improvement over that.

5. Rigorous planar lower bounds
5.1 Two-anchor bound

Fix two distinct points x,x
′
∈X. Associate to each y∈Y the pair

(∥y−x∥
2
,∥y−x
′
∥
2
)∈S
2
.

For each prescribed pair (s,t), the point y belongs to the intersection of two circles with distinct centers. There are at most two such points. Therefore

n≤2D
2
,

so

D≥
2
n
	​

	​

.
(10)

This is sharp as a purely two-anchor argument; it does not use the other n−2 centers.

5.2 Fixed-radius incidence bound

A stronger bound follows from treating each distance separately.

For r>0, let

e
r
	​

:=∣{(x,y)∈X×Y:∥x−y∥=r}∣.
Lemma

There is an absolute constant C such that

e
r
	​

≤Cn
4/3
.
(11)
Proof

Draw the n radius-r circles centered at the points of X.

A circle incident to at most two points of Y accounts for at most 2n incidences in total. On every remaining circle, connect its incident Y-points cyclically by circular arcs. This creates a topological multigraph on the n vertices Y, with at least e
r
	​

−2n edges.

Two Y-vertices can be joined by arcs from at most two radius-r circles, because the center of such a circle must lie in the intersection of the two radius-r circles centered at those vertices. After deleting parallel duplicates, a simple graph remains with at least

2
e
r
	​

−2n
	​


edges.

Two distinct circles intersect at most twice, so this drawing has fewer than n
2
 crossings. The crossing lemma states that a simple graph with v vertices and e≥4v edges has at least

64v
2
e
3
	​


crossings. Applying it with v=n yields (11). ∎

There are n
2
 cross-pairs. Under the all-distinct interpretation all have positive distance, so

n
2
=
r∈Δ(X,Y)
∑
	​

e
r
	​

≤CDn
4/3
.

Therefore

D=Ω(n
2/3
).
	​

(12)

If X and Y may overlap but are individually distinct, there are at most n zero-distance pairs, and the same asymptotic conclusion follows.

This is the strongest completely derived lower bound in this analysis. It is far below n/
logn
	​

.

6. Necessary energy growth for an affirmative construction

For x∈X and s∈S, define

m
x
	​

(s):=∣{y∈Y:∥x−y∥
2
=s}∣.

Then

s∈S
∑
	​

m
x
	​

(s)=n.

Cauchy–Schwarz gives

s∈S
∑
	​

m
x
	​

(s)
2
≥
D
n
2
	​

.

Summing over x,

H(X,Y):=
x∈X
∑
	​

s∈S
∑
	​

m
x
	​

(s)
2
≥
D
n
3
	​

.
(13)

The number of unordered isosceles triples (x,{y,y
′
}) with y

=y
′
 is

T(X,Y)=
2
H(X,Y)−n
2
	​

≥
2
1
	​

(
D
n
3
	​

−n
2
).
(14)

Equivalently,

T(X,Y)=
{y,y
′
}⊂Y
∑
	​

∣X∩Bis(y,y
′
)∣,
(15)

where Bis(y,y
′
) is the perpendicular bisector of yy
′
.

Therefore an affirmative construction would necessarily satisfy

D=o(
logn
	​

n
	​

)⟹T(X,Y)=ω(n
2
logn
	​

).
(16)

It would also imply, for every x∈X,

s
max
	​

m
x
	​

(s)≥
D
n
	​

=ω(
logn
	​

).
(17)

Thus every x must be the center of a circle containing ω(
logn
	​

) points of Y, and symmetrically every y must center such a circle through points of X.

A sufficient negative target is consequently

T(X,Y)=O(n
2
logn
	​

).
(18)

No argument obtained here proves (18).

A second energy is

E(X,Y):=
r
∑
	​

e
r
2
	​

=∣{(x,y,x
′
,y
′
):∥x−y∥=∥x
′
−y
′
∥}∣.
(19)

Since

E(X,Y)≥
D
n
4
	​

,

an affirmative construction would require

E(X,Y)=ω(n
3
logn
	​

),
(20)

whereas the universal bound

E(X,Y)=O(n
3
logn
	​

)
(21)

would disprove it.

These are precise intermediate targets.

7. Geometric concentration attacks
Collinear subsets

If k points of X lie on a line L, fix any y∈Y. A circle centered at y intersects L in at most two points. Hence

k≤2D,D≥k/2.
(22)

Thus a desired construction cannot have

ω(
logn
	​

n
	​

)

points of either side on one line.

Low-degree curves

Let k points of X lie on an irreducible algebraic curve Γ of degree δ. For a center y such that Γ is not a circle centered at y, each distance circle around y intersects Γ in at most 2δ points. Therefore

k≤2δD.
(23)

If Γ itself is a circle, at most one point y is its center; another y∈Y gives the same conclusion with δ=2.

Consequently, constructions placing one side on a line, circle, conic, parabola, or any fixed-degree curve give a linear lower bound in the number of points on that curve. This eliminates the obvious factorization constructions such as

(t,t
2
),∥(a,a
2
)−(b,b
2
)∥
2
=(a−b)
2
(1+(a+b)
2
).

The algebraic factorization does not help because the curve-incidence obstruction already forces D=Ω(n).

8. Construction families tested
8.1 Regular polygons and finite symmetry orbits

Take the vertices of a regular 2n-gon and assign alternating vertices to X and Y. Cross-chords correspond to odd cyclic separations, giving

D(X,Y)=⌈
2
n
	​

⌉.
(24)

This yields the exact small cases

F
2
	​

(1)=1,F
2
	​

(2)=1,F
2
	​

(3)=F
2
	​

(4)=2.

For n≥3, D=1 is impossible by the two-anchor bound.

Any construction where one side lies on a common circle has D≥n/2 when viewed from a noncentral point of the other side. Hence cyclic and dihedral symmetry cannot give the desired sublinear scale.

8.2 Cartesian products

Let

X=A×B,Y=C×E.

Then the squared-distance set is

P+Q,

where

P={(a−c)
2
:a∈A,c∈C},Q={(b−e)
2
:b∈B,e∈E}.
(25)

If ∣A∣=∣C∣=m, then

∣A−C∣≥2m−1,

and squaring is at most two-to-one, so

∣P∣≥m.
(26)

Likewise ∣Q∣≥m. Since finite subsets of R satisfy

∣P+Q∣≥∣P∣+∣Q∣−1,

this gives only

D≥2m−1=2
n
	​

−1.
(27)

For arithmetic progressions,

P={0,1,4,…,(m−1)
2
},

so P+P is the set of sums of two squares and gives the lattice scale.

The exact constructive subproblem for this family is:

Find m-point real sets A,B,C,E for which

	​

{(a−c)
2
+(b−e)
2
}
	​

=o(
logm
	​

m
2
	​

).
(28)

No such spectra were found.

A useful rigidity observation is that if every cross-square (a−c)
2
 lies in a single arithmetic progression α+δZ, then

2(a−a
′
)(c−c
′
)∈δZ
(29)

for every a,a
′
∈A and c,c
′
∈C. Fixing one nonzero difference on each side shows that all ratios of differences inside A, and all ratios inside C, are rational. Thus an arithmetic-progression distance spectrum forces both sets toward one-dimensional rational-lattice structure; it is not a freely tunable continuous construction.

8.3 General planar lattices

For a lattice patch with basis vectors v
1
	​

,v
2
	​

, squared distances are values of

Q(u,v)=au
2
+buv+cv
2
,b
2
<4ac.
(30)

To beat the target through lattices, one needs a sequence Q
m
	​

 such that

∣{Q
m
	​

(u,v):∣u∣,∣v∣<m}∣=o(
logm
	​

m
2
	​

).
(31)

Fixed positive-definite integral forms exhibit the same basic binary-norm obstruction as the square lattice. Increasing the discriminant tends to enlarge the numerical range and reduce representation multiplicities by the chosen form; global sparsity of represented integers does not automatically reduce the number of values produced by the m×m difference box.

Finite test

For m=10,15,20, I exhaustively tested every primitive integral form

Q(u,v)=au
2
+buv+cv
2

with

1≤a≤c≤40,b
2
<4ac.

The minimum was attained by u
2
+v
2
:

m
10
15
20
	​

∣{u
2
+v
2
:∣u∣,∣v∣<m}∣
51
106
180
	​

	​


Random tests with coefficients up to 500, for m≤30, likewise found no improvement over the square form. This is only finite evidence.

8.4 Translated lattice cosets

Take one square grid and translate the other by (α,β). For rational shifts α=a/q,β=b/q, the squared-distance values are, after multiplying by q
2
,

(qu−a)
2
+(qv−b)
2
.
(32)

A half-shift (1/2,1/2) gives a modest constant improvement because the relevant coordinates are both odd. It does not alter the observed order.

For example:

m
10
15
20
30
40
	​

unshifted
51
106
180
382
653
	​

(1/2,1/2)-shifted
47
99
167
352
603
	​

	​


An exhaustive search over denominators q≤50 for m=15,25,40 found the half-shift best among those tested.

Modular obstruction

For A,B⊂F
p
2
	​

, let

q(z
1
	​

,z
2
	​

)=z
1
2
	​

+z
2
2
	​

.

Since A−b
0
	​

⊂A−B,

∣A−B∣≥∣A∣.

Every fiber q
−1
(t) contains at most 2p points, because for each first coordinate there are at most two choices of the second. Therefore

∣q(A−B)∣≥
2p
∣A∣
	​

.
(33)

In density language, the fraction of allowed norm residues is at least half the point-set density. Thus periodic congruence filtering loses approximately as much point density as distance-residue density. Repeating many modulus restrictions does not produce an evident vanishing gain.

8.5 Higher-rank generalized arithmetic progressions

A possible attempt is to encode an m
3
 box injectively into the plane:

P={a
1
	​

v
1
	​

+a
2
	​

v
2
	​

+a
3
	​

v
3
	​

:0≤a
i
	​

<m}.
(34)

Its squared differences are values of the rank-two quadratic form

Q(u)=
	​

i
∑
	​

u
i
	​

v
i
	​

	​

2
.
(35)

There is an exact obstruction to making Q integer-valued in only one rational coefficient while keeping the parameterization proper.

Let G=(v
i
	​

⋅v
j
	​

) be the Gram matrix. If all entries of G are rational multiples of one real number λ, then G/λ is a rational matrix of rank at most 2. For three or more generators it has a nonzero rational null vector q. Hence

	​

i
∑
	​

q
i
	​

v
i
	​

	​

2
=q
T
Gq=0,

so

i
∑
	​

q
i
	​

v
i
	​

=0.

Clearing denominators gives a nontrivial integer relation, and the box is not injectively parameterized for large m.

Thus one cannot simply project the three-dimensional integer grid into R
2
 while retaining an integer-valued squared norm with O(m
2
) values. Irrational coefficients preserve injectivity but typically split equality of norms into several independent coefficient equations, sharply reducing collisions.

For example, the proper rank-three set

P
m
	​

={(a+c,b+
2
	​

c):0≤a,b,c<m}

has m
3
 points, while a squared difference is

(u+w)
2
+v
2
+2w
2
+2
2
	​

vw.

It is determined by the integer pair

((u+w)
2
+v
2
+2w
2
,2vw).

Exact symbolic counting for m≤15 produced more than m
3
 distance values once m was moderately large, not fewer.

8.6 Recursive and multiscale products

Suppose one tries to replace every point a by a tiny copy a+εb. Then

∥(a−a
′
)+ε(b−b
′
)∥
2
=∥a−a
′
∥
2
+2ε⟨a−a
′
,b−b
′
⟩+ε
2
∥b−b
′
∥
2
.
(36)

The middle term prevents exact product composition. It vanishes identically only when the two difference spans are orthogonal. In R
2
, this allows at most two nontrivial one-dimensional factors, precisely the Cartesian-grid construction. Four independent one-dimensional factors would require R
4
.

Taking ε extremely small does not help because the problem counts exact equalities, not approximate distances.

9. Why single-color extremal arguments stop too early

Color every edge of K
n,n
	​

 by its distance. There are D colors and n
2
 edges.

Each individual color class is a planar fixed-distance graph and has

O(n
4/3
)

edges. This yields only D=Ω(n
2/3
).

Under the desired affirmative estimate, the average color class would have

D
n
2
	​

=ω(n
logn
	​

)
(37)

edges. This is still much smaller than n
4/3
. Therefore no argument that treats the distance classes independently can reach the threshold. One must exploit the fact that all colors arise from the same two point sets and the same Euclidean coordinates.

The same obstruction appears in the circle-arrangement formulation: combining all nD circles creates high edge multiplicities precisely along perpendicular bisectors rich in X. Controlling those multiplicities reduces to the weighted sum

ℓ
∑
	​

∣X∩ℓ∣w
Y
	​

(ℓ),
(38)

where w
Y
	​

(ℓ) counts pairs of Y-points reflected across ℓ. Crude rich-line estimates recover only bounds around the n
2/3
 regime. The unresolved issue is the joint occurrence of lines that are simultaneously rich in X and strong partial reflection axes of Y.

10. Finite falsification program

No finite n can disprove an eventual-existence assertion. A negative resolution requires a uniform asymptotic lower bound. Finite computation can nevertheless search for configurations with unexpectedly small D.

A direct exact search can proceed as follows.

Fix two anchors x
1
	​

,x
2
	​

. Encode every y by its pair of squared distances in S
2
, plus the choice of side of the anchor line. Every symbol pair occurs at most twice.

Enumerate candidate D-symbol distance matrices satisfying:

rankM≤4,

the two-anchor multiplicity restriction, and the analogous column restrictions.

Gauge-fix

x
1
	​

=(0,0),x
2
	​

=(1,0)

and impose the polynomial equations

∥x
i
	​

−y
j
	​

∥
2
=s
c(i,j)
	​

.

Use exact elimination or real-algebraic certification to decide realizability. Numerical solutions alone would not certify repeated distances.

The number of color matrices grows too rapidly for this to approach the asymptotic range without further structural pruning.

A separate exhaustive integer search found that, among m-element subsets of {0,…,10} containing 0, for 2≤m≤6, arithmetic progressions minimized

∣S(A)+S(A)∣,S(A)={(a−a
′
)
2
:a,a
′
∈A}.

The minima were

3,6,10,15,20

for m=2,3,4,5,6, respectively. Again, this is only local evidence for the Cartesian-product attack.

11. Relation to F=o(f)

Let f
2
	​

(2n) be the minimum number of ordinary nonzero distances among 2n distinct planar points.

For any 2n-point set P, partition P=X⊔Y with ∣X∣=∣Y∣=n. Cross-distances are a subset of all distances in P. Hence

F
2
	​

(n)≤f
2
	​

(2n).
(39)

Therefore F=o(f) would be a stronger assertion than the displayed main question, given the lattice upper bound

f
2
	​

(2n)=O(
logn
	​

n
	​

).

The converse does not follow: even if

F
2
	​

(n)=o(
logn
	​

n
	​

),

the unknown comparison between f
2
	​

(2n) and n/
logn
	​

 prevents concluding F=o(f).

Thus the two questions are not formally equivalent.

12. Precise remaining targets

A successful constructive attack could meet any one of these targets:

Variable quadratic forms

∣{Q
m
	​

(u,v):∣u∣,∣v∣<m}∣=o(m
2
/
logm
	​

).

Cartesian spectra
Construct one-dimensional cross-square spectra P
m
	​

,Q
m
	​

 arising from actual point sets with

∣P
m
	​

+Q
m
	​

∣=o(m
2
/
logm
	​

).

Proper high-rank progression
Find a rank-two positive semidefinite quadratic form on a proper high-rank integer box whose average fiber size is

ω(
logn
	​

).

Weighted bisector construction
Produce X,Y with

{y,y
′
}
∑
	​

∣X∩Bis(y,y
′
)∣=ω(n
2
logn
	​

)

while all radii still belong to one global set of
o(n/
logn
	​

) values.

A negative attack could target either

E(X,Y)=O(n
3
logn
	​

)

or

T(X,Y)=O(n
2
logn
	​

).

Both would rule out the desired construction. The fixed-radius incidence method does not approach either bound because it discards interactions between different radii.

Net status

With repeated indexed points, the literal statement is trivial.

With all 2n points distinct, the verified planar bounds are

Ω(n
2/3
)≤F
2
	​

(n)≤O(
logn
	​

n
	​

).

The R
3
 analogue has an explicit

O(n
2/3
)=o(
logn
	​

n
	​

)

construction.

None of the planar lattice, translated-lattice, Cartesian-product, symmetry, low-degree-curve, high-rank-progression, modular, or multiscale attacks above proves or disproves the intended all-distinct planar assertion.
Offline proof-search report
1. Statement-integrity defect

The immutable wording does not state that the 2n points are distinct.

Under the literal interpretation allowing repetitions, take

x
1
	​

=⋯=x
n
	​

=y
1
	​

=⋯=y
n
	​

.

There is one cross-distance, and

1=o(
logn
	​

n
	​

).

Thus that interpretation collapses immediately.

There are at least three materially different intended conventions:

repetitions are allowed;

each list x
1
	​

,…,x
n
	​

 and y
1
	​

,…,y
n
	​

 is internally distinct, but the lists may overlap;

all 2n points are pairwise distinct.

The comparison with f(2n), which concerns 2n points, strongly suggests convention 3, but it does not formally impose it. Consequently, the exact immutable statement has no unique nontrivial interpretation. All planar analysis below is conditional on the strongest convention: all 2n points are pairwise distinct.

There is a second ambiguity: “one can also ask this for points in R
3
” could mean the same numerical o(n/
logn
	​

) question, or the dimension-specific comparison F
3
	​

=o(f
3
	​

). These are different; the former has a simple affirmative construction given below.

2. Exact reformulations

For finite X,Y⊂R
2
, define

Δ(X,Y)={∥x−y∥
2
:x∈X, y∈Y},m(X,Y)=∣Δ(X,Y)∣.

Squaring does not change the number of distinct nonnegative distances.

The intended main question is whether, for every sufficiently large n, there are disjoint n-point sets X,Y with

m(X,Y)=o(
logn
	​

n
	​

).

Equivalently, if

F
2
	​

(2n)=
∣X∣=∣Y∣=n
X∩Y=∅
	​

min
	​

m(X,Y),

the question is whether

F
2
	​

(2n)=o(
logn
	​

n
	​

).

The function F
2
	​

(2n) is nondecreasing: deleting one point from each side of an (n+1,n+1)-configuration cannot introduce a new distance.

Hence a construction on a subsequence N
k
	​

 suffices for all large n if

k
sup
	​

N
k
	​

N
k+1
	​

	​

<∞

and the little-o estimate holds along that subsequence. A very sparse arithmetic subsequence is not automatically sufficient.

3. Unconditional planar lower bounds
3.1 Two-center bound

Let S=Δ(X,Y), with ∣S∣=m. Fix distinct x,x
′
∈X. Every y∈Y determines

(∥y−x∥,∥y−x
′
∥)∈
S
	​

×
S
	​

.

For prescribed radii r,r
′
, the two circles centered at x,x
′
 intersect in at most two points. Therefore

n≤2m
2
,m≥
2
n
	​

	​

.

This remains the strongest completely elementary general bound obtained here.

It also resolves the fixed-distance boundary case: if m=1, then n≤2. Equality is possible for n=2 by taking the two parts to be the two opposite pairs of vertices of a square.

3.2 A weighted perpendicular-bisector bound

For y∈Y and s∈S, put

k
y,s
	​

=∣{x∈X:∥x−y∥
2
=s}∣.

Since ∑
s
	​

k
y,s
	​

=n, Cauchy–Schwarz gives

s
∑
	​

(
2
k
y,s
	​

	​

)≥
2
1
	​

(
m
n
2
	​

−n).

Summing over y,

T(X,Y):=∣{({x,x
′
},y):x

=x
′
, ∥x−y∥=∥x
′
−y∥}∣≥
2
n
	​

(
m
n
2
	​

−n).
(1)

For each line ℓ, define

μ
X
	​

(ℓ)=∣{{x,x
′
}⊂X:ℓ is the perpendicular bisector of xx
′
}∣.

Then exactly

T(X,Y)=
ℓ
∑
	​

μ
X
	​

(ℓ)∣Y∩ℓ∣.
(2)

Thus high isosceles energy is exactly high weighted incidence with partial reflection axes. Moreover,

μ
X
	​

(ℓ)

counts pairs of points of X exchanged by reflection in ℓ.

Using the following exact incidence theorem:

For a finite set P of points and a finite set L of distinct lines in R
2
,

I(P,L)≤C(∣P∣
2/3
∣L∣
2/3
+∣P∣+∣L∣)

for an absolute constant C,

a dyadic decomposition by the size of μ
X
	​

(ℓ) gives

T(X,Y)=O(n
7/3
).

Combining this with (1) yields

m(X,Y)=Ω(n
2/3
).
(3)

This is far below the required scale:

n
2/3
=o(
logn
	​

n
	​

).

A more structural consequence is obtained by setting

M
X
	​

=
ℓ
max
	​

μ
X
	​

(ℓ).

The unweighted incidence estimate gives

T(X,Y)≤O(M
X
	​

n
2
),

so, when m≪n,

M
X
	​

≳
m
n
	​

.

Therefore a desired construction would force

M
X
	​

=ω(
logn
	​

),

and symmetrically M
Y
	​

=ω(
logn
	​

). Both sides must possess increasingly large partial reflection symmetries.

This does not contradict grid configurations, so it is a structural necessity rather than an obstruction.

4. Difference-set and energy formulations

Let

A=X−Y={x−y:x∈X, y∈Y}.

Then

m(X,Y)=∣{∥z∥
2
:z∈A}∣.

A generic linear projection to R shows

∣X−Y∣≥∣X∣+∣Y∣−1=2n−1.

Consequently, a desired construction must satisfy

m(X,Y)
∣X−Y∣
	​

=ω(
logn
	​

).
(4)

Thus the difference set must have, on average, more than 
logn
	​

 distinct vectors on each occupied circle centered at the origin.

Let

c(z)=∣{(x,y):x−y=z}∣,R
s
	​

=
∥z∥
2
=s
∑
	​

c(z).

Then

s
∑
	​

R
s
	​

=n
2
.

The cross-distance energy is

E
dist
	​

(X,Y)=
s
∑
	​

R
s
2
	​

,

and

E
dist
	​

(X,Y)≥
m(X,Y)
n
4
	​

.
(5)

Hence the desired estimate would require

E
dist
	​

(X,Y)=ω(n
3
logn
	​

).

This second-moment condition is too weak to isolate the main threshold. Lattice-type sets can have radial multiplicities sufficiently uneven that their distance energy is substantially larger than the Cauchy lower bound. An energy-only attack loses precisely the information about the support of the radial distribution.

A viable lower-bound proof therefore needs a multiscale support estimate, not merely a bound on ∑R
s
2
	​

.

5. Natural geometric constructions and their failures
Parallel lines

Write

X={(a
i
	​

,0)},Y={(b
j
	​

,h)}.

The squared distances are

(a
i
	​

−b
j
	​

)
2
+h
2
.

For n-element subsets A,B⊂R,

∣A−B∣≥2n−1.

Since squaring is at most two-to-one,

m(X,Y)≥n.

Thus parallel-line constructions cannot give even o(n).

Orthogonal axes

For

X={(a
i
	​

,0)},Y={(0,b
j
	​

)},

the squared distances form

A
2
+B
2
.

Each of A
2
,B
2
 has at least ⌈n/2⌉ elements, and for finite real sets U,V,

∣U+V∣≥∣U∣+∣V∣−1.

Therefore

m(X,Y)≥n−1.

This is the two-dimensional remnant of the orthogonal-subspace construction, and it remains linear because a sphere in a one-dimensional subspace contains at most two points.

Lines, circles, and bounded-complexity curves

If Y lies on one line, each circle centered at a fixed x∈X meets that line in at most two points, giving

m(X,Y)≥
2
n
	​

.

The same conclusion holds if Y lies on one circle: choose x∈X different from its center.

More generally, if Y lies on the union of k lines and circles, choose x∈X that is not the center of any circular component. Each distance circle centered at x contains at most 2k points of Y, so

m(X,Y)≥
2k
n
	​

.

Any such construction would require

k=ω(
logn
	​

).

An algebraic version follows from Bézout’s theorem:

Two plane algebraic curves over C, of degrees d and e, with no common irreducible component, have at most de distinct intersection points.

If Y lies on a degree-d algebraic curve and x is not the center of one of its circular components, every distance circle through points of Y contains at most 2d of them. Hence

m(X,Y)≥
2d
n
	​

.

Fixed-degree algebraic-curve constructions are therefore excluded.

Regular polygons and finite planar symmetry

A finite orbit under planar rotations is cyclic or dihedral. Distances between two such orbits are controlled by one angular difference parameter and ordinarily give Θ(n) values. The product symmetry behind two orthogonal circles requires two independent two-dimensional rotation planes; it cannot be reproduced by a planar isometry group.

6. Matrix and polynomial reformulations

Let

D
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
.

Writing U,V for the n×2 coordinate matrices and

a
i
	​

=∥x
i
	​

∥
2
,b
j
	​

=∥y
j
	​

∥
2
,

gives

D=a1
T
+1b
T
−2UV
T
.

Therefore

rank
R
	​

D≤4.
(6)

The problem is consequently equivalent to constructing an n×n, m-valued matrix of this special Euclidean form with

m=o(
logn
	​

n
	​

).

Rank alone is inadequate: abstract low-rank matrices can have very few values but fail Euclidean realizability. Even combining rank with distinct rows gives only polynomial bounds such as n≤m
4
; the two-circle argument improves this to n≤2m
2
, still much too weak.

There is also an exact annihilating-polynomial formulation. If

S=Δ(X,Y),Q(t)=
s∈S
∏
	​

(t−s),

then

Q((u
1
	​

−v
1
	​

)
2
+(u
2
	​

−v
2
	​

)
2
)=0on X×Y.
(7)

Let

A
X
	​

=R[u
1
	​

,u
2
	​

]/I(X),A
Y
	​

=R[v
1
	​

,v
2
	​

]/I(Y).

For distinct points, A
X
	​

≅R
n
 and A
Y
	​

≅R
n
. In

A
X
	​

⊗A
Y
	​

≅R
n
2
,

consider

h=(u
1
	​

−v
1
	​

)
2
+(u
2
	​

−v
2
	​

)
2
.

The minimal polynomial of multiplication by h is exactly

s∈Δ(X,Y)
∏
	​

(t−s),

so its degree is precisely m(X,Y).

A lower-bound solution could therefore be phrased as a lower bound on the minimal-polynomial degree of this low-tensor-rank element. Ordinary Hilbert-function arguments recover only approximately the 
n
	​

 scale because n arbitrary planar points can lie on curves of degree O(
n
	​

).

7. High-rank algebraic modules: the most concrete nonstandard construction route

A planar point set need not be a rank-two lattice. A finitely generated additive subgroup of C can have arbitrarily large rank over Z, although it is then nondiscrete.

Let K⊂C be a number field stable under complex conjugation, with

[K:Q]=2d,K
+
=K∩R,[K
+
:Q]=d.

Choose a Q-basis

β
1
	​

,…,β
2d
	​


of K, and define

B
L
	​

={
r=1
∑
2d
	​

a
r
	​

β
r
	​

:0≤a
r
	​

<L}.

Then

∣B
L
	​

∣=L
2d
.

For a suitable translate τ, the sets

X=B
L
	​

,Y=B
L
	​

+τ

are disjoint.

Every squared cross-distance has the form

z
z
,z∈K,

and lies in K
+
. In a fixed basis of K
+
, its d coefficients are quadratic forms of size O
K
	​

(L
2
). Thus dimensional counting gives only

m(X,Y)=O
K
	​

(L
2d
)=O
K
	​

(n).

The needed gain must come from arithmetic sparsity of the relative norm map

N
K/K
+
	​

(z)=z
z
.

A precise construction target is:

∣{z
z
:z∈(B
L
	​

−B
L
	​

)−τ}∣≤C
K
	​

logL
	​

L
2d
	​

,
(8)

with a family of fields satisfying

C
K
	​

d
	​

⟶0.
(9)

The factor 
d
	​

 is necessary because

logn=2dlogL.

This route contains several unresolved obligations:

establish (8) for coefficient boxes and translated boxes, not merely for norm-bounded ideals;

control the dependence of C
K
	​

 on the field, basis, denominators, and discriminant;

control the threshold L
0
	​

(K) uniformly enough for diagonalization;

extend perfect powers L
2d
 to every large n.

A useful obstruction shows why algebraic dimension alone cannot help. Suppose vectors v
1
	​

,…,v
r
	​

∈R
2
 have all pairwise inner products in a real number field E of degree d. If v
1
	​

,v
2
	​

 are linearly independent, solving from their Gram matrix shows

v
j
	​

∈Ev
1
	​

+Ev
2
	​

.

Hence the Q-rank of the generators is at most 2d. Their squared norms lie in the d-dimensional field E, with coefficient sizes quadratic in the box side. Pure coefficient counting therefore gives at best L
2d
, no smaller than the number L
r
 of points. Any gain must be genuinely arithmetic.

A concrete first test field is

K=Q(i,
2
	​

).

Writing

z=a+b
2
	​

+i(c+d
2
	​

)

gives

∣z∣
2
=(a
2
+2b
2
+c
2
+2d
2
)+2(ab+cd)
2
	​

.

Exact enumeration of the symmetric difference box produced:

L
2
4
8
	​

n=L
4
16
256
4096
	​

#{∣z∣
2
}
14
268
4778
	​

	​


At these sizes, this naive higher-rank box shows no improvement over the linear scale. This is only finite falsification, not an asymptotic result.

8. Finite-field and group analogues

Over a finite field F
q
	​

, the entire plane F
q
2
	​

 has q
2
 points but the quadratic expression

(a−c)
2
+(b−d)
2

takes at most q values. This suggests m≍
n
	​

.

The obstruction to lifting this directly to R
2
 is real rank. If a label t∈F
q
	​

 is replaced by a real number s
t
	​

, the resulting translation-invariant matrix

M
uv
	​

=s
Q(u−v)
	​


must have real rank at most 4 to be a planar squared-distance matrix. Its rank is the number of nonzero Fourier coefficients of the kernel g↦s
Q(g)
	​

. Nonconstant radial kernels on F
q
2
	​

 generally have Fourier support on entire dual norm shells, far larger than four.

A precise finite-field falsification target is:

Prove that every nonconstant real-valued function ϕ on F
q
	​

 gives

rank
R
	​

(ϕ(Q(u−v)))
u,v∈F
q
2
	​

	​

≥cq.

That would rule out the most direct modular lifting mechanism.

The same dimensional obstruction appears in character constructions. One circle can encode one cyclic character in R
2
. Separating a two-dimensional finite group requires two independent character pairs, naturally occupying R
4
.

9. The three-dimensional branch

If “ask this in R
3
” means the same numerical bound, there is an explicit construction valid for every n.

Let

L=⌈(2n)
1/3
⌉.

The integer cube

{0,1,…,L−1}
3

contains at least 2n points. Choose any 2n distinct points and divide them into X,Y, each of size n.

Every squared cross-distance is an integer between 1 and

3(L−1)
2
.

Thus

m(X,Y)≤3(L−1)
2
=O(n
2/3
),

and

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

Therefore the same-bound R
3
 branch is affirmative even with all 2n points pairwise distinct. More generally, the d-dimensional integer grid gives O(n
2/d
) distinct distances for every d≥3.

This does not resolve the potentially intended comparison F
3
	​

=o(f
3
	​

).

10. The F=o(f) question

Under the pairwise-distinct planar convention,

F
2
	​

(2n)≤f
2
	​

(2n),

because any balanced partition of a 2n-point configuration has its cross-distances among all distances of that configuration.

The numerical question

F
2
	​

(2n)=o(
logn
	​

n
	​

)

does not by itself imply F
2
	​

=o(f
2
	​

) without a matching lower bound for f
2
	​

. Conversely, F
2
	​

=o(f
2
	​

) is not formally equivalent to the numerical question without an upper comparison for f
2
	​

.

An elementary application of the two-center argument gives

f
2
	​

(N)≥
2
N−2
	​

	​

,

but this is much too weak to connect the two questions at the n/
logn
	​

 scale.

Under the repetition-allowed interpretation, F
2
	​

(2n)=1, while the preceding bound shows f
2
	​

(2n)→∞; then F=o(f) is again trivial. This reinforces why distinctness is a blocking semantic issue.

11. Finite falsification results and proposed searches

For the 4×4 integer grid, exhaustive enumeration of all

(
7
15
	​

)=6435

balanced partitions up to exchanging the colors shows that the minimum number of cross-distance classes is 4. A checkerboard partition attains it, with squared distances

{1,5,9,13}.

This only gives a constant-factor saving and does not suggest a little-o mechanism.

Useful exact computational searches are:

Enumerate small m-symbol matrices and impose vanishing of all 5×5 minors, followed by direct Euclidean realization constraints.

Search rational point configurations by branching on intersections of circles with radii from a prescribed set.

Enumerate modular colorings of large lattice boxes and count represented norm classes in the permitted difference residues.

Test algebraic norm boxes in fields of increasing degree, using exact coefficient tuples rather than floating-point distances.

Search for high-rank generalized arithmetic progressions whose Gram coefficients occupy a small number field but whose norm-value constants decrease.

None of the finite searches can verify the required all-large-n quantifier, but they can eliminate proposed mechanisms.

12. Precise remaining targets

The main unresolved planar branch can be attacked through any of the following exact targets.

Construction target

Produce conjugation-stable algebraic modules and coefficient boxes satisfying (8)–(9), with quantitative onset and all-n interpolation.

Radial inverse target

Classify pairs X,Y for which the norm map compresses X−Y by more than 
logn
	​

. A plausible dichotomy would need to isolate both:

additive-progressive behavior, such as planar grids;

cyclic or cocircular behavior, such as regular polygons.

Neither ordinary additive energy nor radial energy distinguishes these regimes adequately.

Euclidean symbol-matrix target

Prove or disprove a bound of the form

n≤Cm
logm
	​


for every m-valued planar cross-distance matrix with distinct underlying points. Since the elementary bound gives m≥c
n
	​

, the logarithms of m and n are comparable in the relevant range. Such a bound would disprove the requested little-o.

Minimal-polynomial target

Bound below the degree of the minimal polynomial of

h=(u
1
	​

−v
1
	​

)
2
+(u
2
	​

−v
2
	​

)
2

in A
X
	​

⊗A
Y
	​

, exploiting more than the separate Hilbert functions of X and Y.

Status

The intended pairwise-distinct planar statement was neither proved nor disproved.

Established here:

m(X,Y)≥
2
n
	​

	​

,m(X,Y)=Ω(n
2/3
)

using weighted perpendicular-bisector incidences; fixed-complexity line, circle, algebraic-curve, and planar symmetry constructions fail; and the same-bound three-dimensional variant has an explicit O(n
2/3
) construction.

The principal unresolved obstruction is to obtain, or rule out, an additional unbounded improvement beyond the 
logn
	​

-scale radial compression exhibited by two-dimensional norm-type constructions.
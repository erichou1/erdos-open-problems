Offline counterexample and falsification report
1. Statement-integrity obstruction

The exact text does not specify whether the 2n labelled points must be distinct.

If repetitions are allowed, take x
i
	​

=(0,0) and y
j
	​

=(1,0) for every i,j. There is exactly one cross-distance, so the first question is trivially affirmative.

If each list must contain distinct points but X∩Y is permitted, the problem is different.

If all 2n points must be distinct, the problem becomes the substantive interpretation suggested by the surrounding discussion.

Thus the immutable statement has multiple inequivalent readings. The intended strongest reading will be used below for exploration, but this ambiguity blocks a unique verdict on the exact wording.

There is also a quantifier issue: little-o applies to a sequence, not to one configuration. The clean formalization is

F
2
	​

(n):=
X,Y⊂R
2
∣X∣=∣Y∣=n,X∩Y=∅
	​

min
	​

∣Δ(X,Y)∣,Δ(X,Y)={∣x−y∣:x∈X,y∈Y},

and the intended assertion is

n
F
2
	​

(n)
logn
	​

	​

⟶0.

Its negation is

∃ε>0 ∀N ∃n≥N:F
2
	​

(n)≥ε
logn
	​

n
	​

.

Consequently, there is no meaningful “smallest counterexample” to the little-o assertion without first fixing an ε.

2. Elementary planar bounds

Write K=∣Δ(X,Y)∣. Squaring distances does not change their number.

Two-anchor lower bound

Choose distinct x
1
	​

,x
2
	​

∈X. Each y∈Y determines an ordered pair

(∣x
1
	​

−y∣,∣x
2
	​

−y∣)∈Δ(X,Y)
2
.

For a fixed pair of radii, y lies in the intersection of two circles with distinct centers, so there are at most two possibilities. Hence

n≤2K
2
,
K≥
n/2
	​

	​

.

This is the strongest completely elementary universal lower bound found here.

Elementary linear upper bound

Take

x
i
	​

=(cos(2πi/n),sin(2πi/n)),y
j
	​

=2(cos(2πj/n),sin(2πj/n)).

Then

∣x
i
	​

−y
j
	​

∣
2
=5−4cos
n
2π(i−j)
	​

,

so there are at most ⌊n/2⌋+1 distances. Thus

n/2
	​

≤F
2
	​

(n)≤⌊n/2⌋+1
	​

.

The desired scale lies far between these bounds.

3. The three-dimensional variant passes all quantifiers

Under the strongest distinctness interpretation, the R
3
 variant has an elementary construction.

Let M be the least even integer satisfying

2
M
3
	​

≥n.

In the cube

Q
M
	​

={0,1,…,M−1}
3

there are exactly M
3
/2 points of each coordinate-parity class. Choose X to be any n even-parity points and Y any n odd-parity points.

For x∈X,y∈Y,

∣x−y∣
2
=(x
1
	​

−y
1
	​

)
2
+(x
2
	​

−y
2
	​

)
2
+(x
3
	​

−y
3
	​

)
2

is an odd integer between 1 and 3(M−1)
2
. Therefore

∣Δ(X,Y)∣≤⌈
2
3(M−1)
2
	​

⌉=O(M
2
)=O(n
2/3
).

Hence

n/
logn
	​

∣Δ(X,Y)∣
	​

=O(
n
1/3
logn
	​

	​

)⟶0.

This works for every n, with all 2n points distinct and the two sets disjoint. More generally, the same grid argument gives O(n
2/d
) distances in dimension d≥3.

The failure of this argument in the plane is exact: a planar box containing n points has side length on the order of 
n
	​

, so the squared-distance range itself has order n. An additional arithmetic concentration phenomenon is required.

4. Necessary structure of any successful planar construction
4.1 Radial multiplicities and perpendicular bisectors

For y∈Y and δ∈Δ(X,Y), define

m
y
	​

(δ)=∣{x∈X:∣x−y∣=δ}∣.

Since ∑
δ
	​

m
y
	​

(δ)=n, Cauchy–Schwarz gives

δ
∑
	​

m
y
	​

(δ)
2
≥
K
n
2
	​

.

Thus the number of unordered pairs {x,x
′
}⊂X equidistant from y is at least

δ
∑
	​

(
2
m
y
	​

(δ)
	​

)≥
2K
n(n−K)
	​

.

Summing over y,

{x,x
′
}⊂X
∑
	​

∣Y∩B(x,x
′
)∣≥
2K
n
2
(n−K)
	​

,
	​


where B(x,x
′
) is the perpendicular bisector of xx
′
.

Let

L(Y)=
lines ℓ
max
	​

∣Y∩ℓ∣.

Since each B(x,x
′
) is a line,

2K
n
2
(n−K)
	​

≤(
2
n
	​

)L(Y),

and hence

L(Y)≥
K(n−1)
n(n−K)
	​

.
	​


The same holds with X,Y interchanged.

Therefore, if

K=o(
logn
	​

n
	​

),

then necessarily

L(X),L(Y)=ω(
logn
	​

).

So both sets must contain increasingly rich collinear subsets. A construction in general position, or even one with O(
logn
	​

) points per line, cannot work.

4.2 Fixed-complexity curves cannot work

If X is contained in the union of r lines, then for any fixed y, each circle centered at y meets each line in at most two points. Therefore

K≥
2r
n
	​

.

Thus a union of o(
logn
	​

) lines is impossible.

A similar statement applies to algebraic curves. The exact intersection theorem used is:

Two complex projective plane curves of degrees a and b, having no common irreducible component, have at most ab intersection points counted with multiplicity.

A distance circle has degree 2. Hence if one side is supported on curves of total degree D, with no component equal to a distance circle centered at the selected opposite point, then

K≥
2D
n
	​

.

Consequently, any successful algebraic-curve construction must have support degree

D=ω(
logn
	​

).

Lines, circles, conics, fixed-degree parametrized curves, and bounded unions of such objects are eliminated.

4.3 Difference-vector formulation

Let

X−Y={x−y:x∈X,y∈Y}.

A generic linear projection to R shows

∣X−Y∣≥∣X∣+∣Y∣−1=2n−1.

The difference set must lie on K circles centered at the origin. Thus some norm shell contains at least

K
2n−1
	​


distinct difference vectors. Under the desired bound this is

ω(
logn
	​

).

The planar problem can therefore be restated as follows:

Can a bipartite difference set containing at least 2n−1 vectors be concentrated on o(n/
logn
	​

) Euclidean norm shells?

The difficulty is that the difference vectors cannot be chosen independently; they must have the additive form X−Y.

4.4 Equal-distance energy

Let

r(t)=∣{(x,y)∈X×Y:∣x−y∣
2
=t}∣

and define

E(X,Y)=
t
∑
	​

r(t)
2
.

Then

t
∑
	​

r(t)=n
2
,

so

K≥
E(X,Y)
n
4
	​

	​

.

A successful construction would require

E(X,Y)=ω(n
3
logn
	​

).

Equivalently, its used distance values would have average multiplicity

K
n
2
	​

=ω(n
logn
	​

).

A universal estimate

E(X,Y)=O(n
3
logn
	​

)

would immediately rule out the desired construction. Proving or violating this energy threshold is a precise intermediate target.

5. Exact matrix obstruction

Let

D
ij
	​

=∣x
i
	​

−y
j
	​

∣
2
.

Fix x
1
	​

,y
1
	​

, and form the doubly centered matrix

C
ij
	​

=D
ij
	​

−D
i1
	​

−D
1j
	​

+D
11
	​

.

Writing

u
i
	​

=x
i
	​

−x
1
	​

,v
j
	​

=y
j
	​

−y
1
	​

,

gives the exact identity

C
ij
	​

=−2u
i
	​

⋅v
j
	​

	​

.

Therefore

rankC≤2
	​


in the plane, and rankC≤3 in R
3
.

Also,

rankD≤4

in the plane.

This yields a strong finite falsification filter: any proposed k-symbol distance matrix must admit positive real values s
1
	​

,…,s
k
	​

 such that every 3×3 minor of its doubly centered version vanishes.

Rank is necessary but not sufficient. The factorization must additionally satisfy the Euclidean norm equations

D
ij
	​

=∣z+u
i
	​

−v
j
	​

∣
2

for a common vector z=x
1
	​

−y
1
	​

. This extra positive-definite compatibility eliminates many attractive low-rank constructions.

6. Construction families tested and retained failures
6.1 Parallel lines

If X and Y lie on parallel lines with scalar coordinates A,B, then squared distances are

(a−b)
2
+h
2
.

The signed difference set satisfies

∣A−B∣≥2n−1.

Squaring identifies at most two opposite values, giving

K≥n.

No parallel-line construction can work.

6.2 Perpendicular axes

If

X={(a
i
	​

,0)},Y={(0,b
j
	​

)},

then

∣x
i
	​

−y
j
	​

∣
2
=a
i
2
	​

+b
j
2
	​

.

The sets {a
i
2
	​

} and {b
j
2
	​

} each have at least ⌈n/2⌉ elements. For finite real sets A,B,

∣A+B∣≥∣A∣+∣B∣−1.

Hence

K≥n−1.

The attractive reduction to a small sumset remains linear because each axis contributes only one degree of freedom.

6.3 One circle or finitely many circles

For a fixed y not equal to the supporting circle’s center, every distance circle centered at y intersects the support circle in at most two points. Thus one entire side on a circle forces

K≥n/2.

The same reasoning eliminates bounded unions of circles, apart from exceptional concentric components that can occur for at most their finitely many centers.

6.4 Checkerboard lattice construction

For even q, let X,Y be the two parity classes of the q×q integer grid. Each has n=q
2
/2 points. Its cross-distance set is exactly

{a
2
+b
2
:∣a∣,∣b∣≤q−1,a+b odd}.

This is the most effective structured planar family found in the finite searches. It exploits the same norm collisions as the ordinary square lattice but removes the even squared distances.

Direct enumeration produced:

q
20
50
100
200
500
1000
	​

n=q
2
/2
200
1250
5000
20000
125000
500000
	​

K
82
469
1750
6570
38228
145694
	​

	​


The normalized quantity

n
K
logn
	​

	​


was approximately

0.944, 1.002, 1.021, 1.034, 1.048, 1.056.

There is no numerical indication of decay toward zero. This is not an asymptotic proof; it identifies the exact arithmetic bottleneck.

To certify failure of this family, it would suffice to prove

	​

{a
2
+b
2
≤N:a+b odd}
	​

≥c
logN
	​

N
	​


for an absolute c>0.

6.5 Affine and shifted lattices

Finite searches considered:

rational translates of square grids with denominators up to 10;

diagonal quadratic forms a
2
+Db
2
 for 1≤D≤100;

the hexagonal form a
2
+ab+b
2
.

Within the tested ranges, the square form or its half-lattice checkerboard translate was always best. Increasing the discriminant reduced collisions rather than increasing them. These tests do not exclude forms depending delicately on n, but they give no candidate mechanism for an additional vanishing factor.

6.6 Congruence filtering

Checkerboard coloring is a 2-adic congruence filter. A natural idea is to impose many modular conditions so that cross-difference norms occupy very few residue classes.

For an odd prime p, however, every fiber of

(u,v)⟼u
2
+v
2
(modp)

has at most 2p elements: for each u, there are at most two choices of v. Hence for any A⊂F
p
2
	​

,

∣{u
2
+v
2
:(u,v)∈A}∣≥
2p
∣A∣
	​

.

Thus a single prime-modulus restriction cannot create an unbounded advantage between point density and norm-value density. Composite moduli and unions of cosets remain a possible but unproductive branch; the finite tests found only constant-factor gains.

6.7 High-dimensional Hamming schemes do not compress to the plane

The d-dimensional cube has 2
d−1
 points in each parity class and only about d/2 odd cross-Hamming distances. It is tempting to assign a planar Euclidean length to each Hamming distance.

Let M
xy
	​

=s
∣x−y∣
	​

 be such a squared-distance matrix between the two parity classes. Viewing it as a convolution operator and diagonalizing by Walsh characters gives:

a constant assignment has rank 1;

every nonconstant radial assignment has rank at least d.

The reason is that a nonzero Fourier coefficient at level r activates all (
r
d
	​

) characters at that level, and the smallest nontrivial multiplicity is d.

Since a planar squared-distance matrix has rank at most 4, this scheme cannot be realized for d≥5. Thus the successful high-dimensional cube/grid phenomenon cannot simply be relabelled and compressed into R
2
.

6.8 Multiplication-table ideas encounter the Euclidean-signature obstruction

Low-rank expressions such as

(a−c)(b−d)

have potentially few distinct values and expand as row terms, column terms, and a rank-two bilinear term. They resemble squared-distance matrices after double centering.

The obstruction is that Euclidean row terms must be of the form

∣u∣
2
+2z⋅u+constant,

a positive-definite quadratic function. Expressions such as ab are indefinite. They work naturally for a Minkowski quadratic form but not for a real Euclidean norm.

No transformation tested converted multiplication-table sparsity into a valid planar distance configuration.

7. Finite falsification results

An exhaustive search was made over all disjoint n-point subsets X,Y of the 4×4 integer grid. These are exact minima within that finite universe, not global planar minima:

n
minK
	​

2
1
	​

3
2
	​

4
2
	​

5
3
	​

6
3
	​

7
4
	​

8
4
	​

	​


The minimizers are checkerboard fragments. For example, at n=8, the two parity classes have squared cross-distances

{1,5,9,13}.

A heuristic search in the 5×5 grid found n=10, K=5, again using checkerboard fragments with squared distances

{1,5,9,13,17}.

The persistent small-scale pattern K≈n/2 is a boundary artifact; larger grids move toward the n/
logn
	​

 norm-counting scale.

Exact unrestricted finite-search pipeline

For fixed n,k, a complete continuous falsification procedure would be:

Enumerate k-colorings L=(ℓ
ij
	​

) of the n×n cross edges, modulo row, column, and color permutations.

Reject any pattern in which two rows contain an ordered color pair more than twice. Two circles with distinct centers have at most two intersection points.

Introduce distinct nonnegative variables s
1
	​

,…,s
k
	​

.

Set D
ij
	​

=s
ℓ
ij
	​

	​

.

Impose all 3×3 minors of the doubly centered D equal to zero.

Factor the centered matrix as −2UV
T
.

Impose the remaining Euclidean norm equations and all point-distinctness inequalities.

Apply exact real quantifier elimination.

This is finite for each n,k, but grows too rapidly to address the asymptotic question directly.

8. Precise remaining targets

Any one of the following would materially advance the planar problem.

Lower-bound target

Prove the universal energy estimate

E(X,Y)=O(n
3
logn
	​

).

It would imply

K=Ω(
logn
	​

n
	​

)

and negate the intended statement.

Structural target

Prove that whenever

K≪n,

the sets X,Y can be covered, after discarding o(n) points, by bounded-rank generalized arithmetic progressions or by O(K
2
/n)-scale families of rich parallel lines. One would then reduce the problem to norm values of positive-definite binary quadratic forms.

The bisector identity proves only the first weak step: both sets contain lines with approximately n/K points.

Constructive target

Produce X,Y with

∣X∣=∣Y∣=n

such that X−Y lies on

o(
logn
	​

n
	​

)

origin-centered circles. Necessarily, the average used circle must contain

ω(
logn
	​

)

distinct difference vectors and support

ω(n
logn
	​

)

ordered cross-pairs.

No tested line, circle, algebraic-curve, lattice, congruence, product, or finite-field family meets these requirements.

Rank-based construction target

Start from a combinatorial k-symbol matrix with

k=o(n/
logn
	​

)

and satisfy simultaneously:

rank(D
ij
	​

−D
i1
	​

−D
1j
	​

+D
11
	​

)≤2,

the Euclidean norm compatibility equations, and distinctness. Rank alone is insufficient; positive-definite compatibility is the unresolved barrier.

9. Status of the F=o(f) question

Under the intended distinct-point convention,

F
2
	​

(2n)≤f
2
	​

(2n),

because any 2n-point set may be partitioned into two n-point sets, and cross-distances form a subset of all distances.

However, the two questions are not logically equivalent from the supplied statement alone. To deduce F=o(f) from the first question would require a matching lower bound for f(2n); to deduce the first from F=o(f) would require a matching upper bound for f(2n). Neither comparison is supplied here.

Under the literal repetition-allowed interpretation, the definitions become inconsistent with the usual distinct-point meaning of f, reinforcing the initial statement-integrity defect.

Outcome

The exact wording is blocked by the missing distinctness convention.

Under the strongest intended interpretation, the R
3
 variant has an explicit O(n
2/3
) construction for every n.

For the planar variant, no proof or disproof was obtained.

Any successful planar construction must exhibit simultaneously:

ω(
logn
	​

)-rich lines in both sets,
ω(n
logn
	​

) average distance multiplicity,

and

ω(n
3
logn
	​

) equal-distance energy.

All fixed-complexity geometric families and all tested lattice, modular, tensor, and finite-field mechanisms fail to supply the required extra vanishing factor.
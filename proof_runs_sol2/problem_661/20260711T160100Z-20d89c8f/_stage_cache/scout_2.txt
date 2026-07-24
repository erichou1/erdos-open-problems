Scout status

No proof or disproof of the substantive planar interpretation was obtained. There is, however, a blocking statement-integrity defect, several rigorous reductions and lower bounds, a complete construction for the three-dimensional analogue, and a sharply identified arithmetic/geometric gap.

1. Blocking ambiguity in the immutable statement

The sentence does not say that the 2n indexed points are distinct.

Under the literal indexed-point reading, repetitions are permitted. Taking

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

=(1,0)

gives exactly one cross-distance, and

1=o(
logn
	​

n
	​

).

Under the conventional distinct-distance interpretation, one presumably requires all 2n points to be pairwise distinct. These are different mathematical propositions. Because the acceptance criteria require ambiguity to be treated as blocking, the intended nontrivial proposition cannot be extracted uniquely from the immutable wording.

There is a second, smaller formal defect: little-o is a property of a sequence, not of the points chosen at a single fixed n. The natural repaired formulation is

F
2
	​

(2n):=
∣X∣=∣Y∣=n
X∩Y=∅
	​

min
	​

	​

{∥x−y∥:x∈X, y∈Y}
	​


and the question becomes

F
2
	​

(2n)=o(
logn
	​

n
	​

).
(P)

All subsequent planar work is conditional on this pairwise-distinct formulation.

Counting squared distances instead of distances causes no change, because t↦
t
	​

 is injective on [0,∞).

2. Rigorous baseline constructions and obstructions
2.1 A universal linear construction

Let v
0
	​

,…,v
2n−1
	​

 be the vertices of a regular 2n-gon and put

X={v
2a
	​

:0≤a<n},Y={v
2b+1
	​

:0≤b<n}.

Every cross-chord has an odd cyclic step

s∈{1,3,5,…},1≤s≤n,

and its length is

2sin
2n
πs
	​

.

These values are distinct for 1≤s≤n, so

F
2
	​

(2n)≤⌈
2
n
	​

⌉.
(2.1)

This demonstrates that a linear lower bound with constant exceeding 1/2 is impossible. It remains far above the desired o(n/
logn
	​

).

2.2 Two-anchor lower bound

Let D be the global cross-distance set and K=∣D∣. Choose distinct x
1
	​

,x
2
	​

∈X.

Every y∈Y determines

(∥x
1
	​

−y∥,∥x
2
	​

−y∥)∈D
2
.

For any fixed pair (r,s), the corresponding y's lie in

C(x
1
	​

,r)∩C(x
2
	​

,s),

which has at most two points. Hence

n≤2K
2
,K≥
2
n
	​

	​

.
(2.2)

This is the simplest fully rigorous obstruction. It is much too weak at the target scale.

2.3 Line and circle concentration

If a line L contains m points of X, fix any y∈Y. For each r∈D, the circle C(y,r) meets L in at most two points. Therefore

m≤2K.
(2.3)

Similarly, if a circle Γ contains m points of X, choose y∈Y different from the center of Γ. Each C(y,r) meets Γ in at most two points, so again

m≤2K.
(2.4)

The same statements hold with X,Y interchanged.

Thus any hypothetical configuration satisfying (P) must have

L
max
	​

∣X∩L∣, 
Γ
max
	​

∣X∩Γ∣, 
L
max
	​

∣Y∩L∣, 
Γ
max
	​

∣Y∩Γ∣=o(
logn
	​

n
	​

).

In particular, line-based and single-circle constructions cannot work.

3. A self-contained Ω(n
2/3
) lower bound

This is the strongest rigorous general planar lower bound obtained in this attack.

3.1 Fixed-radius incidence lemma

Let P be a set of n points and let C consist of n distinct circles of the same positive radius. Then

I(P,C)=O(n
4/3
).
(3.1)
Proof

On every circle containing t≥2 points of P, join cyclically consecutive incident points by arcs of that circle. If t=2, use both complementary arcs.

Let E be the number of resulting arcs. Circles containing only one point contribute at most n incidences, so

E≥I(P,C)−n.
(3.2)

Two distinct equal-radius circles intersect at at most two points. Therefore the drawing has at most 2(
2
n
	​

)=O(n
2
) proper crossings.

The edge multiplicity between two vertices is at most four: there are at most two equal-radius circles through the pair, and a circle contributes two parallel arcs only when it has exactly those two incident points. Split the multigraph into four simple graphs. One layer has at least E/4 edges.

For completeness, a simple graph with v vertices and e≥4v edges satisfies

cr(G)≥
64v
2
e
3
	​

.
(3.3)

Indeed, sample every vertex independently with probability p=4v/e. The deterministic planar deletion inequality gives

cr(H)≥e(H)−3v(H)

for every sampled graph H. Taking expectations,

p
4
cr(G)≥p
2
e−3pv=
e
4v
2
	​

,

which yields (3.3).

Applying this to the largest simple layer, unless E=O(n), gives

O(n
2
)
E
3
	​

≤O(n
2
),

hence E=O(n
4/3
). Together with (3.2), this proves (3.1).

3.2 Application to the distance problem

For each positive r∈D, consider the n circles

C
r
	​

={C(x,r):x∈X}.

The number m
r
	​

 of cross-pairs at distance r is exactly the incidence count between Y and these circles. Hence

m
r
	​

=O(n
4/3
).

There are n
2
 cross-pairs altogether, so

n
2
=
r∈D
∑
	​

m
r
	​

≤O(Kn
4/3
).

Consequently

K=Ω(n
2/3
).
	​

(3.4)

This still leaves a factor of approximately

n
2/3
n/
logn
	​

	​

=
logn
	​

n
1/3
	​


between the proven lower bound and the scale relevant to (P).

4. Independent shell-counting obstruction

For x∈X and r∈D, write

m
x,r
	​

=∣{y∈Y:∥x−y∥=r}∣.

The number of triples of distinct Y-points lying on a common circle centered at x is

r∈D
∑
	​

(
3
m
x,r
	​

	​

).

Any three noncollinear Y-points have exactly one possible equidistant center, their circumcenter; three collinear points have none. Therefore

x∈X
∑
	​

r∈D
∑
	​

(
3
m
x,r
	​

	​

)≤(
3
n
	​

).
(4.1)

If n=qK+s, with 0≤s<K, convexity gives the exact lower estimate

r∈D
∑
	​

(
3
m
x,r
	​

	​

)≥(K−s)(
3
q
	​

)+s(
3
q+1
	​

).

Thus

n((K−s)(
3
q
	​

)+s(
3
q+1
	​

))≤(
3
n
	​

).
(4.2)

When K=o(n), this asymptotically yields only

K≥(1−o(1))
n
	​

.

This attack exhausts the information obtained from uniqueness of circumcenters. Using four or more concyclic points gives weaker exponents, not stronger ones.

5. The three-dimensional analogue

The three-dimensional version has a direct construction that is much stronger than the requested asymptotic.

Let

M=⌈(2n)
1/3
⌉.

The lattice cube

{0,1,…,M−1}
3

contains at least 2n distinct points. Choose any 2n of them and partition them into X,Y, each of size n.

Every squared cross-distance is a positive integer at most

3(M−1)
2
.

Therefore

∣D(X,Y)∣≤3(M−1)
2
=O(n
2/3
).

Since

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

⟶0,

the three-dimensional construction has

∣D(X,Y)∣=o(
logn
	​

n
	​

).
(5.1)

More generally, the same lattice argument in R
d
, d≥3, gives O(n
2/d
) cross-distances.

The planar dimension is exceptional because a two-dimensional box of 2n lattice points has squared-diameter O(n), not O(n
2/3
).

6. The planar lattice benchmark

Take even M and partition the M×M integer grid by checkerboard parity:

X={(a,b):0≤a,b<M, a+b≡0(mod2)},
Y={(a,b):0≤a,b<M, a+b≡1(mod2)}.

Then

∣X∣=∣Y∣=
2
M
2
	​

=n.

The squared cross-distance set is exactly

A
M
	​

={u
2
+v
2
:∣u∣,∣v∣≤M−1, u+v odd}.
(6.1)

Indeed, every cross-difference has odd coordinate-sum, and every vector in the indicated range with odd coordinate-sum is realized by two grid points of opposite parity.

Thus the lattice construction reduces the problem to estimating

A(M)=∣A
M
	​

∣.

The benchmark claim would be

A(M)=O(
logM
	​

M
2
	​

).
(6.2)

To obtain the requested little-o by this exact construction one would instead need

A(M)=o(
logM
	​

M
2
	​

),
(6.3)

which is a strictly stronger arithmetic assertion.

A basic invariant behind (6.2) is elementary. If

q=u
2
+v
2

and p≡3(mod4) is prime, then the exponent of p in q is even. For if p∣u
2
+v
2
 and p∤v, then (uv
−1
)
2
≡−1(modp), impossible for p≡3(mod4). Hence p∣u,v, and iteration gives even valuation.

For any finite collection P of such primes, the Chinese remainder theorem gives the explicit sieve bound

A(M)≤2M
2
p∈P
∏
	​

(1−
p
1
	​

+
p
2
1
	​

)+
p∈P
∏
	​

p
2
.
(6.4)

Obtaining the precise 
logM
	​

 saving uniformly requires additional quantitative control over the selected primes. That obligation has not been proved here.

Failure of extreme rectangular skewing

Consider an a×b rectangular grid, a≤b. Its squared distances include

u
2
+v
2
,0≤u<a,0≤v<b.

For v≥a
2
, the intervals

[v
2
,v
2
+(a−1)
2
]

for consecutive v's are disjoint. Hence, if b≥2a
2
, there are at least

a(b−a
2
)≥
2
ab
	​


distinct squared distances. The analogous checkerboard partition still gives a linear lower bound, up to constants.

Therefore making the grid extremely thin cannot produce the required saving. Any useful lattice candidate must remain in the balanced or moderately skewed regime.

7. Algebraic reformulations

Let S be the set of squared cross-distances, ∣S∣=K. The condition is

∥x∥
2
+∥y∥
2
−2x⋅y∈S(x∈X, y∈Y).
(7.1)

Define the lifts

Φ(x)=(x
1
	​

,x
2
	​

,∥x∥
2
,1),
Ψ(y)=(−2y
1
	​

,−2y
2
	​

,1,∥y∥
2
).

Then

Φ(x)⋅Ψ(y)=∥x−y∥
2
.
(7.2)

Thus the planar question is equivalent to finding two n-point subsets of two constrained quadratic surfaces in R
4
 whose n
2
 cross inner products use only

o(
logn
	​

n
	​

)

values.

This is not merely a low-rank matrix problem. The squared-distance matrix has rank at most four, but arbitrary rank-four matrices need not arise from the two linked paraboloid constraints in (7.2). Conversely, the ordinary planar grid already gives a rank-four matrix with an arithmetic saving of approximately the relevant logarithmic size, so rank alone is too coarse.

An equivalent circle formulation is

Y⊆
x∈X
⋂
	​

s∈S
⋃
	​

C(x,
s
	​

),
(7.3)

and symmetrically for X. For two fixed centers, the right-hand side has at most 2K
2
 candidate points, reproducing (2.2). The unresolved issue is whether n additional centers can simultaneously retain n candidates when K is below the grid scale.

8. Minimal-counterexample and extremal information

Under the repaired definition, F
2
	​

(2n) is nondecreasing:

F
2
	​

(2n)≤F
2
	​

(2n+2),
(8.1)

because one may delete one point from each side.

Consequently, a construction only at sizes N
t
	​

 with

N
t
	​

N
t+1
	​

	​

→1

would suffice for all large n: take the next larger construction and delete points. This is important for constructions naturally available only at squares or other special sizes.

For each r∈D, let G
r
	​

 be the bipartite graph of pairs at distance r, with m
r
	​

 edges. Then

r∈D
∑
	​

m
r
	​

=n
2
.

Under the desired hypothesis K=o(n/
logn
	​

),

K
1
	​

r
∑
	​

m
r
	​

=
K
n
2
	​

=ω(n
logn
	​

).
(8.2)

Thus a typical distance would have substantially more than n
logn
	​

 realizations.

However, the incidence argument permits

m
r
	​

=O(n
4/3
),

and

n
logn
	​

≪n
4/3
.

Hence no contradiction arises: the average multiplicity required by the conjectural construction lies well below the strongest per-distance geometric upper bound established here.

A deletion-based induction also stalls. A distance class with more than 2n−1 edges cannot disappear after deleting one x-vertex and one y-vertex, because those two stars cover at most 2n−1 edges. Under (8.2), most pair-incidences lie in such robust classes, but this does not control how many distinct sparse classes are lost, so it does not close an induction.

9. Small-n falsification tests

Assume all 2n points are distinct.

For n=1, one distance is unavoidable and sufficient.

For n=2, one distance is possible: take the two parts to be opposite bipartition classes of a square.

For n≥3, one distance is impossible. If all cross-distances were r, then after choosing distinct x
1
	​

,x
2
	​

, all points of Y would lie in

C(x
1
	​

,r)∩C(x
2
	​

,r),

which contains at most two points.

Therefore:

F
2
	​

(6)=2

using the alternating regular hexagon, and

F
2
	​

(8)=2

using the alternating regular octagon.

The first small case not settled by these arguments is n=5:

2≤F
2
	​

(10)≤3.

A classification of planar bipartite two-distance configurations would decide whether five points per side are possible.

I also performed exact finite enumeration inside small integer-grid hosts. The minimum values within those restricted hosts were:

n
2
3
4
5
6
8
	​

host grid
2×2
3×2
3×3
4×3
4×3
4×4
	​

minimum cross-distance count
1
2
2
3
4
4
	​

	​


These are not universal minima. In particular, the regular 12-gon gives 3 distances for n=6, whereas the exhaustive 4×3 grid search gave 4. This explicitly falsifies the idea that small integer-grid searches reliably identify global extremizers.

10. Relation between F and f

Under pairwise distinctness, let f(2n) be the minimum number of all pairwise distances among 2n planar points. Taking an extremal 2n-point set and partitioning it arbitrarily into two n-point classes gives

F
2
	​

(2n)≤f(2n).
(10.1)

But the two asymptotic questions are not logically equivalent without additional estimates.

The implication

F
2
	​

(2n)=o(
logn
	​

n
	​

)⟹F
2
	​

(2n)=o(f(2n))

would require a lower bound

f(2n)=Ω(
logn
	​

n
	​

).

Conversely,

F
2
	​

(2n)=o(f(2n))⟹F
2
	​

(2n)=o(
logn
	​

n
	​

)

would require an upper bound

f(2n)=O(
logn
	​

n
	​

).

Thus a proof that

f(2n)=Θ(
logn
	​

n
	​

)

would make the two formulations equivalent, but that estimate has not been derived from the supplied material.

11. Failed attacks and what they establish

Parallel lines. If X,Y lie on parallel lines with coordinate sets A,B⊂R, the distances determine ∣a−b∣. Since ∣A−B∣≥2n−1, identifying t with −t still leaves at least n values. This route is necessarily linear.

Orthogonal axes. Squared distances become a
2
+b
2
, a sumset of two n-element nonnegative sets unless signs create only a factor-two collapse. Again the elementary sumset lower bound is linear.

Single-circle symmetry. Unless one side consists solely of a circle center, every distance circle intersects the supporting circle in at most two points, forcing at least n/2 distances. The regular polygon attains this scale.

Triple and higher shell energies. Uniqueness of a circumcenter yields only 
n
	​

. Counting larger concyclic subsets gives weaker powers.

Per-distance incidence bounds. The crossing argument reaches n
2/3
, but summing individual distance-class bounds discards interactions between different radii. An improvement must exploit those interactions.

Polynomial vanishing. The polynomial

s∈S
∏
	​

(∥z−x∥
2
−s)

has degree 2K and vanishes on Y. The dimension of planar polynomials of that degree is O(K
2
), so this becomes restrictive only around K≲
n
	​

, far below the target n/
logn
	​

.

Anisotropic lattices. Extreme skewing produces essentially disjoint value intervals and therefore linearly many distances. Balanced positive-definite quadratic forms remain the only plausible lattice regime.

Local congruence engineering. Forcing all differences into a sublattice introduces fixed divisibility, but scaling removes fixed common factors. Degenerate congruence restrictions generally enlarge the coordinate box enough to offset their density saving. No net asymptotic improvement was obtained.

Fractal or digit products. Hierarchical sums in the plane introduce cross terms between scales. Exact distance equalities do not tensorize as they would in mutually orthogonal subspaces of higher dimension.

Projection of higher-dimensional constructions. A linear map R
3
→R
2
 cannot preserve the three-dimensional squared norm on a spanning set of difference vectors. Generic projections destroy the required exact collisions.

12. Precise remaining targets

The main planar problem is reduced to one of the following genuinely missing advances.

Lower-bound route

Prove a restricted rank-four/paraboloid alphabet theorem:

∣{Φ(x)⋅Ψ(y):x∈X, y∈Y}∣≥c
logn
	​

n
	​


for all pairwise-distinct X,Y⊂R
2
, ∣X∣=∣Y∣=n.

A weaker next step would be any improvement

F
2
	​

(2n)=Ω(n
2/3+ε
)

for fixed ε>0, necessarily using interactions among several distance classes rather than treating each radius independently.

Construction route

Produce S
n
	​

⊂[0,∞) and pairwise-distinct X
n
	​

,Y
n
	​

⊂R
2
 such that

∣X
n
	​

∣=∣Y
n
	​

∣=n,∥x−y∥
2
∈S
n
	​


for every x∈X
n
	​

,y∈Y
n
	​

, with

∣S
n
	​

∣=o(
logn
	​

n
	​

).

Within lattice constructions, the precise target is a sequence of positive-definite binary quadratic forms Q
n
	​

 and balanced difference boxes containing n points for which

∣{Q
n
	​

(u,v):(u,v) in the difference box}∣=o(
logn
	​

n
	​

).

No such form or nonlattice mechanism emerged.

Finite structural target

Classify bipartite two-distance configurations in the plane and decide whether n=5 per side is possible. This is the smallest unresolved finite test exposed by the analysis.

The current rigorous planar interval is therefore

Ω(n
2/3
) ≤ F
2
	​

(2n) ≤ ⌈
2
n
	​

⌉,
	​


with the checkerboard lattice isolating the n/
logn
	​

 arithmetic benchmark but not establishing a little-o improvement.
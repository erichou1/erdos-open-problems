I treated the uploaded text as the operative statement, workflow, and untrusted search material. The citation identifies that source only; none of the mathematical conclusions below relies on it as authority. 

Pasted text

1. Exact normalization

Let

Δ(X,Y):={∥x−y∥:x∈X, y∈Y},K(X,Y):=∣Δ(X,Y)∣

and

g(n):=
logn
	​

n
	​

.

The wording permits three inequivalent conventions.

Repetitions allowed: the indexed tuples x
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

 may repeat.

Internal distinctness: X={x
1
	​

,…,x
n
	​

} and Y={y
1
	​

,…,y
n
	​

} each have size n, but X∩Y may be nonempty.

Pairwise distinctness: ∣X∣=∣Y∣=n and X∩Y=∅, so all 2n points are distinct.

The comparison with f(2n) strongly motivates convention 3, but it does not formally impose it.

For a fixed convention C, define

F
C
	​

(n):=
X,Y⊆R
2
∣X∣=∣Y∣=n
C
	​

min
	​

K(X,Y).

Because K is an integer between 1 and n
2
, this minimum exists.

The precise asymptotic assertion is

F
C
	​

(n)=o(g(n)),

equivalently

∀ε>0 ∃N ∀n≥N ∃X,Y satisfying C:K(X,Y)≤ε
logn
	​

n
	​

.

Its negation is

∃ε>0 ∀N ∃n≥N:F
C
	​

(n)≥ε
logn
	​

n
	​

.

The main semantic fork is blocking: convention 1 is trivial, whereas conventions 2 and 3 remain substantive.

2. Attack portfolio
Branch	Required lemma or construction	Fastest falsification test	Principal failure mode
Literal tuple reading	A constant-distance repeated-point configuration	Check that the distance set is nonempty and constant for every n	Does not address either distinctness convention
Higher-dimensional grid	Fit 2n points in a lattice box whose squared-diameter has o(g(n)) integer values	Verify the exponent 2/d<1	In dimension 2, the squared-diameter is already Θ(n)
Fixed-radius incidence	Uniform O(n
4/3
) bound for one distance class	Test zero distance and coincident circles	Gives only K=Ω(n
2/3
)
Bisector and shell energy	Bound all distance classes jointly	Correct every threshold to 
logn
	​

	Crude line-incidence estimates lose too much
Binary quadratic forms	Find forms whose values on balanced difference boxes have an extra vanishing factor	Count exact values for small boxes; vary discriminant and translation	Fixed forms appear to give only the benchmark logarithmic compression
Algebraic high-rank modules	Compress a high-dimensional coefficient box via z
z
ˉ
	Expand norms in a field basis and count coefficient ranges	Dimension counting remains linear unless arithmetic fibers are exceptionally large
Few-symbol distance matrices	Construct a K-symbol matrix with centered rank at most 2 and full Euclidean compatibility	Reject using two-row multiplicities and centered minors	Low rank is necessary but far from sufficient
Polynomial annihilation	Use ∏
s∈S
	​

(∥z−x∥
2
−s) simultaneously for many centers	Put Y on a curve component	A single polynomial may vanish on arbitrarily many structured points
Recursive digit products	Tensor smaller constructions at separated scales	Expand the exact squared distance	The mixed inner-product term destroys exact tensorization in R
2

F versus f	Relate cross-distances to all distances	Check both directions of implication	Requires separate upper or lower information about f
3. Verified claims
C1. Semantic trichotomy

Statement. The three conventions above define genuinely different problems.

Dependencies. None.

Justification. Convention 1 permits repeated indices. Convention 2 forbids repetitions within each list but permits x
i
	​

=y
j
	​

. Convention 3 additionally forbids overlap. Every convention-3 configuration is allowed under convention 2, and every convention-2 configuration is allowed under convention 1, but the converses fail.

C2. Correct quantifier formulation

Statement. Under any fixed convention C, the original asymptotic question is naturally formalized as

F
C
	​

(n)=o(
logn
	​

n
	​

).

Dependencies. C1.

Justification. Minimizing over the allowed configurations absorbs the innermost existential quantifier. The definition of little-o gives the displayed ε,N,n formulation.

C3. Literal repetition-allowed version is affirmative

Statement. Under convention 1,

F
rep
	​

(n)=1

for every n.

Dependencies. C1–C2.

Justification. Set

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

Every cross-distance is 1, so K=1. A distance set cannot be empty because there are n
2
 cross-pairs. Hence the minimum is exactly 1. Moreover

g(n)
1
	​

=
n
logn
	​

	​

⟶0.
C4. Squared distances are equivalent

Statement. Replacing ∥x−y∥ by ∥x−y∥
2
 does not change the number of distinct cross-distances.

Dependencies. None.

Justification. The map t↦t
2
 is injective on [0,∞).

Henceforth distances may be squared without comment.

C5. Monotonicity and all-n interpolation

Statement. Under either distinctness convention,

F(n)≤F(n+1).

Furthermore, suppose configurations exist at sizes

N
1
	​

<N
2
	​

<⋯

such that

K
t
	​

=o(
logN
t
	​

	​

N
t
	​

	​

)

and

t
sup
	​

N
t
	​

N
t+1
	​

	​

<∞.

Then configurations with the same little-o estimate exist for every sufficiently large n.

Dependencies. C2.

Justification. Delete one point from each side of an (n+1,n+1)-configuration; deletion cannot introduce distances.

For N
t−1
	​

<n≤N
t
	​

, delete points from the size-N
t
	​

 construction. If N
t
	​

/n≤C, then

n/
logn
	​

K
t
	​

	​

=
N
t
	​

/
logN
t
	​

	​

K
t
	​

	​

⋅
n
N
t
	​

	​

logN
t
	​

logn
	​

	​

=o(1).

A bounded subsequence ratio is sufficient; convergence of the ratio to 1 is unnecessary.

C6. The one-dimensional pairwise-distinct problem is exact

Statement. For disjoint n-point sets A,B⊂R, at least n absolute cross-differences occur, and this is attainable.

Dependencies. None.

Justification. Write

a
1
	​

<⋯<a
n
	​

,b
1
	​

<⋯<b
n
	​

.

The chain

a
1
	​

−b
n
	​

<a
2
	​

−b
n
	​

<⋯<a
n
	​

−b
n
	​

<a
n
	​

−b
n−1
	​

<⋯<a
n
	​

−b
1
	​


contains 2n−1 distinct signed differences. Since A∩B=∅, zero is absent, and passing from t to ∣t∣ is at most two-to-one. Thus there are at least

⌈
2
2n−1
	​

⌉=n

absolute distances.

Equality is attained by

A={0,2,…,2n−2},B={1,3,…,2n−1},

whose cross-distances are 1,3,…,2n−1.

C7. The same numerical question in R
3
 is affirmative

Statement. For every n, there are 2n pairwise-distinct points in R
3
, divided into two n-point sets, with

K=O(n
2/3
)=o(
logn
	​

n
	​

).

Dependencies. C4.

Justification. Let

m=⌈(2n)
1/3
⌉.

The lattice cube

{0,1,…,m−1}
3

contains at least 2n points. Select any 2n distinct points and partition them into X,Y of size n.

Every squared cross-distance is a positive integer no larger than

3(m−1)
2
.

Therefore

K≤3(m−1)
2
=O(n
2/3
).

Finally,

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

More generally, the same argument gives O(n
2/d
) distances in R
d
, so every d≥3 satisfies this numerical target.

C8. A universal linear planar construction

Statement. For n≥2, under pairwise distinctness,

F
dis
	​

(n)≤⌈
2
n
	​

⌉.

Dependencies. C4.

Justification. Take the vertices v
0
	​

,…,v
2n−1
	​

 of a regular 2n-gon and put

X={v
2a
	​

:0≤a<n},Y={v
2b+1
	​

:0≤b<n}.

A cross-chord has an odd cyclic separation. Its length depends only on the smaller separation

k∈{1,3,5,…},k≤n.

There are exactly ⌈n/2⌉ such values, and chord length is strictly increasing for separations from 1 through n.

For n=2, this is the square construction with one cross-distance.

C9. Two-anchor lower bound

Statement. If each side contains n distinct points, then

K≥
2
n
	​

	​

.

Dependencies. C4.

Justification. Choose distinct x,x
′
∈X. Every y∈Y determines

(∥y−x∥
2
,∥y−x
′
∥
2
)∈S
2
,

where S is the squared cross-distance set and ∣S∣=K.

For prescribed s,t, the point y lies in the intersection of the two circles

∥z−x∥
2
=s,∥z−x
′
∥
2
=t.

Circles with distinct centers have at most two common points, including the degenerate radius-zero cases. Hence

n≤2K
2
.

In particular, K=1 is impossible for n≥3.

C10. Fixed-radius incidence lemma

Statement. Let P be n points and let C be n distinct circles of one fixed positive radius. Then

I(P,C)=O(n
4/3
).

Dependencies. The elementary planar inequality e≤3v−6 for simple planar graphs with v≥3, proved from Euler’s formula below.

Justification.

For every circle containing t≥2 points of P, join cyclically consecutive incident points by arcs of that circle. If t=2, use both complementary arcs. Circles containing exactly one point contribute at most n incidences altogether.

Let E be the number of arcs. Then

E≥I(P,C)−n.

Between two vertices there are at most four arcs: at most two fixed-radius circles pass through the two vertices, and each such circle contributes at most two arcs. Partition the arcs into four simple graph layers, so one layer has at least E/4 edges.

Two distinct circles meet at at most two points. After harmless local perturbation at multiple intersections, the inherited drawing of each layer has fewer than n
2
 proper crossings.

It remains to prove the crossing estimate. For a simple graph with v vertices and e≥4v edges, consider a good drawing and retain each vertex independently with probability

p=
e
4v
	​

.

Any drawn simple graph satisfies

cr(H)≥e(H)−3v(H),

because deleting at most one edge per crossing leaves a planar simple graph, which has at most 3v(H)−6 edges. Taking expectations,

p
4
cr(G)≥p
2
e−3pv=
e
4v
2
	​

.

Thus

cr(G)≥
64v
2
e
3
	​

.

Apply this to the largest layer. If E/4<4n, then E=O(n). Otherwise,

64n
2
(E/4)
3
	​

≤n
2
,

and hence E=O(n
4/3
). Therefore

I(P,C)≤E+n=O(n
4/3
).
C11. Universal planar lower bound

Statement. Under pairwise distinctness,

F
dis
	​

(n)=Ω(n
2/3
).

The same asymptotic lower bound holds under internal distinctness with overlap allowed.

Dependencies. C10.

Justification. For each positive distance r, let e
r
	​

 be the number of ordered cross-pairs (x,y) satisfying ∥x−y∥=r. The n radius-r circles centered at X are distinct, so C10 gives

e
r
	​

=O(n
4/3
).

If X∩Y=∅, all n
2
 cross-pairs have positive distance:

n
2
=
r∈Δ(X,Y)
∑
	​

e
r
	​

≤CKn
4/3
.

Thus

K≥cn
2/3
.

If each list is internally distinct but X∩Y

=∅, there are at most n zero-distance pairs. Hence at least n
2
−n positive pairs remain, yielding the same asymptotic conclusion.

C12. Line and circle concentration obstruction

Statement. If a line contains k points of one side, then

K≥
2
k
	​

.

If a circle contains k points of one side and the opposite side has at least two distinct points, the same bound holds.

Dependencies. None.

Justification. Fix y in the opposite side. Each of the K circles centered at y meets a fixed line in at most two points, so k≤2K.

For a supporting circle Γ, choose y different from its center. Each distance circle centered at y meets Γ in at most two points, because the two circles are distinct. Again k≤2K.

Thus constructions supported on a bounded number of lines or circles cannot approach the target.

C13. Difference-vector lower bound

Statement. For n-point sets X,Y⊂R
2
,

∣X−Y∣≥2n−1.

Dependencies. The one-dimensional signed-difference argument in C6.

Justification. Choose a linear functional ϕ:R
2
→R that is injective on X and separately injective on Y; a generic functional avoids finitely many forbidden directions. Then

∣ϕ(X)−ϕ(Y)∣≥2n−1

by the ordered-chain argument. Since

ϕ(X)−ϕ(Y)=ϕ(X−Y),

projection cannot increase cardinality, and therefore

∣X−Y∣≥∣ϕ(X−Y)∣≥2n−1.

Consequently, if X−Y lies on K origin-centered circles, some occupied circle contains at least

K
2n−1
	​


distinct difference vectors.

C14. Exact checkerboard-lattice reduction

Statement. Let q be even, and partition the q×q integer grid into parity classes

X={(a,b):0≤a,b<q, a+b≡0(mod2)},
Y={(a,b):0≤a,b<q, a+b≡1(mod2)}.

Then ∣X∣=∣Y∣=q
2
/2, and the squared cross-distance set is exactly

{u
2
+v
2
:∣u∣,∣v∣≤q−1, u+v odd}.

Dependencies. C4.

Justification. Every cross-difference (u,v) has u+v odd and lies in the stated coordinate range.

Conversely, every pair (u,v) in that range is realizable as the difference of two grid points: choose coordinate pairs realizing u and v separately. Since u+v is odd, the endpoints have opposite parity.

This is an exact arithmetic reduction. No asymptotic estimate for the number of represented values is imported here.

Small exact checks:

q=2: the value set is {1}.

q=4: the value set is {1,5,9,13}.

These checks support the reduction but do not determine its asymptotic order.

C15. Correct threshold ledger

Statement. Suppose

K=o(
logn
	​

n
	​

).

Then all of the following hold:

K
n
2
	​

=ω(n
logn
	​

),
K
n
	​

=ω(
logn
	​

),
T(X,Y)=ω(n
2
logn
	​

),

and

E(X,Y)=ω(n
3
logn
	​

),

for the isosceles and equal-distance energies defined below.

Dependencies. C2.

Justification. The first two statements are algebraic rearrangements of

K
logn
	​

/n→0.

For x∈X and a squared distance s, define

m
x
	​

(s):=
	​

{y∈Y:∥x−y∥
2
=s}
	​

.

Then

s
∑
	​

m
x
	​

(s)=n.

Since at most K terms are nonzero,

s
max
	​

m
x
	​

(s)≥
K
n
	​

=ω(
logn
	​

)

for every x.

Define the unordered isosceles-triple count

T(X,Y):=
x∈X
∑
	​

s
∑
	​

(
2
m
x
	​

(s)
	​

).

By Cauchy–Schwarz,

s
∑
	​

m
x
	​

(s)
2
≥
K
n
2
	​

.

Therefore

T(X,Y)=
2
1
	​

x
∑
	​

(
s
∑
	​

m
x
	​

(s)
2
−n)≥
2
1
	​

(
K
n
3
	​

−n
2
)=ω(n
2
logn
	​

).

For each squared distance s, let

e
s
	​

:=∣{(x,y)∈X×Y:∥x−y∥
2
=s}∣.

Define

E(X,Y):=
s
∑
	​

e
s
2
	​

.

Since ∑
s
	​

e
s
	​

=n
2
, another application of Cauchy–Schwarz gives

E(X,Y)≥
K
n
4
	​

=ω(n
3
logn
	​

).

All occurrences of logn, rather than 
logn
	​

, in these necessary thresholds would be incorrect.

C16. Exact perpendicular-bisector identity

Statement.

T(X,Y)=
{y,y
′
}⊂Y
∑
	​

∣X∩Bis(y,y
′
)∣,

where Bis(y,y
′
) is the perpendicular bisector of yy
′
.

Dependencies. C15 and internal distinctness of Y.

Justification. A contribution to T(X,Y) is exactly a choice of

x∈X,y

=y
′
∈Y

such that

∥x−y∥=∥x−y
′
∥.

For distinct y,y
′
, this equality holds exactly when x lies on their perpendicular bisector. Both sides count the same triples.

C17. Rich lines are necessary

Statement. Under the target estimate, both X and Y must contain

ω(
logn
	​

)

collinear points.

Dependencies. C15–C16.

Justification. Let

L(X):=
ℓ
max
	​

∣X∩ℓ∣.

By C16,

T(X,Y)≤(
2
n
	​

)L(X).

Since C15 gives

T(X,Y)=ω(n
2
logn
	​

),

it follows that

L(X)=ω(
logn
	​

).

Interchanging X and Y gives the same conclusion for Y.

This is necessary but not contradictory: ω(
logn
	​

) is still far below n/
logn
	​

.

C18. Two sufficient negative targets

Statement. Either universal estimate

T(X,Y)=O(n
2
logn
	​

)

or

E(X,Y)=O(n
3
logn
	​

)

would disprove the pairwise-distinct planar assertion.

Dependencies. C15.

Justification. Each bound contradicts the corresponding ω-estimate forced by the desired construction.

Equivalently, the energy bound would give directly

K
n
4
	​

≤Cn
3
logn
	​

,K≥c
logn
	​

n
	​

.

No such universal bound is established here.

C19. Exact matrix constraints

Statement. Let

D
ij
	​

:=∥x
i
	​

−y
j
	​

∥
2
.

Then

rank
R
	​

D≤4.

Moreover, the doubly centered matrix

C
ij
	​

:=D
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


has

rank
R
	​

C≤2.

Dependencies. C4.

Justification. Let U,V be the n×2 coordinate matrices and set

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
.

Then

D=a1
T
+1b
T
−2UV
T
,

whose rank is at most 1+1+2=4.

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


gives

C
ij
	​

=−2u
i
	​

⋅v
j
	​

,

so C=−2U
′
V
′T
 has rank at most 2.

These conditions are not sufficient. For example, the all-ones matrix has rank 1 and centered rank 0, but for n≥3 it would require every cross-distance to be equal, contradicting C9.

A complete matrix construction must additionally solve

D
ij
	​

=∥z+u
i
	​

−v
j
	​

∥
2

for a common z∈R
2
, with all required point-distinctness inequalities.

C20. Obstruction to rational-Gram high-rank projections

Statement. Let v
1
	​

,…,v
r
	​

∈R
2
, with r≥3. Suppose there is a nonzero real λ such that

v
i
	​

⋅v
j
	​

∈λQ

for every i,j. Then the v
i
	​

 satisfy a nontrivial integer linear relation. Consequently, the coefficient-box map

(a
1
	​

,…,a
r
	​

)⟼
i
∑
	​

a
i
	​

v
i
	​


cannot be injective on all sufficiently large integer boxes.

Dependencies. None.

Justification. The Gram matrix G=(v
i
	​

⋅v
j
	​

) has rank at most 2. The rational matrix G/λ therefore has a nonzero vector q∈Q
r
 in its kernel. Then

0=q
T
Gq=
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
,

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

Clearing denominators gives a nonzero h∈Z
r
 with

i
∑
	​

h
i
	​

v
i
	​

=0.

For every sufficiently large L, choose a
i
	​

=max(0,−h
i
	​

). Then both a and a+h lie in {0,…,L−1}
r
, yet have the same image.

Thus one cannot inject a high-dimensional lattice box into the plane while keeping all Gram coefficients in a single rational scale. Irrational Gram coefficients may restore injectivity, but they typically split norm equality into several coefficient equations.

C21. Relation between F and f

Statement. Under pairwise distinctness, let f(2n) be the minimum number of all nonzero distances among 2n planar points. Then

F
dis
	​

(n)≤f(2n).

The assertions

F
dis
	​

(n)=o(g(n))andF
dis
	​

(n)=o(f(2n))

are not formally equivalent without further estimates on f.

Dependencies. C1–C2.

Justification. Take a 2n-point configuration attaining f(2n) and partition it into two n-point sets. Every cross-distance is among the full set of distances, proving the inequality.

For the implications:

If f(2n)=Ω(g(n)), then F=o(g) implies F=o(f).

If f(2n)=O(g(n)), then F=o(f) implies F=o(g).

Neither comparison for f has been derived here, so the two questions remain logically separate.

4. Falsification and boundary audit
Minimal cases

Under pairwise distinctness:

F
dis
	​

(1)=1.

For n=2, the opposite bipartition classes of a square give

F
dis
	​

(2)=1.

For n≥3, K=1 is impossible by C9.

The alternating regular hexagon and octagon give

F
dis
	​

(3)≤2,F
dis
	​

(4)≤2.

Since K=1 is impossible, both values equal 2.

These examples test the sharpness of the two-anchor argument at the smallest scale.

Zero-distance audit

The fixed-radius incidence argument applies only to positive radii. Under pairwise distinctness there are no zero cross-distances. Under internal distinctness with overlap, there are at most n zero-distance pairs, so removing them does not alter C11.

Reversed-quantifier audit

A finite counterexample at one n cannot disprove an eventual-existence statement. To negate the asymptotic assertion, one must find a fixed ε>0 and infinitely many n satisfying

F(n)≥εg(n).

Conversely, constructions on an arbitrarily sparse subsequence do not automatically prove the all-large-n assertion. C5 records the sufficient bounded-ratio condition.

Threshold audit

The target is n/
logn
	​

. Therefore:

average distance multiplicity=
K
n
2
	​

=ω(n
logn
	​

),

not ω(nlogn);

largest shell around every center≥
K
n
	​

=ω(
logn
	​

),

not ω(logn);

T=ω(n
2
logn
	​

),E=ω(n
3
logn
	​

).

No later argument uses the incorrect stronger thresholds.

5. Surviving construction branches
5.1 Variable binary quadratic forms

A planar lattice with basis v
1
	​

,v
2
	​

 produces squared differences

Q(u,v)=au
2
+buv+cv
2
,b
2
<4ac.

A successful variable-form construction would require forms Q
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

),

while the corresponding point patch has Θ(m
2
) distinct points.

This is an exact finite target. It survives the general lower bounds, but no mechanism was found that gives the required vanishing factor. Increasing coefficient sizes enlarges the numerical range, while degenerating the form pushes the construction toward line-like behavior covered by C12.

Rational translations replace Q(u,v) by shifted quadratic expressions. They may remove congruence classes and improve constants, but no self-contained argument here shows a vanishing asymptotic improvement.

5.2 High-rank algebraic modules

Let K⊂C be a finite-dimensional Q-vector space stable under conjugation, and let

B
L
	​

={
i=1
∑
r
	​

a
i
	​

β
i
	​

:0≤a
i
	​

<L}.

If the β
i
	​

 are Q-independent, then ∣B
L
	​

∣=L
r
. Cross squared distances between B
L
	​

 and a translate are values of

z
z
ˉ
.

Pure coefficient counting gives at best O(L
r
) values, comparable with the number of points. To meet the target, one needs genuinely large fibers of z↦z
z
ˉ
, uniformly in a family whose dimension may increase.

The exact unresolved estimate is of the form

∣{z
z
ˉ
:z∈B
L
	​

−B
L
	​

−τ}∣≤C
r
	​

logL
	​

L
r
	​


with constants satisfying enough decay in r to overcome

log∣B
L
	​

∣
	​

=
rlogL
	​

.

C20 shows that simply forcing all Gram data into one rational coefficient does not work: that destroys injectivity in high rank.

5.3 Few-symbol Euclidean matrices

One may enumerate K-symbol n×n matrices and seek positive symbol values satisfying:

rankC≤2,

all two-row and two-column multiplicity restrictions from circle intersections, and

D
ij
	​

=∥z+u
i
	​

−v
j
	​

∥
2
.

This is a finite exact decision problem for each n,K, after quotienting by row, column, and symbol permutations. It can discover nonlattice configurations, but finite searches cannot decide the all-large-n quantifier.

Rank alone is decisively inadequate by C19.

5.4 Recursive constructions

Replacing every point a by a small copy a+εb gives

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

Exact tensorization requires the mixed term to vanish for all relevant differences. That means the two difference spans are orthogonal. In R
2
, this permits at most two nontrivial one-dimensional factors, recovering Cartesian-grid behavior rather than a many-level product. Making ε small does not help because only exact equality matters.

6. Surviving negative branches
6.1 Multi-radius bisector structure

The fixed-radius argument treats each distance separately and stops at n
2/3
. A threshold-level negative argument must use that all radii arise from the same coordinates.

The exact identity

T(X,Y)=
{y,y
′
}⊂Y
∑
	​

∣X∩Bis(y,y
′
)∣

shows that a hypothetical construction forces many pairs of Y-points to have perpendicular bisectors rich in X, and symmetrically.

The missing theorem would have to distinguish between:

ordinary rich lines containing points accidentally, and

lines that are simultaneously strong partial reflection axes of the opposite set.

A bound of order

T(X,Y)=O(n
2
logn
	​

)

would settle the pairwise-distinct question negatively, but no such estimate was obtained.

6.2 Radial-support and energy bounds

The energy

E=
s
∑
	​

e
s
2
	​


forgets how many distinct difference vectors occupy each radius and how multiplicities are distributed among those vectors.

A universal estimate

E=O(n
3
logn
	​

)

would suffice, but a pure second-moment argument may be too coarse. A stronger multiscale theorem could instead control how many radii carry multiplicities above each dyadic threshold.

The exact needed type of statement is:

For every pair X,Y of n distinct planar points, the radial multiplicity distribution of X−Y cannot simultaneously have support o(n/
logn
	​

) and total mass n
2
.

No proof of such a statement was found.

6.3 Polynomial method

For each x∈X, the polynomial

P
x
	​

(z)=
s∈S
∏
	​

(∥z−x∥
2
−s)

has degree 2K and vanishes on all of Y.

This is exact, but a single polynomial of small degree can vanish on arbitrarily many points lying on its curve. Combining the n translated polynomials is necessary, and their common algebraic structure has not been converted into a threshold-level bound.

7. Dependency ledger
Claim
C1
C2
C3
C4
C5
C6
C7
C8
C9
C10
C11
C12
C13
C14
C15
C16
C17
C18
C19
C20
C21
	​

Dependencies
None
C1
C1,C2
None
C2
None
C4
C4
C4
Euler planar-edge inequality, proved in C10
C10
None
C6
C4
C2
C15
C15,C16
C15
C4
None
C1,C2
	​

	​


No numbered claim relies on an unchecked arithmetic counting theorem or an external incidence theorem.

8. Open-gap ledger
G1. Pairwise-distinct planar construction or obstruction

Resolve one of the mutually exclusive propositions:

∃X
n
	​

,Y
n
	​

⊂R
2
,∣X
n
	​

∣=∣Y
n
	​

∣=n,X
n
	​

∩Y
n
	​

=∅,

with

K(X
n
	​

,Y
n
	​

)=o(
logn
	​

n
	​

),

or

∃c>0 and infinitely many, preferably all large, nF
dis
	​

(n)≥c
logn
	​

n
	​

.

Attacks attempted: fixed-radius incidences, bisector energy, equal-distance energy, lattice norms, translated lattices, few-symbol matrices, high-rank algebraic modules, polynomial annihilation, and recursive products.

None closes the gap.

G2. Internal-distinctness overlap convention

Determine whether allowing X∩Y

=∅, while requiring ∣X∣=∣Y∣=n, changes the asymptotic answer. The universal Ω(n
2/3
) lower bound survives, but no reduction to or from the disjoint convention was proved.

G3. Arithmetic norm-value branch

Establish or refute the existence of a sequence of positive-definite binary quadratic forms, possibly translated or congruence-restricted, with

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

This is the most direct exact construction target.

G4. Multiscale radial-support branch

Prove a theorem strong enough to imply

K(X,Y)=Ω(
logn
	​

n
	​

).

Sufficient formulations include

T(X,Y)=O(n
2
logn
	​

)

or

E(X,Y)=O(n
3
logn
	​

),

but either may be stronger than necessary.

G5. F=o(f)

Under matching pairwise-distinct conventions, decide whether

F
dis
	​

(n)=o(f(2n)).

C21 gives only F
dis
	​

(n)≤f(2n); the ratio question needs additional information about f.

9. Adversarial referee pass

Could C3 be invalid because zero distances are excluded?
No. The witness uses distance 1, not 0.

Could C7 fail for arbitrary n?
No. The ceiling ensures m
3
≥2n, and deletion of lattice points cannot increase the number of available squared-distance integers.

Could the fixed-radius circles in C10 coincide?
No. They have distinct centers and equal positive radius.

Could the arc graph have unbounded parallel-edge multiplicity?
No. Two vertices admit at most two centers of fixed-radius circles, and each circle contributes at most two arcs between that pair, giving multiplicity at most four.

Could C11 accidentally count zero distances using C10?
No. The disjoint case has none; the overlap case removes at most n zero pairs.

Is the direction of the Cauchy inequalities in C15 correct?
Yes:

∑m
i
2
	​

≥
K
(∑m
i
	​

)
2
	​

,∑e
s
2
	​

≥
K
(∑e
s
	​

)
2
	​

.

Were the logarithmic thresholds overstated?
No. Every final threshold uses 
logn
	​

.

Does C17 claim too much?
No. It concludes only ω(
logn
	​

) collinear points, not ω(logn).

Does C19 confuse arbitrary low-rank matrices with Euclidean matrices?
No. It explicitly treats rank as necessary only and records the remaining quadratic compatibility equations.

Does C20 assume that a rational null vector exists?
Yes, validly: a rational matrix of rank at most 2<r has a nontrivial nullspace over Q.

Does the literal affirmative answer settle the intended distinct-point problem?
No. The semantic fork is retained throughout and is the reason the overall outcome is not candidate-proved.

No attack invalidated C1–C21. The failure is not a defective surviving claim; it is the absence of a threshold-level planar construction or lower bound.

Final adjudication

Repetitions allowed: affirmative, with exactly one distance for every n.

All 2n points pairwise distinct in R
3
: affirmative, with O(n
2/3
) distances for every n.

All 2n points pairwise distinct in R
2
: neither a qualifying construction nor a threshold-level lower bound was obtained.

Each list internally distinct but overlap permitted: also unresolved.

Comparison F=o(f): separate and unresolved.

Self-contained planar bounds established here:

Ω(n
2/3
)≤F
dis
	​

(n)≤⌈
2
n
	​

⌉.
<result> OUTCOME: RESOURCE_EXHAUSTED COMPLETENESS_SCORE: 86 PROOF_CONFIDENCE: 18 ADVERSARIAL_SURVIVAL_SCORE: 93 OPEN_GAPS: Pairwise-distinct planar existence of K=o(n/sqrt(log n)) versus a lower bound K=Omega(n/sqrt(log n)); internally-distinct overlapping planar convention; variable binary-quadratic-form norm-value compression below m^2/sqrt(log m); multiscale radial-support or energy bound at the sqrt(log n) threshold; pairwise-distinct comparison F(n)=o(f(2n)) UNCHECKED_IMPORTS: NONE CLAIMS_CHECKED: 21 CLAIMS_TOTAL: 21 CLAIM_IDS: C1;C2;C3;C4;C5;C6;C7;C8;C9;C10;C11;C12;C13;C14;C15;C16;C17;C18;C19;C20;C21 </result>
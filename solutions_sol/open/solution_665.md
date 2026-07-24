# Erdős Problem #665 [unsolved] 42%

---

## ChatGPT Response

Phase 0: Formalization

I use only the definition and quantified question in the uploaded problem statement. 

Pasted text

Let V be an n-element set. A pairwise balanced design, abbreviated PBD, is a family B of proper subsets of V, called blocks, such that

2≤∣B∣<n(B∈B),

and for every distinct x,y∈V, there is exactly one B∈B with x,y∈B.

For a design D=(V,B), define

s(D)=
B∈B
min
	​

∣B∣,K(D)=
B∈B
max
	​

∣B∣,

and let m=∣B∣.

Because the design consisting of all two-element subsets always exists, the extremal function

s
∗
(n)=
D a PBD on n points
max
	​

s(D)

is well-defined.

The target statement is

∃C>0 ∃N ∀n≥N:s
∗
(n)>
n
	​

−C.
	​

(T)

Equivalently, with

h
∗
(n)=
n
	​

−s
∗
(n),

the question is whether

n→∞
limsup
	​

h
∗
(n)<∞.

Its negation is

∀C>0 ∀N ∃n≥N:s
∗
(n)≤
n
	​

−C.
	​

(¬T)

For a successful pair (C,N), the contrapositive form is:

If no PBD on n points has all its blocks larger than 
n
	​

−C, then n<N.

Equivalent formulations

A PBD is equivalently:

A decomposition of the edge set of K
n
	​

 into complete graphs K
∣B∣
	​

.

A finite linear space in which every pair of points lies on exactly one line.

A 0-1 incidence matrix whose distinct rows have scalar product exactly 1.

The problem asks whether K
n
	​

 can, for every sufficiently large n, be decomposed into cliques whose orders all differ from 
n
	​

 by only a bounded amount on the lower side.

Permuting points or blocks does not change the problem.

Phase 1: Universal identities and bounds

For x∈V, let

r
x
	​

=∣{B∈B:x∈B}∣.
Lemma 1: Pair and point identities

Every PBD satisfies

B∈B
∑
	​

(
2
∣B∣
	​

)=(
2
n
	​

)
(1)

and, for each x∈V,

B∈B
x∈B
	​

∑
	​

(∣B∣−1)=n−1.
(2)
Proof

Equation (1) counts unordered pairs of distinct points by their unique containing block.

For fixed x, each of the other n−1 points occurs exactly once with x, giving (2). ∎

Distinct blocks intersect in at most one point: otherwise a pair of common points would occur in two blocks.

Lemma 2: Every point has a nonincident block

For every x∈V, some block does not contain x.

Proof

Suppose every block contains x. For y

=x, let B
y
	​

 be the unique block containing x,y. Given y,z

=x, the block containing y,z also contains x, so it equals both B
y
	​

 and B
z
	​

. Consequently all points lie in one block, contrary to ∣B∣<n. ∎

Lemma 3: Fisher-type inequality

Every PBD has

m≥n.
(3)
Proof

Let M be the n×m incidence matrix. Then

MM
T
=J+diag(r
x
	​

−1),

because distinct points occur together in exactly one block.

Every r
x
	​

≥2, since r
x
	​

=1 would force its unique block to contain every point. Therefore, for nonzero z∈R
n
,

z
T
MM
T
z=(
x
∑
	​

z
x
	​

)
2
+
x
∑
	​

(r
x
	​

−1)z
x
2
	​

>0.

Thus MM
T
 has rank n, and hence m≥n. ∎

Lemma 4: Uniform upper bounds

Let s=s(D) and K=K(D). Then

s≤r
x
	​

≤
s−1
n−1
	​

(x∈V),
(4)

and

K≤
s−1
n−1
	​

.
(5)

In particular,

s(s−1)≤n−1.
(6)
Proof

Choose a block B

∋x. For every y∈B, the block containing x,y is distinct, so r
x
	​

≥∣B∣≥s.

Equation (2) gives

n−1≥r
x
	​

(s−1),

which proves the upper bound for r
x
	​

.

Choose a largest block L, and choose x∈
/
L. The same argument gives r
x
	​

≥K, proving (5). Combining s≤K with (5) gives (6). ∎

Thus no PBD can have minimum block size substantially larger than 
n
	​

. More precisely,

s≤
2
1+
4n−3
	​

	​

=
n
	​

+
2
1
	​

+O(n
−1/2
).
Quantitative stability under the proposed hypothesis

Fix C>0, write q=
n
	​

, and suppose

s>q−C.
(7)

For sufficiently large q,

s−1
n−1
	​

<
q−C−1
q
2
−1
	​

=q+C+1+
q−C−1
C(C+2)
	​

<q+C+2.

Therefore every block size and every replication number satisfies

q−C<∣B∣<q+C+2
	​

,
(8)
q−C<r
x
	​

<q+C+2.
	​

(9)

So the lower-bound hypothesis forces not merely large minimum blocks, but complete additive near-regularity.

From (1),

ms(s−1)≤n(n−1).

If a=2C+1, then

s(s−1)>(q−C)(q−C−1)=q
2
−aq+C(C+1).

For sufficiently large q,

0≤m−n<2aq=(4C+2)
n
	​

.
(10)

Hence

n≤m<n+O
C
	​

(
n
	​

).
	​


This is an almost-symmetric incidence structure.

Disjointness geometry

Define the disjointness graph G on B: two block-vertices are adjacent exactly when the blocks are disjoint.

For a block L, every other block meeting L meets it at a unique point. Hence

deg
G
	​

(L)=m−1−
x∈L
∑
	​

(r
x
	​

−1).
(11)

Using ∣L∣≥s, r
x
	​

≥s, and (10),

deg
G
	​

(L)≤m−1−s(s−1)=O
C
	​

(
n
	​

).
(12)

Thus G has n+O
C
	​

(
n
	​

) vertices, maximum degree O
C
	​

(
n
	​

), and

∣E(G)∣=O
C
	​

(n
3/2
).
(13)

The original points already decompose the complement of G into cliques:

R
x
	​

={B∈B:x∈B}.

Every intersecting pair of blocks occurs in exactly one R
x
	​

. Completing the design to a projective-plane-type structure would amount to decomposing the remaining disjointness edges into additional large cliques, interpreted as missing points.

This is the central completion problem.

A rigidity threshold
Lemma 5: Disjoint blocks force s≤
n
	​


If two blocks are disjoint, then

s
2
≤n.
(14)
Proof

Let A,B be disjoint, with ∣A∣=a, ∣B∣=b. Fix x∈A. The block A, together with the b distinct blocks joining x to the points of B, all contain x. Equation (2) gives

n−1≥(a−1)+b(s−1)≥(s−1)+s(s−1)=s
2
−1.

Therefore n≥s
2
. ∎

Corollary 6: Above 
n
	​

, a projective plane is forced

For sufficiently large n, if

s>
n
	​

,

then all blocks have one common size k, all points have replication k, and

n=k
2
−k+1.

Thus the PBD is a projective plane of order k−1.

Proof

Lemma 5 shows that every two blocks intersect. Their intersection is exactly one point.

Consequently

M
T
M=J+diag(∣B∣−1)

is positive definite, so m≤n. Lemma 3 gives m=n.

Also K<
n
	​

+1 for large n. Given two blocks L
1
	​

,L
2
	​

, choose a point x∈
/
L
1
	​

∪L
2
	​

, possible because ∣L
1
	​

∪L
2
	​

∣<2
n
	​

+2<n.

Every block through x intersects L
i
	​

, and projection from x to L
i
	​

 is a bijection. Hence

r
x
	​

=∣L
1
	​

∣=∣L
2
	​

∣.

Thus all blocks have the same size k. For any point y, choose a block not containing y; projection gives r
y
	​

=k. Equation (2) now yields

n−1=k(k−1).

∎

This verifies that 
n
	​

 is the exact structural transition: even a bounded deficit below it permits disjoint lines and affine-type behavior.

Exact square and projective-plane cases
Lemma 7: The square case is affine

Let q≥3. If a PBD on q
2
 points has

∣B∣≥q(B∈B),

then every block has size q, every point has replication q+1, and the design is an affine plane of order q.

Proof

Lemma 4 gives

K,r
x
	​

≤
q−1
q
2
−1
	​

=q+1.

Thus all block sizes and replications lie in {q,q+1}.

For a point x, let a
x
	​

 be the number of incident blocks of size q+1. Equation (2) becomes

q
2
−1=r
x
	​

(q−1)+a
x
	​

.

Hence either

r
x
	​

=q+1,a
x
	​

=0,

or

r
x
	​

=q,a
x
	​

=q−1.

Suppose there is a block L of size q+1. Every x∈L has a
x
	​

≥1, so r
x
	​

=q and a
x
	​

=q−1.

If M is any other block of size q+1 and x∈
/
M, Lemma 4’s projection argument gives r
x
	​

≥q+1, contradiction. Thus every point of L belongs to every block of size q+1. Two distinct such blocks would then share all q+1 points of L, impossible.

So L is the only block of size q+1. But every x∈L must lie in q−1≥2 such blocks, again a contradiction.

Therefore every block has size q. Equation (2) gives r
x
	​

=q+1.

For a line L and a point x∈
/
L, the q blocks joining x to the q points of L are distinct. Since r
x
	​

=q+1, exactly one additional block through x is disjoint from L. Thus the parallel axiom holds.

Disjointness is transitive: if L,M are both disjoint from N but meet at x, then two lines through x would be parallel to N, contradicting uniqueness. Hence lines split into parallel classes. This is an affine plane. ∎

Consequently, for 0<C≤1, a positive answer with that particular C would force an affine plane of every sufficiently large integer order, because at n=q
2
,

s>q−C

implies s≥q.

Lemma 8: The exact projective parameter

If a PBD on

n=q
2
+q+1

points has all block sizes at least q+1, then it is a projective plane of order q.

Proof

Lemma 4 gives

K,r
x
	​

≤
q
n−1
	​

=q+1.

Hence every block size and every replication number equals q+1. Also two blocks cannot be disjoint because

(q+1)
2
>q
2
+q+1.

The projective-plane axioms follow. ∎

Phase 1 breadth-first search

The confidence column estimates the likelihood that the method, by itself, can settle the original quantified statement.

Rank	Strategy	Hidden assumption or obstruction	Confidence	Novelty	Expected value
1	Auxiliary completion structure	Must globally decompose the disjointness graph into missing-point cliques	30%	High	Very high
2	Explicit construction	Requires sufficiently dense orders supporting plane-like structures	25%	Medium	Very high
3	Direct stability proof	Scalar bounds do not force incidence completion	20%	Medium	High
4	Contradiction via arithmetic	Needs a theorem connecting every near-extremal PBD to a nearby plane	15%	Medium	High
5	Density argument	Leading terms cancel at the affine/projective scale	12%	High	Medium
6	Reflection/duality	Produces an almost-dual problem rather than a simpler one	10%	High	Medium
7	Counterexample construction	Exact pair coverage is much more restrictive than numerical identities	8%	High	Medium
8	Induction on n	Adding one point requires a parallel-class-like partition	5%	Low	Low
9	Cardinal arithmetic/divisibility	Formal parameter sets can satisfy all scalar equations without being realizable	5%	Low	Medium
10	Diagonalization	Can avoid prescribed arithmetic order sets, but not arbitrary PBDs	4%	Medium	Low
11	Compactness	The additive 
n
	​

-scale condition is not retained in an ordinary limit	2%	Medium	Low
12	Transfinite induction	The problem is finite and no successor-extension operation is available	1%	Low	Very low

The three branches selected for detailed exploration are:

Branch A: stability and completion;

Branch B: explicit construction;

Branch C: arithmetic obstruction and counterexample search.

Phase 2: New structures and invariants
1. Extremal deficit
δ(D)=
n
	​

−s(D).

Bounded δ forces all line sizes and all point degrees into an interval of bounded width by (8)–(9).

2. Disjointness graph
G
D
	​

=(B,E),BB
′
∈E⟺B∩B
′
=∅.

Its edges represent precisely the pairs of lines whose missing intersection points would have to be restored in a completion.

3. Missing-point clique

A clique in G
D
	​

 is a family of pairwise disjoint blocks. In a truncated projective plane, all lines through one deleted point form such a clique.

A valid completion would require an edge decomposition of G
D
	​

 into these cliques, with compatibility conditions on how many cliques contain each block.

4. Local connector matching

Let A,B be disjoint blocks, with sizes a,b, and let z∈
/
A∪B. Define

α
z
	​

=#{blocks through z meeting both A and B}.

The a lines joining z to A and the b lines joining z to B have an intersection of size α
z
	​

. Therefore

α
z
	​

≥a+b−r
z
	​

.
(15)

Under (7)–(9),

α
z
	​

>q−3C−2.
	​

(16)

Each of these common blocks determines one point of A and one point of B; no endpoint can be repeated. Thus it is a matching between A and B missing only O
C
	​

(1) vertices.

Let

γ
z
	​

=#{blocks through z disjoint from both A and B}.

Then

γ
z
	​

=r
z
	​

−a−b+α
z
	​

.

Since α
z
	​

≤min(a,b),

0≤γ
z
	​

≤r
z
	​

−max(a,b)<2C+2.
(17)

Thus every exterior point lies on only boundedly many blocks disjoint from both A and B.

These near-perfect local matchings are a strong affine-net signature.

5. Exceptional-line budget

For x∈A, exactly b blocks through x meet B. Besides these and A, the number of remaining blocks is

r
x
	​

−b−1<2C+1.
(18)

Hence all but O
C
	​

(1) lines through each point of A are connectors to B.

Branch A: Stability and completion

The established information is:

∣B∣=
n
	​

+O
C
	​

(1),r
x
	​

=
n
	​

+O
C
	​

(1),
m=n+O
C
	​

(
n
	​

),Δ(G
D
	​

)=O
C
	​

(
n
	​

),

and every disjoint pair A,B induces near-perfect connector matchings at every exterior point.

A natural completion target is the following.

GAP_NODE: Bounded-defect completion

For each fixed C, prove that there exists D=D(C) such that every sufficiently large PBD satisfying

s>
n
	​

−C

can be embedded in a projective plane of some order Q with

∣Q−
n
	​

∣≤D.
(19)

A sufficient combinatorial form would be:

Decompose every edge of G
D
	​

 exactly once into large cliques.

Interpret each clique as a new point.

Ensure each old block receives exactly enough new points to reach size Q+1.

Add any missing lines.

Verify that every two new points lie on exactly one completed line.

Ten recursive attacks on the gap
Attack 1: Direct degree control

Equations (8)–(13) give bounded local defects.

Failure: bounded defects do not determine how disjointness edges must be grouped into cliques.

Attack 2: Maximal families of disjoint blocks

Let L
1
	​

,…,L
t
	​

 be pairwise disjoint. For every point outside their union, the incidence matrix between the r
x
	​

 lines through x and the t selected blocks is almost complete: at most

t(r
x
	​

−s)=O
C
	​

(t)

entries are missing.

Failure: this proves strong local regularity but does not show that a maximal disjoint family has size 
n
	​

+O
C
	​

(1).

Attack 3: Common-disjoint blocks

For disjoint A,B,

z∈
/
A∪B
∑
	​

γ
z
	​

=
L∈B
L∩A=L∩B=∅
	​

∑
	​

∣L∣.
(20)

A lower bound ∑
z
	​

γ
z
	​

≫n would produce Θ(
n
	​

) common-disjoint blocks and begin constructing a missing-point clique.

Failure: (17) supplies only an upper bound on each γ
z
	​

; no positive lower bound follows from the verified identities.

Attack 4: Matrix completion

The incidence matrix is an almost square 0-1 matrix satisfying

MM
T
=J+diag(r
x
	​

−1).

One seeks to add O
C
	​

(
n
	​

) rows and columns to obtain a square matrix P with

PP
T
=QI+J.

Failure: positivity and rank provide size bounds but do not force an integral 0-1 completion.

Attack 5: Inductively add one missing point

Adding one new point requires a family of pairwise disjoint old blocks whose union covers every old point exactly once, so that each old point has a unique joining line to the new point.

Failure: this is precisely a parallel-class problem. There is no verified argument producing the first such class.

Attack 6: Coordinate from two disjoint blocks

The connectors between A and B are indexed by A×B. Every exterior point determines a matching of size q−O
C
	​

(1) in this grid.

Progress: this converts the geometry into a system of near-permutations.

Failure: completing every near-permutation independently does not guarantee that the completed permutations have the required pairwise intersection properties.

Attack 7: Contradict a small maximal disjoint family

Counting pairs inside and outside the union of a maximal disjoint family gives exact first- and second-moment equations.

Failure: at the principal q
4
 and q
3
 scales, the inequalities are equalities for affine-plane-type parameter profiles. The bounded errors are large enough to absorb the desired contradiction.

Attack 8: Dual reflection

The original points give n cliques R
x
	​

 on the m block-vertices, covering every nonedge of G
D
	​

 exactly once.

Progress: the problem becomes completion of an almost-complete dual linear space.

Failure: the uncovered graph is sparse but still has O
C
	​

(n
3/2
) edges; dualization has not reduced the additive-defect difficulty.

Attack 9: Spectral stability

The eigenvalues of

MM
T
=J+diag(r
x
	​

−1)

all lie near 
n
	​

, except for the principal eigenvalue.

Failure: many nonisomorphic 0-1 incidence matrices can have the same coarse spectral bounds. The required clique decomposition is not spectrally forced by the estimates derived here.

Attack 10: Search for a counterexample to completion

One may try to prescribe a sparse disjointness graph with no large clique decomposition and then realize its complement using the original point-cliques R
x
	​

.

Failure: no realization satisfying exact pair uniqueness was constructed. Arbitrary sparse graphs are not valid disjointness graphs of such PBDs.

The completion statement therefore survives all ten attacks but remains unproved.

Branch B: Explicit construction

A substantial family of qualifying designs can be constructed directly.

Lemma 9: Projective plane over a prime field

Let p be prime. Take as points the one-dimensional subspaces of F
p
3
	​

, and as lines the two-dimensional subspaces.

There are

p−1
p
3
−1
	​

=p
2
+p+1

points. Each line contains

p−1
p
2
−1
	​

=p+1

points. Two distinct points span a unique two-dimensional subspace, so every pair lies on exactly one line.

Thus this is a projective plane of order p.

Lemma 10: Large sets with bounded line intersections

For a∈F
p
	​

, define

S
a
	​

={(t
2
+a:t:1):t∈F
p
	​

}∪{(1:0:0)}.

Then:

∣S
a
	​

∣=p+1;

every projective line meets S
a
	​

 in at most two points;

if a

=b, then

S
a
	​

∩S
b
	​

={(1:0:0)}.
Proof

A line has equation

αX+βY+γZ=0.

Its finite intersections with S
a
	​

 satisfy

α(t
2
+a)+βt+γ=0.

If α

=0, this nonzero quadratic has at most two roots, and the point at infinity is not on the line.

If α=0, the equation is linear and has at most one finite root; the point (1:0:0) lies on the line, giving at most two intersections.

For S
a
	​

∩S
b
	​

, equality of finite points with last coordinate 1 forces equal t and then a=b. ∎

Choose d distinct values a
1
	​

,…,a
d
	​

. Their union

U=S
a
1
	​

	​

∪⋯∪S
a
d
	​

	​


has size

∣U∣=dp+1

and every line meets U in at most 2d points.

Proposition 11: A whole interval of n

For every fixed d, every sufficiently large prime p, and every integer

p
2
+(1−d)p≤n≤p
2
+p+1,
(21)

there is a PBD on n points in which every block has size greater than

n
	​

−2d.
Proof

Let

t=p
2
+p+1−n.

By (21),

0≤t≤dp+1=∣U∣.

Delete an arbitrary t-element subset T⊆U. Replace every projective line L by its trace L∖T.

Every trace has size at least

p+1−2d.

For large p, this is at least 2. Every pair of remaining points still lies on its unique original line.

Also

n
	​

≤
p
2
+p+1
	​

<p+1.

Therefore

p+1−2d>
n
	​

−2d.

∎

Thus one prime order p covers an interval of length approximately dp below p
2
, as well as the interval up to p
2
+p+1.

Bounded-gap consequence

Let p<r be consecutive available prime orders, with g=r−p. The intervals in (21) overlap if

r
2
+(1−d)r≤p
2
+p+1.

The difference of the two sides is

p(2g−d)+g
2
+(1−d)g−1.

Thus d=2g is sufficient. Consequently:

If prime orders had gaps bounded by G, the construction would give the desired statement with C=4G.

This does not settle the problem because the required bounded-gap premise is unavailable and, in fact, the next lemma shows that even prime powers have arbitrarily long gaps.

Branch C: Arithmetic obstruction
Lemma 12: Arbitrarily long intervals contain no prime powers

For every L≥1, there are arbitrarily large N such that none of

N+1,…,N+L

is a prime power.

Proof

Choose 2L distinct primes

p
1
	​

,q
1
	​

,…,p
L
	​

,q
L
	​

.

Set M
j
	​

=p
j
	​

q
j
	​

. The M
j
	​

 are pairwise coprime.

By the Chinese remainder construction, there is an integer N satisfying

N≡−j(modM
j
	​

)(1≤j≤L).

Explicitly, with M=∏
j
	​

M
j
	​

, choose u
j
	​

 such that

u
j
	​

(M/M
j
	​

)≡1(modM
j
	​

)

and take

N≡
j=1
∑
L
	​

(−j)u
j
	​

M
j
	​

M
	​

(modM).

Then N+j is divisible by the two distinct primes p
j
	​

,q
j
	​

. Hence N+j is not a power of a single prime.

Adding arbitrary multiples of M makes N arbitrarily large. ∎

Therefore constructions relying only on prime or prime-power projective planes cannot cover all sufficiently large n with a fixed deletion parameter d.

This is not a disproof of the original statement. It leaves two possibilities not eliminated by the argument:

projective planes of other orders could supply the missing intervals;

qualifying PBDs might exist without admitting a nearby projective-plane completion.

Eliminating both possibilities requires the unresolved stability-completion theorem from Branch A, together with an independent obstruction to all nearby possible plane orders.

Counterexample and arithmetic sanity checks

Pure numerical identities cannot settle realization.

For every integer q, the formal affine-plane parameters

n=q
2
,m=q
2
+q,∣B∣=q,r
x
	​

=q+1

satisfy all scalar identities:

m(
2
q
	​

)=(
2
q
2
	​

),
(q+1)(q−1)=q
2
−1.

Thus divisibility and cardinal arithmetic may permit a parameter set even when no incidence structure has been produced. Any disproof must use genuine geometric compatibility, not only equations (1)–(2).

Conversely, random clique decompositions are not a plausible direct construction: two random subsets of size approximately 
n
	​

 have expected intersection approximately 1, but a PBD requires every pair of blocks to intersect in at most one point and imposes exact pair coverage. The structure is already at a rigid finite-geometry density.

Verified theorem pool

The following statements were established without unresolved dependencies:

Pair identity: equation (1).

Point identity: equation (2).

Fisher bound: m≥n.

Minimum-size bound: s(s−1)≤n−1.

Near-regularity: bounded deficit below 
n
	​

 forces all block sizes and degrees into a bounded interval.

Near-symmetry: m=n+O
C
	​

(
n
	​

).

Sparse disjointness: Δ(G)=O
C
	​

(
n
	​

).

Disjoint-line bound: disjoint blocks imply s≤
n
	​

.

Above-threshold rigidity: s>
n
	​

 forces a projective plane.

Square rigidity: n=q
2
 and s≥q force an affine plane.

Exact projective rigidity: n=q
2
+q+1 and s≥q+1 force a projective plane.

Prime-field construction: the intervals (21) admit designs with deficit <2d.

Arithmetic gap lemma: prime powers have arbitrarily long gaps.

The unresolved dependency is:

bounded additive deficit⟹bounded-distance projective-plane completion.
	​


The local connector matchings, sparse disjointness graph, and bounded degree defects provide substantial evidence of rigidity, but none of the deductions above constructs the required global clique decomposition or derives a contradiction from its failure.

Final state

RESOURCE_EXHAUSTED

The original quantified statement has not been proved or disproved. The available reasoning establishes the complete collection of structural and constructive results above, but the bounded-defect completion node remains unresolved after the ten independent attacks recorded in Branch A.

PROOF_CONFIDENCE: 96/100
Confidence that the stated lemmas and constructions are logically correct.

COMPLETENESS_SCORE: 42/100
The extremal identities, exact boundary cases, local stability, and a broad construction are rigorous; the global completion step required for the original statement is absent.

ADVERSARIAL_SURVIVAL_SCORE: 92/100
The established claims survived checks for strict inequalities, block duplication, small-degree exceptions, quantifier scope, and unjustified arithmetic conclusions.

RESOURCE_USAGE:
Approximately 100% of the allocated proof-search budget; 12 broad strategies examined, 3 branches developed in detail, 13 verified results retained, and 10 recursive attacks made on the principal gap.

I have not used WiFi, internet search, web search, external databases, external retrieved documents, external citations, or literature-status information. All mathematical reasoning was derived from the user-supplied problem statement, explicit assumptions, definitions, and deductions performed within this session.

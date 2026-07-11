I use the attached statement and scout bundle as the sole source material; the scout claims are rechecked rather than treated as authority.

1. Exact normalization

Let n≥2 be an integer. A Latin square of order n is a map

L:X×X→X,∣X∣=n,

whose restriction to every row and every column is bijective. Two Latin squares L,M are orthogonal when

(x,y)⟼(L(x,y),M(x,y))

is a bijection X
2
→X
2
. Let f(n) be the largest cardinality of a pairwise orthogonal family.

The notation ≫ is not defined in the statement. I adopt the standard absolute interpretation

∃c>0 ∃N ∀n≥N,f(n)≥c
n
	​

.
(Q)

Its exact negation is

∀c>0 ∀N ∃n≥N,f(n)<c
n
	​

,

equivalently

n→∞
liminf
	​

n
	​

f(n)
	​

=0.

This quantifier order matters:

An assertion only for infinitely many n is much weaker: powers of 2 already give f(n)=n−1.

Allowing the implied constant to depend on n makes the statement vacuous.

There is no single “smallest counterexample” to (Q); a disproof requires an infinite sequence.

The order n=1 is convention-dependent and irrelevant asymptotically.

2. Attack portfolio
Branch A: critical-scale PBD gluing

Construct idempotent MOLS on prime-power blocks and glue them over a pairwise balanced design.

Required terminal lemma:

∃A,B>0 ∀x≫1 ∀v≥Ax
2
,

there is a PBD of order v whose block sizes are prime powers in [x,Bx].

Fastest falsification tests are point-degree equations, global pair counting, Fisher’s inequality, and the sharper block-size interval derived below.

Likely failure mode: at t≍
v
	​

, every block is forced into a narrow interval around 
v
	​

. Sparse palettes that merely pass gcd conditions are inadequate.

Branch B: incomplete transversal-design embedding

Embed an order-q, q+1-column orthogonal array inside an order-n array with the same columns.

Required terminal lemma:

ITD(q+1,n;q)for all sufficiently large prime powers q and all n≥q
2
.

Fastest falsification test: the exact count of rows containing zero, one, or at least two old symbols. At the first perturbation n=q
2
+1, the problem becomes an explicit matching-frame system.

Likely failure mode: the threshold count is necessary but does not guarantee the compatible matchings needed simultaneously for all coordinate pairs.

Branch C: direct hypergraph matching

Encode an orthogonal array as a perfect matching in a highly symmetric hypergraph.

Required terminal lemma: that hypergraph has a perfect matching for

r=⌊c
n
	​

⌋+2.

Fastest falsification test: compute edge size, degrees, codegrees, and greedy packing density; test whether arbitrary partial arrays can be extended.

Likely failure mode: although normalized codegrees are 1/n, the edge size is Θ(n), and arbitrary regular linear instances can have no perfect matching.

Branch D: arithmetic-sensitive upper bounds

Stress-test orders n=2p, where products, cyclic-linear squares, and broad group constructions collapse.

Required terminal lemma:

L of order 2p
max
	​

ρ(L)=o(
p
	​

)

along infinitely many primes p, where ρ(L) counts compatible transversal resolutions.

Fastest falsification test: enumerate transversals and resolutions in finite examples and test parity, incidence ranks, and Smith-type invariants.

Likely failure mode: all presently visible parity obstructions apply only to restricted algebraic Latin squares, not to arbitrary ones.

3. Aggressive falsification of tempting intermediate claims
3.1 Gcd conditions do not imply a PBD

For the sparse palette

K={32,64,243}

and v=1026, let a,b,c be the respective block counts and B=a+b+c.

A nontrivial PBD has B≥1026. Pair counting gives

496a+2016b+29403c=(
2
1026
	​

)=525825,

or

525825=496B+1520b+28907c.

If c≥1, then

496B+28907≥496⋅1026+28907=537803>525825.

Thus c=0. The right side is then divisible by 16, while 525825≡1(mod16), a contradiction.

The same v also rules out

K={32,64,81,243}.

If a 243-block occurs, the preceding Fisher estimate is already too large. Without one, every (
2
k
	​

) for k=32,64,81 is even, whereas (
2
1026
	​

) is odd.

Thus eliminating the two elementary gcd obstructions is nowhere near sufficient.

3.2 Arbitrary extension of an orthogonal array is false

For even n, the cyclic Latin square

L(x,y)=x+y(modn)

has no transversal.

Indeed, a transversal would have cells (x,π(x)), with both π(x) and x+π(x) permutations of Z
n
	​

. Writing

S=
x=0
∑
n−1
	​

x,

we have S≡n/2(modn), but

x
∑
	​

(x+π(x))≡2S≡0(modn),

contradicting the fact that the symbols x+π(x) form a permutation and hence have sum S.

Therefore even a regular linear 3-partite hypergraph arising from a Latin square may have no perfect matching. A proof cannot extend arbitrary partial families greedily.

3.3 Product and translation constructions fail on 2p

The product construction gives

f(2p)≥min{f(2),f(p)}=1.

More generally, for translation-type squares

L
π
	​

(x,y)=π(x)+y(modn),

orthogonality of L
π
	​

,L
σ
	​

 requires

x⟼π(x)−σ(x)

to be a permutation. When n is even,

x
∑
	​

(π(x)−σ(x))≡0(modn),

whereas the sum of a permutation is n/2(modn). Hence this entire construction class contains at most one square.

This is only a construction obstruction, not an upper bound on f(2p).

4. Strongest surviving claims
C1. Standard asymptotic formulation

Claim.
Under the adopted meaning of ≫, the problem is exactly (Q), and its negation is

n→∞
liminf
	​

n
	​

f(n)
	​

=0.

Dependencies: none.

Justification.
This is the definition of a positive lower liminf.

C2. Orthogonal-array and code equivalence

Claim.
The following are equivalent for integers n≥2 and r≥2:

There are r−2 MOLS of order n.

There is an n
2
×r array over an n-element alphabet such that every pair of columns contains every ordered symbol pair exactly once.

There is a set C⊆[n]
r
, ∣C∣=n
2
, in which distinct words agree in at most one coordinate.

There is a transversal design with r groups of size n, every pair of points from different groups occurring in exactly one block.

Dependencies: none.

Justification.
From MOLS, assign to cell (x,y) the word

(x,y,L
1
	​

(x,y),…,L
r−2
	​

(x,y)).

The Latin and orthogonality conditions give the pair-projection property.

Conversely, choose any two columns as row and column coordinates. Every remaining column defines a Latin square, and any two define orthogonal squares.

For the code formulation, the pair-projection property implies agreement in at most one coordinate. Conversely, projection onto two fixed coordinates is injective on n
2
 words and maps into a set of size n
2
, hence is bijective.

The transversal-design formulation is obtained by interpreting a word as one point selected from each coordinate group.

C3. Universal upper bound

Claim.

f(n)≤n−1.

Dependencies: C2.

Justification.
Suppose an orthogonal array has r columns. In each column, the number of unordered pairs of rows agreeing there is

n(
2
n
	​

).

No pair of distinct rows agrees in two columns. Hence

rn(
2
n
	​

)≤(
2
n
2
	​

).

After cancellation,

r(n−1)≤n
2
−1=(n−1)(n+1),

so r≤n+1. Since f(n)=r−2, the result follows.

C4. Quadratic-threshold equivalence

Define

N(t)=inf{N: f(n)≥t for every integer n≥N},

allowing N(t)=∞.

Claim.
Statement (Q) is equivalent to

N(t)=O(t
2
).

Dependencies: C1.

Justification.

If f(n)≥c
n
	​

 for n≥N
0
	​

, then

n≥max{N
0
	​

,t
2
/c
2
}⟹f(n)≥t,

so N(t)=O(t
2
).

Conversely, suppose N(t)≤Ct
2
 for all sufficiently large t. For large n, put

t=⌊
C
n
	​

	​

⌋.

Then n≥Ct
2
, so f(n)≥t. Consequently,

f(n)≥
2
C
	​

1
	​

n
	​


for all sufficiently large n.

C5. Prime-power construction

Imported theorem, stated exactly.
For every prime power q=p
e
, there exists a field F
q
	​

 with q elements.

Claim.
For every prime power q,

f(q)=q−1.

Dependencies: C3 and the stated finite-field theorem.

Justification.
For a∈F
q
×
	​

, define

L
a
	​

(x,y)=ax+y.

Every L
a
	​

 is Latin. If a

=b, then from

u=ax+y,v=bx+y

one uniquely recovers

x=(a−b)
−1
(u−v),y=u−ax.

Thus the q−1 squares are mutually orthogonal. C3 gives equality.

C6. Idempotent reduction

Let g(n) be the maximum number of mutually orthogonal idempotent Latin squares, where L(x,x)=x.

Claim.
For n≥2,

f(n)−1≤g(n)≤f(n),g(n)≤n−2.

For prime powers q,

g(q)=q−2.

Dependencies: C2, C3, C5.

Justification.
The inequality g(n)≤f(n) is immediate.

Given f(n) MOLS, distinguish one square L
0
	​

. The cells carrying a fixed symbol of L
0
	​

 form a common transversal of every other square. Move this transversal to the diagonal and relabel symbols separately in each remaining square, producing f(n)−1 idempotent MOLS.

For the sharper upper bound, suppose g(n)=n−1. The associated orthogonal array has n+1 columns, so equality holds in the pair count of C3. Every two distinct rows would therefore agree in exactly one coordinate. But idempotence supplies the constant rows

(a,a,…,a),a∈[n],

and two such rows agree in no coordinate. Contradiction.

For a prime power, the squares

M
a
	​

(x,y)=ax+(1−a)y,a∈F
q
	​

∖{0,1},

are idempotent and mutually orthogonal, yielding q−2; the upper bound gives equality.

C7. PBD closure

Claim.
If a pairwise balanced design on V has the property that every block supports t idempotent MOLS, then

g(∣V∣)≥t.

Dependencies: C6.

Justification.
Choose local idempotent squares L
i
B
	​

 on every block. Define

L
i
	​

(x,x)=x,

and for x

=y, let B(x,y) be the unique block containing them and put

L
i
	​

(x,y)=L
i
B(x,y)
	​

(x,y).

For fixed x, the sets B∖{x}, over blocks B∋x, partition V∖{x}. Local idempotence shows that each global row and column is a permutation.

For outputs u

=v, their unique common block reduces global orthogonality to local orthogonality. For (u,u), local idempotence makes (u,u) the unique producing cell.

C8. Sharp PBD square-root ceiling

Consider a nontrivial PBD on v points, meaning V itself is not a block, used through C7 to construct t idempotent MOLS.

Claim.

(t+1)(t+2)≤v−1.

Moreover every block of size b satisfies

t+2≤b≤
t+1
v−1
	​

.

Dependencies: C6 and C7.

Justification.
Every block supporting t idempotent MOLS has size at least t+2.

Let A be the point-block incidence matrix. To prove the PBD Fisher inequality b
tot
	​

≥v, suppose A
T
z=0. Let r
x
	​

 be the number of blocks through x and S=∑
x
	​

z
x
	​

. Summing the block equations through x gives

(r
x
	​

−1)z
x
	​

+S=0.

In a nontrivial PBD, r
x
	​

≥2. Hence

z
x
	​

=−
r
x
	​

−1
S
	​

.

Summing over x forces S=0, and then z=0. Thus A has row rank v, so the number of blocks is at least v.

Now

(
2
v
	​

)=
B
∑
	​

(
2
∣B∣
	​

)≥v(
2
t+2
	​

),

which gives the first inequality.

For the blockwise upper bound, fix a block B of size b and a point x∈
/
B. For every y∈B, the block through x,y contains at least t points outside B∪{x}. These outside sets are disjoint for different y. Therefore

bt≤v−b−1,

or

b≤
t+1
v−1
	​

.

Thus t≍
v
	​

 forces every useful block to have order Θ(
v
	​

). This is the intrinsic critical exponent of PBD gluing.

C9. Equality rigidity in the PBD ceiling

Claim.
If

v−1=(t+1)(t+2)

and a nontrivial PBD constructs t idempotent MOLS, then:

every block has size t+2;

there are exactly v blocks;

every point belongs to t+2 blocks;

every two distinct blocks intersect in exactly one point.

Dependencies: C8.

Justification.
Equality must hold in every inequality used in C8. Hence there are exactly v blocks and every block has size k=t+2.

The point degree is

r
x
	​

=
k−1
v−1
	​

=k.

For a fixed block B, the number of incidences between B and all other blocks is

k(r
x
	​

−1)=k(k−1)=v−1.

There are exactly v−1 other blocks, and two blocks can intersect in at most one point because pairs of points lie in unique blocks. Hence every other block intersects B exactly once.

So equality demands a projective-plane-type incidence structure, not a flexible generic decomposition.

C10. A sufficient critical PBD theorem

Claim.
Suppose there exist absolute A,B>0 such that, for every sufficiently large x and every v≥Ax
2
, there is a PBD of order v whose block sizes are prime powers in [x,Bx]. Then (Q) holds.

Dependencies: C5–C8.

Justification.
Every such block supports at least x−2 idempotent MOLS. C7 gives

f(v)≥g(v)≥x−2.

Take

x=⌊
A
v
	​

	​

⌋.

Then

f(v)≥
2
A
	​

1
	​

v
	​


for sufficiently large v.

No proof of the hypothesized PBD theorem was obtained.

C11. Exact incomplete-design threshold

Define ITD(r,n;q) to be an r-column orthogonal array of order n containing an r-column orthogonal subarray of order q on designated q-symbol subsets.

Claim.
If n>q and ITD(q+1,n;q) exists, then

n≥q
2
.

Dependencies: C2.

Justification.
Call the core symbols old. An outside row contains at most one old symbol, because every pair of old symbols in different columns is already used by the core.

A fixed old symbol occurs n times in its full column and q times in the core, hence in n−q outside rows. There are (q+1)q old coordinate-symbol choices, so the number of one-old rows is

(q+1)q(n−q).

The number of all-new rows is therefore

n
2
−q
2
−(q+1)q(n−q)=(n−q)(n−q
2
).

It must be nonnegative. Since n>q, this gives n≥q
2
.

C12. The ITD threshold is attained

Claim.
For every prime power q,

ITD(q+1,q
2
;q)

exists.

Dependencies: C5.

Justification.
Let E=F
q
2
	​

, so ∣E∣=q
2
. Index coordinates by

F
q
	​

∪{∞}.

For x,y∈E, set

X
t
	​

=x+ty(t∈F
q
	​

),X
∞
	​

=y.

Any two coordinates determine x,y, so these q
4
 rows form an orthogonal array of order q
2
.

Let H be any one-dimensional F
q
	​

-subspace of E. Restricting to x,y∈H gives an order-q subarray with the same q+1 columns.

C13. Exact structure of the first perturbation

Put

n=q
2
+1,m=n−q=q
2
−q+1.

Claim.
After relabeling the new symbols, an ITD(q+1,q
2
+1;q) is equivalent to:

an order-q core;

one all-new perfect matching

{(z,z,…,z):z∈[m]};

for every old symbol a in coordinate i, a perfect matching across the q new groups other than i;

for every pair of new groups, these anchored matchings partition all ordered off-diagonal pairs.

Dependencies: C11.

Justification.
For n=q
2
+1, every new symbol lies in exactly one all-new row: it occurs in n rows total and in q
2
 one-old rows. Thus the all-new rows form a perfect matching.

For a fixed old anchor (i,a), its m outside rows meet every new symbol exactly once in every other coordinate, hence form a perfect matching across those groups.

For a pair of new groups, the all-new matching covers the diagonal pairs. All other pairs must be covered exactly once by anchored rows whose old coordinate is outside that pair. Conversely, these conditions verify every possible pair of coordinate symbols.

C14. Translation-frame sufficient condition

Let G be an abelian group of order

m=q
2
−q+1.

Suppose there are shifts d
i,a,j
	​

∈G, defined for

i

=j,i,j∈{0,…,q},a∈[q],

such that for every j

=k,

{d
i,a,k
	​

−d
i,a,j
	​

:i∈
/
{j,k}, a∈[q]}=G∖{0}

with each nonzero element occurring once.

Claim.
Such shifts construct

ITD(q+1,q
2
+1;q).

Dependencies: C12 and C13.

Justification.
For each anchor (i,a) and z∈G, use the row having old symbol a in coordinate i and new symbol

z+d
i,a,j
	​


in coordinate j

=i. Add the diagonal all-new rows (z,…,z).

Old-old pairs are covered by the core. Old-new pairs are covered uniquely because z↦z+d is bijective. A new-new off-diagonal pair (u,v) has nonzero difference v−u, which uniquely identifies (i,a) by the frame condition and then uniquely determines z.

C15. Explicit first perturbation for q=3

Claim.

ITD(4,10;3)

exists.

Dependencies: C14.

Justification.
Take G=Z
7
	​

. For each missing coordinate i, use the following three shift rows; entries are ordered by coordinates 0,1,2,3:

i=0
i=1
i=2
i=3
	​

(∗,0,1,2)
(0,∗,1,4)
(0,1,∗,5)
(0,2,6,∗)
	​

(∗,0,2,1)
(0,∗,2,6)
(0,3,∗,2)
(0,4,3,∗)
	​

(∗,0,3,5)
(0,∗,5,3)
(0,5,∗,1)
(0,6,4,∗)
	​


For the six coordinate pairs, the applicable differences split as

01
02
03
12
13
23
	​

{1,3,5}∪{2,4,6}
{1,2,5}∪{6,3,4}
{4,6,3}∪{5,2,1}
{1,2,3}∪{4,6,5}
{2,1,5}∪{4,6,3}
{1,6,2}∪{3,4,5}.
	​


Each is exactly Z
7
	​

∖{0}. C14 therefore applies.

C16. A second first-perturbation construction

Claim.

ITD(5,17;4)

exists.

Dependencies: C14.

Justification.
Let G=(F
13
	​

,+) and

H={1,5,8,12}≤F
13
×
	​

.

Its three multiplicative cosets are

H,2H={2,3,10,11},4H={4,6,7,9}.

Use the off-diagonal matrix

C=
	​

∗
0
0
0
0
	​

0
∗
4
12
3
	​

5
1
∗
9
10
	​

2
2
8
∗
4
	​

12
11
7
8
∗
	​

	​

.

Index the four old symbols by h∈H and put

d
i,h,j
	​

=hC
ij
	​

.

For coordinate pairs 01,02,…,34, the differences

C
ik
	​

−C
ij
	​

(i∈
/
{j,k})

are respectively

01
02
03
04
12
13
14
23
24
34
	​

(4,12,3)
(1,9,10)
(2,8,4)
(11,7,8)
(5,10,7)
(2,4,1)
(12,3,9)
(10,1,7)
(7,10,12)
(10,9,12).
	​


Every triple contains one representative from each of H,2H,4H. Multiplication by all h∈H therefore gives every nonzero element of F
13
	​

 exactly once. C14 applies.

These two finite constructions support the first-perturbation route but do not establish uniform existence.

C17. Direct perfect-matching formulation

For integers r,n, define a hypergraph H
r,n
	​

:

vertices are tuples (i,j,a,b) with 1≤i<j≤r and a,b∈[n];

a word x=(x
1
	​

,…,x
r
	​

)∈[n]
r
 defines the edge

e
x
	​

={(i,j,x
i
	​

,x
j
	​

):i<j}.

Claim.
A perfect matching in H
r,n
	​

 is exactly an r-column orthogonal array of order n.

Furthermore,

∣e
x
	​

∣=(
2
r
	​

),deg(v)=n
r−2
,

and the maximum codegree of two distinct compatible vertices is

n
r−3
.

Dependencies: C2.

Justification.
A perfect matching covers every coordinate-pair-symbol-pair specification once, which is precisely the orthogonal-array condition. The degree and codegree follow by fixing respectively two or at least three coordinates of a word.

At r=Θ(
n
	​

), edge size is Θ(n) and normalized codegree is 1/n. However,

(
2
r
	​

)
n
1
	​

=Θ(1),

so the accumulated overlaps within one edge remain macroscopic. No exact matching or absorption argument covering this regime was derived.

C18. Compatible-resolution formulation

For a Latin square L, let ρ(L) be the largest number of pairwise compatible resolutions of its cells into transversals, where two resolutions are compatible when every transversal from one meets every transversal from the other in exactly one cell.

Claim.
For n>1,

f(n)=1+
L
max
	​

ρ(L).

Dependencies: C2.

Justification.
An orthogonal mate M of L partitions the cells of L into the n symbol classes of M, each a transversal. Conversely, labeling the transversals of a resolution produces an orthogonal mate.

Two mates are orthogonal exactly when their two resolutions are compatible. Thus a family containing L consists of L plus a compatible family of resolutions.

Consequently, a disproof of (Q) would follow from an infinite sequence n
j
	​

 such that

L of order n
j
	​

max
	​

ρ(L)=o(
n
j
	​

	​

).

No universal invariant proving this was found.

5. Dependency ledger
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
	​

Dependencies
none
none
C2
C1
C3+finite-field existence
C2,C3,C5
C6
C6,C7
C8
C5,C7,C8
C2
C5
C11
C12,C13
C14
C14
C2
C2
	​

	​

6. Open-gap ledger

G1: Critical PBD theorem.
Prove that every sufficiently large v≥Ax
2
 has a PBD with all block sizes prime powers in [x,Bx].

Attacks made: elementary divisibility palettes; Fisher and pair-count tests; narrow block interval; affine-plane modifications. Sparse palettes fail, and no uniform construction survives.

G2: Uniform ITD embedding.
Prove ITD(q+1,n;q) for enough prime powers q and every n≥q
2
.

Attacks made: exact threshold count; equality construction; exact first-perturbation matching frame; translation frames; explicit q=3,4 constructions. No uniform frame or method for arbitrary residual degree t=n−q
2
 was obtained.

G3: Direct hypergraph matching.
Prove that H
r,n
	​

 has a perfect matching for r≥c
n
	​

.

Attacks made: degree-codegree analysis; greedy packing; arbitrary extension tests. Greedy packing produces only O(n) words at the target scale rather than n
2
, and arbitrary regular linear instances can fail to have one perfect matching.

G4: Universal arithmetic obstruction.
Find an infinite sequence, plausibly n=2p, with

L
max
	​

ρ(L)=o(
n
	​

).

Attacks made: product bottlenecks; cyclic parity; group and translation constructions; real incidence rank. These eliminate broad construction subclasses but give no upper bound for arbitrary Latin squares.

7. Adversarial referee pass

Notation check: the conclusion is conditional on the standard absolute meaning of ≫. No other interpretation is silently used.

OA equivalence: the converse code implication uses both ∣C∣=n
2
 and alphabet size n; without the cardinality equality, agreement at most one would not imply every ordered pair occurs.

Upper bound: each pair of rows is counted at most once, not exactly once. Equality is used only in C6 under the explicit assumption r=n+1.

Idempotent reduction: one square is necessarily discarded. No claim g(n)=f(n) is made.

PBD closure: local symbol sets are identified with the actual block points. Idempotence is necessary for compatibility on diagonals.

PBD ceiling: the design must be nontrivial. Allowing V itself as a block makes the construction tautological and invalidates Fisher’s inequality in the required form.

Block interval: the outside point x exists only for a proper block, which is ensured by nontriviality.

ITD threshold: the conclusion n≥q
2
 is asserted only for n>q; the core-only case n=q makes the factor n−q vanish.

Threshold construction: the order-q core is a one-dimensional subspace of the q
2
-symbol alphabet, not an unjustified identification of F
q
	​

 with F
q
2
	​

.

Finite frames: every listed difference condition can be checked directly. These cases are not promoted to an asymptotic theorem.

Hypergraph route: small normalized codegree alone is not asserted to imply a perfect matching when edge size grows with n.

Negative route: obstructions to cyclic, group, product, or translation constructions are not claimed as upper bounds on f(n).

The last fully justified claims are C17 and C18. None supplies a terminal proof or counterexample without one of G1–G4.

<result> OUTCOME: RESOURCE_EXHAUSTED COMPLETENESS_SCORE: 86 PROOF_CONFIDENCE: 0 ADVERSARIAL_SURVIVAL_SCORE: 93 OPEN_GAPS: G1: prove a uniform quadratic-threshold PBD theorem using prime-power blocks of order Theta(sqrt(v)); G2: prove ITD(q+1,n;q) uniformly for enough prime powers q and all n at or above q^2; G3: prove a perfect-matching theorem for the symmetric orthogonal-array hypergraph when r=Theta(sqrt(n)); G4: establish an arithmetic-sensitive universal bound max_L rho(L)=o(sqrt(n)) along an infinite sequence UNCHECKED_IMPORTS: NONE CLAIMS_CHECKED: 18 CLAIMS_TOTAL: 18 CLAIM_IDS: C1;C2;C3;C4;C5;C6;C7;C8;C9;C10;C11;C12;C13;C14;C15;C16;C17;C18 </result>
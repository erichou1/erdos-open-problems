Status

No proof or disproof is obtained.

There is also a formal blocking defect: the supplied statement does not define ≫. The mathematically substantive interpretation suggested by the surrounding bounds is

∃c>0 ∃N ∀n≥N,f(n)≥c
n
	​

.
(U)

All attacks below concern (U), without asserting that (U) is formally part of the immutable statement. Under the much weaker “infinitely many n” interpretation, prime-power orders already give a linear lower bound; under an n-dependent implied constant, the assertion becomes vacuous.

1. Exact equivalent formulations
1.1 Orthogonal arrays

An orthogonal array OA(n
2
,k,n,2) is an n
2
×k array over an n-element alphabet such that, in every pair of columns, each ordered pair of symbols occurs exactly once.

There are r MOLS of order n if and only if there is an

OA(n
2
,r+2,n,2).

Indeed, index the rows by cells (x,y). Use x,y as the first two columns and the entries of the r Latin squares as the remaining columns. Conversely, the first two OA columns label rows and columns, and every further column defines a Latin square.

Thus the problem is equivalent to asking whether every sufficiently large n admits an OA(n
2
,k,n,2) with

k≥c
n
	​

.
1.2 Orthogonal partitions

Each OA column partitions its n
2
 rows into n fibers of size n. Two columns satisfy the OA condition exactly when every fiber of one intersects every fiber of the other in one point.

Hence f(n)+2 is the maximum number of pairwise orthogonal uniform partitions of an n
2
-element set into n classes of size n.

1.3 Transversal designs

Equivalently, r MOLS of order n correspond to a transversal design TD(r+2,n): there are r+2 groups of size n, every block meets every group once, and every pair of points from distinct groups occurs in exactly one block.

1.4 Factorizations of K
n,n
	​


A Latin square is a decomposition of the edges of K
n,n
	​

 into n perfect matchings. Two Latin squares are orthogonal exactly when every matching from one factorization meets every matching from the other in one edge.

So the problem asks for c
n
	​

 pairwise orthogonal 1-factorizations of K
n,n
	​

.

2. Universal upper bound

The standard upper bound follows directly from the partition formulation.

For each OA column j, let U
j
	​

⊆R
n
2
 be the space of functions constant on each fiber of column j and having total sum zero. Then

dimU
j
	​

=n−1.

If i

=j, every fiber of column i intersects every fiber of column j once, so

U
i
	​

⊥U
j
	​

.

All U
j
	​

 lie in the (n
2
−1)-dimensional space orthogonal to the all-ones vector. Therefore

k(n−1)≤n
2
−1=(n−1)(n+1),

and hence

k≤n+1,f(n)≤n−1.

This also shows that any order h supporting r MOLS must satisfy

h≥r+1.

The linear-algebra relaxation leaves an enormous gap: it permits k of order n, so it does not detect the proposed 
n
	​

 threshold.

3. The exact threshold formulation

Define

N(r)=inf{N: f(n)≥r for every integer n≥N},

allowing N(r)=∞.

Then (U) is equivalent to

N(r)=O(r
2
).
(T)
Proof of equivalence

If f(n)≥c
n
	​

 for n≥N
0
	​

, then for sufficiently large r,

n≥c
−2
r
2
⟹f(n)≥r.

Thus N(r)=O(r
2
).

Conversely, suppose N(r)≤Cr
2
 for all large r. Given large n, take

r=⌊
C
n
	​

	​

⌋.

Then n≥Cr
2
, so f(n)≥r, and consequently

f(n)≥
2
C
	​

1
	​

n
	​


for all sufficiently large n.

Thus the whole problem can be viewed as reducing the eventual-existence threshold for r MOLS to its natural quadratic scale.

Taking the exponents stated in the supplied text at face value, a lower bound f(n)≫n
α
 translates into N(r)=O(r
1/α
). The requested exponent 1/2 is exactly the target N(r)=O(r
2
).

4. Elementary constructions
4.1 Prime powers

Let q be a prime power and let F
q
	​

 be a field with q elements. For a∈F
q
×
	​

, define

L
a
	​

(x,y)=ax+y.

Each L
a
	​

 is Latin. If a

=b, then from

u=ax+y,v=bx+y

one recovers

x=
a−b
u−v
	​

,y=u−ax.

Hence the q−1 squares L
a
	​

 are mutually orthogonal. Combined with the universal upper bound,

f(q)=q−1.

For local constructions it is useful to have idempotent squares. For

a∈F
q
	​

∖{0,1},M
a
	​

(x,y)=ax+(1−a)y,

we have M
a
	​

(x,x)=x. These form q−2 mutually orthogonal idempotent Latin squares.

Thus every prime power q≥r+2 supports r idempotent MOLS.

4.2 Direct products

If there are r MOLS of orders m and n, then there are r MOLS of order mn, by applying corresponding squares coordinatewise. Therefore

f(mn)≥min{f(m),f(n)}.

If

n=
i
∏
	​

q
i
	​


is its decomposition into pairwise coprime prime powers, this gives

f(n)≥
i
min
	​

(q
i
	​

−1).

This proves the desired scale for products of two comparable prime powers, but it collapses on orders such as 2q.

5. Pairwise balanced design closure

A pairwise balanced design, abbreviated PBD, on a set V is a collection of blocks such that every two distinct points lie in exactly one block.

PBD closure lemma

Suppose that every block B of a PBD on v points supports r idempotent MOLS. Then there are r MOLS of order v.

Proof

For every block B, choose local idempotent MOLS

L
1
B
	​

,…,L
r
B
	​

.

Define global squares by

L
j
	​

(x,x)=x

and, for x

=y, let B be the unique block containing x,y and put

L
j
	​

(x,y)=L
j
B
	​

(x,y).

Fix x. The sets B∖{x}, over blocks containing x, partition V∖{x}. Since the local square is idempotent, its row x, restricted to B∖{x}, contains exactly B∖{x}. Hence every global row is a permutation; the same argument applies to columns.

For orthogonality, the pair (u,u) occurs only at (u,u). If u

=v, let B be the unique block containing u,v. Local orthogonality gives a unique cell in B
2
 producing (u,v), and that cell is off-diagonal. Thus it is also the unique global cell producing the pair.

6. A precise sufficient design target

For fixed r, let

Q
r
	​

={q:q is a prime power and q≥r+2}.

If K
n
	​

 can be decomposed into cliques whose orders lie in Q
r
	​

, then the blocks form a PBD and the closure lemma gives

f(n)≥r.

Thus the following statement would imply the desired result:

There is an absolute C such that, for every sufficiently large r and every n≥Cr
2
, K
n
	​

 has a clique decomposition with every clique order a prime power at least r+2.

This target can be reduced to only three admissible block sizes of order r.

Let 2
a
 be the least power of 2 at least r+2, and let 3
b
 be the least power of 3 at least r+2 with b odd. Set

K
r
	​

={2
a
,2
a+1
,3
b
}.

All three numbers are O(r). The elementary necessary divisibility conditions for a PBD with block sizes in K are

gcd{k−1:k∈K}∣n−1

and

gcd{k(k−1):k∈K}∣n(n−1).

For this K
r
	​

,

gcd(2
a
−1,2
a+1
−1)=1,

so the first gcd is 1. Also

gcd{k(k−1):k∈K
r
	​

}=2,

because b is odd and 3
b
−1≡2(mod4). Since n(n−1) is always even, there is no elementary congruence obstruction.

Therefore an especially concrete intermediate target is:

∃C∀r≫1∀n≥Cr
2
,K
n
	​

 decomposes into K
2
a
	​

,K
2
a+1
	​

,K
3
b
	​

.
(CD)

I cannot prove (CD).

This target is structurally demanding. At n=Θ(r
2
) and block size Θ(r), the number of blocks is Θ(n), the same scale as an affine or projective plane. Indeed, a nontrivial PBD has at least n blocks: if A is its point-block incidence matrix, then

AA
T
=J+diag(ρ
x
	​

−1)

is positive definite when there is no block containing every point, so rankA=n.

Thus (CD) asks for plane-scale incidence structures for every sufficiently large order, not merely a generic dense graph decomposition.

7. Explicit affine-plane interval constructions

Let q be a prime power. On F
q
2
	​

, the affine lines form q+1 parallel classes, each containing q disjoint q-point lines.

7.1 Orders q
2
+t

Choose t parallel classes and add one new “direction point” for each selected class. Extend every line in that class by its direction point. Finally, put all direction points in one block when t≥2.

This gives a PBD on

q
2
+t

points with block sizes among

q,q+1,t.

All pair checks are immediate:

two affine points lie on their unique affine line;

a direction point and an affine point lie on the unique line of that parallel class through the affine point;

two direction points lie in the direction block.

Therefore, if q,q+1,t all support r idempotent MOLS, then

f(q
2
+t)≥r.

For t=0 or 1, the t-block is unnecessary.

7.2 Orders q
2
−q+t

Choose an affine line H, retain only t of its q points, and delete the others. The distinguished line becomes a t-block. Every other line has size q or q−1.

This gives a PBD on

q
2
−q+t

points with block sizes among

q,q−1,t.
7.3 What these constructions expose

They cover full intervals of length Θ(q) around q
2
, but to obtain r=cq MOLS every nontrivial block must have order at least r+1. Thus:

a small residual block t<r+1 is fatal;

q+1 or q−1 must itself support almost the maximum possible number of MOLS;

the square-root lower bound at the smaller orders q±1 would give only O(
q
	​

), not O(q).

This is a general scale mismatch.

Suppose a PBD proof of f(n)≥c
n
	​

 uses blocks of size at most M
n
	​

. Every block B must support c
n
	​

 idempotent MOLS, so

f(∣B∣)≥c
n
	​

≥
M
c
	​

∣B∣.

Thus every ingredient order must already have a positive linear fraction of the maximum number of MOLS. A square-root theorem cannot bootstrap itself through smaller PBD blocks. Prime powers supply linear-quality ingredients, but arbitrary orders do not.

8. Product and inflation constructions: exact failures
8.1 Coordinatewise products retain the smallest factor

Suppose the alphabet is a Cartesian product and every global Latin square acts coordinatewise. For two such squares to be orthogonal, their component squares must be orthogonal in every coordinate. Therefore any family obtained this way has size at most the minimum family size among the factors.

No rearrangement of the index set in a coordinatewise tensor product removes this bottleneck.

8.2 Affine constructions over a product of fields

Let

R=
i
∏
	​

F
q
i
	​

	​


and consider affine squares

L
a
	​

(x,y)=ax+y,a∈R
×
.

Two slopes a,b give orthogonal squares exactly when a−b is a unit. Projection onto each F
q
i
	​

	​

 shows that the slope coordinates must be distinct in every factor. Consequently,

∣A∣≤
i
min
	​

(q
i
	​

−1).

This upper bound is attained within this affine family. Thus all CRT-affine constructions reproduce exactly the direct-product lower bound.

8.3 Cyclic translation obstruction for even order

Let n be even and consider Latin squares of the form

L
t
	​

(x,y)=ϕ
t
	​

(x)+y

on Z
n
	​

, where ϕ
t
	​

 is a permutation.

If L
t
	​

,L
s
	​

 were orthogonal, then

x⟼ϕ
t
	​

(x)−ϕ
s
	​

(x)

would have to be a permutation: the difference of the two outputs determines x, and then y.

But

x
∑
	​

(ϕ
t
	​

(x)−ϕ
s
	​

(x))≡0(modn),

whereas the sum of a permutation of Z
n
	​

 is

0+1+⋯+(n−1)=
2
n(n−1)
	​

≡
2
n
	​


≡0(modn).

Therefore this entire translation-based ansatz produces at most one Latin square when n is even.

This is an obstruction to the construction, not an upper bound on f(n).

8.4 Unequal blow-ups cannot adjust residues

Consider the following natural inflation scheme. Start with an outer Latin square L of order m. Replace outer row i, column j, and symbol z by clusters of sizes

r
i
	​

,c
j
	​

,s
z
	​

,

and require the block replacing cell (i,j) to use only symbols from the cluster corresponding to L(i,j).

Fix a micro-row inside outer row i. In outer row i, symbol z occurs in a unique outer column j. The micro-row has c
j
	​

 entries in that cell-block, all drawn from the s
z
	​

-element cluster. For the global row to contain every symbol once, necessarily

c
j
	​

=s
z
	​

.

As i varies while j is fixed, L(i,j) runs through all outer symbols. Hence all s
z
	​

 and all c
j
	​

 are equal. The column argument similarly forces all r
i
	​

 equal.

Thus this entire nonuniform blow-up mechanism collapses to uniform inflation and cannot repair the smallest-factor or residue obstruction.

8.5 Restricting a field construction forces subgroup sizes

Let G be a finite abelian group, let a be an automorphism, and suppose subsets X,Y,S⊆G, all of size m, satisfy

x+ay∈S

and give a Latin square on X×Y.

For every y∈Y,

X+ay=S.

Fix y
0
	​

∈Y. Then

a(y−y
0
	​

)∈H:={g:X+g=X}.

Thus Y is contained in a coset of a
−1
H, giving

m=∣Y∣≤∣H∣.

But X is a union of H-cosets, so ∣H∣≤∣X∣=m. Hence equality holds, and X,Y are cosets of a subgroup of order m.

In the additive group of a finite field, subgroup orders are powers of the characteristic. Therefore simply restricting rows, columns, and symbols of a finite-field Latin square cannot create arbitrary nearby orders.

9. Direct extension as hypergraph factorization

Suppose an OA(n
2
,k,n,2) has already been constructed. Form a k-partite k-uniform hypergraph H:

its vertices are coordinate-symbol pairs (j,a);

every OA row gives one hyperedge containing its k coordinate-symbol pairs.

Then:

∣V(H)∣=kn,∣E(H)∣=n
2
,

every vertex has degree n, and every pair of vertices from different parts has codegree one. Thus H is regular and linear.

Adding one more OA column is equivalent to coloring the edges of H with n colors so that intersecting edges receive different colors. Since every vertex has degree n, a proper n-edge-coloring is exactly a decomposition into n perfect matchings.

Hence:

An OA(n
2
,k,n,2) extends by one column if and only if its associated regular linear k-partite hypergraph is 1-factorizable.

Regularity and linearity are insufficient

Take the cyclic Latin square of even order,

L(i,j)=i+j(modn).

A transversal would choose columns π(i), one from each row, such that the symbols

i+π(i)

also form a permutation. Summing modulo n,

i
∑
	​

(i+π(i))≡2
i
∑
	​

i≡0(modn).

But the sum of a permutation of Z
n
	​

 is n/2(modn), a contradiction. Thus this Latin square has no transversal.

Its associated 3-partite regular linear hypergraph has no perfect matching, let alone a 1-factorization. Therefore the tempting stronger assertion

“every regular linear k-partite hypergraph is 1-factorizable”

is false already for k=3.

Remaining direct target

One would have to construct the OA columns while maintaining additional pseudorandom or absorbing structure:

begin with the row and column partitions;

find a 1-factorization of the current hypergraph;

use it as the next coordinate;

prove that the new hypergraph retains enough expansion and absorber structure;

continue for k=c
n
	​

 steps.

A naive local-lemma attack does not reach this range. If edges are randomly assigned one of n colors, a conflict event has probability 1/n and depends on O(kn) other conflict events, giving a symmetric criterion of order k, not k/
n
	​

. It can at best address bounded k.

A random-greedy matching plus absorption argument is a plausible direct route, but the exact theorem needed is not established here.

10. An incomplete-design attack at the square-root scale

The following auxiliary object isolates a more delicate construction.

10.1 Holey difference template

Let q be a prime power, let k≥3, and let h≥0. Put

q
0
	​

=q−h(k−2).

A holey difference template consists of:

q
0
	​

 full vectors in F
q
k
	​

;

for each i∈{1,…,k} and each u∈{1,…,h}, one partial vector defined on all coordinates except i;

such that for every pair j

=ℓ, the following differences list every element of F
q
	​

 exactly once:

v
ℓ
	​

−v
j
	​


over all full vectors and all partial vectors whose missing coordinate is neither j nor ℓ.

10.2 Construction lemma

Such a template produces an incomplete TD(k,q+h) whose hole has h points in every group.

For every full vector v and every t∈F
q
	​

, make the block

{(j,v
j
	​

+t):1≤j≤k}.

For a partial vector missing coordinate i, make the block consisting of its designated hole point in group i and

(j,v
j
	​

+t),j

=i.

For two old points in groups j,ℓ, their difference identifies the unique template vector and then t. For a hole point and an old point, t is uniquely determined. No block contains two hole points.

If the holes themselves support a TD(k,h), filling the hole gives a TD(k,q+h), hence k−2 MOLS of order q+h.

10.3 Necessary counting condition

The inequality

h(k−2)≤q

is not merely an artifact of the template. It is necessary for any incomplete TD(k,q+h) with a common hole of size h.

There are kh hole points. Each hole point must occur in exactly q blocks to meet every old point in each other group. Since a block cannot contain two hole points, there are

khq

one-hole blocks.

Let B
0
	​

 be the number of all-old blocks. Counting pairs of old points gives

B
0
	​

(
2
k
	​

)+khq(
2
k−1
	​

)=q
2
(
2
k
	​

).

Therefore

B
0
	​

=q(q−h(k−2)),

so h(k−2)≤q.

10.4 Consequence for the square-root problem

Set

r=k−2.

To fill a nontrivial hole, the upper bound gives

h≥r+1.

The counting inequality gives

hr≤q.

Thus

r(r+1)≤q.

If r=c
n
	​

 and n=q+h, then necessarily

h≤
r
q
	​

=O(
n
	​

),q=n−O(
n
	​

).

So this method needs:

a prime-power or otherwise highly structured core q within O(
n
	​

) of n;

a residual hole h=Θ(
n
	​

) that already supports nearly h MOLS;

existence of the holey difference template.

This is exactly at the desired counting scale, but it replaces the original problem by a strong additive representation and near-complete-hole problem.

10.5 Finite tests of the template

For q=3,k=4,h=1, there is a template. Take the one full row

(0,0,0,0)

and partial rows

	​

∗
0
0
0
	​

0
∗
1
2
	​

1
2
∗
1
	​

2
1
2
∗
	​

	​

.

For every pair of columns, the full row contributes difference 0, while the two applicable partial rows contribute 1 and 2.

An offline exhaustive search found no translated holey difference template for

q=5,k=4,h=1.

The search normalized the first available entry of every template row to 0, enumerated the three required full rows and one partial row of each missing-coordinate type, and maintained six difference masks, rejecting any repeated difference. This is only a finite nonexistence result for this restricted template class; it is not an upper bound on f(6) and is not used as an asymptotic premise.

It does show that the counting condition h(k−2)≤q is far from sufficient.

11. A Fourier attack on non-coordinatewise algebraic squares

Coordinatewise products fail, so one can seek constructions coupling different arithmetic components.

Let G be a finite abelian group of order n. Choose permutations

α
t
	​

,β
t
	​

:G→G

and define

L
t
	​

(x,y)=α
t
	​

(x)+β
t
	​

(y).

Every L
t
	​

 is Latin.

For two indices t,u, and characters χ,ψ of G, define

A
t,u
	​

(χ,ψ)=
x∈G
∑
	​

χ(α
t
	​

(x))ψ(α
u
	​

(x)),
B
t,u
	​

(χ,ψ)=
y∈G
∑
	​

χ(β
t
	​

(y))ψ(β
u
	​

(y)).

The Fourier transform of the output-pair multiplicity function factors as

A
t,u
	​

(χ,ψ)B
t,u
	​

(χ,ψ).

Therefore L
t
	​

,L
u
	​

 are orthogonal exactly when

A
t,u
	​

(χ,ψ)B
t,u
	​

(χ,ψ)=0

for every nontrivial character pair (χ,ψ).

This produces an exact algebraic target: for every pair t,u, the Fourier supports of the two permutation graphs must be complementary away from the trivial character.

It may permit coupling between small and large prime factors that is impossible in a tensor product. However, generic random permutations have very few exact Fourier zeros, so randomness alone is unlikely to solve these equations. A construction would need highly structured complementary spectral supports.

No such family of size c
n
	​

 is produced here.

12. Minimal-counterexample and induction attacks

Fix a proposed constant c. Suppose n is a minimal large integer with

f(n)<c
n
	​

.
Product induction fails by exponent loss

If n=ab, minimality gives at most

f(a)≥c
a
	​

,f(b)≥c
b
	​

.

The product construction yields only

f(n)≥cmin(
a
	​

,
b
	​

).

For a balanced factorization a,b≍
n
	​

, this is only cn
1/4
. Thus induction through products halves the exponent.

PBD induction fails by scale mismatch

If a block has order b≍
n
	​

, minimality at order b gives only

f(b)≥c
b
	​

≍n
1/4
,

whereas the PBD closure requires c
n
	​

 local MOLS. Thus ordinary induction on block order is also too weak.

A minimal counterexample would have to be attacked with ingredients having linear-quality MOLS, not merely smaller instances of the same square-root assertion.

13. Disproof routes

To disprove (U), one needs an infinite sequence n
j
	​

→∞ satisfying

n
j
	​

	​

f(n
j
	​

)
	​

⟶0.

No such sequence is produced.

Orders with a persistent small prime-power factor, especially

n=2m,

are natural stress cases because:

direct products give only one square from the factor 2;

all CRT-affine constructions have the same bottleneck;

cyclic translation constructions admit no orthogonal pair;

unequal blow-ups cannot repair the factor.

None of these facts is an upper bound on arbitrary MOLS.

A modular-incidence attack also stalls. If p∣n, the fiber incidence vectors of an OA have very special inner products over F
p
	​

: same-column fibers have inner product 0, while fibers from distinct columns have inner product 1. Zero-sum combinations form a large isotropic system, but modular dependencies can be substantial. The resulting rank calculations do not give an o(
n
	​

) upper bound.

The usual real rank calculation gives only f(n)≤n−1, which is far too weak to falsify (U).

14. Concrete computational falsification tests

Finite computation cannot settle the asymptotic quantifiers, but it can reject overly strong intermediate claims.

OA search

For fixed n,r, search directly for an OA(n
2
,r+2,n,2). Fix the first two columns as row and column coordinates, then impose pair-projection constraints on the remaining columns. Symmetry reduction may fix one Latin square to reduced form, but it may not assume that square is cyclic.

PBD target search

For fixed r,n, solve the exact-cover problem whose universe is E(K
n
	​

) and whose candidate sets are edge sets of cliques of orders in K
r
	​

. Failure for many n≍r
2
 would falsify the strong clique-decomposition target (CD), though not the original MOLS assertion.

Hypergraph extension search

Given an OA with k columns, test whether its associated regular linear k-partite hypergraph has an n-edge-coloring. This separates “bad” OAs that cannot be extended from potentially pseudorandom extendable ones.

Holey-template search

The finite search described above already shows that the simple translated hole mechanism is not universal.

Obligation ledger

The following have been proved directly here:

the OA, partition, transversal-design, and K
n,n
	​

-factorization reformulations;

the upper bound f(n)≤n−1;

the equivalence of the square-root assertion with N(r)=O(r
2
);

the prime-power construction and its idempotent version;

the product construction;

the PBD closure lemma;

a three-prime-power clique-decomposition target with no elementary congruence obstruction;

explicit PBDs of orders q
2
+t and q
2
−q+t;

the smallest-factor obstruction for coordinatewise and CRT-affine constructions;

the cyclic translation obstruction in even order;

the impossibility of unequal cluster inflation in the natural blow-up model;

the subgroup obstruction to truncating finite-field squares;

the hypergraph 1-factorization reformulation and a self-contained nonextendable cyclic example;

the holey difference-template construction and its necessary inequality h(k−2)≤q;

the Fourier characterization for separable permutation constructions.

The unresolved obligations are concentrated in three possible routes:

Constructive design route: prove a quadratic-scale prime-power clique decomposition.
	​

Direct route: construct and repeatedly factor pseudorandom OA hypergraphs up to k=c
n
	​

.
	​

Disproof route: find an infinite family with a genuine o(
n
	​

) upper bound.
	​


None of the attacks completes any of these obligations, so the exact original assertion is not resolved.
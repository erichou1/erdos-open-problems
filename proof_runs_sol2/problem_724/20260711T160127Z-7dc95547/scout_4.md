Offline attack report

I obtained no proof or disproof of the stated asymptotic claim. The strongest output is a set of exact reformulations, two sharp square-root barriers, and a concrete completion problem whose first unresolved perturbation is already highly structured.

Throughout,

f(n)≫n
1/2

means that there are absolute constants c>0 and N such that

f(n)≥c
n
	​

(n≥N).
1. Four exact reformulations

Suppose L
1
	​

,…,L
k
	​

 are MOLS of order n, and set r=k+2. For every cell (x,y), form the word

(x,y,L
1
	​

(x,y),…,L
k
	​

(x,y))∈[n]
r
.

The resulting set C has n
2
 words, and any two coordinate positions contain every ordered pair of symbols exactly once.

Consequently, the following are equivalent.

There are k MOLS of order n.

There is an orthogonal array with n
2
 rows, r=k+2 columns, alphabet size n, and strength 2.

There is a code

C⊆[n]
r
,∣C∣=n
2
,

such that distinct codewords agree in at most one coordinate.

The complete balanced r-partite graph with n vertices in each part has a decomposition into copies of K
r
	​

, each copy using one vertex from each part.

The code in item 3 meets the elementary Singleton bound exactly, so the problem asks for nonlinear n-ary MDS codes of dimension 2 and length ≫
n
	​

, for every alphabet size n.

There is also a probability formulation. On a uniform probability space Ω of n
2
 atoms, one seeks r uniform random variables

X
1
	​

,…,X
r
	​

:Ω→[n]

such that every pair (X
i
	​

,X
j
	​

) is uniform on [n]
2
. Since ∣Ω∣=n
2
, every pair determines the atom of Ω uniquely.

2. Elementary upper bounds

Count unordered pairs of codewords that agree in a coordinate. Each coordinate contributes

n(
2
n
	​

)

such pairs. Since two codewords agree in at most one coordinate,

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

Hence

r(n−1)≤n
2
−1=(n−1)(n+1),

so

r≤n+1,f(n)≤n−1.

This bound is insensitive to the arithmetic of n, so it offers no route to disproving the square-root claim along composite orders.

3. Idempotent MOLS and a lossless gluing operation

Call a Latin square L idempotent when

L(x,x)=x

for every symbol x. Let g(n) be the maximum number of mutually orthogonal idempotent Latin squares of order n.

Lemma 1

For n≥2,

f(n)−1≤g(n)≤f(n).
Proof

The second inequality is immediate.

Given k=f(n) MOLS, distinguish one square L
0
	​

 and fix one of its symbols a. The cells on which L
0
	​

=a contain one cell in every row and every column.

For every other square L
i
	​

, orthogonality with L
0
	​

 implies that L
i
	​

 takes all n symbols exactly once on these cells. Thus these cells form a common transversal of L
1
	​

,…,L
k−1
	​

.

Permute columns to move this transversal to the main diagonal, then relabel the symbols of each square separately so that its diagonal becomes 1,2,…,n. This produces k−1 idempotent MOLS. ∎

Thus

f(n)≫
n
	​

⟺g(n)≫
n
	​

.
Lemma 2

For n≥2,

g(n)≤n−2.
Proof

Suppose g(n)=t, so the associated code has r=t+2 coordinates. Idempotence gives the n codewords

(a,a,…,a),a∈[n].

If r=n+1, equality holds in the preceding pair count. Therefore every pair of distinct codewords must agree in exactly one coordinate. But two distinct diagonal codewords agree in no coordinate. Hence r

=n+1, so r≤n and t≤n−2. ∎

Pairwise balanced design closure

A pairwise balanced design, abbreviated PBD, is a set V together with blocks B⊆2
V
 such that every pair of distinct points lies in exactly one block.

Lemma 3

If every block B∈B supports k idempotent MOLS, then V supports k idempotent MOLS.

Proof

On every block B, choose local idempotent MOLS

L
1
B
	​

,…,L
k
B
	​

.

Define globally

L
i
	​

(x,x)=x,

and, for x

=y, let B be the unique block containing x,y, and put

L
i
	​

(x,y)=L
i
B
	​

(x,y).

Fixing x, the unique block containing x,z reduces the equation L
i
	​

(x,y)=z to one local Latin-square equation. Hence every row and column is a permutation.

Likewise, for u

=v, any cell producing the ordered pair (u,v) must lie in the unique block containing u,v, where local orthogonality gives uniqueness. The case u=v is handled by idempotence. ∎

For a prime power q, over F
q
	​

 the squares

L
a
	​

(x,y)=ax+(1−a)y,a∈F
q
	​

∖{0,1},

are idempotent MOLS. Indeed, both coefficients are nonzero, and for a

=b the relevant determinant is

a(1−b)−b(1−a)=a−b

=0.

Therefore

g(q)≥q−2.

This gives a clean sufficient target:

Construct, for every sufficiently large n, a PBD on n points whose nontrivial block sizes are prime powers at least c
n
	​

+2.

That would prove the original claim.

4. The PBD route has an intrinsic square-root ceiling

The previous reduction is not merely one possible route. It operates exactly at its extremal scale.

Fisher-type inequality for PBDs

Consider a nontrivial PBD on v points, meaning that V itself is not a block. Let b be the number of blocks.

Then

b≥v.

To prove this, let A be the point-block incidence matrix. Suppose a vector (z
x
	​

)
x∈V
	​

 satisfies

x∈B
∑
	​

z
x
	​

=0

for every block B. Let r
x
	​

 be the number of blocks containing x, and let S=∑
x
	​

z
x
	​

. Summing the block equations over blocks containing x gives

0=r
x
	​

z
x
	​

+
y

=x
∑
	​

z
y
	​

=(r
x
	​

−1)z
x
	​

+S.

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

Summing over x forces S=0, and then every z
x
	​

=0. Thus A has row rank v, so b≥v.

Now suppose every block supports k idempotent MOLS. By Lemma 2, every block has size at least k+2. Therefore

(
2
v
	​

)=
B∈B
∑
	​

(
2
∣B∣
	​

)≥b(
2
k+2
	​

)≥v(
2
k+2
	​

).

Consequently,

(k+1)(k+2)≤v−1.

Thus any nontrivial PBD gluing construction necessarily satisfies

k<
v
	​

.

So PBD gluing can potentially prove the requested lower bound, but it cannot prove a larger-order bound. It must construct designs near the Fisher threshold, with roughly v blocks of size roughly 
v
	​

.

A parity obstruction inside the prime-power-block route

For every point x,

B∋x
∑
	​

(∣B∣−1)=v−1.

If v is even, the right side is odd. Hence every point lies in an odd number of even-sized blocks.

If all block sizes are prime powers, every even block must have order 2
a
. Thus, for even v, the powers-of-two blocks must cover every point. A construction using only odd prime-sized blocks cannot work.

This is a genuine local divisibility constraint on the PBD strategy, although it is not an obstruction to arbitrary MOLS.

5. Standard recursive ideas do not approach the target
Direct products

If there are k MOLS of orders m and n, taking ordered pairs of their symbols gives k MOLS of order mn. Thus

f(mn)≥min{f(m),f(n)}.

For balanced prime powers m,n≍
mn
	​

, this proves a square-root bound. But for

N=2p

with p a large odd prime, it gives only

f(2p)≥f(2)=1.

The family 2p is therefore a useful stress test: any proof must genuinely overcome a fixed small factor.

Ordinary induction also fails structurally. Even assuming

f(d)≥c
d
	​


for all smaller d, the product construction for n=ab yields only

min{c
a
	​

,c
b
	​

},

which is O(n
1/4
) for balanced factors.

The same issue affects PBD induction. If the only information available on a proper block B is

g(∣B∣)≥c
∣B∣
	​

,

then it cannot supply c
n
	​

 global squares unless ∣B∣ is comparable to n. The useful blocks must have much denser families, essentially g(∣B∣)=Θ(∣B∣), as prime powers do.

6. Broad algebraic constructions have a small-factor barrier
Translation-type squares

Let the symbols be Z
n
	​

, and consider

L
π
	​

(x,y)=x+π(y),

where π is a permutation. Two such squares L
π
	​

,L
σ
	​

 are orthogonal exactly when

y⟼π(y)−σ(y)

is a permutation.

If n is even, no such pair exists. Indeed,

y
∑
	​

(π(y)−σ(y))≡0(modn),

whereas the sum of the values of any permutation of Z
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

Thus this entire nonlinear-looking translation model produces at most one square for even n.

Abelian coset constructions

Let G be an abelian group of order n
2
. Suppose the coordinate partitions arise as cosets of subgroups

H
1
	​

,…,H
r
	​

,∣H
i
	​

∣=n,

with

H
i
	​

∩H
j
	​

={0}

for i

=j. These give pairwise orthogonal partitions.

Write

n=
p
∏
	​

p
a
p
	​

.

Inside the p-primary component G
p
	​

, each H
i
	​

 has a subgroup of order p
a
p
	​

, and these subgroups are pairwise disjoint outside the identity. Therefore

r(p
a
p
	​

−1)≤p
2a
p
	​

−1,

so

r≤p
a
p
	​

+1.

Since k=r−2,

k≤
p
a
p
	​

∥n
min
	​

(p
a
p
	​

−1).

For n=2p, this gives k≤1 throughout the entire abelian coset model.

This is not an upper bound on f(2p). It proves only that group-linear, ring-linear, subgroup-spread, and related shared-translation constructions cannot settle the problem.

7. A sharp embedding problem at the square-root threshold

The most concrete intermediate target found is an incomplete transversal design.

Define ITD(r,n;q) to mean an orthogonal array of order n with r columns that contains, on designated q-element subalphabets in every coordinate, an orthogonal array of order q with the same r columns.

Equivalently, it is a K
r
	​

-decomposition of the balanced complete r-partite graph of group size n containing a K
r
	​

-decomposition on designated q-subsets.

Take

r=q+1.
Exact counting obstruction

Suppose n>q and ITD(q+1,n;q) exists. Call the designated symbols old and the remaining n−q symbols new.

Any row outside the subarray contains at most one old symbol, because every pair of old symbols in distinct coordinates is already used inside the subarray.

For a fixed coordinate i and a fixed old symbol a, there are exactly n−q outside rows with X
i
	​

=a: pair a with each new symbol in any other fixed coordinate.

Hence the number of outside rows containing exactly one old symbol is

(q+1)q(n−q).

The total number of outside rows is

n
2
−q
2
.

Therefore the number of all-new rows is

n
2
−q
2
−(q+1)q(n−q)=(n−q)(n−q
2
).

This must be nonnegative. Since n>q,

n≥q
2
.
	​


Thus q
2
 is a necessary threshold for embedding a complete order-q structure with q+1 coordinates.

The threshold value exists

Let q be a prime power. Use F
q
2
	​

 as the alphabet, and index q+1 coordinates by

F
q
	​

∪{∞}.

For x,y∈F
q
2
	​

, define

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

Any two coordinates determine x,y, so this is an order-q
2
 orthogonal array with q+1 columns.

Restricting to x,y∈F
q
	​

 gives an order-q subarray. Therefore

ITD(q+1,q
2
;q)

exists.

The counting threshold is consequently sharp.

The strongest concrete sufficient target

Prove:

ITD(q+1,n;q) exists for every prime power q and every n≥q
2
.
	​


This would imply the original statement. Indeed, the prime-in-a-dyadic-interval theorem says that for every real x≥2, there is a prime between x and 2x. For large n, choose a prime

4
n
	​

	​

<q<
2
n
	​

	​

.

Then n≥q
2
, and the proposed embedding theorem would give

f(n)≥q−1>
4
n
	​

	​

−1≫
n
	​

.

This embedding statement is stronger than the original problem, so its failure would not disprove the original claim.

Structure just above the threshold

Write

n=q
2
+t.

Every new symbol occurs in exactly t all-new rows. Indeed, a new symbol occurs in n rows total, and it occurs in exactly q
2
 one-old rows: there are q other coordinates and q possible old symbols in each.

Thus the all-new rows form a (q+1)-partite linear hypergraph in which every new vertex has degree exactly t.

At t=0, there are no all-new rows.

At t=1, the all-new rows must form one perfect matching across the q+1 new groups. Therefore the first perturbation

ITD(q+1,q
2
+1;q)
	​


has an especially rigid form: the order-q
2
 endpoint construction must be modified so that exactly one common transversal of all-new symbols remains uncovered by the one-old rows.

This is the smallest focused target generated by the embedding attack.

8. Anchored matching-frame reformulation

Let

m=n−q,r=q+1.

For each coordinate i, let N
i
	​

 be its m new symbols.

For every old symbol a in coordinate i, the m rows containing a outside the core select one new symbol from every other coordinate. In every other coordinate, these m symbols are all distinct.

Thus every pair (i,a) defines a perfect matching across the q new groups

N
j
	​

,j

=i.

Call the collection of all these matchings an anchored matching frame if no pair of new symbols in two groups occurs more than once.

For any fixed pair N
j
	​

,N
k
	​

, anchors in the other q−1 coordinates contribute

q(q−1)

perfect matchings between N
j
	​

 and N
k
	​

. Consequently the unused bipartite graph between N
j
	​

,N
k
	​

 is

m−q(q−1)=n−q
2
=t

regular.

Hence ITD(q+1,n;q) is equivalent to:

an anchored matching frame on q+1 groups of size m;

a decomposition of the resulting t-regular residual multipartite graph into copies of K
q+1
	​

.

This separates the problem into a highly structured matching-frame construction and a residual exact-decomposition problem.

9. Direct hypergraph perfect-matching formulation

Fix r. Define a hypergraph H
r,n
	​

 as follows.

Its vertices are all specifications

(i,j,a,b),1≤i<j≤r,a,b∈[n].

A word x=(x
1
	​

,…,x
r
	​

)∈[n]
r
 defines a hyperedge

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

Then:

every edge has size

s=(
2
r
	​

);

every vertex has degree

d=n
r−2
;

two distinct compatible vertices have codegree at most

n
r−3
=
n
d
	​

.

A perfect matching in H
r,n
	​

 has exactly n
2
 edges and is precisely an orthogonal array with r columns.

Thus the original problem is exactly the assertion that this extremely symmetric hypergraph has a perfect matching for

r=⌊c
n
	​

⌋+2.

The normalized codegree is only 1/n, which looks favorable. However, the edge size is

(
2
r
	​

)=Θ(n)

at the desired scale. The overlap correction among the neighborhoods of the vertices of one edge is therefore no longer negligible:

n
s
	​

=Θ(1).

This is where fixed-uniformity matching heuristics cease to apply directly.

Failure of naive greedy selection

For a fixed word, the number of words agreeing with it in at least two coordinates is

D=
j=2
∑
r
	​

(
j
r
	​

)(n−1)
r−j
=n
r
−(n−1)
r
−r(n−1)
r−1
.

For r=O(
n
	​

),

D∼(
2
r
	​

)n
r−2
.

A maximal greedy code therefore gives only about

D
n
r
	​

≍
r
2
n
2
	​

.

At r=c
n
	​

, this is only O(n) codewords, while n
2
 are required.

The local codegree is small, but naive packing loses a factor of order n.

Failure of unstructured random partitions

Fix one balanced variable X:Ω→[n], where ∣Ω∣=n
2
. The number of balanced labeled variables is

(n!)
n
(n
2
)!
	​

,

while the number orthogonal to X is

(n!)
n
.

Thus a uniformly random balanced variable is orthogonal to X with probability

(n
2
)!
(n!)
2n
	​

=exp(−n
2
+O(nlogn)).

A first-moment clique heuristic in the graph of balanced partitions therefore reaches only logarithmically many coordinates. Any successful probabilistic construction must preserve substantial algebraic or decompositional structure; independent random partitions are far too sparse.

10. Counterexample and upper-bound attacks

The most natural candidate family for a disproof is

n=2p,p large prime.

All elementary algebraic constructions collapse there, but none of the following gives an upper bound on arbitrary MOLS:

The real incidence-space argument gives only f(n)≤n−1.

Reduction modulo 2 makes the incidence Gram matrix highly singular; no useful lower bound on its rank follows from the orthogonal-array axioms alone.

Coarse-graining each 2p-symbol coordinate into a 2-symbol and a p-symbol coordinate produces pairwise independent variables of higher index, not MOLS of orders 2 and p.

The parity obstruction applies only to translation-type quasigroups.

The small-Sylow bound applies only to abelian coset constructions.

Therefore no arithmetic invariant capable of proving

f(2p)=o(
p
	​

)

was found.

11. Finite falsification tests

For fixed q,n, the embedding problem is an exact-cover instance.

Use r=q+1 coordinates, with q old and m=n−q new symbols in each coordinate. Candidate outside rows are exactly the r-tuples containing at most one old symbol.

There are

m
r
+rqm
r−1

candidate rows. The residual pair constraints number

(
2
r
	​

)(n
2
−q
2
),

and exactly

n
2
−q
2

rows must be selected.

For the first nontrivial square-root perturbation,

(q,n)=(3,10),

this gives:

r=4,m=7,
7
4
+4⋅3⋅7
3
=6517

candidate rows,

(
2
4
	​

)(10
2
−3
2
)=546

exact pair constraints, and 91 selected rows.

An unsymmetrized branch-and-bound formulation is already poorly conditioned at this size. Useful symmetry-breaking should fix:

the order-q core;

one all-new perfect matching when n=q
2
+1;

permutations of coordinates;

permutations of old symbols;

permutations of new symbols in several groups.

Small q=2 checks

The counting obstruction gives n≥4.

n=4 exists by the field construction.

n=5 is witnessed by the Latin square

	​

0
1
2
3
4
	​

1
0
3
4
2
	​

3
4
0
2
1
	​

4
2
1
0
3
	​

2
3
4
1
0
	​

	​

.

Its top-left 2×2 subarray is the order-2 Latin square.

n=6 is witnessed by addition modulo 6, whose rows and columns indexed by {0,3} form an order-2 subsquare.

Thus the first three permissible orders do not falsify the embedding target.

12. Ranked intermediate targets
Target A: first perturbation of the sharp embedding threshold

Prove or disprove, uniformly in prime powers q,

ITD(q+1,q
2
+1;q).

The all-new component is forced to be one perfect matching, so every remaining obligation is explicit.

Target B: full embedding conjecture

Prove

ITD(q+1,n;q)for all n≥q
2
.

This would prove the original statement with an absolute constant.

Target C: critical PBD decomposition

Find c>0 such that every large n admits an edge decomposition

K
n
	​

=
α
⨆
	​

K
s
α
	​

	​

,

where every s
α
	​

 is a prime power and

s
α
	​

≥c
n
	​

+2.

For even n, powers-of-two blocks must cover every vertex.

Target D: direct symmetric-hypergraph absorption

Construct a perfect matching in H
r,n
	​

 for

r=⌊c
n
	​

⌋+2.

An argument must handle hyperedge size Θ(n), exact rather than approximate coverage, and a residual structure supporting absorption.

Target E: genuine arithmetic upper invariant

To disprove the statement, derive an invariant applying to all orthogonal arrays, not merely linear or translation-invariant ones, and show along some infinite family—most plausibly n=2p—that

r=o(
n
	​

).

No candidate invariant of this strength emerged.

Status

The original statement remains unresolved in this analysis.

The main concrete advances are:

Nontrivial PBD recursion is intrinsically capped at k<
n
	​

,
	​


and

ITD(q+1,n;q) requires n≥q
2
, with equality attainable.
	​


Thus the exponent 1/2 appears simultaneously as the extremal scale for block-design gluing and as the sharp threshold for embedding a complete prime-power core.
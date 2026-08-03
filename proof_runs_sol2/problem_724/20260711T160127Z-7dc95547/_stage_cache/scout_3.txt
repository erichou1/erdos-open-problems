Interpretation and logical status

I interpret

f(n)≫n
1/2

as the assertion

∃c>0 ∃N ∀n≥N,f(n)≥c
n
	​

.
(S)

Without this standard interpretation, the symbol ≫ is undefined in the supplied statement.

The attacks below neither prove nor disprove (S). They isolate a concrete positive design-theoretic target, identify hostile sequences for existing constructions, and give finite falsification frameworks.

1. Exact reformulations

Let X be an n-element set. A Latin square is a map

L:X
2
→X

such that each map y↦L(x,y) and x↦L(x,y) is a bijection. Two Latin squares L,M are orthogonal when

(x,y)⟼(L(x,y),M(x,y))

is a bijection X
2
→X
2
.

1.1 Orthogonal-array formulation

A family L
1
	​

,…,L
t
	​

 of MOLS gives

C={(x,y,L
1
	​

(x,y),…,L
t
	​

(x,y)):x,y∈X}⊆X
t+2
.

Projection onto any two coordinates is a bijection onto X
2
.

Conversely, any subset C⊆X
k
 of size n
2
 whose projection onto every pair of coordinates is bijective gives k−2 MOLS after choosing two coordinates as row and column coordinates.

Thus

f(n)+2

is the maximum number k of columns in an index-one orthogonal array of strength 2 and alphabet size n.

Equivalently, it is the maximum k for which there is a code

C⊆X
k
,∣C∣=n
2
,

such that two distinct codewords agree in at most one coordinate.

This turns the problem into:

Must there always exist n
2
 words over an n-letter alphabet, of length Ω(
n
	​

), with pairwise agreement at most one?

1.2 Universal upper bound

The orthogonal-array formulation gives

f(n)≤n−1.
(1)

Proof: suppose the array has k columns. For each column j and symbol a, let e
j,a
	​

∈R
n
2
 be the indicator vector of rows having symbol a in column j. Set

u
j,a
	​

=e
j,a
	​

−
n
1
	​

1.

For each fixed j, these vectors span an (n−1)-dimensional space U
j
	​

. If i

=j, every ordered symbol pair occurs exactly once, giving

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
−1)-dimensional space perpendicular to 1. Hence

k(n−1)≤n
2
−1=(n−1)(n+1),

so k≤n+1, yielding (1).

This bound is far too weak to decide the 
n
	​

 scale.

2. Positive constructions and their limitations
2.1 Prime-power orders

For every prime power q, a field F
q
	​

 exists. For a∈F
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
=b, the equations

ax+y=u,bx+y=v

have a unique solution because a−b

=0. Therefore the q−1 squares L
a
	​

 are mutually orthogonal.

Together with (1),

f(q)=q−1
(2)

for every prime power q.

Thus the proposed lower bound is much weaker than what holds on prime powers. The entire difficulty is interpolation between those orders.

2.2 Direct products

If a and b are positive integers, then

f(ab)≥min(f(a),f(b)).
(3)

Indeed, given MOLS A
i
	​

 of order a and B
i
	​

 of order b, define

C
i
	​

((x,u),(y,v))=(A
i
	​

(x,y),B
i
	​

(u,v)).

Consequently, if n=qr with q,r comparable prime powers, then

f(n)≥min(q−1,r−1)≍
n
	​

.

For example, if

λ
n
	​

≤q,r≤λ
−1
n
	​

,

then

f(n)≥λ
n
	​

−1.

But tensoring cannot produce more than the minimum. If one attempts to use squares indexed by pairs (i,j), two product squares are orthogonal only when both their first indices and their second indices differ. A pairwise compatible set of index pairs is therefore a matching and has size at most min(f(a),f(b)).

So the direct-product method fundamentally fails on orders such as

n=2p,p an odd prime,

where it yields only one square.

3. Exact logic of a counterexample

Set

R(n)=
n
	​

f(n)
	​

.

Then

(S)⟺
n→∞
liminf
	​

R(n)>0.

Therefore a disproof requires a sequence n
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

There is no individual “smallest counterexample” to the original asymptotic statement. A smallest counterexample exists only after fixing particular constants c,N in the stronger assertion

f(n)≥c
n
	​

(n≥N).

Finite computation can refute a proposed pair (c,N), but no finite list of values can refute (S).

4. Hostile sequence n=2p

The family n=2p is a particularly clean test because several broad algebraic constructions degenerate there.

4.1 Cyclic-linear squares

For a∈(Z/nZ)
×
, consider

L
a
	​

(x,y)=ax+y(modn).

Two such squares are orthogonal exactly when a−b is also a unit.

Let p
0
	​

 be the smallest prime divisor of n. Reduction modulo p
0
	​

 shows that the elements of any admissible set A must be distinct nonzero residues modulo p
0
	​

. Thus

∣A∣≤p
0
	​

−1.

This is attained by A={1,…,p
0
	​

−1}, because all its elements and nonzero differences are coprime to n. Therefore

max{cyclic-linear MOLS of order n}=p
0
	​

−1.
(4)

In particular, for every even n, this subclass gives only one square.

Hence cyclic-linear constructions have

n
	​

number produced
	​

→0

along n=2p. This falsifies the entire cyclic-linear strategy, not the original statement.

4.2 Group tables of order 2p

An orthogonal mate of a Latin square partitions its cells into n disjoint transversals. Thus a square with no transversal has no orthogonal mate.

Suppose a finite group G admits a surjective homomorphism

χ:G→Z/2Z

whose kernel has odd order. Assume the Cayley table of G has a transversal. Such a transversal has cells

(x,π(x)),x∈G,

where π is a permutation, and the products xπ(x) also enumerate G. Applying χ and summing in Z/2Z,

x∈G
∑
	​

χ(xπ(x))=
x
∑
	​

χ(x)+
x
∑
	​

χ(π(x))=0.

But because the products enumerate G,

x∈G
∑
	​

χ(xπ(x))=
g∈G
∑
	​

χ(g)=∣kerχ∣≡1(mod2),

a contradiction.

For a group of order 2p, where p is an odd prime, the Sylow p-subgroup is unique: its number divides 2 and is congruent to 1(modp). The quotient has order 2, and its kernel has odd order p. Therefore:

No group table of order 2p has an orthogonal mate.
(5)

The same holds for any isotope of such a group table.

Again, this is not an upper bound on f(2p). It proves that any large family at order 2p must be genuinely non-group-based.

5. Transversals and orthogonal resolutions

Fix a Latin square L. A resolution into transversals is a partition of its n
2
 cells into n transversals.

An orthogonal mate M of L gives such a resolution: the cells carrying each fixed symbol of M form a transversal of L. Conversely, labeling the classes of a transversal resolution gives an orthogonal mate.

Two resolutions are orthogonal exactly when every transversal from one meets every transversal from the other in one cell.

Let ρ(L) be the maximum number of pairwise orthogonal resolutions of L. Then, for n>1,

f(n)=1+
L
max
	​

ρ(L).
(6)

This is an exact counterexample-search formulation.

For the candidate sequence n=2p, a disproof of (S) would follow from

L of order 2p
max
	​

ρ(L)=o(
p
	​

).
(7)

The group-table argument proves ρ(L)=0 for a restricted class of L, but the maximum in (7) ranges over every Latin square.

If τ(L) denotes the total number of transversals of L, then

ρ(L)≤
n
τ(L)
	​

,

because distinct orthogonal resolutions cannot share a transversal. Thus the stronger uniform estimate

L
max
	​

τ(L)=o(n
3/2
)

along some sequence would disprove (S). This appears too strong as a practical route; controlling compatible resolutions rather than merely counting transversals is the more precise target.

6. Pairwise balanced designs: the strongest positive reduction

A pairwise balanced design PBD(v,K) consists of a v-element point set and blocks whose sizes lie in K, such that every pair of distinct points lies in exactly one block. Equivalently, it is a decomposition of the edges of K
v
	​

 into cliques K
k
	​

, k∈K.

6.1 Idempotent MOLS

Let g(n) be the maximum number of mutually orthogonal idempotent Latin squares, where

L(x,x)=x.

Then

f(n)−1≤g(n)≤f(n).
(8)

For the nontrivial inequality, take t=f(n) MOLS and select one square L
0
	​

. The cells containing a fixed symbol in L
0
	​

 form a common transversal of the other t−1 squares. Permute rows and columns to put this transversal on the diagonal, then independently relabel the symbols of each remaining square so that its diagonal entry in position x is x.

For a prime power q, the squares

Q
a
	​

(x,y)=ax+(1−a)y,a∈F
q
	​

∖{0,1},

are idempotent and mutually orthogonal. Hence

g(q)≥q−2.
(9)
6.2 PBD closure

If a PBD(v,K) exists, then

g(v)≥
k∈K
min
	​

g(k).
(10)

Proof: take t=min
k∈K
	​

g(k), and put t idempotent MOLS on every block. For x

=y, let B(x,y) be the unique block containing them and define

Q
i
	​

(x,y)=Q
i
B(x,y)
	​

(x,y),Q
i
	​

(x,x)=x.

Idempotence and the unique-block property imply that each Q
i
	​

 is Latin. Given two outputs u

=v, their unique containing block identifies the local square in which orthogonality gives a unique input pair. Equal outputs arise only from a diagonal input. Thus the global squares are mutually orthogonal.

Consequently:

If K consists of prime powers, then

f(v)≥
k∈K
min
	​

(k−2).
(11)

This turns the original problem into a concrete clique-decomposition problem.

7. A precise sufficient target

For each sufficiently large n, let q be the largest power of 2 satisfying

q≤
n
	​

.

Then

q
2
≤n<4q
2
andq>
2
n
	​

	​

.

Define

K
q
	​

={k:q≤k≤2q, k is a prime power}.

Consider the following statement:

For every sufficiently large power of 2 q and every v∈[q
2
,4q
2
), there is a PBD(v,K
q
	​

).
(P)

If (P) holds, then by (11),

f(v)≥q−2.

For q≥4,

q−2≥
2
q
	​

>
4
v
	​

	​

.

Thus (P) would prove the original assertion with, for example, c=1/4.

This is the sharpest positive intermediate target obtained here:

Decompose every K
v
	​

, with q
2
≤v<4q
2
, into cliques whose orders are prime powers between q and 2q.

It is sufficient but not necessary: MOLS might exist without arising from this PBD construction.

8. Necessary tests for the PBD target

For a PBD(v,K), define

α(K)=gcd{k−1:k∈K},β(K)=gcd{k(k−1):k∈K}.

Counting pairs through a fixed point gives

α(K)∣v−1.
(12)

Counting ordered pairs globally gives

β(K)∣v(v−1).
(13)

More precisely, if r
x,k
	​

 is the number of k-blocks through x, then

v−1=
k∈K
∑
	​

r
x,k
	​

(k−1).
(14)

If b
k
	​

 is the total number of k-blocks, then

(
2
v
	​

)=
k∈K
∑
	​

b
k
	​

(
2
k
	​

).
(15)

There is also Fisher’s inequality:

k∈K
∑
	​

b
k
	​

≥v,
(16)

provided no block is the entire point set.

For completeness, let A be the point-block incidence matrix. Then

AA
T
=J+diag(r
x
	​

−1).

If every point lies in at least two blocks, the diagonal term is positive definite and hence AA
T
 has rank v. Therefore the number of columns of A, namely the number of blocks, is at least v.

Conditions (12)–(16) are necessary, not sufficient.

9. A tempting sparse palette, and its explicit failure

Let q=2
a
, and let r
q
	​

 be the smallest odd power of 3 satisfying

r
q
	​

≥q.

Successive odd powers of 3 differ by a factor 9, so

q≤r
q
	​

<9q.

All three numbers

q,2q,r
q
	​


are prime powers.

Moreover,

gcd(q−1,2q−1)=1,

and since r
q
	​

≡3(mod4),

gcd{q(q−1),2q(2q−1),r
q
	​

(r
q
	​

−1)}=2.

Thus the elementary PBD divisibility conditions are automatically satisfied for the palette

{q,2q,r
q
	​

}.

It is tempting to ask for a PBD(v,{q,2q,r
q
	​

}) throughout q
2
≤v<4q
2
. This would also prove the desired bound. However, this sparse target is false.

Take

q=32,r
q
	​

=243,v=1026.

Suppose a PBD exists, with a,b,c blocks of sizes 32,64,243, and put

B=a+b+c.

Fisher gives B≥1026. Pair counting gives

496a+2016b+29403c=(
2
1026
	​

)=525825.

Equivalently,

525825=496B+1520b+28907c.

If c≥1, then

525825≥496⋅1026+28907=537803,

which is impossible. Hence c=0. But then the right-hand side

496B+1520b

is divisible by 16, while

525825≡1(mod16).

Contradiction.

Therefore

PBD(1026,{32,64,243})

does not exist.

This falsification shows that merely killing the two gcd obstructions is insufficient. A successful palette needs many more nearby block sizes to repair pair-count residues without forcing the number of blocks below Fisher’s bound.

10. Finite tests of the broader palette

I tested the broader set

K
q
	​

={k:q≤k≤2q, k a prime power}

for

q=4,8,16,32,64,128.

For every integer v with q
2
≤v<4q
2
, the following scalar necessary conditions were checked exactly:

v−1 is a nonnegative integer combination of the numbers k−1, k∈K
q
	​

.

(
2
v
	​

) is a nonnegative integer combination of (
2
k
	​

), k∈K
q
	​

.

The second representation can be chosen with at least v total blocks, as required by Fisher’s inequality.

α(K
q
	​

)=1 and β(K
q
	​

)=2.

The results were:

| q | ∣K
q
	​

∣ | α(K
q
	​

) | β(K
q
	​

) | Local failures | Global/Fisher failures |
|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 1 | 2 | 0 | 0 |
| 8 | 5 | 1 | 2 | 0 | 0 |
| 16 | 9 | 1 | 2 | 0 | 0 |
| 32 | 10 | 1 | 2 | 0 | 0 |
| 64 | 18 | 1 | 2 | 0 | 0 |
| 128 | 27 | 1 | 2 | 0 | 0 |

Thus no scalar arithmetic counterexample to target (P) appeared in these ranges.

This is only a feasibility test. It does not construct the blocks or enforce consistency between the local representations at different points.

11. Geometric interpolation attacks

Finite affine geometry gives several natural PBDs, but each introduces a block whose order is not controlled well enough.

11.1 Deleting collinear points

Start with the affine plane on F
q
2
	​

, whose lines form a PBD(q
2
,{q}). Delete s points lying on one line.

The remaining line intersections have sizes

q,q−1,q−s.

Therefore one obtains

PBD(q
2
−s,{q,q−1,q−s}).

To obtain Ω(q) global MOLS using PBD closure, all three block orders must support Ω(q) MOLS. The block q−s is fatal when s is close to q, and q−1 is not controlled merely because q is a prime power.

11.2 Adding points

Assign each of r≤q+1 new points to a different parallel class of the affine plane. Add a new point to every line in its assigned class, and add one extra block containing all new points. This yields

PBD(q
2
+r,{q,q+1,r}).

Pairs of old points remain covered by their original line. A new point and an old point lie together on the unique line of its assigned parallel class through the old point. Two new points lie only in the extra block.

Again, the blocks of orders q+1 and r obstruct an Ω(q) conclusion unless both are themselves “excellent” orders supporting linearly many MOLS.

11.3 Why induction does not repair this

Suppose the desired 
m
	​

 lower bound were already known for smaller block orders m≍
n
	​

. Applying it inside the blocks would give only

f(m)≫
m
	​

≍n
1/4
.

PBD closure would therefore produce only n
1/4
 global MOLS.

To obtain c
n
	​

 global MOLS from blocks of order m, one needs

f(m)≥c
n
	​

.

Since f(m)≤m−1, the blocks must have order Ω(
n
	​

), and they must support a number of MOLS linear in their own order. Prime powers have this property; the inductive hypothesis alone does not.

Thus naive induction necessarily loses the exponent by a factor of 1/2.

12. Exact finite-search formulations
12.1 Direct MOLS satisfiability model

For t proposed MOLS, use integer variables

A
s
	​

(r,c)∈{0,…,n−1},1≤s≤t.

Impose:

every row of every A
s
	​

 is all-different;

every column of every A
s
	​

 is all-different;

for every s<s
′
, the n
2
 values

nA
s
	​

(r,c)+A
s
′
	​

(r,c)

are all-different.

This system is satisfiable exactly when t MOLS of order n exist.

Useful symmetry breaking includes:

first row of every square fixed as 0,1,…,n−1;

first column of the first square fixed as 0,1,…,n−1.

An unsatisfiability certificate for t proves f(n)<t, but a disproof of the asymptotic statement would require a uniform infinite family of such certificates.

12.2 Resolution-graph model

For each isotopy class of Latin squares L:

enumerate all transversals of L;

enumerate exact covers of the cells by n transversals;

make each such resolution a graph vertex;

connect two vertices when every transversal in one meets every transversal in the other exactly once;

compute the clique number.

By (6),

f(n)=1+
L
max
	​

ω(R
L
	​

).

This is likely better suited to upper-bound searches because it separates the choice of the base square from compatible orthogonal mates.

12.3 Small exhaustive check

A row-by-row enumeration of every labeled Latin square, followed by maximum-clique computation in the orthogonality graph, gave:

n	Number of labeled Latin squares	Orthogonality-graph edges	Maximum clique
2	2	0	1
3	12	36	2
4	576	3456	3

Thus

f(2)=1,f(3)=2,f(4)=3,

consistent with the exact prime-power formula. This validates the finite encoding but provides no asymptotic evidence.

13. Failure ledger
Orthogonal-array and coding bounds

They give the exact general upper bound f(n)≤n−1, but no arithmetic-sensitive bound below 
n
	​

 on any infinite sequence.

Nearest-prime-power interpolation

A large family at an order q cannot simply be restricted to order n<q: deleting rows, columns, and symbols does not generally preserve the Latin property or orthogonality. There is no established monotonicity f(n+1)≥f(n).

Direct products

They prove the target for balanced products of excellent orders, but collapse to the smallest factor. The sequence 2p exposes the bottleneck.

Cyclic, ring-linear, and group-based constructions

They are severely obstructed at even orders, especially 2p. These are construction failures, not upper bounds for arbitrary Latin squares.

Minimal-counterexample induction

There is no natural reduction from an order n counterexample to a smaller order. PBD recursion also loses the exponent unless all constituent orders already have linearly many MOLS.

Affine-plane truncation and extension

These constructions introduce small remainder blocks or neighboring orders q±1, neither of which is guaranteed to support Ω(q) MOLS.

Sparse PBD palettes

The palette {q,2q,r
q
	​

} passes the elementary gcd tests but fails stronger pair-count plus Fisher constraints, explicitly at (q,v)=(32,1026).

Probabilistic selection

Choosing random Latin squares does not give a usable estimate: orthogonality is a global n
2
-cell condition, and no sufficiently dense orthogonality graph has been established. Random approximate clique decompositions would also have to be converted into exact decompositions without introducing small blocks.

Parity or residue invariants

The quotient-parity argument eliminates specific group tables. No invariant has been derived that bounds the number of compatible resolutions for every Latin square of order 2p. Such a uniform invariant would be a genuine negative breakthrough.

14. Remaining precise obligations

A positive resolution would follow from any one of the following.

PBD interval lemma: Prove target (P):

PBD(v,K
q
	​

)for all q
2
≤v<4q
2
,

where q is a sufficiently large power of 2 and K
q
	​

 is the set of prime powers in [q,2q].

Direct orthogonal-array construction: Construct, for every large n, a set

C⊆[n]
k
,∣C∣=n
2
,k≥c
n
	​

,

in which distinct words agree in at most one coordinate.

Large-block decomposition by excellent orders: Find a PBD of order n whose block orders are all Θ(
n
	​

) and each support a number of MOLS linear in its order.

A negative resolution would require:

an explicit sequence n
j
	​

→∞, plausibly n
j
	​

=2p
j
	​

 or another arithmetically hostile family; and

a uniform upper bound

L
max
	​

ρ(L)=o(
n
j
	​

	​

),

or another certificate proving

f(n
j
	​

)=o(
n
j
	​

	​

).

The current attacks provide neither. The broad PBD interval lemma remains the most concrete positive target, while the compatible-resolution parameter ρ(L) on orders 2p is the cleanest counterexample target.
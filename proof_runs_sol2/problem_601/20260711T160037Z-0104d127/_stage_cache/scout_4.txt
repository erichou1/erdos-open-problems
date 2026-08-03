Interpretation defect

The statement does not define “infinite path.” This materially affects the answer.

I will use the standard graph-theoretic interpretation:

G is a simple undirected graph.

An infinite path is a ray v
0
	​

,v
1
	​

,… of distinct vertices with v
n
	​

v
n+1
	​

∈E(G).

It need not be induced.

The order type of a subset of α is measured using the inherited ordinal order.

Under the induced-path interpretation, the statement is false for every infinite α: the complete graph on α has neither an induced infinite path nor an independent set of type α.

There is also a boundary convention concerning whether 0 counts as a limit ordinal. If it does, the assertion is trivially true at 0.

Everything below is conditional on the standard ray interpretation.

1. Exact structural reduction

Write P(α) for the assertion in the problem.

1.1 Finite-separator rank of rayless graphs

Define classes R
ξ
	​

 recursively:

R
0
	​

={G:G is finite}.

For ξ>0, put G∈R
ξ
	​

 when there is a finite set
S⊆V(G) such that every component of G−S lies in some
R
η
	​

 with η<ξ.

Lemma

A graph has no ray if and only if it belongs to some R
ξ
	​

.

Proof

If G∈R
ξ
	​

, induct on ξ. Suppose S witnesses membership. A ray uses only finitely many vertices of S, so a tail of the ray lies in one component of G−S, contradicting the induction hypothesis.

Conversely, suppose G belongs to no R
ξ
	​

. Some connected component H
0
	​

 also has no rank; otherwise the supremum of the component ranks would rank G.

Choose v
0
	​

∈H
0
	​

. Inductively, suppose H
n
	​

 is connected and unranked and v
n
	​

∈H
n
	​

. Some component H
n+1
	​

 of H
n
	​

−v
n
	​

 must be unranked; otherwise {v
n
	​

} and the ranks of the components would rank H
n
	​

. Since H
n
	​

 is connected, v
n
	​

 has a neighbor v
n+1
	​

∈H
n+1
	​

.

Then

v
0
	​

,v
1
	​

,v
2
	​

,…

is a ray. Hence every rayless graph has a finite-separator rank. □

This proof does not invoke any external structure theorem.

1.2 Forest representation

Recursively choose the finite separators in the preceding lemma. Place each separator in a node of a rooted decomposition forest, and make the components after its removal the child subtrees.

Every vertex eventually enters a finite separator, since otherwise its successive components would have strictly decreasing ordinal ranks forever.

Two vertices assigned to incomparable decomposition nodes cannot be adjacent.

Replace each finite separator bag by a finite chain of singleton nodes, attaching all child subtrees beneath the last node in that chain. This produces a rooted forest T such that:

every branch of T is finite, although branch lengths need not be uniformly bounded;

V(T)=V(G);

every edge of G joins comparable vertices of T.

Conversely, if T is a rooted forest with no infinite branch, its comparability graph is rayless. Indeed, removing a root separates its child subtrees, and induction on the well-founded tree rank applies.

Therefore:

Exact reformulation

Under the standard interpretation,

P(α)⟺every rooted forest order on α with no infinite branch has an antichain of order type α.
	​


The forward implication uses the comparability graph. The reverse implication uses the decomposition forest of a rayless graph: incomparable vertices are nonadjacent in the original graph.

This appears to be the cleanest exact reduction.

1.3 Finite ancestral set mapping

For a node x∈T, let

A(x)={y:y is a strict ancestor of x}.

Then every A(x) is finite. A set X is an antichain exactly when

A(x)∩X=∅for every x∈X.

Thus the problem is equivalently a free-set problem for a highly structured finite set mapping: the sets A(x) are finite, transitive, linearly ordered by ancestry, and admit no infinite ancestry chain.

An arbitrary finite set mapping is too general; the ancestral structure is essential.

2. Consequences of the forest reduction
2.1 Every rayless graph is countably colorable

Color each forest node by its depth. Comparable nodes have different depths, so each depth level is an antichain. Consequently every rayless graph has a proper coloring by ω colors.

Hence a sufficient ordinal condition is

α⟶(α)
ω
1
	​

,

meaning that every countable coloring of α has a color class of order type α.

This sufficient condition is far from necessary.

2.2 Every infinite initial ordinal satisfies the assertion
Cardinal antichain lemma

Every infinite rooted forest with no infinite branch has an antichain of the same cardinality as its vertex set.

Proof is by induction on tree rank. For each child subtree T
i
	​

:

if T
i
	​

 is infinite, take an antichain of size ∣T
i
	​

∣;

if T
i
	​

 is finite and nonempty, take one vertex.

The child subtrees are mutually incomparable, so the union is an antichain. Replacing each finite positive cardinal ∣T
i
	​

∣ by 1 does not change an infinite cardinal sum:

i
∑
	​

max(1,∣T
i
	​

∣
infinite part
	​

)=
i
∑
	​

∣T
i
	​

∣.

The same argument applies to a forest with multiple roots.

Therefore, if κ is an infinite initial ordinal, every rayless graph on κ has an independent set of cardinality κ. Any subset of κ of cardinality κ has order type exactly κ. Hence

P(κ) holds for every infinite initial ordinal κ.
	​


This isolates the real difficulty: ordinals strictly larger than their initial cardinal.

2.3 A further sufficient family

Let κ be an initial ordinal with

cf(κ)>ω.

For every positive integer n,

κ
n
⟶(κ
n
)
ω
1
	​

.

The proof is inductive.

For n=1, a countable union of sets of cardinality below κ has cardinality below κ.

For the successor step, split κ
n+1
 into blocks

B
ξ
	​

=[κ
n
ξ,κ
n
(ξ+1)),ξ<κ.

Inside each block, some color contains a copy of κ
n
. One color works in κ many blocks, yielding a monochromatic copy of

κ
n
⋅κ=κ
n+1
.

Thus

P(κ
n
) holds whenever cf(κ)>ω and 1≤n<ω.
	​


In particular this covers every finite power ω
1
n
	​

.

3. Finite simultaneous largeness

The separator rank gives a useful strengthening for countable pieces.

Lemma: finite profile preservation

Let G be rayless and let

A
0
	​

,…,A
m−1
	​

⊆V(G)

be infinite sets, where m<ω. Then G has an independent set I such that

∣I∩A
j
	​

∣=ℵ
0
	​

(j<m).
Proof

Induct simultaneously on the finite-separator rank for every finite m.

Choose a finite separator S, with lower-rank components C.

Let J be the set of indices j<m for which A
j
	​

∩C is infinite in at least one component. For each j∈J, choose one witnessing component. Only finitely many components are selected. Inside each such component, apply the induction hypothesis to all the A
j
	​

's that are infinite there.

For each j∈
/
J, every component meets A
j
	​

 finitely, but A
j
	​

−S is infinite. Hence A
j
	​

 meets infinitely many components. After discarding the finitely many previously selected components, the remaining component families are still infinite.

A finite family of infinite sets has pairwise disjoint infinite refinements. Choose disjoint infinite component families for the remaining j's, and in each chosen component take one vertex from the corresponding A
j
	​

.

All selected pieces lie in distinct components or are independent inside a component, so their union is independent. □

Consequence

For every positive integer m,

P(ω⋅m) holds.
	​


Partition ω⋅m into its m consecutive ω-blocks. An independent set meeting every block infinitely has order type ω⋅m.

4. A countable-family theorem and the case ω
2

The preceding lemma cannot be extended by replacing “finitely many” with “countably many” and retaining every requirement. There is, however, a weaker form that is exactly sufficient for ω
2
.

Lemma: infinitely many profiles survive

Let G be rayless and let A
0
	​

,A
1
	​

,… be infinite subsets of V(G). There is an independent set I for which

I∩A
n
	​

 is infinite

for infinitely many n.

Proof

Induct on finite-separator rank. Let C range over the components after deleting a finite separator, and set

M
C
	​

={n:A
n
	​

∩C is infinite}.

There are three cases.

Some M
C
	​

 is infinite.
Apply the induction hypothesis inside that component.

Every M
C
	​

 is finite, but ⋃
C
	​

M
C
	​

 is infinite.
In each component, apply finite profile preservation to the finitely many sets indexed by M
C
	​

. The union over all components works for infinitely many indices.

M=⋃
C
	​

M
C
	​

 is finite.
Reserve finitely many components witnessing every index in M. For n∈
/
M, every component meets A
n
	​

 finitely, so A
n
	​

 meets infinitely many components. A countable family of infinite sets has pairwise disjoint infinite refinements: enumerate ω×ω, choosing a fresh component at each step. Pick one A
n
	​

-vertex in each assigned component.

This gives an independent set meeting every A
n
	​

, n∈
/
M, infinitely, as well as the finitely many indices in M. □

Now write

ω
2
=
n<ω
⋃
	​

B
n
	​

,B
n
	​

=[ωn,ω(n+1)).

An X⊆ω
2
 has order type ω
2
 whenever X∩B
n
	​

 is infinite for infinitely many n. Therefore

P(ω
2
) holds.
	​


The argument does not yet iterate automatically to ω
3
: intersections of components with an ω
2
-block may have many intermediate order types, not merely finite or full.

5. Why finite solutions do not compactly fuse

Consider disjoint infinite stars S
n
	​

, with center c
n
	​

 and infinite leaf set L
n
	​

. Define

A
0
	​

={c
n
	​

:n<ω},A
n+1
	​

=L
n
	​

.

Every finite subfamily of the requirements

∣I∩A
n
	​

∣=ℵ
0
	​


can be met:

take infinitely many leaves in the finitely many relevant stars;

take centers from all the unused stars.

But no independent set meets every A
n
	​

 infinitely. Meeting L
n
	​

 infinitely forces omission of c
n
	​

 for every n, so I∩A
0
	​

=∅.

Thus finite-profile solutions do not admit a naive compactness argument. Any proof at higher ordinal powers must exploit that a full-order-type set may discard many blocks, rather than attempt to satisfy every block requirement.

6. The boundary α=ω
1
ω+2
	​


Let

κ=ω
1
	​

,β=κ
ω
,α=β⋅κ
2
=κ
ω+2
.
6.1 Countable coloring is insufficient

Partition β into

E
0
	​

=[0,κ),E
n
	​

=[κ
n
,κ
n+1
)(n≥1).

Every x<α has a unique representation

x=βξ+y,ξ<κ
2
,y<β.

Color x by the unique n such that y∈E
n
	​

.

The n-th color class has order type at most

κ
n+1
⋅κ
2
=κ
n+3
<κ
ω
<α.

Consequently

α↛(α)
ω
1
	​

.

This is only a failure of the coloring attack, not a graph counterexample.

6.2 Any obstruction must use unbounded finite heights

One has

ω
1
	​

=ω
ω
1
	​

,

and therefore

ω
1
ω+2
	​

=ω
ω
1
	​

⋅(ω+2)
.

Every ordinal of the form ω
δ
 is indivisible under finite colorings:

ω
δ
⟶(ω
δ
)
r
1
	​

(1≤r<ω).

This can be proved by induction on δ:

at a successor exponent, split into ω blocks of the preceding power;

at a limit exponent, one of finitely many colors succeeds for cofinally many smaller exponents.

If a forest representing a counterexample had branch lengths bounded by N, its N depth levels would be a finite partition of α. One level would have order type α, and that level would be an antichain.

Hence:

Any counterexample at ω
1
ω+2
	​

 must have branches of arbitrarily large finite length.
	​


Moreover, let L
n
	​

 be the set of nodes of depth n. In a counterexample:

otp(L
n
	​

)<αfor every n.

For every N<ω,

D
N
	​

=
n≥N
⋃
	​

L
n
	​


must nevertheless have order type α. Indeed, the first N levels form a finite union of sub-α sets. If D
N
	​

 also had order type below α, finitely many sub-α sets would cover α, contradicting finite indivisibility.

Thus the boundary problem reduces to a particularly sharp configuration:

T has no infinite branch;
otp(L
n
	​

)<α for every n;
otp(⋃
n≥N
	​

L
n
	​

)=α for every N;
yet every antichain has order type<α.
	​

	​


This is the principal unresolved fusion problem exposed by the reduction.

6.3 Minimal-rank counterexample constraints

Assume a counterexample exists at a fixed α, and choose one of least forest rank.

Then every proper child cone T
u
	​

 has

otp(V(T
u
	​

))<α.

Otherwise V(T
u
	​

), with its inherited ordinal order, would itself support a lower-rank counterexample of type α.

Therefore a minimal obstruction must assemble α from many smaller incomparable cones, but all possible choices of large local antichains must fail to amalgamate to type α. The obstruction cannot be concentrated in one large descendant subtree.

7. Failed or insufficient attacks
Infinite-degree derivative

Deleting all finite-degree vertices repeatedly is too coarse. The ordinary ray on ω has every vertex of finite degree, so the derivative becomes empty immediately even though the graph contains a ray.

Arbitrary finite-forward set mapping

Deleting finite-degree vertices gives an ordering in which each vertex has finitely many later neighbors. This does not characterize raylessness: the ordinary path ordered as 0<1<2<⋯ has one later neighbor per vertex.

The transitive ancestral mapping is the needed additional structure.

Countable chromaticity

Rayless graphs are countably colorable, but ω
1
ω+2
	​

 has an explicit countable partition into sets of smaller order type. A monochromatic-class argument cannot reach the boundary.

Cardinality alone

Every rayless graph on α has an independent set of cardinality ∣α∣. For noninitial α, such a subset may have order type far below α.

Naive component induction

A lower-rank component of order type γ may contain an independent subset of order type γ while omitting a set whose placement is globally essential. Independent sets chosen separately in components need not amalgamate with the correct external order type.

Greedy selection

For ω+ω, let the graph be a matching between the two ω-blocks. Selecting every vertex in the first block greedily destroys the entire second block, producing only order type ω, although a suitable split of the matching gives order type ω+ω.

Compactness

The disjoint-star construction above shows that every finite collection of block requirements may be satisfiable while all countably many are not. Full order type is not a finitely determined closed condition.

8. Precise intermediate targets
Target A: finite-chain selector

Determine whether every partition of a limit ordinal α into finite sets has a selector of order type α.

A negative answer immediately gives a rayless counterexample: make each finite part a clique and put no edges between parts.

This is the weakest possible counterexample class.

Target B: depth-tail fusion at the boundary

Prove or refute:

If T is a rooted forest on
α=ω
1
ω+2
	​

, has no infinite branch, and every depth tail
⋃
n≥N
	​

L
n
	​

 has order type α, then T has an antichain of order type α.

This isolates exactly the part not handled by finite indivisibility.

Target C: laminar amalgamation

Let {C
i
	​

} be the incomparable child cones in a finite-separator decomposition. Find an ordinal norm N
α
	​

(X) satisfying:

N
α
	​

(X)=N
α
	​

(α) exactly when X contains a copy of α;

the norm behaves controllably under unions of incomparable cones;

replacing each C
i
	​

 by a local full-type antichain does not decrease the total norm.

Ordinary order type lacks the third property.

Target D: cofinal block survival

For ω
2
, “infinitely many blocks survive fully” is sufficient. A higher analogue is needed for

ω
1
ω+2
	​

=(ω
1
ω
	​

)⋅ω
1
2
	​

.

The required invariant must allow local section complexities below ω
1
ω
	​

 to become unbounded, rather than demanding full ω
1
ω
	​

-sections everywhere.

Target E: recursive star obstructions

The finite-versus-countable compactness failure suggests searching among forests made by recursively substituting finite stars into centers, with component heights finite but unbounded.

The labels must be heavily interleaved. Convexly arranged components tend to permit simple ordinal-sum amalgamation; a serious obstruction must use the external ordinal order independently of the tree geometry.

9. Finite falsification program

Finite order type itself is not a faithful surrogate: on n vertices, an antichain of order type n must contain every vertex. A weighted block model is more informative.

Divide {0,…,N−1} into consecutive macroblocks representing successive ordinal scales.

Enumerate rooted forests of bounded height.

For each node v, assign the unit vector of its macroblock.

Compute the Pareto set of antichain block profiles recursively:

P(v)={e
block(v)
	​

}∪
u child of v
⨁
	​

P(u),

where ⊕ is Minkowski addition followed by deletion of dominated vectors.
5. Test whether every antichain misses a prescribed lexicographic target profile, while every depth tail attains that profile.

The search hierarchy should be:

finite chains→star forests→bounded-height forests→unbounded finite-height recursive stars.

Such computation can falsify proposed amalgamation or bounded-height strengthenings, but cannot by itself establish the transfinite assertion.

10. Boundary-condition checks

Infinite successors fail.
For α=λ+1, let the last vertex be the center of a star adjacent to every vertex below it. The graph is rayless. An independent set either omits the center and has order type at most λ, or contains the center and no leaf. Thus the limit assumption is essential.

α=ω holds.
It is an initial ordinal, covered by the cardinal antichain lemma.

α=ω⋅m holds for every finite positive m.

α=ω
2
 holds by the infinitely-many-profiles lemma.

Every infinite initial ordinal holds.

Every finite power κ
n
 with cf(κ)>ω holds.

No complete classification, proof at ω
1
ω+2
	​

, or counterexample has been obtained here. The exact remaining obstruction is the unbounded-finite-depth antichain fusion problem described above.
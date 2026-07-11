Offline structural report

I do not claim a solution or a classification.

1. Blocking ambiguities

The statement is not formally complete until the following are fixed:

“Infinite path” could mean:

a one-way infinite simple path v
0
	​

v
1
	​

v
2
	​

⋯;

a two-way infinite path;

an induced infinite path.

“Graph” presumably means a simple undirected graph.

“Independent set on a set of vertices with order type α” presumably means an independent subset X⊆α whose inherited well-order has type exactly α.

Some conventions count 0 as a limit ordinal.

These choices are material. In particular, the structural reduction below works for an ordinary one-way infinite simple path, not for an induced path. I therefore use the following provisional formalization:

a ray is a sequence (v
n
	​

)
n<ω
	​

 of distinct vertices with v
n
	​

v
n+1
	​

∈E(G).

All statements below are conditional on that interpretation.

2. Exact reduction to an ordinal antichain problem

The graph-theoretic part can be eliminated completely.

Definition 2.1: Rayless rank

Define classes R
ξ
	​

 recursively.

R
0
	​

 consists of finite graphs.

For ξ>0, a graph G belongs to R
ξ
	​

 when there is a finite set S⊆V(G) such that every connected component of G−S belongs to some R
η
	​

 with η<ξ.

Lemma 2.2

A graph is rayless if and only if it belongs to R
ξ
	​

 for some ordinal ξ.

Proof: ranked graphs are rayless

Induct on ξ. Suppose G∈R
ξ
	​

, witnessed by finite S.

If G contained a ray, that ray would meet S only finitely many times. A tail of the ray would therefore lie in a single component of G−S, contradicting the induction hypothesis for that component.

Proof: an unranked graph contains a ray

Suppose some rayless graph is not in any R
ξ
	​

.

If every connected component were ranked, taking the supremum of their ranks would rank the whole graph with separator S=∅. Thus there is a connected unranked graph H
0
	​

.

Choose v
0
	​

∈H
0
	​

. If every component of H
0
	​

−v
0
	​

 were ranked, their ranks together with the finite separator {v
0
	​

} would rank H
0
	​

. Hence some component H
1
	​

 of H
0
	​

−v
0
	​

 is unranked. Since H
0
	​

 is connected, v
0
	​

 has a neighbor v
1
	​

∈H
1
	​

.

Recursively, after obtaining connected unranked H
n
	​

 and v
n
	​

∈H
n
	​

, choose an unranked component

H
n+1
	​

⊆H
n
	​

−v
n
	​


and a neighbor v
n+1
	​

∈H
n+1
	​

 of v
n
	​

.

Then the vertices v
n
	​

 are distinct and

v
0
	​

v
1
	​

v
2
	​

⋯

is a ray. Contradiction. ∎

Definition 2.3: Rayless rooted forest

A rooted forest order ⪯ on a set V has the following properties:

the predecessors of each vertex form a finite chain;

every nonroot vertex has an immediate predecessor;

there is no chain

x
0
	​

≺x
1
	​

≺x
2
	​

≺⋯.

Its comparability graph joins two distinct vertices exactly when they are comparable in the forest order.

Lemma 2.4: Forest representation

Every rayless graph G admits a rayless rooted forest order ⪯ on V(G) such that every edge of G joins comparable vertices.

Proof

Induct on the rayless rank.

For a finite graph, put the vertices of each connected component into an arbitrary finite chain.

For a graph of positive rank, take a finite separator

S={s
0
	​

,…,s
m−1
	​

}

whose complementary components have smaller rank. Put S into a chain

s
0
	​

≺s
1
	​

≺⋯≺s
m−1
	​

.

Construct forest orders recursively inside the components of G−S, and attach every root of each component below s
m−1
	​

. If S=∅, take the disjoint union of the component forests.

Edges inside components are comparable by induction. Edges meeting S are comparable because every element of S is above every vertex in the attached component. Different components of G−S have no edges between them.

The resulting forest has no infinite branch because after passing through the finite chain S, a branch would have to remain inside one lower-rank component. ∎

Lemma 2.5

The comparability graph of a rooted forest with no infinite branch is rayless.

Proof

For a rooted tree, remove its root. The remaining components are the child subtrees. Their well-founded tree ranks are strictly smaller. Induction on this rank shows that their comparability graphs are rayless.

A ray in the full comparability graph would meet the root at most once, so a tail would lie in one child subtree, contradiction.

A forest is the disjoint union of its rooted trees. ∎

Theorem 2.6: Exact forest equivalence

Under the standard interpretation of “infinite path,” the original assertion for α is equivalent to:

Every rooted forest order on the set α with no infinite branch has an antichain whose inherited ordinal order has type α.

Proof

If G is rayless, apply Lemma 2.4. An antichain in the resulting forest consists of pairwise incomparable vertices, so it is independent in G.

Conversely, if a rayless rooted forest T on α has no antichain of type α, take its comparability graph. By Lemma 2.5 it has no ray, and its independent sets are exactly the antichains of T. ∎

This is the main structural reduction. The remaining problem is purely:

Which ordinals force a full-order-type antichain in every branchless forest?
	​

3. A complete cardinal-sized result

The reduction immediately proves a nontrivial class.

Lemma 3.1

Every infinite rooted forest with no infinite branch has an antichain of the same cardinality as its vertex set.

Proof

Let L be the set of leaves.

Every vertex has a leaf descendant. Otherwise, starting at that vertex and repeatedly choosing a child would produce an infinite branch.

Choose for each vertex x a leaf ℓ(x) below x. For a fixed leaf ℓ, the fiber

{x:ℓ(x)=ℓ}

is contained in the finite chain of ancestors of ℓ. Thus every fiber is finite.

Consequently, for infinite T,

∣T∣≤∣L∣⋅ℵ
0
	​

=∣L∣.

Since L⊆T, one has ∣L∣=∣T∣. The leaves form an antichain. ∎

Corollary 3.2

Every infinite initial ordinal κ satisfies the desired graph property.

Indeed, an antichain A⊆κ of cardinality κ must have order type κ: its order type is at most κ, and no ordinal below the initial ordinal κ has cardinality κ.

Thus the standard statement is proved here for

ω, ω
1
	​

, ω
2
	​

,…

and for singular initial ordinals as well.

This argument does not extend directly to noninitial ordinals. For example, a subset of ω
1
	​

⋅2 may have cardinality ℵ
1
	​

 but order type only ω
1
	​

.

4. Simultaneous cardinal preservation

The forest/rank method gives more than one large cardinal set.

Theorem 4.1

Let κ be an infinite regular cardinal. Let G be rayless, and let

A
0
	​

,…,A
m−1
	​

⊆V(G)

all have cardinality κ. Then G has an independent set I such that

∣I∩A
i
	​

∣=κ(i<m).
Proof outline with all essential obligations

Induct on the rayless rank of G. Let S be a finite separator and let {C
j
	​

:j∈J} be the components of G−S.

Call i concentrated if some component C
j
	​

 satisfies

∣A
i
	​

∩C
j
	​

∣=κ.

For each concentrated i, choose one such component. If several indices choose the same component, the induction hypothesis inside that component handles all of them simultaneously.

Now consider a nonconcentrated i. Every A
i
	​

∩C
j
	​

 has size <κ. Since κ is regular and A
i
	​

 has size κ, the set

X
i
	​

={j:A
i
	​

∩C
j
	​


=∅}

has cardinality κ. Removing the finitely many components already reserved for concentrated indices does not change this.

For finitely many κ-sized sets X
i
	​

, there are pairwise disjoint subsets

Y
i
	​

⊆X
i
	​

,∣Y
i
	​

∣=κ.

One direct proof partitions ⋃X
i
	​

 by the finite membership pattern

P(x)={i:x∈X
i
	​

}.

Every X
i
	​

 contains a membership-pattern cell of size κ, and each such cell can be split into finitely many disjoint subsets of size κ.

For each j∈Y
i
	​

, choose one vertex of A
i
	​

∩C
j
	​

. At most one such vertex is chosen in each unreserved component. Distinct components are anticomplete. Combining these vertices with the independent sets from reserved components gives the required I. ∎

Corollary 4.2

For every infinite regular cardinal κ and every positive integer m,

α=κ⋅m

satisfies the desired property.

Partition κ⋅m into its m consecutive κ-blocks. Apply Theorem 4.1 to these blocks. In each block, a κ-sized subset has order type κ, so their ordinal sum has type κ⋅m.

The same proof extends to finite sums of possibly different infinite regular initial ordinals, after grouping the diffuse demands by cardinality.

5. A regular two-cardinal block theorem

The preceding argument can also preserve a full family of blocks.

Lemma 5.1: Disjoint refinement

Let κ be regular infinite, let λ≤κ, and suppose

∣X
ξ
	​

∣=κ(ξ<λ).

Then there are pairwise disjoint sets

Y
ξ
	​

⊆X
ξ
	​

,∣Y
ξ
	​

∣=κ.
Construction

For each stage η<κ, choose fresh points

x
ξ,η
	​

∈X
ξ
	​

(ξ<min(λ,η+1)).

Before any such choice, fewer than κ points have been used, by regularity of κ. For fixed ξ, there are κ stages η≥ξ, so

Y
ξ
	​

={x
ξ,η
	​

:η≥ξ}

has size κ.

Theorem 5.2

Let κ and λ be infinite regular cardinals with λ≤κ. Let G be rayless and let

{A
ξ
	​

:ξ<λ}

be a family of κ-sized vertex sets. Then there are an independent set I and a set S⊆λ of cardinality λ such that

∣I∩A
ξ
	​

∣=κ(ξ∈S).
Rank-induction proof

Let C
j
	​

 be the components after deleting a finite separator.

For each component define

Q
j
	​

={ξ<λ:∣A
ξ
	​

∩C
j
	​

∣=κ}.

There are three cases.

Case 1: Some Q
j
	​

 has size λ

Apply the induction hypothesis inside C
j
	​

.

Case 2: Every Q
j
	​

 has size <λ, but
B=
j
⋃
	​

Q
j
	​


has size λ

One can greedily choose λ distinct pairs

(ξ
η
	​

,j
η
	​

),ξ
η
	​

∈Q
j
η
	​

	​

,

with all ξ
η
	​

 and all j
η
	​

 distinct.

At a stage <λ, the already used components collectively cover fewer than λ indices, by regularity of λ. Hence a new index and a new component remain.

Inside each C
j
η
	​

	​

, use the cardinal-sized independent-set theorem on A
ξ
η
	​

	​

∩C
j
η
	​

	​

. Their union is independent.

Case 3: ∣B∣<λ

For λ many indices ξ, no component contains κ vertices of A
ξ
	​

. Regularity of κ then implies that

X
ξ
	​

={j:A
ξ
	​

∩C
j
	​


=∅}

has size κ.

Apply Lemma 5.1 to obtain pairwise disjoint κ-sized Y
ξ
	​

⊆X
ξ
	​

, and choose one vertex of A
ξ
	​

 from each component in Y
ξ
	​

. ∎

Corollary 5.3

For regular infinite cardinals λ≤κ,

α=κ⋅λ
	​


satisfies the desired property.

Partition κ⋅λ into consecutive blocks B
ξ
	​

 of type κ. The theorem gives λ many blocks, indexed by a subset S⊆λ of order type λ, in each of which the independent set has type κ. Their union has type

κ⋅λ.

This includes, from the arguments developed here,

ω
2
,ω
1
	​

⋅ω,ω
1
2
	​

,

and their regular-cardinal analogues.

6. Bounded-depth forests cannot obstruct powers of ω
Lemma 6.1: Finite partition theorem

For every ordinal β and every finite coloring of ω
β
, some color class has order type ω
β
.

Proof

Induct on β.

For β=0, this is immediate.

If β=γ+1, partition

ω
γ+1

into consecutive blocks of type ω
γ
. By induction, each block has a full-type monochromatic subset. Some color is selected in infinitely many blocks, giving type

ω
γ
⋅ω=ω
γ+1
.

If β is limit, apply the induction hypothesis to every initial segment ω
γ
, γ<β. One of the finitely many colors succeeds for cofinally many γ<β, and hence has order type at least

γ<β
sup
	​

ω
γ
=ω
β
.

∎

Corollary 6.2

If a branchless forest on ω
β
 has bounded finite depth, then it has an antichain of type ω
β
.

Indeed, its finitely many depth levels are antichains and partition the vertex set.

Therefore, any counterexample forest on an additively indecomposable ordinal ω
β
 must have unbounded finite depth.

Moreover, writing L
n
	​

 for the depth-n level and

D
n
	​

=
m≥n
⋃
	​

L
m
	​

,

a counterexample must satisfy

otp(L
n
	​

)<ω
β

for every n, but also

otp(D
n
	​

)=ω
β

for every n. Otherwise the finite partition

L
0
	​

,…,L
n−1
	​

,D
n
	​


would contradict Lemma 6.1.

For the explicitly highlighted boundary, writing κ=ω
1
	​

,

ω
1
	​

=ω
ω
1
	​


and hence

ω
1
ω+2
	​

=(ω
ω
1
	​

)
ω+2
=ω
ω
1
	​

⋅(ω+2)
.

Thus it is a power of ω. A counterexample there cannot have bounded depth.

7. Exact low-rank counterexample tests

The forest formulation produces concrete falsification targets.

Test 1: Finite-class selector obstruction

Partition α into finite classes P. Put a clique on each class and no edges between classes.

This graph is rayless because all components are finite. Its independent sets are precisely partial transversals of P.

Therefore:

If there is a partition of α into finite sets such that every transversal has order type <α, then α is a counterexample.

This is the lowest-rank possible obstruction.

Equivalently, define:

FS(α):every finite-class equivalence relation on α has an α-type transversal.

The original property implies FS(α).

Test 2: Height-one star obstruction

Let R,L⊆α be disjoint and let

p:L→R.

Construct a star forest in which each leaf ℓ has parent p(ℓ).

For S⊆R, the largest antichain having root set S is

A
S
	​

=S∪{ℓ∈L:p(ℓ)∈
/
S}.

Every antichain is contained in some A
S
	​

. Hence this star forest is a counterexample exactly when

otp(A
S
	​

)<αfor every S⊆R.

This gives a precise functional counterexample search:

Find R,L,p such that every root/leaf tradeoff loses full order type.
	​


A matching is the special case in which p is one-to-one.

Test 3: Recursive forest obstruction

For a rooted tree node t, an antichain in its subtree has one of two forms:

{t},

or

u child of t
⋃
	​

A
u
	​

,

where each A
u
	​

 is an antichain in the child subtree.

This gives an exact recursive dynamic description of all possible antichains. Any proposed counterexample can be tested from the leaves upward.

8. Minimal-counterexample constraints

Assume provisionally that a counterexample forest T exists on an ordinal α=ω
β
, and choose one of least forest rank.

Then all of the following are necessary:

Every depth level has order type <α.

Every finite union of depth levels has order type <α.

Every depth tail D
n
	​

 has order type α.

The leaf set has order type <α, even though it has cardinality ∣α∣.

No proper lower-rank subtree whose vertex set has order type α can occur. Such a subtree would itself be a lower-rank counterexample.

The forest must have unbounded finite branch lengths.

Every maximal front, not merely every level, must have order type <α.

Thus any counterexample at ω
1
ω+2
	​

 has to be a genuinely unbounded-rank, order-sensitive construction. Finite-height trees, stars of uniformly bounded iteration depth, and cardinality-only obstructions cannot work.

9. The exact gluing obstruction

The rank induction succeeds whenever one component contains a full-order-type portion. The unresolved situation is when the ordinal is distributed among many lower-rank components.

A naive componentwise induction does not work.

Explicit failure of order-type-preserving replacement

Partition ω
2
 into columns

C
n
	​

={ωk+n:k<ω},n<ω.

Each C
n
	​

 has order type ω.

Choose

I
n
	​

={ωk+n:k≥n}.

Again,

otp(I
n
	​

)=otp(C
n
	​

)=ω

for every n. But in the k-th ω-block, the union ⋃
n
	​

I
n
	​

 contains only k+1 points. Therefore

otp(
n<ω
⋃
	​

I
n
	​

)=1+2+3+⋯=ω,

not ω
2
.

So the following inference is false:

[otp(I
j
	​

)=otp(C
j
	​

) for all j]⟹otp(⋃I
j
	​

)=otp(⋃C
j
	​

).

Any successful induction needs a stronger, interval-sensitive invariant.

10. A precise higher-order intermediate target

For regular κ, the proof for κ⋅λ works because a block of type κ is full exactly when it contributes κ vertices.

For higher powers, define the small-set ideal

J
θ
	​

={X:otp(X)<θ}

on a copy of θ.

Suppose a rank decomposition gives components C
j
	​

, and a target block A
ξ
	​

 of type θ is partitioned into

P
ξj
	​

=A
ξ
	​

∩C
j
	​

.

When no single P
ξj
	​

 has type θ, the needed combinatorial statement is a disjoint-refinement principle:

For sufficiently many ξ, choose pairwise disjoint component-index sets Y
ξ
	​

 such that

otp
	​

j∈Y
ξ
	​

⋃
	​

P
ξj
	​

	​

=θ.

At θ=κ, this reduces to choosing κ many nonempty component intersections, which is exactly the disjoint-refinement argument in Section 5.

At

θ=κ
2
, κ
3
,…,κ
ω
,

mere cardinal support is no longer enough. The chosen pieces must preserve a nested block profile.

A recursive version of this disjoint-refinement principle, together with induction on forest rank and on θ, is a precise route toward

κ
ω+2
.

Failure of this principle would also give a concrete blueprint for constructing a counterexample forest.

11. Stronger boundary target

Let κ=ω
1
	​

. Write

κ
ω+2
=κ
ω
⋅κ
2
.

A useful sufficient statement would be:

For every rayless graph on κ
ω+2
, there is a set S⊆κ
2
 of order type κ
2
 and, for every ξ∈S, an independent subset of the ξ-th consecutive κ
ω
-block having type κ
ω
, with all these subsets mutually anticomplete.

This is stronger than the original conclusion and may itself be false even if the original conclusion is true. It is nevertheless a sharp falsification target: a counterexample to this stronger statement should be examined to see whether its selected pieces can still interleave into a full κ
ω+2
-type antichain.

The weaker, exact obligation is to invent a hierarchical profile invariant that detects order type κ
ω+2
 without insisting on full type inside predetermined blocks.

12. Failed attacks and what they establish
Countable coloring

Every rayless graph is countably colorable by induction on rayless rank: color the finite separator with finitely many colors and reuse a countable palette on the lower-rank components.

This does not solve the ordinal problem. Even ω can be partitioned into countably many singleton color classes, none of type ω.

Thus chromatic number controls cardinality poorly and order type even more poorly.

Largest-cardinality independent set

The leaf argument gives an independent set of full cardinality. This settles initial ordinals but not ordinals such as

κ⋅2,κ
2
,κ
ω
.

Full cardinality can be concentrated in an early segment.

Arbitrary simultaneous preservation

The following stronger statement is false:

For every countable family of infinite sets A
n
	​

 in a rayless graph, there is an independent set meeting every A
n
	​

 infinitely.

Counterexample: take disjoint infinite stars C
n
	​

, with center c
n
	​

 and infinite leaf set L
n
	​

. Let

A
0
	​

={c
n
	​

:n≥1},A
n
	​

=L
n
	​

(n≥1).

An independent set meeting every L
n
	​

 infinitely cannot contain any center c
n
	​

, so it misses A
0
	​

.

Hence only ordinally essential demands may be imposed simultaneously; arbitrary set families are too strong.

Compactness

Finite satisfiability of intersection demands does not automatically give full cardinal or full order type. The star example shows that even countably many infinitude requirements may be globally incompatible.

Random selection

Randomly selecting representatives from finite components may preserve robust density conditions, but order type can depend on sparse, nested, cofinal requirements. Unbounded star degrees can force the probabilities of the relevant choices to tend to zero. This remains a discovery heuristic, not a proof method.

Induction only on α

A component of a rayless graph on α may itself have vertex-set order type α. Thus ordinal induction alone does not decrease. One needs the graph/forest rank as a second induction coordinate.

Pairwise block compatibility

Defining an auxiliary graph whose vertices are ordinal blocks and whose edges indicate pairwise incompatibility is insufficient. Pairwise compatible large choices need not admit a single jointly compatible choice. A successful compression must retain higher-arity information.

13. Finite falsification program

The forest reduction gives a practical finite search scheme.

Partition a finite ordered set into q consecutive macroblocks. For every rooted forest T, associate to each antichain the profile

(a
0
	​

,…,a
q−1
	​

),

where a
i
	​

 is the number of selected vertices in block i.

For a node t, the achievable profile set satisfies the exact recursion

P(t)={e
block(t)
	​

}∪{
u child of t
∑
	​

p
u
	​

:p
u
	​

∈P(u)}.

For a forest, take the Minkowski sum over its roots. Coordinatewise dominated vectors may be discarded.

This allows exhaustive or branch-and-bound searches for finite analogues of:

finite-class selector obstructions;

star-map obstructions;

nested-star obstructions;

failure of two-level block preservation;

candidate patterns whose depth tails remain large while every antichain profile remains deficient.

A scalable obstruction should persist as the block size and number of blocks increase. Isolated finite failures have no direct ordinal force.

Current status

The exact problem has not been resolved here.

The strongest established conclusions are:

The graph problem is exactly a branchless-forest antichain problem.
	​

Every infinite initial ordinal satisfies the property.
	​

If κ,λ are infinite regular cardinals and λ≤κ, then κ⋅λ satisfies it.
	​

Every counterexample on a power ω
β
 requires unbounded finite forest depth.
	​


The remaining central obligation is an order-sensitive, hierarchical disjoint-refinement theorem for the component pieces of a rayless-rank decomposition. At ω
1
ω+2
	​

, cardinal support alone is insufficient; a successful invariant must preserve the nested ω
1
	​

-power block profile through countably many levels and then through two further ω
1
	​

-indexed levels.
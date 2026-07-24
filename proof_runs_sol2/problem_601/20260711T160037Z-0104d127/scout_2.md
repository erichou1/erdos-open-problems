1. Interpretational obstruction

The literal statement is ambiguous in ways that change the answer.

I will provisionally use the following interpretation:

graphs are simple and undirected;

an “infinite path” is a one-way infinite simple path v
0
	​

v
1
	​

v
2
	​

⋯ with distinct vertices;

a subset X⊆α has order type α under the order inherited from α;

“limit ordinal” means a nonzero ordinal with no immediate predecessor.

Two alternative interpretations behave differently:

If “path” means induced path, then the complete graph on any infinite α is an immediate counterexample.

If repeated vertices are allowed, an edge already produces an infinite alternating walk, so the problem changes completely.

If 0 is admitted as a limit ordinal, it satisfies the statement because the empty graph has the empty independent set of order type 0.

Everything below uses the provisional interpretation above.

2. Exact structural reduction

Write P(α) for the property in the question.

The principal reduction is that rayless graphs are precisely the graphs that can be placed inside closures of rooted forests having no infinite branch.

2.1 A rank for rayless graphs

Define classes R
ρ
	​

 recursively.

R
0
	​

 consists of the finite graphs.

For ρ>0, a graph G belongs to R
ρ
	​

 if there is a finite set S⊆V(G) such that every component of G−S belongs to some R
ξ
	​

 with ξ<ρ.

Lemma 1

A graph has no infinite path if and only if it belongs to some R
ρ
	​

.

Proof: rank implies no path

Proceed by induction on ρ.

For ρ=0, the graph is finite. For ρ>0, choose finite S as in the definition. An infinite simple path meets S only finitely many times, so a tail of the path lies in one component of G−S. That component has smaller rank, contradicting induction.

Proof: non-rankability produces a path

Suppose some graph is not in any R
ρ
	​

.

If every component were rankable, then taking the supremum of their ranks and using S=∅ would rank the whole graph. Hence there is a connected non-rankable graph H
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

 were rankable, their ranks would have a supremum, and S={v
0
	​

} would rank H
0
	​

. Thus H
0
	​

−v
0
	​

 has a non-rankable component H
1
	​

.

Because H
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

: take a path from v
0
	​

 to any point of H
1
	​

; its first vertex after v
0
	​

 belongs to H
1
	​

.

Repeat inside H
1
	​

. We obtain nested connected non-rankable graphs

H
n+1
	​

⊆H
n
	​

−v
n
	​


and vertices v
n+1
	​

∈H
n+1
	​

 adjacent to v
n
	​

. The vertices are distinct, so

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

is an infinite path. ∎

2.2 Elimination forests

A rooted forest T on a set V has a partial order ≼
T
	​

, where x≼
T
	​

y means that x is an ancestor of y.

Its closure cl(T) is the graph in which two distinct vertices are adjacent exactly when they are comparable in T.

Lemma 2

Every rayless graph G is a subgraph of cl(T) for some rooted forest T with no infinite branch.

Construction

Induct on the rank from Lemma 1.

For a finite graph, put all vertices into a finite chain.

For a graph of positive rank, choose a finite separator S such that all components C of G−S have lower rank. By induction, construct a forest T
C
	​

 for each component.

Arrange S as a finite chain and make every root of every T
C
	​

 a child of the last point of that chain. If S=∅, take the disjoint union of the forests T
C
	​

.

Every edge of G then has comparable endpoints:

edges within S have comparable endpoints;

edges within one component are handled inductively;

every point of S is an ancestor of every point below it;

there are no edges between distinct components of G−S.

No infinite branch is introduced, because a branch passes through the finite chain S and then remains in one lower-rank forest. ∎

Lemma 3

If T has no infinite branch, then cl(T) has no infinite path.

Proof

For a vertex x, let d(x)∈ω be its depth.

In any finite path in cl(T), a vertex of minimum depth is unique and is an ancestor of every vertex on that path. Indeed, starting from a minimum-depth vertex, every adjacent vertex of no smaller depth must be its descendant, and the same remains true step by step.

Now suppose

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

is an infinite path. The minimum-depth vertices of longer and longer initial segments can move upward only finitely many times, because v
0
	​

 has only finitely many ancestors. Eventually there is a fixed vertex t
0
	​

 that is an ancestor of all sufficiently late v
n
	​

.

After the path leaves t
0
	​

, its tail must lie in one child subtree of t
0
	​

: vertices in two different child subtrees are incomparable, and crossing between them would require revisiting t
0
	​

.

Apply the same argument inside that child subtree. Iteration gives

t
0
	​

≺
T
	​

t
1
	​

≺
T
	​

t
2
	​

≺
T
	​

⋯,

an infinite branch, contradiction. ∎

2.3 Exact reformulation of the problem

Combining the preceding lemmas gives:

Theorem 4: Forest reformulation

For a limit ordinal α, P(α) holds if and only if every rooted forest T on vertex set α, with no infinite branch, has an antichain of order type α.

The two directions are exact:

Given a rayless graph, embed it into the closure of such a forest. An antichain is independent.

Given a forest with no α-type antichain, its closure is rayless and its independent sets are exactly its antichains.

Thus the graph problem is reduced without loss to an ordinal antichain problem.

3. Equivalent finite set-mapping formulation

For a forest T, let

A(y)={x:x≺
T
	​

y},

the set of proper ancestors of y.

Then:

A(y) is finite.

If x∈A(y), then A(x)⊊A(y).

Any two elements of A(y) are comparable by ancestry.

There is no sequence y
0
	​

,y
1
	​

,… with

y
n
	​

∈A(y
n+1
	​

)

for every n.

Conversely, a mapping satisfying these ancestral conditions determines a rooted forest.

A subset X⊆α is an antichain exactly when

A(y)∩X=∅for every y∈X.

Hence:

Theorem 5: Ancestral mapping reformulation

P(α) holds exactly when every finite ancestral mapping A on α has an A-free subset of order type α.

The obstruction is therefore a finite-predecessor hitting relation that meets every copy of α, while its transitive closure contains no infinite chain.

4. Consequences that can be proved completely
4.1 Cardinality version

The order-type requirement is the only genuine obstruction at the cardinal level.

Lemma 6

Every forest T with no infinite branch has an antichain of cardinality ∣T∣.

Proof

Let L be the set of leaves.

Every node has a leaf descendant. Otherwise, beginning at that node and repeatedly choosing a child would produce an infinite branch.

For each node x, choose a leaf ℓ(x) below x. For a fixed leaf l, every point of ℓ
−1
({l}) is an ancestor of l. This ancestor chain is finite. Thus ℓ is finite-to-one.

Consequently, for infinite T,

∣T∣≤∣L∣⋅ℵ
0
	​

=∣L∣.

The reverse inequality is immediate, so ∣L∣=∣T∣. The leaves form an antichain. ∎

Corollary 7

Every rayless graph has an independent set of the same cardinality as its vertex set.

Corollary 8

P(κ) holds for every infinite initial ordinal κ.

Indeed, a subset of the initial ordinal κ having cardinality κ necessarily has order type κ.

This includes singular as well as regular initial ordinals.

4.2 The case α=ω

This also follows from the preceding cardinal argument. Directly, every infinite forest with no infinite branch has infinitely many leaves, and every infinite subset of ω has order type ω.

Thus P(ω) holds.

4.3 A countable-partition sufficient condition

Define

C
ω
	​

(α):for every c:α→ω, ot(c
−1
(n))=α for some n.

Every node of a rooted forest has finite depth, and equal-depth vertices form an antichain. The levels give a countable partition.

Proposition 9

If C
ω
	​

(α) holds, then P(α) holds.

This criterion is sufficient but far from necessary: C
ω
	​

(ω) fails, although P(ω) holds.

4.4 A concrete positive family from the level criterion

Let κ be an infinite initial ordinal with

cf(κ)>ω.
Proposition 10

For every positive integer n,

C
ω
	​

(κ
n
)

holds, and hence P(κ
n
) holds.

Proof

Induct on n.

For n=1, if κ were the union of countably many sets of cardinality less than κ, then their cardinalities would have a supremum below κ, contradicting that the union has size κ.

For the induction step, divide

κ
n+1
=κ
n
⋅κ

into consecutive blocks B
ξ
	​

, ξ<κ, each of order type κ
n
.

Given a countable coloring, the induction hypothesis gives, in each block B
ξ
	​

, a color c(ξ) whose intersection with that block has type κ
n
. Since κ cannot be partitioned into countably many sets of size below κ, one color occurs for κ many block indices. Those indices have order type κ. The union of the corresponding monochromatic copies has type

κ
n
⋅κ=κ
n+1
.

∎

4.5 Where this level argument stops

The countable partition criterion already fails at κ
ω
.

Partition κ
ω
 into the layers

[κ
n
,κ
n+1
),n<ω.

Each layer has order type below κ
ω
.

It also fails at κ
ω+1
=κ
ω
⋅κ: inside every κ
ω
-block, use the same countable decomposition into finite-power layers. For fixed n, the union of the n-th layers over all κ outer blocks has type at most

κ
n+1
⋅κ=κ
n+2
<κ
ω
.

This only shows that the simple “one large level” proof fails. It does not produce a bad forest.

5. Uniformly bounded branch length

Suppose every branch of a forest has at most m vertices. The forest is then the union of m antichain levels.

For an ordinal of the form

α=ω
β
,

a finite union of subsets of order type below α still has order type below α.

One way to verify this is to use the following finite-shuffle inequality. If X
1
	​

,…,X
m
	​

 are subsets of a well-order, then

ot(
i=1
⋃
m
	​

X
i
	​

)≤ot(X
1
	​

)#⋯#ot(X
m
	​

),

where # adds the coefficients in the common Cantor normal forms. The inequality follows by mapping an initial segment to the natural sum of its ranks in the X
i
	​

. Natural sum is strictly increasing in every coordinate. A finite natural sum of ordinals below ω
β
 remains below ω
β
.

Therefore:

Proposition 11

If α=ω
β
, every forest of uniformly bounded finite branch length on α has an antichain of type α.

Consequently, a bad forest on an additively indecomposable α would have to contain branches of arbitrarily large finite length, although it may contain no infinite branch.

6. Necessary features of any counterexample

Suppose T is a bad forest on a nonzero limit ordinal α.

6.1 α cannot be an initial ordinal

The leaf antichain has cardinality ∣α∣. If α were initial, this antichain would have type α.

Thus any bad α must satisfy

∣α∣<α.

The obstruction is necessarily positional, not cardinal.

6.2 Every level is order-small

For every n<ω,

L
n
	​

={x:d(x)=n}

is an antichain, so

ot(L
n
	​

)<α.

Hence failure of C
ω
	​

(α) is necessary for failure of P(α).

6.3 The leaf set is order-small but cardinally full

If L is the leaf set, then

∣L∣=∣α∣andot(L)<α.

This isolates the exact gap between cardinality and order type.

6.4 Finite deletion preserves badness

If F⊆α is finite and α is an infinite limit ordinal, then

ot(α∖F)=α.

Deleting vertices cannot create new comparable pairs, so T−F, relabeled in increasing order, is still bad.

Therefore no bad example can be minimal under deletion of finitely many vertices.

6.5 Heredity to copies of α

If X⊆α has order type α, then the induced forest T[X] is also bad after relabeling: an α-type antichain in T[X] would be one in T.

Thus a bad relation hits every internal copy of α, not merely the entire vertex set.

6.6 Deep bad cores for additively indecomposable α

Assume α=ω
β
. The union of the first n levels has order type below α. Its complement must therefore have type α; otherwise α would be a finite union of order-small sets.

Hence for every n,

T
≥n
	​

={x:d(x)≥n}

has order type α and is still bad.

Any contradiction argument may therefore pass to an α-type core whose vertices all have depth at least n, for arbitrarily large n. The missing step is to make these deep cores concentrate along one branch.

7. Minimal-counterexample consequences

Assume some limit ordinal fails and let α be the least failing limit ordinal.

Then:

α is not an initial ordinal.

For every limit β<α, every no-branch forest on β has a β-type antichain.

Every proper initial segment T↾β, with β<α limit, contains an antichain of type β.

The failure is purely a gluing failure: all smaller initial pieces behave correctly, but their antichains cannot be amalgamated into one of type α.

Passing to any subset of type α gives another bad example on the same ordinal.

Vertex minimality is unavailable because finite deletion preserves badness.

Minimizing the elimination rank rather than the ordinal does not immediately solve the problem. At a finite separator, deleting the separator leaves a disjoint union of lower-rank components, but their ranks may be unbounded below the original rank, and independently chosen antichains in the components need not preserve the order type of their union.

8. Immediate counterexample templates
8.1 Finite equivalence classes

Let E be a partition of α into nonempty finite sets.

A transversal chooses exactly one point from every class.

Define:

FT(α):every partition of α into finite classes has a transversal of type α.
Proposition 12

If FT(α) fails, then P(α) fails.

Proof

Make every class of E a clique and put no edges between distinct classes. Every component is finite, so the graph has no infinite path.

Every independent set is a partial transversal. If it had order type α, extend it to a full transversal. A superset inside α of an α-type set still has type α, contradicting failure of FT(α). ∎

Thus the smallest possible obstruction should first be sought among:

matchings, where every class has size 2;

finite clique decompositions;

then height-two star forests;

only afterward genuinely high-rank forests.

No failure of FT(α) has been established here.

8.2 Height-two star forests

Let the roots be R, and let B
r
	​

 be the set of leaves below root r.

An antichain may, independently for each r,

choose the root r, thereby choosing no leaf in B
r
	​

; or

omit r and choose an arbitrary subset of B
r
	​

.

A height-two counterexample is therefore exactly an ordinal selection system in which every such mixed choice has order type below α.

This is the next obstruction class after finite clique components.

9. Precise intermediate targets
Target A: Bipartite separation

For limit ordinals β,γ, consider:

R(β,γ):

Whenever A,B are independent sets of types β,γ in a rayless graph, there are

A
′
⊆A,B
′
⊆B

with

ot(A
′
)=β,ot(B
′
)=γ

and no edges between A
′
 and B
′
.

If R(β,γ), P(β), and P(γ) hold, then P(β+γ) follows:

find independent sets of full type in the two consecutive blocks;

apply R(β,γ) to eliminate all cross edges;

take their union.

The contrapositive form is especially useful:

If every full-type rectangle A
′
×B
′
 contains an edge, construct an alternating infinite path.

The straightforward recursive construction fails because the edge witnessing one rectangle need not connect to the edge witnessing the next. A reservoir or concentration lemma is still missing.

The limit hypotheses matter. R(1,γ) is false: one vertex joined to every point of B is a rayless star.

Target B: Front selection

A front is an antichain meeting every maximal root-to-leaf branch.

Every antichain extends to a maximal antichain. In a no-branch forest, every maximal antichain is a front: otherwise a leaf on an unmet branch could be added.

Hence the problem is equivalent to finding a front of type α.

At an antichain R, the descendant subtrees T
r
	​

 are disjoint. A front below R has the form

r∈R
⋃
	​

F
r
	​

,

where F
r
	​

 is a front in T
r
	​

.

The exact gluing target is:

Given ordinally interleaved subtrees T
r
	​

, select one front F
r
	​

 from each subtree so that their union retains the full order type of the union of the subtrees.

This is stronger than selecting arbitrary full-type subsets componentwise.

Target C: Concentration-or-front dichotomy

Let T
t
	​

 be a subtree whose vertex set has type α.

One would like to prove:

Either some child u of t has V(T
u
	​

) of type α, or fronts from the child subtrees can be combined into an antichain of type α.

If the first alternative occurred forever, it would produce an infinite branch. Thus the dichotomy would prove P(α).

The unresolved case is when α is distributed over many child subtrees, none individually of type α, but the ordinal interleaving of the subtrees is complicated enough that naive front choices lose order type.

Target D: Finite-transversal theorem

Determine FT(α):

Does every finite-to-one equivalence relation on α have a transversal of type α?

A negative answer immediately gives a counterexample of elimination rank 1. A positive answer eliminates all finite-component obstructions but does not yet handle stars or higher-rank forests.

The size-two case, involving fixed-point-free involutions and independent transversals of matchings, is the first falsification target.

Target E: Rank induction with an ordinal gluing lemma

The graph rank gives a natural induction. The obstacle is entirely at the disjoint-union step.

A sufficient gluing statement would say:

If α is partitioned into vertex sets of lower-rank forests and each forest admits sufficiently many full internal fronts, then some simultaneous choice of fronts has union of type α.

Merely knowing that every component has one antichain of its own full order type is insufficient.

Target F: Cantor-normal-form profile invariant

For powers such as κ
ω+1
, a single level need not be large. A candidate invariant should record, recursively, how much of each canonical block is captured.

For

α=κ
ω
⋅κ,

write B
ξ
	​

, ξ<κ, for the outer κ
ω
-blocks. For X⊆α, record

P
n
	​

(X)={ξ<κ:ot(X∩B
ξ
	​

)≥κ
n
}.

An α-type set must synchronize arbitrarily high finite-power profiles across sufficiently many outer blocks. A useful invariant would show that front replacement operations cannot destroy every profile simultaneously.

The exact synchronization requirement remains to be derived; cardinality of each P
n
	​

(X) alone is not sufficient because decreasing large subsets may have empty intersection.

10. Failed attacks and what they establish
10.1 Arbitrary maximal independent sets

Take an infinite star on α, with center 0. The singleton {0} is maximal independent, while the set of leaves has type α.

Thus maximality by inclusion gives no order-type control.

10.2 Cardinality alone

For α=κ⋅2, a subset contained in the first block may have cardinality κ=∣α∣ but order type only κ<α.

The cardinal theorem cannot settle non-initial ordinals.

10.3 Leaves alone

Let α=ω+ω. Partition the second ω-block into infinite sets B
n
	​

, n<ω. Make n the root of a star whose leaf set is B
n
	​

.

The leaf set is the second block, of type ω<ω+ω.

Nevertheless there is an antichain of type ω+ω: choose the even roots and all leaves below odd roots. This gives infinitely many points in the first block and infinitely many in the second.

Thus a full antichain may require replacing some leaf subfamilies by ancestors.

10.4 Componentwise full-type thinning

In the same construction, let

C
n
	​

={n}∪B
n
	​

.

Each C
n
	​

 has type ω. Replacing C
n
	​

 by B
n
	​

 preserves the order type of every individual piece, but

n
⋃
	​

B
n
	​


has type only ω, whereas

n
⋃
	​

C
n
	​

=ω+ω.

Therefore:

Choosing a full-type subset inside every component does not ensure that their union retains the full ambient order type.

This is the principal failure of naive rank induction.

10.5 Countable coloring alone

Every forest has countably many depth levels, but ω
2
 can be partitioned into countably many consecutive sets of type ω.

A countable antichain cover does not by itself produce a full-order-type antichain.

10.6 Finite-degree peeling

Every nonempty induced subgraph of a rayless graph has a finite-degree vertex. Otherwise, starting at any vertex and repeatedly choosing a new neighbor would construct a path.

However, peeling finite-degree vertices does not directly give the desired ordering. In an infinite star, removing leaves first places the center after infinitely many neighbors. The missing ingredient is the hierarchical finite-separator structure, supplied by the elimination rank.

10.7 Edge-minimal counterexamples

Removing edges preserves raylessness, so it is tempting to seek an edge-minimal bad graph. A Zorn argument would require the intersection of every descending chain of bad edge sets to remain bad.

The property “has no independent set of type α” is not generally closed under such intersections: different stages may retain different obstructing edges, while every fixed pair is eventually removed. An additional compactness argument would be needed.

10.8 Direct recursive branch construction

Badness says every α-type set contains a comparable pair. Selecting one comparable pair does not ensure that an α-type set remains inside the descendant subtree of its upper endpoint.

The witnesses may be distributed among many unrelated finite branches. This is precisely the concentration gap in Target C.

11. Probabilistic and compactness attacks
Random fronts

At each internal node one could randomly either stop at that node or continue into its child subtrees, producing a random front.

For a fixed canonical interval of α, one may try to choose stopping probabilities so that the expected number or profile of selected points is large. The difficulty is that one selected ancestor can replace arbitrarily many leaves, and the ordinal labeling may place those leaves throughout many distant blocks. Ordinary expectation does not track order type.

A viable probabilistic argument would need a block-profile random variable, not merely cardinality.

Compactness

Finite restrictions of a forest always admit maximal antichains, and the space of subsets 2
α
 is compact in the product topology. The antichain condition is closed.

The condition “has order type α” is not compact in the required way: a limit of sets that are increasingly large on initial segments can have much smaller order type. A successful compactness proof therefore needs fusion conditions preserving a complete Cantor-normal-form profile.

12. Finite falsification tests

Finite graphs automatically have no infinite path, so testing arbitrary finite graphs is uninformative. The finite models should preserve the forest closure and ordinal-block structure.

Test 1: Truncated ω
2

Use an N×M grid in lexicographic row order. Call a set (r,s)-large if it contains at least s points in each of at least r rows.

Enumerate or optimize rooted forests of branch length at most h. Ask whether every antichain fails the (r,s)-largeness condition.

Persistent examples as N,M,r,s,h grow would suggest a genuine obstruction. Failure to find examples may expose a finite front-selection invariant.

Test 2: Matching and finite-class obstructions

Partition the finite grid into pairs or bounded finite classes. Use integer programming to maximize the lexicographic row profile of a transversal.

This directly probes FT(α) and its size-two specialization.

Test 3: Bipartite separation

Take two ordered grids approximating β and γ. Require:

no alternating path longer than L;

every pair of large subsets has a cross edge.

Search for examples as L grows. Such examples would falsify overly strong finite versions of R(β,γ).

Test 4: Front-profile dynamic programming

For each node of a finite rooted forest, compute the set of attainable profiles of fronts in its subtree. At a node, the recurrence is:

either select the node;

or combine one attainable profile from each child subtree.

The convexity, closure, or domination properties of these profile sets may suggest the correct infinite invariant.

Finite experiments can falsify candidate gluing lemmas, but they cannot by themselves prove the infinite statement because the maximum finite path length may grow with the truncation.

13. Current boundary of the analysis

The exact graph-theoretic part has been reduced completely:

P(α)⟺every no-infinite-branch rooted forest on α has an antichain of type α
	​


equivalently,

every finite ancestral mapping on α has a free subset of type α.
	​


Established consequences include:

all infinite initial ordinals satisfy P;

every rayless graph has an independent set of full cardinality;

the countable-partition property C
ω
	​

(α) implies P(α);

κ
n
 satisfies P for finite n when cf(κ)>ω;

bounded-height forest obstructions are impossible on additively indecomposable ordinals;

any counterexample must be non-cardinal, have all levels and all fronts order-small, and encode the missing ordinal complexity across many finite branches.

The unresolved core is the front-gluing problem: independently good antichains in ordinally interleaved lower-rank subtrees may lose order type when united, and no concentration principle has yet forced them onto one branch or synchronized them into a full-type front. No general characterization of the limit ordinals has been obtained.
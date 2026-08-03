# Erdős Problem #146 [unsolved] 20%

---

## ChatGPT Response

Phase 0: Formalization
Objects

Let H be a fixed finite graph.

A graph H is bipartite if there exists a partition

V(H)=A⊔B

such that every edge has one endpoint in A and one endpoint in B.

A graph H is r-degenerate if every nonempty induced subgraph H[S], S⊆V(H), has a vertex of degree at most r inside H[S].

Equivalently, H has an ordering

v
1
	​

,…,v
h
	​


such that each v
i
	​

 has at most r neighbors among

v
i+1
	​

,…,v
h
	​

.

Let

ex(n;H)

denote the maximum number of edges in an n-vertex graph containing no copy of H.

The target statement is:

∀r≥1 ∀ finite bipartite r-degenerate H ∃C
H
	​

>0 ∀n≥1,
ex(n;H)≤C
H
	​

n
2−1/r
.

Equivalently:

Every sufficiently dense n-vertex graph with ≫n
2−1/r
 edges must contain every fixed bipartite r-degenerate graph H.

Negation

The negation is:

∃r≥1 ∃ finite bipartite r-degenerate H

such that

∀C>0 ∃n≥1 ∃G
n
	​


with

∣V(G
n
	​

)∣=n,e(G
n
	​

)>Cn
2−1/r
,

and

G
n
	​

 contains no copy of H.

So to disprove the statement, one must construct a fixed bipartite r-degenerate H and an infinite family of H-free graphs whose edge count grows faster than every constant multiple of n
2−1/r
.

Contrapositive

The desired theorem is equivalent to:

If G is an n-vertex graph with

e(G)>C
H
	​

n
2−1/r
,

then G contains a copy of H.

Thus the main task is an embedding theorem:

High edge density forces an embedding of every fixed bipartite r-degenerate graph.

Boundary cases
Case r=1

A 1-degenerate graph is a forest. If H is a fixed forest with h vertices, then any graph with average degree at least h−1 contains H greedily. Hence

ex(n;H)=O(n).

This matches

n
2−1/1
=n.

So the statement is true for r=1.

Case r≥2

The degeneracy ordering allows each new vertex to depend on at most r previously embedded vertices, but those dependencies may alternate between both sides of the bipartition. This is the core difficulty.

Phase 1: Breadth-first proof search

I explored the following independent strategies.

Strategy 1: Direct greedy embedding using degeneracy order

Use a degeneracy ordering

v
1
	​

,…,v
h
	​


and embed vertices in reverse order. When embedding v
i
	​

, it has at most r already embedded neighbors, so one only needs a common neighborhood of at most r vertices.

Obstacle: density

e(G)≫n
2−1/r

only gives average degree ≫n
1−1/r
. It does not guarantee that every r-tuple has a large common neighborhood.

This reduces the problem to finding a large structured subset where all relevant r-tuples have enough common neighbors.

Unresolved gap:

GAP 1:

Find two large vertex sets X,Y such that many or all relevant r-tuples in X have many common neighbors in Y, and vice versa.

Strategy 2: Dependent random choice

Try to find a subset U such that every small subset of U has many common neighbors.

For bipartite G=(X,Y), pick random vertices from Y, and let U⊆X be their common neighborhood.

This can often produce a set U where most r-tuples have many common neighbors.

Obstacle: a single DRC set gives control in one direction only. For a general r-degenerate bipartite graph, the greedy embedding may need common neighborhoods alternating between both sides.

Unresolved gap:

GAP 2:

Construct two mutually rich sets X
′
⊆X, Y
′
⊆Y such that relevant r-tuples in each side have enough common neighbors in the other side.

Strategy 3: Symmetric DRC

Apply DRC from Y into X, then from the resulting X
′
 back into Y, hoping to obtain mutual richness.

Obstacle: the second DRC step may destroy the useful structure from the first step. Iterating DRC causes shrinkage, and the remaining set sizes may fall below what is needed to embed H.

Unresolved gap:

GAP 3:

Prove that the DRC iteration stabilizes at a nontrivial pair (X
′
,Y
′
) rather than collapsing.

No proof obtained.

Strategy 4: Induction on ∣V(H)∣

Let v∈V(H) have degree at most r. Remove v, embed H−v, then try to extend to v.

Obstacle: after embedding H−v, the neighbors of v are fixed. They form a set of at most r vertices. One needs a common neighbor outside the current embedding.

The density of G does not guarantee that this particular r-tuple has any common neighbor.

Unresolved gap:

GAP 4:

Choose the embedding of H−v so that the neighbor set of v lands on a good r-tuple.

This is equivalent to a controlled embedding theorem, not merely an induction.

Strategy 5: Minimal counterexample

Assume a counterexample G with many edges and no copy of H. Pass to a subgraph of high minimum degree.

If

e(G)≫n
2−1/r
,

then one can delete low-degree vertices and obtain a subgraph G
′
 with minimum degree

δ(G
′
)≫n
1−1/r
.

Obstacle: high minimum degree still does not imply that all r-tuples have common neighbors.

For example, even with large minimum degree, neighborhoods may be arranged so that many pairs or r-tuples have empty intersection.

Unresolved gap:

GAP 5:

Upgrade high minimum degree into controlled common-neighborhood structure for the particular pattern required by H.

No proof obtained.

Strategy 6: Counting rooted embeddings

Instead of greedily embedding H, count homomorphisms from H into G.

If the number of homomorphisms is large enough, and the number of non-injective homomorphisms is smaller, then G contains H.

Obstacle: for sparse graphs at density n
−1/r
, homomorphism counts depend on the detailed structure of H. Degeneracy alone gives an upper bound on local dependency, but not enough lower control over injective embeddings.

Unresolved gap:

GAP 6:

Show that every r-degenerate bipartite H has many injective homomorphic images in every graph with e(G)≫n
2−1/r
.

No proof obtained.

Strategy 7: Hypergraph reformulation

Define an auxiliary r-uniform hypergraph on one side of a bipartite host graph: an r-set S is an edge if

∣N(S)∣≥L,

where L is a constant depending on H.

Then embedding H becomes a problem about finding a certain finite pattern inside this auxiliary hypergraph.

Obstacle: density gives a lower bound on the average number of common neighborhoods, but not enough uniformity of the auxiliary hypergraph.

Unresolved gap:

GAP 7:

From

e(G)≫n
2−1/r
,

force the auxiliary r-uniform hypergraph of good tuples to contain the required finite pattern.

No proof obtained.

Strategy 8: Ramsey-cleaning

Color each r-tuple as good or bad depending on whether it has at least L common neighbors. Try to find a large monochromatic subset. If the subset is all-good, embed H.

Obstacle: Ramsey gives a monochromatic subset, but it may be all-bad. Density must rule out large all-bad sets. I could not prove that.

Unresolved gap:

GAP 8:

Show that every sufficiently large subset contains a good r-tuple, or better, a large all-good subset.

No proof obtained.

Strategy 9: Induction on degeneracy layers

Partition H into layers according to a degeneracy deletion process. Attempt to embed the last layer first, then extend layer by layer.

Obstacle: different vertices in one layer may impose overlapping common-neighborhood requirements on the previous layer. The embedding choices become globally coupled.

Unresolved gap:

GAP 9:

Control simultaneous extension demands for many vertices whose neighbor sets are distinct r-tuples.

No proof obtained.

Strategy 10: Blow-up containment

Try to prove that every graph with

e(G)≫n
2−1/r

contains a complete bipartite graph K
s,t
	​

 large enough to contain H.

Obstacle: this is false at the desired exponent for general s,t. Complete bipartite containment alone is too strong.

So this strategy fails.

Strategy 11: Density increment

If the host graph does not contain H, perhaps one can find a denser subgraph on fewer vertices, iterate, and eventually contradict the maximum possible number of edges.

Obstacle: no verified density increment was found. Avoiding H does not obviously force a denser subgraph; it may force pseudorandom-looking behavior instead.

Unresolved gap:

GAP 10:

Find a structural dichotomy: either G contains H, or some large subgraph has noticeably higher normalized density.

No proof obtained.

Strategy 12: Counterexample construction

Try to disprove the statement by constructing H-free graphs with more than

n
2−1/r

edges.

A natural attempt is to use sparse pseudorandom bipartite graphs where most r-tuples have only O(1) common neighbors.

Obstacle: H is fixed. Even constant-size common neighborhoods may be enough to embed a fixed graph if the constants are large. I could not construct a fixed r-degenerate bipartite H avoided by all such dense graphs.

No disproof obtained.

Phase 2: Useful definitions and invariants
Definition: L-good tuple

Let G=(X,Y,E) be bipartite. For S⊆X, define

N(S)=
x∈S
⋂
	​

N(x)⊆Y.

An r-tuple S⊆X is called L-good if

∣N(S)∣≥L.

Similarly for r-tuples in Y.

Motivation: when embedding a vertex whose already embedded neighbors are S, one needs available common neighbors in the opposite side.

Definition: H-admissible pair

A pair of subsets (X
′
,Y
′
) in a bipartite graph G=(X,Y,E) is H-admissible if one can embed H into G[X
′
∪Y
′
] greedily along some degeneracy ordering, with every required common-neighborhood set having at least ∣V(H)∣ unused candidates.

If an H-admissible pair exists, then G contains H.

The target becomes:

Show that every G with e(G)≫n
2−1/r
 contains an H-admissible pair.

This reformulation is correct, but I could not prove the target statement.

Definition: tuple defect

For S⊆X, ∣S∣≤r, define

D
L
	​

(S)=max(0,L−∣N(S)∣).

A graph has small total r-defect on X if

S⊆X
∣S∣≤r
	​

∑
	​

D
L
	​

(S)

is small.

Potential use: if total defect is small, a random embedding of H might avoid defective tuples.

Obstacle: density controls averages of common-neighborhood counts but does not directly control total defect.

Phase 3: Main proof attempts
Branch A: Greedy embedding through good tuples

Let H be r-degenerate with degeneracy ordering

v
1
	​

,…,v
h
	​

.

Embed in reverse order. Suppose v
i
	​

 has already embedded neighbors

v
j
1
	​

	​

,…,v
j
s
	​

	​

,s≤r.

To extend the embedding, the images of those neighbors must have a common neighbor not already used.

Thus, if every s-tuple of already embedded vertices has at least h common neighbors, the embedding succeeds.

So it would suffice to find a set U⊆V(G) such that every relevant s-tuple in U, s≤r, has at least h common neighbors.

For non-bipartite host G, we may first pass to a bipartite subgraph with at least half the edges. Thus it suffices to consider bipartite G=(X,Y,E).

The desired local condition becomes:

∀S⊆X, ∣S∣≤r,∣N(S)∩Y∣≥h,

and similarly from Y into X, at least for the tuples used by the embedding.

The density assumption gives

e(G)≥Cn
2−1/r
.

Let d(y)=∣N(y)∩X∣. Then

y∈Y
∑
	​

(
r
d(y)
	​

)

counts pairs (S,y) with S∈(
r
X
	​

) and y∈N(S).

By convexity,

y∈Y
∑
	​

(
r
d(y)
	​

)

is large when the average degree is large.

Roughly, if ∣X∣,∣Y∣≍n and average degree is ≍Cn
1−1/r
, then

y∈Y
∑
	​

(
r
d(y)
	​

)≍C
r
n
r
.

Since

(
r
∣X∣
	​

)≍n
r
,

the average common neighborhood size of an r-tuple in X is only ≍C
r
, a constant.

For fixed H, a sufficiently large constant might be enough, but this only controls the average. It does not guarantee that the specific tuples needed during embedding are good.

Thus Branch A reaches:

Primary gap A:

Average r-tuple richness must be converted into structured r-tuple richness compatible with every r-degenerate bipartite H.

I could not close this gap.

Branch B: Random embedding

Try to choose the embedding of H randomly so that every required tuple lands on a good tuple.

Let the degeneracy ordering be fixed. For each vertex v
i
	​

, define its forward-neighbor set

F
i
	​

={v
j
	​

:j>i, v
i
	​

v
j
	​

∈E(H)}.

Then

∣F
i
	​

∣≤r.

A reverse greedy embedding fails at step i only if the image of F
i
	​

 has too small a common neighborhood.

Thus one wants to choose images of later vertices so that for every i, the tuple ϕ(F
i
	​

) is good.

This is a constraint satisfaction problem over the auxiliary hypergraph of good tuples.

If the auxiliary hypergraph of good tuples were sufficiently dense and pseudorandom, then a random embedding might work.

But from edge density alone, I only get lower bounds on the average number of witnesses:

S∈(
r
X
	​

)
∑
	​

∣N(S)∣.

This permits the richness to be concentrated on a small family of tuples.

Thus Branch B reaches:

Primary gap B:

Show that the auxiliary hypergraph of good tuples contains the finite dependency pattern induced by the degeneracy ordering of H.

No proof obtained.

Branch C: Induction with controlled extension

Suppose the theorem is true for H−v, where v has degree at most r.

Given dense G, we find a copy of H−v. To extend it to H, the images of N
H
	​

(v) must have a common neighbor.

A naive copy of H−v may not work. Therefore we need a stronger inductive statement:

There are many embeddings of H−v, and among them at least one maps N
H
	​

(v) to a tuple with a common neighbor.

Define

E(H−v,G)

to be the set of embeddings of H−v into G.

One would need a lower bound for

ϕ∈E(H−v,G)
∑
	​

∣N
G
	​

(ϕ(N
H
	​

(v)))∣.

If this sum exceeds

(h−1)∣E(H−v,G)∣,

then some embedding extends.

Obstacle: I could not derive such a lower bound from only

e(G)≫n
2−1/r
.

The embeddings of H−v may be distributed nonuniformly over bad tuples.

Thus Branch C reaches:

Primary gap C:

Prove a weighted common-neighborhood lower bound over embeddings of H−v.

No proof obtained.

Phase 4: Verified partial result

A complete proof was obtained only for the boundary case r=1.

Lemma

If H is a fixed forest with h vertices, then

ex(n;H)≤(h−2)n.
Proof

Let G be an n-vertex graph with average degree at least 2h−2. Then G contains a subgraph G
′
 with minimum degree at least h−1.

Indeed, repeatedly delete vertices of degree at most h−2. If all vertices are deleted, then the original graph had fewer than (h−1)n edges, contradicting the assumed average degree. Hence a nonempty subgraph remains with minimum degree at least h−1.

Now embed the forest H greedily. Root each component of H. Since H has h vertices, at every step fewer than h−1 vertices have already been used. When embedding a new vertex adjacent to its parent, the image of the parent has at least h−1 neighbors in G
′
, so at least one unused neighbor remains.

Thus G
′
, and hence G, contains H.

Therefore every H-free graph has O(n) edges, matching

n
2−1
=n.

So the theorem is proved for r=1.

Phase 5: Attempted extension to r≥2

The natural generalization would be:

Candidate lemma

Let H be fixed, bipartite, and r-degenerate. If G has

e(G)≥C
H
	​

n
2−1/r
,

then there exists a degeneracy-order-compatible embedding of H into G.

To prove this greedily, one needs:

∀S⊆V(G), ∣S∣≤r,

or at least for all relevant S,

∣N
G
	​

(S)∣≥h.

But density only gives an average statement over r-tuples.

Specifically, in a bipartite graph G=(X,Y,E),

S∈(
r
X
	​

)
∑
	​

∣N(S)∣=
y∈Y
∑
	​

(
r
d(y)
	​

).

Large edge count forces the right-hand side to be large, but it does not force every S to have large N(S).

Thus the missing step is not a minor technicality; it is exactly the bridge from average tuple-richness to structured tuple-richness.

I attacked this gap by DRC, symmetric DRC, induction, hypergraph reformulation, Ramsey-cleaning, and weighted embedding counts. None produced a complete proof.

Dependency graph of verified results
Definitions

H bipartite.

H r-degenerate.

ex(n;H).

L-good tuple.

H-admissible pair.

tuple defect.

Verified lemmas
Lemma 1

If H is 1-degenerate, then

ex(n;H)=O(n).

Dependencies:

equivalence between 1-degenerate graphs and forests;

greedy embedding into graphs of minimum degree at least ∣V(H)∣−1.

Lemma 2

In a bipartite graph G=(X,Y,E),

S∈(
r
X
	​

)
∑
	​

∣N(S)∣=
y∈Y
∑
	​

(
r
d(y)
	​

).

Dependencies:

double counting pairs (S,y) such that S⊆N(y).

Lemma 3

A reverse degeneracy-order embedding of H succeeds if every required common-neighborhood tuple has at least ∣V(H)∣ available candidates.

Dependencies:

degeneracy ordering;

greedy embedding;

finite size of H.

Unresolved primary gap

The unresolved core statement is:

High edge density e(G)≫n
2−1/r
 forces enough structured good r-tuples to embed every fixed bipartite r-degenerate H.
	​


I did not prove this statement.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified partial statements; 0 for the full target theorem.

COMPLETENESS_SCORE: 20/100. The r=1 case and several necessary reformulations were rigorously established, but the main r≥2 embedding step remains unresolved.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the negative assessment of the attempted proof strategies; the identified gap survives multiple attacks.

RESOURCE_USAGE: approximately 12 branches explored, 7 auxiliary definitions/invariants generated, 10 major gap nodes identified, 6 failed proof attempts, 1 verified boundary-case proof.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

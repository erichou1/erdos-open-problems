# Erdős Problem #108 [unsolved] 18%

---

## ChatGPT Response

Phase 0: Complete formalization

Let all graphs be finite, simple, undirected.

For a graph G, let χ(G) be its chromatic number.
Let girth(G) be the length of the shortest cycle in G, with girth(G)=∞ if G is acyclic.

The target statement is:

∀r≥4 ∀k≥2 ∃f(k,r)∈N ∀G(χ(G)≥f(k,r)⇒∃H⊆G:girth(H)≥r, χ(H)≥k).

Here H⊆G means V(H)⊆V(G) and E(H)⊆E(G[V(H)]).

Negation

The statement is false iff

∃r≥4 ∃k≥2 ∀N∈N ∃G
N
	​


such that

χ(G
N
	​

)≥N

and every subgraph H⊆G
N
	​

 with girth(H)≥r satisfies

χ(H)<k.

Equivalently, for some fixed r,k, there are graphs of arbitrarily large chromatic number whose every k-chromatic subgraph contains a cycle of length <r.

Contrapositive form

For fixed r,k, the desired assertion is equivalent to:

There exists F=F(k,r) such that if every subgraph H⊆G with girth(H)≥r has χ(H)<k, then

χ(G)<F.

So the problem becomes: can graphs whose high-girth subgraphs all have bounded chromatic number still have unbounded chromatic number?

Extremal cases

For k=2, the statement is true with

f(2,r)=2.

Indeed, if χ(G)≥2, then G has at least one edge. A single edge has girth ∞ and chromatic number 2.

For r=3, the statement is trivial with

f(k,3)=k,

because every graph has girth at least 3 unless it has no cycles, and no cycle shorter than 3 exists in a simple graph.

The real content begins at

r≥4,k≥3.
Phase 1: Breadth-first proof search

I considered the following independent strategies.

1. Direct edge-deletion strategy

Try to start with a high-chromatic graph G, delete edges from short cycles, and preserve chromatic number at least k.

Obstacle: deleting one edge from each short cycle may destroy chromatic number. A critical graph can lose chromatic number after deleting any edge.

Status: no complete proof.

2. Minimal critical subgraph strategy

Replace G by a χ(G)-critical subgraph G
′
. Then every vertex has degree at least χ(G
′
)−1.

Verified fact:

If G is q-critical, then

δ(G)≥q−1.

Proof: if some vertex v had degree at most q−2, then G−v is (q−1)-colorable, and v could be colored using a missing color among its neighbors.

Obstacle: high minimum degree alone does not force high chromatic high-girth subgraphs, since high-degree bipartite graphs can have chromatic number 2.

Status: useful but insufficient.

3. Probabilistic edge sampling

Choose each edge independently with probability p. Hope that the sampled graph has few short cycles but still high chromatic number.

Obstacle: in an arbitrary high-chromatic graph, chromatic number is not controlled by edge density alone. Random edge deletion can easily collapse color constraints.

Status: promising but gap remains: need a theorem saying random sparsification preserves chromatic number in arbitrary high-chromatic graphs.

4. Vertex sampling

Choose a random vertex subset, then perhaps delete short-cycle edges.

Obstacle: vertex sampling preserves induced local structure, including many short cycles. It does not obviously remove short cycles while preserving chromatic number.

Status: unresolved.

5. BFS layering

Fix a root v. Let L
i
	​

 be vertices at distance i from v. Since edges only occur inside a layer or between adjacent layers, if every G[L
i
	​

] had small chromatic number, then G would have small chromatic number.

Verified lemma:

If every layer L
i
	​

 satisfies

χ(G[L
i
	​

])≤c,

then

χ(G)≤2c.

Proof: color even layers using one palette of c colors and odd layers using a disjoint palette of c colors. Edges between adjacent layers use different palettes, and edges inside a layer are properly colored by assumption.

Therefore, if

χ(G)>2c,

some layer has chromatic number >c.

Obstacle: passing to a high-chromatic layer does not obviously increase girth. Short cycles may remain entirely inside the layer.

Status: useful recursive device but not enough.

6. Induction on r

Assume the statement for girth ≥r, try to prove it for girth ≥r+1.

One would start with a subgraph H of girth ≥r and high chromatic number, then try to remove all r-cycles while preserving chromatic number.

Obstacle: removing one edge from every r-cycle can destroy chromatic number.

Status: reduction found, not solved.

7. Induction on k

Assume the statement for k, try to prove it for k+1.

Obstacle: having many girth-≥r, k-chromatic subgraphs does not obviously combine into one (k+1)-chromatic such subgraph.

Status: no complete route.

8. Cardinal arithmetic / finite obstruction formulation

For fixed r,k, define

C
r,k
	​

={G: every H⊆G with girth(H)≥r satisfies χ(H)<k}.

The desired statement is equivalent to saying

G∈C
r,k
	​

sup
	​

χ(G)<∞.

Obstacle: no closure property of C
r,k
	​

 gives an immediate chromatic bound.

Status: reformulation only.

9. Diagonal counterexample search

Try to construct G
n
	​

 with χ(G
n
	​

)→∞ but all high-girth subgraphs have chromatic <k.

Natural candidates include graphs whose chromatic number is generated by many forced short cycles.

Obstacle: every attempted construction must also prevent arbitrary edge deletion from exposing a sparse high-chromatic subgraph.

Status: no counterexample constructed.

10. Compactness / infinitary transfer

Try to prove the finite statement from an infinite version, or disprove it by compactness.

Obstacle: the finite and infinite versions are not automatically equivalent. A sequence of finite counterexamples with χ(G
n
	​

)→∞ does not directly produce an infinite graph of infinite chromatic number with the same forbidden-subgraph property unless one controls embeddings or takes an ultraproduct-like limit, which introduces extra machinery not justified here.

Status: unresolved.

11. Density argument

High chromatic number implies existence of a subgraph with high minimum degree. Perhaps high minimum degree plus non-bipartiteness yields high-girth high-chromatic subgraphs.

Obstacle: high minimum degree alone is compatible with bipartiteness. Chromatic number is a global obstruction not captured by local density.

Status: insufficient.

12. Auxiliary matroid / short-cycle hypergraph strategy

Let the edges of G be vertices of a hypergraph S, whose hyperedges are the edge sets of cycles of length <r. We want a subset of edges avoiding all hyperedges of S, while preserving chromatic number.

Obstacle: being high-chromatic is not a monotone linear condition in the edge set that can be directly handled by hypergraph independence.

Status: promising abstraction, but no proof.

Phase 2: New definitions and invariants
Definition 1: r-sparse chromatic core

For fixed r, define

ψ
r
	​

(G)=max{χ(H):H⊆G, girth(H)≥r}.

The target statement is equivalent to:

∀r≥4, ∀k≥2, ∃Fψ
r
	​

(G)<k⇒χ(G)<F.

So the question asks whether bounded ψ
r
	​

(G) forces bounded χ(G).

Definition 2: short-cycle hitting number

Let

τ
r
	​

(G)

be the minimum number of edges that must be deleted from G to destroy all cycles of length <r.

If τ
r
	​

(G) is small, then one can delete few edges to obtain girth ≥r. But small edge deletion does not guarantee chromatic preservation.

Definition 3: chromatic fragility

Call an edge set X⊆E(G) k-essential if

χ(G−X)<k.

A graph is highly fragile if every short-cycle hitting set is k-essential.

The negation of the theorem says that for some r,k, there are graphs of arbitrarily large chromatic number in which every edge set killing all cycles of length <r is k-essential.

This is a useful adversarial reformulation.

Phase 3: Three main branches
Branch A: Try to prove by deleting short cycles

Suppose G has very large chromatic number. Let G
′
⊆G be q-critical with q=χ(G
′
).

Then

δ(G
′
)≥q−1.

If one could find a subgraph J⊆G
′
 with

χ(J)≥k

and relatively few short cycles, then deleting one edge from each short cycle might preserve χ(J)≥k.

The missing statement would be:

For every r,k, there exists q such that every q-critical graph has a k-chromatic subgraph J where the short cycles can be destroyed without lowering chromatic number below k.

I cannot prove this statement. The obstruction is that critical graphs can be edge-fragile: removing one edge can lower the chromatic number.

Branch A fails at this gap.

Branch B: Try to prove by BFS layering

Let G have large chromatic number. Choose a component of large chromatic number and fix a root v. Let L
i
	​

 be the BFS levels.

Because edges only lie within one level or between consecutive levels, if all levels have chromatic number <m, then

χ(G)≤2m.

Therefore some level L
i
	​

 has large chromatic number.

Now restrict to G[L
i
	​

]. The hope is that cycles in G[L
i
	​

] correspond to longer cycles in G after adding paths through the BFS tree. But this only gives controlled cycles using tree paths, not arbitrary cycles inside L
i
	​

.

More explicitly, if xy∈E(G[L
i
	​

]), then the two tree paths from x and y to their last common ancestor plus the edge xy form a cycle of length

2(i−d)+1,

where d is the depth of the last common ancestor. This is always odd, but its length may be small if x,y share a recent ancestor.

One could try to partition L
i
	​

 by recent ancestors. Edges inside the same recent-ancestor class are dangerous because they create short cycles. Edges between sufficiently separated classes create long cycles relative to the BFS tree.

The needed lemma becomes:

A sufficiently high-chromatic BFS layer contains a high-chromatic subgraph whose edges avoid pairs with recent common ancestors.

I could not prove this. The ancestor classes may be numerous, and coloring arguments do not give a clean bound independent of ∣G∣.

Branch B produces useful structure but does not complete the theorem.

Branch C: Try to disprove using chromatic constructions dominated by short cycles

To disprove the statement, one needs fixed r,k and graphs G
n
	​

 with

χ(G
n
	​

)→∞

such that every subgraph H⊆G
n
	​

 satisfying

girth(H)≥r

has

χ(H)<k.

For r=5, this would mean graphs of unbounded chromatic number whose every C
3
	​

-free and C
4
	​

-free subgraph has chromatic number <k.

A tempting counterexample template is to build chromatic number by repeatedly adding local configurations that force color increases but introduce many short cycles. However, because the desired H is an arbitrary subgraph, not induced, the construction must prevent the deletion of short-cycle edges from revealing a high-chromatic sparse core.

That is very strong. I found no construction satisfying it.

Branch C fails to produce a disproof.

Verified partial results
Lemma 1: The case k=2 is true

For every r≥4,

f(2,r)=2

works.

Proof: If χ(G)≥2, then G contains an edge. A single edge has chromatic number 2 and girth ∞≥r.

Lemma 2: High chromatic number gives a high-minimum-degree subgraph

If χ(G)≥q, then G contains a subgraph G
′
⊆G with

χ(G
′
)=q
′
≥q

and

δ(G
′
)≥q
′
−1.

More simply, taking a χ(G)-critical subgraph gives

δ(G
′
)≥χ(G
′
)−1.

This is verified, but not sufficient.

Lemma 3: BFS layer lemma

For any connected graph G, root v, and BFS levels L
i
	​

, if

χ(G[L
i
	​

])≤c

for every i, then

χ(G)≤2c.

Therefore, if

χ(G)>2c,

then some BFS layer has chromatic number >c.

This is verified, but again insufficient.

Dependency graph of established facts
definitions⇒formal equivalence using ψ
r
	​

(G)
χ(G)≥q⇒∃q-critical G
′
⊆G⇒δ(G
′
)≥q−1
BFS layering⇒[∀i, χ(G[L
i
	​

])≤c]⇒χ(G)≤2c

None of these verified lemmas implies the full target theorem.

Adversarial check

The most plausible proof routes all encounter the same core difficulty:

Deleting short cycles is easy; preserving chromatic number is hard.

The most plausible counterexample routes encounter the dual difficulty:

Forcing high chromatic number through short cycles is possible in spirit, but preventing every edge-deleted high-girth subgraph from having chromatic number k is much harder.

I found no contradiction, no complete proof, and no complete disproof.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified partial lemmas and formal equivalences.
COMPLETENESS_SCORE: 18/100 for the original problem.
ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the negative conclusion “no proof or disproof was established here”; 30/100 for any route toward the full theorem.
RESOURCE_USAGE: approximately 100% of this response budget; 12 strategies examined; 3 branches explored; 3 verified lemmas; 0 complete proofs of the original statement; 0 complete disproofs.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #104 [unsolved] 28%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Phase 0: formalization

I work with finite simple undirected graphs. For a graph G,

χ(G)=chromatic number of G,

and

girth(G)={
min{∣C∣:C is a cycle in G},
∞,
	​

G has a cycle,
G is acyclic.
	​


For fixed integers r≥4, k≥2, the target statement is:

∃N∈N ∀G (χ(G)≥N⟹∃H⊆G (girth(H)≥r ∧ χ(H)≥k)).

Equivalently, define

h
r
	​

(G)=max{χ(H):H⊆G, girth(H)≥r}.

Then the statement becomes:

∀r≥4 ∀k≥2 ∃N∈N ∀G(χ(G)≥N⟹h
r
	​

(G)≥k).

The negation is:

∃r≥4 ∃k≥2 ∀N∈N ∃G
N
	​


such that

χ(G
N
	​

)≥N

but

∀H⊆G
N
	​

,girth(H)≥r⟹χ(H)≤k−1.

So a counterexample family would be a sequence of graphs with unbounded chromatic number but uniformly bounded h
r
	​

(G)≤k−1.

The fixed-(k,r) contrapositive is:

∃N∈N ∀G,h
r
	​

(G)≤k−1⟹χ(G)<N.

Thus the problem asks whether the hereditary graph class

C
k,r
	​

={G:h
r
	​

(G)≤k−1}

has bounded chromatic number.

Boundary cases:

k=2 is trivial.
If χ(G)≥2, then G has an edge. A single edge has girth ∞ and chromatic number 2. Hence

f(2,r)=2

works for every r≥4.

r≤3 would be trivial for simple graphs, because every simple graph has girth at least 3 unless it is acyclic. Then f(k,3)=k. The real obstruction begins at r=4.

Monotonicity, whenever the relevant quantities exist:

f(k,r)≤f(k+1,r),

and

f(k,r)≤f(k,r+1).

The second inequality holds because girth(H)≥r+1 implies girth(H)≥r.

Equivalent formulations
Edge-deletion form

A subgraph H⊆G of girth at least r is obtained by deleting edges until all cycles of length <r are destroyed. Thus the problem asks whether sufficiently large χ(G) guarantees an edge subset F⊆E(G) such that

(V(F),F)

has no cycles of length <r and has chromatic number at least k.

Coloring-certificate form

A graph H has χ(H)≥k iff every (k−1)-coloring of V(H) makes at least one edge of H monochromatic. Therefore the desired H is an edge set F⊆E(G) satisfying simultaneously:

F contains no cycle of length <r,

and

∀φ:V(H)→[k−1],∃uv∈F with φ(u)=φ(v).

So the task is to select edges that hit every (k−1)-coloring while avoiding all short cycles.

Critical-graph reduction

If a counterexample exists for fixed (k,r), then for every m there is an m-chromatic graph G
m
	​

 such that h
r
	​

(G
m
	​

)≤k−1. Passing to an m-critical subgraph preserves the bad property, because every subgraph of the critical graph is also a subgraph of the original graph.

Thus any counterexample family may be assumed to satisfy

χ(G
m
	​

)=m

and

δ(G
m
	​

)≥m−1.

This gives high minimum degree but does not by itself force a high-girth, high-chromatic subgraph.

Verified lemmas
Lemma 1: One-edge deletion lowers chromatic number by at most one

Let G be a graph and e∈E(G). Then

χ(G−e)≥χ(G)−1.

Proof. Let q=χ(G−e). Properly color G−e with q colors. If the two endpoints of e receive distinct colors, this is already a proper coloring of G, so χ(G)≤q. If they receive the same color, recolor one endpoint with a new color. Then G is properly colored with q+1 colors. Hence

χ(G)≤q+1,

so

q≥χ(G)−1.

Thus

χ(G−e)≥χ(G)−1.

More generally, deleting t edges lowers chromatic number by at most t:

χ(G−F)≥χ(G)−∣F∣.
Lemma 2: Every low-coloring has many monochromatic edges, but only linearly many in χ(G)

Let χ(G)=m, and let φ:V(G)→[q] be any q-coloring, not necessarily proper. Let M
φ
	​

 be the set of monochromatic edges under φ. Then

∣M
φ
	​

∣≥m−q.

Proof. Deleting all monochromatic edges gives a q-colorable graph. Therefore

χ(G−M
φ
	​

)≤q.

By Lemma 1,

χ(G−M
φ
	​

)≥m−∣M
φ
	​

∣.

Hence

m−∣M
φ
	​

∣≤q,

so

∣M
φ
	​

∣≥m−q.

This is useful but too weak for a naive union bound over all (k−1)
∣V(G)∣
 colorings.

Lemma 3: The desired statement is equivalent to boundedness of a hereditary class

For fixed k,r, define

C
k,r
	​

={G:h
r
	​

(G)≤k−1}.

Then the desired statement for (k,r) is equivalent to:

sup{χ(G):G∈C
k,r
	​

}<∞.

Proof. If this supremum is finite, take

f(k,r)=1+sup{χ(G):G∈C
k,r
	​

}.

Then every graph with chromatic number at least f(k,r) is not in C
k,r
	​

, so it has some subgraph of girth at least r and chromatic number at least k.

Conversely, if such an f(k,r) exists, then every graph in C
k,r
	​

 has chromatic number <f(k,r), so the class is chromatically bounded.

Breadth-first strategy search

I generated the following independent approaches.

Strategy 1: Direct maximal-subgraph argument

Take a maximal subgraph H⊆G with girth at least r. If χ(H)≥k, done. Otherwise χ(H)≤k−1. Maximality implies every missing edge uv∈E(G)∖E(H) creates a cycle of length <r, so u,v are at distance at most r−2 in H. Hence

G⊆H
r−2
,

where H
r−2
 is the (r−2)-th power of H.

Obstacle: even if χ(H)≤k−1, the graph power H
r−2
 can have unbounded chromatic number. For example, if H is a large star, then H
2
 contains a clique on all leaves. Thus low chromatic number of a maximal high-girth subgraph does not bound χ(G).

Status: failed.

Strategy 2: Random sparsification

Choose a random subgraph G
p
	​

 by keeping each edge independently with probability p. Try to ensure:

χ(G
p
	​

)≥k

while the number of cycles of length <r is small enough that deleting one edge from each such cycle leaves chromatic number at least k.

Obstacle: in an arbitrary high-chromatic graph, the number of short cycles may be enormous. Also, Lemma 2 gives only

∣M
φ
	​

∣≥χ(G)−(k−1)

monochromatic edges for a fixed (k−1)-coloring φ, which is too weak to union-bound over all colorings.

Status: unresolved.

Strategy 3: Critical graph plus minimum degree

Assume a minimal counterexample G with χ(G)=m. Then

δ(G)≥m−1.

Try to build a high-girth subgraph with chromatic number at least k from this large minimum degree.

Obstacle: high minimum degree alone does not imply high chromatic number after imposing large girth. A high-degree bipartite graph can have arbitrarily large girth but chromatic number 2.

Status: failed as a standalone route.

Strategy 4: Induction on r

Assume the statement for r. From a very high-chromatic graph G, obtain a subgraph H with

girth(H)≥r

and very large chromatic number. Then attempt to delete edges from H to destroy all r-cycles while preserving chromatic number at least k.

Obstacle: no verified method was found to delete one edge from each r-cycle while controlling the loss of chromatic number.

Status: reduction found, but not a proof.

Strategy 5: Coloring-hitting formulation

For every (k−1)-coloring φ, choose a monochromatic edge e
φ
	​

. Let

F={e
φ
	​

:φ:V(G)→[k−1]}.

Then (V,F) has chromatic number at least k.

Obstacle: F may contain many short cycles. Need to choose the witnesses e
φ
	​

 so that F avoids all cycles of length <r. No verified selection principle was obtained.

Status: unresolved.

Strategy 6: Hypergraph transversal

Let S
r
	​

(G) be the hypergraph whose hyperedges are the edge sets of cycles of length <r. We need an edge set F⊆E(G) avoiding every hyperedge in S
r
	​

(G), while still being non-(k−1)-colorable.

Obstacle: the acyclicity condition is downward-closed, while non-(k−1)-colorability is upward-closed. The desired F lies at the interface of two opposing monotone properties. No general min-max theorem was derived.

Status: unresolved.

Strategy 7: Ramsey/clique control

If G contains a sufficiently large clique, then G contains any fixed finite graph on that many vertices. Therefore, if one can construct a finite graph F
k,r
	​

 with

girth(F
k,r
	​

)≥r

and

χ(F
k,r
	​

)≥k,

then any bad graph must have bounded clique number.

This part is useful: potential counterexamples must have both unbounded chromatic number and bounded clique number.

Obstacle: bounded clique number plus high chromatic number does not directly produce a high-girth, high-chromatic subgraph.

Status: useful reduction, not a solution.

Strategy 8: BFS layering

In a graph of large minimum degree, take breadth-first layers from a root. If many short cycles are absent, layers expand rapidly. If expansion fails, many short cycles exist. Try to use either case.

Obstacle: expansion gives large trees, but trees are bipartite. Abundance of short cycles is exactly what must eventually be deleted. No bridge was found from expansion to chromatic number ≥k.

Status: failed.

Strategy 9: Degeneracy extraction

Every graph of chromatic number m contains a subgraph of minimum degree at least m−1. Try to extract a sparse subgraph of still-large degeneracy and large girth.

Obstacle: large degeneracy does not force large chromatic number in the desired subgraph unless odd-cycle structure is also retained.

Status: failed.

Strategy 10: Minimal non-(k−1)-colorable certificates

A graph H with χ(H)≥k contains a k-critical subgraph. Try to find a k-critical subgraph whose short cycles can be removed.

Obstacle: k-critical graphs may have many short cycles, and deleting one edge from a k-critical graph may reduce its chromatic number below k.

Status: failed.

Strategy 11: Auxiliary rank function on short cycles

Define a short-cycle rank measuring how entangled the cycles of length <r are. Try induction on that rank.

Obstacle: a graph may have enormous short-cycle rank, and reducing it by edge deletions may destroy the chromatic obstruction.

Status: no verified monotone rank found.

Strategy 12: Counterexample construction

Try to construct graphs G
m
	​

 with χ(G
m
	​

)→∞ but h
r
	​

(G
m
	​

)≤k−1.

Natural attempts fail:

Complete graphs fail because large complete graphs contain every fixed finite high-girth, high-chromatic graph.

Complete multipartite graphs fail for the same reason once they have sufficiently many parts.

Dense blow-ups fail because one can often select sparse cross-edges.

Purely local short-cycle constructions tend to have bounded chromatic number unless arranged globally.

Status: no counterexample found.

Verified auxiliary construction: high-girth high-chromatic graphs exist

This does not solve the main problem, but it proves that bad graphs must have bounded clique number.

For fixed k,r, one can construct a finite graph F
k,r
	​

 with

girth(F
k,r
	​

)≥r

and

χ(F
k,r
	​

)≥k.

Sketch with explicit estimates.

Take a random graph X∼G(n,p) with

p=n
−1+ϵ

where 0<ϵ<1/r.

For a fixed cycle length 3≤ℓ<r, the expected number of ℓ-cycles is at most

2ℓ
n
ℓ
p
ℓ
	​

=O(n
ℓϵ
).

Since ℓ<r and ϵ<1/r,

ℓϵ<1,

so the expected number of cycles of length <r is

o(n).

Now choose

a=⌊
2k
n
	​

⌋.

The expected number of independent sets of size a is at most

(
a
n
	​

)(1−p)
(
2
a
	​

)
.

Using

(
a
n
	​

)≤(
a
en
	​

)
a

and

1−p≤e
−p
,

this is at most

(
a
en
	​

)
a
exp(−p(
2
a
	​

)).

Here a=Θ(n), so the positive exponent from the binomial coefficient is O(n), while

p(
2
a
	​

)=Θ(n
−1+ϵ
n
2
)=Θ(n
1+ϵ
).

Thus the expected number of independent sets of size a tends to 0.

Therefore, for large n, there exists a graph X with fewer than n/(4k) short cycles and no independent set of size n/(2k).

Delete one vertex from each cycle of length <r. The remaining graph F has at least

n−
4k
n
	​


vertices and girth at least r. Its independence number is still less than

2k
n
	​

.

Therefore

χ(F)≥
α(F)
∣V(F)∣
	​

>
n/(2k)
n−n/(4k)
	​

=2k−
2
1
	​

≥k.

So such an F
k,r
	​

 exists.

Consequence: if G is bad for (k,r), meaning h
r
	​

(G)≤k−1, then G cannot contain a clique of size ∣V(F
k,r
	​

)∣, because that clique would contain F
k,r
	​

 as a subgraph. Hence every bad graph has bounded clique number.

This gives:

G∈C
k,r
	​

⟹ω(G)<∣V(F
k,r
	​

)∣.

But bounded clique number does not imply bounded chromatic number, so this does not finish the proof.

Main obstruction after recursive attack

The strongest reduced target I reached is:

Target A:

For every k,r, every graph G with sufficiently large chromatic number and bounded clique number contains a subgraph H⊆G with

girth(H)≥r

and

χ(H)≥k.

This would prove the original statement because bad graphs already have bounded clique number.

However, Target A remains unresolved here. The attempted routes into Target A failed for precise reasons:

High minimum degree gives expansion but not chromatic number after sparsification.

Random edge sampling cannot be controlled using only χ(G), because the number of vertex colorings depends on ∣V(G)∣, which is not bounded in terms of χ(G).

Maximal high-girth subgraphs may have low chromatic number even inside graphs that do contain good subgraphs; arbitrary maximality is too weak.

Deleting short cycles one by one may reduce chromatic number too much.

Bounded clique number blocks the complete-graph obstruction but gives no direct high-girth structure.

Gap-node recursion
GAP NODE 1

Statement:

h
r
	​

(G)≤k−1⟹χ(G)≤C(k,r).

Attacks attempted:

Direct contradiction using critical graphs.

Random sparsification.

Maximal high-girth subgraph.

Induction on r.

Coloring-hitting formulation.

Short-cycle hypergraph formulation.

Clique-bounding plus Ramsey.

BFS expansion.

Degeneracy extraction.

Counterexample search.

Outcome: no proof, no disproof.

GAP NODE 2

Statement:

If G is m-critical and ω(G)≤s, then for m sufficiently large, G contains a high-girth k-chromatic subgraph.

Outcome: no proof. High minimum degree and bounded clique number do not by themselves yield the required edge selection.

GAP NODE 3

Statement:

A random sparse subgraph of an arbitrary high-chromatic graph retains chromatic number at least k while containing few short cycles.

Outcome: no proof. The obstruction is the lack of a sufficiently strong lower bound on monochromatic edges for every (k−1)-coloring.

GAP NODE 4

Statement:

There exists a selection of one monochromatic edge from each (k−1)-coloring such that the selected edge set has girth at least r.

Outcome: no proof. This is a constrained transversal problem with no derived selection theorem.

Final dependency graph of verified results

Verified:

k=2 case:

f(2,r)=2.

Fixed-(k,r) reformulation:

∃f(k,r)⟺C
k,r
	​

 has bounded chromatic number.

Edge-deletion lemma:

χ(G−F)≥χ(G)−∣F∣.

Monochromatic-edge lower bound:

every q-coloring of an m-chromatic graph has at least m−q monochromatic edges.

Existence of finite graphs with both large girth and large chromatic number.

Therefore, any counterexample family must have bounded clique number.

Unresolved:

bounded clique number+unbounded chromatic number⟹high-girth high-chromatic subgraph
	​


for the required parameters.

No complete proof or disproof was obtained from first principles within this run.

PROOF_CONFIDENCE: 92/100

COMPLETENESS_SCORE: 28/100

ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE: approximately 100% of the allocated response budget used; 12 strategies explored; 6 verified lemmas or reductions generated; 8 failed proof attempts recorded; 4 major unresolved gap nodes isolated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

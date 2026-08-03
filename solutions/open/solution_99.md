# Erdős Problem #99 [unsolved] 18%

---

## ChatGPT Response

Phase 0: Formalization

Let all graphs be simple undirected graphs. For a graph H, define

girth(H)={
length of a shortest cycle in H,
∞,
	​

H has a cycle,
H is acyclic.
	​


The target statement is:

∀r≥4 ∀k≥2 ∃f(k,r)<∞ ∀G[χ(G)≥f(k,r)⇒∃H⊆G (girth(H)≥r ∧ χ(H)≥k)].

Equivalently, for fixed k,r, define

C
k,r
	​

={G: every subgraph H⊆G with girth ≥r satisfies χ(H)≤k−1}.

The statement says:

G∈C
k,r
	​

sup
	​

χ(G)<∞.

The negation is:

∃r≥4 ∃k≥2 ∀N ∃G
N
	​

[χ(G
N
	​

)≥N ∧ ∀H⊆G
N
	​

, girth(H)≥r⇒χ(H)≤k−1].

The contrapositive form is:

∀k,r ∃f(k,r)such that if every girth-≥r subgraph of G is (k−1)-colorable, then χ(G)<f(k,r).

Basic monotonicities:

k
1
	​

≤k
2
	​

⇒f(k
1
	​

,r)≤f(k
2
	​

,r)

whenever both sides exist, because requiring chromatic number at least k
2
	​

 is stronger.

Also,

r
1
	​

≤r
2
	​


means girth ≥r
2
	​

 is stronger than girth ≥r
1
	​

. Thus existence for r
2
	​

 implies existence for r
1
	​

, but not conversely.

Verified extremal case: k=2

For every r≥4, one may take

f(2,r)=2.

Indeed, if χ(G)≥2, then G has at least one edge uv. The one-edge subgraph H on {u,v} has no cycles, so

girth(H)=∞≥r,

and

χ(H)=2.

So the statement is proved for k=2.

Equivalent obstruction problem

For k≥3, the task is to rule out graphs G with arbitrarily large chromatic number but whose every high-girth subgraph has chromatic number at most k−1.

Thus the real target is:

High chromatic number must force high-girth chromatic complexity.
	​


A direct proof would need to show that chromatic complexity cannot be supported only by short cycles.

Breadth-first strategy inventory

I tested the following independent proof routes.

Strategy	Core idea	Main obstruction
Direct edge deletion	Delete one edge from every cycle of length <r while preserving χ≥k.	No bound on how many deletions a coloring-critical graph can tolerate.
Random sparsification	Choose a random subgraph, then destroy short cycles.	Need to prove chromatic number survives in an arbitrary host graph.
Minimal critical subgraph	Pass to an N-critical subgraph of G.	Criticality gives minimum degree, but high minimum degree does not force high chromatic high-girth subgraphs.
BFS layering	Use high chromatic number in some level.	A level can still contain many short cycles.
Maximal high-girth subgraph	Take maximal H⊆G with girth ≥r.	Edges outside H only connect vertices at short H-distance, but powers of low-chromatic high-girth graphs can have unbounded chromatic number.
Induction on r	Assume girth ≥r, try to delete all r-cycles.	Requires a strong lemma: high chromatic girth-r graphs contain high chromatic C
r
	​

-free subgraphs.
Induction on k	Build a k-chromatic high-girth subgraph from lower chromatic pieces.	No clean way to force the final color obstruction.
Cardinal compactness	Reduce infinite-looking behavior to finite subgraphs.	Helps only after the finite statement is known.
Diagonal obstruction	Try to construct G
N
	​

 with all high-girth subgraphs low chromatic.	No explicit construction survived basic tests.
Clique reduction	If G has a huge clique, embed a known high-girth k-chromatic graph.	High chromatic number need not come from large cliques.
Average degree	High chromatic critical graph has high minimum degree.	High degree alone does not imply high chromatic number; bipartite graphs can have arbitrary degree.
Auxiliary hypergraph	Treat short cycles as hyperedges and seek a chromatic-preserving transversal.	Need a nontrivial transversal theorem not derived here.

The three most promising routes were random sparsification, maximal high-girth subgraphs, and induction on r. All three reached nontrivial gaps.

Verified theorem pool
Lemma 1: Large complete graphs contain high-girth high-chromatic subgraphs

For every k≥2 and r≥3, there exists a finite graph F
k,r
	​

 such that

girth(F
k,r
	​

)≥randχ(F
k,r
	​

)≥k.

Proof sketch from first principles:

Choose n large and let G∼G(n,p), with

p=n
−α

where

1−
r−1
1
	​

<α<1.

The expected number of cycles of length <r is at most

ℓ=3
∑
r−1
	​

2ℓ
n
ℓ
p
ℓ
	​

=O(n
(1−α)(r−1)
)=o(n).

So with positive probability, fewer than n/2 vertices meet all short cycles.

Now let

s=
2k
n
	​

.

The probability that a fixed s-set is independent is

(1−p)
(
2
s
	​

)
≤exp(−p(
2
s
	​

)).

The number of s-sets is at most

(
s
n
	​

)≤exp(O(n)).

But

p(
2
s
	​

)≍n
−α
⋅n
2
=n
2−α
,

and since α<1,

n
2−α
≫n.

Therefore, with positive probability, no independent set has size s.

Delete one vertex from every cycle of length <r. Since fewer than n/2 vertices are deleted, the remaining graph F has at least n/2 vertices and girth at least r. Its independence number is still less than n/(2k). Hence

χ(F)≥
α(F)
∣V(F)∣
	​

>
n/(2k)
n/2
	​

=k.

So χ(F)≥k.

Therefore, every sufficiently large complete graph contains a subgraph of girth ≥r and chromatic number ≥k.

This proves the original statement for graphs whose chromatic number is witnessed by a sufficiently large clique, but it does not handle arbitrary high-chromatic graphs.

Lemma 2: Maximal high-girth subgraphs localize all remaining edges

Let H⊆G be maximal by edge inclusion subject to

girth(H)≥r.

Then every edge uv∈E(G)∖E(H) has its endpoints connected in H by a path of length at most r−2.

Proof:

If u,v were in different components of H, then adding uv would create no cycle, so girth would remain ≥r, contradicting maximality.

If every u-to-v path in H had length at least r−1, then adding uv would create only cycles of length at least

(r−1)+1=r.

Again H+uv would have girth at least r, contradicting maximality.

Therefore u,v are connected in H by a path of length at most r−2.

So

G⊆H
r−2
,

where H
r−2
 is the graph joining vertices whose H-distance is at most r−2.

This is useful, but insufficient. Even when H has girth ≥r and low chromatic number, the power H
r−2
 can have unbounded chromatic number. For example, if H is a star, then H
2
 contains a clique on all leaves.

Thus this route needs an additional argument controlling the chromatic behavior of local distance neighborhoods. I did not obtain such an argument.

Lemma 3: The k=3 target reduces to long odd cycles

For k=3, a subgraph H with

χ(H)≥3

is equivalent to H being non-bipartite, hence containing an odd cycle.

If additionally

girth(H)≥r,

then H contains an odd cycle of length at least r.

Thus the k=3 case asks whether sufficiently large chromatic number forces an odd cycle of length at least r.

A partial route is:

Pass to a χ(G)-critical subgraph.

Then minimum degree is at least χ(G)−1.

Try to force a long odd cycle from high minimum degree and non-bipartiteness.

The obstruction is parity: high minimum degree gives long cycles, but the direct minimum-degree argument does not automatically force long odd cycles without an additional lemma. I did not complete that lemma from first principles.

Main unresolved gap

The strongest missing statement is the following.

Gap S(k,r)

For every k,r, there exists N=N(k,r) such that every graph G with

χ(G)≥N

has an edge subset E
′
⊆E(G) such that the subgraph

H=(V(G),E
′
)

satisfies

girth(H)≥randχ(H)≥k.

Random sparsification suggests this should be the right mechanism, but the unresolved part is:

prove that chromatic number survives sparsification in an arbitrary high-chromatic host graph.
	​


For complete graphs, this is handled by independence-number estimates. For arbitrary graphs, those estimates fail because the host graph may have many vertex colorings and highly uneven local structure.

Adversarial checks
Check 1: Does high minimum degree suffice?

No. A complete bipartite graph K
n,n
	​

 has minimum degree n, but chromatic number 2. So any proof using only average or minimum degree cannot prove the target statement.

Check 2: Does a maximal high-girth subgraph suffice?

No. If H is a star, then H has girth ∞ and chromatic number 2, but H
2
 contains an arbitrarily large clique on the leaves. Thus bounding χ(H) does not bound χ(G).

Check 3: Does large clique number solve the problem?

Yes, but only in a special case. Large cliques contain every graph on sufficiently few vertices, including a high-girth k-chromatic graph. But high chromatic number can occur with small clique number, so this does not solve the general case.

Check 4: Does deleting one edge from every short cycle preserve chromatic number?

Not automatically. A graph can be chromatic-critical, meaning many edge deletions may reduce chromatic number. No deletion budget sufficient for arbitrary G was derived.

Final state

RESOURCE_EXHAUSTED

I obtained rigorous formalization, proved the case k=2, proved that sufficiently large complete graphs contain the required subgraphs, and isolated several equivalent or sufficient formulations. I did not obtain a complete proof or complete disproof of the full statement.

PROOF_CONFIDENCE: 92/100 for the verified lemmas above.

COMPLETENESS_SCORE: 18/100 for the original problem.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the partial results; 0/100 for the unresolved full claim because no full proof was produced.

RESOURCE_USAGE: about 90% of the available reasoning budget; 12 strategies considered; 3 branches explored in detail; 3 verified lemmas; 3 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

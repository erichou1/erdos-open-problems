# Erdős Problem #80 [unsolved] 55%

---

## ChatGPT Response

Phase 0: Formalization

Let G=(V,E) be a finite simple graph, ∣V∣=n.
For an edge xy∈E, define its book size

b
G
	​

(xy)=∣N(x)∩N(y)∣.

A triangle containing xy is exactly a common neighbor of x,y, so xy is contained in at least one triangle iff b
G
	​

(xy)≥1.

Define

b(G)=
xy∈E
max
	​

b
G
	​

(xy).

For fixed c>0, the problem’s quantity is equivalently

f
c
	​

(n)=min{b(G):∣V(G)∣=n, e(G)≥cn
2
, b
G
	​

(xy)≥1 ∀xy∈E(G)},

provided the family is nonempty. If c≥1/2, then for large n,

e(G)≤(
2
n
	​

)<n
2
/2≤cn
2
,

so the condition becomes vacuous or empty depending on convention. The meaningful range is

0<c<1/2.

The target lower-bound statement f
c
	​

(n)≥M(n) means:

∀G,(∣V(G)∣=n, e(G)≥cn
2
, ∀xy∈E, b
G
	​

(xy)≥1)⟹b(G)≥M(n).

Its negation is:

∃G,∣V(G)∣=n, e(G)≥cn
2
, ∀xy∈E, b
G
	​

(xy)≥1,b(G)<M(n).

The two concrete questions become:

Does there exist ϵ=ϵ(c)>0 such that f
c
	​

(n)>n
ϵ
 eventually?

Does f
c
	​

(n)≫
c
	​

logn eventually?

Phase 1: Breadth-first strategy search
Strategy	Idea	Obstacle	Value
Direct degree-sum	Relate b(G) to e(G) using d(x)+d(y)≤n+b
G
	​

(xy)	Only strong above c=1/4	High
Contradiction with bounded book	Assume b(G)≤B, force sparse structure	Needs removal-type input	High
Explicit construction	Build dense triangle-covered graphs with small books	Gives upper bounds only	High
Induction on n	Delete vertices of small/large degree	Edge-in-triangle condition not stable	Medium
Transfinite/ordinal rank	Not naturally relevant for finite graphs	Artificial	Low
Cardinal arithmetic	Track e,T,b, where T=#triangles	Counting alone too weak	Medium
Diagonalization	Try to build graphs avoiding large books	Turns into construction problem	Medium
Compactness	Limit of bounded-book dense graphs	Needs finite-to-infinite transfer	Medium
Density increment	Find dense pair, pass to subgraph	Edge-in-triangle may vanish	Medium
Reflection/localization	Examine neighborhoods G[N(v)]	Local edge counts only O(n)	Medium
Auxiliary structures	Encode triangles as hyperedges	Promising but complex	High
Counterexample search	Try book O(1) or O(logn) constructions	Runs into removal-type obstruction	High

Top three selected: direct degree-sum, explicit construction, bounded-book contradiction via triangle-removal-type lemma.

Verified theorem pool
Lemma 1: General degree-book inequality

Let G be an n-vertex graph with e=e(G) edges and maximum book size b=b(G). Then

b≥
n
4e
	​

−n.
Proof

For every edge xy∈E,

∣N(x)∪N(y)∣=d(x)+d(y)−∣N(x)∩N(y)∣.

Since N(x)∪N(y)⊆V(G),

d(x)+d(y)−b
G
	​

(xy)≤n.

Thus

d(x)+d(y)≤n+b
G
	​

(xy)≤n+b.

Summing over all edges,

xy∈E
∑
	​

(d(x)+d(y))≤e(n+b).

But the left side equals

v∈V
∑
	​

d(v)
2
.

By Cauchy-Schwarz,

v∈V
∑
	​

d(v)
2
≥
n
(∑
v
	​

d(v))
2
	​

=
n
(2e)
2
	​

=
n
4e
2
	​

.

Therefore

n
4e
2
	​

≤e(n+b).

Since e>0,

n
4e
	​

≤n+b,

so

b≥
n
4e
	​

−n.

Verified.

Consequence

If e(G)≥cn
2
, then

b(G)≥(4c−1)n.

Therefore, for every c>1/4,

f
c
	​

(n)≥(4c−1)n.

This proves a linear lower bound in the range c>1/4.

Lemma 2: Explicit construction for 0<c<1/4

For every fixed 0<c<1/4, there is a constant K
c
	​

 such that for all sufficiently large n,

f
c
	​

(n)≤K
c
	​

n
1/2
.
Construction

Choose t>0 so that

(2t+1)
2
t
2
	​

>c.

This is possible because

t→∞
lim
	​

(2t+1)
2
t
2
	​

=
4
1
	​

.

For integers r,s, define a graph G
r,s
	​

 as follows.

Partition the vertices into

A=A
1
	​

∪⋯∪A
r
	​

,B=B
1
	​

∪⋯∪B
r
	​

,C={z
ij
	​

:1≤i,j≤r},

where

∣A
i
	​

∣=∣B
j
	​

∣=s.

Edges:

Put all edges between A and B.

For each z
ij
	​

, join z
ij
	​

 to every vertex of A
i
	​

∪B
j
	​

.

Put no other edges.

Then

∣V(G
r,s
	​

)∣=2rs+r
2
,

and

e(G
r,s
	​

)=r
2
s
2
+2r
2
s.

Take s=⌊tr⌋. Then

∣V(G
r,s
	​

)∣
2
e(G
r,s
	​

)
	​

=
(2rs+r
2
)
2
r
2
s
2
+2r
2
s
	​

→
(2t+1)
2
t
2
	​

>c.

Thus, after adding isolated vertices if needed to reach exactly n vertices, for all sufficiently large n this graph still has at least cn
2
 edges.

Triangle condition

Every edge lies in a triangle:

If a∈A
i
	​

, b∈B
j
	​

, then abz
ij
	​

 is a triangle.

If a∈A
i
	​

 and az
ij
	​

∈E, then for every b∈B
j
	​

, abz
ij
	​

 is a triangle.

If b∈B
j
	​

 and bz
ij
	​

∈E, then for every a∈A
i
	​

, abz
ij
	​

 is a triangle.

Book sizes

For an edge ab with a∈A
i
	​

, b∈B
j
	​

,

N(a)∩N(b)={z
ij
	​

},

so

b
G
	​

(ab)=1.

For an edge az
ij
	​

 with a∈A
i
	​

,

N(a)∩N(z
ij
	​

)=B
j
	​

,

so

b
G
	​

(az
ij
	​

)=s.

Similarly, for bz
ij
	​

,

b
G
	​

(bz
ij
	​

)=s.

Hence

b(G
r,s
	​

)=s=O
c
	​

(
n
	​

).

Therefore

f
c
	​

(n)≤K
c
	​

n
	​


for every fixed 0<c<1/4.

Verified.

Lemma 3: Conditional divergence from triangle removal

The following implication is rigorous once the triangle-removal lemma is admitted as a theorem.

Triangle-removal lemma

For every η>0, there exists δ>0 such that every n-vertex graph with at most δn
3
 triangles can be made triangle-free by deleting at most ηn
2
 edges.

Claim

For every fixed c>0,

f
c
	​

(n)→∞.
Proof using the triangle-removal lemma

Fix B≥1. Suppose toward contradiction that for arbitrarily large n, there exists an n-vertex graph G such that

e(G)≥cn
2
,

every edge of G lies in a triangle, and

b(G)≤B.

Let T be the number of triangles in G. Since every triangle contributes to three edge-triangle incidences, and each edge is in at most B triangles,

3T=
xy∈E
∑
	​

b
G
	​

(xy)≤Be(G).

Since e(G)≤(
2
n
	​

)<n
2
/2,

T≤
3
B
	​

e(G)<
6
B
	​

n
2
.

Choose

η=
2(2B+1)
c
	​

.

Let δ=δ(η) be supplied by the triangle-removal lemma. For all sufficiently large n,

6
B
	​

n
2
≤δn
3
,

so

T≤δn
3
.

Thus there is a set F⊆E(G) with

∣F∣≤ηn
2

such that G−F is triangle-free.

Now every original edge e∈E(G)∖F lies in at least one triangle of G. Since G−F is triangle-free, that triangle must contain at least one edge of F. Therefore every surviving edge e∈E(G)∖F can be assigned to some deleted edge f∈F lying with e in a triangle.

A fixed deleted edge f∈F lies in at most B triangles. Each such triangle contains at most two other edges. Hence at most 2B surviving edges can be assigned to f. Therefore

∣E(G)∖F∣≤2B∣F∣.

So

e(G)=∣F∣+∣E(G)∖F∣≤(2B+1)∣F∣≤(2B+1)ηn
2
=
2
c
	​

n
2
.

This contradicts

e(G)≥cn
2
.

Thus, for each fixed B, all sufficiently large admissible graphs must satisfy

b(G)>B.

Equivalently,

f
c
	​

(n)→∞.

Conditional on triangle removal, verified.

What the verified results give

For c>1/4,

f
c
	​

(n)≥(4c−1)n.

Also trivially f
c
	​

(n)≤n−2, so this places f
c
	​

(n) in the linear scale for c>1/4.

For 0<c<1/4, the explicit construction gives

f
c
	​

(n)≤K
c
	​

n
	​

.

Using triangle-removal-type input gives only

f
c
	​

(n)→∞,

with no elementary logarithmic lower bound obtained here.

Thus the rigorously established first-principles bounds here are:

1≤f
c
	​

(n)≤K
c
	​

n
	​

for 0<c<1/4
	​


with conditional divergence

f
c
	​

(n)→∞
	​


if the triangle-removal lemma is admitted.

For c>1/4,

f
c
	​

(n)≥(4c−1)n.
	​

Gap nodes
GAP_NODE 1: Prove f
c
	​

(n)≫logn for 0<c<1/4

No proof was obtained. The removal-lemma argument gives divergence but no logarithmic rate unless one inserts quantitative bounds for the triangle-removal lemma. The standard quantitative route gives bounds far weaker than logn.

Attacks attempted:

Direct triangle counting: only gives T≤b(G)e/3, not enough.

Degree-sum inequality: only strong when c>1/4.

Neighborhood density: ∑
v
	​

e(G[N(v)])=3T, but individual neighborhoods may be sparse.

High-degree vertex analysis: graph can be nearly bipartite.

Bipartite-plus-witness construction: gives 
n
	​

 upper bound, not lower.

Induction on vertices: edge-triangle condition is not inherited.

Random subset argument: triangle condition degrades under sampling.

Edge-covering by triangles: becomes a hypergraph covering problem.

Bounded-book contradiction: reduces to removal-type input.

Extremal examples: constructions with rectangular witnesses prevent simple logn lower proof.

Unresolved.

GAP_NODE 2: Disprove polynomial lower from first principles

The construction above only gives

f
c
	​

(n)≤O
c
	​

(
n
	​

),

which does not disprove a lower bound f
c
	​

(n)≥n
ϵ
 for some small ϵ>0.

The problem statement itself contains the stronger external assertion

f
c
	​

(n)≤n
O(1/loglogn)

for c<1/4, which is n
o(1)
. If that assertion is admitted as an assumption from the problem statement, then no fixed-power lower bound f
c
	​

(n)>n
ϵ
 can hold for 0<c<1/4. I did not rederive that construction here.

Unresolved from first principles.

GAP_NODE 3: Improve the upper construction below 
n
	​


The rectangular-witness construction forces book size s≈
n
	​

. To beat 
n
	​

, one would need a more efficient system covering many dense cross-edges by small witness neighborhoods while preventing unintended large common neighborhoods.

No self-contained construction below n
1/2
 was obtained here.

Unresolved.

Dependency graph

Lemma 1 depends only on degree sums and Cauchy-Schwarz.

Lemma 2 depends only on the explicit construction and direct codegree verification.

Lemma 3 depends on:

triangle-removal lemma,

bounded book triangle count,

edge-assignment counting after deletion.

No proof of the triangle-removal lemma was constructed inside this response.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for Lemmas 1 and 2; 85/100 for Lemma 3 conditional on triangle removal.

COMPLETENESS_SCORE: 55/100. Linear lower bound for c>1/4, 
n
	​

 upper bound for c<1/4, and conditional divergence were established. Polynomial and logarithmic lower questions were not resolved from first principles.

ADVERSARIAL_SURVIVAL_SCORE: 88/100 for the verified lemmas. Main surviving gap is the unproved removal lemma and the absence of a logarithmic-rate argument.

RESOURCE_USAGE: approximately 100% of the allotted reasoning budget; 12 strategies generated; 3 main branches explored; 3 principal lemmas generated; 3 unresolved gap nodes retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

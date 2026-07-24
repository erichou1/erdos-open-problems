# Erdős Problem #643 [unsolved] 24%

---

## ChatGPT Response

Formalization

For a finite simple graph G and a cycle C⊆G, let

v(C)=∣V(C)∣,ch
G
	​

(C)=
	​

{xy∈E(G):x,y∈V(C), xy∈
/
E(C)}
	​

.

Define the hereditary class

G={G: ch
G
	​

(C)<v(C) for every cycle C⊆G}.

Then

f(n)=max{e(G):G∈G, v(G)=n}.

The question is whether

∃K<∞ ∀n≥1,f(n)≤Kn.

This is the problem stated in the attachment. 

Pasted text

Quantifiers and negation

The desired assertion is

∃K<∞ ∀G∈G,e(G)≤Kv(G).

Its negation is

∀K<∞ ∃G∈G,e(G)>Kv(G).

Because G is closed under taking subgraphs, the assertion is equivalent to:

∃D∈Nevery nonempty G∈G has a vertex of degree at most D.

Equivalently,

∃D∈Nevery graph with δ(G)>D contains a cycle C with ch
G
	​

(C)≥v(C).

Indeed, bounded minimum degree in every subgraph is precisely bounded degeneracy, which gives a linear edge bound. Conversely, if graphs in the class have a uniform linear edge bound, applying it to every subgraph gives bounded degeneracy after increasing the constant to absorb finitely many small graphs.

Basic equivalent formulation

For a cycle C of length k,

e(G[V(C)])=k+ch
G
	​

(C).

Thus the defining condition is exactly

e(G[V(C)])≤2k−1.

Therefore the forbidden configuration is:

A vertex set S such that G[S] has a Hamiltonian cycle and

e(G[S])≥2∣S∣.

This formulation exposes the central difficulty: global density must be converted into a dense induced subgraph that also has a spanning cycle.

Verified structural facts
1. Heredity and block reduction

Deleting vertices or edges cannot create new chords in an existing cycle, so G is subgraph-closed.

Every cycle, together with every edge joining two of its vertices, lies in a single 2-connected block. Hence G∈G exactly when every block of G belongs to G.

For a connected graph,

B
∑
	​

(∣V(B)∣−1)=∣V(G)∣−1,

where bridges are regarded as two-vertex blocks. Consequently, it would be enough to prove that every 2-connected B∈G satisfies

e(B)≤K(∣V(B)∣−1)

for one absolute K.

2. Cycle-set expansion forced by minimum degree

Let G∈G have minimum degree at least d, and let S=V(C) for a cycle C. Since

e(G[S])≤2∣S∣−1

and

v∈S
∑
	​

d
G
	​

(v)=2e(G[S])+∣∂
G
	​

(S)∣,

we obtain

∣∂
G
	​

(S)∣≥d∣S∣−2(2∣S∣−1)=(d−4)∣S∣+2.
(1)

Thus every cycle vertex set in a hypothetical high-minimum-degree example must have very large edge boundary.

The problem is consequently equivalent to proving that, for some absolute d, every graph of minimum degree at least d has a cycle C whose vertex set violates (1).

3. Exact regular-graph identity

If G is d-regular and S=V(C), then

ch
G
	​

(C)=e(G[S])−∣S∣=
2
(d−2)∣S∣−∣∂
G
	​

(S)∣
	​

.

Hence G∈G precisely when every cycle vertex set satisfies

∣∂
G
	​

(S)∣>(d−4)∣S∣.
(2)

Also, since ∣∂
G
	​

(S)∣≤d(n−∣S∣), every cycle in a good d-regular graph obeys

∣S∣≤
2d−4
dn−2
	​

.
(3)

For large d, this forces every cycle to contain only about half the vertices, but (3) alone does not contradict regularity.

4. Minimum degree four is possible

Every connected non-Hamiltonian 4-regular graph belongs to G. For a proper cycle vertex set S,

ch
G
	​

(C)=∣S∣−
2
∣∂
G
	​

(S)∣
	​

.

Connectedness gives ∣∂
G
	​

(S)∣>0, and parity gives ∣∂
G
	​

(S)∣≥2. Therefore

ch
G
	​

(C)≤∣S∣−1.

A spanning cycle does not exist by assumption.

An explicit example is obtained from two copies of K
5
	​

−ab, adding a new vertex adjacent to the four deficient endpoints. The result is connected and 4-regular, and the new vertex is a cut vertex, so it has no Hamiltonian cycle.

Thus no proof can establish that every graph in G has a vertex of degree at most 3.

5. Sharp elementary bipartite tests

The graph K
4,4
	​

 is forbidden: its Hamiltonian 8-cycle has

16−8=8

chords.

In contrast, K
3,t
	​

 belongs to G for every t. A cycle uses r∈{2,3} vertices from each part. Its induced graph is K
r,r
	​

, so its number of chords is

r
2
−2r,

which is 0 for r=2 and 3<6 for r=3.

This shows that unbounded degrees and arbitrarily large codegrees are compatible with the condition.

6. Restrictions on common neighborhoods

Let uv∈E(G). If G[N(u)∩N(v)] contained a path

p
1
	​

p
2
	​

⋯p
s
	​

,s≥4,

then

up
1
	​

p
2
	​

⋯p
s
	​

vu

would be a cycle on s+2 vertices. The induced graph on these vertices has at least

2s+(s−1)+1=3s

edges, and hence at least

3s−(s+2)=2s−2≥s+2

chords. Therefore, for every edge uv,

G[N(u)∩N(v)] contains no path on four vertices.
(4)

If u,v are nonadjacent and y is another common neighbor outside a common-neighborhood path p
1
	​

…p
s
	​

, then

up
1
	​

⋯p
s
	​

vyu

gives the analogous contradiction for s≥5.

These restrictions defeat constructions based on repeatedly adding universal pairs or nested common-neighborhood hubs.

7. DFS interval restriction

Take a depth-first-search tree T. Every non-tree edge joins an ancestor to a descendant.

For a non-tree edge xy, with x an ancestor of y, let P
T
	​

(x,y) have q vertices. The fundamental cycle consists of this tree path and xy. Every other non-tree edge whose endpoints both lie on the path is a chord. Therefore,

#{ab∈E(G)∖E(T):a,b∈V(P
T
	​

(x,y))}≤q.
(5)

This gives strong local sparsity for nested back edges. The unresolved issue is that the paths in (5) overlap heavily; no valid global charging argument converting (5) into O(n) total back edges was obtained.

8. Longest-cycle bridge restriction

Let C be a longest cycle of length k. Suppose a component outside C contains an x-y path P, internally disjoint from C, of length p, where x,y∈V(C). If the two x-y arcs of C have lengths a and k−a, maximality of C gives

p+a≤k,p+k−a≤k.

Thus

p≤min{a,k−a}.
(6)

This controls the geometry of attachments to a longest cycle but does not bound the total number of attachment edges.

Search branches
Strategy	Verified outcome	Main unresolved point
Direct bounded-degeneracy proof	Reduced exactly to excluding arbitrarily large minimum degree	Need a cycle violating (1)
Contradiction from minimum degree	Obtained cycle-set expansion (1)	Expansion has not been contradicted
Induction on vertices	Block reduction is valid	Crossing/attachment edges resist induction
Longest-cycle analysis	Attachment inequality (6)	No linear charging of all bridges
DFS analysis	Back-edge interval bound (5)	Overlapping intervals prevent summation
Regular/2-factor analysis	Exact boundary identity (2)	No forced low-boundary cycle established
Density/random sampling	Produces smaller dense subgraphs	Does not provide a spanning cycle
Common-neighborhood analysis	Path restrictions such as (4)	High-girth graphs evade codegree arguments
Auxiliary incidence structure	Bipartite formulation becomes exact	No construction or impossibility proof
Counterexample construction	K
3,t
	​

-type and hierarchical attempts tested	All examined superlinear mechanisms create forbidden cycles
Compactness/limit methods	Finite-cycle conditions pass locally	Global cycle length and induced density are lost
Transfinite/cardinal/reflection methods	Reduce to ordinary finite counting	No additional finite structural consequence
Three surviving primary gaps
Gap A: cycle-set expansion

Determine whether there is an absolute d
0
	​

 such that every finite graph with minimum degree at least d
0
	​

 contains a cycle C satisfying

∣∂
G
	​

(V(C))∣≤(d
0
	​

−4)∣V(C)∣+1.

By (1), this would prove the desired linear bound.

No proof of this statement was obtained.

Gap B: globalizing DFS restrictions

Given a rooted tree and ancestor-descendant edges satisfying (5) for every fundamental interval, prove a linear bound after incorporating the restrictions arising from all non-fundamental cycles.

The fundamental-cycle inequalities alone do not yet yield a verified global estimate.

Gap C: imbalanced bipartite constructions

A plausible counterexample framework would have bipartition

∣L∣=N,∣R∣≍dN,

with right degrees about d, giving average degree of order d. For a cycle using A⊆L and B⊆R, where ∣A∣=∣B∣=t, the condition becomes

e(A,B)<4t

whenever the bipartite graph on A∪B has a spanning alternating cycle.

Repeated neighborhoods fail because they create K
4,4
	​

. Partitioned complete-bipartite blocks also fail. No incidence construction with unbounded average degree satisfying the displayed condition was found, and no proof ruling one out was obtained.

Dependency record

The rigorously established chain is

cycle condition⟺e(G[V(C)])≤2∣C∣−1
⟹heredity and block reduction
⟹bounded linear extremal function⟺bounded degeneracy

and, under minimum degree d,

⟹∣∂
G
	​

(V(C))∣≥(d−4)∣V(C)∣+2.

No established lemma contradicts this last expansion inequality for all sufficiently large d, and no construction satisfying it for unbounded d was completed.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100 for the verified lemmas and equivalences.

COMPLETENESS_SCORE: 24/100. The original linear estimate was neither proved nor disproved.

ADVERSARIAL_SURVIVAL_SCORE: 93/100 for the stated partial results; candidate shortcuts were discarded when they failed the 4-regular, K
3,t
	​

, common-neighborhood, or Hamiltonicity tests.

RESOURCE_USAGE: 12 principal strategies examined, 8 verified structural lemmas retained, 7 incomplete proof or construction routes rejected.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

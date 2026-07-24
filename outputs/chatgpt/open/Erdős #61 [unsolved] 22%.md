# Erdős Problem #61 [unsolved] 22%

---

## ChatGPT Response

Phase 0: Formalization

Let all graphs be finite, simple, undirected.

Objects

For a graph G,

ω(G)=maximum clique size,α(G)=maximum independent-set size,

and define

hom(G)=max(ω(G),α(G)).

For fixed graph H, say G is induced-H-free if there is no injective map
ϕ:V(H)→V(G) such that for all distinct x,y∈V(H),

xy∈E(H)⟺ϕ(x)ϕ(y)∈E(G).

The target statement is:

∀H ∃c(H)>0 ∀n≥1 ∀G(∣V(G)∣=n∧G induced-H-free)⇒hom(G)≥n
c(H)
.

Equivalently, for each fixed H, there should be a positive exponent c such that every induced-H-free n-vertex graph has a polynomial-size homogeneous set.

Negation

The negation is:

∃H ∀c>0 ∃n≥1 ∃G

such that

∣V(G)∣=n,G is induced-H-free,

but

hom(G)<n
c
.

Equivalently, for some fixed H, there are induced-H-free graphs G
i
	​

 with n
i
	​

→∞ and

logn
i
	​

loghom(G
i
	​

)
	​

→0.
Contrapositive formulation

For fixed H, the desired statement is equivalent to:

∃c>0 ∀G,hom(G)<∣V(G)∣
c
⇒G contains an induced copy of H.
Complement symmetry

Let 
G
 denote the complement graph.

A set is a clique in G iff it is independent in 
G
, and vice versa, hence

hom(G)=hom(
G
).

Also,

G contains induced H⟺
G
 contains induced 
H
.

Therefore:

T(H)⟺T(
H
).

So the problem is invariant under graph complementation.

Boundary cases

If H=K
1
	​

, then every nonempty graph contains an induced copy of H, so the implication is vacuous for n≥1.

If H=K
2
	​

, then induced-H-free means G has no edges, so

α(G)=n.

If H=
K
2
	​

	​

, then G has no nonedges, so

ω(G)=n.

Thus the statement holds for all H on at most two vertices.

Basic verified lemmas
Lemma 1: Clique-forbidden graphs satisfy a polynomial bound

Let t≥2. If G is K
t
	​

-free, then there exists c
t
	​

>0 such that

α(G)≥∣V(G)∣
c
t
	​

.

In fact one may take c
t
	​

=1/(t−1) up to harmless constants.

Proof.
We prove a slightly weaker but sufficient statement: there is C
t
	​

>0 such that every K
t
	​

-free graph on n vertices has

α(G)≥C
t
	​

n
1/(t−1)
.

Base case t=2: if G is K
2
	​

-free, then G has no edges, so α(G)=n.

Inductive step. Assume the claim for t−1. Let G be K
t
	​

-free on n vertices.

If some vertex v has degree

d(v)≥n
(t−2)/(t−1)
,

then G[N(v)] is K
t−1
	​

-free; otherwise v together with a K
t−1
	​

⊆N(v) would form a K
t
	​

. By induction,

α(G[N(v)])≥C
t−1
	​

d(v)
1/(t−2)
≥C
t−1
	​

n
1/(t−1)
.

If instead every vertex has degree <n
(t−2)/(t−1)
, then the greedy algorithm produces an independent set of size at least

Δ(G)+1
n
	​

≥
n
(t−2)/(t−1)
+1
n
	​

≥C
t
	​

n
1/(t−1)

for an appropriate constant C
t
	​

>0.

Thus every K
t
	​

-free graph has polynomial-size independent set. □

Therefore the target statement holds when H=K
t
	​

. By complement symmetry, it also holds when H=
K
t
	​

	​

.

Lemma 2: Induced-P
3
	​

-free graphs satisfy the statement

Let P
3
	​

 be the three-vertex path. If G has no induced P
3
	​

, then every connected component of G is a clique.

Proof.
Suppose some connected component is not a clique. Then there exist nonadjacent vertices x,y in the same component. Choose a shortest path

x=v
0
	​

,v
1
	​

,…,v
k
	​

=y.

Since x,y are nonadjacent, k≥2. By shortestness, v
0
	​

 is not adjacent to v
2
	​

; otherwise

v
0
	​

,v
2
	​

,…,v
k
	​


would be a shorter path. Hence v
0
	​

,v
1
	​

,v
2
	​

 induce a P
3
	​

, contradiction.

Thus every connected component is a clique. □

Now suppose the component sizes are

s
1
	​

,…,s
m
	​

,
i
∑
	​

s
i
	​

=n.

The largest clique has size max
i
	​

s
i
	​

. Also, choosing one vertex from each component gives an independent set of size m. Therefore

hom(G)≥max(m,
i
max
	​

s
i
	​

).

Since

m⋅
i
max
	​

s
i
	​

≥n,

we get

hom(G)≥
n
	​

.

So c(P
3
	​

)=1/2 works.

By complement symmetry, the same holds for 
P
3
	​

	​

.

Phase 1: Breadth-first strategy search

Here are twelve independent proof directions.

Strategy	Description	Hidden assumption risk	Main obstacle
Direct induction on (	V(H)	)	Remove a vertex x∈H, use information about H−x
Contradiction	Assume counterexamples with hom(G)=n
o(1)
	Medium	Need extract induced H from weak structure
Density increment	Find large dense/sparse subsets recursively	High	Dense/sparse is weaker than complete/empty
Pure-pair route	Prove large complete/anticomplete pair exists	Medium	Such a pair is not forced by elementary arguments
Ramsey recursion	Use ordinary Ramsey bounds plus forbidden induced structure	Low	Ordinary Ramsey gives logarithmic, not polynomial
Vertex-profile embedding	Track adjacency patterns to partial induced copies of H	Medium	Missing one pattern class need not imply homogeneity
Regularity-like partition	Approximate G by a structured reduced graph	High	Approximation errors can destroy induced copies
Dependent random choice	Force common neighborhoods or common non-neighborhoods	Medium	Induced constraints require both adjacency and nonadjacency control
Counterexample construction	Try to build H-free graphs with subpolynomial homogeneity	Low	Random graphs contain every fixed induced H
Blow-up analysis	Study substitution/lexicographic product constructions	Low	Fixed templates still give polynomial homogeneous sets
Rank/invariant method	Define structural rank decreasing under decomposition	Medium	No general decreasing invariant found
Compactness/model route	Use limiting graphons or finitely satisfiable patterns	High	Limit statements need quantitative polynomial extraction

The strongest verified route is the pure-pair route, because if a suitable large pure pair exists recursively, then a polynomial homogeneous set follows. I prove that implication next.

Phase 2: A useful auxiliary theorem
Definition: pure pair

For disjoint nonempty sets A,B⊆V(G), say (A,B) is a pure pair if either every edge between A and B is present, or no edge between A and B is present.

Call A,B a linear pure pair if additionally

∣A∣,∣B∣≥ε∣V(G)∣

for some fixed ε>0.

Lemma 3: Linear pure pairs imply the target statement

Fix H. Suppose there exists ε>0 such that every induced-H-free graph G with at least two vertices contains a pure pair A,B satisfying

∣A∣,∣B∣≥ε∣V(G)∣.

Then H satisfies the desired polynomial homogeneous-set conclusion.

Proof.

Let G be induced-H-free on n vertices. Since induced subgraphs of G are also induced-H-free, the pure-pair hypothesis applies recursively to every induced subgraph with at least two vertices.

Build a binary tree of vertex subsets.

The root is V(G). If a node X has ∣X∣≥2, choose a pure pair A
X
	​

,B
X
	​

⊆X with

∣A
X
	​

∣,∣B
X
	​

∣≥ε∣X∣.

Make A
X
	​

,B
X
	​

 the two children of X. Between the two children, all edges are either complete or empty.

Choose depth

d=⌊log
1/ε
	​

(n/2)⌋.

Then every node at depth j≤d has size at least

ε
j
n≥ε
d
n≥2,

so the construction can proceed to depth d.

At depth d, there are 2
d
 nonempty leaf sets. Pick one representative vertex from each leaf. Let R be the graph induced by these representatives.

The recursive construction guarantees that R is obtained from single vertices by repeated disjoint union or complete join. Such graphs satisfy

ω(R)α(R)≥∣V(R)∣.

We verify this by induction.

For a one-vertex graph, ω=α=1.

Suppose R is a disjoint union of R
1
	​

,R
2
	​

. Then

ω(R)=max(ω(R
1
	​

),ω(R
2
	​

)),

and

α(R)=α(R
1
	​

)+α(R
2
	​

).

Assuming

ω(R
i
	​

)α(R
i
	​

)≥∣V(R
i
	​

)∣,

we get

ω(R)α(R)≥ω(R
1
	​

)α(R
1
	​

)+ω(R
2
	​

)α(R
2
	​

)≥∣V(R
1
	​

)∣+∣V(R
2
	​

)∣=∣V(R)∣.

The complete-join case is complementary: then

ω(R)=ω(R
1
	​

)+ω(R
2
	​

),

and

α(R)=max(α(R
1
	​

),α(R
2
	​

)),

so the same inequality follows.

Thus

hom(R)≥
∣V(R)∣
	​

=
2
d
	​

.

Because R is an induced subgraph of G,

hom(G)≥2
d/2
.

Since

d≥log
1/ε
	​

(n/2)−1,

we obtain

hom(G)≥2
−1/2
(n/2)
2log(1/ε)
log2
	​

.

After reducing the exponent slightly to absorb the constant and finitely many small values of n, there exists c=c(ε)>0 such that

hom(G)≥n
c
.

Therefore H satisfies the desired conclusion. □

Phase 3: Recursive gap attack

The major unresolved statement produced by Lemma 3 is:

Gap A:

For every fixed H, must every induced-H-free graph contain a linear pure pair?

If Gap A were true, the main theorem would follow immediately from Lemma 3.

Now attack Gap A.

Attack A1: direct proof attempt

Assume G is induced-H-free and has no linear pure pair.

Then for every disjoint A,B⊆V(G) with

∣A∣,∣B∣≥εn,

there is at least one edge and at least one nonedge between A and B.

This gives only a weak mixing condition. It does not imply that every vertex of A has both many neighbors and many non-neighbors in B. A single exceptional vertex can carry all the edges or all the nonedges.

So weak pair-mixing alone does not allow greedy embedding of H.

Status: unresolved.

Attack A2: strengthen pair-mixing to vertex-mixing

A stronger useful statement would be:

For some δ>0, every large set X⊆V(G) contains a large subset Y⊆X such that every vertex of Y has at least δ∣Y∣ neighbors and at least δ∣Y∣ non-neighbors in Y.

If this were true, one could attempt to greedily embed any fixed H: at each step, the candidate set for the next vertex would shrink by at most a constant factor.

But absence of a linear pure pair does not obviously imply this vertex-level condition. A graph can avoid large pure pairs while still having many vertices with extremely unbalanced neighborhoods into particular subsets.

Status: unresolved.

Attack A3: partial-copy profile method

Let x∈V(H), and let

J=H−x.

Suppose G contains an induced copy of J, say on vertices indexed by V(J). To extend this copy to H, one needs a vertex v outside the copy satisfying

v∼u⟺x∼
H
	​

u

for every u∈V(J).

Thus every induced J-copy in G forbids one adjacency profile among the at most

2
∣V(H)∣−1

possible profiles.

For H=P
3
	​

, this obstruction is strong enough: forbidding the profile “adjacent to exactly one endpoint of an edge” forces components to be cliques.

For general H, the obstruction is weaker. The missing profile can depend on the particular J-copy, and the remaining profile classes can be distributed irregularly.

Status: unresolved.

Attack A4: induction on ∣V(H)∣

Assume the theorem for every graph on fewer than ∣V(H)∣ vertices. Let x∈V(H), J=H−x.

If G is induced-H-free and some large subset U⊆V(G) is induced-J-free, then induction gives

hom(G)≥hom(G[U])≥∣U∣
c(J)
.

If ∣U∣≥n
θ
, this gives

hom(G)≥n
θc(J)
.

So the hard case is:

Every polynomial-size subset of V(G) contains an induced copy of J.

In that case one needs to show that abundant induced J-copies force an induced H, unless a large homogeneous set already exists.

I cannot justify that implication from the current deductions. The profile obstruction above remains.

Status: unresolved.

Attack A5: density route

Suppose G has neither a large clique nor a large independent set.

Then neither G nor 
G
 can have too small an average degree. Indeed, if

d
(G)≤n
1−c
−1,

then the greedy algorithm gives

α(G)≥
d
(G)+1
n
	​

≥n
c
.

Similarly, if

d
(
G
)≤n
1−c
−1,

then

ω(G)=α(
G
)≥n
c
.

Therefore any counterexample must have both G and 
G
 moderately dense.

This excludes extremely sparse and extremely dense counterexamples. However, it does not force enough uniformity to embed an arbitrary induced H.

Status: useful constraint, not sufficient.

Phase 4: Counterexample search

A disproof would require a fixed graph H and induced-H-free graphs G
i
	​

 with

hom(G
i
	​

)=∣V(G
i
	​

)∣
o(1)
.

Several natural attempts fail.

Attempt C1: random graphs

A random-looking graph typically has very small homogeneous sets, roughly logarithmic in the number of vertices. However, random-looking graphs also contain every fixed adjacency pattern on a fixed number of vertices with high abundance. Thus this does not directly produce induced-H-free examples.

Failure reason: avoids homogeneity but does not avoid induced H.

Attempt C2: complete multipartite graphs

Complete multipartite graphs can avoid some induced configurations. But if there are many parts, choosing one vertex from each part gives a large clique; if there is a large part, that part is a large independent set.

So complete multipartite graphs always have a polynomial, indeed often linear, homogeneous set.

Failure reason: too structured.

Attempt C3: disjoint unions of cliques

Dual to complete multipartite graphs. Either some component is large, giving a large clique, or there are many components, giving a large independent set.

Failure reason: too structured.

Attempt C4: fixed-template blow-ups

Let B be a fixed graph on b vertices, and form iterated blow-ups or lexicographic products based on B.

If B has a clique or independent set of size r≥2, then after t iterations,

n=b
t
,

and the homogeneous set size is at least

r
t
=n
log
b
	​

r
.

Since b,r are fixed, this is polynomial in n.

Failure reason: fixed recursive templates still produce positive exponents.

Phase 5: Verified partial theorem pool

At this point, the following are rigorously established from first principles:

Theorem Pool

Complement symmetry.
If the statement holds for H, it holds for 
H
.

Clique and empty-graph cases.
The statement holds for H=K
t
	​

 and H=
K
t
	​

	​

.

Induced P
3
	​

 and complement.
The statement holds for H=P
3
	​

 and H=
P
3
	​

	​

, with exponent 1/2.

Linear pure-pair implication.
If every induced-H-free graph contains a linear pure pair, then H satisfies the desired polynomial homogeneous-set conclusion.

Counterexample constraints.
Any counterexample sequence for fixed H must be simultaneously non-sparse and non-cosparse in the sense that neither G nor 
G
 may have average degree O(n
1−c
) for the relevant exponent c.

Main unresolved gap

The central unresolved statement reached by the search is:

Does every induced-H-free graph contain enough large pure or structured pairs to force polynomial homogeneity?
	​


The recursive pure-pair mechanism would solve the problem, but I did not prove that every induced-H-free graph has such a pair.

The induction-on-∣H∣ mechanism also reduces to a concrete extension problem:

If every large subset contains H−x, must some copy extend to H?
	​


The answer is not forced by the current deductions, because the missing adjacency profile may vary with the chosen copy of H−x.

Adversarial check

I checked the strongest candidate proof, the pure-pair route.

The implication

linear pure pair property⇒polynomial homogeneous set

survives verification.

The unsupported step would be

induced-H-free⇒linear pure pair property.

That step was not proved. Therefore the full target theorem has not been proved.

No explicit family of induced-H-free graphs with subpolynomial homogeneous number was constructed. Therefore the statement has not been disproved.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified lemmas above.

COMPLETENESS_SCORE: 22/100 for the original theorem.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the partial results; 0/100 for a complete proof, since the main gap remains unresolved.

RESOURCE_USAGE: approximately 100% of this response’s proof-search budget used; 3 main branches explored; 5 verified lemmas generated; 4 failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

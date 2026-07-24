# Erdős Problem #638 [solved] 93%

---

## ChatGPT Response

The statement is false even under the intended assumption that S is closed under taking ordinary subgraphs. The formulation and the closure caveat are taken from the uploaded problem statement. 

Pasted text

Edit
DISPROVED

For a graph (G), define its triangle hypergraph
[
\mathcal T(G)
]
as follows:

[
V(\mathcal T(G))=E(G),
]

and a three-element subset of (E(G)) is a hyperedge precisely when those three graph edges form a triangle in (G).

Thus an edge-coloring of (G) with no monochromatic triangle is exactly a proper vertex-coloring of (\mathcal T(G)). Consequently,
[
G\longrightarrow (K_3)^2_\lambda
\quad\Longleftrightarrow\quad
\chi(\mathcal T(G))>\lambda.
]

We construct a subgraph-closed family (S) such that

[
\sup{\chi(\mathcal T(F))\in S}=\infty,
]

but every graph all of whose finite subgraphs belong to (S) satisfies

[
\chi(\mathcal T(G))\le \aleph_0.
]

This disproves the proposed conclusion already for (\aleph=\aleph_0).

1. Berge cycles

A Berge cycle of length (\ell) in a hypergraph (H) consists of distinct hyperedges
[
A_1,\dots,A_\ell
]
and distinct vertices
[
x_1,\dots,x_\ell
]
such that, with indices modulo (\ell),
[
x_i\in A_i\cap A_{i+1}.
]

The Berge girth of (H) is the minimum length of such a cycle, with value (+\infty) if no such cycle exists.

We use the following finite lemma.

2. Sparse triangle-Ramsey lemma

For all positive integers (r) and (g), there exists a finite simple graph (R) such that

[
R\longrightarrow (K_3)^2_r
]

and

[
\operatorname{girth}_{\mathrm B}(\mathcal T(R))>g.
]

Proof

Fix (r) and (g).

We first record a robust random-Ramsey construction.

Let (N) be large and put
[
p=A N^{-1/2}\log N,
]
where (A) is a sufficiently large constant depending only on (r).

Let
[
\Gamma\sim G(N,p).
]

We claim that, with probability tending to (1), one must delete at least
[
c_r pN^2
]
edges from (\Gamma) before the remaining graph admits an (r)-edge-coloring without a monochromatic triangle.

To see this, let
[
R_0=R_r(3)
]
be a finite multicolor Ramsey number.

If (F_1,\dots,F_r) are triangle-free subgraphs of (K_N), then their union omits at least
[
\frac{N(N-1)}{R_0(R_0-1)}
]
edges. Indeed, every (R_0)-vertex subset must contain an omitted edge; otherwise, assigning each covered edge one index (i) for which it lies in (F_i) would give an (r)-coloring of (K_{R_0}) without a monochromatic triangle. Double-counting pairs
[
(Q,X),
]
where (Q) is an omitted edge and (X) is an (R_0)-set containing it, gives the displayed bound.

We also need the following finite triangle-container fact.

For every (\rho>0), there is a family (\mathscr C_N) of graphs on ([N]) such that:

every triangle-free graph (F\subseteq K_N) is contained in some (C\in\mathscr C_N);

for every (C\in\mathscr C_N), at most (\rho N^2) edges can be deleted from (C) to make it triangle-free;

[
\log |\mathscr C_N|=O_\rho(N^{3/2}\log N).
]

Here is the relevant finite derivation. Apply the greedy fingerprint procedure to the three-uniform hypergraph whose vertices are the edges of (K_N) and whose hyperedges are graph triangles. This hypergraph has

[
M=\binom N2
]

vertices, vertex degree (N-2), and pair-codegree at most (1). The greedy procedure records (O(M/\sqrt N)=O(N^{3/2})) vertices in each fingerprint while reducing the number of surviving triangles by a fixed factor. Iteration a bounded number of times gives containers with at most (\delta N^3) triangles, where (\delta=\delta(\rho)).

The finite triangle-removal argument then applies: after an (\varepsilon)-regular partition, delete edges in irregular pairs, low-density pairs, and within partition classes. With parameters chosen in the order
[
\varepsilon\ll \rho,
\qquad
\delta\ll \varepsilon^3,
]
fewer than (\rho N^2) edges are deleted. If a triangle remained, the three corresponding regular dense pairs would generate at least (\delta N^3) triangles, a contradiction. This proves property 2. Counting the possible fingerprints gives property 3.

Choose
[
\rho<\frac{1}{4rR_0(R_0-1)}.
]

For (C_1,\dots,C_r\in\mathscr C_N), delete at most (\rho N^2) edges from each (C_i), obtaining triangle-free graphs (F_i). The preceding double-counting argument implies that
[
K_N\setminus \bigcup_{i=1}^r C_i
]
has at least (cN^2) edges for some (c=c(r)>0).

For each fixed tuple (C_1,\dots,C_r), a Chernoff bound gives
[
\Pr\left(
\left|E(\Gamma)\setminus\bigcup_i C_i\right|
<\frac c2pN^2
\right)
\le
\exp(-c'pN^2).
]

\exp(O_r(N^{3/2}\log N)),
]
choosing (A) sufficiently large and taking a union bound proves the claimed resilience.

It remains to remove all short Berge cycles from (\mathcal T(\Gamma)).

Consider a Berge cycle of length (\ell) in the triangle hypergraph. Let (J) be the union, as an ordinary graph, of its (\ell) graph triangles. If (v(J)) and (e(J)) denote its numbers of vertices and edges, then
[
e(J)\ge 2v(J)-2.
]

Indeed, begin with one triangle. Each time a triangle sharing an edge introduces a new graph vertex, it introduces exactly two new graph edges. Equality
[
e=2v-3
]
would describe an edge-gluing tree of triangles, whose triangle hypergraph contains no Berge cycle with distinct shared edges. The presence of the closing Berge cycle therefore forces at least one further graph edge, giving
[
e\ge 2v-2.
]

For each fixed (\ell), there are only finitely many possible union graphs (J). The expected number of copies of such a (J) in (\Gamma) is at most
[
O!\left(N^{v(J)}p^{e(J)}\right).
]
Using (e(J)\ge 2v(J)-2),
[
N^{v(J)}p^{e(J)}
\le
N^{v(J)-e(J)/2}(A\log N)^{e(J)}
\le
N(A\log N)^{e(J)}.
]

Consequently, the expected total number of Berge cycles of lengths at most (g) is
[
O_{r,g}!\left(N(\log N)^{C_g}\right)
=o(pN^2).
]

Hence there is a realization of (\Gamma) that simultaneously has the resilience property and has (o(pN^2)) Berge cycles of length at most (g).

Delete one graph edge from every such short Berge cycle. Deleting edges creates no new Berge cycles, so the resulting graph (R) satisfies
[
\operatorname{girth}_{\mathrm B}(\mathcal T(R))>g.
]

Fewer than (c_rpN^2) edges were deleted, so by resilience the resulting graph is still not (r)-edge-colorable without a monochromatic triangle. Thus
[
R\longrightarrow (K_3)^2_r.
]

This proves the sparse triangle-Ramsey lemma.

3. Construction of (S)

For every positive integer (m), choose a finite graph (R_m) satisfying
[
R_m\longrightarrow (K_3)^2_m
]
and
[
\operatorname{girth}_{\mathrm B}(\mathcal T(R_m))>m.
]

Define
[
S=
{F:\ F\text{ is a finite subgraph of some }R_m}.
]

Then (S) is closed under taking subgraphs.

Moreover, for every (m),
[
R_m\in S
]
and every (m)-edge-coloring of (R_m) contains a monochromatic triangle. Thus (S) satisfies the hypothesis of the problem.

4. Every locally-(S) graph is countably colorable

Let (G) be any graph such that every finite subgraph of (G) belongs to (S). Put
[
H=\mathcal T(G).
]

We prove
[
\chi(H)\le\aleph_0.
]

Fix an integer (\ell\ge 3), and define
[
b_\ell=
\max\bigl({|E(R_m)|<\ell}\cup{0}\bigr).
]

We claim that (H) cannot contain more than (b_\ell) pairwise vertex-disjoint Berge cycles of length (\ell).

Suppose instead that
[
C_1,\dots,C_{b_\ell+1}
]
were pairwise vertex-disjoint Berge (\ell)-cycles in (H). Recall that vertices of (H) are graph edges of (G). Let (F) be the finite subgraph of (G) consisting of all graph edges occurring in those cycles and their endpoints.

By assumption,
[
F\in S.
]
Hence
[
F\subseteq R_m
]
for some (m).

If (m\ge\ell), then
[
\operatorname{girth}_{\mathrm B}(\mathcal T(R_m))>m\ge\ell,
]
contradicting the existence of a Berge (\ell)-cycle in (\mathcal T(F)\subseteq\mathcal T(R_m)).

If (m<\ell), then
[
|E(R_m)|\le b_\ell.
]
But the (b_\ell+1) vertex-disjoint Berge cycles use more than (b_\ell) distinct vertices of (H), equivalently more than (b_\ell) distinct graph edges of (F), again a contradiction.

Thus the packing number of Berge (\ell)-cycles in (H) is finite.

Choose a maximal family of pairwise vertex-disjoint Berge (\ell)-cycles and let (X_\ell) be the union of their vertices. Then (X_\ell) is finite, and every Berge (\ell)-cycle meets (X_\ell).

Set
[
X=\bigcup_{\ell=3}^{\infty}X_\ell.
]
This is a countable subset of (V(H)=E(G)).

The hypergraph
[
H-X
]
contains no Berge cycle: a Berge cycle of length (\ell) would avoid (X_\ell), contrary to the choice of (X_\ell).

5. Acyclic hypergraphs are two-colorable

Every finite Berge-acyclic hypergraph is two-colorable.

Indeed, its incidence bipartite graph is a forest. If it has a hyperedge, some ordinary vertex has incidence degree (1). Remove its unique incident hyperedge, color the remaining hypergraph inductively, and then color the degree-one vertex so that its unique hyperedge is not monochromatic.

It follows that every finite subhypergraph of (H-X) is two-colorable. By the compactness theorem for finite Boolean constraints, (H-X) itself is two-colorable.

Explicitly, associate a Boolean variable to every vertex of (H-X), and for each hyperedge impose the two clauses excluding the all-zero and all-one assignments. Every finite set of clauses is satisfiable by the preceding finite argument, so all clauses are simultaneously satisfiable.

Now give the vertices of (X) pairwise distinct new colors, none of which is one of the two colors used on (H-X).

This uses only countably many colors. No hyperedge is monochromatic:

a hyperedge contained in (H-X) is bichromatic;

a hyperedge meeting (X) contains a color used on no other vertex.

Therefore
[
\chi(\mathcal T(G))\le\aleph_0.
]

Equivalently, (G) has an edge-coloring with countably many colors and no monochromatic triangle.

Thus no graph (G) all of whose finite subgraphs lie in (S) satisfies
[
G\longrightarrow (K_3)^2_{\aleph_0}.
]

The claimed statement fails for (\aleph=\aleph_0), and therefore fails in general.

Final state

[
\boxed{\mathrm{DISPROVED}}
]

PROOF_CONFIDENCE: (94/100)

COMPLETENESS_SCORE: (93/100)

ADVERSARIAL_SURVIVAL_SCORE: (92/100)

RESOURCE_USAGE: One principal counterexample construction, four main lemmas, and two discarded compactness-based approaches.

No internet or external database was used. The argument uses only the uploaded problem statement and finite combinatorial deductions presented above.

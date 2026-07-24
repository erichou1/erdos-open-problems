1. Interpretation defect

The statement does not define infinite path. This materially affects the problem.

I will use the standard conditional interpretation:

G is a simple undirected graph.

An infinite path is a ray, meaning distinct vertices

v
0
	​

,v
1
	​

,v
2
	​

,…

with v
n
	​

v
n+1
	​

∈E(G) for every n.

The path need not be induced.

An independent set of order type α means a subset X⊆α, ordered by the inherited ordinal order, with otp(X)=α.

Without this convention, the exact problem is blocked. For example, if “path” means induced path, then the complete graph on any infinite α has neither an infinite induced path nor an independent set of order type α.

There is also a boundary convention concerning 0. If 0 is regarded as a limit ordinal, the property holds there: the empty set is independent and has order type 0.

Everything below is conditional on the ray interpretation. No full classification is claimed.

2. Exact reformulations

Write P(α) for the assertion in the problem. Under the convention above:

P(α)⟺every rayless graph on α has an independent subset of order type α.

Equivalently, an increasing function f:α→α must exist such that

{f(ξ),f(η)}∈
/
E(G)(ξ<η<α).

A counterexample would therefore be a graph G=(α,E) satisfying both:

G has no ray.

Every X⊆α with otp(X)=α contains an edge.

Thus E would be a two-element hitting family for all copies of α inside α, subject to the severe global restriction that E contains no ray.

For a limit α, every X⊆α of order type α is cofinal. Indeed, if supX=β<α, then X⊆β+1, so

otp(X)≤β+1<α.
3. A complete structural description of rayless graphs

The following rank is useful because it is derived directly from the definition of a ray.

Finite-separator rank

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
σ
	​

 with σ<ρ.

When it exists, the least such ρ is denoted r(G).

Rank theorem

A graph is rayless if and only if it has finite-separator rank.

Ranked graphs are rayless

Proceed by induction on the rank. A finite graph has no ray.

Suppose G∈R
ρ
	​

, witnessed by a finite set S, and suppose G contained a ray R. Since the ray has distinct vertices, it meets S only finitely many times. After its last visit to S, a tail of the ray lies in a single component C of G−S. But C has smaller rank, contradicting induction.

Every unranked graph contains a ray

Suppose G has no rank.

If every component of G had a rank, the set of their ranks would have an ordinal supremum τ, and G∈R
τ+1
	​

, witnessed by S=∅. Thus some component is unranked. Replace G by an unranked connected component H
0
	​

.

Choose v
0
	​

∈H
0
	​

. Since H
0
	​

 is unranked, some component H
1
	​

 of H
0
	​

−v
0
	​

 is unranked; otherwise {v
0
	​

} would witness a rank for H
0
	​

. Because H
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

Inductively, after choosing an unranked connected H
n
	​

 and v
n
	​

∈H
n
	​

, choose an unranked component H
n+1
	​

 of H
n
	​

−v
n
	​

, and choose a neighbor

v
n+1
	​

∈H
n+1
	​


of v
n
	​

.

The components are nested and each excludes all previous v
i
	​

, so the vertices are distinct. Hence

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

is a ray.

Therefore the finite-separator rank exactly characterizes rayless graphs.

4. A general cardinal-sized independent set theorem

The rank theorem gives a strong result that holds for every infinite cardinal.

Theorem

Every infinite rayless graph G has an independent set I satisfying

∣I∣=∣V(G)∣.
Proof

Induct on r(G). Let S be a finite separator witnessing the rank, and let C be the components of G−S.

For every infinite component C, induction gives an independent set

I
C
	​

⊆C,∣I
C
	​

∣=∣C∣.

For every nonempty finite component C, choose one vertex x
C
	​

∈C.

Set

I=
C∈C
C infinite
	​

⋃
	​

I
C
	​

∪{x
C
	​

:C∈C, C finite}.

Different components are anticomplete, so I is independent.

The infinite components contribute exactly their original cardinalities. If there are infinitely many finite components, choosing one vertex from each has the same cardinality as their union; if there are only finitely many, they do not affect the infinite total cardinality. Removing the finite set S also does not alter the cardinality. Hence

∣I∣=∣V(G)∣.
Consequence for initial ordinals

If κ is an infinite initial ordinal, then P(κ) holds.

Indeed, the theorem gives I⊆κ with ∣I∣=κ. Since κ is initial, no ordinal below κ has cardinality κ. Therefore

otp(I)=κ.

This handles every infinite initial ordinal, including singular initial ordinals.

It also isolates the central obstruction for noninitial ordinals:

Every rayless graph has a cardinality-large independent set. The unresolved issue is whether that set can be made large in the much finer ordinal-order sense.

For example, a subset of cardinality κ in κ+κ can have order type only κ.

5. An order-sensitive separation lemma

Call two vertex sets A,B anticomplete when no edge has one endpoint in A and one endpoint in B.

A rank argument gives a flexible simultaneous separation theorem.

Finite-pattern separation lemma

Let G be rayless. Suppose we are given pairwise disjoint infinite sets of two kinds:

finitely many mandatory sets

M
0
	​

,…,M
p−1
	​

;

finitely many sequences

(A
n
j
	​

)
n<ω
	​

,j<q.

Then there exist:

infinite M
i
′
	​

⊆M
i
	​

 for every i<p;

an infinite set J
j
	​

⊆ω for every j<q;

infinite B
n
j
	​

⊆A
n
j
	​

 for n∈J
j
	​

;

such that every two distinct selected sets among the M
i
′
	​

 and B
n
j
	​

 are anticomplete.

Proof structure

Induct on r(G). Let S be a finite rank separator, and let C be the components of G−S.

For a mandatory set M
i
	​

, say that component C captures M
i
	​

 when

∣M
i
	​

∩C∣=ℵ
0
	​

.

For a sequence j, say that C is j-rich when

{n:∣A
n
j
	​

∩C∣=ℵ
0
	​

}

is infinite.

For each mandatory set captured somewhere, choose one capturing component. For each sequence with a rich component, choose one rich component. Only finitely many components are chosen. Group together all requirements assigned to the same component and invoke induction inside that component.

It remains to handle:

Mandatory sets having finite intersection with every component.

Sequences having only finitely many infinitely concentrated members in each component.

Remove the finitely many previously chosen components.

A remaining mandatory set meets infinitely many components, because it is infinite and has finite intersection with each component.

For a remaining sequence j, there are two possibilities.

Infinitely many A
n
j
	​

 are infinitely concentrated in some component.

Because no component is j-rich, each component accounts for only finitely many such indices. Thus infinitely many indices can be assigned pairwise distinct home components.

Only finitely many A
n
j
	​

 are infinitely concentrated.

Choose infinitely many of the other indices. Each corresponding set meets infinitely many components.

Now enumerate all component requests countably many times. At every finite stage, only finitely many components have been used.

A spread set has infinitely many eligible components, so a fresh one exists.

For a concentrated sequence, finitely many used components account for only finitely many concentrated indices, so a new index with a new home component exists.

Assign globally distinct components to all requests.

For spread sets, choose one vertex in each of their infinitely many assigned components. For a concentrated set, choose an infinite subset of its assigned home component. Distinct selected sets use disjoint component families, so they are pairwise anticomplete.

The groups previously handled recursively lie in the finitely many removed components and are therefore anticomplete to the newly constructed groups.

6. Exact positive range obtained from the separation lemma
Theorem

Under the ray interpretation, P(α) holds for every nonzero limit ordinal

α<ω
3
.
Proof

Every such ordinal has the unique form

α=ω
2
q+ωp

for finite p,q, not both zero.

Partition each of the q consecutive ω
2
-blocks into its consecutive ω-rows:

A
n
j
	​

=[ω
2
j+ωn,ω
2
j+ω(n+1)),j<q, n<ω.

The final ωp segment consists of p consecutive ω-blocks; use these as the mandatory sets M
i
	​

.

Apply the finite-pattern separation lemma. It gives:

infinitely many selected rows in every ω
2
-block;

an infinite selected subset of every final ω-block;

pairwise anticompleteness between all these selected sets.

Each selected set is countably infinite. Its induced graph is rayless, so the cardinal-sized independent set theorem supplies an infinite independent subset. Because each selected set lies inside an interval of order type ω, that independent subset has order type ω.

Inside each ω
2
-block, infinitely many selected rows each contribute order type ω, so their union has order type

ω⋅ω=ω
2
.

The q major blocks followed by the p final ω-blocks therefore produce an independent set of order type

ω
2
q+ωp=α.

Thus the first countable ordinal not covered by these arguments is

ω
3
.

This is not a claim that ω
3
 fails; it is the first boundary where the present separation invariant is insufficient.

7. The exact next target: ω
3

Write ω
3
 as an array of ω-blocks

A
n,m
	​

=[ω
2
n+ωm,ω
2
n+ω(m+1)),n,m<ω.

The following statement would imply P(ω
3
).

Two-level separation target

For every rayless graph G and every pairwise disjoint family of infinite sets

(A
n,m
	​

)
n,m<ω
	​

,

there exist:

an infinite N⊆ω;

for each n∈N, an infinite M
n
	​

⊆ω;

infinite B
n,m
	​

⊆A
n,m
	​

 for m∈M
n
	​

;

such that all the B
n,m
	​

 are pairwise anticomplete.

After internally thinning each B
n,m
	​

 to an infinite independent set, the resulting union has order type

n∈N
∑
	​

m∈M
n
	​

∑
	​

ω=ω
3
.

The proven finite-pattern lemma is only a one-level version: it can retain infinitely many members of finitely many sequences. At ω
3
, one must retain infinitely many sequences, each with infinitely many surviving members.

This is the first precise unresolved combinatorial obligation produced by the attack.

8. Failed counterexample constructions
8.1 Complete joins between large ordinal blocks

A natural attempt is to divide α into order-essential blocks and put all cross edges between two blocks, forcing an independent set to remain in one block.

This immediately creates a ray whenever both sides are infinite. If

A={a
n
	​

:n<ω},B={b
n
	​

:n<ω},

and every a
n
	​

 is adjacent to every b
m
	​

, then

a
0
	​

,b
0
	​

,a
1
	​

,b
1
	​

,a
2
	​

,b
2
	​

,…

is a ray.

Thus dense joins cannot provide a rayless counterexample.

8.2 Matchings and finite clique partitions

A matching or a disjoint union of finite cliques is rayless. Such graphs are therefore the first natural counterexample candidates.

For ω
2
, they cannot work.

Partition ω
2
 into rows

R
n
	​

=[ωn,ω(n+1)).

Suppose the graph has finite components. Every row meets infinitely many components, because the row is infinite and every component is finite.

Enumerate all pairs (n,k)∈ω
2
. Recursively choose for each (n,k) a vertex in R
n
	​

 belonging to a component not previously used. This is always possible because only finitely many components have been used at each stage.

The selected vertices lie in distinct components, hence form an independent set. Every row contains infinitely many selected vertices, so the selected set has order type ω
2
.

Therefore no finite-component graph can be a counterexample at ω
2
.

The analogous finite-partition transversal question for arbitrary ordinals remains a useful test:

If an infinite ordinal α is partitioned into finite classes, must there be a transversal of order type α?

A negative answer would immediately produce a rank-one counterexample. The arguments above establish the assertion for initial ordinals and for all limit α<ω
3
, but not in general.

8.3 A triangular column construction

Represent ω
2
 as points ωn+m. In column m, one can make the first m points universal to the tail, so an infinite independent subset of that column is forced into rows n≥m.

Choosing the tails in every column gives only finitely many selected points in row n, hence order type merely ω. This initially resembles a counterexample.

It fails because one may choose exceptional early vertices from different columns. The columns can be allocated among the rows so that infinitely many early vertices are selected in every row while never selecting two vertices from the same component. This reconstructs order type ω
2
.

The failure shows that “each component independently loses an initial segment” is not enough; exceptional points from infinitely many components can rebuild the lost ordinal structure.

8.4 Requiring every row to survive is too strong

Let

R
0
	​

={c
n
	​

:n<ω}

and, for n≥1,

R
n
	​

={ℓ
n,k
	​

:k<ω}.

Put edges

c
n
	​

ℓ
n+1,k
	​

(k<ω),

and no others. This is a disjoint union of infinite stars, hence rayless.

There is no independent set that is infinite in every row. If it contains infinitely many centers c
n
	​

, then infinitely many corresponding leaf rows must be empty.

Nevertheless,

n≥1
⋃
	​

R
n
	​


is independent and has order type ω
2
.

Thus the correct ω
2
 demand is not “infinite in every row,” but:

infinite in infinitely many rows.

The finite-pattern separation lemma was formulated at exactly this weaker level.

8.5 Componentwise order preservation does not preserve the global shuffle

Suppose ω
2
 is partitioned into columns

C
m
	​

={ωn+m:n<ω}.

Each C
m
	​

 has order type ω. Define

I
m
	​

={ωn+m:n≥m}.

Then

otp(I
m
	​

)=otp(C
m
	​

)=ω

for every m. However, in row n, the union ⋃
m
	​

I
m
	​

 contains only the n+1 points with m≤n. Consequently,

otp(
m
⋃
	​

I
m
	​

)=ω,

not ω
2
.

Therefore the following tempting rank induction is invalid:

Choose in every component an independent subset having the same order type as that component, and take their union.

The ambient interleaving of the components can collapse the resulting order type.

8.6 Simultaneously retaining every member of a countable family is false

Let A
∗
	​

={c
n
	​

:n<ω}, and let A
n
	​

 be the infinite leaf set of a star centered at c
n
	​

. The graph is a disjoint union of stars.

There cannot be infinite subsets

B
∗
	​

⊆A
∗
	​

,B
n
	​

⊆A
n
	​

(n<ω)

that are all pairwise anticomplete. Every c
n
	​

∈B
∗
	​

 is adjacent to all of A
n
	​

.

Thus a separation theorem retaining every set in a countable family is false. What survives is the weaker version that retains infinitely many members of each of finitely many sequences.

8.7 Cardinality alone cannot settle the problem

The cardinal-sized independent set theorem is optimal at the cardinal level, but insufficient for noninitial ordinals.

For instance, in

α=κ+κ,

a subset contained in the first block may have cardinality κ but order type only κ<α.

Any general solution must therefore control the distribution of the independent set through the ordinal, not merely its size.

9. Minimal-counterexample constraints

Assume conditionally that a counterexample exists, and choose the least counterexample ordinal α. Then choose, among bad rayless graphs on α, one of minimum finite-separator rank.

The preceding results force the following.

Ordinal constraints
α is not an initial ordinal.

Also,

α≥ω
3
,

because every nonzero limit ordinal below ω
3
 has been handled.

For every limit β<α, P(β) holds by minimality. Consequently, whenever Y⊆α has order type β, the rayless graph G[Y] has an independent subset of order type β.

Thus all smaller-order local restrictions are good; the failure must be one of coherence when these local independent sets are assembled.

Rank constraints

Let S be a finite separator witnessing the rank of G. Every component C of G−S has

otp(C)<α.

Otherwise otp(C)=α. Relabeling C by α would give a lower-rank bad graph on α, contradicting rank minimality.

Hence a minimum-rank counterexample must have this form:

a finite separator;

components of strictly smaller order type and strictly smaller graph rank;

the components interleaved in the ambient ordinal so that their union has order type α;

no possible selection of independent subsets from those components has union of order type α.

The obstruction must therefore be an interleaving or shuffle obstruction, not a large internally bad component.

10. A useful invariant: ordinal demand trees

For countable ordinals, the order-type requirement can be encoded as an iterated largeness condition.

For ω
2
, divide into ω-rows. A subset contains a copy of ω
2
 exactly when it is infinite in infinitely many rows.

For ω
3
, divide into blocks indexed by n, each divided into rows indexed by m. A subset contains a copy of ω
3
 when:

infinitely many outer blocks are active;

in every active outer block, infinitely many rows are active;

in every active row, infinitely many points are chosen.

This suggests an ordinal demand tree:

leaves represent ω-blocks;

an ω-branching internal node demands that infinitely many children survive;

finite union nodes encode finite Cantor coefficients and ordinal sums.

The finite-pattern separation lemma proves compatibility between rayless decomposition ranks and demand trees having at most one ω-branching level. The next target is compatibility with two branching levels, beginning with ω
3
.

This reformulates the problem as an interaction between two well-founded structures:

the finite-separator decomposition tree of a rayless graph;

the ordinal demand tree specifying what a copy of α must occupy.

11. Local-to-global formulation

For a least bad α, consider the tree whose nodes are increasing independent embeddings

f:β→α

for smaller β, ordered by extension.

Minimality supplies independent embeddings at all smaller limit order types. A branch of length α would solve the problem for G.

The failure would therefore resemble a tree having arbitrarily long partial independent embeddings but no coherent branch of length α. For ordinals of countable cofinality, this is a fusion problem: independent copies at stages

α
0
	​

<α
1
	​

<⋯,
n
sup
	​

α
n
	​

=α,

need not be nested or even approximately compatible.

The explicit column example above demonstrates why arbitrary local choices cannot simply be united.

12. Finite falsification programs

Finite computation cannot certify raylessness merely by bounding finite path lengths: a rayless graph may contain finite paths of every finite length in different components. Computation should instead use a finite-separator-rank certificate.

Test A: finite-class transversals

For a finite box approximating ω
3
, use vertices

(i,j,k)∈[N]
3
.

Partition the vertices into classes of size at most d. A transversal is encoded by variables x
v
	​

∈{0,1} with

v∈C
∑
	​

x
v
	​

≤1

for each class C.

Define a selector to be (r,s,t)-rich if:

at least r outer indices i are active;

in each active i, at least s middle indices j are active;

in each active (i,j), at least t vertices are selected.

Search for partitions minimizing the largest achievable (r,s,t). A bounded profile as N grows would suggest a rank-one obstruction; unbounded growth would falsify that construction family.

No finite result alone gives the transfinite conclusion, but explicit extremizers could reveal a recursive pattern.

Test B: bounded-rank graph search

Generate graphs together with a decomposition certificate:

each internal node has a separator of size at most s;

deleting it produces child components;

leaves have size at most d;

decomposition depth or ordinal-rank proxy is bounded.

Use a cutting-plane procedure:

propose a graph with the decomposition certificate;

solve for a richest independent set;

if a target-rich independent set exists, add a constraint excluding that graph pattern;

repeat.

The first meaningful target is the finite proxy for the two-level ω
3
 separation statement.

Test C: nested path detection

Any proposed recursive counterexample should be tested not merely for arbitrarily long finite paths but for an extendable nested path system.

The rank theorem gives the exact failure certificate: if after every finite deletion there remains an unranked connected component, the recursive construction produces a ray. Thus a candidate should come with an explicit well-founded finite-separator decomposition, not only an assertion that no obvious ray exists.

13. Current boundary

Under the standard ray interpretation, the present attacks establish:

Every infinite initial ordinal satisfies P(α).
	​


They also establish:

Every nonzero limit α<ω
3
 satisfies P(α).
	​


No counterexample was obtained.

The first untreated countable case is

α=ω
3
.
	​


The sharp next obligation is the two-level separation target for the family A
n,m
	​

. Beyond that, noninitial uncountable ordinals require a cardinal-preserving, order-sensitive separation theorem; the general cardinal-sized independent set theorem alone does not suffice.
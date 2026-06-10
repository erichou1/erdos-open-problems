# Erdős Problem #159 [unsolved] 22%

---

## ChatGPT Response

Phase 0: Formalization

Let R(C
4
	​

,K
n
	​

) be the least integer N such that every red/blue coloring of E(K
N
	​

) contains either a red C
4
	​

 or a blue K
n
	​

.

Equivalently, for a finite simple graph G, interpret red edges as E(G). Then a blue K
n
	​

 is exactly an independent set of size n in G. Thus

R(C
4
	​

,K
n
	​

)≤N

means:

∀G,∣V(G)∣=N,(G is C
4
	​

-free)⇒α(G)≥n.

The target statement is:

∃c>0 ∃C>0 ∃n
0
	​

 ∀n≥n
0
	​

,R(C
4
	​

,K
n
	​

)≤Cn
2−c
.

Equivalently:

∃c>0 ∃C>0 ∃n
0
	​

 ∀n≥n
0
	​

 ∀G,
G is C
4
	​

-free and ∣V(G)∣≥Cn
2−c
⟹α(G)≥n.

Equivalently in independence-number form, with N=∣V(G)∣, the desired theorem is:

∃ε>0 ∃K>0 ∀C
4
	​

-free G,α(G)≥K∣V(G)∣
1/2+ε
.

Indeed, if α(G)≥KN
1/2+ε
, then requiring α(G)≥n gives

N≫n
1/(1/2+ε)
=n
2/(1+2ε)
=n
2−c
,

where

c=2−
1+2ε
2
	​

=
1+2ε
4ε
	​

>0.

So the problem is equivalent to proving a polynomial improvement over the square-root independence bound for every C
4
	​

-free graph.

Negation

The negation is:

∀c>0 ∀C>0 ∀n
0
	​

 ∃n≥n
0
	​

 ∃G

such that

G is C
4
	​

-free,∣V(G)∣≥Cn
2−c
,α(G)<n.

In independence-number form, the negation says that for every ε>0, there exist arbitrarily large C
4
	​

-free graphs G with

α(G)<∣V(G)∣
1/2+ε

up to arbitrary multiplicative constants.

Basic verified lemmas
Lemma 1: Codegree bound

If G is C
4
	​

-free, then every two distinct vertices have at most one common neighbor.

Proof.
Suppose distinct vertices x,y have two distinct common neighbors a,b. Then

x−a−y−b−x

is a 4-cycle, contradiction. Hence

∣N(x)∩N(y)∣≤1.
Lemma 2: Pair-counting bound

If G is C
4
	​

-free on N vertices with degrees d
1
	​

,…,d
N
	​

, then

v∈V(G)
∑
	​

(
2
d(v)
	​

)≤(
2
N
	​

).

Proof.
The left-hand side counts unordered length-two paths x−v−y. Equivalently, it counts triples ({x,y},v) where v is a common neighbor of x,y. By Lemma 1, each unordered pair {x,y} has at most one common neighbor. Therefore the number of such triples is at most (
2
N
	​

).

Thus

v
∑
	​

d(v)(d(v)−1)≤N(N−1).
Lemma 3: Edge bound

If G is C
4
	​

-free on N vertices, then

e(G)≤
4
N(1+
4N−3
	​

)
	​

<
2
1
	​

N
3/2
+
4
1
	​

N.

Proof.
Let m=e(G). By Lemma 2,

v
∑
	​

d(v)
2
−
v
∑
	​

d(v)≤N(N−1).

Since ∑
v
	​

d(v)=2m,

v
∑
	​

d(v)
2
≤N(N−1)+2m.

By Cauchy,

(2m)
2
≤N
v
∑
	​

d(v)
2
≤N
2
(N−1)+2mN.

So

4m
2
−2Nm−N
2
(N−1)≤0.

Solving the quadratic inequality in m,

m≤
8
2N+
4N
2
+16N
2
(N−1)
	​

	​

=
4
N(1+
4N−3
	​

)
	​

.
Lemma 4: Neighborhood matching bound

If G is C
4
	​

-free and v∈V(G), then the induced graph G[N(v)] has maximum degree at most 1. Therefore

α(G[N(v)])≥⌈
2
d(v)
	​

⌉.

Hence

α(G)≥
2
Δ(G)
	​

.

Proof.
Suppose some b∈N(v) has two distinct neighbors a,c∈N(v). Then

a−b−c−v−a

is a 4-cycle. Contradiction. Therefore G[N(v)] has maximum degree at most 1, so it is a disjoint union of isolated vertices and edges. Such a graph has an independent set of size at least half its vertices. Thus

α(G)≥α(G[N(v)])≥
2
d(v)
	​

.

Taking v of maximum degree gives

α(G)≥
2
Δ(G)
	​

.
Lemma 5: Trivial quadratic Ramsey upper bound

For every C
4
	​

-free graph G with α(G)<n,

∣V(G)∣<2n
2
.

Therefore

R(C
4
	​

,K
n
	​

)≤2n
2

up to harmless lower-order changes.

Proof.
Let I be a maximal independent set. Since α(G)<n,

∣I∣≤n−1.

By maximality, every vertex outside I has at least one neighbor in I. Hence

V(G)⊆I∪
u∈I
⋃
	​

N(u).

By Lemma 4, since α(G)<n,

d(u)<2n

for every u. Thus

∣V(G)∣≤∣I∣+
u∈I
∑
	​

d(u)<n+(n)(2n)<2n
2
+n.

With integer cleanup, this gives the quadratic upper bound.

This proves only exponent 2, not 2−c.

Phase 1: Strategy search

I tested the following strategies.

Strategy	Aim	Verified gain	Obstacle
Direct degree-counting	Use codegree bound to force large independent set	Gives α(G)≫N
1/2
	No polynomial improvement
Maximal independent domination	Cover V(G) by neighborhoods of a maximal independent set	Gives N<2n
2
	Only quadratic
High-degree neighborhood	Use G[N(v)] sparse	Gives α(G)≥Δ/2	Does not control average degree sharply
Edge counting plus Caro–Wei	Combine m≤O(N
3/2
) with α≥N
2
/(2m+N)	Gives α≫N
1/2
	Again no exponent gain
Contradiction from bad graph	Assume α<n, N≥n
2−c
	Produces degree window	Window is consistent
Induction on n	Remove high-degree neighborhoods	Local loss too large	No closed recurrence below n
2

Induction on N	Split into subgraphs	Independence can distribute badly	No useful superadditivity
Regularization	Extract subgraph of large minimum degree	Gives δ≲
N
	​

	Same square-root barrier
Triangle removal	Remove vertices from triangles to get triangle-free piece	Too many triangles may exist	Loss too large
Random subset deletion	Choose random S, delete edges	Gives 
N
	​

-scale set	Dependency structure not strong enough
Auxiliary hypergraph	Encode neighborhoods as almost-linear hypergraph	Clean reformulation	Still needs strong container-style estimate
Counterexample construction	Try to build C
4
	​

-free graph with α≈
N
	​

	No construction found	Codegree and neighborhood restrictions severe

Top three branches selected:

Branch A: maximal independent set plus neighborhood matching;

Branch B: random subset / container-style independence search;

Branch C: regularization and expansion.

Phase 2: Auxiliary structures invented
Definition 1: Badness exponent

For a C
4
	​

-free graph G with N=∣V(G)∣ and α=α(G), define

b(G)=
logα
logN
	​

.

The desired theorem is equivalent to showing that there exists c>0 such that eventually

b(G)≤2−c.

The trivial bound gives only

b(G)≤2+o(1).
Definition 2: Pair-load

Define

L(G)=
v∈V(G)
∑
	​

(
2
d(v)
	​

).

For C
4
	​

-free graphs,

L(G)≤(
2
N
	​

).

A graph that threatens the desired theorem must use the pair-load efficiently while keeping independence small.

Definition 3: Neighborhood matching obstruction

For each vertex v, G[N(v)] is a matching plus isolated vertices. Thus every large degree vertex immediately gives a large independent set.

So any bad graph must satisfy simultaneously:

Δ(G)<2α(G),

and

d
(G)≳
α(G)
N
	​

.

If α(G)<n and N≈n
2−c
, then the average degree must lie in the window

n
1−c
≲
d
(G)≲n
1−c/2
,

while

Δ(G)<2n.

This is not contradictory.

Phase 3: Parallel exploration
Branch A: maximal independent set domination

Assume G is C
4
	​

-free, α(G)<n, and N=∣V(G)∣.

Take a maximal independent set

I={x
1
	​

,…,x
t
	​

},t<n.

Every vertex lies in

I∪N(I).

Since each d(x
i
	​

)<2n,

N≤t+
i=1
∑
t
	​

d(x
i
	​

)<n+2n
2
.

This proves only

R(C
4
	​

,K
n
	​

)≪n
2
.

To improve to n
2−c
, one would need a saving in

i=1
∑
t
	​

d(x
i
	​

).

The natural hope is that the neighborhoods N(x
i
	​

) overlap. But overlap is actually small: by the codegree lemma,

∣N(x
i
	​

)∩N(x
j
	​

)∣≤1.

Small overlap makes the domination cover inefficient for improvement. The method naturally gives n
2
, not n
2−c
.

Branch A result: verified quadratic bound; no exponent saving.

Branch B: random subset / edge deletion

Let G be C
4
	​

-free on N vertices with m≤O(N
3/2
).

Choose a random subset S⊆V(G) with probability p.

Then

E∣S∣=pN,

and

Ee(G[S])=p
2
m≤O(p
2
N
3/2
).

Deleting one endpoint from every edge in G[S] gives an independent set of expected size at least

pN−O(p
2
N
3/2
).

Optimizing with

p≍N
−1/2

gives only

α(G)≫N
1/2
.

To get

α(G)≫N
1/2+ε
,

one would need to choose

p=N
−1/2+ε
,

but then

E∣S∣=N
1/2+ε
,

while

Ee(G[S])≤O(N
−1+2ε
N
3/2
)=O(N
1/2+2ε
),

which is larger than ∣S∣ by a factor N
ε
. Simple deletion fails.

One needs extra structural information showing that edges inside S cluster in a way that leaves a large independent set. The C
4
	​

-free condition gives pair-codegree control, but this alone was insufficient in the explored argument.

Branch B result: random deletion gives 
N
	​

, not 
N
	​

⋅N
ε
.

Branch C: regularization and expansion

Assume α(G)<n. By the greedy independent set bound,

α(G)≥
d
+1
N
	​

.

Thus

d
+1>
n
N
	​

.

So

d
≳
n
N
	​

.

If N=n
2−c
, then

d
≳n
1−c
.

On the other hand, Lemma 3 gives

d
≲N
1/2
=n
1−c/2
.

So a hypothetical bad graph must satisfy

n
1−c
≲
d
≲n
1−c/2
.

This interval is nonempty for every c>0. Therefore first-moment degree counting cannot contradict the existence of such a graph.

Now extract a subgraph H⊆G of minimum degree

δ(H)≥
2
d
(G)
	​

.

This is standard: repeatedly delete vertices of degree below 
d
(G)/2; if all vertices were deleted, the total deleted degree would be less than m(G), contradiction.

Since H is C
4
	​

-free, for any v∈V(H), the sets

N
H
	​

(u)∖{v},u∈N
H
	​

(v),

are pairwise disjoint. Otherwise two neighbors u,w∈N
H
	​

(v) would share another common neighbor, forming a C
4
	​

.

Thus

∣V(H)∣≥1+δ(H)+δ(H)(δ(H)−1)≫δ(H)
2
.

This gives

δ(H)≲∣V(H)∣
1/2
≤N
1/2
,

again matching the previous square-root barrier.

Branch C result: expansion recovers only the same N
1/2
 scale.

GAP NODE: required strengthening

The main unresolved statement is:

∃ε>0 ∃K>0 ∀C
4
	​

-free G,α(G)≥K∣V(G)∣
1/2+ε
.

Ten attacks were attempted:

Direct degree proof: fails at α≫N
1/2
.

Contradiction from α<n: gives consistent degree window.

Stronger theorem using local sparsity: neighborhood sparsity gives only matching structure; no polynomial gain extracted.

Weaker theorem sufficient for original: any fixed ε>0 still requires breaking square-root barrier.

Equivalent formulation through b(G): clean but not decisive.

Auxiliary hypergraph: neighborhoods form a highly restricted family, but no complete independence lower bound derived.

Counterexample search: no explicit construction with α≤N
1/2+o(1)
 found.

Extremal degree analysis: bad graphs must have moderate average degree and bounded maximum degree; no contradiction.

Recursive decomposition: deleting neighborhoods loses too many vertices.

Expansion: C
4
	​

-free gives tree-like growth to radius 2, but not enough beyond that.

The gap remains unresolved.

Verified dependency graph

The following results were fully verified:

C4-free⇒pair codegree≤1.
pair codegree≤1⇒
v
∑
	​

(
2
d(v)
	​

)≤(
2
N
	​

).
v
∑
	​

(
2
d(v)
	​

)≤(
2
N
	​

)⇒e(G)≤
2
1
	​

N
3/2
+O(N).
C4-free⇒G[N(v)] has maximum degree ≤1.
G[N(v)] has maximum degree ≤1⇒α(G)≥Δ(G)/2.
α(G)<n⇒Δ(G)<2n.
α(G)<n⇒∣V(G)∣<O(n
2
).

No verified implication obtained:

α(G)<n⇒∣V(G)∣<O(n
2−c
)

for any fixed c>0.

RESOURCE_EXHAUSTED

A complete proof or disproof of

∃c>0,R(C
4
	​

,K
n
	​

)≪n
2−c

was not obtained within the available reasoning budget.

The rigorous deductions obtained prove the quadratic bound

R(C
4
	​

,K
n
	​

)≪n
2
,

and identify the exact missing strengthening as a polynomial improvement over

α(G)≫∣V(G)∣
1/2

for all C
4
	​

-free graphs.

PROOF_CONFIDENCE

92 / 100 for the verified lemmas and reductions.

COMPLETENESS_SCORE

22 / 100 toward the original theorem.

ADVERSARIAL_SURVIVAL_SCORE

85 / 100 for the partial results; 0 / 100 for the unproved main theorem, since no complete proof was found.

RESOURCE_USAGE

Estimated reasoning budget used: 100%.

Branches explored: 3 main branches, 12 initial strategies.

Lemmas generated: 5 fully verified lemmas.

Failed proof attempts: 10 gap-node attacks.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

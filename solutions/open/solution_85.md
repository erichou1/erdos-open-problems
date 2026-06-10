# Erdős Problem #85 [unsolved] 38%

---

## ChatGPT Response

Phase 0: formalization

Let

a(n)=max{δ(G):∣V(G)∣=n,G contains no C
4
	​

}.

Then the threshold definition gives

f(n)=a(n)+1.

Indeed, if a(n)=d, then some C
4
	​

-free graph has minimum degree d, so minimum degree d does not force a C
4
	​

. But no C
4
	​

-free graph has minimum degree d+1, so minimum degree d+1 does force a C
4
	​

.

Thus the question is equivalent to:

∃N∀n≥N,a(n+1)≥a(n).
Negation

The negation is:

∀N∃n≥N,a(n+1)<a(n).

Equivalently, there are arbitrarily large n and some integer d such that

a(n)=d,a(n+1)≤d−1.

So a counterexample at n would mean:

There exists a C
4
	​

-free graph G on n vertices with δ(G)≥d.

There is no C
4
	​

-free graph on n+1 vertices with minimum degree at least d.

Basic invariant: codegrees

For distinct vertices x,y, write

λ(x,y)=∣N(x)∩N(y)∣.

A graph is C
4
	​

-free if and only if

λ(x,y)≤1

for every distinct pair x,y. This is because two distinct common neighbors of x,y form a C
4
	​

.

Therefore, in every C
4
	​

-free graph,

v∈V(G)
∑
	​

(
2
deg(v)
	​

)≤(
2
n
	​

).

If δ(G)≥d, then

n(
2
d
	​

)≤(
2
n
	​

),

so

d(d−1)≤n−1.

Thus

a(n)≤⌊
2
1+
4n−3
	​

	​

⌋.

This is a verified upper bound from first principles.

Equivalent extension formulation

The desired monotonicity would follow from the stronger statement:

For all sufficiently large n, every C
4
	​

-free graph G on n vertices with δ(G)=a(n) can be transformed into a C
4
	​

-free graph on n+1 vertices with minimum degree at least a(n).

But that stronger statement is not obviously true. Local extension can fail.

Suppose G is C
4
	​

-free with δ(G)≥d. One simple way to extend G is to add a new vertex z adjacent to a set S⊆V(G) of size d. This preserves minimum degree at least d. It preserves C
4
	​

-freeness exactly when no two vertices of S have a common neighbor in G. Formally:

Lemma 1: safe vertex-addition criterion

If G is C
4
	​

-free with δ(G)≥d, and there exists S⊆V(G) with ∣S∣=d such that

∀x

=y∈S,N(x)∩N(y)=∅,

then there exists a C
4
	​

-free graph G
′
 on n+1 vertices with δ(G
′
)≥d.

Proof: add a new vertex z adjacent exactly to S. Any new C
4
	​

 would have to use z, hence would have form

z−x−u−y−z

with x,y∈S and u∈N(x)∩N(y), contradicting the defining property of S. Old C
4
	​

's do not appear because G had none. Minimum degree remains at least d, and z has degree d. ∎

So a drop a(n+1)<a(n) can only occur if every extremal C
4
	​

-free n-vertex graph with minimum degree d=a(n) has no such d-set S.

A second extension mechanism: vertex splitting

There is another local extension method.

Let G be C
4
	​

-free with δ(G)≥d. Suppose v∈V(G) has large degree. Remove v, replace it by two adjacent vertices v
1
	​

,v
2
	​

, and partition N(v)=A⊔B. Join v
1
	​

 to every vertex in A, and v
2
	​

 to every vertex in B.

Old neighbors preserve their degree. The new vertices have degrees

deg(v
1
	​

)=∣A∣+1,deg(v
2
	​

)=∣B∣+1.

So we need

∣A∣,∣B∣≥d−1.

The dangerous case is an edge across the partition: if a∈A, b∈B, and ab∈E(G), then

v
1
	​

−a−b−v
2
	​

−v
1
	​


is a C
4
	​

. Therefore we need no edges between A and B.

In a C
4
	​

-free graph, G[N(v)] has maximum degree at most 1. Indeed, if x,y,z∈N(v) and xy,yz∈E(G), then

x−v−z−y−x

is a C
4
	​

. Thus G[N(v)] is a matching plus isolated vertices.

Lemma 2: safe splitting criterion

If G is C
4
	​

-free with δ(G)≥d, and there exists v∈V(G) such that N(v) can be partitioned as

N(v)=A⊔B

with

∣A∣,∣B∣≥d−1

and no edge of G[N(v)] crosses between A and B, then there exists a C
4
	​

-free graph on n+1 vertices with minimum degree at least d.

Proof: perform the split described above. Minimum degree is preserved by the size condition. A new C
4
	​

 cannot use both v
1
	​

,v
2
	​

, because that would require a cross-edge between A and B. A new C
4
	​

 using only v
1
	​

 would correspond to an old C
4
	​

 using v, and similarly for v
2
	​

. Hence no C
4
	​

 is created. ∎

Consequently, a drop a(n+1)<a(n) can only occur in graphs where neither the safe-addition nor safe-splitting mechanism is available.

This already gives a nontrivial obstruction profile for any counterexample.

Tight counting obstruction

The codegree inequality gives

v
∑
	​

(
2
deg(v)
	​

)≤(
2
n
	​

).

Suppose n=d(d−1)+1 and δ(G)≥d. Then

n(
2
d
	​

)=(
2
n
	​

).

Therefore equality must hold everywhere:

every vertex has degree exactly d;

every pair of vertices has exactly one common neighbor.

Thus the adjacency matrix A would satisfy

A
2
=dI+(J−I)=(d−1)I+J.

The all-ones vector has eigenvalue d. On the orthogonal complement of the all-ones vector, every eigenvalue λ of A satisfies

λ
2
=d−1.

So the nontrivial eigenvalues are all ±
d−1
	​

. Since tr(A)=0, we would need

d+r
d−1
	​

−s
d−1
	​

=0

for nonnegative integers r,s with r+s=n−1. Hence

(r−s)
d−1
	​

=−d.

If d>2, this is impossible. If d−1 is not a square, the left side is irrational while the right side is rational. If d−1=q
2
, then d=q
2
+1, so

r−s=−
q
q
2
+1
	​

=−q−
q
1
	​

,

not an integer unless q=1, i.e. d=2.

Therefore:

Lemma 3

For every d>2, there is no C
4
	​

-free graph on

n=d(d−1)+1

vertices with minimum degree at least d.

Thus the crude counting lower bound cannot be sharp for d>2.

This does not prove monotonicity, but it rules out one possible family of extremely tight counterexamples.

Branch analysis
Branch A: prove monotonicity by adding one vertex

This branch reduces the problem to finding a set S of size d=a(n) with pairwise disjoint neighborhoods.

The obstruction is the auxiliary graph H on V(G), where xy∈E(H) iff x,y have a common neighbor in G. A safe set S is an independent set in H.

However,

E(H)=
v
∑
	​

(
2
deg(v)
	​

)

because C
4
	​

-freeness prevents duplicate codegree witnesses. The bound

E(H)≤(
2
n
	​

)

alone gives no useful lower bound on α(H), since H may be very dense. Thus the simple independence-number route stalls.

Unresolved target:

α(H)≥d

for every sufficiently large extremal C
4
	​

-free graph G.

No proof obtained.

Branch B: prove monotonicity by splitting a vertex

This works if some vertex has enough degree and its neighborhood can be split safely.

Since G[N(v)] is a matching, the only obstruction is a partition-size obstruction. If deg(v) is noticeably larger than 2d, splitting succeeds. Therefore any counterexample must have all degrees bounded roughly by 2d.

This is a real restriction, but not enough. A graph may be d-regular, in which case splitting is impossible by degree count.

Unresolved target:

Every sufficiently large extremal C
4
	​

-free graph either has a safely splittable vertex or has a safe d-set for vertex addition.

No proof obtained.

Branch C: prove monotonicity from counting rigidity

A drop a(n+1)<a(n) with d=a(n) means d(d−1)≤n−1, but no graph of order n+1 supports minimum degree d.

The counting inequality alone does not contradict this. It gives only a necessary condition, not a sufficient construction. Lemma 3 shows that equality at n=d(d−1)+1 is impossible for d>2, but does not settle nearby values.

Unresolved target:

Classify or construct C
4
	​

-free graphs with δ≥d for every order after the first admissible order.

No proof obtained.

Verified conclusions

The original statement is equivalent to eventual monotonicity of

a(n)=f(n)−1.

The following are rigorously established:

f(n)=a(n)+1.

Every C
4
	​

-free graph satisfies

v
∑
	​

(
2
deg(v)
	​

)≤(
2
n
	​

).

Therefore

a(n)≤⌊
2
1+
4n−3
	​

	​

⌋.

Safe vertex-addition works if there is a d-set with pairwise disjoint neighborhoods.

Safe vertex-splitting works under the partition condition above.

For every d>2, no C
4
	​

-free graph on d(d−1)+1 vertices has minimum degree at least d.

These results significantly constrain possible counterexamples, but they do not prove or disprove eventual monotonicity.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100
COMPLETENESS_SCORE: 38/100
ADVERSARIAL_SURVIVAL_SCORE: 82/100

RESOURCE_USAGE: approximately 90% reasoning budget used; 3 main branches explored; 6 lemmas or structural claims generated; 3 failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

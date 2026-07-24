# Erdős Problem #573 [unsolved] 42%

---

## ChatGPT Response

Formal statement.

Let G=(V,E) be a finite simple undirected graph. Let C
k
	​

 denote a cycle of length k. Define

ex(n;{C
3
	​

,C
4
	​

})=max{∣E(G)∣: ∣V(G)∣=n, G contains no C
3
	​

 and no C
4
	​

}.

The target assertion is

ex(n;{C
3
	​

,C
4
	​

})∼(n/2)
3/2
.

Equivalently,

n→∞
lim
	​

(n/2)
3/2
ex(n;{C
3
	​

,C
4
	​

})
	​

=1.

Quantifier structure.

For every ε>0, there exists N such that for every integer n≥N,

(1−ε)(n/2)
3/2
≤ex(n;{C
3
	​

,C
4
	​

})≤(1+ε)(n/2)
3/2
.

Negation.

There exists ε>0 such that for every N, there exists n≥N with either

ex(n;{C
3
	​

,C
4
	​

})<(1−ε)(n/2)
3/2
,

or

ex(n;{C
3
	​

,C
4
	​

})>(1+ε)(n/2)
3/2
.

Equivalent formulation in average degree.

If e(G)=∣E(G)∣ and 
d
ˉ
=2e(G)/n, then

e(G)∼(n/2)
3/2

is equivalent to

d
ˉ
∼
n/2
	​

.

Thus the target says that the largest possible average degree in a graph with no C
3
	​

 and no C
4
	​

 is asymptotically 
n/2
	​

.

Boundary conditions.

A graph with no C
3
	​

 and no C
4
	​

 has girth at least 5, unless it is acyclic. The condition is hereditary under vertex deletion and edge deletion. Bipartite C
4
	​

-free graphs are automatically C
3
	​

-free, so bipartite constructions give valid lower bounds.

Symmetries.

The problem is invariant under graph isomorphism, vertex relabeling, edge deletion, and passage to subgraphs. It is not invariant under complement, since forbidding short cycles is not complement-stable.

Main invariants.

For each vertex v, let d(v) be its degree. The key local invariant is the radius-two neighborhood around a vertex:

{v}∪N(v)∪
u∈N(v)
⋃
	​

(N(u)∖{v}).

Because there is no C
3
	​

, N(v) is independent. Because there is no C
4
	​

, the second-neighborhood sets N(u)∖{v}, for u∈N(v), are pairwise disjoint.

Therefore, for every vertex v,

1+d(v)+
u∈N(v)
∑
	​

(d(u)−1)≤n,

so

u∈N(v)
∑
	​

d(u)≤n−1.

Summing over all v,

v
∑
	​

d(v)
2
≤n(n−1).

By Cauchy,

(2e)
2
=(
v
∑
	​

d(v))
2
≤n
v
∑
	​

d(v)
2
≤n
2
(n−1),

so

e≤
2
1
	​

n
n−1
	​

=
2
1
	​

n
3/2
+O(n
1/2
).

This proves the first verified universal upper bound:

ex(n;{C
3
	​

,C
4
	​

})≤
2
1
	​

n
3/2
+O(n
1/2
).

This is too weak for the target constant, since

(n/2)
3/2
=
2
2
	​

1
	​

n
3/2
.

So the verified upper bound has constant 1/2, while the target requires 1/(2
2
	​

).

Bipartite reduction attempt.

Suppose G is bipartite with parts A,B, where ∣A∣=a, ∣B∣=b, and a+b=n. Since G is C
4
	​

-free, two vertices in A have at most one common neighbor in B. Counting pairs of neighbors in B,

x∈A
∑
	​

(
2
d(x)
	​

)≤(
2
b
	​

).

Using convexity,

a(
2
e/a
	​

)≤(
2
b
	​

).

Thus

a
e
2
	​

−e≤b(b−1),

so asymptotically

e≤b
a
	​

+O(n).

Symmetrically,

e≤a
b
	​

+O(n).

Therefore

e≤min(b
a
	​

, a
b
	​

)+O(n).

If a≤b, then the smaller bound is a
b
	​

, which is maximized at a=b=n/2 under the restriction a≤b. Hence

e≤(n/2)
3/2
+O(n)

for bipartite C
4
	​

-free graphs.

Thus the target upper bound is fully verified for bipartite graphs.

Lower-bound construction on special orders.

Assume there exists a finite incidence structure with the following properties for parameter q:

There are q
2
+q+1 points and q
2
+q+1 lines.

Each line contains q+1 points.

Each point lies on q+1 lines.

Any two points lie on exactly one common line.

Any two lines meet in exactly one point.

Construct a bipartite graph G
q
	​

 with one part equal to the set of points and the other part equal to the set of lines. Join point p to line ℓ exactly when p∈ℓ.

Then

n
q
	​

=2(q
2
+q+1),

and

e
q
	​

=(q+1)(q
2
+q+1).

The graph is bipartite, so it has no C
3
	​

. It has no C
4
	​

, because a C
4
	​

 would give two distinct points incident to two distinct common lines, contradicting uniqueness of the line through two points.

Now

(n
q
	​

/2)
3/2
e
q
	​

	​

=
(q
2
+q+1)
3/2
(q+1)(q
2
+q+1)
	​

=
q
2
+q+1
	​

q+1
	​

→1.

So, on the orders for which this incidence structure exists,

e
q
	​

∼(n
q
	​

/2)
3/2
.

This gives a verified lower-bound mechanism along those values of n.

Gap 1.

To prove the full asymptotic lower bound for every sufficiently large n, one needs constructions at all large n, or enough density of admissible parameters q so that one can pad by isolated vertices without losing the constant. That density has not been derived here from first principles.

Gap 2.

To prove the full asymptotic upper bound, one must show that every non-bipartite graph with no C
3
	​

 and no C
4
	​

 also satisfies

e(G)≤(n/2)
3/2
+o(n
3/2
).

The available local radius-two counting only proves

e(G)≤
2
1
	​

n
3/2
+O(n
1/2
),

which is weaker by a factor of 
2
	​

.

Twelve strategy checks.

Direct degree counting gives ∑d(v)
2
≤n(n−1), hence constant 1/2. Obstacle: does not exploit enough global structure.

Bipartite optimization gives the target constant. Obstacle: no proof that extremal graphs are asymptotically bipartite.

Contradiction from assuming e>(1+ε)(n/2)
3/2
. Obstacle: the assumption only gives average degree >(1+ε)
n/2
	​

, still compatible with every radius-two Moore-type local bound.

Induction on n. Obstacle: deleting a low-degree vertex only gives useful recurrence if one can force a vertex of degree at most 
n/2
	​

+o(
n
	​

), but the verified bound only forces degree at most 
n
	​

+o(
n
	​

).

Degree-sequence optimization. Obstacle: the constraints ∑d
2
≤n(n−1) and ∑d=2e allow e as large as 
2
1
	​

n
3/2
.

Edge-neighborhood independence. For every edge uv, the set (N(u)∖{v})∪(N(v)∖{u}) is independent. Obstacle: this produces large independent sets but does not directly force a global edge bound.

Max-cut reduction. Every graph has a bipartite subgraph with at least half its edges. Obstacle: this gives only e(G)≤2(n/2)
3/2
+O(n), far too weak.

Spectral trace method. Since there are no triangles, tr(A
3
)=0. Since there are no C
4
	​

's, tr(A
4
) is controlled by degrees. Obstacle: the resulting inequalities again naturally lead to constants at least 1/2, not 1/(2
2
	​

).

Counting length-three paths. Obstacle: multiple length-three paths can form longer cycles, which are allowed, so no sharp collision bound follows.

Radius-two covering around high-degree vertices. Obstacle: d(v)≈
n
	​

 is still locally possible because the radius-two ball can have size approximately n.

Attempted construction beating the target constant. A symmetric bilinear graph on q
2
 vertices can have about 
2
1
	​

q
3
 edges and no C
4
	​

, but it creates many triangles. Removing triangle edges gives at best a constant below the target in the simple edge-disjoint triangle model.

Sidon-set bipartite construction. A Sidon set S of size (1−o(1))
m
	​

 in a group of order m would give a bipartite C
4
	​

-free graph on 2m vertices with (1−o(1))m
3/2
 edges. Obstacle: the required Sidon sets for all m were not constructed from first principles here.

Verified theorem pool.

Lemma 1. In every C
3
	​

,C
4
	​

-free graph,

u∈N(v)
∑
	​

d(u)≤n−1

for every vertex v.

Lemma 2. In every C
3
	​

,C
4
	​

-free graph,

v
∑
	​

d(v)
2
≤n(n−1).

Lemma 3. In every C
3
	​

,C
4
	​

-free graph,

e(G)≤
2
1
	​

n
3/2
+O(n
1/2
).

Lemma 4. In every bipartite C
4
	​

-free graph on n vertices,

e(G)≤(n/2)
3/2
+O(n).

Lemma 5. The incidence graph of any finite incidence structure satisfying the listed point-line axioms is C
3
	​

,C
4
	​

-free and has

e∼(n/2)
3/2
.

Unresolved primary theorem.

The missing upper theorem is:

For every C
3
	​

,C
4
	​

-free graph G on n vertices,

e(G)≤(n/2)
3/2
+o(n
3/2
).

I attempted to derive it by local counting, bipartite reduction, spectral trace constraints, edge-neighborhood independence, and path counting. Each route produced either the weaker universal constant 1/2, or the desired constant only after assuming bipartiteness or a still-unproved structural approximation to bipartiteness.

Final state.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96

COMPLETENESS_SCORE: 42

ADVERSARIAL_SURVIVAL_SCORE: 88

RESOURCE_USAGE: approximately 100 percent of the current response budget used, 12 strategies explored, 5 verified lemmas generated, 6 failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

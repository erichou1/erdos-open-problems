# Erdős Problem #1070 [unsolved] 27%

---

## ChatGPT Response

Phase 0 — Formalization

For a finite set P⊂R
2
, define its unit-distance graph

G(P)=(P,E
P
	​

),E
P
	​

={{x,y}⊆P:∥x−y∥
2
	​

=1}.

Write α(G) for the maximum cardinality of an independent set of G. Then

f(n)=
P⊂R
2
∣P∣=n
	​

min
	​

α(G(P)).

The minimum exists because α(G(P)) is an integer in {1,…,n}.

The proposed inequality is

∀n∈N,f(n)≥
4
n
	​

.
	​


Because f(n) is integral, this is equivalent to

∀n∈N, ∀P⊂R
2
,∣P∣=n⟹α(G(P))≥⌈
4
n
	​

⌉.
(T)
Negation

The negation of (T) is

∃n∈N ∃P⊂R
2
,∣P∣=nandα(G(P))≤⌈
4
n
	​

⌉−1.
(N)

Equivalently, there is a finite planar point set such that every subset of more than n/4 points contains a pair at distance 1.

Equivalent covering formulation

For every finite graph G,

χ(G)≥
α(G)
∣V(G)∣
	​

.

Indeed, every color class is independent, so a proper coloring with χ(G) colors partitions V(G) into sets of size at most α(G).

Consequently, a counterexample to (T) must satisfy

χ(G(P))≥5.

The converse is invalid: χ(G)≥5 does not imply α(G)<∣V(G)∣/4.

Symmetries and boundary conditions

The graph G(P) is unchanged up to isomorphism under translations, rotations, and reflections of P. General scaling is not a symmetry because it changes the distinguished distance 1.

For 1≤n≤4,

α(G(P))≥1=⌈
4
n
	​

⌉,

so the assertion holds trivially.

Verified geometric structure
Lemma 1: No four planar points are pairwise at unit distance

Suppose p
0
	​

,p
1
	​

,p
2
	​

,p
3
	​

∈R
2
 were pairwise at distance 1. Put

v
i
	​

=p
i
	​

−p
0
	​

,i=1,2,3.

Then ∥v
i
	​

∥=1, and for i

=j,

1=∥v
i
	​

−v
j
	​

∥
2
=∥v
i
	​

∥
2
+∥v
j
	​

∥
2
−2v
i
	​

⋅v
j
	​

=2−2v
i
	​

⋅v
j
	​

,

so v
i
	​

⋅v
j
	​

=
2
1
	​

.

Their Gram matrix is

M=
	​

1
1/2
1/2
	​

1/2
1
1/2
	​

1/2
1/2
1
	​

	​

.

Its eigenvalues are 2,
2
1
	​

,
2
1
	​

, hence it has rank 3. But three vectors in R
2
 have a Gram matrix of rank at most 2, a contradiction.

Therefore every unit-distance graph in R
2
 is K
4
	​

-free.

This condition alone is insufficient: arbitrary K
4
	​

-free graphs need not have independence ratio at least 1/4.

Lemma 2: Two vertices have at most two common neighbors

For distinct points x,y∈P, every common neighbor belongs to

C(x,1)∩C(y,1),

the intersection of two distinct unit circles. Two distinct circles have at most two intersection points. Thus

∣N(x)∩N(y)∣≤2.
(1)

In particular, a unit-distance graph contains no K
2,3
	​

.

Lemma 3: Every induced neighborhood has maximum degree at most two

Fix x∈P. Every y∈N(x) lies on the unit circle centered at x.

After writing such a point as

y=x+(cosθ,sinθ),

two neighbors corresponding to angles θ,ϕ are at unit distance precisely when

∥y−z∥
2
cos(θ−ϕ)
	​

=2−2cos(θ−ϕ)=1,
=
2
1
	​

.
	​


Hence

θ−ϕ≡±
3
π
	​

(mod2π).

For any fixed θ, there are at most two possible angles adjacent to it. Therefore

Δ(G[N(x)])≤2.
(2)

Consequently, every neighborhood is a disjoint union of paths and cycles.

Lemma 4: Every neighborhood contains an independent subset of at least one third of its vertices

A graph of maximum degree at most two is a disjoint union of paths and cycles. Every path or even cycle has independence ratio at least 1/2, and every odd cycle of length ℓ≥3 has independence number (ℓ−1)/2≥ℓ/3. Therefore

α(G[N(x)])≥
3
∣N(x)∣
	​

.
(3)

This is a genuine local constraint, but it does not immediately globalize to α(G)≥n/4.

Lemma 5: Each edge lies in at most two triangles

If xy∈E(G), a third vertex completing xy to a triangle is a common neighbor of x and y. Lemma 2 gives at most two such vertices.

If m and t denote the numbers of edges and triangles, respectively, counting edge–triangle incidences gives

3t≤2m.
(4)
Structural reductions and their unresolved points
Branch A: A maximum-independent-set exchange argument

Let I be a maximum independent set and put R=V(G)∖I. Maximality implies

N
I
	​

(v):=N(v)∩I

=∅(v∈R).

To prove ∣V(G)∣≤4∣I∣, it would suffice to assign every vertex of R to an adjacent vertex of I, with no element of I receiving more than three assignments.

The exact necessary and sufficient condition for such a capacitated matching is

∣X∣≤3∣N
I
	​

(X)∣for every X⊆R.
(5)

Maximum independence gives only

α(G[X])≤∣N
I
	​

(X)∣.
(6)

Indeed, if J⊆X were independent with
∣J∣>∣N
I
	​

(X)∣, then

(I∖N
I
	​

(X))∪J

would be an independent set larger than I.

Thus (5) would follow from

α(G[X])≥
3
∣X∣
	​

.
(7)

But (7) is not established for arbitrary induced subgraphs of unit-distance graphs and is stronger than the original 1/4 target. The exchange method therefore closes only under an unproved stronger assertion.

Branch B: Minimal counterexample analysis

Assume a counterexample G exists and choose one with the minimum number n of vertices. Then

α(G)<
4
n
	​

.
(8)

For every vertex v, minimality gives

α(G−v)≥
4
n−1
	​

.

Since α(G)≥α(G−v),

4
n−1
	​

≤α(G)<
4
n
	​

.

As α(G) is integral, this forces

n≡1(mod4),α(G)=
4
n−1
	​

.
(9)

Write n=4k+1. Then a minimal counterexample must have

α(G)=k.

Moreover, for every vertex v,

α(G−v)=k.
(10)

Thus every vertex can be avoided by some maximum independent set.

This arithmetic rigidity is verified, but it does not itself contradict the geometric constraints (1)–(4).

Branch C: Low-degree deletion

Let G be a minimal counterexample with n=4k+1 and α(G)=k.

Suppose v has degree at most three. Delete its closed neighborhood:

H=G−N[v].

Then

∣V(H)∣≥n−4=4(k−1)+1.

If H obeyed the target inequality, it would contain an independent set of size at least k. Adding v would give an independent set of size k+1 in G, contradicting α(G)=k.

Minimality applies because H has fewer vertices. Therefore a minimal counterexample cannot contain a vertex of degree at most three:

δ(G)≥4.
(11)

Hence any counterexample has a vertex-minimal induced subgraph satisfying simultaneously

⎩
⎨
⎧
	​

∣V(G)∣=4k+1,
α(G)=k,
δ(G)≥4,
G is K
4
	​

-free,
G is K
2,3
	​

-free,
Δ(G[N(v)])≤2∀v.
	​

(12)

No contradiction has been derived from this system.

Branch D: Neighborhood replacement

Fix v. By Lemma 4, N(v) contains an independent set of size at least d(v)/3.

This yields a local independent set, but it cannot generally be combined with an independent set outside N[v], because vertices in the chosen part of N(v) can have edges to vertices outside N[v].

A valid recursive inequality is only

α(G)≥1+α(G−N[v]).
(13)

For minimum degree at least four, this recurrence by itself gives no n/4 lower bound: deleting N[v] may remove substantially more than four vertices.

Branch E: Degree and incidence counting

From the absence of K
2,3
	​

,

z∈V(G)
∑
	​

(
2
d(z)
	​

)=
{x,y}⊆V(G)
∑
	​

∣N(x)∩N(y)∣≤2(
2
n
	​

).
(14)

Thus

z
∑
	​

d(z)
2
−
z
∑
	​

d(z)≤2n(n−1).
(15)

This controls the second moment of the degree sequence, but it permits average degree on the order of 
n
	​

. Standard greedy estimates based only on degrees consequently produce sublinear guarantees in the worst allowed degree range, not the required linear bound n/4.

Branch F: Random-order local selection

Selecting a vertex when it appears before all of its neighbors gives the rigorous bound

α(G)≥
v∈V(G)
∑
	​

d(v)+1
1
	​

.
(16)

For a minimum-degree-four graph, this is not necessarily at least n/4; vertices of degree greater than three contribute less than 1/4.

The neighborhood structure (2) suggests permitting additional selected vertices after resolving local conflicts, but no selection rule was found for which both of the following could be proved:

the resulting set is always independent;

every vertex is selected with probability at least 1/4.

Branch G: Four-part partition

The target follows if every finite unit-distance graph admits a partition into four independent sets. That condition is sufficient because the largest part then has size at least n/4.

It is not equivalent to the target. A graph may satisfy

α(G)≥
4
∣V(G)∣
	​


without being four-colorable. Therefore failure to construct a four-coloring does not resolve the problem, and proving a four-color theorem would be strictly stronger than required.

Branch H: Weighted and fractional formulations

A probability distribution on independent sets satisfying

Pr(v∈I)≥
4
1
	​

for every v
(17)

would imply

E∣I∣≥
4
n
	​


and hence the desired bound.

More generally, the weighted assertion

I independent
max
	​

v∈I
∑
	​

w
v
	​

≥
4
1
	​

v
∑
	​

w
v
	​

(w
v
	​

≥0)
(18)

would imply (17) by finite linear-programming duality and would be stronger than the unweighted problem.

No construction establishing (17) or (18) from the local geometric properties was obtained.

Branch I: Translation-averaging

Let A⊆R
2
 contain no pair at distance 1, and suppose translations of A admit a well-defined averaging procedure with point-inclusion probability ρ. For a finite set P,

E
t
	​

∣P∩(A+t)∣=ρ∣P∣.

Every intersection P∩(A+t) is independent, so some translate gives an independent subset of size at least ρn.

Thus a distance-avoiding set of translation density 1/4 would prove the target. This is only a sufficient mechanism. No such set or averaging construction was derived, and inability to obtain one cannot disprove the finite inequality.

Branch J: Induction using a reducible configuration

Induction would close if every nonempty unit-distance graph contained a set S such that

α(G[S])≥
4
∣S∣
	​


and an independent set chosen in S could be combined with one obtained inductively from G−S.

A vertex of degree at most three supplies such a reducible configuration via S=N[v]. Therefore the unresolved case has minimum degree at least four, as in (11).

No unavoidable reducible configuration of bounded size was proved for the class described by (12).

Branch K: Counterexample construction

To disprove the inequality, one needs a realizable unit-distance graph G satisfying

∣V(G)∣>4α(G).
(19)

Disjoint unions preserve the independence ratio:

∣V(G
1
	​

⊔G
2
	​

)∣
α(G
1
	​

⊔G
2
	​

)
	​

=
∣V(G
1
	​

)∣+∣V(G
2
	​

)∣
α(G
1
	​

)+α(G
2
	​

)
	​

.

Hence disjointly repeating a graph whose independence ratio is greater than 1/4 cannot cross below 1/4.

A successful construction therefore requires a finite unit-distance configuration already having independence ratio below 1/4, or a coupling operation that decreases the ratio. No geometrically verified operation with that property was constructed.

Branch L: Strengthening the local axioms

The verified combinatorial shadow of planar unit-distance realizability includes:

K
4
	​

-free,K
2,3
	​

-free,Δ(G[N(v)])≤2.
(20)

A potentially sufficient abstract theorem would be:

Every finite graph satisfying (20) has α(G)≥
4
∣V(G)∣
	​

.
(21)

Attempts to prove (21) by minimum-degree induction reach the same unresolved case δ(G)≥4. The axioms in (20) do not presently yield a bounded average degree or a forced low-degree vertex.

It also remains unverified whether (21) is even true for all abstract graphs satisfying (20). Thus replacing geometric realizability by (20) may have enlarged the class too much.

Shared verified theorem pool

For every finite unit-distance graph G:

ω(G)≤3.

Every pair of vertices has at most two common neighbors.

G is K
2,3
	​

-free.

Every neighborhood induces a graph of maximum degree at most two.

α(G[N(v)])≥d(v)/3.

Every edge belongs to at most two triangles.

If the n/4 assertion fails, there is a vertex-minimal counterexample with

n=4k+1,α(G)=k,δ(G)≥4.

None of these conclusions implies the target through the deductions established here.

Dependency graph
Euclidean circle intersections⟹∣N(x)∩N(y)∣≤2⟹K
2,3
	​

-free and 3t≤2m.
Angular description on C(x,1)⟹Δ(G[N(x)])≤2⟹α(G[N(x)])≥d(x)/3.
Minimal counterexample⟹n=4k+1, α(G)=k⟹δ(G)≥4.

The final node required for a proof,

α(G)≥
4
∣V(G)∣
	​

,

has not been derived from these verified predecessors.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100
The displayed lemmas and reductions have high confidence, but they do not prove or disprove the original assertion.

COMPLETENESS_SCORE: 27/100
Several necessary structural properties and minimal-counterexample conditions were established; the central global independence estimate remains unresolved.

ADVERSARIAL_SURVIVAL_SCORE: 91/100
The accepted claims survived checks for quantifier errors, hidden coloring assumptions, invalid globalization of local bounds, and unjustified geometric implications.

RESOURCE_USAGE:
Approximately 100% of the allocated response budget; 12 principal branches explored; 7 shared verified lemmas recorded; 12 proof or construction approaches failed to close the global gap.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

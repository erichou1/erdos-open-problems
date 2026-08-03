# Erdős Problem #217 [unsolved] 28%

---

## ChatGPT Response

Phase 0: Formalization

Let n∈N. Let

P={p
1
	​

,…,p
n
	​

}⊂R
2

with all p
i
	​

 distinct. Let

E(P)={{p
i
	​

,p
j
	​

}:1≤i<j≤n}

be the edge set of the complete graph on P. For e={x,y}∈E(P), define

δ(e)=∥x−y∥.

We seek all n such that there exists P satisfying:

No three collinear: no distinct a,b,c∈P lie on one line.

No four concyclic: no distinct a,b,c,d∈P lie on one circle.

Exactly n−1 distinct distances:

∣δ(E(P))∣=n−1.

Distance multiplicities are 1,2,…,n−1: there exists an ordering

d
1
	​

,…,d
n−1
	​


of the distinct distances such that

∣δ
−1
(d
i
	​

)∣=i

for every 1≤i≤n−1.

The total number of pairs is

∣E(P)∣=(
2
n
	​

)=
2
n(n−1)
	​

.

The required multiplicities sum to

1+2+⋯+(n−1)=
2
n(n−1)
	​

,

so the multiplicity condition is numerically consistent.

Negation for fixed n: every n-point set P⊂R
2
 with no three collinear and no four concyclic either determines a number of distinct distances different from n−1, or else the multiplicity multiset is not exactly

{1,2,…,n−1}.

Equivalent graph formulation: we need a geometric realization of K
n
	​

 whose edges are colored by their Euclidean lengths, with exactly n−1 color classes of sizes

1,2,…,n−1,

subject to the two geometric general-position constraints.

Small n
n=1

There are no distances. Under the usual vacuous convention, this satisfies the condition with n−1=0 distances.

So n=1 works, if the empty distance condition is allowed.

n=2

Take two distinct points. There is one distance, occurring once. No three collinear and no four concyclic are vacuous.

So n=2 works.

n=3

Take a nondegenerate isosceles triangle that is not equilateral. Its side-length multiplicities are

2,1.

No three points are collinear, and no four points exist.

So n=3 works.

n=4

A direct construction works.

Let O=(0,0), let

C=(1,0),

and choose

A=(cosθ,sinθ),B=(cosθ,−sinθ)

with, for example, θ=2π/5.

Then

OA=OB=OC=1,

so distance 1 occurs 3 times.

Also

AC=BC=2sin(θ/2),

so this distance occurs 2 times.

Finally

AB=2sinθ,

which occurs once.

For θ=2π/5, the three distances

1,2sin(θ/2),2sinθ

are distinct. Thus the multiplicities are

1,2,3.

No three of the four points are collinear: A,B have the same x-coordinate but O and C do not lie on that vertical line, and O,C lie on the x-axis while A,B do not.

No four are concyclic: A,B,C lie on the unit circle, but O is the center of that circle and is not on it. Since three noncollinear points determine a unique circle, no other circle can contain all four.

So n=4 works.

Prompt-supplied existence data

The problem statement itself asserts constructions for

n=5,6,7,8.

Those are existence claims contained in the supplied statement, but no coordinates are given here, so I cannot internally verify those configurations from first principles inside this session.

Thus, from explicit construction inside this response:

n=1,2,3,4

are verified.

From the statement as supplied:

n=5,6,7,8

are asserted to exist.

Structural lemmas
Lemma 1: Same-distance degree bound

Fix a valid set P. For any point p∈P and any distance r>0, at most three other points of P can lie at distance r from p.

Proof. If four distinct points q
1
	​

,q
2
	​

,q
3
	​

,q
4
	​

∈P all satisfy

∥q
i
	​

−p∥=r,

then q
1
	​

,q
2
	​

,q
3
	​

,q
4
	​

 lie on the circle centered at p of radius r. That would give four points of P on one circle, contradicting the no-four-concyclic condition. Therefore the number is at most 3. ∎

Consequence: each graph formed by edges of a fixed distance has maximum degree at most 3.

Lemma 2: A single distance can occur at most 
2
3n
	​

 times

Let G
r
	​

 be the graph on vertex set P whose edges are exactly the pairs at distance r. By Lemma 1, every vertex of G
r
	​

 has degree at most 3. Hence

2∣E(G
r
	​

)∣=
p∈P
∑
	​

deg
G
r
	​

	​

(p)≤3n.

Therefore

∣E(G
r
	​

)∣≤
2
3n
	​

.

This does not obstruct the desired multiplicity n−1, since

n−1≤
2
3n
	​


for all positive n. ∎

Lemma 3: Isosceles triangle count upper bound

For a fixed unordered base {a,b}⊂P, any point x∈P∖{a,b} with

∥x−a∥=∥x−b∥

lies on the perpendicular bisector of segment ab.

Because no three points of P are collinear, at most two points of P can lie on that perpendicular bisector. Therefore each base has at most two possible isosceles apices.

There are (
2
n
	​

) choices of base, so the total number of isosceles triangles in P, counted by base and apex, is at most

2(
2
n
	​

)=n(n−1).

This gives a genuine restriction, but it is too weak by itself to rule out the required multiplicity pattern.

Lemma 4: Forced lower bound on same-distance adjacent pairs

For a distance class containing m edges, let its graph be G. Same-distance adjacent edge pairs correspond to vertices v with at least two incident edges of that distance. The number is

A(G)=
v∈P
∑
	​

(
2
deg
G
	​

(v)
	​

).

Since deg
G
	​

(v)≤3, distributing 2m degree-units among n vertices with capacity 3, the minimum possible value of A(G) is at least

max(0,2m−n).

For the desired multiplicities m=1,2,…,n−1, the total forced number of same-distance adjacent pairs is at least

m=1
∑
n−1
	​

max(0,2m−n)=⌊
4
(n−1)
2
	​

⌋.

But Lemma 3 only gives the upper bound n(n−1), so again no contradiction follows.

Strategy search

I considered the following independent approaches.

Strategy	Aim	Obstacle
Direct construction	Build sets for all n	Exact distance multiplicities are heavily overdetermined
Induction	Add one point to an example for n−1	New point adds n−1 distances with little control
Reverse induction	Remove a point from an example	No guarantee multiplicities reduce correctly
Same-distance graph bounds	Use max degree 3	Bound allows multiplicity n−1
Isosceles counting	Compare forced repeated-distance structures	Current lower bound far below upper bound
Disjoint equal segment counting	Count pairs of equal-length disjoint edges	No strong elementary upper bound found
Perpendicular-bisector method	Repeated distances imply many bisectors	Needs deeper incidence control
Circle obstruction	Use no-four-concyclic strongly	Only gives local radial degree bound immediately
Algebraic dimension counting	Equalities exceed degrees of freedom	Degenerate structured examples evade naive dimension count
Near-collinear perturbation	Perturb equally spaced line points	Exact equalities are destroyed
Near-circular perturbation	Perturb regular polygon points	Exact equalities and no-four-cyclic conflict
Lattice-style construction	Use repeated squared distances	Controlling exact multiplicities remains unresolved

The strongest verified constraints obtained here are Lemmas 1–4. None proves impossibility for n≥9, and none gives a general construction.

Gap node: n≥9

Primary unresolved statement:

∃P⊂R
2
, ∣P∣=n, P valid, with distance multiplicities 1,2,…,n−1?

For n≥9, I did not obtain either:

a construction, or

a contradiction.

The main obstruction is that the obvious local consequences of no-four-concyclic are too weak. A fixed distance graph may have maximum degree 3, but that still permits n−1 equal edges. The required largest multiplicity therefore survives the first counting attack.

The second obstruction is that the repeated-distance condition creates roughly cubic many equal-edge-pair relations, but many of these may be disjoint equal segments. The no-three-collinear and no-four-concyclic hypotheses strongly limit some adjacent configurations, but I did not derive a sufficient global bound on disjoint equal segments.

Verified conclusion

Internally proved:

n=1,2,3,4

work.

Supplied by the problem statement but not coordinate-verified here:

n=5,6,7,8

work.

For n≥9, no proof or disproof was obtained from the permitted first-principles reasoning in this session.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94/100 for the internally verified n≤4 constructions and lemmas.

COMPLETENESS_SCORE: 28/100 for the full classification problem.

ADVERSARIAL_SURVIVAL_SCORE: 82/100 for the stated partial results; no complete classification survived because none was obtained.

RESOURCE_USAGE: about 85% of the available reasoning budget for this response; 12 strategies considered; 4 verified lemmas generated; 3 main proof attempts failed to close the n≥9 gap.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

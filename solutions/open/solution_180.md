# Erdős Problem #180 [candidate-proved] 100%

---

## ChatGPT Response

DISPROVED

Formal statement

Assume finite simple graphs. For a finite graph family F, let

ex(n;F)=max{e(X):∣V(X)∣=n, X contains no subgraph isomorphic to any F∈F}.

The proposed statement is:

∀F ∃G∈F ∃C=C(F)>0 ∃n
0
	​

 ∀n≥n
0
	​

,ex(n;G)≤Cex(n;F).

Its negation is:

∃F ∀G∈F ∀C>0 ∀n
0
	​

 ∃n≥n
0
	​

ex(n;G)>Cex(n;F).

We prove the negation by an explicit finite family.

Counterexample family

Let

H
1
	​

=K
1,2
	​


be the two-edge star, i.e. a path of length 2, and let

H
2
	​

=2K
2
	​


be a matching of two disjoint edges. Set

F={K
1,2
	​

,2K
2
	​

}.

We compute the three relevant extremal functions.

Lemma 1: ex(n;F)=1 for n≥2

A graph is K
1,2
	​

-free iff no vertex has degree at least 2. Therefore every component is either an isolated vertex or a single edge. Thus every K
1,2
	​

-free graph is a matching.

If the graph is also 2K
2
	​

-free, then it cannot contain two disjoint edges. Since it is already a matching, it can contain at most one edge.

Therefore

e(X)≤1

for every F-free graph X.

Conversely, a graph consisting of one edge and n−2 isolated vertices contains neither K
1,2
	​

 nor 2K
2
	​

. Hence, for n≥2,

ex(n;F)=1.
Lemma 2: ex(n;K
1,2
	​

)=⌊n/2⌋

If a graph is K
1,2
	​

-free, then every vertex has degree at most 1, so the graph is a matching. A matching on n vertices has at most

⌊n/2⌋

edges.

This bound is attained by taking a maximum matching. Therefore

ex(n;K
1,2
	​

)=⌊n/2⌋.

In particular,

ex(n;K
1,2
	​

)≍n.
Lemma 3: ex(n;2K
2
	​

)≥n−1

Take the star K
1,n−1
	​

. It has n−1 edges.

Any two edges of a star share the center vertex, so the star contains no two vertex-disjoint edges. Hence it is 2K
2
	​

-free.

Therefore

ex(n;2K
2
	​

)≥n−1.

So

ex(n;2K
2
	​

)≫n.

For the disproof, the lower bound alone is enough.

Failure of the proposed domination

For F={K
1,2
	​

,2K
2
	​

}, we have

ex(n;F)=1

for all n≥2.

But

ex(n;K
1,2
	​

)=⌊n/2⌋

and

ex(n;2K
2
	​

)≥n−1.

Thus for either G∈F,

ex(n;F)
ex(n;G)
	​

→∞as n→∞.

Equivalently, for every constant C>0, choosing n sufficiently large gives

ex(n;G)>Cex(n;F).

Therefore there is no G∈F such that

ex(n;G)≪
F
	​

ex(n;F).

So the proposed statement is false.

Final state

DISPROVED

PROOF_CONFIDENCE: 100
COMPLETENESS_SCORE: 100
ADVERSARIAL_SURVIVAL_SCORE: 100

RESOURCE_USAGE:
Reasoning budget used: low
Branches explored: 1 decisive construction branch
Lemmas generated: 3
Failed proof attempts: 0

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

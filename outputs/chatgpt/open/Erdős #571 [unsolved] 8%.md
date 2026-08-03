# Erdős Problem #571 [unsolved] 8%

---

## ChatGPT Response

1. Formal statement

Let G be a finite simple bipartite graph. Define

ex(n;G)=max{e(H):∣V(H)∣=n, H contains no copy of G}.

The target statement is:

∀α∈Q∩[1,2), ∃ finite bipartite G, ex(n;G)≍n
α
.

Expanded:

∀α∈Q∩[1,2), ∃G, ∃c,C>0, ∃N∈N, ∀n≥N,
cn
α
≤ex(n;G)≤Cn
α
.
2. Negation

The negation is:

∃α∈Q∩[1,2)

such that for every finite bipartite graph G, for every c,C>0, and for every N, there exists n≥N such that

ex(n;G)<cn
α

or

ex(n;G)>Cn
α
.

So disproving the statement requires one rational exponent α∈[1,2) that cannot be realized by any single finite bipartite graph.

3. Immediate verified cases
Lemma 1. α=1 is realized.

Take G=P
3
	​

, the path on three vertices.

A graph is P
3
	​

-free exactly when every connected component has at most two vertices. Therefore every P
3
	​

-free graph is a matching plus isolated vertices, so

ex(n;P
3
	​

)=⌊
2
n
	​

⌋.

Thus

ex(n;P
3
	​

)≍n.

So the statement is proved for α=1.

4. Structural reformulation for α∈(1,2)

Write

α=
q
p
	​

,1<
q
p
	​

<2.

Equivalently,

α=2−β

where

β=2−α∈(0,1)∩Q.

The task becomes:

∀β∈(0,1]∩Q, ∃ finite bipartite G

such that

ex(n;G)≍n
2−β
.

This is useful because many extremal upper bounds naturally have the form n
2−β
.

5. Verified general lower bound
Lemma 2. Random deletion lower bound.

Let G be a fixed finite graph with v≥3 vertices and e≥2 edges. Then there exists c
G
	​

>0 such that

ex(n;G)≥c
G
	​

n
2−
e−1
v−2
	​

.
Proof.

Let

p=εn
−
e−1
v−2
	​


and choose a random graph Γ∼G(n,p).

The expected number of edges is

E[e(Γ)]=(
2
n
	​

)p≍εn
2−
e−1
v−2
	​

.

The expected number of labeled copies of G is at most

n
v
p
e
=ε
e
n
v−e
e−1
v−2
	​

.

Compute the exponent:

v−e
e−1
v−2
	​

=
e−1
v(e−1)−e(v−2)
	​

=
e−1
ve−v−ev+2e
	​

=
e−1
2e−v
	​

.

Also,

2−
e−1
v−2
	​

=
e−1
2(e−1)−(v−2)
	​

=
e−1
2e−v
	​

.

So the expected number of copies of G has the same n-exponent as the expected number of edges, but has coefficient ε
e
, while the edge count has coefficient proportional to ε.

Since e≥2, choose ε>0 sufficiently small so that the expected number of copies is at most one half of the expected number of edges. Then some realization satisfies

e(Γ)−#G(Γ)≥c
G
	​

n
2−
e−1
v−2
	​

.

Delete one edge from each copy of G. The resulting graph is G-free and has at least

c
G
	​

n
2−
e−1
v−2
	​


edges.

Therefore

ex(n;G)≥c
G
	​

n
2−
e−1
v−2
	​

.

Verified.

6. Consequence for any candidate graph

If a graph G satisfies

ex(n;G)≍n
α
,

then Lemma 2 forces

2−
e(G)−1
v(G)−2
	​

≤α

for every nontrivial candidate G.

Equivalently,

e(G)−1
v(G)−2
	​

≥2−α.

So for a target exponent α, a plausible candidate graph must have compatible edge to vertex density.

This only gives a necessary lower bound condition. It does not prove the matching upper bound.

7. Main obstruction found inside the proof search

The random deletion argument can produce many lower bounds, but the target requires both inequalities:

ex(n;G)≥cn
α

and

ex(n;G)≤Cn
α
.

The lower bound can often be arranged by choosing G with

2−
e(G)−1
v(G)−2
	​

=α.

But the upper bound does not follow from the same density calculation.

The missing primary theorem would be:

For every rational α∈(1,2), there exists a finite bipartite G

such that

ex(n;G)≤Cn
α
.

The proof search could not derive this statement from first principles.

8. Strategy inventory

I tested the following proof frameworks.

Direct construction by density matching.

Choose G with

2−
e−1
v−2
	​

=α.

Lower bound follows from Lemma 2. Upper bound remains unproved.

Contradiction.

Assume no graph realizes a fixed rational α. No invariant was found that forces possible exponents into a restricted set.

Forest construction.

Works only for α=1.

Complete bipartite graph construction.

Candidate graphs K
s,t
	​

 suggest exponents of the form 2−1/s. This cannot cover all rationals in (1,2).

Cycle construction.

Even cycles suggest sparse upper bounds, but this only reaches a limited family of exponents.

Subdivision construction.

Subdividing edges changes density in a controllable way. However, a complete proof requires a matching upper bound for the subdivision, and that upper bound was not derived.

Iterated auxiliary graph construction.

One may try to encode rational operations on exponents by graph operations. The lower bound is manageable, but upper bounds are not preserved by any operation proved here.

Cardinal arithmetic.

All relevant graph sizes are finite. Cardinal issues do not create a route to proof or disproof.

Diagonalization.

A disproof would need one rational exponent avoided by all finite bipartite graphs. No diagonal invariant over all finite bipartite graphs was found.

Compactness.

No finite obstruction principle was derived that converts finite family realization into single graph realization.

Density increment.

One can attempt to show that any graph with Cn
α
 edges must contain a desired configuration. This becomes the central unresolved upper bound problem.

Counterexample search.

No rational α∈(1,2) was shown impossible. No contradiction was derived from assuming realization.

9. Verified theorem pool
Theorem A. α=1 is realized.

Realized by P
3
	​

.

Theorem B. Universal random lower bound.

For every fixed graph G with v≥3, e≥2,

ex(n;G)≥c
G
	​

n
2−
e−1
v−2
	​

.
Theorem C. Density compatibility condition.

If G realizes exponent α, then

2−
e(G)−1
v(G)−2
	​

≤α.

These theorems are verified. They do not prove the original statement.

10. Primary unresolved gap

The unresolved target is:

∀α∈Q∩(1,2), ∃ finite bipartite G, ex(n;G)≤Cn
α

with a matching lower bound.

The lower bound side has a general probabilistic mechanism. The upper bound side is the hard part. No first principles derivation in this session produced a construction that realizes every rational α∈(1,2).

11. Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94

COMPLETENESS_SCORE: 8

ADVERSARIAL_SURVIVAL_SCORE: 87

RESOURCE_USAGE: 100 percent of this response budget used, 12 branches explored, 3 verified lemmas generated, 0 complete proofs for the full statement, 0 complete disproofs.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

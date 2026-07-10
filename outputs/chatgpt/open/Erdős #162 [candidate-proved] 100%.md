# Erdős Problem #162 [candidate-proved] 100%

---

## ChatGPT Response

Formal statement

For a finite family F of finite graphs, define

ex(n;F)=max{∣E(H)∣: ∣V(H)∣=n, H contains no member of F as a subgraph}.

The proposed statement is:

∀F ∃G∈F ∃C
F
	​

>0 ∃n
0
	​

 ∀n≥n
0
	​

,ex(n;G)≤C
F
	​

ex(n;F).

Its negation is:

∃F ∀G∈F ∀C>0 ∀n
0
	​

 ∃n≥n
0
	​

ex(n;G)>Cex(n;F).

I will prove the negation by an explicit finite family.

Counterexample

Let

F={K
1,2
	​

,2K
2
	​

},

where K
1,2
	​

 is a path of length 2, equivalently a star with two edges, and 2K
2
	​

 is a matching of two disjoint edges.

Both graphs are finite, and F is finite.

Step 1: Compute ex(n;F)

A graph contains no K
1,2
	​

 iff every vertex has degree at most 1. Therefore a K
1,2
	​

-free graph is a matching.

If such a graph also avoids 2K
2
	​

, then it cannot contain two disjoint edges. But every two distinct edges in a matching are disjoint. Hence the graph has at most one edge.

Thus for every n≥2,

ex(n;F)=1.

The lower bound is achieved by a graph with exactly one edge and n−2 isolated vertices. The upper bound follows from the previous paragraph.

Step 2: Compute ex(n;K
1,2
	​

)

A graph is K
1,2
	​

-free iff its maximum degree is at most 1. Hence every component is either an isolated vertex or a single edge. Therefore the graph is a matching, so it has at most

⌊
2
n
	​

⌋

edges.

This bound is achieved by a maximum matching. Therefore

ex(n;K
1,2
	​

)=⌊
2
n
	​

⌋.

In particular,

ex(n;K
1,2
	​

)≍n.

Since ex(n;F)=1, we have

ex(n;F)
ex(n;K
1,2
	​

)
	​

=⌊
2
n
	​

⌋→∞.

So

ex(n;K
1,2
	​

)

≪
F
	​

ex(n;F).
Step 3: Lower-bound ex(n;2K
2
	​

)

Consider the star K
1,n−1
	​

. It has n−1 edges, and every pair of edges shares the center vertex. Therefore it contains no two disjoint edges, so it is 2K
2
	​

-free.

Thus

ex(n;2K
2
	​

)≥n−1.

Since again ex(n;F)=1, we get

ex(n;F)
ex(n;2K
2
	​

)
	​

≥n−1→∞.

Therefore

ex(n;2K
2
	​

)

≪
F
	​

ex(n;F).
Conclusion

For the finite family

F={K
1,2
	​

,2K
2
	​

},

we have

ex(n;F)=1,

but for both members G∈F,

ex(n;G)≫n.

Hence there is no G∈F such that

ex(n;G)≪
F
	​

ex(n;F).

So the proposed statement is false.

DISPROVED
	​


PROOF_CONFIDENCE: 100
COMPLETENESS_SCORE: 100
ADVERSARIAL_SURVIVAL_SCORE: 100
RESOURCE_USAGE: small fraction of budget used; 1 branch explored; 3 lemmas generated; 0 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

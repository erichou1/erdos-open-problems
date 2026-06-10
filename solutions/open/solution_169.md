# Erdős Problem #169 [solved] 100%

---

## ChatGPT Response

DISPROVED

Formal statement

Let ex(n;F) be the maximum number of edges in an n-vertex simple graph containing no member of F as a subgraph.

The proposed universal statement is:

∀ finite families F, ∃G∈F, ∃C
F
	​

>0, ∀n≫1,ex(n;G)≤C
F
	​

ex(n;F).

Its negation is:

∃F finite, ∀G∈F, ∀C>0, ∀N, ∃n≥N

such that

ex(n;G)>Cex(n;F).

We prove the negation by explicit construction.

Counterexample

Let

H
1
	​

=K
1,2
	​


be the star with two edges, and let

H
2
	​

=2K
2
	​


be the matching with two disjoint edges. Set

F={K
1,2
	​

,2K
2
	​

}.

This is a finite family of finite graphs.

Step 1: Compute ex(n;F)

Let X be an n-vertex graph avoiding both K
1,2
	​

 and 2K
2
	​

.

Suppose X has two distinct edges e
1
	​

,e
2
	​

.

There are only two possibilities:

e
1
	​

,e
2
	​

 share a vertex.
Then they form a copy of K
1,2
	​

.

e
1
	​

,e
2
	​

 are disjoint.
Then they form a copy of 2K
2
	​

.

Both cases are forbidden. Therefore X has at most one edge.

Conversely, any graph with exactly one edge contains neither K
1,2
	​

 nor 2K
2
	​

. Hence for n≥2,

ex(n;F)=1.
Step 2: Compute ex(n;K
1,2
	​

)

A graph contains no K
1,2
	​

 iff no two edges share a vertex. Therefore every K
1,2
	​

-free graph is a matching.

A matching on n vertices has at most

⌊
2
n
	​

⌋

edges, and such a matching exists. Hence

ex(n;K
1,2
	​

)=⌊
2
n
	​

⌋.

Thus

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

. It has n−1 edges.

Every two edges of K
1,n−1
	​

 share the center vertex, so it contains no two disjoint edges. Hence it is 2K
2
	​

-free.

Therefore

ex(n;2K
2
	​

)≥n−1.

Since ex(n;F)=1, we get

ex(n;F)
ex(n;2K
2
	​

)
	​

≥n−1→∞.

So

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

ex(n;G)→∞

at least linearly in n. Therefore there is no G∈F such that

ex(n;G)≪
F
	​

ex(n;F).

Thus the proposed statement is false.

DISPROVED

PROOF_CONFIDENCE: 100
COMPLETENESS_SCORE: 100
ADVERSARIAL_SURVIVAL_SCORE: 100
RESOURCE_USAGE: approximately 20%; 1 branch explored; 3 lemmas generated; 0 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #620 [unsolved] 35%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Direct answer: from the stated results, every K
4
	​

-free graph on n vertices must contain an induced triangle-free subgraph of size

n
1/2+o(1)
.

More sharply, the stated best known bounds are

n
1/2
loglogn
(logn)
1/2
	​

≪f(n)≪n
1/2
logn.

A fully self-contained proof of those logarithmic bounds was not obtained here.

Verified first-principles lower bound:

Let G be K
4
	​

-free on n vertices.

If some vertex v has degree at least 
n
	​

, then N(v) is triangle-free.
Reason: if N(v) contained a triangle abc, then v,a,b,c would form a K
4
	​

.
So G[N(v)] is an induced triangle-free subgraph of size at least 
n
	​

.

If every vertex has degree less than 
n
	​

, then G has an independent set of size at least

Δ+1
n
	​

>
n
	​

+1
n
	​

.

An independent set is automatically an induced triangle-free subgraph.

Therefore, in all cases,

f(n)≥
n
	​

+1
n
	​

=
n
	​

−o(
n
	​

).

This rigorously proves the elementary baseline

f(n)≫n
1/2
.

PROOF_CONFIDENCE: 95
COMPLETENESS_SCORE: 35
ADVERSARIAL_SURVIVAL_SCORE: 90
RESOURCE_USAGE: 100 percent, 2 branches explored, 2 lemmas generated, 1 failed attempt to derive the sharper logarithmic bounds from first principles.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

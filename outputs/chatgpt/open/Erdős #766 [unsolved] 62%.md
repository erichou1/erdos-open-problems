# Erdős Problem #766 [unsolved] 62%

---

## ChatGPT Response

Formal statement.

For fixed integers k,l with k<l≤k
2
/4,

f(n;k,l)=
∣V(G)∣=k, ∣E(G)∣=l
min
	​

ex(n,G).

Verified estimate:

c
k,l
	​

n
2−
l−1
k−2
	​

≤f(n;k,l)≤C
k,l
	​

n
2−
a(k,l)
1
	​

,

where

a(k,l)=min{a:1≤a≤k/2, a(k−a)≥l}.

Also verified:

f(n;k,l)≤f(n;k,l+1).

So f is nondecreasing in l. I did not prove strict monotonicity.

Reasoning.

Lower bound.
For any fixed k-vertex l-edge graph G, take a random graph on n vertices with edge probability

p=n
−
l−1
k−2
	​

.

Expected edges are Θ(n
2
p). Expected copies of G are O(n
k
p
l
). With this choice,

n
2
p=n
k
p
l
=n
2−
l−1
k−2
	​

.

Deleting one edge from every copy of G leaves a G-free graph with at least

c
k,l
	​

n
2−
l−1
k−2
	​


edges for some constant c
k,l
	​

>0. Since this holds for every G,

f(n;k,l)≥c
k,l
	​

n
2−
l−1
k−2
	​

.

Upper bound.
Choose a=a(k,l), b=k−a, so ab≥l. Pick any l-edge subgraph G⊆K
a,b
	​

, then add isolated vertices if needed so that G has exactly k vertices.

If an n-vertex graph contains K
a,b
	​

, then it contains G. Therefore

ex(n,G)≤ex(n,K
a,b
	​

).

By the standard counting proof for complete bipartite graphs,

ex(n,K
a,b
	​

)≤C
a,b
	​

n
2−1/a
.

Hence

f(n;k,l)≤C
k,l
	​

n
2−
a(k,l)
1
	​

.

Monotonicity.
Let G be any k-vertex graph with l+1 edges. Remove one edge to get a k-vertex graph H with l edges.

Every H-free graph is automatically G-free, so

ex(n,H)≤ex(n,G).

Taking the minimum over all G with l+1 edges gives

f(n;k,l)≤f(n;k,l+1).

Thus f is nondecreasing.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 88
COMPLETENESS_SCORE: 62
ADVERSARIAL_SURVIVAL_SCORE: 75
RESOURCE_USAGE: 85 percent, 3 branches explored, 4 lemmas generated, 1 unresolved strict monotonicity gap.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

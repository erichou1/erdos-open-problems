# Erdős Problem #584 [candidate-proved] 100%

---

## ChatGPT Response

Formalization

Let G be a finite simple undirected graph on n vertices with

e(G)=δn
2
.

Interpret A≫B as: there is an absolute constant c>0 such that A≥cB for all relevant n,δ,G.

The second requested conclusion is:

∃c
2
	​

>0 ∀G ∃H
2
	​

⊆G

such that

e(H
2
	​

)≥c
2
	​

δ
2
n
2

and every two edges of H
2
	​

 lie together on a cycle of length at most 8.

To disprove the full statement, it is enough to disprove this second assertion.

The negation is:

For every c
2
	​

>0, there exist arbitrarily large n and graphs G with e(G)=δn
2
 such that every subgraph H
2
	​

⊆G satisfying the cycle condition has

e(H
2
	​

)<c
2
	​

δ
2
n
2
.

I will prove a stronger statement: there are graphs G with no cycle of length at most 8, but with

δ
2
n
2
→∞.

Then any valid H
2
	​

 has at most one edge, while the required lower bound tends to infinity.

Key construction

For arbitrarily large n, there exists a graph G on n vertices with

e(G)≥βn
9/8

for some absolute β>0, and with no cycle of length at most 8.

Proof

Let R∼G(n,p) with

p=an
−7/8
,

where a>0 is a fixed small absolute constant.

Let X be the number of edges in R. Then

EX=(
2
n
	​

)p≥
4
a
	​

n
9/8

for all sufficiently large n.

Let Y be the number of cycles in R of length 3,4,5,6,7,8. For a fixed ℓ, the number of ℓ cycles in the complete graph on n vertices is at most

2ℓ
n
ℓ
	​

.

Each appears in R with probability p
ℓ
. Hence

EY≤
ℓ=3
∑
8
	​

2ℓ
n
ℓ
p
ℓ
	​

=
ℓ=3
∑
8
	​

2ℓ
a
ℓ
n
ℓ/8
	​

≤C
a
	​

n,

where C
a
	​

 depends only on a.

Since n=o(n
9/8
),

E(X−Y)≥
8
a
	​

n
9/8

for sufficiently large n.

Therefore there is an outcome of R such that

X−Y≥
8
a
	​

n
9/8
.

From this graph, delete one edge from every cycle of length at most 8. At most Y edges are deleted. The remaining graph G satisfies

e(G)≥X−Y≥
8
a
	​

n
9/8
.

Also, G has no cycle of length at most 8, because every such cycle in the original graph lost at least one edge, and deleting edges cannot create new cycles.

Set

β=
8
a
	​

.

Thus

e(G)≥βn
9/8
.
Disproof of the H
2
	​

 conclusion

For this graph G, define

δ=
n
2
e(G)
	​

.

Then

δ
2
n
2
=(
n
2
e(G)
	​

)
2
n
2
=
n
2
e(G)
2
	​

.

Using e(G)≥βn
9/8
,

δ
2
n
2
≥
n
2
β
2
n
9/4
	​

=β
2
n
1/4
.

So

δ
2
n
2
→∞.

Now let H
2
	​

⊆G satisfy the condition that every two edges of H
2
	​

 lie together on a cycle of length at most 8.

If H
2
	​

 had two distinct edges e,f, then by the condition, e and f would lie on a cycle of length at most 8. Since H
2
	​

⊆G, that cycle would also be a cycle in G. But G has no cycle of length at most 8. Contradiction.

Therefore

e(H
2
	​

)≤1.

But for any fixed c
2
	​

>0,

c
2
	​

δ
2
n
2
≥c
2
	​

β
2
n
1/4
→∞.

So for all sufficiently large n,

1<c
2
	​

δ
2
n
2
.

Thus no such H
2
	​

 can satisfy

e(H
2
	​

)≥c
2
	​

δ
2
n
2
.

Therefore the stated universal claim is false.

Sanity check

The construction uses only elementary counting and expectation.

The key quantifier issue is that δ is not fixed independently. It is defined by the graph through e(G)=δn
2
. The constructed graphs have

δ≥βn
−7/8
.

The contradiction applies to the unqualified statement allowing such δ. It does not address a modified statement with an added lower bound on δ, such as δ≥n
−c
 for smaller specified c.

Final state

DISPROVED

PROOF_CONFIDENCE: 97

COMPLETENESS_SCORE: 100 for the literal universal formulation

ADVERSARIAL_SURVIVAL_SCORE: 95

RESOURCE_USAGE: about 35 percent, 1 decisive counterexample branch explored, 2 lemmas generated, 0 failed proof attempts needed

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #579 [unsolved] 28%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

I did not obtain a complete proof or disproof of the stated theorem. I did obtain several verified reductions and partial consequences, but none close the linear independent set gap.

1. Formal statement

For every real δ>0, there should exist constants c(δ)>0 and n
0
	​

(δ) such that for every integer n≥n
0
	​

(δ), every graph G=(V,E) with

∣V∣=n,e(G)≥δn
2
,K
2,2,2
	​

⊈G

satisfies

α(G)≥c(δ)n.

Here K
2,2,2
	​

 means three disjoint vertex pairs A,B,C, each of size 2, such that every edge between distinct pairs is present.

2. Quantifier structure

The statement is

∀δ>0 ∃c>0 ∃n
0
	​

 ∀n≥n
0
	​

 ∀G,

if

∣V(G)∣=n,e(G)≥δn
2
,K
2,2,2
	​

⊈G,

then

α(G)≥cn.

The important dependence is that c may depend on δ, but not on n or G.

3. Negation

The negation is:

There exists some δ>0 such that for every c>0 and every n
0
	​

, there exists n≥n
0
	​

 and a graph G
n
	​

 on n vertices with

e(G
n
	​

)≥δn
2
,K
2,2,2
	​

⊈G
n
	​

,α(G
n
	​

)<cn.

Equivalently, there is a sequence G
n
	​

 with

e(G
n
	​

)≥δn
2
,K
2,2,2
	​

⊈G
n
	​

,α(G
n
	​

)=o(n).
4. Equivalent useful formulation

For a vertex pair P={x,y}, define

N(P)=N(x)∩N(y).

If G has no K
2,2,2
	​

, then for every pair P, the induced graph

G[N(P)]

has no K
2,2
	​

.

Reason: if G[N(P)] contained two disjoint pairs Q,R with all four edges between them, then P,Q,R would form a K
2,2,2
	​

.

So every common neighborhood of a vertex pair is K
2,2
	​

 free.

5. Verified partial consequence

Since

{x,y}⊆V
∑
	​

∣N(x)∩N(y)∣=
v∈V
∑
	​

(
2
d(v)
	​

),

and

n
1
	​

v
∑
	​

d(v)=
n
2e(G)
	​

≥2δn,

convexity gives

v
∑
	​

(
2
d(v)
	​

)≥n(
2
2δn
	​

)

up to lower order integer effects. Therefore some pair P has

∣N(P)∣≫
δ
	​

n.

Let

S=N(P).

Then G[S] has no K
2,2
	​

. By the standard K
2,2
	​

 extremal estimate,

e(G[S])≪∣S∣
3/2
.

This implies

α(G[S])≫∣S∣
1/2
≫
δ
	​

n
1/2
.

So the first principles route proves only

α(G)≫
δ
	​

n
1/2
,

not the required

α(G)≫
δ
	​

n.

This is a real gap, not a cosmetic one.

6. Why the main gap is hard

The obstruction is quantitative.

A large common neighborhood S is forced, and G[S] has no K
2,2
	​

. But graphs with no K
2,2
	​

 can still have far smaller than linear independence number. The usual edge bound gives only a square root scale independent set.

Thus the direct common neighborhood argument cannot prove the theorem unless one adds a new idea using the global density of G, not just the internal structure of one common neighborhood.

7. Independent strategies tested

Direct common neighborhood method
Result: proves α(G)≫
δ
	​

n
1/2
. Gap: not linear.

Auxiliary pair graph
Define a graph whose vertices are unordered pairs of V(G), with two pair vertices adjacent when they form a K
2,2
	​

 in G. A K
2,2,2
	​

 in G becomes a triangle in this auxiliary graph. The auxiliary graph is triangle free and dense. Gap: a large independent set in the auxiliary graph does not directly yield a large independent set in G.

Regularity reduction
A triangle in the reduced graph would embed K
2,2,2
	​

. Hence the reduced graph is triangle free. Gap: an independent set in the reduced graph gives a large vertex union with low regular pair density, but low fixed density does not force a linear independent set.

Density increment
One can find large subsets with special sparse structure. Gap: fixed sparse density still allows sublinear independence.

Contradiction from α(G)=o(n)
Small independence forces every linear subset to contain edges. Gap: it does not force enough edges inside the K
2,2
	​

 free common neighborhoods to contradict their extremal bound.

Iterative common neighborhood descent
Repeatedly passing to common neighborhoods gives stronger forbidden bipartite structures. Gap: the vertex set shrinks and the independence lower bound remains sublinear.

Graphon limit
A dense limit graphon with no K
2,2,2
	​

 appears to contain a positive measure independent set. Gap: transferring that back to finite graphs only gives a subset with o(n
2
) edges, which still does not guarantee a linear independent set.

Blowup counterexample search
Simple blowups of triangle free base graphs preserve density but have linear independent sets. Adding internal edges tends to create K
2,2,2
	​

. No counterexample was verified.

Lexicographic product search
Iterated constructions can force small independence in many forbidden subgraph problems. Gap: the natural candidates create K
2,2,2
	​

.

Maximum cut strategy
A dense graph has a large bipartite subgraph, but adding edges inside both sides tends to create K
2,2,2
	​

. Gap: this gives structural pressure but not a proof.

Counting K
2,2
	​

 configurations
Dense graphs contain many K
2,2
	​

 shaped pair interactions. Gap: the triangle free auxiliary graph can absorb many such interactions without immediately producing a vertex independent set.

Edge deletion inside sparse subsets
Large nearly independent subsets arise in limiting arguments. Gap: deleting one endpoint per edge may delete too many vertices when the subset has o(n
2
), but still superlinear, many edges.

8. Primary unresolved gap

The central unresolved statement is:

Given a dense graph G with no K
2,2,2
	​

, prove that the many large K
2,2
	​

 free common neighborhoods cannot all have sublinear independence while G itself remains quadratically dense.

This is exactly where every tested strategy stalled.

9. Final status

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92
COMPLETENESS_SCORE: 28
ADVERSARIAL_SURVIVAL_SCORE: 85

RESOURCE_USAGE:
Reasoning budget used: high
Branches explored: 12
Verified lemmas generated: 3
Failed proof attempts: 9

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

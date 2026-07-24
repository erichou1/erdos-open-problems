# Erdős Problem #1033 [unsolved] 45%

---

## ChatGPT Response

Formalization

For an n-vertex graph G, define

σ
G
	​

(T):=
v∈V(T)
∑
	​

d
G
	​

(v)

for each triangle T⊆G. The extremal quantity is

h(n):=
∣V(G)∣=n
e(G)>
4
n
2
	​

	​

min
	​

 
T⊆G
T≅K
3
	​

	​

max
	​

σ
G
	​

(T).

Thus the proposed assertion is

∀ε>0 ∃n
0
	​

 ∀n≥n
0
	​

 ∀G:e(G)>
4
n
2
	​

⟹∃T≅K
3
	​

 with σ
G
	​

(T)≥(2(
3
	​

−1)−ε)n.

Its negation is

∃ε>0 ∃
∞
n ∃G
n
	​

:e(G
n
	​

)>
4
n
2
	​

,σ
G
n
	​

	​

(T)<(2(
3
	​

−1)−ε)n

for every triangle T⊆G
n
	​

.

The coefficient in question is

2(
3
	​

−1)=1.4641016….
Verified upper construction

Let

m=⌊
4
n
2
	​

⌋+1,k=⌊cn⌋,ℓ=n−k,

where 1/3<c<1. Begin with the complete bipartite graph K
k,ℓ
	​

, with parts A,B, where ∣A∣=k and ∣B∣=ℓ.

Put

q=m−kℓ.

Since

kℓ=c(1−c)n
2
+O(n),

we have

q=(
4
1
	​

−c(1−c))n
2
+O(n)=(c−
2
1
	​

)
2
n
2
+O(n).

For 1/3<c<1,

(c−
2
1
	​

)
2
≤
4
c
2
	​

,

because this is equivalent to

3c
2
−4c+1≤0,

whose roots are 1/3 and 1. Hence, for sufficiently large n,

q≤
4
k
2
	​

+O(n).

One may therefore place q edges inside A in a bipartite graph H satisfying

Δ(H)≤
k
2q
	​

+O(1).

For example, split A into two parts whose sizes differ by at most one and distribute the q edges as evenly as possible among their vertices.

Let G be the resulting graph. It has exactly m>n
2
/4 edges.

Because B is independent and H is triangle-free, every triangle of G consists of an edge xy∈E(H) and one vertex z∈B. Its degree sum is

d
G
	​

(x)+d
G
	​

(y)+d
G
	​

(z)=(ℓ+d
H
	​

(x))+(ℓ+d
H
	​

(y))+k.

Consequently,

σ
G
	​

(xyz)
	​

≤k+2ℓ+2Δ(H)
≤k+2ℓ+
k
4q
	​

+O(1).
	​


Using k=cn+O(1), ℓ=(1−c)n+O(1), and

q=(c−
2
1
	​

)
2
n
2
+O(n),

we obtain

σ
G
	​

(xyz)
	​

≤[c+2(1−c)+
c
4(c−
2
1
	​

)
2
	​

]n+O(1)
=[2−c+4c−4+
c
1
	​

]n+O(1)
=(3c−2+
c
1
	​

)n+O(1).
	​


The function

f(c)=3c−2+
c
1
	​


satisfies

f
′
(c)=3−
c
2
1
	​

,f
′′
(c)=
c
3
2
	​

>0.

Its unique minimum occurs at

c=
3
	​

1
	​

,

and

f(
3
	​

1
	​

)=
3
	​

−2+
3
	​

=2(
3
	​

−1).

Therefore

h(n)≤2(
3
	​

−1)n+O(1)
	​

.

This calculation is complete and also shows that no universal lower bound with a strictly larger leading coefficient can hold.

Lower-bound issue

To answer the question affirmatively one would need to prove

h(n)≥2(
3
	​

−1)n−o(n).

Equivalently, one must exclude, for every fixed ε>0, all sufficiently large graphs satisfying

e(G)>
4
n
2
	​


and

d(x)+d(y)+d(z)<(2(
3
	​

−1)−ε)n

for every triangle xyz.

The upper construction does not provide this exclusion. The supplied lower estimate

h(n)≥
16
21
	​

n

also does not imply it, since

16
21
	​

=1.3125<1.4641016…=2(
3
	​

−1).

Thus the information in the statement rigorously yields only

16
21
	​

n≤h(n)≤2(
3
	​

−1)n+O(1),

and contains no proof or disproof of the requested matching asymptotic lower bound. I did not derive such a lower bound from first principles within the available reasoning budget.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 99
COMPLETENESS_SCORE: 45
ADVERSARIAL_SURVIVAL_SCORE: 96

RESOURCE_USAGE: Approximately 100% of the allocated response budget; 3 principal approaches examined; 4 auxiliary lemmas used; the upper-bound construction was completed, while the matching lower-bound direction remained unproved.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

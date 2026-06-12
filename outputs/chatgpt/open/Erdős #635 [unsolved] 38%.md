# Erdős Problem #635 [unsolved] 38%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92
COMPLETENESS_SCORE: 38
ADVERSARIAL_SURVIVAL_SCORE: 85
RESOURCE_USAGE: about 95 percent, 3 main branches explored, 6 lemmas generated, 4 failed proof attempts.

Formalization

Let G
N,t
	​

 be the graph on vertices {1,…,N}, with an edge {a,b}, a<b, exactly when

b−a≥tandb−a∣b.

Then the condition on A says exactly that A is an independent set in G
N,t
	​

.

Writing d=b−a, the divisibility condition gives

b=md,a=(m−1)d

for some integer m≥2. Therefore forbidden pairs are precisely consecutive positive multiples of some d≥t:

{(m−1)d,md}.

So the target statement is

α(G
N,t
	​

)≤(
2
1
	​

+o
t
	​

(1))N.

Equivalently, every subset of {1,…,N} with density >1/2+ε must contain two consecutive multiples of some d≥t.

Negation

The proposed bound fails for some fixed t iff there exists ε>0 and arbitrarily large N with an independent set A⊆[N] satisfying

∣A∣≥(
2
1
	​

+ε)N.
Verified observations
Lemma 1: Forbidden pairs are consecutive multiples

For a<b, the pair (a,b) is forbidden iff there are integers d≥t and m≥2 such that

a=(m−1)d,b=md.

Proof: set d=b−a. Then d∣b, so b=md. Since a=b−d=(m−1)d, the result follows.

Lemma 2: Large primes are isolated

If p>N/2 is prime and t≥2, then p has no incident edge in G
N,t
	​

.

Proof: if p is the larger endpoint, then d∣p, so d=1 or d=p. The case d=1 is excluded by t≥2, and d=p gives smaller endpoint 0. If p is the smaller endpoint, then p+d≤N, so d<N/2<p. Since d∣p+d and d∣p+d−p=d, this gives no contradiction directly, but the edge form requires p=(m−1)d, so d∣p, again forcing d=1 or p. Both are impossible. Thus p is isolated.

This shows an exact perfect matching proof cannot work, since there are already o(N) isolated vertices.

Lemma 3: The problem reduces to finding an almost perfect matching

If G
N,t
	​

 has a matching covering N−o
t
	​

(N) vertices, then every independent set has size at most

2
1
	​

N+o
t
	​

(N).

Proof: each matched edge contributes at most one vertex to an independent set. Unmatched vertices contribute at most one each.

This route is valid, but I did not complete the construction of such a matching.

Strategy search summary

The most promising formulation is:

Find a matching in G
N,t
	​

 covering all but o
t
	​

(N) vertices.

Several partial structures work but do not close the proof.

Branch A: Doubling edges

Edges of the form

(n,2n)

exist whenever n≥t. This gives disjoint chains

m,2m,4m,8m,…

for odd m. But these chains alone permit independent sets with density larger than 1/2, so doubling edges are insufficient.

Branch B: Divisor charging

If b∈A and d∣b, t≤d<b, then b−d∈
/
A. Thus selected composite numbers force missing earlier numbers. The issue is multiplicity: many selected b's can charge the same missing number. I did not obtain a uniform enough bound to prove only o(N) excess over N/2.

Branch C: Averaging over divisor paths

For each d≥t, the multiples

d,2d,3d,…,⌊
d
N
	​

⌋d

form a path, so A contains at most half of them, up to rounding. Summing over d≤L gives

n≤N
∑
	​

1
A
	​

(n)r
L
	​

(n)≤
2
1
	​

n≤N
∑
	​

r
L
	​

(n)+O(L),

where

r
L
	​

(n)=∣{d:d∣n, t≤d≤L}∣.

This is rigorous, but it is weighted. To convert it into

∣A∣≤
2
1
	​

N+o(N),

one needs a divisor weight system that behaves like 1 for almost all n. I did not prove such a system from first principles within the session.

Final status

I did not obtain a complete proof or disproof from first principles. The cleanest verified route is the almost perfect matching approach, but the construction of a matching covering all but o
t
	​

(N) vertices remains the unresolved gap.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

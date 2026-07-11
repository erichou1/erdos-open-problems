# Erdős Problem #620 [solved] 75%

---

## ChatGPT Response

Formalization

For a finite simple graph G, define

τ
3
	​

(G):=max{∣S∣:S⊆V(G),G[S] is triangle-free}.

The Erdős–Rogers function in this case is

f(n):=
∣V(G)∣=n
K
4
	​

⊈G
	​

min
	​

τ
3
	​

(G).

Thus f(n) is the largest integer m such that

∀G(∣V(G)∣=n and K
4
	​

⊈G)∃S⊆V(G)

with

∣S∣≥mandK
3
	​

⊈G[S].

The negation of f(n)≥m is that there exists a K
4
	​

-free n-vertex graph for which every set of at least m vertices induces a triangle.

Answer

The bounds supplied in the problem statement are

n
1/2
loglogn
(logn)
1/2
	​

≪f(n)≪n
1/2
logn.

Consequently,

f(n)=n
1/2+o(1)
	​

.

In explicit terms, every K
4
	​

-free graph on n vertices contains an induced triangle-free subgraph of order at least

c
loglogn
nlogn
	​

	​


for some absolute c>0 and all sufficiently large n. Conversely, there exist K
4
	​

-free graphs in which every induced triangle-free subgraph has at most

C
n
	​

logn

vertices for some absolute C>0. Thus the correct polynomial exponent is 1/2, although the logarithmic factor is not determined by these two bounds. 

Pasted text

Indeed, taking logarithms gives

logn
logf(n)
	​

≥
2
1
	​

+
logn
2
1
	​

loglogn−logloglogn+O(1)
	​


and

logn
logf(n)
	​

≤
2
1
	​

+
logn
loglogn+O(1)
	​

.

Both error terms tend to 0, so

n→∞
lim
	​

logn
logf(n)
	​

=
2
1
	​

.
A fully elementary lower bound

Without using either of the deeper logarithmic estimates, one can prove the following precise bound directly:

f(n)≥⌈
2
4n+1
	​

−1
	​

⌉
	​

.

In particular, f(n)≥
n
	​

−O(1).

Proof

Let G be any K
4
	​

-free graph on n vertices, and let

Δ=Δ(G)

be its maximum degree.

Choose a vertex v with d(v)=Δ. Its neighborhood N(v) induces a triangle-free graph. Otherwise, if a,b,c∈N(v) formed a triangle, then the four vertices

{v,a,b,c}

would induce all six edges of a K
4
	​

. Therefore,

τ
3
	​

(G)≥∣N(v)∣=Δ.
(1)

Every graph of maximum degree Δ also has an independent set of size at least

⌈
Δ+1
n
	​

⌉.

To see this, repeatedly select a vertex and delete it together with all its remaining neighbors. Each selection deletes at most Δ+1 vertices, so at least n/(Δ+1) vertices are selected. The selected vertices are independent and therefore induce a triangle-free graph. Hence

τ
3
	​

(G)≥⌈
Δ+1
n
	​

⌉.
(2)

Combining (1) and (2),

τ
3
	​

(G)≥max{Δ,⌈
Δ+1
n
	​

⌉}.

Let

x=
2
4n+1
	​

−1
	​

,

so that

x(x+1)=n.

If Δ≥x, then, because Δ is an integer,

τ
3
	​

(G)≥Δ≥⌈x⌉.

If Δ<x, then

Δ+1
n
	​

>
x+1
n
	​

=x,

and therefore

τ
3
	​

(G)≥⌈
Δ+1
n
	​

⌉≥⌈x⌉.

Thus every K
4
	​

-free n-vertex graph contains an induced triangle-free subgraph with at least

⌈
2
4n+1
	​

−1
	​

⌉

vertices. ∎

Conclusion

The elementary neighborhood-versus-independent-set argument forces approximately 
n
	​

 vertices. The sharper bounds stated in the attachment show that the true answer, up to subpolynomial factors, is

n
1/2+o(1)
	​

.

They leave a logarithmic gap between

loglogn
nlogn
	​

	​

and
n
	​

logn.

PROVED

PROOF_CONFIDENCE: 99/100
COMPLETENESS_SCORE: 75/100 — the elementary 
n
	​

−O(1) bound and the deduction f(n)=n
1/2+o(1)
 from the supplied estimates are complete; the two deep logarithmic estimates themselves were supplied rather than reproved.
ADVERSARIAL_SURVIVAL_SCORE: 98/100
RESOURCE_USAGE: approximately 20%; three principal arguments checked; two elementary lemmas proved.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

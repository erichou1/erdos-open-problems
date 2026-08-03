# Erdős Problem #1013 [unsolved] 55%

---

## ChatGPT Response

Formalization

For each integer k≥1, define

h
3
	​

(k):=min{∣V(G)∣: G is triangle-free and χ(G)=k}.

Equivalently, since every graph with chromatic number at least k contains a k-critical subgraph,

h
3
	​

(k)=min{∣V(G)∣: G is triangle-free and χ(G)≥k}.

The required assertions are:

h
3
	​

(k)=Θ(k
2
logk)

and

∀ε>0 ∃k
0
	​

 ∀k≥k
0
	​

:1≤
h
3
	​

(k)
h
3
	​

(k+1)
	​

≤1+ε.

The lower inequality in the second display follows from monotonicity.

Quantifier structure

The order-of-magnitude assertion means that there are constants c,C>0 and k
0
	​

 such that

∀k≥k
0
	​

,ck
2
logk≤h
3
	​

(k)≤Ck
2
logk.

The ratio assertion means

∀ε>0 ∃k
0
	​

 ∀k≥k
0
	​

,h
3
	​

(k+1)≤(1+ε)h
3
	​

(k).
Negation of the ratio assertion

Because h
3
	​

 is nondecreasing, failure of the limit is equivalent to

∃ε
0
	​

>0 ∀k
0
	​

 ∃k≥k
0
	​

:h
3
	​

(k+1)≥(1+ε
0
	​

)h
3
	​

(k).

Thus a disproof would require infinitely many multiplicative jumps bounded away from 1.

Elementary properties

h
3
	​

(k) is finite for every k, assuming the existence assertion implicit in its definition.

h
3
	​

(k)≥k.

h
3
	​

(k+1)>h
3
	​

(k).

For the third point, suppose h
3
	​

(k+1)≤h
3
	​

(k)=n. A triangle-free graph G on at most n vertices with χ(G)=k+1 contains a (k+1)-critical subgraph H. Deleting any vertex of H leaves a triangle-free graph of chromatic number at most k, but it need not have chromatic number exactly k. Nevertheless H−v contains a k-chromatic subgraph, so

h
3
	​

(k)≤∣V(H)∣−1<h
3
	​

(k+1),

a contradiction. Hence

h
3
	​

(k+1)≥h
3
	​

(k)+1.

No useful upper bound on this increment follows from criticality alone.

Equivalent inverse formulation

Define

f(n):=max{χ(G):∣V(G)∣=n, G triangle-free}.

Adding isolated vertices shows that f(n) is nondecreasing. Then

h
3
	​

(k)=min{n:f(n)≥k}.

Thus

f(n)≥k⟺h
3
	​

(k)≤n.

The statement in the prompt using f(n)=k requires care: f can have plateaus or jump by more than one unless an additional argument is supplied. The always-valid inverse relation is the threshold relation above.

Extremal and boundary cases

For k=1, one isolated vertex gives h
3
	​

(1)=1.

For k=2, one edge gives h
3
	​

(2)=2.

For k=3, the cycle C
5
	​

 is triangle-free and 3-chromatic, while every triangle-free graph on at most four vertices is bipartite. Hence

h
3
	​

(3)=5.

These values provide no direct control of asymptotic successive ratios.

Order of magnitude

The prompt supplies

(
2
1
	​

−o(1))k
2
logk≤h
3
	​

(k)≤(1+o(1))k
2
logk.

Fix any δ∈(0,
2
1
	​

). For all sufficiently large k,

(
2
1
	​

−δ)k
2
logk≤h
3
	​

(k)≤(1+δ)k
2
logk.

Taking, for example, δ=
4
1
	​

, we obtain

4
1
	​

k
2
logk≤h
3
	​

(k)≤
4
5
	​

k
2
logk

for all sufficiently large k. Therefore

h
3
	​

(k)=Θ(k
2
logk)
	​

.

This is the strongest asymptotic conclusion that follows directly from the two displayed bounds alone. They do not establish an asymptotic equivalence h
3
	​

(k)∼ck
2
logk for any fixed c.

Why the quoted bounds do not imply the ratio limit

From the bounds one obtains only

h
3
	​

(k)
h
3
	​

(k+1)
	​

≤
(
2
1
	​

−o(1))k
2
logk
(1+o(1))(k+1)
2
log(k+1)
	​

=2+o(1).

Thus they imply

1≤
k→∞
liminf
	​

h
3
	​

(k)
h
3
	​

(k+1)
	​

≤
k→∞
limsup
	​

h
3
	​

(k)
h
3
	​

(k+1)
	​

≤2,

but not the required limit.

This is not merely a weakness in the calculation. A nondecreasing sequence can satisfy the same two-sided bounds and still have infinitely many multiplicative jumps bounded away from 1.

For example, let

q(k)=k
2
logk

for k≥2, and choose rapidly increasing integers K
j
	​

, with K
j+1
	​

 large enough that

2
1
	​

q(K
j+1
	​

)≥q(K
j
	​

+1).

Define a nondecreasing sequence that follows approximately 
2
1
	​

q(k), jumps near selected K
j
	​

 to approximately q(K
j
	​

), and remains nearly constant until the lower envelope 
2
1
	​

q(k) catches up. Such a sequence satisfies

(
2
1
	​

−o(1))q(k)≤a
k
	​

≤(1+o(1))q(k)

and has jumps with a
K
j
	​

	​

/a
K
j
	​

−1
	​

 close to 2. Therefore regular variation of h
3
	​

 cannot be deduced solely from the displayed estimates.

Conditional route to the ratio limit

A stronger asymptotic equivalence would immediately settle the ratio assertion.

Lemma

Suppose that for some c>0,

h
3
	​

(k)=(c+o(1))k
2
logk.

Then

k→∞
lim
	​

h
3
	​

(k)
h
3
	​

(k+1)
	​

=1.
Proof

Write

h
3
	​

(k)=ck
2
logk(1+ε
k
	​

),ε
k
	​

→0.

Then

h
3
	​

(k)
h
3
	​

(k+1)
	​

=
k
2
(k+1)
2
	​

logk
log(k+1)
	​

1+ε
k
	​

1+ε
k+1
	​

	​

.

Each factor tends to 1:

k
2
(k+1)
2
	​

=(1+
k
1
	​

)
2
⟶1,
logk
log(k+1)
	​

=1+
logk
log(1+1/k)
	​

⟶1,

and

1+ε
k
	​

1+ε
k+1
	​

	​

⟶1.

Hence the product tends to 1. ∎

More generally, it would suffice to prove

h
3
	​

(k)=k
2
logkL(k),

where L(k+1)/L(k)→1. The stated bounds only place L(k) asymptotically between 1/2 and 1; they do not prove this local regularity.

Structural approaches examined
Critical-graph approach

A vertex-critical (k+1)-chromatic graph has minimum degree at least k. This provides a lower bound on its number of edges, but does not construct a k-chromatic graph on almost the same number of vertices, nor a (k+1)-chromatic graph from an extremal k-chromatic graph with o(k
2
logk) additional vertices.

Vertex deletion

Deleting one vertex lowers chromatic number by at most one:

χ(G−v)≥χ(G)−1.

Consequently, deleting a vertex from a vertex-critical (k+1)-chromatic graph produces a k-colorable graph. Criticality gives equality k. This proves

h
3
	​

(k)≤h
3
	​

(k+1)−1,

which is only the already-known monotonicity and gives no upper bound on h
3
	​

(k+1).

Mycielski-type construction

The standard duplication construction preserves triangle-freeness and increases chromatic number by one, but approximately doubles the number of vertices. It yields only an estimate of the form

h
3
	​

(k+1)≤2h
3
	​

(k)+1,

far too weak for a ratio tending to 1.

Inverse-function approach

If one had a pointwise asymptotic

f(n)∼C
logn
n
	​

	​

,

then inversion would give

h
3
	​

(k)∼
C
2
2
	​

k
2
logk,

because logh
3
	​

(k)∼2logk. The ratio limit would then follow from the preceding lemma. No such pointwise asymptotic, with a verified constant and proof, is contained in the supplied assumptions.

Verified conclusions and unresolved target

The supplied information rigorously establishes

h
3
	​

(k)=Θ(k
2
logk)
	​

.

It does not, by itself, establish either

h
3
	​

(k)∼ck
2
logk

for a constant c, or the local estimate

h
3
	​

(k+1)=h
3
	​

(k)+o(h
3
	​

(k)).

A complete proof of the ratio limit therefore requires an additional substantive theorem: either an exact asymptotic for h
3
	​

(k), a sufficiently regular asymptotic for its inverse f(n), or a triangle-free chromatic-number increment construction with o(k
2
logk) vertex overhead. None of these has been derived from the problem statement alone.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 99/100

COMPLETENESS_SCORE: 55/100
The order-of-magnitude asymptotic is proved. The requested successive-ratio limit is not proved from the stated premises.

ADVERSARIAL_SURVIVAL_SCORE: 98/100
The principal conclusion has been restricted to what follows logically from the supplied bounds; no unproved exact constant or regularity assertion was inserted.

RESOURCE_USAGE: approximately 90% of the available reasoning budget; 8 principal approaches examined; 5 lemmas or structural observations established; 4 insufficient approaches identified.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #667 [solved] 100%

---

## ChatGPT Response

Formalization

For integers p≥1 and 1≤q≤(
2
p
	​

), define

G
n
	​

(p,q)={G: ∣V(G)∣=n,e(G[S])≥q for every S∈(
p
V(G)
	​

)}.

Then

H(n;p,q)=
G∈G
n
	​

(p,q)
min
	​

ω(G),

where ω(G) is the clique number of G. Hence

c(p,q)=
n→∞
liminf
	​

logn
logH(n;p,q)
	​

.

The proposed strict monotonicity is

c(p,q+1)>c(p,q)

for every admissible adjacent pair

1≤q<(
2
p−1
	​

)+1.

Its negation is the existence of p,q in this range such that

c(p,q+1)≤c(p,q).

Since increasing q only strengthens the hypothesis, one always has

H(n;p,q+1)≥H(n;p,q),

and consequently

c(p,q+1)≥c(p,q).

Thus it is enough to exhibit two adjacent values with equality.

The supplied statement includes the bound

c(p,(
2
p−1
	​

))≤
2
1
	​

.
(1)

Pasted text

We will prove

c(4,2)≥
2
1
	​

.
(2)

Pointwise monotonicity and (1) will then force

c(4,2)=c(4,3)=
2
1
	​

.
Complement formulation

Let G∈G
n
	​

(4,2), and let

F=
G
.

Every four vertices span six possible edges. Therefore

e(G[S])≥2

is equivalent to

e(F[S])≤4for every S∈(
4
V(F)
	​

).
(3)

Moreover,

ω(G)=α(F),

where α(F) is the independence number of F.

It remains to derive a lower bound for α(F) from (3).

Lemma 1: Neighborhood structure

For every v∈V(F),

Δ(F[N
F
	​

(v)])≤1.
(4)
Proof

Suppose instead that some x∈N
F
	​

(v) has two distinct neighbors

y,z∈N
F
	​

(v).

On the four vertices {v,x,y,z}, the following five edges are present:

vx,vy,vz,xy,xz.

Thus

e(F[{v,x,y,z}])≥5,

contradicting (3). Hence (4) holds. □

A graph of maximum degree at most 1 is a disjoint union of isolated vertices and edges. Therefore, for every v,

α(F[N
F
	​

(v)])≥
2
d
F
	​

(v)
	​

.

Since an independent set inside N
F
	​

(v) is also independent in F,

α(F)≥
2
d
F
	​

(v)
	​

.

Taking v of maximum degree Δ=Δ(F), we obtain

α(F)≥
2
Δ
	​

.
(5)
Lemma 2: Greedy bound

Every graph on n vertices with maximum degree Δ satisfies

α(F)≥
Δ+1
n
	​

.
(6)
Proof

Repeatedly choose a vertex for the independent set and delete it together with all its neighbors. Each choice deletes at most Δ+1 vertices. Consequently at least

Δ+1
n
	​


vertices can be chosen. □

Combining (5) and (6),

α(F)≥max{
2
Δ
	​

,
Δ+1
n
	​

}.
(7)
Uniform square-root bound

There are two cases.

Case 1: Δ≥
n
	​


By (5),

α(F)≥
2
Δ
	​

≥
2
n
	​

	​

.
Case 2: Δ<
n
	​


By (6),

α(F)>
n
	​

+1
n
	​

=
n
	​

n
	​

+1
n
	​

	​

≥
2
n
	​

	​

.

Thus in every case,

α(F)≥
2
n
	​

	​

.
(8)

Because ω(G)=α(F), every G∈G
n
	​

(4,2) contains a clique of order at least 
n
	​

/2. Hence

H(n;4,2)≥
2
n
	​

	​

.

Therefore

c(4,2)
	​

=
n→∞
liminf
	​

logn
logH(n;4,2)
	​

≥
n→∞
liminf
	​

logn
2
1
	​

logn−log2
	​

=
2
1
	​

.
	​

(9)
Equality at two adjacent values

Pointwise monotonicity gives

c(4,3)≥c(4,2)≥
2
1
	​

.

The supplied bound (1), specialized to p=4, gives

c(4,(
2
3
	​

))=c(4,3)≤
2
1
	​

.

Consequently,

c(4,2)=c(4,3)=
2
1
	​

	​

.

Both q=2 and q=3 belong to the required range

1≤q≤(
2
3
	​

)+1=4.

Thus q↦c(4,q) is not strictly increasing.

DISPROVED
The function c(p,q) need not be strictly increasing in q.
	​


PROOF_CONFIDENCE: 99

COMPLETENESS_SCORE: 100

ADVERSARIAL_SURVIVAL_SCORE: 99

RESOURCE_USAGE: One complement argument, three lemmas including monotonicity, and direct verification of all local configurations.

No internet search, external database, or literature lookup was used. The argument uses only the uploaded problem statement and deductions given above.

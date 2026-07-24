# Erdős Problem #657 [unsolved] 32%

---

## ChatGPT Response

0. Formalization

I use the problem statement in the supplied attachment. 

Pasted text

Let

ex
t
	​

(n)=max{∣H∣:H⊆(
t
[n]
	​

) contains no two distinct disjoint pairs with the same union}.

Under the stated “minimum forcing threshold” convention,

f(n;t)=ex
t
	​

(n)+1.

The difference of 1 is asymptotically irrelevant.

The proposed asymptotic is therefore

ex
t
	​

(n)=(1+o(1))(
t−1
n
	​

)(n→∞, t fixed, t≥3).

Its upper-bound formulation is

∀ε>0 ∃n
0
	​

 ∀n≥n
0
	​

:∣H∣>(1+ε)(
t−1
n
	​

)⟹H contains the forbidden configuration.

Its negation is that for some fixed t≥3, some ε>0, and infinitely many n, there are configuration-free families satisfying

∣H∣≥(1+ε)(
t−1
n
	​

).

The supplied lower bound already gives

n→∞
liminf
	​

(
t−1
n
	​

)
ex
t
	​

(n)
	​

≥1.

Thus only the matching asymptotic upper bound is at issue.

1. Exact swap formulation

Suppose

A⊔B=C⊔D,∣A∣=∣B∣=∣C∣=∣D∣=t,

where the two unordered partitions are distinct.

Define

S=A∩C,X=A∩D,Y=B∩C,T=B∩D.

These four sets are pairwise disjoint, and for some 1≤k≤t−1,

∣X∣=∣Y∣=k,∣S∣=∣T∣=t−k,

while

A=S∪X,B=T∪Y,C=S∪Y,D=T∪X.

Conversely, any four pairwise disjoint blocks S,T,X,Y with these sizes produce the forbidden configuration whenever all four displayed unions are edges.

Because exchanging C and D replaces k by t−k, it is enough to consider

1≤k≤⌊
2
t
	​

⌋.
Swap-link families

For disjoint k-sets X,Y, define

L
X,Y
	​

={S∈(
t−k
[n]∖(X∪Y)
	​

):S∪X, S∪Y∈H}.

Then:

Swap-link equivalence.
H is configuration-free if and only if every
L
X,Y
	​

 is intersecting.

Indeed, disjoint S,T∈L
X,Y
	​

 give the four edges

S∪X,T∪Y,S∪Y,T∪X.

The converse follows from the four-block decomposition.

For t=3, this condition with k=1 is already equivalent to the complete forbidden-configuration condition.

2. Verified lower construction

Fix v∈[n], and let M be a matching of t-sets in [n]∖{v}. Set

H={E∈(
t
[n]
	​

):v∈E}∪M.

Its size is

∣H∣=(
t−1
n−1
	​

)+⌊
t
n−1
	​

⌋.

This family is configuration-free:

Two edges through v cannot be disjoint.

If two matching edges form a disjoint pair, their union contains no edge through v, and it contains no third member of the matching.

Suppose A={v}∪S and B∈M are disjoint. Any alternative partition into two edges of H must again have one edge through v and one matching edge B
′
. If B
′

=B, then B
′
, being disjoint from B, would have to lie inside S, but ∣S∣=t−1, impossible.

Moreover,

(
t−1
n
	​

)
(
t−1
n−1
	​

)
	​

=
n
n−t+1
	​

=1−
n
t−1
	​

.

Hence

ex
t
	​

(n)≥(1−o(1))(
t−1
n
	​

).
3. Exact boundary cases

If n<2t, no two t-sets are disjoint, so every t-uniform family is configuration-free.

If n=2t, all disjoint pairs have union [2t]. The t-sets are divided into

q=
2
1
	​

(
t
2t
	​

)

complementary pairs. A configuration-free family may contain both members of at most one complementary pair and at most one member of every other pair. Therefore

ex
t
	​

(2t)=
2
1
	​

(
t
2t
	​

)+1.

These cases also confirm that a local bound on a single 2t-set cannot by itself give the desired n
t−1
 estimate.

4. Local intersection bounds

I use the following finite theorem.

Intersecting-family bound.
If F⊆(
r
[N]
	​

) is intersecting and N≥2r, then

∣F∣≤(
r−1
N−1
	​

).

A direct cyclic-order proof counts pairs consisting of a cyclic ordering and a member of F occurring as r consecutive positions. At most r such intervals can be pairwise intersecting in one cyclic ordering. A fixed r-set occurs as an interval in r!(N−r)! cyclic orderings, giving

∣F∣r!(N−r)!≤r(N−1)!.

Applying this to L
X,Y
	​

, for n≥2t,

∣L
X,Y
	​

∣≤(
t−k−1
n−2k−1
	​

).

Let P
k
	​

 denote the number of unordered pairs E,F∈H satisfying

∣E∩F∣=t−k.

Each such pair has a unique representation

E=S∪X,F=S∪Y

with disjoint k-sets X,Y. Therefore

P
k
	​

≤
2
1
	​

(
k
n
	​

)(
k
n−k
	​

)(
t−k−1
n−2k−1
	​

)
	​

(1)

for 1≤k≤t−1.

For k=t, the union map on disjoint pairs is injective, so

P
t
	​

≤(
2t
n
	​

).

These are rigorous constraints for every intersection size.

5. The codimension-one calculation

For each (t−1)-set S, let

d(S)=∣{x∈
/
S:S∪{x}∈H}∣.

Then

S∈(
t−1
[n]
	​

)
∑
	​

d(S)=t∣H∣.

Pairs of edges intersecting in exactly t−1 vertices are counted by

P
1
	​

=
S
∑
	​

(
2
d(S)
	​

).

From (1),

S
∑
	​

(
2
d(S)
	​

)≤(
2
n
	​

)(
t−2
n−3
	​

).
	​

(2)

Writing N=(
t−1
n
	​

) and m=∣H∣, Cauchy–Schwarz gives

S
∑
	​

(
2
d(S)
	​

)=
2
1
	​

(
S
∑
	​

d(S)
2
−tm)≥
2
1
	​

(
N
t
2
m
2
	​

−tm).

Consequently,

N
t
2
m
2
	​

−tm≤n(n−1)(
t−2
n−3
	​

),

and hence

m=O
t
	​

(n
t−
2
1
	​

).

This is weaker than the O
t
	​

(n
t−1
) estimate supplied in the problem statement. Its importance here is diagnostic: treating the swap-links independently necessarily loses substantial information. A proof of the coefficient 1 must couple different swap-links, rather than merely bound each one as an intersecting family.

6. The shadow-deficiency formulation

Let

∂H={S∈(
t−1
[n]
	​

):S⊆E for some E∈H}.

Define the maximum shadow deficiency

δ
∗
(H)=
G⊆H
max
	​

(∣G∣−∣∂G∣).

Apply the deficiency form of Hall’s matching theorem to the bipartite incidence graph between edges E∈H and their (t−1)-faces. It gives a matching assigning distinct faces to all but exactly δ
∗
(H) edges. In particular,

∣H∣≤(
t−1
n
	​

)+δ
∗
(H).

Thus the desired asymptotic would follow from

δ
∗
(H)=o(n
t−1
)
	​

(3)

uniformly over all configuration-free H.

There is also a useful minimal-obstruction fact.

Minimal deficiency lemma.
If G is inclusion-minimal subject to

∣G∣>∣∂G∣,

then

∣G∣=∣∂G∣+1,

and no edge of G has a private (t−1)-face.

To prove this, let p(E) be the number of faces contained only in E. Minimality gives

∣G∣−1≤∣∂(G∖{E})∣=∣∂G∣−p(E).

Together with ∣G∣>∣∂G∣, this forces equality and p(E)=0.

Therefore any failure of (3) can be reduced to a large configuration-free subfamily in which every (t−1)-face has codegree at least 2.

The unresolved promoted target is:

\boxed{ \begin{minipage}{0.84\linewidth} Prove that a configuration-free \(t\)-graph with no private \((t-1)\)-face has shadow deficiency \(o(n^{t-1})\). \end{minipage}} \tag{S}

Equivalently, if s=∣∂G∣, then one needs

∣G∣≤s+o(n
t−1
).

Since

t∣G∣=
S∈∂G
∑
	​

d(S),

this asks for an average (t−1)-codegree bound

s
1
	​

S
∑
	​

d(S)≤t+o(1).

The constant t is sharp locally: the complete t-graph on 2t−1 vertices has

(
t
2t−1
	​

)=(
t−1
2t−1
	​

)

edges and shadow members, and every shadow member has codegree t.

7. Strategy search
Strategy	Verified gain	Principal obstruction	Confidence / expected value
Direct shadow injection	Reduces the problem to (3)	No construction of a near-system of distinct representatives	High
Contradiction via minimal deficiency	Produces a codegree-≥2 core with deficiency 1 locally	Minimum codegree alone does not control global swap interactions	High
Lower construction	Star plus exterior matching is fully verified	Gives only the lower asymptotic	Complete
Ordinary induction on n	Deletion formula separates H−v and the link	Links need not satisfy the original forbidden condition	Low
Transfinite induction	No additional finite invariant appears	The problem is finite and quantitative; limit stages erase the leading constant	Very low
Cardinal estimates	Establishes the correct n
t−1
 target scale	Cardinality alone does not distinguish structured stars from sparse algebraic families	Low
Diagonalization from counterexamples	Produces an infinite sequence or ultralimit	Density is O(1/n), so ordinary dense limits become empty	Low
Compactness	Could retain finite forbidden-pattern constraints	Does not retain the n
t−1
 normalization without a sparse-limit theory	Low
Local density and EKR	Gives (1), (2), and O(n
t−1/2
)	Independent local estimates lose all coupling between swap sizes	Medium
Reflection/random restriction	Configuration-freeness is inherited	Restriction changes the normalization by an additional factor n/q	Low
Auxiliary algebra/topology	Squarefree products encode disjoint unions; boundary maps encode shadows	Safe local cycles can have large dimension, so linear dependence need not yield a forbidden trade	Medium-low
Counterexample construction	Full stars cannot be superposed: two stars already create swaps for t≥3	No construction with a fixed coefficient exceeding 1 survived verification	Medium

The three highest-value branches are:

Prove the near-Hall property (3) using stability of the swap-link families.

Develop a delta-system decomposition showing that all large swap-links must have compatible centers.

Use a matching-number dichotomy: many disjoint edges should force global sparsity, while bounded matching number should force a one-center structure.

All three reach the same unresolved issue: local intersecting structures must be shown to align globally.

8. Adversarial checks

The following tempting conclusions do not follow from the verified lemmas:

Bounding each L
X,Y
	​

 by the intersecting-family theorem does not imply the coefficient 1.

Avoiding only the k=1 swap is insufficient when t≥4. Four edges arising from a k≥2 swap may have no pair intersecting in t−1 vertices.

A large minimum (t−1)-codegree does not itself force a forbidden configuration; complete t-graphs on at most 2t−1 vertices are counterexamples.

Standard shifting cannot be assumed to preserve the forbidden property.

Counting disjoint pairs is too weak:

P
t
	​

≤(
2t
n
	​

)

has order n
2t
, whereas a family of order n
t−1
 has only order n
2t−2
 unordered pairs.

The stronger claim ∣H∣≤∣∂H∣ has not been established. Treating it as proved would be circular.

No derived statement closes target (S), and no construction with

∣H∣≥(1+ε)(
t−1
n
	​

)

was obtained.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100 for the formalization, lower construction, swap-link equivalence, and local counting lemmas.

COMPLETENESS_SCORE: 32/100. The lower asymptotic and several necessary structural constraints are rigorous, but the coefficient-1 upper bound is not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 94/100 for the claims explicitly marked verified.

RESOURCE_USAGE: 12 principal strategies examined; 9 formal lemmas or reformulations retained; 7 proof routes rejected or left with explicit gaps.

I did not use WiFi, internet search, web search, external databases, or literature-status information. Apart from the user-supplied attachment cited above, the mathematical reasoning was derived from the statement, definitions, and deductions performed in this session.

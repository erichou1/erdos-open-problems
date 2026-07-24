# Erdős Problem #129 [unsolved] 35%

---

## ChatGPT Response

Complete formalization

Let A⊂(1,∞) be countably infinite and satisfy

(∀x,y∈A)(x

=y)(∀k∈Z
≥1
	​

)∣kx−y∣≥1.

Since the condition with k=1 gives ∣x−y∣≥1, every bounded interval contains only finitely many elements of A. Hence A can be enumerated increasingly:

A={a
1
	​

<a
2
	​

<a
3
	​

<⋯}.

For i<j, the inequalities involving a
j
	​

 as the multiplier are automatic:

ka
j
	​

−a
i
	​

≥a
j
	​

−a
i
	​

≥1.

Thus the whole condition is equivalent to

(∀i<j)(∀k≥1)∣ka
i
	​

−a
j
	​

∣≥1.

Equivalently,

a
j
	​

∈
/
k≥1
⋃
	​

(ka
i
	​

−1,ka
i
	​

+1)(i<j).

Define the two target assertions:

S
1
	​

(A):=
a∈A
∑
	​

aloga
1
	​

<∞,

and

S
2
	​

(A):=
a<n
a∈A
	​

∑
	​

a
1
	​

=o(logn).

Let

H
A
	​

(t):=
a≤t
a∈A
	​

∑
	​

a
1
	​

.

Then S
2
	​

(A) is

H
A
	​

(n)=o(logn).

The negations are:

¬S
1
	​

(A):
a∈A
∑
	​

aloga
1
	​

=∞,

and

¬S
2
	​

(A):∃ε>0 ∃n
r
	​

→∞ such that H
A
	​

(n
r
	​

)≥εlogn
r
	​

.

A useful implication is verified:

Lemma 1. S
1
	​

(A)⇒S
2
	​

(A).

Proof. Suppose

a∈A
∑
	​

aloga
1
	​

<∞.

Fix M>e. For n>M,

H
A
	​

(n)=
a≤M
a∈A
	​

∑
	​

a
1
	​

+
M<a≤n
a∈A
	​

∑
	​

a
1
	​

.

For M<a≤n,

a
1
	​

=loga⋅
aloga
1
	​

≤logn⋅
aloga
1
	​

.

Thus

logn
H
A
	​

(n)
	​

≤
logn
H
A
	​

(M)
	​

+
a>M
a∈A
	​

∑
	​

aloga
1
	​

.

Let n→∞, then M→∞. The tail tends to 0. Hence

H
A
	​

(n)=o(logn).

So the first desired estimate is stronger than the second. □

Boundary structure

Lemma 2. An infinite admissible set A contains no element x<2.

Proof. Suppose x∈A and 1<x<2. For any y>x, choose k≥1 nearest to y/x. Then

∣kx−y∣≤
2
x
	​

<1,

contradicting the defining condition. Hence there is no element of A larger than x. Since A⊂(1,x] and distinct elements are at distance at least 1, A would be finite. Contradiction. □

Thus every infinite admissible A satisfies

A⊂[2,∞).

If 2∈A, then every y∈A∖{2} must satisfy

∣2k−y∣≥1(k≥1).

The multiples of 2 have spacing 2, so the only points at distance at least 1 from every even integer are odd integers. Hence

2∈A⟹A∖{2}⊂{3,5,7,…}.

For those odd integers, the condition reduces to exact non-divisibility: if x,y are odd integers and y

=kx, then ∣kx−y∣≥1 automatically.

So the special case 2∈A reduces to a primitive set of odd integers plus the point 2.

Local extremal behavior

There is no purely local sparsity.

Lemma 3. Let X>1, and let B⊂[X,Y] be 1-separated. If

Y≤2X−1,

then B automatically satisfies the admissibility condition internally.

Proof. For x<y∈B, the k=1 inequality is exactly y−x≥1. For k≥2,

kx−y≥2X−Y≥1.

So ∣kx−y∣≥1. □

This means an interval of relative width almost 2 may contain ≍X admissible points. Any global sparsity must therefore come from interactions across separated scales, not from a local packing bound.

Main proof search

The most direct route would be to prove a bound of the shape

H
A
	​

(t)≪loglogt.

That would imply both requested estimates.

Indeed, if

H
A
	​

(t)≤Cloglogt+O(1),

then by partial summation,

a≤N
a∈A
	​

∑
	​

aloga
1
	​

=
logN
H
A
	​

(N)
	​

+∫
e
N
	​

t(logt)
2
H
A
	​

(t)
	​

dt.

The first term is

O(
logN
loglogN
	​

)=o(1),

and the integral is bounded because

∫
e
∞
	​

t(logt)
2
loglogt
	​

dt<∞.

So

H
A
	​

(t)≪loglogt⟹
a∈A
∑
	​

aloga
1
	​

<∞⟹H
A
	​

(n)=o(logn).

But the missing primary theorem is:

H
A
	​

(t)≪loglogt.
	​


I could not prove this from the given hypotheses alone.

Twelve independent strategies checked
Strategy	Core idea	Verified progress	Obstruction
Direct packing	Use k=1 separation	Gives (	A\cap[1,t]
Forbidden intervals	Each x forbids ⋃
k
	​

(kx−1,kx+1)	Total forbidden measure from x up to t is ≍t/x	Overlaps between different x’s are uncontrolled
Greedy sieve	New points survive old forbidden intervals	Heuristic gives H
A
	​

(t)∼
2
1
	​

loglogt	Needs rigorous lower bound for union of forbidden intervals
Contradiction from H
A
	​

(t)≫logt	Assume dense harmonic mass	Would force large total forbidden measure	Again requires overlap control
Dyadic decomposition	Let (\delta_j:=2^{-j}	A\cap[2^j,2^{j+1})	)
Logarithmic coordinates	Write u=logx	Forbidden differences near logk	Windows have variable width 1/x, hard to pack
Cardinal arithmetic	Count admissible points in finite windows	Gives only finite local bounds	No asymptotic improvement
Diagonal counterexample	Try to choose dense blocks recursively	Single dense block works	Future blocks face accumulated forbidden intervals
Transfinite induction	Build A stage-by-stage avoiding old intervals	Produces infinite admissible sets	Does not control harmonic size
Compactness	Prove finite versions, pass to limit	Finite admissible sets exist with high local density	Need uniform global estimates
Auxiliary graph	Vertices x, edges for approximate dilation conflicts	Natural graph model appears	Need strong independent-set bound
Reflection/density	Reflect multiples modulo x	Suggests recurrence H
′
(t)≲e
−2H(t)
/t	Only heuristic without independence

The main repeated obstruction is the same:

How large must 
x∈B
⋃
	​

k≥1
⋃
	​

(kx−1,kx+1) be?

A proof of sufficiently large union measure would likely imply the desired sparsity. But I could not prove such a union lower bound without an additional theorem.

Counterexample search

Several possible counterexample constructions were tested.

1. Dense finite block

Take many 1-separated points in

[X,2X−1].

By Lemma 3, this is internally admissible. This shows that no bound like

∣A∩[X,2X]∣≪
logX
X
	​


can follow from local constraints alone.

But this does not produce an infinite counterexample, because later scales must avoid all approximate multiples of the earlier dense block.

2. Geometric blocks

Try blocks near R
j
. Adjacent blocks can be arranged so that small multiples do not interfere, but non-adjacent blocks eventually interact through some integer dilation k. The obstruction becomes controlling how often

R
j−i

is close to an integer. Even if exact integer coincidences are avoided, block widths create many approximate coincidences.

No counterexample was obtained.

3. Scaled integer blocks

Try

A
j
	​

=α
j
	​

{N
j
	​

,N
j
	​

+1,…,2N
j
	​

−1}.

Each block is internally admissible when α
j
	​

≥1. To add a new block, α
j
	​

 must avoid intervals

	​

α
j
	​

−
n
kx
	​

	​

<
n
1
	​


for all old x and all n∈[N
j
	​

,2N
j
	​

). A union bound only works while the previous harmonic mass is bounded. Therefore this method does not yield a divergent example.

4. Element below 2

Impossible by Lemma 2.

5. Element exactly 2

Then the rest of A lies inside the odd integers and becomes an integer primitive-type problem. This gives no real-valued counterexample.

No disproof was found.

Verified dependency graph

Definitions:

P(A):(∀x

=y∈A)(∀k≥1) ∣kx−y∣≥1.

Verified lemmas:

P(A)⇒A is 1-separated.

P(A)⇒A∩(1,T] is finite for every T.

Infinite P(A)⇒A∩(1,2)=∅.

If 2∈A, then A∖{2}⊂{3,5,7,…}.

S
1
	​

(A)⇒S
2
	​

(A).

H
A
	​

(t)≪loglogt⇒S
1
	​

(A)⇒S
2
	​

(A).

Dense admissible finite blocks exist inside [X,2X−1].

Unresolved primary theorem:

P(A)
⟹
?
	​

H
A
	​

(t)≪loglogt.

Unresolved weaker theorem:

P(A)
⟹
?
	​

H
A
	​

(t)=o(logt).

Unresolved stronger theorem:

P(A)
⟹
?
	​

a∈A
∑
	​

aloga
1
	​

<∞.

No theorem above depends on an unproved statement.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified lemmas only.

COMPLETENESS_SCORE: 35/100. The formal reductions and boundary cases are rigorous, but neither requested sparsity statement was proved or disproved from first principles.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the local lemmas; 0/100 for the unresolved global sparsity claims, because no complete proof was obtained.

RESOURCE_USAGE: approximately 100% of the current reasoning budget used; 12 strategies explored; 7 verified lemmas generated; 5 counterexample frameworks tested; 0 complete proof attempts survived to the main conclusion.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

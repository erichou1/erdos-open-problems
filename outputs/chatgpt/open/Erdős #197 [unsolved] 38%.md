# Erdős Problem #197 [unsolved] 38%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Complete formalization

Let N={1,2,3,…}.

For A⊆N, say A is permutably M3AP-free if there exists a bijection

π:N→A

such that there do not exist i<j<k with

π
i
	​

,π
j
	​

,π
k
	​


forming a monotone 3-term arithmetic progression in value.

Equivalently, define the rank map

ρ
A
	​

(a)=π
−1
(a).

Then A is permutably M3AP-free iff for every value-AP

a<b<c,a+c=2b,a,b,c∈A,

the middle value b is not between a and c in rank:

ρ
A
	​

(b)<min(ρ
A
	​

(a),ρ
A
	​

(c))orρ
A
	​

(b)>max(ρ
A
	​

(a),ρ
A
	​

(c)).

The problem asks whether there exist disjoint A,B⊆N such that

A∪B=N

and both A,B are permutably M3AP-free.

Negation

For every partition

N=A⊔B,

at least one of A,B has the following property: for every bijection π:N→A or π:N→B, there exists a monotone 3-term arithmetic progression appearing in the permutation.

Contrapositive form

If A and B are both permutably M3AP-free, then their union cannot be all of N.

Boundary cases

Every finite set is permutably M3AP-free. Therefore no finite obstruction can disprove the existence of a 2-partition. Any obstruction must be genuinely infinite.

Verified lemma 1: rank formulation

For a<b<c with a+c=2b, the triple appears as a monotone 3-term AP in the permutation exactly when

ρ(a)<ρ(b)<ρ(c)

or

ρ(c)<ρ(b)<ρ(a).

Thus avoiding monotone 3APs is equivalent to requiring b to be rank-extreme among a,b,c.

This lemma is verified directly from the definitions.

Verified lemma 2: every finite set is admissible

For m≥1, order {0,1,…,2
m
−1} by comparing binary expansions from the least significant bit upward. Equivalently, use bit-reversal order.

Let x<y<z and x+z=2y. Put

z−x=2
t
q,q odd.

Since z−x is even, t≥1. Then

y−x=2
t−1
q.

Therefore x and z agree in binary bits 0,…,t−1, while y differs from them first at bit t−1. Hence in least-significant-bit lexicographic order, y is either before both x,z, or after both x,z. So y is never rank-between x,z.

Thus bit-reversal order avoids monotone 3APs on [0,2
m
−1]. Any finite subset of N embeds into such an interval, so every finite subset is admissible.

Adversarial check: This does not prove N itself is admissible, because the limiting bit-reversal order is not an ω-sequence enumeration of all natural numbers. It has infinite blocks before later blocks.

Verified lemma 3: doubling-tail obstruction

Let A⊆N be permutably M3AP-free with rank map ρ. Fix x∈A and d≥1.

Then A cannot contain all but finitely many terms of the ray

x+d, x+2d, x+4d, x+8d,…

that is,

x+2
k
d.
Proof

Assume toward contradiction that for all sufficiently large k,

x+2
k
d∈A.

Only finitely many elements appear before x in the permutation, so for sufficiently large k, all of

x+2
k
d,x+2
k+1
d

also appear after x.

But

x,x+2
k
d,x+2
k+1
d

is a 3-term arithmetic progression because

x+2
k+1
d−x=2
k+1
d,

and the middle is

x+2
k
d.

Since x appears before both other terms, the middle term must not appear between the two endpoints. Therefore the farther endpoint must appear before the middle:

ρ(x+2
k+1
d)<ρ(x+2
k
d)

for every sufficiently large k.

This gives an infinite strictly descending sequence of natural-number ranks:

ρ(x+2
K
d)>ρ(x+2
K+1
d)>ρ(x+2
K+2
d)>⋯,

impossible in N.

So no such eventually full doubling ray may lie inside A.

Adversarial check: The proof uses only the rank-extreme condition and well-ordering of permutation positions. It does not assume density, regularity, or any external theorem.

Consequence

If

N=A⊔B

and both A,B are admissible, then for every x∈A and every d≥1, infinitely many terms of

x+2
k
d

must lie in B. Similarly, for every x∈B, infinitely many terms of every such ray must lie in A.

So any successful 2-partition would need infinite color oscillation along every doubling ray based at every point of its own color.

This is a strong necessary condition, but I did not derive a contradiction from it.

Strategy search summary

I explored the following proof routes.

Strategy	Result
Direct rank contradiction	Produced the doubling-tail obstruction, but not a full contradiction for 2 colors.
Contradiction from least elements of A,B	Gives ray constraints from each least element, but does not force one color to contain a full forbidden ray.
Finite obstruction	Impossible, since every finite set is admissible.
Compactness	Gives non-ω linear orders, not valid permutations.
2-adic bit-reversal order	Proves finite admissibility and explains why N itself fails under the limiting order.
Density argument	No verified density obstruction obtained.
Ramsey-style monochromatic ray theorem	Would solve the problem if true, but I did not prove it.
Infinite arithmetic progression inside one part	Not forced by arbitrary 2-colorings.
Transfinite-rank reformulation	Suggestive but did not yield an ω-rank obstruction.
Canonical-order partition	Bit-reversal restriction cannot obviously yield a finite partition into ω-type subsequences.
Counterexample construction	No explicit 2-partition with valid permutations found.
Stronger forbidden-tree condition	Produced useful necessary conditions, but no contradiction.
Main unresolved gap

The strongest verified reduction is:

If a 2-partition A⊔B=N exists with both parts admissible, then every same-color point x must see infinitely many opposite-color points on every ray x+2
k
d.

To disprove the 2-partition, one would need to prove that no 2-coloring of N can satisfy all these rank-compatible constraints, or find a stronger obstruction involving interactions among multiple rays.

I did not complete that step.

Final status

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92
COMPLETENESS_SCORE: 38
ADVERSARIAL_SURVIVAL_SCORE: 84

RESOURCE_USAGE: approximately 100% of available reasoning budget used; 12 strategy families explored; 3 verified lemmas generated; 5 failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

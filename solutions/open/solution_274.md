# Erdős Problem #274 [unsolved] 28%

---

## ChatGPT Response

Phase 0: complete formalization

Let G be a group. A finite exact coset covering is data

k≥2,H
i
	​

≤G,a
i
	​

∈G,C
i
	​

=a
i
	​

H
i
	​


such that

∀g∈G,∃!i∈{1,…,k} with g∈a
i
	​

H
i
	​

.

The strong target statement is:

In every finite exact coset covering of G, two subgroups have the same index.
	​


Equivalently, there do not exist G,k,H
i
	​

,a
i
	​

 with

G=
i=1
⨆
k
	​

a
i
	​

H
i
	​


and

[G:H
i
	​

]

=[G:H
j
	​

]for all i

=j.

Negation:

∃G,∃k≥2,∃H
i
	​

≤G,∃a
i
	​

∈G:G=
i=1
⨆
k
	​

a
i
	​

H
i
	​


and the indices [G:H
i
	​

] are pairwise distinct.

For finite G, since ∣a
i
	​

H
i
	​

∣=∣H
i
	​

∣,

∣G∣=
i=1
∑
k
	​

∣H
i
	​

∣.

Writing n
i
	​

=[G:H
i
	​

], this becomes

i=1
∑
k
	​

n
i
	​

1
	​

=1.
	​


Thus in the finite case the index spectrum {n
1
	​

,…,n
k
	​

} must be a set of distinct integers ≥2 satisfying an Egyptian-fraction identity.

Verified reductions and lemmas
Lemma 1: finite-index counterexamples reduce to finite groups

Assume all [G:H
i
	​

] are finite. Define

N=
i=1
⋂
k
	​

core
G
	​

(H
i
	​

),core
G
	​

(H
i
	​

)=
g∈G
⋂
	​

gH
i
	​

g
−1
.

Each core
G
	​

(H
i
	​

) has finite index because it is the kernel of the action of G on the finite set G/H
i
	​

. Hence N◃G has finite index.

Since N≤H
i
	​

 for every i, the quotient Q=G/N is finite, and the cosets descend to

(a
i
	​

N)(H
i
	​

/N)⊆Q.

Moreover,

[Q:H
i
	​

/N]=[G:H
i
	​

].

The partition property is preserved because the preimage of (a
i
	​

N)(H
i
	​

/N) is exactly a
i
	​

H
i
	​

.

Therefore:

Any finite-index counterexample gives a finite-group counterexample.
	​


So the finite-index problem may be attacked inside finite groups.

Lemma 2: no finite counterexample with k=2

For finite G,

n
1
	​

1
	​

+
n
2
	​

1
	​

=1.

With n
1
	​

,n
2
	​

≥2,

n
1
	​

n
2
	​

=n
1
	​

+n
2
	​

,

so

(n
1
	​

−1)(n
2
	​

−1)=1.

Thus

n
1
	​

=n
2
	​

=2.

The indices are equal, so they are not distinct.

k=2 is impossible.
	​

Lemma 3: index 2 forces descent to a smaller group

Suppose a finite exact covering contains a coset of a subgroup H with

[G:H]=2.

Left-translate the whole partition so that this coset is H itself.

Every subgroup of index 2 is normal: there are only two left cosets, H and G∖H, and the same two right cosets, so left and right cosets coincide.

Let another part be aK, disjoint from H. Consider the quotient

π:G→G/H.

Since G/H has order 2, the subgroup π(K) is either trivial or all of G/H. If π(K)=G/H, then π(aK)=G/H, so aK meets H, contradiction.

Hence π(K)=1, so

K≤H.

Thus every other coset lies wholly inside the other H-coset G∖H. Translating that coset back into H, the remaining pieces form an exact coset partition of H. Their indices inside H are

[H:K]=
2
[G:K]
	​

.

Distinct G-indices remain distinct after division by 2.

Therefore any finite counterexample containing index 2 produces a smaller counterexample inside H.

Lemma 4: no finite counterexample with k=3

For k=3, distinct indices n
1
	​

<n
2
	​

<n
3
	​

 satisfy

n
1
	​

1
	​

+
n
2
	​

1
	​

+
n
3
	​

1
	​

=1.

If n
1
	​

≥3, then

n
1
	​

1
	​

+
n
2
	​

1
	​

+
n
3
	​

1
	​

≤
3
1
	​

+
4
1
	​

+
5
1
	​

<1,

impossible. Hence n
1
	​

=2.

Then

n
2
	​

1
	​

+
n
3
	​

1
	​

=
2
1
	​

.

The distinct solution is

(n
1
	​

,n
2
	​

,n
3
	​

)=(2,3,6).

But if an index 2 part exists, Lemma 3 implies all remaining indices are even, since each remaining subgroup K≤H has

[G:K]=2[H:K].

The index 3 part contradicts this.

k=3 is impossible.
	​

Lemma 5: no finite counterexample with k=4

Let n
1
	​

<n
2
	​

<n
3
	​

<n
4
	​

. If n
1
	​

≥3, then

i=1
∑
4
	​

n
i
	​

1
	​

≤
3
1
	​

+
4
1
	​

+
5
1
	​

+
6
1
	​

=
20
19
	​

<1.

So n
1
	​

=2.

By Lemma 3, the remaining three cosets descend to an exact partition of the index 2 subgroup H by three cosets with distinct indices inside H. But Lemma 4 says no such k=3 counterexample exists.

Therefore

k=4 is impossible.
	​


So any finite-index counterexample must have

k≥5.
	​

Phase 1: breadth-first proof search

I generated the required strategy set and tracked obstacles.

Strategy	Core idea	Verified progress	Obstacle
Direct proof	Use ∑1/n
i
	​

=1 plus subgroup constraints	Proved k≤4 impossible	Arithmetic alone allows k≥5
Contradiction	Minimal counterexample by (	G	), then k
Construction	Try to build a finite nonabelian partition	Weak non-pairwise version has easy examples	Pairwise distinct-index construction not found
Induction on (	G	)	Descend through normal prime-index parts
Induction on k	Remove one coset and partition complement	Works only when complement is a coset/block	Complement usually not subgroup-like
Transfinite/infinite case	Reduce infinite G to finite quotient	Proved for finite indices	Infinite-index cosets require another lemma
Cardinal arithmetic	Analyze cardinal sizes of cosets	Finite case rigorous	Infinite cardinals erase size information
Diagonalization	Pick element avoiding finitely many cosets	Relevant to infinite-index covers	Need a fully proved finite-cover lemma
Compactness	Encode finite contradictions in quotients	Gives finite quotient framework	Does not force quotient contradiction
Density/measure	Use normalized counting measure	Gives ∑1/n
i
	​

=1	Measure identity too weak
Reflection	Pass to core quotient	Fully proved for finite indices	Finite quotient still unresolved
Auxiliary structure	Use group algebra / representations	Produces strong equations	Need a separating representation not proved
Counterexample search	Check small k, small spectra	k≤4 eliminated	k≥5 remains large
Quotient-shadow method	Project cover through normal subgroups	Prime-index normal case works	General quotient shadows can overlap

Top three branches by expected value:

Minimal finite counterexample plus normal-subgroup descent.

Group algebra / representation equations.

Infinite-to-finite reduction via finite-cover irredundancy.

Phase 2: invented structures
1. Index spectrum
N(C)={[G:H
i
	​

]:1≤i≤k}.

Motivation: exact finite covers force

n∈N
∑
	​

n
1
	​

=1.

Consequence: any counterexample must have k≥5.

2. Core quotient
Q(C)=G/
i
⋂
	​

core
G
	​

(H
i
	​

).

Motivation: removes all non-faithful infinite structure while preserving finite indices.

Consequence: finite-index counterexamples are equivalent to finite quotient counterexamples.

3. Normal-prime splitter

A part aH is a normal-prime splitter if H◃G and [G:H] is prime.

Motivation: quotient G/H has no proper nontrivial subgroup.

Consequence: every other subgroup must lie inside H, producing smaller exact partitions.

4. Representation defect equation

For finite G, the group-algebra identity is

i=1
∑
k
	​

a
i
	​

h∈H
i
	​

∑
	​

h=
g∈G
∑
	​

g.

Applying a nontrivial irreducible representation ρ gives

i=1
∑
k
	​

ρ(a
i
	​

)
h∈H
i
	​

∑
	​

ρ(h)=0.

The obstacle is to prove that some representation detects exactly one maximal contribution. I could not prove that from first principles.

Phase 3: parallel exploration
Branch A: minimal counterexample

Assume a finite counterexample exists with ∣G∣ minimal.

Verified:

k≥5.

No part may have index 2.

More generally, no part may be a normal subgroup of prime index.

Reason: such a part descends to a smaller counterexample, contradicting minimality.

Gap:

A minimal-index subgroup need not be normal by the hypotheses alone. The branch stalls at:

Show a minimal counterexample contains a normal prime-index splitter.

I could not prove this.

Branch B: representation method

From exactness,

1
G
	​

=
i
∑
	​

1
a
i
	​

H
i
	​

	​


as functions on G. In the finite group algebra,

i
∑
	​

a
i
	​

H
i
Σ
	​

=G
Σ
,

where

H
i
Σ
	​

=
h∈H
i
	​

∑
	​

h,G
Σ
=
g∈G
∑
	​

g.

Applying a nontrivial irreducible representation ρ,

i
∑
	​

ρ(a
i
	​

)P
H
i
	​

	​

=0,

where P
H
i
	​

	​

 is a scalar multiple of projection onto the H
i
	​

-fixed subspace.

This would prove the theorem if one could find ρ such that exactly one P
H
i
	​

	​

 survives, or such that the surviving terms cannot cancel because their subgroup indices are distinct.

Gap:

No first-principles proof produced such a representation.
Branch C: construction attempt

A weak reading of “different sizes” is easy: if repetitions are allowed, then examples exist. For instance,

S
3
	​

=A
3
	​

⊔{(12)}⊔{(13)}⊔{(23)}.

Here A
3
	​

 is a coset of A
3
	​

, and each singleton is a coset of the trivial subgroup. The sizes are 3,1,1,1, so not all sizes are equal.

But this does not satisfy the strong pairwise-distinct-index condition, because the singleton cosets all have the same subgroup index.

For the strong formulation, construction must satisfy

i
∑
	​

n
i
	​

1
	​

=1

with distinct n
i
	​

, plus strong subgroup-placement constraints. No construction was obtained.

Verified state of the search

Established rigorously:

Finite-index counterexamples reduce to finite groups.
	​

k=2,3,4 are impossible in finite groups.
	​

A minimal finite counterexample has k≥5.
	​

A minimal finite counterexample contains no normal prime-index part.
	​


Unresolved primary gap:

Rule out finite exact coset partitions with k≥5 and pairwise distinct indices, when no normal prime-index descent is available.
	​


I recursively attacked this gap through induction, quotient descent, arithmetic constraints, representation equations, and construction search. None yielded a complete proof or disproof within the available reasoning budget.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 86/100
COMPLETENESS_SCORE: 28/100
ADVERSARIAL_SURVIVAL_SCORE: 78/100

RESOURCE_USAGE: 100% of available response budget; 14 branches considered; 5 verified lemmas; 6 failed proof attempts; 1 main unresolved gap.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

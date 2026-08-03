# Erdős Problem #653 [unsolved] 22%

---

## ChatGPT Response

The task is to decide whether

g(n)=
P⊂R
2
∣P∣=n
	​

max
	​

∣{R
P
	​

(x):x∈P}∣satisfiesg(n)=(1−o(1))n,

where

R
P
	​

(x)=∣{∥x−y∥:y∈P∖{x}}∣.

Pasted text

1. Formalization

The proposed assertion is

∀ε>0 ∃N ∀n≥N ∃P⊂R
2
:∣P∣=n,∣{R
P
	​

(x):x∈P}∣≥(1−ε)n.

Equivalently,

n−g(n)=o(n).

Its negation is

∃ε
0
	​

>0 ∀N ∃n≥N ∀P⊂R
2
, ∣P∣=n:∣{R
P
	​

(x):x∈P}∣≤(1−ε
0
	​

)n.

Define the distance deficit

D
P
	​

(x)=n−1−R
P
	​

(x).

Thus the question is equivalently whether one can make D
P
	​

(x) assume n−o(n) distinct values.

For every x, partition P∖{x} into its distance classes

C
x,r
	​

={y∈P∖{x}:∥x−y∥=r}.

Then

R
P
	​

(x)=#{r:C
x,r
	​


=∅},

and

D
P
	​

(x)=
r
∑
	​

(∣C
x,r
	​

∣−1).

Translations, rotations, reflections, and uniform scalings preserve all R
P
	​

(x).

2. Two-center bound
Lemma 1

For any two distinct points a,b∈P,

n−2≤2R
P
	​

(a)R
P
	​

(b).
Proof

Map every y∈P∖{a,b} to

(∥y−a∥,∥y−b∥).

There are at most R
P
	​

(a)R
P
	​

(b) possible ordered pairs.

For fixed positive radii r,s, the simultaneous equations

∥y−a∥=r,∥y−b∥=s

describe the intersection of two circles with distinct centers. Such an intersection contains at most two points. Therefore every distance pair has at most two preimages, giving

n−2≤2R
P
	​

(a)R
P
	​

(b).

□

Corollary 2

For every n≥3,

g(n)≤n+1−
2
n−2
	​

	​

.
Proof

Suppose a configuration realizes

r
1
	​

<r
2
	​

<⋯<r
k
	​


as its k distinct R-values. Since r
k
	​

≤n−1,

r
2
	​

+(k−2)≤n−1,

and hence

r
2
	​

≤n−k+1.

Choose vertices attaining r
1
	​

,r
2
	​

. Lemma 1 gives

n−2≤2r
1
	​

r
2
	​

≤2r
2
2
	​

≤2(n−k+1)
2
.

Rearranging proves the claim. □

This establishes a sublinear unavoidable gap, but it is compatible with

g(n)=(1−o(1))n.
3. Collinear and circular constructions cannot suffice
Lemma 3

If all n points lie on one line, then

R
P
	​

(x)≥⌈
2
n−1
	​

⌉

for every x, and consequently

∣{R
P
	​

(x):x∈P}∣≤⌈
2
n
	​

⌉.
Proof

A circle centered at x intersects the line in at most two points. Hence every distance class at x contains at most two points, so

n−1=
r
∑
	​

∣C
x,r
	​

∣≤2R
P
	​

(x).

There are only

n−⌈
2
n−1
	​

⌉=⌈
2
n
	​

⌉

integers in the resulting allowable interval.

For the arithmetic progression P={1,…,n}⊂R,

R
P
	​

(i)=max(i−1,n−i),

and exactly ⌈n/2⌉ values occur. Thus the bound is sharp within the collinear class. □

The identical upper bound applies when all points lie on one circle: a circle centered at a point of P intersects the supporting circle in at most two points.

Therefore neither a one-dimensional construction nor a subset of a single circle can establish the desired asymptotic.

4. Necessary abundance of high-multiplicity distance classes
Lemma 4

If

R
P
	​

(x)<
2
n−1
	​

,

then at least one distance class centered at x contains three or more points.

Proof

If every class had size at most 2, then

n−1=
r
∑
	​

∣C
x,r
	​

∣≤2R
P
	​

(x),

contrary to the hypothesis. □

Consequence

Suppose a configuration has

k≥(1−ε)n

distinct R-values. At most ⌈n/2⌉ possible values are at least

⌈
2
n−1
	​

⌉.

Hence at least

k−⌈
2
n
	​

⌉≥(
2
1
	​

−ε)n−O(1)

vertices must be centers of circles containing at least three other points of P.

Thus a successful construction must contain a linear number of such “rich centers.” Pairwise reflection equalities alone cannot suffice.

5. Isosceles-triangle budget

Let

T
P
	​

(x)=
r
∑
	​

(
2
∣C
x,r
	​

∣
	​

),

the number of unordered isosceles triangles having apex x.

Since

(
2
s
	​

)≥s−1(s≥1),

we have

T
P
	​

(x)≥D
P
	​

(x).

If k distinct R-values occur, then the corresponding deficits are k distinct nonnegative integers. Choosing one representative vertex for each value gives

x∈P
∑
	​

T
P
	​

(x)≥
representatives
∑
	​

D
P
	​

(x)≥0+1+⋯+(k−1)=(
2
k
	​

).

Consequently, any configuration witnessing k=(1−o(1))n must determine

(
2
1
	​

−o(1))n
2

isosceles triangles. This condition is necessary but not contradictory: highly symmetric configurations can have quadratically many isosceles triangles.

6. Exact reflection symmetry has a 3/4-barrier
Lemma 5

If P is invariant under a reflection, then

∣{R
P
	​

(x):x∈P}∣≤
4
3
	​

n+1.
Proof

Let f points lie on the reflection axis and let q=n−f points lie off it. The latter form q/2 mirror pairs.

Reflection preserves distance multisets, so mirror partners have equal R-values. Therefore

h(P):=∣{R
P
	​

(x):x∈P}∣≤f+
2
q
	​

=
2
n+f
	​

.
(1)

Now consider an axis point x. Its distances to the f−1 other axis points give at least

⌈
2
f−1
	​

⌉

distinct values. Its distances to the q off-axis points give at most q/2 additional values, because each mirror pair is equidistant from x. Hence every axis point satisfies

⌈
2
f−1
	​

⌉≤R
P
	​

(x)≤f−1+
2
q
	​

.

The number of possible values among axis points is therefore at most

⌈
2
f
	​

⌉+
2
q
	​

.

The off-axis points can contribute at most q/2 further values, one per mirror pair. Thus

h(P)≤⌈
2
f
	​

⌉+q≤n−
2
f
	​

+1.
(2)

Combining (1) and (2),

h(P)≤min{
2
n+f
	​

,n−
2
f
	​

+1}.

The two expressions balance at f=n/2+O(1), where their common size is 3n/4+O(1). □

Therefore constructions based on one global reflection symmetry cannot prove the desired asymptotic.

7. Generic extension lemma
Lemma 6

For all positive integers n,t,

g(n+t)≥g(n).

More precisely, any n-point configuration can be extended by t points so that every original R-value increases by exactly t.

Proof

Add points successively. When choosing a new point z, avoid:

every circle centered at an existing point whose radius is an already occurring distance from that point;

every perpendicular bisector determined by two existing points.

This is a finite union of lines and circles and therefore does not cover the plane.

Condition 1 ensures that every existing vertex gains one new distinct distance. Condition 2 ensures that z has distinct distances to all existing vertices. Repeating this operation proves the assertion. □

Dense-subsequence consequence

It would be enough to construct integers N
j
	​

 satisfying

N
j
	​

N
j+1
	​

	​

⟶1

and configurations with

g(N
j
	​

)=(1−o(1))N
j
	​

.

Generic extension would then fill the intervening values of n.

This removes divisibility restrictions but does not itself improve the proportion of distinct values.

8. Cartesian-product strategy

Let A,B⊂Z, and embed

P={(a,λb):a∈A, b∈B},

where λ
2
 is irrational.

Then

∥(a,λb)−(a
′
,λb
′
)∥
2
=(a−a
′
)
2
+λ
2
(b−b
′
)
2
.

Irrationality implies that two such squared distances are equal exactly when

∣a−a
′
∣=∣a−a
′′
∣,∣b−b
′
∣=∣b−b
′′
∣.

Writing

U
A
	​

(a)=∣{∣a−a
′
∣:a
′
∈A}∣,

and similarly for B, one gets the exact formula

R
P
	​

((a,λb))+1=U
A
	​

(a)U
B
	​

(b).

Since a one-dimensional m-point set has at most ⌈m/2⌉ distinct U
A
	​

-values, a product with ∣A∣=m, ∣B∣=ℓ produces at most

⌈
2
m
	​

⌉⌈
2
ℓ
	​

⌉=
4
1
	​

mℓ+O(m+ℓ)

distinct products before possible additional collisions.

Thus the straightforward anisotropic-grid product construction is quantitatively inadequate.

9. Strategy audit
Strategy	Verified outcome	Unresolved obstruction
Direct construction	Line and circle models capped near n/2	Need multiplicities ≥3 at linearly many centers
Contradiction	Two-center lemma gives an Ω(
n
	​

) gap	Does not yield a fixed positive-density gap
Induction	Generic extension proves monotonicity	Does not increase the realized proportion
Transfinite induction	No infinite recursion is intrinsic to the finite problem	No useful monotone extension rule
Cardinal estimates	R(x)∈{1,…,n−1} and deficits are integral	Range counting alone is compatible with either answer
Diagonalization	Prescribing deficits requires controlling many circle incidences	Euclidean equality constraints are highly dependent
Compactness	Limit configurations preserve equalities but can create new ones	The count R(x) is discontinuous under limits
Density/random perturbation	Generic perturbation makes most distances distinct	It tends to make many vertices share R=n−1
Reflection	Exact 3n/4+O(1) barrier proved	Breaking symmetry while retaining equalities lacks control
Cartesian products	Exact multiplicative formula obtained	Produces only about n/4 values in the basic form
Lattice construction	Supplies many high-multiplicity shells	No proof that the shell counts can be made almost injective
Counterexample search	Necessary rich-center and isosceles conditions found	Neither condition contradicts n−o(n) distinct values

The two viable unresolved directions are:

construct an irregular lattice or multi-circle incidence configuration in which x↦R
P
	​

(x) is injective on n−o(n) vertices;

prove that a linear number of low-R vertices forces enough repeated R-values to give a positive-density upper gap.

Neither statement has been established by the deductions above.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100 for the stated lemmas and consequences.

COMPLETENESS_SCORE: 22/100. The structural restrictions are rigorous, but neither the required construction nor a disproof has been obtained.

ADVERSARIAL_SURVIVAL_SCORE: 91/100 for the partial results.

RESOURCE_USAGE: 100% of the allocated search for this response; 12 principal strategies examined, 6 formal lemmas established, and multiple construction families excluded.

I used no WiFi, internet search, external databases, theorem repositories, or literature-status information. The only retrieved material used was the problem statement supplied by the user; all mathematical deductions above were carried out from that statement.

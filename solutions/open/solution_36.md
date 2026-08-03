# Erdős Problem #36 [unsolved] 25%

---

## ChatGPT Response

Phase 0: Complete formalization

Let

[2N]={1,2,…,2N}.

A balanced partition is an ordered pair (A,B) such that

A⊔B=[2N],∣A∣=∣B∣=N.

For such a partition define

R
A,B
	​

(x)=#{(a,b)∈A×B:a−b=x}.

The quantity to minimize is

M(A,B)=
x∈Z
max
	​

R
A,B
	​

(x).

Since a,b∈[2N], only

−(2N−1)≤x≤2N−1

can occur, and since A∩B=∅,

R
A,B
	​

(0)=0.

Define the finite extremal value

m
N
	​

=
A⊔B=[2N]
∣A∣=∣B∣=N
	​

min
	​

M(A,B).

The supremal admissible constant is therefore

c
∗
	​

=
N→∞
liminf
	​

N
m
N
	​

	​

.

Indeed, a constant c has the desired eventual property exactly when

∃N
0
	​

 ∀N≥N
0
	​

 ∀A⊔B=[2N] ∃x∈ZR
A,B
	​

(x)≥cN.

Equivalently,

∃N
0
	​

 ∀N≥N
0
	​

m
N
	​

≥cN.

The negation is

∀N
0
	​

 ∃N≥N
0
	​

 ∃A⊔B=[2N]∣A∣=∣B∣=Nand∀x, R
A,B
	​

(x)<cN.

Thus proving c
∗
	​

≥α means proving

m
N
	​

≥αN−o(N).

Proving c
∗
	​

≤β means constructing infinitely many N and balanced partitions with

M(A,B)≤βN+o(N).
Basic symmetries and invariants

Swapping A,B gives

R
B,A
	​

(x)=R
A,B
	​

(−x).

Reflecting the interval by i↦2N+1−i also changes x to −x. Therefore only the unordered pair of profiles

{R(x),R(−x)}

matters.

The total number of ordered pairs (a,b)∈A×B is N
2
, so

x∈Z
∑
	​

R(x)=N
2
.

There are at most 4N−2 nonzero possible differences. Hence

M(A,B)≥
4N−2
N
2
	​

.

Therefore

c
∗
	​

≥
4
1
	​

.

This is the elementary averaging lower bound.

Signed-sequence reformulation

Define

s
i
	​

={
+1,
−1,
	​

i∈A,
i∈B.
	​


Then

i=1
∑
2N
	​

s
i
	​

=0.

Let

S
k
	​

=
i=1
∑
k
	​

s
i
	​

,S
0
	​

=S
2N
	​

=0,

and for 1≤d≤2N−1,

C
d
	​

=
i=1
∑
2N−d
	​

s
i
	​

s
i+d
	​

.

For d>0,

R(d)=
4
1
	​

i=1
∑
2N−d
	​

(1+s
i+d
	​

)(1−s
i
	​

),

so

R(d)=
4
2N−d−C
d
	​

−S
d
	​

−S
2N−d
	​

	​

.

Similarly,

R(−d)=
4
2N−d−C
d
	​

+S
d
	​

+S
2N−d
	​

	​

.

Thus

R(d)+R(−d)=
2
2N−d−C
d
	​

	​

,

and

R(d)−R(−d)=−
2
S
d
	​

+S
2N−d
	​

	​

.

Therefore

max(R(d),R(−d))=
4
2N−d−C
d
	​

+∣S
d
	​

+S
2N−d
	​

∣
	​

.

So the problem is exactly equivalent to minimizing, over all balanced sign sequences s
1
	​

,…,s
2N
	​

,

1≤d≤2N−1
max
	​

4
2N−d−C
d
	​

+∣S
d
	​

+S
2N−d
	​

∣
	​

.

This is a verified exact reformulation.

Verified upper construction: c
∗
	​

≤
2
1
	​


Assume N=2m. Let

A={m+1,m+2,…,3m},

and

B={1,…,m}∪{3m+1,…,4m}.

Then ∣A∣=∣B∣=2m=N.

For x>0, a solution to a−b=x must have b∈{1,…,m}, because if b∈{3m+1,…,4m}, then b+x>3m∈
/
A. Hence

R(x)≤m=
2
N
	​

.

For x<0, by symmetry the only possible contributions come from b∈{3m+1,…,4m}, again giving

R(x)≤m=
2
N
	​

.

Also R(0)=0. Therefore

M(A,B)≤
2
N
	​

.

So for infinitely many N,

m
N
	​

≤
2
N
	​

,

and hence

c
∗
	​

≤
2
1
	​

.

Thus the fully verified first-principles bounds obtained so far are

4
1
	​

≤c
∗
	​

≤
2
1
	​

.
	​

Phase 1: Breadth-first strategy search
Strategy	Description	Hidden assumption checked	Obstacle	Status
Direct averaging	Use ∑
x
	​

R(x)=N
2
	Difference support size ≤4N−2	Stops at 1/4	Verified
Contradiction	Assume R(x)<cN for all x	Must translate to all d	Needs stronger global constraint	Partial
Construction	Build low-overlap partitions	Equal-size condition checked	Only gives 1/2	Verified
Induction on N	Remove two points and compare profiles	Boundary changes are large	Overlaps shift nonlocally	Failed
Transfinite/limit induction	Pass to limiting measurable sets	Needs compactness and recovery	Gives reduction, not exact value	Partial
Cardinal arithmetic	Count possible differences	Support ≤4N−2	Gives only 1/4	Verified
Diagonalization	Try to avoid high values of R(x)	Must preserve balance	Local choices create future collisions	Failed
Compactness	Convert to continuum convolution problem	Requires tightness of step functions	Continuous optimum unknown here	Reduction
Density argument	Use interval densities of A,B	Need uniform local imbalance control	Prefix sums can oscillate	Partial
Reflection argument	Use endpoint asymmetry	Reflection symmetry verified	Does not force large overlap	Weak
Auxiliary structure	Use sign walk S
k
	​

, autocorrelations C
d
	​

	Exact formulas verified	Need nonlinear inequality	Promising but incomplete
Counterexample search	Try to beat 1/2 constructively	Must certify all x	No rigorous construction found	Incomplete

Top three branches selected:

Signed-walk/autocorrelation branch.

Interval-energy branch.

Continuum compactness branch.

Phase 2: New definitions and invariants
Definition 1: symmetric overlap

For d>0, define

U
d
	​

=R(d)+R(−d).

Then

U
d
	​

=
2
2N−d−C
d
	​

	​

.

This measures the number of unordered cross-color pairs at distance d.

Definition 2: skew overlap

Define

D
d
	​

=R(d)−R(−d).

Then

D
d
	​

=−
2
S
d
	​

+S
2N−d
	​

	​

.

This measures the imbalance between right-facing and left-facing cross pairs.

Definition 3: two-sided boundary imbalance

Define

T
d
	​

=S
d
	​

+S
2N−d
	​

.

Then

max(R(d),R(−d))=
4
2N−d−C
d
	​

+∣T
d
	​

∣
	​

.

Thus, if M(A,B)≤M, then for every d,

C
d
	​

≥2N−d+∣T
d
	​

∣−4M.
(1)

This is stronger than the crude inequality

C
d
	​

≥2N−d−4M.
Definition 4: autocorrelation sum constraint

Because ∑
i
	​

s
i
	​

=0,

0=(
i=1
∑
2N
	​

s
i
	​

)
2
=2N+2
d=1
∑
2N−1
	​

C
d
	​

.

Hence

d=1
∑
2N−1
	​

C
d
	​

=−N.
(2)

Combining (1) and (2), if M(A,B)≤M, then

−N=
d=1
∑
2N−1
	​

C
d
	​

≥
d=1
∑
2N−1
	​

(2N−d−4M)+
d=1
∑
2N−1
	​

∣T
d
	​

∣.

Since

d=1
∑
2N−1
	​

(2N−d)=N(2N−1),

we get

−N≥(2N−1)(N−4M)+
d=1
∑
2N−1
	​

∣T
d
	​

∣.

Therefore

d=1
∑
2N−1
	​

∣T
d
	​

∣≤(2N−1)(4M−N)−N.
(3)

This immediately forces M≥N/4+O(1), recovering the trivial lower bound, but it also shows that any partition with M close to N/4 must have very small average two-sided boundary imbalance.

This is a real structural constraint, but by itself it does not force M above N/4.

Phase 3A: Signed-walk branch

Assume for contradiction that

M(A,B)≤cN

for some fixed c<1/2.

Then for all d,

2N−d−C
d
	​

+∣T
d
	​

∣≤4cN.
(4)

Equivalently,

C
d
	​

≥2N−d+∣T
d
	​

∣−4cN.
(5)

For small d, the term 2N−d−4cN is positive whenever

d<(2−4c)N.

Thus, for all such d, C
d
	​

 is forced to be positive unless the boundary term is somehow negative, which it cannot be because ∣T
d
	​

∣≥0. Therefore small-distance autocorrelations must be strongly positive.

However, the total autocorrelation identity

d=1
∑
2N−1
	​

C
d
	​

=−N

requires enough negative autocorrelation at larger distances.

The obstruction is: large d has smaller support length 2N−d, so C
d
	​

 can become quite negative without contradicting the pointwise bound

C
d
	​

≥−(2N−d).

Trying to combine only

C
d
	​

≥2N−d−4cN

with

C
d
	​

≥−(2N−d)

again gives only c≥1/4. The boundary term ∣T
d
	​

∣ is the extra structure, but inequality (3) permits ∣T
d
	​

∣ to be nontrivial once c>1/4.

So this branch proves:

c
∗
	​

≥
4
1
	​

,

and gives a necessary structural condition for near-extremizers, but it does not prove the optimal value.

Phase 3B: Interval-energy branch

For h≥1, define the local cross-energy

W
h
	​

=
d=1
∑
h−1
	​

(h−d)U
d
	​

.

Since

U
d
	​

=R(d)+R(−d)≤2M,

we have

W
h
	​

≤2M
d=1
∑
h−1
	​

(h−d)=Mh(h−1).
(6)

On the other hand,

U
d
	​

=#{(i,j):1≤i<j≤2N, j−i=d, s
i
	​


=s
j
	​

}.

Thus W
h
	​

 counts unlike-colored pairs (i,j) with distance <h, weighted by h−(j−i). Equivalently,

W
h
	​

=
1≤i<j≤2N
∑
	​

(h−(j−i))
+
	​

⋅1
s
i
	​


=s
j
	​

	​

.

In sign notation,

1
s
i
	​


=s
j
	​

	​

=
2
1−s
i
	​

s
j
	​

	​

.

So

W
h
	​

=
2
1
	​

1≤i<j≤2N
∑
	​

(h−(j−i))
+
	​

(1−s
i
	​

s
j
	​

).

A lower bound on W
h
	​

, valid for every balanced sign sequence, would imply through (6)

M≥
h(h−1)
W
h
	​

	​

.

The difficulty is that W
h
	​

 can be reduced by separating the two colors into large blocks, which is exactly what the interval construction does. For small h, no strong universal lower bound exists. For h proportional to N, one obtains nontrivial constraints, but the clean lower bounds derivable here still do not exceed the already established 1/4 without additional information about the sign-walk profile.

This branch therefore gives another route to c
∗
	​

≥1/4, but no exact optimum.

Phase 3C: Continuum compactness branch

Scale the interval by N. Given A⊂[2N], define the step function

f
N
	​

(t)=1
A
	​

(⌈Nt⌉)

on [0,2], with values in {0,1}, and with

∫
0
2
	​

f
N
	​

(t)dt=1.

The complement is 1−f
N
	​

.

The normalized overlap

N
1
	​

R(⌊Nt⌋)

formally approximates

Φ
f
	​

(t)=∫
R
	​

f(u+t)(1−f(u))du,

where f is supported on [0,2] and satisfies

0≤f≤1,∫
0
2
	​

f=1.

The continuum relaxation becomes:

f
inf
	​

∥Φ
f
	​

∥
∞
	​

.

If one could prove compactness plus a no-relaxation-loss theorem showing that extremizers may be taken with f∈{0,1} almost everywhere and that discrete partitions approximate them with no loss, then

c
∗
	​

=
E⊂[0,2]
∣E∣=1
	​

inf
	​

t
sup
	​

∣E∩(E
c
+t)∣.

This is a clean reformulation, but it is not a solution. It moves the problem from a finite combinatorial overlap problem to a continuum convolution extremal problem.

The unresolved core becomes:

Determine 
E⊂[0,2]
∣E∣=1
	​

inf
	​

t
sup
	​

∣E∩(E
c
+t)∣.

I did not derive that value from first principles.

Phase 4: Attacks on verified lemmas
Attack on total-pair lower bound

Claim:

x
∑
	​

R(x)=N
2
.

Every ordered pair (a,b)∈A×B determines exactly one integer x=a−b. Conversely each counted representation is such a pair. Therefore the identity is exact.

The possible nonzero differences are

−(2N−1),…,−1,1,…,2N−1,

so there are 4N−2 of them. Thus

M(A,B)≥
4N−2
N
2
	​

.

No hidden assumption found.

Attack on signed formula

For d>0,

1
A
	​

(i+d)=
2
1+s
i+d
	​

	​

,1
B
	​

(i)=
2
1−s
i
	​

	​

.

Therefore

R(d)=
i=1
∑
2N−d
	​

4
(1+s
i+d
	​

)(1−s
i
	​

)
	​

.

Expanding gives

R(d)=
4
1
	​

[2N−d+
i=1
∑
2N−d
	​

s
i+d
	​

−
i=1
∑
2N−d
	​

s
i
	​

−
i=1
∑
2N−d
	​

s
i
	​

s
i+d
	​

].

Now

i=1
∑
2N−d
	​

s
i+d
	​

=
j=d+1
∑
2N
	​

s
j
	​

=−S
d
	​

,

and

i=1
∑
2N−d
	​

s
i
	​

=S
2N−d
	​

.

So

R(d)=
4
2N−d−C
d
	​

−S
d
	​

−S
2N−d
	​

	​

.

The formula for R(−d) follows symmetrically. No hidden assumption found.

Attack on interval construction

For N=2m,

A=[m+1,3m],B=[1,m]∪[3m+1,4m].

For x>0, b+x∈A implies b<3m, so b must lie in the left block [1,m]. That block has size m, hence R(x)≤m.

For x<0, the same argument after reflection gives R(x)≤m.

Thus M≤m=N/2. No hidden assumption found.

Formal verified theorem pool
Lemma 1: Difference-count identity

For every balanced partition,

x
∑
	​

R(x)=N
2
.

Dependencies: definition of R(x).

Lemma 2: Trivial lower bound

For every balanced partition,

M(A,B)≥
4N−2
N
2
	​

.

Dependencies: Lemma 1 and support size ≤4N−2.

Lemma 3: Signed overlap formula

For every balanced sign sequence and 1≤d≤2N−1,

R(d)=
4
2N−d−C
d
	​

−S
d
	​

−S
2N−d
	​

	​

,
R(−d)=
4
2N−d−C
d
	​

+S
d
	​

+S
2N−d
	​

	​

.

Dependencies: sign encoding.

Lemma 4: Symmetric maximum formula

For every d>0,

max(R(d),R(−d))=
4
2N−d−C
d
	​

+∣S
d
	​

+S
2N−d
	​

∣
	​

.

Dependencies: Lemma 3.

Lemma 5: Autocorrelation sum identity

For every balanced sign sequence,

d=1
∑
2N−1
	​

C
d
	​

=−N.

Dependencies: ∑
i
	​

s
i
	​

=0.

Lemma 6: Middle-block construction

For infinitely many N,

m
N
	​

≤
2
N
	​

.

Dependencies: explicit construction.

Corollary

The following bound is fully proved from first principles:

4
1
	​

≤c
∗
	​

≤
2
1
	​

.
	​


No proof of the exact optimal constant was obtained.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified lemmas and bounds above.

COMPLETENESS_SCORE: 25/100. The problem was formalized exactly, and the elementary bounds were proved, but the exact optimal constant was not determined.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the stated partial results. The signed-sequence reformulation and the bounds survived local checks; no unproved exact-value claim was made.

RESOURCE_USAGE: approximately 100% of the reasoning budget allocated to this response; 3 main branches explored; 6 verified lemmas generated; 4 failed or incomplete proof frameworks retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

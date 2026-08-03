# Erdős Problem #126 [unsolved] 24%

---

## ChatGPT Response

Phase 0: Formalization

Let

N
+
	​

={1,2,3,…}.

Define a set A⊂(1,∞) to be admissible if

∀x,y∈A,x

=y⟹∀k∈N
+
	​

,∣kx−y∣≥1.

For each x>1, define the forbidden open set

F
x
	​

=
k≥1
⋃
	​

(kx−1,kx+1).

Then A is admissible iff

∀x∈A,(A∖{x})∩F
x
	​

=∅.

The two target conclusions are:

T
1
	​

(A):
x∈A
∑
	​

xlogx
1
	​

<∞,

and

T
2
	​

(A):H
A
	​

(n):=
x<n
x∈A
	​

∑
	​

x
1
	​

=o(logn).

The problem asks whether

∀A⊂(1,∞),A countably infinite and admissible⟹T
1
	​

(A),

or at least

∀A⊂(1,∞),A countably infinite and admissible⟹T
2
	​

(A).
Negations

Negation of T
1
	​

:

∃A admissible countably infinite such that 
x∈A
∑
	​

xlogx
1
	​

=∞.

Negation of T
2
	​

:

∃A admissible countably infinite, ∃ε>0, ∃n
j
	​

→∞

such that

x<n
j
	​

x∈A
	​

∑
	​

x
1
	​

≥εlogn
j
	​


for every j.

Equivalent pairwise formulation

Since k=1 is allowed, admissibility immediately implies

x

=y∈A⟹∣x−y∣≥1.

Thus A can be written increasingly as

A={a
1
	​

<a
2
	​

<a
3
	​

<⋯}

with

a
j+1
	​

−a
j
	​

≥1.

For a
i
	​

<a
j
	​

, the condition is equivalent to

dist(
a
i
	​

a
j
	​

	​

,N
+
	​

)≥
a
i
	​

1
	​

.

Indeed,

∣ka
i
	​

−a
j
	​

∣=a
i
	​

	​

k−
a
i
	​

a
j
	​

	​

	​

.

So admissibility means that no ratio a
j
	​

/a
i
	​

 is within 1/a
i
	​

 of a positive integer.

Immediate cardinal estimates

Because the elements are 1-separated,

∣A∩[1,N]∣≤N+O(1).

Therefore

x<N
x∈A
	​

∑
	​

x
1
	​

≤logN+O(1),

and

x<N
x∈A
	​

∑
	​

xlogx
1
	​

≤loglogN+O(1).

The desired conclusions require a genuine improvement over mere separation.

Verified elementary lemmas
Lemma 1: Pairwise separation

If A is admissible, then for all distinct x,y∈A,

∣x−y∣≥1.

Proof.
Take k=1 in the defining condition. Then

∣1⋅x−y∣=∣x−y∣≥1.

So the claim follows. ∎

Lemma 2: Separated counting bound

If A⊂(1,∞) is admissible, then

∣A∩[1,N]∣≤N+1.

Proof.
By Lemma 1, distinct points of A∩[1,N] are separated by distance at least 1. A 1-separated subset of an interval of length N−1 has at most N+1 points. ∎

Lemma 3: Dilation stability

If A is admissible and λ≥1, then

λA:={λx:x∈A}

is admissible.

Proof.
For distinct x,y∈A and k≥1,

∣k(λx)−λy∣=λ∣kx−y∣≥λ≥1.

Thus λA is admissible. ∎

Lemma 4: Integer primitive sets embed as admissible sets

Let B⊂N∩(1,∞) be primitive, meaning no distinct b,c∈B satisfy c=kb for an integer k≥2. Then B is admissible as a subset of (1,∞).

Proof.
Take distinct b,c∈B and k≥1. Since b,c,k are integers, kb−c∈Z. If ∣kb−c∣<1, then kb−c=0, so c=kb.

If k=1, this gives c=b, impossible because b

=c. If k≥2, then c=kb, contradicting primitiveness. Hence ∣kb−c∣≥1. ∎

This shows that any proof must handle the integer primitive-set case as a special subcase.

Phase 1: Breadth-first strategy search

I tested the following independent proof/counterexample strategies.

Strategy	Description	Main obstacle
Direct proof	Use ratio avoidance dist(y/x,N)≥1/x to prove harmonic sparsity	Needs a global packing theorem for ratios
Contradiction	Assume H
A
	​

(N)≥εlogN, force some y≈kx	Requires a density-to-dilation collision lemma
Construction	Build a dense admissible A by choosing points outside prior forbidden intervals	Finite-stage construction works, infinite density control fails
Induction	Add elements one at a time while preserving sparsity bounds	Induction gives existence, not universal upper bounds
Transfinite induction	Well-order A and assign ranks/forbidden mass	No monotone rank controlling all future dilates found
Cardinal arithmetic	Use 1-separation plus forbidden neighborhoods	Only gives O(N), too weak
Diagonalization	Construct A avoiding all forbidden relations while forcing divergent sum	Divergence requires too much reciprocal mass
Compactness	Prove finite obstruction: dense finite sets force violation	Plausible, but finite statement not established
Density/sieve	Treat each x∈A as forbidding residue interval near 0modx	Boundary points can survive full-measure sieves
Reflection	Pass from large A∩[1,N] to scaled local configurations	Scaling error changes the forbidden radius
Auxiliary graph	Graph vertices A, edges for near-dilation conflicts	Admissibility says graph has no edges; need extremal bound
Counterexample search	Use affine lattices or boundary chains y=kx±1	Pairwise compatibility quickly creates new near-dilations

Top three branches:

Density/sieve contradiction.

Block construction counterexample.

Integer/rounding reduction.

Phase 2: New definitions and invariants
Definition: dilation shadow

For B⊂(1,∞), define

F(B)=
x∈B
⋃
	​

k≥1
⋃
	​

(kx−1,kx+1).

Admissibility says

A∩F(A∖{y})=∅

for every y∈A, ignoring the self-point issue.

Definition: reciprocal mass

For B⊂(1,∞),

M(B;N)=
x≤N
x∈B
	​

∑
	​

x
1
	​

.

The desired T
2
	​

 is

M(A;N)=o(logN).
Definition: logarithmic mass
L(B)=
x∈B
∑
	​

xlogx
1
	​

.

The desired T
1
	​

 is L(A)<∞.

Definition: local dilation density

For finite B⊂(1,∞), interval I⊂(1,∞),

D
B
	​

(I)=
∣I∣
∣F(B)∩I∣
	​

.

For one x, heuristically,

D
{x}
	​

([1,N])≈
x
2
	​

.

So a naive union bound gives

D
B
	​

([1,N])≲2
x∈B
∑
	​

x
1
	​

.

But this is not decisive because admissible sets may lie on boundaries of forbidden intervals.

Phase 3: Parallel branch exploration
Branch A: Density/sieve proof attempt

Goal: prove that if

x<N
x∈A
	​

∑
	​

x
1
	​


is a positive proportion of logN, then some pair x,y∈A satisfies ∣kx−y∣<1.

A natural finite target is:

Finite collision lemma. For every ε>0, there exists N
0
	​

 such that if B⊂[1,N] is 1-separated and

b∈B
∑
	​

b
1
	​

≥εlogN,

then there exist distinct x,y∈B and k≥1 with ∣kx−y∣<1.

If true, this proves T
2
	​

.

Gap node A1

The finite collision lemma is the central unresolved statement.

Attacks tried:

Measure union bound.
Fails because forbidden sets may cover most of the line while admissible points survive on interval endpoints.

Closed interval strengthening.
Replace ∣kx−y∣<1 by ∣kx−y∣≤1. Invalid: the original condition allows equality.

Random dilation averaging.
Needs independence between residues ymodx, unavailable.

Graph extremal argument.
Build a graph on B, connect x<y if y is near a multiple of x. Need prove dense reciprocal mass forces an edge. No verified extremal inequality found.

Logarithmic interval packing.
In log-coordinates, forbidden neighborhoods have width about 1/y. Overlaps are too uncontrolled.

Dyadic decomposition.
Inside [N,2N], the condition is mostly just 1-separation, so single-scale arguments are weak.

Multiscale pigeonhole.
Large reciprocal mass requires many occupied scales, but a collision between scales still needs a ratio-near-integer argument.

Residue sieve.
Each x forbids an interval of length 2 modulo x. Boundary phenomena again prevent a clean density contradiction.

Energy method.
Count triples (x,y,k) with ∣kx−y∣<1. Expected count is large under randomness, but no deterministic lower bound was proved.

Compactness/minimal counterexample.
Assume a minimal finite counterexample to the collision lemma. Could not derive structural rigidity strong enough to contradict minimality.

Status: unresolved.

Branch B: Counterexample construction attempt

Try to build an admissible set with

x∈A
∑
	​

xlogx
1
	​

=∞.

A recursive construction can always add one sufficiently large point outside finitely many forbidden intervals, provided the union of previous forbidden sets does not cover everything. But to force divergence, one needs add enough reciprocal mass.

For a finite previous set P, the forbidden measure inside a long interval I=[T,T+L] satisfies

∣F(P)∩I∣≤
p∈P
∑
	​

(
p
2L
	​

+O(1))=2L
p∈P
∑
	​

p
1
	​

+O
P
	​

(1).

Thus if

p∈P
∑
	​

p
1
	​

<
2
1
	​

,

then large intervals contain many allowed points.

But divergence of

x∈A
∑
	​

xlogx
1
	​


forces divergence of

x∈A
∑
	​

x
1
	​


as well, since 1/logx>0. Therefore the finite-stage union-bound construction cannot continue with a uniformly positive allowed density.

Gap node B1

Can one exploit massive overlap of forbidden intervals to keep allowed boundary sets large even when

x∈A
∑
	​

x
1
	​

=∞?

Attacks tried:

Common lattice construction.
Integer primitive sets work, but they do not immediately yield divergence of the weighted sum.

Shifted lattice m+α.
Fails for dense index sets because (k−1)α comes close to integers.

Affine lattice λm+c.
Reduces to avoiding many affine divisibility relations.

Boundary chain x
n+1
	​

=k
n
	​

x
n
	​

+1.
Handles one predecessor but not all earlier predecessors.

Block construction.
Dense blocks inside [N,2N] are internally admissible, but their future dilation shadows are too large.

Superlacunary blocks.
Easy to preserve admissibility, but then

∑1/(xlogx)

tends to converge.

Random greedy construction.
Likely produces admissible sets, but no verified lower bound on logarithmic mass.

Choose all points on endpoints of a fixed forbidden system.
Works for x=2, forcing future points to odd integers, but then the problem reduces to integer primitive behavior.

Use rationally independent numbers.
Avoids exact equality but not absolute distance <1.

Recursive simultaneous congruence.
No consistent high-density system of endpoint congruences was found.

Status: unresolved.

Branch C: Integer or rounding reduction

Because A is 1-separated, one may attempt to map each x∈A to an integer m(x), for example m(x)=⌊x⌋ or m(x)=⌈x⌉, and prove that the resulting integer set is approximately primitive.

The obstruction is that rounding errors are multiplied by k. If y≈kx, then

m(y)−km(x)

contains an error of size roughly k, not O(1). Since k may be as large as y/x, rounding does not preserve the forbidden relation.

Gap node C1

Find a discretization map ϕ:(1,∞)→N such that admissibility of A forces a primitive-like property of ϕ(A).

Attacks tried:

floor map: error grows with k.

nearest-integer map: same issue.

logarithmic binning: loses additive 1-scale information.

multiplicative binning: ratio-near-integer condition becomes too coarse.

adaptive binning by local scale: incompatible across different x.

map x↦⌊Cx⌋: fixed C does not remove growing error.

random shift before rounding: may help average error, but no deterministic conclusion.

use continued fractions of ratios: too pair-dependent.

embed into a semigroup graph: promising but no completed inequality.

replace primitiveness by approximate primitiveness: still needs a new theorem.

Status: unresolved.

Phase 4: Local verification and adversarial attacks
Verified facts that survived attack

A is 1-separated.

Hence ∣A∩[1,N]∣=O(N).

Hence H
A
	​

(N)=O(logN).

Integer primitive sets are admissible.

Dilation by λ≥1 preserves admissibility.

Measure-based forbidden-set arguments fail unless endpoint phenomena are handled.

Candidate proof failure

The tempting proof is:

large reciprocal mass⇒large forbidden measure⇒some A-point lies in a forbidden interval.

The invalid step is the last one. A countable 1-separated set can lie entirely on the boundary of a large union of open intervals. The example x=2 is decisive:

F
2
	​

=
k≥1
⋃
	​

(2k−1,2k+1),

whose complement in (1,∞) is essentially the odd integers. Thus forbidden intervals can cover almost all measure while leaving infinitely many admissible boundary points.

So any valid proof must control boundary accumulation, not just measure.

Candidate counterexample failure

The tempting construction is:

choose dense blocks far apart, avoiding previous forbidden intervals.

The invalid step is assuming finite-stage freedom remains compatible with divergent reciprocal mass. Once the accumulated reciprocal mass

x∈A
∑
	​

x
1
	​


diverges, the naive allowed-density estimate becomes useless. Dense future blocks may be completely blocked unless one exploits exact boundary alignment. No such alignment construction was completed.

Dependency graph of established results
Admissibility⇒pairwise 1-separation⇒∣A∩[1,N]∣=O(N)⇒H
A
	​

(N)=O(logN).

Also:

integer primitive B⇒B admissible.

And:

A admissible, λ≥1⇒λA admissible.

No verified chain was obtained from admissibility to either

x∈A
∑
	​

xlogx
1
	​

<∞

or

H
A
	​

(N)=o(logN).

No verified construction was obtained contradicting either conclusion.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100
This is confidence in the correctness of the verified lemmas and failure analysis above, not confidence in either target theorem.

COMPLETENESS_SCORE: 24/100
The elementary structure was formalized, and several natural proof/counterexample routes were attacked, but neither main target was proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 78/100
The verified lemmas survived direct attacks. The main proof and construction attempts did not survive.

RESOURCE_USAGE:
Reasoning budget used: approximately 100%.
Branches explored: 3 major branches, 12 initial strategies.
Lemmas generated: 4 verified elementary lemmas.
Failed proof attempts: 3 primary attempts, with 30 listed sub-attacks.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

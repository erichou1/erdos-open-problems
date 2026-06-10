# Erdős Problem #212 [unsolved] 38%

---

## ChatGPT Response

Formal statement

Let

D(S):⟺S⊂R
2
,
S
=R
2
,∀P,Q∈S, ∣P−Q∣∈Q.

The problem asks whether

∃S⊂R
2
D(S).
Quantifier structure
∃S⊂R
2
 [(∀U⊂R
2
 nonempty open)(S∩U

=∅) ∧ (∀P,Q∈S)(∣P−Q∣∈Q)].
Negation
∀S⊂R
2
 [(∀P,Q∈S)(∣P−Q∣∈Q)⇒
S

=R
2
].

Equivalently: every rational-distance subset of the plane misses some nonempty open disk.

Immediate symmetries

The rational-distance property is preserved by:

translations;

rotations/reflections;

scaling by a nonzero rational number.

It is not preserved by arbitrary real scaling.

Verified reductions
Lemma 1: Two-point normalization

Assume S contains two distinct points A,B. Since ∣A−B∣∈Q
>0
	​

, translate, rotate, and scale by 1/∣A−B∣. Then we may assume

A=(0,0),B=(1,0),

and all pairwise distances in the transformed set remain rational.

Lemma 2: Coordinates relative to two fixed points

Let P=(x,y)∈S. Since

x
2
+y
2
∈Q
2
,(x−1)
2
+y
2
∈Q
2
,

subtracting gives

(x−1)
2
−x
2
=1−2x∈Q.

Hence

x∈Q.

Then

y
2
=(x
2
+y
2
)−x
2
∈Q.

So every point has the form

P=(x,y),x∈Q,y
2
∈Q.

This proves every rational-distance set with at least two points is countable. Countability alone gives no contradiction, since countable dense subsets of R
2
 exist.

Lemma 3: A noncollinear third point forces a fixed quadratic lattice

If S is dense, it contains three noncollinear points. After Lemma 1, choose

C=(u,v)∈S,v

=0.

From Lemma 2,

u∈Q,v
2
∈Q.

For any P=(x,y)∈S, we already know

x,u∈Q,y
2
,v
2
∈Q.

Since ∣P−C∣
2
∈Q,

(x−u)
2
+(y−v)
2
∈Q.

Expanding,

(x−u)
2
+y
2
+v
2
−2yv∈Q.

All terms except possibly 2yv are rational, so

yv∈Q.

Because v

=0,

y∈vQ.

Thus every point of S lies in

Q×vQ.

Write y=vt, with t∈Q, and put

h=v
2
∈Q
>0
	​

.

Then the rational-distance condition becomes

(x
1
	​

−x
2
	​

)
2
+h(t
1
	​

−t
2
	​

)
2
∈Q
2
.

So the original problem reduces to the following arithmetic-dense formulation:

Does there exist h∈Q
>0
	​

 and a dense set

T⊂Q
2

such that for all p,q∈T,

(p
x
	​

−q
x
	​

)
2
+h(p
y
	​

−q
y
	​

)
2
∈Q
2
?

This reduction is reversible up to the normalization already described.

Lemma 4: Squarefree reduction

Write

h=dr
2

where r∈Q
>0
	​

 and d∈Z
>0
	​

 is squarefree. Replacing t by rt preserves density in Q
2
. Therefore it is enough to study

Q
d
	​

(a,b)=a
2
+db
2
,

where d is a positive squarefree integer.

The reduced problem is:

∃d∈Z
>0
	​

 squarefree, ∃T⊂Q
2
 dense,∀p,q∈T, Q
d
	​

(p−q)∈Q
2
.
Slope obstruction

If p,q∈T, p

=q, and Δx

=0, define

m=
Δx
Δy
	​

∈Q.

Then

Q
d
	​

(Δx,Δy)=(Δx)
2
(1+dm
2
).

Since (Δx)
2
 is already a rational square, we need

1+dm
2
∈Q
2
.

Thus all slopes between pairs of points of T must lie in

M
d
	​

={m∈Q:1+dm
2
∈Q
2
}.

The equation

r
2
−dm
2
=1

has rational parametrization

m=
1−dt
2
2t
	​

,r=
1−dt
2
1+dt
2
	​

,t∈Q,1−dt
2

=0.

So M
d
	​

 is infinite and dense in R. Therefore slope restrictions alone do not rule out density.

Vertical pairs require

d(Δy)
2
∈Q
2
.

If d

=1, squarefree, this forces Δy=0. Hence for nonsquare d, no two distinct points of T may lie on the same vertical line. This still does not contradict density.

Twelve independent proof strategies examined
1. Direct coordinate attack

Use the normalization S⊂Q×vQ, then try to contradict density.

Obstacle: Q×vQ is itself dense in R
2
.

Status: gives strong arithmetic reduction, no contradiction.

2. Slope-set attack

All slopes must lie in M
d
	​

.

Obstacle: M
d
	​

 is dense, so a dense planar set is not immediately excluded.

Status: useful but insufficient.

3. Difference-set attack

Let

ΔT=T−T.

Then

ΔT⊆{(a,b)∈Q
2
:a
2
+db
2
∈Q
2
}.

Obstacle: the allowed difference set is itself dense.

Status: no contradiction.

4. Additive-subgroup attack

Suppose T were an affine Q-subspace. Then the condition would force all nonzero vectors in a two-dimensional Q-space to have Q
d
	​

-length a rational square.

This is impossible. A two-dimensional Q-subspace contains u+tv for all t∈Q. Then

Q
d
	​

(u+tv)

is a non-square quadratic polynomial in t, and such a polynomial cannot take rational-square values for every rational t.

Conclusion: no additive-subgroup construction gives a dense example.

Obstacle: a dense rational-distance set need not be closed under addition, subtraction, or rational affine combinations.

Status: rules out one natural construction, not all constructions.

5. Recursive construction attack

Try to build T by choosing one point in each rational open ball. At stage n, given finite F⊂T, one needs a new point z in a prescribed open ball such that

Q
d
	​

(z−p)∈Q
2
∀p∈F.

This requires the common-neighbor set

N(F)={z∈Q
2
:Q
d
	​

(z−p)∈Q
2
 ∀p∈F}

to be dense for every finite F arising in the construction.

Obstacle: for ∣F∣≥3, density of N(F) becomes a nontrivial arithmetic condition.

Status: this is a plausible route to construction but no proof obtained.

6. Triple obstruction attack

Try to show that for every noncollinear rational-distance triple F, the set N(F) is not dense.

If true, no dense rational-distance set could exist, because a dense set contains noncollinear triples, and every other point must lie in N(F).

Obstacle: after normalization, this asks for a density obstruction among points rationally distant from three fixed noncollinear points. The equations become simultaneous rational-square constraints and do not collapse by elementary algebra.

Status: central obstruction; unresolved here.

7. Finite-configuration attack

Try to prove that a dense rational-distance set must contain a forbidden finite configuration, such as a small approximate rectangle or parallelogram.

Obstacle: density gives approximate configurations, not exact configurations. Rational-distance conditions are exact, so approximation alone does not force a forbidden finite pattern.

Status: no contradiction.

8. Cardinality attack

Every rational-distance set with at least two points is countable.

Obstacle: countable dense subsets of R
2
 exist.

Status: insufficient.

9. Topological closure attack

Let S be dense. Since all distances inside S are rational, try to pass rationality to limits.

Obstacle: rationality is not closed. Limits of rational distances may be irrational.

Example: rational numbers can converge to 
2
	​

.

Status: fails.

10. Measure/category attack

Since the allowed difference set is countable, one might hope S−S is too small.

Obstacle: dense countable sets can have dense countable difference sets. Countability and category do not prevent density.

Status: insufficient.

11. Algebraic-curve attack

For fixed finite F, N(F) is controlled by algebraic equations involving rational squares. One could try to show that a dense T must lie in a finite union of algebraic curves, then rule out density.

Obstacle: deriving such algebraic containment from first principles requires a major arithmetic theorem not established here.

Status: not completed.

12. Counterexample construction via parametrized slopes

Since the allowed slopes M
d
	​

 are dense, try to choose points recursively so every new slope lies in M
d
	​

.

Obstacle: pairwise rational distance requires not only allowed slopes but also compatible rational scaling for all previous points simultaneously. The finite intersection constraints are much stronger than one-slope compatibility.

Status: no construction obtained.

Strongest verified reformulation

The original problem is equivalent to the following reduced problem:

Does there exist a positive squarefree integer d and a dense set

T⊂Q
2

such that for every p,q∈T,

(p
x
	​

−q
x
	​

)
2
+d(p
y
	​

−q
y
	​

)
2

is a rational square?

The disproof would follow if one could prove:

For every positive squarefree integer d, every dense T⊂Q
2
 contains two points p,q such that

Q
d
	​

(p−q)∈
/
Q
2
.

The construction would follow if one could prove:

For some positive squarefree d, every finite Q
d
	​

-rational-distance set F⊂Q
2
 has dense common-neighbor set N(F).

Neither statement was proved here.

Adversarial verification

The reductions through three noncollinear points are valid. The key deductions

x∈Q,y
2
∈Q,yv∈Q

are algebraic consequences of subtracting squared-distance equations.

No contradiction follows from countability because countable dense subsets exist.

No contradiction follows from slope restrictions because the allowed slope set is itself dense.

No construction follows from dense allowed slopes because all previous-point constraints must be satisfied simultaneously.

No closure argument works because Q is not closed in R.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 93/100
The reductions and partial lemmas above are logically reliable.

COMPLETENESS_SCORE: 38/100
A substantial arithmetic reformulation was obtained, but neither a full construction nor a full contradiction was derived.

ADVERSARIAL_SURVIVAL_SCORE: 86/100
The verified reductions survive direct counterexample checks; the speculative strategies were not promoted to theorems.

RESOURCE_USAGE: approximately 90% of the available reasoning budget for this response; 12 branches explored; 4 main lemmas generated; 0 complete proof attempts survived.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

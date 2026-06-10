# Erdős Problem #495 [unsolved] 42%

---

## ChatGPT Response

Complete formalization

Let

F
α,β
	​

(n)=n∥nα∥∥nβ∥.

The question asks whether the following universal statement is true:

∀α,β∈R,
n→∞
liminf
	​

F
α,β
	​

(n)=0.

Expanded quantifier form:

∀α,β∈R, ∀ε>0, ∀N∈N, ∃n≥N

such that

n∥nα∥∥nβ∥<ε.

Negation:

∃α,β∈R, ∃ε
0
	​

>0, ∃N
0
	​

∈N, ∀n≥N
0
	​

,
n∥nα∥∥nβ∥≥ε
0
	​

.

Equivalently, a counterexample is a pair (α,β) for which the product never gets smaller than a positive constant after some point.

Basic invariances

The expression depends only on α,β modulo integers, since

∥n(α+k)∥=∥nα+nk∥=∥nα∥

for every k∈Z.

It is also invariant under sign changes:

∥n(−α)∥=∥−nα∥=∥nα∥.

So the problem may be reduced to

α,β∈[0,1)

without loss of generality.

Boundary cases
Lemma 1: If α∈Q or β∈Q, then the desired limit inferior is 0.

Assume α=a/q with a,q∈Z, q≥1. For every n=kq,

nα=kq⋅
q
a
	​

=ka∈Z.

Therefore

∥nα∥=0.

Hence

n∥nα∥∥nβ∥=0

for infinitely many n, so

n→∞
liminf
	​

n∥nα∥∥nβ∥=0.

Thus any counterexample must have both α and β irrational.

Immediate necessary condition for a counterexample

Assume the negation holds. Then there exist ε
0
	​

>0 and N
0
	​

 such that

n∥nα∥∥nβ∥≥ε
0
	​


for all n≥N
0
	​

.

Since always

∥nβ∥≤
2
1
	​

,

we get

n∥nα∥⋅
2
1
	​

≥ε
0
	​

.

Therefore

n∥nα∥≥2ε
0
	​


for all n≥N
0
	​

. Similarly,

n∥nβ∥≥2ε
0
	​


for all n≥N
0
	​

.

So any counterexample must satisfy the one dimensional lower bounds

n≥1
inf
	​

n∥nα∥>0,
n≥1
inf
	​

n∥nβ∥>0,

after adjusting constants to cover finitely many small n.

Thus any counterexample must be a pair where both coordinates are individually badly approximable.

This is a verified necessary condition, not a proof or disproof.

Equivalent formulations

The original statement is equivalent to each of the following.

Hyperbolic orbit formulation

Let

x
n
	​

=nα(mod1),y
n
	​

=nβ(mod1).

Then the problem asks whether, for every (α,β), the orbit

(nα,nβ)(mod1)

enters the shrinking hyperbolic neighborhood

H
n,ε
	​

={(x,y)∈T
2
:∥x∥∥y∥<ε/n}

infinitely often for every ε>0.

Counterexample formulation

A counterexample is a pair (α,β) for which there exists c>0 such that

∥nα∥∥nβ∥≥
n
c
	​


for all sufficiently large n.

Rational dependence formulation

If 1,α,β are rationally dependent, then the desired result is provable.

Indeed, suppose

u+vα+wβ=0

with integers u,v,w, not all zero.

If w=0, then vα=−u, so α∈Q, already handled.

If w

=0, then

β=−
w
v
	​

α−
w
u
	​

.

Let q be a positive integer chosen later and let n=wq. Then

nβ=wq(−
w
v
	​

α−
w
u
	​

)=−vqα−uq.

Hence

∥nβ∥=∥−vqα−uq∥≤∣v∣∥qα∥.

Also

∥nα∥=∥wqα∥≤∣w∣∥qα∥.

By Dirichlet approximation, for infinitely many q,

∥qα∥<
q
1
	​

.

For such q,

n∥nα∥∥nβ∥≤∣w∣q⋅∣w∣∥qα∥⋅∣v∣∥qα∥=∣v∣w
2
q∥qα∥
2
<
q
∣v∣w
2
	​

.

As q→∞, this tends to 0.

Therefore, if 1,α,β are rationally dependent, the statement is true.

Thus any counterexample must satisfy all three conditions:

α,β∈
/
Q,
n≥1
inf
	​

n∥nα∥>0,
n≥1
inf
	​

n∥nβ∥>0,

and

1,α,β

are rationally independent.

Strategy search

I considered the following independent approaches.

Strategy	Core idea	Result
Direct proof	Force small ∥nα∥∥nβ∥ by pigeonhole	Gives only constant level bounds, not o(1)
Contradiction	Assume n∥nα∥∥nβ∥≥c eventually	Produces strong necessary conditions but no contradiction
Rational dependence	Reduce to one dimensional approximation	Fully proves dependent case
Induction on denominators	Use convergent denominators of α and test β	Fails in bounded approximation case
Transfinite induction	Organize possible counterexamples by approximation rank	No well founded rank found
Cardinal arithmetic	Compare size of forbidden sets to all pairs	Measure and cardinality do not decide universal truth
Diagonalization	Construct α,β avoiding all small product constraints	Constraints overlap too strongly to verify construction
Compactness	Try finite obstruction implies infinite obstruction	Shrinking targets prevent direct compactness
Density	Use density of (nα,nβ) in T
2
	Density alone cannot handle 1/n shrinking
Reflection	Pass to subsequences and induced rotations	No invariant forcing product decay found
Auxiliary structure	Define hyperbolic hitting ranks	Helps formalize the gap but does not prove it
Counterexample search	Try construct badly approximable independent pair	No verified construction obtained

The strongest verified progress is this reduction:

A proof for all α,β would follow if one could prove the statement for rationally independent pairs where both coordinates are badly approximable.

That reduced target is not solved here.

Main unresolved target

The remaining primary theorem is:

T:

For all irrational α,β such that 1,α,β are rationally independent and

n≥1
inf
	​

n∥nα∥>0,
n≥1
inf
	​

n∥nβ∥>0,

one has

n→∞
liminf
	​

n∥nα∥∥nβ∥=0.

I attacked this target in three main branches.

Branch A: Pigeonhole geometry

For N∈N, consider the N points

(nα,nβ)(mod1),1≤n≤N.

Partition [0,1)
2
 into rectangles of widths 1/A and heights 1/B, with AB<N. By pigeonhole, two orbit points land in the same rectangle. Their difference gives an integer m≤N satisfying

∥mα∥≤
A
1
	​

,∥mβ∥≤
B
1
	​

.

Thus

m∥mα∥∥mβ∥≤N⋅
A
1
	​

⋅
B
1
	​

.

Since pigeonhole requires AB<N, this yields only

m∥mα∥∥mβ∥≲1.

It does not force the product to approach 0.

Sanity check: no contradiction follows, because the argument naturally loses exactly the factor needed. This branch proves a bounded liminf upper bound, not a zero liminf.

Branch A fails to prove T.

Branch B: Continued denominator attack

Let q
k
	​

 be denominators giving strong approximation to α, so that

∥q
k
	​

α∥≲
q
k
	​

1
	​

.

Evaluate the target expression at n=q
k
	​

:

q
k
	​

∥q
k
	​

α∥∥q
k
	​

β∥.

If

q
k
	​

∥q
k
	​

α∥→0,

then the whole expression tends to 0, because

∥q
k
	​

β∥≤
2
1
	​

.

So the only difficult case is when

q
k
	​

∥q
k
	​

α∥

is bounded away from 0, exactly the badly approximable case.

Then this branch needs to prove that

∥q
k
	​

β∥

gets arbitrarily small along the denominator sequence of α. But rational independence and density of (nα,nβ) do not by themselves imply smallness along this specific sparse subsequence.

Thus Branch B reduces T to a new target:

S:
k
inf
	​

∥q
k
	​

β∥=0

for every rationally independent badly approximable pair.

No proof of S was obtained. Also, S may be stronger than necessary, because the original problem allows arbitrary n, not only denominators of α.

Branch B fails.

Branch C: Counterexample construction attempt

Assume we try to construct (α,β) such that

n∥nα∥∥nβ∥≥c

for all sufficiently large n.

For each n, the forbidden set is

E
n
	​

(c)={(α,β)∈[0,1)
2
:n∥nα∥∥nβ∥<c}.

Equivalently,

∥nα∥∥nβ∥<
n
c
	​

.

The measure of this forbidden set is comparable to

n
clogn
	​


up to constant factors, because the region ∣xy∣<c/n near the axes has logarithmic area.

The sum

n=1
∑
∞
	​

n
clogn
	​


diverges.

So a direct measure avoidance argument cannot prove that some pair avoids all E
n
	​

(c). Divergence does not prove that avoidance is impossible, but it blocks the simplest Cantor measure construction.

Branch C fails to construct a counterexample.

Verified theorem pool
Theorem 1

If either α or β is rational, then

n→∞
liminf
	​

n∥nα∥∥nβ∥=0.

Status: proved.

Theorem 2

If

n→∞
liminf
	​

n∥nα∥=0

or

n→∞
liminf
	​

n∥nβ∥=0,

then

n→∞
liminf
	​

n∥nα∥∥nβ∥=0.

Proof: since ∥nβ∥≤1/2,

n∥nα∥∥nβ∥≤
2
1
	​

n∥nα∥.

So if the right side has liminf 0, the product also has liminf 0. The same argument applies with α,β reversed.

Status: proved.

Theorem 3

If the original statement fails for some (α,β), then both α and β must be badly approximable in the sense that

n≥1
inf
	​

n∥nα∥>0,
n≥1
inf
	​

n∥nβ∥>0.

Status: proved.

Theorem 4

If 1,α,β are rationally dependent, then

n→∞
liminf
	​

n∥nα∥∥nβ∥=0.

Status: proved.

Dependency graph

The original theorem would follow from:

Theorem 1

plus

Theorem 2

plus

Theorem 4

plus the unresolved target T:

T: badly approximable, rationally independent case.

The only remaining case is exactly:

α,β irrational,
1,α,β rationally independent,
n≥1
inf
	​

n∥nα∥>0,
n≥1
inf
	​

n∥nβ∥>0.

No contradiction, construction, or complete proof was derived for that case.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96

COMPLETENESS_SCORE: 42

ADVERSARIAL_SURVIVAL_SCORE: 88

RESOURCE_USAGE: approximately 100 percent of the bounded response budget used, 12 strategies considered, 4 verified lemmas generated, 3 major failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

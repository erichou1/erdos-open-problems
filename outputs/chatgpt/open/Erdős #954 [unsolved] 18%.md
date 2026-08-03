# Erdős Problem #954 [unsolved] 18%

---

## ChatGPT Response

Phase 0: Formalization

Let

0=a
0
	​

<a
1
	​

<a
2
	​

<⋯

be defined recursively. For k≥1, define the finite representation functions

r
k
	​

(n):=#{(i,j):0≤i≤j≤k, j≥1, a
i
	​

+a
j
	​

=n},

and

R
k
	​

(x):=
n≤x
∑
	​

r
k
	​

(n)=#{(i,j):0≤i≤j≤k, j≥1, a
i
	​

+a
j
	​

≤x}.

Then

a
k+1
	​

=min{n∈Z
≥0
	​

:R
k
	​

(n)<n}.

For the completed infinite sequence, define

r(n):=#{(i,j):0≤i≤j, j≥1, a
i
	​

+a
j
	​

=n},
R(x):=
n≤x
∑
	​

r(n).

The question is whether

R(x)=x+O(x
1/4+o(1)
).

A standard precise interpretation is:

∀ε>0R(x)−x=O
ε
	​

(x
1/4+ε
).

Its negation is

∃ε>0∀C>0∃xR(x)−x>Cx
1/4+ε
.

Define the discrepancy

D(x):=R(x)−x.

The assertion is therefore

D(x)=O(x
1/4+o(1)
).
Basic structural lemmas
Lemma 1: The recursive minimum is well-defined

For fixed k, the total number of admissible pairs is

T
k
	​

=
j=1
∑
k
	​

(j+1)=
2
k(k+3)
	​

.

Thus R
k
	​

(n)≤T
k
	​

 for every n. Consequently,

R
k
	​

(T
k
	​

+1)≤T
k
	​

<T
k
	​

+1.

Hence the defining set for a
k+1
	​

 is nonempty, and

a
k+1
	​

≤
2
k(k+3)
	​

+1.
Lemma 2: Exact behavior at the new term

For every k≥1,

R
k
	​

(a
k+1
	​

)=a
k+1
	​

−1,

and

r
k
	​

(a
k+1
	​

)=0.
Proof

By minimality,

R
k
	​

(a
k+1
	​

−1)≥a
k+1
	​

−1.

Also R
k
	​

 is nondecreasing, so

R
k
	​

(a
k+1
	​

)≥R
k
	​

(a
k+1
	​

−1)≥a
k+1
	​

−1.

By definition,

R
k
	​

(a
k+1
	​

)<a
k+1
	​

.

Since it is integer-valued,

R
k
	​

(a
k+1
	​

)=a
k+1
	​

−1.

The same inequalities force

R
k
	​

(a
k+1
	​

−1)=a
k+1
	​

−1.

Therefore

r
k
	​

(a
k+1
	​

)=R
k
	​

(a
k+1
	​

)−R
k
	​

(a
k+1
	​

−1)=0.

Thus a
k+1
	​

 has no representation using only a
0
	​

,…,a
k
	​

. ∎

Lemma 3: Strict increase follows from the recursion

For every k≥1,

a
k+1
	​

>a
k
	​

.
Proof

For n<a
k
	​

, no pair involving the newly introduced index k has sum at most n, since every such pair has sum at least a
k
	​

. Hence

R
k
	​

(n)=R
k−1
	​

(n)≥n

by the minimality defining a
k
	​

.

At n=a
k
	​

, Lemma 2 applied at the preceding stage gives

R
k−1
	​

(a
k
	​

)=a
k
	​

−1.

Adding a
k
	​

 introduces the pair (0,k), whose sum is a
k
	​

, and introduces no other pair of sum at most a
k
	​

. Therefore

R
k
	​

(a
k
	​

)=R
k−1
	​

(a
k
	​

)+1=a
k
	​

.

Thus no n≤a
k
	​

 satisfies R
k
	​

(n)<n, so a
k+1
	​

>a
k
	​

. ∎

Lemma 4: The infinite discrepancy vanishes at every sequence element

For every k≥1,

R(a
k
	​

)=a
k
	​

,D(a
k
	​

)=0.
Proof

At stage k−1,

R
k−1
	​

(a
k
	​

)=a
k
	​

−1.

The pair (0,k) contributes one further representation at a
k
	​

. Every later term a
j
	​

, j>k, exceeds a
k
	​

, so no later pair has sum at most a
k
	​

. Hence

R(a
k
	​

)=a
k
	​

.

∎

Lemma 5: Nonnegativity of the discrepancy

For every integer x≥1,

D(x)≥0.
Proof

Choose k such that

a
k
	​

≤x<a
k+1
	​

.

No index greater than k can occur in a pair with sum at most x. Thus

R(x)=R
k
	​

(x).

By the defining minimality of a
k+1
	​

, every integer x<a
k+1
	​

 satisfies

R
k
	​

(x)≥x.

Therefore R(x)≥x. ∎

Exact discrepancy dynamics

For every integer n≥1,

D(n)−D(n−1)=r(n)−1.

Thus D is an integer-valued walk that:

starts each interval [a
k
	​

,a
k+1
	​

] at zero;

remains nonnegative;

ends at zero;

increases by r(n)−1 at n;

decreases by one exactly when r(n)=0.

In particular,

D(a
k
	​

)=D(a
k+1
	​

)=0

and

n=a
k
	​

+1
∑
a
k+1
	​

	​

(r(n)−1)=0.

Equivalently,

n=a
k
	​

+1
∑
a
k+1
	​

	​

r(n)=a
k+1
	​

−a
k
	​

.

Since Lemma 2 gives

r
k
	​

(a
k+1
	​

)=0,

and the new pair (0,k+1) is the only representation introduced at a
k+1
	​

, one has

r(a
k+1
	​

)=1.
Counting-function formulation

Let

A(t):=#{j≥1:a
j
	​

≤t}.

For a fixed j, the admissible indices i satisfy

0≤i≤j,a
i
	​

≤x−a
j
	​

.

Hence

R(x)=
j≥1
a
j
	​

≤x
	​

∑
	​

(1+min{j, A(x−a
j
	​

)}).

The initial 1 counts i=0. Therefore

R(x)=A(x)+
j=1
∑
A(x)
	​

min{j,A(x−a
j
	​

)}.

The desired estimate is equivalent to

A(x)+
j=1
∑
A(x)
	​

min{j,A(x−a
j
	​

)}=x+O(x
1/4+o(1)
).

This formulation exposes the central dependence on the local distribution of the a
j
	​

.

Extremal and boundary information

Strict increase of integer terms gives

a
k
	​

≥k.

The total-pair argument gives

a
k+1
	​

≤
2
k(k+3)
	​

+1.

At the creation point,

a
k+1
	​

−1=R
k
	​

(a
k+1
	​

)≤
2
k(k+3)
	​

.

These estimates alone do not determine whether a
k
	​

 has quadratic order; only the quadratic upper bound follows.

The discrepancy excursion on

I
k
	​

=[a
k
	​

,a
k+1
	​

]

has height

H
k
	​

:=
a
k
	​

≤x≤a
k+1
	​

max
	​

D(x).

The original assertion is equivalent to

H
k
	​

≤a
k+1
1/4+o(1)
	​

.

Indeed, every x belongs to one such interval and a
k
	​

≤x≤a
k+1
	​

.

Twelve proof strategies and their obstructions
1. Direct discrepancy control

Attempt to prove a pointwise inequality for D(x) from

D(x)−D(x−1)=r(x)−1.

Obstacle: individual multiplicities r(x) can be large, and the greedy rule controls only cumulative deficiency, not individual multiplicities.

2. Contradiction from a large excursion

Assume

D(y)≫y
1/4+ε
.

Try to show that the excess representations force an earlier future deficiency, contradicting the definition of the next a
k
	​

.

Obstacle: excess mass may be spread across many sums, and converting it into a sufficiently long representation-free interval requires additional structure.

3. Induction over greedy stages

Assume an excursion bound through stage k, then analyze the representations introduced by a
k+1
	​

.

The new representations occur at

a
k+1
	​

+a
i
	​

,0≤i≤k+1.

Obstacle: these points overlap old representation sums in an uncontrolled fashion.

4. Gap analysis

Let

g
k
	​

=a
k+1
	​

−a
k
	​

.

A discrepancy excursion must return to zero over an interval of length g
k
	​

, so trivially

H
k
	​

≤g
k
	​


because each downward step has size at most one.

Obstacle: proving

g
k
	​

≤a
k
1/4+o(1)
	​


is unsupported and is not suggested by the defining rule alone.

5. Additive-energy control

Large r(n) corresponds to many additive coincidences

a
i
	​

+a
j
	​

=a
i
′
	​

+a
j
′
	​

.

One can introduce

E
k
	​

=
n
∑
	​

r
k
	​

(n)
2
.

Cauchy–Schwarz relates representation concentration to E
k
	​

.

Obstacle: no sufficiently strong upper bound for E
k
	​

 follows directly from greediness.

6. Sidon-type structure

Lemma 2 says every newly selected a
k+1
	​

 is absent from the old sumset

{a
i
	​

+a
j
	​

:0≤i≤j≤k, j≥1}.

This resembles a weak sum-avoidance condition.

Obstacle: only the number a
k+1
	​

 itself is avoided; the sequence is not forced to have globally distinct pair sums.

7. Density inversion

Estimate A(x), then substitute into

R(x)=A(x)+
j≤A(x)
∑
	​

min{j,A(x−a
j
	​

)}.

If one had

A(x)=c
x
	​

+O(x
1/4+o(1)
),

a continuum approximation might yield the desired result.

Obstacle: even the leading asymptotic of A(x) is not obtained from the elementary recursive identities.

8. Compactness or finite-window stabilization

Every assertion about R(x) depends on only finitely many sequence terms. One might attempt finite extremal bounds uniform in the stage.

Obstacle: compactness does not supply a quantitative exponent.

9. Diagonal counterexample search

Seek stages where many sums a
i
	​

+a
j
	​

 cluster in a short interval, producing

H
k
	​

≫a
k
1/4+ε
	​

.

Obstacle: finite clustering does not establish infinitely many violating stages.

10. Transfinite or ordinal ranking

Assign a rank to unresolved discrepancy configurations and show each greedy extension decreases rank.

Obstacle: no well-founded rank with quantitative content was found.

11. Reflection across excursion endpoints

Because

D(a
k
	​

)=D(a
k+1
	​

)=0,

one can compare the prefix excess before x with the suffix deficit after x:

D(x)=
n=a
k
	​

+1
∑
x
	​

(r(n)−1)=
n=x+1
∑
a
k+1
	​

	​

(1−r(n)).

Consequently,

D(x)≤#{n:x<n≤a
k+1
	​

, r(n)=0}.

This is exact and useful.

Obstacle: bounding the number of future zero-representation integers by x
1/4+o(1)
 requires a strong covering property not yet derived.

12. Auxiliary interval-cover structure

Each term a
j
	​

 contributes the translate

a
j
	​

+{a
0
	​

,…,a
j
	​

}.

Thus r(n) is the covering multiplicity of n by these finite translates.

The discrepancy is the cumulative excess of this covering over multiplicity one.

Obstacle: the greedy rule ensures prefix coverage only in the cumulative sense R(x)≥x, not literal coverage of every integer.

Strongest rigorously obtained reformulation

For a
k
	​

≤x<a
k+1
	​

,

D(x)=
n=a
k
	​

+1
∑
x
	​

(r(n)−1)=
n=x+1
∑
a
k+1
	​

	​

(1−r(n)).

Since terms with r(n)≥1 contribute nonpositively to the second expression,

D(x)≤Z(x,a
k+1
	​

),

where

Z(u,v):=#{n∈Z:u<n≤v, r(n)=0}.

Therefore the claimed estimate would follow from

Z(x,a
k+1
	​

)≤x
1/4+o(1)
(a
k
	​

≤x<a
k+1
	​

).

This reduction is exact, but it is not a proof: the required zero-count estimate remains unestablished.

Conversely, a disproof would follow from infinitely many excursions satisfying

H
k
	​

≥a
k
1/4+ε
	​


for some fixed ε>0. The defining identities alone do not furnish such a lower bound.

No derivation obtained here establishes either the required upper bound or a contradicting lower bound. In particular, the elementary consequences of the greedy construction control signs and endpoint values of D, but not the maximal height of its excursions at the x
1/4+o(1)
 scale.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100
Confidence applies to the structural lemmas and exact reformulations, not to the unproved target estimate.

COMPLETENESS_SCORE: 18/100
The construction and discrepancy dynamics were rigorously formalized, but the decisive quantitative estimate was not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 91/100
The stated lemmas survive checks of endpoint behavior, quantifier scope, stabilization of the infinite counting function, and integer-valued threshold behavior.

RESOURCE_USAGE:
Reasoning budget used: approximately 100%
Branches explored: 12
Verified lemmas: 5 principal lemmas and several exact identities
Failed proof attempts: 12 strategic branches

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

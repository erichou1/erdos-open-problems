# Erdős Problem #158 [unsolved] 25%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Phase 0: Formalization

Let

r
A
	​

(n)=#{(a,b)∈A
2
:a≤b, a+b=n}.

The hypothesis is

A⊂N,A infinite,∀n∈N, r
A
	​

(n)≤2.

The target statement is

N→∞
liminf
	​

N
	​

A(N)
	​

=0,A(N):=∣A∩[1,N]∣.

Its negation is:

∃ε>0 ∃N
0
	​

 ∀N≥N
0
	​

,A(N)≥ε
N
	​

.

Equivalently, if A={a
1
	​

<a
2
	​

<⋯}, then the negation is equivalent to

∃C>0 ∃k
0
	​

 ∀k≥k
0
	​

,a
k
	​

≤Ck
2
.

Indeed, A(N)≥ε
N
	​

 implies a
k
	​

≤ε
−2
k
2
 for large k, and conversely a
k
	​

≤Ck
2
 implies, for a
k
	​

≤N<a
k+1
	​

,

N
	​

A(N)
	​

=
N
	​

k
	​

≥
C
	​

(k+1)
k
	​

→
C
	​

1
	​

>0.

So the problem is equivalent to:

Can there exist an infinite increasing sequence a
k
	​

 with a
k
	​

=O(k
2
) such that every integer has at most two unordered representations a
i
	​

+a
j
	​

?

Verified elementary consequences
Lemma 1: finite counting bound

If A(N)=t, then all unordered sums of pairs from A∩[1,N] lie in [2,2N], which has 2N−1 possible values. Since each value is used at most twice,

2
t(t+1)
	​

≤2(2N−1).

Thus

A(N)≤
8N
	​

+O(1).

This is far too weak to force the desired liminf 0.

Lemma 2: fixed-difference fibers are Sidon

For d≥1, define

L
d
	​

={x∈N:x∈A, x+d∈A}.

Then L
d
	​

 is a Sidon set.

Proof: suppose x,y,u,v∈L
d
	​

 and

x+y=u+v

with {x,y}

={u,v}. Since x,x+d,y,y+d,u,u+d,v,v+d∈A, the equality gives representations of

x+y+d.

If x<y, then

x+(y+d)=y+(x+d)=x+y+d

already gives two unordered representations. A second distinct pair {u,v} gives at least one additional representation, hence at least three total. That contradicts r
A
	​

(n)≤2. The diagonal case x=y gives one representation x+(x+d), but any distinct second representation again raises the count above 2. Therefore no such distinct {u,v} exists, so L
d
	​

 is Sidon.

This is a genuine structural consequence, but it does not solve the problem because the original set A may distribute its pairs across many different differences d.

Lemma 3: the Sidon proof does not transfer directly

For a Sidon set, each positive difference occurs at most once. Here that is false.

Example mechanism: if B is Sidon and M is large enough to separate sum ranges, then

A=B∪(B+M)

has many repeated differences equal to M. For b
i
	​


=b
j
	​

,

b
i
	​

+(b
j
	​

+M)=b
j
	​

+(b
i
	​

+M),

giving exactly two representations, which is allowed. Thus the “unique differences” route used for ordinary Sidon sets breaks immediately.

Strategy search summary

I explored the following independent routes.

Strategy	Result
Direct pair-counting	Gives A(N)≪
N
	​

, not liminf 0.
Contradiction from a
k
	​

=O(k
2
)	Reduces to controlling saturated sums; no contradiction obtained.
Difference multiplicity	Fixed-difference fibers are Sidon, but many differences may contribute.
Local interval density	Gives convolution-type bounds compatible with 
N
	​

 density.
Additive energy	E(A
N
	​

)≪A(N)
2
, but Cauchy only recovers A(N)≪
N
	​

.
Partition into Sidon subsets	Not enough; even finite unions of sparse Sidon pieces may have alternating dense ranges.
Greedy construction search	Suggests obstruction from saturated sums but does not prove it.
Block construction counterexample	Cross-block sums and repeated differences create uncontrolled collisions.
Digital/base expansion construction	Orientation choices across digits create exponentially many representations.
Modular Sidon construction	Works finitely but does not yield a verified infinite construction.
Compactness from finite models	Would require finite B
2
	​

[2] sets dense at every prefix; not established.
Probabilistic construction	Bad representation triples appear with controllable-looking density, but no rigorous alteration preserving all prefixes was completed.
Main unresolved gap

The strongest verified reformulation is:

If A is B
2
	​

[2] and A(N)≥ε
N
	​

 eventually, then a
k
	​

≤Ck
2
.

To prove the desired result, one must rule out such a quadratic-growth B
2
	​

[2] sequence.

The closest obstruction is this:

When a new element x is added, all sums x+a, a∈A, must avoid sums already represented twice. If A has persistent 
N
	​

-density, one expects saturated sums to become too numerous. But I did not obtain a rigorous covering statement of the form

x+A
≤k
	​

∩S
k
	​


=∅

for every candidate x≤Ck
2
, where S
k
	​

 denotes the set of already saturated sums.

That covering statement is the missing primary theorem.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas above; 0 for the original statement, since no proof or disproof was completed.

COMPLETENESS_SCORE: 25

ADVERSARIAL_SURVIVAL_SCORE: 80 for the local lemmas; not applicable to the unproved main statement.

RESOURCE_USAGE: approximately 12 branches explored, 3 verified lemmas generated, multiple failed proof and construction attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

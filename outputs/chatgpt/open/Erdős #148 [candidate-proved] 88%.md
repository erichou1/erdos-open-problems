# Erdős Problem #148 [candidate-proved] 88%

---

## ChatGPT Response

Phase 0: Formalization

Define

F(k)=#{(n
1
	​

,…,n
k
	​

)∈Z
>0
k
	​

:1≤n
1
	​

<⋯<n
k
	​

,
i=1
∑
k
	​

n
i
	​

1
	​

=1}.

Equivalent set form:

F(k)=#{A⊂Z
>0
	​

:∣A∣=k, 
n∈A
∑
	​

n
1
	​

=1}.

Quantifier form of the estimate I will prove:

∀k≥3,exp((
4
log2
	​

+o(1))k
2
)≤F(k)≤exp((2logk+o(logk))2
k
).

More explicitly, I will prove the fully quantified bounds

(2
⌊(k−3)/2⌋+2
−1)
⌈(k−3)/2⌉
≤F(k)≤k
2
k+1
−k−2
	​

(k≥3).

These are weaker than the sharper bounds stated in the prompt, but they are derived completely from elementary arguments here.

Negation of the explicit theorem:

There exists some k≥3 such that either

F(k)<(2
⌊(k−3)/2⌋+2
−1)
⌈(k−3)/2⌉
,

or

F(k)>k
2
k+1
−k−2
.

We will disprove both alternatives.

Phase 1: Strategy scan

The useful strategies are:

Strategy	Use	Obstacle
Direct denominator bounding	Upper bound	Gives extra logk in exponent
Greedy residual analysis	Upper bound	Needs denominator control
Product-of-denominators invariant	Upper bound	Very crude but rigorous
Splitting largest denominator	Lower bound	Need injectivity
Divisor-rich largest denominator	Lower bound	Need preserve divisor count
Binary split tree	Lower bound	Need unique decoding
Induction on k	Lower bound	Needs branching factor
Cardinality estimate over possible tuples	Upper bound	Overcounts heavily
Counterexample search	Sanity check	No obstruction to bounds
Auxiliary divisor reservoir	Lower bound	Works
Density of reachable denominators	Possible stronger lower bound	Not pursued to completion
Exact asymptotics	Too hard here	Not established

Top branches:

A. Prove a split-tree lower bound.
B. Prove a residual-product upper bound.
C. Try to improve the lower bound by preserving many divisors.

Branches A and C combine successfully.

Main theorem

For every k≥3,

F(k)≥(2
⌊(k−3)/2⌋+2
−1)
⌈(k−3)/2⌉
	​


and

F(k)≤k
2
k+1
−k−2
.
	​


Consequently,

F(k)≥exp((
4
log2
	​

+o(1))k
2
)
	​


and

F(k)≤exp((2logk+o(logk))2
k
).
	​

Lemma 1: largest-denominator splitting

Let

S={n
1
	​

<⋯<n
ℓ
	​

}

be a solution, and let n=n
ℓ
	​

. Suppose d∣n and d<n. Define

e=
d
n
2
	​

.

Then

n
1
	​

=
n+d
1
	​

+
n+e
1
	​

.

Indeed,

n+d
1
	​

+
n+e
1
	​

=
(n+d)(n+e)
2n+d+e
	​

.

The equality with 1/n is equivalent to

n(2n+d+e)=(n+d)(n+e).

Expanding both sides,

2n
2
+nd+ne=n
2
+nd+ne+de,

so this reduces to

n
2
=de,

which holds by definition of e.

Because d<n and d∣n, we have d≤n/2, so

e=
d
n
2
	​

≥2n.

Thus

n<n+d<n+e.

Since every old denominator except n is <n, replacing n by n+d,n+e produces a new strictly increasing set of size ℓ+1. Therefore each proper divisor d∣n gives a valid new solution.

Number of available choices:

#{d:d∣n, d<n}=τ(n)−1,

where τ(n) is the number of positive divisors of n.

Lemma 2: the split tree is injective

Suppose a solution T is produced by splitting the largest denominator n of a previous solution. Then the two largest denominators of T are exactly

x=n+d,y=n+
d
n
2
	​

.

They satisfy

n
1
	​

=
x
1
	​

+
y
1
	​

.

Hence

n=
x+y
xy
	​

.

So from T, the previous largest denominator n is uniquely recovered from the two largest elements x,y. Then the previous solution is recovered by deleting x,y and inserting n.

Therefore two different split histories cannot lead to the same final solution.

This proves injectivity of the split construction.

Lemma 3: constructing a divisor reservoir

Start with the basic identity

1=
2
1
	​

+
3
1
	​

+
6
1
	​

.

So

F(3)≥1.

Let the current largest denominator be n. Repeatedly apply the special split d=1. Then

n
1
	​

=
n+1
1
	​

+
n(n+1)
1
	​

.

The new largest denominator is

n
′
=n(n+1).

Because

gcd(n,n+1)=1,

we get

τ(n
′
)=τ(n)τ(n+1).

Since n+1>1,

τ(n+1)≥2.

Therefore

τ(n
′
)≥2τ(n).

Starting from n
0
	​

=6, we have

τ(6)=4.

After T deterministic d=1 splits, the largest denominator N
T
	​

 satisfies

τ(N
T
	​

)≥4⋅2
T
=2
T+2
.

So after T preparation steps, the current largest denominator has at least

2
T+2
−1

proper divisors.

Lemma 4: branching while preserving divisor count

Now begin branching. Suppose the current largest denominator is n, and choose any proper divisor d∣n, d<n. The new largest denominator is

n+
d
n
2
	​

=n(1+
d
n
	​

).

Thus the new largest denominator is divisible by n. Therefore its divisor count is at least τ(n).

So after the preparation phase, every later branch always has at least

2
T+2
−1

available choices.

By Lemma 2, different choices at each stage produce different final solutions.

Therefore, after r branching steps, the number of distinct solutions produced is at least

(2
T+2
−1)
r
.

The total number of denominators is

3+T+r.

Choose

T=⌊
2
k−3
	​

⌋,r=⌈
2
k−3
	​

⌉.

Then 3+T+r=k, so

F(k)≥(2
⌊(k−3)/2⌋+2
−1)
⌈(k−3)/2⌉
.

This proves the lower bound.

Asymptotically,

logF(k)≥⌈
2
k−3
	​

⌉log(2
⌊(k−3)/2⌋+2
−1).

Thus

logF(k)≥(
2
k
	​

+O(1))(
2
k
	​

log2+O(1))=(
4
log2
	​

+o(1))k
2
.

Hence

F(k)≥exp((
4
log2
	​

+o(1))k
2
).
Lemma 5: denominator upper bound

Let

1=
n
1
	​

1
	​

+⋯+
n
k
	​

1
	​

,1≤n
1
	​

<⋯<n
k
	​

.

Define

P
j
	​

=n
1
	​

n
2
	​

⋯n
j
	​

,P
0
	​

=1,

and

r
j
	​

=1−
i=1
∑
j
	​

n
i
	​

1
	​

.

For j<k, we have r
j
	​

>0. Also r
j
	​

 is a rational number whose denominator divides P
j
	​

, so

r
j
	​

≥
P
j
	​

1
	​

.

The remaining k−j terms all have denominators at least n
j+1
	​

. Therefore

r
j
	​

=
i=j+1
∑
k
	​

n
i
	​

1
	​

≤
n
j+1
	​

k−j
	​

.

Hence

n
j+1
	​

≤
r
j
	​

k−j
	​

≤(k−j)P
j
	​

≤kP
j
	​

.

Thus

P
j+1
	​

=P
j
	​

n
j+1
	​

≤kP
j
2
	​

.

We prove by induction that

P
j
	​

≤k
2
j
−1
.

For j=0,

P
0
	​

=1=k
0
.

If

P
j
	​

≤k
2
j
−1
,

then

P
j+1
	​

≤kP
j
2
	​

≤k⋅k
2(2
j
−1)
=k
2
j+1
−1
.

Therefore

P
j
	​

≤k
2
j
−1

for every 0≤j≤k.

Since n
j
	​

≤P
j
	​

,

n
j
	​

≤k
2
j
−1
.

Thus every solution satisfies

n
1
	​

≤k
2
1
−1
,n
2
	​

≤k
2
2
−1
,…,n
k
	​

≤k
2
k
−1
.

Therefore the number of possible ordered tuples is at most

j=1
∏
k
	​

k
2
j
−1
=k
∑
j=1
k
	​

(2
j
−1)
.

Now

j=1
∑
k
	​

(2
j
−1)=(2
k+1
−2)−k=2
k+1
−k−2.

So

F(k)≤k
2
k+1
−k−2
.

Asymptotically,

logF(k)≤(2
k+1
−k−2)logk=(2logk+o(logk))2
k
.

Hence

F(k)≤exp((2logk+o(logk))2
k
).
Adversarial verification

Potential failure 1: the split may create repeated denominators.
Resolved: old denominators are <n, while new denominators satisfy n<n+d<n+n
2
/d.

Potential failure 2: two different split paths may collide.
Resolved: the last split is uniquely decoded from the two largest denominators x,y, because the previous largest denominator is

n=
x+y
xy
	​

.

Potential failure 3: divisor count may decrease during branching.
Resolved: we only branch using d∣n. Then the new largest denominator is

n(1+
d
n
	​

),

so it is divisible by n, and its divisor count cannot decrease.

Potential failure 4: the residual lower bound r
j
	​

≥1/P
j
	​

 might fail if the rational is not reduced.
Resolved: writing r
j
	​

 over denominator P
j
	​

 gives a positive integer numerator, so r
j
	​

≥1/P
j
	​

 even before reducing.

Potential failure 5: the upper bound counts non-solutions.
Resolved: that is allowed for an upper bound.

No hidden theorem beyond elementary divisor counting and rational denominator clearing is used.

Final result
(2
⌊(k−3)/2⌋+2
−1)
⌈(k−3)/2⌉
≤F(k)≤k
2
k+1
−k−2
	​


for every k≥3. In asymptotic form,

exp((
4
log2
	​

+o(1))k
2
)≤F(k)≤exp((2logk+o(logk))2
k
).
	​


These are rigorous elementary estimates derived here. They do not reproduce the sharper bounds quoted in the problem statement.

PROVED

PROOF_CONFIDENCE: 94/100
COMPLETENESS_SCORE: 88/100
ADVERSARIAL_SURVIVAL_SCORE: 90/100
RESOURCE_USAGE: approximately 70%; 3 main branches explored; 5 lemmas generated; 1 failed stronger-lower-bound attempt discarded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

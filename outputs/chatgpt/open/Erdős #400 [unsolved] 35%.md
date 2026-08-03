# Erdős Problem #400 [unsolved] 35%

---

## ChatGPT Response

Formalization

Fix k≥2. I interpret a! only for nonnegative integers. Since 0!=1!=1, any maximizing tuple may be taken with 1≤a
i
	​

≤n.

Define

g
k
	​

(n)=
1≤a
1
	​

,…,a
k
	​

≤n
a
1
	​

!⋯a
k
	​

!∣n!
	​

max
	​

(
i=1
∑
k
	​

a
i
	​

−n).

The first asserted asymptotic is

∃c
k
	​

≥0:
n≤x
∑
	​

g
k
	​

(n)∼c
k
	​

xlogx.

Equivalently,

x→∞
lim
	​

xlogx
1
	​

n≤x
∑
	​

g
k
	​

(n)=c
k
	​

.

The second asserted almost-all statement is

∃c
k
	​

≥0∀ε>0:#{n<x: ∣g
k
	​

(n)−c
k
	​

logx∣>εlogx}=o(x).

Its negation is

∀c≥0∃ε>0∃x
j
	​

→∞:#{n<x
j
	​

: ∣g
k
	​

(n)−clogx
j
	​

∣>εlogx
j
	​

}

=o(x
j
	​

).

The basic invariant is the prime-adic deficit

D
p
	​

(n;a
1
	​

,…,a
k
	​

)=v
p
	​

(n!)−
i=1
∑
k
	​

v
p
	​

(a
i
	​

!).

The tuple is admissible exactly when

D
p
	​

(n;a
1
	​

,…,a
k
	​

)≥0

for every prime p≤n.

Exact digit-sum formulation

For a prime p, let s
p
	​

(m) be the sum of the base-p digits of m. Legendre’s formula gives

v
p
	​

(m!)=
j≥1
∑
	​

⌊
p
j
m
	​

⌋=
p−1
m−s
p
	​

(m)
	​

.

Therefore, if

d=
i=1
∑
k
	​

a
i
	​

−n,

then

a
1
	​

!⋯a
k
	​

!∣n!

is equivalent to

i=1
∑
k
	​

p−1
a
i
	​

−s
p
	​

(a
i
	​

)
	​

≤
p−1
n−s
p
	​

(n)
	​


for every prime p≤n. Rearranging,

d≤
i=1
∑
k
	​

s
p
	​

(a
i
	​

)−s
p
	​

(n)

for every prime p≤n.

Thus

g
k
	​

(n)=
1≤a
1
	​

,…,a
k
	​

≤n
∀p≤n: ∑a
i
	​

−n≤∑
i
	​

s
p
	​

(a
i
	​

)−s
p
	​

(n)
	​

max
	​

(
i=1
∑
k
	​

a
i
	​

−n).
	​


This immediately proves the standard upper bound. Since a
i
	​

≤n,

s
2
	​

(a
i
	​

)≤⌊log
2
	​

n⌋+1.

Hence

g
k
	​

(n)≤k(⌊log
2
	​

n⌋+1)−s
2
	​

(n)≤k(⌊log
2
	​

n⌋+1)−1.

Also,

g
k
	​

(n)≥k−1

because (a
1
	​

,…,a
k
	​

)=(n,1,…,1) is admissible.

So, rigorously,

k−1≤g
k
	​

(n)≤k⌊log
2
	​

n⌋+k−1.
	​


In particular,

n≤x
∑
	​

g
k
	​

(n)≪
k
	​

xlogx.
Exact multinomial formulation

Let

A=a
1
	​

+⋯+a
k
	​

=n+d.

Then

a
1
	​

!⋯a
k
	​

!
A!
	​


is a multinomial coefficient. Since

n!
A!
	​

=(n+1)(n+2)⋯(n+d),

we have

a
1
	​

!⋯a
k
	​

!∣n!

if and only if

(n+1)(n+2)⋯(n+d)∣(
a
1
	​

,…,a
k
	​

n+d
	​

).

Therefore,

g
k
	​

(n)=max{d:∃a
1
	​

,…,a
k
	​

≥1, ∑a
i
	​

=n+d, (n+1)⋯(n+d)∣(
a
1
	​

,…,a
k
	​

n+d
	​

)}.
	​


This is exact and introduces no asymptotic assumption.

Exact one-large-part reformulation

For 0≤r≤n−1, define

Q
r
	​

(n)=
(n−r)!
n!
	​

=(n−r+1)(n−r+2)⋯n.

For t≥1 and a positive integer M, define

H
t
	​

(M)=
b
1
	​

,…,b
t
	​

≥1
b
1
	​

!⋯b
t
	​

!∣M
	​

max
	​

(b
1
	​

+⋯+b
t
	​

).

Choose the largest part among a
1
	​

,…,a
k
	​

, say a
k
	​

=n−r. Then

a
1
	​

!⋯a
k−1
	​

!∣Q
r
	​

(n),

and

i=1
∑
k
	​

a
i
	​

−n=(a
1
	​

+⋯+a
k−1
	​

)−r.

Conversely, any tuple b
1
	​

,…,b
k−1
	​

 with

b
1
	​

!⋯b
k−1
	​

!∣Q
r
	​

(n)

gives an admissible k-tuple

(b
1
	​

,…,b
k−1
	​

,n−r).

Hence

g
k
	​

(n)=
0≤r≤n−1
max
	​

(H
k−1
	​

(Q
r
	​

(n))−r).
	​


This is another exact reformulation of the original problem.

A verified obstruction sequence for k=2

For k=2, one can completely evaluate g
2
	​

(n) on the sequence

n=2
m
−1.

I claim

g
2
	​

(2
m
−1)=1.
	​


The lower bound is immediate from (a,b)=(n,1), giving g
2
	​

(n)≥1.

For the upper bound, suppose

a!b!∣n!,n=2
m
−1.

Assume b≥a. Write

b=n−r

with 0≤r≤n−1. Then

a!∣
(n−r)!
n!
	​

=(2
m
−r)(2
m
−r+1)⋯(2
m
−1).

Equivalently,

a!∣
j=1
∏
r
	​

(2
m
−j).

For 1≤j<2
m
,

v
2
	​

(2
m
−j)=v
2
	​

(j).

Therefore

v
2
	​

(
j=1
∏
r
	​

(2
m
−j))=
j=1
∑
r
	​

v
2
	​

(j)=v
2
	​

(r!).

Now

a+b−n=a+(n−r)−n=a−r.

If a−r≥2, then a≥r+2, so among r+1,r+2 there is an even integer. Hence

v
2
	​

(a!)>v
2
	​

(r!).

But this contradicts

a!∣
j=1
∏
r
	​

(2
m
−j),

because the product has exactly v
2
	​

(r!) factors of 2. Therefore

a−r≤1.

Thus

a+b−n≤1.

Since the lower bound already gives g
2
	​

(n)≥1, we get

g
2
	​

(2
m
−1)=1.

This proves that even though the universal upper bound is logarithmic, the pointwise value can remain bounded along an infinite sequence.

Consequence connecting the two requested assertions

Suppose the almost-all statement were true for some c
k
	​

. Then, using the proven upper bound

g
k
	​

(n)≪
k
	​

logn,

we would get

n≤x
∑
	​

g
k
	​

(n)=
n≤x
∣g
k
	​

(n)−c
k
	​

logx∣≤εlogx
	​

∑
	​

g
k
	​

(n)+
n≤x
∣g
k
	​

(n)−c
k
	​

logx∣>εlogx
	​

∑
	​

g
k
	​

(n).

The exceptional set has size o(x), and each term is O
k
	​

(logx), so the exceptional contribution is

o(xlogx).

The main set contributes

(c
k
	​

+O(ε))xlogx+o(xlogx).

Letting ε→0, we would obtain

n≤x
∑
	​

g
k
	​

(n)∼c
k
	​

xlogx.

Therefore,

the almost-all statement implies the average-order statement with the same constant.
	​


The converse does not follow from the estimates above.

Branch analysis

The exact theorem pool obtained is:

k−1≤g
k
	​

(n)≤k⌊log
2
	​

n⌋+k−1
	​

g
k
	​

(n)=
1≤a
i
	​

≤n
∀p≤n: ∑a
i
	​

−n≤∑
i
	​

s
p
	​

(a
i
	​

)−s
p
	​

(n)
	​

max
	​

(∑a
i
	​

−n)
	​

g
k
	​

(n)=
0≤r≤n−1
max
	​

(H
k−1
	​

(Q
r
	​

(n))−r)
	​

g
2
	​

(2
m
−1)=1.
	​


The missing step for the first question is an asymptotic evaluation of

n≤x
∑
	​

0≤r≤n−1
max
	​

(H
k−1
	​

(Q
r
	​

(n))−r).

The missing step for the second question is a concentration theorem for the same maximum on a density-1 subset of n<x.

The verified tools above do not prove either asymptotic concentration or its negation.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the displayed lemmas and equivalences.

COMPLETENESS_SCORE: 35 for the original two asymptotic questions.

ADVERSARIAL_SURVIVAL_SCORE: 95 for the proved reductions and the sequence g
2
	​

(2
m
−1)=1.

RESOURCE_USAGE: approximately 100% of the available productive proof search for this response; 3 main reformulations, 4 verified lemmas, 1 exact infinite sequence, and no complete proof or disproof of the two asymptotic assertions.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

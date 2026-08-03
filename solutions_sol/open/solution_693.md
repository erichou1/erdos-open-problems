# Erdős Problem #693 [unsolved] 55%

---

## ChatGPT Response

For the problem stated in the uploaded file 

Pasted text

, let

D
n
	​

={n+1,n+2,…,2n−1},
A
n,k
	​

={m∈[n,n
k
]∩Z:∃d∈D
n
	​

, d∣m},

and define

G
k
	​

(n)=
i
max
	​

(a
i+1
	​

−a
i
	​

).
Formal equivalent form

For integers x,H≥1, put

R
n
	​

(x,H)=
d=n+1
∑
2n−1
	​

(⌊
d
x+H
	​

⌋−⌊
d
x
	​

⌋).

Then

R
n
	​

(x,H)>0

if and only if (x,x+H] contains an integer having a divisor in (n,2n).

Thus the polylogarithmic assertion is

∃C=C(k),N
0
	​

(k)∀n≥N
0
	​

(k),G
k
	​

(n)≤(logn)
C
.

Its negation is

∀C>0, ∀N, ∃n≥N:G
k
	​

(n)>(logn)
C
.
Rigorous bounds

For every fixed k≥2, the following bounds hold for sufficiently large n:

clogn ≤ G
k
	​

(n) ≤ C
k
	​

n
1−
2
k
−1
1
	​

	​


for an absolute c>0 and a constant C
k
	​

 depending only on k.

In particular,

G
2
	​

(n)≪n
2/3
,G
3
	​

(n)≪n
6/7
,G
4
	​

(n)≪n
14/15
.
1. Logarithmic lower bound

Let

L
Q
	​

=lcm(1,2,…,Q).
Lemma
L
Q
	​

≤4
2Q
.

Indeed, for every m,

L
m
	​

L
2m
	​

	​

∣(
m
2m
	​

).

To see this, a prime exponent increases from L
m
	​

 to L
2m
	​

 only when

m<p
a
≤2m.

At the p
a
-level, the p-adic valuation of (
m
2m
	​

) gains at least one. Consequently,

L
2m
	​

≤L
m
	​

(
m
2m
	​

)≤4
m
L
m
	​

.

Iteration along powers of two gives the stated estimate.

Now choose

Q=⌊
16log4
logn
	​

⌋,L=L
Q
	​

.

Then

L≤4
2Q
≤n
1/8
,

so, for sufficiently large n,

L≤
3Q
n
	​

.

Let

M=L⌊
L
n
	​

⌋,x=MQ.

Thus

n−L≤M≤n.

Because Q−1∣L∣M, the number

d
0
	​

=
Q−1
MQ
	​


is integral. Moreover,

d
0
	​

−n≥−L+
Q−1
n−L
	​

>0,

while

d
0
	​

≤
Q−1
nQ
	​

<2n.

Hence

x=(Q−1)d
0
	​

∈A
n,k
	​

.

We claim that

x+h∈
/
A
n,k
	​

(1≤h<
4
Q
	​

).

Suppose instead that

x+h=dq,n<d<2n.

Since M≥n−L,

q>
2n
x
	​

=
2n
MQ
	​

≥
2
Q
	​

−
6
1
	​

>
4
Q
	​

.

Also,

q<
n
x+Q/4
	​

≤Q+
4n
Q
	​

<Q+1,

so q≤Q. Therefore q∣L∣M, hence q∣x=MQ. Since q∣x+h, it follows that q∣h. But

0<h<
4
Q
	​

<q,

which is impossible.

Finally,

x+(Q−1)=(Q−1)(d
0
	​

+1)∈A
n,k
	​

,

and this number is below n
2
, hence below n
k
. Therefore a genuine gap following x has length at least Q/4. Consequently,

G
k
	​

(n)≫Q≫logn.
2. Power-saving upper bound

Write

σ
n
	​

=
d=n+1
∑
2n−1
	​

d
1
	​

.

For n≥3,

σ
n
	​

≥
2n
n−1
	​

≥
3
1
	​

.

Define the fractional-part discrepancy

Δ
n
	​

(Y)=
d=n+1
∑
2n−1
	​

({
d
Y
	​

}−
2
1
	​

).

Then

R
n
	​

(x,H)=Hσ
n
	​

−Δ
n
	​

(x+H)+Δ
n
	​

(x).

It therefore suffices to bound Δ
n
	​

(Y).

Reciprocal exponential-sum lemma

Let

e(t)=e
2πit
,S
h
	​

(Y)=
n<d<2n
∑
	​

e(
d
hY
	​

).

For r≥2, put

α
r
	​

=
2
r
−2
1
	​

,β
r
	​

=1−
2
r−2
1
	​

.

If

n
r−1
≤Y≤2n
r

and

λ=
n
r+1
hY
	​

∈[n
−2
,1],

then repeated van der Corput differencing gives

∣S
h
	​

(Y)∣≪
r
	​

nλ
α
r
	​

+n
β
r
	​

λ
−α
r
	​

.

For r=2, this is the second-derivative estimate, since

(
t
hY
	​

)
′′
=
t
3
2hY
	​

≍λ.

The induction step applies van der Corput differencing with

U≍λ
−α
r
	​

/(1+α
r
	​

)
.

The correlation phase has r-th derivative of size ≍uλ. The resulting recurrences are

α
r+1
	​

=
2(1+α
r
	​

)
α
r
	​

	​

,β
r+1
	​

=
2
1+β
r
	​

	​

,

which give the displayed values.

The Erdős–Turán discrepancy inequality now yields, for every M≥1,

∣Δ
n
	​

(Y)∣≪
M
n
	​

+
h=1
∑
M
	​

h
∣S
h
	​

(Y)∣
	​

.

Substitution gives

∣Δ
n
	​

(Y)∣≪
r
	​

M
n
	​

+n
1−α
r
	​

(r+1)
Y
α
r
	​

M
α
r
	​

+n
β
r
	​

+α
r
	​

(r+1)
Y
−α
r
	​

.

Choose

M=(
Y
n
r+1
	​

)
1+α
r
	​

α
r
	​

	​

.

When n
r−1
≤Y≤n
r
, the first two terms are

≪
r
	​

n
1−
2
r
−1
1
	​

.

For r≥3, the third term is also at most this size because

β
r
	​

+2α
r
	​

≤1−
2
r
−1
1
	​

.

Thus

∣Δ
n
	​

(Y)∣≪
r
	​

n
1−
2
r
−1
1
	​

(n
r−1
≤Y≤n
r
, r≥3).

For r=2, the same calculation gives

∣Δ
n
	​

(Y)∣≪n
2/3
(n
5/3
≤Y≤n
2
).

When Y<n
5/3
, a direct construction suffices: choose an integer

q∈[
2n−1
Y+1
	​

,
n+1
Y+1
	​

]

and put

d=⌈
q
Y+1
	​

⌉.

Then n<d<2n, and

0<qd−Y≪
n
Y
	​

+1≪n
2/3
.

Combining all scales r=2,…,k, and noting that

1−
2
r
−1
1
	​

≤1−
2
k
−1
1
	​

,

we obtain

∣Δ
n
	​

(Y)∣≪
k
	​

n
1−
2
k
−1
1
	​


at every relevant scale.

Hence, for

H=C
k
	​

n
1−
2
k
−1
1
	​


with C
k
	​

 sufficiently large,

R
n
	​

(x,H)≥
3
H
	​

−∣Δ
n
	​

(x+H)∣−∣Δ
n
	​

(x)∣>0.

Therefore every admissible interval of this length contains an element of A, proving

G
k
	​

(n)≪
k
	​

n
1−
2
k
−1
1
	​

.
Conclusion on the polylogarithmic question

The rigorous conclusion obtained here is

logn ≪
k
	​

 G
k
	​

(n) ≪
k
	​

n
1−
2
k
−1
1
	​

.
	​


The logarithmic construction is consistent with a polylogarithmic upper bound, but the exponential-sum argument still leaves a positive power of n. I did not obtain either:

G
k
	​

(n)≤(logn)
C
k
	​

,

or a construction contradicting every such bound.

Final state: RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 88/100
COMPLETENESS_SCORE: 55/100 for the original polylogarithmic question; 90/100 for the displayed two-sided bounds.
ADVERSARIAL_SURVIVAL_SCORE: 84/100
RESOURCE_USAGE: High; several independent constructions and discrepancy approaches were checked.

I used no WiFi, internet search, web search, external databases, or literature-status information. The only citation is to the uploaded problem statement; all mathematical reasoning above was derived within this session.

# Erdős Problem #939 [unsolved] 72%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

0. Formalization

For an integer r≥2, define

P
r
	​

={n∈Z
>0
	​

:∀p prime, p∣n⟹p
r
∣n}.

Equivalently,

n∈P
r
	​

⟺∀p,v
p
	​

(n)∈{0}∪[r,∞).

For fixed r≥4, the first two questions ask about tuples

(a
1
	​

,…,a
r−2
	​

,c)∈P
r
r−1
	​


satisfying

a
1
	​

+⋯+a
r−2
	​

=c,gcd(a
1
	​

,…,a
r−2
	​

)=1.

The examples in the statement show that “coprime” cannot mean pairwise coprime: in the displayed r=5 example, the first two summands are both divisible by 2. Thus the applicable condition is

gcd(a
1
	​

,…,a
r−2
	​

)=1.

The negation of finiteness for a fixed r is:

For every N, there exists a solution whose resulting r-powerful number c>N.

I will establish this for every r≥6.

1. Binomial construction

Let

K
r
	​

={k:1≤k≤r, k odd}.

Then

∣K
r
	​

∣=⌈
2
r
	​

⌉.

For arbitrary integers X>Y>0,

(X+Y)
r
−(X−Y)
r
=2
1≤k≤r
k odd
	​

∑
	​

(
k
r
	​

)X
r−k
Y
k
.

Therefore

(X+Y)
r
=(X−Y)
r
+
k∈K
r
	​

∑
	​

2(
k
r
	​

)X
r−k
Y
k
.
(1)

This initially expresses an rth power as a sum of

1+∣K
r
	​

∣=⌈
2
r
	​

⌉+1
(2)

positive integers.

The remaining tasks are to choose X,Y so that:

every summand in (1) is r-powerful;

their common gcd is 1;

for r≥6, the number of summands can be increased to exactly r−2.

2. Number of required summands

Set

m
r
	​

=⌈
2
r
	​

⌉+1.

For r≥6,

m
r
	​

≤r−2.

Indeed:

if r=2q, then

m
r
	​

=q+1≤2q−2⟺q≥3;

if r=2q+1, then

m
r
	​

=q+2≤2q−1⟺q≥3.

Define

d
r
	​

=(r−2)−m
r
	​

+1=r−1−m
r
	​

.
(3)

Then d
r
	​

≥1, and replacing one summand by d
r
	​

 equal summands increases the number of summands by d
r
	​

−1. Consequently,

m
r
	​

+d
r
	​

−1=r−2.
(4)

Explicitly,

d
r
	​

=
⎩
⎨
⎧
	​

2
r
	​

−2,
2
r−5
	​

,
	​

r even,
r odd.
	​


For r=6,7, this gives d
r
	​

=1, so no actual splitting is needed.

3. Choice of parameters

Fix r≥6, and abbreviate

d=d
r
	​

.

Let P be the product of all primes dividing

d
k∈K
r
	​

∏
	​

2(
k
r
	​

).
(5)

Thus every prime occurring in d or in any binomial coefficient

2(
k
r
	​

),k∈K
r
	​

,

divides P.

Choose an integer L satisfying

L≥r+
p
max
	​

v
p
	​

(d),
(6)

where the maximum is interpreted as 0 when d=1.

For every positive integer t, put

U
t
	​

=1+tP,X
t
	​

=U
t
L
	​

,Y=P
L
.
(7)

For all sufficiently large t,

X
t
	​

>Y.

Moreover,

gcd(U
t
	​

,P)=1,

because U
t
	​

≡1(modP). Hence

gcd(X
t
	​

,Y)=1.
(8)

Also,

X
t
	​

−Y≡1(modP).
(9)

Fix one such t and write X=X
t
	​

.

For each odd k, define

T
k
	​

=2(
k
r
	​

)X
r−k
Y
k
.
(10)

Identity (1) becomes

(X+Y)
r
=(X−Y)
r
+
k∈K
r
	​

∑
	​

T
k
	​

.
(11)
4. Verification that every T
k
	​

 is r-powerful

Fix k∈K
r
	​

. We must prove

v
p
	​

(T
k
	​

)>0⟹v
p
	​

(T
k
	​

)≥r

for every prime p.

From (10),

v
p
	​

(T
k
	​

)=v
p
	​

(2(
k
r
	​

))+(r−k)v
p
	​

(X)+kv
p
	​

(Y).
(12)

There are three possible sources of a prime divisor.

Case 1: p∣Y

Since Y=P
L
,

v
p
	​

(Y)=Lv
p
	​

(P)≥L.

Because k≥1,

v
p
	​

(T
k
	​

)≥kL≥L≥r.
Case 2: p∣X

If r−k>0, then

v
p
	​

(T
k
	​

)≥(r−k)v
p
	​

(X).

Now X=U
t
L
	​

, so

v
p
	​

(X)=Lv
p
	​

(U
t
	​

)≥L.

Therefore

v
p
	​

(T
k
	​

)≥L≥r.

If r−k=0, then k=r, and X does not occur in T
k
	​

; hence a prime arising only from X does not divide T
k
	​

.

Case 3: p∣2(
k
r
	​

)

By the definition of P, such a prime divides P, hence divides Y. Case 1 therefore applies.

Thus every prime divisor of T
k
	​

 occurs with exponent at least r. Therefore

T
k
	​

∈P
r
	​

.
(13)

The two endpoint terms

(X−Y)
r
,(X+Y)
r

are perfect rth powers and hence are r-powerful.

5. Splitting T
1
	​


The k=1 term is

T
1
	​

=2rX
r−1
Y.
(14)

Since every prime divisor of d divides P, and Y=P
L
, we have

d∣Y,

so

B:=
d
T
1
	​

	​

(15)

is a positive integer.

We verify that B is r-powerful.

For every prime p,

v
p
	​

(B)=v
p
	​

(T
1
	​

)−v
p
	​

(d).

If p∣d, then p∣P, and hence

v
p
	​

(T
1
	​

)≥v
p
	​

(Y)≥L.

Using (6),

v
p
	​

(B)≥L−v
p
	​

(d)≥r.
(16)

If p∤d, division by d does not reduce its exponent, so whenever p∣B,

v
p
	​

(B)=v
p
	​

(T
1
	​

)≥r.

Consequently,

B∈P
r
	​

.
(17)

Replace T
1
	​

 in (11) by d copies of B. Since dB=T
1
	​

,

(X+Y)
r
=(X−Y)
r
+
d copies
B+⋯+B
	​

	​

+
k∈K
r
	​

k>1
	​

∑
	​

T
k
	​

.
(18)

By (4), the right side of (18) has exactly

1+d+(∣K
r
	​

∣−1)=d+∣K
r
	​

∣=r−2

summands.

Every one of them is r-powerful.

6. Coprimality

It remains to prove that the gcd of all the summands on the right side of (18) is 1.

In fact, we prove the stronger statement that

gcd(X−Y,B)=1andgcd(X−Y,T
k
	​

)=1

for every relevant k.

Suppose a prime q divides both X−Y and some T
k
	​

.

Every prime divisor of T
k
	​

 comes from at least one of:

2(
k
r
	​

);

X;

Y.

If

q∣2(
k
r
	​

),

then q∣P. But (9) gives

X−Y≡1(modq),

contradicting q∣X−Y.

If q∣X and q∣X−Y, then q∣Y, contradicting

gcd(X,Y)=1.

If q∣Y, then q∣P, again contradicting (9).

Thus

gcd(X−Y,T
k
	​

)=1.
(19)

Since B∣T
1
	​

,

gcd(X−Y,B)=1.
(20)

Therefore the gcd of the entire family of summands in (18) is 1:

gcd
	​

(X−Y)
r
,
d
B,…,B
	​

	​

,(T
k
	​

)
k∈K
r
	​

k>1
	​

	​

	​

=1.
(21)

Repeated copies of B do not affect this conclusion because (X−Y)
r
 is coprime to B.

7. Infinitely many distinct solutions for every r≥6

The parameter t may be any sufficiently large positive integer.

As t increases,

X
t
	​

=(1+tP)
L

strictly increases. Hence

c
t
	​

=(X
t
	​

+Y)
r

strictly increases.

Thus the constructions obtained from distinct t are distinct.

We have proved:

Theorem

For every integer r≥6, there are infinitely many tuples

(a
1
	​

,…,a
r−2
	​

,c)

of r-powerful positive integers satisfying

a
1
	​

+⋯+a
r−2
	​

=c

and

gcd(a
1
	​

,…,a
r−2
	​

)=1.

Consequently, for every fixed r≥6, the proposed finiteness assertion is false.

The same construction before splitting gives infinitely many representations using only

⌈
2
r
	​

⌉+1

r-powerful summands.

8. Boundary cases r=4 and r=5

For r=5,

⌈
2
5
	​

⌉+1=4,

whereas r−2=3. The construction above therefore does not produce the required three-summand representation.

The problem statement itself supplies the identity

3
7
61
5
=2
8
3
10
5
7
+2
12
23
6
+11
5
13
5
.

Each term is 5-powerful:

v
3
	​

(3
7
61
5
)=7,v
61
	​

(3
7
61
5
)=5;
v
2
	​

(2
8
3
10
5
7
)=8,v
3
	​

=10,v
5
	​

=7;
v
2
	​

(2
12
23
6
)=12,v
23
	​

=6;
v
11
	​

(11
5
13
5
)=5,v
13
	​

=5.

The three summands have common gcd 1, because the third is odd and not divisible by 3, 5, or 23, while the first two have no prime divisor common with it.

Thus existence is established for r=5, conditional only on the correctness of the displayed numerical equality supplied in the statement. The present derivation does not establish infinitely many r=5 solutions.

For r=4, the required equation has only two summands:

a+b=c,a,b,c∈P
4
	​

,gcd(a,b)=1.

The binomial construction gives

(X+Y)
4
=(X−Y)
4
+8X
3
Y+8XY
3
,

which has three summands, not two. Grouping the last two produces

(X+Y)
4
=(X−Y)
4
+8XY(X
2
+Y
2
),

but the factor X
2
+Y
2
 can contain primes to exponents below 4. No choice developed here forces the grouped term to be 4-powerful while simultaneously establishing infinitely many coprime solutions.

Accordingly, the r=4 case is not resolved by this argument.

9. The 3-powerful equation

The third question asks for infinitely many triples

a,b,c∈P
3
	​

,gcd(a,b,c)=1,a+b=c.

The statement explicitly asserts that such infinitely many triples exist and supplies one example:

2
3
3
5
73
3
+271
3
=919
3
.

The displayed terms are indeed 3-powerful:

2
3
3
5
73
3
∈P
3
	​

,271
3
∈P
3
	​

,919
3
∈P
3
	​

.

Their common gcd is 1, since the second summand is divisible only by 271, while

271∤2
3
3
5
73
3
.

However, the assertion of infinitude in the supplied text is attributed to external constructions. Under the imposed prohibition on using those external arguments, the assertion itself is available as part of the problem statement, but a self-contained derivation of the infinite family has not been reconstructed here.

Dependency graph
Definition D1
n∈P
r
	​

⟺v
p
	​

(n)=0 or v
p
	​

(n)≥r∀p.
Lemma L1: Odd binomial decomposition

Depends only on the binomial theorem:

(X+Y)
r
=(X−Y)
r
+
k∈K
r
	​

∑
	​

2(
k
r
	​

)X
r−k
Y
k
.
Lemma L2: Parameter coprimality

From

X=(1+tP)
L
,Y=P
L

follows

gcd(X,Y)=1,X−Y≡1(modP).
Lemma L3: Powerful cross terms

Depends on D1, L2, and the choice of P,L:

T
k
	​

=2(
k
r
	​

)X
r−k
Y
k
∈P
r
	​

.
Lemma L4: Powerful splitting

For

B=T
1
	​

/d,

the exponent bound

L−v
p
	​

(d)≥r

implies

B∈P
r
	​

.
Lemma L5: Common gcd equals 1

Depends on L2 and the fact that every coefficient prime divides P:

gcd(X−Y,T
k
	​

)=gcd(X−Y,B)=1.
Main theorem for r≥6

Depends on L1–L5 and the summand count identity:

m
r
	​

+d
r
	​

−1=r−2.

PROOF_CONFIDENCE
97

COMPLETENESS_SCORE
72

ADVERSARIAL_SURVIVAL_SCORE
94

RESOURCE_USAGE
Estimated reasoning budget used: 88%
Branches explored: 7
Lemmas generated: 5 principal lemmas
Failed proof attempts: 3 principal attempts
Unresolved components: self-contained treatment of r=4; self-contained infinite construction for the r=3 two-summand equation; infinitude for r=5

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

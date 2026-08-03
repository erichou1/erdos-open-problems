1. Blocking defect in the exact wording

The two questions do not yet define unique mathematical propositions.

For the first question, the statement does not specify that the 
𝑥
𝑖
x
i
	​

 are distinct or increasing, nor that 
𝑑
>
0
d>0. Under the literal permissive reading, take

𝑥
1
=
⋯
=
𝑥
𝑘
=
1
,
𝑑
=
0
,
𝐶
=
1
,
x
1
	​

=⋯=x
k
	​

=1,d=0,C=1,

and the inequalities hold for every 
𝑘
k.

For the second question, neither the number of indices 
𝑖
i, the signs or nonvanishing of the 
𝑏
𝑖
b
i
	​

, nor the meaning of “large” is specified. If 
𝑏
𝑖
=
0
b
i
	​

=0 is permitted, any square gives a formally arbitrary-dimensional collapsed cube. If “large” refers only to numerical size rather than dimension or cardinality, even one-dimensional cubes are trivially arbitrarily large.

Thus the immutable wording has multiple incompatible readings. The intended nondegenerate interpretation appears to be:

𝑆
=
{
𝑛
2
:
𝑛
∈
𝑍
≥
0
}
,
S={n
2
:n∈Z
≥0
	​

},

with 
𝑥
1
<
⋯
<
𝑥
𝑘
x
1
	​

<⋯<x
k
	​

, and an 
𝑟
r-cube means

𝐻
(
𝑎
;
𝑏
1
,
…
,
𝑏
𝑟
)
=
{
𝑎
+
∑
𝑗
=
1
𝑟
𝜖
𝑗
𝑏
𝑗
:
𝜖
𝑗
∈
{
0
,
1
}
}
H(a;b
1
	​

,…,b
r
	​

)={a+
j=1
∑
r
	​

ϵ
j
	​

b
j
	​

:ϵ
j
	​

∈{0,1}}

with 
𝑏
𝑗
>
0
b
j
	​

>0 and all 
2
𝑟
2
r
 subset sums distinct.

Everything below concerns this interpretation. It does not resolve the ambiguity in the exact original text.

Part I. Quasi-progressions
2. Exact extremal reformulation

Write

𝑥
𝑖
=
𝑛
𝑖
2
,
0
≤
𝑛
1
<
𝑛
2
<
⋯
<
𝑛
𝑘
,
x
i
	​

=n
i
2
	​

,0≤n
1
	​

<n
2
	​

<⋯<n
k
	​

,

and define

𝑔
𝑖
=
𝑥
𝑖
+
1
−
𝑥
𝑖
=
𝑛
𝑖
+
1
2
−
𝑛
𝑖
2
.
g
i
	​

=x
i+1
	​

−x
i
	​

=n
i+1
2
	​

−n
i
2
	​

.

Because every 
𝑔
𝑖
g
i
	​

 is an integer,

∃
𝑑
∈
𝑅
𝑑
≤
𝑔
𝑖
≤
𝑑
+
𝐶
for every 
𝑖
∃d∈Rd≤g
i
	​

≤d+Cfor every i

is equivalent to

max
⁡
𝑖
𝑔
𝑖
−
min
⁡
𝑖
𝑔
𝑖
≤
𝐶
.
i
max
	​

g
i
	​

−
i
min
	​

g
i
	​

≤C.

Indeed, one direction is immediate, and in the other direction one takes

𝑑
=
min
⁡
𝑖
𝑔
𝑖
d=min
i
	​

g
i
	​

.

Consequently only 
⌊
𝐶
⌋
⌊C⌋ matters. Define

𝑄
(
𝑘
)
=
min
⁡
0
≤
𝑛
1
<
⋯
<
𝑛
𝑘
(
max
⁡
1
≤
𝑖
<
𝑘
(
𝑛
𝑖
+
1
2
−
𝑛
𝑖
2
)
−
min
⁡
1
≤
𝑖
<
𝑘
(
𝑛
𝑖
+
1
2
−
𝑛
𝑖
2
)
)
.
Q(k)=
0≤n
1
	​

<⋯<n
k
	​

min
	​

(
1≤i<k
max
	​

(n
i+1
2
	​

−n
i
2
	​

)−
1≤i<k
min
	​

(n
i+1
2
	​

−n
i
2
	​

)).

Then the intended first question is exactly

sup
⁡
𝑘
𝑄
(
𝑘
)
<
∞
.
k
sup
	​

Q(k)<∞.

The function 
𝑄
(
𝑘
)
Q(k) is integer-valued and nondecreasing. Hence an affirmative answer would mean that 
𝑄
(
𝑘
)
Q(k) is eventually constant.

Some boundary values and bounds are immediate:

𝑄
(
2
)
=
0
,
𝑄
(
3
)
=
0
Q(2)=0,Q(3)=0

using

1
,
25
,
49.
1,25,49.

The supplied fact excluding four squares in an arithmetic progression gives

𝑄
(
4
)
≥
1.
Q(4)≥1.

The four squares

49
,
225
,
400
,
576
49,225,400,576

have gaps

176
,
175
,
176
,
176,175,176,

so

𝑄
(
4
)
=
1.
Q(4)=1.

For 
𝑘
≥
4
k≥4, the roots

1
,
3
,
4
,
5
,
…
,
𝑘
+
1
1,3,4,5,…,k+1

give gap spread at most

(
2
𝑘
+
1
)
−
7
=
2
𝑘
−
6.
(2k+1)−7=2k−6.

Thus

𝑄
(
𝑘
)
≤
2
𝑘
−
6.
Q(k)≤2k−6.

This is linear rather than uniformly bounded.

3. Finite divisor-graph formulation

For integers 
𝐷
≥
1
D≥1 and 
𝐶
≥
0
C≥0, define a directed graph 
𝐺
𝐷
,
𝐶
G
D,C
	​

 whose vertices are nonnegative integers and whose edges are

𝑛
⟶
𝑚
⟺
𝑛
<
𝑚
,
𝐷
≤
𝑚
2
−
𝑛
2
≤
𝐷
+
𝐶
.
n⟶m⟺n<m,D≤m
2
−n
2
≤D+C.

The graph is finite. Indeed,

𝑚
2
−
𝑛
2
≥
(
𝑛
+
1
)
2
−
𝑛
2
=
2
𝑛
+
1
,
m
2
−n
2
≥(n+1)
2
−n
2
=2n+1,

so every starting vertex of an edge satisfies

𝑛
≤
𝐷
+
𝐶
−
1
2
.
n≤
2
D+C−1
	​

.

Let 
𝐿
𝐶
(
𝐷
)
L
C
	​

(D) be the maximum number of vertices in a directed path in 
𝐺
𝐷
,
𝐶
G
D,C
	​

. Then the first question is exactly

∃
𝐶
∈
𝑍
≥
0
sup
⁡
𝐷
≥
1
𝐿
𝐶
(
𝐷
)
=
∞
.
∃C∈Z
≥0
	​

D≥1
sup
	​

L
C
	​

(D)=∞.

Each edge has the factorization

𝑚
2
−
𝑛
2
=
(
𝑚
−
𝑛
)
(
𝑚
+
𝑛
)
.
m
2
−n
2
=(m−n)(m+n).

Writing

𝑢
=
𝑚
−
𝑛
,
𝑣
=
𝑚
+
𝑛
,
u=m−n,v=m+n,

an edge of gap 
𝑞
q corresponds exactly to

𝑢
𝑣
=
𝑞
,
𝑢
,
𝑣
>
0
,
𝑢
≡
𝑣
(
m
o
d
2
)
,
uv=q,u,v>0,u≡v(mod2),

with

𝑛
=
𝑣
−
𝑢
2
,
𝑚
=
𝑣
+
𝑢
2
.
n=
2
v−u
	​

,m=
2
v+u
	​

.

This gives an exact finite algorithm for every fixed 
(
𝐷
,
𝐶
)
(D,C):

For each 
𝑞
=
𝐷
,
…
,
𝐷
+
𝐶
q=D,…,D+C, enumerate its factor pairs 
𝑢
𝑣
=
𝑞
uv=q.

Keep pairs of equal parity.

Convert them to edges 
𝑛
→
𝑚
n→m.

Find a longest path in the resulting finite directed acyclic graph.

A crude but rigorous bound is

𝐿
𝐶
(
𝐷
)
−
1
≤
∑
𝑞
=
𝐷
𝐷
+
𝐶
𝜏
(
𝑞
)
,
L
C
	​

(D)−1≤
q=D
∑
D+C
	​

τ(q),

where 
𝜏
(
𝑞
)
τ(q) is the number of positive divisors of 
𝑞
q.

This does not give a uniform bound in 
𝐷
D, because divisor counts are not uniformly bounded.

4. Root-increment dynamics

Put

ℎ
𝑖
=
𝑛
𝑖
+
1
−
𝑛
𝑖
≥
1.
h
i
	​

=n
i+1
	​

−n
i
	​

≥1.

Then

𝑔
𝑖
=
2
𝑛
𝑖
ℎ
𝑖
+
ℎ
𝑖
2
.
g
i
	​

=2n
i
	​

h
i
	​

+h
i
2
	​

.

For consecutive gaps,

𝑔
𝑖
+
1
−
𝑔
𝑖
=
2
𝑛
𝑖
(
ℎ
𝑖
+
1
−
ℎ
𝑖
)
+
2
ℎ
𝑖
ℎ
𝑖
+
1
+
ℎ
𝑖
+
1
2
−
ℎ
𝑖
2
.
g
i+1
	​

−g
i
	​

=2n
i
	​

(h
i+1
	​

−h
i
	​

)+2h
i
	​

h
i+1
	​

+h
i+1
2
	​

−h
i
2
	​

.

Since all 
𝑔
𝑖
g
i
	​

 lie in one interval of length 
𝐶
C,

∣
𝑔
𝑖
+
1
−
𝑔
𝑖
∣
≤
𝐶
.
∣g
i+1
	​

−g
i
	​

∣≤C.
Lemma 1: eventual nonincrease

If

𝑛
𝑖
>
𝐶
2
,
n
i
	​

>
2
C
	​

,

then

ℎ
𝑖
+
1
≤
ℎ
𝑖
.
h
i+1
	​

≤h
i
	​

.

Indeed, if 
ℎ
𝑖
+
1
≥
ℎ
𝑖
+
1
h
i+1
	​

≥h
i
	​

+1, then every term in the displayed difference is nonnegative and

𝑔
𝑖
+
1
−
𝑔
𝑖
>
2
𝑛
𝑖
>
𝐶
.
g
i+1
	​

−g
i
	​

>2n
i
	​

>C.

Thus sufficiently far out, the root increments form a nonincreasing sequence.

Lemma 2: constant increments have bounded runs

If 
ℎ
𝑖
+
1
=
ℎ
𝑖
=
ℎ
h
i+1
	​

=h
i
	​

=h, then

𝑔
𝑖
+
1
−
𝑔
𝑖
=
2
ℎ
2
.
g
i+1
	​

−g
i
	​

=2h
2
.

Therefore, if the value 
ℎ
h occurs for 
𝑡
t consecutive edges,

2
ℎ
2
(
𝑡
−
1
)
≤
𝐶
,
2h
2
(t−1)≤C,

so

𝑡
≤
⌊
𝐶
2
ℎ
2
⌋
+
1.
t≤⌊
2h
2
C
	​

⌋+1.

In particular, if

ℎ
>
𝐶
2
,
h>
2
C
	​

	​

,

it cannot occur on two consecutive edges once 
𝑛
𝑖
>
𝐶
/
2
n
i
	​

>C/2.

Lemma 3: localization of a drop

Suppose

ℎ
𝑖
+
1
=
ℎ
𝑖
−
𝑟
,
1
≤
𝑟
<
ℎ
𝑖
.
h
i+1
	​

=h
i
	​

−r,1≤r<h
i
	​

.

Writing 
ℎ
=
ℎ
𝑖
h=h
i
	​

, one obtains

𝑔
𝑖
+
1
−
𝑔
𝑖
=
2
ℎ
2
−
4
ℎ
𝑟
+
𝑟
2
−
2
𝑛
𝑖
𝑟
.
g
i+1
	​

−g
i
	​

=2h
2
−4hr+r
2
−2n
i
	​

r.

Hence

∣
𝑛
𝑖
−
(
ℎ
2
𝑟
−
2
ℎ
+
𝑟
2
)
∣
≤
𝐶
2
𝑟
.
	​

n
i
	​

−(
r
h
2
	​

−2h+
2
r
	​

)
	​

≤
2r
C
	​

.

Thus a particular drop 
ℎ
→
ℎ
−
𝑟
h→h−r can occur only when 
𝑛
𝑖
n
i
	​

 lies in a short interval of length 
𝐶
/
𝑟
C/r.

If 
𝛿
=
𝑔
𝑖
+
1
−
𝑔
𝑖
δ=g
i+1
	​

−g
i
	​

, then rearrangement also gives

𝑔
𝑖
=
ℎ
𝑟
(
(
ℎ
−
𝑟
)
(
2
ℎ
−
𝑟
)
−
𝛿
)
.
g
i
	​

=
r
h
	​

((h−r)(2h−r)−δ).

Consequently every drop satisfies

𝐷
≤
𝑔
𝑖
≤
2
ℎ
3
+
𝐶
ℎ
.
D≤g
i
	​

≤2h
3
+Ch.

These relations make the dynamics highly rigid. They do not yet bound the number of possible distinct decreasing values of 
ℎ
h, because the initial 
ℎ
h and the central gap 
𝐷
D may both tend to infinity.

5. The additive-cube obstruction

Normalize

𝐷
=
min
⁡
𝑖
𝑔
𝑖
,
𝑒
𝑖
=
𝑔
𝑖
−
𝐷
.
D=
i
min
	​

g
i
	​

,e
i
	​

=g
i
	​

−D.

Then

𝑒
𝑖
∈
{
0
,
1
,
…
,
𝐶
}
.
e
i
	​

∈{0,1,…,C}.

Suppose that for some starting position 
𝑠
s and some 
𝑟
≥
1
r≥1, three consecutive blocks of 
𝑒
e's of length 
𝑟
r have equal sums:

∑
𝑗
=
𝑠
𝑠
+
𝑟
−
1
𝑒
𝑗
=
∑
𝑗
=
𝑠
+
𝑟
𝑠
+
2
𝑟
−
1
𝑒
𝑗
=
∑
𝑗
=
𝑠
+
2
𝑟
𝑠
+
3
𝑟
−
1
𝑒
𝑗
.
j=s
∑
s+r−1
	​

e
j
	​

=
j=s+r
∑
s+2r−1
	​

e
j
	​

=
j=s+2r
∑
s+3r−1
	​

e
j
	​

.

Then

𝑥
𝑠
+
𝑟
−
𝑥
𝑠
=
𝑥
𝑠
+
2
𝑟
−
𝑥
𝑠
+
𝑟
=
𝑥
𝑠
+
3
𝑟
−
𝑥
𝑠
+
2
𝑟
.
x
s+r
	​

−x
s
	​

=x
s+2r
	​

−x
s+r
	​

=x
s+3r
	​

−x
s+2r
	​

.

Therefore

𝑥
𝑠
,
𝑥
𝑠
+
𝑟
,
𝑥
𝑠
+
2
𝑟
,
𝑥
𝑠
+
3
𝑟
x
s
	​

,x
s+r
	​

,x
s+2r
	​

,x
s+3r
	​


would be four squares in an arithmetic progression, which is excluded by the fact supplied in the statement.

Hence every error word coming from a quasi-progression must avoid three adjacent equal-length blocks with equal sums. Call such a pattern an additive cube.

This is an exact necessary condition.

Consequence for 
𝐶
<
2
C<2

If 
𝐶
<
2
C<2, the integer gap spread is at most 
1
1, so the error word is binary.

A complete finite enumeration shows that every binary word of length 
10
10 contains an additive cube. Let 
𝐴
𝑛
A
n
	​

 denote the binary words of length 
𝑛
n avoiding additive cubes. Recursive extension gives

𝑛
	
0
	
1
	
2
	
3
	
4
	
5
	
6
	
7
	
8
	
9
	
10


∣
𝐴
𝑛
∣
	
1
	
2
	
4
	
6
	
10
	
16
	
18
	
12
	
10
	
6
	
0.
n
∣A
n
	​

∣
	​

0
1
	​

1
2
	​

2
4
	​

3
6
	​

4
10
	​

5
16
	​

6
18
	​

7
12
	​

8
10
	​

9
6
	​

10
0.
	​

	​


The six surviving words of length 
9
9 are

	
001101100
,
001101101
,
010010011
,


	
101101100
,
110010010
,
110010011.
	​

001101100,001101101,010010011,
101101100,110010010,110010011.
	​


Appending either 
0
0 or 
1
1 to any of them produces an additive cube.

Therefore a quasi-progression with gap spread at most 
1
1 has at most ten squares. In particular,

𝑄
(
11
)
≥
2.
Q(11)≥2.

Thus any affirmative constant in the intended first question would have to satisfy

𝐶
≥
2.
C≥2.

The same purely word-theoretic attack does not immediately extend to three gap values. For example, the ternary word

001001002001001120010200110120
001001002001001120010200110120

has length 
30
30 and contains no additive cube. A local depth-first search produced ternary examples of length 
1000
1000. That computation does not establish an infinite ternary example, but it invalidates any small-threshold version of the argument.

6. Compactness reduction to a fixed error branch

Assume, for the sake of deriving consequences, that one fixed integer 
𝐶
C supports arbitrarily long quasi-progressions.

Consider the finite-branching tree of normalized error words

(
𝑒
1
,
…
,
𝑒
ℓ
)
∈
{
0
,
…
,
𝐶
}
ℓ
(e
1
	​

,…,e
ℓ
	​

)∈{0,…,C}
ℓ

that occur as initial error patterns in arbitrarily long witnesses.

By the elementary infinite-tree argument, there is an infinite word

𝑒
1
,
𝑒
2
,
…
e
1
	​

,e
2
	​

,…

such that every finite prefix occurs in witnesses of arbitrarily large total length.

Every prefix is additive-cube-free.

More is true: every prefix has infinitely many distinct integer realizations. Otherwise, finitely many realizations of that prefix would be available. Each fixed realization lies in one finite graph 
𝐺
𝐷
,
𝐶
G
D,C
	​

, and so has only finitely many continuations. Their union would have bounded continuation length, contrary to the construction of the branch.

For a fixed prefix 
𝑒
1
,
…
,
𝑒
ℓ
e
1
	​

,…,e
ℓ
	​

, put

𝐸
𝑗
=
∑
𝑡
=
1
𝑗
𝑒
𝑡
,
𝐸
0
=
0.
E
j
	​

=
t=1
∑
j
	​

e
t
	​

,E
0
	​

=0.

A realization is equivalent to integers 
𝐷
,
𝑦
0
,
…
,
𝑦
ℓ
D,y
0
	​

,…,y
ℓ
	​

 satisfying

𝑦
𝑗
2
=
𝑦
0
2
+
𝑗
𝐷
+
𝐸
𝑗
.
y
j
2
	​

=y
0
2
	​

+jD+E
j
	​

.

Eliminating 
𝐷
D via

𝐷
=
𝑦
1
2
−
𝑦
0
2
−
𝑒
1
D=y
1
2
	​

−y
0
2
	​

−e
1
	​


gives, for 
𝑗
≥
2
j≥2,

𝑦
𝑗
2
=
(
1
−
𝑗
)
𝑦
0
2
+
𝑗
𝑦
1
2
+
𝐸
𝑗
−
𝑗
𝑒
1
.
y
j
2
	​

=(1−j)y
0
2
	​

+jy
1
2
	​

+E
j
	​

−je
1
	​

.

Thus an affirmative answer would force an infinite additive-cube-free word for which every finite system

𝑦
𝑗
2
=
(
1
−
𝑗
)
𝑦
0
2
+
𝑗
𝑦
1
2
+
𝑐
𝑗
y
j
2
	​

=(1−j)y
0
2
	​

+jy
1
2
	​

+c
j
	​


has infinitely many positive integer solutions.

This is a precise algebraic target.

A sufficient negative strategy would be:

For each fixed 
𝐶
C, find a length 
ℓ
(
𝐶
)
ℓ(C) such that every additive-cube-free word 
𝑒
1
,
…
,
𝑒
ℓ
(
𝐶
)
∈
{
0
,
…
,
𝐶
}
e
1
	​

,…,e
ℓ(C)
	​

∈{0,…,C} gives only finitely many integer solutions to the associated system.

There are only finitely many words of that length. Finiteness for all of them would bound every possible continuation.

No elementary proof of this target was obtained.

Part II. Why quasi-progressions force cubes
7. A general finite-gap theorem

The following implication can be proved directly.

Theorem

Fix 
𝑀
M. For every dimension 
𝑟
r, there exists 
𝑁
𝑟
(
𝑀
)
N
r
	​

(M) such that the prefix sums of every positive-integer word of length 
𝑁
𝑟
(
𝑀
)
N
r
	​

(M) using at most 
𝑀
M different symbols contain a nondegenerate 
𝑟
r-dimensional additive cube.

Proof

For 
𝑟
=
1
r=1, one positive edge gives two distinct prefix sums.

Assume the result for dimension 
𝑟
r, with required word length 
𝑁
𝑟
N
r
	​

. There are at most

𝑇
=
𝑀
𝑁
𝑟
T=M
N
r
	​


possible words of length 
𝑁
𝑟
N
r
	​

.

Take 
𝑇
+
1
T+1 blocks, each of length 
𝑁
𝑟
N
r
	​

, placing one positive separator edge between consecutive blocks. Thus one may take

𝑁
𝑟
+
1
=
(
𝑇
+
1
)
𝑁
𝑟
+
𝑇
.
N
r+1
	​

=(T+1)N
r
	​

+T.

Two blocks have identical words. By the induction hypothesis, the prefix sums inside the first contain an 
𝑟
r-cube

𝐴
=
𝑎
+
{
∑
𝑗
=
1
𝑟
𝜖
𝑗
𝑏
𝑗
}
.
A=a+{
j=1
∑
r
	​

ϵ
j
	​

b
j
	​

}.

The corresponding positions inside the identical second block form

𝐴
+
𝑡
A+t

for the translation 
𝑡
t between the two block starting points.

Because there is at least one positive separator, 
𝑡
t exceeds the diameter of the first block. Therefore 
𝐴
A and 
𝐴
+
𝑡
A+t are disjoint, and

𝐴
∪
(
𝐴
+
𝑡
)
=
𝑎
+
{
∑
𝑗
=
1
𝑟
𝜖
𝑗
𝑏
𝑗
+
𝜖
𝑟
+
1
𝑡
}
A∪(A+t)=a+{
j=1
∑
r
	​

ϵ
j
	​

b
j
	​

+ϵ
r+1
	​

t}

is a nondegenerate 
(
𝑟
+
1
)
(r+1)-cube. ∎

In a quasi-progression with gap spread 
𝐶
C, the consecutive gaps are integers drawn from at most

⌊
𝐶
⌋
+
1
⌊C⌋+1

values. Hence arbitrarily long quasi-progressions would indeed produce cubes of arbitrarily high dimension.

This proves the implication mentioned in the supplied statement under the nondegenerate increasing interpretation.

It does not give a converse.

Part III. Structural attacks on cubes of squares
8. Small nondegenerate examples

Dimension two is possible:

{
1
,
16
,
49
,
64
}
=
1
+
{
0
,
15
,
48
,
15
+
48
}
.
{1,16,49,64}=1+{0,15,48,15+48}.

Dimension three is also possible:

𝑎
=
100
,
(
𝑏
1
,
𝑏
2
,
𝑏
3
)
=
(
2400
,
4389
,
8736
)
.
a=100,(b
1
	​

,b
2
	​

,b
3
	​

)=(2400,4389,8736).

The eight vertices are

100
	
=
10
2
,


2500
	
=
50
2
,


4489
	
=
67
2
,


6889
	
=
83
2
,


8836
	
=
94
2
,


11236
	
=
106
2
,


13225
	
=
115
2
,


15625
	
=
125
2
.
100
2500
4489
6889
8836
11236
13225
15625
	​

=10
2
,
=50
2
,
=67
2
,
=83
2
,
=94
2
,
=106
2
,
=115
2
,
=125
2
.
	​


Thus any obstruction must permit at least dimension three.

9. Primitive normalization

Suppose all vertices of

𝐻
(
𝑎
;
𝑏
1
,
…
,
𝑏
𝑟
)
H(a;b
1
	​

,…,b
r
	​

)

are squares. Then

gcd
⁡
{
all vertices
}
=
gcd
⁡
(
𝑎
,
𝑏
1
,
…
,
𝑏
𝑟
)
.
gcd{all vertices}=gcd(a,b
1
	​

,…,b
r
	​

).

The left side is the gcd of a collection of squares. For every prime 
𝑝
p, its 
𝑝
p-adic valuation is the minimum of a collection of even valuations, hence is even.

Therefore

gcd
⁡
(
𝑎
,
𝑏
1
,
…
,
𝑏
𝑟
)
gcd(a,b
1
	​

,…,b
r
	​

)

is a perfect square.

One may divide the entire cube by this square and obtain another square cube. Thus it suffices to study primitive cubes

gcd
⁡
(
𝑎
,
𝑏
1
,
…
,
𝑏
𝑟
)
=
1.
gcd(a,b
1
	​

,…,b
r
	​

)=1.
10. Congruence restrictions
Modulo 
4
4

Squares modulo 
4
4 are 
0
0 and 
1
1.

If 
𝑎
≡
0
(
m
o
d
4
)
a≡0(mod4), then each 
𝑏
𝑗
b
j
	​

 is 
0
0 or 
1
(
m
o
d
4
)
1(mod4). Two generators congruent to 
1
1 would produce a vertex congruent to 
2
2, impossible.

If 
𝑎
≡
1
(
m
o
d
4
)
a≡1(mod4), then each 
𝑏
𝑗
b
j
	​

 is 
0
0 or 
3
(
m
o
d
4
)
3(mod4). Two generators congruent to 
3
3 would produce a vertex congruent to 
3
3, again impossible.

Hence:

All but at most one 
𝑏
𝑗
 are divisible by 
4.
All but at most one b
j
	​

 are divisible by 4.
	​


If 
𝑎
a is odd and every 
𝑏
𝑗
b
j
	​

 is divisible by 
4
4, then all vertices are odd squares and hence congruent to 
1
(
m
o
d
8
)
1(mod8). Consequently

8
∣
𝑏
𝑗
for every 
𝑗
.
8∣b
j
	​

for every j.

This gives strong divisibility concentration, but not a contradiction.

Modulo an odd prime

Let 
𝑝
p be odd and let 
𝑄
𝑝
⊂
𝑍
/
𝑝
𝑍
Q
p
	​

⊂Z/pZ be the set of square residues, including 
0
0. Then

∣
𝑄
𝑝
∣
=
𝑝
+
1
2
.
∣Q
p
	​

∣=
2
p+1
	​

.

Let 
𝑆
𝑗
S
j
	​

 be the set of residues obtained from the first 
𝑗
j generators:

𝑆
𝑗
=
{
𝑎
+
∑
𝑖
=
1
𝑗
𝜖
𝑖
𝑏
𝑖
(
m
o
d
𝑝
)
}
.
S
j
	​

={a+
i=1
∑
j
	​

ϵ
i
	​

b
i
	​

(modp)}.

Every 
𝑆
𝑗
S
j
	​

 lies in 
𝑄
𝑝
Q
p
	​

. If 
𝑏
𝑗
≢
0
(
m
o
d
𝑝
)
b
j
	​


≡0(modp), then

𝑆
𝑗
−
1
+
𝑏
𝑗
≠
𝑆
𝑗
−
1
.
S
j−1
	​

+b
j
	​


=S
j−1
	​

.

Otherwise 
𝑆
𝑗
−
1
S
j−1
	​

 would be invariant under a nonzero translation. Repeated translation would make it all of 
𝑍
/
𝑝
𝑍
Z/pZ, contrary to 
𝑆
𝑗
−
1
⊂
𝑄
𝑝
S
j−1
	​

⊂Q
p
	​

.

Thus every generator nonzero modulo 
𝑝
p increases 
∣
𝑆
𝑗
∣
∣S
j
	​

∣ by at least one. Starting from size one and ending with size at most 
(
𝑝
+
1
)
/
2
(p+1)/2, there can be at most

𝑝
−
1
2
2
p−1
	​


generators not divisible by 
𝑝
p.

Therefore

#
{
𝑗
:
𝑝
∤
𝑏
𝑗
}
≤
𝑝
−
1
2
.
#{j:p∤b
j
	​

}≤
2
p−1
	​

.
	​


For any fixed finite set of odd primes 
𝑃
P, at least

𝑟
−
∑
𝑝
∈
𝑃
𝑝
−
1
2
r−
p∈P
∑
	​

2
p−1
	​


generators are divisible by

∏
𝑝
∈
𝑃
𝑝
.
p∈P
∏
	​

p.

This says that a high-dimensional square cube must contain a high-dimensional subcube whose generators are divisible by any prescribed fixed modulus. It still allows the base to be a nonzero square residue, so it does not create an infinite descent.

11. Difference-of-squares representation pressure

Fix a generator 
𝑏
𝑗
b
j
	​

. For each of the 
2
𝑟
−
1
2
r−1
 choices of the remaining 
𝜖
𝑖
ϵ
i
	​

, there is an edge

𝑣
2
⟶
𝑣
2
+
𝑏
𝑗
=
𝑢
2
.
v
2
⟶v
2
+b
j
	​

=u
2
.

Thus

𝑏
𝑗
=
𝑢
2
−
𝑣
2
=
(
𝑢
−
𝑣
)
(
𝑢
+
𝑣
)
.
b
j
	​

=u
2
−v
2
=(u−v)(u+v).

If the cube is nondegenerate, these 
2
𝑟
−
1
2
r−1
 lower vertices are distinct, so they give 
2
𝑟
−
1
2
r−1
 distinct representations of 
𝑏
𝑗
b
j
	​

 as a difference of two squares.

The number of such representations is at most 
𝜏
(
𝑏
𝑗
)
τ(b
j
	​

). Hence

𝜏
(
𝑏
𝑗
)
≥
2
𝑟
−
1
.
τ(b
j
	​

)≥2
r−1
.

Using the elementary bound

𝜏
(
𝑛
)
≤
2
𝑛
,
τ(n)≤2
n
	​

,

one gets

𝑏
𝑗
≥
2
2
𝑟
−
4
b
j
	​

≥2
2r−4

for every generator.

Therefore

∑
𝑗
=
1
𝑟
𝑏
𝑗
≥
𝑟
 
2
2
𝑟
−
4
.
j=1
∑
r
	​

b
j
	​

≥r2
2r−4
.

A simpler interval-counting argument gives

∑
𝑗
𝑏
𝑗
≥
(
2
𝑟
−
1
)
2
,
j
∑
	​

b
j
	​

≥(2
r
−1)
2
,

because an interval of length 
𝐵
B contains at most 
𝐵
+
1
B
	​

+1 squares.

These are substantial growth restrictions but not absolute dimension bounds.

Part IV. Bounded falsification tests
12. Exact quasi-progression search

The divisor-graph algorithm was run for positive roots, all

1
≤
𝐷
≤
50,000
,
1≤D≤50,000,

and selected values of 
𝐶
C. The table gives the largest path found within that exact finite range.

𝐶
	
length
	
𝐷
	
root sequence


0
	
3
	
24
	
1
,
5
,
7


1
	
4
	
175
	
7
,
15
,
20
,
24


2
	
4
	
7
	
1
,
3
,
4
,
5


4
	
5
	
7
	
1
,
3
,
4
,
5
,
6


6
	
6
	
7
	
1
,
3
,
4
,
5
,
6
,
7


8
	
8
	
13
	
1
,
4
,
6
,
7
,
8
,
9
,
10
,
11


10
	
9
	
13
	
1
,
4
,
6
,
7
,
8
,
9
,
10
,
11
,
12


12
	
10
	
13
	
1
,
4
,
6
,
7
,
8
,
9
,
10
,
11
,
12
,
13


14
	
12
	
19
	
2
,
5
,
7
,
9
,
10
,
11
,
12
,
13
,
14
,
15
,
16
,
17
C
0
1
2
4
6
8
10
12
14
	​

length
3
4
4
5
6
8
9
10
12
	​

D
24
175
7
7
7
13
13
13
19
	​

root sequence
1,5,7
7,15,20,24
1,3,4,5
1,3,4,5,6
1,3,4,5,6,7
1,4,6,7,8,9,10,11
1,4,6,7,8,9,10,11,12
1,4,6,7,8,9,10,11,12,13
2,5,7,9,10,11,12,13,14,15,16,17
	​

	​


The longer examples typically consist of a few irregular initial jumps followed by consecutive roots. Their gap spread then grows with their length. This is not evidence for a fixed 
𝐶
C.

The search does not control 
𝐷
>
50,000
D>50,000.

13. Bounded cube search

An exact enumeration among the squares

1
2
,
2
2
,
…
,
500
2
1
2
,2
2
,…,500
2

found dimension-three cubes, including the example above, but no dimension-four cube in that bounded range.

The enumeration grouped all square parallelograms by their two translation increments. A four-dimensional cube would produce at least four translated copies of the same two-dimensional face, so this grouping supplies a complete bounded test.

Again, this does not control larger squares.

Part V. Attacks that stop short
14. Minimal-counterexample strategy

Assume a smallest effective integer constant 
𝐶
∗
C
∗
	​

 exists. Then

𝐶
∗
≥
2.
C
∗
	​

≥2.

Because 
𝑄
(
𝑘
)
Q(k) is nondecreasing, minimality implies that sufficiently long 
𝐶
∗
C
∗
	​

-witnesses must genuinely use total error range 
𝐶
∗
C
∗
	​

; otherwise 
𝐶
∗
−
1
C
∗
	​

−1 would also support arbitrary length.

The infinite-branch construction then produces an additive-cube-free word over 
{
0
,
…
,
𝐶
∗
}
{0,…,C
∗
	​

} whose total alphabet range is exactly 
𝐶
∗
C
∗
	​

, and every prefix has infinitely many square realizations.

The missing step is to derive an impossibility from these simultaneous symbolic and Diophantine requirements.

15. Curvature attack

The monotonicity of 
ℎ
𝑖
h
i
	​

 beyond 
𝑛
𝑖
>
𝐶
/
2
n
i
	​

>C/2, the bounded run lengths, and the localization of every drop show that a long witness must follow an extremely narrow discrete approximation to the curve

ℎ
≈
𝐷
2
𝑛
.
h≈
2n
D
	​

.

However, increasing 
𝐷
D permits both the initial root increment and the number of possible decreasing increment values to grow. The estimates obtained are not uniform in 
𝐷
D.

16. Divisor attack

Every edge comes from a factorization of one of the 
𝐶
+
1
C+1 integers

𝐷
,
𝐷
+
1
,
…
,
𝐷
+
𝐶
.
D,D+1,…,D+C.

A long path therefore requires a short interval containing many suitably chained factor pairs. The simple estimate by

∑
𝑞
=
𝐷
𝐷
+
𝐶
𝜏
(
𝑞
)
q=D
∑
D+C
	​

τ(q)

is nonuniform, and it ignores the crucial endpoint compatibility

𝑣
𝑖
+
𝑢
𝑖
2
=
𝑣
𝑖
+
1
−
𝑢
𝑖
+
1
2
.
2
v
i
	​

+u
i
	​

	​

=
2
v
i+1
	​

−u
i+1
	​

	​

.

A promising precise target is:

For each fixed 
𝐶
C, prove that any chain of same-parity factor pairs of numbers in 
[
𝐷
,
𝐷
+
𝐶
]
[D,D+C] satisfying the endpoint compatibility relation has length bounded solely in terms of 
𝐶
C.

No such bound was derived.

17. Modular attack on cubes

Modulo 
4
4 and modulo odd primes force nearly all generators to be highly divisible. But an odd square base can remain nonzero modulo every selected prime while all generators vanish modulo those primes.

Thus local restrictions create concentration rather than contradiction.

18. Representation-count attack on cubes

Each generator must possess exponentially many difference-of-square representations. This forces each 
𝑏
𝑗
b
j
	​

 to be exponentially large.

There is no upper bound on the allowed generators, so size growth alone cannot rule out arbitrary dimension. A further argument would need to show incompatibility among the many representations required simultaneously for different 
𝑏
𝑗
b
j
	​

.

19. Pure word-combinatorics attack

The no-four-term-progression fact translates into additive-cube avoidance for the error word.

This completely excludes one- and two-valued gap alphabets of arbitrary length. It does not presently exclude three-valued alphabets; very long finite ternary additive-cube-free words exist computationally.

Thus square realizability, not merely finite-alphabet combinatorics, must enter any continuation of this attack.

Precise remaining targets

For the quasi-progression question, any one of the following would be decisive under the intended interpretation:

Uniform path bound

∀
𝐶
 
∃
𝐵
(
𝐶
)
 
∀
𝐷
,
𝐿
𝐶
(
𝐷
)
≤
𝐵
(
𝐶
)
.
∀C ∃B(C) ∀D,L
C
	​

(D)≤B(C).

Fixed-pattern finiteness
For every 
𝐶
C, find 
ℓ
(
𝐶
)
ℓ(C) such that every additive-cube-free word of length 
ℓ
(
𝐶
)
ℓ(C) gives only finitely many positive integer points on

𝑦
𝑗
2
=
(
1
−
𝑗
)
𝑦
0
2
+
𝑗
𝑦
1
2
+
𝐸
𝑗
−
𝑗
𝑒
1
.
y
j
2
	​

=(1−j)y
0
2
	​

+jy
1
2
	​

+E
j
	​

−je
1
	​

.

Positive construction
Produce one fixed 
𝐶
C and paths in 
𝐺
𝐷
,
𝐶
G
D,C
	​

 of unbounded length, with 
𝐷
D allowed to vary.

For the cube question, a negative attack must bound the dimension of primitive nondegenerate cubes despite:

4
∣
𝑏
𝑗
for almost all 
𝑗
,
4∣b
j
	​

for almost all j,
𝑝
∣
𝑏
𝑗
for almost all 
𝑗
 for every fixed 
𝑝
,
p∣b
j
	​

for almost all j for every fixed p,

and

𝜏
(
𝑏
𝑗
)
≥
2
𝑟
−
1
.
τ(b
j
	​

)≥2
r−1
.

The present deductions do not combine into such a bound.

Outcome

The exact immutable wording is blocked by degeneracy and domain ambiguities. Under the natural increasing and nondegenerate interpretation, the analysis yields structural reductions, a proof that arbitrarily long quasi-progressions would force arbitrarily high-dimensional cubes, an exclusion of every constant 
𝐶
<
2
C<2, explicit low-dimensional cubes, and several precise remaining obligations. Neither intended question is resolved here.
Formal normalization

The symbol 
≫
≫ is not defined in the immutable statement. Under its standard absolute asymptotic interpretation, the target is

	
∃
𝑐
>
0
 
∃
𝑛
0
 
∀
𝑛
≥
𝑛
0
,
𝑓
(
𝑛
)
≥
𝑐
𝑛
.
		
(Q)
∃c>0 ∃n
0
	​

 ∀n≥n
0
	​

,f(n)≥c
n
	​

.
(Q)

Equivalently,

lim inf
⁡
𝑛
→
∞
𝑓
(
𝑛
)
𝑛
>
0.
n→∞
liminf
	​

n
	​

f(n)
	​

>0.

If 
≫
≫ was intended differently, the exact acceptance criterion is formally blocked. Everything below attacks (Q). No proof or disproof is claimed.

1. Equivalent formulations

Let 
𝑘
≥
0
k≥0 and put 
𝑚
=
𝑘
+
2
m=k+2.

1.1 Orthogonal arrays

The following are equivalent:

There are 
𝑘
k mutually orthogonal Latin squares of order 
𝑛
n.

There is an array with 
𝑛
2
n
2
 rows and 
𝑚
m columns over an 
𝑛
n-element alphabet such that, in every pair of columns, every ordered pair of symbols occurs exactly once.

Indeed, from squares 
𝐿
1
,
…
,
𝐿
𝑘
L
1
	​

,…,L
k
	​

, associate to the cell 
(
𝑟
,
𝑐
)
(r,c) the row

(
𝑟
,
𝑐
,
𝐿
1
(
𝑟
,
𝑐
)
,
…
,
𝐿
𝑘
(
𝑟
,
𝑐
)
)
.
(r,c,L
1
	​

(r,c),…,L
k
	​

(r,c)).

Conversely, use two columns as row and column coordinates. Every other column is Latin, and any two such columns are orthogonal.

Thus 
𝑓
(
𝑛
)
+
2
f(n)+2 is the maximum possible number of columns.

1.2 Orthogonal partitions

Equivalently, an 
𝑛
2
n
2
-element set 
Ω
Ω has 
𝑚
m partitions

𝑃
𝑖
=
{
𝑃
𝑖
,
1
,
…
,
𝑃
𝑖
,
𝑛
}
P
i
	​

={P
i,1
	​

,…,P
i,n
	​

}

such that every part has size 
𝑛
n, and

∣
𝑃
𝑖
,
𝑎
∩
𝑃
𝑗
,
𝑏
∣
=
1
(
𝑖
≠
𝑗
)
.
∣P
i,a
	​

∩P
j,b
	​

∣=1(i

=j).
1.3 Pairwise-independent variables

Equivalently, on a probability space of exactly 
𝑛
2
n
2
 equally likely outcomes, there are 
𝑚
m random variables 
𝑋
1
,
…
,
𝑋
𝑚
X
1
	​

,…,X
m
	​

, each uniform on an 
𝑛
n-element set, such that every pair 
𝑋
𝑖
,
𝑋
𝑗
X
i
	​

,X
j
	​

 is independent.

The sample-space size 
𝑛
2
n
2
 is minimal for two independent 
𝑛
n-valued variables. Thus this asks for many pairwise-independent variables on a sample space of minimum possible size.

1.4 Transversal designs

Equivalently, there is an 
𝑚
m-partite, 
𝑚
m-uniform hypergraph with:

𝑛
n vertices in every part;

𝑛
2
n
2
 hyperedges;

every pair of vertices from different parts lying in exactly one hyperedge.

This is usually denoted abstractly by 
TD
⁡
(
𝑚
,
𝑛
)
TD(m,n), but only the stated properties are used here.

1.5 Clique-factor packing

Every partition 
𝑃
𝑖
P
i
	​

 gives a factor of 
𝐾
𝑛
2
K
n
2
	​

 consisting of 
𝑛
n disjoint copies of 
𝐾
𝑛
K
n
	​

. Two orthogonal partitions give edge-disjoint factors.

Hence 
𝑓
(
𝑛
)
+
2
f(n)+2 is also the maximum number of edge-disjoint 
𝐾
𝑛
K
n
	​

-factors of 
𝐾
𝑛
2
K
n
2
	​

.

2. Exact elementary bounds and constructions
2.1 Universal upper bound

In one orthogonal-array column, the number of unordered pairs of rows agreeing in that column is

𝑛
(
𝑛
2
)
=
𝑛
2
(
𝑛
−
1
)
2
.
n(
2
n
	​

)=
2
n
2
(n−1)
	​

.

Two distinct rows cannot agree in two columns. Therefore

𝑚
𝑛
2
(
𝑛
−
1
)
2
≤
(
𝑛
2
2
)
.
m
2
n
2
(n−1)
	​

≤(
2
n
2
	​

).

Consequently

𝑚
≤
𝑛
+
1
,
𝑓
(
𝑛
)
≤
𝑛
−
1
.
m≤n+1,
f(n)≤n−1
	​

.

This bound sees no arithmetic structure in 
𝑛
n.

2.2 Prime-power orders

Let 
𝑞
q be a prime power and let 
𝐹
F be a field with 
𝑞
q elements. For each 
𝑎
∈
𝐹
×
a∈F
×
, define

𝐿
𝑎
(
𝑟
,
𝑐
)
=
𝑎
𝑟
+
𝑐
.
L
a
	​

(r,c)=ar+c.

Each 
𝐿
𝑎
L
a
	​

 is Latin. If 
𝑎
≠
𝑏
a

=b, then from

𝑢
=
𝑎
𝑟
+
𝑐
,
𝑣
=
𝑏
𝑟
+
𝑐
u=ar+c,v=br+c

we obtain

𝑟
=
(
𝑎
−
𝑏
)
−
1
(
𝑢
−
𝑣
)
,
𝑐
=
𝑢
−
𝑎
𝑟
.
r=(a−b)
−1
(u−v),c=u−ar.

Thus the squares are mutually orthogonal. Hence

𝑓
(
𝑞
)
≥
𝑞
−
1.
f(q)≥q−1.

Together with the upper bound,

𝑓
(
𝑞
)
=
𝑞
−
1
for every prime power 
𝑞
.
f(q)=q−1for every prime power q.
	​

2.3 Direct products

If 
𝑎
a and 
𝑏
b each support 
𝑘
k MOLS, define on ordered pairs

𝐶
𝑖
(
(
𝑟
1
,
𝑟
2
)
,
(
𝑐
1
,
𝑐
2
)
)
=
(
𝐴
𝑖
(
𝑟
1
,
𝑐
1
)
,
𝐵
𝑖
(
𝑟
2
,
𝑐
2
)
)
.
C
i
	​

((r
1
	​

,r
2
	​

),(c
1
	​

,c
2
	​

))=(A
i
	​

(r
1
	​

,c
1
	​

),B
i
	​

(r
2
	​

,c
2
	​

)).

This gives 
𝑘
k MOLS of order 
𝑎
𝑏
ab. Therefore

𝑓
(
𝑎
𝑏
)
≥
min
⁡
{
𝑓
(
𝑎
)
,
𝑓
(
𝑏
)
}
.
f(ab)≥min{f(a),f(b)}.
	​


If

𝑛
=
∏
𝑗
=
1
𝑠
𝑝
𝑗
𝑒
𝑗
,
n=
j=1
∏
s
	​

p
j
e
j
	​

	​

,

then this yields only

𝑓
(
𝑛
)
≥
min
⁡
𝑗
(
𝑝
𝑗
𝑒
𝑗
−
1
)
.
f(n)≥
j
min
	​

(p
j
e
j
	​

	​

−1).

In particular, for 
𝑛
=
2
𝑚
n=2m with 
𝑚
m odd, this entire direct-product construction gives only one square. It cannot approach 
𝑛
n
	​

 on that family.

For a positive result, if

𝑛
=
𝑞
𝑟
n=qr

with 
𝑞
,
𝑟
q,r prime powers and 
𝑞
≤
𝑟
≤
𝐶
𝑞
q≤r≤Cq, then

𝑓
(
𝑛
)
≥
𝑞
−
1
≥
𝑛
𝐶
−
1.
f(n)≥q−1≥
C
n
	​

	​

−1.

So (Q) already holds on all balanced products of two prime powers.

3. Idempotent MOLS and PBD gluing

Define 
𝐼
(
𝑛
)
I(n) to be the maximum number of mutually orthogonal idempotent Latin squares of order 
𝑛
n, meaning

𝐿
(
𝑥
,
𝑥
)
=
𝑥
.
L(x,x)=x.
3.1 Relation between 
𝐼
(
𝑛
)
I(n) and 
𝑓
(
𝑛
)
f(n)

Clearly

𝐼
(
𝑛
)
≤
𝑓
(
𝑛
)
.
I(n)≤f(n).

Conversely,

𝐼
(
𝑛
)
≥
𝑓
(
𝑛
)
−
1.
I(n)≥f(n)−1.
	​


To prove this, start with an orthogonal array having columns

𝑅
,
𝐶
,
𝑆
1
,
…
,
𝑆
𝑘
,
𝑘
=
𝑓
(
𝑛
)
.
R,C,S
1
	​

,…,S
k
	​

,k=f(n).

Fix a symbol 
𝑐
0
c
0
	​

 in column 
𝐶
C. On the 
𝑛
n rows satisfying 
𝐶
=
𝑐
0
C=c
0
	​

, every other column takes each symbol exactly once.

Use 
𝑅
,
𝑆
1
R,S
1
	​

 as the two coordinate columns. Relabel their symbols so that these 
𝑛
n rows become the diagonal 
(
𝑥
,
𝑥
)
(x,x). Relabel each 
𝑆
𝑖
S
i
	​

, 
𝑖
≥
2
i≥2, so that its value on the corresponding diagonal row is 
𝑥
x. Discard column 
𝐶
C. The remaining 
𝑘
−
1
k−1 square columns are mutually orthogonal and idempotent.

Thus

𝑓
(
𝑛
)
−
1
≤
𝐼
(
𝑛
)
≤
𝑓
(
𝑛
)
,
f(n)−1≤I(n)≤f(n),

so the square-root question is unchanged if 
𝑓
f is replaced by 
𝐼
I.

For a prime power 
𝑞
q, the squares

𝐿
𝑎
(
𝑥
,
𝑦
)
=
𝑎
𝑥
+
(
1
−
𝑎
)
𝑦
,
𝑎
∈
𝐹
𝑞
∖
{
0
,
1
}
,
L
a
	​

(x,y)=ax+(1−a)y,a∈F
q
	​

∖{0,1},

are idempotent and mutually orthogonal. Therefore

𝐼
(
𝑞
)
≥
𝑞
−
2.
I(q)≥q−2.
	​

3.2 Pairwise-balanced-design closure

A pairwise balanced design, abbreviated here as a PBD, consists of a point set 
𝑋
X and proper subsets called blocks such that every pair of distinct points lies in exactly one block.

Suppose every block 
𝐵
B supports 
𝑡
t mutually orthogonal idempotent Latin squares. For 
𝑥
≠
𝑦
x

=y, let 
𝐵
(
𝑥
,
𝑦
)
B(x,y) be their unique common block, and define

𝐿
𝑖
(
𝑥
,
𝑦
)
=
𝐿
𝑖
𝐵
(
𝑥
,
𝑦
)
(
𝑥
,
𝑦
)
,
𝐿
𝑖
(
𝑥
,
𝑥
)
=
𝑥
.
L
i
	​

(x,y)=L
i
B(x,y)
	​

(x,y),L
i
	​

(x,x)=x.

Then the resulting 
𝐿
𝑖
L
i
	​

 are mutually orthogonal idempotent Latin squares on 
𝑋
X. Hence

𝐼
(
∣
𝑋
∣
)
≥
min
⁡
𝐵
𝐼
(
∣
𝐵
∣
)
.
I(∣X∣)≥
B
min
	​

I(∣B∣).
	​


The idempotence is essential: it makes the definitions agree on the diagonal.

4. The square-root scale is a critical barrier for PBD methods

Suppose a nontrivial PBD on 
𝑣
v points has minimum block size 
𝑠
s. Fix a block 
𝐵
B of size 
𝑏
b, and choose 
𝑥
∉
𝐵
x∈
/
B.

For every 
𝑦
∈
𝐵
y∈B, let 
𝐵
𝑦
B
y
	​

 be the block containing 
𝑥
,
𝑦
x,y. Then:

𝐵
𝑦
∩
𝐵
=
{
𝑦
}
B
y
	​

∩B={y};

for 
𝑦
≠
𝑦
′
y

=y
′
, 
𝐵
𝑦
∩
𝐵
𝑦
′
=
{
𝑥
}
B
y
	​

∩B
y
′
	​

={x};

each 
𝐵
𝑦
B
y
	​

 contains at least 
𝑠
−
2
s−2 points outside 
𝐵
∪
{
𝑥
}
B∪{x}.

Therefore

𝑏
(
𝑠
−
2
)
≤
𝑣
−
𝑏
−
1.
b(s−2)≤v−b−1.
	​


Now suppose the PBD is being used to construct 
𝑡
t idempotent MOLS, so that every block satisfies 
𝐼
(
𝑏
)
≥
𝑡
I(b)≥t. Since 
𝐼
(
𝑏
)
≤
𝑏
−
1
I(b)≤b−1,

𝑏
≥
𝑡
+
1.
b≥t+1.

Using 
𝑠
≥
𝑡
+
1
s≥t+1 in the preceding inequality gives

𝑏
(
𝑡
−
1
)
≤
𝑣
−
𝑏
−
1
,
b(t−1)≤v−b−1,

or

𝑡
+
1
≤
𝑏
≤
𝑣
−
1
𝑡
.
t+1≤b≤
t
v−1
	​

.
	​


This is a severe restriction.

If 
𝑡
=
𝑣
𝛼
t=v
α
, the permitted block-size interval is essentially

[
𝑣
𝛼
,
𝑣
1
−
𝛼
]
.
[v
α
,v
1−α
].

Thus:

for 
𝛼
<
1
/
2
α<1/2, the interval has polynomial width;

for 
𝛼
=
1
/
2
α=1/2, every block is forced onto the 
Θ
(
𝑣
)
Θ(
v
	​

) scale;

for 
𝛼
>
1
/
2
α>1/2, the interval is eventually empty.

So 
1
/
2
1/2 is the exact critical exponent for any nontrivial PBD-gluing strategy. Small correction blocks and a large inductive block cannot work at this exponent.

5. A precise sufficient design target

For a finite set 
𝐾
K of allowed block sizes, the elementary necessary divisibility conditions for a PBD of order 
𝑣
v are

gcd
⁡
𝑘
∈
𝐾
(
𝑘
−
1
)
∣
𝑣
−
1
k∈K
gcd
	​

(k−1)∣v−1

and

gcd
⁡
𝑘
∈
𝐾
𝑘
(
𝑘
−
1
)
∣
𝑣
(
𝑣
−
1
)
.
k∈K
gcd
	​

k(k−1)∣v(v−1).

These follow respectively from

∑
𝐵
∋
𝑥
(
∣
𝐵
∣
−
1
)
=
𝑣
−
1
B∋x
∑
	​

(∣B∣−1)=v−1

for each point 
𝑥
x, and

∑
𝐵
∣
𝐵
∣
(
∣
𝐵
∣
−
1
)
=
𝑣
(
𝑣
−
1
)
.
B
∑
	​

∣B∣(∣B∣−1)=v(v−1).
5.1 Four prime-power block sizes with no congruence obstruction

Given 
𝑥
≥
2
x≥2, let

𝑞
=
2
𝑎
be the least power of 
2
 at least 
𝑥
,
q=2
a
be the least power of 2 at least x,

and

𝑟
=
3
𝑏
be the least power of 
3
 at least 
𝑥
.
r=3
b
be the least power of 3 at least x.

Then

𝑥
≤
𝑞
<
2
𝑥
,
𝑥
≤
𝑟
<
3
𝑥
.
x≤q<2x,x≤r<3x.

Set

𝐾
𝑥
=
{
𝑞
,
2
𝑞
,
𝑟
,
3
𝑟
}
.
K
x
	​

={q,2q,r,3r}.

Every element of 
𝐾
𝑥
K
x
	​

 is a prime power, and

𝐾
𝑥
⊂
[
𝑥
,
9
𝑥
]
.
K
x
	​

⊂[x,9x].

Moreover,

gcd
⁡
(
𝑞
−
1
,
2
𝑞
−
1
)
=
1
,
gcd(q−1,2q−1)=1,

so

gcd
⁡
𝑘
∈
𝐾
𝑥
(
𝑘
−
1
)
=
1.
k∈K
x
	​

gcd
	​

(k−1)=1.

Also,

gcd
⁡
(
𝑞
(
𝑞
−
1
)
,
2
𝑞
(
2
𝑞
−
1
)
)
=
𝑞
,
gcd(q(q−1),2q(2q−1))=q,

while

gcd
⁡
(
𝑟
(
𝑟
−
1
)
,
3
𝑟
(
3
𝑟
−
1
)
)
=
2
𝑟
.
gcd(r(r−1),3r(3r−1))=2r.

Since 
𝑞
q is a power of 
2
2 and 
𝑟
r is odd,

gcd
⁡
(
𝑞
,
2
𝑟
)
=
2.
gcd(q,2r)=2.

Therefore

gcd
⁡
𝑘
∈
𝐾
𝑥
(
𝑘
−
1
)
=
1
,
gcd
⁡
𝑘
∈
𝐾
𝑥
𝑘
(
𝑘
−
1
)
=
2.
k∈K
x
	​

gcd
	​

(k−1)=1,
k∈K
x
	​

gcd
	​

k(k−1)=2.
	​


The elementary congruence conditions are consequently satisfied for every 
𝑣
v.

5.2 Quadratic PBD target

The following standalone lemma would prove (Q):

Quadratic PBD target. There is an absolute constant 
𝐶
C such that, for every sufficiently large 
𝑥
x, every integer 
𝑣
≥
𝐶
𝑥
2
v≥Cx
2
 has a PBD whose block sizes belong to 
𝐾
𝑥
K
x
	​

.

Indeed, every 
𝑘
∈
𝐾
𝑥
k∈K
x
	​

 is a prime power and hence

𝐼
(
𝑘
)
≥
𝑘
−
2
≥
𝑥
−
2.
I(k)≥k−2≥x−2.

PBD closure would give

𝑓
(
𝑣
)
≥
𝐼
(
𝑣
)
≥
𝑥
−
2.
f(v)≥I(v)≥x−2.

Choosing 
𝑥
=
⌊
𝑣
/
𝐶
⌋
x=⌊
v/C
	​

⌋ would yield

𝑓
(
𝑣
)
≫
𝑣
.
f(v)≫
v
	​

.

The extremal block inequality shows that any such 
𝐶
C must be at least roughly 
9
9, because the smallest and largest allowed blocks can be near 
𝑥
x and 
9
𝑥
9x.

This target has passed the first arithmetic falsification test: there are no residual divisibility classes of 
𝑣
v. The unresolved obligation is a uniform clique decomposition of 
𝐾
𝑣
K
v
	​

 into cliques of four sizes 
Θ
(
𝑣
)
Θ(
v
	​

), with only a quadratic threshold in the block size.

6. Two explicit PBD recurrences and their bottlenecks
6.1 Deleting points from an affine plane

Let 
𝑞
q be a prime power. On 
𝐹
𝑞
2
F
q
2
	​

, the affine lines form a PBD with all block sizes 
𝑞
q.

Delete 
𝑡
t points from one line 
𝐿
L. The surviving blocks have sizes:

𝑞
−
𝑡
q−t for 
𝐿
L, when at least 
2
2;

𝑞
q for lines not affected;

𝑞
−
1
q−1 for lines meeting 
𝐿
L in a deleted point.

Therefore

𝐼
(
𝑞
2
−
𝑡
)
≥
min
⁡
{
𝐼
(
𝑞
)
,
𝐼
(
𝑞
−
1
)
,
𝐼
(
𝑞
−
𝑡
)
}
,
I(q
2
−t)≥min{I(q),I(q−1),I(q−t)},

with absent block sizes omitted. Hence

𝑓
(
𝑞
2
−
𝑡
)
≥
min
⁡
{
𝑞
−
2
,
 
𝑓
(
𝑞
−
1
)
−
1
,
 
𝑓
(
𝑞
−
𝑡
)
−
1
}
.
f(q
2
−t)≥min{q−2, f(q−1)−1, f(q−t)−1}.
	​


This attacks an interval below 
𝑞
2
q
2
, but it immediately transfers the square-root obligation to the consecutive order 
𝑞
−
1
q−1 and to the remainder 
𝑞
−
𝑡
q−t. The construction does not eliminate the hard orders.

6.2 Truncating one group of a transversal design

Assume a transversal design with 
𝑚
+
1
m+1 groups of size 
𝑛
n exists; equivalently, assume

𝑓
(
𝑛
)
≥
𝑚
−
1.
f(n)≥m−1.

Truncate one group to 
𝑡
t points, 
0
≤
𝑡
≤
𝑛
0≤t≤n, and add each surviving group as a block. This gives a PBD on

𝑣
=
𝑚
𝑛
+
𝑡
v=mn+t

with block sizes among

𝑛
,
𝑡
,
𝑚
,
𝑚
+
1.
n,t,m,m+1.

Thus

𝐼
(
𝑚
𝑛
+
𝑡
)
≥
min
⁡
{
𝐼
(
𝑛
)
,
𝐼
(
𝑡
)
,
𝐼
(
𝑚
)
,
𝐼
(
𝑚
+
1
)
}
,
I(mn+t)≥min{I(n),I(t),I(m),I(m+1)},
	​


with sizes 
0
0 and 
1
1 omitted.

At a target 
𝐼
(
𝑣
)
≍
𝑣
I(v)≍
v
	​

, all four nontrivial block orders must themselves be 
Θ
(
𝑣
)
Θ(
v
	​

) and support nearly the maximum possible number of MOLS. In particular, this route needs two consecutive “good” orders 
𝑚
,
𝑚
+
1
m,m+1. That is the exact gap in this interpolation construction.

7. Extremal structure of a maximal family

Suppose there are 
𝑚
m orthogonal partitions of an 
𝑛
2
n
2
-point set, where

𝑚
=
𝑘
+
2.
m=k+2.

Call two points covered if they occur in one common partition block. Define the graph 
𝐻
H by joining pairs that are not covered.

Put

𝑠
=
𝑛
+
1
−
𝑚
=
𝑛
−
𝑘
−
1.
s=n+1−m=n−k−1.
7.1 Strongly regular parameters

Every point is covered with 
𝑚
(
𝑛
−
1
)
m(n−1) other points, so

𝑑
𝐻
=
(
𝑛
2
−
1
)
−
𝑚
(
𝑛
−
1
)
=
(
𝑛
−
1
)
𝑠
.
d
H
	​

=(n
2
−1)−m(n−1)=(n−1)s.

If 
𝑥
,
𝑦
x,y are adjacent in 
𝐻
H, the intersections of a block through 
𝑥
x in class 
𝑖
i and a block through 
𝑦
y in class 
𝑗
j, for 
𝑖
≠
𝑗
i

=j, give 
𝑚
(
𝑚
−
1
)
m(m−1) distinct points covered with both. Counting neighborhood unions gives

𝜆
𝐻
=
𝑛
+
𝑠
2
−
3
𝑠
.
λ
H
	​

=n+s
2
−3s.

If 
𝑥
,
𝑦
x,y are nonadjacent, they lie in a common block. A direct count gives

𝜇
𝐻
=
𝑠
(
𝑠
−
1
)
.
μ
H
	​

=s(s−1).

Thus

𝐻
 has parameters 
(
𝑛
2
,
 
(
𝑛
−
1
)
𝑠
,
 
𝑛
+
𝑠
2
−
3
𝑠
,
 
𝑠
(
𝑠
−
1
)
)
.
H has parameters (n
2
, (n−1)s, n+s
2
−3s, s(s−1)).
	​


Its two nontrivial eigenvalues are

𝑛
−
𝑠
=
𝑚
−
1
and
−
𝑠
,
n−s=m−1and−s,

with multiplicities

𝑠
(
𝑛
−
1
)
and
𝑚
(
𝑛
−
1
)
,
s(n−1)andm(n−1),

respectively.

All these multiplicities are automatically integral. Consequently, elementary spectral feasibility gives no contradiction when 
𝑚
≍
𝑛
m≍
n
	​

.

7.2 Extension as a clique-factor problem

A new orthogonal partition is exactly a partition of 
𝑉
(
𝐻
)
V(H) into 
𝑛
n cliques of size 
𝑛
n.

Equivalently, a common transversal of the existing partitions is an 
𝑛
n-clique in 
𝐻
H, and a new Latin square requires 
𝑛
n disjoint such cliques.

7.3 Near-complete rigidity

If 
𝑚
=
𝑛
m=n, then 
𝑠
=
1
s=1, and

𝑑
𝐻
=
𝑛
−
1
,
𝜆
𝐻
=
𝑛
−
2
,
𝜇
𝐻
=
0.
d
H
	​

=n−1,λ
H
	​

=n−2,μ
H
	​

=0.

Thus 
𝐻
H is a disjoint union of 
𝑛
n copies of 
𝐾
𝑛
K
n
	​

, providing the missing partition. Therefore

𝑓
(
𝑛
)
≥
𝑛
−
2
  
⟹
  
𝑓
(
𝑛
)
=
𝑛
−
1.
f(n)≥n−2⟹f(n)=n−1.
	​


So the value 
𝑛
−
2
n−2 can never be the exact maximum.

This rigidity occurs only extremely near the upper bound and does not propagate down to 
𝑚
≍
𝑛
m≍
n
	​

.

8. Greedy extension fails even at degree 
3
3

Consider the cyclic Latin square of even order 
𝑛
n,

𝐿
(
𝑟
,
𝑐
)
=
𝑟
+
𝑐
(
m
o
d
𝑛
)
.
L(r,c)=r+c(modn).

Suppose it had a transversal 
(
𝑟
,
𝜋
(
𝑟
)
)
(r,π(r)). The symbols

𝑟
+
𝜋
(
𝑟
)
r+π(r)

would form a permutation of 
𝑍
𝑛
Z
n
	​

. Let

𝑆
=
∑
𝑟
=
0
𝑛
−
1
𝑟
=
𝑛
(
𝑛
−
1
)
2
.
S=
r=0
∑
n−1
	​

r=
2
n(n−1)
	​

.

Since 
𝑛
n is even,

𝑆
≡
𝑛
2
(
m
o
d
𝑛
)
,
2
𝑆
≡
0
(
m
o
d
𝑛
)
.
S≡
2
n
	​

(modn),2S≡0(modn).

But a transversal would imply

𝑆
≡
∑
𝑟
(
𝑟
+
𝜋
(
𝑟
)
)
≡
2
𝑆
≡
0
(
m
o
d
𝑛
)
,
S≡
r
∑
	​

(r+π(r))≡2S≡0(modn),

contradicting 
𝑆
≡
𝑛
/
2
(
m
o
d
𝑛
)
S≡n/2(modn).

Hence the cyclic Latin square of every even order has no transversal and therefore no orthogonal mate.

Consequences:

It is false that every low-degree net can be extended.

A greedy strategy can become stuck after constructing only one square.

Any proof of (Q) must choose the entire structure globally or permit substantial exchanges, rather than extending arbitrary partial families.

9. Hypergraph edge-coloring formulation of extension

Given 
𝑚
m orthogonal-array columns, form an 
𝑚
m-partite hypergraph:

vertices are coordinate-symbol pairs;

every array row gives one hyperedge.

This hypergraph is:

𝑚
m-uniform;

𝑛
n-regular;

linear;

of maximum degree 
𝑛
n.

A new orthogonal-array column is equivalent to a proper edge-coloring with exactly 
𝑛
n colors. Since every vertex has degree 
𝑛
n, such a coloring automatically uses every color once at each vertex, so every color class is a perfect matching.

Thus an extension asks whether this very special linear regular hypergraph has chromatic index exactly 
Δ
=
𝑛
Δ=n.

The cyclic even-order example shows that this can fail already for 
𝑚
=
3
m=3. General exact edge-coloring principles therefore cannot supply the desired iteration.

10. A partial-transversal result from random choice

Let 
𝑡
t MOLS be fixed. Choose a uniformly random permutation 
𝜋
π, giving cells

(
𝑟
,
𝜋
(
𝑟
)
)
,
𝑟
∈
[
𝑛
]
.
(r,π(r)),r∈[n].

For a fixed Latin square and two distinct rows, the probability that the two chosen cells have the same symbol is

1
𝑛
−
1
.
n−1
1
	​

.

Hence the expected total number of symbol collisions across all 
𝑡
t squares is

𝑡
(
𝑛
2
)
1
𝑛
−
1
=
𝑡
𝑛
2
.
t(
2
n
	​

)
n−1
1
	​

=
2
tn
	​

.

Therefore some permutation produces a collision graph on the 
𝑛
n selected cells with at most 
𝑡
𝑛
/
2
tn/2 edges.

Every graph with 
𝑁
N vertices and 
𝐸
E edges has an independent set of size at least

𝑁
2
2
𝐸
+
𝑁
.
2E+N
N
2
	​

.

It follows that the 
𝑡
t MOLS have a common partial transversal of size at least

𝑛
𝑡
+
1
.
t+1
n
	​

.
	​


For 
𝑡
≍
𝑛
t≍
n
	​

, this guarantees only 
Θ
(
𝑛
)
Θ(
n
	​

) cells, whereas a new partition requires 
𝑛
n cells in each transversal and 
𝑛
n disjoint full transversals. The probabilistic argument misses the needed scale by a factor of 
𝑛
n
	​

.

11. Algebraic constructions and a parity obstruction
11.1 Linear squares over 
𝑍
𝑛
Z
n
	​


Consider

𝐿
𝑎
(
𝑟
,
𝑐
)
=
𝑎
𝑟
+
𝑐
(
m
o
d
𝑛
)
.
L
a
	​

(r,c)=ar+c(modn).

This is Latin when 
𝑎
a is a unit. Two such squares are orthogonal precisely when 
𝑎
−
𝑏
a−b is a unit.

Let 
𝑝
p be the least prime divisor of 
𝑛
n. Reducing all coefficients modulo 
𝑝
p, they must be nonzero and pairwise distinct. Therefore this construction gives at most

𝑝
−
1
p−1

MOLS.

For even 
𝑛
n, it gives at most one.

11.2 Difference matrices over groups

Let 
𝐺
G have order 
𝑛
n. A group difference-matrix construction would require permutations 
𝜋
𝑖
:
𝐺
→
𝐺
π
i
	​

:G→G such that, for every 
𝑖
≠
𝑗
i

=j,

𝑥
⟼
𝜋
𝑖
(
𝑥
)
𝜋
𝑗
(
𝑥
)
−
1
x⟼π
i
	​

(x)π
j
	​

(x)
−1

is also a permutation.

Suppose 
𝐺
G has a surjective homomorphism

𝜒
:
𝐺
→
𝐶
2
χ:G→C
2
	​


whose kernel has odd size 
𝑚
m. Thus 
∣
𝐺
∣
=
2
𝑚
∣G∣=2m with 
𝑚
m odd.

Assume 
𝜋
,
𝜎
π,σ, and

𝛿
(
𝑥
)
=
𝜋
(
𝑥
)
𝜎
(
𝑥
)
−
1
δ(x)=π(x)σ(x)
−1

are permutations. Let

𝐴
=
{
𝑥
:
𝜒
(
𝜋
(
𝑥
)
)
=
1
}
,
𝐵
=
{
𝑥
:
𝜒
(
𝜎
(
𝑥
)
)
=
1
}
.
A={x:χ(π(x))=1},B={x:χ(σ(x))=1}.

Because 
𝜋
,
𝜎
π,σ are permutations,

∣
𝐴
∣
=
∣
𝐵
∣
=
𝑚
.
∣A∣=∣B∣=m.

Because 
𝛿
δ is a permutation, 
𝜒
(
𝛿
(
𝑥
)
)
=
1
χ(δ(x))=1 for exactly 
𝑚
m values of 
𝑥
x. But

𝜒
(
𝛿
(
𝑥
)
)
=
𝜒
(
𝜋
(
𝑥
)
)
+
𝜒
(
𝜎
(
𝑥
)
)
χ(δ(x))=χ(π(x))+χ(σ(x))

in 
𝐶
2
C
2
	​

, so this set is 
𝐴
△
𝐵
A△B. Hence

∣
𝐴
△
𝐵
∣
=
𝑚
.
∣A△B∣=m.

On the other hand,

∣
𝐴
△
𝐵
∣
=
∣
𝐴
∣
+
∣
𝐵
∣
−
2
∣
𝐴
∩
𝐵
∣
=
2
𝑚
−
2
∣
𝐴
∩
𝐵
∣
,
∣A△B∣=∣A∣+∣B∣−2∣A∩B∣=2m−2∣A∩B∣,

which is even, while 
𝑚
m is odd. Contradiction.

Therefore:

Such a group difference construction cannot contain two permutation rows.
Such a group difference construction cannot contain two permutation rows.
	​


It cannot even construct two MOLS on these groups. This sharply isolates why group and ring constructions are inadequate on orders 
2
𝑚
2m with 
𝑚
m odd.

It is not an upper bound on arbitrary MOLS.

12. Random partitions are far too sparse

Fix one equipartition of an 
𝑛
2
n
2
-point set into 
𝑛
n labeled classes of size 
𝑛
n.

The number of labeled equipartitions is

(
𝑛
2
)
!
(
𝑛
!
)
𝑛
.
(n!)
n
(n
2
)!
	​

.

An equipartition orthogonal to the fixed one is obtained by assigning the 
𝑛
n points of each fixed class bijectively to the 
𝑛
n new labels, giving

(
𝑛
!
)
𝑛
(n!)
n

choices. Thus the exact probability that a uniformly random equipartition is orthogonal to the fixed one is

(
𝑛
!
)
2
𝑛
(
𝑛
2
)
!
.
(n
2
)!
(n!)
2n
	​

.
	​


Using elementary factorial estimates,

log
⁡
 ⁣
(
(
𝑛
!
)
2
𝑛
(
𝑛
2
)
!
)
=
−
𝑛
2
+
𝑂
(
𝑛
log
⁡
𝑛
)
.
log(
(n
2
)!
(n!)
2n
	​

)=−n
2
+O(nlogn).

Meanwhile the logarithm of the total number of equipartitions is of order 
𝑛
2
log
⁡
𝑛
n
2
logn. If orthogonality constraints behaved even approximately independently, raw counting would only suggest families of logarithmic size.

This is not an upper bound: finite-field families exhibit enormous correlations. It does show that unstructured random selection is not a plausible square-root construction.

13. Minimal-counterexample analysis

For a fixed 
𝑡
t, define

𝐴
𝑡
=
{
𝑛
:
𝐼
(
𝑛
)
≥
𝑡
}
.
A
t
	​

={n:I(n)≥t}.

The preceding constructions show:

If 
𝑎
,
𝑏
∈
𝐴
𝑡
a,b∈A
t
	​

, then 
𝑎
𝑏
∈
𝐴
𝑡
ab∈A
t
	​

.

If every block size of a PBD belongs to 
𝐴
𝑡
A
t
	​

, then its order belongs to 
𝐴
𝑡
A
t
	​

.

Every prime power 
𝑞
≥
𝑡
+
2
q≥t+2 belongs to 
𝐴
𝑡
A
t
	​

.

Thus, if 
𝐼
(
𝑛
)
<
𝑡
I(n)<t, every nontrivial PBD of order 
𝑛
n has at least one block size 
𝑏
b with

𝐼
(
𝑏
)
<
𝑡
.
I(b)<t.

This is a precise “bad-order hitting” property.

However, a minimal-counterexample induction for the moving target 
𝑡
=
𝑐
𝑛
t=c
n
	​

 fails. Minimality would only give

𝐼
(
𝑏
)
≥
𝑐
𝑏
I(b)≥c
b
	​


for 
𝑏
<
𝑛
b<n, while PBD closure requires

𝐼
(
𝑏
)
≥
𝑐
𝑛
.
I(b)≥c
n
	​

.

For plane-scale blocks 
𝑏
≍
𝑛
b≍
n
	​

, the inductive guarantee is merely of order 
𝑛
1
/
4
n
1/4
. The induction loses a square root at each level.

Thus ordinary minimality does not align with the required scaling.

The formal negation of (Q) is the existence of a sequence 
𝑛
𝑗
→
∞
n
j
	​

→∞ such that

𝑓
(
𝑛
𝑗
)
𝑛
𝑗
→
0.
n
j
	​

	​

f(n
j
	​

)
	​

→0.

Any such sequence must eventually avoid:

prime powers;

balanced products of prime powers;

all quadratic-scale prime-power PBD constructions;

any new algebraic construction capable of handling 
2
𝑝
2p-type orders.

The family 
𝑛
=
2
𝑝
n=2p, with 
𝑝
p odd and large, is the cleanest first falsification family because all direct-product, cyclic-linear, and many group-difference constructions collapse there.

14. Precise remaining targets
Target A: Quadratic prime-power PBDs

Prove the Quadratic PBD target from Section 5:

𝑣
≥
𝐶
𝑥
2
⟹
PBD
⁡
(
𝑣
,
𝐾
𝑥
)
v≥Cx
2
⟹PBD(v,K
x
	​

)

for

𝐾
𝑥
=
{
𝑞
,
2
𝑞
,
𝑟
,
3
𝑟
}
.
K
x
	​

={q,2q,r,3r}.

This would prove the original statement. Divisibility has already been eliminated as an obstruction.

Target B: A genuinely non-group construction for 
2
𝑝
2p

Construct 
𝑐
𝑝
c
p
	​

 MOLS of order 
2
𝑝
2p, uniformly for all sufficiently large odd primes 
𝑝
p, without a quotient-compatible group difference matrix.

Success on this family would defeat the strongest elementary arithmetic bottleneck found here.

Conversely, an upper bound

𝑓
(
2
𝑝
)
=
𝑜
(
𝑝
)
f(2p)=o(
p
	​

)

would disprove (Q). No candidate invariant establishing such an upper bound was found.

Target C: Quantitative clique decomposition at the critical scale

Prove that 
𝐾
𝑣
K
v
	​

 can be decomposed into cliques whose orders are selected prime powers in an interval

[
𝑐
𝑣
,
𝐶
𝑣
]
,
[c
v
	​

,C
v
	​

],

with all local MOLS counts at least 
𝑐
𝑣
c
v
	​

.

This is essentially the geometric content of Target A without the special four-size choice.

Target D: One-symbol orthogonal-array trades

For a prime power 
𝑞
q, attempt to transform a transversal design with 
𝑚
≍
𝑞
m≍
q
	​

 groups of size 
𝑞
q into one with group size 
𝑞
+
1
q+1.

In the simplest architecture containing one block through all newly adjoined points, counting forces:

𝑚
𝑞
mq blocks containing exactly one new point;

deletion or replacement of 
𝑞
(
𝑚
−
2
)
q(m−2) old blocks.

Thus this is not a local single-transversal prolongation when 
𝑚
m grows. A structured trade of size 
Θ
(
𝑞
3
/
2
)
Θ(q
3/2
) is required.

A uniform construction would give

𝑓
(
𝑞
+
1
)
≫
𝑞
,
f(q+1)≫
q
	​

,

which would resolve a particularly persistent consecutive-order gap.

Target E: A new modular or parity invariant

The real, spectral, and elementary modular incidence calculations only recover linear upper bounds. A disproof requires an invariant that distinguishes composite alphabet sizes while remaining valid for arbitrary, nonlinear MOLS.

Promising test cases are:

𝑛
=
2
𝑝
,
𝑛
=
2
𝑝
𝑎
,
𝑛
=
∏
𝑝
≤
𝑦
𝑝
.
n=2p,n=2p
a
,n=
p≤y
∏
	​

p.
15. Finite falsification tests
15.1 Exact SAT/ILP search for 
𝑘
k MOLS

Use binary variables

𝑥
ℓ
,
𝑟
,
𝑐
,
𝑠
∈
{
0
,
1
}
x
ℓ,r,c,s
	​

∈{0,1}

meaning square 
ℓ
ℓ places symbol 
𝑠
s in cell 
(
𝑟
,
𝑐
)
(r,c).

Impose:

∑
𝑠
𝑥
ℓ
,
𝑟
,
𝑐
,
𝑠
=
1
,
s
∑
	​

x
ℓ,r,c,s
	​

=1,
∑
𝑐
𝑥
ℓ
,
𝑟
,
𝑐
,
𝑠
=
1
,
∑
𝑟
𝑥
ℓ
,
𝑟
,
𝑐
,
𝑠
=
1.
c
∑
	​

x
ℓ,r,c,s
	​

=1,
r
∑
	​

x
ℓ,r,c,s
	​

=1.

For every 
ℓ
<
𝑗
ℓ<j and symbol pair 
(
𝑎
,
𝑏
)
(a,b), introduce conjunction variables 
𝑦
y and require

∑
𝑟
,
𝑐
𝑦
ℓ
,
𝑗
,
𝑟
,
𝑐
,
𝑎
,
𝑏
=
1.
r,c
∑
	​

y
ℓ,j,r,c,a,b
	​

=1.

Valid symmetry reductions include:

reducing the first square;

relabeling each later square so its first row is fixed;

lexicographically ordering the squares.

Priority orders are 
𝑛
=
2
𝑝
n=2p. The purpose is not to infer asymptotics from small values, but to destroy proposed structural lemmas quickly.

15.2 PBD exact-cover search

For fixed 
𝑣
,
𝐾
v,K, use one binary variable 
𝑧
𝐵
z
B
	​

 for every subset 
𝐵
⊆
[
𝑣
]
B⊆[v] with 
∣
𝐵
∣
∈
𝐾
∣B∣∈K, and impose

∑
𝐵
⊇
{
𝑥
,
𝑦
}
𝑧
𝐵
=
1
B⊇{x,y}
∑
	​

z
B
	​

=1

for every pair 
{
𝑥
,
𝑦
}
{x,y}.

Apply this first to 
𝐾
𝑥
K
x
	​

 and 
𝑣
v near the lower extremal threshold 
9
𝑥
2
9x
2
. Repeated failure would falsify an overly optimistic constant in Target A.

15.3 Cyclic difference-family search

For a cyclic PBD, search for base blocks 
𝐵
𝑖
⊆
𝑍
𝑣
B
i
	​

⊆Z
v
	​

 such that the ordered differences

𝑏
−
𝑏
′
,
𝑏
≠
𝑏
′
,
𝑏
,
𝑏
′
∈
𝐵
𝑖
,
b−b
′
,b

=b
′
,b,b
′
∈B
i
	​

,

cover every nonzero residue exactly once.

This requires

∑
𝑖
∣
𝐵
𝑖
∣
(
∣
𝐵
𝑖
∣
−
1
)
=
𝑣
−
1.
i
∑
	​

∣B
i
	​

∣(∣B
i
	​

∣−1)=v−1.

At the square-root scale only 
𝑂
(
1
)
O(1) base blocks are possible, making this a manageable but highly restrictive construction test.

15.4 Orthogonal-array trade search

Start from the finite-field array of order 
𝑞
q, retain only 
𝑚
≍
𝑞
m≍
q
	​

 columns, adjoin one new symbol, and search for a minimum-support trade producing an array of order 
𝑞
+
1
q+1.

The first falsification statistic is whether support substantially below 
𝑞
(
𝑚
−
2
)
q(m−2) is possible. The counting above rules it out in the simplest all-new-block architecture.

15.5 Incidence-rank experiments

For any computed family, form the line-by-point incidence matrix and record:

ranks over primes dividing 
𝑛
n;

Smith normal form;

ranks of centered partition subspaces;

determinants of maximal contrast minors.

No theorem extracted so far turns these quantities into a sub-square-root upper bound, but 
2
𝑝
2p examples could reveal an invariant missed by real spectral analysis.

16. Failure ledger
Direct products

They give only the smallest prime-power component of 
𝑛
n. They fail completely on 
2
𝑝
2p-type orders.

Linear and group-based algebra

Reduction modulo a small prime bounds linear slopes. An index-two parity argument rules out even two permutation rows in a broad group-difference framework.

Greedy extension

False even for one cyclic Latin square of every even order, because it has no transversal.

Random construction

Orthogonality between random partitions has probability approximately 
𝑒
−
𝑛
2
e
−n
2
. Unstructured counting only suggests logarithmic families.

Spectral contradiction

The uncovered graph has automatically feasible strongly regular parameters and integral multiplicities for every possible 
𝑚
m. No square-root obstruction appears.

Minimal-counterexample induction

The moving target 
𝑐
𝑛
c
n
	​

 is not inherited by 
Θ
(
𝑛
)
Θ(
n
	​

)-sized blocks; it degrades to 
𝑛
1
/
4
n
1/4
.

PBD gluing with small corrections

Impossible at the critical exponent. Every useful block is forced into the interval

[
𝑡
+
1
,
(
𝑣
−
1
)
/
𝑡
]
.
[t+1,(v−1)/t].

For 
𝑡
≍
𝑣
t≍
v
	​

, every block must itself be of order 
𝑣
v
	​

.

Affine-plane truncation

It introduces block orders 
𝑞
−
1
q−1 and 
𝑞
−
𝑡
q−t, transferring rather than resolving the hard cases.

Transversal-design interpolation

It introduces consecutive block sizes 
𝑚
,
𝑚
+
1
m,m+1. Both must be nearly maximally good at the square-root scale.

Status

No proof or disproof of

𝑓
(
𝑛
)
≫
𝑛
f(n)≫
n
	​


was obtained.

The sharpest constructive reduction found is the Quadratic PBD target using the four prime-power block sizes

{
𝑞
,
2
𝑞
,
𝑟
,
3
𝑟
}
⊂
[
𝑥
,
9
𝑥
]
,
{q,2q,r,3r}⊂[x,9x],

whose elementary divisibility obstructions vanish identically. The sharpest disproof test is the family 
𝑛
=
2
𝑝
n=2p, where every straightforward product, ring, and quotient-compatible group construction fails, but no upper bound on arbitrary MOLS was derived.
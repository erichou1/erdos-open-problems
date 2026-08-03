1. Blocking defects in the immutable statement

The literal wording does not specify the nondegeneracy conditions needed for either question.

For the first question, it does not explicitly require x
1
	​

,…,x
k
	​

 to be distinct or d>0. Thus the constant sequence x
i
	​

=1, with d=0, satisfies the displayed inequalities for every k and every C>0.

For the second question, “arbitrarily large cubes” does not specify whether “large” means dimension or cardinality, whether the b
i
	​

 must be positive or nonzero, or whether all 2
r
 subset sums must be distinct. Allowing b
i
	​

=0 gives cubes of arbitrarily large nominal dimension without enlarging the underlying set.

Consequently, the exact immutable statement does not determine a unique nondegenerate proposition. The analysis below uses the conventional working interpretation:

x
i
	​

=n
i
2
	​

,0<n
1
	​

<⋯<n
k
	​

,d>0,

and an r-dimensional proper square cube

H(a;b
1
	​

,…,b
r
	​

)=a+{
i=1
∑
r
	​

ϵ
i
	​

b
i
	​

:ϵ
i
	​

∈{0,1}},

with b
i
	​

>0, all 2
r
 subset sums distinct, and every element a square. This working interpretation is not a repair of the immutable statement.

2. Exact normalization of the quasi-progression problem

Put

Δ
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

The existence of some real d satisfying

d≤Δ
i
	​

≤d+C

for every i is equivalent to

i
max
	​

Δ
i
	​

−
i
min
	​

Δ
i
	​

≤C.

Since the Δ
i
	​

 are integers, only

W=⌊C⌋

matters. Thus define the extremal quantity

R
k
	​

=
0<n
1
	​

<⋯<n
k
	​

min
	​

[
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

)].

Then R
k
	​

 is a nondecreasing sequence of nonnegative integers, and the intended first question is exactly

k
sup
	​

R
k
	​

<∞?

Some exact or constructive values are:

R
2
	​

=0,R
3
	​

=0,R
4
	​

=1.

Indeed,

1,25,49

is a three-term progression of squares, while the supplied fact excluding four-term progressions gives R
4
	​

≥1, and

49,225,400,576

has gaps

176,175,176.

Further constructions give

R
5
	​

≤4,R
6
	​

≤6,R
7
	​

≤7,R
9
	​

≤10.

For example:

W
1
2
4
6
10
	​

roots n
i
	​

(7,15,20,24)
(1,3,4,5)
(1,3,4,5,6)
(1,3,4,5,6,7)
(1,4,6,7,8,9,10,11,12)
	​

square-gap range
[175,176]
[7,9]
[7,11]
[7,13]
[13,23].
	​

	​


These are constructions only, not global optimality assertions beyond R
4
	​

.

3. Error words and additive cubes

Let

D=
i
min
	​

Δ
i
	​

,Δ
i
	​

=D+e
i
	​

,e
i
	​

∈{0,1,…,W}.

Suppose that the word e
1
	​

e
2
	​

⋯e
k−1
	​

 contains three consecutive blocks of equal length r and equal sum:

t=j
∑
j+r−1
	​

e
t
	​

=
t=j+r
∑
j+2r−1
	​

e
t
	​

=
t=j+2r
∑
j+3r−1
	​

e
t
	​

.

Then

x
j+r
	​

−x
j
	​

=x
j+2r
	​

−x
j+r
	​

=x
j+3r
	​

−x
j+2r
	​

,

because each difference equals rD plus the corresponding error-block sum. Hence

x
j
	​

,x
j+r
	​

,x
j+2r
	​

,x
j+3r
	​


would be a four-term arithmetic progression of squares.

Therefore:

Every error word arising from a square quasi-progression must avoid three consecutive equal-length blocks having equal sums.

Call such a forbidden configuration an additive cube.

Binary error alphabet

For W=1, an exhaustive extension recursion gives the number of additive-cube-free binary words of lengths 0,1,…,10:

1,2,4,6,10,16,18,12,10,6,0.

The six maximal words of length 9 are

	​

001101100,001101101,010010011,
101101100,110010010,110010011.
	​


No one-symbol extension of any of them remains additive-cube-free. The recursion is exhaustive because, when a letter is appended, only additive cubes ending at the new final position need to be checked.

Consequently, under the intended interpretation,

W≤1⟹k≤10.

Thus any constant capable of supporting arbitrary lengths would have to satisfy

⌊C⌋≥2.
Failure of the error-word obstruction

The same exact backtracking reaches length 1000 over the alphabet {0,1,2} without encountering an additive cube. This does not establish an infinite ternary word, but it decisively blocks any argument claiming that a short purely word-combinatorial bound handles every fixed W.

Moreover, additive-cube avoidance is only necessary. Most such words do not satisfy the additional factorization conditions required for realization by consecutive squares.

4. Thin-hyperbola reformulation

Define

h
i
	​

=n
i+1
	​

−n
i
	​

,p
i
	​

=n
i
	​

+n
i+1
	​

.

Then

Δ
i
	​

=p
i
	​

h
i
	​

,

and the consecutive pairs satisfy the exact adjacency law

p
i+1
	​

=p
i
	​

+h
i
	​

+h
i+1
	​

.

There are also the arithmetic restrictions

p
i
	​

>h
i
	​

>0,p
i
	​

≡h
i
	​

(mod2).

Thus the first problem becomes:

Can there be arbitrarily long chains of lattice points (p
i
	​

,h
i
	​

) lying in a strip

D≤p
i
	​

h
i
	​

≤D+W

around a hyperbola, with

p
i+1
	​

−p
i
	​

=h
i
	​

+h
i+1
	​

?

Equivalently, each h
i
	​

 is a divisor of one of the W+1 consecutive integers

D,D+1,…,D+W,

and the corresponding complementary divisors must obey the adjacency equation.

4.1 Large root gaps must decrease

We have

Δ
i+1
	​

−Δ
i
	​

	​

=p
i+1
	​

h
i+1
	​

−p
i
	​

h
i
	​

=p
i
	​

(h
i+1
	​

−h
i
	​

)+(h
i
	​

+h
i+1
	​

)h
i+1
	​

.
	​


If h
i+1
	​

≥h
i
	​

, then

Δ
i+1
	​

−Δ
i
	​

≥2h
i
2
	​

.

But ∣Δ
i+1
	​

−Δ
i
	​

∣≤W. Hence

h
i+1
	​

≥h
i
	​

⟹h
i
	​

≤
W/2
	​

.

Therefore, throughout the phase where

h
i
	​

>
W/2
	​

,

the sequence h
i
	​

 must strictly decrease.

This is a genuine monovariant, but it does not by itself give a uniform length bound because h
1
	​

 is unrestricted.

4.2 Rigidity of a decreasing step

Suppose

h
i
	​

=v,h
i+1
	​

=w<v,s=v−w.

Then

Δ
i+1
	​

−Δ
i
	​

=−p
i
	​

s+w(v+w),

so

∣p
i
	​

(v−w)−w(v+w)∣≤W.
	​


Thus p
i
	​

 must lie in an interval of width 2W/(v−w) around

v−w
w(v+w)
	​

.

For v−w>2W, there is at most one possible integer p
i
	​

.

Writing

Δ
i
	​

=D+e
i
	​

,0≤e
i
	​

≤W,

and eliminating p
i
	​

 gives the stronger exact equation

D(h
i
	​

−h
i+1
	​

)=h
i
	​

h
i+1
	​

(h
i
	​

+h
i+1
	​

)+e
i
	​

h
i+1
	​

−e
i+1
	​

h
i
	​

.
	​


Define the cubic quotient

Q(v,w)=
v−w
vw(v+w)
	​

,v>w.

Every decreasing adjacent pair must satisfy

∣D−Q(h
i
	​

,h
i+1
	​

)∣≤W
h
i
	​

−h
i+1
	​

h
i
	​

+h
i+1
	​

	​

.
	​


Hence all successive gap pairs must give approximately the same value of the nonlinear expression Q, with explicitly controlled error.

Remaining gap

The strict decrease of the h
i
	​

 is insufficient. In the continuous relaxation, when v and w are close,

D(v−w)≈2v
3
,

so the expected decrement is

v−w≈
D
2v
3
	​

.

The resulting differential model permits about D
1/3
 steps before reaching the small-gap regime. This is only a heuristic, but it explains why monotonicity alone cannot provide a bound independent of D. A proof must exploit exact divisibility, parity, or incompatibility between consecutive cubic quotients.

5. Exact finite-search formulation for the first problem

For fixed W and a root cutoff N, form a directed acyclic graph with vertices 1,…,N. There is an edge

n⟶m,n<m,

labeled by

m
2
−n
2
.

A quasi-progression is exactly a directed path whose edge-label diameter is at most W.

An exhaustive search needs only the state

(current root, minimum label, maximum label).

A candidate next root m is admitted precisely when

max(M,m
2
−n
2
)−min(L,m
2
−n
2
)≤W.

This search is exact under the chosen root cutoff. The unresolved issue is a theorem giving a root cutoff depending only on W and the desired path length. Without such a cutoff, finite nonexistence does not become a global result.

6. Why quasi-progressions imply Hilbert cubes

The implication mentioned in the statement can be established directly by a finite-word induction.

Let A be a finite alphabet of size q, and let

z
0
	​

=0,z
j
	​

=
t=1
∑
j
	​

(d+a
t
	​

),a
t
	​

∈A,

with all increments positive.

Lemma

For every r, there exists N
r
	​

(q) such that the partial-sum set

{z
0
	​

,z
1
	​

,…,z
N
r
	​

(q)
	​

}

contains a proper Hilbert cube of dimension r.

Proof

Take N
1
	​

(q)=1.

Assume N
r
	​

(q)=L. Set

T=q
L
+1.

Inside a sufficiently long word, select T disjoint blocks of L letters, placing at least one unused letter between consecutive blocks. There are only q
L
 possible length-L words, so two selected blocks are identical.

By the induction hypothesis, the partial sums inside each block contain an r-cube. Choose a canonical witness, for example the lexicographically first list of relative vertex positions. Since the two blocks have identical increment words, the same relative positions determine translated copies of the same r-cube.

If the translation between the block starts is B>0, their union is

H(a;b
1
	​

,…,b
r
	​

)∪(H(a;b
1
	​

,…,b
r
	​

)+B)=H(a;b
1
	​

,…,b
r
	​

,B).

The separating unused letter ensures the second copy lies strictly after the first, so the enlarged cube is proper.

A crude valid recurrence is

N
r+1
	​

(q)=(q
N
r
	​

(q)
+1)N
r
	​

(q)+q
N
r
	​

(q)
.

This proves the lemma.

For a square quasi-progression with width W, the alphabet consists of the W+1 possible errors e
i
	​

. Thus arbitrarily long quasi-progressions would produce proper square cubes of every dimension.

7. Boolean and discrete-curvature reformulation of square cubes

Assume a proper r-cube of squares exists. For every subset S⊆[r], define

Y(S)=
a+
i∈S
∑
	​

b
i
	​

	​

.

Then Y(S) is a positive integer and

Y(S)
2
=a+
i∈S
∑
	​

b
i
	​


is affine on the Boolean cube.

Equivalently, all mixed discrete derivatives of order at least 2 vanish after squaring:

Δ
i
	​

Δ
j
	​

(Y
2
)(S)=0.

Every two-dimensional face therefore satisfies

Y(S)
2
+Y(S∪{i,j})
2
=Y(S∪{i})
2
+Y(S∪{j})
2
.

This is the exact local parallelogram equation.

8. A higher-order integer-curvature invariant

For nonempty T⊆[r]∖S, define

κ
T
	​

(S)=(−1)
∣T∣−1
Δ
T
	​

Y(S).

Here Δ
T
	​

 means applying all discrete differences in the directions in T.

Let

f(x)=
x
	​

.

Repeated finite-difference integration gives

Δ
T
	​

Y(S)=∫
0
b
i
1
	​

	​

	​

⋯∫
0
b
i
t
	​

	​

	​

f
(t)
(A+u
1
	​

+⋯+u
t
	​

)du
1
	​

⋯du
t
	​

,

where

A=a+
j∈S
∑
	​

b
j
	​

,t=∣T∣.

Since

f
(t)
(x)=(−1)
t−1
2
t
(2t−3)!!
	​

x
1/2−t
,

we obtain

κ
T
	​

(S)>0.
	​


Because all Y(S) are integers,

κ
T
	​

(S)∈Z
≥1
	​

.
	​


The curvatures also obey the recursion

κ
T∪{j}
	​

(S)=κ
T
	​

(S)−κ
T
	​

(S∪{j}).
	​


Consequently,

κ
T
	​

(S∪{j})≤κ
T
	​

(S)−1.

Adding all still-unused directions one at a time gives

κ
T
	​

(S)≥r−∣S∣−∣T∣+1.
	​


Thus every mixed curvature is not merely nonzero: it must be large enough to survive all remaining Boolean directions while decreasing by at least one each time.

There is also the quantitative estimate

1≤κ
T
	​

(S)≤
2
t
A
t−1/2
(2t−3)!!
	​

i∈T
∏
	​

b
i
	​

,

hence

i∈T
∏
	​

b
i
	​

≥
(2t−3)!!
2
t
	​

A
t−1/2
.
	​


These inequalities force rapid size growth, but presently give no dimension-independent contradiction because a and the b
i
	​

 may grow arbitrarily quickly.

9. Edge marginals and the face-defect equation

For i∈
/
S, define the integer edge marginal

m
i
	​

(S)=Y(S∪{i})−Y(S).

Since the square difference along direction i is always b
i
	​

,

b
i
	​

=m
i
	​

(S)(2Y(S)+m
i
	​

(S)).
	​


As Y(S) increases, the positive solution

m=
Y(S)
2
+b
i
	​

	​

−Y(S)

strictly decreases. Hence for j∈
/
S∪{i},

m
i
	​

(S∪{j})≤m
i
	​

(S)−1.

In fact,

m
i
	​

(S)−m
i
	​

(S∪{j})=m
j
	​

(S)−m
j
	​

(S∪{i})=κ
{i,j}
	​

(S).

Put

y=Y(S),α=m
i
	​

(S),β=m
j
	​

(S),c=κ
{i,j}
	​

(S).

Then

Y(S∪{i,j})=y+α+β−c.

Substitution into the face equation yields

2αβ=c(2(y+α+β)−c).
	​


Moreover,

1≤c<min(α,β).

This is an exact Diophantine parametrization of every two-dimensional face.

10. Divisor explosion in every cube direction

Fix i. For every S⊆[r]∖{i},

b
i
	​

=(Y(S∪{i})−Y(S))(Y(S∪{i})+Y(S)).

Thus each context S supplies a factorization of b
i
	​

 as a difference of two squares.

Because the cube is proper, the values Y(S) are distinct. For fixed b
i
	​

, the marginal

m
i
	​

(S)=
Y(S)
2
+b
i
	​

	​

−Y(S)

is strictly decreasing as a function of Y(S). Hence the 2
r−1
 values m
i
	​

(S) are all distinct positive divisors of b
i
	​

.

Therefore

τ(b
i
	​

)≥2
r−1
,
	​


where τ is the divisor-counting function, and also

m
i
	​

(∅)≥2
r−1
.
	​


This forces every side length to be enormous. It does not give a contradiction because integers can have arbitrarily many divisors.

11. Modular restrictions and the failed descent

Squares modulo 4 belong to {0,1}.

If a≡0(mod4), every b
i
	​

 is 0 or 1(mod4), and two different b
i
	​

≡1(mod4) would create a vertex congruent to 2(mod4). If a≡1(mod4), every b
i
	​

 is 0 or 3(mod4), and two sides congruent to 3 would create a vertex congruent to 3(mod4).

Hence

all but at most one b
i
	​

 are divisible by 4.
	​


The same argument modulo 3, where the square residues are again {0,1}, gives

all but at most one b
i
	​

 are divisible by 3.
	​


After discarding at most two directions, one obtains a large subcube whose sides are all divisible by 12.

The descent fails because:

If the subcube consists of values divisible by 4, dividing by 4 preserves squares.

But an all-odd subcube consists of values 1(mod4); its sides may all be highly divisible without the values themselves having a common square factor.

Thus modular concentration forces large divisibility of the sides but does not presently force a common square divisor of all vertices.

12. Small proper square cubes

Local face equations do not prohibit even dimension 3.

A proper two-dimensional example is

H(1;15,48)={1,16,49,64}.

A proper three-dimensional example is

H(4;4485,7392,20160).

Its eight vertices are

4
4+4485
4+7392
4+20160
4+4485+7392
4+4485+20160
4+7392+20160
4+4485+7392+20160
	​

=2
2
,
=4489=67
2
,
=7396=86
2
,
=20164=142
2
,
=11881=109
2
,
=24649=157
2
,
=27556=166
2
,
=32041=179
2
.
	​


Thus any attempted universal obstruction must use genuinely higher-dimensional compatibility, not only individual two-faces.

13. Exact finite search for square cubes

With a root cutoff R, let

Q
R
	​

={1
2
,2
2
,…,R
2
}.

For each possible base square a, define

D
a
	​

={q−a:q∈Q
R
	​

, q>a}.

A recursive search chooses b
1
	​

<b
2
	​

<⋯, maintaining the set of existing subset sums Σ. A proposed side b is valid exactly when

b+Σ⊆D
a
	​

.

After adding it, replace

Σ⟵Σ∪(b+Σ).

This is an exact search for proper cubes under the root bound. It produces the three-dimensional example above. As in the quasi-progression search, the unresolved problem is converting a bounded search into an unbounded theorem.

14. Failure ledger
Equal-gap and arithmetic-progression extraction

Equal individual errors do not suffice; one needs three consecutive blocks with equal total error. Long ternary additive-cube-free words block this route.

Large-gap monovariant

The root gaps h
i
	​

 strictly decrease above 
W/2
	​

, but their initial value can be arbitrarily large. The continuous relaxation permits long decreasing chains.

Divisor counting

Every cube side needs exponentially many difference-of-square representations, but highly composite integers can supply arbitrarily many divisors.

Concavity and higher curvature

All mixed curvatures are positive integers and obey strong monotonicity. The resulting inequalities force very rapid growth, not a contradiction independent of height.

Modular descent

Most directions become divisible by any selected small modulus, but the cube parameters may absorb arbitrarily much divisibility. The all-odd branch prevents immediate division by a square.

Compactness

Arbitrarily long finite quasi-progressions for fixed W would not directly give an infinite path through a fixed finitely branching tree: the baseline D, starting root, and divisor interval all vary. A normalization preserving the square property has not been found.

Purely local face analysis

Proper dimension-three cubes exist, so no contradiction involving only isolated two-faces can settle the second question.

15. Precise remaining targets

The first question would be negatively resolved by proving the following uniform statement.

Uniform thin-hyperbola chain target.
For every fixed W, there is L(W) such that no integer sequence satisfying

D≤p
i
	​

h
i
	​

≤D+W,p
i+1
	​

=p
i
	​

+h
i
	​

+h
i+1
	​

,

together with p
i
	​

>h
i
	​

>0 and p
i
	​

≡h
i
	​

(mod2), has length exceeding L(W).

A positive construction would instead require arbitrarily long compatible divisor chains among W+1 consecutive integers.

For the second question, a negative result would follow from a height-independent bound on integer-valued functions Y for which Y
2
 is positive affine on a Boolean cube. The new curvature formulation isolates this as:

Integer complete-curvature target.
Bound the dimension of an integer function Y satisfying

Y(S)
2
=a+
i∈S
∑
	​

b
i
	​

,b
i
	​

>0,

using the complete family

κ
T
	​

(S)=(−1)
∣T∣−1
Δ
T
	​

Y(S)∈Z
>0
	​

.

A positive result would require a dimension-lifting construction: starting from a square cube H, find one integer B>0 such that both H and H+B consist entirely of squares. This amounts to finding a common difference-of-squares parameter with one representation for every vertex of H.

Under the conventional nondegenerate interpretation, neither target has been closed here. The established pieces are the exact gap-diameter normalization, the additive-cube obstruction and binary bound, the thin-hyperbola/divisor-chain equations, the finite-word proof that quasi-progressions imply cubes, the integer-curvature hierarchy, the divisor explosion, the modular concentration, and explicit proper cubes through dimension 3.
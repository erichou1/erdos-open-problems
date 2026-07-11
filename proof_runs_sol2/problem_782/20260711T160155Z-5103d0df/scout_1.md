1. Blocking formal defect

The immutable wording does not determine a unique nontrivial proposition.

If repetitions are allowed and d is unrestricted, the first question is trivially affirmative: choose any square x, put x
i
	​

=x, and take d=−C/2. Then

x
i
	​

+d≤x
i+1
	​

≤x
i
	​

+d+C.

If zero generators are allowed, the second question is trivially affirmative: take a square and b
i
	​

=0 for every i.

It is not specified whether d,a,b
i
	​

 must be integers, whether d,b
i
	​

>0, whether the x
i
	​

 must be distinct, whether all 2
r
 cube vertices must be distinct, or whether “arbitrarily large” means unbounded dimension or merely unbounded numerical size.

These choices materially change the questions. Consequently, the exact immutable text cannot be proved or disproved under the stated acceptance rule without first resolving the ambiguity.

The analysis below uses the standard nondegenerate interpretation:

S={n
2
:n∈Z
≥0
	​

},

the x
i
	​

 are distinct and increasing, d>0, and an r-cube means

a+{
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

∈{0,1}}

with a,b
i
	​

∈Z
≥0
	​

, b
i
	​

>0, and all 2
r
 subset sums distinct.

No resolution of either question is claimed.

2. The quasi-progression problem
2.1 Integer normalization

Write

q
i
	​

=x
i+1
	​

−x
i
	​

∈Z.

If q
i
	​

∈[d,d+C] with d∈R, then, setting

D=⌈d⌉,e
i
	​

=q
i
	​

−D,

we have

e
i
	​

∈{0,1,…,M},M≤⌊C⌋.

Thus the problem is equivalent to asking whether, for some fixed integer M≥0, there are arbitrarily long sequences of squares satisfying

x
i+1
	​

−x
i
	​

=D+e
i
	​

,e
i
	​

∈{0,…,M},

where D may depend on the sequence.

In particular, C<1 reduces to an exact arithmetic progression. Using the supplied assertion that four distinct integer squares cannot form a nonconstant four-term arithmetic progression, any successful C must satisfy C≥1.

The obstruction disappears immediately at width 1:

49, 225, 400, 576

has consecutive differences

176, 175, 176.
2.2 Universal finite-alphabet graph

Put

x
i
	​

=n
i
2
	​

,h
i
	​

=n
i+1
	​

−n
i
	​

>0.

Then

q
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

=h
i
	​

(2n
i
	​

+h
i
	​

)=D+e
i
	​

.

This produces an exact graph formulation independent of D.

Define Γ
M
	​

 to have vertices

(n,h,e)∈Z
≥0
	​

×Z
>0
	​

×{0,…,M},

with a directed edge

(n,h,e)⟶(n+h,h
′
,e
′
)

when

h
′
(2(n+h)+h
′
)−h(2n+h)=e
′
−e.

Along every directed path,

h
i
	​

(2n
i
	​

+h
i
	​

)−e
i
	​


is constant; this constant is D. Conversely, every quasi-progression gives such a path.

Hence the first problem becomes:

Does Γ
M
	​

 have arbitrarily long directed paths for some fixed M?

This eliminates the moving parameter D, but the graph remains infinite.

2.3 Linked factor-chain formulation

Define

u
i
	​

=2n
i
	​

+h
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

D+e
i
	​

=h
i
	​

u
i
	​


and

u
i+1
	​

=u
i
	​

+h
i
	​

+h
i+1
	​

.

Also u
i
	​

≥h
i
	​

 and u
i
	​

≡h
i
	​

(mod2).

Thus the first problem is exactly equivalent to the existence, for some fixed M, of arbitrarily long systems

D+e
i
	​

=h
i
	​

u
i
	​

,e
i
	​

∈{0,…,M},
u
i+1
	​

−u
i
	​

=h
i
	​

+h
i+1
	​

,

with the parity conditions above.

This may be viewed as a linked factor chain among M+1 consecutive integers. Each D+e
i
	​

 is factored, and adjacent factorizations are tied together by the additive relation on complementary factors.

A uniform bound on lengths of such linked factor chains would disprove the first assertion.

3. Exact root-gap identities

Since all q
i
	​

 lie in an interval of width M,

∣q
i+1
	​

−q
i
	​

∣≤M.

Writing N=n
i+1
	​

, a=h
i
	​

, and b=h
i+1
	​

, direct expansion gives

q
i+1
	​

−q
i
	​

=2N(b−a)+a
2
+b
2
.
(1)

This elementary identity imposes substantial structure.

3.1 Nondecreasing root gaps are small

If b≥a, then

q
i+1
	​

−q
i
	​

≥a
2
+b
2
≥2a
2
.

Consequently,

b≥a⟹2a
2
≤M.
(2)

Thus whenever

h
i
	​

>
M/2
	​

,

the root gaps must strictly decrease:

h
i+1
	​

<h
i
	​

.

A constant root gap h causes q
i
	​

 to rise by exactly 2h
2
 per step. Therefore a run of equal root gaps has length bounded in terms of M.

3.2 The decreasing phase

Suppose

r
i
	​

=h
i
	​

−h
i+1
	​

>0.

Then (1) becomes

	​

2n
i+1
	​

r
i
	​

−(h
i
2
	​

+h
i+1
2
	​

)
	​

≤M.
(3)

Thus

n
i+1
	​

≈
2r
i
	​

h
i
2
	​

+h
i+1
2
	​

	​

.

This is the hard regime. It says that the decrement r
i
	​

 must almost divide a particular sum of two squares, with an error selected from a fixed finite set.

In particular,

2r
i
	​

∣h
i
2
	​

+h
i+1
2
	​

−δ
i
	​


for some δ
i
	​

∈[−M,M]∩Z.

3.3 Exact two-step compatibility

Let

a=h
i
	​

,b=h
i+1
	​

,c=h
i+2
	​

,
r=a−b>0,s=b−c>0,
δ=q
i+1
	​

−q
i
	​

,η=q
i+2
	​

−q
i+1
	​

.

Eliminating n
i+1
	​

 from two instances of (3) gives

2b
2
(s−r)+6brs+rs(r−s)−δs+ηr=0.
(4)

This is an exact bounded-error recurrence for successive decrements.

Two useful consequences follow.

Equal decrements

If s=r, then (4) gives

δ−η=6br.

Since ∣δ−η∣≤2M,

3br≤M.
(5)

Hence two consecutive equal decrements are impossible when the intermediate gap b is large.

Decrement descent versus halving

Assume r≤b and s≥r. The non-error part of (4) is at least 6brs, whereas

∣δs−ηr∣≤M(r+s).

Since

r+s
rs
	​

≥
2
1
	​

,

we obtain

3b≤M.

Therefore, whenever b>M/3,

r≤b⟹s<r.
(6)

So in the large-gap phase, every transition has one of two forms:

Halving event: r>b, equivalently h
i
	​

>2h
i+1
	​

.

Decrement descent: r
i+1
	​

<r
i
	​

.

This substantially narrows the possible dynamics. It does not finish the argument because the initial gaps and decrements may be arbitrarily large.

Repeated halving events allow unbounded scale loss, while a long block without halving forces many strictly decreasing positive decrements and hence a very large initial root gap.

3.4 The small-gap tail is uniformly bounded

Once all h
i
	​

 are bounded by 
M
	​

, equation (1) implies that a change in h
i
	​

 can occur only while n
i
	​

=O(M). Indeed, if a,b≤
M
	​

 and a

=b, then

2n
i+1
	​

∣a−b∣≤M+a
2
+b
2
≤3M.

Thus n
i+1
	​

≤3M/2. Once the root is larger, the gap must remain constant, and a constant-gap run has bounded length.

Therefore all possible unbounded behavior is concentrated in the initial phase where the h
i
	​

 are large, strictly decreasing, and satisfy (3)–(6).

This is the sharpest isolated core obtained here.

4. Why quasi-progressions force cubes

The claimed implication can be proved directly from finite words.

Suppose

x
t+1
	​

=x
1
	​

+tD+S
t
	​

,S
t
	​

=e
1
	​

+⋯+e
t
	​

,

where every e
i
	​

 belongs to the finite alphabet

A={0,…,M}.

Consider the lattice path

P
t
	​

=(t,S
t
	​

)∈Z
2
.
Finite-word cube lemma

For every r, there is a finite L
r
	​

 such that every sufficiently long word over A contains vectors

P
t
0
	​

+∑ϵ
j
	​

u
j
	​

	​

=P
t
0
	​

	​

+
j=1
∑
r
	​

ϵ
j
	​

(u
j
	​

,v
j
	​

)

for all ϵ
j
	​

∈{0,1}, with all 2
r
 points distinct.

Proof

Use induction on r.

For the induction step, divide a sufficiently long word into many equal-length blocks, leaving one unused symbol between consecutive blocks. There are only finitely many possible blocks. Two blocks are therefore identical.

By induction, the path inside the first block contains an r-cube. Because the second block has exactly the same word, the corresponding path points form a translate of that cube. The separator ensures the two copies are disjoint. Their union is an (r+1)-cube. ∎

Apply the linear map

(t,s)⟼x
1
	​

+Dt+s.

It sends every path point P
t
	​

 to the square x
t+1
	​

. Hence the lattice cube maps to

a+{
j=1
∑
r
	​

ϵ
j
	​

(Du
j
	​

+v
j
	​

)}.

Because the x
t
	​

 are increasing, all images remain distinct and every generator is positive.

Thus:

Under the nondegenerate interpretation, arbitrarily long quasi-progressions of fixed width imply square cubes of arbitrarily large dimension.

The block lengths produced by this argument grow extremely rapidly, but only finiteness is needed.

5. Structural reformulations of square cubes

Let

x
S
	​

=a+
i∈S
∑
	​

b
i
	​

=y
S
2
	​

,S⊆[r].

All x
S
	​

 are assumed distinct.

5.1 Every face is a parallelogram of squares

For i,j∈
/
S,

y
S
2
	​

+y
S∪{i,j}
2
	​

=y
S∪{i}
2
	​

+y
S∪{j}
2
	​

.
(7)

Thus the full problem is equivalent to assigning integer square roots to a Boolean lattice so that all two-dimensional faces satisfy (7).

5.2 Recursive factor-set formulation

For b>0, define

P(b)={u
2
:u≥0, u
2
+b is a square}.

Then an r-cube with final generator b
r
	​

 is exactly the union

H∪(H+b
r
	​

),

where H is an (r−1)-cube contained in P(b
r
	​

).

Moreover,

u
2
∈P(b)

if and only if

b=vw,v,w>0,v≡w(mod2),

with

u=
2
w−v
	​

.

So P(b) is finite and explicitly parameterized by factor pairs of b.

The second question is therefore equivalent to:

Are the factor-pair sets P(b) capable of containing cubes of unbounded dimension as b varies?

This is a coherent divisor problem rather than a density problem.

5.3 Exponential factorization requirement

Fix a nonempty T⊆[r] and put

B
T
	​

=
i∈T
∑
	​

b
i
	​

.

For every S⊆[r]∖T,

B
T
	​

=y
S∪T
2
	​

−y
S
2
	​

=(y
S∪T
	​

−y
S
	​

)(y
S∪T
	​

+y
S
	​

).
(8)

The lower roots y
S
	​

 are distinct, so the first factors in (8) are distinct positive integers. There are 2
r−∣T∣
 of them, and each is at most 
B
T
	​

	​

. Consequently,

B
T
	​

	​

≥2
r−∣T∣

and hence

B
T
	​

≥4
r−∣T∣
.
	​

(9)

In particular,

b
i
	​

≥4
r−1
	​

(10)

for every generator.

Equivalently, every generator b
i
	​

 must have at least 2
r−1
 distinct difference-of-square representations arising coherently from the other directions.

This proves that high-dimensional cubes, if they exist, must occur at exponentially large scale. It gives no dimension bound because the scale is unrestricted.

5.4 Strict root concavity

For i∈
/
S, define the root increment

ρ
i
	​

(S)=y
S∪{i}
	​

−y
S
	​

.

For fixed b
i
	​

,

ρ
i
	​

(S)=
y
S
2
	​

+b
i
	​

	​

−y
S
	​

.

This is a strictly decreasing function of y
S
	​

. Therefore, for j∈
/
S∪{i},

ρ
i
	​

(S)>ρ
i
	​

(S∪{j}).

Equivalently,

κ
ij
	​

(S)=y
S∪{i}
	​

+y
S∪{j}
	​

−y
S
	​

−y
S∪{i,j}
	​


is a positive integer, so

κ
ij
	​

(S)≥1.
(11)

When y
S
	​

>0, calculus gives the upper bound

κ
ij
	​

(S)≤
4y
S
3
	​

b
i
	​

b
j
	​

	​

.

Thus

b
i
	​

b
j
	​

≥4y
S
3
	​

.
	​

(12)

Taking S=[r]∖{i,j} constrains every pair of generators in terms of almost the entire cube.

Again, this forces rapid growth and rough comparability but does not bound r.

6. Congruence compression
6.1 Modulo 4

A difference of two squares is never 2(mod4). Therefore every nonempty subset sum

i∈T
∑
	​

b
i
	​


avoids 2(mod4).

It follows that:

no b
i
	​

 is 2(mod4);

there cannot be two generators congruent to 1(mod4);

there cannot be two generators congruent to 3(mod4).

Hence:

All but at most two generators are divisible by 4.
	​

(13)

If there are two odd generators, one must be 1(mod4) and the other 3(mod4).

6.2 Odd-prime lemma

Let p be an odd prime. At most

2
p−1
	​


of the generators can be nonzero modulo p.

Proof

Let b
1
	​

,…,b
t
	​

 be the generators not divisible by p. Modulo p, all subset sums

a+
i=1
∑
t
	​

ϵ
i
	​

b
i
	​


must lie among the (p+1)/2 square residues.

Starting with A
0
	​

={a}, define

A
j
	​

=A
j−1
	​

∪(A
j−1
	​

+b
j
	​

).

If A
j−1
	​


=F
p
	​

 and b
j
	​


=0, then A
j−1
	​

+b
j
	​


=A
j−1
	​

; otherwise A
j−1
	​

 would be invariant under translation by a nonzero element and hence equal to all of F
p
	​

. Therefore

∣A
j
	​

∣≥∣A
j−1
	​

∣+1.

Thus ∣A
t
	​

∣≥t+1. Since A
t
	​

 lies in the square residues,

t+1≤
2
p+1
	​

.

Hence t≤(p−1)/2. ∎

Examples:

p=3
p=5
p=7
	​

:all but at most one b
i
	​

 are divisible by 3,
:all but at most two are divisible by 5,
:all but at most three are divisible by 7.
	​


For any finite set P of odd primes, deleting at most

p∈P
∑
	​

2
p−1
	​


directions leaves a subcube whose every generator is divisible by

p∈P
∏
	​

p.
(14)

This is strong divisibility compression, but not a contradiction: the generators may be arbitrarily large.

7. Explicit low-dimensional falsification tests

The claim “square cubes stop already in dimension 3” is false.

A 2-cube is

{1,16,49,64}=1+{0,15}+{0,48}.

A nondegenerate 3-cube is

4+{ϵ
1
	​

(4485)+ϵ
2
	​

(7392)+ϵ
3
	​

(20160)}.

Its eight values are

value
4
4489
7396
11881
20164
24649
27556
32041
	​

square root
2
67
86
109
142
157
166
179.
	​

	​


So any attempted proof must allow at least dimension 3.

An exhaustive recursive search over all squares with roots at most 500 found no nondegenerate 4-cube. The recursion used the exact criterion

H
r+1
	​

=H
r
	​

∪(H
r
	​

+b),H
r
	​

+b⊆S.

This is only a bounded falsification test, not evidence sufficient for a global conclusion.

8. Quasi-progression computation

For fixed integer width M and root bound N, one can exhaustively construct, for each integer D, the directed acyclic graph

n⟶m⟺D≤m
2
−n
2
≤D+M

on 0≤n<m≤N, and compute its longest path.

Results of bounded searches included:

M
0
1
2
3
4
6
7
8
10
	​

root bound
1000
1000
500
500
500
500
500
500
500
	​

largest length found
3
4
4
4
5
6
7
8
9.
	​

	​


Some witnesses are

0,9,16,25,36

with gaps 9,7,9,11, of width 4, and

0,16,36,49,64,81,100

with gaps 16,20,13,15,17,19, of width 7.

For M=1, no length-5 sequence was found with roots at most 1000.

9. A precise width-1 subproblem

For a hypothetical length-5 sequence at width 1, write

x
i+1
	​

−x
i
	​

=D+e
i
	​

,e
i
	​

∈{0,1}.

There are sixteen binary error words of length four.

Six contain 000 or 111, and therefore contain four consecutive squares in an exact arithmetic progression.

Direct residue checking modulo 3 eliminates

0011,0110,1001,1100.

Direct residue checking modulo 4 eliminates

0101,1010.

The four residual patterns are

0010,0100,1011,1101.

For example, pattern 0010 requires square roots y
0
	​

,…,y
4
	​

 satisfying

y
j
2
	​

=A+jD+S
j
	​

,(S
0
	​

,…,S
4
	​

)=(0,0,0,1,1),

and in particular

y
0
2
	​

+y
4
2
	​

−2y
2
2
	​

=1.

Thus even the concrete target

Prove that no five increasing squares have all four gaps in {D,D+1}

reduces to four unresolved bounded-defect quadratic systems after elementary sieving.

This is a useful weaker target; it is not resolved here.

10. Failed approaches and what they establish
Fixed-modulus obstruction

A fixed modulus cannot settle the cube problem. Scaling an existing cube by a square divisible by that modulus makes every generator and every vertex 0 modulo the modulus. Primitive normalization helps, but the odd-prime lemma still yields divisibility rather than contradiction.

Divisor counting

The bound b
i
	​

≥4
r−1
 is strong but scale-free. Integers can have arbitrarily many divisors, and no upper bound on b
i
	​

 is available.

Density or random-model arguments

Squares are sparse, and a random model predicts that high-dimensional cubes should be extremely rare. But the parameters a,b
i
	​

 have no height restriction and the square conditions are highly correlated. A density estimate cannot produce exact global nonexistence.

Continuous approximation

Ignoring integrality, the quasi-progression dynamics resembles

n
i+1
2
	​

−n
i
2
	​

≈D,

whose real solution is simply

n
i
	​

≈
A+iD
	​

.

Thus the real limiting problem has arbitrarily long solutions. Any proof must use arithmetic discreteness, particularly the divisibility in (3).

Compactness

Arbitrarily long paths could be reduced modulo every fixed modulus and diagonalized to a profinite path. However D can tend to 0 profinitely by taking it divisible by successively larger moduli, producing a degenerate constant profinite solution. This loses the archimedean scale and gives no contradiction.

Minimal-height cube induction

An r-cube splits into two (r−1)-cubes. Choosing a primitive cube of minimal height does not create a descent: both faces have lower dimension, not the same dimension. Scaling symmetry defeats a naive extremal argument.

Pure monotonicity of root gaps

The gaps h
i
	​

 are eventually decreasing, but their initial size is unbounded. The two-step identity gives decrement descent or halving, yet both mechanisms can last longer when the initial scale grows.

11. Precise remaining targets

The following would constitute genuine progress.

Linked-factor-chain bound.
Prove that for every fixed M, every system

D+e
i
	​

=h
i
	​

u
i
	​

,u
i+1
	​

−u
i
	​

=h
i
	​

+h
i+1
	​

,0≤e
i
	​

≤M

has length bounded solely in terms of M.

Large decreasing-phase monovariant.
Find a quantity attached to

(h
i
	​

,r
i
	​

,δ
i
	​

)

that changes strictly under the exact recurrence (4), including across halving events.

Width-1 obstruction.
Resolve the four remaining binary error patterns for length 5. This would prove that C=1 does not work, but would not resolve larger C.

Uniform factor-set cube bound.
Prove that the maximum cube dimension inside

P(b)={u
2
:u
2
+b is square}

is bounded independently of b.

Combine congruence compression with concavity.
The modular lemmas force large common divisibility on a high-dimensional subcube, while (12) constrains generator sizes relative to the top root. At present these inequalities are compatible; an additional primitive-height estimate is missing.

The exact original statement remains blocked by its degeneracy ambiguities. Under the standard nondegenerate interpretation, the finite-alphabet implication, linked-factor-chain reformulation, decrement recurrence, exponential divisor requirement, modular compression, and explicit three-dimensional example are established, but neither question is resolved.
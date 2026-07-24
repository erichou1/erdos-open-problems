Offline proof-search report

I used only the uploaded statement and the accompanying untrusted scout material, rechecking every retained assertion independently. The file reference identifies the input rather than serving as mathematical evidence. 

Pasted text

1. Exact normalization and semantic obstruction
First question

The literal quantifier structure appears to be

∃C>0 ∀k≥1 ∃x
1
	​

,…,x
k
	​

 ∃d ∀i<k:x
i
	​

+d≤x
i+1
	​

≤x
i
	​

+d+C,

where every x
i
	​

 is a square.

The wording leaves unresolved:

whether the x
i
	​

 must be distinct or strictly increasing;

whether d must be positive;

whether d must be an integer;

whether 0 is included among the squares.

The distinction is material. Without distinctness or positivity of d, the constant sequence x
i
	​

=1, d=0, works for every k.

Second question

The intended quantifier structure is presumably

∀r≥1 ∃a,b
1
	​

,…,b
r
	​

{a+
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

∈{0,1}}⊆{n
2
:n∈Z
≥0
	​

},

with b
i
	​

>0 and all 2
r
 subset sums distinct.

The wording does not explicitly specify:

the number of generators;

their domain or signs;

whether zero generators are permitted;

whether all vertices must be distinct;

whether “large” means large dimension, cardinality, or numerical magnitude.

If b
i
	​

=0 is allowed and “large” means nominal dimension, a=1 gives collapsed cubes of every dimension.

Thus the immutable wording does not define a unique proposition. The substantive analysis below uses the following working interpretation, without asserting that it is the only possible repair.

Working interpretation

A quasi-progression consists of

0≤n
1
	​

<n
2
	​

<⋯<n
k
	​

,x
i
	​

=n
i
2
	​

,

whose consecutive square gaps have uniformly bounded diameter.

A proper r-cube consists of integers

a≥0,b
1
	​

,…,b
r
	​

>0,

such that all 2
r
 subset sums are distinct and all numbers

a+
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


are squares.

The negation of the first intended assertion is:

For every fixed gap width W, there is a bound B(W) on the length of every such sequence.

Because a face of a proper cube is proper, the negation of the second assertion is:

There exists a dimension r
0
	​

 in which no proper square cube exists.

2. Attack portfolio
Branch	Required decisive lemma	Fastest falsification test	Principal failure mode
Literal interpretation	Check omitted nondegeneracy conditions	Constant sequences and zero generators	Produces trivial answers to only some readings
Negative quasi-progression	Uniform bound for linked factor chains in W+1 consecutive integers	Search exact chains satisfying product, parity, and endpoint compatibility	Initial factor scale is unrestricted
Positive quasi-progression	Construct arbitrarily long compatible chains for one fixed W	Verify every product and shared endpoint exactly	Continuous approximations do not preserve integrality
Symbolic-error attack	Show every sufficiently long realizable error word creates four square terms in progression	Exhaust finite alphabets and then test the associated quadratic systems	Ternary additive-cube-free words already survive substantial lengths
Negative cube attack	Convert curvature, divisibility, and divisor explosion into a dimension bound	Test every proposed inequality on explicit 3-cubes	All restrictions can be absorbed by enormous generators
Positive cube attack	Lift an r-cube by a common square translate	Solve x+B=□ simultaneously for all existing vertices	Number of linked equations doubles each dimension
Transfer attack	Extract proper Hilbert cubes from finite-gap sequences	Canonical repeated-block induction	Gives only first-question ⇒ second-question
3. Numbered claims
C1. Semantic ambiguity is mathematically material

Dependencies: none.

The literal first question is affirmative under the permissive reading allowing repeated terms and d=0: take

x
1
	​

=⋯=x
k
	​

=1.

The displayed inequalities become

1≤1≤1+C.

The nominal-dimension reading of the second question is affirmative if zero generators are permitted:

a=1,b
1
	​

=⋯=b
r
	​

=0.

The resulting set is {1}, regardless of r.

These constructions do not answer the proper interpretations. They prove that the missing conventions change the proposition.

C2. Integer-width normalization

Dependencies: C1 and the working strict-increase convention.

Let

G
i
	​

=x
i+1
	​

−x
i
	​

∈Z
>0
	​

.

There exists a real d such that

d≤G
i
	​

≤d+Cfor all i

if and only if

i
max
	​

G
i
	​

−
i
min
	​

G
i
	​

≤C.

The reverse implication follows by taking d=min
i
	​

G
i
	​

. Since the diameter is an integer, this is equivalent to

i
max
	​

G
i
	​

−
i
min
	​

G
i
	​

≤W,W=⌊C⌋.

Putting

D=
i
min
	​

G
i
	​

,G
i
	​

=D+e
i
	​

,

we obtain

e
i
	​

∈{0,1,…,W}.

Thus the intended first question is equivalent to:

Does some fixed integer W≥0 admit arbitrarily long increasing square sequences whose consecutive gaps all belong to one interval

{D,D+1,…,D+W},

where D may vary between sequences?

Only the integer width W matters.

C3. Exact linked-factor-chain equivalence

Dependencies: C2.

Write

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

,p
i
	​

=n
i+1
	​

+n
i
	​

.

Then

D+e
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

p
i
	​

.

Consecutive factor pairs satisfy

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

They also satisfy

p
i
	​

≥h
i
	​

>0,p
i
	​

≡h
i
	​

(mod2),

with equality p
i
	​

=h
i
	​

 exactly when n
i
	​

=0. If positive squares only are used, then p
i
	​

>h
i
	​

.

Conversely, suppose positive integers h
i
	​

,p
i
	​

 satisfy

D+e
i
	​

=h
i
	​

p
i
	​

,p
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

together with

p
i
	​

≥h
i
	​

,p
i
	​

≡h
i
	​

(mod2).

Define

n
i
	​

=
2
p
i
	​

−h
i
	​

	​

,n
i+1
	​

=
2
p
i
	​

+h
i
	​

	​

.

The adjacency equation ensures that the upper root reconstructed from the i-th pair equals the lower root reconstructed from the (i+1)-st pair. Hence the factor chain reconstructs an increasing square quasi-progression.

Therefore the first intended question is exactly a problem about arbitrarily long compatible factorizations of W+1 consecutive integers.

C4. One-step root-gap identity

Dependencies: C3.

Let

a=h
i
	​

,b=h
i+1
	​

,N=n
i+1
	​

,

and let

δ
i
	​

=G
i+1
	​

−G
i
	​

.

Direct expansion gives

δ
i
	​

=2N(b−a)+a
2
+b
2
.
	​


Because all G
i
	​

 lie in an interval of width W,

∣δ
i
	​

∣≤W.

If b≥a, every term on the right is nonnegative, so

a
2
+b
2
≤W.

In particular,

b≥a⟹2a
2
≤W.

Consequently,

h
i
	​

>
W/2
	​

⟹h
i+1
	​

<h
i
	​

.

If h
i+1
	​

=h
i
	​

=h, then

G
i+1
	​

−G
i
	​

=2h
2
.

A plateau of t consecutive root gaps equal to h therefore satisfies

2h
2
(t−1)≤W,

so

t≤⌊
2h
2
W
	​

⌋+1.

Thus large root gaps strictly decrease, while every constant run is uniformly bounded.

C5. Exact decreasing-step equation and cubic quotient

Dependencies: C3–C4.

Suppose

a=h
i
	​

>b=h
i+1
	​

,e
i
	​

,e
i+1
	​

∈{0,…,W}.

Eliminating p
i
	​

 from the linked-factor equations gives

D(a−b)=ab(a+b)+e
i
	​

b−e
i+1
	​

a.
	​


Therefore every decreasing pair satisfies

	​

D−
a−b
ab(a+b)
	​

	​

≤W
a−b
a+b
	​

.

Define the cubic quotient

Q(a,b)=
a−b
ab(a+b)
	​

.

Every adjacent decreasing pair must approximate the same integer D, with an explicit error controlled only by W and the ratio (a+b)/(a−b).

This is substantially stronger than mere monotonicity, but it does not yet yield a scale-independent length bound.

C6. Two-step recurrence and descent-versus-halving dichotomy

Dependencies: C4–C5.

Assume three successive root gaps strictly decrease:

a=h
i
	​

>b=h
i+1
	​

>c=h
i+2
	​

.

Set

r=a−b,s=b−c,

and

δ=G
i+1
	​

−G
i
	​

,η=G
i+2
	​

−G
i+1
	​

.

Eliminating n
i+1
	​

 from two copies of C4 gives

2b
2
(s−r)+6brs+rs(r−s)−δs+ηr=0.
	​

Equal decrements

If s=r, the equation becomes

δ−η=6br.

Since ∣δ−η∣≤2W,

3br≤W.

Thus equal consecutive decrements are impossible when br>W/3.

Transition classification

Assume r≤b and s≥r. Since c=b−s>0, we have s<b, and hence

2b
2
−rs>0.

The non-error terms satisfy

2b
2
(s−r)+6brs+rs(r−s)=(s−r)(2b
2
−rs)+6brs≥6brs.

Therefore

6brs≤W(r+s).

Because

rs
r+s
	​

=
r
1
	​

+
s
1
	​

≤2,

we obtain

3b≤W.

Consequently, whenever b>W/3, every transition has one of two forms:

Decrement descent:

r≤b⟹s<r.

Halving event:

r>b⟺a=b+r>2b.

This is a genuine structural dichotomy. It does not terminate the chain because arbitrarily large initial gaps may support many decreasing decrements, while halving events can repeatedly reduce the scale.

C7. Uniformly bounded small-gap tail

Dependencies: C4.

Assume W≥1, and suppose that at some point

h
i
	​

≤
W
	​

.

Then every later root gap is also at most 
W
	​

. Indeed:

if h
j+1
	​

<h
j
	​

, the assertion is immediate;

if h
j+1
	​

≥h
j
	​

, C4 gives h
j+1
2
	​

≤W.

Now suppose

h
j
	​

,h
j+1
	​

≤
W
	​

,h
j
	​


=h
j+1
	​

.

From C4,

2n
j+1
	​

∣h
j+1
	​

−h
j
	​

∣≤W+h
j
2
	​

+h
j+1
2
	​

≤3W.

Since the difference is a positive integer,

n
j+1
	​

≤
2
3W
	​

.

Thus, once the root exceeds 3W/2, the root gap can no longer change. It becomes constant, and its remaining plateau has length at most

⌊
2h
2
W
	​

⌋+1≤⌊
2
W
	​

⌋+1.

Because roots increase by at least one at each edge, the total number of edges after the first occurrence of h
i
	​

≤
W
	​

 is at most the coarse bound

2W+4.

Therefore every possible unbounded chain must spend almost all of its length in the regime

h
i
	​

>
W
	​

,

where the gaps are strictly decreasing.

C8. Additive-cube obstruction for the error word

Dependencies: C2 and the supplied premise that four distinct squares do not form a nonconstant arithmetic progression.

Suppose three consecutive blocks of the error word have equal length r and equal sum:

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

Each corresponding block of square gaps has sum

rD+the common error sum.

Hence

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


form a four-term arithmetic progression.

Strict increase makes these four squares distinct, contradicting the supplied premise.

Thus every realizable error word avoids three adjacent equal-length blocks having equal sums. Call such a forbidden pattern an additive cube.

C9. Exact global bound for widths W≤1

Dependencies: C8.

For binary words, exhaustive recursive extension gives the following counts of additive-cube-free words:

1,2,4,6,10,16,18,12,10,6,0

for lengths 0,1,…,10.

The six surviving words of length 9 are

	​

001101100,001101101,010010011,
101101100,110010010,110010011.
	​


Appending either 0 or 1 to any one creates an additive cube.

The enumeration is exhaustive: when a letter is appended to an already valid word, it is enough to inspect forbidden configurations ending at the new final position.

A width-1 quasi-progression with k square vertices has a binary error word of length k−1. Therefore

W≤1⟹k≤10.
	​


In terms of the original real constant:

C<2

cannot support arbitrarily long proper quasi-progressions.

This is a global conclusion, not a bounded-height experiment.

C10. Finite-gap sequences contain proper Hilbert cubes

Dependencies: C2.

Let A⊂Z
>0
	​

 be a finite alphabet of size q. For a word

a
1
	​

,a
2
	​

,…,a
i
	​

∈A,

write its prefix sums as

z
0
	​

=0,z
t
	​

=
i=1
∑
t
	​

a
i
	​

.
Theorem

For every r, there exists N
r
	​

(q) such that the prefix sums of every word of length N
r
	​

(q) contain a proper additive cube of dimension r.

Proof

For r=1, take any two consecutive prefix sums.

Assume the assertion for r, with block length

L=N
r
	​

(q).

There are at most

T=q
L

possible words of length L.

Take T+1 disjoint blocks of length L, placing one unused positive letter between consecutive blocks. Two blocks are identical.

Inside each block, choose the lexicographically first relative r-cube witness. This canonical rule ensures that identical blocks select cubes with the same relative positions and the same directions.

Let the first selected cube be H, and let B be the difference between the two block-start prefix sums. The second selected cube is exactly H+B.

Because at least one positive separator lies between the blocks,

B>diam(H).

Hence H and H+B are disjoint, and

H∪(H+B)

is a proper (r+1)-cube.

One valid recurrence is

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

This completes the induction.

Application

A width-W square quasi-progression has consecutive positive gaps drawn from at most W+1 values. Its square values are translates of the corresponding prefix sums.

Therefore:

arbitrarily long proper square quasi-progressions⟹proper square cubes of every dimension.
	​


The implication stated in the problem is thus established under the working interpretations.

C11. Primitive normalization and congruence compression for cubes

Dependencies: the proper-cube convention.

Suppose

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

=Y(S)
2
,S⊆[r].
Square gcd

The gcd of all vertices equals

gcd(a,b
1
	​

,…,b
r
	​

),

because every b
i
	​

 is the difference between the vertex a+b
i
	​

 and the base a.

The gcd of a finite collection of squares is itself a square: every prime valuation is the minimum of even valuations.

Hence

gcd(a,b
1
	​

,…,b
r
	​

)

is a perfect square. Dividing by it produces another integer square cube. It is therefore enough to study primitive cubes satisfying

gcd(a,b
1
	​

,…,b
r
	​

)=1.
Modulo 4

If a≡0(mod4), then every b
i
	​

 is 0 or 1(mod4), and two sides congruent to 1 would create a vertex congruent to 2.

If a≡1(mod4), then every b
i
	​

 is 0 or 3(mod4), and two sides congruent to 3 would create a vertex congruent to 3.

Therefore

all but at most one b
i
	​

 are divisible by 4.
	​

Odd primes

Let p be odd, and let Q
p
	​

 be the set of quadratic residues modulo p, including zero:

∣Q
p
	​

∣=
2
p+1
	​

.

Process the directions one at a time. If A is the current subset-sum residue set and b
i
	​


≡0(modp), then

A∪(A+b
i
	​

)

is strictly larger than A. Otherwise A=A+b
i
	​

, making A invariant under a nonzero translation, hence equal to all of F
p
	​

, impossible because A⊆Q
p
	​

.

Starting from one residue and remaining inside Q
p
	​

, at most

2
p−1
	​


directions can be nonzero modulo p. Thus

#{i:p∤b
i
	​

}≤
2
p−1
	​

.
	​


For every fixed finite set of primes, a high-dimensional cube therefore has a high-dimensional face whose directions are divisible by their product.

The resulting descent is incomplete. For example, modulo 3, an exceptional direction allows selection of an opposite face all of whose vertices are divisible by 9, but this loses one dimension. If no exceptional direction exists, the primitive base may simply remain 1(mod3).

C12. Complete integer curvature and exponential curvature spectra

Dependencies: the proper-cube convention.

For nonempty T⊆[r]∖S, define

κ
T
	​

(S)=(−1)
∣T∣−1
Δ
T
	​

Y(S),

where Δ
T
	​

 is the mixed Boolean finite difference in the directions in T.

Let t=∣T∣, and write

A
S
	​

=a+
j∈S
∑
	​

b
j
	​

.

Repeated finite-difference integration for f(x)=
x
	​

 gives

κ
T
	​

(S)=
2
t
(2t−3)!!
	​

∫
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

(A
S
	​

+u
1
	​

+⋯+u
t
	​

)
1/2−t
du
1
	​

⋯du
t
	​

.

At A
S
	​

=0, this is interpreted by the convergent limit from positive A
S
	​

.

The integrand is positive, so

κ
T
	​

(S)>0.

It is also an integer, being an integer linear combination of the integer roots Y(U). Therefore

κ
T
	​

(S)∈Z
>0
	​

.
	​


The recursion is

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


More strongly, for fixed T, the integral is a strictly decreasing function of A
S
	​

. Properness makes the 2
r−t
 values

A
S
	​

,S⊆[r]∖T,

distinct. Consequently the corresponding curvatures are 2
r−t
 distinct positive integers.

Define the curvature spectrum

K
T
	​

={κ
T
	​

(S):S⊆[r]∖T}.

Then

∣K
T
	​

∣=2
r−t
,

and, because S=∅ has the smallest base,

κ
T
	​

(∅)≥2
r−t
.
	​


This strengthens the merely linear “survival” bound.

For a two-face, put

y=Y(S),α=Δ
i
	​

Y(S),β=Δ
j
	​

Y(S),c=κ
{i,j}
	​

(S).

Then

Y(S∪{i,j})=y+α+β−c,

and the affine-square face identity gives

2αβ=c(2(y+α+β)−c).
	​


Moreover

1≤c<min(α,β).

These are strong exact Diophantine constraints, but they remain compatible with sufficiently large parameters.

C13. Divisor explosion in every direction

Dependencies: the proper-cube convention; compatible with C12.

Fix a direction i. For every

S⊆[r]∖{i},

define the positive root marginal

m
i
	​

(S)=Y(S∪{i})−Y(S).

Then

b
i
	​

=Y(S∪{i})
2
−Y(S)
2
=m
i
	​

(S)(2Y(S)+m
i
	​

(S)).

Thus every m
i
	​

(S) is a positive divisor of b
i
	​

.

For fixed b
i
	​

, the real function

y⟼
y
2
+b
i
	​

	​

−y

is strictly decreasing. Since the lower cube vertices Y(S)
2
 are distinct, the 2
r−1
 values m
i
	​

(S) are distinct positive integers.

Therefore

τ(b
i
	​

)≥2
r−1
,
	​


where τ is the divisor-counting function.

The largest marginal occurs at S=∅, so

m
i
	​

(∅)≥2
r−1
.

Hence

b
i
	​

≥m
i
	​

(∅)
2
≥4
r−1
.
	​


Every direction must therefore be exponentially large and have exponentially many coherent difference-of-square representations.

This is not a dimension bound because the generators have no permitted upper bound.

C14. Minimal countertests to overstrong lemmas

Dependencies: direct calculation.

Width 1 is not locally impossible

The squares

49,225,400,576

have consecutive gaps

176,175,176.

Thus a width-1 quasi-progression can have four vertices.

Genuine halving events occur

The roots

5,32,45,55

give gaps

999,1001,1000,

of width 2. Their root gaps are

27,13,10.

The first decrement is

27−13=14>13,

so it is a genuine halving event.

The roots

1,41,58,71,82

give square gaps

1680,1683,1677,1683,

of width 6, and root gaps

40,17,13,11.

The first transition is a halving event, followed by decrement descent:

23, 4, 2.

Thus neither “decrements always decrease” nor “halving occurs only once” can be assumed without proof.

Ternary symbolic avoidance survives beyond the binary threshold

The word

001001002001001120010200110120

has length 30 and contains no three consecutive equal-length blocks with equal sums. This was checked directly over every possible starting point and block length.

Therefore the binary finite-word obstruction does not automatically extend to width 2.

Proper square cubes exist through dimension 3

A proper 2-cube is

1+{0,15,48,15+48}={1,16,49,64}.

A proper 3-cube is

H(4;4485,7392,20160).

Its vertices are

4
4489
7396
11881
20164
24649
27556
32041
	​

2
2
67
2
86
2
109
2
142
2
157
2
166
2
179
2
	​


Thus isolated face equations, simple congruences, and low-order curvature cannot rule out all nontrivial cubes.

4. Failed attacks and retained information
Pure monotonicity

C4 proves eventual strict decrease of large root gaps, but the initial gap is unrestricted. A decreasing sequence of positive integers can be arbitrarily long when its initial value varies.

Decrement monovariants

C6 shows decrement descent except at halving events. C14 gives exact halving examples. A valid monovariant must decrease through both transition types and be bounded below independently of D.

No such quantity was obtained.

Continuous relaxation

Ignoring integrality, the relation

D(a−b)≈ab(a+b)

allows slowly decreasing trajectories over a number of steps growing with the scale. Thus archimedean monotonicity alone cannot be decisive.

Fixed error words

For a fixed word e
1
	​

,…,e
k−1
	​

, put

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

.

Eliminating D gives

n
j
2
	​

=(j−1)n
2
2
	​

−(j−2)n
1
2
	​

+E
j−1
	​

−(j−1)e
1
	​

.

This converts the problem into finitely many simultaneous quadratic-square systems for each fixed W,k.

Modular tests can eliminate individual words, but no uniform theorem proving finiteness for every sufficiently long word was obtained.

Fixed-modulus cube obstructions

Scaling an existing cube by a square makes every parameter divisible by any prescribed fixed modulus. Primitive normalization prevents this trivial evasion, but C11 still yields concentration rather than contradiction.

Divisor and curvature growth

C12–C13 force exponential curvature spectra, exponentially many divisors, and exponentially large sides. All these estimates are lower bounds, whereas the problem imposes no height upper bound.

Minimal-height descent

Taking a face lowers dimension. Dividing a highly divisible face may reduce height, but does not produce a smaller cube of the same dimension. Hence it cannot directly contradict minimality at fixed dimension.

Positive dimension lifting

To lift a square cube H, one needs a single B>0 such that

x+B

is a square for every x∈H. Equivalently, H must lie in

P(B)={u
2
:u
2
+B is a square}.

No mechanism was found that solves these exponentially many linked equations while preserving properness.

5. Dependency ledger
Claim	Dependencies	Status
C1	None	Checked
C2	C1 plus strict increase	Checked
C3	C2	Checked, including the n
i
	​

=0 boundary
C4	C3	Checked by expansion
C5	C3–C4	Checked algebraically
C6	C4–C5	Checked algebraically; inequality direction corrected
C7	C4	Checked
C8	C2 and supplied no-4-AP premise	Checked
C9	C8 and exhaustive 2
10
-case recursion	Checked
C10	C2	Checked inductively with canonical selection
C11	Proper-cube definition	Checked
C12	Properness and finite-difference calculus	Checked
C13	Properness	Checked
C14	Direct arithmetic	Checked
6. Open-gap ledger
G1. Semantic ruling

A unique answer to the immutable text requires conventions for distinctness, positivity, generator domains, properness, and the meaning of “large.”

G2. Uniform linked-factor-chain problem

For each fixed W, determine whether there is a bound B(W) on systems

D+e
i
	​

=h
i
	​

p
i
	​

,p
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

,0≤e
i
	​

≤W,

with the required parity and positivity conditions.

A negative answer needs one fixed W and explicit arbitrarily long chains. A positive uniform bound would disprove the first intended assertion.

G3. Large-phase termination

C6 reduces the large phase to decrement descent and halving. The missing proposition is a scale-independent bound on all alternating combinations of those two mechanisms.

G4. Height-independent cube dimension bound

C11–C13 must be strengthened into a contradiction depending only on dimension, not on the sizes of a,b
i
	​

.

G5. Cube dimension lifting

The positive alternative requires a construction which, from an r-cube H, produces B such that

H∪(H+B)

is a proper square (r+1)-cube.

7. Adversarial referee pass

The literal affirmative constructions do not answer the proper interpretations; they are used only to certify ambiguity.

C2 requires strict increase. Without it, the normalization still describes gap diameter, but gaps need not be positive and the subsequent factor formulation changes.

C3 corrects an omitted boundary condition in the scout material:

p
i
	​

=h
i
	​


is possible on an edge beginning at 0
2
.

C6 applies only when three consecutive root gaps strictly decrease. It cannot be used across plateaus or increases without first invoking C4.

The inference in C6 uses

rs
r+s
	​

≤2,

not the reversed inequality appearing in one scout derivation.

C7 bounds only the tail after a root gap reaches 
W
	​

; it does not bound the initial decreasing phase.

C9 uses the supplied no-four-square-AP statement and a complete finite binary enumeration. It proves only W≤1, not all fixed widths.

C10 needs canonical selection inside repeated blocks. Mere existence of unrelated cubes in two identical blocks would be insufficient. The canonical rule repairs this.

C11’s sharp modulo-4 conclusion is “all but at most one,” not “all but at most two.”

C12 uses properness critically: without distinct vertices, the curvature spectrum need not contain 2
r−∣T∣
 distinct values.

C12–C13 prove rapid growth but supply no upper bound. Treating growth alone as nonexistence would be invalid.

The explicit 3-cube defeats any proposed proof using only one or two-dimensional face impossibility.

The last surviving point is therefore not a hidden algebraic omission but the absence of a scale-independent termination or dimension argument.

<result> OUTCOME: RESOURCE_EXHAUSTED COMPLETENESS_SCORE: 72 PROOF_CONFIDENCE: 95 ADVERSARIAL_SURVIVAL_SCORE: 92 OPEN_GAPS: Resolve the semantic nondegeneracy conventions; For each fixed W prove a uniform linked-factor-chain bound or construct arbitrarily long chains for one W; Prove a height-independent bound on dimensions of proper square cubes or construct proper cubes in every dimension UNCHECKED_IMPORTS: NONE CLAIMS_CHECKED: 14 CLAIMS_TOTAL: 14 CLAIM_IDS: C1;C2;C3;C4;C5;C6;C7;C8;C9;C10;C11;C12;C13;C14 </result>
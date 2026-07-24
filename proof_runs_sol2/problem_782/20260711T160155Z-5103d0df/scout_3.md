Status

I do not obtain a proof or disproof of either intended question. I do obtain exact reductions, a proof of the stated implication between them, several necessary conditions, and exhaustive finite searches.

There is also a genuine blocking defect: the immutable wording does not uniquely specify either proposition.

Literal degeneracies

For the first question, neither distinctness nor d>0 is stated. Thus, under a literal permissive reading,

x
1
	​

=⋯=x
k
	​

=1,d=0

works for every k and every C>0.

For the second question, the following are unspecified:

the number of indices i;

whether a,b
i
	​

 are integers;

whether b
i
	​

>0;

whether all 2
r
 subset sums must be distinct;

whether “arbitrarily large” means unbounded dimension or unbounded cardinality;

whether 0 counts as a square.

If zero directions are allowed, then a=1 and b
i
	​

=0 gives a syntactic cube of every dimension, but the displayed set is only {1}.

Thus these trivializations demonstrate ambiguity rather than resolve the intended questions.

1. Natural precise versions

I used the following standard repairs solely for the attacks below.

Quasi-progression version Q
L
	​


Does there exist an integer L≥0 such that for every k≥1 there are

0≤n
1
	​

<n
2
	​

<⋯<n
k
	​


for which, writing

g
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

,

one has

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

≤L?

This exactly absorbs the real constants in the original inequalities. Indeed, integer gaps g
i
	​

 lie in some real interval of length C exactly when

maxg
i
	​

−ming
i
	​

≤⌊C⌋.

Conversely, choose d=ming
i
	​

. Thus only L=⌊C⌋ matters.

The fact supplied in the prompt about four squares in arithmetic progression excludes L=0 under this interpretation.

Proper square-cube version H
r
	​


For every r, do there exist integers

a≥0,b
1
	​

,…,b
r
	​

>0

such that all 2
r
 numbers

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

,ϵ
i
	​

∈{0,1},

are distinct perfect squares?

Everything below that concerns “cubes” uses this proper version.

2. Exact quasi-progression formulations

Let

D=
i
min
	​

g
i
	​

,g
i
	​

=D+e
i
	​

,

where

e
i
	​

∈{0,1,…,L},
i
min
	​

e
i
	​

=0.
2.1 Fixed error-word formulation

Once the finite word e
1
	​

,…,e
k−1
	​

 is fixed, all later squares are determined algebraically by the first two roots.

Since

D=n
2
2
	​

−n
1
2
	​

−e
1
	​

,

for j≥2,

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

+
t=1
∑
j−1
	​

e
t
	​

−(j−1)e
1
	​

.
	​


Therefore, for fixed L,k, the problem is a finite collection of simultaneous Diophantine problems: there are at most

(L+1)
k−1

error words, and each asks whether k−2 explicit binary quadratic forms can simultaneously be squares.

This is exact, but it does not itself control the heights of possible solutions.

2.2 Factor-pair dynamics

Define

q
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

g
i
	​

=q
i
	​

p
i
	​

,

with

p
i
	​

>q
i
	​

>0,p
i
	​

≡q
i
	​

(mod2),

and consecutive factor pairs obey

p
i+1
	​

=p
i
	​

+q
i
	​

+q
i+1
	​

.
	​


Conversely, positive integer factor pairs satisfying these parity conditions and this recurrence reconstruct the roots through

n
i
	​

=
2
p
i
	​

−q
i
	​

	​

.

Thus Q
L
	​

 is equivalent to finding arbitrarily long paths of linked factor pairs for which all products q
i
	​

p
i
	​

 lie in one interval of L+1 consecutive integers.

2.3 Root-step monotonicity

Write n=n
i
	​

, q=q
i
	​

, and q
′
=q
i+1
	​

. Then

g
i+1
	​

−g
i
	​

=2n(q
′
−q)+2qq
′
+q
′2
−q
2
.

If q
′
=q+s with s≥0, then

g
i+1
	​

−g
i
	​

=2ns+2q
2
+4qs+s
2
.
	​


Consequences:

If q
i+1
	​

≥q
i
	​

, then

2q
i
2
	​

≤L.

Hence any step size exceeding 
L/2
	​

 must strictly decrease at the next step.

If q
i+1
	​

>q
i
	​

, then

g
i+1
	​

−g
i
	​

>2n
i
	​

.

Hence, once n
i
	​

>L/2, the sequence q
i
	​

 can never increase.

A consecutive run with constant value q
i
	​

=q has successive square gaps differing by exactly 2q
2
. Therefore such a run contains at most

⌊
2q
2
L
	​

⌋+1

gaps.

So after a bounded initial region, the root increments form a nonincreasing sequence with uniformly bounded plateaus.

This does not finish the problem: q
1
	​

 is unbounded, so an arbitrarily long strictly decreasing portion has not been excluded.

2.4 Exact constraint on a decrease

If

q
i+1
	​

=q
i
	​

−r,r>0,

then

g
i+1
	​

−g
i
	​

=2q
i
2
	​

−2r(n
i
	​

+2q
i
	​

)+r
2
.
	​


Consequently,

	​

2q
i
2
	​

−2r(n
i
	​

+2q
i
	​

)+r
2
	​

≤L.

For fixed L,q
i
	​

,r, this confines n
i
	​

 to an interval of length

r
L
	​

.

This gives a sparse exact transition algorithm and suggests that a successful negative proof might come from a descent on these transitions. I did not find such a descent.

2.5 Constraints on every block

For every t≥1,

n
i+t
2
	​

−n
i
2
	​

=
j=i
∑
i+t−1
	​

g
j
	​

,

so

tD≤n
i+t
2
	​

−n
i
2
	​

≤t(D+L).

Writing

Q
i,t
	​

=n
i+t
	​

−n
i
	​

,P
i,t
	​

=n
i+t
	​

+n
i
	​

,

gives

Q
i,t
	​

P
i,t
	​

∈[tD,tD+tL].

Thus not only the individual gaps, but every consecutive block sum, must be representable as a difference of two squares inside a short interval around a multiple of D.

3. An elementary proof that quasi-progressions imply cubes

This proves the implication asserted in the supplied text, under the natural proper interpretations above.

Affine-prefix-cube lemma

Fix L,r≥0. There exists N
r
	​

(L) such that every integer sequence

E(0),E(1),…,E(N
r
	​

−1)

with

0≤E(t+1)−E(t)≤L

contains positive integers h
1
	​

,…,h
r
	​

 and a base a for which all indices

a+
i=1
∑
r
	​

ϵ
i
	​

h
i
	​


are distinct and

E(a+
i
∑
	​

ϵ
i
	​

h
i
	​

)=E(a)+
i
∑
	​

ϵ
i
	​

c
i
	​

	​


for suitable integers c
1
	​

,…,c
r
	​

.

Proof by induction

For r=1, any two consecutive indices work.

Assume the result for r, with block length N
r
	​

. Within a block of N
r
	​

 indices, choose one such r-cube canonically.

Its type consists of:

the ordered directions h
1
	​

,…,h
r
	​

;

the corresponding coefficients c
1
	​

,…,c
r
	​

.

There are only finitely many types, uniformly in E, because

1≤h
i
	​

<N
r
	​

,0≤c
i
	​

≤LN
r
	​

.

For instance, the number of types is at most

T
r
	​

=(N
r
	​

(LN
r
	​

+1))
r
.

Partition a sufficiently long interval into T
r
	​

+1 disjoint blocks of length N
r
	​

. Two selected cubes have the same type. Let their bases be a<b, and put

h
r+1
	​

=b−a.

Because the blocks are disjoint and ordered, h
r+1
	​

 is larger than the span of the earlier cube, so all new subset-sum indices are distinct.

For every old cube offset s,

E(b+s)−E(b)=E(a+s)−E(a)

because the two cubes have the same type. Hence

E(a+h
r+1
	​

+s)−E(a+s)=E(b)−E(a),

independent of s. This supplies the new coefficient

c
r+1
	​

=E(b)−E(a)

and completes the induction.

Application to square quasi-progressions

For a quasi-progression, write

g
j
	​

=D+e
j
	​

,0≤e
j
	​

≤L,

and define

E(t)=
j<t
∑
	​

e
j
	​

.

Then

x
t
	​

=x
0
	​

+tD+E(t).

On the affine index cube supplied by the lemma,

x
a+∑ϵ
i
	​

h
i
	​

	​

=x
a
	​

+
i
∑
	​

ϵ
i
	​

(Dh
i
	​

+c
i
	​

).

Thus the square values form a proper additive cube with directions

b
i
	​

=Dh
i
	​

+c
i
	​

>0.

Therefore:

An affirmative natural answer to the first question implies one to the second.
	​


The proof is elementary and does not use an external combinatorial theorem.

4. Finite quasi-progression search

I used the following exhaustive bounded-root search.

For every n<m≤R, a possible next root p must satisfy

	​

(p
2
−m
2
)−(m
2
−n
2
)
	​

≤L.

Hence it suffices to check

⌈
2m
2
−n
2
−L
	​

⌉≤p≤⌊
2m
2
−n
2
+L
	​

⌋.

A depth-first search on the resulting acyclic graph records the minimum and maximum gap already used and accepts a transition exactly when their difference remains at most L.

For roots at most 1000, the exact maximum lengths were:

L:       0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
max k:   3  4  4  4  5  5  6  7  8  8  9  9 10 11 12 12 13 14 15 15 16

Allowing 0
2
 did not change any of these maximum lengths.

Representative witnesses, given by their roots, are:

(7,15,20,24),g=(176,175,176),

which has width 1;

(1,3,4,5,6),g=(8,7,9,11),

which has width 4;

(1,4,6,7,8,9,10,11,12),

whose gap range is [13,23], of width 10;

and

(1,5,7,9,11,12,13,…,22),

whose gaps are

24,24,32,40,23,25,27,…,43,

of width 20, giving length 16.

Additional searches found:

no width-1 sequence of length 5 with largest root at most 5000;

no width-2 sequence of length 5 with largest root at most 3000;

no width-4 sequence of length 6 with largest root at most 3000.

These are exhaustive bounded statements, not global exclusions.

Width 1, length 5: modular elimination

Normalize the four gaps as

D+e
1
	​

,…,D+e
4
	​

,e
i
	​

∈{0,1},

with both symbols occurring.

Of the 14 nonconstant error words, direct residue enumeration eliminates six:

0011, 0110, 1001, 1100

have no solution modulo 3, and

0101, 1010

have no solution modulo 4.

The eight words surviving all moduli through 100 were

0001, 0010, 0100, 0111, 1000, 1011, 1101, 1110.

Thus small congruences remove almost half the cases, but they do not settle even L=1,k=5.

5. Exact formulations for square cubes

Let

s
ϵ
2
	​

=a+
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

,ϵ∈{0,1}
r
.

Then s
ϵ
2
	​

, as a function on the Boolean cube, is affine. Equivalently, every mixed discrete second derivative vanishes:

s
ϵ
2
	​

+s
ϵ+e
i
	​

+e
j
	​

2
	​

=s
ϵ+e
i
	​

2
	​

+s
ϵ+e
j
	​

2
	​

.
	​


In Fourier terminology, the square of the integer-valued root function has no terms of degree at least two.

For every direction i,

(s
ϵ+e
i
	​

	​

−s
ϵ
	​

)(s
ϵ+e
i
	​

	​

+s
ϵ
	​

)=b
i
	​

,
	​


independently of the other coordinates.

5.1 Strict-concavity obstruction

For fixed b>0, the function

ϕ
b
	​

(t)=
t+b
	​

−
t
	​

=
t+b
	​

+
t
	​

b
	​


is strictly decreasing in t.

Fix a cube direction i. The 2
r−1
 lower vertices

t
ϵ
	​

=a+
j

=i
∑
	​

ϵ
j
	​

b
j
	​


are distinct in a proper cube. Therefore the corresponding root increments

s
ϵ+e
i
	​

	​

−s
ϵ
	​

=ϕ
b
i
	​

	​

(t
ϵ
	​

)

are 2
r−1
 distinct positive integers.

Consequently, at the smallest lower vertex,

s
e
i
	​

	​

−s
0
	​

≥2
r−1
,

and hence

b
i
	​

≥4
r−1
.
	​


Thus the largest cube vertex is at least

r4
r−1
,

apart from the nonnegative base term.

This proves rapid necessary growth, but unbounded size is allowed.

5.2 Divisor obstruction

Each of those 2
r−1
 distinct increments gives a distinct same-parity factorization

b
i
	​

=(s
ϵ+e
i
	​

	​

−s
ϵ
	​

)(s
ϵ+e
i
	​

	​

+s
ϵ
	​

).

If every square is positive, this implies

τ(b
i
	​

)≥2
r
,
	​


where τ is the number of positive divisors.

If a zero lower vertex is permitted, the equal-factor representation can occur once, giving the slightly weaker

τ(b
i
	​

)≥2
r
−1.

Since integers can have arbitrarily many divisors, this is not a contradiction.

5.3 A general modular dimension bound

Let p be an odd prime, and let Q
p
	​

 be the set of square residues modulo p, so

∣Q
p
	​

∣=
2
p+1
	​

.

Process the cube directions one at a time. Let S be the set of residues reached by subset sums of the processed directions. Necessarily

S⊆Q
p
	​

.

If a newly processed direction satisfies b
i
	​


≡0(modp), the new set is

S∪(S+b
i
	​

).

This set is strictly larger than S: otherwise S would be invariant under translation by a nonzero residue, and since Z/pZ is generated by that residue, S would equal every residue modulo p, impossible.

Starting from one residue and remaining inside a set of size (p+1)/2, there can therefore be at most

2
p−1
	​


directions not divisible by p. Hence

#{i:p∤b
i
	​

}≤
2
p−1
	​

.
	​


In particular:

all but at most one b
i
	​

 are divisible by 3;

a direct analogous check modulo 4 shows all but at most one b
i
	​

 are divisible by 4;

consequently, at least r−2 directions are divisible by 12.

For any finite set of odd primes P, at least

r−
p∈P
∑
	​

2
p−1
	​


directions are divisible by ∏
p∈P
	​

p.

This forces extensive divisibility in high dimension, but the directions can grow without bound, so it does not close the argument.

6. Exhaustive square-cube search

I enumerated cubes recursively.

A proper 2-cube consists of four distinct squares

u
0
	​

<u
1
	​

<u
2
	​

<u
3
	​


satisfying

u
0
	​

+u
3
	​

=u
1
	​

+u
2
	​

.

Store it canonically as

(a;b
1
	​

,b
2
	​

),b
1
	​

≤b
2
	​

.

To construct an (r+1)-cube, pair two r-cubes with the same ordered direction tuple and bases a<a
′
. Their union has new direction a
′
−a. Retain it exactly when all 2
r+1
 vertices are distinct squares.

This recursion is exhaustive: every (r+1)-cube has two opposite r-faces with the same remaining directions.

Results

Allowing 0
2
:

there is no proper 3-cube whose largest root is at most 124;

the first largest-root threshold at which one exists is 125;

among roots at most 1000, the enumeration produced
332,755 proper 2-cubes,
78 proper 3-cubes, and
no proper 4-cube.

The smallest-threshold 3-cube found is

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

Its vertices are

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


The absence of a 4-cube through root 1000 is only a finite falsification result.

7. Failed attacks and what they establish
Monotone root increments

The q
i
	​

 become nonincreasing and have bounded plateaus once the roots are moderately large. This looks close to a termination argument, but the initial increment q
1
	​

 can be arbitrarily large. No bound depending only on L emerged.

Congruence automata for quasi-progressions

For fixed L and modulus M, one can make a finite graph on root residues and DmodM. It usually contains trivial cycles because roots may repeat modulo M and D+e may vanish modulo M. Thus ordinary modular path obstruction is too weak unless supplemented by size or valuation information.

Scaling and compactness

After normalizing a hypothetical long chain by 
D
	​

, fixed initial segments approach the real trajectory

y
i
2
	​

=α+i.

That real limiting trajectory exists, so compactness loses precisely the integer obstruction that matters.

Divisor counting for cubes

Every direction must have exponentially many difference-of-square representations. This forces enormous, highly composite directions but gives no contradiction because there is no upper bound on the b
i
	​

.

Modular cube restrictions

High dimension forces most directions to be divisible by any prescribed finite collection of primes. This yields large common divisibility but not an infinite descent: the base square can remain a nonzero quadratic residue modulo those primes.

Dimension counting

The system

s
ϵ
2
	​

=a+∑ϵ
i
	​

b
i
	​


has exponentially many equations, suggesting overdetermination. But algebraic dimension alone does not rule out isolated integer solutions or special structured families.

Random-spacing heuristic

At root scale n, consecutive square spacing is about 2n, so repeatedly landing inside a fixed-width window appears unlikely. The factor-pair recurrence creates strong dependence, making an independence heuristic unusable as proof.

8. Precise remaining targets

The most concrete unresolved obligations are:

Width 1, length 5.
Resolve the eight surviving binary error words by descent, factorization, or complete analysis of their simultaneous quadratic equations. This would not settle the original existential quantifier over all L, but it is the smallest unresolved test case after the finite search.

A symbolic height/descent theorem for Q
L
	​

.
Use

	​

2q
2
−2r(n+2q)+r
2
	​

≤L

to show that every sufficiently long chain admits a smaller chain with the same width. Such a descent would turn bounded computation into a proof of a uniform length bound.

A uniform cube-dimension obstruction.
Strengthen concavity, divisor multiplicity, and simultaneous prime divisibility into an actual upper bound on r. By the affine-prefix-cube lemma, this would also disprove the quasi-progression statement.

A constructive alternative.
Produce, for one fixed L, compatible integer solutions to the fixed-error-word systems for all lengths. Local or numerical solvability is insufficient; the construction must preserve the same L indefinitely.

Under the natural repaired meanings, neither question is resolved here. The exact immutable wording remains formally blocked by its missing distinctness, positivity, domain, and cube-size conventions.
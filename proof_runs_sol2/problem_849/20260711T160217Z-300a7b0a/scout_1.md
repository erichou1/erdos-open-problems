Status

I did not obtain a proof or disproof of the quantified statement. The attacks below are self-contained and establish several exact reductions, an infinite constructive collision family, obstructions to combining those collisions, and an exhaustive verification that no a≤10
18
 has five solutions.

Define

r(a)=#{(n,k)∈Z
2
:1≤k≤
2
n
	​

, (
k
n
	​

)=a}.

The original assertion is

∀t≥1∃a∈Zr(a)=t.

Unboundedness of r(a) would not by itself prove this, because some intermediate integer multiplicities might be omitted.

1. Exact normalization
Boundary cases

Within the permitted region,

n≥2,(
k
n
	​

)≥(
1
2
	​

)=2.

Hence

r(a)=0(a≤1).

For every a≥2,

(
1
a
	​

)=a,

and (a,1) satisfies 1≤1≤a/2. Therefore every positive-multiplicity value has the automatic representation

(a,1).

Consequently,

r(a)=1+#{k≥2:∃n≥2k, (
k
n
	​

)=a}(a≥2).
At most one row for each lower index

For fixed k,

(
k
n
	​

)
(
k
n+1
	​

)
	​

=
n+1−k
n+1
	​

>1.

Thus n↦(
k
n
	​

) is strictly increasing. For any fixed a and k, there is at most one possible n.

So multiplicity is exactly the number of distinct lower indices k representing a.

Ordering of representations

Suppose

(
k
n
	​

)=(
ℓ
m
	​

),k<ℓ.

Then necessarily n>m. Indeed, if n≤m, then

(
k
n
	​

)≤(
k
m
	​

)<(
ℓ
m
	​

),

because the entries in the left half of a fixed row strictly increase with k.

Thus, after ordering all representations by lower index,

1=k
1
	​

<k
2
	​

<⋯<k
r(a)
	​

,

the corresponding row indices satisfy

a=n
1
	​

>n
2
	​

>⋯>n
r(a)
	​

.

Every candidate is therefore a strictly decreasing lattice chain in n and a strictly increasing chain in k.

Finiteness and a lower bound for any witness

Since n≥2k,

a=(
k
n
	​

)≥(
k
2k
	​

).

Also,

(
k
2k
	​

)=
j=1
∏
k
	​

j
k+j
	​

≥2
k
.

Hence every representation satisfies

k≤log
2
	​

a,

so r(a) is always finite.

If r(a)=t, then the largest of t distinct positive lower indices is at least t. Therefore

a≥(
t
2t
	​

)
	​

.

This is necessary but far too weak to settle the problem.

2. Exact verification of multiplicities 1,2,3,4

The first four multiplicities can be certified without relying on a search.

t=1

Take a=2. The representation (2,1) exists. For k≥2,

(
k
n
	​

)≥(
2
4
	​

)=6>2.

Thus r(2)=1.

t=2

Take a=10. Its representations are

(
1
10
	​

)=10,(
2
5
	​

)=10.

For k≥3,

(
k
n
	​

)≥(
3
6
	​

)=20>10.

Thus r(10)=2.

t=3

For a=120,

(
1
120
	​

)=(
2
16
	​

)=(
3
10
	​

)=120.

There is no k=4 representation because

(
4
8
	​

)=70<120<126=(
4
9
	​

).

For k≥5,

(
k
n
	​

)≥(
5
10
	​

)=252>120.

Thus

r(120)=3.
t=4

For a=3003,

(
1
3003
	​

)=(
2
78
	​

)=(
5
15
	​

)=(
6
14
	​

)=3003.

The omitted lower indices are excluded as follows:

(
3
27
	​

)=2925<3003<3276=(
3
28
	​

),

and

(
4
17
	​

)=2380<3003<3060=(
4
18
	​

).

For k≥7,

(
k
n
	​

)≥(
7
14
	​

)=3432>3003.

Hence

r(3003)=4.
3. A constructive infinite collision family

A natural way to obtain two nontrivial representations is to seek

(
k
n
	​

)=(
k+1
n−1
	​

).

The quotient is

(
k+1
n−1
	​

)
(
k
n
	​

)
	​

=
(n−k)(n−k−1)
n(k+1)
	​

.

Therefore equality is equivalent to

n(k+1)=(n−k)(n−k−1).

As a quadratic equation in n,

n
2
−(3k+2)n+k(k+1)=0.

Its discriminant must be a square:

y
2
=5k
2
+8k+4.

Putting

x=5k+4

turns this into

x
2
−5y
2
=−4
	​

.

The solution x=29,y=13 gives k=5 and

n=
2
3k+2+y
	​

=15,

recovering

(
5
15
	​

)=(
6
14
	​

)=3003.
An explicit recurrence

Starting from any positive solution, define

x
′
=
2
7x+15y
	​

,y
′
=
2
3x+7y
	​

.

Direct expansion gives

x
′
2
−5y
′
2
=x
2
−5y
2
.

Moreover,

2x
′
≡2x(mod5),

so x
′
≡x≡4(mod5). Hence

k
′
=
5
x
′
−4
	​


is again an integer. Positivity shows x
′
>x, so this produces infinitely many distinct solutions.

The first few resulting collision blocks are

(
5
15
	​

)
(
39
104
	​

)
(
272
714
	​

)
(
1869
4895
	​

)
	​

=(
6
14
	​

),
=(
40
103
	​

),
=(
273
713
	​

),
=(
1870
4894
	​

).
	​


Each common value has at least three representations after including the automatic k=1 representation.

This does not certify that the later values have exactly three representations: they might possess additional, unrelated representations.

4. Why the collision gadget does not readily yield t=5
No three-term unit-diagonal block

Suppose one tries to chain the preceding construction:

(
k
n
	​

)=(
k+1
n−1
	​

)=(
k+2
n−2
	​

).

Set q=n−k. The first equality gives

q(q−1)=(q+k)(k+1).

The second gives

(q−2)(q−3)=(q+k−1)(k+2).

After expansion, these become

q
2
−kq−2q−k
2
−k=0

and

q
2
−kq−7q−k
2
−k+8=0.

Subtracting yields

8−5q=0,

which is impossible for integral q.

Therefore

(
k
n
	​

)=(
k+1
n−1
	​

)=(
k+2
n−2
	​

) has no admissible integer solution.
	​


The simplest attempt to extend a two-vertex collision block to three vertices fails absolutely.

Two separate unit-diagonal blocks cannot share a value

For a given k, the admissible root is

n(k)=
2
3k+2+
5k
2
+8k+4
	​

	​

.

This is strictly increasing with k. If k<ℓ are two lower indices producing unit-diagonal collision blocks, then

n(k)<n(ℓ).

Since both coordinates increase,

(
k
n(k)
	​

)<(
ℓ
n(ℓ)
	​

).

Thus two distinct blocks of the form

(
k
n
	​

)=(
k+1
n−1
	​

)

can never have the same common value.

So the tempting construction

1 automatic representation+2 representations from one block+2 from another block=5

is impossible.

The remaining Pell-based target

To reach five representations using one such block, one would need two further unrelated representations. A particularly concrete target is to solve simultaneously

⎩
⎨
⎧
	​

(
k
n
	​

)=(
k+1
n−1
	​

),
8(
k
n
	​

)+1=s
2
,
(
ℓ
m
	​

)=(
k
n
	​

),
	​


where

ℓ∈
/
{1,2,k,k+1}.

The square condition supplies the k=2 representation. The initial Pell solution gives 3003, satisfying the square condition, but the direct check above excludes the final extra representation.

No mechanism was found to force the third equation.

5. Exact finite falsification through 10
18

The following search is exhaustive for every a≤A, not merely row-bounded.

For k≥3 and k≤n/2,

(
k
n
	​

)≥(
3
n
	​

).

Therefore, when a≤10
18
,

(
3
n
	​

)≤10
18
,

which forces

n≤1817121.

For each such n, the coefficients increase with k through the left half, so enumeration can stop as soon as the coefficient exceeds 10
18
. A k=2 representation is detected exactly by

a=(
2
m
	​

)⟺8a+1=(2m−1)
2
.

The core exact-integer enumeration is:

Python
Run
from collections import defaultdict
from math import comb, isqrt

A = 10**18
N = 1_817_121

reps = defaultdict(list)

for n in range(6, N + 1):
    k = 3
    c = comb(n, 3)

    while k <= n // 2 and c <= A:
        reps[c].append((n, k))
        c = c * (n - k) // (k + 1)
        k += 1

answer = []

for a, nontrivial in reps.items():
    rr = list(nontrivial)

    s = isqrt(8 * a + 1)
    if s * s == 8 * a + 1:
        rr.append(((s + 1) // 2, 2))

    multiplicity = 1 + len(rr)  # automatic (a, 1)

    if multiplicity >= 3:
        answer.append((a, multiplicity, sorted(rr)))

The complete output with multiplicity at least three is:

a
120
210
1540
3003
7140
11628
24310
	​

r(a)
3
3
3
4
3
3
3
	​

non-k=1 representations
(16,2),(10,3)
(21,2),(10,4)
(56,2),(22,3)
(78,2),(15,5),(14,6)
(120,2),(36,3)
(153,2),(19,5)
(221,2),(17,8)
	​

	​


Consequently, the exact finite statement proved by this computation is

a≤10
18
⟹r(a)≤4.
	​


In particular, any witness for t=5 must satisfy

a>10
18
.

This does not supply a global upper bound.

6. Analytic inverse formulation

For a representation (
k
n
	​

)=a,

(
k
n
	​

)=
k!
n(n−1)⋯(n−k+1)
	​

.

Since each numerator factor lies between n−k+1 and n,

k!
(n−k+1)
k
	​

≤a≤
k!
n
k
	​

.

Define

X
k
	​

(a)=(ak!)
1/k
.

Then every representation must satisfy

X
k
	​

(a)≤n≤X
k
	​

(a)+k−1.
	​


Thus the original question can be viewed as asking whether, for every t, some a makes the exact binomial equation hit an integer in at least t−1 of these correlated inverse windows, with no additional hits.

The obstruction is that the windows for different k involve incompatible fractional powers of the same integer a. The inequalities locate possible rows but provide no control over simultaneous exact integrality.

7. Arithmetic invariants

From

k(
k
n
	​

)=n(
k−1
n−1
	​

)

and (
k
n
	​

)=a, one obtains

n∣ka.

Therefore

gcd(n,k)
n
	​

∣a.
	​


For several nontrivial representations (n
i
	​

,k
i
	​

), this gives

lcm
i
	​

(
gcd(n
i
	​

,k
i
	​

)
n
i
	​

	​

)∣a.

This can force a to be large, but no argument was found showing that five such divisors are incompatible.

For every prime p, the factorial valuation formula gives the stronger exact condition

v
p
	​

(a)=
j≥1
∑
	​

(⌊
p
j
n
	​

⌋−⌊
p
j
k
	​

⌋−⌊
p
j
n−k
	​

⌋).

All representations of the same a must have the same valuation profile for every prime. This is a potentially strong digital invariant, but I found no uniform argument bounding the number of pairs with a common profile.

8. Extremal and double-counting attack

Let I(A) be the number of nontrivial incidences

I(A)=#{(n,k):2≤k≤n/2, (
k
n
	​

)≤A}.

Because

(
k
n
	​

)≥(
2
n
	​

),

we have

n<
2A
	​

+1.

Also k≤log
2
	​

A. Hence the crude but uniform estimate

I(A)≤(
2A
	​

+1)⌊log
2
	​

A⌋.

Let

E
t
	​

(A)=#{a≤A:r(a)≥t}.

Every such value contributes at least t−1 nontrivial incidences, so

E
t
	​

(A)≤
t−1
(
2A
	​

+1)log
2
	​

A
	​

.
	​


Thus values with any fixed multiplicity at least t≥2 have density zero among the integers.

This is only an average statement. It does not exclude a sparse sequence of values with arbitrarily large multiplicity.

9. Set-system formulation

For k≥2, define

B
k
	​

={(
k
n
	​

):n≥2k}.

Then

r(a)=1+#{k≥2:a∈B
k
	​

}.

The problem is therefore exactly the degree-spectrum problem for the family

{B
2
	​

,B
3
	​

,B
4
	​

,…}:

does some integer have every prescribed finite incidence degree?

This formulation isolates the missing structural issue. Pairwise intersections such as B
k
	​

∩B
ℓ
	​

 are not enough; a positive solution requires arbitrarily high-order intersections, while a negative solution requires proving that sufficiently high-order intersections are empty or that some exact degree is skipped.

10. Precise remaining targets

A full negative resolution would follow from the stronger statement

r(a)≤4for every a.

A weaker but sufficient negative target is merely

r(a)

=5for every a.

A positive resolution needs substantially more than unboundedness. One must construct, for every t, indices

1=κ
1
	​

<κ
2
	​

<⋯<κ
t
	​


and rows

a=n
1
	​

>n
2
	​

>⋯>n
t
	​

≥2κ
t
	​


such that

(
κ
i
	​

n
i
	​

	​

)=a

for all i, and then exclude every other k. The bound k≤log
2
	​

a makes this final exclusion finite once a candidate is available.

For t=5, a minimal candidate must contain four nontrivial representations. The proved collision obstructions imply:

it cannot obtain four nontrivial representations from two unit-diagonal Pell blocks;

it cannot contain a three-term unit-diagonal chain;

if it contains one unit-diagonal block, its other two nontrivial representations must arise from genuinely different equations.

That is the narrowest concrete remaining construction target found here.

Failure ledger

Pascal-recursion chaining: fails because the recursion gives sums rather than equal coefficients, and the most natural three-term diagonal equality is impossible.

Pell collision family: succeeds in producing infinitely many values with at least three representations, but cannot be combined with a second such block and does not control unrelated extra representations.

Triangular augmentation: succeeds at 3003, turning one collision block into multiplicity four, but no method forces an additional representation.

Inverse asymptotics: localizes each possible row to a short interval but does not force simultaneous exact hits.

Divisibility and p-adic invariants: give exact necessary conditions but no uniform incompatibility for five representations.

Double counting: proves extreme multiplicities are sparse but cannot rule out isolated examples.

Minimal-counterexample reasoning: no monotone operation on a or on representations was found. In particular, a value with many representations cannot currently be transformed into one with exactly one fewer representation.

Finite computation: rules out t≥5 only through a=10
18
; it supplies no finite global search bound.

Accordingly, the exact original quantifiers remain unresolved by these attacks.
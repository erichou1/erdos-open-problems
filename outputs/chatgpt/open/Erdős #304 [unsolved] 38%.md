# Erdős Problem #304 [unsolved] 38%

---

## ChatGPT Response

Formal statement

For integers b≥2 and 1≤a<b, define

N(a,b)=min{k≥1:∃1<n
1
	​

<⋯<n
k
	​

, 
b
a
	​

=
i=1
∑
k
	​

n
i
	​

1
	​

}.

Then

N(b)=
1≤a<b
max
	​

N(a,b).

The proposed upper bound is:

∃C>0,∃b
0
	​

,∀b≥b
0
	​

,∀a∈{1,…,b−1},N(a,b)≤Cloglogb.

Its negation is:

∀C>0,∀b
0
	​

,∃b≥b
0
	​

,∃a∈{1,…,b−1},N(a,b)>Cloglogb.

The strongest fully verified result I can derive here is the lower bound

N(b)≥(1−o(1))log
2
	​

logb.

I cannot prove or disprove the matching upper bound N(b)≪loglogb from first principles in this session.

Basic equivalent formulation

If

b
a
	​

=
i=1
∑
k
	​

n
i
	​

1
	​

,

and L=lcm(n
1
	​

,…,n
k
	​

), then

b
aL
	​

=
i=1
∑
k
	​

n
i
	​

L
	​

.

Thus, after passing to a common denominator, the problem becomes:

Find a common multiple L of the reduced denominator of a/b, and represent the integer aL/b as a sum of distinct proper divisors of L.

Conversely, if L is such that aL/b∈Z, and if

b
aL
	​

=d
1
	​

+⋯+d
k
	​


with distinct proper divisors d
i
	​

∣L, then setting n
i
	​

=L/d
i
	​

 gives

b
a
	​

=
i=1
∑
k
	​

n
i
	​

1
	​

.

So the desired upper bound is equivalent to a sparse divisor-subset representation statement.

Lemma 1: N(a,b) is finite

Let 0<a<b. Choose

n=⌈
a
b
	​

⌉.

Then

0≤
b
a
	​

−
n
1
	​

=
bn
an−b
	​

.

If an=b, then 
b
a
	​

=1/n and we are done.

Otherwise 0<an−b<a, because n<b/a+1. Thus the numerator strictly decreases. Repeating this greedy step eventually reaches numerator 1, and the denominators strictly increase, so the unit fractions are distinct.

Therefore

N(a,b)≤a≤b−1.

This gives only the trivial upper bound

N(b)≤b−1.
Lemma 2: denominator bound for decompositions of 1

Suppose

1=
x
1
	​

1
	​

+⋯+
x
m
	​

1
	​

,

where

2≤x
1
	​

≤x
2
	​

≤⋯≤x
m
	​


are integers, not necessarily distinct.

Define

P
j
	​

=x
1
	​

x
2
	​

⋯x
j
	​

.

Since

x
1
	​

1
	​

+⋯+
x
j
	​

1
	​


has denominator dividing P
j
	​

, the positive remainder

R
j
	​

=1−
i=1
∑
j
	​

x
i
	​

1
	​


is either 0, or at least 1/P
j
	​

.

For j<m, R
j
	​

>0, so

R
j
	​

≥
P
j
	​

1
	​

.

But also

R
j
	​

=
i=j+1
∑
m
	​

x
i
	​

1
	​

≤
x
j+1
	​

m−j
	​

.

Hence

P
j
	​

1
	​

≤
x
j+1
	​

m−j
	​

,

so

x
j+1
	​

≤(m−j)P
j
	​

≤mP
j
	​

.

Also x
1
	​

≤m, since otherwise

1=
i=1
∑
m
	​

x
i
	​

1
	​

<m⋅
m
1
	​

=1.

Thus

P
1
	​

≤m,

and inductively

P
j+1
	​

=P
j
	​

x
j+1
	​

≤mP
j
2
	​

.

Therefore

P
j
	​

≤m
2
j
−1
.

In particular every denominator in a length-m decomposition of 1 satisfies

x
i
	​

≤m
2
m
−1
.
Corollary: lower bound for N(b)

Take a=b−1. Suppose

b
b−1
	​

=
n
1
	​

1
	​

+⋯+
n
k
	​

1
	​

.

Then adjoining 1/b gives

1=
b
1
	​

+
n
1
	​

1
	​

+⋯+
n
k
	​

1
	​

.

This is a decomposition of 1 into m=k+1 unit fractions, allowing repetitions.

By Lemma 2,

b≤m
2
m
−1
.

Taking logarithms,

logb≤(2
m
−1)logm.

Therefore

m≥(1−o(1))log
2
	​

logb.

Since m=k+1,

N(b)≥N(b−1,b)≥(1−o(1))log
2
	​

logb.

So the lower-order estimate

N(b)≫loglogb

is proved from first principles.

Search for the matching upper bound

The desired statement is:

N(b)≪loglogb.

Using the divisor formulation, it would follow from the following strong sparse-divisor principle:

For every 1≤a<b, there exists an integer L with b∣L such that aL/b is a sum of O(loglogb) distinct proper divisors of L.

I attacked this through three main branches.

Branch A: divisor-subset construction

Goal: choose L so that aL/b has a very short representation as a sum of divisors of L.

Verified reduction:

b
a
	​

=
i=1
∑
k
	​

n
i
	​

1
	​

⟺
b
aL
	​

=
i=1
∑
k
	​

d
i
	​

,d
i
	​

∣L, d
i
	​

<L.

Obstacle: choosing L freely gives many divisors, but forcing the specific target aL/b to be a short divisor-subset sum is nontrivial. Binary representation gives O(logb) terms, not O(loglogb), unless the available divisor weights grow extremely rapidly in a way adapted to a and b.

Unresolved gap:

Sparse divisor-subset completion lemma
	​


No proof obtained.

Branch B: complement via decompositions of 1

For a=b−1, the problem becomes equivalent in one direction to finding short decompositions of 1 containing 1/b. Lemma 2 shows that any such decomposition must have length at least ≍loglogb.

To prove the upper bound even for a=b−1, one would need:

For every b, there exists a decomposition

1=
b
1
	​

+
x
1
	​

1
	​

+⋯+
x
k
	​

1
	​


with k≪loglogb, and with the remaining denominators distinct.

The lower-bound lemma shows that loglogb is the correct possible scale, but it does not construct such decompositions.

Unresolved gap:

Every b occurs in a length O(loglogb) decomposition of 1.
	​


No proof obtained.

Branch C: accelerated greedy descent

The ordinary greedy algorithm reduces the numerator strictly:

b
a
	​

−
⌈b/a⌉
1
	​

=
b
′
a
′
	​

,0≤a
′
<a.

This proves finiteness, but not a logarithmic bound.

A possible route would be to prove that at each step one can choose a unit fraction so that the reduced numerator shrinks by a fixed factor:

a
′
≤θa,θ<1.

Then after O(logb) steps the numerator reaches 1. To reach O(loglogb), one would need much faster collapse, roughly

a
′
≤a
θ

or a comparable multiplicative structure.

Obstacle: the numerator after subtracting 1/n is

an−b,

after reduction by

gcd(an−b,bn).

The available cancellation depends on congruences between n and b. I found no argument forcing enough cancellation uniformly for all a,b.

Unresolved gap:

Uniform accelerated numerator-reduction lemma
	​


No proof obtained.

Verified conclusions

The following are rigorously established here:

N(a,b)<∞.
N(b)≤b−1.
N(b)≥N(b−1,b)≥(1−o(1))log
2
	​

logb.

Thus the lower bound

N(b)≫loglogb

is proved.

The proposed matching upper bound

N(b)≪loglogb

was not proved or disproved.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94/100
COMPLETENESS_SCORE: 38/100
ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE: approximately 100% of the useful reasoning budget for this response; 3 main branches explored; 4 verified lemmas/corollaries generated; 3 major upper-bound proof attempts failed.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

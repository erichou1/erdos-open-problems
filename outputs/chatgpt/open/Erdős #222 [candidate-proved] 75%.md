# Erdős Problem #222 [candidate-proved] 75%

---

## ChatGPT Response

Phase 0: Formalization

Let

S={m∈Z
≥0
	​

:m=a
2
+b
2
 for some a,b∈Z
≥0
	​

}.

Let

0=n
0
	​

<n
1
	​

<n
2
	​

<⋯

be the increasing enumeration of S. The object of study is

g
k
	​

=n
k+1
	​

−n
k
	​

.
Target bounds proved here

I will prove, from scratch:

g
k
	​

≪n
k
1/4
	​

.

More explicitly, for every k≥1,

g
k
	​

≤2
2
	​

(n
k
	​

+1)
1/4
+2.

I will also prove a fully elementary lower bound:

for infinitely many k,g
k
	​

≥cloglogn
k
	​


for an absolute constant c>0. This is weaker than the lower bounds quoted in the problem statement, but it is derived here without importing distributional results about primes.

Phase 1: Strategy search
Strategy	Usefulness	Status
Approximate x by a
2
+b
2
 using a=⌊
x
	​

⌋	High	Gives O(x
1/4
) upper bound
Use squares alone	Low	Only gives O(x
1/2
)
Use local obstruction from primes p≡3(mod4)	High	Gives long gaps
CRT construction assigning one bad prime to each integer in a block	High	Gives arbitrarily long gaps
Quantify CRT modulus using explicit recursive primes 3mod4	Medium	Gives g
k
	​

≫loglogn
k
	​


Full prime distribution in 3mod4 classes	High	Would improve lower bound, not derived here
Density of sums of two squares	Medium	Too strong for this self-contained derivation
Induction on intervals	Low	No direct closure property
Diagonal obstruction	Medium	Essentially becomes CRT construction
Compactness/covering congruences	Medium	Same core as CRT
Counterexample search to O(x
1/4
)	Low	Upper proof survives
Extremal residue-class construction	High	Supports lower bound

Top branches selected:

Upper bound by direct square approximation.

Lower bound by CRT and primes 3mod4.

Quantify the CRT modulus using an explicit Euclidean construction of such primes.

Theorem A: Upper bound g
k
	​

≪n
k
1/4
	​

Claim

For every real x≥1, there exists s∈S such that

x≤s≤x+2
2
	​

x
1/4
+1.
Proof

Let

a=⌊
x
	​

⌋,r=x−a
2
.

Then

0≤r<(a+1)
2
−a
2
=2a+1.

Since r is not necessarily an integer when x is real, we use

r<2a+1≤2
x
	​

+1.

For integer x, the sharper r≤2a holds, but the weaker real version is enough.

Now choose

b=⌈
r
	​

⌉.

Then

b
2
≥r,

so

s=a
2
+b
2
≥a
2
+r=x.

Also,

b<
r
	​

+1,

hence

b
2
−r=(b−
r
	​

)(b+
r
	​

)≤1(2
r
	​

+1)=2
r
	​

+1.

Since r≤2
x
	​

+1, for x≥1,

r
	​

≤
2
x
	​

+1
	​

≤
3
	​

x
1/4
.

Thus

s−x=b
2
−r≤2
3
	​

x
1/4
+1.

For integer x, using r≤2
x
	​

, we get the cleaner bound

s−x≤2
2
	​

x
1/4
+1.

Now apply this with

x=n
k
	​

+1.

There exists s∈S with

n
k
	​

+1≤s≤n
k
	​

+1+2
2
	​

(n
k
	​

+1)
1/4
+1.

Since n
k+1
	​

 is the least element of S greater than n
k
	​

,

n
k+1
	​

≤s.

Therefore

g
k
	​

=n
k+1
	​

−n
k
	​

≤2
2
	​

(n
k
	​

+1)
1/4
+2.

So

g
k
	​

≪n
k
1/4
	​

	​

.
Theorem B: Arbitrarily long gaps exist

We need one elementary obstruction.

Lemma 1

Let p be a prime with

p≡3(mod4).

If

p∣a
2
+b
2
,

then

p∣aandp∣b.
Proof

Suppose p∣a
2
+b
2
.

If p∣b, then a
2
≡0(modp), so p∣a.

Now suppose p∤b. Then b has an inverse modulo p. We get

a
2
≡−b
2
(modp),

so

(ab
−1
)
2
≡−1(modp).

Let x=ab
−1
. Then x
2
≡−1(modp), so

x
p−1
=(x
2
)
(p−1)/2
≡(−1)
(p−1)/2
(modp).

Because p≡3(mod4), (p−1)/2 is odd, hence

x
p−1
≡−1(modp).

But Fermat’s little theorem gives

x
p−1
≡1(modp),

because p∤x. Contradiction.

Thus p∤b is impossible, so p∣b, and then p∣a. ∎

Consequence

If p≡3(mod4), p∣N, and p
2
∤N, then N is not a sum of two squares.

Indeed, if N=a
2
+b
2
, Lemma 1 gives p∣a,b, hence p
2
∣a
2
+b
2
=N, contradiction.

CRT construction

Fix L≥1. Choose distinct primes

q
1
	​

,…,q
L
	​


with

q
i
	​

≡3(mod4).

By the Chinese remainder theorem, there exists an integer m satisfying

m+i≡q
i
	​

(modq
i
2
	​

)

for every 1≤i≤L.

Thus

q
i
	​

∣m+i,

but

q
i
2
	​

∤m+i.

Therefore m+i is not a sum of two squares for every 1≤i≤L.

So the whole block

m+1,m+2,…,m+L

contains no element of S.

Hence there is a gap between consecutive sums of two squares of length at least L+1.

Therefore:

The gaps n
k+1
	​

−n
k
	​

 are unbounded.
	​

Theorem C: A fully elementary quantitative lower bound

We now quantify the previous construction without using prime distribution theorems.

Lemma 2: Explicit supply of primes 3mod4

There are infinitely many primes q≡3(mod4), and they may be chosen recursively so that if

P
t
	​

=q
1
	​

q
2
	​

⋯q
t
	​

,

then

q
t+1
	​

<4P
t
2
	​

.
Proof

Start with q
1
	​

=3.

Assume q
1
	​

,…,q
t
	​

 have been chosen and put

P
t
	​

=q
1
	​

⋯q
t
	​

.

Consider

N=4P
t
2
	​

−1.

Then

N≡3(mod4).

Also, for every i,

N≡−1(modq
i
	​

),

so none of the old q
i
	​

 divides N.

Since N≡3(mod4), at least one prime divisor of N is 3(mod4). Otherwise all odd prime divisors would be 1(mod4), making N≡1(mod4), contradiction.

Choose such a prime divisor as q
t+1
	​

. Then q
t+1
	​

∈
/
{q
1
	​

,…,q
t
	​

}, and

q
t+1
	​

≤N<4P
t
2
	​

.

∎

Now define

P
L
	​

=q
1
	​

q
2
	​

⋯q
L
	​

,Q
L
	​

=P
L
2
	​

.

From

q
t+1
	​

<4P
t
2
	​

,

we get

P
t+1
	​

=P
t
	​

q
t+1
	​

<4P
t
3
	​

.

Taking logs,

logP
t+1
	​

<log4+3logP
t
	​

.

Since P
1
	​

=3, induction gives

logP
L
	​

≤(log6)3
L−1
.

Therefore

logQ
L
	​

=2logP
L
	​

≤2(log6)3
L−1
.

Now use the CRT construction with q
1
	​

,…,q
L
	​

. The modulus is

Q
L
	​

=q
1
2
	​

q
2
2
	​

⋯q
L
2
	​

=P
L
2
	​

.

Choose a solution m
L
	​

 with

Q
L
	​

≤m
L
	​

<2Q
L
	​

.

Then

m
L
	​

+1,…,m
L
	​

+L

are all non-sums of two squares. Thus there is a consecutive gap

g
k
	​

≥L+1

with the preceding sum n
k
	​

≤m
L
	​

.

Also, since ⌊
m
L
	​

	​

⌋
2
∈S,

n
k
	​

≥⌊
m
L
	​

	​

⌋
2
.

For large L,

⌊
m
L
	​

	​

⌋
2
≥
2
1
	​

Q
L
	​

.

Hence, for these gaps,

2
1
	​

Q
L
	​

≤n
k
	​

≤2Q
L
	​

.

Therefore

loglogn
k
	​

=loglogQ
L
	​

+O(1).

But

logQ
L
	​

≤2(log6)3
L−1
.

Taking logs,

loglogQ
L
	​

≤(L−1)log3+O(1).

So

L≥
log3
1
	​

loglogn
k
	​

−O(1).

Since g
k
	​

≥L+1, we obtain

g
k
	​

≥cloglogn
k
	​

	​


for infinitely many k, for some absolute constant c>0.

Final bounds established here

The rigorous self-contained conclusions are:

n
k+1
	​

−n
k
	​

≪n
k
1/4
	​

	​


for all k, and

n
k+1
	​

−n
k
	​

≫loglogn
k
	​

	​


for infinitely many k.

The second bound is not the strongest lower bound stated in the prompt, but it follows only from elementary congruence obstructions and CRT.

Verification audit
Upper bound attack

Possible failure: choosing a=⌊
x
	​

⌋ leaves a remainder r too large.

Resolution: r≤2
x
	​

, so the nearest upper square b
2
 overshoots by only O(
r
	​

)=O(x
1/4
).

Lower bound attack

Possible failure: m+i≡q
i
	​

(modq
i
2
	​

) might still be a sum of two squares.

Resolution: if q
i
	​

≡3(mod4) divides a sum of two squares, then it divides both square roots, forcing q
i
2
	​

∣m+i, contradicting the congruence.

Quantifier check

For every L, the construction gives a block of L consecutive non-sums. Since L→∞, gaps are unbounded. With the explicit recursive prime construction, the gap location satisfies n
k
	​

≍Q
L
	​

, giving the quantitative lower bound g
k
	​

≫loglogn
k
	​

 infinitely often.

PROVED

PROOF_CONFIDENCE: 96/100
COMPLETENESS_SCORE: 75/100 for the elementary bounds proved here; not a complete determination of the true optimal gap size.
ADVERSARIAL_SURVIVAL_SCORE: 92/100
RESOURCE_USAGE: about 60%; 3 main branches explored; 4 lemmas generated; 0 failed proof attempts retained as essential.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

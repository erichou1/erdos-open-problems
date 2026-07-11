# Erdős Problem #635 [solved] 100%

---

## ChatGPT Response

Formal statement

For fixed t≥1, define

M
t
	​

(N):=max∣A∣,

where the maximum is over all A⊆{1,…,N} satisfying

a,b∈A,b−a≥t⟹b−a∤b.

The uploaded question asks whether M
t
	​

(N)≤(
2
1
	​

+o
t
	​

(1))N. 

Pasted text

We prove the stronger precise statement

N→∞
lim
	​

N
M
t
	​

(N)
	​

=
2
1
	​

	​


for every fixed t≥1. Equivalently, for every fixed t and every ε>0, there is N
0
	​

(t,ε) such that

N≥N
0
	​

(t,ε)⟹∣A∣≤(
2
1
	​

+ε)N.

Its contrapositive says that if N is sufficiently large and

∣A∣>(
2
1
	​

+ε)N,

then there exist a<b in A such that

b−a≥t,b−a∣b.

The qualification “fixed t” is necessary: if t>N−1, the condition is vacuous and A={1,…,N} is possible.

1. Reformulation as paths of multiples

Let a<b, and put d=b−a. Then

d∣b⟺a=kd,b=(k+1)d

for some integer k≥1.

Indeed, if d∣b, then d∣b−d=a, so a=kd and b=(k+1)d. The converse is immediate.

Consequently, for every integer d≥t, the sequence

d,2d,3d,…,⌊
d
N
	​

⌋d

cannot contain two consecutive terms belonging to A.

Let

m
d
	​

=⌊
d
N
	​

⌋.

A binary sequence of length m
d
	​

 with no consecutive 1's contains at most ⌈m
d
	​

/2⌉ ones. Hence

∣A∩{d,2d,…,m
d
	​

d}∣≤⌈
2
m
d
	​

	​

⌉.
(1)

Introduce the balanced indicator

f(n):=21
A
	​

(n)−1∈{−1,1}.

Equation (1) gives, for every integer d≥t,

k≤N/d
∑
	​

f(kd)≤1.
(2)
2. A self-contained supply of averaging moduli

We need finite sets of primes p≥t for which

p
∑
	​

p
1
	​


is arbitrarily large.

Lemma 1

The sum of the reciprocals of the primes diverges. Therefore, after deleting all primes below any fixed t, the remaining reciprocal sum still diverges.

Proof

For x≥2, unique prime factorization gives

p≤x
∏
	​

(1−
p
1
	​

)
−1
=
p≤x
∏
	​

(1+
p
1
	​

+
p
2
1
	​

+⋯)≥
n≤x
∑
	​

n
1
	​

,
(3)

because every n≤x has all its prime factors at most x.

Suppose ∑
p
	​

1/p converged. Since

−log(1−
p
1
	​

)=
j≥1
∑
	​

jp
j
1
	​

≤
j≥1
∑
	​

p
j
1
	​

=
p−1
1
	​

≤
p
2
	​

,

the products on the left of (3) would be bounded uniformly in x. But the harmonic sums on the right diverge, a contradiction.

Removing finitely many primes does not affect divergence. ∎

Thus, for every L>0, we may choose a finite set P of primes satisfying

p≥t(p∈P),λ:=
p∈P
∑
	​

p
1
	​

≥L.
(4)

Write r=∣P∣.

3. Prime-divisor averaging

For n≤N, define

H(n):=
λ
1
	​

p∈P
∑
	​

1
p∣n
	​

.
(5)

This is a normalized count of the selected prime divisors of n.

Using (2) for every p∈P,

n≤N
∑
	​

f(n)H(n)
	​

=
λ
1
	​

p∈P
∑
	​

n≤N
p∣n
	​

∑
	​

f(n)
=
λ
1
	​

p∈P
∑
	​

k≤N/p
∑
	​

f(kp)
≤
λ
r
	​

.
	​

(6)

It remains to show that H(n) is close to 1 on average.

Lemma 2

For H defined by (5),

n≤N
∑
	​

(1−H(n))
2
≤
λ
N
	​

+
λ
2r
	​

.
(7)
Proof

For each positive integer q, write

δ
q
	​

:=⌊
q
N
	​

⌋−
q
N
	​

,−1<δ
q
	​

≤0.

First,

n≤N
∑
	​

H(n)=
λ
1
	​

p∈P
∑
	​

⌊
p
N
	​

⌋=N+
λ
1
	​

p∈P
∑
	​

δ
p
	​

.
(8)

Because the primes in P are distinct,

n≤N
∑
	​

H(n)
2
	​

=
λ
2
1
	​

	​

p∈P
∑
	​

⌊
p
N
	​

⌋+2
p,q∈P
p<q
	​

∑
	​

⌊
pq
N
	​

⌋
	​

.
	​

(9)

Let

σ
2
	​

:=
p∈P
∑
	​

p
2
1
	​

.

Since

λ
2
=σ
2
	​

+2
p<q
∑
	​

pq
1
	​

,

the main term in (9) equals

λ
2
N
	​

(λ+λ
2
−σ
2
	​

)=N+
λ
N
	​

−
λ
2
Nσ
2
	​

	​

.

Therefore

n≤N
∑
	​

(1−H(n))
2
	​

=N−2
n≤N
∑
	​

H(n)+
n≤N
∑
	​

H(n)
2
=
λ
N
	​

−
λ
2
Nσ
2
	​

	​

−
λ
2
	​

p∈P
∑
	​

δ
p
	​

+
λ
2
1
	​

	​

p∈P
∑
	​

δ
p
	​

+2
p<q
∑
	​

δ
pq
	​

	​

.
	​


The final parenthesis is nonpositive, while

−
p∈P
∑
	​

δ
p
	​

<r.

Discarding the negative terms gives

n≤N
∑
	​

(1−H(n))
2
≤
λ
N
	​

+
λ
2r
	​

.

∎

4. The upper bound

Using ∣f(n)∣=1, equation (6), Cauchy–Schwarz, and Lemma 2,

n≤N
∑
	​

f(n)
	​

=
n≤N
∑
	​

f(n)H(n)+
n≤N
∑
	​

f(n)(1−H(n))
≤
λ
r
	​

+
n≤N
∑
	​

∣1−H(n)∣
≤
λ
r
	​

+
N
n≤N
∑
	​

(1−H(n))
2
	​

≤
λ
r
	​

+
λ
N(N+2r)
	​

	​

.
	​

(10)

But

n≤N
∑
	​

f(n)=2∣A∣−N.

Thus, for every finite set P of primes at least t,

N
∣A∣
	​

≤
2
1
	​

+
2λN
r
	​

+
2
1
	​

λ
1+2r/N
	​

	​

	​

.
(11)

Now fix t and ε>0. By Lemma 1, choose a fixed finite P of primes at least t such that

λ=
p∈P
∑
	​

p
1
	​


is sufficiently large that

2
λ
	​

1
	​

<
2
ε
	​

.

After P is fixed, so is r. Letting N→∞ in (11) gives

N→∞
limsup
	​

N
M
t
	​

(N)
	​

≤
2
1
	​

+
2
λ
	​

1
	​

.

Because λ can be arbitrarily large,

N→∞
limsup
	​

N
M
t
	​

(N)
	​

≤
2
1
	​

.
(12)
5. Matching lower bound

Let

A={n≤N:n is odd}.

If a,b∈A, then b−a is even. A positive even integer cannot divide the odd integer b. Thus this A satisfies the condition for every t≥1, and

∣A∣=⌈
2
N
	​

⌉.
(13)

Combining (12) and (13),

M
t
	​

(N)=
2
N
	​

+o
t
	​

(N)
	​


for every fixed t≥1. In particular,

∣A∣≤(
2
1
	​

+o
t
	​

(1))N
	​


with the o
t
	​

(1) interpreted as N→∞ for fixed t.

For t=1, the exact bound follows immediately because two consecutive integers cannot both belong to A, giving

M
1
	​

(N)=⌈
2
N
	​

⌉=⌊
2
N+1
	​

⌋.
Final state

PROVED

PROOF_CONFIDENCE: 99/100
COMPLETENESS_SCORE: 100/100
ADVERSARIAL_SURVIVAL_SCORE: 99/100

No WiFi, internet search, external databases, literature-status information, or external citations were used. The only citation identifies the user-provided problem statement; all mathematical reasoning above was derived directly from the definitions.

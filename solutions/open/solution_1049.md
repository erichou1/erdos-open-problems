# Erdős Problem #1049 [unsolved] 24%

---

## ChatGPT Response

Formalization

Let t>1 be rational. Write

t=
b
a
	​

,a,b∈N,a>b,gcd(a,b)=1,

and put q=b/a∈(0,1). Define

L(a,b):=
n=1
∑
∞
	​

t
n
−1
1
	​

.

Since

t
m
−1
1
	​

=
1−q
m
q
m
	​

=
r=1
∑
∞
	​

q
mr
,

and all terms are nonnegative, rearrangement is justified. Therefore

L(a,b)=
m,r≥1
∑
	​

q
mr
=
n=1
∑
∞
	​

τ(n)q
n
=
n=1
∑
∞
	​

τ(n)
a
n
b
n
	​

.

The target assertion is

∀a,b∈N,(a>b, gcd(a,b)=1)⟹L(a,b)∈
/
Q.

Its negation is

∃a>b≥1,gcd(a,b)=1,∃A∈Z, C∈N:L(a,b)=
C
A
	​

.

Thus a contradiction proof must start from a fixed reduced pair (a,b) and a rational representation L=A/C.

An exact equivalent consequence of rationality is obtained by multiplying by Ca
N
. For every N≥1,

Aa
N
=C
n=1
∑
N
	​

τ(n)b
n
a
N−n
+C
k=1
∑
∞
	​

τ(N+k)
a
k
b
N+k
	​

.

The first two displayed quantities are integers. Hence rationality implies

R
N
	​

:=C
k=1
∑
∞
	​

τ(N+k)
a
k
b
N+k
	​

∈Z(N≥1).
(1)

Moreover R
N
	​

>0. Consequently, it would suffice to construct one N for which R
N
	​

<1.

Divisibility-block approach

Fix K≥1. If

a
k
∣Cτ(N+k)(1≤k≤K),
(2)

then, because b
N+k
 is an integer, the first K summands in R
N
	​

 are integers. Combining this with (1), rationality would imply that

E
N,K
	​

:=C
k>K
∑
	​

τ(N+k)
a
k
b
N+k
	​


is a positive integer.

Using the elementary estimate τ(m)≤m, one obtains

E
N,K
	​

≤Cb
N
k>K
∑
	​

(N+k)q
k
,q=
a
b
	​

.

The geometric sums give

k>K
∑
	​

(N+k)q
k
=q
K+1
(
1−q
N+K+1
	​

+
(1−q)
2
q
	​

).

Therefore

E
N,K
	​

≤Cb
N
q
K+1
(
1−q
N+K+1
	​

+
(1−q)
2
q
	​

).
(3)

For (3) to tend below 1, it is necessary, up to logarithmic terms, that

Klog
b
a
	​

>Nlogb.

Thus when b>1, the required divisibility block has length approximately

K>
log(a/b)
logb
	​

N.
(4)

This is a linear-length block following N, rather than a block whose length merely tends to infinity.

Explicit simultaneous divisibility construction

Conditions of the form (2) can be forced individually. For each 1≤k≤K, choose an integer d
k
	​

 divisible by

gcd(a
k
,C)
a
k
	​


and choose distinct primes p
k
	​

. Impose

N+k≡p
k
d
k
	​

−1
	​

(modp
k
d
k
	​

	​

).
(5)

Then

v
p
k
	​

	​

(N+k)=d
k
	​

−1,

so

d
k
	​

∣τ(N+k).

It follows that a
k
∣Cτ(N+k). Since the moduli p
k
d
k
	​

	​

 are pairwise coprime, the Chinese remainder theorem supplies infinitely many N satisfying all conditions (5).

However, the least positive such N can be comparable to

k=1
∏
K
	​

p
k
d
k
	​

	​

,

while d
k
	​

 is at least of order a
k
/C. Consequently,

logN≳
k=1
∑
K
	​

a
k
logp
k
	​

≳a
K
,

so this construction yields at best

K=O(loglogN).

That is incompatible with the linear requirement (4) whenever b>1.

This is not merely a missing estimate: the elementary integer-base mechanism loses a factor b
N
 after multiplication by a
N
. Eliminating that factor would require either:

rational approximants whose denominators incorporate the numerator b
N
 without destroying the error estimate;

a divisibility block of length proportional to its starting point;

cancellation in a signed auxiliary linear form, rather than the positive tail E
N,K
	​

; or

a different family of Padé-type identities producing errors of order exp(−cN
2
).

I did not derive such an auxiliary construction from first principles, and therefore obtained neither a proof nor a counterexample.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 98/100
Confidence concerns the verified identities and the stated obstruction, not the unresolved irrationality assertion.

COMPLETENESS_SCORE: 24/100

ADVERSARIAL_SURVIVAL_SCORE: 94/100 for the established partial deductions.

RESOURCE_USAGE: Approximately 100% of the allocated proof-search budget; several approaches examined, one exact rationality consequence established, one explicit divisibility construction analyzed, and the principal quantitative failure isolated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

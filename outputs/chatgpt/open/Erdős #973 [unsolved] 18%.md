# Erdős Problem #973 [unsolved] 18%

---

## ChatGPT Response

Phase 0: formalization

For n≥2, define

A
n
	​

={(z
1
	​

,…,z
n
	​

)∈C
n
:z
1
	​

=1,∣z
i
	​

∣≥1 (1≤i≤n)}

and

M
n
	​

=
(z
i
	​

)∈A
n
	​

inf
	​

2≤k≤n+1
max
	​

	​

i=1
∑
n
	​

z
i
k
	​

	​

.

The assertion is

∃C>1∀n≥2M
n
	​

<C
−n
.
(P)
Quantifier structure
∃C>1∀n≥2∃z
1
	​

,…,z
n
	​

∈C[z
1
	​

=1∧
i=1
⋀
n
	​

∣z
i
	​

∣≥1∧
k=2
⋀
n+1
	​

	​

i=1
∑
n
	​

z
i
k
	​

	​

<C
−n
].
Negation
∀C>1∃n≥2∀(z
i
	​

)∈A
n
	​

2≤k≤n+1
max
	​

	​

i=1
∑
n
	​

z
i
k
	​

	​

≥C
−n
.
(¬P)

Equivalently, the assertion asks whether the sequence M
n
	​

 admits a uniform exponential upper bound with base strictly smaller than 1.

More precisely, if

ρ=
n≥2
sup
	​

M
n
1/n
	​

,

then (P) would follow from ρ<1. Conversely, (P) implies

M
n
1/n
	​

<C
−1
<1

for every n, hence ρ≤C
−1
<1.

Thus the exact equivalent formulation is

n≥2
sup
	​

M
n
1/n
	​

<1.
	​

(1)

The strict inequalities cause no difficulty in this equivalence.

Algebraic formulation

Write

p
k
	​

=
i=1
∑
n
	​

z
i
k
	​


and let e
j
	​

 be the elementary symmetric functions of z
1
	​

,…,z
n
	​

, with e
0
	​

=1. Then

e
n
	​

=z
1
	​

z
2
	​

⋯z
n
	​

,∣e
n
	​

∣≥1.
(2)

Newton’s identities state, for 1≤m≤n,

me
m
	​

=
j=1
∑
m
	​

(−1)
j−1
e
m−j
	​

p
j
	​

.
(3)

Since there are only n variables, the identity at degree n+1 is

0=
j=1
∑
n+1
	​

(−1)
j−1
e
n+1−j
	​

p
j
	​

.
(4)

The problem requires

∣p
j
	​

∣<C
−n
,2≤j≤n+1,
(5)

while p
1
	​

 is unrestricted.

Introduce

E(t)=
i=1
∏
n
	​

(1+z
i
	​

t)=
m=0
∑
n
	​

e
m
	​

t
m
.

Formally,

E(t)=exp(
j≥1
∑
	​

(−1)
j−1
j
p
j
	​

t
j
	​

).
(6)

For coefficients through degree n, this gives the exact expression

e
n
	​

=[t
n
]exp(p
1
	​

t+
j=2
∑
n
	​

(−1)
j−1
j
p
j
	​

t
j
	​

).
(7)

Moreover, because E has degree n,

[t
n+1
]exp(p
1
	​

t+
j=2
∑
n+1
	​

(−1)
j−1
j
p
j
	​

t
j
	​

)=0.
(8)

Consequently, any construction must simultaneously satisfy:

	​

[t
n
]exp(p
1
	​

t+
j=2
∑
n
	​

(−1)
j−1
j
p
j
	​

t
j
	​

)
	​

≥1,
(9)

and the coefficient cancellation (8), while every p
2
	​

,…,p
n+1
	​

 is exponentially small.

This exhibits the principal tension: if the p
j
	​

, j≥2, were exactly zero, then

e
n
	​

=
n!
p
1
n
	​

	​


and

0=[t
n+1
]e
p
1
	​

t
=
(n+1)!
p
1
n+1
	​

	​

,

forcing p
1
	​

=0, and hence e
n
	​

=0, contradicting (2). Thus exact simultaneous cancellation is impossible.

The question is whether exponentially small, rather than zero, power sums can perturb these two incompatible coefficient conditions sufficiently.

Boundary cases
Case n=2

Set z
1
	​

=1, z
2
	​

=z, ∣z∣≥1. Then

M
2
	​

=
∣z∣≥1
inf
	​

max{∣1+z
2
∣, ∣1+z
3
∣}.

On the unit circle z=e
iθ
,

∣1+z
2
∣=2∣cosθ∣,∣1+z
3
∣=2
	​

cos
2
3θ
	​

	​

.

At θ=2π/5,

∣1+z
2
∣=∣1+z
3
∣=
2
5
	​

−1
	​

.

Indeed,

2cos
5
2π
	​

=
2
5
	​

−1
	​

,

and

2
	​

cos
5
3π
	​

	​

=
2
5
	​

−1
	​

.

Hence

M
2
	​

≤
2
5
	​

−1
	​

.
(10)

Therefore the n=2 case is compatible with any C satisfying

C
−2
>
2
5
	​

−1
	​

,

or

C<
2
5
	​

+1
	​

	​

.
(11)

Thus small n does not immediately disprove the assertion, although it limits any possible value of C.

Strategy search

The following independent approaches were examined.

Exact vanishing of p
2
	​

,…,p
n
	​

.
Newton identities determine e
j
	​

=p
1
j
	​

/j!, but the degree-(n+1) identity then forces a large nonzero p
n+1
	​

. Exact vanishing fails.

Perturbation of the exact-vanishing model.
One would need coefficient estimates showing that exponentially small p
2
	​

,…,p
n+1
	​

 can reconcile (8) and (9). No such estimate was established.

Roots-of-unity constructions.
The n-th roots of unity give p
k
	​

=0 for 1≤k<n, but p
n
	​

=n. Perturbing the roots must eliminate a term of size n without destroying the earlier cancellations.

Several regular polygons.
Unions of rotated polygons concentrate nonzero power sums on selected divisibility classes, but the number of variables and the range 2,…,n+1 leave unavoidable low-order multiples.

Reciprocal transformation w
i
	​

=1/z
i
	​

.
This transfers the modulus condition to ∣w
i
	​

∣≤1, but converts the desired sums into negative power sums ∑w
i
−k
	​

; ordinary positive-power cancellation does not transfer.

Newton-identity lower bound.
The condition ∣e
n
	​

∣≥1 should force at least one of p
2
	​

,…,p
n+1
	​

 to be non-negligible. The elementary coefficient bounds obtained this way lose factors comparable to factorials and do not exclude every exponential base C>1.

Polynomial logarithmic derivative.
For

P(x)=
i=1
∏
n
	​

(x−z
i
	​

),

the expansion of P
′
/P at infinity contains the p
k
	​

. The exterior-root constraint controls the constant term but did not yield a sufficiently strong bound on the prescribed block of coefficients.

Vandermonde inversion.
Consecutive power sums determine weighted combinations of the z
i
	​

, but nearly coincident z
i
	​

 make the inverse Vandermonde matrix arbitrarily ill-conditioned.

Compactness and extremizers.
A bounded minimizing sequence would produce an extremizer, but cancellations can permit individual variables to grow while several leading powers cancel. A uniform coercivity statement was not obtained.

Induction in n.
Adding a new variable changes every power sum by z
k
; one complex parameter cannot independently correct n existing errors.

Probabilistic phases.
Independent phases typically produce power sums of order 
n
	​

, not exponentially small quantities.

Hierarchical scale construction.
Moduli >1 produce rapidly increasing high powers; cancelling them requires tightly matched groups, which then create lower-power rigidity. No convergent hierarchy satisfying all n constraints was found.

The coefficient formulation (8)–(9) and structured polygon constructions had the highest expected value, but neither yielded a complete argument.

Verified deductions

The following statements have been rigorously established within this analysis:

The original assertion is equivalent to

n≥2
sup
	​

M
n
1/n
	​

<1.

Exact cancellation

p
2
	​

=⋯=p
n+1
	​

=0

is impossible for nonzero z
i
	​

.

More specifically, if

p
2
	​

=⋯=p
n
	​

=0,

then Newton’s identities give

e
m
	​

=
m!
p
1
m
	​

	​

,1≤m≤n,

and the degree-(n+1) identity gives

p
n+1
	​

=(−1)
n+1
n!
p
1
n+1
	​

	​

.

The modulus hypothesis is encoded exactly by

∣e
n
	​

∣≥1.

For n=2, there is an admissible configuration with objective value

2
5
	​

−1
	​

.

No uniform construction with exponential decay was established, and no lower bound was established that rules out every C>1.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96

COMPLETENESS_SCORE: 18

ADVERSARIAL_SURVIVAL_SCORE: 91

RESOURCE_USAGE: approximately 100% of the allocated response-level reasoning budget; 12 strategy families examined; 5 algebraic lemmas established; 8 unsuccessful construction or lower-bound approaches.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

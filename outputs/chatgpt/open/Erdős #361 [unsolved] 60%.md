# Erdős Problem #361 [unsolved] 60%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let

F
c
	​

(n)=max{∣A∣:A⊆{1,…,⌊cn⌋}, n∈
/
Σ(A)},

where

Σ(A)={
a∈B
∑
	​

a:B⊆A}.

Put

m=⌊cn⌋.

We seek F
c
	​

(n) for fixed c>0, large n, and whether F
c
	​

(n) has irregular dependence on arithmetic properties of n.

Quantifier structure

For fixed c>0:

F
c
	​

(n)=
A
max
	​

∣A∣

subject to

A⊆[m],∀B⊆A,
b∈B
∑
	​

b

=n.

The negation of admissibility is:

∃B⊆A
b∈B
∑
	​

b=n.
Complete solution for c≥1

Assume c≥1, so m≥n for all sufficiently large n.

Every integer >n is harmless: no subset containing such an element can sum to n, since all elements are positive. The element n itself is forbidden, since {n} sums to n.

So the problem reduces to maximizing the size of

A∩{1,…,n−1}.

For each 1≤x<n, the pair

{x,n−x}

cannot both lie in A, because then x+(n−x)=n.

The integers 1,…,n−1 split into pairs

{1,n−1},{2,n−2},…

and, when n is even, the singleton {n/2}.

Therefore

∣A∩[n−1]∣≤⌊
2
n
	​

⌋.

This bound is sharp: take

A
0
	​

={⌈
2
n
	​

⌉,⌈
2
n
	​

⌉+1,…,n−1},

with n/2 included when n is even. Any two distinct elements of A
0
	​

 have sum >n, and no single element equals n. Thus n∈
/
Σ(A
0
	​

), and

∣A
0
	​

∣=⌊
2
n
	​

⌋.

Including all integers n+1,…,m, we obtain

F
c
	​

(n)=(m−n)+⌊
2
n
	​

⌋.

Equivalently,

F
c
	​

(n)=⌊cn⌋−n+⌊
2
n
	​

⌋
	​

(c≥1).

So for c≥1,

F
c
	​

(n)=(c−
2
1
	​

)n+O(1),

and the dependence on n is only the ordinary floor/parity dependence.

General lower-bound constructions for 0<c<1

For 0<c<1, the problem becomes much more arithmetic.

1. Divisibility obstruction

If d∤n, then the set

A
d
	​

={a≤m:d∣a}

is admissible, because every subset sum of A
d
	​

 is divisible by d, while n is not.

Thus

F
c
	​

(n)≥⌊
d
⌊cn⌋
	​

⌋

for every d≥2 with d∤n.

Therefore

F
c
	​

(n)≥
d≥2, d∤n
max
	​

⌊
d
⌊cn⌋
	​

⌋.
	​


This already shows strong arithmetic irregularity in the available constructions. For example, if n is odd, taking d=2 gives

F
c
	​

(n)≥⌊
2
⌊cn⌋
	​

⌋=
2
c
	​

n+O(1).

But if n is divisible by many small integers, this construction becomes much weaker.

2. Interval-layer obstruction

Fix an integer k≥1. Consider the interval

I
k
	​

(n,m)={a∈[m]:
k+1
n
	​

<a≤
k
n
	​

}.

Any subset of I
k
	​

(n,m) with at least k+1 elements has sum >n.

Any subset of I
k
	​

(n,m) with at most k elements has sum <n, up to harmless boundary issues caused by distinctness. More precisely, if a
1
	​

<⋯<a
j
	​

≤n/k with j≤k, then for j<k,

a
1
	​

+⋯+a
j
	​

≤j
k
n
	​

<n.

For j=k, equality would require all a
i
	​

=n/k, impossible for distinct integers. Hence the sum is <n.

Thus I
k
	​

(n,m) is admissible, and

F
c
	​

(n)≥∣I
k
	​

(n,m)∣.

Asymptotically,

∣I
k
	​

(n,m)∣=(min(c,
k
1
	​

)−
k+1
1
	​

)
+
	​

n+O(1),

where x
+
	​

=max(x,0).

Hence

F
c
	​

(n)≥
k≥1
max
	​

(min(c,
k
1
	​

)−
k+1
1
	​

)
+
	​

n+O(1).
	​


For example, if 1/3<c<1/2, then the interval

(
3
n
	​

,⌊cn⌋]

is admissible and has size roughly

(c−
3
1
	​

)n.

If c≥1/2, the upper-half construction gives

A={a:
2
n
	​

<a≤cn},

with size roughly

(c−
2
1
	​

)n.
3. Small-total obstruction

If

1+2+⋯+t=
2
t(t+1)
	​

<n,

then

A={1,2,…,t}

is admissible. This gives

F
c
	​

(n)≥⌊
2
8n+1
	​

−1
	​

⌋−O(1),

as long as t≤m. This is only O(
n
	​

), so it is negligible compared with the linear constructions above, but it matters in small numerical cases.

What is rigorously established here

For all c>0,

F
c
	​

(n)≥max{
d≥2, d∤n
max
	​

⌊
d
⌊cn⌋
	​

⌋,
k≥1
max
	​

∣I
k
	​

(n,⌊cn⌋)∣,⌊
2
8n+1
	​

−1
	​

⌋−O(1)}.

For c≥1, the exact answer is proved:

F
c
	​

(n)=⌊cn⌋−n+⌊
2
n
	​

⌋.
	​


For 0<c<1, I did not complete a proof of a matching upper bound from first principles inside this session. The natural candidate asymptotic is governed by the maximum of the divisibility obstruction and the interval-layer obstruction, namely something of the form

F
c
	​

(n)=max{
d≥2, d∤n
max
	​

d
c
	​

,
k≥1
max
	​

(min(c,
k
1
	​

)−
k+1
1
	​

)
+
	​

}n+o(n),

but I have not proved the required inverse theorem here, so I cannot mark the full 0<c<1 case as proved.

Does the answer depend irregularly on n?

For c≥1, only mildly:

F
c
	​

(n)=⌊cn⌋−n+⌊
2
n
	​

⌋.

For 0<c<1, the lower-bound constructions already exhibit strong arithmetic dependence. In particular, if n is odd, the even-number construction gives

F
c
	​

(n)≥
2
c
	​

n+O(1).

If n is divisible by many small integers, that construction is unavailable for small d, and the best divisibility obstruction may be much smaller. Thus the extremal behavior is expected to depend on divisibility properties of n, not just on the size of n.

The exact irregular dependence for 0<c<1 remains unproved in this derivation.

Final state report

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 95 for the c≥1 exact formula; 100 for the stated lower-bound constructions; 45 for the unproved candidate asymptotic in 0<c<1.

COMPLETENESS_SCORE: 60. The case c≥1 is complete. The case 0<c<1 has strong constructions but lacks a matching upper bound.

ADVERSARIAL_SURVIVAL_SCORE: 90 for the proved parts; 35 for the speculative asymptotic because the inverse theorem was not established.

RESOURCE_USAGE: roughly 85% of the available reasoning budget used; 3 main construction branches explored; 5 lemmas generated; 1 full proof completed; 1 major unresolved upper-bound problem remains.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

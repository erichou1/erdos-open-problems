# Erdős Problem #377 [unsolved] 35%

---

## ChatGPT Response

Complete formalization

Let

f(n)=
p≤n
p prime
	​

∑
	​

1
p∤(
n
2n
	​

)
	​

p
1
	​

.

The question is:

∃C>0 ∀n≥1:f(n)≤C.
Quantifier structure
∃C>0∀n∈N
≥1
	​

p≤n
p prime
p∤(
n
2n
	​

)
	​

∑
	​

p
1
	​

≤C.
Negation
∀C>0 ∃n≥1:f(n)>C.

Equivalently,

n≥1
sup
	​

f(n)=∞.
Contrapositive form

There is no clean contrapositive because the statement is existential-universal. The natural disproof target is a sequence n
j
	​

→∞ such that

f(n
j
	​

)→∞.
Basic divisibility reformulation

For a prime p, write the base-p expansion

n=d
0
	​

+d
1
	​

p+⋯+d
m
	​

p
m
,0≤d
i
	​

≤p−1.
Lemma 1: carry criterion

For prime p,

p∤(
n
2n
	​

)

if and only if adding n+n in base p produces no carry.

Equivalently,

p∤(
n
2n
	​

)⟺d
i
	​

≤
2
p−1
	​

for every i.
Verification

By Legendre’s formula,

v
p
	​

(n!)=
a≥1
∑
	​

⌊
p
a
n
	​

⌋.

Hence

v
p
	​

(
n
2n
	​

)=
a≥1
∑
	​

(⌊
p
a
2n
	​

⌋−2⌊
p
a
n
	​

⌋).

For each a, the summand is either 0 or 1, because

⌊2x⌋−2⌊x⌋∈{0,1}.

It equals 1 precisely when the fractional part of n/p
a
 is at least 1/2, i.e.

nmodp
a
≥
2
p
a
	​

.

Thus v
p
	​

(
n
2n
	​

)=0 exactly when

nmodp
a
<
2
p
a
	​

for every a≥1.

That is equivalent to every base-p digit of n being at most (p−1)/2. ∎

So the problem becomes:

Is 
n
sup
	​

p≤n
p prime
all base-p digits of n≤(p−1)/2
	​

∑
	​

p
1
	​

<∞?
	​

Equivalent interval formulation

For every a≥1, the no-carry condition implies

nmodp
a
<
2
p
a
	​

.

Writing

q
a
	​

=⌊
p
a
n
	​

⌋,

this is equivalent to

q
a
	​

p
a
≤n<(q
a
	​

+
2
1
	​

)p
a
.

Equivalently,

p
a
∈(
q
a
	​

+1/2
n
	​

,
q
a
	​

n
	​

].

Thus for a bad prime p, every power p
a
≤n must lie in one of the “left-half” intervals

(
q+1/2
n
	​

,
q
n
	​

].

This gives a necessary condition:

p∤(
n
2n
	​

)⟹∀a≥1, p
a
≤n:p
a
∈
q≥1
⋃
	​

(
q+1/2
n
	​

,
q
n
	​

].

The difficult point is that this is a simultaneous condition over all powers p,p
2
,p
3
,….

Extremal and boundary cases
p=2

The only allowed binary digit is 0. Hence for n≥1,

2∣(
n
2n
	​

).

So p=2 never contributes.

p>n/2

Then n=p+r, 0≤r<p. The base-p digits are 1,r. Since 1≤(p−1)/2 for odd p≥3, the only nontrivial condition is

r=n−p≤
2
p−1
	​

.

Thus

p∤(
n
2n
	​

)⟺p≥
3
2n+1
	​

(p>n/2).

So all contributing primes p>n/2 lie in

[
3
2n+1
	​

,n].

Their reciprocal contribution is small, roughly of size O(1/logn), so the main danger cannot come from primes extremely close to n.

p>
n
	​


Write

n=kp+r,0≤r<p.

Then k<p, so n has two base-p digits k,r. The no-carry condition is

k≤
2
p−1
	​

andr≤
2
p−1
	​

.

Equivalently,

p≥2k+1

and

p≥
2k+1
2n+1
	​

.

Since k=⌊n/p⌋, the possible p’s for each k lie in a short interval of the form

k+1
n
	​

<p≤
k
n
	​


plus the extra lower-half restriction

n−kp≤
2
p−1
	​

.

This already suggests that the large-prime contribution should be bounded.

Breadth-first strategy search
1. Direct digit-density proof

Show that for primes in the range

n
1/(m+1)
<p≤n
1/m
,

the condition that all m+1 base-p digits of n are at most (p−1)/2 gives a deterministic saving roughly 2
−m
.

Obstacle: deterministic digit restrictions for a fixed n do not automatically behave like independent random conditions.

2. Contradiction via many bad primes

Assume

p∈S
∑
	​

p
1
	​


is large for bad primes S. Try to force incompatible congruence restrictions on n modulo many prime powers.

Obstacle: the conditions are inequalities modulo p
a
, not exact congruences.

3. Construction of counterexamples

Try to build n whose base-p digits are all small for many primes p.

Natural attempt: choose n satisfying

nmodp
a
≤
2
p
a
−1
	​


for many p
a
.

Obstacle: CRT construction requires modulus roughly

p∈S
∏
	​

p
⌊logn/logp⌋
,

which quickly exceeds n. This suggests counterexamples are hard to build, but it is not a proof.

4. Induction on n

Use the recursion

n=qp+r,0≤r<p.

Then p is bad for n iff

r≤
2
p−1
	​


and p is also bad for q=⌊n/p⌋, unless q<p, in which case q≤(p−1)/2 is required.

Obstacle: q depends on p, so a clean induction bound for f(n) does not immediately close.

5. Dyadic prime grouping

Group primes by

P<p≤2P.

For fixed P, the number of relevant base-p digits is about

m∼
logP
logn
	​

.

Expected saving is 2
−m
.

Obstacle: need a deterministic upper bound for primes satisfying simultaneous digit inequalities.

6. Power-interval sieve

For each bad p, every p
a
 must lie in a left-half interval

(
q+1/2
n
	​

,
q
n
	​

].

Try to bound primes whose powers repeatedly land in these intervals.

Obstacle: powers p
a
 are highly correlated; one interval condition alone is too weak.

7. Large sieve style

Interpret the bad condition as requiring n to lie in half of the residue classes modulo each p
a
. A large-sieve-type inequality might show that too many such conditions cannot hold for one n.

Obstacle: the target is a pointwise statement in n, not an averaged statement over n.

8. Entropy argument

Each bad prime p imposes approximately

⌊
logp
logn
	​

⌋

binary restrictions. Try to show that total entropy restrictions cannot exceed logn.

Obstacle: entropy counting controls the number of possible n, not directly the worst-case set for one n.

9. Product obstruction

If many primes are bad, maybe their product or a related product divides or avoids some small integer built from n, causing contradiction.

Obstacle: badness is non-divisibility of (
n
2n
	​

), not divisibility of another fixed integer.

10. Smoothness comparison

Bad primes are those missing from the central binomial coefficient. Try to compare the product of bad primes with (
n
2n
	​

) or with ∏
p≤n
	​

p.

Obstacle: absence from (
n
2n
	​

) gives no direct divisibility relation.

11. Transfinite induction

No natural transfinite structure appears. Ordinary induction on n, on digit length, or on prime scale is more relevant.

Obstacle: none of the objects require transfinite ordering.

12. Counterexample search by structured n

Try special values:

n=
2
M−1
	​

,M=
p≤y
∏
	​

p
a
.

Then for primes p∣M,

nmodp
a
=
2
p
a
−1
	​

.

Obstacle: this controls only the first a base-p digits. To control all digits up to size n, one would need p
a
>n, impossible for many small primes simultaneously.

Shared verified theorem pool
Lemma 1
p∤(
n
2n
	​

)⟺all base-p digits of n≤
2
p−1
	​

.

Verified above.

Lemma 2

For bad p, every power p
a
≤n satisfies

nmodp
a
<
2
p
a
	​

.

Equivalently,

p
a
∈(
q+1/2
n
	​

,
q
n
	​

]

for q=⌊n/p
a
⌋.

Verified directly from Lemma 1.

Lemma 3

For p>n/2,

p∤(
n
2n
	​

)⟺p≥
3
2n+1
	​

.

Verified above.

Lemma 4

For p>
n
	​

, with k=⌊n/p⌋, badness is equivalent to

k≤
2
p−1
	​


and

n−kp≤
2
p−1
	​

.

Verified by the two-digit base-p expansion.

Main unresolved gap

The central gap is:

Prove a uniform bound for primes p satisfying all simultaneous digit inequalities.
	​


A single digit condition gives only a constant-factor saving. To prove the desired statement, one needs a cumulative saving over all base-p digits. Formally, one wants something like

n
1/(m+1)
<p≤n
1/m
p∤(
n
2n
	​

)
	​

∑
	​

p
1
	​

≪2
−m

or at least a summable bound in m. I could not derive this from the digit inequalities alone.

Attempted disproof route

To disprove the statement, one would need a sequence n
j
	​

 and prime sets S
j
	​

 such that

p∈S
j
	​

∑
	​

p
1
	​

→∞

and every p∈S
j
	​

 has all digits of n
j
	​

 at most (p−1)/2.

The CRT-style construction fails because to force all relevant base-p digits for many primes p, one would need simultaneous restrictions modulo

p
⌊logn/logp⌋
,

and the combined modulus becomes much larger than n. This is evidence against an easy counterexample, but not a disproof.

Adversarial check

The following possible proof shortcuts fail:

Using only the least significant digit.
This only enforces

nmodp≤
2
p−1
	​

,

which is far too weak.

Using only the leading digit.
This restricts p to roughly the upper half of each logarithmic scale

n
1/(m+1)
<p≤n
1/m
,

but the resulting harmonic contribution over m is not obviously summable.

Assuming digit independence.
The base-p digits of a fixed integer n as p varies are not independent random variables. Any proof relying on independence would be unjustified.

CRT construction as disproof.
CRT can force finitely many residue inequalities, but forcing all digit inequalities for many primes requires too large a modulus.

Reducing to an averaged statement.
Average boundedness of f(n) would not imply pointwise boundedness.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified reductions; 0 for a proof of the original boundedness statement.

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 70 for the reductions; unresolved for the main theorem.

RESOURCE_USAGE: approximately 90% of available reasoning budget; 12 strategies explored; 4 verified lemmas generated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

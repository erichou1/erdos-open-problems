# Erdős Problem #386 [unsolved] 35%

---

## ChatGPT Response

Formalization

Let

P(n,k):∃d∈Z
>0
	​

 such that d∣(
k
n
	​

) and cn<d≤n.

The problem asks whether

∃c>0 ∀n≥2 ∀k∈{1,…,n−1}:P(n,k)

is true.

By symmetry,

(
k
n
	​

)=(
n−k
n
	​

),

so it is enough to consider

1≤k≤
2
n
	​

.

The negation is:

∀c>0 ∃n≥2 ∃1≤k<n

such that every divisor d≤n of (
k
n
	​

) satisfies

d≤cn.

Equivalently, if

D(n,k)=max{d≤n:d∣(
k
n
	​

)},

the problem asks whether

n,k
inf
	​

n
D(n,k)
	​

>0.
Verified divisibility facts
Lemma 1: cyclic divisor

Let g=gcd(n,k). Then

g
n
	​

∣(
k
n
	​

).

Proof:

(
k
n
	​

)=
k
n
	​

(
k−1
n−1
	​

)=
k/g
n/g
	​

(
k−1
n−1
	​

).

Since gcd(n/g,k/g)=1 and (
k
n
	​

) is an integer, k/g∣(
k−1
n−1
	​

). Hence n/g∣(
k
n
	​

).

Thus always

D(n,k)≥
gcd(n,k)
n
	​

≥
k
n
	​

.

This proves the easy bound mentioned in the statement, but it does not give an absolute constant because k may grow with n.

Lemma 2: binomial transfer divisor

For every 1≤j≤k,

gcd((
j
n
	​

),(
j
k
	​

))
(
j
n
	​

)
	​

∣(
k
n
	​

).

Proof:

(
j
n
	​

)(
k−j
n−j
	​

)=(
k
n
	​

)(
j
k
	​

).

Let

A=(
j
n
	​

),B=(
j
k
	​

),h=gcd(A,B).

Then A/h is coprime to B/h, and

h
A
	​

(
k−j
n−j
	​

)=(
k
n
	​

)
h
B
	​

.

Therefore A/h∣(
k
n
	​

).

This creates many divisors, but I did not obtain a uniform way to force one of them into (cn,n].

Lemma 3: one-step descending divisor

Using

(
k
n
	​

)=
k
n−k+1
	​

(
k−1
n
	​

),

let

h=gcd(k,(
k−1
n
	​

)).

Then

k/h
n−k+1
	​

∣(
k
n
	​

).

Also, by Lemma 1 applied to (
k−1
n
	​

),

gcd(n,k−1)
n
	​

∣(
k−1
n
	​

).

Since gcd(k,gcd(n,k−1))=1, this implies

h≥gcd(n,k).

Therefore (
k
n
	​

) has a divisor at least

k
gcd(n,k)(n−k+1)
	​

.

This is strong when k has a large common factor with n, especially when k∣n, but it still does not yield an absolute constant in the remaining regime where gcd(n,k) is intermediate.

Main obstruction reached

The natural combined lower bounds are

D(n,k)≥
gcd(n,k)
n
	​


and

D(n,k)≥
k
gcd(n,k)(n−k+1)
	​

.

Writing g=gcd(n,k), these give

n
D(n,k)
	​

≥max{
g
1
	​

, 
kn
g(n−k+1)
	​

}.

For k≤n/2, this implies

n
D(n,k)
	​

≳max{
g
1
	​

,
2k
g
	​

}.

Optimizing over g gives only about

k
	​

1
	​

,

which still tends to 0. Thus these two elementary divisibility mechanisms alone cannot prove the required absolute constant.

The higher transfer divisors from Lemma 2 should, in principle, attack this gap, but I did not complete a proof that one of them, or one of its sub-divisors, must always lie in (cn,n].

Branch outcomes

Twelve independent approaches were considered:

Strategy	Outcome
Direct use of n/gcd(n,k)	Gives only n/k.
Symmetry k↔n−k	Reduces to k≤n/2, not enough.
One-step recurrence	Gives useful divisor ≥g(n−k+1)/k, not uniform.
Higher binomial-transfer divisors	Promising, but no uniform interval-control proof obtained.
Prime-divisor search	Large prime divisors help when k≫n, but not when k=o(n).
Consecutive-interval divisor search	Counterexamples to divisibility by a number in (n−k,n] block this route.
p-adic valuation formula	Gives exact local criteria but no global selection theorem.
Greedy divisor construction	Fails for abstract divisor multisets with large multiplicative gaps.
Smooth/rough decomposition	Needs a nontrivial uniform subset-product theorem not proved.
Induction on k	Divisibility is not preserved cleanly under Pascal recurrence.
Reduction to lcm quotients	Produces large divisors but not controlled below n.
Counterexample construction	No explicit infinite construction found.

The central unresolved target is:

Show that one of the verified divisors or its sub-divisors must enter (cn,n].

I could not prove or disprove this target within the available reasoning budget.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas above.

COMPLETENESS_SCORE: 35.

ADVERSARIAL_SURVIVAL_SCORE: 90 for the partial results; no complete proof or disproof was obtained.

RESOURCE_USAGE: roughly 100% of available reasoning budget; 12 branches explored; 3 verified lemmas generated; several failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

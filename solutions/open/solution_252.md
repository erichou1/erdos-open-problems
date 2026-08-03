# Erdős Problem #252 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Formalization

Let

σ
k
	​

(n)=
d∣n
∑
	​

d
k
,k∈Z
≥1
	​

, n∈Z
≥1
	​

.

Define

S
k
	​

=
n=1
∑
∞
	​

n!
σ
k
	​

(n)
	​

.

The question is:

∀k∈Z
≥1
	​

,S
k
	​

∈
/
Q?
Convergence

For every n,

σ
k
	​

(n)≤
d=1
∑
n
	​

d
k
≤n
k+1
.

Thus

0≤
n!
σ
k
	​

(n)
	​

≤
n!
n
k+1
	​

,

and ∑n
k+1
/n! converges. Therefore S
k
	​

 is a well-defined real number.

Negation

The negation of the desired statement is:

∃k≥1,S
k
	​

∈Q.

Equivalently, there exist integers A,B with B≥1 such that

S
k
	​

=
B
A
	​

.
Main rationality criterion

Assume S
k
	​

=A/B. For every N≥B, N!S
k
	​

∈Z. Also

N!
n=1
∑
N
	​

n!
σ
k
	​

(n)
	​

=
n=1
∑
N
	​

σ
k
	​

(n)
n!
N!
	​

∈Z.

Therefore the tail

T
N,k
	​

:=N!
n=N+1
∑
∞
	​

n!
σ
k
	​

(n)
	​


must be an integer for every N≥B. Writing n=N+r,

T
N,k
	​

=
r=1
∑
∞
	​

(N+1)(N+2)⋯(N+r)
σ
k
	​

(N+r)
	​

.

Thus:

S
k
	​

∈Q⟹T
N,k
	​

∈Zfor all sufficiently large N.

Contrapositive:

If infinitely many N satisfy T
N,k
	​

∈
/
Z, then S
k
	​

∈
/
Q.

This is the central reduction, but not a solution.

Tail truncation lemma

For fixed k≥1,

T
N,k
	​

=
r=1
∑
k+1
	​

(N+1)(N+2)⋯(N+r)
σ
k
	​

(N+r)
	​

+O
k
	​

(
N
1
	​

).
Proof

For r≥k+2,

σ
k
	​

(N+r)≤(N+r)
k+1
.

If r≤N, then

(N+1)(N+2)⋯(N+r)≥N
r

and

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

≤
N
r
(2N)
k+1
	​

=2
k+1
N
k+1−r
.

Summing over r=k+2,…,N gives O
k
	​

(1/N).

If r>N, then (N+1)⋯(N+r)≥r!, while N+r≤2r, so

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

≤
r!
(2r)
k+1
	​

,

whose tail from r>N is O
k
	​

(1/N). Hence the truncation lemma holds.

Therefore, if S
k
	​

∈Q, then for all sufficiently large N,

dist(
r=1
∑
k+1
	​

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

,Z)≤
N
C
k
	​

	​

.

So irrationality follows if one can find infinitely many N for which this finite expression stays a fixed positive distance away from every integer.

Verified special cases from first principles

I can prove k=1 and k=2 by this method.

Case k=1

Let N=p−1, where p is a large prime. Then

T
p−1,1
	​

=
p
σ
1
	​

(p)
	​

+O(
p
1
	​

).

Since p is prime,

σ
1
	​

(p)=1+p,

so

p
σ
1
	​

(p)
	​

=1+
p
1
	​

.

Thus

T
p−1,1
	​

=1+
p
1
	​

+O(
p
1
	​

).

More directly, the full tail is positive, and the part after the first term is O(1/p). Hence for all sufficiently large primes p,

1<T
p−1,1
	​

<2.

If S
1
	​

∈Q, then T
p−1,1
	​

∈Z for all sufficiently large p. But no integer lies strictly between 1 and 2. Contradiction.

Therefore

S
1
	​

∈
/
Q.
Case k=2

Again let N=p−1, with p a large odd prime. Then

T
p−1,2
	​

=
p
σ
2
	​

(p)
	​

+
p(p+1)
σ
2
	​

(p+1)
	​

+O(
p
1
	​

).

Since p is prime,

σ
2
	​

(p)=1+p
2
,

so

p
σ
2
	​

(p)
	​

=p+
p
1
	​

.

Now write

δ
2
	​

(m):=
m
2
σ
2
	​

(m)
	​

=
e∣m
∑
	​

e
2
1
	​

.

Then

p(p+1)
σ
2
	​

(p+1)
	​

=
p
p+1
	​

δ
2
	​

(p+1).

Because p is odd, p+1 is even, so 1∣p+1 and 2∣p+1. Hence

δ
2
	​

(p+1)≥1+
4
1
	​

=
4
5
	​

.

Also,

δ
2
	​

(p+1)=
e∣p+1
∑
	​

e
2
1
	​

≤
e=1
∑
∞
	​

e
2
1
	​

.

Using the elementary estimate

e=3
∑
∞
	​

e
2
1
	​

<
9
1
	​

+∫
3
∞
	​

x
2
dx
	​

=
9
1
	​

+
3
1
	​

=
9
4
	​

,

we get

e=1
∑
∞
	​

e
2
1
	​

<1+
4
1
	​

+
9
4
	​

=
36
61
	​

<
4
7
	​

.

Thus

4
5
	​

≤δ
2
	​

(p+1)<
4
7
	​

.

Therefore

p+
p
1
	​

+
4
5
	​

⋅
p
p+1
	​

+O(
p
1
	​

)≤T
p−1,2
	​

<p+
p
1
	​

+
4
7
	​

⋅
p
p+1
	​

+O(
p
1
	​

).

For sufficiently large p,

p+1<T
p−1,2
	​

<p+2.

If S
2
	​

∈Q, then T
p−1,2
	​

∈Z for all sufficiently large primes p. But no integer lies strictly between p+1 and p+2. Contradiction.

Therefore

S
2
	​

∈
/
Q.
Phase 1: Breadth-first search for general k

For fixed general k, the same tail criterion says rationality would force

T
N,k
	​

∈Z

for all sufficiently large N. The obstruction is that the first k+1 tail terms contain large nontrivial divisor information from

N+1, N+2,…, N+k+1.

I generated the following independent strategies.

Strategy	Description	Hidden assumption	Main obstacle	Status
Direct prime shift	Set N=p−1 with p prime	Only need infinitely many primes	Terms p+1,…,p+k uncontrolled	Works for k=1,2, not general
Contradiction via integer intervals	Show T
N,k
	​

∈(M,M+1)	Need uniform bounds	For k≥3, middle terms grow polynomially	Incomplete
Controlled factor construction	Force N+r=a
r
	​

q
r
	​

 with q
r
	​

 prime	Need simultaneous prime values of linear forms	Not derivable here	Conditional route only
Induction on k	Relate σ
k+1
	​

 to σ
k
	​

	Need algebraic recurrence	No useful recurrence preserving factorial denominator	Failed
Transfinite induction	Treat all k as ordered family	Requires monotone implication P(k)⇒P(k+1)	No monotone structure found	Failed
Cardinal arithmetic	Use density of bad N	Need enough N avoiding near-integrality	Divisor patterns too irregular	Incomplete
Diagonalization	Construct N avoiding all integer traps	Need local congruence control of N+r	Requires prime/composite control	Incomplete
Compactness	Work modulo many small primes simultaneously	Need finite obstruction implies global obstruction	Near-integer is archimedean, not purely modular	Incomplete
Density argument	Show many N have fractional part bounded away from 0	Need distribution of divisor sums	Too strong without extra input	Incomplete
Reflection argument	Pass from large N to local divisor patterns	Need finitely many local patterns	Large prime factors matter	Incomplete
Auxiliary structure	Define finite-window divisor profile	Helps organize terms	Does not force contradiction alone	Useful but insufficient
Counterexample search	Try rationality-compatible profiles	Need construct infinitely many profiles	No actual rational example found	No disproof

Top three by expected value:

Finite-window divisor profile.

Prime-shift N=p−1.

Controlled factor construction.

Phase 2: New definitions and invariants
Definition 1: Rational tail
T
N,k
	​

:=
r=1
∑
∞
	​

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

.

Rationality of S
k
	​

 implies eventual integrality of T
N,k
	​

.

Definition 2: Truncated tail
F
N,k
	​

:=
r=1
∑
k+1
	​

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

.

Then

T
N,k
	​

=F
N,k
	​

+O
k
	​

(1/N).

Thus rationality implies

dist(F
N,k
	​

,Z)=O
k
	​

(1/N).
Definition 3: Complement-divisor density

For m≥1,

δ
k
	​

(m):=
m
k
σ
k
	​

(m)
	​

=
e∣m
∑
	​

e
k
1
	​

.

Then

1≤δ
k
	​

(m)≤
e=1
∑
∞
	​

e
k
1
	​


for k≥2, with the upper bound finite.

This is useful because

(N+1)⋯(N+r)
σ
k
	​

(N+r)
	​

=
(N+1)⋯(N+r)
(N+r)
k
δ
k
	​

(N+r)
	​

.

So the r-th term has size roughly

N
k−r+1
δ
k
	​

(N+r).

For r≤k, this can grow polynomially in N. For r=k+1, it is roughly constant. For r≥k+2, it is O(1/N).

Definition 4: Finite-window divisor profile

For fixed k, define the divisor profile of N by

D
k
	​

(N):=({e:e∣N+1},{e:e∣N+2},…,{e:e∣N+k+1}).

The truncated tail is determined by these divisor sets through

F
N,k
	​

=
r=1
∑
k+1
	​

e∣N+r
∑
	​

(N+1)⋯(N+r)
(N+r)
k
/e
k
	​

.

The problem becomes: prove that for infinitely many N, this finite profile makes F
N,k
	​

 bounded away from integers.

Phase 3: Parallel exploration
Branch A: Prime-shift branch

Set N=p−1, p prime.

Then

T
p−1,k
	​

=
r=1
∑
k+1
	​

p(p+1)⋯(p+r−1)
σ
k
	​

(p+r−1)
	​

+O
k
	​

(1/p).

The r=1 term is controlled:

p
σ
k
	​

(p)
	​

=
p
1+p
k
	​

=p
k−1
+
p
1
	​

.

So the first term is an integer plus 1/p.

The r=2 term involves p+1, which is even. Since 2∣p+1, the divisor (p+1)/2 contributes

p(p+1)
((p+1)/2)
k
	​

=
2
k
p
(p+1)
k−1
	​

.

For k=1, this is O(1/p).

For k=2, this is approximately 1/4, giving the interval obstruction above.

For k≥3, this is approximately

2
k
p
k−2
	​

,

which is no longer bounded. Its fractional part depends on p modulo powers of 2, and it may interact with other large contributions from p+2,…,p+k.

Gap node A

Prove that the combined fractional part of

F
p−1,k
	​


is bounded away from 0 for infinitely many primes p.

Attack attempts on Gap A

Use residues of primes modulo 2
k
.

Separate the forced divisor (p+1)/2.

Bound all other divisor contributions.

Use pigeonhole on prime residue classes.

Try to show no residue class causes exact cancellation.

Expand all rational functions in powers of p.

Track denominators coming from fixed small divisors.

Compare archimedean fractional parts with modular residues.

Try p≡1(mod2
k
).

Try p≡−1(mod2
k
).

Failure

The forced 2-divisibility of p+1 gives useful structure, but other numbers p+2,…,p+k may have large or small divisors in uncontrolled ways. Without proving infinitely many primes with additional restrictions on p+i, this branch does not close for arbitrary k.

Branch B: Controlled factor construction

Try to choose N so that

N+r=a
r
	​

q
r
	​


for 1≤r≤k+1, where each a
r
	​

 is small and known, and each q
r
	​

 is prime.

Then

σ
k
	​

(N+r)=σ
k
	​

(a
r
	​

)σ
k
	​

(q
r
	​

)

provided gcd(a
r
	​

,q
r
	​

)=1. Since

σ
k
	​

(q
r
	​

)=1+q
r
k
	​

,

each term becomes explicitly computable up to O(1/N).

This would reduce the problem to evaluating a rational function depending only on the chosen small integers a
r
	​

. If one can choose the a
r
	​

 so that the limiting fractional part is nonzero, then irrationality follows.

Gap node B

Construct infinitely many N such that all the linear forms

N+r=a
r
	​

q
r
	​


have prime quotient q
r
	​

.

Failure

This is a simultaneous primality problem for finitely many linear forms. I cannot prove the needed infinite construction from first principles here. Thus Branch B is a conditional framework, not a proof.

Branch C: Pure density of divisor profiles

Try to prove directly that the set of N for which

dist(F
N,k
	​

,Z)≤C
k
	​

/N

has density <1. Then infinitely many N violate eventual integrality.

Useful observation

The condition

dist(F
N,k
	​

,Z)≤C
k
	​

/N

is extremely rigid: F
N,k
	​

 is a finite sum of rational functions depending on the divisor sets of N+1,…,N+k+1. Exact near-integrality for every sufficiently large N would impose many simultaneous constraints on consecutive integers.

Gap node C

Show that these near-integrality constraints cannot hold for all large N.

Attacks

Compare F
N+1,k
	​

−F
N,k
	​

.

Use parity changes between N+r and N+r+1.

Separate largest-divisor terms.

Average over N≤X.

Estimate variance of F
N,k
	​

mod1.

Use small prime divisibility patterns.

Force a local pattern by Chinese remainders.

Try to show one local pattern gives a forbidden interval.

Construct N with N+r all highly composite.

Construct N with one N+r prime.

Failure

Averaging requires information about the distribution of divisor sums modulo 1. I can prove neither sufficient equidistribution nor sufficient avoidance of integers from elementary deductions alone.

Phase 4: Local verification of accepted lemmas
Lemma: eventual tail integrality under rationality

Accepted.

Dependencies:

S
k
	​

=A/B.

N≥B.

N!S
k
	​

∈Z.

Finite partial contribution is integral.

No hidden assumption found.

Lemma: truncation after k+1 terms is O
k
	​

(1/N)

Accepted.

Dependencies:

σ
k
	​

(n)≤n
k+1
.

Product denominator lower bounds.

Factorial decay for r>N.

No hidden assumption found.

Lemma: k=1 irrational

Accepted.

Dependencies:

Infinitely many primes.

Tail criterion.

T
p−1,1
	​

∈(1,2) for large p.

No circularity found.

Lemma: k=2 irrational

Accepted.

Dependencies:

Infinitely many odd primes.

Complement divisor identity.

Bound 5/4≤δ
2
	​

(p+1)<7/4.

Tail criterion.

Interval p+1<T
p−1,2
	​

<p+2.

No circularity found.

Dependency graph

Verified:

Convergence
⇓
S
k
	​

 well-defined
⇓
S
k
	​

∈Q⟹T
N,k
	​

∈Z eventually
⇓
T
N,k
	​

=F
N,k
	​

+O
k
	​

(1/N)
⇓

For k=1,2, prime shifts produce forbidden integer intervals.

Unresolved for arbitrary k:

∃
∞
Ndist(F
N,k
	​

,Z)≫
k
	​

1.

This unresolved statement is the main remaining theorem needed for the full problem.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified reductions and the k=1,2 proofs.

COMPLETENESS_SCORE: 35/100 for the original all-k problem, since the general case remains unresolved in this derivation.

ADVERSARIAL_SURVIVAL_SCORE: 88/100 for the accepted lemmas; 20/100 for the general proof attempt.

RESOURCE_USAGE: roughly 100% of the usable reasoning budget for this response; 3 major branches explored; 7 core lemmas/definitions generated; 3 failed general proof frameworks retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

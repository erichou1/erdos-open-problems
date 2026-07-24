# Erdős Problem #454 [unsolved] 34%

---

## ChatGPT Response

1. Formal statement

Assume the index variable in the minimum is

i∈{1,2,…,n−1}.

Let p
k
	​

 be the kth prime and define

f(n)=
1≤i<n
min
	​

(p
n+i
	​

+p
n−i
	​

).

Define

h(n)=f(n)−2p
n
	​

.

The target theorem is

∀M∈R, ∀N∈N, ∃n≥Nh(n)>M.

Equivalently,

∀M,∀N,∃n≥N,∀i∈{1,…,n−1},p
n+i
	​

+p
n−i
	​

−2p
n
	​

>M.

The negation is

∃M∈R,∃N∈N,∀n≥N,∃i∈{1,…,n−1}p
n+i
	​

+p
n−i
	​

−2p
n
	​

≤M.

So the problem asks whether there are infinitely far out prime indices n for which every symmetric pair around p
n
	​

 has midpoint arbitrarily far above p
n
	​

.

2. Gap reformulation

Let

g
k
	​

=p
k+1
	​

−p
k
	​


be the kth prime gap.

For 1≤i<n,

p
n+i
	​

−p
n
	​

=
t=0
∑
i−1
	​

g
n+t
	​

,

and

p
n
	​

−p
n−i
	​

=
t=1
∑
i
	​

g
n−t
	​

.

Therefore

p
n+i
	​

+p
n−i
	​

−2p
n
	​

=
t=0
∑
i−1
	​

g
n+t
	​

−
t=1
∑
i
	​

g
n−t
	​

.

Equivalently,

p
n+i
	​

+p
n−i
	​

−2p
n
	​

=
t=0
∑
i−1
	​

(g
n+t
	​

−g
n−1−t
	​

).

Define the outward gap walk

W
n
	​

(i)=
t=0
∑
i−1
	​

(g
n+t
	​

−g
n−1−t
	​

)for 1≤i<n.

Then

h(n)=
1≤i<n
min
	​

W
n
	​

(i).

Thus the target theorem becomes

∀M,∀N,∃n≥N,∀i∈{1,…,n−1},W
n
	​

(i)>M.

This is the cleanest internal form of the problem.

3. Immediate necessary conditions

Taking i=1,

W
n
	​

(1)=g
n
	​

−g
n−1
	​

.

Therefore

h(n)>M⟹g
n
	​

−g
n−1
	​

>M.

So the desired theorem implies the strictly weaker statement

n→∞
limsup
	​

(g
n
	​

−g
n−1
	​

)=∞.

This necessary condition is not enough. Even if the first outward step is large, the later prefix sums

W
n
	​

(2),W
n
	​

(3),…,W
n
	​

(n−1)

could later fall below M.

Taking i=n−1,

W
n
	​

(n−1)=p
2n−1
	​

+p
1
	​

−2p
n
	​

=p
2n−1
	​

+2−2p
n
	​

.

Thus another necessary condition for h(n)>M is

p
2n−1
	​

+2−2p
n
	​

>M.

The target requires all intermediate inequalities too, not only the first and last.

4. Equivalent geometric form

For each i<n,

p
n+i
	​

+p
n−i
	​

−2p
n
	​

>M

is equivalent to

2
p
n+i
	​

+p
n−i
	​

	​

>p
n
	​

+
2
M
	​

.

So h(n)>M means p
n
	​

 lies at least M/2 below every symmetric chord midpoint determined by index pairs (n−i,n+i).

This is a discrete convexity condition centered at index n, but it must hold simultaneously for every radius i<n.

5. Boundary cases and invariants

For n=1, the minimum has no valid positive index, so the natural domain is n≥2.

For n=2, only i=1 is allowed:

h(2)=p
3
	​

+p
1
	​

−2p
2
	​

=5+2−6=1.

For n≥3, all prime gaps except g
1
	​

=1 are even. Therefore most local gap differences are even, except when the symmetric interval reaches p
1
	​

=2.

The cardinality of the minimization set is

∣{1,…,n−1}∣=n−1.

So each h(n) is the minimum of finitely many explicitly defined integers.

6. Twelve independent strategies

Direct proof through gap walks
Goal: find infinitely many n whose outward walk W
n
	​

(i) stays above M.
Obstacle: the first step requires g
n
	​

−g
n−1
	​

>M, and no internal derivation produced this for primes.

Contradiction from bounded h(n)
Assume h(n)≤M eventually. Then each large n has some witness radius i(n) with W
n
	​

(i(n))≤M.
Obstacle: the witnesses may vary irregularly, so no global contradiction follows.

Construction using long composite intervals
Factorial blocks prove arbitrarily long prime gaps.
Obstacle: a long gap alone does not control the immediately preceding gap or all outward prefix sums.

Induction on n
Try to propagate a lower bound for h(n) from earlier centers.
Obstacle: changing n completely changes the paired gaps in W
n
	​

(i).

Transfinite induction
No natural transfinite structure appears. The problem is indexed by N, and ordinary induction does not expose a monotone property.

Cardinal arithmetic
The minimum uses n−1 radii. One might try to count bad centers.
Obstacle: without a strong distribution theorem for prime gaps, the counting argument has no verified density estimate.

Diagonalization
Try to choose n avoiding all bad radii i.
Obstacle: the constraints W
n
	​

(i)>M are not independent, and no construction of such an n was obtained.

Compactness
Model prime gaps as a positive integer sequence and seek a finite obstruction.
Obstacle: artificial positive sequences can satisfy many basic prime gap properties while failing the target behavior.

Density argument
Show many centers have large rightward growth compared with leftward growth.
Obstacle: no density estimate for the required asymmetric gap dominance was derived from the definitions alone.

Reflection argument
Use the pairing g
n+t
	​

 versus g
n−1−t
	​

.
Obstacle: the reflection is formal, but primes do not provide an evident symmetry breaking principle strong enough to force arbitrarily large positive prefix floors.

Auxiliary structure invention
Define outward dominance centers, prefix floors, and mirror gap walks.
Obstacle: these structures clarify the target but do not force existence.

Counterexample search
Try to build a positive increasing sequence with unbounded gaps but bounded h(n).
Observation: sequences like a
n
	​

=n
2
 have unbounded gaps but bounded local minimum behavior.
Obstacle: this does not disprove the prime statement because primes have additional arithmetic constraints.

Top three strategies after ranking:

Gap walk dominance.

Contradiction from bounded h(n).

Long composite interval construction.

All three reached unresolved required statements.

7. New definitions

Define the prefix floor

Φ(n)=
1≤i<n
min
	​

W
n
	​

(i).

Then

Φ(n)=h(n).

Define an M dominant center as an index n such that

W
n
	​

(i)>Mfor every 1≤i<n.

The theorem becomes

∀M,∀N,∃n≥Nn is M dominant.

Define the first gate

A(n)=g
n
	​

−g
n−1
	​

.

Then

n is M dominant⟹A(n)>M.

Define the terminal gate

B(n)=p
2n−1
	​

+2−2p
n
	​

.

Then

n is M dominant⟹B(n)>M.

Define the full obstruction set

O
M
	​

(n)={i∈{1,…,n−1}:W
n
	​

(i)≤M}.

Then n is M dominant exactly when

O
M
	​

(n)=∅.

This reformulation isolates the problem as the existence of infinitely far out centers with empty obstruction set.

8. Verified lemmas
Lemma 1: Gap walk identity

For every n≥2 and 1≤i<n,

p
n+i
	​

+p
n−i
	​

−2p
n
	​

=W
n
	​

(i).

Proof:

p
n+i
	​

−p
n
	​

=
t=0
∑
i−1
	​

g
n+t
	​

.

Also,

p
n
	​

−p
n−i
	​

=
t=1
∑
i
	​

g
n−t
	​

.

Therefore

p
n+i
	​

+p
n−i
	​

−2p
n
	​

=(p
n+i
	​

−p
n
	​

)−(p
n
	​

−p
n−i
	​

)
=
t=0
∑
i−1
	​

g
n+t
	​

−
t=1
∑
i
	​

g
n−t
	​

=
t=0
∑
i−1
	​

(g
n+t
	​

−g
n−1−t
	​

).

This is exactly W
n
	​

(i). Verified.

Lemma 2: First gate necessity

If h(n)>M, then

g
n
	​

−g
n−1
	​

>M.

Proof:

Since

h(n)=
1≤i<n
min
	​

W
n
	​

(i),

we have

h(n)≤W
n
	​

(1).

But

W
n
	​

(1)=g
n
	​

−g
n−1
	​

.

So if h(n)>M, then

g
n
	​

−g
n−1
	​

≥h(n)>M.

Verified.

Lemma 3: Terminal gate necessity

If h(n)>M, then

p
2n−1
	​

+2−2p
n
	​

>M.

Proof:

Since i=n−1 is allowed,

h(n)≤W
n
	​

(n−1).

By direct substitution,

W
n
	​

(n−1)=p
2n−1
	​

+p
1
	​

−2p
n
	​

.

Because p
1
	​

=2,

W
n
	​

(n−1)=p
2n−1
	​

+2−2p
n
	​

.

Thus h(n)>M implies the terminal inequality. Verified.

Lemma 4: Arbitrarily large prime gaps

For every integer m≥2, there exists a prime gap of length at least m.

Proof:

Let

A=(m+1)!.

Then every integer

A+2,A+3,…,A+(m+1)

is composite, since A+j is divisible by j for each 2≤j≤m+1.

Let r be the largest prime less than A+2, and let s be the smallest prime greater than A+(m+1). Such primes exist because there are primes below A+2, and Euclid's argument gives primes above any integer.

There are no primes in

[A+2,A+(m+1)].

Thus r and s are separated by at least m+1, so some prime gap is at least m+1. Verified.

Important limitation:

Lemma 4 does not imply Lemma 2's needed condition

g
n
	​

−g
n−1
	​

>M.

A large gap can be preceded by another large gap. The factorial construction does not control the previous prime gap.

9. GAP NODE 1

Target gap:

∀M,∀N,∃n≥Ng
n
	​

−g
n−1
	​

>M.

This is necessary for the main theorem.

Ten attacks:

Direct proof from factorial gaps
Fails because factorial gaps do not control g
n−1
	​

.

Contradiction assuming g
n
	​

−g
n−1
	​

≤M eventually
This permits gaps to grow slowly. No contradiction follows from gap unboundedness alone.

Stronger theorem
Try to prove infinitely many large gaps preceded by small gaps. No derivation was found.

Weaker theorem sufficient for original goal
No weaker replacement works, because the original goal itself forces g
n
	​

−g
n−1
	​

>M.

Equivalent formulation
The statement is equivalent to unbounded positive jumps in the prime gap sequence. This clarifies the target but does not prove it.

Auxiliary construction
Try to force a prime immediately before a long composite interval. This would require control over primality at an endpoint, which was not derived.

New invariant
The telescoping sum

k=a
∑
b
	​

(g
k
	​

−g
k−1
	​

)=g
b
	​

−g
a−1
	​


shows total gap growth over an interval, but does not force one jump to be large unless the interval length is controlled.

Counterexample search among abstract gap sequences
A sequence of gaps can be unbounded while all adjacent increases are bounded. Therefore unbounded gaps alone cannot prove this.

Extremal configuration
Record gaps satisfy g
n
	​

>g
j
	​

 for j<n, but the increment g
n
	​

−g
n−1
	​

 can still be small.

Recursive decomposition
To prove the first gate, one needs a mechanism producing sharp upward transitions in consecutive prime gaps. No such mechanism was derived from the definitions alone.

Status of GAP NODE 1: unresolved.

10. GAP NODE 2

Target gap:

g
n
	​

−g
n−1
	​

>MandW
n
	​

(i)>M for all 2≤i<n.

Even if the first gate is solved, this second gap remains.

Ten attacks:

Direct prefix control
Need every cumulative right gap sum to exceed every cumulative left gap sum by M. No direct construction was found.

Contradiction from a bad prefix
If W
n
	​

(i)≤M, then the left block of i gaps nearly cancels the right block. This gives local information but no contradiction.

Stronger theorem
Try to find centers where every paired gap satisfies

g
n+t
	​

>g
n−1−t
	​

+M.

This is far stronger than needed and no proof was derived.

Weaker theorem
It is enough that all prefix sums stay above M, not each term. Still no derivation was found.

Equivalent formulation
The outward walk must have prefix minimum above M. This is exact but not self proving.

Auxiliary structure
Define positive drift centers where the outward sequence has persistent right bias. No existence proof was obtained.

New invariant
The terminal value W
n
	​

(n−1) controls total drift, but a walk can have positive final value and still dip below M.

Counterexample search
Artificial walks can begin with a large positive jump and later fall below M. Therefore the first gate is insufficient.

Extremal radius analysis
Small i depends on local gaps. Large i depends on global prime growth. The middle range remains uncontrolled.

Recursive decomposition
This gap splits into local, middle, and terminal control. The middle range is the hard unresolved portion.

Status of GAP NODE 2: unresolved.

11. Branch outcomes
Branch A: large local gap

Assumption:

There are infinitely many n with very large g
n
	​

.

Verified from Lemma 4 only in the weaker sense that prime gaps are unbounded.

Attempt:

Use a large g
n
	​

 to force

W
n
	​

(i)>M

for every i.

Failure:

For i=1, one needs

g
n
	​

−g
n−1
	​

>M,

not merely g
n
	​

>M. For larger i, one needs cumulative right dominance. A single large gap does not guarantee this.

Result:

Branch A does not prove the theorem.

Branch B: contradiction from bounded h(n)

Assumption:

There exist M,N such that for all n≥N,

h(n)≤M.

Then for every n≥N, there exists i(n)<n with

W
n
	​

(i(n))≤M.

Attempt:

Use the witnesses i(n) to force a global structural restriction on the prime gaps.

Failure:

The witness radius i(n) can vary with n. No contradiction was derived.

Result:

Branch B does not disprove the theorem.

Branch C: factorial construction

Verified:

There are arbitrarily long intervals of consecutive composite integers, hence arbitrarily large prime gaps.

Attempt:

Use these long gaps as the first right gap g
n
	​

.

Failure:

The construction does not show that the previous gap g
n−1
	​

 is smaller by an arbitrarily large amount. It also does not control outward prefix sums beyond i=1.

Result:

Branch C proves only a necessary background fact, not the target theorem.

12. Adversarial referee check

Candidate claim 1:

“Large prime gaps imply the theorem.”

Attack:

False as a logical implication. The theorem requires

g
n
	​

−g
n−1
	​

>M

and all outward prefix inequalities. Large g
n
	​

 alone does not supply either condition.

Candidate claim 2:

“Record prime gaps imply the theorem.”

Attack:

A record gap can exceed the previous gap by only a small amount. Also, even a large first prefix does not force later prefixes to remain above M.

Candidate claim 3:

“The terminal inequality should dominate.”

Attack:

A walk can have large final value but small or negative earlier prefix minimum. Since h(n) is a minimum over all radii, terminal growth is insufficient.

Candidate claim 4:

“Unbounded gaps imply unbounded adjacent positive jumps.”

Attack:

An abstract sequence can be unbounded while adjacent increases stay bounded. Therefore this inference is invalid without extra arithmetic input.

All candidate proof routes fail under local verification.

13. Dependency graph

Definitions:

p
k
	​

,g
k
	​

,f(n),h(n),W
n
	​

(i),Φ(n).

Verified dependencies:

Lemma 1 depends only on definitions of g
k
	​

 and telescoping sums.

Lemma 2 depends on Lemma 1 and the allowed radius i=1.

Lemma 3 depends on Lemma 1 and the allowed radius i=n−1.

Lemma 4 depends on the factorial composite block construction and infinitude of primes.

Unresolved dependencies:

Main theorem requires GAP NODE 1 and GAP NODE 2.

GAP NODE 1 was not proved.

GAP NODE 2 was not proved.

No theorem in the verified pool implies the main theorem.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 93

COMPLETENESS_SCORE: 34

ADVERSARIAL_SURVIVAL_SCORE: 91

RESOURCE_USAGE: 100 percent of the available reasoning budget used, 3 main branches explored, 4 verified lemmas generated, 4 failed proof attempts identified.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

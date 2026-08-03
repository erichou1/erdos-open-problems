# Erdős Problem #289 [unsolved] 24%

---

## ChatGPT Response

Formalization

Let an interval mean

I=[a,b]∩N={a,a+1,…,b},a≤b.

The conditions are:

∣I
i
	​

∣=b
i
	​

−a
i
	​

+1≥2,

and after reordering,

b
i
	​

+2≤a
i+1
	​

(1≤i<k),

so the intervals are disjoint and separated by at least one missing integer.

Since any interval containing 1 has reciprocal sum at least 1+1/2>1, every valid interval must lie in {2,3,…}.

Define a finite set S⊆{2,3,…} to be admissible if its maximal consecutive runs all have length at least 2. Then the problem is equivalent to:

∃K ∀k≥K ∃S⊂N finite admissible with exactly k runs and 
n∈S
∑
	​

n
1
	​

=1.

Negation:

∀K ∃k≥K ∀S,S admissible with k runs⟹
n∈S
∑
	​

n
1
	​


=1.

Equivalent endpoint form:

∃K ∀k≥K ∃2≤a
1
	​

≤b
1
	​

<a
2
	​

≤b
2
	​

<⋯<a
k
	​

≤b
k
	​


such that

b
i
	​

−a
i
	​

+1≥2,b
i
	​

+2≤a
i+1
	​

,

and

i=1
∑
k
	​

(H
b
i
	​

	​

−H
a
i
	​

−1
	​

)=1.

Boundary facts:

k=1 is impossible. For a single interval [a,b] with b−a+1≥2, choose the unique integer in [a,b] divisible by the largest power of 2 occurring in that interval. Multiplying ∑
n=a
b
	​

1/n by the interval lcm gives an odd numerator over an even denominator, so the sum is not an integer.

The obstruction for one interval does not immediately extend to several intervals, because top 2-adic contributions from different intervals can cancel.

The problem is not merely about representing 1 as an Egyptian fraction. The selected denominators must form consecutive runs of length at least 2.

Breadth-first strategy search
Strategy	Description	Hidden assumption	Obstacle	Status
Direct construction	Build intervals greedily below residual r.	Greedy residual terminates.	Residuals tend to tiny rationals without exact closure.	Failed.
Contradiction	Assume admissible S sums to 1; use p-adic valuation.	A parity obstruction survives multiple intervals.	Known-type cancellation between intervals is possible; no contradiction found.	Failed.
Unit expansion	Use identities converting unit fractions into length-2 intervals plus smaller unit fractions.	Remaining unit fractions can be finitely absorbed.	Leaves isolated singletons.	Partial.
Induction on k	Find exact refinement increasing interval count.	A usable local replacement occurs inside a representation of 1.	Found refinements have total sum >1, not directly insertable.	Partial.
Transfinite induction	Well-order construction attempts.	Infinite search helps finite target.	Objects are finite; no useful limit object gives exact equality.	No progress.
Cardinal arithmetic	Count attainable sums with bounded denominator.	A bound on largest denominator can be proved.	No such bound found.	Failed.
Diagonalization	Avoid bad residues/isolated runs recursively.	Choices remain independent.	Exact reciprocal equalities couple choices globally.	Failed.
Compactness	Use infinite admissible binary sequences.	Infinite exact subseries can be truncated.	Exact finite equality does not follow from convergence/compactness.	Failed.
Density	Show block sums are dense near 1.	Approximation implies equality.	Exact rational equality is stronger.	Failed.
Reflection	Prove any large construction reflects to bounded pattern.	There is bounded structural core.	Denominators may escape to infinity.	Failed.
Auxiliary graph	Encode unit expansions as a directed graph.	A path/tree reaches zero isolated leaves.	Reachability unresolved.	Partial.
Counterexample search	Prove infinitely many k impossible.	A congruence obstruction depends on k.	No invariant strong enough found.	Failed.

Top three branches selected: unit-expansion construction, exact refinement identities, and p-adic obstruction search.

Verified lemmas
Lemma 1: Unit-to-pair expansion

For every n≥1,

n
1
	​

=
2n
1
	​

+
2n+1
1
	​

+
2n(2n+1)
1
	​

.

Proof:

n
1
	​

−
2n
1
	​

−
2n+1
1
	​

=
2n
1
	​

−
2n+1
1
	​

=
2n(2n+1)
1
	​

.

This gives one interval [2n,2n+1] plus a smaller unit fraction.

Lemma 2: More general unit-to-pair expansion

Suppose

n
1
	​

=
a
1
	​

+
a+1
1
	​

+
R
1
	​

.

Let

D=a(a+1)−n(2a+1).

Then

R
1
	​

=
na(a+1)
D
	​

.

Moreover, R∈N if and only if

D∣n
2
.

Proof. We compute:

n
1
	​

−
a
1
	​

−
a+1
1
	​

=
na(a+1)
a(a+1)−n(2a+1)
	​

=
na(a+1)
D
	​

.

Also,

a(a+1)=D+n(2a+1),

so

na(a+1)=nD+n
2
(2a+1).

Thus D∣na(a+1) iff D∣n
2
(2a+1).

If g∣D and g∣2a+1, then since

D=a(a+1)−n(2a+1),

we get g∣a(a+1). But

gcd(a,2a+1)=1,gcd(a+1,2a+1)=1,

so gcd(a(a+1),2a+1)=1. Hence g=1, so

gcd(D,2a+1)=1.

Therefore D∣n
2
(2a+1) iff D∣n
2
.

Lemma 3: A concrete near-construction for 1

Start from

1=
2
1
	​

+
3
1
	​

+
6
1
	​

.

Use:

2
1
	​

=
4
1
	​

+
5
1
	​

+
20
1
	​

,
3
1
	​

=
6
1
	​

+
7
1
	​

+
42
1
	​

,
6
1
	​

=
14
1
	​

+
15
1
	​

+
35
1
	​

.

Therefore

1=
n=4
∑
7
	​

n
1
	​

+
14
1
	​

+
15
1
	​

+
20
1
	​

+
35
1
	​

+
42
1
	​

.

Equivalently,

1=
n∈[4,7]
∑
	​

n
1
	​

+
n∈[14,15]
∑
	​

n
1
	​

+
20
1
	​

+
35
1
	​

+
42
1
	​

.

This is close to a valid representation, but the terms 20,35,42 are isolated singletons, so it is not admissible.

Further expansion gives:

20
1
	​

=
44
1
	​

+
45
1
	​

+
198
1
	​

,
35
1
	​

=
84
1
	​

+
85
1
	​

+
204
1
	​

,
42
1
	​

=
90
1
	​

+
91
1
	​

+
585
1
	​

.

Thus

1=[4,7]+[14,15]+[44,45]+[84,85]+[90,91]+
198
1
	​

+
204
1
	​

+
585
1
	​

,

where bracket notation means summing reciprocals over that interval. Again, the remaining unit fractions are isolated.

This branch does not close.

Lemma 4: A count-changing block identity

From Lemma 1, with

U(n)=2n(2n+1),

we have

n
1
	​

=
2n
1
	​

+
2n+1
1
	​

+
U(n)
1
	​

.

Subtracting this identity from the full interval [n,U(n)] gives:

m=n+1
∑
U(n)
	​

m
1
	​

=
m=n
∑
2n−1
	​

m
1
	​

+
m=2n+2
∑
U(n)−1
	​

m
1
	​

.

So one interval equals two separated intervals:

[n+1,U(n)]⟷[n,2n−1] ∪ [2n+2,U(n)−1].

For n=2, this is the explicit identity

m=3
∑
20
	​

m
1
	​

=
m=2
∑
3
	​

m
1
	​

+
m=6
∑
19
	​

m
1
	​

.

This increases the number of intervals by 1, but the interval sums are already larger than 1 for n≥2, so this identity cannot be directly inserted into a representation of 1.

Branch outcomes
Branch A: Construct 1 by expanding unit fractions

Verified progress:

1=[4,7]+[14,15]+
20
1
	​

+
35
1
	​

+
42
1
	​

.

Then:

1=[4,7]+[14,15]+[44,45]+[84,85]+[90,91]+
198
1
	​

+
204
1
	​

+
585
1
	​

.

Unresolved target:

198
1
	​

+
204
1
	​

+
585
1
	​


must be converted into admissible intervals without producing isolated singleton leaves.

GAP_NODE(A):

Can the unit-expansion graph starting from {20,35,42} terminate with all leaves lying in runs of length at least 2?

Attacks tried:

Direct expansion using a=2n: produces infinite Sylvester-type tails.

Alternative expansion using divisors D∣n
2
: gives finitely many local options but no closure found.

Try forcing residual denominators to be consecutive: no general mechanism found.

Try absorbing leaves into existing intervals: denominators too far apart.

Try expanding only the smallest isolated leaf: produces larger isolated leaves.

Try expanding only leaves with nearby possible partners: no partner-forcing invariant found.

Try 2-adic obstruction against closure: no contradiction.

Try stronger theorem “every unit fraction has finite admissible expansion”: not proved.

Try weaker theorem “the specific residual triple closes”: not proved.

Try graph reachability with isolation defect decreasing: no monotone defect function found.

Branch A remains open.

Branch B: Prove cofinality of attainable k

Let

A={k:∃ admissible S with k runs and 
n∈S
∑
	​

1/n=1}.

The target is:

A is cofinite.

A sufficient route would be:

Find one admissible representation of 1.

Find exact local replacements increasing the number of runs by elements of a finite set with gcd 1.

Ensure replacements can be placed without overlap or adjacency failures.

Verified count-changing identity:

[n+1,2n(2n+1)]=[n,2n−1]∪[2n+2,2n(2n+1)−1].

Obstacle: both sides have reciprocal sum about log(4n), exceeding 1 for n≥2. Therefore this identity cannot appear inside a positive representation of 1.

GAP_NODE(B):

Find a small-sum exact refinement identity usable inside a representation of 1.

Attacks tried:

Parametrize identities from unit expansions.

Search for one-interval to two-interval equalities with small total.

Use complements inside a larger interval.

Try scaling the known count-changing identity.

Try translating endpoints.

Try replacing a length-2 block by several later blocks.

Try using the residual unit fraction as a glue term.

Try deriving identities from divisor conditions.

Try using gcd-one count increments.

Try proving refinements exist asymptotically by density.

No usable refinement was proved.

Branch C: Disprove by p-adic obstruction

For one interval, the largest 2-power divisor occurs uniquely, so the reciprocal sum cannot be an integer.

For several intervals, let L=lcm(S). If

n∈S
∑
	​

n
1
	​

=1,

then

n∈S
∑
	​

n
L
	​

=L.

For a prime p, terms with maximal p-adic valuation among denominators control the numerator modulo p. This gives necessary cancellation conditions.

Obstacle: these conditions are not strong enough. Multiple intervals can supply multiple maximal p-power terms, allowing cancellation. The given style of integer-valued examples shows that the one-interval obstruction does not generalize naively.

GAP_NODE(C):

Prove or disprove a stronger invariant such as “every admissible reciprocal integer sum is even.”

Attacks tried:

Top 2-adic valuation count.

Modulo 2L numerator comparison.

Odd/even denominator splitting.

Induction on halving even denominators.

Endpoint parity analysis.

Maximal denominator prime-power attack.

Run-length parity invariant.

LCM numerator parity invariant.

Counterexample construction for odd integer sums.

Reduction to block-level 2-adic leading terms.

No contradiction with sum 1 was proved.

Dependency graph of verified results

Definitions:

admissible set;

run count;

unit-expansion edge;

isolation defect;

block-refinement identity.

Verified lemmas:

Single interval cannot sum to an integer.

Unit expansion:

1/n=1/(2n)+1/(2n+1)+1/(2n(2n+1)).

General pair expansion criterion:

1/n=1/a+1/(a+1)+1/R

with R∈N iff

D=a(a+1)−n(2a+1)>0,D∣n
2
.

Near-construction:

1=[4,7]+[14,15]+
20
1
	​

+
35
1
	​

+
42
1
	​

.

Count-changing block identity:

[n+1,2n(2n+1)]=[n,2n−1]∪[2n+2,2n(2n+1)−1].

Unresolved primary targets:

close the isolated unit leaves in Branch A;

find a usable small-sum refinement identity for Branch B;

prove a global obstruction for Branch C.

No theorem depending on these unresolved targets is accepted.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 88/100 for the verified lemmas and reductions above.

COMPLETENESS_SCORE: 24/100. A full proof or disproof of the original statement was not obtained.

ADVERSARIAL_SURVIVAL_SCORE: 70/100. The verified identities survived local checks; the construction and obstruction branches did not close.

RESOURCE_USAGE: 100% of available reasoning budget for this response; 12 strategy classes considered; 3 main branches explored; 5 verified lemmas recorded; 3 primary gap nodes generated; multiple failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

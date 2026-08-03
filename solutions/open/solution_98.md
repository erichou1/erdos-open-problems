# Erdős Problem #98 [unsolved] 18%

---

## ChatGPT Response

0. Formalization

Let P⊂R
2
, ∣P∣=n. Define

D(P)={∣p−q∣:p,q∈P, p

=q},d(P)=∣D(P)∣.

Call P admissible if:

no three points of P are collinear;

no four points of P lie on one circle.

Then

h(n)=min{d(P):P⊂R
2
, ∣P∣=n, P admissible}.

The question is:

n→∞
lim
	​

n
h(n)
	​

=∞?
	​


Quantifier form:

∀M>0 ∃N ∀n≥N ∀P admissible,d(P)≥Mn.

Negation:

∃M>0 ∀N ∃n≥N ∃P admissible,d(P)≤Mn.

So a disproof would require infinitely many admissible configurations with only O(n) distinct distances.

1. Immediate verified invariants

For every point p∈P and every radius r>0, the circle centered at p of radius r contains at most three points of P, because four points on that circle would violate admissibility.

Therefore each point sees any fixed distance at most three times.

Let k=d(P). Around a fixed p, the other n−1 points are distributed among k distance classes, each of size at most 3. Hence

n−1≤3k.

Thus

d(P)≥
3
n−1
	​

	​

.

Consequently,

h(n)≥
3
n−1
	​

	​

.

This proves only a linear lower bound, not h(n)/n→∞.

2. Equal-distance energy attempt

Let

q
r
	​

=#{(p,q)∈P
2
:p

=q, ∣p−q∣=r}.

Then

r∈D(P)
∑
	​

q
r
	​

=n(n−1).

For fixed r, each point has at most three neighbors at distance r, so

q
r
	​

≤3n.

Also,

r∈D(P)
∑
	​

q
r
2
	​


counts ordered pairs of ordered segments of equal length. For each ordered segment (a,b) and each choice of c, there are at most three choices of d with ∣c−d∣=∣a−b∣. Therefore

r
∑
	​

q
r
2
	​

≤3n
2
(n−1).

By Cauchy,

(
r
∑
	​

q
r
	​

)
2
≤d(P)
r
∑
	​

q
r
2
	​

.

So

n
2
(n−1)
2
≤d(P)⋅3n
2
(n−1),

hence again

d(P)≥
3
n−1
	​

.

This recovers the same linear bound and gives no superlinear growth.

3. Isosceles-triangle attempt

For a fixed base {a,b}, any point p satisfying

∣p−a∣=∣p−b∣

lies on the perpendicular bisector of ab. Since no three points of P are collinear, that perpendicular bisector contains at most two points of P. Therefore each base has at most two possible isosceles apices.

So the number of unordered isosceles triangles in P is at most

2(
2
n
	​

)=n(n−1).

Now count from the apex side. Around each apex p, distances occur in classes of size at most 3. If k=d(P), then n−1 points are placed into k boxes of capacity 3. This can force many isosceles triangles only when k is close to (n−1)/3. Optimizing the box count again gives only

k≥
3
n−1
	​

.

So the no-three-collinear condition, via perpendicular bisectors, still does not force d(P)/n→∞.

4. Twelve strategy scan
Strategy	Result
Direct radial counting	Gives h(n)≥(n−1)/3.
Equal-distance energy	Gives same lower bound.
Isosceles triangle counting	Gives same lower bound.
Contradiction assuming d(P)≤Cn	Requires new global structure; local bounds allow it.
Per-distance graph decomposition	Each distance graph has max degree 3, but this alone permits O(n) colors.
Induction on n	Removing one point loses uncontrolled distance information.
Transfinite/ordering argument	No useful monotone rank found.
Cardinal arithmetic	Total pair count divided by local multiplicity gives only linear.
Diagonalization	No contradiction obtained from finitely many distance labels.
Compactness/limit configuration	Degenerations may introduce forbidden collinear/cyclic limits.
Density argument	Need a density notion stronger than local circle occupancy.
Counterexample construction	Regular polygons and grids fail admissibility; perturbations destroy equalities.

The strongest verified theorem remains

h(n)≥
3
n−1
	​

	​

.
5. Main unresolved gap

To prove the desired statement, one needs:

∀C>0 ∃N ∀n≥N,d(P)>Cn

for every admissible P.

Equivalently, one must rule out arbitrarily large admissible configurations whose complete graph edges can be colored by only Cn distance colors, with each color having maximum degree at most 3, and with all colors geometrically realized as Euclidean distances.

The local admissibility constraints prove maximum degree 3 per distance color, but they do not by themselves prevent O(n) distance colors. A genuinely global obstruction would be needed.

I did not obtain such an obstruction from the allowed first-principles arguments.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified partial lemmas.
COMPLETENESS_SCORE: 18/100 for the original question.
ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the lower bound h(n)≥(n−1)/3; 0/100 for a proof of h(n)/n→∞.
RESOURCE_USAGE: 12 strategies scanned, 3 main branches developed, 5 verified lemmas/observations, no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

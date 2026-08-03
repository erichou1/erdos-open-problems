# Erdős Problem #155 [unsolved] 35%

---

## ChatGPT Response

Formalization

Let a finite set A⊂Z be Sidon if

a+b=c+d,a,b,c,d∈A

implies the unordered pairs are equal:

{a,b}={c,d}.

Define

F(N)=max{∣A∣:A⊆{1,…,N}, A Sidon}.

The statement is:

∀k≥1 ∃N
0
	​

 ∀N≥N
0
	​

,F(N+k)≤F(N)+1.

Its negation is:

∃k≥1 ∀N
0
	​

 ∃N≥N
0
	​

,F(N+k)≥F(N)+2.

Since F(N+1)≤F(N)+1 is immediate by deleting the possible new element N+1, the issue is whether two jumps can occur inside a fixed-length interval infinitely often.

Threshold reformulation

Define the threshold function

G(r)=min{N:F(N)≥r}.

Equivalently, G(r) is the smallest interval length needed to contain a Sidon set of size r.

Then

F(N)=max{r:G(r)≤N}.

Also G(r+1)>G(r). Indeed, F(N+1)≤F(N)+1, so F cannot jump by two at a single point.

Now fix k. The original property for this k is equivalent to

∃r
0
	​

 ∀r≥r
0
	​

,G(r+1)−G(r)≥k.

Proof:

If eventually G(r+1)−G(r)≥k, then for large N, set r=F(N)+1. Since N<G(r),

N+k<G(r)+k≤G(r+1),

so F(N+k)<r+1=F(N)+2, hence F(N+k)≤F(N)+1.

Conversely, if infinitely often

G(r+1)−G(r)≤k−1,

take

N=G(r)−1.

Then F(N)=r−1, while

N+k=G(r)−1+k≥G(r+1),

so

F(N+k)≥r+1=F(N)+2.

Therefore the original problem is exactly equivalent to proving

G(r+1)−G(r)→∞.
Diameter version

Let

L(r)=min{maxA−minA:∣A∣=r, A⊂Z, A Sidon}.

Then

G(r)=L(r)+1.

So the original problem is exactly equivalent to

L(r+1)−L(r)→∞.

This is the cleanest internal reformulation.

Verified lemmas
Lemma 1: difference uniqueness

For a finite set A⊂Z, A is Sidon iff all positive differences a−b, a>b, are distinct.

If

a−b=c−d>0,

then

a+d=c+b.

Sidonicity forces {a,d}={c,b}, which forces (a,b)=(c,d). Conversely, if two pair-sums are equal but the unordered pairs differ, rearranging gives two distinct equal positive differences. Thus the two formulations are equivalent.

Lemma 2: crude lower bound

A Sidon set of size r has

(
2
r
	​

)

distinct positive differences. If its diameter is D, those differences lie in {1,…,D}. Hence

L(r)≥(
2
r
	​

).

This proves quadratic growth of L(r), but by itself it does not imply

L(r+1)−L(r)→∞,

because a quadratically growing sequence may still have infinitely many small local increments.

Lemma 3: superadditivity

For p,q≥1,

L(p+q−1)≥L(p)+L(q).

Take an optimal Sidon set

a
1
	​

<a
2
	​

<⋯<a
p+q−1
	​

.

The first p elements form a Sidon set, so

a
p
	​

−a
1
	​

≥L(p).

The last q elements

a
p
	​

<a
p+1
	​

<⋯<a
p+q−1
	​


form a Sidon set, so

a
p+q−1
	​

−a
p
	​

≥L(q).

Adding gives

a
p+q−1
	​

−a
1
	​

≥L(p)+L(q).

Thus

L(p+q−1)≥L(p)+L(q).

A useful consequence is

L(r+s)−L(r)≥L(s+1).

Using L(s+1)≥(
2
s+1
	​

),

L(r+s)−L(r)≥
2
s(s+1)
	​

.

So in any block of s consecutive gaps

L(r+1)−L(r),…,L(r+s)−L(r+s−1),

the average gap is at least

2
s+1
	​

.

This proves that large gaps occur frequently. It does not prove that every sufficiently late gap is large.

Lemma 4: no arbitrarily long runs of small gaps

Fix k. Suppose

L(i+1)−L(i)≤k−1

for every i=r,r+1,…,r+s−1. Then

L(r+s)−L(r)≤s(k−1).

But Lemma 3 gives

L(r+s)−L(r)≥
2
s(s+1)
	​

.

Therefore

2
s(s+1)
	​

≤s(k−1),

so

s+1≤2k−2,

hence

s≤2k−3.

Thus, for fixed k, there cannot be 2k−2 consecutive bad gaps. However, this still allows isolated bad gaps infinitely often.

Lemma 5: the claim holds for k=1 and k=2

For k=1, the inequality

F(N+1)≤F(N)+1

is immediate.

For k=2, it suffices to prove

L(r+1)−L(r)≥2

for all r≥2.

Suppose A={0=a
1
	​

<a
2
	​

<⋯<a
r+1
	​

=D} is an optimal Sidon set of size r+1, so D=L(r+1). If

L(r+1)−L(r)≤1,

then deleting a
1
	​

 gives an r-element Sidon set of diameter D−a
2
	​

, so

D−a
2
	​

≥L(r).

Thus

a
2
	​

≤D−L(r)≤1,

so a
2
	​

=1.

Similarly, deleting a
r+1
	​

 gives

a
r
	​

≥L(r),

so

D−a
r
	​

≤1,

hence a
r
	​

=D−1.

For r+1≥4, this gives two distinct pairs with difference 1:

a
2
	​

−a
1
	​

=1,a
r+1
	​

−a
r
	​

=1,

contradicting the Sidon difference condition.

The remaining small case r=2 has

L(2)=1,L(3)=3,

so

L(3)−L(2)=2.

Therefore

L(r+1)−L(r)≥2

for all r≥2, and hence

F(N+2)≤F(N)+1

for all sufficiently large N, in fact for all relevant N.

Main unresolved target after reductions

The full statement is equivalent to:

L(r+1)−L(r)→∞.
	​


The established tools prove:

L(r)≥(
2
r
	​

),

and

L(r+s)−L(r)≥L(s+1),

and they imply large gaps occur in every long enough block. But they do not rule out infinitely many isolated bounded gaps.

To disprove the original statement, it would be enough to find some fixed K and infinitely many r such that

L(r+1)−L(r)≤K.

To prove the original statement, one must rule this out for every fixed K.

Boundary structure of a bad gap

Assume for some fixed K that

L(r+1)−L(r)≤K.

Let

A={0=a
1
	​

<a
2
	​

<⋯<a
r+1
	​

=D}

be an optimal Sidon set of size r+1, with D=L(r+1).

Deleting a
1
	​

 gives

D−a
2
	​

≥L(r),

so

a
2
	​

≤D−L(r)≤K.

Deleting a
r+1
	​

 gives

a
r
	​

≥L(r),

so

D−a
r
	​

≤K.

Thus every bounded bad gap forces an optimal set to have a point within K of the left endpoint and a point within K of the right endpoint.

So if infinitely many bad gaps exist for fixed K, then after passing to an infinite subsequence there are fixed integers

α,β∈{1,…,K}

such that infinitely many optimal Sidon sets have the form

0,α,…,D−β,D.

Since equal positive differences are forbidden, for all sufficiently large such examples,

α

=β.

Also, no other pair in the set may have difference α or β.

This is a genuine structural restriction, but within this session I could not turn it into either:

a contradiction for large r,

or

a construction showing infinitely many such optimal sets exist.
Strategy audit
Strategy	Result
Direct monotonicity of F	proves only F(N+1)≤F(N)+1
Threshold reformulation	gives exact equivalence to G(r+1)−G(r)→∞
Diameter reformulation	gives exact equivalence to L(r+1)−L(r)→∞
Difference counting	proves L(r)≥(
2
r
	​

), insufficient locally
Superadditivity	proves large gaps occur frequently, not eventually everywhere
Bad-gap contradiction	gives endpoint clustering, no contradiction obtained
Induction on r	no inductive monotonicity of gaps proved
Compactness / fixed profile	reduces to fixed endpoint profiles (α,β), unresolved
Counterexample construction	would need infinitely many optimal rulers with bounded gap; not achieved
Reflection symmetry	swaps α,β, gives no new contradiction
Density of bad gaps	bad gaps cannot occur in long consecutive runs, but may be isolated
Auxiliary forbidden-difference graph	finite forbidden differences do not by themselves bound the size
Dependency graph

Verified:

Sidon⟺unique positive differences.
L(r)≥(
2
r
	​

).
L(p+q−1)≥L(p)+L(q).
Original statement⟺L(r+1)−L(r)→∞.
L(r+1)−L(r)≥2(r≥2).

Therefore verified:

F(N+1)≤F(N)+1,

and

F(N+2)≤F(N)+1.

Not verified:

L(r+1)−L(r)→∞.
Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified reductions and lemmas.

COMPLETENESS_SCORE: 35/100 for the original problem, because the exact core statement was reduced to L(r+1)−L(r)→∞, but not proved or disproved.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the established lemmas; 0/100 for the full claim because no complete proof or disproof was obtained.

RESOURCE_USAGE: roughly 100% of the allocated reasoning budget; 12 strategies considered; 5 verified lemmas; 3 main failed proof routes.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

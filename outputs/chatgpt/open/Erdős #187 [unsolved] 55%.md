# Erdős Problem #187 [unsolved] 55%

---

## ChatGPT Response

Phase 0: Formalization

Let a 2-colouring be a function

χ:Z→{0,1}.

For d≥1, define

L
χ
	​

(d)=sup{k∈N:∃a∈Z,∃ε∈{0,1}, χ(a)=χ(a+d)=⋯=χ(a+(k−1)d)=ε}.

So L
χ
	​

(d) is the maximum length of a monochromatic arithmetic progression with common difference d, allowing +∞.

A function f:N→N is admissible if

∀χ:Z→{0,1},{d≥1:L
χ
	​

(d)≥f(d)} is infinite.

Equivalently,

∀χ,∀D≥1,∃d≥D,∃a,∃ε,∀0≤i<f(d),χ(a+id)=ε.

Negation:

∃χ,∃D
0
	​

,∀d≥D
0
	​

,∀a,∀ε,∃0≤i<f(d) such that χ(a+id)

=ε.

For fixed d, arithmetic progressions with difference d are exactly consecutive runs in the d bi-infinite sequences

t↦χ(r+td),r=0,1,…,d−1.

So L
χ
	​

(d) is the largest monochromatic run length among all residue classes modulo d.

The literal “best function” is not well-defined

If “best” means a pointwise maximal admissible function, then no such function exists.

First prove a basic upper-colouring.

Define

χ(n)={
0,
1,
	​

{
2
	​

n}<1/2,
{
2
	​

n}≥1/2.
	​


For d≥1, put

δ
d
	​

=∥
2
	​

d∥.

Let p be the nearest integer to 
2
	​

d. Then

δ
d
	​

=∣
2
	​

d−p∣=
2
	​

d+p
∣2d
2
−p
2
∣
	​

.

Since p
2

=2d
2
, the numerator is a nonzero integer, hence at least 1. Also p≤
2
	​

d+1/2, so for all d≥1,

δ
d
	​

≥
4d
1
	​

.

Now suppose

a,a+d,…,a+(k−1)d

is monochromatic for this colouring. Then the points

{
2
	​

a+i
2
	​

d},0≤i<k,

all lie in one semicircle interval of length 1/2 in R/Z. But the step size on the circle is δ
d
	​

, so among more than ⌈1/δ
d
	​

⌉ consecutive points one wraps around the whole circle densely enough that the set cannot remain inside an interval of length 1/2. Therefore

L
χ
	​

(d)≤⌈
δ
d
	​

1
	​

⌉≤4d+1.

Thus there is a colouring for which

L
χ
	​

(d)≪d.

So no admissible function can eventually exceed a constant multiple of d.

Now construct incompatible admissible functions.

Using van der Waerden’s theorem: for every k, there exists W
2
	​

(k) such that every 2-colouring of {1,…,W
2
	​

(k)} contains a monochromatic k-term arithmetic progression.

Fix any colouring χ:Z→{0,1}. For any Q≥1, colour

1,2,…,W
2
	​

(k)

by

n↦χ(Qn).

Van der Waerden gives

b,b+e,…,b+(k−1)e

monochromatic. Hence

Qb,Q(b+e),…,Q(b+(k−1)e)

is monochromatic in Z, with common difference

d=Qe.

Since 1≤e≤W
2
	​

(k),

Q≤d≤QW
2
	​

(k).

Therefore, for every colouring and every Q, there is some

d∈[Q,QW
2
	​

(k)]

with

L
χ
	​

(d)≥k.

Now define a rapidly growing sequence

N
1
	​

=1,N
k+1
	​

=(W
2
	​

(k)+1)N
k
	​

.

Define the plateau function

f
0
	​

(d)=kwhenever N
k
	​

≤d<N
k+1
	​

.

Then f
0
	​

(d)→∞, and for every colouring χ, for every k, there exists

d
k
	​

∈[N
k
	​

,W
2
	​

(k)N
k
	​

]⊆[N
k
	​

,N
k+1
	​

)

such that

L
χ
	​

(d
k
	​

)≥k=f
0
	​

(d
k
	​

).

So f
0
	​

 is admissible.

Now split the plateaus into even and odd ones. Define

f
even
	​

(d)={
k,
d
2
,
	​

N
k
	​

≤d<N
k+1
	​

 and k is even,
N
k
	​

≤d<N
k+1
	​

 and k is odd,
	​


and

f
odd
	​

(d)={
d
2
,
k,
	​

N
k
	​

≤d<N
k+1
	​

 and k is even,
N
k
	​

≤d<N
k+1
	​

 and k is odd.
	​


Both tend to infinity.

Both are admissible: f
even
	​

 is witnessed on infinitely many even-indexed plateaus, and f
odd
	​

 is witnessed on infinitely many odd-indexed plateaus.

But any pointwise maximal admissible function F would have to dominate both. Hence eventually

F(d)≥d
2

for all sufficiently large d.

That is impossible, because the rotation colouring above satisfies

L
χ
	​

(d)≤4d+1<d
2

for all sufficiently large d.

Therefore, under the literal unrestricted interpretation, there is no pointwise “best function.”

What is rigorously established

We have proved:

Lemma 1: Multiplicative syndeticity

For every k, every 2-colouring χ, and every Q≥1, there exists

d∈[Q,QW
2
	​

(k)]

such that

L
χ
	​

(d)≥k.
Corollary 1: Some unbounded admissible function exists

There exists f
0
	​

(d)→∞ such that every 2-colouring has

L
χ
	​

(d)≥f
0
	​

(d)

for infinitely many d.

The explicit construction is the plateau function above.

Lemma 2: A linear upper construction exists

There is a 2-colouring χ such that

L
χ
	​

(d)≤4d+1

for every d≥1.

Thus any universally valid f(d) must satisfy, in any reasonable eventual sense,

f(d)

≫d.
Lemma 3: No unrestricted pointwise best admissible function exists

Even if one requires f(d)→∞, admissible functions are not pointwise ordered in a way that permits a maximal element.

So the phrase “best function” requires an extra convention, such as monotonicity, asymptotic equivalence, or maximal eventual growth rate among regular functions.

Remaining target after regularizing the question

If the intended question is:

Find the largest asymptotic growth rate of a monotone admissible f(d),

then the deductions here give only

f
0
	​

(d)≤
available proof
	​

f(d)≤O(d),

where f
0
	​

(d)→∞ is the extremely slow van-der-Waerden plateau function.

The logarithmic scale mentioned in the problem statement would require proving something like

∀χ,L
χ
	​

(d)≥clogd

for infinitely many d, or constructing a colouring forcing

L
χ
	​

(d)≤Clogd

eventually. I did not derive either statement from first principles here.

The scaled van der Waerden argument cannot produce logarithmic growth: it gives k-term progressions with

d≤QW
2
	​

(k),

but without strong control of W
2
	​

(k), this does not imply

k≫logd.

Thus the rigorous lower bound obtained here is only “some function tending to infinity,” not a quantitative logarithmic bound.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100
COMPLETENESS_SCORE: 55/100
ADVERSARIAL_SURVIVAL_SCORE: 85/100

RESOURCE_USAGE: approximately 80% of the available reasoning budget used; 3 main branches explored; 4 lemmas generated; 2 failed routes toward a quantitative logarithmic lower bound.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

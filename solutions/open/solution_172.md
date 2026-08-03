# Erdős Problem #172 [unsolved] 28%

---

## ChatGPT Response

Phase 0: Complete formalization

Let [r]={1,…,r}. A finite colouring of N is a map

c:N→[r]

for some positive integer r.

For a finite set A⊂N, define

FS(A)={
a∈B
∑
	​

a:∅

=B⊆A},
FP(A)={
a∈B
∏
	​

a:∅

=B⊆A}.

Including singleton products does not change the strength, because singletons already appear in FS(A).

The target statement is:

∀r≥1 ∀c:N→[r] ∀k≥1 ∃A⊂N∣A∣≥kandc is constant on FS(A)∪FP(A).
	​


Equivalently, for every k, there exist distinct positive integers a
1
	​

,…,a
k
	​

 and a colour γ∈[r] such that for every nonempty I⊆{1,…,k},

c(
i∈I
∑
	​

a
i
	​

)=γ,c(
i∈I
∏
	​

a
i
	​

)=γ.
Negation

The negation is:

∃r≥1 ∃c:N→[r] ∃K≥1

such that for every finite A⊂N with ∣A∣≥K, the set

FS(A)∪FP(A)

is not monochromatic.

Equivalently,

∃r,c,K ∀A⊂N, ∣A∣≥K, ∃x,y∈FS(A)∪FP(A)c(x)

=c(y).
Boundary cases

For k=1, the statement is trivial: choose any a∈N, and FS({a})∪FP({a})={a}.

For k=2, the statement asks for x

=y such that

x, y, x+y, xy

all have the same colour. Thus the full problem contains this as its first nontrivial finite case.

For one colour, the statement is trivial for every k.

Cardinality estimates

If ∣A∣=k, then

∣FS(A)∣≤2
k
−1,∣FP(A)∣≤2
k
−1,

so

∣FS(A)∪FP(A)∣≤2
k+1
−2.

Collisions may occur, for example if products equal sums, but no collision can hurt monochromaticity.

Hypergraph formulation

For each k, define a k-set A⊂N to be good if FS(A)∪FP(A) is monochromatic. The problem asks whether every finite colouring produces good k-sets for all k.

The negation says that some colouring has bounded good-set size.

Phase 1: Breadth-first proof search

Here are independent strategies and their status after first-principles examination.

Strategy	Idea	Hidden assumption	Main obstacle	Status
Direct construction	Build a
1
	​

,…,a
k
	​

 recursively	Need colour class stable under many additive/multiplicative constraints	Arbitrary colour classes need not be stable under shifts or dilations	Failed
Contradiction	Assume maximal good set size K−1, force extension	Need a way to extend a good set	Extension requires simultaneous constraints z+s and zp	Gap
Induction on k	Extend good k-set to good k+1-set	Need common colour intersection nonempty	No density or syndeticity guaranteed	Failed
Ramsey on variables	Colour tuples by colours of their sums/products	Ramsey gives structured homogeneous tuples	Homogeneity of tuples does not force all polynomial values into one colour	Incomplete
Powers b
t
i
	​

	Products become sums of exponents	Sums become base-b digit masks	Need simultaneous control of two unrelated induced colourings	Major gap
Modular obstruction search	Try colourings mod m	Maybe residues obstruct	Multiples of m defeat all residue colourings	No obstruction
p-adic obstruction search	Colour by v
p
	​

(n)modq	Maybe valuation parity obstructs	Rapid powers defeat it	No obstruction
Digit-sum obstruction	Colour by binary digit-sum parity	Sums of powers alternate	Other choices such as 3,6 already defeat small cases	No proof
Density	Use one colour class with positive upper density	Dense sets often contain additive patterns	Products are not controlled by density alone	Gap
Compactness	Large finite good sets might imply infinite good set	Infinite extraction from arbitrary finite cliques	False in general hypergraphs	Failed
Diagonal counterexample	Build colouring to kill all large A one by one	Need finite number of colours and permanent consistency	Later recolouring can revive earlier patterns	Gap
Auxiliary algebra	Encode sums and products in a larger semiring	Need transfer back to N	No embedding preserves both freely	Gap

Top three branches pursued:

Powers/exponent coding.

Recursive extension of good sets.

Counterexample search through natural invariant colourings.

Phase 2: New definitions and useful invariants
Definition 1: Good set

A finite set A⊂N is c-good if FS(A)∪FP(A) is monochromatic.

This is the direct object.

Definition 2: Extension profile

If A is already good with colour γ, define the extension requirements for a new element z∈
/
A:

c(z)=γ,
c(z+
a∈B
∑
	​

a)=γfor all B⊆A,
c(z
a∈B
∏
	​

a)=γfor all B⊆A.

Thus z must lie in a finite intersection of additive shifts and multiplicative preimages of the same colour class.

Motivation: this isolates exactly why induction is difficult.

Definition 3: Exponent-coded candidate

Fix b≥2. For T={t
1
	​

,…,t
k
	​

}⊂N, define

A
T
	​

={b
t
:t∈T}.

Then

FP(A
T
	​

)={b
∑
t∈U
	​

t
:∅

=U⊆T},

while

FS(A
T
	​

)={
t∈U
∑
	​

b
t
:∅

=U⊆T}.

This turns product control into additive control on exponents, but leaves sum control as base-b digit-mask control.

Definition 4: Local invariant colouring

A colouring is local-invariant if it depends only on finitely many congruence and valuation data, for example

nmodm,v
p
1
	​

	​

(n)modq
1
	​

,…,v
p
s
	​

	​

(n)modq
s
	​

.

These colourings are natural candidates for counterexamples, so they should be tested first.

Verified partial results
Lemma 1: Pure congruence colourings cannot disprove the statement

Assume c(n) depends only on nmodm. Then for every k, there is a c-good set A of size k.

Proof.

Choose

A={m,2m,…,km}.

Every nonempty finite sum of elements of A is divisible by m. Every nonempty finite product of elements of A is also divisible by m. Hence every element of FS(A)∪FP(A) is congruent to 0modm, so every such element has the same colour.

Thus congruence colourings are not counterexamples. □

Lemma 2: Single p-adic valuation residue colourings cannot disprove the statement

Assume

c(n)=ϕ(v
p
	​

(n)modq)

for some prime p, integer q≥1, and finite map ϕ. Then for every k, there is a c-good set A of size k.

Proof.

Choose distinct integers

M
1
	​

<⋯<M
k
	​


and put

a
i
	​

=p
qM
i
	​

.

Let

A={a
1
	​

,…,a
k
	​

}.

For any nonempty I⊆{1,…,k}, let m=min
i∈I
	​

M
i
	​

. Then

i∈I
∑
	​

a
i
	​

=p
qm
	​

1+
i∈I
M
i
	​

>m
	​

∑
	​

p
q(M
i
	​

−m)
	​

.

The parenthesized factor is congruent to 1modp, hence is not divisible by p. Therefore

v
p
	​

(
i∈I
∑
	​

a
i
	​

)=qm≡0modq.

Also,

v
p
	​

(
i∈I
∏
	​

a
i
	​

)=q
i∈I
∑
	​

M
i
	​

≡0modq.

Thus every element of FS(A)∪FP(A) has valuation 0modq, hence the same colour. □

Lemma 3: Finite local invariant colourings cannot disprove the statement

Suppose c(n) depends only on the data

nmodm,v
p
1
	​

	​

(n)modq
1
	​

,…,v
p
s
	​

	​

(n)modq
s
	​

.

Then for every k, there exists a c-good set A of size k.

Proof.

Let

R=m
ℓ=1
∏
s
	​

p
ℓ
q
ℓ
	​

	​

.

Choose

A={R
M
1
	​

,…,R
M
k
	​

}

with

M
1
	​

<⋯<M
k
	​

.

Every element of A is divisible by m, so every nonempty finite sum and product from A is congruent to 0modm.

For each p
ℓ
	​

,

v
p
ℓ
	​

	​

(R
M
i
	​

)≡0modq
ℓ
	​

.

For products, this remains obvious. For sums, if M
j
	​

 is minimal among the chosen exponents in the sum, then

i∈I
∑
	​

R
M
i
	​

=R
M
j
	​

	​

1+
i∈I
M
i
	​

>M
j
	​

	​

∑
	​

R
M
i
	​

−M
j
	​

	​

.

Because p
ℓ
	​

∣R, the parenthesized factor is 1modp
ℓ
	​

, so it contributes no additional p
ℓ
	​

-adic valuation. Therefore the p
ℓ
	​

-adic valuation of the sum is exactly M
j
	​

v
p
ℓ
	​

	​

(R), divisible by q
ℓ
	​

.

Thus all sums and products have the same entire local-invariant profile, hence the same colour. □

This eliminates a broad family of possible counterexamples, but arbitrary finite colourings need not be local-invariant.

Branch A: Powers and exponent coding

Fix b≥2. Try

A={b
t
1
	​

,…,b
t
k
	​

}.

For U

=∅,

t∈U
∏
	​

b
t
=b
∑
t∈U
	​

t
,

so product colours are controlled by the colouring

d
Π
	​

(U)=c(b
∑
t∈U
	​

t
).

Sums are controlled by

d
Σ
	​

(U)=c(
t∈U
∑
	​

b
t
).

If one could find arbitrarily large T⊂N such that the pair-colouring

U↦(d
Σ
	​

(U),d
Π
	​

(U))

is constant over all nonempty U⊆T, then the desired result would follow. Indeed, for singleton U={t},

d
Σ
	​

({t})=c(b
t
)=d
Π
	​

({t}),

so the two constant coordinates would have to be equal.

However, the required statement is too strong for arbitrary colourings of finite subsets. For example, a colouring of finite sets by ∣U∣mod2 has no two-element T on which all nonempty subsets have the same colour. Therefore a proof through this route would need to use special structure of the induced colourings coming from c, not merely finite Ramsey theory.

Branch A reaches the following gap:

GAP A:

Given c:N→[r], prove that for some base b and arbitrarily large finite T,

c(
t∈U
∑
	​

b
t
)=c(b
∑
t∈U
	​

t
)

is independent of nonempty U⊆T.

I could not prove GAP A from first principles.

Branch B: Recursive extension

Assume A is already good with colour γ. To extend A by one element z, we need

c(z)=γ,
c(z+s)=γfor every s∈FS(A),
c(zp)=γfor every p∈FP(A).

Thus z must lie in

C
γ
	​

∩
s∈FS(A)
⋂
	​

(C
γ
	​

−s)∩
p∈FP(A)
⋂
	​

p
−1
C
γ
	​

,

where

C
γ
	​

={n:c(n)=γ},
C
γ
	​

−s={z:z+s∈C
γ
	​

},
p
−1
C
γ
	​

={z:zp∈C
γ
	​

}.

A finite colouring guarantees that some C
γ
	​

 is infinite, but it does not guarantee that these shifted and dilated intersections are nonempty.

So induction reduces to:

GAP B:

For some good A of colour γ, prove that

C
γ
	​

∩
s∈FS(A)
⋂
	​

(C
γ
	​

−s)∩
p∈FP(A)
⋂
	​

p
−1
C
γ
	​


=∅.

This gap is exactly the simultaneous additive-multiplicative obstruction. I could not close it.

Branch C: Counterexample search

A counterexample would be a finite colouring c and a bound K such that every A with ∣A∣≥K has two elements of FS(A)∪FP(A) of different colours.

Natural candidates fail.

Congruence colourings fail

Already proved by Lemma 1.

Valuation residue colourings fail

Already proved by Lemmas 2 and 3.

Growth-based colourings

One may try colouring by intervals such as

[2
2m
,2
2m+1
)versus[2
2m+1
,2
2m+2
),

but rapidly growing sets can make sums behave like their largest terms, while products jump in a controlled way. I found no rigorous way to force a contradiction for all large A.

Digit-based colourings

Colouring by binary digit-sum parity initially attacks powers of two, since sums of distinct powers have digit-sum equal to the number of summands. But this does not by itself block arbitrary A. Even small examples can avoid the obvious obstruction. For instance, with colour

c(n)=s
2
	​

(n)mod2,

where s
2
	​

(n) is the number of 1's in the binary expansion,

3, 6, 9, 18

all have even binary digit-sum:

3=11
2
	​

,6=110
2
	​

,9=1001
2
	​

,18=10010
2
	​

.

Thus A={3,6} is good for this colouring in the k=2 case.

This does not prove the digit-sum colouring works for arbitrary k, but it defeats the simplest counterexample attempt.

Branch C reaches:

GAP C:

Construct a finite colouring whose monochromatic sum-product good sets have bounded size, or prove that no such construction can exist.

I could not construct such a colouring.

Compactness check

A tempting argument would be:

“If every finite k works, then perhaps an infinite A works.”

This implication is false in general combinatorial structures.

Example: partition N into disjoint finite blocks B
1
	​

,B
2
	​

,… with ∣B
n
	​

∣=n. Put edges only inside each B
n
	​

. Then there are arbitrarily large finite cliques, but no infinite clique.

Therefore, even if arbitrarily large finite good sets exist, an infinite good set does not follow by a bare compactness argument.

So finite and infinite versions are logically different unless extra structure is proved.

Dependency graph of verified results
Definitions of FS,FP
⇓

Lemma 1: congruence colourings admit arbitrary good sets.

⇓

Lemma 2: single valuation residue colourings admit arbitrary good sets.

⇓

Lemma 3: finite local invariant colourings admit arbitrary good sets.

These lemmas are fully proved, but they do not imply the original theorem because an arbitrary finite colouring need not be determined by finitely many congruence or valuation invariants.

The original theorem remains dependent on at least one unresolved gap equivalent in strength to a genuinely simultaneous additive-multiplicative recurrence principle.

Adversarial verification
Attack on Lemma 1

Potential issue: products might not stay 0modm.
Resolution: every product contains at least one factor divisible by m, so the product is divisible by m.

Lemma survives.

Attack on Lemma 2

Potential issue: the valuation of a sum may be larger than the minimum valuation because of cancellation.
Resolution: after factoring out the minimal power p
qm
, the remaining factor is 1modp, so no additional p-adic factor appears.

Lemma survives.

Attack on Lemma 3

Potential issue: several primes may interfere.
Resolution: for each chosen prime p
ℓ
	​

, the same minimum-exponent argument works independently because the bracket is 1modp
ℓ
	​

.

Lemma survives.

Attack on Branch A

The branch assumes one can homogenize all finite subsets of T. This is false for arbitrary finite-subset colourings. The induced colouring from c may have more structure, but that structure was not enough to prove the needed homogenization.

Branch A fails.

Attack on Branch B

The branch assumes a good set can be extended. The exact extension condition is a finite intersection of shifted and dilated colour classes. Finite colourings alone do not imply such intersections are nonempty.

Branch B fails.

Attack on Branch C

No counterexample colouring was produced. The tested natural colourings all admit large good sets or at least fail in small cases.

Branch C fails to disprove the statement.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92/100 for the verified partial lemmas and formal reductions.

COMPLETENESS_SCORE: 28/100 for the original problem.

ADVERSARIAL_SURVIVAL_SCORE: 85/100 for the partial results; 0/100 for a complete proof or disproof, because none was obtained.

RESOURCE_USAGE: approximately 100% of this response’s reasoning budget; 3 main branches explored; 3 verified lemmas generated; 3 major unresolved gap nodes isolated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

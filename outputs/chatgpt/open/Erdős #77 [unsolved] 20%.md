# Erdős Problem #77 [unsolved] 20%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let R(k) be the least n∈N such that every red/blue colouring of E(K
n
	​

) contains a red K
k
	​

 or a blue K
k
	​

.

Target:

Find 
k→∞
lim
	​

R(k)
1/k
.

Equivalent logarithmic form: define

a
k
	​

=logR(k).

Then the target is to determine whether

k→∞
lim
	​

k
a
k
	​

	​


exists, and if so compute

exp(
k→∞
lim
	​

k
a
k
	​

	​

).

Negation of existence:

∃ε>0 ∀K ∃m,n≥K
	​

R(m)
1/m
−R(n)
1/n
	​

≥ε.

Equivalently,

k→∞
liminf
	​

R(k)
1/k
<
k→∞
limsup
	​

R(k)
1/k
.
Verified elementary bounds
Upper bound

Define the two-parameter Ramsey number R(s,t) as the least n such that every red/blue colouring of K
n
	​

 contains a red K
s
	​

 or a blue K
t
	​

.

Claim:

R(s,t)≤R(s−1,t)+R(s,t−1).

Proof: take a vertex v. Among the other vertices, either at least R(s−1,t) are joined to v in red, or at least R(s,t−1) are joined to v in blue. In the first case, the red-neighbour set contains either a red K
s−1
	​

, which together with v gives a red K
s
	​

, or a blue K
t
	​

. The second case is symmetric.

With boundary values R(1,t)=R(s,1)=1, induction gives

R(s,t)≤(
s−1
s+t−2
	​

).

Therefore

R(k)=R(k,k)≤(
k−1
2k−2
	​

)≤4
k−1
.

Hence

k→∞
limsup
	​

R(k)
1/k
≤4.
Lower bound

Colour each edge of K
n
	​

 independently red or blue with probability 1/2.

For a fixed k-set of vertices, the probability it is monochromatic is

2⋅2
−(
2
k
	​

)
=2
1−(
2
k
	​

)
.

So the expected number of monochromatic K
k
	​

’s is

(
k
n
	​

)2
1−(
2
k
	​

)
.

If this expectation is <1, then at least one colouring has no monochromatic K
k
	​

, so R(k)>n.

For any fixed c<
2
	​

, take n=⌊c
k
⌋. Then

(
k
n
	​

)2
1−(
2
k
	​

)
≤
k!
c
k
2
	​

2
1−k(k−1)/2
=
k!
2
1+k/2
	​

(
2
	​

c
	​

)
k
2
.

Since c/
2
	​

<1, this tends to 0. Hence for all sufficiently large k,

R(k)>c
k
.

Therefore

k→∞
liminf
	​

R(k)
1/k
≥
2
	​

.

So the fully verified conclusion is

2
	​

≤
k→∞
liminf
	​

R(k)
1/k
≤
k→∞
limsup
	​

R(k)
1/k
≤4.
	​

Proof-search attempts toward the actual limit

I tested the following first-principles routes.

Strategy	Goal	Result
Direct monotonicity	Use R(k)≤R(k+1) to force root convergence	Fails: monotonicity of R(k) does not imply monotonicity of R(k)
1/k
.
Submultiplicativity	Prove R(k+ℓ)≤CR(k)R(ℓ)	No verified inequality strong enough.
Supermultiplicativity	Prove R(k+ℓ)≥cR(k)R(ℓ)	Product constructions give lower bounds of different shape, not enough for convergence.
Fekete lemma route	Show logR(k) is approximately subadditive	Main missing lemma: no verified near-subadditivity.
Random lower bounds	Improve 
2
	​

 to a candidate value	Gives lower exponential bounds but not a matching limit.
Recursive upper bounds	Refine R(s,t)≤R(s−1,t)+R(s,t−1)	Gives exponential upper bounds but not convergence.
Diagonalization	Construct oscillating colourings	No construction proves nonexistence of the limit.
Compactness	Pass to limiting infinite colourings	Does not directly control exponential growth rate.
Density increment	Force a large structured monochromatic region	Produces possible upper-bound mechanisms, not a limit.
Induction on k	Relate R(k+1) sharply to R(k)	Available inequalities are too coarse.
Auxiliary invariant	Track colour-pattern profiles of vertices	No invariant found that determines exponential rate.
Counterexample search	Try to make R(k)
1/k
 oscillate	No valid construction, since R(k) is fixed by a universal extremal property.

The central unresolved target became:

Prove or disprove that 
k
logR(k)
	​

 converges.

Every attempted reduction led back to needing a structural inequality relating R(k+ℓ) to R(k) and R(ℓ) with subexponential error. I found no first-principles proof of such an inequality.

Final result

I did not obtain a proof of existence, a proof of nonexistence, or a value for the limit.

The strongest rigorously established statement from this offline derivation is:

2
	​

≤
k→∞
liminf
	​

R(k)
1/k
≤
k→∞
limsup
	​

R(k)
1/k
≤4.
	​


The requested value of

k→∞
lim
	​

R(k)
1/k

was not determined.

Confidence report

PROOF_CONFIDENCE: 96/100
COMPLETENESS_SCORE: 20/100
ADVERSARIAL_SURVIVAL_SCORE: 90/100

RESOURCE_USAGE: approximately 100% of the available proof-search budget for this response; 12 strategies explored; 2 fully verified lemmas; multiple failed proof routes; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

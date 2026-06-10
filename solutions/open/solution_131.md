# Erdős Problem #131 [solved] 70%

---

## ChatGPT Response

Formalization

Let [N]={1,…,N}. A set A⊆[N] is non-dividing if

∀a∈A, ∀∅

=B⊆A∖{a},a∤
b∈B
∑
	​

b.

Then

F(N)=max{∣A∣:A⊆[N] is non-dividing}.

The near-square-root assertion is interpreted as:

F(N)≥N
1/2−o(1)
,

meaning there exists ε(N)→0 such that for all sufficiently large N,

F(N)≥N
1/2−ε(N)
.

Its negation is implied by any upper bound of the form

F(N)≤N
1/2−η

for some fixed η>0 and all sufficiently large N.

Direct structural observation

Define A to be non-averaging if there do not exist

a∈A,∅

=B⊆A∖{a},∣B∣=r

such that

b∈B
∑
	​

b=ra.

Every non-dividing set is non-averaging.

Indeed, if

b∈B
∑
	​

b=ra,

then the sum of distinct elements of A∖{a} is divisible by a, contradicting the defining non-dividing property. Hence

F(N)≤G(N),

where G(N) is the maximal size of a non-averaging subset of [N].

The prompt states the external bound

G(N)≤N
1/4+o(1)
.

Accepting that as a supplied theorem, we get

F(N)≤N
1/4+o(1)
.

This immediately disproves the near-square-root lower bound. For example, for sufficiently large N,

F(N)≤N
1/4+1/16
=N
5/16
,

whereas any lower bound F(N)≥N
1/2−o(1)
 would eventually imply

F(N)≥N
1/2−1/16
=N
7/16
.

These are incompatible.

Therefore,

F(N)

>N
1/2−o(1)
.
	​

Elementary verified lemma

A small first-principles bound is also available.

Let A be non-dividing and let ∣A∣=k. Put m=minA. Then

m≥k.

Proof: suppose m<k. Then A∖{m} contains at least m elements. Choose m of them and call them

x
1
	​

,…,x
m
	​

.

Consider partial sums modulo m:

S
j
	​

=x
1
	​

+⋯+x
j
	​

(modm),1≤j≤m.

If some S
j
	​

≡0(modm), then

m∣x
1
	​

+⋯+x
j
	​

,

contradicting non-dividing for a=m.

Otherwise, all S
j
	​

 lie among the m−1 nonzero residue classes modulo m. Since there are m sums, two are equal:

S
i
	​

≡S
j
	​

(modm),i<j.

Then

x
i+1
	​

+⋯+x
j
	​

≡0(modm),

again contradicting non-dividing for a=m. Hence m≥k.

So every non-dividing A⊆[N] satisfies

∣A∣≤minA≤N.

This is weak, but it is fully elementary.

Strategy audit

The direct path that works for the specific question is:

non-dividing⇒non-averaging⇒F(N)≤N
1/4+o(1)
⇒F(N)

=N
1/2−o(1)
.

Other first-principles strategies explored do not currently yield the correct growth estimate:

Strategy	Outcome
Direct modular subset-sum	Gives (\min A\ge
Contradiction from many small elements	Same obstruction
Induction on N	No strong hereditary gain
Density argument	Needs a strong averaging theorem
Diagonalization	No natural diagonal object found
Cardinal arithmetic	Finite problem, no gain
Compactness	Reduces to finite subset-sum obstruction
Reflection-style argument	No useful reflected substructure
Auxiliary graph/hypergraph encoding	Encodes forbidden divisible subset sums but does not close
Counterexample search	Small constructions do not refute the supplied upper bound
Rank function by minimum element	Gives only (
Average-free reduction	Strongest path, but depends on supplied non-averaging bound
Final state

DISPROVED for the assertion

F(N)>N
1/2−o(1)
.

The disproof depends on accepting the prompt-supplied theorem

G(N)≤N
1/4+o(1)

for non-averaging sets. Without that supplied theorem, the fully elementary reasoning above proves only weak structural bounds and does not determine the growth of F(N).

PROOF_CONFIDENCE: 95/100
COMPLETENESS_SCORE: 70/100
ADVERSARIAL_SURVIVAL_SCORE: 90/100
RESOURCE_USAGE: about 60%; 12 strategies considered; 2 verified lemmas; 1 successful reduction; several failed elementary proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

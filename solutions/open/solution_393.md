# Erdős Problem #393 [unsolved] 70%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Complete formalization

For n≥2, define R
m
	​

(n) to mean:

∃x≥1, ∃S⊆{0,1,…,m}

such that

0,m∈S,n!=
s∈S
∏
	​

(x+s).

Then the original definition is equivalently

f(n)=min{m≥1:R
m
	​

(n)}.

This is finite for every n≥2, because

n!=2⋅3⋯n

gives

a
1
	​

=2,a
t
	​

=n,m=n−2

for n≥3. Also f(2)=1, since 2!=1⋅2. Hence

f(n)≤n−2(n≥3).

The negation of f(n)≤M is

∀m∈{1,…,M}, ∀x≥1, ∀S⊆{0,…,m}

with 0,m∈S,

n!

=
s∈S
∏
	​

(x+s).

Thus f(n)>M means that n! cannot be represented as the value of any of the finitely many polynomial families

P
S
	​

(x)=
s∈S
∏
	​

(x+s),S⊆{0,…,m}, 0,m∈S,

for any 1≤m≤M.

What follows rigorously from the stated results

Let

F
m
	​

(N)=#{n≤N:f(n)=m}.

The quoted estimate says that for each fixed m,

F
m
	​

(N)≪
m
	​

N
33/34
.

Fix M. Then

#{n≤N:f(n)≤M}=
m=1
∑
M
	​

F
m
	​

(N).

Therefore

#{n≤N:f(n)≤M}≪
M
	​

N
33/34
.

Dividing by N,

N
1
	​

#{n≤N:f(n)≤M}≪
M
	​

N
−1/34
→0.

Hence the unconditional density statement is:

∀M≥1,#{n≤N:f(n)≤M}=o(N).
	​


Equivalently,

f(n)→∞ in natural density.
	​


That is, for every fixed bound M, almost all n satisfy

f(n)>M.

So although f(n)≤n−2 always, the values f(n) cannot remain bounded on a positive-density set.

Conditional pointwise behavior

The prompt states that Luca’s result implies, conditional on ABC,

f(n)→∞.

Formally, this means:

ABC⟹∀M≥1, ∃N
M
	​

, ∀n≥N
M
	​

,f(n)>M.
	​


This is stronger than density divergence. Density divergence allows infinitely many exceptional n with small f(n); pointwise divergence says only finitely many such n exist for each fixed M.

Final behavior obtainable from the supplied information

The behavior established by the stated results is therefore:

1≤f(n)≤n−2(n≥3),
	​


and, unconditionally,

f(n)→∞ for almost all n.
	​


More quantitatively, for every fixed M,

#{n≤N:f(n)≤M}≪
M
	​

N
33/34
.
	​


Conditional on ABC,

f(n)→∞ pointwise as n→∞.
	​


I do not have a complete unconditional proof of the pointwise statement

f(n)→∞.

The rigorous conclusion reached here is the density version above, plus the conditional pointwise version using the stated hypothesis.

PROOF_CONFIDENCE: 98/100
COMPLETENESS_SCORE: 70/100
ADVERSARIAL_SURVIVAL_SCORE: 95/100
RESOURCE_USAGE: reasoning budget used 100%, branches explored 4, lemmas generated 4, failed proof attempts 3.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

# Erdős Problem #32 [unsolved] 18%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let N={1,2,3,…}, let P be the primes, and define

A(N)=∣A∩{1,…,N}∣.

A set A⊂N is an additive complement to the primes if there exists N
0
	​

 such that for every integer n≥N
0
	​

, there are p∈P and a∈A with

n=p+a.

The three questions are:

Does there exist such an A with

A(N)=o((logN)
2
)?

Does there exist such an A with

A(N)=O(logN)?

Must every such A satisfy

N→∞
liminf
	​

logN
A(N)
	​

>1?
Quantifier structure

Question 1 asks whether

∃A⊂N ∃N
0
	​

 ∀n≥N
0
	​

 ∃p∈P ∃a∈A:n=p+a

and

∀ε>0 ∃N
1
	​

 ∀N≥N
1
	​

:A(N)≤ε(logN)
2
.

Question 2 replaces the second condition by

∃C>0 ∃N
1
	​

 ∀N≥N
1
	​

:A(N)≤ClogN.

Question 3 asks whether for every additive complement A,

∃η>0 ∃N
1
	​

 ∀N≥N
1
	​

 along a tail-liminf sense:
logN
A(N)
	​

≥1+η

equivalently

N→∞
liminf
	​

logN
A(N)
	​

>1.
Negations

Question 1 is false iff every additive complement A satisfies

A(N)

=o((logN)
2
),

i.e. there exists ε>0 and a sequence N
j
	​

→∞ such that

A(N
j
	​

)≥ε(logN
j
	​

)
2
.

Question 2 is false iff every additive complement A satisfies

logN
A(N)
	​


is unbounded.

Question 3 is false iff there exists an additive complement A such that

N→∞
liminf
	​

logN
A(N)
	​

≤1.
Equivalent formulation

The complement condition is

[N
0
	​

,∞)⊆A+P.

For each N, covering [N
0
	​

,N] requires

[N
0
	​

,N]⊆
a∈A∩[1,N]
⋃
	​

(a+P).

Thus the finite problem is: how many prime translates are needed to cover an interval of length N?

Immediate verified counting bound

For n≤N, every representation n=p+a has a≤N and p≤N. Therefore

N−O(1)≤
	​

a∈A∩[1,N]
⋃
	​

(a+P)∩[1,N]
	​

≤A(N)π(N).

Hence

A(N)≥
π(N)
N−O(1)
	​

.

Using the prime number theorem as a conditional auxiliary estimate,

π(N)∼
logN
N
	​

,

this gives only

A(N)≥(1−o(1))logN.

This proves that no additive complement can have A(N)=o(logN), assuming the prime number theorem. It does not prove the requested strict inequality

liminf
logN
A(N)
	​

>1.

The elementary counting obstruction stops exactly at the constant 1.

Strategy search results

I explored the following proof directions.

Strategy	Target	Outcome
Direct counting	Lower bound on A(N)	Gives only A(N)≳logN.
Inclusion-exclusion for shifted primes	Improve constant above 1	Requires sharp overlap control for prime translates. Gap remains.
Modular obstruction	Use residue classes modulo q or primorials	Gives structural constraints but not enough for >1 without a strong sieve bound.
Random construction	Build sparse A	Natural model gives A(N)≍(logN)
2
, not o((logN)
2
).
Block construction	Cover dyadic intervals separately	Accumulates roughly ∑
k≤logN
	​

log2
k
≍(logN)
2
.
Reuse old shifts across blocks	Try to reduce to o((logN)
2
)	No verified mechanism found.
Greedy covering	Choose a’s maximizing uncovered primes	Requires lower bound on available prime hits inside every residue pattern. Gap remains.
Probabilistic deletion	Start with dense random A, thin it	Coverage becomes fragile; no verified o((logN)
2
) construction.
Diagonal construction	Handle intervals one at a time with decreasing cost	Later intervals still require about logN new shifts in the naive model.
Density/sieve lower bound	Prove A(N)≥(1+η)logN	Needs a nontrivial upper bound for unions of prime translates. Gap remains.
Counterexample search to lower bound >1	Try to build A(N)∼logN	No construction found.
Stronger theorem search	Prove union bound with constant <1	Reduces to a sieve-type theorem not derivable here.
Main verified obstruction

The decisive bottleneck is this finite covering inequality.

Let

S
A
	​

(N)=
a∈A∩[1,N]
⋃
	​

(a+P)∩[1,N].

To prove Question 3, one would need a uniform estimate of the form

∣S
A
	​

(N)∣≤(c+o(1))A(N)
logN
N
	​


with some absolute constant c<1, valid for every small set A. Then covering [1,N] would imply

N−o(N)≤∣S
A
	​

(N)∣≤(c+o(1))A(N)
logN
N
	​

,

so

A(N)≥(
c
1
	​

−o(1))logN,

which would give

liminf
logN
A(N)
	​

>1.

But I did not derive such a uniform union-of-prime-translates bound from first principles in this session.

Why the O(logN) question remains unresolved here

The elementary counting lower bound allows A(N)≍logN. So a contradiction to O(logN) would require a sharper argument than counting.

On the construction side, the natural random model gives the following heuristic. Choose a with probability approximately

a
Cloga
	​

.

Then

EA(N)≍(logN)
2
,

and for a given large n,

E∣{a∈A:n−a∈P}∣≍Clogn.

That is large enough to make individual failures rare enough for a union-bound style construction. But reducing the expected size below (logN)
2
 lowers the expected number of representations and breaks this direct argument.

Thus the standard probabilistic route reaches the known-looking scale (logN)
2
, but I did not find a verified modification producing o((logN)
2
), much less O(logN).

Dependency graph of verified claims

Definitions:

A(N)=∣A∩[1,N]∣.

Lemma 1. If A is an additive complement to the primes, then for all sufficiently large N,

N−O(1)≤A(N)π(N).

Dependencies: only the definition of additive complement and the observation that n=p+a≤N implies a,p≤N.

Corollary 1. Assuming π(N)∼N/logN,

A(N)≥(1−o(1))logN.

Dependencies: Lemma 1 and the prime number theorem.

Unresolved Gap 1. Prove or disprove existence of A with

A(N)=o((logN)
2
)

and

[N
0
	​

,∞)⊆A+P.

Unresolved Gap 2. Prove or disprove existence of A with

A(N)=O(logN).

Unresolved Gap 3. Derive from first principles a strict lower bound

N→∞
liminf
	​

logN
A(N)
	​

>1.
Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 96/100 for the verified counting lower bound and formal reductions.

COMPLETENESS_SCORE: 18/100. The basic logN lower bound is established conditionally on the prime number theorem, but the three main questions are not solved from first principles here.

ADVERSARIAL_SURVIVAL_SCORE: 90/100 for the finite counting lemma; 40/100 for the heuristic construction discussion, which is not a proof.

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; 12 strategies explored; 3 main gap nodes isolated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning above was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

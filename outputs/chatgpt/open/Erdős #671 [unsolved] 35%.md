# Erdős Problem #671 [unsolved] 35%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

For each n, assume the nodes

a
1
n
	​

,…,a
n
n
	​

∈[−1,1]

are distinct, since otherwise the Lagrange basis is not uniquely defined.

Define

λ
n
	​

(x)=
i=1
∑
n
	​

∣p
i
n
	​

(x)∣

and

L
n
	​

f(x)=
i=1
∑
n
	​

f(a
i
n
	​

)p
i
n
	​

(x).

The two questions are asking whether one can choose a triangular array of nodes such that:

For every f∈C[−1,1], there exists x∈[−1,1] such that

n→∞
limsup
	​

λ
n
	​

(x)=∞

and

L
n
	​

f(x)→f(x).

More strongly,

n→∞
limsup
	​

λ
n
	​

(x)=∞

for every x∈[−1,1], while still for every f∈C[−1,1], there exists at least one x such that

L
n
	​

f(x)→f(x).
Verified obstruction

Fix a point x
0
	​

∈[−1,1]. Define the linear functionals

T
n
x
0
	​

	​

(f)=L
n
	​

f(x
0
	​

)−f(x
0
	​

).

Then

∥L
n
	​

(⋅)(x
0
	​

)∥=λ
n
	​

(x
0
	​

).

Also,

∥T
n
x
0
	​

	​

∥≥λ
n
	​

(x
0
	​

)−1.

Therefore, if

n→∞
limsup
	​

λ
n
	​

(x
0
	​

)=∞,

then

n
sup
	​

∥T
n
x
0
	​

	​

∥=∞.

By the uniform boundedness principle, it is impossible that

T
n
x
0
	​

	​

(f)→0

for every f∈C[−1,1].

So no single fixed bad point x
0
	​

 can work for all continuous f. Any positive construction would need the convergence point to depend on f.

Negation of the first question

The first question is false exactly if:

For every triangular node system, there exists some f∈C[−1,1] such that for every x∈[−1,1],

n
limsup
	​

λ
n
	​

(x)=∞⟹L
n
	​

f(x)

→f(x).

I could prove this at a single prescribed bad point by uniform boundedness, but I could not complete the required simultaneous diagonalization over the whole bad set

B={x:
n
limsup
	​

λ
n
	​

(x)=∞}.
Negation of the second question

The second question is false exactly if:

For every triangular node system satisfying

n
limsup
	​

λ
n
	​

(x)=∞for every x∈[−1,1],

there exists f∈C[−1,1] such that

L
n
	​

f(x)

→f(x)

for every x∈[−1,1].

A plausible route is a Baire category diagonalization using the pointwise unboundedness of the functionals

f↦L
n
	​

f(x)−f(x)

at every x, but I did not complete a gap free proof.

Final status

I obtained a rigorous obstruction:

n
limsup
	​

λ
n
	​

(x
0
	​

)=∞

prevents convergence at that fixed x
0
	​

 for all continuous f.

I did not obtain a complete proof or disproof of either global existence question.

PROOF_CONFIDENCE: 95
COMPLETENESS_SCORE: 35
ADVERSARIAL_SURVIVAL_SCORE: 80
RESOURCE_USAGE: 100 percent reasoning budget, 3 branches explored, 1 verified lemma, 2 failed global proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

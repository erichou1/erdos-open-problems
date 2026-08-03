# Erdős Problem #84 [unsolved] 20%

---

## ChatGPT Response

Formal statement

For each integer n≥3, let

F
n
	​

={A⊆{3,…,n}:∃ graph G on n vertices such that C(G)=A},

where

C(G)={ℓ∈{3,…,n}:G contains a cycle of length ℓ}.

Then

f(n)=∣F
n
	​

∣.

The requested theorem is the conjunction of:

f(n)=o(2
n
)
	​


and

2
n/2
f(n)
	​

→∞
	​

.

Equivalently,

∀ε>0, ∃N, ∀n≥N,f(n)≤ε2
n
,

and

∀M>0, ∃N, ∀n≥N,f(n)≥M2
n/2
.

The negations are:

∃ε>0, ∀N, ∃n≥N,f(n)>ε2
n
,

and

∃M>0, ∀N, ∃n≥N,f(n)<M2
n/2
.

The contrapositive forms do not simplify usefully because f(n) is defined existentially over graphs and the target statements are asymptotic counting statements.

Verified basic construction

A useful graph family gives the classical-scale lower bound.

Let P=v
1
	​

v
2
	​

⋯v
n
	​

 be a path. For any subset

S⊆{j∈{3,…,n}:j is odd},

construct G
S
	​

 by adding the chord v
1
	​

v
j
	​

 for every j∈S.

For every j∈S, the edge v
1
	​

v
j
	​

 together with the path v
1
	​

v
2
	​

⋯v
j
	​

 gives a cycle of length j.

Any cycle using two chords v
1
	​

v
i
	​

,v
1
	​

v
j
	​

, with i<j, has length

(j−i)+2.

Since i,j are both odd, j−i is even, hence (j−i)+2 is even.

Therefore the odd cycle lengths of G
S
	​

 are exactly S. Thus distinct S’s give distinct cycle sets. Hence

f(n)≥2
∣{3≤j≤n:j odd}∣
.

So

f(n)≥2
⌊(n−1)/2⌋
.

This proves only

f(n)≥2
n/2−O(1)
.

It does not prove

f(n)/2
n/2
→∞.

The missing factor cannot be obtained merely by this parity-chord construction.

Attempted route for the stronger lower bound

One natural idea is to encode more than one bit per two possible lengths by allowing chords from several parity classes. However, if chords v
1
	​

v
i
	​

 and v
1
	​

v
j
	​

 are both allowed, then the two-chord cycle length

∣i−j∣+2

appears automatically. Thus direct membership of chord endpoints is not freely recoverable unless the encoded lengths avoid the difference set

D(S)={∣i−j∣+2:i,j∈S, i

=j}.

The parity construction works because odd chord endpoints generate only even two-chord cycle lengths. Attempts to add many even chord endpoints fail because even endpoints interact with odd endpoints and may create odd cycle lengths, destroying injective recovery of the original choices.

A possible route would be to find large sets

S⊆{3,…,n}

such that

∣x−y∣+2∈
/
S

for all distinct x,y∈S, with

∣S∣=
2
n
	​

+ω(1).

Then the same chord construction would imply

f(n)≥2
n/2+ω(1)
.

But I did not obtain such a set. The obvious extremal family, one parity class, has size only ∼n/2. Adding elements of the other parity appears to force many deletions from the original parity class because equations of the form

z=∣e−o∣+2

with e even and o,z odd create many forbidden pairs.

So this branch does not currently prove the required lower bound.

Attempted route for the upper bound

A structural approach is to reduce a graph to its 2-core, then suppress maximal degree-2 paths to form a kernel multigraph. If the kernel has few branch vertices, then the cycle lengths are determined by relatively few path lengths, giving a small number of possible cycle sets.

The difficulty is the complementary case: if the kernel has many branch vertices, one needs to prove that the cycle set cannot be arbitrary. A sufficient statement would be something like:

Every graph with sufficiently large cyclic complexity forces a long interval, or another large structured family, of cycle lengths.

If such a statement gave a forced block of r(n)→∞ cycle lengths, then the number of possible cycle sets would be at most roughly

2
n−r(n)

up to polynomial factors, yielding

f(n)=o(2
n
).

But I did not derive such a forcing lemma from first principles. The obstruction is that large cyclic complexity does not automatically give a clean interval of cycle lengths by elementary arguments; cactus-like graphs, theta graphs, and subdivided kernels show that cycle lengths can remain arithmetically sparse unless additional structure is proved.

Thus the upper-bound branch also remains incomplete.

Formal gap nodes

The proof would require resolving at least one strong lower-bound gap and one strong upper-bound gap.

GAP 1: super-2
n/2
 construction

Find a family of graphs on n vertices producing at least

2
n/2+ω(1)

distinct cycle sets.

The verified parity-chord family gives only

2
n/2−O(1)
.
GAP 2: o(2
n
) upper bound

Prove that the family of all realizable cycle sets omits an asymptotically non-negligible fraction of all subsets of {3,…,n}.

A sufficient but unproved route would be:

large cyclic complexity⟹many forced cycle lengths.

I did not produce a first-principles proof of this implication.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified parity-chord lower bound; 0 for the full requested theorem.

COMPLETENESS_SCORE: 20

ADVERSARIAL_SURVIVAL_SCORE: 85 for the partial construction; 0 for the missing asymptotic claims.

RESOURCE_USAGE: approximately 100% of the available reasoning budget for this response; several branches explored; main verified lemma generated; multiple failed proof attempts identified.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

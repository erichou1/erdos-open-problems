# Erdős Problem #137 [unsolved] 35%

---

## ChatGPT Response

Formalization

Let

P(m,k)=m(m+1)⋯(m+k−1),m≥1, k≥3.

For a prime p, write v
p
	​

(N) for the exponent of p in N.

A positive integer N>1 is powerful iff

∀p,p∣N⟹v
p
	​

(N)≥2.

Equivalently,

N is not powerful⟺∃p prime such that v
p
	​

(N)=1.

So the target statement is:

∀k≥3, ∀m≥1, ∃p prime with v
p
	​

(P(m,k))=1.
	​


Its negation is:

∃k≥3, ∃m≥1such that∀p, v
p
	​

(P(m,k))

=1.

That is, every prime dividing P(m,k) divides it to exponent at least 2.

Basic invariants

For 0≤i<j≤k−1,

gcd(m+i,m+j)∣j−i.

Therefore, if p≥k, then p cannot divide two distinct factors m+i and m+j, because then

p∣(m+j)−(m+i)=j−i,

but 1≤j−i≤k−1<p, impossible.

Thus:

p≥k, p∣m+i⟹v
p
	​

(P(m,k))=v
p
	​

(m+i).

So in any hypothetical powerful product, every prime p≥k appearing in any single factor must appear there with exponent at least 2.

Lemma 1: large-prime isolation

Lemma. If p≥k and p∣m+i, then

v
p
	​

(P(m,k))=v
p
	​

(m+i).

Proof. Suppose p∣m+i and p∣m+j for i

=j. Then

p∣(m+j)−(m+i)=j−i.

But 0<∣j−i∣≤k−1<p, contradiction. Hence p divides exactly one factor. Therefore its total valuation in P(m,k) is exactly its valuation in that factor. ∎

Consequence. If P(m,k) is powerful, then for every i, every prime p≥k dividing m+i satisfies

v
p
	​

(m+i)≥2.

So all possible exponent-1 prime factors of individual terms must be among primes <k.

Lemma 2: bounded squarefree defect per factor

For 0≤i≤k−1, define

A
k,i
	​

:=
0≤j≤k−1
j

=i
	​

∏
	​

∣i−j∣=i!(k−1−i)!.

Define the squarefree defect of m+i by

D
i
	​

=
p∣m+i
v
p
	​

(m+i)=1
	​

∏
	​

p.

Lemma. If P(m,k) is powerful, then

D
i
	​

∣rad(A
k,i
	​

).

Proof. Let p∣D
i
	​

. Then v
p
	​

(m+i)=1. Since P(m,k) is powerful, we need v
p
	​

(P(m,k))≥2. Therefore p must divide at least one other factor m+j, j

=i. Hence

p∣(m+j)−(m+i)=j−i.

Thus p∣∣j−i∣, and since ∣j−i∣ is one of the factors in A
k,i
	​

, we get

p∣A
k,i
	​

.

Because D
i
	​

 is squarefree, this gives

D
i
	​

∣rad(A
k,i
	​

).

∎

Corollary 3: every factor is a bounded squarefree multiple of a powerful number

If P(m,k) is powerful, then for each i,

m+i=D
i
	​

Q
i
	​

,

where

D
i
	​

∣rad(i!(k−1−i)!)

and Q
i
	​

 is powerful.

Proof. By definition, D
i
	​

 contains exactly the primes appearing in m+i to exponent 1. After dividing m+i by D
i
	​

, every remaining prime has exponent either 0 or at least 2. Hence Q
i
	​

=(m+i)/D
i
	​

 is powerful. ∎

So a hypothetical counterexample would force an entire block

m,m+1,…,m+k−1

to lie in finitely many sets of the form

d⋅{powerful numbers},

where each allowed d depends only on k and i.

For k=3, this becomes especially restrictive:

A
3,0
	​

=2,A
3,1
	​

=1,A
3,2
	​

=2.

Thus, if

m(m+1)(m+2)

were powerful, then

m=d
0
	​

Q
0
	​

,m+1=Q
1
	​

,m+2=d
2
	​

Q
2
	​

,

where

d
0
	​

,d
2
	​

∈{1,2},

and Q
0
	​

,Q
1
	​

,Q
2
	​

 are powerful. In particular, the middle term m+1 itself must be powerful.

This is a genuine reduction, not a proof.

Breadth-first strategy search
1. Direct prime-isolation proof

Try to prove that among m,…,m+k−1, some factor has a prime p≥k appearing to exponent exactly 1.

Obstacle: large primes may appear squared inside individual factors.

Status: unresolved.

2. Contradiction using minimal counterexample

Assume a counterexample (m,k) with minimal k, then minimal m. Try to remove one endpoint or compare P(m,k) with P(m,k−1).

Obstacle: a powerful number divided by one factor need not remain powerful.

Status: unresolved.

3. Induction on k

If P(m,k) powerful, compare

P(m,k)=P(m,k−1)(m+k−1).

Obstacle: prime exponents may be repaired by the final factor.

Status: unresolved.

4. Transfinite induction

No natural well-ordered structure stronger than ordinary induction appears. The parameters are finite integers.

Status: no useful structure found.

5. Cardinality/density

Powerful numbers up to x are sparse. Indeed every powerful number can be written as

a
2
b
3

with b squarefree. Hence there are O(
x
	​

) powerful numbers up to x.

Obstacle: sparsity alone does not exclude local coincidences of finitely many shifted sparse sets.

Status: gives heuristic pressure, not proof.

6. Diagonalization

Try to assign to each factor m+i a private prime p
i
	​

 appearing once.

Obstacle: the same small prime can appear in several factors and repair exponent 1 defects.

Status: unresolved.

7. Compactness/local-to-global

Try to prove impossibility modulo sufficiently many prime powers.

Obstacle: for any fixed modulus, local congruence solutions may exist without producing global integer solutions.

Status: unresolved.

8. Density modulo primes

For p≥k, a residue class mod p
2
 can force p∣m+i but p
2
∤m+i, which would kill powerfulness.

Obstacle: one must prove at least one such obstruction occurs for every m,k, not merely for most m.

Status: unresolved.

9. Reflection symmetry

The block is symmetric under

i↦k−1−i.

The defect bounds satisfy

A
k,i
	​

=A
k,k−1−i
	​

.

Obstacle: symmetry gives no contradiction.

Status: weak invariant only.

10. Auxiliary graph structure

Construct a graph on indices 0,…,k−1, joining i,j if some prime p divides both m+i and m+j.

Every edge label p must divide ∣i−j∣.

Obstacle: large primes produce isolated vertices but may appear squared, so isolation is not enough.

Status: useful language, no contradiction.

11. Counterexample construction

To build a counterexample, one would need each m+i to be a bounded squarefree multiple of a powerful number.

Obstacle: simultaneous equations

m+i=d
i
	​

Q
i
	​


for k≥3 are highly rigid. No construction follows from the reductions.

Status: no counterexample produced.

12. Stronger theorem attempt

Try to prove:

∀m,k≥3, ∃p≥k with v
p
	​

(P(m,k))=1.

This would imply the target theorem.

Obstacle: this stronger statement may fail structurally because all primes ≥k in a block could, in principle, appear squared inside their own factors.

Status: stronger theorem not proved.

Primary gap

The central unresolved statement is:

Every block m,…,m+k−1, k≥3, contains a prime p whose total valuation in the block is 1.
	​


The verified lemmas reduce this to the following sharper form:

In every block of length k≥3, some factor has a prime exponent-1 defect not repairable by another factor.
	​


Equivalently, at least one defect prime must fail to divide the bounded difference product

i!(k−1−i)!.

I could not prove that final assertion from the elementary reductions above.

Adversarial verification of accepted lemmas
Lemma 1 attack

Possible failure: p=k might divide two terms whose difference is k.

But the largest possible difference between two indices in a block of length k is k−1, not k. Therefore p=k still cannot divide two distinct factors.

Lemma 1 survives.

Lemma 2 attack

Possible failure: a prime p with v
p
	​

(m+i)=1 might become exponent ≥2 in the product without dividing another factor.

Impossible, because valuations add:

v
p
	​

(P(m,k))=
j=0
∑
k−1
	​

v
p
	​

(m+j).

If v
p
	​

(m+i)=1, then to make the total at least 2, some other term must contribute positive p-adic valuation.

Lemma 2 survives.

Corollary 3 attack

Possible failure: after removing the exponent-1 primes, a remaining prime might have exponent 1.

Impossible by construction: every prime with exponent exactly 1 was removed once; all other remaining exponents are at least 2.

Corollary 3 survives.

Dependency graph
Definition of powerful
⇓
P(m,k) powerful⟺∀p, v
p
	​

(P(m,k))

=1
⇓
Large-prime isolation lemma
⇓
p≥k, p∣m+i⟹v
p
	​

(m+i)≥2
⇓
Only primes p<k may occur to exponent 1 inside a factor
⇓
D
i
	​

∣rad(i!(k−1−i)!)
⇓
m+i=D
i
	​

Q
i
	​

,Q
i
	​

 powerful

This is a rigorous reduction, but the final impossibility of such a block was not proved.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the lemmas proved above; 0 for the original theorem as a completed proof.

COMPLETENESS_SCORE: 35. The main structural reduction is rigorous, but the decisive global contradiction is missing.

ADVERSARIAL_SURVIVAL_SCORE: 90 for the local reductions; not applicable to the unproved main theorem.

RESOURCE_USAGE: approximately 80% of the available reasoning budget used; 12 strategies explored; 3 verified lemmas generated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

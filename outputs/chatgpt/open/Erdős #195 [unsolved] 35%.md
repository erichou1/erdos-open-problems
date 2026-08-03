# Erdős Problem #195 [unsolved] 35%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formalization

Let a permutation of Z mean a bijection

π:Z→Z.

A monotone k-term arithmetic progression means: there exist integers a∈Z, d∈Z
>0
	​

, such that

a, a+d, …, a+(k−1)d

satisfy either

π(a)<π(a+d)<⋯<π(a+(k−1)d)

or

π(a)>π(a+d)>⋯>π(a+(k−1)d).

Define

K=max{k:∀π:Z→Z bijective, ∃a,d>0 giving a monotone k-AP}.

The problem asks for K.

The negation of “every permutation contains a monotone k-AP” is:

∃π:Z→Z bijective such that for all a∈Z,d>0,
π(a),π(a+d),…,π(a+(k−1)d)

is neither strictly increasing nor strictly decreasing.

The trivial lower bound is

K≥2,

because any two distinct values are automatically monotone.

The statement quoted in the problem gives an upper-bound input:

K≤4.

So the remaining first-principles target is

K≥4.

I was not able to derive that from scratch in this session.

Verified structural lemma for the k=3 obstruction

It is useful to translate the problem into an order relation. Write

x≺y⟺π(x)<π(y).

Then ≺ is a total order of type Z on the set Z.

A monotone 3-term AP is a triple

x−d, x, x+d

such that the three terms appear in ≺-order either as

x−d≺x≺x+d

or

x+d≺x≺x−d.

Therefore, if a permutation has no monotone 3-term AP, then for every x∈Z and every d>0,

x−d≺x⟺x+d≺x.

Equivalently, the lower set

L
x
	​

={y∈Z:y≺x}

is invariant under reflection about x:

y∈L
x
	​

⟺2x−y∈L
x
	​

.

This is a strong necessary condition.

Now suppose u≺v are adjacent in the permutation order, and put

δ=v−u.

Then L
v
	​

=L
u
	​

∪{u}. Reflection-invariance gives:

u∈L
v
	​

⟹2v−u=v+δ∈L
v
	​

.

Since u≺v are adjacent and v+δ

=u, we must have

v+δ≺u≺v.

Similarly, using reflection about u,

v∈
/
L
u
	​

⟹2u−v=u−δ∈
/
L
u
	​

,

so

u≺v≺u−δ.

Thus every adjacent pair u≺v in a hypothetical no-monotone-3 permutation forces

v+δ≺u≺v≺u−δ.

More strongly, on the arithmetic line

u+nδ,n∈Z,

one obtains the parity separation

u+2mδ≺u≺v≺u+(2m+1)δ

for all relevant nonzero m, with the even congruence class forced to the left side and the odd congruence class forced to the right side.

This suggests a rigid 2-adic-type obstruction, but I did not complete the contradiction needed to prove K≥3, let alone K≥4.

Strategy search summary

The following approaches were considered.

Direct order-theoretic proof.
Convert the permutation into a total order ≺ and try to force a monotone AP. Produced the reflection-invariance lemma above, but no full contradiction.

Adjacent-pair analysis.
Study adjacent elements u≺v. This gave strong parity separation on the line u+(v−u)Z, but did not force a global contradiction.

Minimal adjacent difference.
Let D=min∣v−u∣ over adjacent pairs. Attempted to use the forced inequalities

v+(v−u)≺u≺v≺u−(v−u)

to contradict minimality. No contradiction was completed.

Symmetric lower-set dynamics.
A no-monotone-3 order would require every lower set L
x
	​

 to be reflection-invariant about x. This is very restrictive, but I did not prove impossibility.

Finite approximation.
Finite permutations can avoid small monotone APs, so finite obstruction alone is insufficient.

Compactness-style reasoning.
A compactness argument risks producing a total order not representable by a bijection Z→Z, so it does not directly solve the problem.

2-adic structure.
The adjacent-pair parity separation resembles 2-adic lexicographic order. Such structures explain why finite avoiders exist, but I did not turn this into a proof or disproof for genuine bi-infinite permutations.

Ramsey/van der Waerden route.
Infinite Ramsey gives large monotone subsequences, but those subsequences may be sparse and need not contain arithmetic progressions.

Density route.
No natural positive-density subset was forced by bijectivity alone.

Induction on AP length.
A monotone 4-AP would imply a monotone 3-AP, but the k=3 case itself was not resolved internally.

Contradiction via one-sided tails.
One-sided permutations of Z immediately force monotone 3-APs from the first two terms, but a bi-infinite permutation has no first element, so this does not transfer directly.

Construction search.
A construction avoiding monotone 5-AP is asserted in the prompt via the K≤4 bound, but I did not reconstruct such a permutation from first principles.

Current rigorous conclusion

From the problem statement plus verified deductions:

2≤K≤4.

Using the quoted upper-bound claim alone:

K≤4.

But I did not complete a proof that every permutation of Z contains a monotone 4-term arithmetic progression. Therefore I cannot honestly output PROVED.

Final state:

RESOURCE_EXHAUSTED
	​


PROOF_CONFIDENCE: 92/100 for the formalization and verified lemmas.
COMPLETENESS_SCORE: 35/100.
ADVERSARIAL_SURVIVAL_SCORE: 80/100 for the local structural lemma; low for the full target because the main lower bound remains unproved here.
RESOURCE_USAGE: about 85%; 12 strategies considered; 1 main structural lemma generated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

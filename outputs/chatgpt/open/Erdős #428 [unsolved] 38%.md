# Erdős Problem #428 [unsolved] 38%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

The statement was not proved or disproved from first principles within this response. The rigorous deductions below produce strong necessary structure, but the remaining core assertion reduces to simultaneous primality of large finite reflected patterns, and I do not have a first principles proof or disproof of that assertion.

1. Formal statement

Let

P={p∈N:p is prime},π(x)=∣P∩[1,x]∣.

For A⊆N, define n to be good for A if

∀a∈A,0<a<n⇒n−a∈P.

The problem asks whether

∃A⊆N

such that

{n∈N:n is good for A}

is infinite and

x→∞
liminf
	​

π(x)
∣A∩[1,x]∣
	​

>0.

Equivalently, there are A⊆N, an infinite set G⊆N, and a constant c>0 such that

∀n∈G, ∀a∈A∩[1,n−1], n−a∈P

and eventually

∣A∩[1,x]∣≥cπ(x).
2. Negation

The negation is:

For every A⊆N, either

x→∞
liminf
	​

π(x)
∣A∩[1,x]∣
	​

=0

or A has only finitely many good n.

A disproof of existence must prove that every A with infinitely many good n has zero lower density relative to the primes.

3. First necessary condition: finite admissibility
Lemma 1

If A has infinitely many good n, then for every prime q, the set A misses at least one residue class modulo q.

Proof

Assume A has infinitely many good n. Fix a prime q.

Suppose instead that A occupies every residue class modulo q. Then choose a finite set

F⊆A

containing one representative from each residue class modulo q.

Because there are infinitely many good n, choose a good n so large that

n>maxF+q.

Since F covers all residues modulo q, there exists a∈F such that

a≡n(modq).

Then

q∣n−a.

Also

n−a>q.

So n−a is a positive integer larger than q divisible by q, hence composite. This contradicts the definition of good n.

Therefore A misses at least one residue class modulo every prime q. ∎

Immediate consequences:

For q=2, all elements of A have the same parity.

For q=3, A uses at most two residue classes modulo 3.

For every prime q, A uses at most q−1 residue classes modulo q.

This is necessary, but it is not enough to disprove the statement, because a set can miss one residue class modulo each prime and still plausibly have prime scale size.

4. Stronger finite pattern condition
Lemma 2

If A has infinitely many good n, then every finite subset F⊆A has infinitely many reflected prime realizations:

∃
∞
n∈N∀a∈F, n−a∈P.
Proof

Let F⊆A be finite. Since A has infinitely many good n, choose any good n>maxF. Then for every a∈F,

a<n,

so by goodness,

n−a∈P.

There are infinitely many such good n, and all sufficiently large ones exceed maxF. Therefore the displayed condition holds for infinitely many n. ∎

Thus every finite subset of A behaves like an admissible prime pattern under reflection.

This is much stronger than the residue obstruction, but it still does not directly contradict the desired density condition.

5. Residue behavior of the good shifts

Let

G={n:n is good for A}.

For a prime q, define

R
q
	​

={r∈Z/qZ:infinitely many n∈G satisfy n≡r(modq)}.
Lemma 3

For every prime q,

(Amodq)∩R
q
	​

=∅.
Proof

Assume a∈A, r∈R
q
	​

, and

a≡r(modq).

Since r∈R
q
	​

, there are infinitely many good n∈G with

n≡r(modq).

Choose such an n with

n>a+q.

Then

n−a≡r−a≡0(modq),

and

n−a>q.

So n−a is composite, contradicting goodness of n. ∎

Consequences:

For every prime q, the residues used infinitely often by good n are forbidden to A.

Since R
q
	​


=∅, Lemma 1 follows again.

If A uses q−1 residue classes modulo q, then all sufficiently large good n must lie in the single remaining residue class modulo q.

6. Main obstruction after first principles reasoning

The problem becomes this:

Construct or rule out a set A of prime scale size such that every finite subset F⊆A has infinitely many n for which all numbers n−a, with a∈F, are prime.

Equivalently, one needs either:

Construction:∃A of prime scale density with infinitely many full reflected prime rows,

or

Disproof:∀A with infinitely many full reflected prime rows,∣A∩[1,x]∣=o(π(x)).

The residue lemmas do not prove either side.

They only show that A must be globally sifted: it must miss at least one residue class modulo every prime.

7. Search branches
Branch A: Direct contradiction by modular residues

This proves Lemmas 1 through 3.

Failure point: missing one residue class modulo every prime does not force A to be smaller than prime scale. It is compatible with the target order of magnitude.

Status: structural information only.

Branch B: Construct A by choosing forbidden residues

One can imagine choosing one forbidden residue r
q
	​

 modulo each prime q, then defining

B={a∈N:a

≡r
q
	​

(modq) for every prime q}.

Such a set has the correct kind of modular structure.

Failure point: to make B work, one must produce infinitely many n such that

n−a∈P

for every a∈B∩[1,n−1]. This is a large simultaneous primality requirement, not forced by the residue construction alone.

Status: construction incomplete.

Branch C: Recursive construction of good shifts

Suppose finite A
m
	​

={a
1
	​

,…,a
m
	​

} has been selected. To extend the construction, one would need infinitely many n such that

n−a
1
	​

,…,n−a
m
	​


are all prime.

The modular obstruction says this is possible only if A
m
	​

 does not cover every residue class modulo any prime.

Failure point: admissibility is necessary, but from first principles here I do not have a proof that every admissible finite reflected pattern occurs infinitely often.

Status: core gap.

8. Verified conclusions

The following are rigorously established from the problem statement alone:

If such an A exists, then A misses at least one residue class modulo every prime.

In particular, all elements of A have the same parity.

Every finite subset F⊆A must be realized infinitely often as a reflected prime pattern.

For every prime q, the residue classes occupied infinitely often by good n are disjoint from the residue classes occupied by A.

These constraints do not by themselves contradict

x→∞
liminf
	​

π(x)
∣A∩[1,x]∣
	​

>0.
9. Unresolved primary gap

The unresolved statement is:

Given a set A of prime scale size that misses at least one residue class modulo every prime, can there exist infinitely many n such that

A∩[1,n−1]⊆n−P?

I do not have a proof or disproof of this statement from first principles in the present reasoning budget.

10. Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 93

COMPLETENESS_SCORE: 38

ADVERSARIAL_SURVIVAL_SCORE: 86

RESOURCE_USAGE: 100 percent of the response budget allocated to this proof search, 3 main branches explored, 3 verified lemmas generated, 3 failed proof attempts retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

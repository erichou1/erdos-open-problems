# Erdős Problem #91 [unsolved] 15%

---

## ChatGPT Response

Formal statement

Let

D(A)={∥a−b∥:a,b∈A, a

=b}

for a finite set A⊂R
2
, and define

m(n)=min{∣D(A)∣:A⊂R
2
, ∣A∣=n}.

Two finite point sets A,B⊂R
2
 are similar if there exist c>0, an isometry T of R
2
, and possibly a reflection, depending on convention, such that

B=T(cA).

The target statement is:

∃N ∀n≥N ∃A,B⊂R
2

such that

∣A∣=∣B∣=n,∣D(A)∣=∣D(B)∣=m(n),

and A,B are not similar.

Equivalently: for all sufficiently large n, the set of similarity classes of minimizers of ∣D(A)∣ has size at least 2.

Quantifier structure

The statement is:

∃N∈N ∀n∈N, n≥N:∣Min(n)/∼∣≥2,

where

Min(n)={A⊂R
2
:∣A∣=n, ∣D(A)∣=m(n)}.

The negation is:

∀N∈N ∃n≥N:∣Min(n)/∼∣≤1.

So to disprove the statement, one would need infinitely many n for which all minimizers are mutually similar, or no minimizer exists under the intended formalization.

Immediate verified facts
Lemma 1: similarity preserves the number of distinct distances.

If B=T(cA) with c>0 and T an isometry, then

D(B)=cD(A),

so

∣D(B)∣=∣D(A)∣.

Thus similarity classes are the natural quotient objects for this problem.

Lemma 2: the theorem cannot be proved by producing two arbitrary good configurations.

To prove the statement, it is not enough to find two non-similar n-point sets with few distinct distances. One must prove that both achieve the exact minimum m(n). Therefore any construction must be paired with a matching lower bound.

This creates the central obstruction:

Need exact control of m(n) and at least two extremizers.
Equivalent formulations

The target is equivalent to each of the following.

Formulation 1: extremal multiplicity

For all sufficiently large n, the extremal problem

∣A∣=n
min
	​

∣D(A)∣

has at least two geometrically distinct minimizers.

Formulation 2: non-uniqueness in moduli space

Let M
n
	​

 be the space of n-point subsets of R
2
 modulo similarity. Define

F
n
	​

([A])=∣D(A)∣.

Then the theorem says

∣argmin
[A]∈M
n
	​

	​

F
n
	​

∣≥2

for all sufficiently large n.

Formulation 3: failure of eventual rigidity

The negation says that there are arbitrarily large n for which the extremal configuration is unique up to similarity.

So the desired theorem is an eventual non-rigidity theorem for the distinct-distance minimization problem.

Boundary and extremal cases

For small n, uniqueness can occur. The statement itself mentions n=3 and n=5 as cases with unique minimizers up to similarity.

So any proof must use genuinely large-n behavior. A proof by small-case classification cannot scale directly.

The most obvious candidate configurations for small distance sets are structured objects such as:

k×ℓ rectangular grids,triangular lattice patches,regular polygons,unions of structured patches.

But verifying optimality for any of these requires a lower bound matching their exact number of distances.

Main obstruction discovered

A proof of the requested statement would require something of the following strength:

∃N ∀n≥N:m(n)=r(n)

for some explicitly controlled function r(n), together with at least two non-similar constructions A
n
	​

,B
n
	​

 satisfying

∣D(A
n
	​

)∣=∣D(B
n
	​

)∣=r(n).

Without an exact lower bound for m(n), one cannot certify that either construction is a minimizer.

A weaker asymptotic estimate such as

m(n)≤Cf(n)

or

m(n)≥cf(n)

does not suffice. Even a sharp asymptotic formula would not necessarily suffice, because the theorem is about exact minimizers, not asymptotic minimizers.

Strategy audit

I tested the following approaches from first principles.

1. Direct construction

Try to construct two non-similar sets A
n
	​

,B
n
	​

 with the same number of distances.

Obstacle: equality of distance counts does not imply optimality.

Required missing theorem:

∣D(A)∣≥∣D(A
n
	​

)∣

for every n-point set A.

Unresolved.

2. Perturbation of a minimizer

Start from one minimizer A, perturb it continuously, and try to preserve all distance coincidences.

Obstacle: generic perturbations destroy equalities among distances, increasing ∣D(A)∣. Nontrivial perturbations preserving the exact distance partition require the configuration to have a positive-dimensional deformation space, which is not guaranteed.

Unresolved.

3. Reflection or mirror image

If “similarity” excludes reflections, a chiral minimizer and its mirror would be non-similar. But under the usual broader convention, reflections are similarities. Even if reflections are excluded, one still needs a chiral minimizer for all large n.

Unresolved.

4. Grid comparison

Rectangular grids are natural low-distance candidates. For example, an a×b grid has squared distances of the form

i
2
+j
2
,0≤i<a,0≤j<b,

not both zero.

Different aspect ratios can produce non-similar grids.

Obstacle: one must prove that some grid is exactly optimal for all sufficiently large n, or that at least two grids are exactly optimal. No such conclusion follows from first principles here.

Unresolved.

5. Induction on n

Try to build minimizers of size n+1 from minimizers of size n.

Obstacle: deleting a point from a minimizer need not produce a minimizer for n−1, and adding a point to a minimizer may introduce many new distances.

No monotone extremal structure is forced by the definition alone.

Unresolved.

6. Compactness / existence

One can try to normalize configurations by diameter 1 and take limits.

Obstacle: limit configurations can collide, producing fewer than n distinct points. The existence of minimizers is plausible but requires a careful semialgebraic compactness argument. Even if existence is proved, it gives no multiplicity.

Insufficient.

7. Contradiction from eventual uniqueness

Assume that for infinitely many n, all minimizers are similar. Try to force a contradiction by adding or deleting points.

Obstacle: uniqueness of minimizers at size n does not obviously constrain minimizers at size n+1. There is no direct hereditary property.

Unresolved.

8. Cardinality/moduli argument

The space of configurations is continuous, while distance-count values are discrete. One might hope that minima occur on positive-dimensional families.

Obstacle: minimizers can be isolated. The discreteness of the objective does not force multiple similarity classes.

Invalid as a proof.

9. Algebraic-dependence argument

A configuration with few distances satisfies many polynomial equations among squared distances. Perhaps those equations force flexible families.

Obstacle: polynomial systems can have isolated solutions. More equations usually imply rigidity, not flexibility.

Invalid without a new rigidity theorem.

10. Counterexample search

A possible disproof route would be to show infinitely many n have unique minimizers. But proving uniqueness is at least as hard as proving non-uniqueness, because it again requires exact knowledge of all minimizers.

No disproof obtained.

Verified conclusion

The desired theorem does not follow from the definitions alone through any of the above elementary routes. Every viable proof path requires a major missing ingredient: exact control of the minimizers or exact lower bounds for m(n).

Therefore I cannot honestly present a proof or disproof of the stated assertion from first principles in this session.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100
There is no claimed proof of the original theorem, so the confidence applies only to the formalization and the diagnosis of the missing logical ingredients.

COMPLETENESS_SCORE: 15
The setup, negation, equivalent formulations, and elementary invariance facts are established. The central theorem remains unproved.

ADVERSARIAL_SURVIVAL_SCORE: 90
The main conclusion is conservative: no proof was obtained. The identified gap is genuine because exact extremality is required.

RESOURCE_USAGE:
Reasoning budget used: approximately 85%
Branches explored: 10
Verified lemmas generated: 2
Failed proof attempts: 8

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

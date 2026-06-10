# Erdős Problem #173 [unsolved] 25%

---

## ChatGPT Response

Phase 0: Formalization

Let a 2-colouring be a function

χ:R
2
→{R,B}.

For a nondegenerate triangle T, write T∈E(χ) if there is no monochromatic congruent copy of T in (R
2
,χ).

The target statement is:

∀χ:R
2
→{R,B},∣E(χ)∣≤1.

Equivalently:

∀χ, ∀T
1
	​

,T
2
	​

,T
1
	​


≅T
2
	​

⟹at least one of T
1
	​

,T
2
	​

 has a monochromatic congruent copy.

Negation:

There exists a colouring χ and two noncongruent triangles T
1
	​

,T
2
	​

 such that neither T
1
	​

 nor T
2
	​

 has a monochromatic congruent copy.

A triangle T with side lengths a,b,c is avoided exactly when every congruent copy of T has vertex-colour pattern RRB,RBR,BRR,BBR,BRB, or RBB, never RRR or BBB.

Verified basic lemma
Lemma 1: one monochromatic edge per avoided triangle-copy

Assume T∈E(χ). Then every congruent copy of T contains exactly one monochromatic side.

Proof. Any three vertices coloured with two colours contain at least one same-coloured pair. If the three vertices were all the same colour, that would be a forbidden monochromatic copy of T. Therefore the colour pattern is 2+1, so exactly one of the three sides joins equal colours. □

Equivalently, for every copy ABC≅T,

1
χ(A)=χ(B)
	​

+1
χ(B)=χ(C)
	​

+1
χ(C)=χ(A)
	​

=1.

This is the main structural constraint.

Consequence: forced apex rule

Let T have side lengths a,b,c. Suppose AB is a same-coloured segment of length a. Let C,C
′
 be the two possible third vertices such that

AC=AC
′
=b,BC=BC
′
=c.

If T is avoided, then

χ(C)=χ(C
′
)

=χ(A)=χ(B).

Proof. Since AB is already the unique monochromatic side in each copy ABC and ABC
′
, the other two vertices must have the opposite colour. □

Thus avoiding T forces every same-coloured side of T to generate two opposite-coloured apexes.

Phase 1: strategy search

I tested the following proof directions from first principles.

Strategy	Core idea	Status
Direct proof	Show every non-equilateral triangle is forced monochromatically	Reduced to a hard global consistency problem
Contradiction	Assume two avoided triangles and derive incompatible forced-apex constraints	Promising but incomplete
Finite configuration	Build a finite point set forcing one of two triangles	No universal construction found
Induction on generated configurations	Repeatedly reflect triangle copies across same-coloured sides	Produces many forced colours but no contradiction in full generality
Transfinite induction	Try to construct a colouring avoiding two triangles and contradict extension	No decisive obstruction found
Cardinal arithmetic	Compare continuum many copies with two colour classes	Cardinality alone too weak
Diagonalization	Attempt to build a colouring avoiding two prescribed triangles	No verified construction
Compactness	Reduce to finite colourability of every finite induced hypergraph	Needs finite obstruction or finite model theorem; unresolved
Density	Use positive-density-like arguments	Not available for arbitrary colourings
Reflection	Exploit rotations/reflections of an avoided triangle around a mono side	Gives forced-apex lemma only
Auxiliary structure	Encode same-colour edges as a signed complete geometric graph	Useful but not sufficient
Counterexample search	Examine strip-like colourings	Supports the “one equilateral exception” pattern but does not prove theorem

The highest-value branches were:

Signed-edge consistency.

Forced-apex propagation.

Finite obstruction construction.

Phase 2: useful reformulation

Define, for distinct X,Y∈R
2
,

σ(X,Y)={
+1,
−1,
	​

χ(X)=χ(Y),
χ(X)

=χ(Y).
	​


For any triple A,B,C,

σ(A,B)σ(B,C)σ(C,A)=+1,

because each vertex colour appears twice in the product.

If ABC≅T and T is avoided, then exactly one edge is monochromatic, so the sign pattern is

(+1,−1,−1)

in some order.

Thus avoidance of T says:

∀ABC≅T,σ(A,B)+σ(B,C)+σ(C,A)=−1.

This is strong, but not obviously contradictory for one triangle; for example, strip colourings show that at least one equilateral size can satisfy such a constraint.

Phase 3: branch exploration
Branch A: prove every non-equilateral triangle is unavoidable

Target:

T non-equilateral⟹T∈
/
E(χ).

If true, the original theorem would reduce to showing at most one equilateral side length can be avoided.

Verified progress:

If T is avoided, every same-coloured side of length a,b, or c forces two opposite-coloured apexes. For a side a, the two apexes are separated by distance

2h
a
	​

,

where h
a
	​

 is the altitude to side a.

So a same-coloured a-edge forces a same-coloured 2h
a
	​

-edge in the opposite colour.

Gap:

There is no verified reason that this derived same-coloured 2h
a
	​

-edge must interact with another copy of T, unless 2h
a
	​

 happens to equal one of a,b,c or another controlled distance.

This branch proves useful local structure but does not close the global argument.

Branch B: assume two avoided triangles

Assume two noncongruent triangles T
1
	​

,T
2
	​

∈E(χ).

Each avoided triangle imposes its own exact-one-monochromatic-edge rule. If the two triangles share a side length d, then any same-coloured d-segment triggers forced apexes for both triangles. One hopes to arrange these apex sets so that one forced point must be both colours.

Verified conditional statement:

If two avoided triangles T
1
	​

,T
2
	​

 share a side length d, and there exists a same-coloured segment AB of length d such that a forced apex from T
1
	​

 coincides geometrically with a point forced to have the opposite colour by T
2
	​

, then contradiction follows.

Gap:

For arbitrary noncongruent triangles, their side lengths need not overlap, and even when they do, the required forced-apex coincidence is not automatic.

So this proves a conditional obstruction, not the full theorem.

Branch C: finite obstruction

For a fixed avoided triangle T, define a hypergraph whose vertices are points of a finite configuration F⊂R
2
, and whose hyperedges are triples congruent to T.

Avoiding T means F admits a 2-colouring with no monochromatic hyperedge.

For the desired theorem, one would need:

For every pair of nonconuent triangles T
1
	​

,T
2
	​

, there exists a finite F⊂R
2
 such that every 2-colouring of F contains a monochromatic copy of T
1
	​

 or T
2
	​

.

I found no general construction of such an F.

The obstruction is that the local exact-one-edge rule is satisfiable on many natural finite configurations, especially lattice-like configurations generated by one triangle.

Verified special structural fact for right triangles

Let T be a right triangle with legs a,b. If T is avoided, then every rectangle of side lengths a,b has exactly two red vertices and two blue vertices.

Proof. The four triples obtained by deleting one vertex of such a rectangle are exactly the four congruent right triangles with legs a,b. If three vertices of the rectangle had the same colour, those three would form a monochromatic copy of T. Therefore no colour appears three or four times among the rectangle vertices. Since there are four vertices and two colours, the rectangle is split 2+2. □

This is a strong consistency condition. However, deriving a contradiction from it for all a,b requires an additional geometric argument that I did not complete from first principles here.

Current dependency graph

Verified:

T∈E(χ)⟹every copy of T has exactly one monochromatic edge.
T∈E(χ)⟹same-coloured side forces both apexes to the opposite colour.
T right and T∈E(χ)⟹every a×b rectangle is 2-2 coloured.

Unresolved primary target:

∣E(χ)∣≤1.

Unresolved stronger target:

T non-equilateral⟹T∈
/
E(χ).

Unresolved equilateral target:

At most one equilateral side length can be avoided by a fixed colouring.
Adversarial check

The attempted proof cannot be declared complete because the forced-apex rule is only local. It shows that avoided triangles impose rigid constraints around same-coloured side segments, but it does not yet prove those constraints are globally inconsistent for two noncongruent triangles.

The main missing step is a universal geometric forcing mechanism:

T
1
	​

,T
2
	​

∈E(χ),T
1
	​


≅T
2
	​

⟹some point is forced to have two colours.

No fully verified mechanism of that form was obtained.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified lemmas; 0 for the full theorem as proved.

COMPLETENESS_SCORE: 25

ADVERSARIAL_SURVIVAL_SCORE: 90 for the local lemmas; 20 for the global approach.

RESOURCE_USAGE: approximately 100% of the allotted reasoning budget; 3 main branches explored; 4 verified lemmas/conditional facts generated; 3 failed full-proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

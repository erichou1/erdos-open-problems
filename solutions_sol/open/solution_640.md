# Erdős Problem #640 [unsolved] 20%

---

## ChatGPT Response

Formalization

For n∈N
≥1
	​

, let P(n) mean that there exist nondegenerate closed Euclidean triangles T,τ and isometries g
1
	​

,…,g
n
	​

 such that

T=
i=1
⋃
n
	​

g
i
	​

(τ),int(g
i
	​

(τ))∩int(g
j
	​

(τ))=∅(i

=j).

Thus the desired set is

S={n≥1:P(n)}.

The area identity

[T]=n[τ]

is necessary but far from sufficient.

Verified constructions and closure
Square closure

If m∈S, then

mk
2
∈S(k≥1).

Indeed, subdivide each of the m congruent tiles into k
2
 congruent triangles by the standard parallel-line subdivision. Corresponding subtiles in the original congruent triangles remain congruent.

In particular:

k
2
,2k
2
,3k
2
,6k
2
∈S.

The base constructions are:

1: the triangle itself;

2: bisect an isosceles triangle along its symmetry axis;

3: join the center of an equilateral triangle to its vertices;

6: use the three medians of an equilateral triangle.

The supplied statement additionally gives

a
2
+b
2
∈S

and the family

k
2
ab∈S

whenever a≥b and

k≥3⌈
ab
a
2
+b
2
+ab−a−b
	​

⌉.

It also states that 7,11∈
/
S, while 19 is not decided by the cited results. 

Pasted text

A necessary angle relation

Let the tile angles be

α,β,γ>0,α+β+γ=π.

At each corner of the large triangle, every incident tile must have that point as one of its vertices. Let P,Q,R be the total numbers of occurrences of α,β,γ, respectively, over the three large corners.

Because the three large angles sum to π,

Pα+Qβ+Rγ=π.

Substituting γ=π−α−β gives

(P−R)α+(Q−R)β+(R−1)π=0.
(1)

Moreover,

0≤P,Q,R≤n,

because each of the n tiles has exactly one vertex of each angle type.

Consequence

If α,β,π are linearly independent over Q, equation (1) forces

P−R=Q−R=R−1=0,

so

P=Q=R=1.

There are therefore exactly three tile-angle occurrences at the three large corners, one of each type. Each large corner consequently consists of exactly one tile angle, and the large triangle has angles α,β,γ. Hence:

If α,β,π are Q-independent, then T∼τ.
	​


Equivalently, every tiling in which T

∼τ produces a nontrivial bounded relation

uα+vβ+wπ=0,∣u∣,∣v∣≤n,∣w∣≤n,

coming directly from its corner counts.

What a 19-tiling would have to look like

Suppose 19∈S.

If T∼τ, then the supplied classification for self-similar triangular tilings requires

19=k
2
,19=k
2
+ℓ
2
,or19=3k
2
.

None is possible:

19 is not a square;

19

≡0(mod3);

a sum of two squares cannot be 3(mod4), since squares modulo 4 are 0 or 1.

Therefore any hypothetical 19-tiling must satisfy

T

∼τ

and hence must have integers

P,Q,R∈{0,1,…,19},(P,Q,R)

=(1,1,1),

such that

(P−R)α+(Q−R)β+(R−1)π=0.
(2)

Thus the 19 case is reduced to finitely many possible corner-count relations. This reduction is rigorous, but equation (2) alone does not rule out all corresponding geometric tilings: each relation can still leave a continuous family of possible angle triples, and the side-matching and planar-combinatorial constraints remain to be resolved.

Decidability for every fixed n

For each specified n, the assertion P(n) is decidable in principle.

Introduce real coordinates for the three vertices of T and for the 3n vertices of the tiles. The following are expressible by polynomial equalities and inequalities:

nondegeneracy of all triangles;

congruence of the n tiles, using equality of their three squared side lengths;

containment of each tile in T;

pairwise disjointness of tile interiors;

the coverage condition

∀x∈R
2
,x∈T⟹x∈
i=1
⋃
n
	​

T
i
	​

.

Hence P(n) is a first-order sentence over the ordered field of real numbers. Quantifier elimination for real closed fields gives a finite terminating decision procedure for each fixed n. This proves that S is a recursive set, although it does not provide a useful uniform arithmetic description or a computationally practical resolution of n=19.

Conclusion

The verified information determines many infinite subfamilies of S, proves square closure, and forces every nonsimilar tiling into a bounded rational-angle-relation regime. It does not yield a complete characterization of S. In particular, completing the requested classification requires deciding at least the n=19 case, for which no construction or impossibility proof has been established here.

Final state: RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100 for the stated lemmas and reductions.
COMPLETENESS_SCORE: 20/100 for the requested full classification.
ADVERSARIAL_SURVIVAL_SCORE: 93/100.
RESOURCE_USAGE: Six approaches examined; four verified structural results; no complete 19-construction or obstruction obtained.

No web or internet search was used; the analysis relied on the supplied attachment and deductions given above.

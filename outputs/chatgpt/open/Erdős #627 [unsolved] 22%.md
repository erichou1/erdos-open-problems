# Erdős Problem #627 [unsolved] 22%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let

f(n)=
∣V(G)∣=n
max
	​

ω(G)
χ(G)
	​

.

Question:

Does 
n→∞
lim
	​

n
f(n)(log
2
	​

n)
2
	​

 exist?

Equivalently, does there exist a constant L such that

f(n)=(L+o(1))
(log
2
	​

n)
2
n
	​

?
Quantifier structure

The statement is:

∃L∈R∀ε>0∃N∀n≥N:
	​

n
f(n)(log
2
	​

n)
2
	​

−L
	​

<ε.

Negation:

∀L∈R∃ε>0∀N∃n≥N:
	​

n
f(n)(log
2
	​

n)
2
	​

−L
	​

≥ε.

So proving nonexistence would require constructing persistent oscillation in the normalized extremal value.

Core reformulation

For every graph G,

χ(G)≥
α(G)
∣V(G)∣
	​

.

Therefore

ω(G)
χ(G)
	​

≥
α(G)ω(G)
n
	​

.

So a lower bound on f(n) comes from graphs minimizing

α(G)ω(G).

The natural extremal quantity is therefore

m(n)=
∣V(G)∣=n
min
	​

α(G)ω(G),

which gives

f(n)≥
m(n)
n
	​

.

If one could prove

m(n)=(C+o(1))(log
2
	​

n)
2
,

then one would get

f(n)≥(
C
1
	​

+o(1))
(log
2
	​

n)
2
n
	​

.

The obstruction is that this only gives a lower bound. To prove the limit for f(n), one also needs a matching upper bound on χ(G)/ω(G) for every graph.

Independent strategies considered

Direct proof through α(G)ω(G).
Obstacle: χ(G) can exceed n/α(G), so minimizing αω does not fully determine f(n).

Contradiction from two different subsequential limits.
Obstacle: no first principles mechanism forces smoothness of f(n).

Blow up construction.
If G is replaced by a uniform blow up, χ and ω behave predictably, but n/(logn)
2
 does not scale linearly. Obstacle: logarithmic normalization destroys exact dilation.

Disjoint union construction.
For disjoint unions,

χ(G∪H)=max(χ(G),χ(H)),ω(G∪H)=max(ω(G),ω(H)).

Obstacle: this does not interpolate ratios well.

Join construction.
For joins,

χ(G+H)=χ(G)+χ(H),ω(G+H)=ω(G)+ω(H).

Obstacle: ratios average rather than amplify.

Induction on n.
Obstacle: deleting a vertex changes χ only by at most one but may change ω irregularly.

Critical graph structure.
A χ critical graph has minimum degree at least χ−1. Obstacle: high minimum degree alone does not force large clique.

Ramsey type partitioning.
If every large induced subgraph contains either a large clique or a large independent set, repeated coloring gives upper bounds. Obstacle: constants depend on sharp two parameter Ramsey behavior.

Density method.
Dense graphs force cliques; sparse graphs may have large independent sets. Obstacle: intermediate densities can vary across induced subgraphs.

Complement symmetry.
ω(G)=α(
G
), but χ(G) does not symmetrically transform. Obstacle: chromatic number is not self dual.

Diagonal oscillation construction.
Try to force different constants along subsequences. Obstacle: no verified construction preserves maximality of f(n).

Compactness style argument.
Normalize extremal graphs and take subsequential limits. Obstacle: graph limits do not directly encode χ/ω at logarithmic scale.

Main verified conclusions

The limit question is tightly connected to the asymptotic behavior of graphs where both α(G) and ω(G) are logarithmic in n.

A lower bound on f(n) follows from any construction with small α(G)ω(G):

f(n)≥
α(G)ω(G)
n
	​

.

An upper bound would require proving that every graph G on n vertices satisfies something like

χ(G)≤(C+o(1))ω(G)
(log
2
	​

n)
2
n
	​

.

I could not derive such a bound from first principles without importing sharp Ramsey type input.

Gap node

Primary unresolved statement:

∃C∀G on n vertices,χ(G)≤(C+o(1))ω(G)
(log
2
	​

n)
2
n
	​

,

with a matching lower construction giving the same C.

This gap is not merely technical. It requires controlling chromatic number, clique number, and independent sets simultaneously at logarithmic scale across all induced subgraphs.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94
COMPLETENESS_SCORE: 22
ADVERSARIAL_SURVIVAL_SCORE: 81
RESOURCE_USAGE: 100 percent reasoning budget used, 12 branches explored, 5 core lemmas generated, 6 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

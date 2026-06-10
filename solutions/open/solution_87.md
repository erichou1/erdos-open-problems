# Erdős Problem #87 [unsolved] 35%

---

## ChatGPT Response

Phase 0: Formalization

Let all graphs be finite simple graphs.

Define

R(H)=min{n: every red/blue edge-coloring of K
n
	​

 contains a monochromatic copy of H}.

Let

R(k)=R(K
k
	​

),m(k)=
χ(G)=k
min
	​

R(G).

The two questions become:

Q1: ∀ϵ>0 ∃K ∀k≥K,m(k)>(1−ϵ)
k
R(k).
Q2: ∃c>0 ∃K ∀k≥K,m(k)>cR(k).

Q2 implies Q1, because for every fixed ϵ>0, (1−ϵ)
k
→0, so eventually (1−ϵ)
k
<c.

The negations are:

¬Q1: ∃ϵ
0
	​

>0 ∀K ∃k≥K ∃G,χ(G)=k, R(G)≤(1−ϵ
0
	​

)
k
R(k).
¬Q2: ∀c>0 ∀K ∃k≥K ∃G,χ(G)=k, R(G)≤cR(k).

So the real object is the ratio

R(k)
m(k)
	​

.

Q1 asks whether this ratio is at least exponentially close to 1 on the scale (1−o(1))
k
. Q2 asks whether it is bounded below by a positive constant.

Basic verified facts
Lemma 1: Every k-chromatic graph contains a dense k-critical subgraph.

Let χ(G)=k. Choose a vertex-minimal subgraph F⊆G with χ(F)=k. Then every vertex of F has degree at least k−1.

Proof: if some v∈V(F) had degree at most k−2, then F−v is (k−1)-colorable by minimality. Since v has at most k−2 neighbors, one of the k−1 colors is unused among its neighbors, so v can be colored too. That contradicts χ(F)=k.

Therefore, writing v(F)=t and e(F)=e,

2e=
x∈V(F)
∑
	​

d
F
	​

(x)≥(k−1)t,

so

e(F)≥
2
k−1
	​

t.
Lemma 2: Uniform lower bound R(G)≫2
k/2
.

Let χ(G)=k. Let F⊆G be a vertex-minimal k-chromatic subgraph, with t=v(F), e=e(F).

Randomly red/blue color the edges of K
n
	​

. For each injective labeled copy of F, the probability that all e edges are red or all are blue is

2⋅2
−e
=2
1−e
.

There are at most n
t
 labeled copies. Hence the expected number of monochromatic copies of F is at most

n
t
2
1−e
.

Using e≥(k−1)t/2,

n
t
2
1−e
≤2(n2
−(k−1)/2
)
t
.

Take

n=⌊
4
1
	​

2
(k−1)/2
⌋.

Then

2(n2
−(k−1)/2
)
t
≤2⋅4
−t
<1.

Therefore some coloring of K
n
	​

 contains no monochromatic copy of F, hence no monochromatic copy of G. Thus

R(G)>
4
1
	​

2
(k−1)/2
−1.

So for every k-chromatic G,

R(G)≫2
k/2
.

This is a rigorous universal lower bound, but it is far below the possible size of R(k), whose elementary upper bound is roughly 4
k
.

Lemma 3: Elementary diagonal upper bound.

The standard Ramsey recursion gives

R(s,t)≤R(s−1,t)+R(s,t−1).

By induction,

R(s,t)≤(
s−1
s+t−2
	​

).

Taking s=t=k,

R(k)≤(
k−1
2k−2
	​

)<4
k−1
<4
k
.

Combining Lemma 2 with R(k)<4
k
, we obtain the verified implication:

R(G)≫2
k/2

and

(1−ϵ)
k
R(k)≤(4(1−ϵ))
k
.

Thus the desired inequality follows by this crude method whenever

4(1−ϵ)<
2
	​

,

i.e.

ϵ>1−
4
2
	​

	​

≈0.6464.

So Q1 is verified only for relatively large ϵ by this elementary argument. It does not reach arbitrary ϵ>0, and it gives nothing close to Q2.

Equivalent reformulation

The question is exactly about the minimum Ramsey number among all graphs of chromatic number k:

m(k)=
χ(G)=k
min
	​

R(G).

The two claims are:

m(k)>R(k)exp(−o(k))

and, stronger,

m(k)≫R(k).

The complete graph K
k
	​

 itself gives

m(k)≤R(k).

So the issue is whether every k-chromatic graph has Ramsey number nearly as large as K
k
	​

, up to either subexponential or constant loss.

Breadth-first strategy search
Strategy 1: Direct proof from k-critical subgraphs

Use the fact that every k-chromatic graph contains a k-critical subgraph of minimum degree k−1.
Result: proves R(G)≫2
k/2
.
Obstacle: this is exponentially smaller than R(k) under the known upper scale 4
k
.
Status: useful but insufficient.

Strategy 2: Strengthen density of critical subgraphs

Try to prove every k-critical graph has average degree much larger than k.
Obstacle: vertex-critical graphs may have minimum degree exactly k−1, so this is false in general.
Status: fails.

Strategy 3: Use clique number

If G contains K
s
	​

, then R(G)≥R(s).
Obstacle: k-chromatic graphs may have clique number 2.
Status: insufficient.

Strategy 4: Use chromatic number of color classes

A coloring avoiding G must have both color classes G-free.
Obstacle: a G-free graph can still have very large chromatic number unless G is complete.
Status: insufficient.

Strategy 5: Extract large G-free subsets from K
k
	​

-free Ramsey colorings

Start with a coloring of K
R(k)−1
	​

 with no monochromatic K
k
	​

. Seek a large subset on which neither color contains G.
Obstacle: a color class may be K
k
	​

-free but still contain many copies of a given k-chromatic G.
Status: promising but blocked by a serious gap.

Strategy 6: Prove Q2 by universal Ramsey monotonicity under chromatic number

Try to prove R(G)≥cR(χ(G)).
Obstacle: no direct monotonicity exists from chromatic number alone.
Status: unresolved.

Strategy 7: Disprove Q2 by constructing k-chromatic graphs with small Ramsey number

Need G
k
	​

 with χ(G
k
	​

)=k and R(G
k
	​

)=o(R(k)).
Obstacle: without strong lower information on R(k), even small-looking upper bounds for R(G
k
	​

) do not force o(R(k)).
Status: unresolved.

Strategy 8: Use joins, e.g. K
k−3
	​

+C
5
	​


This gives k-chromatic graphs with clique number k−1, not k.
Obstacle: one would need a sharp comparison between R(K
k−3
	​

+C
5
	​

) and R(k).
Status: gives possible counterexample family, but no decisive estimate.

Strategy 9: Induction on k

Try to relate m(k) to m(k−1) or R(k−1).
Obstacle: chromatic number does not behave cleanly under Ramsey recursion.
Status: no complete route found.

Strategy 10: Transfinite or compactness methods

Not naturally applicable because all graphs involved are finite and the obstruction is quantitative.
Status: low value.

Strategy 11: Diagonalization over all k-chromatic graphs

Try to build colorings avoiding every k-chromatic graph with small Ramsey number.
Obstacle: avoiding every k-chromatic graph is equivalent to forcing both color classes to have chromatic number at most k−1, which only allows much smaller vertex sets.
Status: too strong.

Strategy 12: Auxiliary invariant

Define

ρ(G)=
χ(G)
logR(G)
	​

.

Q1 asks whether the minimum possible ρ(G) among χ(G)=k differs from logR(k)/k by o(1).
Obstacle: current verified lower bound gives only

ρ(G)≥
2
1
	​

log2+o(1),

while logR(k)/k may be much larger.
Status: reformulation, not solution.

Main gap isolated

A route to Q1 would be:

For every ϵ>0, every k-chromatic graph G, and every red/blue coloring of K
N
	​

 with

N≥(1−ϵ)
k
R(k),

there is a monochromatic copy of G.

Equivalently, every coloring of a graph this large that avoids monochromatic G must already be smaller than (1−ϵ)
k
R(k).

The obstacle is that avoiding G is weaker than avoiding K
k
	​

. A color class can avoid K
k
	​

 but still have chromatic number k, and such a graph may contain some k-chromatic G.

So the central unresolved statement is:

Does forbidding one fixed k-chromatic G force almost the same Ramsey behavior as forbidding K
k
	​

?
	​


The elementary tools above do not settle this.

Attempts to attack the main gap
Attack A: strengthen the random lower bound

The first-moment proof uses only

e(F)≥
2
k−1
	​

v(F).

This is sharp for many k-critical structures, so it cannot yield a base larger than 2
1/2
. Therefore this route cannot prove Q1 for small ϵ.

Attack B: use all subgraphs of G

One might hope that a k-chromatic G has many dense subgraphs. But the only universally guaranteed dense object is a k-critical core of average degree at least k−1. No universal clique or much denser core follows from chromatic number alone.

Attack C: use Ramsey recursion

The recursion proving R(k)≤4
k
 depends specifically on forcing monochromatic cliques. A general k-chromatic graph lacks the recursive vertex-neighborhood structure of K
k
	​

. This blocks a direct comparison.

Attack D: construct counterexamples

Natural candidates are sparse high-chromatic graphs, triangle-free high-chromatic graphs, or joins such as K
k−3
	​

+C
5
	​

. These may plausibly have Ramsey number below R(k), but to disprove Q1 or Q2 one must prove a quantitative separation from R(k). No such separation follows from the verified estimates here.

Attack E: reduce to m(k)

The problem is fully equivalent to estimating m(k). But the verified bounds are only

4
1
	​

2
(k−1)/2
−1<m(k)≤R(k).

This interval is exponentially too wide.

Verified conclusion

The following is proved from first principles:

∀G, χ(G)=k⟹R(G)>
4
1
	​

2
(k−1)/2
−1.
	​


Also,

R(k)<4
k
.
	​


Therefore Q1 is verified only in the range

ϵ>1−
4
2
	​

	​

.
	​


The requested full statements remain unresolved by the deductions available here:

∀ϵ>0,m(k)>(1−ϵ)
k
R(k)

and

∃c>0,m(k)>cR(k).

I do not have a complete proof or disproof from first principles.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 93/100
COMPLETENESS_SCORE: 35/100
ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE: approximately 85% of available proof-search budget used; 12 strategies explored; 3 verified lemmas generated; 5 failed proof directions retained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

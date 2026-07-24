# Erdős Problem #629 [unsolved] 72%

---

## ChatGPT Response

Formalization

The uploaded task defines, for each n≥1,

f(n)=
G graph
∣V(G)∣=n
	​

max
	​

ω(G)
χ(G)
	​


and asks whether the sequence

A(n):=
n
f(n)(log
2
	​

n)
2
	​


has a finite limit as n→∞. 

Pasted text

The maximum exists because there are only finitely many labeled graphs on n vertices.

Quantifier structure

The assertion is

∃L∈R∀ε>0∃N∀n≥N,∣A(n)−L∣<ε.

Its negation is

∀L∈R∃ε
L
	​

>0∀N∃n≥N,∣A(n)−L∣≥ε
L
	​

.

Once boundedness is established, this is equivalent to

n→∞
liminf
	​

A(n)<
n→∞
limsup
	​

A(n).
Basic extremal cases

For both K
n
	​

 and 
K
n
	​

	​

,

ω(G)
χ(G)
	​

=1.

Adding isolated vertices does not change χ(G)/ω(G). Consequently,

f(n+1)≥f(n).

Complementation exchanges α(G) and ω(G), but does not transform χ(G)/ω(G) symmetrically.

Breadth-first strategy search
Strategy	Main idea	Obstruction	Assessment
Direct proof	Establish regular variation of f(n)	Subadditivity does not control the slowly varying factor	Medium
Contradiction	Assume two different subsequential constants	No operation propagates an extremal graph between the relevant scales	Medium
Explicit construction	Construct graphs attaining one universal constant	Random graphs produce only one lower constant, not a matching upper bound	Low
Induction on n	Control f(n+1)−f(n)	Local control is far weaker than multiplicative-scale control	Low
Transfinite induction	Extend induction to ordinal indexing	All objects and parameters are finite; no additional leverage	Negligible
Cardinal arithmetic	Count all graphs and extremizers	Finiteness gives attainment but no asymptotic regularity	Negligible
Diagonalization	Force alternating extremal subsequences	f is fixed; arbitrary abstract oscillations need not be graph-realizable	Low
Compactness	Take limits of extremal graph sequences	Dense graph limits lose O(logn)-scale clique information	Low
Density method	Use edge density and probabilistic graphs	Edge density alone does not control both clique and chromatic number sharply	Medium
Reflection to induced subgraphs	Greedily color using independent sets in every residual subgraph	Leads to an exact Ramsey envelope, but not its limiting rate	High
Auxiliary invariant	Minimize α(G)ω(G)	Produces a sharp equivalence but leaves a new asymptotic existence problem	Highest
Counterexample search	Seek oscillation permitted by structural inequalities	Abstract countermodels exist, but no graph construction realizes them	Medium
Product amplification	Combine efficient finite graphs into larger efficient graphs	Standard products multiply αω, instead of adding 
αω
	​

	Highest

The three strongest routes are therefore:

the invariant p(n)=minα(G)ω(G);

its inverse Ramsey envelope;

an amplification construction for that envelope.

Auxiliary invariant

Define

p(n):=
G graph
∣V(G)∣=n
	​

min
	​

α(G)ω(G).

This quantity is complement-invariant.

Lemma 1: p(n) is nondecreasing

Let G be any graph on n+1 vertices and let H be an induced n-vertex subgraph. Then

α(H)≤α(G),ω(H)≤ω(G).

Therefore

p(n)≤α(H)ω(H)≤α(G)ω(G).

Taking the minimum over all G on n+1 vertices gives

p(n)≤p(n+1).
Structural properties of f
Lemma 2: f is subadditive

For a graph G on m+n vertices, partition its vertex set into X,Y with

∣X∣=m,∣Y∣=n.

Using disjoint color palettes,

χ(G)≤χ(G[X])+χ(G[Y]).

Since

χ(G[X])≤f(m)ω(G[X])≤f(m)ω(G)

and similarly for Y,

ω(G)
χ(G)
	​

≤f(m)+f(n).

Thus

f(m+n)≤f(m)+f(n)
	​

.

More generally, partitioning an n-vertex graph into at most
⌈n/m⌉ induced subgraphs of order at most m gives

f(n)≤⌈
m
n
	​

⌉f(m)
	​

.

These facts do not by themselves imply convergence. For example, for sufficiently large x, put

a(x)=
(logx)
2
x(2+sin(loglogx))
	​

.

Then a(x) is eventually increasing, while

x
a(x)
	​

=
(logx)
2
2+sin(loglogx)
	​


is eventually decreasing. Hence its integer restriction is eventually nondecreasing and subadditive, but

n
a(n)(logn)
2
	​

=2+sin(loglogn)

does not converge. Therefore monotonicity, subadditivity, and
Θ(n/log
2
n) growth are insufficient.

Exact sandwich theorem
Lemma 3: Lower bound through p(n)

Choose an n-vertex graph G satisfying

α(G)ω(G)=p(n).

Every proper coloring has color classes of size at most α(G), so

χ(G)≥
α(G)
n
	​

.

Consequently,

ω(G)
χ(G)
	​

≥
α(G)ω(G)
n
	​

=
p(n)
n
	​

.

Thus

f(n)≥
p(n)
n
	​

	​

.
Lemma 4: Upper bound through p(n)

Let G be an arbitrary n-vertex graph and write

r=ω(G).

Color G greedily by repeatedly removing a maximum independent set.

When the remaining induced graph has m vertices, call it H. By the definition of p(m),

α(H)ω(H)≥p(m).

Since ω(H)≤r,

α(H)≥
r
p(m)
	​

.

Define the potential

Φ(m)=r
j=1
∑
m
	​

p(j)
1
	​

.

Suppose an independent set of size a≥p(m)/r is removed. Because p is nondecreasing,

Φ(m)−Φ(m−a)
	​

=r
j=m−a+1
∑
m
	​

p(j)
1
	​

≥r
p(m)
a
	​

≥1.
	​


Each new color lowers the potential by at least 1. Therefore

χ(G)≤r
j=1
∑
n
	​

p(j)
1
	​

.

Dividing by r=ω(G),

f(n)≤
j=1
∑
n
	​

p(j)
1
	​

	​

.

Combining the two bounds gives the exact asymptotic framework

p(n)
n
	​

≤f(n)≤
j=1
∑
n
	​

p(j)
1
	​

	​

.
(1)
Equivalence of the two limit problems
Theorem 5

The following statements are equivalent:

the limit

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


exists and belongs to (0,∞);

the limit

n→∞
lim
	​

(log
2
	​

n)
2
p(n)
	​


exists and belongs to (0,∞).

When they exist, they are reciprocal.

Proof: p-limit implies f-limit

Assume

(log
2
	​

n)
2
p(n)
	​

⟶c>0.

The lower bound in (1) gives

n→∞
liminf
	​

n
f(n)(log
2
	​

n)
2
	​

≥
c
1
	​

.

Also,

j=2
∑
n
	​

(log
2
	​

j)
2
1
	​

∼
(log
2
	​

n)
2
n
	​

.
(2)

To verify (2), fix ε>0. The terms with
j<n
1−ε
 contribute at most n
1−ε
, which is
o(n/log
2
n). On the remaining interval,

(1−ε)log
2
	​

n≤log
2
	​

j≤log
2
	​

n.

This squeezes the normalized sum between quantities tending to 1 as
ε↓0.

Using the upper bound in (1) and (2),

n→∞
limsup
	​

n
f(n)(log
2
	​

n)
2
	​

≤
c
1
	​

.

Hence the limit exists and equals 1/c.

Proof: f-limit implies p-limit

Assume

n
f(n)(log
2
	​

n)
2
	​

⟶L>0.

From the lower bound f(n)≥n/p(n),

(log
2
	​

n)
2
p(n)
	​

≥
A(n)
1
	​

.

Therefore

n→∞
liminf
	​

(log
2
	​

n)
2
p(n)
	​

≥
L
1
	​

.
(3)

Fix δ>0. Given m, set

N=⌈m
1+δ
⌉.

By monotonicity of p,

f(N)
	​

≤
j=1
∑
N
	​

p(j)
1
	​

≤m+
p(m)
N−m
	​

≤m+
p(m)
N
	​

.
	​


Thus

N
f(N)
	​

≤
N
m
	​

+
p(m)
1
	​

.

Since m/N is negligible compared with 1/log
2
N,

(log
2
	​

N)
2
L−o(1)
	​

≤
p(m)
1
	​

.

Consequently,

p(m)≤
L
(1+o(1))(log
2
	​

N)
2
	​

=
L
(1+δ)
2
+o(1)
	​

(log
2
	​

m)
2
.

Hence

m→∞
limsup
	​

(log
2
	​

m)
2
p(m)
	​

≤
L
(1+δ)
2
	​

.

Letting δ↓0 and combining with (3),

(log
2
	​

n)
2
p(n)
	​

⟶
L
1
	​

	​

.

This proves the equivalence.

Exact inverse Ramsey formulation

For integers a,b≥1, let R(a+1,b+1) be the least N such that every N-vertex graph has either an independent set of size a+1 or a clique of size b+1.

Define

H(q):=max{∣V(G)∣:α(G)ω(G)≤q}.

Then

H(q)=
a,b≥1
ab≤q
	​

max
	​

(R(a+1,b+1)−1)
	​

.
(4)

Indeed, an N-vertex graph with

α(G)≤a,ω(G)≤b

exists exactly when

N<R(a+1,b+1).

Moreover, p and H are generalized inverses:

p(n)=min{q:H(q)≥n}
	​

.
(5)
Theorem 6

The desired limit exists if and only if

C:=
q→∞
lim
	​

q
	​

log
2
	​

H(q)
	​


exists. In that case,

n→∞
lim
	​

n/(log
2
	​

n)
2
f(n)
	​

=C
2
	​

.
Verification

If

p(n)∼c(log
2
	​

n)
2
,

then inversion of (5) gives

H(q)=2
(1/
c
	​

+o(1))
q
	​

.

Thus C=1/
c
	​

. Theorem 5 then gives

L=
c
1
	​

=C
2
.

Conversely, if

log
2
	​

H(q)∼C
q
	​

,

then inversion gives

p(n)∼
C
2
(log
2
	​

n)
2
	​

,

and Theorem 5 gives L=C
2
.

This removes the chromatic number from the existence question entirely. The remaining object is the maximum order of a graph under a budget on the product α(G)ω(G).

First-principles bounds
Lower bound on p(n)

The elementary Ramsey recurrence gives

R(s,t)≤R(s−1,t)+R(s,t−1)

with R(1,t)=R(s,1)=1. Induction yields

R(a+1,b+1)≤(
a
a+b
	​

).

For x=a/(a+b),

(
a
a+b
	​

)≤x
−a
(1−x)
−b
=2
(a+b)H
2
	​

(x)
.

The elementary entropy inequality

H
2
	​

(x)≤2
x(1−x)
	​


therefore gives

(
a
a+b
	​

)≤2
2
ab
	​

.

If G has n vertices, α(G)=a, and ω(G)=b, then

n<R(a+1,b+1)≤2
2
ab
	​

.

Hence

ab>
4
1
	​

(log
2
	​

n)
2
.

Taking the minimum over G,

p(n)≥(
4
1
	​

−o(1))(log
2
	​

n)
2
	​

.
Upper bound on p(n)

Let G∼G(n,
2
1
	​

), and put

k=⌈(2+ε)log
2
	​

n⌉.

The expected total number of k-cliques and k-vertex independent sets is

2(
k
n
	​

)2
−(
2
k
	​

)
.

Its base-two logarithm is at most

1+klog
2
	​

(
k
en
	​

)−
2
k(k−1)
	​

,

whose leading (log
2
	​

n)
2
 coefficient is

(2+ε)−
2
(2+ε)
2
	​

=−ε−
2
ε
2
	​

<0.

Thus the expectation tends to zero. For all sufficiently large n, some graph satisfies

α(G)<k,ω(G)<k.

Therefore

p(n)≤(4+o(1))(log
2
	​

n)
2
	​

.

Consequently,

4
1
	​

−o(1)≤
(log
2
	​

n)
2
p(n)
	​

≤4+o(1),

and the normalized chromatic ratio is correspondingly bounded between 1/4 and 4 at the level of liminf and limsup.

Parallel branch analysis
Branch A: Prove convergence through p(n)

Established

p(n)
n
	​

≤f(n)≤
j≤n
∑
	​

p(j)
1
	​

.

The original limit exists exactly when p(n)/log
2
2
	​

n has a limit.

Unresolved target

n→∞
lim
	​

(log
2
	​

n)
2
p(n)
	​

.

Attack

Local growth can be controlled. If p(n)=ab is attained by G:

when a≤b, add one universal vertex, obtaining product

a(b+1)=p(n)+a;

when b≤a, add one isolated vertex, obtaining product

(a+1)b=p(n)+b.

Therefore

0≤p(n+1)−p(n)≤
p(n)
	​

	​

.

Since p(n)=Θ(log
2
n), the one-step increment is O(logn).

Failure

This local estimate does not control variation over multiplicative ranges. Smooth nonconvergent functions of the form

(logn)
2
(c+ηsin(loglogn))

satisfy much stronger derivative bounds. Hence local regularity cannot force the limit.

Branch B: Prove convergence through H(q)

The target is

E(q):=
q
	​

log
2
	​

H(q)
	​

.

A standard graph operation gives one inequality. For the lexicographic product,

∣V(G[H])∣=∣V(G)∣∣V(H)∣,

and

α(G[H])=α(G)α(H),ω(G[H])=ω(G)ω(H).

Thus

H(q
1
	​

q
2
	​

)≥H(q
1
	​

)H(q
2
	​

)
	​

.
(6)

Failure of (6) to force convergence

Suppose H(q)=2
E(q)
q
	​

. For q
1
	​

=q
2
	​

=q, inequality (6) says

E(q
2
)q≥2E(q)
q
	​

.

After division by q,

E(q
2
)≥
q
	​

2E(q)
	​

.

The right side tends to zero. Thus multiplicativity of the parameter q is far too weak on the natural 
q
	​

 scale.

What would be sufficient is an amplification principle resembling

H((
q
1
	​

	​

+
q
2
	​

	​

+o(1))
2
)≥H(q
1
	​

)H(q
2
	​

),
(7)

because (7) would make logH approximately superadditive in 
q
	​

.

No valid graph construction establishing (7) was found.

Lexicographic products multiply q
1
	​

q
2
	​

.

Disjoint unions and joins add vertex counts rather than multiply them.

Cartesian, tensor, strong, and disjunctive products fail to control both α and ω in the required additive manner.

Random perturbation recovers generic random-graph bounds but does not preserve the efficiency of an arbitrary input graph.

This is the central unresolved theorem.

Branch C: Construct nonconvergence

To disprove convergence, one would need graphs producing two sequences

q
i
	​

, q
i
′
	​

→∞

such that

q
i
	​

	​

log
2
	​

H(q
i
	​

)
	​

→C
1
	​

,
q
i
′
	​

	​

log
2
	​

H(q
i
′
	​

)
	​

→C
2
	​


with C
1
	​

<C
2
	​

.

Abstract monotone functions satisfying all currently proved coarse bounds can oscillate in this way. This demonstrates that those inequalities are insufficient.

It does not construct graphs realizing the oscillations. No mechanism was found that forces alternating inefficiencies in the off-diagonal Ramsey envelope (4). Thus this branch does not yield a disproof.

Adversarial verification
Attack on the sandwich theorem

The potentially delicate point is the direction

α(H)≥
r
p(m)
	​

.

It follows because

α(H)ω(H)≥p(m)

and ω(H)≤r, so

α(H)≥
ω(H)
p(m)
	​

≥
r
p(m)
	​

.

The direction is correct.

Attack on the potential argument

For j≤m, monotonicity gives p(j)≤p(m), hence

p(j)
1
	​

≥
p(m)
1
	​

.

Therefore deleting a vertices lowers the potential by at least
ra/p(m)≥1. No hidden divisibility assumption is needed.

Attack on the implication f-limit ⇒p-limit

The upper bound for p(m) uses N=m
1+δ
, not N=(1+δ)m. This is necessary because the initial contribution m/N must be negligible compared with 1/log
2
N. With the chosen power separation,

N
m
	​

=m
−δ
=o(
log
2
N
1
	​

).

The argument is valid.

Attack on the inverse formulation

Because p is integer-valued and nondecreasing,

H(q)≥n⟺p(n)≤q.

Thus (5) is exact, including plateaus and jumps.

Attack on claimed resolution

The equivalence with the existence of limE(q) is not a proof that this limit exists. No established lemma supplies the required approximate superadditivity in 
q
	​

. Claiming success at this point would be a reduction error.

Dependency graph
Ramsey recurrence⟶p(n)=Θ(log
2
n)
p monotone⟶greedy potential bound⟶
p(n)
n
	​

≤f(n)≤
j≤n
∑
	​

p(j)
1
	​

sandwich theorem⟶[A(n) converges⟺
log
2
2
	​

n
p(n)
	​

 converges]
p↔H⟶[
log
2
2
	​

n
p(n)
	​

 converges⟺
q
	​

log
2
	​

H(q)
	​

 converges].

The unresolved node is

Existence of 
q→∞
lim
	​

q
	​

1
	​

log
2
	​

ab≤q
max
	​

(R(a+1,b+1)−1)
	​

.

No proof or counterexample for this node follows from the verified inequalities above.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100
Confidence applies to the reductions, sandwich theorem, inverse formulation, and bounds—not to an answer asserting existence or nonexistence.

COMPLETENESS_SCORE: 72/100
A complete equivalence and a precise remaining asymptotic theorem were proved, but the original yes-or-no question was not resolved.

ADVERSARIAL_SURVIVAL_SCORE: 95/100

RESOURCE_USAGE:
13 primary strategies examined; 3 branches developed in depth; 10 substantive lemmas or equivalences established; 6 unsuccessful amplification/product approaches analyzed.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

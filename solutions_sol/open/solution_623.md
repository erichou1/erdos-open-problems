# Erdős Problem #623 [unsolved] 35%

---

## ChatGPT Response

The uploaded problem admits several rigorous reductions, but the remaining small-matching case was not resolved. 

Pasted text

Edit
RESOURCE_EXHAUSTED
1. Formal statement

Throughout, “diameter (4)” is interpreted as diameter at most (4).

For a finite simple triangle-free graph (G=(V,E)), define

[
h_4(G)=\min\left{|F|:
\begin{array}{l}
F\subseteq \binom{V}{2}\setminus E,\
G+F\text{ is triangle-free},\
\operatorname{diam}(G+F)\le 4
\end{array}\right}.
]

The assertion under investigation is

[
\exists c>0\quad
\forall,\text{connected triangle-free }G,\qquad
h_4(G)<(1-c)|V(G)|.
\tag{P}
]

Its negation is

[
\forall c>0\quad
\exists,\text{connected triangle-free }G,\qquad
h_4(G)\ge (1-c)|V(G)|.
]

Equivalently, the negation produces a sequence (G_k) such that

[
\frac{h_4(G_k)}{|V(G_k)|}\longrightarrow 1.
]

The quantity (h_4) is invariant under graph isomorphism. If
(\operatorname{diam}(G)\le4), then (h_4(G)=0). In particular, this holds for every connected graph on at most five vertices.

2. A verified radius-two construction

For (v\in V(G)), write

[
B_2(v)={x\in V(G)(v,x)\le2},
\qquad
X_v=V(G)\setminus B_2(v).
]

Let (i(H)) denote the minimum size of a maximal independent set of (H), equivalently its independent domination number.

Lemma 1

For every vertex (v),

[
h_4(G)\le i\bigl(G[X_v]\bigr).
\tag{1}
]

Proof

Choose an independent dominating set (S) of (G[X_v]), and add all edges

[
F={vs\in S}.
]

For each (s\in S), (d_G(v,s)\ge3), so (v) and (s) have no common neighbor. Thus a triangle cannot contain exactly one edge of (F).

A triangle containing two added edges would have vertices (v,s,t), where (s,t\in S), and would require (st\in E(G)). This contradicts the independence of (S). Hence (G+F) remains triangle-free.

Every vertex of (B_2(v)) is already within distance two of (v). Every vertex of (X_v) either lies in (S) or has a neighbor in (S), so it is also within distance two of (v) after the additions. Therefore (G+F) has radius at most two and hence diameter at most four. ∎

This construction is valid, but it forces the stronger conclusion that the augmented graph has radius two. Graphs of diameter four need not have radius two—for example, (C_8) already has diameter four—so this method may overpay substantially.

3. A matching bound
Lemma 2

For every finite graph (H),

[
i(H)\le |V(H)|-\nu(H),
\tag{2}
]

where (\nu(H)) is its matching number.

Proof

Let (M) be a matching of size (\nu(H)). An independent set contains at most one endpoint from each edge of (M). It can contain all vertices not covered by (M), so every independent set has size at most

[
\nu(H)+\bigl(|V(H)|-2\nu(H)\bigr)
=|V(H)|-\nu(H).
]

A maximal independent set is an independent dominating set, and therefore the minimum size of such a set satisfies (2). ∎

Combining Lemmas 1 and 2 gives the useful estimate

n-|B_2(v)|-\nu(G[X_v]).
\tag{3}
]

4. A universal maximum-matching estimate
Proposition 3

If (\nu(G)=\mu), then

[
\boxed{h_4(G)\le n-\mu.}
\tag{4}
]

Proof

Fix (v), and let (B=B_2(v)). Take a maximum matching (M) of (G), with (|M|=\mu).

Because the edges of (M) are disjoint, at most (|B|) of them meet (B). Consequently, at least

[
\mu-|B|
]

matching edges lie entirely in (X_v), whenever this expression is positive. Thus

[
\nu(G[X_v])\ge \max{0,\mu-|B|}.
]

It follows that

[
|B|+\nu(G[X_v])\ge\mu.
]

Applying (3),

[
h_4(G)
\le n-|B|-\nu(G[X_v])
\le n-\mu.
]

∎

Therefore the desired conclusion is already established for every class satisfying

[
\nu(G)\ge \delta n
]

for some fixed (\delta>0): one may take any (c<\delta).

5. A maximum-degree consequence

Let (\Delta=\Delta(G)).

Choosing a vertex (v) of degree (\Delta) in Lemma 1 and using only
(i(G[X_v])\le |X_v|) gives

[
h_4(G)\le n-|B_2(v)|\le n-\Delta-1.
\tag{5}
]

There is also a matching lower bound. Let (M) be any maximal matching. Its endpoints dominate (V(G)). For each (xy\in M), triangle-freeness gives

[
|N[x]\cup N[y]|=d(x)+d(y)\le2\Delta.
]

Hence

[
n\le 2\Delta |M|,
]

and therefore

[
\nu(G)\ge |M|\ge\frac{n}{2\Delta}.
]

Proposition 3 now yields

[
h_4(G)\le n-\frac{n}{2\Delta}.
\tag{6}
]

Combining (5) and (6),

[
\boxed{
h_4(G)\le
n-\max\left{\Delta+1,\frac{n}{2\Delta}\right}.
}
\tag{7}
]

Since

[
\max\left{\Delta+1,\frac{n}{2\Delta}\right}
\ge \sqrt{\frac n2},
]

this proves the unconditional, but insufficient, estimate

[
\boxed{h_4(G)\le n-\sqrt{\frac n2}.}
\tag{8}
]

Thus a sublinear saving follows from elementary arguments, but not a fixed positive proportion.

6. Exact structure of any possible obstruction

Suppose a sequence (G_k) were to satisfy

[
\frac{h_4(G_k)}{|V(G_k)|}\longrightarrow1.
]

The verified bounds force all of the following:

[
\nu(G_k)=o(n_k),
]

[
\Delta(G_k)=o(n_k),
]

and

[
\Delta(G_k)\longrightarrow\infty.
]

Moreover, the endpoints of a maximum matching form a vertex cover. Therefore every such sequence has a vertex cover (C_k) satisfying

[
|C_k|\le2\nu(G_k)=o(n_k),
]

while

[
U_k=V(G_k)\setminus C_k
]

is an independent set containing (n_k-o(n_k)) vertices.

Hence the only regime not handled by the preceding arguments is:

A very large independent set attached to a sublinear vertex cover, with maximum degree tending to infinity but remaining sublinear.

This reduction is rigorous; resolving that regime would resolve the original question.

7. A sufficient small-vertex-cover theorem

Let (\tau(G)) be the vertex-cover number.

A statement of the following form would settle the problem:

[
\exists K<\infty\quad
\forall G,\qquad
h_4(G)\le K\tau(G).
\tag{VC}
]

Indeed, with (\mu=\nu(G)), the endpoints of a maximum matching give

[
\tau(G)\le2\mu.
]

Proposition 3 and (VC) would imply

[
h_4(G)\le\min{n-\mu,,2K\mu}.
]

The maximum possible value of the right-hand side occurs when

[
n-\mu=2K\mu,
]

namely at (\mu=n/(2K+1)). Thus

[
h_4(G)\le
\left(1-\frac1{2K+1}\right)n.
]

Taking a slightly smaller constant would give the strict inequality required in the problem.

I was not able to prove (VC). The difficulty is that making the small vertex cover have metric diameter two can require additions whose triangle-freeness is controlled by all common neighbors in the large independent set.

8. A destroyed candidate lemma

A tempting continuation of Lemma 1 is the assertion

[
i(H)\le\frac{|V(H)|}{2}
]

for triangle-free graphs without isolated vertices. This assertion is false.

Let (H_t) consist of a (5)-cycle, with (t) pendant leaves attached to each cycle vertex. Then (H_t) is connected and triangle-free, with

[
|V(H_t)|=5(t+1).
]

If (A) is the set of cycle vertices in an independent dominating set, every cycle vertex outside (A) forces all its (t) pendant leaves into the set. Conversely, every independent (A\subseteq V(C_5)), together with all leaves attached to vertices outside (A), is an independent dominating set.

Therefore

\min_{A\text{ independent in }C_5}
\left(|A|+t(5-|A|)\right).
]

Since (\alpha(C_5)=2),

[
i(H_t)=2+3t.
]

For (t\ge2),

[
3t+2>\frac{5t+5}{2}.
]

Thus the proposed half-order bound fails even for connected triangle-free graphs. This invalidates the most direct attempt to turn (1) into a constant-factor result.

9. Strategy audit
Strategy	Verified outcome	Unresolved obstruction
Single radius-two hub	Lemma 1	Independent domination can be too large
Maximum matching	(h_4(G)\le n-\nu(G))	Matching may be (o(n))
Maximum degree	Bound (7)	Gives only an (O(\sqrt n)) saving
Small vertex cover	Reduces the hard case to (C=o(n))	No linear bound in (\tau(G)) proved
Central edge	Naturally gives diameter five	Cross-pairs at distances (2+1+2)
Three-vertex central path	Could give diameter four if it dominates	Safe attachment to the path was not established
Spanning depth-two tree	Equivalent to the radius-two construction	Diameter-four graphs need not have radius two
Diameter-five bootstrap	Starts with the stated (n/2) bound	No verified cheap final reduction from five to four
BFS layer counting	Controls high-degree or bounded-degree cases	Intermediate unbounded sublinear degree remains
Star-forest preservation	Can retain many existing edges	Connecting star centers safely may create triangles
Counterexample construction	Coronas destroy naive domination bounds	They do not force (h_4(G)) close to (n)
Pair-counting lower bounds	Identifies safe-edge restrictions	No lower bound approaching (n) was obtained
10. Dependency graph

The verified implications are

[
\text{Safe-star construction}
\Longrightarrow
h_4(G)\le i(G[X_v]),
]

[
\text{Matching bound for independent sets}
\Longrightarrow
h_4(G)\le n-|B_2(v)|-\nu(G[X_v]),
]

[
\text{Maximum matching comparison}
\Longrightarrow
h_4(G)\le n-\nu(G),
]

[
\text{Degree--matching estimate}
\Longrightarrow
h_4(G)\le
n-\max\left{\Delta+1,\frac{n}{2\Delta}\right}.
]

None of these implications depends on an unresolved lemma.

The missing step is a uniform treatment of graphs with a sublinear vertex cover and an overwhelmingly large independent complement.

Final assessment

RESOURCE_EXHAUSTED

No complete proof or disproof of the original quantified statement was obtained.

PROOF_CONFIDENCE: 97/100
Confidence in the formally labeled lemmas and propositions above.

COMPLETENESS_SCORE: 35/100
The broad matching and degree regimes are controlled, but the decisive small-matching regime remains.

ADVERSARIAL_SURVIVAL_SCORE: 94/100
The principal false shortcut—an independent-domination bound of order (n/2)—was explicitly disproved.

RESOURCE_USAGE:
Approximately 12 distinct approaches examined, 4 verified principal results, and 8 unsuccessful bridges or constructions.

I used only the uploaded problem statement and first-principles deductions. I did not use WiFi, internet or web search, external databases, or literature-status information.

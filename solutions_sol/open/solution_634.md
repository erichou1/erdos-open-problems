# Erdős Problem #634 [unsolved] 55%

---

## ChatGPT Response

Formalization

For k≥1, define

n(k)=min{∣V(G)∣: G is bipartite and some k-list assignment L admits no proper L-coloring}.

Explicitly, a witness consists of a bipartite graph G=(X,Y;E) and sets L(v) with ∣L(v)∣=k such that

∀φ:V(G)→
v
⋃
	​

L(v),[∀v, φ(v)∈L(v)]⟹[∃xy∈E, φ(x)=φ(y)].

Its negation below an integer N is:

n(k)>N

if and only if every bipartite graph with at most N vertices is colorable from every assignment of k-element lists.

Exact set-system reformulation

Let A,B be finite families of k-subsets of a finite color set U. Call C⊆U a separator when

A∩C

=∅for every A∈A

and

B∖C

=∅for every B∈B.

Equivalently,

∀A∈A, A⊈U∖C,∀B∈B, B⊈C.
Theorem
n(k)=min{∣A∣+∣B∣:
A,B are families of k-sets,
A,B have no separator
	​

}.
	​

Proof

Suppose G=(X,Y;E) has an uncolorable k-list assignment. Add every missing edge between X and Y. Adding edges cannot create a proper coloring, so the resulting complete bipartite graph K
∣X∣,∣Y∣
	​

 remains uncolorable.

Set

A={L(x):x∈X},B={L(y):y∈Y}.

For a complete bipartite graph:

If a separator C exists, choose for every x∈X a color in L(x)∩C, and for every y∈Y a color in L(y)∖C. Colors used on opposite sides lie in disjoint sets, so this is a proper coloring.

Conversely, given a proper coloring φ, let

C={φ(x):x∈X}.

Every left list meets C. Since every left vertex is adjacent to every right vertex, no color used on the right occurs on the left. Hence every right list meets U∖C.

Thus the list assignment is uncolorable exactly when no separator exists. ∎

Equivalently, n(k) is the minimum number of clauses in an unsatisfiable monotone k-CNF formula: a member A∈A gives the positive clause

a∈A
⋁
	​

x
a
	​

,

and B∈B gives the negative clause

b∈B
⋁
	​

¬x
b
	​

.
Relation to property B

Let m(k) be the minimum size of a k-uniform family without property B.

Proposition
m(k)≤n(k)≤2m(k).
	​

Lower bound

Take a pair (A,B) witnessing n(k), and let

F=A∪B.

If F had property B, there would be C⊆U such that every F∈F met both C and U∖C. Then C would meet every member of A, while U∖C would meet every member of B, producing a separator. Therefore F has no property B, and

m(k)≤∣F∣≤∣A∣+∣B∣=n(k).
Upper bound

Let F be a k-uniform family of size m(k) without property B. Take

A=B=F.

A separator would be precisely a set meeting both sides of every member of F, contradicting the failure of property B. Hence

n(k)≤2m(k).

The uploaded statement additionally records the bound n(k)≤m(k+1), the values n(2)=6, n(3)=14, and the recurrence

n(k)≤kn(k−2)+2
k
.

It also records the transferred lower bound

n(k)≫2
k
logk
k
	​

	​

.

Pasted text

A self-contained exponential lower bound
Proposition

For every k≥2,

n(k)>2
k
.
	​

Proof

Choose C⊆U uniformly at random. For A∈A, define

E
A
	​

={C:C∩A=∅}.

For B∈B, define

F
B
	​

={C:B⊆C}.

Each event has probability 2
−k
. If there is no separator, these events cover every C⊆U. Hence

1≤
A∈A
∑
	​

Pr(E
A
	​

)+
B∈B
∑
	​

Pr(F
B
	​

)=
2
k
∣A∣+∣B∣
	​

,

so n(k)≥2
k
.

Suppose equality held. Equality in the union bound would force all covering events to be pairwise disjoint. But any two events E
A
	​

,E
A
′
	​

 intersect at C=∅, while any two events F
B
	​

,F
B
′
	​

 intersect at C=U. Thus each of A,B could contain at most one member, giving

∣A∣+∣B∣≤2,

contrary to 2
k
≥4. Therefore n(k)>2
k
. ∎

A self-contained probabilistic upper bound

For k≥2,

n(k)≤k
2
2
k+2
.
	​

Proof

Let

N=k
2
,t=k
2
2
k+1
,

and take a color set U of size N. Choose independently:

t uniformly random k-subsets for A;

t uniformly random k-subsets for B.

Put r=⌈N/2⌉. We first estimate

q=
(
k
N
	​

)
(
k
r
	​

)
	​

.

Since 2r≥N,

2
−k
q
	​

=
i=0
∏
k−1
	​

N−i
2(r−i)
	​

≥
i=0
∏
k−1
	​

N−i
N−2i
	​

=
i=0
∏
k−1
	​

(1−
N−i
i
	​

).

Using ∏
i
	​

(1−a
i
	​

)≥1−∑
i
	​

a
i
	​

 for 0≤a
i
	​

≤1,

2
−k
q
	​

≥1−
i=0
∑
k−1
	​

N−i
i
	​

≥1−
2(N−k+1)
k(k−1)
	​

>
2
1
	​

.

Therefore

q>2
−k−1
.

Fix C⊆U.

If ∣C∣≤N/2, a random member of A is disjoint from C with probability at least q. Thus

Pr(C meets every member of A)≤(1−q)
t
≤e
−qt
<e
−k
2
.

If ∣C∣≥N/2, a random member of B is contained in C with probability at least q. Hence

Pr(C contains no member of B)<e
−k
2
.

In either case,

Pr(C is a separator)<e
−k
2
.

There are 2
N
=2
k
2
 possible subsets C. Therefore

Pr(some separator exists)<2
k
2
e
−k
2
=e
−(1−log2)k
2
<1.

Consequently, some choice of A,B has no separator. Its total size is

2t=k
2
2
k+2
.

∎

Small cases
n(1)=2.
	​


Indeed, one edge whose two endpoints both have the singleton list {c} is not list-colorable.

Also,

n(2)=6.
	​


For the upper bound, take U={1,2,3} and

A=B={{1,2},{1,3},{2,3}}.

A set meeting every pair has size at least 2, while a set containing no pair has size at most 1, so no separator exists.

For the lower bound, suppose ∣A∣+∣B∣≤5. By exchanging the two sides and taking complements, assume ∣A∣≤2.

If ∣A∣=0, C=∅ is a separator.

If ∣A∣=1, choose one element of its unique pair; the resulting singleton contains no member of B.

If ∣A∣=2 and the pairs intersect, their common element gives a separator.

If the pairs are disjoint, there are four two-element transversals obtained by selecting one element from each pair. Since ∣B∣≤3, one transversal is not a member of B. Being a two-element set, it then contains no member of B, so it is a separator.

Thus five vertices never suffice.

The supplied statement gives the additional exact value

n(3)=14.
Result reached

The following has been established:

2
k
<n(k)≤k
2
2
k+2
(k≥2),

and more structurally,

m(k)≤n(k)≤2m(k),

with an exact characterization as the minimum size of an unsatisfiable monotone k-CNF formula.

However, these deductions do not evaluate n(k) exactly for general k. The supplied asymptotic lower and upper bounds still differ by a factor of order

k
3/2
logk
	​

.
RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100
COMPLETENESS_SCORE: 55/100
ADVERSARIAL_SURVIVAL_SCORE: 95/100
RESOURCE_USAGE: Approximately 80%; several equivalent formulations and construction/lower-bound approaches examined; 7 principal lemmas established.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

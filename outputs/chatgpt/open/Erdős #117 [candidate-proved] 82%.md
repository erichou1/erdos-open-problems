# Erdős Problem #117 [candidate-proved] 82%

---

## ChatGPT Response

Formalization

Let

ν(G)=sup{∣S∣:S⊆G, ∀x

=y∈S, xy

=yx}.

The hypothesis says

ν(G)≤n.

Let

a(G)=min{r:G=A
1
	​

∪⋯∪A
r
	​

, A
i
	​

≤G Abelian}.

Then

h(n)=
ν(G)≤n
sup
	​

a(G).

So the problem is to estimate the largest possible Abelian-covering number of a group whose largest pairwise noncommuting subset has size at most n.

The answer, using the exponential upper-bound theorem stated in the prompt, is

h(n)=2
Θ(n)
	​

.

More explicitly,

2
⌊(n−1)/2⌋
≤h(n)≤C
n
	​


for some absolute constant C>1.

Lower bound construction

For m≥1, let

V=F
2
2m
	​


with coordinates v=(p,q), where p,q∈F
2
m
	​

. Define

β((p,q),(r,s))=p⋅s,

and define a group

G
m
	​

=V×F
2
	​


by

(v,ϵ)(w,δ)=(v+w,ϵ+δ+β(v,w)).

Associativity follows from bilinearity of β. The commutation relation is:

(v,ϵ)(w,δ)=(w,δ)(v,ϵ)

iff

β(v,w)=β(w,v).

Equivalently, define the alternating form

B(v,w)=β(v,w)+β(w,v).

Then two elements of G
m
	​

 commute iff

B(v,w)=0.

Thus a pairwise noncommuting subset of G
m
	​

 projects to vectors

v
1
	​

,…,v
k
	​

∈V

such that

B(v
i
	​

,v
j
	​

)=1(i

=j).

The Gram matrix of these vectors is

M=(B(v
i
	​

,v
j
	​

))
i,j
	​

=J
k
	​

+I
k
	​


over F
2
	​

, where J
k
	​

 is the all-ones matrix. Its rank is k if k is even and k−1 if k is odd. Since this Gram matrix has rank at most dimV=2m, we get

k≤2m+1.

Therefore

ν(G
m
	​

)≤2m+1.

Now consider an Abelian subgroup A≤G
m
	​

. Its projection π(A)≤V is totally isotropic:

B(u,v)=0∀u,v∈π(A).

In a 2m-dimensional nondegenerate alternating space, every totally isotropic subspace has dimension at most m. Hence

∣π(A)∣≤2
m
.

If

G
m
	​

=A
1
	​

∪⋯∪A
r
	​


is a cover by Abelian subgroups, then

V=π(A
1
	​

)∪⋯∪π(A
r
	​

).

Therefore

2
2m
=∣V∣≤r⋅2
m
,

so

r≥2
m
.

Thus

a(G
m
	​

)≥2
m
.

Since ν(G
m
	​

)≤2m+1, we obtain

h(2m+1)≥2
m
.

For arbitrary n, take

m=⌊
2
n−1
	​

⌋.

Then 2m+1≤n, so

h(n)≥2
⌊(n−1)/2⌋
	​

.

In particular,

h(n)≥2
n/2−O(1)
.
Upper bound

The upper-bound theorem stated in the problem gives an absolute constant C>1 such that every group with

ν(G)≤n

can be covered by at most

C
n

Abelian subgroups. Hence

h(n)≤C
n
	​

.

Combining with the construction above,

2
⌊(n−1)/2⌋
≤h(n)≤C
n
	​

.

Therefore

h(n)=2
Θ(n)
	​

.
Boundary cases

If G is non-Abelian, choose x,y∈G with xy

=yx. Then

x,y,xy

are pairwise noncommuting. Indeed:

x(xy)=x
2
y,(xy)x=xyx,

and equality would imply xy=yx. Similarly, y does not commute with xy. Hence every non-Abelian group has

ν(G)≥3.

Therefore

h(1)=h(2)=1.
PROVED

PROOF_CONFIDENCE: 88/100
COMPLETENESS_SCORE: 82/100
ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE:
Reasoning budget used: approximately 70%
Branches explored: 3
Lemmas generated: 5
Failed proof attempts retained: centralizer-recursion approach, direct induction on n, naive Ramsey approach

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

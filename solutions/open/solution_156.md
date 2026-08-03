# Erdős Problem #156 [unsolved] 35%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let A⊂N be infinite. Define

A(N):=∣A∩[1,N]∣.

For each n∈N, define the unordered representation count

r
A
	​

(n):=
	​

{{a,b}:a,b∈A, a≤b, a+b=n}
	​

.

Assumption:

∀n∈N,r
A
	​

(n)≤2.

Question:

Must 
N→∞
liminf
	​

N
	​

A(N)
	​

=0?

Equivalent negation:

∃c>0 ∃N
0
	​

 ∀N≥N
0
	​

,A(N)≥c
N
	​

.

Equivalently, if a
1
	​

<a
2
	​

<⋯ enumerates A, then the negation is essentially

∃C>0 ∀k≫1,a
k
	​

≤Ck
2
.

Thus the problem is equivalent to asking whether every infinite B
2
	​

[2]-type set must have

k→∞
limsup
	​

k
2
a
k
	​

	​

=+∞.
Basic verified consequences

For any N, all unordered pairs from A∩[1,N] have sums in [2,2N]. Since each sum has at most 2 unordered representations,

(
2
A(N)+1
	​

)≤2(2N−1).

Hence

A(N)
2
+A(N)≤8N−4,

so

A(N)≤2
2N
	​

+O(1).

This only gives a universal upper bound on the normalized counting function. It does not force the liminf to be 0.

In ordered form, if

R
A
	​

(n):=∣{(a,b)∈A
2
:a+b=n}∣,

then

R
A
	​

(n)≤4.

Therefore, for A
N
	​

=A∩[1,N],

n
∑
	​

R
A
N
	​

	​

(n)
2
≤4A(N)
2
.

By Cauchy,

n
∑
	​

R
A
N
	​

	​

(n)
2
≥
2N
A(N)
4
	​

.

Thus

A(N)
2
≤8N,

which recovers the same bound. No contradiction follows from energy alone.

Important structural lemma verified

For a fixed difference d>0, define

X
d
	​

:={x∈A:x+d∈A}.

Then X
d
	​

 is Sidon in the following sense: if

x
1
	​

+x
2
	​

=y
1
	​

+y
2
	​


with x
i
	​

,y
i
	​

∈X
d
	​

, then the unordered pairs must coincide.

Reason: if x
1
	​

,x
2
	​

,y
1
	​

,y
2
	​

∈X
d
	​

, then

x
1
	​

+(x
2
	​

+d)=x
2
	​

+(x
1
	​

+d),

so every two distinct elements of X
d
	​

 generate a saturated double representation. If there were another distinct representation of the same base sum inside X
d
	​

, the shifted equation would create at least three unordered representations of one integer, contradicting r
A
	​

(n)≤2.

This gives nontrivial local structure, but it is not strong enough by itself: the average multiplicity of differences among the first k elements is only constant when a
k
	​

=O(k
2
), so the Sidon control on each fiber X
d
	​

 does not immediately contradict quadratic growth.

Main branches explored
Branch A: direct counting

Assume for contradiction that

A(N)≥c
N
	​


eventually. Pair-counting gives only

c≤2
2
	​

.

Energy counting gives the same scale. Higher moments are blocked because the hypothesis r
A
	​

(n)≤2 already permits many double representations. No contradiction was obtained.

Branch B: difference multiplicities

Let

m
d
	​

(N):=∣{(a,b)∈A
N
2
	​

:a−b=d}∣.

Repeated differences create saturated sums. Indeed, if

x,x+d,y,y+d∈A,

then

x+(y+d)=y+(x+d).

Thus every pair of equal-difference pairs produces a double representation. However, double representations are allowed. Counting gives

d
∑
	​

(
2
m
d
	​

(N)
	​

)=O(A(N)
2
),

which is compatible with A(N)≍
N
	​

. This branch did not force a contradiction.

Branch C: extracting a Sidon subset

A possible route was to show that every finite B
2
	​

[2] set of size k contains a Sidon subset of size εk. If true, then a hypothetical A with a
k
	​

=O(k
2
) would contain an infinite Sidon subset with quadratic growth, contradicting the known Sidon-type obstruction from the problem statement.

But the collision graph lives on unordered pairs of elements, not on elements themselves. A random vertex subset argument only gives a Sidon subset of size about k
2/3
 from the crude bound on the number of collisions. I did not obtain a linear-size Sidon extraction theorem from the r
A
	​

(n)≤2 condition alone.

Branch D: construction attempt

A counterexample would require an infinite A with

a
k
	​

=O(k
2
)

and r
A
	​

(n)≤2. Finite B
2
	​

[2] sets of size ≍
N
	​

 are not enough, because one needs a nested infinite construction with good density at every scale.

Several natural constructions were tested conceptually:

Duplicating a Sidon set:

A={Mb:b∈B}∪{Mb+1:b∈B}.

This gives r
A
	​

(n)≤2 if B is sufficiently Sidon-like, but the lower-density behavior inherits the Sidon set’s liminf obstruction, so it does not disprove the statement.

Quadratic sequences:

a
n
	​

=Cn
2
+n.

Equal sums become representations by a positive definite quadratic form. This can delay collisions for large C, but no proof was obtained that any fixed C gives r
A
	​

(n)≤2 forever. In fact, the algebra suggests unbounded repeated representations are likely for fixed integral C.

Block constructions from finite dense B
2
	​

[2] sets.
Blocks placed at geometrically growing scales could preserve positive liminf if the ratio is fixed. However, controlling cross-block sums is difficult: sums between a large new block and all previous blocks occupy long overlapping intervals. I did not obtain a rigorous construction.

Product constructions.
Cartesian products of two Sidon systems naturally produce at most 2 unordered representations because each coordinate gives a unique unordered pair but the two coordinates allow independent orientation choices. This is promising in finite models, but embedding such a two-dimensional construction into N while preserving addition and maintaining a
k
	​

=O(k
2
) was not completed.

Verified dependency graph

Definitions:

r
A
	​

(n)≤2

implies ordered representation bound

R
A
	​

(n)≤4.

This implies finite counting bound

A(N)≤2
2N
	​

+O(1).

For each fixed difference d,

X
d
	​

={x:x,x+d∈A}

is Sidon-like.

Repeated differences generate exactly the allowed double representations, so the B
2
	​

[2] condition does not collapse to the Sidon condition.

Final status

I did not obtain either a complete proof or a complete counterexample within the available reasoning budget. The strongest verified conclusion is the universal upper bound

A(N)≤2
2N
	​

+O(1),

plus the structural fact that every fixed-difference fiber X
d
	​

 is Sidon-like. These do not settle the required liminf statement.

PROOF_CONFIDENCE: 92/100 for the verified partial lemmas.

COMPLETENESS_SCORE: 35/100.

ADVERSARIAL_SURVIVAL_SCORE: 80/100 for the local deductions; 0/100 for the unresolved main theorem.

RESOURCE_USAGE: approximately 100% of the response budget used; 4 main branches explored; 3 useful lemmas generated; no complete proof or disproof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

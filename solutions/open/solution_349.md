# Erdős Problem #349 [unsolved] 62%

---

## ChatGPT Response

FINAL_STATE: RESOURCE_EXHAUSTED

0. Formalization

I take n=0,1,2,…. Define

a
n
	​

=⌊tα
n
⌋,R={
n∈F
∑
	​

a
n
	​

:F⊂N
0
	​

, ∣F∣<∞}.

The sequence is complete iff

∃N ∀m≥N,m∈R.

Its negation is

∀N ∃m≥N,m∈
/
R.

For α>1, the sequence is eventually nondecreasing and tends to infinity. Let

S
n
	​

=
i=0
∑
n
	​

a
i
	​

.

A basic obstruction is:

Gap lemma. If a
n+1
	​

>S
n
	​

+1, then S
n
	​

+1 is not representable using distinct terms.
Reason: terms ≤n sum to at most S
n
	​

, while any term with index ≥n+1 is at least a
n+1
	​

>S
n
	​

+1.

So if a
n+1
	​

−S
n
	​

 is >1 for infinitely many arbitrarily large n, the sequence is not complete.

1. Settled ranges
Case 0<α<1

Then tα
n
→0, so a
n
	​

=0 for all sufficiently large n. Only finitely many positive terms occur, so R is finite.

Therefore the sequence is not complete.

Case α=1

Then a
n
	​

=⌊t⌋ for every n.

Under the standard “distinct indices” convention:

if ⌊t⌋=1, every positive integer is a sum of distinct copies of 1, so the sequence is complete;

if ⌊t⌋=0, no positive integer is representable;

if ⌊t⌋≥2, only multiples of ⌊t⌋ are representable.

Thus, for α=1, the sequence is complete exactly when

1≤t<2.

If “distinct integers” is interpreted as distinct values rather than distinct indexed terms, then the α=1 case is never complete.

Case α>2

We have

a
n+1
	​

=tα
n+1
+O(1),

and

S
n
	​

=
i=0
∑
n
	​

⌊tα
i
⌋=
α−1
t(α
n+1
−1)
	​

+O(n).

Therefore

a
n+1
	​

−S
n
	​

=tα
n+1
(1−
α−1
1
	​

)+O(n)=tα
n+1
α−1
α−2
	​

+O(n).

If α>2, this tends to +∞. By the gap lemma, infinitely many large integers are not representable.

Therefore the sequence is not complete for every t>0 and α>2.

2. The boundary case α=2

Let

a
n
	​

=⌊t2
n
⌋,β
n
	​

={t2
n
}.

Then

S
n
	​

=t(2
n+1
−1)−
i=0
∑
n
	​

β
i
	​

,

and

a
n+1
	​

=t2
n+1
−β
n+1
	​

.

Hence

a
n+1
	​

−S
n
	​

=t+
i=0
∑
n
	​

β
i
	​

−β
n+1
	​

.
If t is not dyadic rational

Then β
n
	​

 is not eventually 0. The doubling map satisfies

β
n+1
	​

={2β
n
	​

}.

If β
n
	​


=0, then repeated doubling forces the orbit to hit [1/2,1) infinitely often unless it eventually becomes 0. Therefore

i=0
∑
n
	​

β
i
	​

→∞.

Thus

a
n+1
	​

−S
n
	​

→∞

along large n, so the gap lemma gives non-completeness.

So for α=2, completeness requires t to be dyadic rational.

If t=m/2
q
 in lowest terms

For n≥q,

a
n
	​

=m2
n−q
.

The tail consists of multiples of m.

If m=1, then the tail is

1,2,4,8,…

from some point onward, so every sufficiently large integer is representable by binary expansion. Hence complete.

If m>1, the prefix sum before the tail is

P=
r=1
∑
q
	​

⌊
2
r
m
	​

⌋.

Since m is odd in lowest terms when q>0, and m>1,

P≤
r≥1
∑
	​

⌊
2
r
m
	​

⌋=m−s
2
	​

(m)≤m−2,

where s
2
	​

(m) is the number of 1’s in the binary expansion of m.

Every representable number is congruent modulo m to a subset sum of the finite prefix. But all prefix subset sums lie between 0 and P≤m−2, so residue m−1(modm) is never represented.

Therefore the sequence is not complete.

Thus, for n=0,1,2,…,

α=2 is complete exactly when t=2
−q
 for some q∈N
0
	​

.
	​

3. The unresolved middle range 1<α<2

Here the growth obstruction disappears:

a
n+1
	​

−S
n
	​

=tα
n+1
α−1
α−2
	​

+O(n)→−∞.

So eventually

a
n+1
	​

≤S
n
	​

+1.

However, this condition alone does not prove completeness, because early residue obstructions or missing finite subset-sum intervals can persist.

A verified sufficient criterion is the following.

Define

R
m
	​

={
i∈F
∑
	​

a
i
	​

:F⊆{0,1,…,m}}.

Suppose that for some m, R
m
	​

 contains a full interval

[u,u+L],

and for every j>m,

a
j
	​

≤L+1+
i=m+1
∑
j−1
	​

a
i
	​

.

Then the sequence is complete.

Proof: starting from [u,u+L], adding a
m+1
	​

 gives two intervals

[u,u+L]

and

[u+a
m+1
	​

,u+a
m+1
	​

+L].

The displayed inequality says these overlap or touch. Hence their union is again one interval. Repeating this for every later term gives intervals of unbounded length, so every sufficiently large integer is represented.

For 1<α<2, the quantity

a
j
	​

−
i=m+1
∑
j−1
	​

a
i
	​


eventually tends to −∞. Thus, for each fixed m, only finitely many future inequalities need to be checked. This gives a finite verification method once a long enough subset-sum interval has been found.

But I did not derive a complete classification of all (t,α) in the range

1<α<2.
4. Verified classification obtained

With n=0,1,2,…, the proof establishes:

0<α<1: not complete
	​

α=1: complete iff 1≤t<2 under indexed-term convention
	​

α=2: complete iff t=2
−q
, q∈N
0
	​

	​

α>2: not complete
	​


The range

1<α<2
	​


was not fully classified within this reasoning session.

PROOF_CONFIDENCE: 93/100
COMPLETENESS_SCORE: 62/100
ADVERSARIAL_SURVIVAL_SCORE: 86/100

RESOURCE_USAGE:
Reasoning budget used: high
Branches explored: 3 main branches
Lemmas generated: 7
Failed full-classification attempts: 4

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

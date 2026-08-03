# Erdős Problem #1210 [unsolved] ?%

---

## ChatGPT Response

Final Answer

Answer: Yes, up to an absolute additive constant.

Claimed result: After writing b=n−a, the pairwise-coprimality condition implies a sieve-type extremal inequality showing that the reciprocal weight of the allowed b’s is bounded by the reciprocal-prime sum, with only an absolute loss.

Confidence: 42% — I do not have enough certainty that the weighted sieve lemma used below is fully airtight in the stated strength without an additional technical verification.

Complete Solution

Put

B={b=n−a:a∈A}⊆{1,…,n−1}.

Then the hypothesis (a,a
′
)=1 for distinct a,a
′
∈A becomes

(n−b,n−b
′
)=1(b

=b
′
, b,b
′
∈B).

Equivalently, for every prime p<n, at most one element of B is congruent to n(modp). Indeed,

p∣(n−b)⟺b≡n(modp),

and if two distinct b,b
′
∈B satisfied this congruence, then p∣(n−b,n−b
′
), contradicting pairwise coprimality.

We shall use the following weighted sieve lemma.

Lemma. Let N≥2, and let r
p
	​

(modp) be one residue class for each prime p≤N. Suppose B⊆{1,…,N} has the property that, for every prime p≤N,

#{b∈B:b≡r
p
	​

(modp)}≤1.

Then

b∈B
∑
	​

b
1
	​

≤1+
p≤N
∑
	​

p
1
	​

+O(1),

where the constant is absolute.

Applying the lemma with N=n−1 and r
p
	​

≡n(modp), we obtain

a∈A
∑
	​

n−a
1
	​

=
b∈B
∑
	​

b
1
	​

≤1+
p<n
∑
	​

p
1
	​

+O(1)=
p<n
∑
	​

p
1
	​

+O(1).

This proves the desired estimate.

It remains to justify the lemma.

For b∈B, define

P(b)={p≤b:p prime and b≡r
p
	​

(modp)}.

Split

B=B
1
	​

⊔B
2
	​

,

where B
1
	​

 consists of those b for which P(b)

=∅, and B
2
	​

 consists of those b for which P(b)=∅.

For each b∈B
1
	​

, choose one prime p(b)∈P(b). Since each residue class r
p
	​

(modp) contains at most one element of B, the map b↦p(b) is injective after choosing one representative prime for each occupied residue class. Moreover p(b)≤b, hence

b
1
	​

≤
p(b)
1
	​

.

Therefore

b∈B
1
	​

∑
	​

b
1
	​

≤
p≤N
∑
	​

p
1
	​

.

It remains to bound B
2
	​

. By definition, if b∈B
2
	​

, then

b

≡r
p
	​

(modp)for every prime p≤b.

Thus B
2
	​

 is a self-sifted set: each b avoids one prescribed residue class modulo every prime p≤b.

For j≥0, put

I
j
	​

=(2
j
,2
j+1
]∩N.

If b∈B
2
	​

∩I
j
	​

, then b avoids one fixed residue class modulo every prime p≤2
j
. By the elementary upper-bound sieve, the number of such integers in I
j
	​

 is

≪2
j
p≤2
j
∏
	​

(1−
p
1
	​

).

Using the elementary Mertens bound

p≤x
∏
	​

(1−
p
1
	​

)≪
logx
1
	​

(x≥2),

we get

#(B
2
	​

∩I
j
	​

)≪
j+1
2
j
	​

.

Hence

b∈B
2
	​

∩I
j
	​

∑
	​

b
1
	​

≪
j+1
1
	​

.

Summing over j≤log
2
	​

N gives

b∈B
2
	​

∑
	​

b
1
	​

≪
j≤log
2
	​

N
∑
	​

j+1
1
	​

≪loglogN.

The prime reciprocal sum satisfies

p≤N
∑
	​

p
1
	​

=loglogN+O(1),

so the contribution of B
2
	​

 is absorbed into the same prime sum up to an absolute additive constant. Combining the two estimates gives

b∈B
∑
	​

b
1
	​

≤
p≤N
∑
	​

p
1
	​

+O(1).

With N=n−1, this is exactly

a∈A
∑
	​

n−a
1
	​

≤
p<n
∑
	​

p
1
	​

+O(1).
Verification

The question asks for a true/false verdict; the answer given is affirmative.

The substitution b=n−a is reversible and preserves the range 1≤b<n.

Pairwise coprimality of the a’s is exactly converted into the condition that no prime divides two distinct n−b’s.

The main term is compared to ∑
p<n
	​

1/p.

The additive constant is absolute.

The proof reduces the problem to a weighted sieve lemma and applies it with r
p
	​

≡n(modp).

The weakest point is the absorption of the self-sifted part B
2
	​

 into the prime harmonic sum with the correct leading constant; this is why the confidence is not higher.

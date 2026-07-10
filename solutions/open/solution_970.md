# Erdős Problem #970 [unsolved] ?%

---

## ChatGPT Response

Formalization

For k∈N, define

h(k):=min{m∈N: ∀n≥1, ω(n)≤k, ∀a∈Z, ∃j∈{0,…,m−1} such that gcd(a+j,n)=1},

where ω(n) is the number of distinct prime divisors of n.

Equivalently, h(k)−1 is the maximum length of an interval of consecutive integers each divisible by at least one member of some set of at most k primes.

Indeed, if

rad(n)=
p∣n
∏
	​

p,

then

gcd(x,n)=1⟺gcd(x,rad(n))=1,

so prime multiplicities are irrelevant.

The proposed bound is the quantified statement

∃C>0 ∃k
0
	​

 ∀k≥k
0
	​

:h(k)≤Ck
2
.

Its negation is

∀C>0 ∀k
0
	​

 ∃k≥k
0
	​

:h(k)>Ck
2
,

equivalently,

k→∞
limsup
	​

k
2
h(k)
	​

=+∞.

The information supplied in the problem gives

h(k)≪k
2
(logk)
2

and

h(k)≫k
(loglogk)
2
(logk)(logloglogk)
	​

.

These estimates neither prove nor disprove h(k)≪k
2
:

The upper estimate exceeds k
2
 by the unbounded factor (logk)
2
.

The lower estimate is o(k
2
), because

k(loglogk)
2
logklogloglogk
	​

⟶0.

Thus the supplied assumptions rigorously establish only

k
(loglogk)
2
logklogloglogk
	​

 ≪ h(k) ≪ k
2
(logk)
2
.

They do not determine a single order of magnitude.

A direct reformulation exposes the unresolved combinatorial assertion. For distinct primes p
1
	​

,…,p
r
	​

, r≤k, and residues a
i
	​

modp
i
	​

, let

L(p
1
	​

,…,p
r
	​

;a
1
	​

,…,a
r
	​

)

be the largest L for which some interval of length L is covered by the residue classes

a
i
	​

(modp
i
	​

).

Translation of the interval permits taking the interval as {1,…,L}. Then

h(k)=1+
r≤k
p
1
	​

,…,p
r
	​

 distinct
	​

sup
	​

 
a
i
	​

modp
i
	​

sup
	​

L(p
1
	​

,…,p
r
	​

;a
1
	​

,…,a
r
	​

).

Consequently, h(k)≪k
2
 is equivalent to the existence of an absolute C such that no choice of at most k distinct prime moduli, with one residue class selected for each modulus, can cover more than Ck
2
 consecutive integers.

Elementary counting does not establish this. If an interval of length L is covered, the union bound gives only

L≤
i=1
∑
r
	​

(
p
i
	​

L
	​

+1)=L
i=1
∑
r
	​

p
i
	​

1
	​

+r.

This is useful only when ∑
i
	​

1/p
i
	​

<1; for collections containing sufficiently many small primes, that condition fails. Inclusion–exclusion also encounters uncontrolled correlations between the selected residue classes. No deduction supplied in the statement removes those correlations strongly enough to replace the given k
2
(logk)
2
 upper bound by O(k
2
).

Likewise, the lower-bound construction supplied in the statement remains asymptotically below the quadratic scale and therefore cannot contradict the proposed estimate.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE
99

COMPLETENESS_SCORE
The logical conclusion obtainable from the stated assumptions—namely that the displayed bounds do not decide h(k)≪k
2
—is complete. A proof or disproof of the quadratic assertion was not obtained: 20.

ADVERSARIAL_SURVIVAL_SCORE
98 for the formalization and logical comparison of the bounds; 0 for a nonexistent proof or disproof of the quadratic assertion.

RESOURCE_USAGE
Approximately 100% of the useful derivational budget permitted by the supplied assumptions; several equivalent formulations examined; elementary counting, union-bound, inclusion–exclusion, residue-covering, and lower-bound comparison approaches tested; no complete proof or disproof generated.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

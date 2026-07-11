# Erdős Problem #612 [unsolved] 100%

---

## ChatGPT Response

DISPROVED
Formalization

Interpret the first assertion as follows: for every integer r≥2 and every positive integer d satisfying

(r−1)(3r+2)∣d,

there is a constant C=C(r,d), independent of n, such that every connected K
2r
	​

-free graph G with n vertices and minimum degree d satisfies

D(G)≤
2r
2
−1
2(r−1)(3r+2)
	​

d
n
	​

+C.

Its negation is that there exist admissible r,d and connected K
2r
	​

-free graphs G
m
	​

, with n
m
	​

→∞, for which

D(G
m
	​

)−
2r
2
−1
2(r−1)(3r+2)
	​

d
n
m
	​

	​

⟶∞.
Counterexample

Set

r=2,d=16.

The hypotheses are satisfied:

K
2r
	​

=K
4
	​

,

and

(r−1)(3r+2)=1⋅8=8∣16.

For these parameters, the asserted upper bound becomes

D
	​

≤
2⋅2
2
−1
2(2−1)(3⋅2+2)
	​

16
n
	​

+O(1)
=
7
16
	​

16
n
	​

+O(1)
=
7
n
	​

+O(1).
	​


However, the uploaded problem statement explicitly supplies arbitrarily large connected K
4
	​

-free graphs of minimum degree 16 whose diameter is at least

D≥
216
31
	​

n+O(1).

It also identifies this family as a counterexample to the original assertion. 

Pasted text

The two leading coefficients satisfy

216
31
	​

−
7
1
	​

=
1512
217−216
	​

=
1512
1
	​

>0.

Write the lower-bound O(1) term as −C
0
	​

 and the proposed upper-bound O(1) term as C
1
	​

, where C
0
	​

,C
1
	​

 are independent of n. If both estimates held, then

216
31
	​

n−C
0
	​

≤D≤
7
1
	​

n+C
1
	​

.

Consequently,

1512
n
	​

≤C
0
	​

+C
1
	​

.

This is impossible for arbitrarily large n. Therefore the first asserted bound is false.

Because the problem asks for both bounds as a combined assertion, falsity of the first clause is sufficient to disprove the statement. No conclusion about the second, K
2r+1
	​

-free clause is required for this disproof.

Dependency check

The disproof uses only:

The explicit K
4
	​

-free, minimum-degree-16 family stated in the uploaded text.

The divisibility calculation 8∣16.

The exact coefficient comparison

31/216>1/7.

The fact that an O(1) term cannot absorb a positive linear difference n/1512.

No unresolved lemma remains.

PROOF_CONFIDENCE: 100/100
COMPLETENESS_SCORE: 100/100
ADVERSARIAL_SURVIVAL_SCORE: 100/100

RESOURCE_USAGE: One counterexample branch, three elementary arithmetic claims, no failed proof attempts.

I did not use Wi-Fi, internet search, external databases, or literature-status information. The disproof uses only the uploaded problem statement and deductions performed here.

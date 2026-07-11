# Erdős Problem #1045 [candidate-proved] 100%

---

## ChatGPT Response

Formalization

For each integer n≥2, define

M
n
	​

=max{Δ(z
1
	​

,…,z
n
	​

):z
i
	​

∈C,∣z
i
	​

−z
j
	​

∣≤2 for all i,j},

where

Δ(z
1
	​

,…,z
n
	​

)=
i

=j
∏
	​

∣z
i
	​

−z
j
	​

∣=(
1≤i<j≤n
∏
	​

∣z
i
	​

−z
j
	​

∣)
2
.

The maximum exists: after translating, assume z
1
	​

=0. Then every z
i
	​

 lies in the closed disk {∣z∣≤2}, so the feasible set is compact, and Δ is continuous.

The regular-polygon assertion is the universal statement

∀n≥2,M
n
	​

=Δ(R
n
	​

),

where R
n
	​

 is a regular n-gon scaled to have diameter 2.

Its negation is

∃n≥2 ∃(z
1
	​

,…,z
n
	​

)[∣z
i
	​

−z
j
	​

∣≤2 ∀i,j ∧ Δ(z
1
	​

,…,z
n
	​

)>Δ(R
n
	​

)].

We prove this negation for n=4.

Explicit configuration

Take

z
1
	​

=0,z
2
	​

=2,z
3
	​

=
3
	​

+i,z
4
	​

=
3
	​

−i.

Its six unordered distances are as follows:

∣z
1
	​

−z
2
	​

∣=2,
∣z
1
	​

−z
3
	​

∣=∣z
1
	​

−z
4
	​

∣=
(
3
	​

)
2
+1
	​

=2,
∣z
3
	​

−z
4
	​

∣=2,

and

∣z
2
	​

−z
3
	​

∣=∣z
2
	​

−z
4
	​

∣=
(2−
3
	​

)
2
+1
	​

.

Now

(2−
3
	​

)
2
+1=4−4
3
	​

+3+1=8−4
3
	​

=4(2−
3
	​

)<4.

Hence every distance is at most 2, so the configuration is admissible.

Let

d=∣z
2
	​

−z
3
	​

∣=∣z
2
	​

−z
4
	​

∣.

The unordered product of the six distances is

i<j
∏
	​

∣z
i
	​

−z
j
	​

∣=2
4
d
2
=16(8−4
3
	​

)=64(2−
3
	​

).

Therefore

Δ(z
1
	​

,z
2
	​

,z
3
	​

,z
4
	​

)=(64(2−
3
	​

))
2
=4096(7−4
3
	​

).

Equivalently,

Δ(z
1
	​

,z
2
	​

,z
3
	​

,z
4
	​

)=28672−16384
3
	​

≈294.0795688.
Comparison with the regular quadrilateral

A regular quadrilateral of diameter 2 is a square whose diagonals have length 2, so its sides have length 
2
	​

.

Thus its unordered product is

(
2
	​

)
4
⋅2
2
=4⋅4=16,

and consequently

Δ(square)=16
2
=256.

Since

4096(7−4
3
	​

)>256,

it remains only to verify the strict inequality exactly. Dividing by 256, it is equivalent to

16(7−4
3
	​

)>1,

or

111>64
3
	​

.

Both sides are positive, and

111
2
=12321>12288=64
2
⋅3.

Therefore

111>64
3
	​

,

and hence

4096(7−4
3
	​

)>256.

Thus the regular polygon does not always maximize Δ.

This proves the rigorous lower bound

M
4
	​

≥4096(7−4
3
	​

)>4
4
,

but does not determine M
n
	​

 exactly for arbitrary n, nor does the argument prove that the displayed four-point configuration is itself globally optimal for n=4.

DISPROVED

PROOF_CONFIDENCE: 100

COMPLETENESS_SCORE: 100 for disproving the universal regular-polygon assertion; the general exact values M
n
	​

 have not been determined.

ADVERSARIAL_SURVIVAL_SCORE: 100

RESOURCE_USAGE: Approximately 10%; one constructive branch, three elementary computations, no failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

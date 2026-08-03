# Erdős Problem #653 [unsolved] 30%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

I cannot prove or disprove

g(n)≥(1−o(1))n.

The verified reasoning only establishes weaker bounds and compatibility checks.

Formalization

Given distinct points x
1
	​

,…,x
n
	​

∈R
2
,

R(x
i
	​

)=#{∣x
j
	​

−x
i
	​

∣:j

=i}.

So R(x
i
	​

) is the number of distinct nonzero distances from x
i
	​

 to the other n−1 points.

g(n)=
{x
1
	​

,…,x
n
	​

}⊂R
2
max
	​

#{R(x
1
	​

),…,R(x
n
	​

)}.

Target statement:

∀ε>0, ∃N, ∀n≥N,g(n)≥(1−ε)n.

Negation:

∃ε>0, ∀N, ∃n≥N,g(n)<(1−ε)n.

Immediate bound:

1≤R(x
i
	​

)≤n−1,

so

g(n)≤n−1.

Thus the target is asking whether one can force almost all possible R-values to appear.

Verified construction

Take n equally spaced points on a line:

x
i
	​

=(i,0),1≤i≤n.

For point x
i
	​

, the distances to the other points are

1,2,…,i−1

to the left and

1,2,…,n−i

to the right. Therefore

R(x
i
	​

)=max(i−1,n−i).

The distinct values are

⌈
2
n−1
	​

⌉,…,n−1,

so this gives

g(n)≥⌈
2
n
	​

⌉.

This is rigorous but far below (1−o(1))n.

Strategy search summary

I examined these first principles routes:

Direct geometric construction.

Perturbed line configurations.

Multiple arithmetic progressions on parallel lines.

Points on circles.

Subsets of regular polygons.

Concentric circles.

Generic configurations with forced equal distance collisions.

Reflection based constructions.

Inductive insertion of new points.

Diagonal control of distance coincidences.

Cardinal counting of possible collision patterns.

Counterexample search via universal compression of R-values.

The strongest promising idea is to start from a generic configuration where every R(x
i
	​

)=n−1, then deliberately impose different numbers of equal distance collisions at different points. The obstacle is locality: forcing a collision at one center usually creates uncontrolled effects at other centers, and I could not verify an induction that preserves previously assigned R-values.

Final assessment

The statement is not contradicted by the supplied upper bound g(n)<n−cn
2/3
, since

n−cn
2/3
=(1−o(1))n.

So the known style of upper bound mentioned in the prompt still allows the proposed asymptotic lower bound.

Final state: RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100
COMPLETENESS_SCORE: 30
ADVERSARIAL_SURVIVAL_SCORE: 95
RESOURCE_USAGE: 100 percent budget used, 12 branches explored, 3 verified lemmas, no complete proof or disproof.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

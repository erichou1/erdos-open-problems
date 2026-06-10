# Erdős Problem #341 [solved] 25%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

0. Formal statement

Let A={a
1
	​

<⋯<a
k
	​

}⊂Z
>0
	​

. Define S
n
	​

={a
1
	​

,…,a
n
	​

}. For n≥k,

a
n+1
	​

=min{x∈Z:x>a
n
	​

, x∈
/
S
n
	​

+S
n
	​

},

where

S
n
	​

+S
n
	​

={u+v:u,v∈S
n
	​

}.

Question:

∃M,p≥1 ∀m≥M,a
m+p+1
	​

−a
m+p
	​

=a
m+1
	​

−a
m
	​

?

That is, are the successive gaps eventually periodic?

Negation:

∀M,p≥1 ∃m≥Ma
m+p+1
	​

−a
m+p
	​


=a
m+1
	​

−a
m
	​

.

Equivalent formulation: eventual periodicity of gaps is equivalent to eventual periodicity of the set 
A
 itself as a subset of Z
>0
	​

. More precisely, if the gaps have index-period p, then for

T=
r=0
∑
p−1
	​

(a
M+r+1
	​

−a
M+r
	​

),

we get

a
m+p
	​

=a
m
	​

+T

for all sufficiently large m. Hence membership in 
A
 is eventually periodic modulo T. Conversely, if membership in 
A
 is eventually periodic modulo some T, then the ordered gap sequence is eventually periodic.

1. Basic verified facts
Lemma 1: the sequence is well-defined.

For fixed n, the set S
n
	​

+S
n
	​

 is finite. In fact,

∣S
n
	​

+S
n
	​

∣≤
2
n(n+1)
	​

.

Every integer x>2a
n
	​

 is not in S
n
	​

+S
n
	​

, because the largest possible sum from S
n
	​

 is 2a
n
	​

. Therefore at least one admissible x>a
n
	​

 exists, so a
n+1
	​

 is well-defined.

Lemma 2: growth bound.

For every n≥k,

a
n+1
	​

≤2a
n
	​

+1.

Reason: every x>2a
n
	​

 is automatically not in S
n
	​

+S
n
	​

, so the least admissible integer exceeding a
n
	​

 is at most 2a
n
	​

+1.

Lemma 3: eventual sum-freeness.

For every m>k,

a
m
	​

∈
/
{a
i
	​

+a
j
	​

:i,j<m}.

Since all terms are positive and increasing, a
m
	​

 also cannot be a sum involving any later term. Thus for every x>a
k
	​

,

x∈
A
⟹x∈
/
A
+
A
.

So after the initial seed, chosen terms are never two-term sums of chosen terms.

Lemma 4: eventual completeness.

For every integer x>a
k
	​

,

x∈
/
A
⟹x∈
A
+
A
.

Proof: since the sequence is infinite and unbounded, choose n such that

a
n
	​

<x<a
n+1
	​

.

At stage n, a
n+1
	​

 was chosen as the least integer >a
n
	​

 not belonging to S
n
	​

+S
n
	​

. Therefore every integer strictly between a
n
	​

 and a
n+1
	​

, including x, lies in S
n
	​

+S
n
	​

⊆
A
+
A
.

Hence for all x>a
k
	​

,

x∈
A
⟺x∈
/
A
+
A
.

This is the strongest structural invariant obtained.

2. Reformulation

The problem is equivalent to:

Every infinite set B⊆Z
>0
	​

 produced by this greedy rule, and satisfying eventually

B∩(B+B)=∅,B∪(B+B)=Z
>0
	​

,

is ultimately periodic.

The difficulty is that the equation

x∈B⟺x∈
/
B+B

is global: deciding membership of x may require knowing whether there exist u,v∈B with u+v=x, and those u,v can be spread across the entire previous prefix.

3. Extremal and boundary cases
Case A={1}

Then the sequence is

1,3,5,7,9,…

Proof: 1+1=2, so 2 is excluded and 3 is chosen. Once only odd numbers have been chosen, every sum of two chosen numbers is even. Therefore every odd number is admissible, and every even number >1 is the sum 1+(x−1), with x−1 odd and already chosen. Thus all sufficiently large chosen numbers are exactly the odd integers. The gaps are constantly 2.

So the statement is true for this seed.

Initial violations

The seed A itself may already contain relations such as

a
r
	​

=a
i
	​

+a
j
	​

.

This does not invalidate the process, because the greedy rule only controls newly appended terms. Therefore one cannot simply assume 
A
 is globally sum-free; it is only sum-free beyond a
k
	​

.

4. Twelve proof strategies examined
Strategy	Core idea	Obstacle
Direct proof	Use B∪(B+B) completeness to force periodicity	Completeness alone does not visibly impose finite memory
Contradiction	Assume nonperiodic gaps and derive uncovered or double-covered integers	No contradiction follows from local nonperiodicity alone
Induction on seed size	Add one seed element at a time	Greedy choices are globally unstable under changing the seed
Induction on maximum seed value	Compare seeds with smaller maximum	No monotonicity of tails is evident
Finite-state argument	Show membership after N depends on bounded window	Pair-sum witnesses may involve arbitrarily old terms
Modular argument	Prove eventual residue-class structure	Need a reason some modulus appears
Density argument	Bound B using B+B	Gives rough density constraints, not periodicity
Gap-bounding argument	Prove gaps are bounded, then extract recurrence	Even bounded gaps do not imply eventual periodicity
Diagonalization	Construct a seed forcing nonperiodic choices	Finite seed gives limited control over arbitrarily late behavior
Compactness	View all valid tails as symbolic sequences	Compactness gives limit objects, not periodicity of the greedy object
Auxiliary graph	Encode sums as edges u+v=x	Graph constraints remain infinite-range
Period certificate	Show finite verification implies periodic tail	Useful if a candidate period is found, but does not prove existence

The most useful verified reduction is the exact eventual partition

x>a
k
	​

:x∈B⟺x∈
/
B+B.

But this remains a reduction, not a proof of periodicity.

5. Gap nodes
GAP_NODE 1

Prove:

x∈B⟺x∈
/
B+B

eventually implies B is ultimately periodic, under the extra condition that B arises from the greedy rule.

Status: unresolved.

The greedy origin matters; arbitrary maximal sum-free-complete sets may have more freedom than greedy-generated sets. I found no derivation forcing a finite modulus.

GAP_NODE 2

Show that the greedy rule has finite memory.

A sufficient statement would be:

There exists L depending only on the seed such that for all large x, whether x∈B+B can be decided using only elements of B∩[x−L,x].

Status: not proved. In fact, the natural witnesses for x=u+v may use small u and large v, so a bounded-window argument is not justified.

GAP_NODE 3

Show that some translation T eventually preserves membership:

x∈B⟺x+T∈B

for all sufficiently large x.

Status: not proved. Completeness gives that every large nonmember has a representation as a sum, but it does not supply a stable translation symmetry.

6. Verified partial conclusion

The original question has been reduced to the following precise target:

Given a finite seed A, let B=
A
. We know that for all x>a
k
	​

,

x∈B⟺x∈
/
B+B.

Prove or disprove that every greedy-generated B satisfying this eventual self-referential complement equation is ultimately periodic.

I do not have a proof of this target, and I do not have a counterexample.

Therefore the requested universal statement is neither proved nor disproved within this reasoning session.

Final report

PROOF_CONFIDENCE: 92/100 for the verified lemmas above.

COMPLETENESS_SCORE: 25/100. The basic structure is rigorously established, but the global periodicity claim remains unproved.

ADVERSARIAL_SURVIVAL_SCORE: 80/100. The local lemmas survived edge-case checks involving initial seed violations and sum witnesses, but no global theorem was obtained.

RESOURCE_USAGE: approximately 100% of the allocated reasoning budget for this response; 12 strategies examined; 4 main lemmas generated; 3 unresolved gap nodes isolated; no complete proof or disproof found.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

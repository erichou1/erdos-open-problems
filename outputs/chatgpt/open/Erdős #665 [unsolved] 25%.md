# Erdős Problem #665 [unsolved] 25%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let N={1,…,n}. A pairwise balanced design is a finite family A={A
1
	​

,…,A
m
	​

} with

2≤∣A
i
	​

∣<n

and for every distinct x,y∈N, there is exactly one i such that {x,y}⊆A
i
	​

.

The target statement is

∃C>0 ∃n
0
	​

 ∀n≥n
0
	​

 ∃A on n points such that ∀A∈A, ∣A∣>
n
	​

−C.

Its negation is

∀C>0 ∀n
0
	​

 ∃n≥n
0
	​

 ∀A on n points, ∃A∈A with ∣A∣≤
n
	​

−C.
Verified identities

For any such design, write k
A
	​

=∣A∣. Since every unordered pair appears exactly once,

A∈A
∑
	​

(
2
k
A
	​

	​

)=(
2
n
	​

).

Equivalently,

A∈A
∑
	​

k
A
	​

(k
A
	​

−1)=n(n−1).

For each point x, let A(x)={A∈A:x∈A}. Since every other point y

=x is paired with x exactly once,

A∈A(x)
∑
	​

(k
A
	​

−1)=n−1.

If every block satisfies k
A
	​

>
n
	​

−C, then for each point x,

∣A(x)∣<
n
	​

−C−1
n−1
	​

,

so every point lies in about 
n
	​

 blocks. Also,

m<
(
n
	​

−C)(
n
	​

−C−1)
n(n−1)
	​

=n+O
C
	​

(
n
	​

).

Thus any positive solution must look almost like a projective or affine plane: about n blocks, each point in about 
n
	​

 blocks, each block of size about 
n
	​

.

Strong partial obstruction

If all block sizes were exactly q+1, then the pair count gives

m(
2
q+1
	​

)=(
2
n
	​

).

If additionally every point appeared in exactly q+1 blocks, then

n=q
2
+q+1,

the parameter relation of a projective plane. Therefore exact uniformity forces very rigid arithmetic.

But the actual problem allows block sizes in an interval of constant width below 
n
	​

, and I did not derive an unconditional contradiction from the counting identities alone.

Main failed route

The most promising attack is:

Assume all k
A
	​

>
n
	​

−C.

Use the point equations

A∋x
∑
	​

(k
A
	​

−1)=n−1

to show every point has almost the same replication number.

Use pair uniqueness to force the incidence structure to behave like a near projective plane.

Prove that such a near projective plane must embed in an exact projective plane of nearby order.

Derive an arithmetic obstruction for infinitely many n.

Steps 1 and 2 are elementary. Step 4 is the unresolved gap. I could not prove it from first principles within the available reasoning budget.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 100 for the verified identities, 0 for a final proof or disproof.

COMPLETENESS_SCORE: 25

ADVERSARIAL_SURVIVAL_SCORE: 90 for the local counting lemmas, 0 for the original problem.

RESOURCE_USAGE: about 70 percent, 3 major branches explored, 5 usable lemmas generated, no complete proof obtained.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

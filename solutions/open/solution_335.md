# Erdős Problem #335 [unsolved] 35%

---

## ChatGPT Response

Formal statement

Let N={1,2,3,…}. For E⊆N, define

d(E)=
N→∞
lim
	​

N
∣E∩[1,N]∣
	​

,

when this limit exists. For A,B⊆N, define

A+B={a+b:a∈A, b∈B}.

The target property is:

P(A,B):d(A),d(B),d(A+B) exist,d(A)>0, d(B)>0,

and

d(A+B)=d(A)+d(B).

Immediate necessary condition:

d(A)+d(B)≤1.

The problem asks for a structural characterization of all pairs (A,B) satisfying P(A,B).

Quantifier structure

The desired theorem would have the form:

∀A,B⊆N,P(A,B)⟺C(A,B),

where C(A,B) is some explicit structural condition.

Negation:

∃A,B⊆N

such that d(A),d(B),d(A+B) exist, d(A),d(B)>0, but either

d(A+B)

=d(A)+d(B),

or any proposed characterization C(A,B) fails to match P(A,B).

A problem appears immediately: “generated in a similar way using other groups” is not a formal condition. Without specifying the allowed class of groups, actions, measurable sets, null modifications, and whether finite exceptional orbit hits are allowed, the statement is not a theorem with a definite truth value.

So I separate the task into two parts:

Prove rigorous structural facts about P(A,B).

Test whether a clean rotation/compact-group-type characterization can survive first-prles counterexamples.

Boundary conditions and invariances
Symmetry
P(A,B)⟺P(B,A).
Translation invariance

If A
′
=A+t, B
′
=B+s, then densities are unchanged and

A
′
+B
′
=(A+B)+(s+t),

so

P(A,B)⟺P(A
′
,B
′
).
Dilation

For h≥1, define

hA={ha:a∈A}.

Then

d(hA)=
h
d(A)
	​

,d(hA+hB)=
h
d(A+B)
	​

.

Thus

P(A,B)⟹P(hA,hB).
Finite changes are not harmless

This is crucial. Equality is not stable under finite perturbations.

Take

A=4N,B=4N.

Then

d(A)=d(B)=
4
1
	​

,

but

A+B=4N,

so

d(A+B)=
4
1
	​


=
2
1
	​

.

Now add one point:

A
′
=4N∪{1}.

Then

d(A
′
)=
4
1
	​

,

but

A
′
+B=(4N+4N)∪(1+4N).

This occupies two residue classes modulo 4, so

d(A
′
+B)=
2
1
	​

=d(A
′
)+d(B).

Thus a single exceptional element can change failure into equality. Any complete characterization must account for finite exceptional elements, not only asymptotic density or residue-class densities.

A large rigorous wild family

The following construction shows that equality can hold while almost arbitrary internal structure is present.

Lemma 1: Zero-density exact additive complements exist

Define subsets of N
0
	​

={0,1,2,…}:

P={
j≥0
∑
	​

ε
j
	​

2
2j
:ε
j
	​

∈{0,1}, finitely many 1},
Q={
j≥0
∑
	​

ε
j
	​

2
2j+1
:ε
j
	​

∈{0,1}, finitely many 1}.

So P consists of numbers whose binary expansion uses only even-position bits, and Q uses only odd-position bits.

Every n∈N
0
	​

 has a unique binary expansion. Split its even-position bits into p∈P and its odd-position bits into q∈Q. Then

n=p+q.

Hence

P+Q=N
0
	​

.

Also,

∣P∩[0,N]∣=O(
N
	​

),∣Q∩[0,N]∣=O(
N
	​

),

so

d(P)=d(Q)=0.
Lemma 2: Arbitrary dense sets can be added without changing the sumset conclusion

Let E,F⊆N
0
	​

 have densities

d(E)=p,d(F)=1−p,

where 0<p<1. Define

C=E∪P,D=F∪Q.

Since P,Q have density 0,

d(C)=p,d(D)=1−p.

But because P+Q=N
0
	​

,

C+D⊇P+Q=N
0
	​

.

Therefore

C+D=N
0
	​

.
Theorem: A large family satisfying equality

Fix h≥1, 0<p<1, and arbitrary E,F⊆N
0
	​

 with densities p and 1−p. Let

A={h(c+1):c∈C},
B={h(d+1):d∈D}.

Then

d(A)=
h
p
	​

,d(B)=
h
1−p
	​

.

Also,

A+B={h(c+d+2):c∈C, d∈D}.

Since C+D=N
0
	​

,

A+B={h(n+2):n∈N
0
	​

}.

This is all sufficiently large multiples of h, so

d(A+B)=
h
1
	​

.

Therefore

d(A+B)=
h
1
	​

=
h
p
	​

+
h
1−p
	​

=d(A)+d(B).

So P(A,B) holds.

Consequence

For every h≥1 and every 0<p<1, there are pairs (A,B) satisfying

d(A)=
h
p
	​

,d(B)=
h
1−p
	​

,d(A+B)=
h
1
	​

.

Moreover, E and F were arbitrary apart from their densities. Thus equality can coexist with essentially arbitrary internal behavior inside the active residue class.

For example, take h=2, p=1/2. Then

d(A)=d(B)=
4
1
	​

,

and

d(A+B)=
2
1
	​

=d(A)+d(B).

This gives deterministic versions of the “random subset of the evens” phenomenon.

Why this obstructs a clean characterization

The construction proves that equality is not explained solely by circle rotations, finite periodicity, or residue-class structure. A full characterization would need to include at least the following phenomena:

Periodic containers: A+B may live inside one or more residue classes.

Saturation by zero-density sets: zero-density additive complements can force C+D to be all of N
0
	​

.

Arbitrary dense noise: large parts of A and B may be arbitrary while equality still holds.

Finite exceptional elements: adding one element can change d(A+B) by a positive amount.

That means a classification in terms of only density, residue classes, or “regular” group rotations cannot be complete unless it allows highly irregular null-density and finite-exception behavior.

Explored proof routes
Branch A: residue-class classification

A tempting approach is to decompose A,B modulo h. If

A⊆r+hN,B⊆s+hN,

then

A+B⊆r+s+hN.

This gives upper bound

d(A+B)≤
h
1
	​

.

Equality can happen when the internal sumset saturates the residue class. The construction above forces precisely that.

Obstacle: internal saturation can be caused by arbitrary density sets plus zero-density additive complements. So residue data alone is insufficient.

Branch B: finite-additive-combinatorial lower bounds

For finite X,Y⊆Z,

∣X+Y∣≥∣X∣+∣Y∣−1.

Applying this to A∩[1,N] and B∩[1,N] only gives

∣(A+B)∩[2,2N]∣≳(d(A)+d(B))N,

which yields a weak density lower bound over [1,2N]. It does not characterize equality.

Obstacle: the finite inequality loses too much information because sums spread over an interval twice as long.

Branch C: compact-group model

The proposed circle construction has the form

A={n:{nθ}∈X
A
	​

},B={n:{nθ}∈X
B
	​

},

with

μ(X
A
	​

+X
B
	​

)=μ(X
A
	​

)+μ(X
B
	​

).

But the examples above show that any “group model” would need to allow null modifications and finite orbit exceptions that can still change the density of the integer sumset. Without a precise definition of permitted groups and measurable sets, this branch cannot become a theorem.

Obstacle: “generated in a similar way” is not formal enough to prove or disprove.

Verified result

A complete characterization was not obtained. But the following is proved:

Theorem. For every h≥1, every 0<p<1, and every pair E,F⊆N
0
	​

 with densities p and 1−p, there exist A,B⊆N such that

d(A)=
h
p
	​

,d(B)=
h
1−p
	​

,d(A+B)=d(A)+d(B)=
h
1
	​

,

and the arbitrary internal structure of E,F is retained inside A,B.

This proves that any full characterization must be extremely broad and cannot be merely a clean periodic or rotation-type inverse theorem unless the phrase “using other groups” is made broad enough to encode arbitrary dense subsets plus null-density additive bases.

Dependency graph

Binary expansion uniqueness
⇒P+Q=N
0
	​

.

Counting binary strings on half the bit positions
⇒d(P)=d(Q)=0.

Union with zero-density sets preserves density
⇒d(E∪P)=d(E), d(F∪Q)=d(F).

P+Q=N
0
	​

 and P⊆C, Q⊆D
⇒C+D=N
0
	​

.

Dilation by h
⇒d(A)=p/h, d(B)=(1−p)/h, d(A+B)=1/h.

Therefore

d(A+B)=d(A)+d(B).

No unresolved lemma is used in this construction.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94/100
COMPLETENESS_SCORE: 35/100
ADVERSARIAL_SURVIVAL_SCORE: 88/100

RESOURCE_USAGE: approximately 100% of the intended reasoning budget for this response; 12 strategy classes considered, 3 main branches explored, 5 lemmas/results generated, 3 attempted routes rejected as insufficient for a full characterization.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

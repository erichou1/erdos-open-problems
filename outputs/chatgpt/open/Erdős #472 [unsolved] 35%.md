# Erdős Problem #472 [unsolved] 35%

---

## ChatGPT Response

Formalization

Let P be the set of primes.

A finite initial sequence is a strictly increasing list

q
1
	​

<q
2
	​

<⋯<q
m
	​

,q
i
	​

∈P.

For n≥m, define the candidate set

C
n
	​

={q
n
	​

+q
i
	​

−1:1≤i≤n, q
n
	​

+q
i
	​

−1∈P}.

The recurrence is defined at stage n exactly when C
n
	​


=∅. If defined, then

q
n+1
	​

=minC
n
	​

.

The target statement is

∃m≥1 ∃q
1
	​

<⋯<q
m
	​

∈P ∀n≥m, C
n
	​


=∅.

Equivalently, there exists a finite prime seed whose deterministic extension never gets stuck.

Quantifier structure

The exact quantifier structure is

∃m ∃(q
1
	​

,…,q
m
	​

) ∀n≥m ∃i≤n:q
n
	​

+q
i
	​

−1∈P,

with the extra deterministic condition that q
n+1
	​

 is the smallest such prime.

The negation is

∀m ∀(q
1
	​

,…,q
m
	​

) ∃N≥m:∀i≤N, q
N
	​

+q
i
	​

−1∈
/
P,

where q
1
	​

,…,q
N
	​

 is the sequence generated up to the first failure point.

Shifted formulation

Define

a
n
	​

=q
n
	​

−1.

Then q
n
	​

=a
n
	​

+1, and the recurrence becomes

a
n+1
	​

=a
n
	​

+a
i
	​


where i≤n, a
n
	​

+a
i
	​

+1∈P, and a
i
	​

 is minimal among all earlier offsets producing a prime.

Thus the problem becomes:

Find a finite increasing sequence a
1
	​

<⋯<a
m
	​

, each satisfying a
j
	​

+1∈P, such that the deterministic rule

a
n+1
	​

=a
n
	​

+min{a
i
	​

:i≤n, a
n
	​

+a
i
	​

+1∈P}

is defined forever.

This shifted version is cleaner because the operation is additive.

Basic verified invariants
Lemma 1: Strict growth

If q
n+1
	​

 is defined, then

q
n+1
	​

>q
n
	​

.

Proof: Since q
i
	​

≥2,

q
n
	​

+q
i
	​

−1≥q
n
	​

+1.

Therefore every candidate is larger than q
n
	​

. So the sequence is strictly increasing after every successful step.

Lemma 2: GCD invariant

Let

g=gcd(a
1
	​

,…,a
m
	​

).

Then

g∣a
n
	​


for every generated n.

Proof: Initially true by definition. If g∣a
n
	​

 and g∣a
i
	​

, then

g∣a
n
	​

+a
i
	​

=a
n+1
	​

.

So the invariant propagates by induction.

Consequence:

q
n
	​

≡1(modg)

for every generated n.

Lemma 3: Parity

If the initial sequence contains no 2, then every q
n
	​

 is odd, every a
n
	​

=q
n
	​

−1 is even, and every future increment is even.

If 2 is present, then a=1 is an available offset. But after the current term is an odd prime greater than 2, the candidate

q
n
	​

+2−1=q
n
	​

+1

is even and greater than 2, hence composite. So the offset from 2 becomes inert after the first odd term.

Lemma 4: Fixed finite offsets cannot guarantee primality for all inputs

Let A be any finite set of positive integers. There exist arbitrarily large integers x such that

x+a

is composite for every a∈A.

Proof: For each a∈A, choose a distinct prime r
a
	​

 larger than every ∣a−b∣ with b∈A. Impose the congruence

x≡−a(modr
a
	​

).

The moduli r
a
	​

 are pairwise coprime, so the Chinese remainder construction gives infinitely many integer solutions x. For each such x,

r
a
	​

∣x+a.

Choosing x sufficiently large ensures x+a>r
a
	​

, so x+a is composite.

This proves that no proof can rely on a fixed finite offset set hitting primes for every large input. However, it does not disprove the original statement, because the generated sequence may avoid those trap values and because the available offset set grows over time.

Lemma 5: A single fixed offset cannot drive the sequence forever

Suppose from some point onward the same offset d=q
i
	​

−1 is always used. Then the terms form

q
N+t
	​

=q
N
	​

+td.

Taking t=q
N
	​

, we get

q
N+q
N
	​

	​

=q
N
	​

(1+d),

which is composite and larger than q
N
	​

. Therefore the same fixed offset cannot be used at every later step.

This does not rule out infinitely many uses of one offset at scattered times.

Extremal cases
Seed (2)

The first forced steps are

2→3→5→7→11→13→17→19→23→29.

But the offset from 2 becomes inert after 3, so the behavior is essentially controlled by later offsets.

No proof of infinitude follows from this computation.

Seed (3,5)

The first steps are

3,5,7,11,13,17,19,23,29,31,…

The small offsets are

2,4,6,10,12,16,…

where each offset is one less than an earlier generated prime.

This seed is a natural candidate because it immediately supplies the offsets 2 and 4, then 6, then more offsets. But proving it never gets stuck requires showing that every generated q
n
	​

 has some earlier offset q
i
	​

−1 such that

q
n
	​

+q
i
	​

−1

is prime. I could not derive that from first principles.

Seed (5,7) dies

Compute exactly:

5,7.

Next:

7+5−1=11

is prime, so q
3
	​

=11.

Then

11+5−1=15,11+7−1=17,

so q
4
	​

=17.

Then

17+5−1=21,17+7−1=23,

so q
5
	​

=23.

Then

23+5−1=27,23+7−1=29,

so q
6
	​

=29.

Now all candidates are

29+5−1=33,
29+7−1=35,
29+11−1=39,
29+17−1=45,
29+23−1=51,
29+29−1=57.

All are composite. So this seed stops.

This shows that some starting sequences fail, but it does not settle whether some other seed succeeds.

Equivalent graph formulation

Let a state be a finite valid prefix

(q
1
	​

,…,q
n
	​

).

There is a deterministic transition from a state to a longer state exactly when C
n
	​


=∅. The transition appends minC
n
	​

.

The problem asks whether at least one finite initial state has an infinite forward orbit.

The disproof direction would require showing every finite initial state eventually reaches a dead state.

The proof direction would require constructing one finite initial state whose orbit avoids all dead states forever.

Breadth search over strategies

Direct proof using seed (3,5).
Goal: prove C
n
	​


=∅ for every generated n.
Obstacle: requires prime existence inside a dynamically generated sparse shift set.

Contradiction from assuming an infinite sequence.
Goal: extract modular obstruction.
Obstacle: the offset set grows, so residue obstructions can be escaped.

Explicit constructive seed.
Goal: choose a finite seed with strong offset coverage.
Obstacle: finite coverage cannot guarantee primality for all future inputs by Lemma 4.

Induction using offset density.
Goal: prove the generated offsets become sufficiently dense.
Obstacle: density of offsets does not force shifted primes without a strong prime distribution theorem.

Induction using residue avoidance.
Goal: maintain an invariant that the current term avoids all bad residue classes.
Obstacle: new moduli appear endlessly, and avoiding all simultaneously is not directly enforceable.

Transfinite induction on prefix trees.
Goal: treat finite prefixes as nodes and infer an infinite branch.
Obstacle: arbitrarily long prefixes are trivial because the initial seed length can be chosen arbitrarily long before recurrence starts.

Cardinal arithmetic.
Goal: compare countably many seeds with possible obstruction patterns.
Obstacle: countability gives no existence or nonexistence result.

Diagonalization.
Goal: construct a seed defeating the first obstruction, then the second, and so on.
Obstacle: the seed must be finite, so infinite diagonal requirements cannot be directly encoded.

Compactness.
Goal: prove finite satisfiability implies infinite satisfiability.
Obstacle: the recurrence is deterministic only after the seed, and no uniform finite seed length is obtained.

Density argument.
Goal: show many offsets become available, making a hit likely.
Obstacle: likelihood is not proof, and the needed lower bound is not derivable here.

Reflection argument.
Goal: show a large valid prefix contains a reusable self similar structure.
Obstacle: primality is not invariant under translation or scaling.

Counterexample search.
Goal: prove every seed eventually falls into a CRT trap.
Obstacle: CRT constructs trap integers but does not force the generated sequence to hit one.

Highest expected value branches:

Shifted additive formulation with invariants.

Modular obstruction and CRT trap analysis.

Prefix tree and compactness analysis.

New definitions and structures
Active offset

At stage n, define

d
n
	​

=q
n+1
	​

−q
n
	​

.

Then

d
n
	​

=q
i
	​

−1

for some i≤n. The active offset is the earlier shifted term used to move forward.

Offset set
D
n
	​

={q
i
	​

−1:1≤i≤n}.

Then

C
n
	​

={q
n
	​

+d:d∈D
n
	​

, q
n
	​

+d∈P}.

The recurrence chooses the smallest prime among these shifted candidates, equivalently the smallest d∈D
n
	​

 producing a prime.

Dead point

A generated state is dead if

∀d∈D
n
	​

,q
n
	​

+d∈
/
P.

The problem asks whether some seed avoids dead points forever.

Residue mask

For a modulus r, define

M
r
	​

(D)={−d(modr):d∈D}.

If

q
n
	​

(modr)∈M
r
	​

(D
n
	​

),

then at least one candidate is divisible by r. To make all candidates composite, one needs a collection of moduli assigning a divisor to every offset.

Finite trap certificate

A finite trap certificate for (q
n
	​

,D
n
	​

) is a function assigning to each d∈D
n
	​

 a prime r
d
	​

 such that

q
n
	​

+d≡0(modr
d
	​

)

and

q
n
	​

+d>r
d
	​

.

If such a certificate exists, the state is dead.

CRT proves trap certificates exist for many abstract integers x, but not necessarily for integers x that arise as generated terms.

Branch A: Attempted proof for seed (3,5)

Target theorem:

∀n≥2, C
n
	​


=∅

for the seed (3,5).

The recurrence begins with

3,5,7,11,13,17,19,23,29.

Offsets available early are

2,4,6,10,12,16,18,22,28.

A tempting invariant is:

For every generated q
n
	​

, at least one small available offset d makes q
n
	​

+d prime.

But this is not justified. Lemma 4 blocks any argument that a fixed finite group of offsets works for all large values. The proof would need to use the fact that q
n
	​

 is not arbitrary but generated by the same process.

New target:

S
A
	​

:The generated values avoid all CRT trap classes for their current offset sets.

Attack on S
A
	​

: CRT gives trap classes modulo products of auxiliary primes. Nothing in the recurrence visibly prevents landing in those classes. No contradiction is obtained, but no proof is obtained either.

Branch A fails at S
A
	​

.

Branch B: Attempted disproof by modular traps

Target theorem:

Every finite seed eventually reaches a dead point.

A possible route:

For a current finite offset set D
n
	​

, construct a trap residue class xmodM such that

x+d

is composite for every d∈D
n
	​

.

This is possible by Lemma 4. The unresolved part is forcing the actual generated value q
n
	​

 to enter such a trap class.

The generated sequence is adaptive. Once a new term appears, it also becomes a new offset, changing the future trap structure. Therefore a trap for D
n
	​

 does not automatically remain decisive for D
n+1
	​

.

New target:

S
B
	​

:Every deterministic orbit intersects one of its own dynamically updated trap classes.

I found no derivation of S
B
	​

. A purely finite CRT argument is insufficient because it constructs possible dead values, not unavoidable dead values.

Branch B fails at S
B
	​

.

Branch C: Attempted compactness argument

A common structural route would be:

If arbitrarily long valid finite behaviors exist, then an infinite behavior exists.

But here that reasoning fails because the seed length is arbitrary. For any L, one can choose a seed of length L, and the sequence has length at least L before the recurrence is even tested. Thus arbitrarily long finite prefixes do not imply anything.

A corrected compactness target would require a uniform bound m on seed length and arbitrarily long valid continuations from some seed length m. That has not been established.

Branch C fails because finite satisfiability is trivialized by arbitrary seed length.

Central gap node

The core unresolved statement is:

G:∃ finite seed (q
1
	​

,…,q
m
	​

) such that its orbit never reaches a dead point.

Ten attacks on G:

Prove directly for (3,5).
Blocked by lack of a guaranteed shifted prime.

Prove directly for (2).
Equivalent difficulty after the offset 1 becomes inert.

Build a seed with many small offsets.
Blocked because every finite offset set has CRT traps.

Use the growing offset set.
Requires proving growth avoids all traps, unresolved.

Prove every seed dies.
Requires forcing orbit into a trap, unresolved.

Strengthen to “every generated term has a small active offset.”
False as a general theorem without proof, and no bound is available.

Weaken to “infinitely many steps are possible.”
Still requires all finite stages to be nondead.

Reformulate as additive semigroup dynamics.
Gives gcd invariants but no prime existence result.

Use residue masks.
Gives obstruction language but no inevitability.

Search for monotone rank preventing death.
No rank function found that increases while guaranteeing future prime hits.

The gap remains unresolved.

Dependency graph of verified results

Definitions:

Prime sequence recurrence.

Candidate set C
n
	​

.

Shifted variables a
n
	​

=q
n
	​

−1.

Offset set D
n
	​

.

Dead point.

Residue mask.

Trap certificate.

Verified lemmas:

Strict growth depends only on q
i
	​

≥2.

GCD invariant depends only on a
n+1
	​

=a
n
	​

+a
i
	​

.

Parity behavior depends only on prime parity.

Fixed finite offset trap depends on CRT.

Single fixed offset cannot drive forever depends on divisibility of arithmetic progressions.

Seed (5,7) dies by explicit calculation.

Unresolved statements:

Existence of one infinite seed.

Death of every seed.

Infinitude of seed (3,5).

Inevitability of dynamically updated CRT traps.

Avoidance of traps by a generated orbit.

No unresolved statement is used as a proved lemma.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97

COMPLETENESS_SCORE: 35

ADVERSARIAL_SURVIVAL_SCORE: 88

RESOURCE_USAGE: approximately 100 percent of the available response budget used, 3 main branches explored, 6 verified lemmas generated, 3 failed proof attempts recorded.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

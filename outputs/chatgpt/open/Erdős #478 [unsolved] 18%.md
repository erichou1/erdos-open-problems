# Erdős Problem #478 [unsolved] 18%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

0. Complete formalization
Objects

Let p be a prime. Work in the finite field F
p
	​

. Since 1≤k<p, every factorial k! is nonzero modulo p, so

A
p
	​

⊆F
p
×
	​

.

Define the factorial orbit

x
k
	​

=k!(modp),1≤k≤p−1.

Then

A
p
	​

={x
k
	​

:1≤k≤p−1}.

The recurrence is

x
k+1
	​

=(k+1)x
k
	​

,1≤k≤p−2.

Thus A
p
	​

 is the set of vertices visited by the deterministic walk in F
p
×
	​

 whose successive multipliers are 2,3,…,p−1.

Formal statement

The target statement is

∣A
p
	​

∣∼(1−
e
1
	​

)p

as p→∞ through primes.

Equivalently,

p→∞, p prime
lim
	​

p
∣A
p
	​

∣
	​

=1−
e
1
	​

.

Since ∣F
p
×
	​

∣=p−1, another equivalent form is

p→∞, p prime
lim
	​

p−1
∣A
p
	​

∣
	​

=1−
e
1
	​

.

The two formulations are equivalent because

p
p−1
	​

→1.
Quantifier structure

The statement means

∀ε>0, ∃P, ∀p≥P, p prime⟹
	​

p
∣A
p
	​

∣
	​

−(1−
e
1
	​

)
	​

<ε.

The quantified variable is p, restricted to primes. The constant P may depend on ε, not on p.

Negation

The negation is

∃ε
0
	​

>0, ∀P, ∃p≥P, p prime

such that

	​

p
∣A
p
	​

∣
	​

−(1−
e
1
	​

)
	​

≥ε
0
	​

.

Equivalently, there exists an infinite sequence of primes p
j
	​

→∞ such that

	​

p
j
	​

∣A
p
j
	​

	​

∣
	​

−(1−
e
1
	​

)
	​

≥ε
0
	​

.
Collision formulation

For 1≤a<b≤p−1,

a!≡b!(modp)

if and only if

(a+1)(a+2)⋯b≡1(modp).

Proof:

b!=a!⋅(a+1)(a+2)⋯b.

Since a!

=0(modp), multiplication by (a!)
−1
 is valid in F
p
×
	​

. Therefore

a!≡b!⟺(a+1)⋯b≡1.

Thus ∣A
p
	​

∣ is the number of equivalence classes of indices 1,…,p−1 under the relation

a∼b⟺a!≡b!(modp).
Fiber formulation

For each r∈F
p
×
	​

, define

m
p
	​

(r)=∣{1≤k≤p−1:k!≡r(modp)}∣.

Then

∣A
p
	​

∣=∣{r∈F
p
×
	​

:m
p
	​

(r)>0}∣.

Also

r∈F
p
×
	​

∑
	​

m
p
	​

(r)=p−1.

The target statement becomes

∣{r:m
p
	​

(r)>0}∣∼(1−
e
1
	​

)p.
Missing residue formulation

Let

M
p
	​

=F
p
×
	​

∖A
p
	​

.

Then

∣A
p
	​

∣=(p−1)−∣M
p
	​

∣.

The target statement is equivalent to

∣M
p
	​

∣∼
e
p
	​

.

Since p−1∼p, this is also equivalent to

∣M
p
	​

∣∼
e
p−1
	​

.
Occupancy formulation

If p−1 independent uniformly random samples were drawn from a set of size p−1, then the expected number of occupied values would be

(p−1)(1−(1−
p−1
1
	​

)
p−1
)∼(1−
e
1
	​

)(p−1).

The problem asks whether the deterministic sequence

1!,2!,…,(p−1)!

has the same first-order number of occupied residue classes as this random occupancy model.

This is only a reformulation by analogy, not a proof.

Boundary conditions

For p=2,

A
2
	​

={1!mod2}={1},

so ∣A
2
	​

∣=1.

For p=3,

1!≡1,2!≡2(mod3),

so ∣A
3
	​

∣=2.

For p>2, Wilson’s theorem gives

(p−1)!≡−1(modp).

Also

(p−1)!=(p−1)(p−2)!≡−(p−2)!(modp).

Thus

−(p−2)!≡−1(modp),

so

(p−2)!≡1(modp).

Since

1!≡1(modp),

there is always a collision

1!≡(p−2)!(modp)

for p>3. Therefore

∣A
p
	​

∣≤p−2.

This upper bound is much larger than (1−
e
1
	​

)p, so it does not decide the target statement.

Symmetries

The factorial sequence is not invariant under arbitrary multiplication by F
p
×
	​

. However, it has a reversal relation.

For 1≤k≤p−1,

k!(p−1−k)!≡(−1)
k+1
(modp).

Verification:

(p−1)!=1⋅2⋯k⋅(k+1)⋯(p−1).

Modulo p,

(k+1)(k+2)⋯(p−1)≡(−1)(−2)⋯(−(p−1−k)).

Thus

(k+1)⋯(p−1)≡(−1)
p−1−k
(p−1−k)!.

Since p is odd for p>2, p−1 is even, so

(−1)
p−1−k
=(−1)
k
.

Wilson gives

(p−1)!≡−1.

Therefore

k!(−1)
k
(p−1−k)!≡−1,

so

k!(p−1−k)!≡(−1)
k+1
.

Consequences:

(p−1−k)!≡(−1)
k+1
(k!)
−1
.

Therefore

A
p
	​


is not necessarily closed under inversion, but the reverse-indexed factorial values are signed inverses of the forward-indexed values.

Cardinality estimates known from first principles

Since

A
p
	​

/A
p
	​

={ab
−1
:a,b∈A
p
	​

},

and each quotient is in F
p
×
	​

, we have

∣A
p
	​

/A
p
	​

∣≤∣A
p
	​

∣
2
.

Now every t∈F
p
×
	​

 occurs as a quotient of factorials:

For 1≤t≤p−1,

t=
(t−1)!
t!
	​

(modp)

provided t≥2. Also 1=1!/1!. Since both t! and (t−1)! are in A
p
	​

, every nonzero residue lies in A
p
	​

/A
p
	​

. Hence

A
p
	​

/A
p
	​

=F
p
×
	​

.

Therefore

p−1≤∣A
p
	​

∣
2
,

so

∣A
p
	​

∣≥
p−1
	​

.

This lower bound is far below the target order p.

1. Equivalent formulations
Formulation 1: distinct vertices of a deterministic walk

Let

x
1
	​

=1,x
k+1
	​

=(k+1)x
k
	​

.

Then

∣A
p
	​

∣=∣{x
1
	​

,…,x
p−1
	​

}∣.

The target is that this deterministic walk visits asymptotically (1−
e
1
	​

)p distinct nonzero residues.

Formulation 2: number of occupied fibers

Let

m
p
	​

(r)=∣{k:k!≡r(modp)}∣.

Then the target is

∣{r:m
p
	​

(r)>0}∣=(1−
e
1
	​

+o(1))p.
Formulation 3: collision graph

Define a graph G
p
	​

 on vertices {1,…,p−1}, where a and b are adjacent if

a!≡b!(modp).

Then connected components are exactly equality classes because equality is transitive. The number of connected components is ∣A
p
	​

∣. The target is

#components(G
p
	​

)∼(1−
e
1
	​

)p.

Equivalently, collisions must merge roughly

(p−1)−(1−
e
1
	​

)p∼
e
p
	​


indices into already visited residue classes.

Formulation 4: interval products equal to 1

For 1≤a<b≤p−1, define

P(a,b)=
j=a+1
∏
b
	​

j(modp).

Then

a!≡b!⟺P(a,b)=1.

Therefore all collisions are controlled by intervals of consecutive residues whose product is 1.

Formulation 5: recurrence inverse problem

Given r∈F
p
×
	​

, the question whether r∈A
p
	​

 is whether the recurrence

x
k+1
	​

=(k+1)x
k
	​

,x
1
	​

=1

hits r before k=p.

The target is that the number of hit states is asymptotic to (1−
e
1
	​

)p.

2. Extremal cases and constraints
Minimum possible size from quotient coverage

Since A
p
	​

/A
p
	​

=F
p
×
	​

,

∣A
p
	​

∣≥
p−1
	​

.

So any counterexample with ∣A
p
	​

∣=o(p) must still have ∣A
p
	​

∣≥p
1/2+o(1)
.

Maximum possible size

Since 1!=(p−2)!(modp) for p>3,

∣A
p
	​

∣≤p−2.

Thus the density ∣A
p
	​

∣/p lies between approximately 0 and 1, with only the weak first-principles lower bound p
−1/2
.

Collision count versus distinct count

Let

n=p−1.

Let D=∣A
p
	​

∣. The number of repeated appearances beyond the first is

R=n−D.

The target statement is

R∼
e
p
	​

.

The pairwise collision count

C=#{(a,b):1≤a<b≤p−1, a!≡b!}

is not equal to R, because one residue may occur more than twice. But

C=
r∈F
p
×
	​

∑
	​

(
2
m
p
	​

(r)
	​

).

Also

R=
r:m
p
	​

(r)>0
∑
	​

(m
p
	​

(r)−1).

For every m≥1,

m−1≤(
2
m
	​

)

when m≥2, with equality only at m=2. Hence

R≤C.

No useful reverse bound exists without controlling large fibers.

3. Breadth-first strategy search
Strategy 1: Direct equidistribution of factorial values

Goal: prove that k! behaves like random sampling in F
p
×
	​

.

Hidden assumption: local recurrence multipliers do not create long-range structure.

Obstacle: deterministic recurrence has strong algebraic dependencies.

Confidence: low.

Expected value: high if achievable, but no verified path found.

Strategy 2: Count missing residues by additive characters

Use

1
r∈
/
A
p
	​

	​

=
k=1
∏
p−1
	​

(1−1
k!=r
	​

).

Obstacle: product expansion requires high-order correlation control for factorial residues.

Confidence: low.

Expected value: high but blocked by uncontrolled correlations.

Strategy 3: Count collisions by interval products

Analyze

j=a+1
∏
b
	​

j≡1.

Obstacle: requires counting consecutive interval products equal to 1 across all lengths.

Confidence: medium for partial bounds, low for asymptotic.

Expected value: medium.

Strategy 4: Moment method for fibers

Compute or bound

r
∑
	​

m
p
	​

(r)
q

for q=1,2,3,….

Obstacle: the first moment is trivial; the second moment counts interval products equal to 1, already hard. Higher moments are harder.

Confidence: low.

Expected value: high if enough moments match Poisson.

Strategy 5: Induction on p

Try to relate A
p
	​

 and A
q
	​

 for smaller primes.

Obstacle: factorial residues modulo different primes do not embed naturally.

Confidence: very low.

Expected value: low.

Strategy 6: Induction on k

Track the growth of

S
k
	​

={1!,2!,…,k!}.

Obstacle: whether x
k+1
	​

∈S
k
	​

 depends on global modular recurrence.

Confidence: low.

Expected value: medium for martingale-like heuristic, not proof.

Strategy 7: Multiplicative subgroup obstruction

If A
p
	​

 were trapped in a subgroup or coset, then quotient coverage would fail.

Since

A
p
	​

/A
p
	​

=F
p
×
	​

,

no proper subgroup containment is possible.

Obstacle: this only proves spreading in quotient sense, not large cardinality.

Confidence: verified but weak.

Expected value: low.

Strategy 8: Diagonalization counterexample search

Try to construct infinitely many primes where many collisions occur or few collisions occur.

Obstacle: prime modulus is not freely constructible from desired factorial congruences.

Confidence: low.

Expected value: medium for disproof, no construction found.

Strategy 9: Polynomial encoding

Represent k!≡r through polynomial congruences.

Obstacle: factorial is not a low-degree polynomial in k over F
p
	​

 on the interval 1,…,p−1, except through interpolation of degree at most p−2, which loses structure.

Confidence: low.

Expected value: low.

Strategy 10: Reflection using reversal identity

Use

(p−1−k)!≡(−1)
k+1
(k!)
−1
.

Obstacle: gives symmetry between visited values and signed inverses, but does not count distinct values.

Confidence: verified identity, low counting power.

Expected value: medium for structural constraints.

Strategy 11: Auxiliary graph expansion

Build a graph on F
p
×
	​

 with edges

x
k
	​

→x
k+1
	​

.

Obstacle: the graph is only a path with predetermined edge labels, not an expander generated by a fixed set.

Confidence: low.

Expected value: medium.

Strategy 12: Random injection comparison

Compare the deterministic walk to random sampling without replacement in multipliers.

Obstacle: the multipliers 2,…,p−1 are exactly all nonzero residues except 1, so there is complete dependence.

Confidence: low.

Expected value: high heuristic value, no proof.

Strategy 13: Transfinite induction

Not naturally applicable because all objects are finite for each prime p, and the asymptotic limit is over a countable sequence of finite problems.

Obstacle: no well-founded transfinite structure improves the finite counting problem.

Confidence: very low.

Expected value: low.

Strategy 14: Compactness or ultraproduct limit

Take a nonprincipal limiting object of finite fields and factorial orbits.

Obstacle: the target numerical constant requires quantitative asymptotics, not just first-order transfer.

Confidence: low.

Expected value: medium for contradiction framework, not enough for asymptotic.

Strategy ranking

Top three selected branches:

Collision interval analysis.

Fiber moment method.

Reversal identity and structural constraints.

4. Theorem discovery layer
Definition: interval product spectrum

For 1≤ℓ≤p−2, define

N
p
	​

(ℓ)=∣{a:1≤a≤p−1−ℓ, 
j=a+1
∏
a+ℓ
	​

j≡1(modp)}∣.

Then pairwise collisions satisfy

C
p
	​

=
ℓ=1
∑
p−2
	​

N
p
	​

(ℓ).

Motivation: collisions are indexed by interval length ℓ=b−a.

Consequence: controlling all N
p
	​

(ℓ) controls pairwise collisions.

Possible application: if C
p
	​

 had asymptotic 
2
1
	​

(p−1), this would match the second moment of independent occupancy. But the target ∣A
p
	​

∣ needs more than pairwise collisions.

Definition: factorial fiber profile

Define

m
p
	​

=(m
p
	​

(r))
r∈F
p
×
	​

	​

.

Motivation: ∣A
p
	​

∣ is the support size of m
p
	​

.

Consequence:

r
∑
	​

m
p
	​

(r)=p−1.

Possible application: support size follows if the empirical distribution of m
p
	​

(r) approaches Poisson with mean 1 conditioned on finite total mass. This remains unproved.

Definition: collision energy

Define

E
p
	​

=
r
∑
	​

m
p
	​

(r)
2
.

Then

E
p
	​

=(p−1)+2C
p
	​

.

Motivation: the second moment detects clustering.

Consequence: by Cauchy-Schwarz,

(p−1)
2
=
	​

r∈A
p
	​

∑
	​

m
p
	​

(r)
	​

2
≤∣A
p
	​

∣E
p
	​

.

Thus

∣A
p
	​

∣≥
E
p
	​

(p−1)
2
	​

.

Possible application: if E
p
	​

=O(p), then ∣A
p
	​

∣≫p. But the target needs the exact constant 1−
e
1
	​

, far beyond this.

Definition: reverse-paired orbit

Define the involution on indices

ρ(k)=p−1−k.

Then

x
ρ(k)
	​

=(−1)
k+1
x
k
−1
	​

.

Motivation: pairs opposite indices.

Consequence: if x
k
	​

=x
j
	​

, then

x
ρ(k)
	​

=(−1)
k+1
x
k
−1
	​

,x
ρ(j)
	​

=(−1)
j+1
x
j
−1
	​

.

If k≡j(mod2), then

x
ρ(k)
	​

=x
ρ(j)
	​

.

If k

≡j(mod2), then

x
ρ(k)
	​

=−x
ρ(j)
	​

.

Possible application: collisions induce reverse collisions or signed reverse relations. This gives structure but not an asymptotic count.

5. Verified lemmas
Lemma 1: quotient coverage

For every prime p,

A
p
	​

/A
p
	​

=F
p
×
	​

.

Proof:

Let t∈F
p
×
	​

.

If t=1, then

1=
1!
1!
	​

.

If 2≤t≤p−1, then

(t−1)!
t!
	​

=t.

Both t! and (t−1)! belong to A
p
	​

. Therefore t∈A
p
	​

/A
p
	​

. Since t was arbitrary,

F
p
×
	​

⊆A
p
	​

/A
p
	​

.

The reverse containment is automatic because A
p
	​

⊆F
p
×
	​

. Hence

A
p
	​

/A
p
	​

=F
p
×
	​

.

Therefore

p−1≤∣A
p
	​

∣
2
,

so

∣A
p
	​

∣≥
p−1
	​

.

This lemma is verified.

Lemma 2: collision equivalence

For 1≤a<b≤p−1,

a!≡b!(modp)

if and only if

j=a+1
∏
b
	​

j≡1(modp).

Proof already given above. This lemma is verified.

Lemma 3: reversal identity

For odd prime p and 1≤k≤p−2,

(p−1−k)!≡(−1)
k+1
(k!)
−1
(modp).

Proof already given above. This lemma is verified.

Lemma 4: unavoidable collision

For every prime p>3,

1!≡(p−2)!(modp).

Proof:

Wilson’s theorem gives

(p−1)!≡−1(modp).

Also

(p−1)!=(p−1)(p−2)!≡−(p−2)!(modp).

Therefore

−(p−2)!≡−1(modp),

so

(p−2)!≡1(modp).

Since 1!≡1, the collision follows.

This lemma is verified assuming Wilson’s theorem. Wilson’s theorem can be proved from first principles by pairing each nonzero residue with its inverse in F
p
×
	​

, leaving only 1 and −1 self-inverse, so the product of all nonzero residues is −1.

6. Branch A: interval collision analysis
Target

Prove or disprove

∣A
p
	​

∣∼(1−
e
1
	​

)p.

Since ∣A
p
	​

∣ is the support size of factorial fibers, a natural intermediate target is to understand collisions

a!≡b!(modp).

By Lemma 2, this is equivalent to

j=a+1
∏
b
	​

j≡1.
Branch A.1: fixed interval length

For fixed ℓ=b−a,

j=a+1
∏
a+ℓ
	​

j

is a polynomial in a of degree ℓ:

Q
ℓ
	​

(a)=
i=1
∏
ℓ
	​

(a+i).

The collision condition is

Q
ℓ
	​

(a)≡1(modp).

Thus

Q
ℓ
	​

(a)−1≡0(modp).

If Q
ℓ
	​

(a)−1 is not the zero polynomial over F
p
	​

, then it has at most ℓ roots.

For fixed ℓ<p, its degree is ℓ, and its leading coefficient is 1, so it is not zero. Therefore

N
p
	​

(ℓ)≤ℓ.

This is verified.

However,

ℓ=1
∑
p−2
	​

ℓ≍p
2
,

which is too weak. It does not even give C
p
	​

=O(p).

Branch A.2: complementary interval length

Using Wilson,

j=a+1
∏
b
	​

j⋅
j=b+1
∏
p−1
	​

j⋅
j=1
∏
a
	​

j≡−1.

If

j=a+1
∏
b
	​

j≡1,

then

a!⋅
j=b+1
∏
p−1
	​

j≡−1.

Now

j=b+1
∏
p−1
	​

j≡(−1)
p−1−b
(p−1−b)!.

For odd p,

(−1)
p−1−b
=(−1)
b
.

Hence collision implies

a!(−1)
b
(p−1−b)!≡−1.

Equivalently,

a!(p−1−b)!≡(−1)
b+1
.

This gives a complementary relation, but it does not reduce the count of collisions enough.

Branch A.3: attempt to estimate total collision count

If interval products behaved uniformly, then for each of approximately 
2
1
	​

p
2
 pairs (a,b), the probability that the interval product equals 1 would be about 1/(p−1), giving

C
p
	​

≈
2
p
	​

.

But this is only a heuristic. A proof would require showing that the products

j=a+1
∏
b
	​

j

are sufficiently equidistributed over F
p
×
	​

 as (a,b) ranges over intervals.

GAP_NODE A

Prove

C
p
	​

=
r
∑
	​

(
2
m
p
	​

(r)
	​

)∼
2
p
	​

.

Attack strategies:

Direct polynomial root counting over all lengths.

Separate short and long intervals.

Use complementary intervals to reduce long intervals to short intervals.

Estimate exponential sums over interval products.

Reparameterize by endpoints using factorial quotients.

Count solutions to b!≡a!.

Use multiplicative characters.

Bound high-multiplicity residues.

Search for forced structured collision families.

Compare with random occupancy moments.

Result: no proof obtained. Even if proved, this would not imply the target support size without controlling higher moments.

Branch A fails to prove or disprove the target.

7. Branch B: fiber moment method
Target

Let

m
p
	​

(r)=∣{k:k!≡r}∣.

The desired support size is

∣{r:m
p
	​

(r)>0}∣.

If the distribution of m
p
	​

(r) matched a Poisson distribution of mean 1, then

Pr(m
p
	​

(r)>0)≈1−e
−1
,

giving

∣A
p
	​

∣≈(1−e
−1
)(p−1).
Verified identities

First moment:

r
∑
	​

m
p
	​

(r)=p−1.

Second moment:

r
∑
	​

m
p
	​

(r)
2
=
r
∑
	​

m
p
	​

(r)+2
r
∑
	​

(
2
m
p
	​

(r)
	​

)=(p−1)+2C
p
	​

.

Higher moments:

r
∑
	​

m
p
	​

(r)
q

counts ordered q-tuples

(k
1
	​

,…,k
q
	​

)

such that

k
1
	​

!≡k
2
	​

!≡⋯≡k
q
	​

!(modp).

Equivalently, for each pair i,j,

t=min(k
i
	​

,k
j
	​

)+1
∏
max(k
i
	​

,k
j
	​

)
	​

t≡1

after orienting the quotient correctly.

Branch B.1: Cauchy lower bound

By Cauchy-Schwarz,

	​

r∈A
p
	​

∑
	​

m
p
	​

(r)
	​

2
≤∣A
p
	​

∣
r∈A
p
	​

∑
	​

m
p
	​

(r)
2
.

Thus

(p−1)
2
≤∣A
p
	​

∣E
p
	​

,

where

E
p
	​

=
r
∑
	​

m
p
	​

(r)
2
.

Therefore

∣A
p
	​

∣≥
E
p
	​

(p−1)
2
	​

.

If E
p
	​

∼2p, then this gives

∣A
p
	​

∣≳
2
p
	​

.

But the desired constant is about 0.632p, and this method cannot produce it from the second moment alone.

Branch B.2: factorial fibers as occupancy profile

The exact identity

∣A
p
	​

∣=
r
∑
	​

1
m
p
	​

(r)>0
	​


can be written using falling factorial moments:

1
m>0
	​

=1−1
m=0
	​

.

To estimate 1
m=0
	​

, one would need all moments or a strong distributional approximation.

For random occupancy with n=N=p−1,

Pr(m=0)=(1−
N
1
	​

)
N
→e
−1
.

For factorial residues, no verified independence or moment convergence has been established.

GAP_NODE B

Prove that the empirical fiber distribution satisfies

p−1
1
	​

∣{r:m
p
	​

(r)=j}∣→
j!
e
−1
	​


for each fixed j≥0.

This would imply

p−1
∣A
p
	​

∣
	​

=1−
p−1
1
	​

∣{r:m
p
	​

(r)=0}∣→1−e
−1
.

Attack strategies:

Prove convergence of all factorial moments.

Prove convergence of finitely many moments plus tightness.

Directly estimate empty fibers.

Model the recurrence as pseudorandom.

Use character sums for m
p
	​

(r).

Count ordered collision tuples.

Bound high multiplicity fibers.

Establish approximate independence of events k!≡r.

Use entropy inequalities.

Search for algebraic obstruction to Poisson behavior.

Result: no proof obtained. Branch B gives the cleanest sufficient condition, but it remains unverified.

8. Branch C: reversal identity and structural constraints
Target

Use

(p−1−k)!≡(−1)
k+1
(k!)
−1

to force or exclude certain support sizes.

Branch C.1: induced transformation on A
p
	​


For every k, if

x
k
	​

=k!,

then

x
p−1−k
	​

=(−1)
k+1
x
k
−1
	​

.

Thus reverse values lie in

A
p
	​

∩A
p
−1
	​


up to signs depending on parity.

Define

A
p
+
	​

={k!:k odd},A
p
−
	​

={k!:k even}.

Then reversal implies

{(p−1−k)!:k odd}⊆(A
p
+
	​

)
−1
,

and

{(p−1−k)!:k even}⊆−(A
p
−
	​

)
−1
.

This gives relations among parity-restricted factorial sets.

Branch C.2: parity split

Let

E
p
	​

={k!:1≤k≤p−1, k even},
O
p
	​

={k!:1≤k≤p−1, k odd}.

Then

A
p
	​

=E
p
	​

∪O
p
	​

.

The recurrence alternates parity:

x
k+1
	​

=(k+1)x
k
	​

.

No direct independence or disjointness follows.

Branch C.3: collision propagation

Suppose

x
a
	​

=x
b
	​

.

Then

x
p−1−a
	​

=(−1)
a+1
x
a
−1
	​

,
x
p−1−b
	​

=(−1)
b+1
x
b
−1
	​

.

If a≡b(mod2), then

x
p−1−a
	​

=x
p−1−b
	​

.

Thus every same-parity collision induces another collision under reversal.

If a

≡b(mod2), then

x
p−1−a
	​

=−x
p−1−b
	​

.

This gives a signed relation, not necessarily a collision.

Consequence

Same-parity collisions come in reflected pairs unless the pair is fixed by reversal. Fixed behavior would require

{a,b}={p−1−a,p−1−b}.

That implies

a+b=p−1.

This is a special symmetric collision condition.

However, this structural pairing does not determine the total support size.

GAP_NODE C

Convert reversal symmetry into a support-size asymptotic.

Attack strategies:

Analyze parity-restricted supports E
p
	​

,O
p
	​

.

Count same-parity collisions.

Count opposite-parity signed collisions.

Study fixed collision pairs with a+b=p−1.

Use inversion symmetry to constrain missing residues.

Compare A
p
	​

, A
p
−1
	​

, and −A
p
−1
	​

.

Derive inequalities involving ∣A
p
	​

∩A
p
−1
	​

∣.

Search for forced missing residues.

Search for forced present residues.

Combine with quotient coverage.

Result: no route to the constant 1−
e
1
	​

 obtained.

9. Counterexample search from first principles

To disprove the target, it would suffice to prove either:

p→∞
limsup
	​

p
∣A
p
	​

∣
	​

>1−
e
1
	​

+ε

or

p→∞
liminf
	​

p
∣A
p
	​

∣
	​

<1−
e
1
	​

−ε

for some ε>0.

Possible high-support obstruction

If factorials are mostly distinct, then

∣A
p
	​

∣=p−O(1),

contradicting the target. But the only verified universal collision is

1!=(p−2)!.

No mechanism was derived forcing near-injectivity for infinitely many primes.

Possible low-support obstruction

If factorial values repeatedly fall into a smaller set B
p
	​

⊂F
p
×
	​

 with

∣B
p
	​

∣≤cp

for some

c<1−
e
1
	​

,

then the target fails. But quotient coverage gives

B
p
	​

/B
p
	​

=F
p
×
	​


if B
p
	​

=A
p
	​

, which prevents subgroup-type concentration. It does not prevent arbitrary sets of size cp, so this does not disprove low support.

Computational examples avoided

No computation or external data was used. Small cases can test consistency but cannot prove or disprove the asymptotic statement.

No counterexample construction was found.

10. Dependency graph of verified results
Definition D1
A
p
	​

={k!(modp):1≤k<p}.

Dependencies: none.

Conclusion: factorial residue support.

Lemma L1: collision equivalence

Dependencies: field cancellation in F
p
×
	​

.

Conclusion:

a!≡b!⟺
j=a+1
∏
b
	​

j≡1.
Lemma L2: quotient coverage

Dependencies: definition of factorial and division in F
p
×
	​

.

Conclusion:

A
p
	​

/A
p
	​

=F
p
×
	​

.
Corollary C1: square-root lower bound

Dependencies: L2 and ∣A/A∣≤∣A∣
2
.

Conclusion:

∣A
p
	​

∣≥
p−1
	​

.
Lemma L3: Wilson theorem

Dependencies: inverse pairing in F
p
×
	​

.

Conclusion:

(p−1)!≡−1.
Corollary C2: unavoidable collision

Dependencies: L3.

Conclusion:

1!≡(p−2)!.
Corollary C3: upper bound

Dependencies: C2.

Conclusion:

∣A
p
	​

∣≤p−2

for p>3.

Lemma L4: reversal identity

Dependencies: Wilson theorem and modular sign conversion.

Conclusion:

(p−1−k)!≡(−1)
k+1
(k!)
−1
.

No verified lemma in the dependency graph implies

∣A
p
	​

∣∼(1−
e
1
	​

)p.

No verified lemma disproves it either.

11. Final adversarial check
Possible circularity

The proof search did not assume the target asymptotic. Random occupancy was used only as a heuristic formulation, not as a theorem.

Quantifier check

The target requires uniform convergence over all sufficiently large primes. No branch established such convergence. No branch established an infinite exceptional prime sequence either.

Hidden theorem check

Wilson’s theorem was used only after giving a first-principles proof by inverse pairing.

Polynomial root bounds were used with verified hypotheses: a nonzero polynomial of degree ℓ over a field has at most ℓ roots.

Cardinal arithmetic check

The lower bound

p−1≤∣A
p
	​

∣
2

is justified by quotient coverage and the trivial inequality ∣A/A∣≤∣A∣
2
.

No asymptotic cardinal estimate strong enough to prove the target was established.

Main unresolved gaps

The following remain unresolved:

Whether the fiber profile m
p
	​

(r) approaches Poisson mean 1.

Whether the collision count satisfies C
p
	​

∼p/2.

Whether higher collision moments match random occupancy.

Whether reversal symmetry creates systematic deviations from random occupancy.

Whether there exist infinite prime subsequences with support density separated from 1−
e
1
	​

.

Because at least one unresolved gap is essential to every route attempted, no proof or disproof was completed.

Final state

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 92

COMPLETENESS_SCORE: 18

ADVERSARIAL_SURVIVAL_SCORE: 86

RESOURCE_USAGE:

Reasoning budget used: 100 percent of this response.

Branches explored: 3 primary branches, with 14 initial strategies.

Lemmas generated: 4 verified main lemmas, plus several reformulations.

Failed proof attempts: 6 major attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

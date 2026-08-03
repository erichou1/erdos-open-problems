# Erdős Problem #291 [unsolved] 55%

---

## ChatGPT Response

Formalization

Let

H
n
	​

=
k=1
∑
n
	​

k
1
	​

,L
n
	​

=lcm(1,…,n),a
n
	​

=L
n
	​

H
n
	​

.

Then a
n
	​

∈Z. Define

G
n
	​

=(a
n
	​

,L
n
	​

).

The problem asks whether both sets are infinite:

{n≥1:G
n
	​

=1},{n≥1:G
n
	​

>1}.

Equivalently:

∀N ∃n≥N with G
n
	​

=1,

and

∀N ∃n≥N with G
n
	​

>1.

The negation is:

∃N ∀n≥N, G
n
	​

>1

or

∃N ∀n≥N, G
n
	​

=1.
Basic reduction to reduced denominators

Write

H
n
	​

=
B
n
	​

A
n
	​

	​

,(A
n
	​

,B
n
	​

)=1.

Since L
n
	​

 is divisible by every 1,…,n, it is divisible by B
n
	​

. Thus

a
n
	​

=L
n
	​

H
n
	​

=A
n
	​

B
n
	​

L
n
	​

	​

.

Therefore

(a
n
	​

,L
n
	​

)=(A
n
	​

B
n
	​

L
n
	​

	​

, B
n
	​

B
n
	​

L
n
	​

	​

)=
B
n
	​

L
n
	​

	​

.

So

G
n
	​

=1⟺B
n
	​

=L
n
	​

.

Thus the coprime case means: no cancellation occurs when H
n
	​

 is written over the full denominator L
n
	​

.

Prime-level criterion

Fix a prime p≤n. Let

e=e
p
	​

(n)=max{r:p
r
≤n},

so

v
p
	​

(L
n
	​

)=e.

Let d=d
p
	​

(n) be the leading digit of n in base p, meaning

d=⌊
p
e
n
	​

⌋,1≤d≤p−1.

Now

a
n
	​

=
j=1
∑
n
	​

j
L
n
	​

	​

.

Modulo p, the term L
n
	​

/j vanishes unless j contains the full p
e
-factor. The only such j≤n are

j=ip
e
,1≤i≤d.

Thus

a
n
	​

≡
i=1
∑
d
	​

ip
e
L
n
	​

	​

(modp).

Let

U=
p
e
L
n
	​

	​

.

Since v
p
	​

(L
n
	​

)=e, we have p∤U. Therefore

a
n
	​

≡U
i=1
∑
d
	​

i
−1
(modp).

Because U

≡0(modp),

p∣a
n
	​

⟺
i=1
∑
d
	​

i
−1
≡0(modp).

Equivalently, if

H
d
	​

=
B
d
	​

A
d
	​

	​


in lowest terms, then p∤B
d
	​

, since d<p, and hence

p∣a
n
	​

⟺p∣A
d
	​

.

Since p∣L
n
	​

, this gives the exact condition

p∣G
n
	​

⟺p∣A
d
p
	​

(n)
	​

.

So

G
n
	​

=1⟺∀p≤n,p∤A
d
p
	​

(n)
	​

.
Infinite non-coprime cases

Take

n=2⋅3
m

for m≥0. Then the leading digit of n in base 3 is 2, because

2⋅3
m
≤n<3
m+1
.

For d=2,

H
2
	​

=1+
2
1
	​

=
2
3
	​

,

whose numerator is 3. Therefore the prime-level criterion gives

3∣G
n
	​

.

Hence

G
2⋅3
m
	​

>1

for every m≥0. Therefore

{n≥1:G
n
	​

>1}

is infinite.

This part is proved.

The remaining target

The unresolved part is:

∀N ∃n≥N such that ∀p≤n,p∤A
d
p
	​

(n)
	​

.

Equivalently, define the forbidden digit set

Z
p
	​

={1≤d≤p−1:
i=1
∑
d
	​

i
−1
≡0(modp)}.

Then

G
n
	​

=1⟺d
p
	​

(n)∈
/
Z
p
	​

for every prime p≤n.

For each bad pair (p,d) with d∈Z
p
	​

, the forbidden n’s are exactly the intervals

dp
e
≤n<(d+1)p
e
,e≥1.

Thus the coprime problem becomes:

Are there infinitely many integers n avoiding all forbidden intervals [dp
e
,(d+1)p
e
)?
Search branches attempted
Branch A: direct construction

Try to build an infinite explicit sequence n
m
	​

 whose leading digit avoids Z
p
	​

 for every p≤n
m
	​

.

The obstruction is that avoiding one prime base does not stabilize avoidance in another prime base. For example, choosing n to have leading digit 1 in base 3 gives no automatic control over its leading digit in base 5,7,11,….

No verified infinite family was obtained.

Branch B: interval-complement argument

The forbidden set is

p
⋃
	​

d∈Z
p
	​

⋃
	​

e≥1
⋃
	​

[dp
e
,(d+1)p
e
).

A proof of infinite coprime n would follow if one could prove that this union does not cover all sufficiently large integers.

However, the simple density estimate is too weak. Even the always-forbidden digit d=p−1 gives intervals

[(p−1)p
e
,p
e+1
),

and these have logarithmic size comparable to 1/p. Summing over primes gives a divergent obstruction, so a naive union bound cannot prove infinitude.

No covering or non-covering theorem was derived from first principles.

Branch C: contradiction from eventual non-coprimality

Assume for contradiction that for every sufficiently large n, some prime p≤n satisfies

d
p
	​

(n)∈Z
p
	​

.

This means every sufficiently large n lies in at least one forbidden interval.

A contradiction would require showing that the forbidden intervals cannot form an eventual covering system. I found no elementary invariant preventing such a covering. The intervals have many overlaps and occur across incommensurable prime scales, so the contradiction route did not close.

Verified conclusions

We have proved:

{n≥1:G
n
	​

>1} is infinite.
	​


We have also proved the exact criterion:

G
n
	​

=1⟺∀p≤n,p∤A
d
p
	​

(n)
	​

	​


where H
d
	​

=A
d
	​

/B
d
	​

 is reduced and d
p
	​

(n) is the leading digit of n in base p.

But I did not obtain a proof or disproof of

{n≥1:G
n
	​

=1} is infinite.
	​


Therefore the full two-part statement was not proved or disproved within this session.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 94/100
COMPLETENESS_SCORE: 55/100
ADVERSARIAL_SURVIVAL_SCORE: 88/100

RESOURCE_USAGE: approximately 80% reasoning budget used; 3 main branches explored; 4 verified lemmas generated; 3 failed proof attempts for the coprime infinitude.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

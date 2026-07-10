# Erdős Problem #913 [unsolved] 18%

---

## ChatGPT Response

Formalization

For n∈N
>0
	​

, write

n(n+1)=
p∣n(n+1)
∏
	​

p
v
p
	​

(n(n+1))
.

Define

P(n)⟺∀p

=q(pq∣n(n+1)⟹v
p
	​

(n(n+1))

=v
q
	​

(n(n+1))).

The question is whether

∀N∈N∃n>NP(n).

Its negation is

∃N∈N∀n>N¬P(n),

where

¬P(n)⟺∃p

=q:p,q∣n(n+1)andv
p
	​

(n(n+1))=v
q
	​

(n(n+1)).

Because gcd(n,n+1)=1, every prime divides exactly one of n,n+1. Consequently, P(n) is equivalent to injectivity of the combined valuation map

p⟼{
v
p
	​

(n),
v
p
	​

(n+1),
	​

p∣n,
p∣n+1.
	​


Thus all positive exponents occurring in the factorizations of n and n+1, including exponents on the same side, must be pairwise distinct.

A necessary cardinality bound is

ω(n(n+1))≤max{r:
2
r(r+1)
	​

≤log
2
	​

(n(n+1))},

since r distinct positive exponents have sum at least 1+⋯+r, and every associated prime is at least 2. This bound creates no contradiction with infinitely many possible n.

Verified conditional construction

Let p be an odd prime and suppose

q=8p
2
−1

is also prime. Set n=q. Then

n(n+1)=(8p
2
−1)(8p
2
)=q2
3
p
2
.

The primes q,2,p are distinct:

p

=2, since p is odd;

q

=2, since q is odd and greater than 2;

q

=p, because q=8p
2
−1>p.

Therefore the prime exponents are exactly

1,3,2,

which are pairwise distinct. Hence

p and 8p
2
−1 prime⟹P(8p
2
−1).

Thus infinitely many such primes p would imply an affirmative answer. This is only a conditional implication; it does not prove the required infinitude.

Other verified infinite-family reductions

Several elementary templates yield valid n whenever an associated prime condition holds.

Prime powers

If a≥2 and 2
a
−1 is prime, then for

n=2
a
−1

we have

n(n+1)=(2
a
−1)2
a
,

with exponents {1,a}, which are distinct. Hence P(n).

Similarly, if 2
a
+1 is prime and n=2
a
, then

n(n+1)=2
a
(2
a
+1),

again with exponents {a,1}.

Neither template gives an unconditional infinitude without proving an additional prime-producing assertion.

A general three-exponent template

Suppose a,b,c are distinct positive integers and

n=r
a
,n+1=s
b
t
c

for distinct primes r,s,t. Then P(n). The same holds with the two consecutive integers interchanged.

However, constructing infinitely many solutions of

r
a
+1=s
b
t
c

with fixed pairwise-distinct exponents is itself an unresolved Diophantine requirement in the present derivation. The reduction therefore supplies no unconditional proof.

Structural obstructions encountered

An elementary construction must tightly control the complete prime factorizations of two consecutive integers. Merely forcing divisibility is insufficient: any uncontrolled cofactor can introduce

two primes both with exponent 1;

an exponent already appearing in the prescribed portion;

repeated exponents among its own prime factors.

Chinese-remainder constructions prescribe local valuations but do not ensure that the remaining cofactors have acceptable factorizations.

Pell-type equations can force prescribed square divisors on both n and n+1, but arbitrary residual factors remain. Moreover, two distinct residual primes appearing to the first power immediately violate injectivity.

Expressions such as x
m
−1 generally split into several factors. If two different prime divisors occur only once, the exponent 1 repeats. Thus algebraic factorization alone does not provide the required control.

Recursive Euclidean constructions of the form N
j+1
	​

=N
j
	​

+1 guarantee new prime divisors but do not control their multiplicities or prevent repeated valuations.

Adversarial check of the conditional construction

The factorization

(8p
2
−1)(8p
2
)=(8p
2
−1)2
3
p
2

uses p odd. For p=2,

8p
2
=32=2
5
,

so the purported separate exponents 3 and 2 collapse into the single exponent 5. Therefore the oddness hypothesis is essential.

The primality of 8p
2
−1 is also essential to this particular argument. If it is composite, its distinct prime factors can have repeated exponents, especially exponent 1. No acceptable factorization follows merely from its numerical form.

No argument developed here proves that infinitely many odd primes p make 8p
2
−1 prime, nor does any developed alternative avoid an equally substantive uncontrolled-factorization problem.

RESOURCE_EXHAUSTED

PROOF_CONFIDENCE: 97/100
Confidence that the verified implications and identified limitations above are logically correct.

COMPLETENESS_SCORE: 18/100
Several constructions and structural constraints were rigorously established, but neither the required infinitude nor its negation was proved.

ADVERSARIAL_SURVIVAL_SCORE: 94/100
The conditional family survives edge-case and factorization checks; it remains explicitly conditional.

RESOURCE_USAGE:
Approximately 100% of the allocated reasoning budget; more than 12 construction/reduction directions examined; 5 verified structural observations; multiple failed unconditional construction attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

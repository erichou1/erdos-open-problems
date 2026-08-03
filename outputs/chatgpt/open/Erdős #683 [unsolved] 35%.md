# Erdős Problem #683 [unsolved] 35%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formal statement

Let P(m) denote the largest prime divisor of m, for m≥2. Since (
0
n
	​

)=(
n
n
	​

)=1, the problem only concerns 1≤k≤n−1.

The claim is:

∃c>0 ∀n≥2 ∀k∈{1,…,n−1}:P(
k
n
	​

)≥min(n−k+1,k
1+c
).
Quantifier structure

The constant c must be universal. It cannot depend on n or k.

Negation:

∀c>0 ∃n≥2 ∃1≤k≤n−1:P(
k
n
	​

)<min(n−k+1,k
1+c
).

Equivalently, for every c>0, one would need a binomial coefficient whose prime factors are all smaller than both n−k+1 and k
1+c
.

Reduction by symmetry

Since

(
k
n
	​

)=(
n−k
n
	​

),

write r=min(k,n−k). The known input from the problem statement gives:

P(
r
n
	​

)>rwhenever r≤n/2.

For k>n/2, we have r=n−k, so

P(
k
n
	​

)=P(
r
n
	​

)>r=n−k.

Because P(
k
n
	​

) is an integer,

P(
k
n
	​

)≥n−k+1.

Thus the whole problem is settled for k>n/2.

So the only hard range is

1≤k≤n/2.

There the desired bound becomes

P(
k
n
	​

)≥min(n−k+1,k
1+c
).

Sylvester and Schur only gives

P(
k
n
	​

)>k.

The gap is therefore:

P(
k
n
	​

)>k⟹?P(
k
n
	​

)≥k
1+c
.

This implication is false in general without additional information, because >k does not force >k
1+c
.

Key verified partial theorem

For all k>n/2,

P(
k
n
	​

)≥n−k+1.

Proof: Let r=n−k. Then r<n/2, and

(
k
n
	​

)=(
r
n
	​

).

By Sylvester and Schur,

P(
r
n
	​

)>r.

Since the largest prime divisor is an integer,

P(
k
n
	​

)≥r+1=n−k+1.

This verifies exactly the large k half.

Remaining primary target

It remains to prove or disprove:

∃c>0 ∀n≥2 ∀1≤k≤n/2:P(
k
n
	​

)≥min(n−k+1,k
1+c
).

The difficult subcase is when

n−k+1>k
1+c
,

because then the target becomes

P(
k
n
	​

)≥k
1+c
.

That requires a uniform power improvement over Sylvester and Schur.

Attempted proof routes

Direct proof through the numerator

(
k
n
	​

)=
k!
(n−k+1)(n−k+2)⋯n
	​


would work if one could show that some prime p>k
1+c
 divides the numerator with exponent exceeding its exponent in k!. This reduces to proving that the interval

[n−k+1,n]

contains prime power structure that cannot be cancelled by k!. I could not prove this from first principles.

Contradiction would assume all prime divisors satisfy

p<k
1+c
.

Then (
k
n
	​

) is k
1+c
-smooth. A size argument gives

(
k
n
	​

)≥(
k
n
	​

)
k
,

but smooth numbers can still be extremely large because small primes may appear with high multiplicity. This does not contradict smoothness.

A valuation approach writes

v
p
	​

(
k
n
	​

)=v
p
	​

(n!)−v
p
	​

(k!)−v
p
	​

((n−k)!).

To prove the claim, one needs some p≥k
1+c
 with positive valuation. I found no elementary argument forcing such a prime uniformly for every interval of length k.

Conclusion

The statement is fully verified for k>n/2, but the essential range k≤n/2 requires proving a uniform power improvement

P(
k
n
	​

)≥k
1+c

whenever n−k+1 is larger than k
1+c
. I did not obtain a proof or a counterexample from first principles within the available reasoning budget.

PROOF_CONFIDENCE: 95
COMPLETENESS_SCORE: 35
ADVERSARIAL_SURVIVAL_SCORE: 80
RESOURCE_USAGE: 100 percent reasoning budget used, 3 main branches explored, 1 verified lemma generated, 3 failed proof attempts.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information. All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

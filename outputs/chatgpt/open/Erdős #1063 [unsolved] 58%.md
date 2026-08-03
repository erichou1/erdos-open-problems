# Erdős Problem #1063 [unsolved] 58%

---

## ChatGPT Response

RESOURCE_EXHAUSTED

Formalization

For k≥2, n≥2k, and 0≤i<k, define

D
i
	​

(n,k)⟺n−i∣(
k
n
	​

).

Then

n
k
	​

=min{n≥2k:∣{i∈{0,…,k−1}:D
i
	​

(n,k)}∣=k−1}.

The quantifier structure is

∃!i
0
	​

∈{0,…,k−1}¬D
i
0
	​

	​

(n,k)and∀i

=i
0
	​

, D
i
	​

(n,k).

Its negation is that either no index fails or at least two indices fail.

For every i,

n−i
(
k
n
	​

)
	​

=
k!
∏
0≤j<k
j

=i
	​

	​

(n−j)
	​

.

Consequently,

D
i
	​

(n,k)⟺k!∣
0≤j<k
j

=i
	​

∏
	​

(n−j).
(1)

Equivalently, for every prime p,

D
i
	​

(n,k)⟺
0≤j<k
j

=i
	​

∑
	​

v
p
	​

(n−j)≥v
p
	​

(k!).
(2)

These equivalences are exact.

A rigorous exponential upper construction

Let

L
k
	​

=lcm(1,2,…,k−1)

and set

N=kL
k
	​

.

For k≥3, L
k
	​

≥2, so N≥2k.

We prove that precisely the index i=0 fails at n=N.

Divisibility for 1≤i<k

Fix a prime p, and put

a=v
p
	​

(k),b=v
p
	​

(L
k
	​

)=
1≤j<k
max
	​

v
p
	​

(j).

Then

v
p
	​

(N)=a+b.

For every 1≤j<k, the integer p
v
p
	​

(j)
 divides both N and j. Hence

v
p
	​

(N−j)≥v
p
	​

(j).
(3)

For fixed 1≤i<k, the product in (1) contains N and all N−j with 1≤j<k, j

=i. Therefore

v
p
	​

	​

0≤j<k
j

=i
	​

∏
	​

(N−j)
	​

	​

=v
p
	​

(N)+
1≤j<k
j

=i
	​

∑
	​

v
p
	​

(N−j)
≥a+b+
1≤j<k
j

=i
	​

∑
	​

v
p
	​

(j)
=a+b+v
p
	​

((k−1)!)−v
p
	​

(i).
	​


Since v
p
	​

(i)≤b,

a+b+v
p
	​

((k−1)!)−v
p
	​

(i)≥a+v
p
	​

((k−1)!)=v
p
	​

(k!).

This holds for every prime p. Thus

k!∣
0≤j<k
j

=i
	​

∏
	​

(N−j),

and therefore

N−i∣(
k
N
	​

)(1≤i<k).
(4)
Failure at i=0

Choose any prime p∣k. Then a=v
p
	​

(k)>0, so

v
p
	​

(N)=a+b>b≥v
p
	​

(j)(1≤j<k).

Whenever v
p
	​

(N)>v
p
	​

(j), one has

v
p
	​

(N−j)=v
p
	​

(j).

Indeed, writing j=p
r
u, with p∤u, and noting that
p
r+1
∣N, gives

N−j=p
r
(p
v
p
	​

(N)−r
q−u),

where the parenthesized factor is nonzero modulo p.

Hence

v
p
	​

(
j=1
∏
k−1
	​

(N−j))
	​

=
j=1
∑
k−1
	​

v
p
	​

(N−j)
=
j=1
∑
k−1
	​

v
p
	​

(j)
=v
p
	​

((k−1)!)
=v
p
	​

(k!)−v
p
	​

(k)
<v
p
	​

(k!).
	​


Thus

k!∤
j=1
∏
k−1
	​

(N−j),

and by (1),

N∤(
k
N
	​

).
(5)

Equations (4)–(5) prove that N=kL
k
	​

 has exactly one exceptional index, namely i=0. Therefore

n
k
	​

≤klcm(1,2,…,k−1)
	​

(k≥3).
(6)

For k=2, direct calculation gives n
2
	​

=4.

Because n
k
	​

 is defined only among n≥2k,

2k≤n
k
	​

≤klcm(1,2,…,k−1).
	​

(7)

Using the least-common-multiple asymptotic explicitly supplied in the problem statement,

loglcm(1,…,k−1)=(1+o(1))k,

we obtain

n
k
	​

≤exp((1+o(1))k).
	​

(8)

Thus the fully verified estimate derivable here is

2k≤n
k
	​

≤e
(1+o(1))k
.
	​


No matching exponential lower bound, polynomial upper bound, or asymptotic formula for n
k
	​

 has been established in this session. In particular, the construction proves an upper bound but does not prove that its exponential scale is necessary.

Dependency graph
factorial formula for (
k
n
	​

)⟹(1)⟹(2)
v
p
	​

(N)=v
p
	​

(k)+v
p
	​

(L
k
	​

)⟹(3)⟹D
i
	​

(N,k)(1≤i<k)
p∣k⟹v
p
	​

(N)>v
p
	​

(j)⟹v
p
	​

(N−j)=v
p
	​

(j)⟹¬D
0
	​

(N,k)
⟹n
k
	​

≤kL
k
	​

.

PROOF_CONFIDENCE: 99

COMPLETENESS_SCORE: 58

ADVERSARIAL_SURVIVAL_SCORE: 97

RESOURCE_USAGE: approximately 100% of the practical response budget; 3 principal branches examined; 5 lemmas formalized; 2 attempted routes toward stronger lower bounds did not produce a verified result.

I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session.

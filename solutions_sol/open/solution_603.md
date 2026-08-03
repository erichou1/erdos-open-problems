# Erdős Problem #603 [unsolved] ?%

---

## ChatGPT Response

The conclusion is stronger than any fixed upper bound: the requested cardinal does not exist. 

Pasted text

Edit
Theorem

There is no cardinal (C) such that every family (\mathcal A) of countably infinite sets satisfying

[
|A\cap B|\ne 2\qquad(A,B\in\mathcal A,\ A\ne B)
]

admits a coloring with at most (C) colors in which no member of (\mathcal A) is monochromatic.

In fact, such families have unbounded chromatic number.

Proof

Let (\lambda) be an arbitrary infinite cardinal. We construct a family satisfying the intersection condition that cannot be properly colored with (\lambda) colors.

We use the following instance of the Erdős–Rado partition theorem:

[
(2^\lambda)^+\longrightarrow (\lambda^+)^2_\lambda.
]

Explicitly, if

[
\kappa=(2^\lambda)^+
]

and

[
c:[\kappa]^2\longrightarrow\lambda
]

is any coloring of the two-element subsets of (\kappa) with (\lambda) colors, then there is a set (H\subseteq\kappa) of cardinality (\lambda^+) such that (c) is constant on ([H]^2).

Set

[
X=[\kappa]^2.
]

For every countably infinite set (S\subseteq\kappa), define

[
A_S=[S]^2.
]

Let

[
\mathcal A={A_S\in[\kappa]^{\aleph_0}}.
]

Each (A_S) is countably infinite.

Verification of the intersection condition

For distinct countably infinite (S,T\subseteq\kappa),

[S]^2\cap[T]^2

[S\cap T]^2.
]

Let (\mu=|S\cap T|).

If (\mu\le 1), then

[
|A_S\cap A_T|=0.
]

If (\mu=n) is finite with (n\ge2), then

[
|A_S\cap A_T|=\binom n2.
]

The sequence of possible values is

[
1,3,6,10,\ldots,
]

and none of these equals (2).

If (\mu) is infinite, then

[
|A_S\cap A_T|=\mu,
]

which is also not (2). Hence

[
|A_S\cap A_T|\ne2
]

for all distinct (A_S,A_T\in\mathcal A).

No (\lambda)-coloring works

Suppose that

[
c\longrightarrow\lambda
]

is a coloring of the union of the family. Since every pair of elements of (\kappa) belongs to some countably infinite (S\subseteq\kappa),

[
\bigcup\mathcal A=X=[\kappa]^2.
]

Thus (c) is a (\lambda)-coloring of ([\kappa]^2). By the stated Erdős–Rado relation, there is (H\subseteq\kappa) with

[
|H|=\lambda^+
]

such that (c) is constant on ([H]^2).

Choose any countably infinite set (S\subseteq H). Then

[
A_S=[S]^2\subseteq[H]^2,
]

so (A_S) is monochromatic. Therefore no coloring with at most (\lambda) colors avoids monochromatic members of (\mathcal A).

Since (\lambda) was an arbitrary infinite cardinal, the chromatic numbers of families satisfying the required intersection condition are unbounded among all cardinals. Finite proposed bounds are also impossible, since a family that is not countably colorable is not colorable with finitely many colors.

Consequently, there is no smallest cardinal (C), and indeed no universal cardinal upper bound at all.

[
\boxed{\text{No such cardinal }C\text{ exists.}}
]

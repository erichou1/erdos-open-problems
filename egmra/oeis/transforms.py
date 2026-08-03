"""Typed OEIS transform registry (spec §8.2).

Transforms are generated locally and deduplicated before any remote query. Each
transform declares input/output domains, parameters, preconditions and (where
relevant) an inverse; an undefined transform *fails visibly* rather than silently
emitting a query. All arithmetic is exact (``int`` / ``fractions.Fraction``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import comb, gcd
from types import MappingProxyType
from typing import Any, Callable

Seq = list  # list[int | Fraction]


class TransformError(ValueError):
    """Raised when a transform's precondition is violated (fails visibly)."""


@dataclass(frozen=True)
class TransformSpec:
    name: str
    input_domain: str        # integer | rational
    output_domain: str
    params: tuple[str, ...]
    has_inverse: bool
    apply: Callable[..., Seq]
    description: str = ""


# ── transform implementations ────────────────────────────────────────────────

def _require_int(seq: Seq) -> None:
    for value in seq:
        if isinstance(value, bool):
            raise TransformError("transform requires integers, not booleans")
        if isinstance(value, Fraction):
            if value.denominator == 1:
                continue
            raise TransformError("transform requires an integer sequence")
        if type(value) is not int:
            raise TransformError("transform requires an integer sequence")


def t_identity(seq: Seq) -> Seq:
    return list(seq)


def t_shift_index(seq: Seq, *, offset: int = 0) -> Seq:
    # Index relabeling does not change values; offset is recorded in the path.
    if not isinstance(offset, int):
        raise TransformError("shift_index offset must be an integer")
    return list(seq)


def t_drop_prefix(seq: Seq, *, count: int = 1) -> Seq:
    if count < 0 or count >= len(seq):
        raise TransformError("drop_prefix count out of range")
    return list(seq[count:])


def t_negate(seq: Seq) -> Seq:
    return [-x for x in seq]


def t_absolute(seq: Seq) -> Seq:
    return [abs(x) for x in seq]


def t_complement(seq: Seq, *, universe: int | None = None) -> Seq:
    if universe is None:
        raise TransformError("complement requires an explicit universe/baseline")
    return [universe - x for x in seq]


def t_normalize_gcd(seq: Seq) -> Seq:
    _require_int(seq)
    ints = [int(x) for x in seq]
    g = 0
    for x in ints:
        g = gcd(g, x)
    if g == 0:
        raise TransformError("normalize_gcd requires a nonzero scale")
    return [x // g for x in ints]


def t_first_difference(seq: Seq) -> Seq:
    if len(seq) < 2:
        raise TransformError("first_difference needs at least two terms")
    return [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]


def t_higher_differences(seq: Seq, *, order: int = 2) -> Seq:
    if order < 1:
        raise TransformError("higher_differences order must be >= 1")
    out = list(seq)
    for _ in range(order):
        out = t_first_difference(out)
    return out


def t_partial_sums(seq: Seq) -> Seq:
    out: Seq = []
    total = 0
    for x in seq:
        total = total + x
        out.append(total)
    return out


def t_ratios_if_exact(seq: Seq) -> Seq:
    out: Seq = []
    for i in range(len(seq) - 1):
        if seq[i] == 0:
            raise TransformError("ratios_if_exact rejects zero denominators")
        out.append(Fraction(seq[i + 1]) / Fraction(seq[i]))
    if not out:
        raise TransformError("ratios_if_exact needs at least two terms")
    return out


def t_even_subsequence(seq: Seq) -> Seq:
    return list(seq[0::2])


def t_odd_subsequence(seq: Seq) -> Seq:
    return list(seq[1::2])


def t_arithmetic_subsequence(seq: Seq, *, start: int = 0, step: int = 2) -> Seq:
    if step < 1 or start < 0:
        raise TransformError("arithmetic_subsequence needs start>=0, step>=1")
    return list(seq[start::step])


def t_interleave_split(seq: Seq, *, part: int = 0) -> Seq:
    if part not in (0, 1):
        raise TransformError("interleave_split part must be 0 or 1")
    return list(seq[part::2])


def t_binomial_transform(seq: Seq) -> Seq:
    _require_int(seq)
    n = len(seq)
    return [sum(comb(i, k) * seq[k] for k in range(i + 1)) for i in range(n)]


def t_inverse_binomial(seq: Seq) -> Seq:
    _require_int(seq)
    n = len(seq)
    return [sum((-1) ** (i - k) * comb(i, k) * seq[k] for k in range(i + 1)) for i in range(n)]


def _mobius(n: int) -> int:
    if n == 1:
        return 1
    result = 1
    d = 2
    m = n
    while d * d <= m:
        if m % d == 0:
            m //= d
            if m % d == 0:
                return 0
            result = -result
        d += 1
    if m > 1:
        result = -result
    return result


def t_mobius_transform(seq: Seq) -> Seq:
    """b[n] = sum_{d|n} mu(n/d) a[d]  (1-indexed Mobius inversion)."""
    _require_int(seq)
    n = len(seq)  # seq[0] is a(1)
    out: Seq = []
    for i in range(1, n + 1):
        total = 0
        for d in range(1, i + 1):
            if i % d == 0:
                total += _mobius(i // d) * seq[d - 1]
        out.append(total)
    return out


def t_euler_transform(seq: Seq) -> Seq:
    """Euler transform b from a via the standard c/b recurrence (1-indexed)."""
    _require_int(seq)
    n = len(seq)
    a = [0] + [int(x) for x in seq]  # 1-indexed
    c = [0] * (n + 1)
    b = [0] * (n + 1)
    for k in range(1, n + 1):
        c[k] = sum(d * a[d] for d in range(1, k + 1) if k % d == 0)
    for k in range(1, n + 1):
        b[k] = c[k] + sum(c[j] * b[k - j] for j in range(1, k))
        if b[k] % k != 0:
            raise TransformError("euler_transform produced a non-integer term")
        b[k] //= k
    return b[1:]


def t_dirichlet_inverse(seq: Seq) -> Seq:
    """Dirichlet inverse; requires an invertible first term (a(1) = ±1)."""
    _require_int(seq)
    a = [0] + [int(x) for x in seq]
    if abs(a[1]) != 1:
        raise TransformError("dirichlet_inverse requires an invertible first term (a(1)=±1)")
    n = len(seq)
    b = [Fraction(0)] * (n + 1)
    b[1] = Fraction(1, a[1])
    for m in range(2, n + 1):
        total = Fraction(0)
        for d in range(1, m):
            if m % d == 0:
                total += Fraction(a[m // d]) * b[d]
        b[m] = -total / a[1]
    result = b[1:]
    if all(x.denominator == 1 for x in result):
        return [int(x) for x in result]
    return result


_REGISTRY: dict[str, TransformSpec] = {}


def _register(spec: TransformSpec) -> None:
    _REGISTRY[spec.name] = spec


for _spec in [
    TransformSpec("identity", "integer", "integer", (), True, t_identity),
    TransformSpec("shift_index", "integer", "integer", ("offset",), True, t_shift_index),
    TransformSpec("drop_prefix", "integer", "integer", ("count",), False, t_drop_prefix),
    TransformSpec("negate", "integer", "integer", (), True, t_negate),
    TransformSpec("absolute", "integer", "integer", (), False, t_absolute),
    TransformSpec("complement", "integer", "integer", ("universe",), True, t_complement),
    TransformSpec("normalize_gcd", "integer", "integer", (), False, t_normalize_gcd),
    TransformSpec("first_difference", "integer", "integer", (), False, t_first_difference),
    TransformSpec("higher_differences", "integer", "integer", ("order",), False, t_higher_differences),
    TransformSpec("partial_sums", "integer", "integer", (), True, t_partial_sums),
    TransformSpec("ratios_if_exact", "integer", "rational", (), False, t_ratios_if_exact),
    TransformSpec("even_subsequence", "integer", "integer", (), False, t_even_subsequence),
    TransformSpec("odd_subsequence", "integer", "integer", (), False, t_odd_subsequence),
    TransformSpec("arithmetic_subsequence", "integer", "integer", ("start", "step"), False, t_arithmetic_subsequence),
    TransformSpec("interleave_split", "integer", "integer", ("part",), False, t_interleave_split),
    TransformSpec("binomial_transform", "integer", "integer", (), True, t_binomial_transform),
    TransformSpec("inverse_binomial", "integer", "integer", (), True, t_inverse_binomial),
    TransformSpec("euler_transform", "integer", "integer", (), False, t_euler_transform),
    TransformSpec("mobius_transform", "integer", "integer", (), False, t_mobius_transform),
    TransformSpec("dirichlet_inverse", "integer", "rational", (), False, t_dirichlet_inverse),
]:
    _register(_spec)


REGISTERED_TRANSFORMS = tuple(_REGISTRY)


def get_transform(name: str) -> TransformSpec:
    if name not in _REGISTRY:
        raise TransformError(f"undefined transform {name!r}; registered: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def apply_transform(name: str, seq: Seq, **params: Any) -> Seq:
    spec = get_transform(name)
    values = list(seq)
    if spec.input_domain == "integer":
        _require_int(values)
    unexpected = set(params) - set(spec.params)
    if unexpected:
        raise TransformError(f"transform {name} got unexpected params {sorted(unexpected)}")
    try:
        return spec.apply(values, **params)
    except TypeError as exc:
        raise TransformError(f"invalid parameters for transform {name}: {exc}") from exc


@dataclass(frozen=True)
class TransformStep:
    name: str
    params: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        spec = get_transform(self.name)
        unexpected = set(self.params) - set(spec.params)
        if unexpected:
            raise TransformError(
                f"transform {self.name} got unexpected params {sorted(unexpected)}"
            )
        object.__setattr__(self, "params", MappingProxyType(dict(self.params)))

    def label(self) -> str:
        if not self.params:
            return self.name
        inner = ",".join(f"{k}={v}" for k, v in sorted(self.params.items()))
        return f"{self.name}:{inner}"


def apply_path(seq: Seq, path: list[TransformStep]) -> Seq:
    out = list(seq)
    for step in path:
        out = apply_transform(step.name, out, **step.params)
    return out

"""Safe operator-supplied predicates for the counterexample/boundary probes.

The intake probes accept an executable ``predicate(n) -> bool`` so the
counterexample search genuinely enumerates small cases. On the arbitrary/browser
path the operator supplies that predicate from the command line. To keep this an
operator *input* rather than an arbitrary code-execution surface, the predicate is
a single **bounded expression over the integer variable ``n``** (e.g.
``"n*n >= 0"`` or ``"all(k*k >= 0 for k in range(n+1))"``). It is parsed to an AST,
validated against a strict whitelist (no imports, attribute access, subscripting,
lambdas, f-strings, or arbitrary calls — only a small set of numeric builtins),
compiled once, and evaluated with an empty ``__builtins__`` so there is no path to
the interpreter internals. This is deliberately *not* a general programming
facility; a predicate that cannot be expressed this way should be exercised
through the sandboxed finite-experiment path instead.
"""

from __future__ import annotations

import ast
from typing import Callable

_MAX_PREDICATE_LEN = 2000

# The only callables a predicate may invoke. Each is a pure, side-effect-free
# numeric builtin; none can reach the filesystem, network, or interpreter state.
_SAFE_BUILTINS: dict[str, Callable] = {
    "abs": abs,
    "min": min,
    "max": max,
    "pow": pow,
    "int": int,
    "bool": bool,
    "len": len,
    "sum": sum,
    "all": all,
    "any": any,
    "range": range,
    "divmod": divmod,
}

# Node types permitted anywhere in the expression. Anything omitted here
# (Attribute, Subscript, Lambda, NamedExpr, Starred, Dict, comprehensions over
# dicts, f-strings, await, yield, …) is rejected, which closes the usual
# ``().__class__.__bases__`` style sandbox escapes because attribute access and
# subscripting are simply not in the grammar.
_ALLOWED_NODES: tuple[type, ...] = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or,
    ast.UnaryOp, ast.Not, ast.USub, ast.UAdd, ast.Invert,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
    ast.Pow, ast.LShift, ast.RShift, ast.BitAnd, ast.BitOr, ast.BitXor,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.In, ast.NotIn,
    ast.Constant, ast.Name, ast.Load, ast.Call, ast.IfExp,
    ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.comprehension,
    ast.Tuple, ast.List, ast.Set,
    # ``Store`` only ever appears as a comprehension ``for`` target in an
    # eval-mode expression (no assignment statements exist), so permitting it
    # does not admit mutation.
    ast.Store,
)


class PredicateError(ValueError):
    """An operator predicate is malformed or uses a disallowed construct."""


def _comprehension_targets(tree: ast.AST) -> set[str]:
    """Names bound by comprehension ``for`` clauses (they are local to the expr)."""
    targets: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.comprehension):
            continue
        stack = [node.target]
        while stack:
            current = stack.pop()
            if isinstance(current, ast.Name):
                targets.add(current.id)
            elif isinstance(current, (ast.Tuple, ast.List)):
                stack.extend(current.elts)
            else:
                raise PredicateError("predicate uses an unsupported comprehension target")
    return targets


def compile_bounded_predicate(expression: str, *, var: str = "n") -> Callable[[int], bool]:
    """Compile a safe bounded predicate expression over ``var`` into a callable.

    The returned callable maps an integer to a ``bool``. It only ever evaluates
    the whitelisted, AST-validated expression with an empty ``__builtins__`` and a
    fixed set of numeric helpers, so it cannot import modules, touch the
    filesystem/network, or reach interpreter internals.
    """
    if not isinstance(expression, str) or not expression.strip():
        raise PredicateError("predicate expression must be a non-empty string")
    if len(expression) > _MAX_PREDICATE_LEN:
        raise PredicateError(
            f"predicate expression exceeds {_MAX_PREDICATE_LEN} characters"
        )
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise PredicateError(f"predicate is not a valid expression: {exc}") from exc

    comprehension_vars = _comprehension_targets(tree)
    allowed_names = {var} | set(_SAFE_BUILTINS) | comprehension_vars
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise PredicateError(
                f"predicate uses a disallowed construct: {type(node).__name__}"
            )
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float, bool)):
            raise PredicateError("predicate literals must be numeric or boolean")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise PredicateError(f"predicate references an unknown name: {node.id}")
        if isinstance(node, ast.Call):
            if node.keywords or not isinstance(node.func, ast.Name):
                raise PredicateError("predicate calls must be positional calls to a builtin")
            if node.func.id not in _SAFE_BUILTINS:
                raise PredicateError(
                    "predicate may only call: " + ", ".join(sorted(_SAFE_BUILTINS))
                )
            if any(isinstance(arg, ast.Starred) for arg in node.args):
                raise PredicateError("predicate calls may not use argument unpacking")

    code = compile(tree, "<egmra-predicate>", "eval")
    base_globals = {"__builtins__": {}, **_SAFE_BUILTINS}

    def predicate(value: int) -> bool:
        # Names resolve from globals so comprehension-nested scopes see the
        # variable and helpers; __builtins__ is empty so nothing else is reachable.
        return bool(eval(code, {**base_globals, var: value}))  # noqa: S307 - AST-whitelisted

    return predicate

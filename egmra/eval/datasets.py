"""Evaluation datasets: local fixtures + pinned-benchmark manifests (spec §13.7).

The §13.7 evaluation set composition is encoded here. Concrete, *executable* local
fixtures (elementary true/false/ambiguous statements with predicates) let the eval
harness genuinely run. External benchmarks (miniF2F, PutnamBench, ProofNet#) are
described as pinned manifests with the exact fetch command — they are not bundled
(licensing + size; see DECISIONS.md D-004).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

# The §13.7 evaluation-set composition.
EVAL_SET_COMPOSITION = {
    "false_ambiguous_elementary": 20,
    "minif2f_proofnet_sharp_subset": "regression subset",
    "putnam_imo_formal": 20,
    "literature_retrieval": 10,
    "computation_plus_proof": 10,
    "historical_erdos": 20,
    "unsolved_deployment": "small; no solve-rate claim",
}


@dataclass(frozen=True)
class FixtureProblem:
    problem_id: str
    statement: bytes
    expected_outcome: str          # verified / honest_triage / refuted
    predicate_src: str = ""        # a python expression body: fn of n -> bool
    scope: str = "general"
    level: int = 1

    def predicate(self):
        if not self.predicate_src:
            return None
        expression = _compile_fixture_predicate(self.predicate_src)

        def predicate(n: int) -> bool:
            if type(n) is not int:
                raise TypeError("fixture predicates accept exact integers only")
            return bool(_evaluate_fixture_predicate(expression, n))

        return predicate


# Concrete, executable local fixtures (a subset that actually runs in tests).
FIXTURE_PROBLEMS = [
    FixtureProblem("fx-true-square", b"Prove that for all natural numbers n, n squared is >= 0.",
                   "verified", "n * n >= 0", scope="finite_domain", level=1),
    FixtureProblem("fx-false-prime", b"Prove that for all positive integers n, n is prime.",
                   "honest_triage", "_isprime(n)", level=1),
    FixtureProblem("fx-true-even-sum", b"Prove that for all n, 2*n is even.",
                   "verified", "(2 * n) % 2 == 0", scope="finite_domain", level=1),
    FixtureProblem("fx-false-all-even", b"Prove that for all natural numbers n, n is even.",
                   "honest_triage", "n % 2 == 0", level=1),
    FixtureProblem("fx-ambiguous", b"Show that the sequence grows, where it is bounded, "
                                   b"and there exists a limit.", "honest_triage", level=1),
]


@dataclass(frozen=True)
class BenchmarkManifest:
    name: str
    commit: str
    fetch_command: str
    semantic_audit_required: bool
    note: str = ""


PINNED_BENCHMARKS = {
    "miniF2F": BenchmarkManifest(
        "miniF2F", "facebookresearch/miniF2F@pinned",
        "git clone https://github.com/facebookresearch/miniF2F && git checkout <pinned>",
        semantic_audit_required=False, note="mature/saturated; regression only"),
    "ProofNet#": BenchmarkManifest(
        "ProofNet#", "aclanthology 2025.emnlp-main.907 corrected ports",
        "obtain corrected ProofNet# Lean4 ports (31.8% of original ports had errors)",
        semantic_audit_required=True),
    "PutnamBench": BenchmarkManifest(
        "PutnamBench", "trishullab/PutnamBench@a23d8e6d4e9e3418fd78f76de7bfcb9414cbfd39",
        "git clone https://github.com/trishullab/PutnamBench && git checkout a23d8e6",
        semantic_audit_required=True, note="factored-answer policy, pass@k, tool budget matter"),
    "IMO-LeanProofBench": BenchmarkManifest(
        "IMO-LeanProofBench", "google-deepmind/superhuman@96fa6c4cc3a9bb7450ee7b6773b659d3a030dace",
        "git clone https://github.com/google-deepmind/superhuman && git checkout 96fa6c4",
        semantic_audit_required=True),
}


def _isprime(n: int) -> bool:  # helper referenced by fixture predicates
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def fixture(problem_id: str) -> FixtureProblem:
    for f in FIXTURE_PROBLEMS:
        if f.problem_id == problem_id:
            return f
    raise KeyError(f"unknown fixture {problem_id!r}")


_ALLOWED_PREDICATE_NODES = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or,
    ast.UnaryOp, ast.Not, ast.USub, ast.UAdd,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Mod, ast.FloorDiv,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Name, ast.Load, ast.Constant, ast.Call,
)


def _compile_fixture_predicate(source: str):
    if not isinstance(source, str) or not source.strip() or len(source) > 1000:
        raise ValueError("unsafe fixture predicate: invalid source")
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise ValueError("unsafe fixture predicate: invalid expression") from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > 128:
        raise ValueError("unsafe fixture predicate: expression is too complex")
    call_function_nodes = {
        id(node.func) for node in nodes if isinstance(node, ast.Call)
    }
    for node in nodes:
        if not isinstance(node, _ALLOWED_PREDICATE_NODES):
            raise ValueError(
                f"unsafe fixture predicate: {type(node).__name__} is forbidden"
            )
        if isinstance(node, ast.Name) and node.id not in {"n", "_isprime"}:
            raise ValueError(f"unsafe fixture predicate: name {node.id!r} is forbidden")
        if isinstance(node, ast.Name) and node.id == "_isprime" \
                and id(node) not in call_function_nodes:
            raise ValueError("unsafe fixture predicate: _isprime must be called")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id != "_isprime" \
                    or len(node.args) != 1 or node.keywords:
                raise ValueError("unsafe fixture predicate: only _isprime(n) may be called")
        if isinstance(node, ast.Constant):
            if type(node.value) not in {bool, int} \
                    or (type(node.value) is int and abs(node.value) > 1_000_000_000):
                raise ValueError("unsafe fixture predicate: invalid constant")
    return tree.body


def _evaluate_fixture_predicate(node: ast.AST, n: int) -> bool | int:
    """Evaluate the closed fixture expression language without Python ``eval``."""
    if isinstance(node, ast.Constant):
        constant_value = node.value
        if type(constant_value) is bool:
            return constant_value
        if type(constant_value) is int:
            return constant_value
        raise ValueError("unsafe fixture predicate: invalid constant")
    if isinstance(node, ast.Name):
        if node.id != "n":
            raise ValueError("unsafe fixture predicate: invalid bare name")
        return n
    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_fixture_predicate(node.operand, n)
        if isinstance(node.op, ast.Not):
            return not operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result: bool | int = True
            for child in node.values:
                result = _evaluate_fixture_predicate(child, n)
                if not result:
                    return result
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for child in node.values:
                result = _evaluate_fixture_predicate(child, n)
                if result:
                    return result
            return result
    if isinstance(node, ast.BinOp):
        left = _evaluate_fixture_predicate(node.left, n)
        right = _evaluate_fixture_predicate(node.right, n)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
    if isinstance(node, ast.Compare):
        left = _evaluate_fixture_predicate(node.left, n)
        for op, comparator in zip(node.ops, node.comparators, strict=True):
            right = _evaluate_fixture_predicate(comparator, n)
            if isinstance(op, ast.Eq):
                passed = left == right
            elif isinstance(op, ast.NotEq):
                passed = left != right
            elif isinstance(op, ast.Lt):
                passed = left < right
            elif isinstance(op, ast.LtE):
                passed = left <= right
            elif isinstance(op, ast.Gt):
                passed = left > right
            elif isinstance(op, ast.GtE):
                passed = left >= right
            else:  # validation should make this unreachable
                raise ValueError("unsafe fixture predicate: invalid comparator")
            if not passed:
                return False
            left = right
        return True
    if isinstance(node, ast.Call):
        argument = _evaluate_fixture_predicate(node.args[0], n)
        if type(argument) is not int:
            raise TypeError("_isprime fixture arguments must be exact integers")
        return _isprime(argument)
    raise ValueError(f"unsafe fixture predicate: unsupported {type(node).__name__}")

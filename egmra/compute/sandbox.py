"""Fail-closed computational execution backends.

``RestrictedPythonExecutor`` is deliberately *not* described as an operating-
system sandbox.  It accepts a small, capability-free Python subset, executes it
in a fresh resource-limited process, and exposes no imports, attributes, file,
process, environment, or network APIs.  This is suitable for small exact local
checks, not for arbitrary untrusted Python.

``ContainerSandbox`` executes the same restricted program inside a real OCI
runtime with a read-only root, no network, no capabilities, a non-root user,
bounded resources, and no unsandboxed fallback.  When the runtime/image is not
available, the result says so explicitly.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from egmra.compute.spec import ExperimentSpec
from egmra.provenance.hashing import canonical_json, content_id


_RUNNER_VERSION = "restricted-python-v2"
_MAX_CODE_BYTES = 256 * 1024
_MAX_INPUT_BYTES = 1_000_000
_SAFE_BUILTIN_NAMES = (
    "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "int",
    "len", "list", "max", "min", "pow", "print", "range", "reversed",
    "round", "sorted", "str", "sum", "tuple", "zip",
)

_ALLOWED_AST_NODES = (
    ast.Module,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.Assign,
    ast.AnnAssign,
    ast.AugAssign,
    ast.For,
    ast.While,
    ast.If,
    ast.Break,
    ast.Continue,
    ast.Expr,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Subscript,
    ast.Slice,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.comprehension,
    ast.Lambda,
    ast.IfExp,
    ast.keyword,
    ast.And,
    ast.Or,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.LShift,
    ast.RShift,
    ast.BitOr,
    ast.BitXor,
    ast.BitAnd,
    ast.MatMult,
    ast.Invert,
    ast.Not,
    ast.UAdd,
    ast.USub,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Is,
    ast.IsNot,
    ast.In,
    ast.NotIn,
)

_RUNNER_TEMPLATE = r'''
import builtins
import json
import os
import resource
import sys

def _apply_required_limits():
    cpu = int(os.environ["EGMRA_CPU"])
    memory = int(os.environ["EGMRA_MEM"])
    processes = int(os.environ["EGMRA_PROCESSES"])
    file_size = int(os.environ["EGMRA_FILE_SIZE"])
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    # macOS reports memory rlimits but rejects setting them for modern Python
    # processes.  The trusted parent enforces RSS there; Linux/OCI uses AS here.
    if sys.platform != "darwin":
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_NPROC, (processes, processes))
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_size, file_size))
    resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
    os.umask(0o077)

_apply_required_limits()
with open(os.environ["EGMRA_INPUTS"], "r", encoding="utf-8") as _handle:
    _inputs = json.load(_handle)
with open(os.environ["EGMRA_CODE"], "r", encoding="utf-8") as _handle:
    _code = _handle.read()

_safe_names = %r
_safe_builtins = {name: getattr(builtins, name) for name in _safe_names}
if os.environ["EGMRA_ARITHMETIC"] == "exact":
    def _exact_pow(base, exponent, modulus=None):
        if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
            raise ValueError("exact arithmetic policy forbids non-integer or negative exponents")
        if modulus is None:
            return builtins.pow(base, exponent)
        return builtins.pow(base, exponent, modulus)
    _safe_builtins["pow"] = _exact_pow
_globals = {"__builtins__": _safe_builtins}
exec(compile(_code, "<egmra-restricted-job>", "exec"), _globals, _globals)
_entry = os.environ["EGMRA_ENTRY"]
_fn = _globals.get(_entry)
if not callable(_fn):
    raise RuntimeError("validated experiment entry point is missing")
_result = _fn(_inputs)
_payload = json.dumps(
    _result,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
if len(_payload.encode("utf-8")) > int(os.environ["EGMRA_OUTPUT_LIMIT"]):
    raise RuntimeError("output limit exceeded")
with open(os.environ["EGMRA_OUTPUT"], "x", encoding="utf-8") as _handle:
    _handle.write(_payload)
'''


class CodePolicyError(ValueError):
    """Raised when experiment source requests a forbidden capability."""


@dataclass(frozen=True)
class SandboxResult:
    ok: bool
    output: object
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    failure_kind: str = ""
    isolation: str = ""
    environment_hash: str = ""


def _runner_source() -> str:
    return _RUNNER_TEMPLATE % (_SAFE_BUILTIN_NAMES,)


def _validate_code(spec: ExperimentSpec, code: str) -> None:
    encoded = code.encode("utf-8")
    if len(encoded) > _MAX_CODE_BYTES:
        raise CodePolicyError("code policy rejects source larger than 256 KiB")
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise CodePolicyError(f"code policy rejects invalid syntax: {exc.msg}") from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > 10_000:
        raise CodePolicyError("code policy rejects an oversized syntax tree")
    if not tree.body or any(not isinstance(node, ast.FunctionDef) for node in tree.body):
        raise CodePolicyError("code policy permits only top-level function definitions")

    function_names = {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
    if spec.entry_point not in function_names:
        raise CodePolicyError(f"code policy requires entry point {spec.entry_point!r}")
    reserved = set(_SAFE_BUILTIN_NAMES)

    for node in nodes:
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise CodePolicyError(
                f"code policy forbids syntax {type(node).__name__}"
            )
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("_") or node.name in reserved:
                raise CodePolicyError("code policy forbids private or builtin-shadowing functions")
            if node.decorator_list or node.returns is not None or node.type_comment:
                raise CodePolicyError("code policy forbids decorators and annotations")
        if isinstance(node, ast.arg):
            if node.arg.startswith("_") or node.arg in reserved or node.annotation is not None:
                raise CodePolicyError("code policy forbids private, annotated, or builtin-shadowing arguments")
        if isinstance(node, ast.Name):
            if node.id.startswith("_"):
                raise CodePolicyError("code policy forbids private runtime names")
            if isinstance(node.ctx, ast.Store) and node.id in reserved:
                raise CodePolicyError("code policy forbids shadowing safe builtins")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in reserved and node.func.id not in function_names:
                    raise CodePolicyError(
                        f"code policy forbids call target {node.func.id!r}"
                    )
            elif not isinstance(node.func, ast.Lambda):
                raise CodePolicyError("code policy permits only direct safe calls")
        if spec.arithmetic_mode == "exact":
            if isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
                raise CodePolicyError("exact arithmetic policy forbids floating-point literals")
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                raise CodePolicyError("exact arithmetic policy forbids '/' because it produces float")
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                raise CodePolicyError(
                    "exact arithmetic policy requires checked pow() instead of '**'"
                )


def _validate_restricted_policy(spec: ExperimentSpec) -> str | None:
    if spec.sandbox_policy != "restricted-python-subprocess":
        return "execution policy requires restricted-python-subprocess"
    if spec.network != "off":
        return "network policy cannot enforce an allowlist in the restricted executor"
    if spec.max_processes != 1:
        return "process policy requires max_processes=1 in the restricted executor"
    return None


def _environment_hash(
    *,
    isolation: str,
    executable: str,
    image_id: str = "",
    runtime_identity: Mapping[str, Any] | None = None,
) -> str:
    return content_id(
        {
            "runner": _RUNNER_VERSION,
            "isolation": isolation,
            "executable": executable,
            "python": sys.version,
            "platform": platform.platform(),
            "image_id": image_id,
            "runtime_identity": dict(runtime_identity or {}),
        }
    )


def _probe_python(executable: Path) -> dict[str, Any]:
    probe = (
        "import json,platform,resource,sys;"
        "print(json.dumps({'implementation':sys.implementation.name,"
        "'version':list(sys.version_info[:3]),'platform':platform.platform(),"
        "'resource':all(hasattr(resource,n) for n in "
        "['RLIMIT_CPU','RLIMIT_FSIZE','RLIMIT_NPROC','RLIMIT_NOFILE'])},sort_keys=True))"
    )
    try:
        completed = subprocess.run(
            [str(executable), "-I", "-c", probe],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            env={"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Python executable probe failed: {exc}") from exc
    if completed.returncode != 0:
        raise ValueError("Python executable failed the isolated runtime probe")
    try:
        identity = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("Python executable returned a malformed runtime identity") from exc
    if not isinstance(identity, dict) or identity.get("implementation") not in {"cpython", "pypy"} \
            or not identity.get("resource"):
        raise ValueError("Python executable lacks the required isolated resource runtime")
    version = identity.get("version")
    if not isinstance(version, list) or version[:2] < [3, 9]:
        raise ValueError("Python executable must be Python 3.9 or newer")
    digest = hashlib.sha256()
    try:
        with executable.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exc:
        raise ValueError("Python executable could not be hashed") from exc
    identity["binary_sha256"] = digest.hexdigest()
    identity["path"] = str(executable)
    return identity


def _base_environment(spec: ExperimentSpec, *, inputs: Path, code: Path, output: Path) -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "EGMRA_INPUTS": str(inputs),
        "EGMRA_CODE": str(code),
        "EGMRA_OUTPUT": str(output),
        "EGMRA_ENTRY": spec.entry_point,
        "EGMRA_CPU": str(spec.cpu_seconds),
        "EGMRA_MEM": str(spec.memory_bytes),
        "EGMRA_PROCESSES": str(spec.max_processes),
        "EGMRA_FILE_SIZE": str(max(spec.max_output_bytes, spec.max_log_bytes) + 4096),
        "EGMRA_OUTPUT_LIMIT": str(spec.max_output_bytes),
        "EGMRA_ARITHMETIC": spec.arithmetic_mode,
        "PYTHONHASHSEED": str(spec.seed),
    }


def _write_job_files(work_path: Path, spec: ExperimentSpec, code: str) -> tuple[Path, Path, Path, Path]:
    inputs_path = work_path / "inputs.json"
    code_path = work_path / "code.py"
    output_path = work_path / "output.json"
    runner_path = work_path / "runner.py"
    inputs_payload = canonical_json(spec.to_dict()["inputs"])
    if len(inputs_payload.encode("utf-8")) > _MAX_INPUT_BYTES:
        raise CodePolicyError("input policy rejects payload larger than 1 MB")
    inputs_path.write_text(inputs_payload, encoding="utf-8")
    code_path.write_text(code, encoding="utf-8")
    runner_path.write_text(_runner_source(), encoding="utf-8")
    return inputs_path, code_path, output_path, runner_path


def _read_log(path: Path, limit: int) -> tuple[str, bool]:
    size = path.stat().st_size if path.exists() else 0
    data = path.read_bytes()[: limit + 1] if path.exists() else b""
    return data[:limit].decode("utf-8", errors="replace"), size > limit


def _kill_process_group(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # A just-exiting macOS child can briefly reject killpg even though
        # Popen has not reaped it yet.  Killing the direct process is sufficient
        # here because the restricted language cannot spawn descendants.
        try:
            proc.kill()
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def _wait_with_limits(
    proc: subprocess.Popen[Any],
    *,
    stdout_path: Path,
    stderr_path: Path,
    log_limit: int,
    wall_seconds: float,
    memory_bytes: int | None = None,
) -> tuple[bool, bool, bool]:
    """Return timeout/log/memory outcomes without buffering child streams."""

    deadline = time.monotonic() + wall_seconds
    while proc.poll() is None:
        if time.monotonic() >= deadline:
            _kill_process_group(proc)
            return True, False, False
        if (stdout_path.exists() and stdout_path.stat().st_size > log_limit) or \
                (stderr_path.exists() and stderr_path.stat().st_size > log_limit):
            _kill_process_group(proc)
            return False, True, False
        if memory_bytes is not None:
            rss = _resident_bytes(proc.pid)
            if rss is not None and rss > memory_bytes:
                _kill_process_group(proc)
                return False, False, True
        time.sleep(0.01)
    return False, False, False


def _resident_bytes(pid: int) -> int | None:
    """Read RSS without importing optional packages into the trust boundary."""

    status = Path(f"/proc/{pid}/status")
    if status.exists():
        try:
            for line in status.read_text(encoding="ascii").splitlines():
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
        except (OSError, UnicodeError, ValueError, IndexError):
            return None
    if sys.platform == "darwin":
        try:
            measured = subprocess.run(
                ["/bin/ps", "-o", "rss=", "-p", str(pid)],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
                env={"PATH": "/usr/bin:/bin"},
            )
            if measured.returncode == 0 and measured.stdout.strip():
                return int(measured.stdout.strip()) * 1024
        except (OSError, subprocess.TimeoutExpired, ValueError):
            return None
    return None


def _schema_error(value: Any, schema: Mapping[str, Any], *, path: str = "$") -> str | None:
    allowed = {
        "type", "required", "properties", "additionalProperties", "items", "enum", "const",
        "minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems",
    }
    unknown = set(schema) - allowed
    if unknown:
        return f"{path}: unsupported schema keywords {sorted(unknown)!r}"
    if "const" in schema and value != schema["const"]:
        return f"{path}: value does not equal schema const"
    if "enum" in schema and value not in schema["enum"]:
        return f"{path}: value is not in schema enum"

    expected = schema.get("type")
    predicates = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected is not None:
        if expected not in predicates:
            return f"{path}: unsupported schema type {expected!r}"
        if not predicates[expected](value):
            return f"{path}: expected {expected}, got {type(value).__name__}"

    if isinstance(value, dict):
        required = schema.get("required", ())
        if not isinstance(required, (list, tuple)) or any(not isinstance(key, str) for key in required):
            return f"{path}: schema required must be a string array"
        missing = [key for key in required if key not in value]
        if missing:
            return f"{path}: missing required keys {missing!r}"
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            return f"{path}: schema properties must be an object"
        for key, item in value.items():
            if key in properties:
                child = properties[key]
                if not isinstance(child, Mapping):
                    return f"{path}.{key}: property schema must be an object"
                error = _schema_error(item, child, path=f"{path}.{key}")
                if error:
                    return error
            elif schema.get("additionalProperties", True) is False:
                return f"{path}: additional property {key!r} is forbidden"
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            return f"{path}: too few items"
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            return f"{path}: too many items"
        item_schema = schema.get("items")
        if item_schema is not None:
            if not isinstance(item_schema, Mapping):
                return f"{path}: items schema must be an object"
            for index, item in enumerate(value):
                error = _schema_error(item, item_schema, path=f"{path}[{index}]")
                if error:
                    return error
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            return f"{path}: string is too short"
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return f"{path}: string is too long"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            return f"{path}: number is below minimum"
        if "maximum" in schema and value > schema["maximum"]:
            return f"{path}: number is above maximum"
    return None


def _finalize_result(
    *,
    spec: ExperimentSpec,
    proc: subprocess.Popen[Any],
    stdout_path: Path,
    stderr_path: Path,
    output_path: Path,
    timed_out: bool,
    log_exceeded: bool,
    memory_exceeded: bool,
    isolation: str,
    environment_hash: str,
) -> SandboxResult:
    stdout, stdout_exceeded = _read_log(stdout_path, spec.max_log_bytes)
    stderr, stderr_exceeded = _read_log(stderr_path, spec.max_log_bytes)
    if timed_out:
        return SandboxResult(
            False, None, proc.returncode or -1, stdout, "wall-clock timeout", True,
            "timeout", isolation, environment_hash,
        )
    if log_exceeded or stdout_exceeded or stderr_exceeded:
        return SandboxResult(
            False, None, proc.returncode or -1, stdout, "output limit exceeded", False,
            "output_limit", isolation, environment_hash,
        )
    if memory_exceeded:
        return SandboxResult(
            False, None, proc.returncode or -1, stdout, "memory limit exceeded", False,
            "memory_limit", isolation, environment_hash,
        )
    output_size = output_path.stat().st_size if output_path.exists() else 0
    if output_size > spec.max_output_bytes:
        return SandboxResult(
            False, None, proc.returncode or -1, stdout, "output limit exceeded", False,
            "output_limit", isolation, environment_hash,
        )
    if proc.returncode == -getattr(signal, "SIGXCPU", 10_000):
        return SandboxResult(
            False, None, proc.returncode, stdout, "CPU limit exceeded", False,
            "cpu_limit", isolation, environment_hash,
        )
    if proc.returncode != 0 or not output_path.exists():
        if "output limit exceeded" in stderr.lower() or output_size >= spec.max_output_bytes:
            stderr = "output limit exceeded"
            failure_kind = "output_limit"
        else:
            failure_kind = "execution_failed"
        return SandboxResult(
            False, None, proc.returncode or -1, stdout, stderr or "execution failed", False,
            failure_kind, isolation, environment_hash,
        )
    try:
        output = json.loads(output_path.read_text(encoding="utf-8"))
        canonical_json(output)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return SandboxResult(
            False, None, proc.returncode, stdout, f"invalid JSON output: {exc}", False,
            "invalid_output", isolation, environment_hash,
        )
    if spec.output_schema:
        error = _schema_error(output, spec.output_schema)
        if error:
            return SandboxResult(
                False, None, proc.returncode, stdout, f"output schema violation: {error}", False,
                "schema_violation", isolation, environment_hash,
            )
    return SandboxResult(True, output, proc.returncode, stdout, stderr, False, "", isolation, environment_hash)


class RestrictedPythonExecutor:
    """Execute a capability-free Python subset in a constrained child process.

    This language restriction is defense in depth for local/CI finite checks. It
    is not a kernel, VM, or container security boundary.
    """

    policy = "restricted-python-subprocess"
    security_boundary = "language-restriction"
    isolation = "restricted-python-process"
    __slots__ = ("_python_executable", "_python_identity")
    _python_executable: str
    _python_identity: Mapping[str, Any]

    def __init__(self, python_executable: str | Path | None = None):
        candidate = Path(python_executable) if python_executable is not None else Path(sys.executable)
        if not candidate.is_absolute():
            raise ValueError("Python executable must be an absolute path")
        try:
            resolved = candidate.resolve(strict=True)
            info = resolved.stat()
        except OSError as exc:
            raise ValueError(f"Python executable is unavailable: {candidate}") from exc
        if not stat.S_ISREG(info.st_mode) or not os.access(resolved, os.X_OK):
            raise ValueError("Python executable must be a regular executable file")
        identity = _probe_python(resolved)
        frozen_identity = dict(identity)
        frozen_identity["version"] = tuple(frozen_identity["version"])
        object.__setattr__(self, "_python_executable", str(resolved))
        object.__setattr__(self, "_python_identity", MappingProxyType(frozen_identity))

    @property
    def python_executable(self) -> str:
        return self._python_executable

    @property
    def python_identity(self) -> Mapping[str, Any]:
        return self._python_identity

    def __setattr__(self, name: str, value: Any) -> None:
        del name, value
        raise AttributeError("validated executor configuration is immutable")

    def run(self, spec: ExperimentSpec, code: str) -> SandboxResult:
        environment_hash = _environment_hash(
            isolation=self.isolation,
            executable=self.python_executable,
            runtime_identity=self.python_identity,
        )
        policy_error = _validate_restricted_policy(spec)
        if policy_error:
            return SandboxResult(
                False, None, -1, "", policy_error, False, "policy_violation",
                self.isolation, environment_hash,
            )
        try:
            _validate_code(spec, code)
        except CodePolicyError as exc:
            return SandboxResult(
                False, None, -1, "", str(exc), False, "policy_violation",
                self.isolation, environment_hash,
            )

        with tempfile.TemporaryDirectory(prefix="egmra-restricted-") as work:
            work_path = Path(work)
            try:
                inputs_path, code_path, output_path, runner_path = _write_job_files(
                    work_path, spec, code
                )
            except (CodePolicyError, OSError, ValueError) as exc:
                return SandboxResult(
                    False, None, -1, "", str(exc), False, "policy_violation",
                    self.isolation, environment_hash,
                )
            stdout_path = work_path / "stdout.log"
            stderr_path = work_path / "stderr.log"
            env = _base_environment(
                spec, inputs=inputs_path, code=code_path, output=output_path
            )
            with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
                try:
                    proc = subprocess.Popen(
                        [self.python_executable, "-I", str(runner_path)],
                        stdin=subprocess.DEVNULL,
                        stdout=stdout_handle,
                        stderr=stderr_handle,
                        env=env,
                        cwd=work,
                        close_fds=True,
                        start_new_session=True,
                    )
                except OSError as exc:
                    return SandboxResult(
                        False, None, -1, "", f"executor unavailable: {exc}", False,
                        "sandbox_unavailable", self.isolation, environment_hash,
                    )
                timed_out, log_exceeded, memory_exceeded = _wait_with_limits(
                    proc,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    log_limit=spec.max_log_bytes,
                    wall_seconds=spec.wall_seconds,
                    memory_bytes=spec.memory_bytes,
                )
            return _finalize_result(
                spec=spec,
                proc=proc,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                output_path=output_path,
                timed_out=timed_out,
                log_exceeded=log_exceeded,
                memory_exceeded=memory_exceeded,
                isolation=self.isolation,
                environment_hash=environment_hash,
            )


# Compatibility import for the original public API.  The object itself is
# honestly named and labeled, so production state never records "sandbox" for
# this language-restricted executor.
SubprocessSandbox = RestrictedPythonExecutor


_IMAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/:@+-]{0,254}$")


class ContainerSandbox:
    """Run a restricted experiment inside a hardened Docker/Podman container."""

    policy = "container"
    security_boundary = "oci"
    isolation = "oci-container"
    __slots__ = ("_image", "_runtime", "_python_command")
    _image: str
    _runtime: str
    _python_command: str

    def __init__(self, image: str, *, runtime: str = "docker", python_command: str = "python3"):
        if not _IMAGE_RE.fullmatch(image) or image.startswith("-"):
            raise ValueError("container image must be a non-option OCI image reference")
        if not runtime or any(char.isspace() for char in runtime):
            raise ValueError("container runtime must be a command name or absolute path")
        if python_command not in {"python", "python3"}:
            raise ValueError("container python command must be python or python3")
        object.__setattr__(self, "_image", image)
        object.__setattr__(self, "_runtime", runtime)
        object.__setattr__(self, "_python_command", python_command)

    @property
    def image(self) -> str:
        return self._image

    @property
    def runtime(self) -> str:
        return self._runtime

    @property
    def python_command(self) -> str:
        return self._python_command

    def __setattr__(self, name: str, value: Any) -> None:
        del name, value
        raise AttributeError("validated container configuration is immutable")

    def run(self, spec: ExperimentSpec, code: str) -> SandboxResult:
        unavailable_hash = _environment_hash(
            isolation=self.isolation, executable=self.runtime, image_id="unavailable"
        )
        runtime_path = shutil.which(self.runtime)
        if runtime_path is None:
            return SandboxResult(
                False, None, -1, "", f"OCI runtime unavailable: {self.runtime}", False,
                "sandbox_unavailable", self.isolation, unavailable_hash,
            )
        if spec.sandbox_policy != "container" or spec.network != "off":
            return SandboxResult(
                False, None, -1, "", "container policy requires sandbox_policy=container and network=off",
                False, "policy_violation", self.isolation, unavailable_hash,
            )
        try:
            _validate_code(spec, code)
        except CodePolicyError as exc:
            return SandboxResult(
                False, None, -1, "", str(exc), False, "policy_violation",
                self.isolation, unavailable_hash,
            )

        try:
            inspected = subprocess.run(
                [runtime_path, "image", "inspect", "--format", "{{.Id}}", self.image],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=min(spec.wall_seconds, 15.0),
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/local/bin"},
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return SandboxResult(
                False, None, -1, "", f"OCI runtime unavailable: {exc}", False,
                "sandbox_unavailable", self.isolation, unavailable_hash,
            )
        if inspected.returncode != 0 or not inspected.stdout.strip():
            return SandboxResult(
                False, None, inspected.returncode, inspected.stdout,
                "OCI image unavailable locally; pulling is disabled", False,
                "sandbox_unavailable", self.isolation, unavailable_hash,
            )
        image_id = inspected.stdout.strip()
        environment_hash = _environment_hash(
            isolation=self.isolation, executable=str(Path(runtime_path).resolve()), image_id=image_id
        )

        with tempfile.TemporaryDirectory(prefix="egmra-oci-") as work:
            work_path = Path(work)
            job_path = work_path / "job"
            output_dir = work_path / "output"
            job_path.mkdir(mode=0o700)
            output_dir.mkdir(mode=0o733)
            inputs_path, code_path, output_path, runner_path = _write_job_files(job_path, spec, code)
            container_output = output_dir / "output.json"
            stdout_path = work_path / "stdout.log"
            stderr_path = work_path / "stderr.log"
            container_name = f"egmra-{uuid.uuid4().hex}"
            env = _base_environment(
                spec,
                inputs=Path("/job/inputs.json"),
                code=Path("/job/code.py"),
                output=Path("/output/output.json"),
            )
            command = [
                runtime_path,
                "run",
                "--rm",
                "--pull=never",
                "--name",
                container_name,
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--user=65534:65534",
                f"--pids-limit={spec.max_processes}",
                f"--memory={spec.memory_bytes}",
                f"--memory-swap={spec.memory_bytes}",
                "--cpus=1.0",
                f"--ulimit=cpu={spec.cpu_seconds}:{spec.cpu_seconds}",
                "--ulimit=nofile=16:16",
                f"--tmpfs=/tmp:rw,noexec,nosuid,nodev,size={min(spec.memory_bytes // 4, 64 * 1024**2)}",
                "--workdir=/tmp",
                "--entrypoint",
                self.python_command,
                "--volume",
                f"{job_path}:/job:ro",
                "--volume",
                f"{output_dir}:/output:rw",
            ]
            for key, value in env.items():
                command.extend(("--env", f"{key}={value}"))
            # Execute the immutable ID that was inspected and fingerprinted,
            # not a mutable tag that could be retargeted between inspect/run.
            command.extend((image_id, "-I", "/job/runner.py"))
            with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
                try:
                    proc = subprocess.Popen(
                        command,
                        stdin=subprocess.DEVNULL,
                        stdout=stdout_handle,
                        stderr=stderr_handle,
                        env={"PATH": "/usr/bin:/bin:/usr/local/bin"},
                        cwd=work,
                        close_fds=True,
                        start_new_session=True,
                    )
                except OSError as exc:
                    return SandboxResult(
                        False, None, -1, "", f"OCI runtime unavailable: {exc}", False,
                        "sandbox_unavailable", self.isolation, environment_hash,
                    )
                timed_out, log_exceeded, memory_exceeded = _wait_with_limits(
                    proc,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    log_limit=spec.max_log_bytes,
                    wall_seconds=spec.wall_seconds,
                )
                if timed_out or log_exceeded:
                    subprocess.run(
                        [runtime_path, "rm", "-f", container_name],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=10,
                        check=False,
                        env={"PATH": "/usr/bin:/bin:/usr/local/bin"},
                    )
            return _finalize_result(
                spec=spec,
                proc=proc,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                output_path=container_output,
                timed_out=timed_out,
                log_exceeded=log_exceeded,
                memory_exceeded=memory_exceeded,
                isolation=self.isolation,
                environment_hash=environment_hash,
            )

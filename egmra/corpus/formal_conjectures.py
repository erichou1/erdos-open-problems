"""Community-reviewed formal targets from the formal-conjectures repository (R5).

496 Erdős problems have human-reviewed Lean 4 statements in
``google-deepmind/formal-conjectures``.  Adopting one as the *intended formal
obligation* removes the largest semantic-risk surface in a formal run: trusting
a fresh model translation of the informal statement (compilation ≠ faithfulness;
see the pipeline gap analysis §3.4).

Trust model — deliberately narrow:

* the fetched Lean source is **prompt context and an obligation pin only**.  It
  is never truth authority (the community statement can itself be wrong), never
  a proof, and never bypasses the formal-correspondence review: a kernel-checked
  declaration still needs an independently signed
  :class:`~egmra.truth.entities.FormalCorrespondenceCertificate` before it can
  support the informal claim;
* fetches are HTTPS-only from ``raw.githubusercontent.com``, size-capped, and
  content-hashed.  Pin ``ref`` to an immutable tag (the repository publishes
  ``bench-v{N}-lean4.{X}.{Y}`` snapshot tags) for anything release-adjacent;
  ``main`` is mutable and therefore recorded as non-reproducible.
"""

from __future__ import annotations

import hashlib
import re
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlsplit

FORMAL_CONJECTURES_HOST = "raw.githubusercontent.com"
FORMAL_CONJECTURES_URL = (
    "https://raw.githubusercontent.com/google-deepmind/formal-conjectures/"
    "{ref}/FormalConjectures/ErdosProblems/{number}.lean"
)
DEFAULT_REF = "main"
_MAX_SOURCE_BYTES = 1_000_000
_FETCH_TIMEOUT_S = 30.0
_DECLARATION_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:noncomputable\s+)?"
    r"(?:theorem|lemma|def|abbrev)\s+([A-Za-z_][A-Za-z0-9_.']*)",
    re.MULTILINE,
)


class FormalConjectureUnavailable(RuntimeError):
    """The community formal statement could not be fetched or parsed."""


@dataclass(frozen=True)
class FormalConjectureTarget:
    """One fetched community Lean statement with provenance."""

    problem: int
    ref: str
    url: str
    lean_source: str
    sha256: str
    declaration_names: tuple[str, ...] = field(default_factory=tuple)

    @property
    def reproducible_ref(self) -> bool:
        """A mutable branch ref cannot pin the obligation for release use."""
        return self.ref not in {"main", "master", "HEAD"}

    def to_dict(self) -> dict:
        return {
            "problem": self.problem,
            "ref": self.ref,
            "url": self.url,
            "sha256": self.sha256,
            "declaration_names": list(self.declaration_names),
            "reproducible_ref": self.reproducible_ref,
            "source_bytes": len(self.lean_source.encode("utf-8")),
            "trust_note": (
                "prompt context and obligation pin only; never truth authority "
                "and never a substitute for the formal-correspondence review"
            ),
        }


def parse_declarations(lean_source: str) -> tuple[str, ...]:
    """Extract top-level declaration names (theorem/lemma/def/abbrev)."""
    return tuple(dict.fromkeys(_DECLARATION_RE.findall(lean_source)))


def _default_fetcher(url: str) -> bytes:  # pragma: no cover - live network path
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != FORMAL_CONJECTURES_HOST \
            or parsed.username is not None or parsed.password is not None:
        raise FormalConjectureUnavailable(
            f"refusing to fetch outside https://{FORMAL_CONJECTURES_HOST}"
        )
    request = urllib.request.Request(
        url, headers={"User-Agent": "egmra-formal-target/1.0"})
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT_S) as response:
        return response.read(_MAX_SOURCE_BYTES + 1)


def fetch_formal_conjecture(
    number: int, *, ref: str = DEFAULT_REF, fetcher=None,
) -> FormalConjectureTarget:
    """Fetch and parse the community Lean statement for Erdős problem ``number``.

    ``fetcher(url) -> bytes`` is injectable for hermetic tests; the default
    performs the allowlisted live fetch.
    """
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("problem number must be a positive integer")
    ref = str(ref).strip()
    if not re.fullmatch(r"[A-Za-z0-9._\-/]+", ref):
        raise ValueError("ref must be a plain git ref (tag, branch, or commit)")
    url = FORMAL_CONJECTURES_URL.format(ref=ref, number=number)
    fetch = fetcher or _default_fetcher
    try:
        raw = fetch(url)
    except FormalConjectureUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 - normalize transport failures
        raise FormalConjectureUnavailable(
            f"formal-conjectures fetch failed for problem {number}@{ref}: {exc}"
        ) from exc
    if not isinstance(raw, (bytes, bytearray)):
        raise FormalConjectureUnavailable("fetcher must return bytes")
    if len(raw) > _MAX_SOURCE_BYTES:
        raise FormalConjectureUnavailable("formal statement exceeds the size cap")
    try:
        source = bytes(raw).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FormalConjectureUnavailable("formal statement is not UTF-8") from exc
    if not source.strip():
        raise FormalConjectureUnavailable("formal statement is empty")
    declarations = parse_declarations(source)
    if not declarations:
        raise FormalConjectureUnavailable(
            "no theorem/def declaration found in the fetched Lean source"
        )
    return FormalConjectureTarget(
        problem=number,
        ref=ref,
        url=url,
        lean_source=source,
        sha256=hashlib.sha256(bytes(raw)).hexdigest(),
        declaration_names=declarations,
    )

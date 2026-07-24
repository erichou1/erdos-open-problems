#!/usr/bin/env python3
"""Offline literature / related-work grounding from the local Erdős corpus.

Real proofs are cumulative: they invoke known theorems and build on adjacent
results. The solver runs closed-book by policy, so on its own it can only recall
related work from parametric memory (and must re-derive it). This module gives
the search stages an *offline, first-party* grounding step: for a target
problem it finds the most related problems in the local corpus and extracts the
known results/bounds/conjectures stated in their write-ups, using three
signals already present in the repository:

  * shared topic tags        (problem_catalog.json -> problems[N].tags)
  * shared citations         (\\cite{...} keys in individual/problem_N.tex)
  * statement term overlap   (TF-IDF cosine over the .tex write-ups)

The result is rendered as an explicitly UNTRUSTED block. It is a recall aid,
never authority: the solver must still state and verify the exact hypotheses of
any theorem it uses, the adversarial reviewers and the Lean kernel still
gatekeep, and runs that used it are flagged rediscovery-eligible so the
"verified novel solution" lane stays honest. No network access.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_CITE_RE = re.compile(r"\\cite[a-zA-Z]*\{([^}]*)\}")
_COMMENT_RE = re.compile(r"(?<!\\)%.*")
_RESULT_RE = re.compile(
    r"\\leq|\\geq|\\ll|\\gg|\bprov(?:ed|es|en)\b|\bconjectur|\btheorem\b"
    r"|\bshow(?:ed|s|n)?\b|\bbound(?:s|ed)?\b|\bknown\b|\\cite",
    re.IGNORECASE,
)
_STOPWORDS = frozenset("""
a an the of to in and or is are for that this with we it as be on by if then
there exists every all any some such which whose let define given where when
from into over under has have had not no yes but also more most than then thus
hence so we our can may must will shall would could each both between among
problem erdos erdős source status open tags prize updated last document
""".split())


# ── low-level tex helpers ─────────────────────────────────────────────────────

def _tex_path(root: Path, n: int) -> Path:
    return Path(root) / "individual" / f"problem_{n}.tex"


def _read_tex(root: Path, n: int) -> str:
    try:
        return _tex_path(root, n).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def citations(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in _CITE_RE.finditer(tex):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def _strip_preamble(tex: str) -> str:
    for marker in (r"\maketitle", r"\begin{document}"):
        idx = tex.find(marker)
        if idx >= 0:
            return tex[idx + len(marker):].replace(r"\end{document}", " ")
    return tex


def display_text(tex: str) -> str:
    """A human-readable-ish rendering that keeps math but drops LaTeX chrome."""
    text = _COMMENT_RE.sub(" ", tex)
    text = _strip_preamble(text)
    text = re.sub(r"\\(?:title|author|date|section\*?|subsection\*?)\{([^}]*)\}",
                  r" \1 ", text)
    text = re.sub(r"\\(?:textbf|emph|textit|texttt|mathrm|mathbf|textrm)\{([^}]*)\}",
                  r"\1", text)
    text = re.sub(r"\\url\{[^}]*\}", " ", text)
    text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)
    # Formatting commands that may be glued directly to following text
    # (e.g. "\noindentStatus"); qquad before quad so it is not left as "\q".
    text = re.sub(r"\\(?:noindent|maketitle|centering|newpage|qquad|quad|medskip"
                  r"|bigskip|smallskip|small|footnotesize|large|Large)", " ", text)
    text = re.sub(r"\\(?:par|newline|label|ref|eqref)\b", " ", text)
    text = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_headers(text: str) -> str:
    text = re.sub(r"Erd\\?[HŐő].*?erdosproblems\.com", " ", text)
    text = re.sub(r"(?i)\b(status:|no prize|prize:|tags:)[^.]*", " ", text)
    text = re.sub(r"(?i)last updated:[^.]*", " ", text)
    text = re.sub(r"^[\s.,;:]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z]{4,}", text.lower()) if w not in _STOPWORDS]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]


def _statement_snippet(tex: str, limit: int = 280) -> str:
    body = _strip_headers(display_text(tex))
    return body[:limit].rstrip() + ("…" if len(body) > limit else "")


def _result_sentences(tex: str, limit: int, sentence_cap: int = 260) -> tuple[str, ...]:
    out: list[str] = []
    for sentence in _sentences(_strip_headers(display_text(tex))):
        if _RESULT_RE.search(sentence):
            out.append(sentence[:sentence_cap].rstrip()
                       + ("…" if len(sentence) > sentence_cap else ""))
        if len(out) >= limit:
            break
    return tuple(out)


# ── data model ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RelatedProblem:
    number: int
    score: float
    shared_tags: tuple[str, ...]
    shared_citations: tuple[str, ...]
    statement: str
    results: tuple[str, ...]


@dataclass(frozen=True)
class LiteratureContext:
    problem_number: int
    related: tuple[RelatedProblem, ...]
    references: tuple[str, ...]
    rendered: str
    sha256: str

    def is_empty(self) -> bool:
        return not self.related

    def grounding_record(self) -> dict:
        return {
            "enabled": not self.is_empty(),
            "source": "local_corpus",
            "rediscovery_eligible": not self.is_empty(),
            "sha256": self.sha256,
            "related_problems": [r.number for r in self.related],
            "references": list(self.references),
        }


# ── corpus loading + scoring ─────────────────────────────────────────────────

def _load_tags(root: Path) -> dict[int, set[str]]:
    try:
        catalog = json.loads((Path(root) / "problem_catalog.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out: dict[int, set[str]] = {}
    for key, value in catalog.get("problems", {}).items():
        try:
            number = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict) and isinstance(value.get("tags"), list):
            out[number] = {str(t).strip().lower() for t in value["tags"] if str(t).strip()}
    return out


def _corpus_texts(root: Path) -> dict[int, str]:
    texts: dict[int, str] = {}
    for path in (Path(root) / "individual").glob("problem_*.tex"):
        match = re.fullmatch(r"problem_(\d+)", path.stem)
        if not match:
            continue
        try:
            texts[int(match.group(1))] = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return texts


def _tfidf(toks: list[str], df: Counter, num_docs: int) -> dict[str, float]:
    if not toks:
        return {}
    counts = Counter(toks)
    length = len(toks)
    return {
        word: (count / length) * math.log(num_docs / (1 + df[word]))
        for word, count in counts.items()
    }


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    dot = sum(value * b.get(word, 0.0) for word, value in a.items())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _render(problem_number: int, related: list[RelatedProblem],
            references: tuple[str, ...]) -> str:
    if not related:
        return ""
    lines = [
        f"Related prior work located in the local Erdős corpus for problem "
        f"#{problem_number}. This is UNTRUSTED recall material: it is not part "
        f"of the locked problem and is never authority. Use it only to suggest "
        f"attacks and to recall theorems you then state and verify exactly.",
        "",
    ]
    for item in related:
        tag_bit = f" shared tags: {', '.join(item.shared_tags)};" if item.shared_tags else ""
        cite_bit = (f" shared refs: {', '.join(item.shared_citations)};"
                    if item.shared_citations else "")
        lines.append(f"- Erdős #{item.number} (relevance {item.score:.2f};{tag_bit}{cite_bit})")
        if item.statement:
            lines.append(f"    statement: {item.statement}")
        for result in item.results:
            lines.append(f"    known result: {result}")
    if references:
        lines.append("")
        lines.append(
            "Citation keys referenced by these related problems (recall the exact "
            "theorem behind each and verify its hypotheses before any use): "
            + ", ".join(references)
        )
    return "\n".join(lines)


def research_literature(
    root: Path, problem_number: int, *,
    max_related: int = 6, max_results_each: int = 3, max_refs: int = 15,
    min_cosine: float = 0.05,
) -> LiteratureContext:
    """Find related corpus problems + their known results for a target problem."""
    root = Path(root)
    target_tex = _read_tex(root, problem_number)
    if not target_tex.strip():
        return LiteratureContext(problem_number, (), (), "", "")

    tags = _load_tags(root)
    target_tags = tags.get(problem_number, set())
    target_cites = citations(target_tex)

    texts = _corpus_texts(root)
    texts.pop(problem_number, None)
    if not texts:
        return LiteratureContext(problem_number, (), (), "", "")

    doc_tokens = {n: tokens(display_text(t)) for n, t in texts.items()}
    target_tokens = tokens(display_text(target_tex))
    df: Counter = Counter()
    for toks in doc_tokens.values():
        df.update(set(toks))
    df.update(set(target_tokens))
    num_docs = len(doc_tokens) + 1
    target_vector = _tfidf(target_tokens, df, num_docs)

    scored: list[RelatedProblem] = []
    for number, tex in texts.items():
        candidate_cites = citations(tex)
        candidate_tags = tags.get(number, set())
        shared_tags = target_tags & candidate_tags
        shared_cites = target_cites & candidate_cites
        cosine = _cosine(target_vector, _tfidf(doc_tokens[number], df, num_docs))
        score = (0.40 * _jaccard(target_tags, candidate_tags)
                 + 0.35 * _jaccard(target_cites, candidate_cites)
                 + 0.25 * cosine)
        if score <= 0 or not (shared_tags or shared_cites or cosine >= min_cosine):
            continue
        scored.append(RelatedProblem(
            number=number, score=round(score, 3),
            shared_tags=tuple(sorted(shared_tags)),
            shared_citations=tuple(sorted(shared_cites)),
            statement=_statement_snippet(tex),
            results=_result_sentences(tex, max_results_each),
        ))

    scored.sort(key=lambda r: (-r.score, r.number))
    related = scored[:max_related]

    references: set[str] = set()
    for item in related:
        references |= citations(_read_tex(root, item.number))
    ordered_refs = tuple(sorted(references or target_cites))[:max_refs]

    rendered = _render(problem_number, related, ordered_refs)
    sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest() if rendered else ""
    return LiteratureContext(problem_number, tuple(related), ordered_refs, rendered, sha)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem_number", type=int)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--max-related", type=int, default=6)
    args = parser.parse_args()
    context = research_literature(args.root, args.problem_number,
                                  max_related=args.max_related)
    print(context.rendered or "(no related corpus work found)")
    print("\n---\nprovenance:", json.dumps(context.grounding_record(), indent=2))


if __name__ == "__main__":
    main()

"""Five-gate rendering (spec §11.5 final paragraph).

The communication layer renders the five-gate profile and fixed vocabulary; it
never compresses the profile into a self-reported "confidence 95%".
"""

from __future__ import annotations

from egmra.release.certificate import ReleaseCertificate
from egmra.truth.events import EventLog

_FORBIDDEN_TERMS = ("confidence", "% sure", "probability of correctness")


def render_certificate(
    certificate: ReleaseCertificate, *, env: dict[str, str] | None = None,
    now: float | None = None, max_age_s: float = 900.0,
    event_log: EventLog | None = None,
) -> dict:
    rendered = certificate.render(
        env=env, now=now, max_age_s=max_age_s, event_log=event_log
    )
    _assert_no_confidence(rendered)
    return rendered


def render_human_summary(
    certificate: ReleaseCertificate, *, env: dict[str, str] | None = None,
    now: float | None = None, max_age_s: float = 900.0,
    event_log: EventLog | None = None,
) -> str:
    # Direct/human rendering is a release entry point too.  Validate the same
    # signature, gate attestation, promotion authorization, and freshness first.
    certificate.render(
        env=env, now=now, max_age_s=max_age_s, event_log=event_log
    )
    gates = certificate.gates.profile()
    lines = [
        f"Result: {certificate.gates.summary_label()}",
        f"  truth={gates['truth']}  intent={gates['intent']}  "
        f"formal={gates['formal_correspondence']}",
        f"  novelty={gates['novelty']}  significance={gates['significance']}  "
        f"reproducibility={gates['reproducibility']}",
    ]
    if certificate.unresolved_risks:
        lines.append("  unresolved risks: " + "; ".join(certificate.unresolved_risks))
    text = "\n".join(lines)
    _assert_no_confidence({"text": text})
    return text


def _assert_no_confidence(payload: dict) -> None:
    blob = str(payload).lower()
    for term in _FORBIDDEN_TERMS:
        if term in blob:
            raise ValueError(f"rendering must not collapse gates into '{term}'")

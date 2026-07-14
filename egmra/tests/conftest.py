"""Security configuration shared by EGMRA tests.

Production code deliberately has no public fallback signing keys.  Tests use
explicit, process-local keys so they exercise the authenticated paths without
weakening runtime defaults.
"""

from __future__ import annotations

import pytest


TEST_KEYS = {
    "EGMRA_EVENT_KEY": "event-test-key-that-is-at-least-32-bytes",
    "EGMRA_POLICY_KEY": "policy-test-key-that-is-at-least-32-bytes",
    "EGMRA_EVIDENCE_KEY": "evidence-test-key-that-is-at-least-32-bytes",
    "EGMRA_RELEASE_KEY": "release-test-key-that-is-at-least-32-bytes",
    "EGMRA_GATE_KEY": "gate-test-key-that-is-at-least-32-bytes",
    "EGMRA_PROMOTION_KEY": "promotion-test-key-that-is-at-least-32-bytes",
    "EGMRA_LEAN_CHECKER_KEY": "lean-checker-test-key-that-is-at-least-32-bytes",
    "EGMRA_AUTHORITY_KEY": "authority-test-key-that-is-at-least-32-bytes",
    "EGMRA_TRUTH_SNAPSHOT_KEY": "truth-snapshot-test-key-that-is-at-least-32-bytes",
    "EGMRA_CHECKPOINT_KEY": "checkpoint-test-key-that-is-at-least-32-bytes",
    "EGMRA_MODEL_ATTESTATION_KEY": "model-attestation-test-key-at-least-32-bytes",
    "EGMRA_INTENT_REVIEW_KEY": "intent-review-test-key-that-is-at-least-32-bytes",
    "EGMRA_FORMAL_CORRESPONDENCE_KEY": (
        "formal-correspondence-test-key-that-is-at-least-32-bytes"
    ),
    "EGMRA_LEGACY_REVIEW_KEY": "legacy-review-test-key-that-is-at-least-32-bytes",
    "EGMRA_LEGACY_EVIDENCE_KEY": "legacy-evidence-test-key-that-is-at-least-32-bytes",
}


@pytest.fixture(autouse=True)
def _authenticated_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in TEST_KEYS.items():
        monkeypatch.setenv(name, value)

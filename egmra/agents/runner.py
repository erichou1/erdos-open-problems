"""Model-runner protocol and attested identity (spec §6.5, §14.2).

Workers call models through a ``ModelRunner`` that always returns an attested (or
explicitly unattested) model identity alongside the response, so downstream
independence claims are honest. ``DeterministicRunner`` lets tests exercise the
orchestration without any provider credentials; real providers plug in behind the
same protocol (see DECISIONS.md D-004).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity, attest_model_identity


@dataclass(frozen=True)
class RunnerResponse:
    text: str
    model: AttestedModelIdentity
    context_id: str
    prompt_hash: str


class ModelRunner(Protocol):
    runner_id: str

    def run(self, prompt: str, *, stage: str) -> RunnerResponse: ...


@dataclass
class DeterministicRunner:
    """A seeded, credential-free runner for tests and offline orchestration.

    Its identity is *unattested* (a local label), so it can never count as
    independent-model evidence — exactly the honest behavior the spec requires.
    """

    runner_id: str = "deterministic-local"
    responses: dict[str, str] = field(default_factory=dict)
    calls: list[dict] = field(default_factory=list)

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        prompt_hash = sha256_hex(prompt)
        text = self.responses.get(stage, f"[deterministic:{stage}] {prompt[:64]}")
        self.calls.append({"stage": stage, "prompt_hash": prompt_hash})
        return RunnerResponse(
            text=text,
            model=AttestedModelIdentity(
                provider="local", model=self.runner_id,
                ui_surface="test", account_class="local",
            ),
            context_id=sha256_hex(f"{self.runner_id}:{stage}:{prompt_hash}"),
            prompt_hash=prompt_hash,
        )


@dataclass
class AttestedRunner:
    """Adapter for a real provider that attests model/version/build ids.

    ``call`` performs the network request and MUST return
    ``(text, provider, model, version, build_id)``. Without a configured call it
    raises rather than fabricating a response (spec: no silent mock).
    """

    runner_id: str
    provider: str
    ui_surface: str = "api"
    account_class: str = "standard"
    call: Callable[..., tuple[str, str, str, str]] | None = None

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:  # pragma: no cover - needs provider
        if self.call is None:
            raise RuntimeError(
                f"AttestedRunner '{self.runner_id}' has no provider call configured; "
                "configure real credentials or use DeterministicRunner for local runs"
            )
        text, model, version, build_id = self.call(prompt=prompt, stage=stage)
        prompt_hash = sha256_hex(prompt)
        return RunnerResponse(
            text=text,
            model=attest_model_identity(
                provider=self.provider, model=model, version=version, build_id=build_id,
                ui_surface=self.ui_surface, account_class=self.account_class,
            ),
            context_id=sha256_hex(f"{self.runner_id}:{stage}:{prompt_hash}:{build_id}"),
            prompt_hash=prompt_hash,
        )

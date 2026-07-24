"""Attested API model runners (OpenAI-compatible + Anthropic).

The browser provider is *unattested* by design (a UI label can never prove
which model produced text), which caps hostile-review independence at a single
collapsed lineage.  API providers are different: the provider's response body
echoes an immutable model/version identifier and a request id, which is
exactly what :func:`attest_model_identity` requires.  Two hostile reviewers
driven by two *different* attested providers therefore carry genuinely
distinct lineages — the missing trust primitive for a live T3.

Honesty and security invariants:

* the API key is read from the environment only and never logged;
* requests are HTTPS-only to a pinned per-provider host, without redirects;
* responses are size-capped and strictly parsed — a malformed response raises
  instead of degrading to fabricated text;
* the attestation binds the *response's* model string (e.g.
  ``gpt-4o-2024-11-20``), not the caller's requested alias.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from egmra.agents.runner import AttestedRunner

_MAX_RESPONSE_BYTES = 4_000_000
_TIMEOUT_SECONDS = 180.0

#: Transport signature: (url, headers, payload_dict) -> parsed JSON dict.
Transport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


class ApiProviderError(RuntimeError):
    """The provider is unreachable, rejected the request, or replied malformed."""


@dataclass(frozen=True)
class ApiProviderSpec:
    provider: str            # lineage label, e.g. "openai"
    host: str                # pinned HTTPS host
    path: str                # request path
    api_key_env: str         # environment variable holding the key
    default_model: str
    model_env: str           # optional override env var
    style: str               # "openai" | "anthropic"


PROVIDERS: dict[str, ApiProviderSpec] = {
    "openai-api": ApiProviderSpec(
        provider="openai", host="api.openai.com", path="/v1/chat/completions",
        api_key_env="OPENAI_API_KEY", default_model="gpt-4o",
        model_env="OPENAI_MODEL", style="openai"),
    "deepseek-api": ApiProviderSpec(
        provider="deepseek", host="api.deepseek.com", path="/chat/completions",
        api_key_env="DEEPSEEK_API_KEY", default_model="deepseek-reasoner",
        model_env="DEEPSEEK_MODEL", style="openai"),
    "anthropic-api": ApiProviderSpec(
        provider="anthropic", host="api.anthropic.com", path="/v1/messages",
        api_key_env="ANTHROPIC_API_KEY", default_model="claude-sonnet-4-5",
        model_env="ANTHROPIC_MODEL", style="anthropic"),
}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        raise ApiProviderError(f"provider redirected the request ({code}); refusing")


def _default_transport(url: str, headers: dict[str, str],
                       payload: dict[str, Any]) -> dict[str, Any]:
    if not url.startswith("https://"):
        raise ApiProviderError("provider requests must use https")
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"}, method="POST")
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=_TIMEOUT_SECONDS) as response:
            body = response.read(_MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read(400).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - diagnostics only
            pass
        raise ApiProviderError(f"provider returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise ApiProviderError(f"provider unreachable: {exc}") from exc
    if len(body) > _MAX_RESPONSE_BYTES:
        raise ApiProviderError("provider response exceeds the size cap")
    try:
        document = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApiProviderError(f"provider response is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ApiProviderError("provider response is not a JSON object")
    return document


def _parse_openai(document: dict[str, Any]) -> tuple[str, str, str]:
    choices = document.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ApiProviderError("openai-style response has no choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise ApiProviderError("openai-style response has no message content")
    model = str(document.get("model") or "")
    request_id = str(document.get("id") or "")
    if not model:
        raise ApiProviderError("openai-style response carries no model identifier")
    return text, model, request_id


def _parse_anthropic(document: dict[str, Any]) -> tuple[str, str, str]:
    content = document.get("content")
    if not isinstance(content, list) or not content:
        raise ApiProviderError("anthropic response has no content blocks")
    parts = [
        block.get("text") for block in content
        if isinstance(block, dict) and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    text = "\n".join(part for part in parts if part)
    if not text.strip():
        raise ApiProviderError("anthropic response has no text content")
    model = str(document.get("model") or "")
    request_id = str(document.get("id") or "")
    if not model:
        raise ApiProviderError("anthropic response carries no model identifier")
    return text, model, request_id


def build_api_call(spec: ApiProviderSpec, *, transport: Transport | None = None,
                   env: dict[str, str] | None = None) -> Callable[..., tuple[str, str, str, str]]:
    """Return an :class:`AttestedRunner`-compatible ``call``.

    The returned callable performs one provider request per invocation and
    returns ``(text, model, version, build_id)`` where ``model``/``version``
    come from the provider's response body (immutable identifiers), never
    from the caller's alias.
    """
    source = os.environ if env is None else env
    api_key = source.get(spec.api_key_env, "").strip()
    if not api_key:
        raise ApiProviderError(
            f"{spec.api_key_env} is not configured; export it to use this provider")
    requested_model = source.get(spec.model_env, "").strip() or spec.default_model
    send = transport or _default_transport
    url = f"https://{spec.host}{spec.path}"

    def call(*, prompt: str, stage: str) -> tuple[str, str, str, str]:
        if spec.style == "anthropic":
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
            payload: dict[str, Any] = {
                "model": requested_model,
                "max_tokens": 8192,
                "messages": [{"role": "user", "content": prompt}],
            }
            document = send(url, headers, payload)
            text, model, request_id = _parse_anthropic(document)
        else:
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": requested_model,
                "messages": [{"role": "user", "content": prompt}],
            }
            document = send(url, headers, payload)
            text, model, request_id = _parse_openai(document)
        # version = the provider-echoed immutable model string; build_id = the
        # provider request id (unique per response).
        return text, model, model, request_id or f"{spec.provider}:{stage}"

    return call


def build_api_runner(provider_key: str, *, transport: Transport | None = None,
                     env: dict[str, str] | None = None) -> AttestedRunner:
    """Build an attested runner for a registered API provider."""
    spec = PROVIDERS.get(provider_key)
    if spec is None:
        raise ApiProviderError(
            f"unknown API provider {provider_key!r}; "
            f"choose from {sorted(PROVIDERS)}")
    return AttestedRunner(
        runner_id=f"{provider_key}-runner",
        provider=spec.provider,
        ui_surface="api",
        call=build_api_call(spec, transport=transport, env=env),
    )

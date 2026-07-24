"""Agents plane (Module E): 7 authorities, method profiles, prompts, runners."""

from egmra.agents.authorities import (
    AUTHORITIES,
    AUTHORITY_PERMISSIONS,
    Authority,
    AuthorityError,
    AuthorityToken,
    AuthorityTokenIssuer,
    authority,
    is_forbidden,
)
from egmra.agents.profiles import (
    DIVERSITY_AXES,
    DiversityAudit,
    MethodProfile,
    differing_axes,
    is_genuinely_diverse,
)
from egmra.agents.prompts import ROLE_PROMPTS, role_prompt, role_prompt_hash
from egmra.agents.browser_runner import (
    BROWSER_RUNNER_VERSION,
    BrowserBackend,
    BrowserChatGPTRunner,
    BrowserProviderUnavailable,
    BrowserResponseError,
    BrowserRunnerError,
    BrowserTranscript,
    PlaywrightChatGPTBackend,
)
from egmra.agents.runner import (
    AttestedRunner,
    DeterministicRunner,
    ModelRunner,
    RunnerResponse,
)
from egmra.agents.throttle import SharedThrottle

__all__ = [
    "AUTHORITIES", "AUTHORITY_PERMISSIONS", "Authority", "AuthorityError",
    "AuthorityToken", "AuthorityTokenIssuer", "authority", "is_forbidden",
    "DIVERSITY_AXES", "DiversityAudit", "MethodProfile", "differing_axes",
    "is_genuinely_diverse",
    "ROLE_PROMPTS", "role_prompt", "role_prompt_hash",
    "AttestedRunner", "DeterministicRunner", "ModelRunner", "RunnerResponse",
    "BROWSER_RUNNER_VERSION", "BrowserBackend", "BrowserChatGPTRunner",
    "BrowserProviderUnavailable", "BrowserResponseError", "BrowserRunnerError",
    "BrowserTranscript", "PlaywrightChatGPTBackend", "SharedThrottle",
]

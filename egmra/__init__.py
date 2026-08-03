"""EGMRA — Evidence-Gated Mathematical Research Architecture.

A hierarchical, event-sourced, neuro-symbolic research operating system with
five independent release gates (statement fidelity, truth, novelty,
significance, reproducibility), implementing
``docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md``.

The package is organized by the four planes of the specification:

* ``egmra.truth``   — interpretations, claims, evidence, dependencies, revocation
* ``egmra.search``  — programs, blueprints, experiments, proof states
* ``egmra.control`` — leases, throttling, parallelism, recovery, congestion
* ``egmra.comms``   — progress reports, five-gate rendering, human steering

plus supporting subsystems (``intake``, ``retrieval``, ``oeis``, ``compute``,
``lean``, ``agents``, ``verification``, ``release``, ``selection``, ``learning``,
``orchestrator``, ``eval``).
"""

__version__ = "0.1.0"

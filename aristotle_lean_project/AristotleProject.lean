import Mathlib

/-!
Pinned Lean/Mathlib environment for Aristotle (Lean v4.28.0, Mathlib v4.28.0).

Aristotle writes candidate proofs into this project; EGMRA then re-checks them
locally with its pinned kernel (`egmra.lean.replay.LeanReplayVerifier`) before
anything is trusted. A vendor "COMPLETE" is never a proof on its own.

A trivial theorem so `lake build` succeeds on a fresh checkout.
-/

theorem egmra_project_builds : True := trivial

"""Orchestrator: main research loop, checkpoint/resume, runtime roles."""

from egmra.orchestrator.checkpoint import Checkpoint, ResumeReport, resume, take_checkpoint
from egmra.orchestrator.campaign import Assignment, Campaign, CampaignError
from egmra.orchestrator.loop import (
    AttackEvaluator,
    BudgetLedger,
    DeterministicWorker,
    MechanicalAttackEvaluator,
    ResearchResult,
    Worker,
    WorkerOutput,
    research,
)
from egmra.orchestrator.roles import RUNTIME_ROLES, SERVICES, RoleLayout
from egmra.orchestrator.result_states import (
    ResultClassification,
    ResultState,
    classify_result,
)
from egmra.orchestrator.runner_worker import (
    RunnerWorker,
    StructuredDemoRunner,
    WorkerResponseSchemaError,
    parse_worker_response,
)

__all__ = [
    "Checkpoint", "ResumeReport", "resume", "take_checkpoint",
    "Assignment", "Campaign", "CampaignError",
    "AttackEvaluator", "BudgetLedger", "DeterministicWorker", "MechanicalAttackEvaluator",
    "ResearchResult", "Worker", "WorkerOutput", "research",
    "RUNTIME_ROLES", "SERVICES", "RoleLayout",
    "ResultClassification", "ResultState", "classify_result",
    "RunnerWorker", "StructuredDemoRunner", "WorkerResponseSchemaError",
    "parse_worker_response",
]

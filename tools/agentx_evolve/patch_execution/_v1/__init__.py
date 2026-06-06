"""
Legacy v1 governed patch execution implementation.

This package preserves the v1 OOP-based patch execution API
for existing consumers. New code should use
``agentx_evolve.patch_execution`` (v2 functional API) instead.
"""

from .patch_models import (
    PatchSession, PatchAction, RollbackSnapshot,
    ImplementationEvidence, ImplementationSessionStatus,
    ApprovedMutation, MutationAllowlist,
    SESSION_CREATED, SESSION_LOADED, SESSION_PROPOSAL_LOADED,
    SESSION_GOVERNANCE_CHECKED, SESSION_PATCH_APPLIED,
    SESSION_VALIDATED, SESSION_ACCEPTED, SESSION_ROLLED_BACK,
    SESSION_FAILED, SESSION_BLOCKED,
    ACTION_UPDATE, ACTION_CREATE, ACTION_DELETE,
    utc_now_iso, new_id,
)
from .file_change_guard import FileChangeGuard
from .git_diff_guard import GitDiffGuard
from .implementation_session import ImplementationSession
from .patch_applier import PatchApplier
from .rollback_manager import RollbackManager
from .implementation_validation_gate import ImplementationValidationGate
from .implementation_evidence import ImplementationEvidenceWriter

__all__ = [
    "PatchSession", "PatchAction", "RollbackSnapshot",
    "ImplementationEvidence", "ImplementationSessionStatus",
    "ApprovedMutation", "MutationAllowlist",
    "FileChangeGuard", "GitDiffGuard",
    "ImplementationSession", "PatchApplier",
    "RollbackManager", "ImplementationValidationGate",
    "ImplementationEvidenceWriter",
    "SESSION_CREATED", "SESSION_LOADED", "SESSION_PROPOSAL_LOADED",
    "SESSION_GOVERNANCE_CHECKED", "SESSION_PATCH_APPLIED",
    "SESSION_VALIDATED", "SESSION_ACCEPTED", "SESSION_ROLLED_BACK",
    "SESSION_FAILED", "SESSION_BLOCKED",
    "ACTION_UPDATE", "ACTION_CREATE", "ACTION_DELETE",
    "utc_now_iso", "new_id",
]

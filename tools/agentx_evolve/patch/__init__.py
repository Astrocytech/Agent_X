"""
[DEPRECATED] agentx_evolve.patch — legacy v1 governed patch execution.

This package is the v1 OOP-based patch execution system.
It has been superseded by the v2 system at ``agentx_evolve.patch_execution``
(dataclass + functional API with dry-run/live modes, session locking,
policy bridges, and audit events).

New code should use ``agentx_evolve.patch_execution`` instead.
This package is preserved for existing consumers until all tests
are migrated.
"""
import warnings
warnings.warn(
    "agentx_evolve.patch is deprecated; use agentx_evolve.patch_execution instead",
    DeprecationWarning, stacklevel=2,
)

from .patch_models import (
    PatchSession, PatchAction, RollbackSnapshot,
    ImplementationEvidence, ImplementationSessionStatus,
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
from .implementation_evidence import ImplementationEvidence

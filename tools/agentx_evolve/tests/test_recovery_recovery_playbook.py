import pytest

from agentx_evolve.recovery.recovery_playbook import (
    REQUIRED_RULE_IDS,
    ALL_RECOVERY_ACTIONS,
    FAILURE_TO_RULE_MAP,
    get_recovery_rule_for_failure,
    get_allowed_recovery_actions,
    _get_default_actions_for_rule,
)
from agentx_evolve.recovery.failure_models import (
    ACTION_RETRY, ACTION_REBUILD_CONTEXT, ACTION_ROLLBACK,
    ACTION_BLOCK_SESSION, ACTION_ENTER_SAFE_MODE,
    ACTION_REQUEST_HUMAN_REVIEW, ACTION_REJECT_OUTPUT,
    ACTION_REVALIDATE, ACTION_NO_ACTION,
)


def test_required_rule_ids():
    assert len(REQUIRED_RULE_IDS) == 17
    assert "REC-POL-001-MODEL-INVALID-OUTPUT" in REQUIRED_RULE_IDS
    assert "REC-POL-017-UNKNOWN-FAILURE" in REQUIRED_RULE_IDS


def test_all_recovery_actions():
    assert ACTION_RETRY in ALL_RECOVERY_ACTIONS
    assert ACTION_REBUILD_CONTEXT in ALL_RECOVERY_ACTIONS
    assert ACTION_ROLLBACK in ALL_RECOVERY_ACTIONS
    assert ACTION_BLOCK_SESSION in ALL_RECOVERY_ACTIONS
    assert ACTION_ENTER_SAFE_MODE in ALL_RECOVERY_ACTIONS
    assert ACTION_REQUEST_HUMAN_REVIEW in ALL_RECOVERY_ACTIONS
    assert ACTION_REJECT_OUTPUT in ALL_RECOVERY_ACTIONS
    assert ACTION_REVALIDATE in ALL_RECOVERY_ACTIONS
    assert ACTION_NO_ACTION in ALL_RECOVERY_ACTIONS
    assert len(ALL_RECOVERY_ACTIONS) == 9


def test_failure_to_rule_map_has_all_required():
    known_classes = {
        "MODEL_INVALID_OUTPUT", "MODEL_INSUFFICIENT_CONTEXT",
        "PATCH_APPLY_FAILED", "VALIDATION_FAILED", "GOVERNANCE_BLOCKED",
        "RISK_TOO_HIGH", "SOURCE_GUARD_FAILED", "ROLLBACK_FAILED",
        "SCHEMA_VALIDATION_FAILED", "TOOL_FAILURE", "LOCK_CONFLICT",
        "ATOMIC_WRITE_FAILED", "PROMPT_CONTRACT_FAILED", "POLICY_DENIED",
        "PATH_TRAVERSAL", "PATH_OUTSIDE_REPO", "SYMLINK_ESCAPE",
        "L0_WRITE_BLOCKED", "PROTECTED_PATH_BLOCKED",
        "SECRET_REDACTION_FAILED", "UNKNOWN_FAILURE",
        "CAPABILITY_MISSING", "ROLE_NOT_AUTHORIZED", "TOOL_NOT_ALLOWED",
        "MODEL_NOT_ALLOWED", "PATH_NOT_ALLOWED", "NETWORK_MODE_DENIED",
        "APPROVAL_REQUIRED", "SOURCE_WRITE_DISABLED",
        "RUNTIME_WRITE_BOUNDARY_VIOLATION", "SUBPROCESS_BLOCKED",
        "COMMAND_NOT_ALLOWLISTED", "NETWORK_BLOCKED",
        "UNEXPECTED_FILE_MUTATION", "IMPLEMENTATION_SESSION_FAILED",
    }
    for fc in known_classes:
        assert fc in FAILURE_TO_RULE_MAP, f"{fc} missing from FAILURE_TO_RULE_MAP"


def test_get_recovery_rule_for_known_failure():
    rule = get_recovery_rule_for_failure("MODEL_INVALID_OUTPUT")
    assert rule["rule_id"] == "REC-POL-001-MODEL-INVALID-OUTPUT"
    assert rule["failure_class"] == "MODEL_INVALID_OUTPUT"
    assert ACTION_REJECT_OUTPUT in rule["actions"]
    assert ACTION_RETRY in rule["actions"]


def test_get_recovery_rule_for_unknown_failure():
    rule = get_recovery_rule_for_failure("BOGUS_CLASS")
    assert rule["rule_id"] == "REC-POL-017-UNKNOWN-FAILURE"
    assert rule["failure_class"] == "BOGUS_CLASS"


def test_get_recovery_rule_for_sandbox_critical():
    rule = get_recovery_rule_for_failure("PATH_TRAVERSAL")
    assert rule["rule_id"] == "REC-POL-015-SANDBOX-CRITICAL"


def test_get_allowed_recovery_actions():
    actions = get_allowed_recovery_actions()
    assert isinstance(actions, set)
    assert actions == ALL_RECOVERY_ACTIONS


def test_get_default_actions_model_invalid_output():
    actions = _get_default_actions_for_rule("REC-POL-001-MODEL-INVALID-OUTPUT")
    assert actions == [ACTION_REJECT_OUTPUT, ACTION_RETRY]


def test_get_default_actions_model_insufficient_context():
    actions = _get_default_actions_for_rule("REC-POL-002-MODEL-INSUFFICIENT-CONTEXT")
    assert actions == [ACTION_REBUILD_CONTEXT]


def test_get_default_actions_patch_apply_failed():
    actions = _get_default_actions_for_rule("REC-POL-003-PATCH-APPLY-FAILED")
    assert ACTION_ROLLBACK in actions
    assert ACTION_BLOCK_SESSION in actions


def test_get_default_actions_policy_denied():
    actions = _get_default_actions_for_rule("REC-POL-014-POLICY-DENIED")
    assert actions == [ACTION_BLOCK_SESSION]


def test_get_default_actions_sandbox_critical():
    actions = _get_default_actions_for_rule("REC-POL-015-SANDBOX-CRITICAL")
    assert ACTION_ENTER_SAFE_MODE in actions
    assert ACTION_REQUEST_HUMAN_REVIEW in actions


def test_get_default_actions_unknown_rule():
    actions = _get_default_actions_for_rule("NONEXISTENT-RULE")
    assert actions == [ACTION_BLOCK_SESSION]

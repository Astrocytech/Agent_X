import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanApprovalScope,
    scope_matches_action,
    validate_scope,
    normalize_scope,
    VALIDATION_VALID,
    VALIDATION_INVALID,
    SCOPE_ACTION,
    SCOPE_TOOL_CALL,
)


class TestHumanApprovalScope:
    def test_scope_matches_action_returns_true_for_matching_action(self):
        scope = HumanApprovalScope(
            scope_id="s-ma-001",
            scope_type=SCOPE_ACTION,
            action_id="apply_patch",
        )
        result = scope_matches_action(scope, "apply_patch", "modify", {})
        assert result is True

    def test_scope_matches_action_returns_false_for_different_action(self):
        scope = HumanApprovalScope(
            scope_id="s-ma-002",
            scope_type=SCOPE_ACTION,
            action_id="apply_patch",
        )
        result = scope_matches_action(scope, "delete_files", "modify", {})
        assert result is False

    def test_scope_matches_action_blocked_effect(self):
        scope = HumanApprovalScope(
            scope_id="s-ma-003",
            scope_type=SCOPE_ACTION,
            blocked_effects=["delete"],
        )
        result = scope_matches_action(scope, "apply_patch", "delete", {})
        assert result is False

    def test_validate_scope_returns_valid_for_valid_scope(self):
        scope = HumanApprovalScope(
            scope_id="s-vs-001",
            scope_type=SCOPE_ACTION,
        )
        result = validate_scope(scope)
        assert result.status == VALIDATION_VALID
        assert result.allowed is True

    def test_validate_scope_returns_invalid_for_empty_scope_id(self):
        scope = HumanApprovalScope(scope_id="", scope_type=SCOPE_ACTION)
        result = validate_scope(scope)
        assert result.status == VALIDATION_INVALID
        assert result.allowed is False

    def test_validate_scope_returns_invalid_for_empty_scope_type(self):
        scope = HumanApprovalScope(scope_id="s-vs-002", scope_type="")
        result = validate_scope(scope)
        assert result.status == VALIDATION_INVALID
        assert result.allowed is False

    def test_normalize_scope_sorts_lists(self):
        scope = HumanApprovalScope(
            scope_id="s-ns-001",
            scope_type=SCOPE_ACTION,
            file_paths=["z.py", "a.py", "m.py"],
            allowed_effects=["write", "read"],
            blocked_effects=["delete"],
        )
        normalized = normalize_scope(scope)
        assert normalized.file_paths == ["a.py", "m.py", "z.py"]
        assert normalized.allowed_effects == ["read", "write"]
        assert normalized.blocked_effects == ["delete"]

    def test_normalize_scope_preserves_scope_id(self):
        scope = HumanApprovalScope(
            scope_id="s-ns-002",
            scope_type=SCOPE_TOOL_CALL,
        )
        normalized = normalize_scope(scope)
        assert normalized.scope_id == "s-ns-002"
        assert normalized.scope_type == SCOPE_TOOL_CALL

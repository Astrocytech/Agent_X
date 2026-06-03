import pytest
from agentx_evolve.recovery.failure_taxonomy import (
    FailureGroup, FG_TRANSIENT, FG_PERMANENT, group_failure,
)


class TestFailureGroupConstants:
    def test_fg_transient_value(self):
        assert FG_TRANSIENT == "TRANSIENT"

    def test_fg_permanent_value(self):
        assert FG_PERMANENT == "PERMANENT"


class TestFailureGroup:
    def test_transient_classification(self):
        assert FailureGroup.classify("MODEL_INVALID_OUTPUT") == FG_TRANSIENT
        assert FailureGroup.classify("TOOL_FAILURE") == FG_TRANSIENT
        assert FailureGroup.classify("LOCK_CONFLICT") == FG_TRANSIENT

    def test_permanent_classification(self):
        assert FailureGroup.classify("ROLLBACK_FAILED") == FG_PERMANENT
        assert FailureGroup.classify("GOVERNANCE_BLOCKED") == FG_PERMANENT
        assert FailureGroup.classify("UNKNOWN_FAILURE") == FG_PERMANENT

    def test_unknown_failure_defaults_permanent(self):
        assert FailureGroup.classify("SOME_UNKNOWN") == FG_PERMANENT

    def test_normalization_handles_case_and_spaces(self):
        assert FailureGroup.classify("model_invalid_output") == FG_TRANSIENT
        assert FailureGroup.classify("  rollback_failed  ") == FG_PERMANENT


class TestGroupFailureFunction:
    def test_group_failure_delegates(self):
        assert group_failure("MODEL_INVALID_OUTPUT") == FG_TRANSIENT
        assert group_failure("ROLLBACK_FAILED") == FG_PERMANENT

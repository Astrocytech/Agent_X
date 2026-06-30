from __future__ import annotations

import pytest
from agentx_evolve.adapters.adapter_failures import (
    FailureClass,
    failure_outcome,
    ADAPTER_FAILURE_CLASSES,
    OUTCOME_BLOCKED,
    OUTCOME_RETRYABLE,
    OUTCOME_DENIED,
    OUTCOME_ESCALATE,
)


class TestFailureTaxonomy:
    def test_timeout_maps_to_retryable(self):
        fc = FailureClass("model_timeout", "timed out")
        assert fc.outcome == OUTCOME_RETRYABLE

    def test_refusal_maps_to_blocked(self):
        fc = FailureClass("model_refusal", "refused")
        assert fc.outcome == OUTCOME_BLOCKED

    def test_schema_error_maps_to_denied(self):
        fc = FailureClass("model_schema_error", "bad schema")
        assert fc.outcome == OUTCOME_DENIED

    def test_tool_denied_maps_to_denied(self):
        assert failure_outcome("tool_denied") == OUTCOME_DENIED

    def test_execution_error_maps_to_blocked(self):
        assert failure_outcome("tool_execution_error") == OUTCOME_BLOCKED

    def test_evidence_error_maps_to_blocked(self):
        assert failure_outcome("evidence_normalization_error") == OUTCOME_BLOCKED

    def test_adapter_not_registered_maps_to_denied(self):
        assert failure_outcome("adapter_not_registered") == OUTCOME_DENIED

    def test_context_contamination_maps_to_escalate(self):
        assert failure_outcome("context_contamination") == OUTCOME_ESCALATE

    def test_prompt_injection_maps_to_escalate(self):
        assert failure_outcome("prompt_injection_detected") == OUTCOME_ESCALATE

    def test_capability_mismatch_maps_to_denied(self):
        assert failure_outcome("capability_mismatch") == OUTCOME_DENIED

    def test_budget_exceeded_maps_to_denied(self):
        assert failure_outcome("budget_exceeded") == OUTCOME_DENIED

    def test_all_failure_classes_have_outcome(self):
        for fc in ADAPTER_FAILURE_CLASSES:
            outcome = failure_outcome(fc)
            assert outcome in (OUTCOME_BLOCKED, OUTCOME_RETRYABLE, OUTCOME_DENIED, OUTCOME_ESCALATE)

    def test_failure_class_to_dict(self):
        fc = FailureClass("model_timeout", "too slow")
        d = fc.to_dict()
        assert d["failure_class"] == "model_timeout"
        assert d["reason"] == "too slow"
        assert d["outcome"] == OUTCOME_RETRYABLE

    def test_unknown_failure_class_raises(self):
        with pytest.raises(ValueError):
            FailureClass("nonexistent")

    def test_no_orphan_outcomes(self):
        known = {OUTCOME_BLOCKED, OUTCOME_RETRYABLE, OUTCOME_DENIED, OUTCOME_ESCALATE}
        for fc in ADAPTER_FAILURE_CLASSES:
            assert failure_outcome(fc) in known

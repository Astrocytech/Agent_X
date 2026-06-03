import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_RUN_ADMISSION_DENIED,
    ORCH_DEPENDENCY_MISSING,
    ORCH_CONTRACT_INCOMPATIBLE,
    ORCH_INVALID_STATE_TRANSITION,
    ORCH_TERMINAL_STATE_IMMUTABLE,
    ORCH_GATE_NOT_CHECKED,
    ORCH_GATE_BLOCKED,
    ORCH_TOOL_BINDING_INVALID,
    ORCH_TOOL_RESULT_MISSING,
    ORCH_MODEL_BINDING_INVALID,
    ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION,
    ORCH_PROMPT_CONTRACT_MISSING,
    ORCH_POLICY_DENIED,
    ORCH_SANDBOX_DENIED,
    ORCH_PATCH_LAYER_DENIED,
    ORCH_HUMAN_APPROVAL_MISSING,
    ORCH_PROMOTION_DENIED,
    ORCH_RETRY_LIMIT_EXCEEDED,
    ORCH_BUDGET_EXCEEDED,
    ORCH_EVIDENCE_MISSING,
    ORCH_EVIDENCE_HASH_MISMATCH,
    ORCH_REPLAY_MISMATCH,
    ORCH_INTERRUPT_REQUESTED,
    ORCH_FAILURE_UNCLASSIFIED,
    ORCH_APPROVED_PLAN_HASH_MISMATCH,
    ORCH_SIDE_EFFECT_MISMATCH,
    ORCH_AUTHORITY_SNAPSHOT_MISSING,
    ORCH_LEDGER_SEQUENCE_INVALID,
    ORCH_EVIDENCE_QUARANTINED,
    ORCH_UNKNOWN_FAILURE,
    ALL_ORCHESTRATOR_FAILURE_CLASSES,
)


def test_orch_run_admission_denied():
    assert ORCH_RUN_ADMISSION_DENIED == "ORCH_RUN_ADMISSION_DENIED"


def test_orch_dependency_missing():
    assert ORCH_DEPENDENCY_MISSING == "ORCH_DEPENDENCY_MISSING"


def test_orch_contract_incompatible():
    assert ORCH_CONTRACT_INCOMPATIBLE == "ORCH_CONTRACT_INCOMPATIBLE"


def test_orch_invalid_state_transition():
    assert ORCH_INVALID_STATE_TRANSITION == "ORCH_INVALID_STATE_TRANSITION"


def test_orch_terminal_state_immutable():
    assert ORCH_TERMINAL_STATE_IMMUTABLE == "ORCH_TERMINAL_STATE_IMMUTABLE"


def test_orch_gate_not_checked():
    assert ORCH_GATE_NOT_CHECKED == "ORCH_GATE_NOT_CHECKED"


def test_orch_gate_blocked():
    assert ORCH_GATE_BLOCKED == "ORCH_GATE_BLOCKED"


def test_orch_tool_binding_invalid():
    assert ORCH_TOOL_BINDING_INVALID == "ORCH_TOOL_BINDING_INVALID"


def test_orch_tool_result_missing():
    assert ORCH_TOOL_RESULT_MISSING == "ORCH_TOOL_RESULT_MISSING"


def test_orch_model_binding_invalid():
    assert ORCH_MODEL_BINDING_INVALID == "ORCH_MODEL_BINDING_INVALID"


def test_orch_model_output_contract_violation():
    assert ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION == "ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION"


def test_orch_prompt_contract_missing():
    assert ORCH_PROMPT_CONTRACT_MISSING == "ORCH_PROMPT_CONTRACT_MISSING"


def test_orch_policy_denied():
    assert ORCH_POLICY_DENIED == "ORCH_POLICY_DENIED"


def test_orch_sandbox_denied():
    assert ORCH_SANDBOX_DENIED == "ORCH_SANDBOX_DENIED"


def test_orch_patch_layer_denied():
    assert ORCH_PATCH_LAYER_DENIED == "ORCH_PATCH_LAYER_DENIED"


def test_orch_human_approval_missing():
    assert ORCH_HUMAN_APPROVAL_MISSING == "ORCH_HUMAN_APPROVAL_MISSING"


def test_orch_promotion_denied():
    assert ORCH_PROMOTION_DENIED == "ORCH_PROMOTION_DENIED"


def test_orch_retry_limit_exceeded():
    assert ORCH_RETRY_LIMIT_EXCEEDED == "ORCH_RETRY_LIMIT_EXCEEDED"


def test_orch_budget_exceeded():
    assert ORCH_BUDGET_EXCEEDED == "ORCH_BUDGET_EXCEEDED"


def test_orch_evidence_missing():
    assert ORCH_EVIDENCE_MISSING == "ORCH_EVIDENCE_MISSING"


def test_orch_evidence_hash_mismatch():
    assert ORCH_EVIDENCE_HASH_MISMATCH == "ORCH_EVIDENCE_HASH_MISMATCH"


def test_orch_replay_mismatch():
    assert ORCH_REPLAY_MISMATCH == "ORCH_REPLAY_MISMATCH"


def test_orch_interrupt_requested():
    assert ORCH_INTERRUPT_REQUESTED == "ORCH_INTERRUPT_REQUESTED"


def test_orch_failure_unclassified():
    assert ORCH_FAILURE_UNCLASSIFIED == "ORCH_FAILURE_UNCLASSIFIED"


def test_orch_approved_plan_hash_mismatch():
    assert ORCH_APPROVED_PLAN_HASH_MISMATCH == "ORCH_APPROVED_PLAN_HASH_MISMATCH"


def test_orch_side_effect_mismatch():
    assert ORCH_SIDE_EFFECT_MISMATCH == "ORCH_SIDE_EFFECT_MISMATCH"


def test_orch_authority_snapshot_missing():
    assert ORCH_AUTHORITY_SNAPSHOT_MISSING == "ORCH_AUTHORITY_SNAPSHOT_MISSING"


def test_orch_ledger_sequence_invalid():
    assert ORCH_LEDGER_SEQUENCE_INVALID == "ORCH_LEDGER_SEQUENCE_INVALID"


def test_orch_evidence_quarantined():
    assert ORCH_EVIDENCE_QUARANTINED == "ORCH_EVIDENCE_QUARANTINED"


def test_orch_unknown_failure():
    assert ORCH_UNKNOWN_FAILURE == "ORCH_UNKNOWN_FAILURE"


def test_all_failure_classes_length():
    assert len(ALL_ORCHESTRATOR_FAILURE_CLASSES) >= 30


def test_all_failure_classes_unique():
    assert len(ALL_ORCHESTRATOR_FAILURE_CLASSES) == len(set(ALL_ORCHESTRATOR_FAILURE_CLASSES))


def test_all_failure_classes_values():
    for fc in ALL_ORCHESTRATOR_FAILURE_CLASSES:
        assert fc.startswith("ORCH_")
        assert isinstance(fc, str)

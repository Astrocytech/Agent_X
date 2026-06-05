#!/usr/bin/env python3
"""Standalone schema validator for all Orchestrator schemas.

Usage:
    python tools/agentx_evolve/tests/validate_orchestrator_schemas.py

Exits with 0 if all schemas pass, 1 otherwise.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Required: pip install jsonschema")
    sys.exit(1)

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

ORCHESTRATOR_SCHEMAS = [
    "orchestration_session.schema.json",
    "orchestration_state.schema.json",
    "orchestration_task.schema.json",
    "orchestration_plan.schema.json",
    "orchestration_step.schema.json",
    "orchestration_step_result.schema.json",
    "orchestration_run_ledger.schema.json",
    "orchestration_tool_binding.schema.json",
    "orchestration_model_binding.schema.json",
    "orchestration_prompt_binding.schema.json",
    "orchestration_policy_decision.schema.json",
    "orchestration_approval_gate.schema.json",
    "orchestration_promotion_gate.schema.json",
    "orchestration_recovery_action.schema.json",
    "orchestration_audit_event.schema.json",
    "orchestration_evidence_manifest.schema.json",
    "orchestration_review_report.schema.json",
    "orchestration_completion_record.schema.json",
    "orchestration_run_lock.schema.json",
    "orchestration_replay_record.schema.json",
    "orchestration_context_package_binding.schema.json",
    "orchestration_command_binding.schema.json",
    "orchestration_mcp_exposure.schema.json",
    "orchestration_dependency_status.schema.json",
    "orchestration_resource_budget.schema.json",
    "orchestration_plan_revision.schema.json",
    "orchestration_stop_event.schema.json",
    "orchestration_session_isolation.schema.json",
    "task_plan.schema.json",
    "execution_step.schema.json",
    "tool_invocation_binding.schema.json",
    "model_invocation_binding.schema.json",
    "prompt_binding.schema.json",
    "approval_gate_record.schema.json",
    "promotion_gate_record.schema.json",
    "recovery_action.schema.json",
    "orchestrator_evidence_event.schema.json",
    "run_ledger.schema.json",
    "orchestrator_evidence_manifest.schema.json",
    "orchestrator_review_report.schema.json",
    "orchestrator_completion_record.schema.json",
    "run_admission.schema.json",
    "orchestrator_failure_class.schema.json",
    "orchestrator_contract_compatibility.schema.json",
    "governance_gate.schema.json",
    "orchestrator_audit.schema.json",
    "tool_call_binding.schema.json",
    "model_call_binding.schema.json",
    "human_approval_binding.schema.json",
    "promotion_gate_binding.schema.json",
    "failure_recovery_binding.schema.json",
    "session_state.schema.json",
]


def valid_instance(schema_name: str) -> dict:
    base = {
        "schema_version": "1.0",
        "schema_id": schema_name,
        "warnings": [],
        "errors": [],
    }
    if schema_name == "orchestration_session.schema.json":
        base.update({
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "requested_task_id": "t-001",
            "requested_task_summary": "test",
            "initiating_role": "dev",
            "orchestration_mode": "EXECUTE_CONTROLLED",
            "state": "CREATED", "session_status": "ACTIVE",
            "idempotency_key": "ik-001",
        })
    elif schema_name == "orchestration_state.schema.json":
        base.update({
            "state_id": "st-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "previous_state": "", "current_state": "CREATED",
            "terminal": False, "reason": "init", "state_version": 1,
            "evidence_refs": [],
        })
    elif schema_name == "orchestration_task.schema.json":
        base.update({
            "task_id": "t-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "title": "test task", "description": "a test",
            "task_type": "IMPLEMENTATION", "risk_level": "low",
            "requested_outputs": [], "constraints": [],
            "allowed_roles": [], "allowed_tools": [],
            "allowed_model_profiles": [],
            "requires_human_approval": False,
            "requires_governance": False,
            "requires_promotion_gate": False,
        })
    elif schema_name == "task_plan.schema.json":
        base.update({
            "plan_id": "plan-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "task_id": "t-001", "plan_status": "PENDING",
            "steps": [], "plan_hash": "abc", "plan_version": 1,
        })
    elif schema_name == "execution_step.schema.json":
        base.update({
            "step_id": "step-001", "plan_id": "plan-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "step_index": 0, "step_name": "test",
            "step_type": "POLICY", "assigned_role": "orchestrator",
            "status": "PENDING",
        })
    elif schema_name == "tool_invocation_binding.schema.json":
        base.update({
            "binding_id": "tb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "tool_name": "source_reader", "caller_role": "tool_agent",
            "requested_effect": "read", "arguments_summary": "{}",
            "dispatch_status": "PENDING", "idempotency_key": "tk-001",
        })
    elif schema_name == "model_invocation_binding.schema.json":
        base.update({
            "binding_id": "mb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "model_profile_id": "default",
            "prompt_contract_version": "1.0",
            "prompt_binding_id": "pb-001", "caller_role": "model_agent",
            "requested_task_type": "impl", "status": "PENDING",
            "idempotency_key": "mk-001",
        })
    elif schema_name == "prompt_binding.schema.json":
        base.update({
            "binding_id": "pb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "prompt_contract_id": "pc-001",
            "prompt_contract_version": "1.0",
            "input_contract_schema_id": "input.json",
            "output_contract_schema_id": "output.json",
        })
    elif schema_name == "approval_gate_record.schema.json":
        base.update({
            "approval_record_id": "ag-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "gate_type": "APPROVAL",
            "reason": "need approval",
            "required_approver_role": "human",
            "approval_status": "PENDING",
        })
    elif schema_name == "promotion_gate_record.schema.json":
        base.update({
            "promotion_record_id": "pg-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "promotion_target": "next_layer",
            "promotion_status": "PENDING",
            "promotion_decision": "", "evidence_refs": [],
        })
    elif schema_name == "recovery_action.schema.json":
        base.update({
            "recovery_action_id": "ra-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "failure_class": "TEST", "failure_severity": "medium",
            "recovery_strategy": "NONE", "action_status": "PENDING",
            "retry_count": 0, "max_retries": 1,
        })
    elif schema_name == "orchestrator_evidence_event.schema.json":
        base.update({
            "event_id": "evt-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "event_type": "TEST", "status": "OK", "message": "test",
            "evidence_refs": [],
        })
    elif schema_name == "run_ledger.schema.json":
        base.update({
            "ledger_id": "ledger-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "final_status": "", "task_id": "t-001",
            "steps_total": 0, "steps_completed": 0, "steps_failed": 0,
            "steps_blocked": 0, "final_decision": "CONTINUE",
            "events": [], "event_count": 0,
        })
    elif schema_name == "orchestrator_evidence_manifest.schema.json":
        base.update({
            "manifest_id": "em-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "validated_commit": "", "evidence_files": [],
            "evidence_file_hashes": {}, "runtime_artifacts": [],
            "source_mutation_status": "NOT_MUTATED",
            "final_decision": "NOT_DONE",
            "evidence_manifest_sha256": "abc",
        })
    elif schema_name == "orchestrator_review_report.schema.json":
        base.update({
            "review_report_id": "rr-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "reviewed_commit": "", "reviewed_at": "now",
            "commands_run": [], "blockers": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "abc",
            "completion_record_sha256": "abc",
            "final_verdict": "NOT_DONE",
            "review_report_sha256": "abc",
        })
    elif schema_name == "orchestrator_completion_record.schema.json":
        base.update({
            "completion_record_id": "cr-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "component_name": "Self-Evolution Orchestrator",
            "status": "DONE", "validated_commit": "",
            "validated_at": "now", "canonical_subdirectories": [],
            "commands_run": [], "evidence_manifest_sha256": "abc",
            "review_report_sha256": "abc",
            "implementation_score": 0.0, "final_decision": "DONE",
            "completion_record_sha256": "abc",
        })
    elif schema_name == "run_admission.schema.json":
        base.update({
            "admission_id": "adm-001", "run_id": "run-001",
            "created_at": "now", "requested_objective": "test",
            "risk_level": "low", "allowed_mode": "EXECUTE_CONTROLLED",
            "decision": "ALLOWED", "evidence_refs": [],
        })
    elif schema_name == "orchestrator_failure_class.schema.json":
        base.update({
            "failure_class": "TEST_FAILURE",
            "description": "a test failure class",
            "severity": "medium",
        })
    elif schema_name == "orchestrator_contract_compatibility.schema.json":
        base.update({
            "compatibility_id": "cc-001", "run_id": "run-001",
            "created_at": "now", "checked_at": "now",
            "layer_contracts": {},
            "compatibility_status": "COMPATIBLE",
        })
    elif schema_name == "governance_gate.schema.json":
        base.update({
            "gate_id": "gg-001", "run_id": "run-001",
            "gate_type": "GOVERNANCE",
            "gate_status": "APPROVED",
            "created_at": "now",
        })
    elif schema_name == "orchestrator_audit.schema.json":
        base.update({
            "audit_id": "aud-001", "run_id": "run-001",
            "event_type": "STATE_TRANSITION",
            "created_at": "now",
        })
    elif schema_name == "orchestration_plan.schema.json":
        base.update({
            "plan_id": "plan-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "task_id": "t-001", "plan_status": "PENDING",
            "steps": [], "plan_hash": "abc", "plan_version": 1,
        })
    elif schema_name == "orchestration_step.schema.json":
        base.update({
            "step_id": "step-001", "plan_id": "plan-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "step_index": 0, "step_name": "test",
            "step_type": "POLICY", "assigned_role": "orchestrator",
            "status": "PENDING",
        })
    elif schema_name == "orchestration_step_result.schema.json":
        base.update({
            "step_result_id": "sr-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "source_component": "SelfEvolutionOrchestrator",
            "result_status": "SUCCESS",
        })
    elif schema_name == "orchestration_run_ledger.schema.json":
        base.update({
            "ledger_id": "ledger-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "final_status": "", "task_id": "t-001",
            "steps_total": 0, "steps_completed": 0, "steps_failed": 0,
            "steps_blocked": 0, "final_decision": "CONTINUE",
            "events": [], "event_count": 0,
        })
    elif schema_name == "orchestration_tool_binding.schema.json":
        base.update({
            "binding_id": "tb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "tool_name": "source_reader", "caller_role": "tool_agent",
            "requested_effect": "read", "arguments_summary": "{}",
            "dispatch_status": "PENDING", "idempotency_key": "tk-001",
        })
    elif schema_name == "orchestration_model_binding.schema.json":
        base.update({
            "binding_id": "mb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "model_profile_id": "default",
            "prompt_contract_version": "1.0",
            "prompt_binding_id": "pb-001", "caller_role": "model_agent",
            "requested_task_type": "impl", "status": "PENDING",
            "idempotency_key": "mk-001",
        })
    elif schema_name == "orchestration_prompt_binding.schema.json":
        base.update({
            "binding_id": "pb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "prompt_contract_id": "pc-001",
            "prompt_contract_version": "1.0",
            "input_contract_schema_id": "input.json",
            "output_contract_schema_id": "output.json",
        })
    elif schema_name == "orchestration_policy_decision.schema.json":
        base.update({
            "gate_id": "pd-001", "run_id": "run-001",
            "gate_type": "GOVERNANCE", "gate_status": "APPROVED",
            "policy_decision": "ALLOW",
            "created_at": "now",
        })
    elif schema_name == "orchestration_approval_gate.schema.json":
        base.update({
            "approval_record_id": "ag-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "gate_type": "APPROVAL",
            "reason": "need approval",
            "required_approver_role": "human",
            "approval_status": "PENDING",
        })
    elif schema_name == "orchestration_promotion_gate.schema.json":
        base.update({
            "promotion_record_id": "pg-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "promotion_target": "next_layer",
            "promotion_status": "PENDING",
            "promotion_decision": "", "evidence_refs": [],
        })
    elif schema_name == "orchestration_recovery_action.schema.json":
        base.update({
            "recovery_action_id": "ra-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "failure_class": "TEST", "failure_severity": "medium",
            "recovery_strategy": "NONE", "action_status": "PENDING",
            "retry_count": 0, "max_retries": 1,
        })
    elif schema_name == "orchestration_audit_event.schema.json":
        base.update({
            "audit_id": "aud-001", "run_id": "run-001",
            "event_type": "STATE_TRANSITION",
            "created_at": "now",
        })
    elif schema_name == "orchestration_evidence_manifest.schema.json":
        base.update({
            "manifest_id": "em-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "validated_commit": "", "evidence_files": [],
            "evidence_file_hashes": {}, "runtime_artifacts": [],
            "source_mutation_status": "NOT_MUTATED",
            "final_decision": "NOT_DONE",
            "evidence_manifest_sha256": "abc",
        })
    elif schema_name == "orchestration_review_report.schema.json":
        base.update({
            "review_report_id": "rr-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "reviewed_commit": "", "reviewed_at": "now",
            "commands_run": [], "blockers": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "abc",
            "completion_record_sha256": "abc",
            "final_verdict": "NOT_DONE",
            "review_report_sha256": "abc",
        })
    elif schema_name == "orchestration_completion_record.schema.json":
        base.update({
            "completion_record_id": "cr-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
            "component_name": "Self-Evolution Orchestrator",
            "status": "DONE", "validated_commit": "",
            "validated_at": "now", "canonical_subdirectories": [],
            "commands_run": [], "evidence_manifest_sha256": "abc",
            "review_report_sha256": "abc",
            "implementation_score": 0.0, "final_decision": "DONE",
            "completion_record_sha256": "abc",
        })
    elif schema_name == "orchestration_run_lock.schema.json":
        base.update({
            "lock_id": "lk-001", "session_id": "sess-001",
            "run_id": "run-001", "acquired_at": "now",
            "lock_type": "SESSION", "lock_holder": "orch",
            "target_scope": "sess-001", "status": "ACTIVE",
        })
    elif schema_name == "orchestration_replay_record.schema.json":
        base.update({
            "replay_id": "rp-001", "session_id": "sess-001",
            "run_id": "run-001", "original_run_id": "orig-001",
            "created_at": "now", "source_component": "SelfEvolutionOrchestrator",
            "replay_status": "PENDING",
        })
    elif schema_name == "orchestration_context_package_binding.schema.json":
        base.update({
            "binding_id": "cb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "source_component": "SelfEvolutionOrchestrator",
            "context_package_id": "ctx-001", "context_package_version": "1.0",
        })
    elif schema_name == "orchestration_command_binding.schema.json":
        base.update({
            "binding_id": "cmd-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "source_component": "SelfEvolutionOrchestrator",
            "command_line": "pytest", "status": "PENDING",
        })
    elif schema_name == "orchestration_mcp_exposure.schema.json":
        base.update({
            "exposure_id": "mcp-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "exposure_status": "INACTIVE",
        })
    elif schema_name == "orchestration_dependency_status.schema.json":
        base.update({
            "dependency_status_id": "ds-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "checked_at": "now", "dependencies": {},
            "source_component": "SelfEvolutionOrchestrator",
        })
    elif schema_name == "orchestration_resource_budget.schema.json":
        base.update({
            "budget_id": "bg-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "max_steps": 100, "max_retries_total": 10,
            "max_retries_per_step": 3, "max_tool_calls": 50,
            "max_model_calls": 20, "max_run_seconds": 3600,
            "max_step_seconds": 600,
            "steps_used": 0, "retries_used": 0,
            "tool_calls_used": 0, "model_calls_used": 0,
            "time_elapsed_seconds": 0.0, "status": "ACTIVE",
        })
    elif schema_name == "orchestration_plan_revision.schema.json":
        base.update({
            "revision_id": "rv-001", "plan_id": "plan-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "source_component": "SelfEvolutionOrchestrator",
            "revision_number": 1, "old_plan_hash": "",
            "new_plan_hash": "abc", "changes": [],
        })
    elif schema_name == "orchestration_stop_event.schema.json":
        base.update({
            "event_id": "se-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "stop_type": "CANCEL", "triggered_by": "human",
            "reason": "manual stop",
        })
    elif schema_name == "orchestration_session_isolation.schema.json":
        base.update({
            "isolation_id": "iso-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "isolation_status": "ISOLATED",
            "artifact_paths": [], "locked_sessions": [],
        })
    elif schema_name == "tool_call_binding.schema.json":
        base.update({
            "binding_id": "tb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "tool_name": "source_reader", "caller_role": "tool_agent",
            "requested_effect": "read", "arguments_summary": "{}",
            "dispatch_status": "PENDING", "idempotency_key": "tk-001",
        })
    elif schema_name == "human_approval_binding.schema.json":
        base.update({
            "approval_record_id": "ag-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "created_at": "now", "gate_type": "APPROVAL",
            "reason": "need approval",
            "required_approver_role": "human",
            "approval_status": "PENDING",
        })
    elif schema_name == "promotion_gate_binding.schema.json":
        base.update({
            "promotion_record_id": "pg-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "promotion_target": "next_layer",
            "promotion_status": "PENDING",
            "promotion_decision": "", "evidence_refs": [],
        })
    elif schema_name == "failure_recovery_binding.schema.json":
        base.update({
            "recovery_action_id": "ra-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now",
            "failure_class": "TEST", "failure_severity": "medium",
            "recovery_strategy": "NONE", "action_status": "PENDING",
            "retry_count": 0, "max_retries": 1,
        })
    elif schema_name == "model_call_binding.schema.json":
        base.update({
            "binding_id": "mb-001", "step_id": "step-001",
            "session_id": "sess-001", "run_id": "run-001",
            "model_profile_id": "default",
            "prompt_contract_version": "1.0",
            "prompt_binding_id": "pb-001", "caller_role": "model_agent",
            "requested_task_type": "impl", "status": "PENDING",
            "idempotency_key": "mk-001",
        })
    elif schema_name == "session_state.schema.json":
        base.update({
            "state_id": "st-001", "session_id": "sess-001",
            "run_id": "run-001", "created_at": "now", "updated_at": "now",
            "source_component": "SelfEvolutionOrchestrator",
            "previous_state": "", "session_state": "CREATED",
            "terminal": False, "reason": "init", "state_version": 1,
            "evidence_refs": [],
        })
    base.setdefault("source_component", "SelfEvolutionOrchestrator")
    return base


def main() -> int:
    errors = []
    tested = 0
    for sname in ORCHESTRATOR_SCHEMAS:
        spath = SCHEMA_DIR / sname
        if not spath.exists():
            errors.append(f"MISSING: {sname}")
            continue
        schema = json.loads(spath.read_text())
        instance = valid_instance(sname)
        try:
            jsonschema.validate(instance, schema)
            tested += 1
        except jsonschema.ValidationError as e:
            errors.append(f"VALIDATION FAIL: {sname} — {e.message}")

    total = len(ORCHESTRATOR_SCHEMAS)
    print(f"Schemas tested: {tested}/{total}")
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All Orchestrator schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

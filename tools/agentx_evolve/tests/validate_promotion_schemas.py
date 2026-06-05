#!/usr/bin/env python3
"""Standalone schema validator for all Promotion schemas.

Usage:
    python tools/agentx_evolve/tests/validate_promotion_schemas.py

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


def _collect_refs(schema: dict, refs: set) -> None:
    for key, val in schema.items():
        if key == "$ref" and isinstance(val, str) and val.startswith("#/definitions/"):
            refs.add(val.split("/")[-1])
        elif isinstance(val, dict):
            _collect_refs(val, refs)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    _collect_refs(item, refs)


def _inject_definitions(schema: dict) -> dict:
    refs: set[str] = set()
    _collect_refs(schema, refs)
    if not refs:
        return schema
    if "definitions" not in schema:
        schema["definitions"] = {}
    for refname in refs:
        if refname not in schema["definitions"]:
            schema["definitions"][refname] = {"type": "object"}
    return schema


SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def valid_instance(schema_name: str) -> dict:
    base = {
        "schema_version": "1.0",
        "schema_id": schema_name,
        "warnings": [],
        "errors": [],
    }
    if schema_name == "promotion_audit.schema.json":
        base.update({
            "audit_id": "aud-001",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "event_type": "GATE_DECISION",
            "event_data": {},
            "actor": "system",
        })
    elif schema_name == "promotion_release_candidate.schema.json":
        base.update({
            "candidate_id": "rc-001",
            "candidate_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "component_name": "Promotion Release Gate",
            "roadmap_layer": "LAYER_3",
            "candidate_type": "IMPLEMENTATION",
            "source_commit": "abc123",
            "changed_files": [],
            "changed_schemas": [],
            "changed_tests": [],
            "required_validations": [],
            "required_approvals": [],
            "required_evidence": [],
            "git_status_summary": {},
        })
    elif schema_name == "promotion_validation_evidence.schema.json":
        base.update({
            "evidence_id": "ev-001",
            "evidence_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "validated_commit": "abc123",
            "validation_started_at": "now",
            "validation_completed_at": "now",
            "commands": [],
            "compileall_status": "NOT_RUN",
            "compileall_exit_code": None,
            "pytest_status": "NOT_RUN",
            "pytest_exit_code": None,
            "schema_validation_status": "NOT_RUN",
            "schema_validation_exit_code": None,
            "source_mutation_status": "NOT_CHECKED",
            "evidence_files": [],
            "evidence_hashes": [],
        })
    elif schema_name == "promotion_git_evidence.schema.json":
        base.update({
            "git_evidence_id": "ge-001",
            "git_evidence_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "working_tree_status": "CLEAN",
            "expected_runtime_artifacts_only": False,
            "changed_files": [],
            "diff_name_only": [],
            "commit_reachable": True,
            "untracked_files": [],
            "forbidden_git_actions_detected": [],
        })
    elif schema_name == "promotion_approval_reference.schema.json":
        base.update({
            "approval_id": "ap-001",
            "approval_hash": "abc",
            "created_at": "now",
            "approved_by": "Alice",
            "approval_type": "HUMAN_REVIEW",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "scope": [],
            "approved_commit": "abc123",
            "source": "test",
        })
    elif schema_name == "promotion_risk_acceptance.schema.json":
        base.update({
            "risk_acceptance_id": "ra-001",
            "risk_acceptance_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "risks": [],
            "accepted_risks": [],
            "blocking_risks": [],
        })
    elif schema_name == "promotion_gate_decision.schema.json":
        base.update({
            "decision_id": "gd-001",
            "gate_decision_hash": "abc",
            "idempotency_key": "ik-001",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision": "BLOCK",
            "status": "BLOCKED",
            "reason": "test",
            "checks_run": [],
            "passed_checks": [],
            "failed_checks": [],
            "blocking_failures": [],
            "required_approvals_status": "NOT_RUN",
            "validation_status": "NOT_RUN",
            "risk_status": "NOT_RUN",
            "policy_status": "NOT_RUN",
            "patch_evidence_status": "NOT_RUN",
            "tool_evidence_status": "NOT_RUN",
            "git_status": "NOT_RUN",
            "expiry_status": "NOT_RUN",
            "dry_run": False,
        })
    elif schema_name == "promotion_gate_policy.schema.json":
        base.update({
            "policy_id": "pol-001",
            "policy_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "source_component": "PromotionReleaseGate",
            "require_clean_git_state": True,
            "validation_freshness_minutes": 1440,
        })
    elif schema_name == "promotion_gate_record.schema.json":
        base.update({
            "promotion_record_id": "rec-001",
            "session_id": "sess-001",
            "run_id": "run-001",
            "created_at": "now",
            "promotion_target": "production",
            "promotion_status": "PENDING",
            "promotion_decision": "PENDING",
            "evidence_refs": [],
        })
    elif schema_name == "promotion_gate_binding.schema.json":
        base.update({
            "promotion_record_id": "bind-001",
            "session_id": "sess-001",
            "run_id": "run-001",
            "created_at": "now",
            "promotion_target": "production",
            "promotion_status": "PENDING",
            "promotion_decision": "PENDING",
            "evidence_refs": [],
        })
    elif schema_name == "promotion_evidence_manifest.schema.json":
        base.update({
            "manifest_id": "man-001",
            "manifest_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "gate_decision_hash": "abc",
            "idempotency_key": "ik-001",
            "runtime_artifact_root": ".agentx-init/promotion/",
            "evidence_files": [],
            "evidence_file_hashes": [],
            "source_mutation_status": "NOT_CHECKED",
            "hash_status": "NOT_RUN",
            "final_decision": "BLOCKED",
        })
    elif schema_name == "promotion_review_report.schema.json":
        base.update({
            "review_report_id": "rr-001",
            "review_report_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "reviewed_commit": "abc123",
            "review_environment": {},
            "commands_run": [],
            "coverage_statuses": {},
            "blockers": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "final_verdict": "NOT_DONE",
        })
    elif schema_name == "promotion_completion_record.schema.json":
        base.update({
            "completion_record_id": "cr-001",
            "completion_record_hash": "abc",
            "created_at": "now",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "component_name": "Promotion Release Gate",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "decision_status": "APPROVED",
            "decision": "PROMOTE",
            "approved_at": "now",
            "basis_documents": [],
            "validated_commands": [],
            "validated_evidence": [],
            "release_scope": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "review_report_path": "",
            "review_report_sha256": "",
            "final_decision": "DONE",
        })
    elif schema_name == "promotion_expiry.schema.json":
        base.update({})
    return base


def check_schema(schema: dict, sname: str, errors: list) -> int:
    tested = 0
    try:
        jsonschema.Draft7Validator.check_schema(schema)
        tested += 1
    except jsonschema.SchemaError as e:
        errors.append(f"SCHEMA ERROR: {sname} — {e.message}")
        return tested

    instance = valid_instance(sname)
    try:
        jsonschema.validate(instance, schema)
        tested += 1
    except jsonschema.ValidationError as e:
        errors.append(f"VALIDATION FAIL: {sname} — {e.message}")
        return tested

    if len(instance) >= 3:
        broken = dict(instance)
        req_keys = schema.get("required", [])
        if req_keys:
            broken.pop(req_keys[0], None)
            try:
                jsonschema.validate(broken, schema)
                errors.append(f"MISSING REQUIRED NOT DETECTED: {sname}")
            except jsonschema.ValidationError:
                tested += 1

    enum_props = []
    for pname, pdef in schema.get("properties", {}).items():
        if "enum" in pdef:
            enum_props.append((pname, pdef["enum"]))
    if enum_props:
        prop_name, valid_vals = enum_props[0]
        bad_instance = dict(instance)
        bad_instance[prop_name] = "__INVALID_ENUM__"
        try:
            jsonschema.validate(bad_instance, schema)
            errors.append(f"INVALID ENUM NOT DETECTED: {sname} ({prop_name})")
        except jsonschema.ValidationError:
            tested += 1

    return tested


def main() -> int:
    errors = []
    tested = 0
    total_tests = 0

    schema_paths = sorted(SCHEMA_DIR.glob("promotion_*.json"))
    if not schema_paths:
        errors.append("No promotion_*.json schemas found")
        print("Schemas tested: 0")
        print("Individual checks passed: 0/0")
        if errors:
            for e in errors:
                print(f"  - {e}")
        return 1

    for spath in schema_paths:
        sname = spath.name
        schema = json.loads(spath.read_text())
        schema = _inject_definitions(schema)
        total_tests += 4
        tested += check_schema(schema, sname, errors)

    total = len(schema_paths)
    print(f"Schemas tested: {total}")
    print(f"Individual checks passed: {tested}/{total_tests}")
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All Promotion schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

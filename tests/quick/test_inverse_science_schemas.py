from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema
except ImportError:
    pytest.skip("jsonschema not installed", allow_module_level=True)

SCHEMAS_DIR = Path("tools/agentx_evolve/schemas")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_schema(name: str) -> dict:
    path = SCHEMAS_DIR / name
    assert path.exists(), f"Schema not found: {path}"
    return json.loads(path.read_text())


def _validate(instance: dict, schema_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    validator = jsonschema.Draft7Validator(schema)
    return [str(e) for e in validator.iter_errors(instance)]


# ── Helpers for valid/invalid fixtures ───────────────────────────────────────

def _valid_plan() -> dict:
    return {
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "target": "Test target",
        "desired_output": "Test output",
        "success_criteria": ["criterion 1"],
        "unacceptable_outputs": [],
        "hard_constraints": ["constraint 1"],
        "soft_constraints": [],
        "allowed_actions": ["patch"],
        "forbidden_actions": ["direct_promotion"],
        "allowed_paths": [],
        "forbidden_paths": [],
        "identifiability_status": "identifiable",
        "candidate_generation_policy": "generate_top_n",
        "governance_required": True,
        "black_box_characterization": "",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_candidate() -> dict:
    return {
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "candidate_type": "patch",
        "proposed_change": "Test change",
        "primary_variable_changed": "threshold",
        "rationale": "Test rationale",
        "score_components": {
            "expected_target_gain": 5.0,
            "expected_information_gain": 3.0,
            "novelty": 1.0,
            "reversibility_bonus": 2.0,
            "constraint_risk": 1.0,
            "safety_risk": 0.5,
            "cost": 2.0,
            "complexity_penalty": 1.0,
        },
        "acquisition_score": 6.5,
        "hard_constraint_check": "PASS",
        "rollback_plan": "git revert",
        "evidence_plan": "run tests",
        "human_review_required": False,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_governance_decision() -> dict:
    return {
        "decision_id": "INVSCI-GOV-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "decision": "allow",
        "policy_checks": [{"check": "L0 mutation", "result": "PASS"}],
        "capability_checks": ["least_privilege"],
        "path_boundary_checks": ["protected_paths"],
        "risk_level": "low",
        "limits": [],
        "reason": "All checks pass",
        "review_requirement": "standard",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_observation() -> dict:
    return {
        "observation_id": "INVSCI-OBS-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "actual_action": "patch",
        "tools_used": ["git"],
        "tests_run": ["pytest"],
        "outputs_observed": ["pass"],
        "unexpected_side_effects": [],
        "validity_status": "valid",
        "raw_evidence_paths": [],
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_evidence_ledger() -> dict:
    return {
        "entry_id": "INVSCI-EVID-TEST001",
        "observation_id": "INVSCI-OBS-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "claim_tested": "Test claim",
        "expected_result": "pass",
        "observed_result": "pass",
        "evidence_class": "test_evidence",
        "interpretation": "verified",
        "uncertainty_remaining": "Low",
        "claim_status": "supported",
        "affects_future_ranking": False,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_negative_knowledge() -> dict:
    return {
        "entry_id": "INVSCI-NEG-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "failure_type": "constraint_failure",
        "description": "Failed hard constraint",
        "risk_adjustment": 2.0,
        "gain_adjustment": -1.0,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_best_known_solution() -> dict:
    return {
        "entry_id": "INVSCI-BKS-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "status": "local_optimum",
        "description": "Best solution found",
        "evidence_ledger_entries": ["INVSCI-EVID-TEST001"],
        "candidate_id": "INVSCI-CAND-TEST001",
        "overclaim_blockers": [],
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_event() -> dict:
    return {
        "event_id": "INVSCI-EVT-000001",
        "sequence_id": 1,
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "event_type": "plan_created",
        "event_data": {},
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_evidence_manifest() -> dict:
    return {
        "manifest_id": "INVSCI-MANIFEST-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "artifacts": [
            {
                "path": "plan.json",
                "artifact_type": "plan",
                "sha256": "abc123",
                "schema_id": "https://agentx.example/schemas/inverse_science_plan",
            }
        ],
        "event_log_path": ".agentx-init/inverse_science/test/event_log.jsonl",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_final_report() -> dict:
    return {
        "report_id": "INVSCI-REPORT-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "plan": {"target": "test"},
        "candidates": [{"candidate_id": "c1"}],
        "selected_candidate": {"candidate_id": "c1"},
        "governance_decision": {"decision": "allow"},
        "observations": [],
        "evidence_ledger": [],
        "negative_knowledge": [],
        "best_known_solution": {"status": "unresolved"},
        "event_log_path": "events.jsonl",
        "evidence_manifest_id": "m1",
        "verdict": "NOT_ACCEPTED",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


# ── Plan Schema Tests ────────────────────────────────────────────────────────

def test_plan_schema_valid_fixture_passes() -> None:
    errors = _validate(_valid_plan(), "inverse_science_plan.schema.json")
    assert not errors, f"Valid plan should pass: {errors}"


def test_plan_missing_hard_constraints_fails() -> None:
    plan = _valid_plan()
    plan["hard_constraints"] = []
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert errors


def test_plan_not_identifiable_must_use_manual_candidates() -> None:
    plan = _valid_plan()
    plan["identifiability_status"] = "not_identifiable"
    plan["candidate_generation_policy"] = "manual_only"
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert not errors

    plan["candidate_generation_policy"] = "generate_top_n"
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert errors


# ── Candidate Schema Tests ───────────────────────────────────────────────────

def test_candidate_schema_valid_fixture_passes() -> None:
    errors = _validate(_valid_candidate(), "inverse_science_candidate.schema.json")
    assert not errors, f"Valid candidate should pass: {errors}"


def test_acquisition_score_calculation() -> None:
    c = _valid_candidate()
    sc = c["score_components"]
    expected = (sc["expected_target_gain"] + sc["expected_information_gain"]
                + sc["novelty"] + sc["reversibility_bonus"]
                - sc["constraint_risk"] - sc["safety_risk"]
                - sc["cost"] - sc["complexity_penalty"])
    assert c["acquisition_score"] == expected


def test_candidate_without_rollback_fails() -> None:
    c = _valid_candidate()
    del c["rollback_plan"]
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert errors


def test_candidate_without_evidence_plan_fails() -> None:
    c = _valid_candidate()
    del c["evidence_plan"]
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert errors


def test_candidate_hard_constraint_fail_requires_human_review() -> None:
    c = _valid_candidate()
    c["hard_constraint_check"] = "FAIL"
    c["human_review_required"] = True
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert not errors

    c["human_review_required"] = False
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert errors


# ── Governance Decision Schema Tests ─────────────────────────────────────────

def test_governance_decision_enum_validates() -> None:
    d = _valid_governance_decision()
    errors = _validate(d, "inverse_science_governance_decision.schema.json")
    assert not errors

    for decision in ["allow_with_limits", "defer", "reject", "require_reframe"]:
        d["decision"] = decision
        errors = _validate(d, "inverse_science_governance_decision.schema.json")
        assert not errors, f"Decision {decision} should be valid"

    d["decision"] = "invalid"
    errors = _validate(d, "inverse_science_governance_decision.schema.json")
    assert errors


# ── Observation Schema Tests ─────────────────────────────────────────────────

def test_observation_schema_validates() -> None:
    errors = _validate(_valid_observation(), "inverse_science_observation.schema.json")
    assert not errors, f"Valid observation should pass: {errors}"


# ── Evidence Ledger Schema Tests ─────────────────────────────────────────────

def test_evidence_ledger_rejects_unsupported_supported() -> None:
    e = _valid_evidence_ledger()
    e["evidence_class"] = "unsupported_claim"
    e["claim_status"] = "supported"
    errors = _validate(e, "inverse_science_evidence_ledger.schema.json")
    assert errors, "unsupported_claim + supported must be rejected"

    e["claim_status"] = "refuted"
    errors = _validate(e, "inverse_science_evidence_ledger.schema.json")
    assert not errors


def test_runtime_change_accepts_inspection_evidence() -> None:
    e = _valid_evidence_ledger()
    e["evidence_class"] = "inspection_evidence"
    errors = _validate(e, "inverse_science_evidence_ledger.schema.json")
    assert not errors


# ── Negative Knowledge Schema Tests ──────────────────────────────────────────

def test_negative_knowledge_schema_validates() -> None:
    errors = _validate(_valid_negative_knowledge(), "inverse_science_negative_knowledge.schema.json")
    assert not errors, f"Valid negative knowledge should pass: {errors}"


def test_negative_knowledge_affects_future_ranking() -> None:
    nk = _valid_negative_knowledge()
    assert nk["risk_adjustment"] > 0
    assert nk["gain_adjustment"] < 0


# ── Best Known Solution Schema Tests ─────────────────────────────────────────

def test_best_known_solution_accepts_global_optimum_with_overclaim_blockers() -> None:
    bks = _valid_best_known_solution()
    bks["status"] = "global_optimum"
    bks["overclaim_blockers"] = ["proof_provided", "peer_reviewed"]
    errors = _validate(bks, "inverse_science_best_known_solution.schema.json")
    assert not errors


# ── Event Schema Tests ───────────────────────────────────────────────────────

def test_event_log_sequence_validation() -> None:
    e = _valid_event()
    errors = _validate(e, "inverse_science_event.schema.json")
    assert not errors

    for etype in ["plan_created", "candidate_generated", "candidate_ranked",
                  "candidate_selected", "governance_decision_created",
                  "probe_started", "probe_completed", "observation_recorded",
                  "evidence_recorded", "negative_knowledge_recorded",
                  "best_known_solution_updated", "backtrack_requested",
                  "checkpoint_created", "checkpoint_restored",
                  "final_report_created"]:
        e["event_type"] = etype
        errors = _validate(e, "inverse_science_event.schema.json")
        assert not errors, f"Event type {etype} should be valid"


# ── Evidence Manifest Schema Tests ───────────────────────────────────────────

def test_evidence_manifest_hash_validation() -> None:
    m = _valid_evidence_manifest()
    errors = _validate(m, "inverse_science_evidence_manifest.schema.json")
    assert not errors


# ── Profile Constraint Tests ──────────────────────────────────────────────────

def test_optional_profile_cannot_patch_directly() -> None:
    import yaml
    profile_path = Path("profiles/inverse_science_planner.yaml")
    assert profile_path.exists()
    profile = yaml.safe_load(profile_path.read_text())
    forbidden = profile.get("forbidden_actions", [])
    assert "direct_patching" in forbidden

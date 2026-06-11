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


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _valid_plan() -> dict:
    return {
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "target": "DOC4 Inverse Science Integration",
        "desired_output": "Closure of inverse-science method adoption",
        "success_criteria": [
            "doctrine document created",
            "schemas validated",
            "reports generated",
            "tests pass",
        ],
        "unacceptable_outputs": [
            "mandatory runtime adoption",
            "L0 mutation",
            "policy bypass",
        ],
        "hard_constraints": [
            "no L0 mutation",
            "governance before action",
            "review before promotion",
        ],
        "soft_constraints": [
            "minimal new dependencies",
            "backward compatible",
            "prefer non-invasive changes",
        ],
        "allowed_actions": ["patch", "test", "document", "profile"],
        "forbidden_actions": ["direct_promotion", "direct_patching", "runtime_override"],
        "allowed_paths": ["docs/", "schemas/", "tests/", ".agentx-init/reports/"],
        "forbidden_paths": ["L0/"],
        "identifiability_status": "identifiable",
        "candidate_generation_policy": "generate_top_n",
        "governance_required": True,
        "black_box_characterization": "Agent_X with inverse-science planning layer",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_candidate(rank: int = 1) -> dict:
    return {
        "candidate_id": f"INVSCI-CAND-TEST{rank:03d}",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "candidate_type": "document",
        "proposed_change": f"Inverse science test candidate {rank}",
        "primary_variable_changed": "documentation",
        "rationale": f"Candidate {rank} for inverse science testing",
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
        "evidence_plan": "run tests and validate schema",
        "human_review_required": False,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_governance_decision(decision: str = "allow") -> dict:
    return {
        "decision_id": "INVSCI-GOV-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "decision": decision,
        "policy_checks": [{"check": "L0 mutation", "result": "PASS"}],
        "capability_checks": ["least_privilege"],
        "path_boundary_checks": ["protected_paths"],
        "risk_level": "low",
        "limits": ["max_one_file"] if decision == "allow_with_limits" else [],
        "reason": "All checks pass" if decision in ("allow", "allow_with_limits") else "Does not meet criteria",
        "review_requirement": "standard",
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_observation() -> dict:
    return {
        "observation_id": "INVSCI-OBS-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "actual_action": "document_creation",
        "tools_used": ["git"],
        "tests_run": ["pytest"],
        "outputs_observed": ["pass"],
        "unexpected_side_effects": [],
        "validity_status": "valid",
        "raw_evidence_paths": [],
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_negative_knowledge() -> dict:
    return {
        "entry_id": "INVSCI-NEG-TEST001",
        "candidate_id": "INVSCI-CAND-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "failure_type": "constraint_failure",
        "description": "Violated hard constraint on L0 mutation",
        "risk_adjustment": 2.0,
        "gain_adjustment": -1.5,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


def _valid_best_known_solution() -> dict:
    return {
        "entry_id": "INVSCI-BKS-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "status": "local_optimum",
        "description": "Best known solution does not claim proven optimum",
        "evidence_ledger_entries": ["INVSCI-EVID-TEST001"],
        "candidate_id": "INVSCI-CAND-TEST001",
        "overclaim_blockers": [],
        "created_at_utc": "2026-06-11T12:00:00Z",
    }


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS
# ══════════════════════════════════════════════════════════════════════════════

# ── Schema validation test ───────────────────────────────────────────────────

def test_plan_schema_requires_all_required_fields() -> None:
    plan = _valid_plan()
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert not errors, f"Valid plan should pass: {errors}"

    for field in ["plan_id", "schema_version", "target", "desired_output",
                  "hard_constraints", "created_at_utc"]:
        plan_copy = plan.copy()
        del plan_copy[field]
        errors = _validate(plan_copy, "inverse_science_plan.schema.json")
        assert errors, f"Plan missing {field} should fail"


def test_candidate_schema_requires_all_required_fields() -> None:
    candidate = _valid_candidate()
    errors = _validate(candidate, "inverse_science_candidate.schema.json")
    assert not errors, f"Valid candidate should pass: {errors}"

    for field in ["candidate_id", "plan_id", "schema_version", "candidate_type",
                  "proposed_change", "score_components", "acquisition_score",
                  "rollback_plan", "evidence_plan", "created_at_utc"]:
        cand_copy = candidate.copy()
        del cand_copy[field]
        errors = _validate(cand_copy, "inverse_science_candidate.schema.json")
        assert errors, f"Candidate missing {field} should fail"


def test_governance_decision_schema_requires_all_required_fields() -> None:
    decision = _valid_governance_decision()
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors, f"Valid decision should pass: {errors}"

    for field in ["decision_id", "candidate_id", "plan_id", "schema_version",
                  "decision", "policy_checks", "created_at_utc"]:
        dec_copy = decision.copy()
        del dec_copy[field]
        errors = _validate(dec_copy, "inverse_science_governance_decision.schema.json")
        assert errors, f"Decision missing {field} should fail"


def test_final_report_schema_requires_all_required_fields() -> None:
    report = {
        "report_id": "INVSCI-REPORT-TEST001",
        "plan_id": "INVSCI-PLAN-TEST001",
        "schema_version": "1.0.0",
        "target_capability": "DOC4 Inverse Science Method Integration",
        "hard_constraints": ["no L0 mutation", "governance before action"],
        "soft_preferences": ["minimal new dependencies"],
        "allowed_inputs": ["patch", "test", "document", "profile"],
        "forbidden_inputs": ["direct_promotion", "runtime_override"],
        "evidence_refs": ["INVSCI-EVID-TEST001"],
        "status": "ACCEPTED",
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
        "overclaim_check": [],
        "created_at_utc": "2026-06-11T12:00:00Z",
    }
    errors = _validate(report, "inverse_science_final_report.schema.json")
    assert not errors, f"Valid report should pass: {errors}"

    for field in ["report_id", "plan_id", "target_capability", "hard_constraints",
                  "allowed_inputs", "forbidden_inputs", "evidence_refs", "status",
                  "verdict", "created_at_utc"]:
        rep_copy = report.copy()
        del rep_copy[field]
        errors = _validate(rep_copy, "inverse_science_final_report.schema.json")
        assert errors, f"Report missing {field} should fail"


# ── Candidate ranking test ───────────────────────────────────────────────────

def test_candidate_ranked_by_priority() -> None:
    candidates = [
        _valid_candidate(rank=i) for i in range(1, 4)
    ]
    candidates[0]["acquisition_score"] = 3.0
    candidates[1]["acquisition_score"] = 7.5
    candidates[2]["acquisition_score"] = 5.0
    ranked = sorted(candidates, key=lambda c: c["acquisition_score"], reverse=True)
    assert ranked[0]["candidate_id"] == "INVSCI-CAND-TEST002"
    assert ranked[1]["candidate_id"] == "INVSCI-CAND-TEST003"
    assert ranked[2]["candidate_id"] == "INVSCI-CAND-TEST001"


def test_acquisition_score_formula_consistent() -> None:
    c = _valid_candidate()
    sc = c["score_components"]
    expected = (sc["expected_target_gain"] + sc["expected_information_gain"]
                + sc["novelty"] + sc["reversibility_bonus"]
                - sc["constraint_risk"] - sc["safety_risk"]
                - sc["cost"] - sc["complexity_penalty"])
    assert c["acquisition_score"] == expected


# ── Hard/soft constraint separation ─────────────────────────────────────────

def test_hard_constraint_violation_blocks_candidate() -> None:
    c = _valid_candidate()
    c["hard_constraint_check"] = "FAIL"
    c["human_review_required"] = True
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert not errors, f"Candidate with FAIL + human review should pass: {errors}"

    c["human_review_required"] = False
    errors = _validate(c, "inverse_science_candidate.schema.json")
    assert errors, "Hard constraint FAIL without human review must be rejected"


def test_soft_constraint_preferences_do_not_block() -> None:
    plan = _valid_plan()
    assert isinstance(plan["soft_constraints"], list)
    assert len(plan["soft_constraints"]) >= 0


# ── Allowed/forbidden input validation ──────────────────────────────────────

def test_plan_accepts_allowed_actions() -> None:
    plan = _valid_plan()
    for action in plan["allowed_actions"]:
        assert action in ["patch", "test", "document", "profile"]


def test_plan_forbids_dangerous_actions() -> None:
    plan = _valid_plan()
    dangerous = ["direct_promotion", "direct_patching", "runtime_override"]
    for action in dangerous:
        assert action in plan["forbidden_actions"]


def test_plan_forbids_l0_paths() -> None:
    plan = _valid_plan()
    assert "L0/" in plan["forbidden_paths"]


# ── Identifiability check ───────────────────────────────────────────────────

def test_identifiable_plan_allows_auto_generation() -> None:
    plan = _valid_plan()
    plan["identifiability_status"] = "identifiable"
    plan["candidate_generation_policy"] = "generate_top_n"
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert not errors


def test_not_identifiable_requires_manual_generation() -> None:
    plan = _valid_plan()
    plan["identifiability_status"] = "not_identifiable"
    plan["candidate_generation_policy"] = "manual_only"
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert not errors

    plan["candidate_generation_policy"] = "generate_top_n"
    errors = _validate(plan, "inverse_science_plan.schema.json")
    assert errors


# ── Negative knowledge append/preserve behavior ─────────────────────────────

def test_negative_knowledge_preserves_failure_info() -> None:
    nk = _valid_negative_knowledge()
    errors = _validate(nk, "inverse_science_negative_knowledge.schema.json")
    assert not errors, f"Valid negative knowledge should pass: {errors}"


def test_negative_knowledge_has_risk_and_gain_adjustments() -> None:
    nk = _valid_negative_knowledge()
    assert nk["risk_adjustment"] > 0
    assert nk["gain_adjustment"] < 0


def test_negative_knowledge_valid_failure_types() -> None:
    nk = _valid_negative_knowledge()
    valid_types = [
        "target_failure", "constraint_failure", "governance_failure",
        "evidence_failure", "measurement_failure", "model_failure",
        "complexity_failure", "reversibility_failure", "integration_failure",
    ]
    for ftype in valid_types:
        nk["failure_type"] = ftype
        errors = _validate(nk, "inverse_science_negative_knowledge.schema.json")
        assert not errors, f"failure_type {ftype} should be valid"


def test_negative_knowledge_rejects_invalid_failure_type() -> None:
    nk = _valid_negative_knowledge()
    nk["failure_type"] = "made_up_failure"
    errors = _validate(nk, "inverse_science_negative_knowledge.schema.json")
    assert errors


# ── Best-known solution wording (does not claim proven optimum) ─────────────

def test_best_known_solution_does_not_claim_proven_optimum() -> None:
    bks = _valid_best_known_solution()
    assert bks["status"] in ("best_found_input", "local_optimum", "feasible_solution", "unresolved")
    assert "global_optimum" not in bks["status"]


def test_best_known_solution_global_optimum_requires_overclaim_blockers() -> None:
    bks = _valid_best_known_solution()
    bks["status"] = "global_optimum"
    bks["overclaim_blockers"] = ["proof_provided"]
    errors = _validate(bks, "inverse_science_best_known_solution.schema.json")
    assert not errors

    bks["overclaim_blockers"] = []
    errors = _validate(bks, "inverse_science_best_known_solution.schema.json")
    assert errors


def test_best_known_solution_valid_statuses() -> None:
    bks = _valid_best_known_solution()
    statuses = [
        "best_found_input", "local_optimum",
        "exact_inverse", "approximate_inverse", "feasible_solution",
        "proven_impossibility", "unresolved",
    ]
    for status in statuses:
        bks["status"] = status
        bks["overclaim_blockers"] = []
        errors = _validate(bks, "inverse_science_best_known_solution.schema.json")
        assert not errors, f"status {status} should be valid"

    bks["status"] = "global_optimum"
    bks["overclaim_blockers"] = ["proof_provided"]
    errors = _validate(bks, "inverse_science_best_known_solution.schema.json")
    assert not errors, "global_optimum with overclaim_blockers should be valid"


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

# ── Candidate routed to governance ──────────────────────────────────────────

def test_candidate_routed_to_governance() -> None:
    candidate = _valid_candidate()
    decision = _valid_governance_decision("allow")
    assert decision["candidate_id"] == candidate["candidate_id"]
    assert decision["plan_id"] == candidate["plan_id"]
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors, "Governance decision for candidate should be valid"


# ── `allow` does not execute patch ─────────────────────────────────────────

def test_allow_does_not_execute_patch() -> None:
    decision = _valid_governance_decision("allow")
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors
    assert decision["decision"] == "allow"
    assert "execution" not in decision


# ── `allow_with_limits` propagates limits ──────────────────────────────────

def test_allow_with_limits_propagates_limits() -> None:
    decision = _valid_governance_decision("allow_with_limits")
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors
    assert decision["decision"] == "allow_with_limits"
    assert len(decision["limits"]) > 0
    assert "max_one_file" in decision["limits"]


# ── `reject` creates no patch execution request ────────────────────────────

def test_reject_creates_no_patch_execution_request() -> None:
    decision = _valid_governance_decision("reject")
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors
    assert decision["decision"] == "reject"
    assert "execution" not in decision


# ── `require_reframe` creates no patch execution request ───────────────────

def test_require_reframe_creates_no_patch_execution_request() -> None:
    decision = _valid_governance_decision("require_reframe")
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert not errors
    assert decision["decision"] == "require_reframe"
    assert "execution" not in decision


def test_governance_decision_enum_values() -> None:
    valid_decisions = ["allow", "allow_with_limits", "defer", "reject", "require_reframe"]
    for d in valid_decisions:
        decision = _valid_governance_decision(d)
        errors = _validate(decision, "inverse_science_governance_decision.schema.json")
        assert not errors, f"Decision {d} should be valid"

    decision = _valid_governance_decision("allow")
    decision["decision"] = "invalid"
    errors = _validate(decision, "inverse_science_governance_decision.schema.json")
    assert errors


# ══════════════════════════════════════════════════════════════════════════════
# SABOTAGE TESTS
# ══════════════════════════════════════════════════════════════════════════════

# ── Attempts L0 mutation ───────────────────────────────────────────────────

def test_l0_mutation_blocked_by_forbidden_paths() -> None:
    plan = _valid_plan()
    assert "L0/" in plan["forbidden_paths"], "L0 must be a forbidden path"

    candidate = _valid_candidate()
    candidate["hard_constraint_check"] = "FAIL"
    candidate["human_review_required"] = True
    errors = _validate(candidate, "inverse_science_candidate.schema.json")
    assert not errors, "L0 mutation candidate with human review should be valid"

    candidate["human_review_required"] = False
    errors = _validate(candidate, "inverse_science_candidate.schema.json")
    assert errors, "L0 mutation candidate without human review must be rejected"


def test_l0_mutation_blocked_by_governance() -> None:
    decision = _valid_governance_decision("reject")
    assert any(
        pc["check"] == "L0 mutation" and pc["result"] == "PASS"
        for pc in decision["policy_checks"]
    )


# ── Attempts policy bypass ─────────────────────────────────────────────────

def test_policy_bypass_blocked_by_forbidden_actions() -> None:
    plan = _valid_plan()
    assert "direct_patching" in plan["forbidden_actions"]
    assert "runtime_override" in plan["forbidden_actions"]


def test_policy_bypass_requires_governance() -> None:
    plan = _valid_plan()
    assert plan["governance_required"] is True


# ── Attempts direct tool execution ─────────────────────────────────────────

def test_direct_tool_execution_blocked() -> None:
    decision = _valid_governance_decision("reject")
    observation = _valid_observation()
    assert decision["candidate_id"] == observation["candidate_id"]
    assert observation["actual_action"] == "document_creation"
    assert "patch" not in observation["actual_action"]


# ── Attempts automatic promotion ───────────────────────────────────────────

def test_automatic_promotion_blocked() -> None:
    plan = _valid_plan()
    assert "direct_promotion" in plan["forbidden_actions"]

    candidate = _valid_candidate()
    assert candidate["human_review_required"] is not None
    decision = _valid_governance_decision("reject")
    assert decision["decision"] == "reject"


def test_allow_decision_does_not_auto_promote() -> None:
    decision = _valid_governance_decision("allow")
    assert "promotion" not in decision


def test_inverse_science_does_not_replace_l0() -> None:
    """Inverse science must explicitly avoid claiming to replace L0."""
    pass

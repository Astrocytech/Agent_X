import pytest

from tools.agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
    CrossLayerCheck, FinalAcceptanceValidationResult, FinalAcceptanceDeviation,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    STATUS_PASS, STATUS_FAIL, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY,
    STATUS_NOT_CHECKED, STATUS_NOT_RUN, STATUS_STALE,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
)


def _item(layer_id: str, path: str = "/tmp/test", exists: bool = True,
          readable: bool = True, required: bool = True) -> FinalAcceptanceEvidenceItem:
    return FinalAcceptanceEvidenceItem(
        layer_id=layer_id, artifact_path=path, artifact_type="test",
        required=required, exists=exists, readable=readable,
    )


def _check(check_id: str, status: str = STATUS_PASS, severity: str = SEVERITY_NON_BLOCKING,
           requirement: str = "test req") -> CrossLayerCheck:
    return CrossLayerCheck(
        check_id=check_id, source_layer="A", target_layer="B",
        requirement=requirement, status=status, severity=severity,
    )


def _validation(command: str = "test", status: str = STATUS_PASS) -> FinalAcceptanceValidationResult:
    return FinalAcceptanceValidationResult(
        command_name=command, command_text=command, status=status,
        exit_code=0 if status == STATUS_PASS else 1,
    )


def _deviation(did: str = "D001", safety: str = "none") -> FinalAcceptanceDeviation:
    return FinalAcceptanceDeviation(
        deviation_id=did, area="test", layer_id="L1", description="test",
        reason="test", safety_impact=safety,
    )


class TestCalculateFinalVerdict:
    def test_all_pass_no_deferrals(self):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            evidence_manifest=manifest,
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_PASS},
        )
        assert verdict == VERDICT_ACCEPTED
        assert rating == 1.0
        assert blockers == []
        assert high == []

    def test_all_pass_with_safe_deferrals(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_DEFERRED_SAFELY},
            safe_deferrals=[{"layer_id": "L2", "reason": "not applicable"}],
        )
        assert verdict == VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS

    def test_blocker_present_returns_not_accepted(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            blockers=["Something is broken"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_high_issues_present_returns_not_accepted(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            high_issues=["Something is concerning"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_layer_fail_creates_blocker(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_FAIL},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("L1" in b for b in blockers)

    def test_layer_stale_creates_blocker(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_STALE},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_cross_layer_blocker_adds_blocker(self):
        checks = [_check("CL-001", status=STATUS_FAIL, severity=SEVERITY_BLOCKER)]
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            cross_layer_checks=checks,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("CL-001" in b for b in blockers)

    def test_cross_layer_high_adds_high_issue(self):
        checks = [_check("CL-002", status=STATUS_FAIL, severity=SEVERITY_HIGH)]
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            cross_layer_checks=checks,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("CL-002" in h for h in high)

    def test_validation_failure_adds_high_issue(self):
        results = [_validation("compileall", status=STATUS_FAIL)]
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            validation_results=results,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("compileall" in h for h in high)

    def test_schema_validation_failure_adds_high_issue(self):
        results = [_validation("schema_check", status=STATUS_FAIL)]
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            schema_validation_results=results,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_critical_deviation_adds_blocker(self):
        devs = [_deviation("D001", safety="critical")]
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            deviations=devs,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("D001" in b for b in blockers)

    def test_evidence_item_unreadable_adds_blocker(self):
        items = [_item("L1", "/tmp/test", exists=True, readable=False, required=True)]
        manifest = FinalAcceptanceEvidenceManifest(items=items)
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            evidence_manifest=manifest,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_implementation_rating_calculation(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_FAIL, "L3": STATUS_PASS},
        )
        assert rating == 2.0 / 3.0

    def test_empty_layer_statuses(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict()
        assert verdict == VERDICT_ACCEPTED
        assert rating == 1.0

    def test_mixed_pass_and_not_applicable(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={
                "L1": STATUS_PASS, "L2": STATUS_NOT_APPLICABLE,
                "L3": STATUS_DEFERRED_SAFELY,
            },
        )
        assert verdict == VERDICT_ACCEPTED
        assert rating == 1.0

    def test_some_not_checked_means_not_all_accepted(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_NOT_CHECKED},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_some_not_run(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_NOT_RUN},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    def test_bootstrap_self_no_effect_on_pass(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            bootstrap_self=True,
        )
        assert verdict == VERDICT_ACCEPTED

    def test_no_safe_deferrals_rejects_deferrals(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_DEFERRED_SAFELY},
            safe_deferrals=[{"layer_id": "L2", "reason": "not applicable"}],
            no_safe_deferrals=True,
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("L2" in b for b in blockers)

    def test_no_safe_deferrals_no_effect_without_deferrals(self):
        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            no_safe_deferrals=True,
        )
        assert verdict == VERDICT_ACCEPTED

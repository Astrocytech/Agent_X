import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.promotion_gate import (
    check_promotion_ready,
    create_promotion_gate_record,
    request_promotion_decision,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    PromotionGateRecord,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
)


class TestCheckPromotionReadyWithManifestAndReport:
    def test_check_promotion_ready_with_manifest_and_report(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
            evidence_manifest_sha256="abc123",
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is True
        assert blockers == []


class TestCheckPromotionReadyBlockedMissingManifest:
    def test_check_promotion_ready_blocked_missing_manifest(self):
        ready, blockers = check_promotion_ready(None, OrchestratorReviewReport(review_report_id="r-1"))
        assert ready is False
        assert any("manifest is missing" in b.lower() for b in blockers)


class TestCheckPromotionReadyBlockedMissingHash:
    def test_check_promotion_ready_blocked_missing_hash(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is False
        assert any("hash" in b.lower() for b in blockers)


class TestCheckPromotionReadyBlockedReportBlockers:
    def test_check_promotion_ready_blocked_report_blockers(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
            evidence_manifest_sha256="abc123",
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
            blockers=["Review found issues", "Quality gate not met"],
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is False
        assert "Review found issues" in blockers
        assert "Quality gate not met" in blockers


class TestCreatePromotionGateRecord:
    def test_create_promotion_gate_record(self):
        record = create_promotion_gate_record("run-1", promotion_target="production")
        assert record.promotion_record_id.startswith("pg-")
        assert record.run_id == "run-1"
        assert record.promotion_target == "production"
        assert record.promotion_status == GATE_STATUS_PENDING


class TestRequestPromotionDecisionWithAdapter:
    def test_request_promotion_decision_with_adapter(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def approve_adapter(**kw):
            return {"decision": GATE_STATUS_APPROVED}

        result = request_promotion_decision(record, approve_adapter)
        assert result.promotion_status == GATE_STATUS_APPROVED
        assert result.promotion_decision == GATE_STATUS_APPROVED

    def test_request_promotion_decision_with_adapter_denies(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def deny_adapter(**kw):
            return {"decision": GATE_STATUS_DENIED, "reason": "not ready"}

        result = request_promotion_decision(record, deny_adapter)
        assert result.promotion_status == GATE_STATUS_DENIED
        assert result.promotion_decision == GATE_STATUS_DENIED
        assert any("not ready" in e for e in result.errors)


class TestRequestPromotionDecisionWithoutAdapterDefaultsApproved:
    def test_request_promotion_decision_without_adapter_defaults_approved(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )
        result = request_promotion_decision(record, None)
        assert result.promotion_status == GATE_STATUS_APPROVED
        assert result.promotion_decision == GATE_STATUS_APPROVED


class TestRequestPromotionDecisionHandlesAdapterError:
    def test_request_promotion_decision_handles_adapter_error(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def broken_adapter(**kw):
            raise Exception("gate crashed")

        result = request_promotion_decision(record, broken_adapter)
        assert result.promotion_status == GATE_STATUS_DENIED
        assert result.promotion_decision == GATE_STATUS_DENIED
        assert any("gate error" in e.lower() for e in result.errors)


from agentx_evolve.promotion.promotion_gate import MvpPromotionGate


class TestMvpPromotionGate:
    def setup_method(self):
        self.gate = MvpPromotionGate()

    def test_promotion_requires_all_checks(self):
        class FakeAction:
            action_id = "act-1"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a2",
            "review_ref": "rev-1", "evidence_refs": [{"path": "/x"}],
            "observation_ref": "obs-1", "gate_result": "ALLOW", "invariant_pass": True,
        })
        assert decision.promoted

    def test_promotion_requires_review_evidence_observation_gate_invariant(self):
        class FakeAction:
            action_id = "act-all"
        full = {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a2",
            "review_ref": "rev-1", "evidence_refs": [{"path": "/x"}],
            "observation_ref": "obs-1", "gate_result": "ALLOW", "invariant_pass": True,
        }
        assert self.gate.evaluate(FakeAction(), full).promoted
        for key in ("review_ref", "evidence_refs", "observation_ref", "gate_result", "invariant_pass"):
            partial = dict(full)
            if key == "evidence_refs":
                partial[key] = []
            elif key in ("review_ref", "observation_ref"):
                partial[key] = ""
            elif key == "gate_result":
                partial[key] = "DENY"
            elif key == "invariant_pass":
                partial[key] = False
            assert not self.gate.evaluate(FakeAction(), partial).promoted, \
                f"Should deny when {key} is missing/invalid"

    def test_self_promotion_denied(self):
        class FakeAction:
            action_id = "act-2"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a1",
        })
        assert not decision.promoted
        assert "self-promotion" in decision.reason.lower()

    def test_self_promotion_denied_with_reason(self):
        class FakeAction:
            action_id = "act-2b"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a1",
        })
        assert not decision.promoted
        assert "self-promotion" in decision.reason.lower()
        assert "denied" in decision.reason.lower()
        assert len(decision.reason) > 10

    def test_self_promotion_decision_is_recorded(self):
        class FakeAction:
            action_id = "act-2c"
        self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a1",
        })
        assert len(self.gate.decisions) == 1
        rec = self.gate.decisions[0]
        assert not rec.promoted

    def test_missing_review_denied(self):
        class FakeAction:
            action_id = "act-3"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a2",
            "review_ref": "", "evidence_refs": [{"path": "/x"}],
            "observation_ref": "obs-1", "gate_result": "ALLOW", "invariant_pass": True,
        })
        assert not decision.promoted
        assert "review" in str(decision.errors).lower()

    def test_missing_evidence_denied(self):
        class FakeAction:
            action_id = "act-4"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a2",
            "review_ref": "rev-1", "evidence_refs": [],
            "observation_ref": "obs-1", "gate_result": "ALLOW", "invariant_pass": True,
        })
        assert not decision.promoted

    def test_invariant_fail_denied(self):
        class FakeAction:
            action_id = "act-5"
        decision = self.gate.evaluate(FakeAction(), {
            "run_id": "r1", "agent_id": "a1", "target_agent": "a2",
            "review_ref": "rev-1", "evidence_refs": [{"path": "/x"}],
            "observation_ref": "obs-1", "gate_result": "ALLOW", "invariant_pass": False,
        })
        assert not decision.promoted

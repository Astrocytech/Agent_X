from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
    FinalAcceptanceEvidenceItem, FinalAcceptanceEvidenceManifest,
    CrossLayerCheck, FinalAcceptanceValidationResult,
    FinalAcceptanceDeviation, FinalAcceptanceArtifactHash,
    FinalAcceptanceModePolicy, FinalAcceptanceReport,
    FinalAcceptanceCompletionRecord,
    STATUS_PASS, STATUS_FAIL, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY,
    STATUS_NOT_CHECKED, STATUS_NOT_RUN, STATUS_STALE, STATUS_PARTIAL,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
)


class TestFinalAcceptanceLayer:
    def test_defaults(self):
        layer = FinalAcceptanceLayer()
        assert layer.layer_id == ""
        assert layer.layer_name == ""
        assert layer.roadmap_number == 0
        assert layer.required_for_acceptance is True
        assert layer.safe_deferral_allowed is False
        assert layer.bootstrap_self_layer is False
        assert layer.acceptance_modes_required == []
        assert layer.deferral_modes_allowed == []

    def test_custom_values(self):
        layer = FinalAcceptanceLayer(
            layer_id="TEST_LAYER",
            layer_name="Test Layer",
            roadmap_number=42,
            required_for_acceptance=False,
            safe_deferral_allowed=True,
            bootstrap_self_layer=True,
            acceptance_modes_required=[MODE_IMPLEMENTATION_ACCEPTANCE],
            deferral_modes_allowed=[MODE_SOURCE_ONLY_ACCEPTANCE],
            expected_evidence_aliases=["alias1"],
            stale_after_days=30,
        )
        assert layer.layer_id == "TEST_LAYER"
        assert layer.roadmap_number == 42
        assert layer.bootstrap_self_layer is True
        assert layer.stale_after_days == 30


class TestFinalAcceptanceLayerRegistry:
    def test_defaults(self):
        reg = FinalAcceptanceLayerRegistry()
        assert reg.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert reg.bootstrap_self is False
        assert reg.layers == []

    def test_custom_registry(self):
        layer = FinalAcceptanceLayer(layer_id="L1")
        reg = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc",
            reviewed_branch="main",
            created_at="2026-01-01T00:00:00Z",
            acceptance_mode=MODE_PRODUCTION_ACCEPTANCE,
            bootstrap_self=True,
            layers=[layer],
        )
        assert reg.reviewed_commit == "abc"
        assert reg.acceptance_mode == MODE_PRODUCTION_ACCEPTANCE
        assert len(reg.layers) == 1


class TestFinalAcceptanceEvidenceItem:
    def test_defaults(self):
        item = FinalAcceptanceEvidenceItem()
        assert item.exists is False
        assert item.readable is False
        assert item.schema_valid is True
        assert item.stale is False

    def test_found_item(self):
        item = FinalAcceptanceEvidenceItem(
            layer_id="L1",
            artifact_path="/tmp/test.json",
            artifact_type="completion_record",
            exists=True,
            readable=True,
            sha256="abc123",
            schema_valid=True,
        )
        assert item.exists is True
        assert item.readable is True
        assert item.sha256 == "abc123"


class TestCrossLayerCheck:
    def test_defaults(self):
        c = CrossLayerCheck()
        assert c.status == STATUS_PASS
        assert c.severity == SEVERITY_NON_BLOCKING

    def test_failed_blocker(self):
        c = CrossLayerCheck(
            check_id="CL-001",
            source_layer="A",
            target_layer="B",
            requirement="Must pass",
            status=STATUS_FAIL,
            severity=SEVERITY_BLOCKER,
            reason="Not satisfied",
        )
        assert c.status == STATUS_FAIL
        assert c.severity == SEVERITY_BLOCKER


class TestFinalAcceptanceReport:
    def test_defaults(self):
        r = FinalAcceptanceReport()
        assert r.final_verdict == VERDICT_NOT_ACCEPTED
        assert r.implementation_rating == 0.0
        assert r.bootstrap_mode_used is False
        assert r.self_hash_mode == "EXCLUDED_FROM_SELF_HASH"

    def test_accepted_report(self):
        r = FinalAcceptanceReport(
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            bootstrap_mode_used=True,
            layer_statuses={"L1": STATUS_PASS},
        )
        assert r.final_verdict == VERDICT_ACCEPTED
        assert r.implementation_rating == 1.0


class TestFinalAcceptanceCompletionRecord:
    def test_defaults(self):
        r = FinalAcceptanceCompletionRecord()
        assert r.status == "VALIDATED"
        assert r.final_verdict == VERDICT_NOT_ACCEPTED
        assert r.bootstrap_mode_used is False

    def test_full_record(self):
        r = FinalAcceptanceCompletionRecord(
            status="COMPLETED",
            reviewed_commit="abc",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.95,
            commands_run=[{"name": "test", "status": "PASS"}],
            artifacts_created=["report.json"],
            accepted_safe_deferrals=[{"layer_id": "L1"}],
            unresolved_blockers=[],
            unresolved_high_issues=[],
        )
        assert r.status == "COMPLETED"
        assert len(r.commands_run) == 1
        assert len(r.artifacts_created) == 1


class TestFinalAcceptanceDeviation:
    def test_defaults(self):
        d = FinalAcceptanceDeviation()
        assert d.safety_impact == "none"

    def test_high_impact(self):
        d = FinalAcceptanceDeviation(
            deviation_id="D001",
            area="security",
            layer_id="SECURITY_SANDBOX",
            description="Test deviation",
            reason="Testing",
            safety_impact="high",
            compensating_control="Manual review",
            accepted_status="DEFERRED_SAFELY",
        )
        assert d.safety_impact == "high"
        assert d.compensating_control == "Manual review"


class TestFinalAcceptanceArtifactHash:
    def test_defaults(self):
        h = FinalAcceptanceArtifactHash()
        assert h.artifact_path == ""
        assert h.sha256 == ""

    def test_hash(self):
        h = FinalAcceptanceArtifactHash(
            artifact_path="/tmp/file.txt",
            sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )
        assert h.artifact_path == "/tmp/file.txt"
        assert len(h.sha256) == 64


class TestFinalAcceptanceModePolicy:
    def test_defaults(self):
        p = FinalAcceptanceModePolicy()
        assert p.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert p.mode_rules == {}

    def test_custom(self):
        p = FinalAcceptanceModePolicy(
            acceptance_mode=MODE_RELEASE_ACCEPTANCE,
            mode_rules={"key": "value"},
        )
        assert p.acceptance_mode == MODE_RELEASE_ACCEPTANCE

from agentx_evolve.final_acceptance.acceptance_models import (
    STATUS_PASS, STATUS_FAIL, STATUS_PARTIAL, STATUS_NOT_CHECKED,
    STATUS_NOT_RUN, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY, STATUS_STALE,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    ALL_STATUSES, ALL_VERDICTS, ALL_SEVERITIES, ALL_MODES,
    VALIDATED_NOT_ACCEPTED,
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceItem,
    FinalAcceptanceEvidenceManifest, CrossLayerCheck, FinalAcceptanceValidationResult,
    FinalAcceptanceDeviation, FinalAcceptanceArtifactHash, FinalAcceptanceModePolicy,
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord,
)


class TestConstants:
    def test_status_values(self):
        assert STATUS_PASS == "PASS"
        assert STATUS_FAIL == "FAIL"
        assert STATUS_PARTIAL == "PARTIAL"
        assert STATUS_NOT_CHECKED == "NOT_CHECKED"
        assert STATUS_NOT_RUN == "NOT_RUN"
        assert STATUS_NOT_APPLICABLE == "NOT_APPLICABLE"
        assert STATUS_DEFERRED_SAFELY == "DEFERRED_SAFELY"
        assert STATUS_STALE == "STALE"

    def test_verdict_values(self):
        assert VERDICT_ACCEPTED == "ACCEPTED"
        assert VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS == "ACCEPTED_WITH_SAFE_DEFERRALS"
        assert VERDICT_NOT_ACCEPTED == "NOT_ACCEPTED"

    def test_severity_values(self):
        assert SEVERITY_BLOCKER == "BLOCKER"
        assert SEVERITY_HIGH == "HIGH"
        assert SEVERITY_NON_BLOCKING == "NON_BLOCKING"

    def test_mode_values(self):
        assert MODE_IMPLEMENTATION_ACCEPTANCE == "IMPLEMENTATION_ACCEPTANCE"
        assert MODE_SOURCE_ONLY_ACCEPTANCE == "SOURCE_ONLY_ACCEPTANCE"
        assert MODE_NON_PRODUCTION_ACCEPTANCE == "NON_PRODUCTION_ACCEPTANCE"
        assert MODE_PRODUCTION_ACCEPTANCE == "PRODUCTION_ACCEPTANCE"
        assert MODE_RELEASE_ACCEPTANCE == "RELEASE_ACCEPTANCE"

    def test_validated_not_accepted(self):
        assert VALIDATED_NOT_ACCEPTED == "VALIDATED_NOT_ACCEPTED"

    def test_all_statuses_frozenset(self):
        assert isinstance(ALL_STATUSES, frozenset)
        assert len(ALL_STATUSES) == 8
        for s in [STATUS_PASS, STATUS_FAIL, STATUS_PARTIAL, STATUS_NOT_CHECKED,
                  STATUS_NOT_RUN, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY, STATUS_STALE]:
            assert s in ALL_STATUSES

    def test_all_verdicts_frozenset(self):
        assert isinstance(ALL_VERDICTS, frozenset)
        assert len(ALL_VERDICTS) == 3
        for v in [VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED]:
            assert v in ALL_VERDICTS

    def test_all_severities_frozenset(self):
        assert isinstance(ALL_SEVERITIES, frozenset)
        assert len(ALL_SEVERITIES) == 3
        for s in [SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING]:
            assert s in ALL_SEVERITIES

    def test_all_modes_frozenset(self):
        assert isinstance(ALL_MODES, frozenset)
        assert len(ALL_MODES) == 5
        for m in [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
                  MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE]:
            assert m in ALL_MODES


class TestFinalAcceptanceLayer:
    def test_defaults(self):
        layer = FinalAcceptanceLayer()
        assert layer.layer_id == ""
        assert layer.layer_name == ""
        assert layer.roadmap_number == 0
        assert layer.required_for_acceptance is True
        assert layer.bootstrap_self_layer is False
        assert layer.stale_after_days is None

    def test_custom_values(self):
        layer = FinalAcceptanceLayer(
            layer_id="TEST_LAYER",
            layer_name="Test Layer",
            roadmap_number=5,
            required_for_acceptance=False,
            stale_after_days=90,
        )
        assert layer.layer_id == "TEST_LAYER"
        assert layer.layer_name == "Test Layer"
        assert layer.roadmap_number == 5
        assert layer.required_for_acceptance is False
        assert layer.stale_after_days == 90

    def test_list_fields_default_to_empty(self):
        layer = FinalAcceptanceLayer()
        assert layer.acceptance_modes_required == []
        assert layer.deferral_modes_allowed == []
        assert layer.expected_evidence_aliases == []
        assert layer.warnings == []
        assert layer.errors == []


class TestFinalAcceptanceLayerRegistry:
    def test_defaults(self):
        reg = FinalAcceptanceLayerRegistry()
        assert reg.layers == []
        assert reg.reviewed_commit is None
        assert reg.reviewed_branch is None
        assert reg.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert reg.bootstrap_self is False

    def test_with_layers(self):
        layer = FinalAcceptanceLayer(layer_id="L1", layer_name="Layer 1")
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[layer])
        assert len(reg.layers) == 1
        assert reg.layers[0].layer_id == "L1"

    def test_with_commit_and_branch(self):
        reg = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc123", reviewed_branch="main",
        )
        assert reg.reviewed_commit == "abc123"
        assert reg.reviewed_branch == "main"


class TestFinalAcceptanceEvidenceItem:
    def test_defaults(self):
        item = FinalAcceptanceEvidenceItem()
        assert item.layer_id == ""
        assert item.exists is False
        assert item.readable is False
        assert item.required is True
        assert item.sha256 is None
        assert item.stale is False

    def test_custom_values(self):
        item = FinalAcceptanceEvidenceItem(
            layer_id="L1", artifact_path="/path/to/artifact",
            exists=True, readable=True, sha256="abcdef",
        )
        assert item.layer_id == "L1"
        assert item.artifact_path == "/path/to/artifact"
        assert item.exists is True
        assert item.readable is True
        assert item.sha256 == "abcdef"


class TestFinalAcceptanceEvidenceManifest:
    def test_defaults(self):
        manifest = FinalAcceptanceEvidenceManifest()
        assert manifest.items == []
        assert manifest.reviewed_commit is None

    def test_with_items(self):
        item = FinalAcceptanceEvidenceItem(layer_id="L1")
        manifest = FinalAcceptanceEvidenceManifest(items=[item])
        assert len(manifest.items) == 1


class TestCrossLayerCheck:
    def test_defaults(self):
        check = CrossLayerCheck()
        assert check.status == STATUS_PASS
        assert check.severity == SEVERITY_NON_BLOCKING

    def test_failed_check(self):
        check = CrossLayerCheck(
            check_id="CL-001", status=STATUS_FAIL, severity=SEVERITY_BLOCKER,
        )
        assert check.status == STATUS_FAIL
        assert check.severity == SEVERITY_BLOCKER


class TestFinalAcceptanceValidationResult:
    def test_defaults(self):
        result = FinalAcceptanceValidationResult()
        assert result.status == STATUS_NOT_RUN
        assert result.exit_code is None

    def test_passed_result(self):
        result = FinalAcceptanceValidationResult(
            command_name="test", status=STATUS_PASS, exit_code=0,
        )
        assert result.command_name == "test"
        assert result.exit_code == 0


class TestFinalAcceptanceDeviation:
    def test_defaults(self):
        dev = FinalAcceptanceDeviation()
        assert dev.deviation_id == ""
        assert dev.safety_impact == "none"

    def test_critical_deviation(self):
        dev = FinalAcceptanceDeviation(
            deviation_id="D001", safety_impact="critical", description="Critical issue",
        )
        assert dev.deviation_id == "D001"
        assert dev.safety_impact == "critical"


class TestFinalAcceptanceArtifactHash:
    def test_defaults(self):
        h = FinalAcceptanceArtifactHash()
        assert h.artifact_path == ""
        assert h.sha256 == ""

    def test_custom(self):
        h = FinalAcceptanceArtifactHash(artifact_path="/a/b.txt", sha256="ff")
        assert h.artifact_path == "/a/b.txt"
        assert h.sha256 == "ff"


class TestFinalAcceptanceModePolicy:
    def test_defaults(self):
        policy = FinalAcceptanceModePolicy()
        assert policy.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert policy.mode_rules == {}


class TestFinalAcceptanceReport:
    def test_defaults(self):
        report = FinalAcceptanceReport()
        assert report.final_verdict == VERDICT_NOT_ACCEPTED
        assert report.layer_statuses == {}
        assert report.blockers == []

    def test_accepted_report(self):
        report = FinalAcceptanceReport(
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
        )
        assert report.final_verdict == VERDICT_ACCEPTED
        assert report.implementation_rating == 1.0


class TestFinalAcceptanceCompletionRecord:
    def test_defaults(self):
        record = FinalAcceptanceCompletionRecord()
        assert record.status == "VALIDATED"
        assert record.final_verdict == VERDICT_NOT_ACCEPTED
        assert record.commands_run == []
        assert record.artifacts_created == []

    def test_not_accepted_record(self):
        record = FinalAcceptanceCompletionRecord(
            status=VALIDATED_NOT_ACCEPTED, final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0, created_at="now",
        )
        assert record.status == VALIDATED_NOT_ACCEPTED
        assert record.final_verdict == VERDICT_NOT_ACCEPTED

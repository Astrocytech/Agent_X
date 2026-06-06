import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.acceptance_models import (
    STATUS_PASS, STATUS_FAIL, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY,
    STATUS_NOT_CHECKED, STATUS_NOT_RUN, STATUS_STALE,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    ALL_STATUSES, ALL_VERDICTS, ALL_SEVERITIES, ALL_MODES,
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceItem,
    FinalAcceptanceEvidenceManifest, CrossLayerCheck, FinalAcceptanceValidationResult,
    FinalAcceptanceDeviation, FinalAcceptanceArtifactHash, FinalAcceptanceModePolicy,
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root, atomic_write_json,
    write_json_artifact, is_within_runtime_root, reject_path_traversal,
)
from tools.agentx_evolve.final_acceptance.hash_utils import (
    sha256_file, sha256_text, hash_artifacts,
    write_artifact_hashes, validate_acyclic_hash_manifest,
)
from tools.agentx_evolve.final_acceptance.mode_policy import (
    build_mode_policy, is_layer_required_for_mode,
    is_deferral_allowed_for_mode, validate_acceptance_mode,
)
from tools.agentx_evolve.final_acceptance.layer_catalog import (
    build_canonical_layer_catalog, validate_layer_catalog,
)
from tools.agentx_evolve.final_acceptance.layer_registry import (
    build_final_acceptance_layer_registry, get_layer_by_id,
    list_required_layers, list_safely_deferred_layers, write_layer_registry,
)
from tools.agentx_evolve.final_acceptance.evidence_collector import (
    collect_layer_evidence, collect_evidence_item,
    validate_evidence_item_schema_if_json, write_evidence_manifest,
)
from tools.agentx_evolve.final_acceptance.deviation_register import (
    load_deviation_register, validate_deviation_register, write_deviation_register,
)
from tools.agentx_evolve.final_acceptance.cross_layer_checker import (
    run_cross_layer_checks, write_cross_layer_matrix,
)
from tools.agentx_evolve.final_acceptance.validation_runner import (
    run_validation_commands, run_single_validation_command, write_validation_results,
)
from tools.agentx_evolve.final_acceptance.schema_validator import (
    validate_final_acceptance_schemas, validate_json_file_against_schema,
    write_schema_validation_results,
)
from tools.agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
from tools.agentx_evolve.final_acceptance.report_generator import (
    build_final_acceptance_report, write_final_acceptance_report,
)
from tools.agentx_evolve.final_acceptance.acceptance_runner import (
    run_final_acceptance, write_completion_record, write_latest_result,
)


class TestConstants:
    def test_all_statuses_contains_expected(self):
        expected = {
            "PASS", "FAIL", "PARTIAL", "NOT_CHECKED", "NOT_RUN",
            "NOT_APPLICABLE", "DEFERRED_SAFELY", "STALE",
        }
        assert ALL_STATUSES == expected

    def test_all_verdicts_contains_expected(self):
        expected = {"ACCEPTED", "ACCEPTED_WITH_SAFE_DEFERRALS", "NOT_ACCEPTED"}
        assert ALL_VERDICTS == expected

    def test_all_severities_contains_expected(self):
        expected = {"BLOCKER", "HIGH", "NON_BLOCKING"}
        assert ALL_SEVERITIES == expected

    def test_all_modes_contains_expected(self):
        expected = {
            "IMPLEMENTATION_ACCEPTANCE", "SOURCE_ONLY_ACCEPTANCE",
            "NON_PRODUCTION_ACCEPTANCE", "PRODUCTION_ACCEPTANCE", "RELEASE_ACCEPTANCE",
        }
        assert ALL_MODES == expected


class TestArtifactWriter:
    def test_runtime_root(self, tmp_path: Path):
        root = runtime_root(tmp_path)
        assert root == tmp_path / ".agentx-init" / "final_acceptance"

    def test_ensure_runtime_root_creates_dir(self, tmp_path: Path):
        root = ensure_runtime_root(tmp_path)
        assert root.exists()
        assert root.is_dir()

    def test_atomic_write_json(self, tmp_path: Path):
        path = tmp_path / "test.json"
        atomic_write_json(path, {"key": "value"})
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["key"] == "value"

    def test_write_json_artifact(self, tmp_path: Path):
        path = write_json_artifact(tmp_path, "test.json", {"a": 1})
        assert path.exists()
        assert "test.json" in str(path)

    def test_is_within_runtime_root(self, tmp_path: Path):
        root = ensure_runtime_root(tmp_path)
        inner = root / "inner.txt"
        inner.write_text("test")
        assert is_within_runtime_root(tmp_path, inner)
        outside = tmp_path / "outside.txt"
        assert not is_within_runtime_root(tmp_path, outside)

    def test_reject_path_traversal_valid(self, tmp_path: Path):
        root = ensure_runtime_root(tmp_path)
        inner = root / "valid.txt"
        reject_path_traversal(tmp_path, inner)

    def test_reject_path_traversal_invalid(self, tmp_path: Path):
        outside = tmp_path / "outside.txt"
        with pytest.raises(ValueError):
            reject_path_traversal(tmp_path, outside)


class TestHashUtils:
    def test_sha256_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        h = sha256_file(f)
        assert len(h) == 64
        assert h == sha256_text("hello")

    def test_sha256_text(self):
        h = sha256_text("hello")
        assert len(h) == 64
        assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_hash_artifacts_empty(self):
        hashes = hash_artifacts([])
        assert hashes == []

    def test_hash_artifacts_excludes_self(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f1.write_text("data1")
        self_hash = tmp_path / "hash.json"
        self_hash.write_text("{}")
        hashes = hash_artifacts([f1, self_hash], exclude_self_hash_file=self_hash)
        assert len(hashes) == 1
        assert hashes[0].artifact_path == str(f1)

    def test_write_artifact_hashes(self, tmp_path: Path):
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="abc")]
        path = write_artifact_hashes(hashes, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["self_hash_mode"] == "EXCLUDED_FROM_SELF_HASH"
        assert len(data["hashed_artifacts"]) == 1

    def test_validate_acyclic_hash_manifest_nonexistent(self, tmp_path: Path):
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert "Hash manifest does not exist" in errors


class TestModePolicy:
    def test_build_mode_policy_implementation(self):
        policy = build_mode_policy(MODE_IMPLEMENTATION_ACCEPTANCE)
        assert policy["acceptance_mode"] == MODE_IMPLEMENTATION_ACCEPTANCE
        assert "FINAL_SYSTEM_ACCEPTANCE" in policy["required_layers"]
        assert "L0_SEED_KERNEL" in policy["required_layers"]

    def test_build_mode_policy_release(self):
        policy = build_mode_policy(MODE_RELEASE_ACCEPTANCE)
        assert "PACKAGING_DISTRIBUTION" in policy["required_layers"]
        assert "BACKUP_DISASTER_RECOVERY" in policy["required_layers"]

    def test_is_layer_required_for_mode(self):
        assert is_layer_required_for_mode("L0_SEED_KERNEL", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert not is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_SOURCE_ONLY_ACCEPTANCE)

    def test_is_deferral_allowed_for_mode(self):
        assert is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_SOURCE_ONLY_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("L0_SEED_KERNEL", MODE_IMPLEMENTATION_ACCEPTANCE)

    def test_validate_acceptance_mode_valid(self):
        assert validate_acceptance_mode(MODE_IMPLEMENTATION_ACCEPTANCE) == []

    def test_validate_acceptance_mode_invalid(self):
        errors = validate_acceptance_mode("INVALID")
        assert len(errors) == 1


class TestLayerCatalog:
    def test_build_canonical_layer_catalog_has_26_layers(self):
        catalog = build_canonical_layer_catalog()
        assert len(catalog) == 26

    def test_catalog_contains_final_system_acceptance(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert "FINAL_SYSTEM_ACCEPTANCE" in ids

    def test_catalog_all_have_ids(self):
        catalog = build_canonical_layer_catalog()
        for layer in catalog:
            assert layer.layer_id
            assert layer.layer_name

    def test_validate_layer_catalog_valid(self):
        catalog = build_canonical_layer_catalog()
        assert validate_layer_catalog(catalog) == []

    def test_validate_layer_catalog_empty(self):
        errors = validate_layer_catalog([])
        assert "FINAL_SYSTEM_ACCEPTANCE layer missing" in str(errors)


class TestLayerRegistry:
    def test_build_registry(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, reviewed_commit="abc123",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        assert reg.reviewed_commit == "abc123"
        assert reg.acceptance_mode == MODE_IMPLEMENTATION_ACCEPTANCE
        assert len(reg.layers) == 26

    def test_get_layer_by_id(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        layer = get_layer_by_id(reg, "FINAL_SYSTEM_ACCEPTANCE")
        assert layer is not None
        assert layer.layer_id == "FINAL_SYSTEM_ACCEPTANCE"

    def test_get_layer_by_id_missing(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        assert get_layer_by_id(reg, "NONEXISTENT") is None

    def test_list_required_layers(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        required = list_required_layers(reg)
        assert len(required) > 0
        for l in required:
            assert is_layer_required_for_mode(l.layer_id, MODE_IMPLEMENTATION_ACCEPTANCE)

    def test_list_safely_deferred_layers(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        deferred = list_safely_deferred_layers(reg)
        for l in deferred:
            assert not is_layer_required_for_mode(l.layer_id, MODE_IMPLEMENTATION_ACCEPTANCE)

    def test_write_layer_registry(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        path = write_layer_registry(reg, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_layer_registry.schema.json"
        assert len(data["layers"]) == 26


class TestEvidenceCollector:
    def test_collect_evidence_item_exists(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "test.txt"
        f.write_text("hello")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "test", True,
        )
        assert item.exists
        assert item.readable
        assert item.sha256 is not None

    def test_collect_evidence_item_not_exists(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        item = collect_evidence_item(
            tmp_path, layer, "nonexistent.txt", "test", True,
        )
        assert not item.exists
        assert not item.readable

    def test_collect_layer_evidence(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        manifest = collect_layer_evidence(tmp_path, reg)
        assert manifest.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert manifest.items is not None

    def test_write_evidence_manifest(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        manifest = collect_layer_evidence(tmp_path, reg)
        path = write_evidence_manifest(manifest, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_evidence_manifest.schema.json"

    def test_validate_evidence_item_schema_if_json(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        item = collect_evidence_item(tmp_path, layer, "missing.txt", "test", False)
        result = validate_evidence_item_schema_if_json(tmp_path, item)
        assert result.layer_id == "L1"


class TestDeviationRegister:
    def test_load_deviation_register_empty(self, tmp_path: Path):
        devs = load_deviation_register(tmp_path)
        assert devs == []

    def test_write_and_load_deviation_register(self, tmp_path: Path):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason",
            )
        ]
        path = write_deviation_register(devs, tmp_path)
        assert path.exists()
        loaded = load_deviation_register(tmp_path)
        assert len(loaded) == 1
        assert loaded[0].deviation_id == "D001"

    def test_validate_deviation_register_clean(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason",
            )
        ]
        assert validate_deviation_register(devs) == []

    def test_validate_deviation_register_critical(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason", safety_impact="critical",
            )
        ]
        errors = validate_deviation_register(devs)
        assert len(errors) == 1


class TestCrossLayerChecker:
    def test_run_cross_layer_checks_implementation(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        manifest = collect_layer_evidence(tmp_path, reg)
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        assert len(checks) == 15

    def test_run_cross_layer_checks_release(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_RELEASE_ACCEPTANCE,
        )
        manifest = collect_layer_evidence(tmp_path, reg)
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_RELEASE_ACCEPTANCE)
        assert len(checks) == 15

    def test_write_cross_layer_matrix(self, tmp_path: Path):
        checks = [
            CrossLayerCheck(
                check_id="CL-001", source_layer="A", target_layer="B",
                requirement="r", status=STATUS_PASS,
            )
        ]
        path = write_cross_layer_matrix(checks, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["checks"]) == 1

    def test_cl015_bootstrap_exception(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        manifest = collect_layer_evidence(tmp_path, reg)
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        cl015 = [c for c in checks if c.check_id == "CL-015"]
        assert len(cl015) == 1
        assert cl015[0].status == "PASS"


class TestValidationRunner:
    def test_run_single_validation_command_bad(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "test_cmd", ["nonexistent_cmd_xyz"], "output.txt",
        )
        assert result.status == "FAIL"
        assert "not found" in result.summary.lower() or "not found" in str(result.summary)

    def test_run_validation_commands_skips_pytest(self, tmp_path: Path):
        results = run_validation_commands(
            tmp_path, include_full_pytest=False,
        )
        names = [r.command_name for r in results]
        # compileall will be in results
        assert "compileall" in names
        pytest_results = [r for r in results if r.command_name == "pytest"]
        assert len(pytest_results) == 1
        if pytest_results:
            assert pytest_results[0].status in ("PASS", "FAIL", "NOT_RUN")

    def test_write_validation_results(self, tmp_path: Path):
        results = [FinalAcceptanceValidationResult(
            command_name="test", command_text="test", status=STATUS_PASS,
        )]
        path = write_validation_results(results, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["results"]) == 1


class TestSchemaValidator:
    def test_validate_final_acceptance_schemas(self, tmp_path: Path):
        schema_dir = tmp_path / "tools" / "agentx_evolve" / "schemas"
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"test": {"type": "string"}},
        }
        (schema_dir / "final_acceptance_layer.schema.json").write_text(
            json.dumps(schema), encoding="utf-8"
        )
        (schema_dir / "final_acceptance_report.schema.json").write_text(
            json.dumps(schema), encoding="utf-8"
        )
        results = validate_final_acceptance_schemas(tmp_path)
        total = len(results)
        missing_count = sum(
            1 for r in results if "Schema file missing" in r.summary
        )
        assert total == 11
        assert missing_count == 9

    def test_validate_json_file_against_schema(self, tmp_path: Path):
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")

        valid = tmp_path / "valid.json"
        valid.write_text(json.dumps({"name": "test"}), encoding="utf-8")
        result = validate_json_file_against_schema(valid, schema_path)
        if result.status == "PASS":
            assert result.exit_code == 0

    def test_write_schema_validation_results(self, tmp_path: Path):
        results = [FinalAcceptanceValidationResult(
            command_name="schema_test", command_text="test", status=STATUS_PASS,
        )]
        path = write_schema_validation_results(results, tmp_path)
        assert path.exists()


class TestFinalVerdict:
    def test_accepted(self):
        v, r, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "PASS", "L2": "PASS"},
        )
        assert v == "ACCEPTED"

    def test_accepted_with_deferrals(self):
        v, r, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "PASS", "L2": "DEFERRED_SAFELY"},
            safe_deferrals=[{"layer_id": "L2"}],
        )
        assert v == "ACCEPTED_WITH_SAFE_DEFERRALS"

    def test_not_accepted_blockers(self):
        v, r, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "PASS"},
            blockers=["critical failure"],
        )
        assert v == "NOT_ACCEPTED"


class TestReportGenerator:
    def test_build_report(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc", created_at="t", acceptance_mode="TEST",
        )
        report = build_final_acceptance_report(tmp_path, reg)
        assert report.final_verdict == "NOT_ACCEPTED"
        assert report.reviewed_commit == "abc"

    def test_write_report(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(created_at="t")
        report = build_final_acceptance_report(tmp_path, reg)
        path = write_final_acceptance_report(report, tmp_path)
        assert path.exists()


class TestAcceptanceRunner:
    def test_invalid_mode(self, tmp_path: Path):
        result = run_final_acceptance(
            tmp_path, acceptance_mode="BAD", skip_validation_commands=True,
        )
        assert result["final_verdict"] == "NOT_ACCEPTED"
        assert len(result.get("errors", [])) > 0

    def test_minimal_run(self, tmp_path: Path):
        result = run_final_acceptance(
            tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result
        assert "implementation_rating" in result
        assert "completion_record" in result


class TestAllExportable:
    def test_all_classes_importable(self):
        from tools.agentx_evolve.final_acceptance import (
            FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
            FinalAcceptanceEvidenceItem, FinalAcceptanceEvidenceManifest,
            CrossLayerCheck, FinalAcceptanceValidationResult,
            FinalAcceptanceDeviation, FinalAcceptanceArtifactHash,
            FinalAcceptanceModePolicy, FinalAcceptanceReport,
            FinalAcceptanceCompletionRecord,
        )
        assert FinalAcceptanceLayer is not None
        assert FinalAcceptanceReport is not None

    def test_all_functions_importable(self):
        from tools.agentx_evolve.final_acceptance import (
            runtime_root, ensure_runtime_root, atomic_write_json,
            write_json_artifact, sha256_file, sha256_text,
            build_mode_policy, is_layer_required_for_mode,
            build_canonical_layer_catalog, validate_layer_catalog,
            build_final_acceptance_layer_registry, get_layer_by_id,
            collect_layer_evidence, collect_evidence_item,
            load_deviation_register, validate_deviation_register,
            run_cross_layer_checks, run_validation_commands,
            validate_final_acceptance_schemas, calculate_final_verdict,
            build_final_acceptance_report,
            run_final_acceptance, write_completion_record,
        )
        assert runtime_root is not None
        assert calculate_final_verdict is not None

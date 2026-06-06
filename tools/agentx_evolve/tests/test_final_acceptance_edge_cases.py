import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.acceptance_runner import run_final_acceptance
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    VERDICT_NOT_ACCEPTED, MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    VALIDATED_NOT_ACCEPTED,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root, atomic_write_json, write_json_artifact,
)
from tools.agentx_evolve.final_acceptance.hash_utils import validate_acyclic_hash_manifest
from tools.agentx_evolve.final_acceptance.report_generator import (
    build_final_acceptance_report, _completion_record_to_dict,
)
from tools.agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
from tools.agentx_evolve.final_acceptance.layer_catalog import build_canonical_layer_catalog
from tools.agentx_evolve.final_acceptance.layer_registry import (
    build_final_acceptance_layer_registry,
)


class TestEdgeEmptyRepo:
    def test_empty_dir_run(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        assert runtime.exists()

    def test_empty_dir_without_bootstrap(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
        )
        assert "final_verdict" in result


class TestEdgeNoGitRepository:
    def test_nonexistent_repo_root(self):
        with pytest.raises(Exception):
            run_final_acceptance(
                repo_root=Path("/nonexistent/path/xyz"),
                skip_validation_commands=True,
                skip_schema_validation=True,
                skip_cross_layer_checks=True,
            )

    def test_relative_path(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result


class TestEdgeCorruptedRuntime:
    def test_corrupted_completion_record(self, tmp_path: Path):
        runtime = ensure_runtime_root(tmp_path)
        (runtime / "final_acceptance_completion_record.json").write_text(
            "{corrupt", encoding="utf-8"
        )
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result

    def test_corrupted_report(self, tmp_path: Path):
        runtime = ensure_runtime_root(tmp_path)
        (runtime / "final_acceptance_report.json").write_text(
            "not json", encoding="utf-8"
        )
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result

    def test_corrupted_evidence(self, tmp_path: Path):
        runtime = ensure_runtime_root(tmp_path)
        (runtime / "final_acceptance_evidence_manifest.json").write_text(
            "{bad", encoding="utf-8"
        )
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result


class TestEdgeModeBoundaries:
    def test_all_modes_run_without_error(self, tmp_path: Path):
        for mode in [
            "IMPLEMENTATION_ACCEPTANCE", "SOURCE_ONLY_ACCEPTANCE",
            "NON_PRODUCTION_ACCEPTANCE", "PRODUCTION_ACCEPTANCE", "RELEASE_ACCEPTANCE",
        ]:
            result = run_final_acceptance(
                repo_root=tmp_path,
                acceptance_mode=mode,
                skip_validation_commands=True,
                skip_schema_validation=True,
                skip_cross_layer_checks=True,
                bootstrap_self=True,
            )
            assert "final_verdict" in result, f"Failed for mode {mode}"

    def test_mode_case_sensitive(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode="implementation_acceptance",
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED
        assert len(result.get("errors", [])) > 0

    def test_mode_with_whitespace(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=" IMPLEMENTATION_ACCEPTANCE ",
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED


class TestEdgeHashManifest:
    def test_no_artifacts_does_not_crash(self, tmp_path: Path):
        runtime = ensure_runtime_root(tmp_path)
        from tools.agentx_evolve.final_acceptance.hash_utils import hash_artifacts
        hashes = hash_artifacts([])
        assert hashes == []

    def test_hash_manifest_empty_runtime(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert "Hash manifest does not exist" in errors

    def test_duplicate_artifact_hashing(self, tmp_path: Path):
        runtime = ensure_runtime_root(tmp_path)
        (runtime / "a.txt").write_text("data")
        (runtime / "b.txt").write_text("data")
        from tools.agentx_evolve.final_acceptance.hash_utils import hash_artifacts
        hashes = hash_artifacts([runtime / "a.txt", runtime / "a.txt"])
        assert len(hashes) == 1


class TestEdgeCompletionRecord:
    def test_validated_not_accepted_status(self):
        from tools.agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceCompletionRecord,
        )
        record = FinalAcceptanceCompletionRecord(
            status=VALIDATED_NOT_ACCEPTED,
            created_at="t",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
        )
        d = _completion_record_to_dict(record)
        assert d["status"] == VALIDATED_NOT_ACCEPTED

    def test_all_fields_empty(self):
        from tools.agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceCompletionRecord,
        )
        record = FinalAcceptanceCompletionRecord()
        d = _completion_record_to_dict(record)
        assert d["status"] == "VALIDATED"
        assert d["reviewed_commit"] is None
        assert d["commands_run"] == []
        assert d["artifacts_created"] == []
        assert d["review_environment"] == {}

    def test_review_environment_empty_dict(self):
        from tools.agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceCompletionRecord,
        )
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED", created_at="t",
            review_environment={},
            final_verdict="ACCEPTED", implementation_rating=1.0,
        )
        d = _completion_record_to_dict(record)
        assert d["review_environment"] == {}


class TestEdgeReport:
    def test_report_no_hashes(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        report = build_final_acceptance_report(tmp_path, reg)
        assert report.artifact_hashes == []
        assert report.artifact_hashes_path == ""
        assert report.artifact_hashes_sha256 is None

    def test_report_empty_layer_statuses(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        report = build_final_acceptance_report(tmp_path, reg)
        assert report.layer_statuses == {}

    def test_report_all_nullable_fields(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        report = build_final_acceptance_report(
            tmp_path, reg, blockers=[], high_issues=[], non_blocking_followups=[],
        )
        assert report.blockers == []
        assert report.high_issues == []
        assert report.non_blocking_followups == []


class TestEdgeVerdict:
    def test_all_none_inputs(self):
        verdict, rating, b, h, n = calculate_final_verdict()
        assert verdict is not None
        assert rating > 0

    def test_no_layers_passes(self):
        verdict, rating, b, h, n = calculate_final_verdict(
            layer_statuses={},
        )
        assert verdict == "ACCEPTED"
        assert rating == 1.0

    def test_all_statuses_not_accepted(self):
        for status in ["NOT_CHECKED", "NOT_RUN", "STALE", "FAIL", "PARTIAL"]:
            verdict, rating, b, h, n = calculate_final_verdict(
                layer_statuses={"L1": status},
            )
            assert verdict == "NOT_ACCEPTED", f"Status {status} should be NOT_ACCEPTED"

    def test_all_statuses_accepted(self):
        for status in ["PASS", "NOT_APPLICABLE", "DEFERRED_SAFELY"]:
            verdict, rating, b, h, n = calculate_final_verdict(
                layer_statuses={"L1": status},
                safe_deferrals=[{"layer_id": "L1"}] if status == "DEFERRED_SAFELY" else [],
            )
            assert verdict in ("ACCEPTED", "ACCEPTED_WITH_SAFE_DEFERRALS"), \
                f"Status {status} should be ACCEPTED"


class TestEdgeLayers:
    def test_catalog_empty_layer_id(self):
        from tools.agentx_evolve.final_acceptance.layer_catalog import validate_layer_catalog
        from tools.agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayer
        layers = [
            FinalAcceptanceLayer(layer_id="", layer_name="Empty ID"),
            FinalAcceptanceLayer(layer_id="FINAL_SYSTEM_ACCEPTANCE", layer_name="FSA"),
        ]
        errors = validate_layer_catalog(layers)
        assert any("empty layer_id" in e.lower() for e in errors)

    def test_registry_empty_layers(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayerRegistry
        reg = FinalAcceptanceLayerRegistry(created_at="t", layers=[])
        assert len(reg.layers) == 0


class TestEdgeAtomicWrite:
    def test_atomic_write_to_nested_dir(self, tmp_path: Path):
        path = tmp_path / "a" / "b" / "c" / "test.json"
        atomic_write_json(path, {"key": "value"})
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["key"] == "value"

    def test_atomic_write_overwrites(self, tmp_path: Path):
        path = tmp_path / "test.json"
        atomic_write_json(path, {"v": 1})
        atomic_write_json(path, {"v": 2})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["v"] == 2

    def test_atomic_write_empty_dict(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        atomic_write_json(path, {})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == {}

    def test_atomic_write_sort_keys(self, tmp_path: Path):
        path = tmp_path / "sorted.json"
        atomic_write_json(path, {"b": 2, "a": 1})
        content = path.read_text(encoding="utf-8").strip()
        assert '"a"' in content
        assert '"b"' in content


class TestEdgeRuntimeRoot:
    def test_nonexistent_runtime_root(self, tmp_path: Path):
        root = runtime_root(tmp_path)
        assert not root.exists()

    def test_ensure_creates_parents(self, tmp_path: Path):
        nested = tmp_path / "a" / "b" / "c"
        path = ensure_runtime_root(nested)
        assert path.exists()

    def test_write_artifact_creates_dir(self, tmp_path: Path):
        path = write_json_artifact(tmp_path, "test.json", {"x": 1})
        assert path.exists()


class TestEdgeCliFlagCombinations:
    def test_skip_all_flags(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
            no_safe_deferrals=True,
        )
        assert "final_verdict" in result

    def test_run_with_commit_no_branch(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            reviewed_commit="abc123",
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result

    def test_run_with_branch_no_commit(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            reviewed_branch="feature/test",
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result


class TestEdgeImportAll:
    def test_all_exports_accessible(self):
        from tools.agentx_evolve.final_acceptance import (
            cli_main, VALIDATED_NOT_ACCEPTED,
            write_artifact_hashes, validate_acyclic_hash_manifest,
            build_mode_policy, build_canonical_layer_catalog,
            build_final_acceptance_layer_registry, get_layer_by_id,
            list_required_layers, list_safely_deferred_layers,
            collect_layer_evidence, collect_evidence_item,
            validate_evidence_item_schema_if_json, write_evidence_manifest,
            load_deviation_register, validate_deviation_register, write_deviation_register,
            run_cross_layer_checks, write_cross_layer_matrix,
            run_validation_commands, run_single_validation_command, write_validation_results,
            validate_final_acceptance_schemas, validate_json_file_against_schema,
            write_schema_validation_results, calculate_final_verdict,
            build_final_acceptance_report, write_final_acceptance_report,
            run_final_acceptance, write_completion_record, write_latest_result,
        )
        assert VALIDATED_NOT_ACCEPTED == "VALIDATED_NOT_ACCEPTED"
        assert cli_main is not None

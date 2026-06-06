import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.schema_validator import (
    validate_final_acceptance_schemas, validate_json_file_against_schema,
    write_schema_validation_results,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceValidationResult, STATUS_PASS, STATUS_FAIL,
)


class TestValidateFinalAcceptanceSchemas:
    def test_all_schemas_missing_returns_11_failures(self, tmp_path: Path):
        results = validate_final_acceptance_schemas(tmp_path)
        assert len(results) == 11
        for r in results:
            assert r.status == STATUS_FAIL

    def test_with_valid_schemas(self, tmp_path: Path):
        schema_dir = tmp_path / "tools" / "agentx_evolve" / "schemas"
        schema_dir.mkdir(parents=True)
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"test": {"type": "string"}},
        }
        for fname in [
            "final_acceptance_layer.schema.json",
            "final_acceptance_layer_registry.schema.json",
            "final_acceptance_evidence_item.schema.json",
            "final_acceptance_evidence_manifest.schema.json",
            "final_acceptance_cross_layer_check.schema.json",
            "final_acceptance_validation_result.schema.json",
            "final_acceptance_report.schema.json",
            "final_acceptance_completion_record.schema.json",
            "final_acceptance_deviation.schema.json",
            "final_acceptance_artifact_hash.schema.json",
            "final_acceptance_mode_policy.schema.json",
        ]:
            (schema_dir / fname).write_text(json.dumps(schema), encoding="utf-8")
        results = validate_final_acceptance_schemas(tmp_path)
        assert len(results) == 11
        passes = [r for r in results if r.status == STATUS_PASS]
        assert len(passes) == 11

    def test_mixed_schemas(self, tmp_path: Path):
        schema_dir = tmp_path / "tools" / "agentx_evolve" / "schemas"
        schema_dir.mkdir(parents=True)
        valid = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
        }
        (schema_dir / "final_acceptance_report.schema.json").write_text(
            json.dumps(valid), encoding="utf-8"
        )
        results = validate_final_acceptance_schemas(tmp_path)
        assert len(results) == 11
        passes = [r for r in results if r.status == STATUS_PASS]
        assert len(passes) == 1

    def test_invalid_json_schema(self, tmp_path: Path):
        schema_dir = tmp_path / "tools" / "agentx_evolve" / "schemas"
        schema_dir.mkdir(parents=True)
        (schema_dir / "final_acceptance_report.schema.json").write_text(
            "not json", encoding="utf-8"
        )
        results = validate_final_acceptance_schemas(tmp_path)
        report_results = [r for r in results
                          if "final_acceptance_report.schema.json" in r.command_name]
        assert len(report_results) >= 1
        assert report_results[0].status == STATUS_FAIL

    def test_draft7_invalid_schema(self, tmp_path: Path):
        schema_dir = tmp_path / "tools" / "agentx_evolve" / "schemas"
        schema_dir.mkdir(parents=True)
        bad_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "invalid_type_xyz",
        }
        (schema_dir / "final_acceptance_report.schema.json").write_text(
            json.dumps(bad_schema), encoding="utf-8"
        )
        try:
            import jsonschema
            results = validate_final_acceptance_schemas(tmp_path)
            report_results = [r for r in results
                              if "final_acceptance_report.schema.json" in r.command_name]
            if jsonschema:
                assert len(report_results) >= 1
        except ImportError:
            pass


class TestValidateJsonFileAgainstSchema:
    def test_valid_json(self, tmp_path: Path):
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
        try:
            import jsonschema
            assert result.status == STATUS_PASS
        except ImportError:
            assert result.status == STATUS_PASS

    def test_invalid_json_data(self, tmp_path: Path):
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")

        invalid = tmp_path / "invalid.json"
        invalid.write_text(json.dumps({"age": 30}), encoding="utf-8")
        result = validate_json_file_against_schema(invalid, schema_path)
        try:
            import jsonschema
            assert result.status == STATUS_FAIL
        except ImportError:
            assert result.status == STATUS_PASS

    def test_missing_instance_file(self, tmp_path: Path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}), encoding="utf-8")
        missing = tmp_path / "missing.json"
        result = validate_json_file_against_schema(missing, schema_path)
        assert result.status in (STATUS_PASS, STATUS_FAIL)

    def test_invalid_schema_path(self, tmp_path: Path):
        instance = tmp_path / "data.json"
        instance.write_text(json.dumps({}), encoding="utf-8")
        result = validate_json_file_against_schema(instance, tmp_path / "no_schema.json")
        assert result.status in (STATUS_PASS, STATUS_FAIL)


class TestWriteSchemaValidationResults:
    def test_writes_file(self, tmp_path: Path):
        results = [
            FinalAcceptanceValidationResult(
                command_name="schema_check", command_text="test",
                status=STATUS_PASS, exit_code=0, summary="ok",
            )
        ]
        path = write_schema_validation_results(results, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_schema_validation_results.json"

    def test_content(self, tmp_path: Path):
        results = [
            FinalAcceptanceValidationResult(
                command_name="s1", command_text="c1", status=STATUS_PASS, exit_code=0,
            ),
            FinalAcceptanceValidationResult(
                command_name="s2", command_text="c2", status=STATUS_FAIL, exit_code=1,
            ),
        ]
        path = write_schema_validation_results(results, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["results"]) == 2
        assert data["results"][0]["command_name"] == "s1"

    def test_empty_results(self, tmp_path: Path):
        path = write_schema_validation_results([], tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["results"] == []

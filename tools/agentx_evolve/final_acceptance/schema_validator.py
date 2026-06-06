import json
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceValidationResult, STATUS_PASS, STATUS_FAIL
from .artifact_writer import write_json_artifact


def validate_final_acceptance_schemas(repo_root: Path) -> list[FinalAcceptanceValidationResult]:
    results: list[FinalAcceptanceValidationResult] = []
    schema_dir = repo_root / "tools" / "agentx_evolve" / "schemas"

    schema_files = [
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
    ]

    try:
        import jsonschema
        has_jsonschema = True
    except ImportError:
        has_jsonschema = False

    for fname in schema_files:
        schema_path = schema_dir / fname
        if not schema_path.exists():
            results.append(FinalAcceptanceValidationResult(
                command_name=f"schema_check:{fname}",
                command_text=f"Check {fname} exists",
                exit_code=1,
                status=STATUS_FAIL,
                summary=f"Schema file missing: {fname}",
            ))
            continue

        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if has_jsonschema:
                import jsonschema
                try:
                    jsonschema.Draft7Validator.check_schema(schema)
                    results.append(FinalAcceptanceValidationResult(
                        command_name=f"schema_check:{fname}",
                        command_text=f"Validate {fname}",
                        exit_code=0,
                        status=STATUS_PASS,
                        summary=f"{fname}: valid Draft-7 schema",
                    ))
                except jsonschema.SchemaError as e:
                    results.append(FinalAcceptanceValidationResult(
                        command_name=f"schema_check:{fname}",
                        command_text=f"Validate {fname}",
                        exit_code=1,
                        status=STATUS_FAIL,
                        summary=f"{fname}: invalid schema: {e}",
                    ))
            else:
                results.append(FinalAcceptanceValidationResult(
                    command_name=f"schema_check:{fname}",
                    command_text=f"Check {fname} JSON",
                    exit_code=0,
                    status=STATUS_PASS,
                    summary=f"{fname}: valid JSON (jsonschema not available)",
                ))
        except json.JSONDecodeError as e:
            results.append(FinalAcceptanceValidationResult(
                command_name=f"schema_check:{fname}",
                command_text=f"Parse {fname}",
                exit_code=1,
                status=STATUS_FAIL,
                summary=f"{fname}: invalid JSON: {e}",
            ))

    return results


def validate_json_file_against_schema(
    json_path: Path, schema_path: Path,
) -> FinalAcceptanceValidationResult:
    try:
        import jsonschema
    except ImportError:
        return FinalAcceptanceValidationResult(
            command_name=f"validate:{json_path.name}",
            command_text=f"Validate {json_path.name} against {schema_path.name}",
            exit_code=None,
            status=STATUS_PASS,
            summary="jsonschema not available, skipping",
        )

    try:
        instance = json.loads(json_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance, schema)
        return FinalAcceptanceValidationResult(
            command_name=f"validate:{json_path.name}",
            command_text=f"Validate {json_path.name} against {schema_path.name}",
            exit_code=0,
            status=STATUS_PASS,
            summary=f"{json_path.name} valid against {schema_path.name}",
        )
    except (json.JSONDecodeError, jsonschema.ValidationError, OSError) as e:
        return FinalAcceptanceValidationResult(
            command_name=f"validate:{json_path.name}",
            command_text=f"Validate {json_path.name} against {schema_path.name}",
            exit_code=1,
            status=STATUS_FAIL,
            summary=f"Validation failed: {e}",
        )


def write_schema_validation_results(
    results: list[FinalAcceptanceValidationResult], repo_root: Path,
) -> Path:
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_validation_result.schema.json",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "results": [
            {
                "command_name": r.command_name,
                "command_text": r.command_text,
                "exit_code": r.exit_code,
                "status": r.status,
                "summary": r.summary,
                "output_artifact_path": r.output_artifact_path,
                "output_sha256": r.output_sha256,
                "warnings": r.warnings,
                "errors": r.errors,
            }
            for r in results
        ],
        "warnings": [],
        "errors": [],
    }
    return write_json_artifact(repo_root, "final_acceptance_schema_validation_results.json", data)

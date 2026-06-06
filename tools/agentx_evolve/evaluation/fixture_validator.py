from __future__ import annotations
from pathlib import Path
import json


def _load_schema(path: str) -> dict | None:
    try:
        import jsonschema
        p = Path(__file__).parent.parent / "schemas" / path
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return None


def _validate_against_schema(instance: dict, schema_path: str) -> list[str]:
    schema = _load_schema(schema_path)
    if schema is None:
        return [f"Schema not found: {schema_path}"]
    errors: list[str] = []
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(instance):
            errors.append(f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}")
    except ImportError:
        errors.append("jsonschema not available")
    except Exception as exc:
        errors.append(str(exc))
    return errors


def validate_benchmark_suite(suite: dict) -> tuple[bool, list[str]]:
    errors = _validate_against_schema(suite, "evaluation_benchmark_suite.schema.json")
    if not errors:
        if not suite.get("case_refs"):
            errors.append("suite has no case_refs")
    return (len(errors) == 0, errors)


def validate_benchmark_case(case: dict) -> tuple[bool, list[str]]:
    errors = _validate_against_schema(case, "evaluation_benchmark_case.schema.json")
    if not errors:
        case_type = case.get("case_type", "")
        if case_type not in (
            "STATIC_EXPECTED_RESULT", "TOOL_CALL_EXPECTED_RESULT", "POLICY_DENIAL_EXPECTED_RESULT",
            "REGRESSION_EXPECTED_FAILURE", "ARTIFACT_EXPECTED_RESULT",
            "REPORT_GENERATION_EXPECTED_RESULT", "NEGATIVE_FIXTURE_VALIDATION",
        ):
            errors.append(f"Unknown case_type: {case_type}")
    return (len(errors) == 0, errors)


def validate_expected_result(expected: dict) -> tuple[bool, list[str]]:
    errors = _validate_against_schema(expected, "evaluation_expected_result.schema.json")
    if not errors:
        comparators = expected.get("comparators", [])
        for i, comp in enumerate(comparators):
            ctype = comp.get("type", "")
            if ctype not in (
                "EXACT_MATCH", "CONTAINS", "REGEX_MATCH", "STATUS_MATCH",
                "FAILURE_CLASS_MATCH", "ARTIFACT_EXISTS", "NUMERIC_EQUALS",
                "NUMERIC_AT_LEAST", "NUMERIC_AT_MOST", "LIST_CONTAINS",
                "DICT_HAS_KEY", "CUSTOM_STATIC_CHECK",
            ):
                errors.append(f"comparator[{i}]: unknown type {ctype}")
    return (len(errors) == 0, errors)


def validate_threshold(threshold: dict) -> tuple[bool, list[str]]:
    errors = _validate_against_schema(threshold, "evaluation_threshold.schema.json")
    return (len(errors) == 0, errors)


def validate_baseline(baseline: dict) -> tuple[bool, list[str]]:
    errors = _validate_against_schema(baseline, "evaluation_baseline.schema.json")
    return (len(errors) == 0, errors)


def validate_fixture_tree(fixture_root: Path) -> dict:
    result = {
        "status": "PASS",
        "fixtures_found": [],
        "errors": [],
        "warnings": [],
    }
    if not fixture_root.exists():
        result["status"] = "FAIL"
        result["errors"].append(f"Fixture root not found: {fixture_root}")
        return result
    for subdir in ["smoke", "regression", "negative", "baselines"]:
        d = fixture_root / subdir
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix == ".json":
                    result["fixtures_found"].append(str(f.relative_to(fixture_root)))
    if not result["fixtures_found"]:
        result["warnings"].append("No fixture files found")
    return result

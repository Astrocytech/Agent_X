from __future__ import annotations
import json
from pathlib import Path


SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

REQUIRED_SCHEMAS = [
    "outcome_event.schema.json",
    "outcome_review.schema.json",
    "learning_signal.schema.json",
    "memory_candidate.schema.json",
    "learning_policy_decision.schema.json",
    "regression_link.schema.json",
    "outcome_review_report.schema.json",
    "learning_audit_event.schema.json",
    "follow_up_task_proposal.schema.json",
    "learning_lock.schema.json",
    "learning_review_index.schema.json",
    "learning_evidence_manifest.schema.json",
    "learning_implementation_review_report.schema.json",
    "learning_completion_record.schema.json",
    "learning_adapter_result.schema.json",
]


def test_all_required_schemas_exist():
    for fname in REQUIRED_SCHEMAS:
        path = SCHEMAS_DIR / fname
        assert path.exists(), f"Missing schema: {fname}"


def test_all_schemas_are_valid_json():
    for fname in REQUIRED_SCHEMAS:
        path = SCHEMAS_DIR / fname
        schema = json.loads(path.read_text())
        assert "$schema" in schema, f"Missing $schema in {fname}"
        assert "type" in schema, f"Missing type in {fname}"
        assert "properties" in schema, f"Missing properties in {fname}"


def test_all_schemas_have_required_top_level_keys():
    for fname in REQUIRED_SCHEMAS:
        path = SCHEMAS_DIR / fname
        schema = json.loads(path.read_text())
        assert "title" in schema or "description" in schema, f"Missing title/description in {fname}"
        assert "required" in schema, f"Missing required in {fname}"
        assert "additionalProperties" in schema, f"Missing additionalProperties in {fname}"


def test_all_schemas_have_schema_version_field():
    for fname in REQUIRED_SCHEMAS:
        path = SCHEMAS_DIR / fname
        schema = json.loads(path.read_text())
        props = schema.get("properties", {})
        assert "schema_version" in props, f"Missing schema_version property in {fname}"


def test_all_schemas_set_additional_properties_false():
    for fname in REQUIRED_SCHEMAS:
        path = SCHEMAS_DIR / fname
        schema = json.loads(path.read_text())
        assert schema.get("additionalProperties") is False, f"additionalProperties not false in {fname}"

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "llm_worker")


class TestLLMWorkerTaskSchema:
    def test_accepts_valid_task(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_task.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_task.schema.json",
            "task_id": "t-test",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "requested_by": "tester",
            "caller_role": "developer",
            "worker_mode": "PLAN_ONLY",
            "implementation_goal": "test",
            "target_component_id": "test-module",
            "target_files": [],
            "dry_run": True,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_task_id(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_task.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_task.schema.json",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "requested_by": "tester",
            "caller_role": "developer",
            "worker_mode": "PLAN_ONLY",
            "implementation_goal": "test",
            "target_component_id": "test",
            "target_files": [],
            "dry_run": True,
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_rejects_invalid_worker_mode(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_task.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_task.schema.json",
            "task_id": "t-bad",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "requested_by": "tester",
            "caller_role": "developer",
            "worker_mode": "INVALID_MODE",
            "implementation_goal": "test",
            "target_component_id": "test",
            "target_files": [],
            "dry_run": True,
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_valid_fixture(self):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, "valid_llm_worker_task.json")
        with open(fpath) as f:
            data = json.load(f)
        spath = os.path.join(SCHEMA_DIR, data["schema_id"])
        with open(spath) as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)

    def test_missing_fixture_fails(self):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, "missing_llm_worker_task.json")
        with open(fpath) as f:
            data = json.load(f)
        spath = os.path.join(SCHEMA_DIR, data["schema_id"])
        with open(spath) as f:
            schema = json.load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_invalid_fixture_fails(self):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, "invalid_llm_worker_task.json")
        with open(fpath) as f:
            data = json.load(f)
        spath = os.path.join(SCHEMA_DIR, data["schema_id"])
        with open(spath) as f:
            schema = json.load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

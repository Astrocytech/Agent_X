import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "llm_worker")


class TestLLMWorkerResultSchema:
    def test_accepts_success(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_result.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_result.schema.json",
            "worker_result_id": "wr-test",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "status": "SUCCESS",
            "message": "done",
            "worker_mode": "PLAN_ONLY",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(data, schema)

    def test_accepts_blocked(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_result.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_result.schema.json",
            "worker_result_id": "wr-blocked",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-002",
            "status": "BLOCKED",
            "message": "blocked",
            "worker_mode": "RESTRICTED",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(data, schema)

    def test_rejects_invalid_status(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_result.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_result.schema.json",
            "worker_result_id": "wr-bad",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-003",
            "status": "UNKNOWN_STATUS",
            "message": "bad",
            "worker_mode": "PLAN_ONLY",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_rejects_missing_task_id(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "llm_worker_result.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "llm_worker_result.schema.json",
            "worker_result_id": "wr-bad",
            "created_at": "2026-06-05T00:00:00",
            "source_component": "LLMImplementationWorker",
            "status": "SUCCESS",
            "message": "bad",
            "worker_mode": "PLAN_ONLY",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_valid_success_fixture(self):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, "valid_worker_result_success.json")
        with open(fpath) as f:
            data = json.load(f)
        spath = os.path.join(SCHEMA_DIR, data["schema_id"])
        with open(spath) as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)

    def test_valid_blocked_fixture(self):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, "valid_worker_result_blocked.json")
        with open(fpath) as f:
            data = json.load(f)
        spath = os.path.join(SCHEMA_DIR, data["schema_id"])
        with open(spath) as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)

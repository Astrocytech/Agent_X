import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    DependencyStatus,
    LLMWorkerResult,
    LLMWorkerAuditEvent,
)
from agentx_evolve.workers.llm_implementation_worker.worker_logger import (
    append_worker_task,
    append_dependency_status,
    append_worker_result,
    write_latest_worker_result,
    append_worker_audit,
)


class TestWorkerLogger:
    def test_writes_histories(self, tmp_path):
        task = LLMWorkerTask(task_id="t-001")
        result = append_worker_task(task, tmp_path)
        assert "sha256" in result
        assert "path" in result

    def test_writes_latest_atomically(self, tmp_path):
        result = LLMWorkerResult(
            worker_result_id="wr-001",
            task_id="t-001",
            status="SUCCESS",
            message="done",
            worker_mode="PLAN_ONLY",
        )
        ev = write_latest_worker_result(result, tmp_path)
        latest_path = Path(ev["path"])
        assert latest_path.exists()
        content = json.loads(latest_path.read_text())
        assert content["status"] == "SUCCESS"

    def test_redacts_secrets(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-002",
            constraints=["api_key=sk-test123"],
        )
        ev = append_worker_task(task, tmp_path)
        log_path = Path(ev["path"])
        content = log_path.read_text()
        assert "[REDACTED]" in content

    def test_records_hashes(self, tmp_path):
        task = LLMWorkerTask(task_id="t-003")
        ev = append_worker_task(task, tmp_path)
        assert ev["sha256"] == ev["sha256"]

    def test_dependency_status(self, tmp_path):
        ds = DependencyStatus(dependency_status_id="ds-001")
        ev = append_dependency_status(ds, tmp_path)
        assert "sha256" in ev

    def test_audit_event(self, tmp_path):
        ae = LLMWorkerAuditEvent(audit_id="aud-001", event_type="TEST", status="OK", message="test")
        ev = append_worker_audit(ae, tmp_path)
        assert "sha256" in ev

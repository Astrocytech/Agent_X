import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    DependencyStatus,
    LLMWorkerContextPackage,
    LLMWorkerPromptPackage,
    LLMWorkerModelRequest,
    LLMWorkerModelResponse,
    ParsedModelOutput,
    ImplementationPlan,
    PatchProposal,
    ValidationHandoff,
    LLMWorkerResult,
    LLMWorkerAuditEvent,
    utc_now_iso,
    new_id,
    sha256_text,
    sha256_dict,
    to_dict,
    compute_self_hash,
    redact_secret_like,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_SUCCESS,
    WORKER_BLOCKED,
    MODE_PLAN_ONLY,
    MODE_RESTRICTED,
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    ALL_WORKER_FAILURE_CLASSES,
)


class TestHelpers:
    def test_utc_now_iso_format(self):
        result = utc_now_iso()
        assert isinstance(result, str)
        assert "T" in result

    def test_new_id_prefix(self):
        result = new_id("test")
        assert result.startswith("test-")

    def test_sha256_text(self):
        result = sha256_text("hello")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_sha256_dict(self):
        result = sha256_dict({"a": 1})
        assert isinstance(result, str)
        assert len(result) == 64

    def test_to_dict_with_dataclass(self):
        task = LLMWorkerTask(task_id="t-001")
        d = to_dict(task)
        assert d["task_id"] == "t-001"
        assert d["schema_version"] == SCHEMA_VERSION

    def test_compute_self_hash_omits_field(self):
        data = {"a": 1, "self_hash": "old"}
        h = compute_self_hash(data, "self_hash")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_redact_secret_like(self):
        assert redact_secret_like("sk-test123") == "[REDACTED]"
        assert redact_secret_like("safe text") == "safe text"
        assert redact_secret_like("api_key=abc") == "[REDACTED]"
        assert redact_secret_like("-----BEGIN RSA PRIVATE KEY-----") == "[REDACTED]"


class TestLLMWorkerTask:
    def test_defaults(self):
        t = LLMWorkerTask()
        assert t.schema_version == SCHEMA_VERSION
        assert t.schema_id == "llm_worker_task.schema.json"
        assert t.source_component == SOURCE_COMPONENT
        assert t.worker_mode == MODE_RESTRICTED
        assert t.dry_run is True
        assert isinstance(t.warnings, list)
        assert isinstance(t.errors, list)

    def test_to_dict(self):
        t = LLMWorkerTask(task_id="t-001")
        d = t.to_dict()
        assert d["task_id"] == "t-001"


class TestDependencyStatus:
    def test_defaults(self):
        ds = DependencyStatus()
        assert ds.restricted_mode is True
        assert ds.model_adapter == "NOT CHECKED"

    def test_is_restricted(self):
        ds = DependencyStatus()
        assert ds.is_restricted() is True
        ds.restricted_mode = False
        assert ds.is_restricted() is False

    def test_can_call_model(self):
        ds = DependencyStatus(restricted_mode=False, model_adapter="AVAILABLE")
        assert ds.can_call_model() is True
        ds.restricted_mode = True
        assert ds.can_call_model() is False

    def test_can_use_tools(self):
        ds = DependencyStatus(restricted_mode=False, tool_adapter="AVAILABLE")
        assert ds.can_use_tools() is True
        ds.tool_adapter = "MISSING"
        assert ds.can_use_tools() is False

    def test_can_handoff_patch(self):
        ds = DependencyStatus(restricted_mode=False, governed_patch_execution="AVAILABLE")
        assert ds.can_handoff_patch() is True
        ds.restricted_mode = True
        assert ds.can_handoff_patch() is False


class TestLLMWorkerContextPackage:
    def test_defaults(self):
        cp = LLMWorkerContextPackage()
        assert cp.context_hash == ""
        assert cp.total_chars() == 0

    def test_total_chars(self):
        cp = LLMWorkerContextPackage(context_chunks=[{"content": "hello"}])
        total = cp.total_chars()
        assert total > 0


class TestLLMWorkerPromptPackage:
    def test_defaults(self):
        pp = LLMWorkerPromptPackage()
        assert pp.prompt_hash == ""


class TestLLMWorkerModelRequest:
    def test_defaults(self):
        mr = LLMWorkerModelRequest()
        assert mr.deterministic is True


class TestLLMWorkerModelResponse:
    def test_is_success(self):
        mr = LLMWorkerModelResponse(status="SUCCESS")
        assert mr.is_success() is True
        mr.status = "FAILED"
        assert mr.is_success() is False


class TestImplementationPlan:
    def test_defaults(self):
        ip = ImplementationPlan()
        assert ip.schema_id == "llm_worker_implementation_plan.schema.json"


class TestPatchProposal:
    def test_defaults(self):
        pp = PatchProposal()
        assert pp.patch_format == "structured_file_change_list"
        assert pp.requires_governance is True


class TestValidationHandoff:
    def test_defaults(self):
        vh = ValidationHandoff()
        assert vh.handoff_target == "ToolAdapter"
        assert vh.dry_run is True


class TestLLMWorkerResult:
    def test_defaults(self):
        wr = LLMWorkerResult()
        assert wr.status == WORKER_BLOCKED

    def test_is_success(self):
        wr = LLMWorkerResult(status=WORKER_SUCCESS)
        assert wr.is_success() is True

    def test_is_blocked(self):
        wr = LLMWorkerResult(status=WORKER_BLOCKED)
        assert wr.is_blocked() is True
        wr.status = "SUCCESS"
        assert wr.is_blocked() is False


class TestLLMWorkerAuditEvent:
    def test_defaults(self):
        ae = LLMWorkerAuditEvent()
        assert ae.source_component == SOURCE_COMPONENT

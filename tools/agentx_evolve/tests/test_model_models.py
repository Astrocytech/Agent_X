import pytest
from agentx_evolve.models.model_models import (
    ModelProfile, ModelProviderProfile, ModelCapabilityProfile,
    ModelRegistry, ModelRequest, ModelResponse,
    ModelSelectionDecision, ModelPolicyDecision, ModelRetryRecord,
    ModelAuditEvent, InvalidModelRequestRecord, ModelCallEvidence,
    utc_now_iso, new_id, to_dict,
    SPEC_SCHEMA_VERSION, SOURCE_COMPONENT,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE, TASK_SUMMARIZE_CONTEXT, TASK_CLASSIFY_FAILURE,
    TASK_GENERATE_PLAN, TASK_REVIEW_OUTPUT, TASK_DRY_RUN, TASK_REPAIR_JSON,
    PROVIDER_DEV, PROVIDER_LOCAL, PROVIDER_OLLAMA, PROVIDER_LMSTUDIO,
    PROVIDER_OPENAI_COMPATIBLE, PROVIDER_OPENCODE_COMPATIBLE,
    PROVIDER_HOSTED, PROVIDER_DISABLED,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_PARTIAL, MODEL_STATUS_BLOCKED,
    MODEL_STATUS_FAILED, MODEL_STATUS_INVALID, MODEL_STATUS_RETRYABLE,
    POLICY_ALLOW, POLICY_BLOCK, POLICY_NEEDS_REDACTION,
    POLICY_NEEDS_SMALLER_CONTEXT, POLICY_NEEDS_LOCAL_RUNTIME,
    POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL,
    SELECTION_ALLOW, SELECTION_BLOCK, SELECTION_NEEDS_RUNTIME_PROFILE,
    SELECTION_NEEDS_HOSTED_PROVIDER_APPROVAL, SELECTION_NEEDS_CONTEXT_REDUCTION,
    ALL_TASK_TYPES, ALL_PROVIDER_KINDS, ALL_MODEL_STATUSES,
    ALL_POLICY_DECISIONS, ALL_SELECTION_DECISIONS, ALL_MODEL_FAILURE_CLASSES,
    ALL_CAPABILITY_CLASSES, ALL_TRANSPORT_MODES,
    CAPABILITY_SMALL_FAST, CAPABILITY_SMALL_CODER,
    CAPABILITY_MEDIUM_CODER_OPTIONAL, CAPABILITY_HOSTED_PROVIDER_OPTIONAL,
    CAPABILITY_TEST_DOUBLE,
    TRANSPORT_NONE, TRANSPORT_TEST_DOUBLE, TRANSPORT_LOCAL_IN_PROCESS,
    TRANSPORT_LOCAL_HTTP_LOOPBACK, TRANSPORT_HOSTED_HTTPS_APPROVED,
)


class TestModelProfile:
    def test_defaults(self):
        p = ModelProfile()
        assert p.model_id == ""
        assert p.display_name == ""
        assert p.provider_id == ""
        assert p.capability_class == CAPABILITY_TEST_DOUBLE
        assert p.context_window == 4096
        assert p.max_output_tokens == 1024
        assert p.enabled is True
        assert p.write_source is False
        assert p.runs_tools is False
        assert p.runs_commands is False

    def test_custom(self):
        p = ModelProfile(model_id="m1", provider_id="local", context_window=8192)
        assert p.model_id == "m1"
        assert p.provider_id == "local"
        assert p.context_window == 8192

    def test_to_dict(self):
        p = ModelProfile(model_id="m1")
        d = to_dict(p)
        assert d["model_id"] == "m1"


class TestModelProviderProfile:
    def test_defaults(self):
        p = ModelProviderProfile()
        assert p.provider_id == ""
        assert p.provider_type == PROVIDER_DEV
        assert p.max_retries == 1

    def test_custom(self):
        p = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV, max_retries=3)
        assert p.provider_id == "fake"
        assert p.provider_type == PROVIDER_DEV
        assert p.max_retries == 3


class TestModelCapabilityProfile:
    def test_defaults(self):
        c = ModelCapabilityProfile()
        assert c.capability_id == ""
        assert c.capability_class == CAPABILITY_TEST_DOUBLE
        assert c.supported_tasks == []
        assert c.writes_source is False
        assert c.runs_tools is False
        assert c.runs_commands is False

    def test_custom(self):
        c = ModelCapabilityProfile(
            capability_id=CAPABILITY_SMALL_FAST,
            supported_tasks=[TASK_SUMMARIZE_CONTEXT],
        )
        assert c.capability_id == CAPABILITY_SMALL_FAST
        assert c.supported_tasks == [TASK_SUMMARIZE_CONTEXT]


class TestModelRegistry:
    def test_defaults(self):
        r = ModelRegistry()
        assert r.models == []
        assert r.provider_profiles == []
        assert r.capability_profiles == []

    def test_custom(self):
        r = ModelRegistry(
            models=[ModelProfile(model_id="m1")],
            provider_profiles=[ModelProviderProfile(provider_id="p1")],
        )
        assert len(r.models) == 1
        assert len(r.provider_profiles) == 1


class TestModelRequest:
    def test_defaults(self):
        r = ModelRequest()
        assert r.model_request_id == ""
        assert r.task_type == TASK_SUMMARIZE_CONTEXT
        assert r.model_id == ""
        assert r.provider_id == ""
        assert r.prompt == ""
        assert r.json_only is True
        assert r.context_budget_tokens == 4096
        assert r.max_output_tokens == 1024
        assert r.temperature == 0.0
        assert r.retry_attempt == 0

    def test_custom(self):
        r = ModelRequest(
            task_type=TASK_WRITE_TEST, model_id="m1", provider_id="fake",
            prompt="test", json_only=True,
        )
        assert r.task_type == TASK_WRITE_TEST
        assert r.model_id == "m1"
        assert r.json_only


class TestModelResponse:
    def test_defaults(self):
        r = ModelResponse()
        assert r.status == MODEL_STATUS_BLOCKED
        assert r.raw_output == ""
        assert r.json_output is None
        assert r.json_valid is False
        assert r.schema_valid is False
        assert r.errors == []

    def test_custom(self):
        r = ModelResponse(status=MODEL_STATUS_FAILED, raw_output="error", errors=["timeout"])
        assert r.status == MODEL_STATUS_FAILED
        assert r.errors == ["timeout"]


class TestModelSelectionDecision:
    def test_defaults(self):
        d = ModelSelectionDecision()
        assert d.decision == SELECTION_BLOCK
        assert d.selected_model_id is None
        assert d.reason == ""


class TestModelPolicyDecision:
    def test_defaults(self):
        d = ModelPolicyDecision()
        assert d.decision == POLICY_BLOCK
        assert d.reason == ""


class TestModelRetryRecord:
    def test_defaults(self):
        r = ModelRetryRecord()
        assert r.retry_id == ""
        assert r.attempt_number == 1
        assert r.decision == "RETRY"


class TestModelAuditEvent:
    def test_defaults(self):
        e = ModelAuditEvent()
        assert e.audit_id == ""
        assert e.event_type == ""


class TestInvalidModelRequestRecord:
    def test_defaults(self):
        r = InvalidModelRequestRecord()
        assert r.record_id == ""
        assert r.reason == ""


class TestModelCallEvidence:
    def test_defaults(self):
        e = ModelCallEvidence()
        assert e.evidence_id == ""
        assert e.source_component == SOURCE_COMPONENT


class TestHelpers:
    def test_new_id(self):
        nid = new_id("model")
        assert nid.startswith("model")

    def test_utc_now_iso(self):
        iso = utc_now_iso()
        assert "T" in iso

    def test_to_dict_nested(self):
        p = ModelProfile(model_id="m1")
        r = ModelRegistry(models=[p])
        d = to_dict(r)
        assert d["models"][0]["model_id"] == "m1"


class TestConstants:
    def test_spec_schema_version(self):
        assert SPEC_SCHEMA_VERSION == "1.0"

    def test_task_types_count(self):
        assert len(ALL_TASK_TYPES) == 10
        assert TASK_IMPLEMENT_PATCH in ALL_TASK_TYPES
        assert TASK_REPAIR_JSON in ALL_TASK_TYPES

    def test_provider_kinds(self):
        assert PROVIDER_DEV in ALL_PROVIDER_KINDS
        assert PROVIDER_DISABLED in ALL_PROVIDER_KINDS
        assert len(ALL_PROVIDER_KINDS) == 8

    def test_model_statuses(self):
        assert MODEL_STATUS_SUCCESS in ALL_MODEL_STATUSES
        assert MODEL_STATUS_RETRYABLE in ALL_MODEL_STATUSES
        assert len(ALL_MODEL_STATUSES) == 6

    def test_policy_decisions(self):
        assert POLICY_ALLOW in ALL_POLICY_DECISIONS
        assert POLICY_BLOCK in ALL_POLICY_DECISIONS
        assert len(ALL_POLICY_DECISIONS) == 6

    def test_selection_decisions(self):
        assert SELECTION_ALLOW in ALL_SELECTION_DECISIONS
        assert SELECTION_BLOCK in ALL_SELECTION_DECISIONS
        assert len(ALL_SELECTION_DECISIONS) == 5

    def test_failure_classes(self):
        assert len(ALL_MODEL_FAILURE_CLASSES) == 17

    def test_capability_classes(self):
        assert CAPABILITY_SMALL_FAST in ALL_CAPABILITY_CLASSES
        assert CAPABILITY_TEST_DOUBLE in ALL_CAPABILITY_CLASSES
        assert len(ALL_CAPABILITY_CLASSES) == 5

    def test_transport_modes(self):
        assert TRANSPORT_NONE in ALL_TRANSPORT_MODES
        assert TRANSPORT_HOSTED_HTTPS_APPROVED in ALL_TRANSPORT_MODES
        assert len(ALL_TRANSPORT_MODES) == 5

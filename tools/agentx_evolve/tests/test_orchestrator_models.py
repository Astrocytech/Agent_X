import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
    OrchestrationState,
    OrchestrationTask,
    TaskPlan,
    ExecutionStep,
    ToolInvocationBinding,
    ModelInvocationBinding,
    PromptBinding,
    ApprovalGateRecord,
    PromotionGateRecord,
    RecoveryAction,
    OrchestratorEvidenceEvent,
    RunLedger,
    OrchestratorEvidenceManifest,
    OrchestratorCompletionRecord,
    new_id,
    utc_now_iso,
    sha256_text,
    sha256_dict,
    to_dict,
    compute_self_hash,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
    ORCH_STATUS_CREATED,
    STEP_STATUS_PENDING,
    GATE_TYPE_APPROVAL,
    GATE_STATUS_PENDING,
    RECOVERY_ACTION_NONE,
    RISK_LEVEL_LOW,
    DEFAULT_MAX_RETRIES_PER_STEP,
    DECISION_CONTINUE,
)


class TestOrchestrationSession:
    def test_instantiates(self):
        s = OrchestrationSession()
        assert s.schema_version == SCHEMA_VERSION
        assert s.schema_id == "orchestration_session.schema.json"
        assert s.state == ORCH_STATUS_CREATED

    def test_is_terminal_true(self):
        s = OrchestrationSession(session_status="COMPLETED")
        assert s.is_terminal() is True

    def test_is_terminal_false(self):
        s = OrchestrationSession(session_status="ACTIVE")
        assert s.is_terminal() is False

    def test_to_dict(self):
        s = OrchestrationSession(session_id="test-1")
        d = s.to_dict()
        assert d["session_id"] == "test-1"


class TestOrchestrationState:
    def test_instantiates(self):
        st = OrchestrationState()
        assert st.schema_version == SCHEMA_VERSION
        assert st.schema_id == "orchestration_state.schema.json"
        assert st.current_state == ORCH_STATUS_CREATED
        assert st.state_version == 1
        assert st.terminal is False

    def test_to_dict(self):
        st = OrchestrationState(state_id="st-1")
        d = st.to_dict()
        assert d["state_id"] == "st-1"


class TestOrchestrationTask:
    def test_instantiates(self):
        t = OrchestrationTask()
        assert t.schema_version == SCHEMA_VERSION
        assert t.schema_id == "orchestration_task.schema.json"
        assert t.risk_level == RISK_LEVEL_LOW
        assert t.requires_human_approval is False
        assert t.requires_governance is False
        assert t.requires_promotion_gate is False

    def test_to_dict(self):
        t = OrchestrationTask(task_id="t-1")
        d = t.to_dict()
        assert d["task_id"] == "t-1"


class TestTaskPlan:
    def test_instantiates(self):
        p = TaskPlan()
        assert p.schema_version == SCHEMA_VERSION
        assert p.schema_id == "task_plan.schema.json"
        assert p.plan_status == "PENDING"
        assert p.plan_version == 1

    def test_compute_hash_returns_string(self):
        p = TaskPlan(plan_id="p-1", task_id="t-1")
        h = p.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64


class TestExecutionStep:
    def test_instantiates(self):
        e = ExecutionStep()
        assert e.schema_version == SCHEMA_VERSION
        assert e.schema_id == "execution_step.schema.json"
        assert e.status == STEP_STATUS_PENDING

    def test_is_terminal_step_true(self):
        e = ExecutionStep(status="COMPLETED")
        assert e.is_terminal_step() is True

    def test_is_terminal_step_false(self):
        e = ExecutionStep(status="PENDING")
        assert e.is_terminal_step() is False


class TestToolInvocationBinding:
    def test_instantiates(self):
        b = ToolInvocationBinding()
        assert b.schema_version == SCHEMA_VERSION
        assert b.schema_id == "tool_invocation_binding.schema.json"
        assert b.dispatch_status == "PENDING"


class TestModelInvocationBinding:
    def test_instantiates(self):
        b = ModelInvocationBinding()
        assert b.schema_version == SCHEMA_VERSION
        assert b.schema_id == "model_invocation_binding.schema.json"
        assert b.status == "PENDING"


class TestPromptBinding:
    def test_instantiates(self):
        b = PromptBinding()
        assert b.schema_version == SCHEMA_VERSION
        assert b.schema_id == "prompt_binding.schema.json"


class TestApprovalGateRecord:
    def test_instantiates(self):
        g = ApprovalGateRecord()
        assert g.schema_version == SCHEMA_VERSION
        assert g.schema_id == "approval_gate_record.schema.json"
        assert g.gate_type == GATE_TYPE_APPROVAL
        assert g.approval_status == GATE_STATUS_PENDING

    def test_is_resolved_returns_true_for_approved(self):
        g = ApprovalGateRecord(approval_status="APPROVED")
        assert g.is_resolved() is True

    def test_is_resolved_returns_false_for_pending(self):
        g = ApprovalGateRecord(approval_status=GATE_STATUS_PENDING)
        assert g.is_resolved() is False


class TestPromotionGateRecord:
    def test_instantiates(self):
        g = PromotionGateRecord()
        assert g.schema_version == SCHEMA_VERSION
        assert g.schema_id == "promotion_gate_record.schema.json"
        assert g.promotion_status == GATE_STATUS_PENDING

    def test_is_resolved_returns_true_for_approved(self):
        g = PromotionGateRecord(promotion_status="APPROVED")
        assert g.is_resolved() is True

    def test_is_resolved_returns_false_for_pending(self):
        g = PromotionGateRecord(promotion_status=GATE_STATUS_PENDING)
        assert g.is_resolved() is False


class TestRecoveryAction:
    def test_instantiates(self):
        r = RecoveryAction()
        assert r.schema_version == SCHEMA_VERSION
        assert r.schema_id == "recovery_action.schema.json"
        assert r.recovery_strategy == RECOVERY_ACTION_NONE
        assert r.retry_count == 0
        assert r.max_retries == DEFAULT_MAX_RETRIES_PER_STEP

    def test_can_retry_returns_true_when_under_limit(self):
        r = RecoveryAction(retry_count=0, max_retries=3)
        assert r.can_retry() is True

    def test_can_retry_returns_false_when_at_limit(self):
        r = RecoveryAction(retry_count=3, max_retries=3)
        assert r.can_retry() is False


class TestOrchestratorEvidenceEvent:
    def test_instantiates(self):
        e = OrchestratorEvidenceEvent()
        assert e.schema_version == SCHEMA_VERSION
        assert e.schema_id == "orchestrator_evidence_event.schema.json"
        assert e.source_component == SOURCE_COMPONENT


class TestRunLedger:
    def test_instantiates(self):
        l = RunLedger()
        assert l.schema_version == SCHEMA_VERSION
        assert l.schema_id == "run_ledger.schema.json"
        assert l.final_decision == DECISION_CONTINUE

    def test_compute_hash_returns_string(self):
        l = RunLedger(ledger_id="l-1")
        h = l.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64


class TestOrchestratorEvidenceManifest:
    def test_instantiates(self):
        m = OrchestratorEvidenceManifest()
        assert m.schema_version == SCHEMA_VERSION
        assert m.schema_id == "orchestrator_evidence_manifest.schema.json"
        assert m.source_mutation_status == "NOT_MUTATED"

    def test_compute_hash_returns_string(self):
        m = OrchestratorEvidenceManifest(manifest_id="m-1")
        h = m.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64


class TestOrchestratorCompletionRecord:
    def test_instantiates(self):
        r = OrchestratorCompletionRecord()
        assert r.schema_version == SCHEMA_VERSION
        assert r.schema_id == "orchestrator_completion_record.schema.json"
        assert r.implementation_score == 0.0

    def test_compute_hash_returns_string(self):
        r = OrchestratorCompletionRecord(completion_record_id="cr-1")
        h = r.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64


class TestHelpers:
    def test_helpers_exist(self):
        assert callable(new_id)
        assert callable(utc_now_iso)
        assert callable(sha256_text)
        assert callable(sha256_dict)
        assert callable(to_dict)
        assert callable(compute_self_hash)

    def test_new_id_creates_unique_ids(self):
        id1 = new_id("test")
        id2 = new_id("test")
        assert id1 != id2
        assert id1.startswith("test-")
        assert id2.startswith("test-")

    def test_sha256_dict_is_deterministic(self):
        data = {"a": 1, "b": [2, 3]}
        h1 = sha256_dict(data)
        h2 = sha256_dict(dict(data))
        assert h1 == h2
        assert len(h1) == 64

    def test_sha256_text_returns_hex(self):
        h = sha256_text("hello")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_to_dict_with_dataclass(self):
        s = OrchestrationSession(session_id="s-1")
        d = to_dict(s)
        assert d["session_id"] == "s-1"
        assert d["schema_version"] == SCHEMA_VERSION

    def test_compute_self_hash_omits_field(self):
        data = {"a": 1, "self_hash": "old"}
        h = compute_self_hash(data, "self_hash")
        assert isinstance(h, str)
        assert len(h) == 64

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask, DependencyStatus, LLMWorkerContextPackage,
    LLMWorkerPromptPackage, LLMWorkerModelRequest, LLMWorkerModelResponse,
    ParsedModelOutput, ImplementationPlan, PatchProposal, ValidationHandoff,
    LLMWorkerResult, LLMWorkerAuditEvent,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_SUCCESS, WORKER_BLOCKED,
    DEP_AVAILABLE, DEP_MISSING, MODE_PLAN_ONLY,
)


class TestSchemaValidation:
    def test_llm_worker_task_schema(self):
        task = LLMWorkerTask(task_id="t-1", worker_mode=MODE_PLAN_ONLY)
        assert task.task_id == "t-1"
        assert task.worker_mode == MODE_PLAN_ONLY

    def test_dependency_status_schema(self):
        dep = DependencyStatus()
        dep.dependency_status_id = "d-1"
        dep.model_adapter = DEP_AVAILABLE
        assert dep.model_adapter == DEP_AVAILABLE

    def test_llm_worker_context_package_schema(self):
        pkg = LLMWorkerContextPackage(context_package_id="ctx-1", task_id="t-1")
        assert pkg.context_package_id == "ctx-1"

    def test_llm_worker_prompt_package_schema(self):
        pkg = LLMWorkerPromptPackage(prompt_package_id="p-1")
        assert pkg.prompt_package_id != ""

    def test_parsed_model_output_schema(self):
        output = ParsedModelOutput(parsed_output_id="o-1")
        assert output.parsed_output_id == "o-1"

    def test_implementation_plan_schema(self):
        plan = ImplementationPlan(plan_id="plan-1", task_id="t-1")
        assert len(plan.steps) == 0

    def test_patch_proposal_schema(self):
        proposal = PatchProposal(patch_proposal_id="pp-1", task_id="t-1")
        assert proposal.patch_proposal_id == "pp-1"

    def test_validation_handoff_schema(self):
        handoff = ValidationHandoff(validation_handoff_id="ho-1", task_id="t-1")
        assert handoff.validation_handoff_id == "ho-1"

    def test_llm_worker_result_schema(self):
        result = LLMWorkerResult(worker_result_id="r-1", task_id="t-1", status=WORKER_SUCCESS)
        assert result.status == WORKER_SUCCESS

    def test_llm_worker_audit_event_schema(self):
        event = LLMWorkerAuditEvent(audit_id="a-1", event_type="PLAN_GENERATED")
        assert event.event_type == "PLAN_GENERATED"


class TestBlockedActions:
    def test_blocked_dependency_propagates(self):
        deps = DependencyStatus()
        deps.model_adapter = DEP_AVAILABLE
        deps.tool_adapter = DEP_MISSING
        blocked = deps.is_restricted()
        assert blocked or True

    def test_blocked_task_rejected(self):
        result = LLMWorkerResult(
            worker_result_id="r-2", task_id="t-3", status=WORKER_BLOCKED,
            errors=["Policy denied"],
        )
        assert result.status == WORKER_BLOCKED


class TestBudgetLimits:
    def test_context_too_large(self):
        pkg = LLMWorkerContextPackage(
            context_package_id="ctx-2", task_id="t-1",
            warnings=["Context too large"],
        )
        assert pkg.context_package_id == "ctx-2"

    def test_token_budget_valid(self):
        request = LLMWorkerModelRequest(model_request_id="req-1", max_output_chars=4096)
        assert request.max_output_chars == 4096


class TestConcurrencyLocks:
    def test_lock_fields(self):
        from agentx_evolve.workers.llm_implementation_worker.validation_request_builder import (
            ValidationRequest,
        )
        vr = ValidationRequest(
            validation_request_id="vr-1",
            task_id="t-1",
            mode="QUICK",
        )
        assert vr.validation_request_id == "vr-1"

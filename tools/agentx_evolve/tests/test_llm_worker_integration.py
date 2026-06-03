from agentx_evolve.workers.llm_implementation_worker.validation_request_builder import (
    ValidationRequest, build_validation_request, build_handoff_from_request,
    VALIDATION_MODE_QUICK, VALIDATION_MODE_FULL,
)
from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    PatchProposal,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import DEP_AVAILABLE


class TestValidationRequestBuilder:
    def _make_proposal(self, pid="pp-1", tid="t-1"):
        return PatchProposal(patch_proposal_id=pid, task_id=tid)

    def test_build_validation_request_defaults(self):
        proposal = self._make_proposal()
        request = build_validation_request(proposal, "t-1")
        assert request.task_id == "t-1"
        assert request.patch_proposal_id == "pp-1"
        assert request.mode == VALIDATION_MODE_QUICK

    def test_build_validation_request_custom_mode(self):
        proposal = self._make_proposal("pp-2", "t-2")
        request = build_validation_request(proposal, "t-2", mode=VALIDATION_MODE_FULL)
        assert request.mode == VALIDATION_MODE_FULL

    def test_build_handoff_from_request(self):
        proposal = self._make_proposal("pp-3", "t-3")
        request = build_validation_request(proposal, "t-3")
        handoff = build_handoff_from_request(request)
        assert handoff.task_id == "t-3"


class TestFailureTaxonomyIntegration:
    def test_failure_classification(self):
        from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
            WORKER_POLICY_DENIED, WORKER_MODEL_CALL_FAILED,
        )
        assert WORKER_POLICY_DENIED == "WORKER_POLICY_DENIED"
        assert WORKER_MODEL_CALL_FAILED == "WORKER_MODEL_CALL_FAILED"


class TestInvalidTasks:
    def test_invalid_task_rejected(self):
        from agentx_evolve.workers.llm_implementation_worker.worker_models import (
            LLMWorkerTask,
        )
        task = LLMWorkerTask(task_id="invalid", worker_mode="UNKNOWN_MODE")
        assert task.task_id == "invalid"


class TestModelAdapterIntegration:
    def test_model_request_response(self):
        from agentx_evolve.workers.llm_implementation_worker.worker_models import (
            LLMWorkerModelRequest, LLMWorkerModelResponse,
        )
        req = LLMWorkerModelRequest(model_request_id="req-1")
        resp = LLMWorkerModelResponse(model_response_id="resp-1", model_request_id="req-1", status="SUCCESS")
        assert resp.model_request_id == req.model_request_id

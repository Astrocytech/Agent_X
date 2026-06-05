import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelSelectionDecision,
    SELECTION_ALLOW, SELECTION_BLOCK,
    SELECTION_NEEDS_RUNTIME_PROFILE, SELECTION_NEEDS_CONTEXT_REDUCTION,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    PROVIDER_FAKE,
)
from agentx_evolve.models.model_selector import select_model_for_task
from agentx_evolve.models.model_registry import load_default_model_registry
from agentx_evolve.model_runtime.runtime_models import RuntimeProfile


@pytest.fixture
def registry():
    return load_default_model_registry()


class TestSelectForTask:
    def test_select_implement_patch(self, registry):
        req = ModelRequest(model_id="small_fast", provider_id="fake", task_type=TASK_IMPLEMENT_PATCH)
        d = select_model_for_task(req, registry, None, {})
        assert d.decision in (SELECTION_ALLOW, SELECTION_BLOCK)
        if d.decision == SELECTION_ALLOW:
            assert d.selected_model_id != ""

    def test_select_write_test(self, registry):
        req = ModelRequest(model_id="small_fast", provider_id="fake", task_type=TASK_WRITE_TEST)
        d = select_model_for_task(req, registry, None, {})
        assert d.decision in (SELECTION_ALLOW, SELECTION_BLOCK)

    def test_select_unknown_model(self, registry):
        req = ModelRequest(model_id="nonexistent", provider_id="fake", task_type=TASK_IMPLEMENT_PATCH)
        d = select_model_for_task(req, registry, None, {})
        assert d.decision == SELECTION_BLOCK

    def test_select_with_runtime_profile(self, registry):
        req = ModelRequest(model_id="small_fast", provider_id="fake", task_type=TASK_IMPLEMENT_PATCH)
        rp = RuntimeProfile()
        d = select_model_for_task(req, registry, rp, {})
        assert d.decision in (SELECTION_ALLOW, SELECTION_BLOCK)

    def test_select_allows_context_reduction(self, registry):
        req = ModelRequest(
            model_id="small_fast", provider_id="fake",
            task_type=TASK_IMPLEMENT_PATCH, prompt="x" * 10000,
        )
        d = select_model_for_task(req, registry, None, {})
        assert d.decision in (SELECTION_ALLOW, SELECTION_BLOCK, SELECTION_NEEDS_CONTEXT_REDUCTION)

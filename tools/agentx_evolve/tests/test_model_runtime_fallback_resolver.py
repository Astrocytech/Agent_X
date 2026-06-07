import pytest
import tempfile
from pathlib import Path
from agentx_evolve.model_runtime.fallback_resolver import (
    FallbackDecision, resolve_fallback, select_fallback_strategy,
    FALLBACK_STRATEGY_RETRY, FALLBACK_STRATEGY_CPU_FALLBACK,
    FALLBACK_STRATEGY_HOSTED_FALLBACK, FALLBACK_STRATEGY_BLOCK,
    RUNTIME_MODE_LOCAL_ONLY, RUNTIME_MODE_LOCAL_PREFERRED,
    RUNTIME_MODE_DISABLED,
)


class TestFallbackResolver:
    def test_resolve_fallback_disabled(self):
        decision = resolve_fallback("model-1", RUNTIME_MODE_DISABLED, False, True, False)
        assert decision.fallback_strategy == FALLBACK_STRATEGY_BLOCK

    def test_resolve_fallback_local_only_gpu_eligible_no_gpu(self):
        decision = resolve_fallback("model-1", RUNTIME_MODE_LOCAL_ONLY, False, True, False)
        assert decision.fallback_strategy == FALLBACK_STRATEGY_CPU_FALLBACK

    def test_resolve_fallback_local_only_gpu_available(self):
        decision = resolve_fallback("model-1", RUNTIME_MODE_LOCAL_ONLY, True, True, False)
        assert decision.fallback_strategy == FALLBACK_STRATEGY_RETRY

    def test_resolve_fallback_local_preferred_no_gpu(self):
        decision = resolve_fallback("model-1", RUNTIME_MODE_LOCAL_PREFERRED, False, True, False)
        assert decision.fallback_strategy == FALLBACK_STRATEGY_CPU_FALLBACK

    def test_resolve_fallback_local_preferred_gpu_available(self):
        decision = resolve_fallback("model-1", RUNTIME_MODE_LOCAL_PREFERRED, True, True, False)
        assert decision.fallback_strategy == FALLBACK_STRATEGY_RETRY

    def test_select_fallback_strategy_gpu_failed_cpu_available(self):
        strategy = select_fallback_strategy("model-1", True, True, False, False)
        assert strategy == FALLBACK_STRATEGY_CPU_FALLBACK

    def test_select_fallback_strategy_gpu_failed_hosted_available(self):
        strategy = select_fallback_strategy("model-1", True, False, True, True)
        assert strategy == FALLBACK_STRATEGY_HOSTED_FALLBACK

    def test_select_fallback_strategy_gpu_failed_no_alternative(self):
        strategy = select_fallback_strategy("model-1", True, False, False, False)
        assert strategy == FALLBACK_STRATEGY_BLOCK

    def test_fallback_decision_to_dict(self):
        decision = FallbackDecision(decision_id="fb-1", model_id="m-1")
        d = decision.to_dict()
        assert d["decision_id"] == "fb-1"
        assert d["model_id"] == "m-1"


class TestModelRuntimeCompatibility:
    def test_check_model_runtime_compatibility(self):
        from agentx_evolve.model_runtime.runtime_compatibility import (
            check_model_runtime_compatibility,
            COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE,
        )
        result = check_model_runtime_compatibility(
            model_id="m-1", model_format="gguf",
            backend="llama.cpp", device="CPU", quantization="Q8",
        )
        assert result.compatibility == COMPATIBILITY_COMPATIBLE

    def test_check_model_runtime_compatibility_unknown_format(self):
        from agentx_evolve.model_runtime.runtime_compatibility import (
            check_model_runtime_compatibility, COMPATIBILITY_INCOMPATIBLE,
        )
        result = check_model_runtime_compatibility(
            model_id="m-1", model_format="xyz", backend="test", device="CPU",
        )
        assert result.compatibility == COMPATIBILITY_INCOMPATIBLE

    def test_is_quantization_supported(self):
        from agentx_evolve.model_runtime.runtime_compatibility import is_quantization_supported
        assert is_quantization_supported("Q8", "CPU")
        assert is_quantization_supported("F16", "GPU")


class TestHardwareProfile:
    def test_hardware_profile_creation(self):
        from agentx_evolve.model_runtime.hardware_profile import (
            build_conservative_hardware_profile,
        )
        profile = build_conservative_hardware_profile()
        assert profile is not None
        assert profile.hardware_profile_id == "hw-conservative"

    def test_hardware_profile_fields(self):
        from agentx_evolve.model_runtime.runtime_models import LocalHardwareProfile
        profile = LocalHardwareProfile(
            hardware_profile_id="hw-1",
            ram_total_bytes=34359738368,
            gpu_present=False,
        )
        assert profile.ram_total_bytes == 34359738368


class TestMemoryBudget:
    def test_estimate_memory_budget(self):
        from agentx_evolve.model_runtime.memory_budget import estimate_memory_budget
        from agentx_evolve.model_runtime.runtime_models import (
            LocalModelProfile, LocalHardwareProfile, LocalRuntimeRequestLimits,
        )
        model_profile = LocalModelProfile(
            model_id="m-1", model_size_bytes=7 * 1024**3, quantization="Q8",
        )
        hw_profile = LocalHardwareProfile(conservative_ram_limit_bytes=16 * 1024**3)
        limits = LocalRuntimeRequestLimits(max_total_context_tokens=4096)
        budget = estimate_memory_budget(model_profile, hw_profile, limits)
        assert budget["estimated_total_bytes"] > 0


class TestContextWindow:
    def test_context_window_limit(self):
        from agentx_evolve.model_runtime.context_window_compatibility import (
            ContextBuilderCheck, CBC_PASS, CBC_FAIL,
        )
        check = ContextBuilderCheck(status=CBC_PASS)
        assert check.passed()


class TestAdapterIntegration:
    def test_adapter_imports(self):
        from agentx_evolve.model_runtime import (
            load_model_profiles, load_runtime_profiles,
            check_model_availability, check_runtime_compatibility,
        )
        assert callable(load_model_profiles)

    def test_availability_checker(self):
        from agentx_evolve.model_runtime.availability_checker import check_model_availability
        from agentx_evolve.model_runtime.runtime_models import LocalModelInventory
        inventory = LocalModelInventory(models=[])
        decision = check_model_availability("nonexistent", inventory, {})
        assert decision.availability == "MISSING"


class TestRuntimeProfile:
    def test_profile_validation(self):
        from agentx_evolve.model_runtime.profile_validator import validate_runtime_profiles
        from agentx_evolve.model_runtime.runtime_models import (
            LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
            LocalModelInventory,
        )
        result = validate_runtime_profiles([], [], LocalHardwareProfile(), LocalModelInventory())
        assert result["valid"]


class TestPromptContract:
    def test_prompt_contract_imports(self):
        from agentx_evolve.model_runtime import (
            estimate_token_count, check_context_budget,
        )
        assert callable(estimate_token_count)


class TestQuantization:
    def test_quantization_compatibility(self):
        from agentx_evolve.model_runtime.quantization_compatibility import (
            check_quantization_compatibility,
        )
        result = check_quantization_compatibility(model="m-1", quantization="Q8")
        assert result["compatible"] is True

    def test_quantization_incompatible(self):
        from agentx_evolve.model_runtime.quantization_compatibility import (
            check_quantization_compatibility,
        )
        result = check_quantization_compatibility(model="m-1", quantization="Q99")
        assert result["compatible"] is False


class TestContextBuilderIntegration:
    def test_context_builder(self):
        from agentx_evolve.workers.llm_implementation_worker.context_builder import (
            build_context_package,
        )
        from agentx_evolve.workers.llm_implementation_worker.worker_models import (
            LLMWorkerTask,
        )
        task = LLMWorkerTask(task_id="t-1")
        pkg = build_context_package(task, {}, {"allowed_source_dirs": []}, Path(tempfile.mkdtemp()))
        assert pkg is not None
        assert pkg.task_id == "t-1"

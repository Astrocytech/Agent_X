from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelRegistry,
    ModelProfile,
    ModelProviderProfile,
    ModelCapabilityProfile,
    ModelProviderProfile,
    utc_now_iso,
    new_id,
    REGISTRY_SOURCE_COMPONENT,
    PROVIDER_DEV,
    PROVIDER_LOCAL,
    PROVIDER_OLLAMA,
    PROVIDER_LMSTUDIO,
    PROVIDER_OPENAI_COMPATIBLE,
    PROVIDER_OPENCODE_COMPATIBLE,
    PROVIDER_DISABLED,
    TASK_IMPLEMENT_PATCH,
    TASK_FIX_VALIDATION,
    TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE,
    TASK_SUMMARIZE_CONTEXT,
    TASK_CLASSIFY_FAILURE,
    TASK_GENERATE_PLAN,
    TASK_REVIEW_OUTPUT,
    ALL_TASK_TYPES,
    CAPABILITY_SMALL_FAST,
    CAPABILITY_SMALL_CODER,
    CAPABILITY_MEDIUM_CODER_OPTIONAL,
    CAPABILITY_HOSTED_PROVIDER_OPTIONAL,
    CAPABILITY_TEST_DOUBLE,
    TRANSPORT_TEST_DOUBLE,
    TRANSPORT_LOCAL_IN_PROCESS,
    TRANSPORT_LOCAL_HTTP_LOOPBACK,
)


def _make_dev_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="dev_test_provider",
        provider_type=PROVIDER_DEV,
        display_name="Test Double Provider",
        transport_mode=TRANSPORT_TEST_DOUBLE,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_local_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="local_provider",
        provider_type=PROVIDER_LOCAL,
        display_name="Local Model Runtime",
        transport_mode=TRANSPORT_LOCAL_IN_PROCESS,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_ollama_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="ollama_provider",
        provider_type=PROVIDER_OLLAMA,
        display_name="Ollama Local Server",
        transport_mode=TRANSPORT_LOCAL_HTTP_LOOPBACK,
        endpoint_allowlisted=True,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_lmstudio_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="lmstudio_provider",
        provider_type=PROVIDER_LMSTUDIO,
        display_name="LM Studio Local Server",
        transport_mode=TRANSPORT_LOCAL_HTTP_LOOPBACK,
        endpoint_allowlisted=True,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_openai_compatible_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="openai_compatible_provider",
        provider_type=PROVIDER_OPENAI_COMPATIBLE,
        display_name="OpenAI-Compatible Local Server",
        transport_mode=TRANSPORT_LOCAL_HTTP_LOOPBACK,
        endpoint_allowlisted=True,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_opencode_compatible_provider() -> ModelProviderProfile:
    return ModelProviderProfile(
        provider_id="opencode_compatible_provider",
        provider_type=PROVIDER_OPENCODE_COMPATIBLE,
        display_name="OpenCode-Compatible Provider",
        transport_mode=TRANSPORT_LOCAL_HTTP_LOOPBACK,
        endpoint_allowlisted=True,
        local_only=True,
        network_allowed=False,
        hosted_fallback_allowed=False,
    )


def _make_capability_test_double() -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        capability_id="test_double",
        capability_class=CAPABILITY_TEST_DOUBLE,
        description="Deterministic test double for all schema paths",
        supported_tasks=list(ALL_TASK_TYPES),
        requires_json_output=True,
        requires_output_schema=False,
        max_context_window=4096,
        writes_source=False,
        runs_tools=False,
        runs_commands=False,
    )


def _make_capability_small_fast() -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        capability_id="small_fast",
        capability_class=CAPABILITY_SMALL_FAST,
        description="Small fast model for summarization and classification",
        supported_tasks=[TASK_SUMMARIZE_CONTEXT, TASK_CLASSIFY_FAILURE, TASK_EXPLAIN_FAILURE],
        requires_json_output=True,
        requires_output_schema=False,
        max_context_window=4096,
        writes_source=False,
        runs_tools=False,
        runs_commands=False,
    )


def _make_capability_small_coder() -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        capability_id="small_coder",
        capability_class=CAPABILITY_SMALL_CODER,
        description="Small coder model for implementation and test tasks",
        supported_tasks=[TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST, TASK_GENERATE_PLAN],
        requires_json_output=True,
        requires_output_schema=True,
        max_context_window=8192,
        writes_source=False,
        runs_tools=False,
        runs_commands=False,
    )


def _make_capability_medium_coder() -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        capability_id="medium_coder",
        capability_class=CAPABILITY_MEDIUM_CODER_OPTIONAL,
        description="Medium coder model for harder implementation tasks",
        supported_tasks=[TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST, TASK_GENERATE_PLAN, TASK_REVIEW_OUTPUT],
        requires_json_output=True,
        requires_output_schema=True,
        max_context_window=16384,
        writes_source=False,
        runs_tools=False,
        runs_commands=False,
    )


def _make_capability_hosted_provider() -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        capability_id="hosted_provider",
        capability_class=CAPABILITY_HOSTED_PROVIDER_OPTIONAL,
        description="Hosted provider for tasks that exceed local capacity",
        supported_tasks=list(ALL_TASK_TYPES),
        requires_json_output=True,
        requires_output_schema=False,
        max_context_window=32768,
        writes_source=False,
        runs_tools=False,
        runs_commands=False,
    )


def load_default_model_registry() -> ModelRegistry:
    now = utc_now_iso()
    registry = ModelRegistry(
        registry_id=new_id("reg"),
        created_at=now,
    )

    # Provider profiles
    for p in [
        _make_dev_provider(),
        _make_local_provider(),
        _make_ollama_provider(),
        _make_lmstudio_provider(),
        _make_openai_compatible_provider(),
        _make_opencode_compatible_provider(),
    ]:
        registry.provider_profiles.append(p)

    # Capability profiles
    for c in [
        _make_capability_test_double(),
        _make_capability_small_fast(),
        _make_capability_small_coder(),
        _make_capability_medium_coder(),
        _make_capability_hosted_provider(),
    ]:
        registry.capability_profiles.append(c)

    # Model profiles
    registry.models.append(ModelProfile(
        model_id="dev_test_model",
        display_name="Test Double Model",
        provider_id="dev_test_provider",
        capability_class=CAPABILITY_TEST_DOUBLE,
        context_window=4096,
        max_output_tokens=1024,
        enabled=True,
    ))

    registry.models.append(ModelProfile(
        model_id="small_fast_local",
        display_name="Small Fast Local",
        provider_id="local_provider",
        capability_class=CAPABILITY_SMALL_FAST,
        context_window=4096,
        max_output_tokens=1024,
        enabled=True,
    ))

    registry.models.append(ModelProfile(
        model_id="small_coder_local",
        display_name="Small Coder Local",
        provider_id="local_provider",
        capability_class=CAPABILITY_SMALL_CODER,
        context_window=8192,
        max_output_tokens=2048,
        enabled=True,
    ))

    registry.models.append(ModelProfile(
        model_id="medium_coder_optional",
        display_name="Medium Coder (Optional)",
        provider_id="ollama_provider",
        capability_class=CAPABILITY_MEDIUM_CODER_OPTIONAL,
        context_window=16384,
        max_output_tokens=4096,
        enabled=True,
    ))

    registry.models.append(ModelProfile(
        model_id="hosted_provider_optional",
        display_name="Hosted Provider (Disabled by Default)",
        provider_id="openai_compatible_provider",
        capability_class=CAPABILITY_HOSTED_PROVIDER_OPTIONAL,
        context_window=32768,
        max_output_tokens=8192,
        enabled=False,
    ))

    return registry


def register_model(registry: ModelRegistry, profile: ModelProfile) -> ModelRegistry:
    for existing in registry.models:
        if existing.model_id == profile.model_id:
            registry.errors.append(f"Duplicate model_id: {profile.model_id}")
            registry.warnings.append("Duplicate model rejected")
            return registry
    registry.models.append(profile)
    return registry


def register_provider_profile(registry: ModelRegistry, profile: ModelProviderProfile) -> ModelRegistry:
    for existing in registry.provider_profiles:
        if existing.provider_id == profile.provider_id:
            registry.errors.append(f"Duplicate provider_id: {profile.provider_id}")
            registry.warnings.append("Duplicate provider rejected")
            return registry
    registry.provider_profiles.append(profile)
    return registry


def get_model_profile(registry: ModelRegistry, model_id: str) -> ModelProfile | None:
    for m in registry.models:
        if m.model_id == model_id:
            return m
    return None


def get_provider_profile(registry: ModelRegistry, provider_id: str) -> ModelProviderProfile | None:
    for p in registry.provider_profiles:
        if p.provider_id == provider_id:
            return p
    return None


def list_enabled_models(registry: ModelRegistry) -> list[ModelProfile]:
    return [m for m in registry.models if m.enabled]


def list_models_for_task(registry: ModelRegistry, task_type: str) -> list[ModelProfile]:
    results = []
    for m in registry.models:
        if not m.enabled:
            continue
        cap = _find_capability(registry, m.capability_class)
        if cap is None:
            continue
        if task_type in cap.supported_tasks:
            results.append(m)
    return results


def _find_capability(registry: ModelRegistry, capability_class: str) -> ModelCapabilityProfile | None:
    for c in registry.capability_profiles:
        if c.capability_class == capability_class:
            return c
    return None

import pytest
from agentx_evolve.models.model_models import (
    ModelRegistry, ModelProfile, ModelProviderProfile, ModelCapabilityProfile,
    PROVIDER_DEV, PROVIDER_LOCAL, PROVIDER_DISABLED,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    CAPABILITY_SMALL_FAST, CAPABILITY_TEST_DOUBLE,
)
from agentx_evolve.models.model_registry import (
    load_default_model_registry,
    register_model,
    register_provider_profile,
    get_model_profile,
    get_provider_profile,
    list_enabled_models,
    list_models_for_task,
)


class TestLoadDefault:
    def test_default_registry_has_five_models(self):
        r = load_default_model_registry()
        assert len(r.models) == 5

    def test_default_registry_has_six_providers(self):
        r = load_default_model_registry()
        assert len(r.provider_profiles) == 6

    def test_default_registry_has_five_capabilities(self):
        r = load_default_model_registry()
        assert len(r.capability_profiles) == 5

    def test_default_models_enabled(self):
        r = load_default_model_registry()
        enabled = [m for m in r.models if m.enabled]
        assert len(enabled) >= 4

    def test_hosted_provider_optional_disabled_by_default(self):
        r = load_default_model_registry()
        for m in r.models:
            if "hosted_provider_optional" in m.model_id:
                assert m.enabled is False

    def test_default_model_ids(self):
        r = load_default_model_registry()
        ids = {m.model_id for m in r.models}
        assert ids == {
            "dev_test_model",
            "small_fast_local",
            "small_coder_local",
            "medium_coder_optional",
            "hosted_provider_optional",
        }

    def test_default_provider_ids(self):
        r = load_default_model_registry()
        ids = {p.provider_id for p in r.provider_profiles}
        assert ids == {
            "dev_test_provider",
            "local_provider",
            "ollama_provider",
            "lmstudio_provider",
            "openai_compatible_provider",
            "opencode_compatible_provider",
        }


class TestRegisterModel:
    def test_register_new_model_to_defaults(self):
        r = load_default_model_registry()
        p = ModelProfile(model_id="custom_model", provider_id="dev_test_provider")
        result = register_model(r, p)
        assert result is r
        matches = [m for m in r.models if m.model_id == "custom_model"]
        assert len(matches) == 1
        assert matches[0].provider_id == "dev_test_provider"

    def test_register_duplicate_rejected(self):
        r = load_default_model_registry()
        orig = get_model_profile(r, "small_fast_local")
        assert orig is not None
        orig_provider = orig.provider_id

        p = ModelProfile(model_id="small_fast_local", provider_id="dev_test_provider")
        result = register_model(r, p)
        assert result is r

        updated = get_model_profile(r, "small_fast_local")
        assert updated is not None
        assert updated.provider_id == orig_provider
        assert any("Duplicate model_id" in e for e in r.errors)
        assert any("Duplicate model rejected" in w for w in r.warnings)

    def test_register_model_returns_registry(self):
        r = load_default_model_registry()
        p = ModelProfile(model_id="another_model", provider_id="local_provider")
        result = register_model(r, p)
        assert result is r


class TestRegisterProvider:
    def test_register_new_provider(self):
        r = load_default_model_registry()
        p = ModelProviderProfile(provider_id="custom_prov", provider_type=PROVIDER_DEV)
        result = register_provider_profile(r, p)
        assert result is r
        assert any(p.provider_id == "custom_prov" for p in r.provider_profiles)

    def test_register_duplicate_provider_rejected(self):
        r = load_default_model_registry()
        orig = get_provider_profile(r, "dev_test_provider")
        assert orig is not None
        orig_type = orig.provider_type

        p = ModelProviderProfile(provider_id="dev_test_provider", provider_type=PROVIDER_LOCAL)
        result = register_provider_profile(r, p)
        assert result is r

        updated = get_provider_profile(r, "dev_test_provider")
        assert updated is not None
        assert updated.provider_type == orig_type
        assert any("Duplicate provider_id" in e for e in r.errors)
        assert any("Duplicate provider rejected" in w for w in r.warnings)

    def test_register_provider_returns_registry(self):
        r = load_default_model_registry()
        p = ModelProviderProfile(provider_id="another_prov", provider_type=PROVIDER_DEV)
        result = register_provider_profile(r, p)
        assert result is r


class TestGetModel:
    def test_get_existing(self):
        r = load_default_model_registry()
        p = get_model_profile(r, "small_fast_local")
        assert p is not None
        assert p.model_id == "small_fast_local"

    def test_get_nonexistent(self):
        r = load_default_model_registry()
        p = get_model_profile(r, "nonexistent")
        assert p is None

    def test_get_empty_registry(self):
        r = ModelRegistry()
        p = get_model_profile(r, "anything")
        assert p is None


class TestGetProvider:
    def test_get_existing(self):
        r = load_default_model_registry()
        p = get_provider_profile(r, "dev_test_provider")
        assert p is not None
        assert p.provider_type == PROVIDER_DEV

    def test_get_nonexistent(self):
        r = load_default_model_registry()
        p = get_provider_profile(r, "nonexistent")
        assert p is None


class TestListEnabled:
    def test_list_enabled_returns_enabled_only(self):
        r = load_default_model_registry()
        enabled = list_enabled_models(r)
        for m in enabled:
            assert m.enabled is True

    def test_list_enabled_excludes_disabled(self):
        r = load_default_model_registry()
        enabled_ids = {m.model_id for m in list_enabled_models(r)}
        assert "hosted_provider_optional" not in enabled_ids


class TestListForTask:
    def test_returns_at_least_one(self):
        r = load_default_model_registry()
        models = list_models_for_task(r, TASK_IMPLEMENT_PATCH)
        assert len(models) >= 1

    def test_returns_only_enabled(self):
        r = load_default_model_registry()
        models = list_models_for_task(r, TASK_FIX_VALIDATION)
        for m in models:
            assert m.enabled is True

    def test_returns_empty_for_unknown_task(self):
        r = load_default_model_registry()
        models = list_models_for_task(r, "unknown_task_type")
        assert models == []

    def test_returns_models_with_matching_capability(self):
        r = load_default_model_registry()
        models = list_models_for_task(r, TASK_WRITE_TEST)
        assert len(models) >= 1
        for m in models:
            cap_id = m.capability_class
            cap = next(
                (c for c in r.capability_profiles if c.capability_class == cap_id),
                None,
            )
            assert cap is not None
            assert TASK_WRITE_TEST in cap.supported_tasks

import pytest
from agentx_evolve.policy.model_policy import (
    find_model_profile,
    model_may_execute_commands,
    model_may_execute_tools,
    model_may_read_source,
    model_may_use_network,
    model_may_write_files,
    model_profile_exists,
    model_task_allowed,
)
from agentx_evolve.policy.policy_models import ModelPolicy, ModelProfile


@pytest.fixture
def sample_policy():
    return ModelPolicy(
        policy_id="mp-1",
        model_profiles=[
            ModelProfile(
                model_profile_id="read_only",
                provider_type="local",
                allowed_task_types=["code_analysis", "code_review"],
                blocked_task_types=["code_generation"],
                may_read_source_context=True,
                may_write_files=False,
                may_execute_tools=False,
                may_execute_commands=False,
                may_use_network=False,
            ),
            ModelProfile(
                model_profile_id="full_access",
                provider_type="remote",
                allowed_task_types=["code_generation", "testing"],
                may_read_source_context=True,
                may_write_files=True,
                may_execute_tools=True,
                may_execute_commands=True,
                may_use_network=True,
                requires_human_approval=True,
            ),
        ],
    )


class TestFindModelProfile:
    def test_found(self, sample_policy):
        profile = find_model_profile("read_only", sample_policy)
        assert profile is not None
        assert profile.model_profile_id == "read_only"

    def test_not_found(self, sample_policy):
        assert find_model_profile("nonexistent", sample_policy) is None


class TestModelTaskAllowed:
    def test_allowed(self, sample_policy):
        assert model_task_allowed("read_only", "code_analysis", sample_policy) is True

    def test_blocked(self, sample_policy):
        assert model_task_allowed("read_only", "code_generation", sample_policy) is False

    def test_unknown_profile(self, sample_policy):
        assert model_task_allowed("unknown", "anything", sample_policy) is False


class TestMayFunctions:
    def test_read_only_profile(self, sample_policy):
        assert model_may_read_source("read_only", sample_policy) is True
        assert model_may_write_files("read_only", sample_policy) is False
        assert model_may_execute_tools("read_only", sample_policy) is False
        assert model_may_execute_commands("read_only", sample_policy) is False
        assert model_may_use_network("read_only", sample_policy) is False

    def test_full_access_profile(self, sample_policy):
        assert model_may_read_source("full_access", sample_policy) is True
        assert model_may_write_files("full_access", sample_policy) is True
        assert model_may_execute_tools("full_access", sample_policy) is True
        assert model_may_execute_commands("full_access", sample_policy) is True
        assert model_may_use_network("full_access", sample_policy) is True

    def test_unknown_profile(self, sample_policy):
        assert model_may_read_source("unknown", sample_policy) is False


class TestModelProfileExists:
    def test_exists(self, sample_policy):
        assert model_profile_exists("read_only", sample_policy) is True

    def test_not_exists(self, sample_policy):
        assert model_profile_exists("nonexistent", sample_policy) is False

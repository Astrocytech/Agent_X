from __future__ import annotations

from .policy_models import ModelPolicy, ModelProfile


def find_model_profile(model_profile_id: str, model_policy: ModelPolicy) -> ModelProfile | None:
    for profile in model_policy.model_profiles:
        if profile.model_profile_id == model_profile_id:
            return profile
    return None


def model_profile_exists(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    return find_model_profile(model_profile_id, model_policy) is not None


def model_task_allowed(model_profile_id: str, task_type: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    if task_type in profile.blocked_task_types:
        return False
    if task_type in profile.allowed_task_types:
        return True
    if len(profile.allowed_task_types) == 0:
        return True
    return False


def model_may_read_source(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    return profile.may_read_source_context


def model_may_write_files(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    return profile.may_write_files


def model_may_execute_tools(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    return profile.may_execute_tools


def model_may_execute_commands(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    return profile.may_execute_commands


def model_may_use_network(model_profile_id: str, model_policy: ModelPolicy) -> bool:
    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return False
    return profile.may_use_network

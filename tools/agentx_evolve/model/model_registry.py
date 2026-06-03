from __future__ import annotations
from agentx_evolve.model.model_models import (
    ModelProfile, MP_SMALL_FAST, MP_SMALL_CODER,
    MP_MEDIUM_CODER, MP_HOSTED_FALLBACK,
)


def default_profiles() -> list[ModelProfile]:
    return [
        ModelProfile(
            profile_id=MP_SMALL_FAST,
            name="Small Fast",
            description="Small fast model for simple tasks",
            provider="local", model_name="qwen2.5-coder:1.5b",
            max_tokens=2048, temperature=0.1,
            timeout_seconds=30, retry_limit=1,
            token_budget=4096,
        ),
        ModelProfile(
            profile_id=MP_SMALL_CODER,
            name="Small Coder",
            description="Small coding model for patch generation",
            provider="local", model_name="qwen2.5-coder:3b",
            max_tokens=4096, temperature=0.2,
            timeout_seconds=60, retry_limit=2,
            token_budget=8192,
        ),
        ModelProfile(
            profile_id=MP_MEDIUM_CODER,
            name="Medium Coder (Optional)",
            description="Medium coding model for complex changes",
            provider="local", model_name="codellama:7b",
            max_tokens=8192, temperature=0.2,
            timeout_seconds=120, retry_limit=2,
            token_budget=16384,
        ),
        ModelProfile(
            profile_id=MP_HOSTED_FALLBACK,
            name="Hosted Fallback (Optional)",
            description="Hosted model fallback for complex tasks",
            provider="opencode", model_name="gpt-4o-mini",
            max_tokens=8192, temperature=0.2,
            timeout_seconds=120, retry_limit=3,
            token_budget=32768,
        ),
    ]


class ModelRegistry:
    def __init__(self):
        self._profiles: dict[str, ModelProfile] = {}
        for p in default_profiles():
            self._profiles[p.profile_id] = p

    def get_profile(self, profile_id: str) -> ModelProfile | None:
        return self._profiles.get(profile_id)

    def list_profiles(self) -> list[ModelProfile]:
        return list(self._profiles.values())

    def add_profile(self, profile: ModelProfile) -> ModelProfile:
        self._profiles[profile.profile_id] = profile
        return profile

    def remove_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            return True
        return False

    def get_profile_for_task(self, task_type: str) -> ModelProfile:
        task_profiles = {
            "GENERATE_PLAN": MP_SMALL_FAST,
            "IMPLEMENT_PATCH": MP_SMALL_CODER,
            "FIX_VALIDATION": MP_SMALL_CODER,
            "WRITE_TEST": MP_SMALL_CODER,
            "EXPLAIN_FAILURE": MP_SMALL_FAST,
            "REVIEW_CODE": MP_MEDIUM_CODER,
        }
        profile_id = task_profiles.get(task_type, MP_SMALL_FAST)
        profile = self._profiles.get(profile_id)
        return profile or self._profiles[MP_SMALL_FAST]

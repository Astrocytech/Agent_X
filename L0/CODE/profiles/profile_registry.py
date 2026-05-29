from __future__ import annotations

from profiles.agent_profile_schema import AgentProfileSchema


class ProfileRegistry:
    def __init__(self):
        self._profiles: dict[str, AgentProfileSchema] = {}

    def load_builtin_profiles(self, loader, profile_ids: list[str]) -> None:
        for pid in profile_ids:
            profile = loader.load(pid)
            self.register(profile)

    def register(self, profile: AgentProfileSchema) -> None:
        self._profiles[profile.id] = profile

    def get(self, profile_id: str) -> AgentProfileSchema | None:
        return self._profiles.get(profile_id)

    def validate(self, profile: AgentProfileSchema) -> list[str]:
        issues = []
        if not profile.id:
            issues.append("Profile must have an id")
        if not profile.name:
            issues.append("Profile must have a name")
        return issues

    def list_all(self) -> list[str]:
        return list(self._profiles.keys())

    def __len__(self) -> int:
        return len(self._profiles)

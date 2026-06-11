from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_PROFILE_IDS = {"STRICT", "DRY_RUN", "REPLAY", "AUDIT_ONLY"}
LIVE_PROFILES = {"STRICT", "AUDIT_ONLY"}
KNOWN_FIELDS = {"profile_id", "description", "allow_live_execution", "allow_network",
                "allow_source_mutation", "require_review", "require_rollback_plan",
                "max_actions", "metadata"}


@dataclass
class MvpRuntimeProfile:
    profile_id: str = "STRICT"
    description: str = ""
    allow_live_execution: bool = True
    allow_network: bool = False
    allow_source_mutation: bool = False
    require_review: bool = True
    require_rollback_plan: bool = True
    max_actions: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        issues = self.validate()
        if issues:
            raise ValueError(f"Invalid profile: {'; '.join(issues)}")

    def validate(self) -> list[str]:
        issues = []
        if self.profile_id not in VALID_PROFILE_IDS:
            issues.append(f"Unknown profile_id: {self.profile_id}")
        if self.profile_id in LIVE_PROFILES and not self.allow_live_execution:
            issues.append(f"Profile {self.profile_id} must allow live execution")
        return issues

    def is_live(self) -> bool:
        return self.profile_id in LIVE_PROFILES

    def is_dry_run(self) -> bool:
        return self.profile_id == "DRY_RUN"

    def is_replay(self) -> bool:
        return self.profile_id == "REPLAY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "description": self.description,
            "allow_live_execution": self.allow_live_execution,
            "allow_network": self.allow_network,
            "allow_source_mutation": self.allow_source_mutation,
            "require_review": self.require_review,
            "require_rollback_plan": self.require_rollback_plan,
            "max_actions": self.max_actions,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpRuntimeProfile:
        extra = [k for k in data if k not in KNOWN_FIELDS]
        if extra:
            raise ValueError(f"Unknown fields: {extra}")
        return cls(
            profile_id=data.get("profile_id", "STRICT"),
            description=data.get("description", ""),
            allow_live_execution=data.get("allow_live_execution", True),
            allow_network=data.get("allow_network", False),
            allow_source_mutation=data.get("allow_source_mutation", False),
            require_review=data.get("require_review", True),
            require_rollback_plan=data.get("require_rollback_plan", True),
            max_actions=data.get("max_actions", 10),
            metadata=data.get("metadata", {}),
        )


DEFAULT_PROFILES: dict[str, MvpRuntimeProfile] = {
    "STRICT": MvpRuntimeProfile(
        profile_id="STRICT", description="Full governance, no network, no source mutation",
        allow_live_execution=True, allow_network=False, allow_source_mutation=False,
    ),
    "DRY_RUN": MvpRuntimeProfile(
        profile_id="DRY_RUN", description="Simulate without side effects",
        allow_live_execution=False, allow_network=False, allow_source_mutation=False,
        require_rollback_plan=False,
    ),
    "REPLAY": MvpRuntimeProfile(
        profile_id="REPLAY", description="Replay previous run from recorded context",
        allow_live_execution=False, allow_network=False, allow_source_mutation=False,
        require_review=False, require_rollback_plan=False,
    ),
    "AUDIT_ONLY": MvpRuntimeProfile(
        profile_id="AUDIT_ONLY", description="Read-only audit of existing state",
        allow_live_execution=True, allow_network=False, allow_source_mutation=False,
        require_review=True, max_actions=0,
    ),
}


def load_profile(profile_id: str) -> MvpRuntimeProfile:
    if profile_id not in DEFAULT_PROFILES:
        raise ValueError(f"Unknown profile: {profile_id}")
    return DEFAULT_PROFILES[profile_id]

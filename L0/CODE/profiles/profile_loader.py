from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from profiles.agent_profile_schema import (
    AgentProfileSchema,
    KNOWN_FIELDS,
    REQUIRED_FIELDS,
)


class ProfileLoader:
    def __init__(self, profiles_dir: str | Path):
        self.profiles_dir = Path(profiles_dir)

    def load(self, profile_id: str) -> AgentProfileSchema:
        path = self.profiles_dir / f"{profile_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_id}")
        data = yaml.safe_load(path.read_text())
        return AgentProfileSchema(
            **{k: v for k, v in data.items() if k in AgentProfileSchema.__dataclass_fields__}
        )

    def load_builtin(self, builtin_dir: str | Path, profile_id: str) -> AgentProfileSchema:
        return ProfileLoader(builtin_dir).load(profile_id)

    def list_ids(self) -> list[str]:
        return [p.stem for p in self.profiles_dir.glob("*.yaml")]

    def validate_profile(self, profile: AgentProfileSchema) -> list[str]:
        """Validate profile startup requirements.

        Checks all REQUIRED_FIELDS have values.  String fields must be
        non-empty; list fields may be empty (e.g. blank_slate has no tools).
        Returns a list of error messages (empty = valid).
        """
        errors: list[str] = []
        for field_name in REQUIRED_FIELDS:
            value = getattr(profile, field_name, None)
            if isinstance(value, str) and not value:
                errors.append(f"Required field '{field_name}' is missing or empty")
            elif value is None:
                errors.append(f"Required field '{field_name}' is missing")
        return errors

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate a raw profile config dict for unknown fields.

        Returns a list of error messages (empty = valid).
        """
        errors: list[str] = []
        for key in config:
            if key not in KNOWN_FIELDS:
                errors.append(f"Unknown field '{key}' is not allowed in profile config")
        return errors

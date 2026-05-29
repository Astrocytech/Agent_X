from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def _iter_builtin_profiles() -> list[dict]:
    profiles: list[dict] = []
    profiles_dir = ROOT / "L0/CODE" / "profiles" / "builtin"
    for yaml_file in sorted(profiles_dir.glob("*.yaml")):
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        profiles.append(data)
    return profiles


def test_every_builtin_profile_has_id() -> None:
    for profile in _iter_builtin_profiles():
        assert "id" in profile, f"Profile missing 'id': {profile.get('name', 'unknown')}"


def test_every_builtin_profile_has_allowed_tools() -> None:
    for profile in _iter_builtin_profiles():
        assert "allowed_tools" in profile, (
            f"Profile '{profile.get('id')}' missing 'allowed_tools'"
        )


def test_every_builtin_profile_allows_only_seed_emit_answer() -> None:
    for profile in _iter_builtin_profiles():
        allowed = profile.get("allowed_tools", [])
        for tool in allowed:
            assert tool == "seed.emit_answer", (
                f"Profile '{profile.get('id')}' allows non-seed tool: {tool}"
            )

"""LocalProfilePort — L0 seed profile port that loads profiles from YAML files."""

from __future__ import annotations

from pathlib import Path

from profiles.agent_profile_schema import Profile

_PROFILE_DIRS = [
    Path(__file__).resolve().parents[2] / "profiles" / "builtin",
]


def _load_known_tools() -> set[str]:
    import yaml

    path = (
        Path(__file__).resolve().parents[3]
        / "CODE"
        / "governance"
        / "policies"
        / "seed_tool_risk.yaml"
    )
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return set((data or {}).get("tools", {}).keys())
    return set()


_KNOWN_TOOLS: set[str] = _load_known_tools()


class ProfileNotFoundError(Exception):
    pass


class LocalProfilePort:
    runtime_safety_class = "production_seed_port"

    def load(self, profile_id: str) -> Profile:
        for _PROFILE_DIR in _PROFILE_DIRS:
            path = _PROFILE_DIR / f"{profile_id}.yaml"
            if path.exists():
                break
            path = _PROFILE_DIR / f"{profile_id}.yml"
            if path.exists():
                break
        else:
            raise ProfileNotFoundError(profile_id)
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Profile {profile_id} is not a valid YAML dict")
        data.setdefault("id", profile_id)

        for field in ("id", "name", "allowed_tools", "forbidden_tools"):
            if field not in data or data.get(field) is None:
                raise ValueError(f"Profile {profile_id} missing required field: {field}")
            if isinstance(data[field], str) and not data[field]:
                raise ValueError(f"Profile {profile_id} missing required field: {field}")

        allowed = data.get("allowed_tools", [])
        if isinstance(allowed, list):
            for tool in allowed:
                if tool not in _KNOWN_TOOLS:
                    raise ValueError(
                        f"Profile {profile_id} contains unknown tool '{tool}' — "
                        f"must be one of {sorted(_KNOWN_TOOLS)}"
                    )

        hashes_path = Path(__file__).resolve().parents[2] / "profiles" / "PROFILE_HASHES.yaml"
        if hashes_path.exists():
            import hashlib

            hash_data = yaml.safe_load(hashes_path.read_text(encoding="utf-8"))
            profile_hashes = (hash_data or {}).get("profile_hashes", {})
            expected = profile_hashes.get(path.name)
            if expected:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual != expected:
                    raise ValueError(
                        f"Profile {profile_id} hash mismatch: expected {expected}, got {actual}"
                    )

        return Profile(
            id=data.get("id", profile_id),
            name=data.get("name", ""),
            role=data.get("role", ""),
            allowed_tools=data.get("allowed_tools", []),
            planner_style=data.get("planner_style", "direct"),
            memory_retrieval=data.get("memory_retrieval", "focused"),
            evaluation_criteria=data.get("evaluation_criteria", []),
            raw=data,
        )

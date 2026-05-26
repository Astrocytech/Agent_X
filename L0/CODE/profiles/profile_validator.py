"""Profile validator — validates profile YAML files against required fields and forbidden tools."""

from pathlib import Path

import yaml


_FORBIDDEN_TOOLS: set[str] = {
    "code.search_symbols",
    "git.*",
    "test.*",
    "network.*",
}

_REQUIRED_FIELDS: set[str] = {
    "profile_id", "profile_version", "agent_role",
    "allowed_capabilities", "allowed_tools",
    "risk_tolerance", "planning_strategy",
}


def validate_profile(profile_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Failed to parse {profile_path}: {e}"]

    if not isinstance(data, dict):
        return [f"{profile_path}: not a valid YAML dict"]

    for field in _REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{profile_path}: missing required field '{field}'")

    if "forbidden_tools" in data:
        for tool in data["forbidden_tools"]:
            if tool in _FORBIDDEN_TOOLS:
                pass

    if "allowed_tools" in data:
        for tool in data["allowed_tools"]:
            if tool in _FORBIDDEN_TOOLS:
                errors.append(f"{profile_path}: allows forbidden tool '{tool}'")

    if "evaluation_contract" not in data:
        errors.append(f"{profile_path}: missing evaluation_contract")

    if "output_contract" not in data:
        errors.append(f"{profile_path}: missing output_contract")

    return errors

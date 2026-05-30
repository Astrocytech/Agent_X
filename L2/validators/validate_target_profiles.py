"""Validate L2 target profiles against taxonomy rules.

Loads L1/target_taxonomy.yaml to determine allowed target kinds,
required and forbidden framework capabilities, and migration rules.
Framework profiles are validated against framework_rules.
"""

from pathlib import Path
from typing import Any

from L1.validators.common import load_yaml

LEGACY_PROFILES_WITHOUT_TARGET_KIND: set[str] = {
    "coding_agent.yaml",
    "symbolic_regression_controller.yaml",
    "research_agent.yaml",
    "repo_maintenance_agent.yaml",
    "orchestrator.yaml",
}

FORBIDDEN_CHECK_LOCATIONS: list[str] = [
    "required_capabilities",
    "features",
    "forbidden_actions",
]

BOOLEAN_FORBIDDEN_KEYS: list[str] = [
    "requires_l0_runtime_self_modification",
    "requires_separate_framework_seed_repo",
    "hidden_state_without_replay",
    "unmediated_tool_execution",
    "ungoverned_promotion",
]

FORBIDDEN_CAPABILITY_TOKENS: set[str] = {
    "l0_runtime_self_modification",
    "unmediated_tool_execution",
    "ungoverned_promotion",
    "hidden_unlogged_state_mutation",
}


def _collect_tokens(data: dict) -> set[str]:
    """Collect string tokens from locations to check for forbidden capabilities.

    Only scans the specific locations listed in FORBIDDEN_CHECK_LOCATIONS.
    Does not scan the profile's own forbidden_capabilities field, since
    that is a self-declaration of what the profile prohibits, not what
    it does.
    """
    tokens: set[str] = set()

    for loc in FORBIDDEN_CHECK_LOCATIONS:
        parts = loc.split(".")
        val: Any = data
        try:
            for part in parts:
                if isinstance(val, dict):
                    val = val.get(part, {})
                else:
                    val = {}
                    break
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        tokens.add(item)
            elif isinstance(val, dict):
                for v in val.values():
                    if isinstance(v, str):
                        tokens.add(v)
        except Exception:
            pass

    for key in BOOLEAN_FORBIDDEN_KEYS:
        if data.get(key) is True:
            tokens.add(key)

    return tokens


def validate_profiles(
    profile_dir: str | Path = "L2/profiles",
    taxonomy_path: str | Path = "L1/target_taxonomy.yaml",
) -> list[str]:
    """Validate all YAML profiles against taxonomy rules.

    Returns a list of error messages. Empty list means all profiles
    are valid.
    """
    errors: list[str] = []
    tax = load_yaml(str(taxonomy_path))
    if tax is None:
        return [f"Cannot load taxonomy: {taxonomy_path}"]

    allowed_kinds: set[str] = set(
        tax.get("allowed_target_kinds", [])
    )
    fw_rules: dict = tax.get("framework_rules", {})
    required_caps: set[str] = set(
        fw_rules.get("required_capabilities", [])
    )
    forbidden_caps: set[str] = set(
        fw_rules.get("forbidden_capabilities", [])
    )

    profile_path = (
        Path(profile_dir)
        if not isinstance(profile_dir, Path)
        else profile_dir
    )
    if not profile_path.is_dir():
        return [f"Profile directory not found: {profile_dir}"]

    for yaml_file in sorted(profile_path.glob("*.yaml")):
        data = load_yaml(str(yaml_file))
        if data is None:
            errors.append(
                f"{yaml_file.name}: Could not parse YAML"
            )
            continue

        target_kind = data.get("target_kind")

        if target_kind is None:
            if yaml_file.name in LEGACY_PROFILES_WITHOUT_TARGET_KIND:
                continue
            else:
                errors.append(
                    f"{yaml_file.name}: New profile must declare "
                    f"target_kind (not in legacy allowlist)"
                )
                continue

        if target_kind not in allowed_kinds:
            errors.append(
                f"{yaml_file.name}: Unknown target_kind "
                f"'{target_kind}'"
            )
            continue

        if target_kind == "framework":
            declared_caps: set[str] = set(
                data.get("required_capabilities", [])
            )
            missing = required_caps - declared_caps
            for cap in sorted(missing):
                errors.append(
                    f"{yaml_file.name}: Missing required "
                    f"framework capability '{cap}'"
                )

            all_tokens = _collect_tokens(data)
            found_forbidden = forbidden_caps & all_tokens
            for cap in sorted(found_forbidden):
                errors.append(
                    f"{yaml_file.name}: Forbidden framework capability "
                    f"'{cap}' found in profile capabilities/features"
                )

            found_extra = FORBIDDEN_CAPABILITY_TOKENS & all_tokens
            for cap in sorted(found_extra):
                errors.append(
                    f"{yaml_file.name}: Forbidden capability token "
                    f"'{cap}' found in profile capabilities/features"
                )

    return errors

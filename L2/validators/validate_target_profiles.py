"""Validate L2 target profiles against taxonomy rules."""

from pathlib import Path

from L1.validators.common import load_yaml


def _load_taxonomy(taxonomy_path: str | Path = "L1/target_taxonomy.yaml") -> dict | None:
    return load_yaml(str(taxonomy_path))


def validate_profiles(
    profile_dir: str | Path = "L2/profiles",
    taxonomy_path: str | Path = "L1/target_taxonomy.yaml",
) -> list[str]:
    """
    Validate all YAML profiles against taxonomy rules.

    Returns a list of error messages. Empty list means all profiles are valid.
    """
    errors: list[str] = []
    tax = _load_taxonomy(taxonomy_path)
    if tax is None:
        return [f"Cannot load taxonomy: {taxonomy_path}"]

    allowed_kinds: set[str] = set(tax.get("allowed_target_kinds", []))
    framework_config: dict = tax.get("framework", {})
    required_caps: set[str] = set(framework_config.get("required_capabilities", []))
    forbidden_caps: set[str] = set(framework_config.get("forbidden_capabilities", []))
    required_manifest_fields: set[str] = set(framework_config.get("required_manifest_fields", []))
    migration_default: str = tax.get("migration", {}).get("missing_target_kind_default", "agent")
    allow_legacy: bool = tax.get("migration", {}).get("allow_legacy_profiles_without_target_kind", True)

    profile_path = Path(profile_dir) if not isinstance(profile_dir, Path) else profile_dir
    if not profile_path.is_dir():
        return [f"Profile directory not found: {profile_dir}"]

    for yaml_file in sorted(profile_path.glob("*.yaml")):
        data = load_yaml(str(yaml_file))
        if data is None:
            errors.append(f"{yaml_file.name}: Could not parse YAML")
            continue

        target_kind = data.get("target_kind")

        if target_kind is None:
            if allow_legacy:
                # Legacy profile without target_kind: apply migration default
                continue
            else:
                errors.append(f"{yaml_file.name}: New profile must declare target_kind")
                continue

        if target_kind not in allowed_kinds:
            errors.append(f"{yaml_file.name}: Unknown target_kind '{target_kind}'")
            continue

        if target_kind == "framework":
            # Check required capabilities
            declared_caps = set(data.get("required_capabilities", []))
            missing = required_caps - declared_caps
            for cap in sorted(missing):
                errors.append(f"{yaml_file.name}: Missing required framework capability '{cap}'")

            # Check forbidden capabilities
            all_declared = set(data.get("required_capabilities", []))
            all_declared |= set(data.get("features", []))
            for cap in sorted(forbidden_caps & all_declared):
                errors.append(f"{yaml_file.name}: Forbidden framework capability '{cap}' is required or declared")

            # Check forbidden booleans
            if data.get("requires_l0_runtime_self_modification") is True:
                errors.append(f"{yaml_file.name}: Must not require L0 runtime self-modification")
            if data.get("requires_separate_framework_seed_repo") is True:
                errors.append(f"{yaml_file.name}: Must not require a separate root Framework_X seed repo")
            if data.get("hidden_state_without_replay") is True:
                errors.append(f"{yaml_file.name}: Must not require hidden non-replayable state")

    return errors

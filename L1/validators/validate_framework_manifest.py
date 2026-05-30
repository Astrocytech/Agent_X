"""Validate framework package manifests against required fields and rules."""

from pathlib import Path

from L1.validators.common import load_yaml


def validate_manifest(path: str | Path) -> list[str]:
    """Validate a framework manifest YAML file.

    Returns a list of error messages. Empty list means valid.
    """
    errors: list[str] = []
    data = load_yaml(str(path))
    if data is None:
        return [f"Cannot load or parse manifest: {path}"]

    manifest_name = Path(path).name

    if "manifest_version" not in data:
        errors.append(f"{manifest_name}: Missing required field 'manifest_version'")

    if data.get("target_kind") != "framework":
        errors.append(
            f"{manifest_name}: target_kind must be 'framework', "
            f"got '{data.get('target_kind')}'"
        )

    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        errors.append(f"{manifest_name}: 'name' is required and must be non-empty")

    purpose = data.get("purpose")
    if not purpose or not isinstance(purpose, str) or not purpose.strip():
        errors.append(f"{manifest_name}: 'purpose' is required and must be non-empty")

    interfaces = data.get("required_interfaces")
    if not interfaces or not isinstance(interfaces, list) or len(interfaces) == 0:
        errors.append(f"{manifest_name}: 'required_interfaces' must be a non-empty list")

    prom = data.get("promotion")
    if not isinstance(prom, dict):
        errors.append(f"{manifest_name}: 'promotion' must be a mapping")
    else:
        for gate in ["requires_tests", "requires_evidence_bundle", "requires_rollback_plan"]:
            if gate not in prom:
                errors.append(f"{manifest_name}: promotion.{gate} is required")

    pkg = data.get("packaging")
    if not isinstance(pkg, dict):
        errors.append(f"{manifest_name}: 'packaging' must be a mapping")
    else:
        for field in ["exportable", "includes_profile", "includes_evaluation_spec"]:
            if field not in pkg:
                errors.append(f"{manifest_name}: packaging.{field} is required")

    roll = data.get("rollback")
    if not isinstance(roll, dict):
        errors.append(f"{manifest_name}: 'rollback' must be a mapping")
    elif "supported" not in roll:
        errors.append(f"{manifest_name}: rollback.supported is required")

    compat = data.get("compatibility")
    if not isinstance(compat, dict):
        errors.append(f"{manifest_name}: 'compatibility' must be a mapping")
    else:
        if compat.get("agent_x_l0_neutral") is not True:
            errors.append(
                f"{manifest_name}: compatibility.agent_x_l0_neutral must be true"
            )
        if compat.get("no_runtime_self_modification") is not True:
            errors.append(
                f"{manifest_name}: compatibility.no_runtime_self_modification "
                "must be true"
            )

    return errors

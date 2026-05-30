"""Validate framework package manifests against required fields and rules."""

from pathlib import Path

from L1.validators.common import load_yaml


ALLOWED_PROMOTION_STATUSES = {
    "rejected",
    "revise",
    "experimental_framework_profile",
    "exportable_framework_package",
    "promoted_framework_package",
}

REQUIRED_CONTRACT_FIELDS = [
    "module_registry",
    "extension_contract",
    "composition_contract",
    "evaluator_contract",
    "promotion_contract",
    "packaging_contract",
    "rollback_contract",
    "compatibility_contract",
]

REQUIRED_TOP_LEVEL_FIELDS = [
    "id",
    "name",
    "version",
    "target_kind",
    "source_profile",
    "purpose",
    "contracts",
    "artifacts",
    "compatibility",
    "promotion",
    "validation",
]


def validate_manifest(path: str | Path) -> list[str]:
    """
    Validate a framework manifest YAML file.

    Returns a list of error messages. Empty list means valid.
    """
    errors: list[str] = []
    data = load_yaml(str(path))
    if data is None:
        return [f"Cannot load or parse manifest: {path}"]

    manifest_name = Path(path).name

    # Check required top-level fields
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data:
            errors.append(f"{manifest_name}: Missing required top-level field '{field}'")

    # Check target_kind
    if data.get("target_kind") != "framework":
        errors.append(f"{manifest_name}: target_kind must be 'framework', got '{data.get('target_kind')}'")

    # Check contracts
    contracts = data.get("contracts", {})
    if isinstance(contracts, dict):
        for field in REQUIRED_CONTRACT_FIELDS:
            if field not in contracts:
                errors.append(f"{manifest_name}: Missing required contract field '{field}'")
    elif "contracts" in data:
        errors.append(f"{manifest_name}: contracts must be a mapping")

    # Check artifacts
    artifacts = data.get("artifacts", {})
    if isinstance(artifacts, dict):
        required_artifact_keys = {"profile", "blueprint", "tests", "evaluation_report", "evidence_report", "rollback_notes"}
        missing = required_artifact_keys - set(artifacts.keys())
        for key in sorted(missing):
            errors.append(f"{manifest_name}: Missing required artifact field '{key}'")
    elif "artifacts" in data:
        errors.append(f"{manifest_name}: artifacts must be a mapping")

    # Check compatibility
    compat = data.get("compatibility", {})
    if isinstance(compat, dict):
        if "agent_x_l0_version" not in compat:
            errors.append(f"{manifest_name}: Missing compatibility field 'agent_x_l0_version'")
        if "agent_x_l1_version" not in compat:
            errors.append(f"{manifest_name}: Missing compatibility field 'agent_x_l1_version'")
    elif "compatibility" in data:
        errors.append(f"{manifest_name}: compatibility must be a mapping")

    # Check promotion
    prom = data.get("promotion", {})
    if isinstance(prom, dict):
        status = prom.get("status")
        if not status:
            errors.append(f"{manifest_name}: promotion.status is required")
        elif status not in ALLOWED_PROMOTION_STATUSES:
            errors.append(f"{manifest_name}: Invalid promotion status '{status}'")
    elif "promotion" in data:
        errors.append(f"{manifest_name}: promotion must be a mapping")

    # Check validation
    val = data.get("validation", {})
    if isinstance(val, dict):
        blocked = val.get("blocked_reasons", [])
        if isinstance(blocked, list) and len(blocked) > 0:
            errors.append(f"{manifest_name}: Manifest is blocked: {', '.join(blocked)}")
    elif "validation" in data:
        errors.append(f"{manifest_name}: validation must be a mapping")

    return errors

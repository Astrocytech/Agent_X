"""Validate framework package manifests against required fields and rules.

This validator checks all fields listed in the framework package manifest
schema and enforces the constraints defined in L1/target_taxonomy.yaml
framework_rules. It is a reusable production validator called by both
validate_all.py and L1 tests.
"""

from pathlib import Path

from L1.validators.common import load_yaml

ALLOWED_PROMOTION_STATUSES: set[str] = {
    "rejected",
    "revise",
    "experimental_framework_profile",
    "exportable_framework_package",
}

REQUIRED_MANIFEST_FIELDS: list[str] = [
    "manifest_version",
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
    "packaging",
    "rollback",
    "required_interfaces",
]


def validate_manifest(path: str | Path) -> list[str]:
    """Validate a framework manifest YAML file.

    Returns a list of error messages. Empty list means the manifest is
    valid.
    """
    errors: list[str] = []
    data = load_yaml(str(path))
    if data is None:
        return [f"Cannot load or parse manifest: {path}"]

    manifest_name = Path(path).name

    _check_required_fields(data, manifest_name, errors)
    _check_target_kind(data, manifest_name, errors)
    _check_name(data, manifest_name, errors)
    _check_purpose(data, manifest_name, errors)
    _check_contracts(data, manifest_name, errors)
    _check_artifacts(data, manifest_name, errors)
    _check_compatibility(data, manifest_name, errors)
    _check_promotion(data, manifest_name, errors)
    _check_packaging(data, manifest_name, errors)
    _check_rollback(data, manifest_name, errors)
    _check_required_interfaces(data, manifest_name, errors)
    _check_validation(data, manifest_name, errors)

    return errors


def _check_required_fields(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in data:
            errors.append(
                f"{manifest_name}: Missing required field '{field}'"
            )


def _check_target_kind(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    kind = data.get("target_kind")
    if kind is not None and kind != "framework":
        errors.append(
            f"{manifest_name}: target_kind must be 'framework', "
            f"got '{kind}'"
        )


def _check_name(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        errors.append(
            f"{manifest_name}: 'name' is required "
            f"and must be a non-empty string"
        )


def _check_purpose(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    purpose = data.get("purpose")
    if not purpose or not isinstance(purpose, str) or not purpose.strip():
        errors.append(
            f"{manifest_name}: 'purpose' is required "
            f"and must be a non-empty string"
        )


def _check_contracts(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    contracts = data.get("contracts")
    if contracts is None:
        errors.append(
            f"{manifest_name}: 'contracts' is required"
        )
    elif not isinstance(contracts, dict) or len(contracts) == 0:
        errors.append(
            f"{manifest_name}: 'contracts' must be "
            f"a non-empty mapping"
        )


def _check_artifacts(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    artifacts = data.get("artifacts")
    if artifacts is None:
        errors.append(
            f"{manifest_name}: 'artifacts' is required"
        )
    elif not isinstance(artifacts, dict) or len(artifacts) == 0:
        errors.append(
            f"{manifest_name}: 'artifacts' must be "
            f"a non-empty mapping"
        )


def _check_compatibility(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    compat = data.get("compatibility")
    if compat is None:
        errors.append(
            f"{manifest_name}: 'compatibility' is required"
        )
    elif not isinstance(compat, dict):
        errors.append(
            f"{manifest_name}: 'compatibility' must be a mapping"
        )
    else:
        if compat.get("agent_x_l0_neutral") is not True:
            errors.append(
                f"{manifest_name}: "
                f"compatibility.agent_x_l0_neutral must be true"
            )
        if compat.get("no_runtime_self_modification") is not True:
            errors.append(
                f"{manifest_name}: "
                f"compatibility.no_runtime_self_modification "
                f"must be true"
            )


def _check_promotion(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    prom = data.get("promotion")
    if prom is None:
        errors.append(
            f"{manifest_name}: 'promotion' is required"
        )
    elif not isinstance(prom, dict):
        errors.append(
            f"{manifest_name}: 'promotion' must be a mapping"
        )
    else:
        for gate in [
            "requires_tests",
            "requires_evidence_bundle",
            "requires_rollback_plan",
        ]:
            if gate not in prom:
                errors.append(
                    f"{manifest_name}: promotion.{gate} is required"
                )
        status = prom.get("status")
        if status is not None:
            if status not in ALLOWED_PROMOTION_STATUSES:
                errors.append(
                    f"{manifest_name}: Invalid promotion status "
                    f"'{status}'"
                )


def _check_packaging(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    pkg = data.get("packaging")
    if pkg is None:
        errors.append(
            f"{manifest_name}: 'packaging' is required"
        )
    elif not isinstance(pkg, dict):
        errors.append(
            f"{manifest_name}: 'packaging' must be a mapping"
        )
    else:
        for field in [
            "exportable",
            "includes_profile",
            "includes_evaluation_spec",
        ]:
            if field not in pkg:
                errors.append(
                    f"{manifest_name}: packaging.{field} is required"
                )


def _check_rollback(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    roll = data.get("rollback")
    if roll is None:
        errors.append(
            f"{manifest_name}: 'rollback' is required"
        )
    elif not isinstance(roll, dict):
        errors.append(
            f"{manifest_name}: 'rollback' must be a mapping"
        )
    elif "supported" not in roll:
        errors.append(
            f"{manifest_name}: rollback.supported is required"
        )


def _check_required_interfaces(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    interfaces = data.get("required_interfaces")
    if interfaces is None:
        errors.append(
            f"{manifest_name}: 'required_interfaces' is required"
        )
    elif not isinstance(interfaces, list) or len(interfaces) == 0:
        errors.append(
            f"{manifest_name}: 'required_interfaces' must be "
            f"a non-empty list"
        )


def _check_validation(
    data: dict,
    manifest_name: str,
    errors: list[str],
) -> None:
    val = data.get("validation")
    if val is not None:
        if not isinstance(val, dict):
            errors.append(
                f"{manifest_name}: 'validation' must be a mapping"
            )

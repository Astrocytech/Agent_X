"""Validate L1 target taxonomy YAML against schema requirements."""

from pathlib import Path

from L1.validators.common import (
    ValidationResult,
    PASS,
    WARNING,
    BLOCKED,
    FAIL,
    load_yaml,
)


def validate(path: str | Path = "L1/target_taxonomy.yaml") -> ValidationResult:
    """
    Validate the target taxonomy file.

    Returns ValidationResult with PASS or FAIL status and error list.
    """
    errors: list[str] = []
    warnings: list[str] = []

    data = load_yaml(str(path))
    if data is None:
        return ValidationResult(
            name="TargetTaxonomy",
            status=FAIL,
            errors=[f"Could not load or parse: {path}"],
        )

    if "allowed_target_kinds" not in data:
        errors.append("Missing top-level key: allowed_target_kinds")
    else:
        kinds = data["allowed_target_kinds"]
        if not isinstance(kinds, list):
            errors.append("allowed_target_kinds must be a list")
        elif "framework" not in kinds:
            errors.append("allowed_target_kinds must include 'framework'")

    if "target_kinds" not in data:
        errors.append("Missing top-level key: target_kinds")
    elif "framework" not in data["target_kinds"]:
        errors.append("Missing target_kinds.framework")

    if "framework_rules" not in data:
        errors.append("Missing top-level key: framework_rules")
    else:
        fw = data["framework_rules"]
        if not isinstance(fw, dict):
            errors.append("framework_rules must be a mapping")
        else:
            caps = fw.get("required_capabilities", [])
            if not isinstance(caps, list) or len(caps) == 0:
                errors.append("framework_rules.required_capabilities must be a non-empty list")

            forbidden = fw.get("forbidden_capabilities", [])
            if not isinstance(forbidden, list) or len(forbidden) == 0:
                errors.append("framework_rules.forbidden_capabilities must be a non-empty list")

            manifest_fields = fw.get("required_manifest_fields", [])
            if not isinstance(manifest_fields, list) or len(manifest_fields) == 0:
                errors.append("framework_rules.required_manifest_fields must be a non-empty list")

    if "migration" not in data:
        errors.append("Missing top-level key: migration")
    else:
        mig = data["migration"]
        if mig.get("missing_target_kind_default") != "agent":
            warnings.append("migration.missing_target_kind_default should be 'agent'")
        if mig.get("allow_legacy_profiles_without_target_kind") is not True:
            warnings.append("migration.allow_legacy_profiles_without_target_kind should be true")

    status = FAIL if errors else (WARNING if warnings else PASS)
    return ValidationResult(
        name="TargetTaxonomy",
        status=status,
        errors=errors,
        warnings=warnings,
    )

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.packaging.packaging_models import (
    ALL_PACKAGE_FORMATS,
    ALL_PACKAGE_STATUSES,
    PACKAGE_NAME,
    PACKAGE_VERSION,
    RUNTIME_ARTIFACT_ROOT,
    REJECTION_SCHEMA_INVALID,
    SEVERITY_BLOCKER,
    PackageManifest,
    new_id,
)


def load_package_manifest(manifest_path: Path) -> PackageManifest:
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except Exception as exc:
        return PackageManifest(errors=[f"Failed to read manifest file {manifest_path}: {exc}"])

    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        return PackageManifest(errors=[f"Invalid JSON in manifest {manifest_path}: {exc}"])

    if not isinstance(data, dict):
        return PackageManifest(errors=[f"Manifest root must be a JSON object, got {type(data).__name__}"])

    errors: list[str] = []
    if "package_name" not in data or not data["package_name"]:
        errors.append("Missing or empty required field: package_name")
    if "package_version" not in data or not data["package_version"]:
        errors.append("Missing or empty required field: package_version")

    manifest = PackageManifest(errors=errors)
    manifest.manifest_id = data.get("manifest_id", new_id("manifest"))

    dataclass_fields = set(manifest.__dataclass_fields__)
    for key, value in data.items():
        if key in dataclass_fields:
            setattr(manifest, key, value)

    if errors:
        return manifest

    return manifest


def validate_package_manifest(
    manifest: PackageManifest,
    schema_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []

    for i, pat in enumerate(manifest.include_patterns):
        if not isinstance(pat, str):
            errors.append(
                f"include_patterns[{i}] must be a string, "
                f"got {type(pat).__name__}"
            )

    for i, pat in enumerate(manifest.exclude_patterns):
        if not isinstance(pat, str):
            errors.append(
                f"exclude_patterns[{i}] must be a string, "
                f"got {type(pat).__name__}"
            )

    for i, fpath in enumerate(manifest.forbidden_paths):
        if not isinstance(fpath, str):
            errors.append(
                f"forbidden_paths[{i}] must be a string, "
                f"got {type(fpath).__name__}"
            )

    for i, ext in enumerate(manifest.forbidden_extensions):
        if not isinstance(ext, str):
            errors.append(
                f"forbidden_extensions[{i}] must be a string, "
                f"got {type(ext).__name__}"
            )

    if manifest.default_package_format not in ALL_PACKAGE_FORMATS:
        errors.append(
            f"default_package_format must be one of {ALL_PACKAGE_FORMATS}, "
            f"got {manifest.default_package_format!r}"
        )

    for i, fmt in enumerate(manifest.allowed_package_formats):
        if fmt not in ALL_PACKAGE_FORMATS:
            errors.append(
                f"allowed_package_formats[{i}] must be one of {ALL_PACKAGE_FORMATS}, "
                f"got {fmt!r}"
            )

    if not isinstance(manifest.source_root, str):
        errors.append(
            f"source_root must be a string, "
            f"got {type(manifest.source_root).__name__}"
        )

    runtime_roots_checks = {
        "build_output_root": manifest.build_output_root,
        "staging_root": manifest.staging_root,
        "evidence_root": manifest.evidence_root,
        "report_root": manifest.report_root,
    }
    for root_name, root_val in runtime_roots_checks.items():
        if not root_val.startswith(RUNTIME_ARTIFACT_ROOT):
            errors.append(
                f"{root_name} must be under "
                f"{RUNTIME_ARTIFACT_ROOT!r}, got {root_val!r}"
            )

    has_readme = any(
        "README.md" in req for req in manifest.required_files
    )
    has_makefile = any(
        "Makefile" in req for req in manifest.required_files
    )
    if not has_readme:
        errors.append("required_files should include at least a README.md or equivalent")
    if not has_makefile:
        errors.append("required_files should include at least a Makefile or equivalent")

    if schema_path is not None:
        try:
            schema_raw = schema_path.read_text(encoding="utf-8")
            schema = json.loads(schema_raw)
            if not isinstance(schema, dict):
                errors.append(f"Schema file {schema_path} must contain a JSON object")
        except FileNotFoundError:
            errors.append(f"Schema file not found: {schema_path}")
        except json.JSONDecodeError as exc:
            errors.append(f"Schema file {schema_path} is not valid JSON: {exc}")

    return errors

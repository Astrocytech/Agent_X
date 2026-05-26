from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]

SCALAR_KEYS = {
    "version",
    "seed_package_version",
    "release_type",
    "generated",
}

ALLOWED_TOP_LEVEL_IMPORTS = {
    "__future__",
    "abc",
    "ast",
    "collections",
    "dataclasses",
    "datetime",
    "enum",
    "hashlib",
    "importlib",
    "inspect",
    "jsonschema",
    "json",
    "logging",
    "os",
    "pathlib",
    "shutil",
    "sys",
    "tempfile",
    "time",
    "typing",
    "uuid",
    "yaml",
    "CODE",
    "core_kernel",
    "governance",
    "kernel_composition",
    "profiles",
    "scripts",
    "tool_gateway",
}

FORBIDDEN_IMPORTS = {
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "httpx",
    "paramiko",
    "ftplib",
    "docker",
    "torch",
    "transformers",
    "openai",
    "anthropic",
    "selenium",
    "playwright",
    "pip",
    "setuptools",
    "poetry",
    "conda",
}

ALLOWED_SEED_TOOLS = {"emit_answer.py"}

FORBIDDEN_IMPORT_EXEMPT = {
    "CODE/core_kernel/evidence/",
    "CODE/kernel_composition/local_seed_ports/local_evidence_writer_port.py",
    "CODE/kernel_composition/local_seed_ports/local_trace_port.py",
    "CODE/kernel_composition/local_seed_ports/local_checkpoint_port.py",
}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path.name} must parse to a mapping")
    return data


def flatten_manifest_files(manifest: dict) -> set[str]:
    files: set[str] = set()
    for value in manifest.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    files.add(item)
    return files


def iter_seed_python_files(manifest: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for key, value in manifest.items():
        if key in SCALAR_KEYS:
            continue
        if not isinstance(value, list):
            continue
        for rel_path in value:
            if isinstance(rel_path, str) and rel_path.endswith(".py"):
                files.append(ROOT / rel_path)
    return files


def validate_seed_package_manifest() -> dict[str, Any]:
    path = ROOT / "SEED_PACKAGE_MANIFEST.yaml"
    manifest = load_yaml(path)

    required_keys = {
        "version",
        "seed_package_version",
        "release_type",
        "seed_l0_public_api",
        "seed_l0_public_contracts",
        "seed_l0_runtime",
        "seed_l0_composition",
        "seed_l0_default_ports",
        "seed_l0_profiles",
        "seed_l0_gateway",
        "seed_l0_governance",
        "seed_authority",
    }

    missing = required_keys - set(manifest)
    if missing:
        raise AssertionError(f"SEED_PACKAGE_MANIFEST.yaml missing keys: {sorted(missing)}")

    for key, value in manifest.items():
        if key in SCALAR_KEYS:
            continue
        if not isinstance(value, list):
            raise AssertionError(f"{key} must be a list")
        for rel_path in value:
            if not isinstance(rel_path, str):
                raise AssertionError(f"{key} contains non-string path: {rel_path!r}")
            full_path = ROOT / rel_path
            if not full_path.exists():
                raise AssertionError(f"{key} references missing path: {rel_path}")

    return manifest


def validate_capability_manifest() -> None:
    path = ROOT / "CAPABILITY_MANIFEST.yaml"
    manifest = load_yaml(path)

    required_keys = {
        "version",
        "generated",
        "kernel_capabilities",
        "blocked_capabilities",
    }

    missing = required_keys - set(manifest)
    if missing:
        raise AssertionError(f"CAPABILITY_MANIFEST.yaml missing keys: {sorted(missing)}")

    for section in ("kernel_capabilities", "blocked_capabilities"):
        entries = manifest[section]
        if not isinstance(entries, list):
            raise AssertionError(f"{section} must be a list")
        ids: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise AssertionError(f"{section} contains non-mapping entry: {entry!r}")
            capability_id = entry.get("id")
            if not capability_id:
                raise AssertionError(f"{section} entry missing id: {entry!r}")
            if capability_id in ids:
                raise AssertionError(f"{section} duplicate id: {capability_id}")
            ids.add(capability_id)


def validate_manifest_closure(manifest: dict[str, Any]) -> None:
    manifest_files = flatten_manifest_files(manifest)

    for py in Path(ROOT / "CODE").rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        rel = py.relative_to(ROOT).as_posix()
        if rel not in manifest_files:
            raise AssertionError(
                f"CODE python file not in SEED_PACKAGE_MANIFEST.yaml: {rel}"
            )


def validate_seed_import_boundary(manifest: dict[str, Any]) -> None:
    for path in iter_seed_python_files(manifest):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()

        for node in ast.walk(tree):
            imported_name: str | None = None

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.name.split(".")[0]

                    if imported_name in FORBIDDEN_IMPORTS:
                        exempt = any(rel.startswith(e) for e in FORBIDDEN_IMPORT_EXEMPT)
                        if not exempt:
                            raise AssertionError(
                                f"{rel} imports forbidden module: {imported_name}"
                            )

                    if imported_name in ("extensions", "examples"):
                        raise AssertionError(
                            f"{rel} imports extension code: {imported_name}"
                        )

                    if imported_name not in ALLOWED_TOP_LEVEL_IMPORTS:
                        raise AssertionError(
                            f"{rel} imports forbidden top-level module: {imported_name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                if node.level > 0:
                    continue
                imported_name = node.module.split(".")[0]

                if imported_name in FORBIDDEN_IMPORTS:
                    exempt = any(rel.startswith(e) for e in FORBIDDEN_IMPORT_EXEMPT)
                    if not exempt:
                        raise AssertionError(
                            f"{rel} imports forbidden module: {imported_name}"
                        )

                if imported_name in ("extensions", "examples"):
                    raise AssertionError(
                        f"{rel} imports extension code: {imported_name}"
                    )

                if imported_name not in ALLOWED_TOP_LEVEL_IMPORTS:
                    raise AssertionError(
                        f"{rel} imports forbidden top-level module: {imported_name}"
                    )


def validate_test_boundary() -> None:
    test_dir = ROOT / "tests" / "seed_l0"
    for py in test_dir.glob("*.py"):
        if py.name == "__init__.py":
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in ("extensions", "examples"):
                        raise AssertionError(
                            f"tests/seed_l0/{py.name} imports extension code: {root}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                if node.level > 0:
                    continue
                root = node.module.split(".")[0]
                if root in ("extensions", "examples"):
                    raise AssertionError(
                        f"tests/seed_l0/{py.name} imports extension code: {root}"
                    )


def validate_seed_tool_registry() -> None:
    seed_tools_dir = ROOT / "CODE" / "tool_gateway" / "seed_tools"
    for item in seed_tools_dir.glob("*.py"):
        if item.name == "__init__.py":
            continue
        if item.name not in ALLOWED_SEED_TOOLS:
            raise AssertionError(
                f"Unexpected seed tool file: {item.relative_to(ROOT).as_posix()}"
            )

    sys.path.insert(0, str(ROOT / "CODE"))
    from tool_gateway.seed_tool_registry import list_seed_tool_names  # type: ignore[import-untyped]
    names = list_seed_tool_names()
    if set(names) != {"seed.emit_answer"}:
        raise AssertionError(f"seed tools must be exactly seed.emit_answer, got: {names}")


def validate_blocked_capabilities() -> None:
    invariants = load_yaml(ROOT / "SEED_INVARIANTS.yaml")
    capability = load_yaml(ROOT / "CAPABILITY_MANIFEST.yaml")

    forbidden_classes = set(
        invariants.get("tool_boundary", {}).get("forbidden_l0_tool_classes", [])
    )
    blocked_ids = {e["id"] for e in capability["blocked_capabilities"]}

    for cls in forbidden_classes:
        if "self_modification" in cls:
            mapped = "production_self_modification"
        elif "shell" in cls:
            mapped = "direct_shell_execution"
        elif "network" in cls:
            mapped = "uncontrolled_network_access"
        elif "filesystem_write" in cls:
            mapped = "uncontrolled_filesystem_write"
        elif "promotion" in cls:
            mapped = "runtime_promotion"
        elif "package_install" in cls:
            mapped = "package_installation"
        elif "credential_access" in cls:
            mapped = "credential_access"
        else:
            mapped = f"direct_{cls}_access"
        if mapped not in blocked_ids:
            raise AssertionError(
                f"forbidden_l0_tool_class '{cls}' has no matching blocked_capability "
                f"in CAPABILITY_MANIFEST.yaml (expected id: {mapped})"
            )


def validate_profile_structure() -> None:
    profiles_dir = ROOT / "CODE" / "profiles" / "builtin"
    for yaml_file in profiles_dir.glob("*.yaml"):
        profile = load_yaml(yaml_file)
        if "id" not in profile:
            raise AssertionError(f"Profile {yaml_file.name} missing 'id'")
        if "allowed_tools" not in profile:
            raise AssertionError(f"Profile {yaml_file.name} missing 'allowed_tools'")


def main() -> None:
    manifest = validate_seed_package_manifest()
    validate_capability_manifest()
    validate_manifest_closure(manifest)
    validate_seed_import_boundary(manifest)
    validate_test_boundary()
    validate_seed_tool_registry()
    validate_blocked_capabilities()
    validate_profile_structure()
    print("=== validate-seed-manifests: OK ===")


if __name__ == "__main__":
    main()

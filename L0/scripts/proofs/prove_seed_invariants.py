"""Seed invariant proof — machine-checked invariant contract for L0 seed."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / "L0/CODE"

FORBIDDEN_IMPORTS_IN_L0 = {
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "httpx",
    "paramiko",
    "ftplib",
}

L0_FORBIDDEN_EXTENSION_IMPORT_ROOTS = [
    ROOT / "L0/CODE" / "core_kernel",
    ROOT / "L0/CODE" / "governance",
    ROOT / "L0/CODE" / "tool_gateway" / "seed_tools",
    ROOT / "L0/CODE" / "kernel_composition" / "local_seed_ports",
]

ALLOWED_SEED_TOOLS = {"emit_answer.py"}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iter_python_files(root: Path):
    yield from root.rglob("*.py")


def flatten_manifest_files(manifest: dict) -> set[str]:
    files: set[str] = set()
    for value in manifest.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    files.add(item)
    return files


def module_imports_extensions(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("extensions") or ".extensions" in alias.name:
                    return True
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith("extensions") or ".extensions" in mod:
                return True
    return False


def has_forbidden_import(tree: ast.AST) -> list[str]:
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS_IN_L0:
                    found.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS_IN_L0:
                found.append(node.module or root)
    return found


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    manifest = load_yaml(ROOT / "L0/manifests/SEED_PACKAGE_MANIFEST.yaml")
    invariants = load_yaml(ROOT / "L0/manifests/SEED_INVARIANTS.yaml")
    manifest_files = flatten_manifest_files(manifest)

    errors: list[str] = []

    for rel in manifest_files:
        if not (ROOT / rel).exists():
            errors.append(f"manifest file missing: {rel}")

    for py in iter_python_files(CODE):
        rel = py.relative_to(ROOT).as_posix()

        if "__pycache__" in rel:
            continue

        if rel.startswith("examples/extensions/"):
            continue

        if rel not in manifest_files:
            errors.append(f"L0 python file missing from SEED_PACKAGE_MANIFEST.yaml: {rel}")

        source = py.read_text(encoding="utf-8")
        tree = ast.parse(source)

        if any(is_under(py, root) for root in L0_FORBIDDEN_EXTENSION_IMPORT_ROOTS):
            if module_imports_extensions(tree):
                errors.append(f"L0 imports extension code: {rel}")

        forbidden = has_forbidden_import(tree)
        if forbidden and not rel.startswith(
            (
        "L0/CODE/core_kernel/evidence/",
        "L0/CODE/kernel_composition/local_seed_ports/local_evidence_writer_port.py",
        "L0/CODE/kernel_composition/local_seed_ports/local_trace_port.py",
        "L0/CODE/kernel_composition/local_seed_ports/local_checkpoint_port.py",
            )
        ):
            errors.append(f"forbidden L0 import in {rel}: {forbidden}")

    seed_tools = ROOT / "L0/CODE" / "tool_gateway" / "seed_tools"
    for item in seed_tools.glob("*.py"):
        if item.name == "__init__.py":
            continue
        if item.name not in ALLOWED_SEED_TOOLS:
            errors.append(f"unexpected seed tool: {item.relative_to(ROOT).as_posix()}")

    if errors:
        print("SEED INVARIANT PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("SEED INVARIANT PROOF: OK")
    print(f"- checked manifest files: {len(manifest_files)}")
    print(f"- checked python files: {len(list(iter_python_files(CODE)))}")
    print(f"- authority: {invariants.get('name', 'unknown')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

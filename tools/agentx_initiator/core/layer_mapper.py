from __future__ import annotations
from pathlib import Path
from typing import Optional
from agentx_initiator.core.path_registry import _detect_repo_root


LAYER_RULES = {
    "L0": {
        "allowed_dirs": ["CODE", "docs", "scripts", "tests", "manifests"],
        "cannot_import": ["L1", "L2", "L3", "L4", "L5"],
        "is_independent": True,
        "is_protected": True,
    },
    "L1": {
        "allowed_dirs": [
            "controller", "docs", "fic", "standards", "tests",
            "sib", "ecosystem", "eqc", "generated", "evidence",
            "evaluators", "promotion", "schemas", "templates", "fixtures",
            "validators", "patch_planner", "proof_runner", "workflows",
            "prompts", "reports",
        ],
        "cannot_import": ["L2", "L3", "L4", "L5"],
        "is_independent": False,
        "is_protected": False,
    },
    "L2": {
        "allowed_dirs": [
            "profiles", "blueprints", "evaluation_specs", "integration_specs",
            "extension_specs", "docs", "tests", "standards", "generated",
            "fic", "sib", "eqc", "validators", "evidence", "bootstrap",
        ],
        "forbidden_runtime_dirs": [
            "controller", "runtime", "agents", "tools",
            "model_router", "memory", "autonomy",
        ],
        "is_independent": False,
        "is_protected": False,
    },
}


def classify_agentx_layer(path: Path) -> str:
    try:
        resolved = path.resolve()
    except OSError:
        return "unknown"

    root = _detect_repo_root().resolve()
    try:
        rel = resolved.relative_to(root)
    except ValueError:
        return "unknown"

    parts = rel.parts
    if not parts:
        return "unknown"

    first = parts[0]
    if first in ("L0", "L1", "L2"):
        return first
    if first == "agentx_initiator":
        return "L1"
    if first == "validators":
        return "L1"
    if first == "scripts":
        return "L1"
    if first in ("profiles", "blueprints", "integration_specs",
                 "evaluation_specs"):
        return "L2"

    return "unknown"


def is_protected_path(path: Path) -> bool:
    layer = classify_agentx_layer(path)
    if layer in ("L0",):
        return True
    try:
        resolved = path.resolve()
    except OSError:
        return False
    if "standards" in resolved.parts and "governance" in resolved.parts:
        return True
    if path.suffix == ".json" and "schemas" in resolved.parts:
        return False
    return False


def classify_protection_level(path: Path, layer: Optional[str] = None) -> str:
    if layer is None:
        layer = classify_agentx_layer(path)
    if layer == "L0":
        return "critical"
    try:
        resolved = path.resolve()
    except OSError:
        return "low"
    parts_lower = [p.lower() for p in resolved.parts]
    if "standards" in parts_lower and "governance" in parts_lower:
        return "high"
    if path.suffix == ".json" and "schemas" in resolved.parts:
        return "medium"
    if "test" in path.name.lower():
        return "low"
    if layer == "unknown":
        return "low"
    return "medium"


def build_layer_map(files: Optional[list] = None,
                    directories: Optional[list] = None) -> dict:
    if files is not None or directories is not None:
        layers: dict[str, dict] = {}
        for entry in (files or []) + (directories or []):
            layer = classify_agentx_layer(
                Path(entry.path) if hasattr(entry, "path") else Path(str(entry))
            )
            if layer not in layers:
                layers[layer] = {"entries": [], "file_count": 0}
            layers[layer]["entries"].append(str(entry))
            layers[layer]["file_count"] += 1
        return {
            "schema_version": "1.0",
            "layer_summary": {k: v["file_count"] for k, v in layers.items()},
            "entries": layers,
            "warnings": [],
            "errors": [],
        }

    root = _detect_repo_root()
    mapping = {}
    for layer_name, rules in LAYER_RULES.items():
        layer_path = root / layer_name
        if not layer_path.exists():
            continue
        dirs = [d.name for d in layer_path.iterdir() if d.is_dir()]
        violations = _detect_violations(layer_name, dirs, rules)
        mapping[layer_name] = {
            "path": str(layer_path),
            "exists": True,
            "directories": dirs,
            "rules": rules,
            "violations": violations,
        }
    return mapping


def build_protected_path_map(files: Optional[list] = None,
                              directories: Optional[list] = None) -> dict:
    entries = []
    if files:
        for f in files:
            p = Path(f.path) if hasattr(f, "path") else Path(str(f))
            if is_protected_path(p):
                entries.append({
                    "path": str(p),
                    "protection_level": classify_protection_level(p),
                    "layer": classify_agentx_layer(p),
                    "reason": "",
                })
    if directories:
        for d in directories:
            p = Path(d.path) if hasattr(d, "path") else Path(str(d))
            if is_protected_path(p):
                entries.append({
                    "path": str(p),
                    "protection_level": classify_protection_level(p),
                    "layer": classify_agentx_layer(p),
                    "reason": "",
                })
    return {
        "schema_version": "1.0",
        "entries": entries,
        "warnings": [],
        "errors": [],
    }


def _detect_violations(layer: str, dirs: list[str], rules: dict) -> list[str]:
    violations = []
    if "forbidden_runtime_dirs" in rules:
        for forbidden in rules["forbidden_runtime_dirs"]:
            if forbidden in dirs:
                violations.append(f"Contains forbidden runtime dir: {forbidden}")
    return violations

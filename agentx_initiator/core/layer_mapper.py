from pathlib import Path
from agentx_initiator.core.paths import repo_root


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


def build_layer_map() -> dict:
    root = repo_root()
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


def _detect_violations(layer: str, dirs: list[str], rules: dict) -> list[str]:
    violations = []
    if "forbidden_runtime_dirs" in rules:
        for forbidden in rules["forbidden_runtime_dirs"]:
            if forbidden in dirs:
                violations.append(f"Contains forbidden runtime dir: {forbidden}")
    return violations

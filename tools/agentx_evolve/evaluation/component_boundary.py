"""Component boundary enforcement.

Item 41 (36.1): Enforce dependency direction between layers
and prevent lower layers from importing higher layers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


LAYER_ORDER = [
    "L0",
    "L1",
    "L2",
    "tools/agentx_initiator",
    "tools/agentx_evolve",
    "examples",
    "benchmarks",
    "tests",
]

LAYER_RANK = {layer: i for i, layer in enumerate(LAYER_ORDER)}

# Disallowed import directions: lower layer -> higher layer (by rank)
# Higher can import lower, but not vice versa.
FORBIDDEN_UPWARD = True

# Explicitly allowed cross-layer imports
ALLOWED_CROSS_IMPORTS: list[tuple[str, str]] = [
    ("tests", "tools/agentx_evolve"),
    ("tests", "examples"),
    ("tests", "benchmarks"),
    ("benchmarks", "tools/agentx_evolve"),
    ("examples", "tools/agentx_evolve"),
    ("examples", "benchmarks"),
]


def classify_path(path: str) -> str | None:
    """Classify a file path into the layer it belongs to."""
    p = path.replace("\\", "/")
    for layer in LAYER_ORDER:
        if p.startswith(layer):
            return layer
    return None


def check_import(source_file: str, imported_module: str) -> dict[str, Any]:
    """Check if an import violates layer dependency direction."""
    source_layer = classify_path(source_file)
    # Determine target layer from the import path
    target_layer = None
    for layer in LAYER_ORDER:
        if imported_module.startswith(layer.replace("/", ".")) or imported_module.startswith(layer):
            target_layer = layer
            break

    if source_layer is None or target_layer is None:
        return {"allowed": True, "reason": "unclassified path"}

    source_rank = LAYER_RANK.get(source_layer, 99)
    target_rank = LAYER_RANK.get(target_layer, 99)

    # Allow same layer
    if source_rank == target_rank:
        return {"allowed": True, "reason": "same layer"}

    # Lower rank importing from higher rank is forbidden
    if FORBIDDEN_UPWARD and source_rank < target_rank:
        # Check explicit allowlist
        if (source_layer, target_layer) in ALLOWED_CROSS_IMPORTS:
            return {"allowed": True, "reason": f"explicitly allowed: {source_layer} -> {target_layer}"}
        return {
            "allowed": False,
            "reason": f"{source_layer} -> {target_layer}: lower layer cannot import higher layer",
        }

    # Higher rank importing from lower rank is allowed
    return {"allowed": True, "reason": f"{source_layer} -> {target_layer}: downward import allowed"}


def scan_file_imports(file_path: str) -> list[dict[str, Any]]:
    """Scan a Python file for import statements and check them."""
    import ast
    results = []
    p = Path(file_path)
    if not p.exists() or not p.suffix == ".py":
        return results

    try:
        tree = ast.parse(p.read_text())
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result = check_import(str(p), alias.name)
                if not result["allowed"]:
                    results.append({
                        "file": str(p),
                        "import": alias.name,
                        "reason": result["reason"],
                        "line": node.lineno,
                    })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result = check_import(str(p), node.module)
                if not result["allowed"]:
                    results.append({
                        "file": str(p),
                        "import": node.module,
                        "reason": result["reason"],
                        "line": node.lineno,
                    })
    return results


def scan_directory(directory: str | Path) -> list[dict[str, Any]]:
    """Recursively scan all Python files in a directory for boundary violations."""
    all_violations = []
    base = Path(directory)
    for f in sorted(base.rglob("*.py")):
        violations = scan_file_imports(str(f))
        all_violations.extend(violations)
    return all_violations

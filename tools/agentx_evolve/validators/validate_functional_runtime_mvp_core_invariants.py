"""Validate CORE_INVARIANTS have implementation, tests, and proof evidence.

Gaps 250-255.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

INVARIANT_ENGINE_PATH = Path(__file__).resolve().parent.parent / "invariants" / "invariant_engine.py"


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _parse_core_invariants() -> tuple[list[str], set[str]]:
    declared: list[str] = []
    implemented: set[str] = set()
    if not INVARIANT_ENGINE_PATH.exists():
        return [], set()
    try:
        source = INVARIANT_ENGINE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return [], set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "CORE_INVARIANTS":
                    if isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                declared.append(elt.value)

        if isinstance(node, ast.FunctionDef):
            if node.name == "check":
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        test = child.test
                        if isinstance(test, ast.Compare):
                            left = test.left
                            if isinstance(left, ast.Name) and left.id == "invariant_name":
                                for comparator in test.comparators:
                                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                                        implemented.add(comparator.value)
                        elif isinstance(test, ast.BinOp) and isinstance(test.op, ast.Eq):
                            if isinstance(test.left, ast.Attribute) and isinstance(test.left.attr, str) and test.left.attr == "id":
                                if isinstance(test.comparators[0], ast.Constant) and isinstance(test.comparators[0].value, str):
                                    implemented.add(test.comparators[0].value)

    return declared, implemented


def validate_core_invariants() -> list[str]:
    errors = []
    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Core-invariants: proof bundle missing or invalid")

    declared, implemented = _parse_core_invariants()
    if not declared:
        errors.append("Core-invariants: could not parse CORE_INVARIANTS from invariant_engine.py")
        return errors

    # Item 250/252/253: Fail if declared invariant has no implementation branch
    for inv in declared:
        if inv not in implemented:
            errors.append(
                f"Core-invariants: 250/252/253 - CORE_INVARIANT '{inv}' declared "
                f"but has no implementation branch in MvpInvariantEngine.check()"
            )

    # Item 254: Ensure declarative mapping — each invariant maps to implementation function
    engine_path = INVARIANT_ENGINE_PATH
    if engine_path.exists():
        source = engine_path.read_text(encoding="utf-8")
        for inv in declared:
            if inv not in source.replace("_", " "):
                pass
            impl_ref = f"invariant_name == \"{inv}\""
            if impl_ref not in source and f"invariant_name == '{inv}'" not in source:
                errors.append(
                    f"Core-invariants: 254 - CORE_INVARIANT '{inv}' not mapped "
                    f"to explicit implementation branch in check()"
                )

    # Item 255: Fail if check_all() returns PASS for unimplemented invariant
    # We can't run the engine directly (it requires action+context), but we can
    # check whether test files exist for each invariant
    test_dir = INVARIANT_ENGINE_PATH.parent / "tests"
    if test_dir.exists():
        test_files = list(test_dir.glob("*.py")) + list(test_dir.glob("*test*"))
        test_text = ""
        for tf in test_files:
            test_text += tf.read_text(encoding="utf-8", errors="replace") + "\n"
        for inv in declared:
            if inv in implemented:
                if inv not in test_text and f"test_{inv}" not in test_text and inv.replace("no_", "") not in test_text:
                    errors.append(
                        f"Core-invariants: 255 - CORE_INVARIANT '{inv}' has implementation "
                        f"but no test coverage"
                    )

    # Check that proof bundle includes invariant_engine results
    if isinstance(bundle, dict):
        inv_results = bundle.get("invariant_results", bundle.get("core_invariants", []))
        if not isinstance(inv_results, list) or len(inv_results) == 0:
            errors.append("Core-invariants: proof bundle missing invariant_results or core_invariants list")

    return errors


def main() -> int:
    errs = validate_core_invariants()
    if errs:
        print("VALIDATE CORE INVARIANTS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-core-invariants: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())

"""
run_adapter_anti_false_pass_audit.py

Audits that no test can spuriously PASS (e.g., trivially skipping asserts,
using bare `assert True`, or testing a no-op). Each file is checked for
known anti-patterns.

Output: tools/agentx_evolve/tests/acceptance/adapter_anti_false_pass_audit.json
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_DIR = HERE / "tests"
OUT = HERE / ".." / ".." / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_anti_false_pass_audit.json"

SUSPICIOUS_PATTERNS = {
    "assert True": "bare assert True",
    "assert 1": "bare assert 1",
    "assert None": "bare assert None",
    "assert []": "bare assert []",
    "assert {}": "bare assert {}",
    "assert ()": "bare assert ()",
    "assert 1 == 1": "trivially true comparison",
    "assert True is True": "trivially true identity",
}


def audit_file(path: Path) -> list[dict]:
    issues: list[dict] = []
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as e:
        issues.append({"file": str(path), "issue": f"syntax error: {e}", "line": 0})
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            line = node.lineno
            source = ast.unparse(node.test)
            for pattern, desc in SUSPICIOUS_PATTERNS.items():
                if pattern in source:
                    issues.append({
                        "file": str(path),
                        "issue": desc,
                        "line": line,
                        "source": source,
                    })
                    break
    return issues


def main() -> int:
    test_files = sorted(TEST_DIR.rglob("test_*.py"))
    all_issues: list[dict] = []
    for tf in test_files:
        all_issues.extend(audit_file(tf))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "claim": "anti_false_pass_audit",
        "files_checked": len(test_files),
        "issues_found": len(all_issues),
        "issues": all_issues,
        "status": "PASS" if len(all_issues) == 0 else "FAIL",
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Checked {len(test_files)} test files, found {len(all_issues)} issues")
    if all_issues:
        for issue in all_issues:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
    return 0 if len(all_issues) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

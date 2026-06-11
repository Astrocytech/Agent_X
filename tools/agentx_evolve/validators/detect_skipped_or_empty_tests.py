#!/usr/bin/env python3
"""Detect skipped or empty tests."""
import ast, sys, os
from pathlib import Path

def detect(test_dir="tests"):
    issues = []
    base = Path(test_dir)
    if not base.is_dir():
        return issues
    for py_file in base.rglob("test_*.py"):
        try:
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                        issues.append(f"{py_file}:{node.lineno}: test '{node.name}' is empty/pass-only")
        except SyntaxError:
            issues.append(f"{py_file}: syntax error")
    return issues

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "tests"
    issues = detect(target)
    if issues:
        print(f"ISSUES: {len(issues)} empty/skipped test(s):"); [print(f"  - {i}") for i in issues]
    else:
        print(f"PASS: no empty or skipped tests found in {target}")

if __name__ == "__main__":
    main()

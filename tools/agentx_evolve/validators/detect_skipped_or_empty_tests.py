"""Detect skipped, empty, or weak tests.

Item 14.2: Strengthened detection for tests that do not verify real behavior.
"""
import ast, sys, os
from pathlib import Path


def detect(test_dir="tests"):
    issues = []
    base = Path(test_dir)
    if not base.is_dir():
        return issues
    for py_file in base.rglob("test_*.py"):
        try:
            text = py_file.read_text()
            tree = ast.parse(text)
        except SyntaxError:
            issues.append(f"{py_file}: syntax error")
            continue

        for node in ast.walk(tree):
            # Check test functions
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Detect @unittest.skip / @pytest.mark.skip decorators
                is_skipped = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and func.attr in ("skip", "skipIf", "skipUnless"):
                            is_skipped = True
                    elif isinstance(dec, ast.Attribute) and dec.attr == "skip":
                        is_skipped = True
                if is_skipped:
                    issues.append(f"{py_file}:{node.lineno}: test '{node.name}' is skipped")
                    continue

                # Empty or pass-only body
                if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                    issues.append(f"{py_file}:{node.lineno}: test '{node.name}' is empty/pass-only")
                    continue

                # Only-import body
                if len(node.body) == 1 and isinstance(node.body[0], ast.Import):
                    issues.append(f"{py_file}:{node.lineno}: test '{node.name}' only imports")
                    continue

                # Assert True-only body
                if (len(node.body) == 1 and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and node.body[0].value.value is True):
                    issues.append(f"{py_file}:{node.lineno}: test '{node.name}' only asserts True")
                    continue

                # Broad try/except: pass
                _check_broad_except(py_file, node, issues)

    return issues


def _check_broad_except(py_file, func_node, issues):
    for node in ast.walk(func_node):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    issues.append(f"{py_file}:{func_node.lineno}: test '{func_node.name}' has bare except")
                elif isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                    body_has_assert = any(
                        isinstance(n, ast.Assert) for n in ast.walk(handler)
                    )
                    if not body_has_assert:
                        issues.append(
                            f"{py_file}:{func_node.lineno}: test '{func_node.name}' "
                            f"has broad `except Exception` without assertion"
                        )


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "tests"
    issues = detect(target)
    if issues:
        print(f"ISSUES: {len(issues)} weak/empty/skipped test(s):"); [print(f"  - {i}") for i in issues]
    else:
        print(f"PASS: no empty or skipped tests found in {target}")


if __name__ == "__main__":
    main()

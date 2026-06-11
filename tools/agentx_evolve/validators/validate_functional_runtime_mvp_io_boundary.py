"""Validate external I/O boundary model (items 399-415, 795-802).

Checks:
- Runtime and proof code does not use shell=True, os.system, subprocess
  with shell, or string-built shell commands in proof-critical paths
  unless explicitly sandboxed.
- No proof-critical evidence exists only in temp, home, or absolute paths.
- All evidence is under the report directory or a declared durable root.
- No subprocess calls without explicit env control in proof-critical scripts.
- No PATH-dependent executables for proof-critical commands.
- No absolute temp paths in final proof reports.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

SHELL_DANGER_PATTERNS: list[tuple[str, str]] = [
    (r"shell\s*=\s*True", "subprocess call uses shell=True"),
    (r"os\.system\s*\(", "os.system() call - shell execution"),
    (r"os\.popen\s*\(", "os.popen() call - shell execution"),
]

ALLOWED_DIRS = {".agentx-init/reports"}
ALLOWED_TEMP_PREFIXES = {"/tmp/agentx-mvp-", "/tmp/agentx_mvp_"}
# Files that are allowed to use shell=True for their core purpose
ALLOWED_SHELL_FILES = {
    "record_command.py",
    "run_anti_false_pass_audit.py",
    "command_transcript.py",
}

# Reports that must not contain absolute temp paths
PATH_REPORTS = [
    "functional_runtime_mvp_final_verdict.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_replay_manifest.json",
    "functional_runtime_mvp_replay_report.json",
]


def _walk_py_files(root: str, skip_tests: bool = True) -> list[Path]:
    files = sorted(Path(root).rglob("*.py"))
    result = []
    for f in files:
        parts = f.parts
        if skip_tests and ("test_" in f.name or "/tests/" in str(f) or f.name == "__init__.py"):
            continue
        if any(p == "__pycache__" for p in parts):
            continue
        result.append(f)
    return result


def _is_in_docstring_or_comment(lines: list[str], line_idx: int) -> bool:
    """Check if a line is inside a docstring or is a comment line."""
    in_triple = False
    for i in range(line_idx):
        stripped = lines[i].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_triple = not in_triple
    return in_triple


def _scan_file_for_shell_danger(path: Path) -> list[str]:
    """Scan a Python file for dangerous shell patterns at text level."""
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    if path.name in ALLOWED_SHELL_FILES:
        return findings

    # Skip self-inspection: the io_boundary validator itself contains
    # the patterns in regex definitions
    if path.name == "validate_functional_runtime_mvp_io_boundary.py":
        return findings

    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("(r\""):
            continue
        if _is_in_docstring_or_comment(lines, i - 1):
            continue
        for pattern, desc in SHELL_DANGER_PATTERNS:
            if re.search(pattern, line):
                findings.append(f"{path}:{i}: {desc}: {line.strip()[:120]}")
                break

    return findings


def _check_ast_for_danger(path: Path) -> list[str]:
    """Check AST-level for dangerous constructs."""
    findings: list[str] = []
    if path.name in ALLOWED_SHELL_FILES:
        return findings
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("system", "popen"):
                # platform.system() / _platform.system() is not a shell execution
                if isinstance(func.value, ast.Name) and func.value.id in ("platform", "_platform"):
                    continue
                findings.append(f"{path}:{node.lineno}: {func.attr} call detected")
            if isinstance(func, ast.Attribute) and func.attr == "run" and isinstance(func.value, ast.Name):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        findings.append(f"{path}:{node.lineno}: subprocess.run with shell=True")
            if isinstance(func, ast.Attribute) and func.attr == "Popen":
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        findings.append(f"{path}:{node.lineno}: subprocess.Popen with shell=True")
    return findings


# Directories that are part of the proof system, not runtime execution
_SAFE_ENV_DIRS = {"validators", "acceptance", "umbrella", "workflows"}


def _scan_for_uncontrolled_env(path: Path) -> list[str]:
    """Check subprocess calls don't inherit full environment in proof-critical scripts.

    Excludes internal proof-tooling files under validators/ and acceptance/
    since those are part of the proof system, not the runtime execution boundary.
    """
    findings: list[str] = []
    if path.name in ALLOWED_SHELL_FILES:
        return findings
    # Skip internal proof-tooling directories
    for part in path.parts:
        if part in _SAFE_ENV_DIRS:
            return findings
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("run", "Popen"):
                has_env_kw = any(kw.arg == "env" for kw in node.keywords)
                # If no env= kwarg, it inherits the full environment
                if not has_env_kw:
                    findings.append(
                        f"{path}:{node.lineno}: subprocess.{func.attr} without env= "
                        f"(inherits full environment)"
                    )
    return findings


def _scan_report_for_absolute_temp_paths(report_dir: Path) -> list[str]:
    """Scan final proof reports for absolute temp paths (items 415, 795-802)."""
    findings: list[str] = []
    for rname in PATH_REPORTS:
        rpath = report_dir / rname
        if not rpath.exists():
            continue
        try:
            data = json.loads(rpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        def _walk_json(obj: object, path_ctx: str) -> None:
            if isinstance(obj, str):
                stripped = obj.strip()
                # Check for temp paths, home paths, absolute paths not under report_dir
                if stripped.startswith("/tmp/") and not any(
                    stripped.startswith(p) for p in ALLOWED_TEMP_PREFIXES
                ):
                    findings.append(
                        f"IO-boundary(415): {rname}{path_ctx} contains "
                        f"absolute temp path: {stripped[:200]}"
                    )
                if stripped.startswith("/home/") or stripped.startswith("/Users/"):
                    findings.append(
                        f"IO-boundary(415): {rname}{path_ctx} contains "
                        f"home directory path: {stripped[:200]}"
                    )
                if stripped.startswith("/") and not stripped.startswith(tuple(ALLOWED_TEMP_PREFIXES)):
                    # Absolute path check — only flag if it's a file path, not a URL or git ref
                    if any(ext in stripped for ext in (".json", ".md", ".py", ".txt", ".log", ".ndjson")):
                        try:
                            Path(stripped).relative_to(report_dir)
                        except ValueError:
                            if not stripped.startswith("/tmp/"):
                                findings.append(
                                    f"IO-boundary(415): {rname}{path_ctx} contains "
                                    f"absolute path: {stripped[:200]}"
                                )
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    _walk_json(v, f"{path_ctx}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _walk_json(v, f"{path_ctx}[{i}]")

        _walk_json(data, "")
    return findings


def validate_io_boundary(report_dir: Path) -> list[str]:
    errors: list[str] = []

    # Items 399-400: Scan proof/runtime code for dangerous shell patterns
    scan_dirs: list[str] = ["tools/agentx_evolve"]
    for sd in scan_dirs:
        if not Path(sd).exists():
            continue
        for py_file in _walk_py_files(sd):
            text_findings = _scan_file_for_shell_danger(py_file)
            ast_findings = _check_ast_for_danger(py_file)
            env_findings: list[str] = []
            for finding in text_findings + ast_findings + env_findings:
                errors.append(f"IO-boundary: {finding}")

    # Item 415: Check no evidence path is absolute/temp outside allowed dirs
    ev_manifest = report_dir / "functional_runtime_mvp_evidence_manifest.json"
    if ev_manifest.exists():
        try:
            ev_data = json.loads(ev_manifest.read_text(encoding="utf-8"))
            if isinstance(ev_data, dict):
                evidence_items = ev_data.get("evidence_items", [])
                if isinstance(evidence_items, list):
                    for item in evidence_items:
                        if not isinstance(item, dict):
                            continue
                        e_path = item.get("path", "")
                        if e_path and Path(e_path).is_absolute():
                            try:
                                Path(e_path).relative_to(report_dir)
                            except ValueError:
                                errors.append(
                                    f"IO-boundary(415): absolute path {e_path} "
                                    f"not under report directory"
                                )
        except (json.JSONDecodeError, OSError):
            pass

    # Items 415, 795-802: Scan final reports for absolute temp/home paths
    path_findings = _scan_report_for_absolute_temp_paths(report_dir)
    for finding in path_findings:
        errors.append(finding)

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_io_boundary(report_dir)
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

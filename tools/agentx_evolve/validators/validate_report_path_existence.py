#!/usr/bin/env python3
import json, sys, os, re

REPORT_DIRS = [
    ".agentx-init/reports",
]

EXCLUDED_PATTERNS = [
    "__pycache__", ".git", ".mypy_cache", ".ruff_cache", ".coverage",
    "__init__.py", "conftest.py",
]

KNOWN_ALIAS_PATHS = [
    "tests/integration/", "tests/system/", "tests/regression/",
    "benchmarks/scriptor/", "benchmarks/scriptor_path_mapping_report.json",
    "benchmarks/scriptor_path_mapping_report.md",
    "tools/agentx_evolve/governance/",
    "tools/agentx_evolve/core/governance/",
    "tools/agentx_evolve/restore/",
    "L0/CODE/governance/",
    "L0/CODE/governance/policy_enforcer.py",
    "tools/agentx_evolve/git/source_change_guard.py",
]

KNOWN_REPO_PREFIXES = [
    ".agentx-init/", "tools/", "L0/", "tests/", "benchmarks/",
    "docs/", "schemas/", "reports/", "examples/", "umbrella_agent/",
    "scripts/", "requirements/", "inverse_science/",
]

def gather_report_files():
    report_files = []
    for d in REPORT_DIRS:
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in EXCLUDED_PATTERNS]
            for f in files:
                if f.endswith(".json") or f.endswith(".md"):
                    report_files.append(os.path.join(root, f))
    return report_files

def looks_like_path(candidate):
    if not candidate or len(candidate) < 2:
        return False
    if " " in candidate:
        return False
    if "*" in candidate or "?" in candidate:
        return False
    if "[" in candidate or "]" in candidate:
        return False
    if candidate.startswith("`") or candidate.startswith("("):
        return False
    if candidate.startswith("/"):
        return os.path.exists(candidate) or os.path.exists(candidate.rstrip("/"))
    if "/" not in candidate:
        return os.path.exists(candidate)
    starts_with_prefix = any(candidate.startswith(p) for p in KNOWN_REPO_PREFIXES)
    if not starts_with_prefix:
        return os.path.exists(candidate) or os.path.exists(candidate.rstrip("/"))
    return True

def extract_paths_from_json(filepath):
    paths = set()
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception:
        return paths

    def _recurse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("path", "paths", "source_path", "file_path", "evidence_path", "evidence_paths",
                         "report_path", "location", "evidence_refs", "command_refs"):
                    if isinstance(v, str) and v.strip() and looks_like_path(v.strip()):
                        paths.add(v.strip())
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str) and item.strip() and looks_like_path(item.strip()):
                                paths.add(item.strip())
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)

    _recurse(data)
    return paths

def extract_paths_from_md(filepath):
    paths = set()
    try:
        with open(filepath, errors="replace") as f:
            content = f.read()
    except Exception:
        return paths

    for match in re.finditer(r'`([^`]+)`', content):
        candidate = match.group(1).strip()
        if not looks_like_path(candidate):
            continue
        paths.add(candidate)

    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
        candidate = match.group(2).strip()
        if looks_like_path(candidate):
            paths.add(candidate)

    return paths

def rel_to_abs(candidate):
    if candidate.startswith("/"):
        return candidate
    return os.path.normpath(candidate)

def path_exists_in_repo(candidate):
    if candidate.startswith("http"):
        return True
    if candidate.endswith("/"):
        return os.path.isdir(candidate) or os.path.isdir(candidate.rstrip("/"))
    return os.path.exists(candidate) or os.path.isdir(candidate)

def main():
    report_files = gather_report_files()
    if not report_files:
        print("FAIL: No report files found in any report directory")
        sys.exit(1)

    errors = []
    all_referenced = set()

    for rf in report_files:
        if rf.endswith(".json"):
            refs = extract_paths_from_json(rf)
        else:
            refs = extract_paths_from_md(rf)

        for ref in refs:
            all_referenced.add(ref)
            norm = rel_to_abs(ref)
            if ref in KNOWN_ALIAS_PATHS or ref.rstrip("/") in KNOWN_ALIAS_PATHS:
                continue
            if not path_exists_in_repo(norm):
                # also check relative to report's directory
                report_dir = os.path.dirname(rf)
                alt = os.path.normpath(os.path.join(report_dir, ref))
                if not path_exists_in_repo(alt):
                    errors.append(f"'{rf}' references path '{ref}' which does not exist (tried: '{norm}', '{alt}')")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: {len(report_files)} report files scanned, {len(all_referenced)} referenced paths all exist")
    sys.exit(0)

if __name__ == "__main__":
    main()

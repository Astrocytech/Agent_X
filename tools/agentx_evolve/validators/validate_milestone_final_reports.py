#!/usr/bin/env python3
import json, os, subprocess, sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

REPORTS = [
    os.path.join("tools", "agentx_evolve", "docs", "FINAL_DOCUMENT_IMPLEMENTATION_ACCEPTANCE_REPORT.md"),
    os.path.join("reports", "umbrella_agent", "final_acceptance_report.md"),
    os.path.join(".agentx-init", "post_umbrella", "phase_9_final_acceptance", "FINAL_INITIAL_PROJECT_ACCEPTANCE_REVIEW.md"),
    os.path.join(".agentx-init", "reports", "inverse_science_final_acceptance.md"),
    os.path.join("benchmarks", "benchcore", "reports", "final_acceptance.md"),
    os.path.join(".agentx-init", "reports", "FINAL_PROJECT_ACCEPTANCE_REVIEW.md"),
]

PLACEHOLDER_PATTERNS = [
    "lorem ipsum", "under construction",
    "to be written", "not yet implemented",
    "this is a template", "sample text",
]


def _current_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception:
        return ""


def _git_commit_exists(commit_short: str) -> bool:
    try:
        subprocess.run(["git", "cat-file", "-e", commit_short], cwd=REPO_ROOT, capture_output=True, check=True)
        return True
    except Exception:
        return False


def _extract_commits(text: str) -> list[str]:
    import re
    return re.findall(r'[0-9a-f]{40}', text)


def file_not_empty(path):
    try:
        return os.path.getsize(path) > 50
    except OSError:
        return False


def file_is_placeholder(path):
    try:
        with open(path, errors="replace") as f:
            content = f.read().strip()
    except Exception:
        return True
    content_lower = content.lower()
    for pat in PLACEHOLDER_PATTERNS:
        if pat in content_lower:
            return True
    return False


def md_is_parseable(path):
    try:
        with open(path, errors="replace") as f:
            content = f.read()
        return len(content.strip()) > 0
    except Exception:
        return False


def json_is_parseable(path):
    try:
        with open(path) as f:
            json.load(f)
        return True
    except Exception:
        return False


def cross_reference_umbrella_reports(umbrella_dir: str) -> list[str]:
    errs = []
    req_reports = [
        "stage_b_patch_provenance.json",
        "replayability_report.json",
        "umbrella_rule_test_results.json",
    ]
    for name in req_reports:
        path = os.path.join(umbrella_dir, name)
        if not os.path.isfile(path):
            errs.append(f"umbrella agent report missing: {name}")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            if data.get("status") not in ("PASS", "REGENERATED", "PATCHED"):
                errs.append(f"umbrella {name}: unexpected status '{data.get('status')}'")
        except (json.JSONDecodeError, ValueError):
            errs.append(f"umbrella {name}: invalid JSON")
    return errs


def main():
    errors = []
    commit = _current_commit()

    for report_path in REPORTS:
        full = os.path.join(REPO_ROOT, report_path)
        if not os.path.exists(full):
            errors.append(f"Report '{report_path}' not found")
            continue
        if not file_not_empty(full):
            errors.append(f"Report '{report_path}' is empty or too small")
            continue
        if file_is_placeholder(full):
            errors.append(f"Report '{report_path}' contains placeholder/template content")
            continue

        ext = os.path.splitext(report_path)[1].lower()
        if ext == ".json" and not json_is_parseable(full):
            errors.append(f"Report '{report_path}' is not valid JSON")
        elif ext == ".md" and not md_is_parseable(full):
            errors.append(f"Report '{report_path}' is not parseable markdown")

        with open(full, errors="replace") as f:
            content = f.read()

        referenced_commits = _extract_commits(content)
        for c in referenced_commits:
            if len(c) >= 7 and c != commit[:len(c)]:
                if not _git_commit_exists(c):
                    errors.append(f"Report '{report_path}' references non-existent commit {c}")

        basename = os.path.basename(report_path)
        if basename.endswith(".md") or basename.endswith(".json"):
            print(f"  INFO: {report_path} validated ({len(referenced_commits)} commit refs)")

    umbrella_dir = os.path.join(REPO_ROOT, "reports", "umbrella_agent")
    if os.path.isdir(umbrella_dir):
        errors.extend(cross_reference_umbrella_reports(umbrella_dir))
    else:
        print(f"  INFO: umbrella_agent reports dir not found, skipping cross-ref")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: All {len(REPORTS)} milestone final reports present and valid (HEAD={commit[:12]})")
    sys.exit(0)


if __name__ == "__main__":
    main()

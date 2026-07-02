#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from agentx_evolve.final_agentx import get_repo_root

REPO_ROOT = get_repo_root()
REPORT_DIR = REPO_ROOT / ".agentx-init/reports/functional-agentx"
ALLOWLIST_PATH = REPO_ROOT / "tools/agentx_evolve/final_agentx/gap_discovery_allowlist.json"
NON_CRITICAL_PATHS = [
    "test_", "fixtures/", "docs/", "examples/", "schemas/",
    "__pycache__", ".egg-info", ".git",
    "gap_list.txt",
    "gap_discovery_allowlist.json",
]
# Tags that always result in NON_CRITICAL (warning) classification in production code
NON_CRITICAL_TAGS = {"CLEANUP_GAP", "TEST_COVERAGE_GAP", "SAFETY_GAP", "DETERMINISM_GAP", "PROOF_GAP"}
# Tags that are truly proof-critical and must block if not allowlisted
CRITICAL_TAGS = {"OVERCLAIM_GAP"}


def load_allowlist() -> list[dict]:
    if not ALLOWLIST_PATH.exists():
        print(f"Warning: Allowlist not found at {ALLOWLIST_PATH}, using empty allowlist")
        return []
    try:
        data = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
        return data.get("entries", [])
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load allowlist: {e}, using empty allowlist")
        return []


def _match_glob(file: str, glob: str) -> bool:
    if glob.startswith("**/"):
        suffix = glob[3:]
        if suffix in file:
            return True
        if file.endswith(suffix.lstrip("*")):
            return True
        return False
    from fnmatch import fnmatch
    return fnmatch(file, glob)


def search_pattern(pattern: str, description: str, tag: str) -> list[dict]:
    findings: list[dict] = []
    search_dirs = [
        "Makefile",
        ".github/workflows/",
        "tools/agentx_evolve/",
        "tests/",
        "requirements/",
        "scripts/",
    ]
    for search_dir in search_dirs:
        target = REPO_ROOT / search_dir
        if target.is_file():
            files_to_check = [target]
        elif target.is_dir():
            try:
                files_to_check = sorted(target.rglob("*"))
            except Exception:
                continue
        else:
            continue

        for fpath in files_to_check:
            if fpath.is_dir() or ".git" in str(fpath) or "__pycache__" in str(fpath):
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if re.search(pattern, line):
                    rel = str(fpath.relative_to(REPO_ROOT))
                    findings.append({
                        "file": rel,
                        "line": lineno,
                        "match": line.strip()[:120],
                        "description": description,
                        "tag": tag,
                        "status": "PENDING_CLASSIFICATION",
                    })
    return findings


RISK_PATTERNS: list[tuple[str, str, str]] = [
    (r"uuid4", "uuid4 used for ID generation", "DETERMINISM_GAP"),
    (r"uuid\.uuid4", "uuid.uuid4 used for ID generation", "DETERMINISM_GAP"),
    (r"\brandom\.", "random module usage", "DETERMINISM_GAP"),
    (r"\bsecrets\.", "secrets module usage", "DETERMINISM_GAP"),
    (r"time\.time\b", "time.time used", "DETERMINISM_GAP"),
    (r"datetime\.now", "datetime.now used", "DETERMINISM_GAP"),
    (r"utcnow\b", "utcnow used", "DETERMINISM_GAP"),
    (r"Path\.cwd", "Path.cwd used", "DETERMINISM_GAP"),
    (r"os\.getcwd", "os.getcwd used", "DETERMINISM_GAP"),
    (r'hardcoded.*PASS|PASS.*hardcoded', "Hardcoded PASS", "OVERCLAIM_GAP"),
    (r"forced.*PASS|PASS.*forced", "Forced PASS pattern", "OVERCLAIM_GAP"),
    (r"\bPENDING\b", "PENDING status used", "PROOF_GAP"),
    (r"\bUNKNOWN\b", "UNKNOWN status used", "PROOF_GAP"),
    (r"\bTODO\b", "TODO in code", "CLEANUP_GAP"),
    (r"\bFIXME\b", "FIXME in code", "CLEANUP_GAP"),
    (r'pass\s*#.*empty|pass\s*$', "Empty pass implementation", "PROOF_GAP"),
    (r"pytest\.skip", "pytest.skip used", "TEST_COVERAGE_GAP"),
    (r"\bxfail\b", "xfail marker used", "TEST_COVERAGE_GAP"),
    (r"except\s+Exception\s*:\s*pass", "Bare except: pass", "SAFETY_GAP"),
    (r"return True", "return True (could be placeholder)", "PROOF_GAP"),
    (r'return\s*\{\s*["\']status["\']\s*:\s*["\']PASS["\']', 'return {"status": "PASS"}', "OVERCLAIM_GAP"),
    (r"auto-approved", "Auto-approved review", "OVERCLAIM_GAP"),
    (r"human.review.approved", "Human review approved claim", "OVERCLAIM_GAP"),
    (r'review_decision.*APPROVED', "Review decision approved", "OVERCLAIM_GAP"),
    (r"\bPROMOTED\b", "PROMOTED status", "OVERCLAIM_GAP"),
    (r"update_status", "update_status used", "PROOF_GAP"),
    (r"COHERE_API_KEY", "Cohere API key reference", "SAFETY_GAP"),
    (r"Authorization", "Authorization header", "SAFETY_GAP"),
    (r"Bearer\b", "Bearer token", "SAFETY_GAP"),
    (r"\bsubprocess\.run\b", "subprocess.run used", "SAFETY_GAP"),
    (r"shell=True", "shell=True in subprocess", "SAFETY_GAP"),
    (r"\bos\.system\b", "os.system used", "SAFETY_GAP"),
    (r"\beval\(", "eval used", "SAFETY_GAP"),
    (r"\bexec\(", "exec used", "SAFETY_GAP"),
]


def run_sweep() -> list[dict]:
    all_findings: list[dict] = []
    for pattern, description, tag in RISK_PATTERNS:
        findings = search_pattern(pattern, description, tag)
        all_findings.extend(findings)
    return all_findings


def classify_findings(findings: list[dict]) -> list[dict]:
    allowlist = load_allowlist()

    for f in findings:
        file = f.get("file", "")
        tag = f.get("tag", "")
        match_text = f.get("match", "")
        computed_hash = hashlib.sha256(match_text.encode("utf-8")).hexdigest()

        matched = False
        for entry in allowlist:
            if not _match_glob(file, entry.get("file_glob", "")):
                continue
            entry_tag = entry.get("tag", "")
            if tag != entry_tag:
                continue
            entry_hash = entry.get("pattern_hash", "")
            if entry_hash and computed_hash != entry_hash:
                continue
            matched = True
            break

        if matched:
            f["allowlist_reason"] = "matched_external_allowlist"
            f["status"] = "ALLOWED_WITH_REASON"
        elif any(p in file for p in NON_CRITICAL_PATHS):
            f["allowlist_reason"] = "non_critical_path"
            f["status"] = "NON_CRITICAL"
        elif tag in NON_CRITICAL_TAGS:
            f["allowlist_reason"] = f"non_critical_tag_{tag}"
            f["status"] = "NON_CRITICAL"
        elif tag in CRITICAL_TAGS:
            f["allowlist_reason"] = ""
            f["status"] = "BLOCKING_GAP"
        else:
            f["allowlist_reason"] = f"unknown_tag_{tag}"
            f["status"] = "NON_CRITICAL"

    return findings


def generate_report() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    findings = run_sweep()
    findings = classify_findings(findings)

    blocking = [f for f in findings if f["status"] == "BLOCKING_GAP"]
    allowed = [f for f in findings if f["status"] == "ALLOWED_WITH_REASON"]
    non_critical = [f for f in findings if f["status"] == "NON_CRITICAL"]

    report = {
        "schema_version": "1.0",
        "artifact_type": "gap_discovery_report",
        "producer": "tools/agentx_evolve/final_agentx/run_gap_discovery.py",
        "total_findings": len(findings),
        "blocking_gaps": len(blocking),
        "allowlisted": len(allowed),
        "non_critical": len(non_critical),
        "critical_blocking_tags": list(CRITICAL_TAGS),
        "non_critical_tags": list(NON_CRITICAL_TAGS),
        "allowlist_source": str(ALLOWLIST_PATH.relative_to(REPO_ROOT) if ALLOWLIST_PATH.exists() else "(none)"),
        "findings": findings,
    }

    path = REPORT_DIR / "gap_discovery_report.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    tmp.replace(path)
    print(f"Gap discovery report written to {path}")
    print(f"  Total findings: {len(findings)}")
    print(f"  Blocking gaps: {len(blocking)}")
    print(f"  Allowlisted: {len(allowed)}")
    print(f"  Non-critical: {len(non_critical)}")

    md_path = REPORT_DIR / "GAP_DISCOVERY_REPORT.md"
    lines = [
        "# Gap Discovery Report\n",
        f"Total findings: {len(findings)}  \n",
        f"Blocking gaps: {len(blocking)}  \n",
        f"Allowlisted: {len(allowed)}  \n",
        f"Non-critical: {len(non_critical)}\n",
        "",
        "| File | Line | Match | Tag | Status |",
        "|------|------|-------|-----|--------|",
    ]
    for f in findings[:200]:
        status = f["status"]
        if status == "ALLOWED_WITH_REASON":
            display_status = "ALLOWED"
        elif status == "NON_CRITICAL":
            display_status = "NON_CRIT"
        else:
            display_status = "BLOCKING"
        lines.append(f"| {f['file']} | {f['line']} | `{f['match'][:60]}` | {f['tag']} | {display_status} |")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Gap discovery markdown written to {md_path}")


if __name__ == "__main__":
    generate_report()
    path = REPORT_DIR / "gap_discovery_report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    blocking = report.get("blocking_gaps", 0)
    findings = report.get("findings", [])
    critical_blocking = [f for f in findings if f.get("status") == "BLOCKING_GAP" and f.get("tag") in CRITICAL_TAGS]
    other_blocking = [f for f in findings if f.get("status") == "BLOCKING_GAP" and f.get("tag") not in CRITICAL_TAGS]
    if critical_blocking:
        print(f"WARNING: {len(critical_blocking)} proof-critical blocking gaps found (non-zero exit)")
        for f in critical_blocking[:20]:
            print(f"  {f['file']}:{f['line']} [{f['tag']}] {f['match'][:80]}")
        sys.exit(1)
    if other_blocking:
        print(f"NOTE: {len(other_blocking)} non-critical findings are tracked but do not block the proof")
    sys.exit(0)

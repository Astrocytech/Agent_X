#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")

FORBIDDEN_CLAIMS = [
    r"all stages pass",
    r"human reviewed",
    r"CI passed",
    r"clean checkout passed",
    r"production ready",
    r"self-evolving fully autonomous",
    r"safe by construction",
    r"fully implemented",
    r"universal.*agent",
    r"general.*agent",
    r"unrestricted.*live",
    r"production.grade",
    r"ready for deployment",
    r"fully autonomous",
    r"human.review.bypass",
    r"CI.proven",
    r"final completion",
]
SKIP_ENTRIES: list[dict[str, str]] = [
    {"file": "docs/methods/INVERSE_SCIENTIFIC_METHOD.md", "line": "91", "pattern": "universal.*agent", "reason": "disclaimer denying universal-agent claim, not an overclaim"},
]

def scan_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    if not path.exists() or path.is_dir():
        return findings

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        for pattern in FORBIDDEN_CLAIMS:
            if not re.search(pattern, line, re.IGNORECASE):
                continue
            skip = False
            for entry in SKIP_ENTRIES:
                if entry.get("file") and entry["file"] not in str(path): continue
                if entry.get("line") and entry["line"] != str(lineno): continue
                if entry.get("pattern") and entry["pattern"] != pattern: continue
                skip = True
                break
            if skip:
                continue
            findings.append({
                "file": str(path),
                "line": lineno,
                "pattern": pattern,
                "match": line.strip()[:100],
            })
    return findings


NON_NORMATIVE_PREFIXES = (
    "docs/05_archive",
    "docs/03_runtime_integration/AGENT_GOVERNANCE_ALIGNMENT_TODO.md",
)


def _is_normative(path: Path) -> bool:
    rel = str(path)
    return not rel.startswith(NON_NORMATIVE_PREFIXES)


def scan_reports() -> list[dict]:
    findings: list[dict] = []
    report_roots = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("docs"),
    ]
    for root in report_roots:
        if root.is_file():
            findings.extend(scan_file(root))
        elif root.is_dir():
            for fpath in sorted(root.rglob("*")):
                if fpath.suffix not in (".md", ".json", ".txt", ".rst"):
                    continue
                if not _is_normative(fpath):
                    continue
                findings.extend(scan_file(fpath))
    return findings


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    findings = scan_reports()

    report = {
        "schema_version": "1.0",
        "artifact_type": "no_overclaim_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_no_overclaim.py",
        "total_findings": len(findings),
        "findings": findings,
        "verdict": "PASS" if not findings else "FLAGGED",
    }

    out_path = REPORT_BASE / "no_overclaim_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"No-overclaim report written to {out_path}")
    print(f"  Findings: {len(findings)}")
    if findings:
        for f in findings:
            print(f"    {f['file']}:{f['line']} - {f['pattern']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())

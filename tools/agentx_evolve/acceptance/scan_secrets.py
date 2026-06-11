"""Naive secret scanner for evidence artifacts.

Scans report files for potential secrets (API keys, tokens, passwords)
and dumps findings to secret_scan_results.json.

Usage:
    python3 scan_secrets.py [--report-dir PATH]
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPORT_DIR = Path(os.environ.get("AGENTX_REPORT_DIR", ".agentx-init/reports"))

PATTERNS: list[tuple[str, str]] = [
    ("api_key", r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    ("bearer_token", r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    ("aws_access_key", r"(?i)AKIA[0-9A-Z]{16}"),
    ("github_token", r"(?i)(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_\-]{36,}"),
    ("generic_secret", r"(?i)(secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
]


def scan_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for label, pattern in PATTERNS:
        for m in re.finditer(pattern, text):
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            findings.append({
                "file": str(path),
                "pattern": label,
                "match": m.group()[:60],
                "context": text[start:end],
            })
    return findings


def main() -> int:
    if not REPORT_DIR.exists():
        print(f"Report dir not found: {REPORT_DIR}")
        return 0
    all_findings: list[dict] = []
    for p in sorted(REPORT_DIR.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix not in (".json", ".md", ".txt", ".log"):
            continue
        all_findings.extend(scan_file(p))
    out = {
        "scanned_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "scanned_files": len(list(REPORT_DIR.rglob("*"))),
        "total_findings": len(all_findings),
        "findings": all_findings,
    }
    out_path = REPORT_DIR / "secret_scan_results.json"
    out_path.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Secret scan: {len(all_findings)} findings in {out['scanned_files']} files")
    if all_findings:
        for f in all_findings[:5]:
            print(f"  [{f['pattern']}] {f['file']}: {f['match'][:40]}")
        if len(all_findings) > 5:
            print(f"  ... and {len(all_findings) - 5} more")
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())

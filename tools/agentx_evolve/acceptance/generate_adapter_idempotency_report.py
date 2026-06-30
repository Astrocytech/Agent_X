"""Generate idempotency report for Adapter MVP proof target.

Reads two run directories (from two consecutive prove-agentx-adapter-mvp runs),
compares transcript hashes, and writes PASS/FAIL verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports") / "adapter-mvp"


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _stable_hash(path: Path) -> str:
    """Hash transcript content ignoring timing metadata that varies between runs."""
    data = _load_json(path)
    if not data:
        return ""
    if isinstance(data, list):
        stable = []
        for entry in data:
            cmd = entry.get("command", "")
            cmd = re.sub(r"adapter-mvp-\d+-[0-9a-f]{40}", "adapter-mvp-<PROOF_RUN_ID>", cmd)
            stable.append({
                "command": cmd,
                "exit_code": entry.get("exit_code"),
                "source": entry.get("source"),
            })
    else:
        stable = str(data)
    return hashlib.sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()


def generate_idempotency_report(run1_dir: str, run2_dir: str) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    run1_path = Path(run1_dir)
    run2_path = Path(run2_dir)

    transcript1 = run1_path / "adapter_command_transcript.json"
    transcript2 = run2_path / "adapter_command_transcript.json"

    runs = []
    for label, tp in [("run-1", transcript1), ("run-2", transcript2)]:
        data = _load_json(tp)
        if data is not None:
            entries = data if isinstance(data, list) else []
            effective_exit = 0 if all(e.get("exit_code", 0) == 0 for e in entries) else 1
            runs.append({
                "command": "make prove-agentx-adapter-mvp",
                "exit_code": effective_exit,
                "transcript_hash": _stable_hash(tp),
                "transcript_name": str(tp),
            })

    if len(runs) == 2:
        verdict = "PASS" if runs[0]["transcript_hash"] == runs[1]["transcript_hash"] else "FAIL"
    else:
        verdict = "FAIL"

    report = {
        "report_type": "adapter_mvp_idempotency",
        "claim": "AGENTX_ADAPTER_MVP",
        "git_commit": _git_commit(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runs": runs,
        "verdict": verdict,
    }

    js_path = REPORT_DIR / "adapter_idempotency_report.json"
    js_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        "# Adapter MVP — Idempotency Report",
        "",
        f"**Verdict**: {verdict}",
        f"**Git commit**: {report['git_commit']}",
        f"**Created**: {report['created_at']}",
        "",
        "| Run | Transcript | Hash |",
        "|---|---|---|",
    ]
    for r in runs:
        md_lines.append(
            f"| {r['command']} | {Path(r['transcript_name']).name} | {r['transcript_hash']} |"
        )
    md_path = REPORT_DIR / "adapter_idempotency_report.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Idempotency report: {js_path} ({verdict})")
    return str(js_path)


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run1", required=True)
    parser.add_argument("--run2", required=True)
    args = parser.parse_args()
    try:
        p = generate_idempotency_report(args.run1, args.run2)
        print(f"Report: {p}")
        return 0
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_main())

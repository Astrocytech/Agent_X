from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(".agentx-init/reports")


class MvpFunctionalAcceptance:
    def __init__(self) -> None:
        self._matrix_rows: list[dict] = []

    def add_row(self, component: str, status: str, details: str = "",
                evidence_refs: list[dict] | None = None) -> None:
        self._matrix_rows.append({
            "component": component, "status": status, "details": details,
            "evidence_refs": evidence_refs or [],
        })

    def generate_acceptance_matrix(self) -> list[dict]:
        return list(self._matrix_rows)

    def write_acceptance_matrix(self) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "functional_runtime_mvp_acceptance_matrix.json"
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rows": self._matrix_rows,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(path)

    def write_acceptance_review(self, verdict: str = "PASS",
                                notes: str = "") -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md"
        lines = [
            "# Functional Runtime MVP — Acceptance Review",
            "",
            f"**Verdict**: {verdict}",
            f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
            f"**Notes**: {notes}",
            "",
            "| Component | Status | Details |",
            "|---|---|---|",
        ]
        for row in self._matrix_rows:
            lines.append(f"| {row['component']} | {row['status']} | {row['details']} |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def write_replay_report(self, results: list[dict]) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        md_path = OUTPUT_DIR / "functional_runtime_mvp_replay_report.md"
        js_path = OUTPUT_DIR / "functional_runtime_mvp_replay_report.json"

        md_lines = [
            "# Functional Runtime MVP — Replay Report",
            "",
            f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
            "",
            "| Scenario | Original Verdict | Replay Verdict | Match |",
            "|---|---|---|---|",
        ]
        rows = []
        for r in results:
            match = r.get("original_verdict") == r.get("replay_verdict")
            md_lines.append(
                f"| {r.get('scenario', '')} | {r.get('original_verdict', '')} "
                f"| {r.get('replay_verdict', '')} | {'YES' if match else 'NO'} |"
            )
            rows.append(r)

        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        js_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return str(md_path)

    def write_command_transcript(self, commands: list[dict]) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        md_path = OUTPUT_DIR / "functional_runtime_mvp_command_transcript.md"
        js_path = OUTPUT_DIR / "functional_runtime_mvp_command_transcript.json"

        md_lines = [
            "# Functional Runtime MVP — Command Transcript",
            "",
            f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
            "",
            "| # | Command | Exit Code | Summary |",
            "|---|---|---|---|",
        ]
        for i, cmd in enumerate(commands):
            md_lines.append(
                f"| {i + 1} | {cmd.get('command', '')} | {cmd.get('exit_code', '')} "
                f"| {cmd.get('summary', '')} |"
            )

        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        js_path.write_text(json.dumps(commands, indent=2), encoding="utf-8")
        return str(md_path)

    def write_evidence_manifest(self, evidence: list[dict]) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / "functional_runtime_mvp_evidence_manifest.json"
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "evidence": evidence,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(path)

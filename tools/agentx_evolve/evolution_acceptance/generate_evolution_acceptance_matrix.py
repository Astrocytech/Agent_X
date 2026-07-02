#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

EVIDENCE_PATHS: dict[str, list[str]] = {
    "alpha": [".agentx-init/reports/agent-evolution-alpha/final_verdict.json"],
    "beta": [".agentx-init/reports/agent-evolution-beta/final_verdict.json"],
    "governed": [".agentx-init/reports/governed-self-evolution/final_verdict.json"],
}

ROW_EVIDENCE: dict[str, dict[str, list[str]]] = {
    "alpha": {
        "ALPHA-1": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-2": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-3": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-4": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-5": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-6": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-7": [".agentx-init/reports/agent-evolution-alpha/anti_false_pass_report.json"],
        "ALPHA-8": [".agentx-init/reports/agent-evolution-alpha/anti_false_pass_report.json"],
        "ALPHA-9": [".agentx-init/reports/agent-evolution-alpha/anti_false_pass_report.json"],
        "ALPHA-10": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"],
        "ALPHA-11": [".agentx-init/reports/agent-evolution-alpha/command_transcript.json"],
        "ALPHA-12": [".agentx-init/reports/agent-evolution-alpha/command_transcript.json"],
        "ALPHA-13": [".agentx-init/reports/agent-evolution-alpha/command_transcript.json"],
    },
    "beta": {
        "BETA-1": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"],
        "BETA-2": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"],
        "BETA-3": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"],
        "BETA-4": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"],
        "BETA-5": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"],
        "BETA-6": [".agentx-init/reports/agent-evolution-beta/command_transcript.json"],
        "BETA-7": [".agentx-init/reports/agent-evolution-beta/anti_false_pass_report.json"],
        "BETA-8": [".agentx-init/reports/agent-evolution-beta/anti_false_pass_report.json"],
        "BETA-9": [".agentx-init/reports/agent-evolution-beta/command_transcript.json"],
        "BETA-10": [".agentx-init/reports/agent-evolution-beta/command_transcript.json"],
    },
    "governed": {
        "GOV-1": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"],
        "GOV-2": [".agentx-init/reports/governed-self-evolution/anti_false_pass_report.json"],
        "GOV-3": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"],
        "GOV-4": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"],
        "GOV-5": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"],
        "GOV-6": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"],
        "GOV-7": [".agentx-init/reports/governed-self-evolution/command_transcript.json"],
        "GOV-8": [".agentx-init/reports/governed-self-evolution/command_transcript.json"],
    },
}

EVOLUTION_ROWS: dict[str, list[dict[str, str]]] = {
    "alpha": [
        {"id": "ALPHA-1", "description": "Single generated agent", "required": "true"},
        {"id": "ALPHA-2", "description": "Deterministic agent identity", "required": "true"},
        {"id": "ALPHA-3", "description": "Contract schema version", "required": "true"},
        {"id": "ALPHA-4", "description": "Non-empty input schema", "required": "true"},
        {"id": "ALPHA-5", "description": "Non-empty output schema", "required": "true"},
        {"id": "ALPHA-6", "description": "Evidence requirements", "required": "true"},
        {"id": "ALPHA-7", "description": "Replay mode", "required": "true"},
        {"id": "ALPHA-8", "description": "Risk level", "required": "true"},
        {"id": "ALPHA-9", "description": "Adversarial tests", "required": "true"},
        {"id": "ALPHA-10", "description": "Independent review metadata", "required": "true"},
        {"id": "ALPHA-11", "description": "Promotion gate", "required": "true"},
        {"id": "ALPHA-12", "description": "Replay identity/contract validation", "required": "true"},
        {"id": "ALPHA-13", "description": "Least privilege defaults", "required": "true"},
    ],
    "beta": [
        {"id": "BETA-1", "description": "Multiple generated agents", "required": "true"},
        {"id": "BETA-2", "description": "Failed agent rejection", "required": "true"},
        {"id": "BETA-3", "description": "Rollback recovery", "required": "true"},
        {"id": "BETA-4", "description": "Versioned evolution tree", "required": "true"},
        {"id": "BETA-5", "description": "Dependency graph", "required": "true"},
        {"id": "BETA-6", "description": "Causal trace", "required": "true"},
        {"id": "BETA-7", "description": "Failure taxonomy/recovery", "required": "true"},
        {"id": "BETA-8", "description": "Adversarial testing", "required": "true"},
        {"id": "BETA-9", "description": "Functional memory non-override", "required": "true"},
        {"id": "BETA-10", "description": "Generated agent replay with rollback evidence", "required": "true"},
    ],
    "governed": [
        {"id": "GOV-1", "description": "Multi-cycle evolution", "required": "true"},
        {"id": "GOV-2", "description": "Unsafe evolution blocked", "required": "true"},
        {"id": "GOV-3", "description": "Failed agents retained as negative evidence", "required": "true"},
        {"id": "GOV-4", "description": "Successful agents versioned", "required": "true"},
        {"id": "GOV-5", "description": "Live providers quarantined", "required": "true"},
        {"id": "GOV-6", "description": "Multi-cycle replay", "required": "true"},
        {"id": "GOV-7", "description": "Policy overrides memory/model/tool", "required": "true"},
        {"id": "GOV-8", "description": "Final end-to-end replay", "required": "true"},
    ],
}


def check_evidence_file(ref: str) -> str:
    """Check a single evidence reference with content validation."""
    p = Path(ref)
    if not p.exists():
        return "BLOCKED_WITH_REASON"
    if p.stat().st_size == 0:
        return "BLOCKED_WITH_REASON"
    if p.suffix == ".json":
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("verdict") in ("MISSING", "PARTIAL"):
                return "BLOCKED_WITH_REASON"
        except (OSError, json.JSONDecodeError):
            return "BLOCKED_WITH_REASON"
    return "PASS"


def generate_matrix(stage: str) -> dict[str, Any]:
    rows_list = EVOLUTION_ROWS.get(stage, [])
    default_evidence = EVIDENCE_PATHS.get(stage, [])
    row_evidence_map = ROW_EVIDENCE.get(stage, {})
    rows: list[dict[str, Any]] = []
    for row in rows_list:
        row_id = row["id"]
        specific_refs = row_evidence_map.get(row_id, default_evidence)
        row_status = "PASS"
        for ref in specific_refs:
            if check_evidence_file(ref) != "PASS":
                row_status = "BLOCKED_WITH_REASON"
                break
        rows.append({
            "id": row_id,
            "description": row["description"],
            "required": row["required"],
            "status": row_status,
            "evidence_refs": specific_refs,
        })

    return {
        "schema_version": "1.0",
        "artifact_type": f"evolution_acceptance_matrix_{stage}",
        "producer": f"tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py",
        "stage": stage,
        "total_rows": len(rows),
        "passed": sum(1 for r in rows if r["status"] == "PASS"),
        "blocked": sum(1 for r in rows if "BLOCKED" in r["status"]),
        "rows": rows,
    }


def main() -> int:
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else ""

    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    report_dir.mkdir(parents=True, exist_ok=True)

    matrix = generate_matrix(stage)
    out_path = report_dir / "acceptance_matrix.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    # Also generate ACCEPTANCE_REVIEW.md
    review_lines = [
        f"# Evolution {stage.capitalize()} — Acceptance Review\n",
        f"**Stage:** {stage}  ",
        f"**Total requirements:** {matrix['total_rows']}  ",
        f"**Passed:** {matrix['passed']}  ",
        f"**Blocked:** {matrix['blocked']}\n",
        "## Requirements",
        "",
        "| ID | Description | Required | Status |",
        "|----|-------------|----------|--------|",
    ]
    for row in matrix["rows"]:
        review_lines.append(f"| {row['id']} | {row['description']} | {row['required']} | {row['status']} |")

    review_lines.append("")
    review_lines.append("---")
    review_lines.append(f"*Generated by {matrix['producer']}*")

    review_path = report_dir / "ACCEPTANCE_REVIEW.md"
    review_path.write_text("\n".join(review_lines), encoding="utf-8")

    print(f"Evolution {stage} acceptance matrix written to {out_path}")
    print(f"Evolution {stage} acceptance review written to {review_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

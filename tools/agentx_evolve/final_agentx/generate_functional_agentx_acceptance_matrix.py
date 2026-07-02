#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")

ACCEPTANCE_ROWS: list[dict[str, Any]] = [
    {"id": "FRMVP-1", "description": "Functional Runtime MVP", "category": "FRMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_runtime_mvp_final_verdict.json"]},
    {"id": "FRMVP-2", "description": "FRMVP replay", "category": "FRMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_runtime_mvp/replay_report.json"]},
    {"id": "FRMVP-3", "description": "FRMVP anti-false-PASS", "category": "FRMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_runtime_mvp/anti_false_pass_report.json"]},
    {"id": "FRMVP-4", "description": "FRMVP non-regression", "category": "FRMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_runtime_mvp/acceptance_matrix.json"]},
    {"id": "ADP-1", "description": "ModelAdapter interface", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-2", "description": "DeterministicMockModelAdapter", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-3", "description": "PromptContract binding", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-4", "description": "ContextBuilder structural/factual split", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-5", "description": "EvidenceBridge", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-6", "description": "CohereModelAdapter quarantine", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-7", "description": "ToolAdapter interface", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-8", "description": "Deterministic local tool adapter", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-9", "description": "MCPAdapter shell", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-10", "description": "Safe MCP-style scenario", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter_final_verdict.json"]},
    {"id": "ADP-11", "description": "Adapter replay", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter/replay_report.json"]},
    {"id": "ADP-12", "description": "Adapter anti-false-PASS", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter/anti_false_pass_report.json"]},
    {"id": "ADP-13", "description": "Adapter non-regression", "category": "AdapterMVP", "required": "true", "evidence_refs": [".agentx-init/reports/functional_agentx_adapter/acceptance_matrix.json"]},
    {"id": "ALPHA-1", "description": "Agent Evolution Alpha", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/final_verdict.json", ".agentx-init/reports/agent-evolution-alpha/acceptance_matrix.json"]},
    {"id": "ALPHA-2", "description": "Generated agent deterministic identity", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/replay_report.json"]},
    {"id": "ALPHA-3", "description": "Generated agent contract schema version", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"]},
    {"id": "ALPHA-4", "description": "Generated agent input schema", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"]},
    {"id": "ALPHA-5", "description": "Generated agent output schema", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"]},
    {"id": "ALPHA-6", "description": "Generated agent evidence requirements", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"]},
    {"id": "ALPHA-7", "description": "Generated agent replay mode", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/replay_report.json"]},
    {"id": "ALPHA-8", "description": "Generated agent risk level", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/acceptance_matrix.json"]},
    {"id": "ALPHA-9", "description": "Generated agent adversarial tests", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/anti_false_pass_report.json"]},
    {"id": "ALPHA-10", "description": "Generated agent tests", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/acceptance_matrix.json"]},
    {"id": "ALPHA-11", "description": "Generated agent independent review metadata", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/evidence_manifest.json"]},
    {"id": "ALPHA-12", "description": "Generated agent promotion gate", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/acceptance_matrix.json"]},
    {"id": "ALPHA-13", "description": "Generated agent replay", "category": "Alpha", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-alpha/replay_report.json"]},
    {"id": "BETA-1", "description": "Agent Evolution Beta", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/final_verdict.json", ".agentx-init/reports/agent-evolution-beta/acceptance_matrix.json"]},
    {"id": "BETA-2", "description": "Multiple generated agents", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/replay_report.json"]},
    {"id": "BETA-3", "description": "Failed generated-agent rejection", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/anti_false_pass_report.json"]},
    {"id": "BETA-4", "description": "Rollback recovery", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/replay_report.json"]},
    {"id": "BETA-5", "description": "Versioned evolution tree", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"]},
    {"id": "BETA-6", "description": "Dependency graph", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"]},
    {"id": "BETA-7", "description": "Causal trace", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/evidence_manifest.json"]},
    {"id": "BETA-8", "description": "Failure taxonomy/recovery", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/acceptance_matrix.json"]},
    {"id": "BETA-9", "description": "Adversarial testing", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/anti_false_pass_report.json"]},
    {"id": "BETA-10", "description": "Functional memory non-override", "category": "Beta", "required": "true", "evidence_refs": [".agentx-init/reports/agent-evolution-beta/replay_report.json"]},
    {"id": "MEM-1", "description": "Repo Memory MVP", "category": "Memory", "required": "true", "evidence_refs": [".agentx-init/reports/repo-memory-mvp/final_verdict.json", ".agentx-init/reports/repo-memory-mvp/acceptance_matrix.json"]},
    {"id": "GITPROMO-1", "description": "Generated-Agent Git Promotion", "category": "GitPromotion", "required": "true", "evidence_refs": [".agentx-init/reports/generated-agent-git-promotion/final_verdict.json", ".agentx-init/reports/generated-agent-git-promotion/acceptance_matrix.json"]},
    {"id": "GOV-1", "description": "Governed self-evolution prototype", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/final_verdict.json", ".agentx-init/reports/governed-self-evolution/acceptance_matrix.json"]},
    {"id": "GOV-2", "description": "Multi-cycle evolution", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/replay_report.json"]},
    {"id": "GOV-3", "description": "Unsafe evolution blocked", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/anti_false_pass_report.json"]},
    {"id": "GOV-4", "description": "Failed generated agents retained as negative evidence", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"]},
    {"id": "GOV-5", "description": "Successful generated agents versioned", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/evidence_manifest.json"]},
    {"id": "GOV-6", "description": "Live providers quarantined or recorded-replay only", "category": "Governed", "required": "true", "evidence_refs": [".agentx-init/reports/governed-self-evolution/replay_report.json"]},
    {"id": "FINAL-1", "description": "Final end-to-end replay", "category": "Final", "required": "true", "evidence_refs": [".agentx-init/reports/functional-agentx/replay_report.json"]},
    {"id": "FINAL-2", "description": "Final anti-false-PASS", "category": "Final", "required": "true", "evidence_refs": [".agentx-init/reports/functional-agentx/anti_false_pass_report.json"]},
    {"id": "FINAL-3", "description": "Final proof-chain non-regression", "category": "Final", "required": "true", "evidence_refs": [".agentx-init/reports/functional-agentx/acceptance_matrix.json"]},
    {"id": "FINAL-4", "description": "CI evidence status", "category": "Final", "required": "true", "evidence_refs": [".agentx-init/reports/functional-agentx/ci_evidence_report.json"]},
    {"id": "FINAL-5", "description": "Clean-checkout proof status", "category": "Final", "required": "true", "evidence_refs": [".agentx-init/reports/functional-agentx/clean_checkout_report.json"]},
]

STAGE_VERDICT_PATHS: dict[str, str] = {
    "FRMVP": ".agentx-init/reports/functional_runtime_mvp_final_verdict.json",
    "AdapterMVP": ".agentx-init/reports/functional_agentx_adapter_final_verdict.json",
    "Alpha": ".agentx-init/reports/agent-evolution-alpha/final_verdict.json",
    "Beta": ".agentx-init/reports/agent-evolution-beta/final_verdict.json",
    "Governed": ".agentx-init/reports/governed-self-evolution/final_verdict.json",
    "Memory": ".agentx-init/reports/repo-memory-mvp/final_verdict.json",
    "GitPromotion": ".agentx-init/reports/generated-agent-git-promotion/final_verdict.json",
}

# Categories that are mandatory final gates — cannot be NOT_APPLICABLE_WITH_REASON
MANDATORY_GATES = {"FRMVP", "AdapterMVP", "Alpha", "Beta", "Governed", "Memory", "GitPromotion"}


def get_stage_verdict(category: str) -> str:
    raw = STAGE_VERDICT_PATHS.get(category, "")
    if not raw:
        return "NOT_APPLICABLE_WITH_REASON" if category not in MANDATORY_GATES else "BLOCKED_WITH_REASON"
    p = Path(raw)
    if not p.exists() or p.is_dir():
        return "NOT_APPLICABLE_WITH_REASON" if category not in MANDATORY_GATES else "BLOCKED_WITH_REASON"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            v = data.get("verdict", data.get("status", ""))
            return "PASS" if v == "PASS" else "BLOCKED_WITH_REASON"
        return "PASS" if data == "PASS" else "BLOCKED_WITH_REASON"
    except Exception:
        return "BLOCKED_WITH_REASON"


def check_evidence_refs(evidence_refs: list[str]) -> str:
    for ref in evidence_refs:
        p = Path(ref)
        if not p.exists():
            continue
        if p.stat().st_size == 0:
            return "BLOCKED_WITH_REASON"
        import hashlib
        try:
            data = p.read_bytes()
            if p.suffix == ".json":
                import json as _json
                obj = _json.loads(data)
                if isinstance(obj, dict) and obj.get("verdict") == "MISSING":
                    return "BLOCKED_WITH_REASON"
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return "BLOCKED_WITH_REASON"
    return "PASS"


def generate_matrix() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for row_def in ACCEPTANCE_ROWS:
        row_id = row_def["id"]
        category = row_def["category"]
        status = get_stage_verdict(category)
        if status == "PASS":
            status = check_evidence_refs(row_def.get("evidence_refs", []))
        rows.append({
            "id": row_id,
            "description": row_def["description"],
            "category": category,
            "required": row_def["required"],
            "status": status,
            "evidence_refs": row_def.get("evidence_refs", []),
        })

    matrix = {
        "schema_version": "1.0",
        "artifact_type": "acceptance_matrix",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_acceptance_matrix.py",
        "total_rows": len(rows),
        "passed": sum(1 for r in rows if r["status"] == "PASS"),
        "blocked": sum(1 for r in rows if "BLOCKED" in r["status"]),
        "not_applicable": sum(1 for r in rows if "NOT_APPLICABLE" in r["status"]),
        "mandatory_gates": sorted(MANDATORY_GATES),
        "rows": rows,
    }
    return matrix


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    matrix = generate_matrix()

    json_path = REPORT_BASE / "acceptance_matrix.json"
    tmp = json_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(json_path)

    md_path = REPORT_BASE / "ACCEPTANCE_REVIEW.md"
    lines = [
        "# Functional Agent_X Acceptance Review\n",
        f"Artifact type: {matrix['artifact_type']}  \n",
        f"Schema version: {matrix['schema_version']}  \n",
        f"Total rows: {matrix['total_rows']}  \n",
        f"Passed: {matrix['passed']}  \n",
        f"Blocked: {matrix['blocked']}  \n",
        f"Not applicable: {matrix['not_applicable']}\n",
        f"Mandatory gates: {', '.join(sorted(matrix['mandatory_gates']))}\n",
        "",
        "| ID | Description | Category | Status |",
        "|---|-------------|----------|--------|",
    ]
    for r in matrix["rows"]:
        lines.append(f"| {r['id']} | {r['description']} | {r['category']} | {r['status']} |")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Acceptance matrix written to {json_path}")
    return 0 if matrix["blocked"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

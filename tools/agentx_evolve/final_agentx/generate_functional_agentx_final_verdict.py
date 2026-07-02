#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.final_agentx import REPORT_BASE, get_git_commit, get_run_id, get_canonical_artifact_map

CLASSIFICATION_LADDER = [
    "NOT_FUNCTIONAL",
    "FUNCTIONAL_SCAFFOLD",
    "FUNCTIONAL_RUNTIME_MVP",
    "AGENTX_ADAPTER_MVP",
    "FUNCTIONAL_AGENT_EVOLUTION_ALPHA",
    "FUNCTIONAL_AGENT_EVOLUTION_BETA",
    "AGENTX_REPO_MEMORY_MVP",
    "AGENTX_GENERATED_AGENT_GIT_PROMOTION",
    "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE",
    "FUNCTIONAL_AGENTX_COMPLETE",
]

STAGE_GATES = [
    ("FUNCTIONAL_RUNTIME_MVP", ".agentx-init/reports/functional_runtime_mvp_final_verdict.json"),
    ("AGENTX_ADAPTER_MVP", ".agentx-init/reports/functional_agentx_adapter_final_verdict.json"),
    ("FUNCTIONAL_AGENT_EVOLUTION_ALPHA", ".agentx-init/reports/agent-evolution-alpha/final_verdict.json"),
    ("FUNCTIONAL_AGENT_EVOLUTION_BETA", ".agentx-init/reports/agent-evolution-beta/final_verdict.json"),
    ("AGENTX_REPO_MEMORY_MVP", ".agentx-init/reports/repo-memory-mvp/final_verdict.json"),
    ("AGENTX_GENERATED_AGENT_GIT_PROMOTION", ".agentx-init/reports/generated-agent-git-promotion/final_verdict.json"),
    ("FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE", ".agentx-init/reports/governed-self-evolution/final_verdict.json"),
]

FINAL_REQUIRED_REPORTS = get_canonical_artifact_map()

# Validation reports that the generator checks before computing classification.
# Each leaves a "passed" or "all_attacks_blocked" field.
VALIDATION_CHECK_FILES: list[tuple[str, Path, str]] = [
    ("Acceptance matrix validator", REPORT_BASE / "validate_acceptance_matrix.json", "passed"),
    ("Replay validator", REPORT_BASE / "validate_replay.json", "passed"),
    ("Anti-false-PASS audit", REPORT_BASE / "anti_false_pass_report.json", "all_attacks_blocked"),
    ("Gap discovery validator", REPORT_BASE / "validate_gap_discovery.json", "passed"),
    ("Environment validator", REPORT_BASE / "validate_environment.json", "passed"),
    ("No overclaim validator", REPORT_BASE / "validate_no_overclaim.json", "passed"),
    ("Review evidence binding", REPORT_BASE / "review_evidence_binding_validation.json", "passed"),
    ("CI evidence validator", REPORT_BASE / "validate_ci_evidence.json", "passed"),
    ("Command transcript validator", REPORT_BASE / "validate_command_transcript.json", "passed"),
]


def check_validation_results() -> tuple[list[str], int]:
    failures: list[str] = []
    failed_count = 0
    for name, path, field in VALIDATION_CHECK_FILES:
        if not path.exists():
            failures.append(f"{name}: validation result file missing")
            failed_count += 1
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not data.get(field):
                failures.append(f"{name}: {field} is falsy")
                failed_count += 1
        except (OSError, json.JSONDecodeError):
            failures.append(f"{name}: invalid or unreadable")
            failed_count += 1
    return failures, failed_count



def check_substage_verdict(name: str, path_str: str) -> dict:
    p = Path(path_str)
    if not p.exists():
        return {"name": name, "status": "MISSING", "verdict": None, "path": path_str}

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            verdict = data.get("verdict")
            if verdict is None:
                verdict = data.get("status", "UNKNOWN")
            return {"name": name, "status": "PRESENT", "verdict": verdict, "path": path_str}
        return {"name": name, "status": "PRESENT", "verdict": str(data), "path": path_str}
    except Exception as e:
        return {"name": name, "status": "INVALID", "verdict": str(e), "path": path_str}


def check_final_artifact(name: str, rel_path: str) -> dict:
    p = REPORT_BASE / rel_path if not rel_path.startswith(".agentx") else Path(rel_path)
    return {
        "name": name,
        "path": str(p),
        "exists": p.exists(),
    }


def compute_classification(stage_statuses: dict[str, dict]) -> str:
    highest = "NOT_FUNCTIONAL"
    for stage_name, _ in STAGE_GATES:
        info = stage_statuses.get(stage_name, {})
        verdict = info.get("verdict")
        if verdict == "PASS":
            highest = stage_name
        else:
            break

    if highest == "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE":
        highest = "FUNCTIONAL_AGENTX_COMPLETE"
    return highest


def generate_verdict() -> dict[str, Any]:
    run_id = get_run_id()
    git_commit = get_git_commit()

    stage_statuses: dict[str, dict] = {}
    downgrades = []
    missing_gates = 0
    for stage_name, path_str in STAGE_GATES:
        info = check_substage_verdict(stage_name, path_str)
        stage_statuses[stage_name] = info
        if info.get("verdict") != "PASS":
            missing_gates += 1
            if info["status"] == "MISSING":
                downgrades.append(f"{stage_name}: missing verdict file")
            elif info["status"] == "INVALID":
                downgrades.append(f"{stage_name}: invalid verdict file")

    classification = compute_classification(stage_statuses)

    final_artifact_map = get_canonical_artifact_map()
    final_artifacts = []
    missing_final = 0
    for namespace, files in final_artifact_map.items():
        for fname in files:
            if namespace == "functional-agentx":
                rel = fname
                sp = REPORT_BASE / fname
            else:
                rel = f".agentx-init/reports/{namespace}/{fname}"
                sp = Path(rel)
            present = sp.exists()
            final_artifacts.append({
                "namespace": namespace,
                "file": fname,
                "path": str(sp),
                "exists": present,
            })
            if not present and namespace == "functional-agentx":
                missing_final += 1
                downgrades.append(f"Missing final artifact: {namespace}/{fname}")

    total_stages = len(STAGE_GATES)
    passed_gates = total_stages - missing_gates

    import subprocess
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True, stderr=subprocess.STDOUT
        ).strip() or "detached"
    except Exception:
        branch = "UNKNOWN"

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.STDOUT
        ).strip()
        dirty = bool(status)
    except Exception:
        dirty = True

    validation_failures, validation_failed_count = check_validation_results()
    for vf in validation_failures:
        downgrades.append(f"Validation: {vf}")

    validation_ok = validation_failed_count == 0

    verdict = {
        "schema_version": "1.0",
        "artifact_type": "final_verdict",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_final_verdict.py",
        "run_id": run_id,
        "git_commit": git_commit,
        "git_branch": branch,
        "dirty_worktree": dirty,
        "validation_gates_total": len(VALIDATION_CHECK_FILES),
        "validation_gates_passed": validation_ok,
        "validation_failures": validation_failures,
        "verdict": "PASS" if (passed_gates == total_stages and not missing_final and validation_ok and classification in ("FUNCTIONAL_AGENTX_COMPLETE", "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE")) else "PARTIAL",
        "classification": classification,
        "ci_status": "NOT_ATTACHED_WITH_REASON",
        "mandatory_gates_total": total_stages,
        "mandatory_gates_passed": passed_gates,
        "mandatory_gates_failed": missing_gates,
        "downgrades": downgrades,
        "cannot_claim": [s for s, p in STAGE_GATES if stage_statuses.get(s, {}).get("verdict") != "PASS"],
        "stage_statuses": stage_statuses,
        "final_artifacts": final_artifacts,
    }
    return verdict


def generate_classification_report(verdict: dict) -> dict:
    return {
        "schema_version": "1.0",
        "artifact_type": "classification_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_final_verdict.py",
        "run_id": verdict["run_id"],
        "git_commit": verdict["git_commit"],
        "verdict": verdict["verdict"],
        "classification": verdict["classification"],
        "classification_ladder": CLASSIFICATION_LADDER,
        "ci_status": verdict["ci_status"],
        "dirty_worktree": verdict["dirty_worktree"],
        "downgrades": verdict["downgrades"],
        "cannot_claim": verdict["cannot_claim"],
        "mandatory_gates_passed": verdict["mandatory_gates_passed"],
        "mandatory_gates_total": verdict["mandatory_gates_total"],
        "final_artifacts_summary": {
            "total": len(verdict["final_artifacts"]),
            "present": sum(1 for a in verdict["final_artifacts"] if a["exists"]),
            "missing": sum(1 for a in verdict["final_artifacts"] if not a["exists"] and a["namespace"] == "functional-agentx"),
        },
        "notable_exclusions": [],
    }


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    verdict = generate_verdict()

    out_path = REPORT_BASE / "final_verdict.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    class_report = generate_classification_report(verdict)
    class_path = REPORT_BASE / "classification_report.json"
    tmp = class_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(class_report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(class_path)

    print(f"Final verdict written to {out_path}")
    print(f"Classification report written to {class_path}")
    print(f"  Classification: {verdict['classification']}")
    print(f"  Verdict: {verdict['verdict']}")
    print(f"  Gates passed: {verdict['mandatory_gates_passed']}/{verdict['mandatory_gates_total']}")
    print(f"  Dirty worktree: {verdict['dirty_worktree']}")

    if verdict["downgrades"]:
        print("  Downgrades:")
        for d in verdict["downgrades"]:
            print(f"    - {d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

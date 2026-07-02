#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, get_canonical_artifact_map, get_git_commit

VALID_CLASSIFICATIONS = [
    "NOT_FUNCTIONAL", "FUNCTIONAL_SCAFFOLD", "FUNCTIONAL_RUNTIME_MVP",
    "AGENTX_ADAPTER_MVP", "FUNCTIONAL_AGENT_EVOLUTION_ALPHA",
    "FUNCTIONAL_AGENT_EVOLUTION_BETA", "AGENTX_REPO_MEMORY_MVP",
    "AGENTX_GENERATED_AGENT_GIT_PROMOTION",
    "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE",
    "FUNCTIONAL_AGENTX_COMPLETE",
]


def validate() -> list[str]:
    errors: list[str] = []

    verdict_path = REPORT_BASE / "final_verdict.json"
    if not verdict_path.exists():
        errors.append(f"final_verdict.json not found at {verdict_path}")
        return errors

    try:
        data = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid final_verdict.json: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("final_verdict.json must be a JSON object")
        return errors

    classification = data.get("classification", "")
    verdict = data.get("verdict", "")

    if classification not in VALID_CLASSIFICATIONS:
        errors.append(f"Unknown classification: {classification}")

    if verdict == "PARTIAL" and data.get("mandatory_gates_failed", 0) > 0:
        pass

    if verdict in ("FAIL", "BLOCKED"):
        errors.append(f"Verdict is {verdict}")

    # PARTIAL verdict is not acceptable for prove-functional-agentx
    if verdict == "PARTIAL":
        errors.append("Verdict is PARTIAL — prove-functional-agentx requires PASS")

    # Staleness: reject final_verdict.json from a previous run
    current_commit = get_git_commit()
    reported_commit = data.get("git_commit", "")
    if reported_commit and reported_commit != current_commit:
        errors.append(f"Stale final_verdict.json: git_commit {reported_commit} != current {current_commit}")

    # Dirty worktree must lower classification
    if data.get("dirty_worktree") is True:
        errors.append("Dirty worktree detected — cannot prove from dirty checkout")

    # Cannot claim highest classification with failed gates
    if classification in ("FUNCTIONAL_AGENTX_COMPLETE", "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE") and data.get("mandatory_gates_failed", 0) > 0:
        errors.append(f"Cannot claim highest classification with {data['mandatory_gates_failed']} failed gates")

    # Must include AGENTX_REPO_MEMORY_MVP and AGENTX_GENERATED_AGENT_GIT_PROMOTION as mandatory
    stage_statuses = data.get("stage_statuses", {})
    for mandatory in ("AGENTX_REPO_MEMORY_MVP", "AGENTX_GENERATED_AGENT_GIT_PROMOTION"):
        info = stage_statuses.get(mandatory, {})
        if info.get("verdict") != "PASS":
            errors.append(f"Mandatory gate {mandatory} has verdict {info.get('verdict')}")

    # CI status checks
    ci_status = data.get("ci_status", "")
    if ci_status == "PASSED_WITH_RUN_ID":
        if not data.get("workflow_run_id"):
            errors.append("CI status is PASSED_WITH_RUN_ID but no workflow_run_id provided")
    elif ci_status and ci_status not in ("NOT_ATTACHED_WITH_REASON", "NOT_REQUIRED_FOR_LOCAL_CLASSIFICATION", "PASSED_WITH_RUN_ID", "FAILED_WITH_RUN_ID"):
        errors.append(f"Unknown ci_status: {ci_status}")

    # Final artifacts check
    final_artifacts = data.get("final_artifacts", [])
    canonical_map = get_canonical_artifact_map()
    for namespace, files in canonical_map.items():
        for fname in files:
            if fname in ("evidence_manifest.json", "terminal_seal.json"):
                continue  # generated after final verdict and seal wraps it
            matched = any(
                a.get("file") == fname and a.get("namespace") == namespace and a.get("exists")
                for a in final_artifacts
            )
            if not matched and namespace == "functional-agentx":
                errors.append(f"Canonical final artifact missing: {namespace}/{fname}")

    # Check classification_report.json exists and agrees
    class_path = REPORT_BASE / "classification_report.json"
    if not class_path.exists():
        errors.append("classification_report.json not found")
    else:
        try:
            class_data = json.loads(class_path.read_text(encoding="utf-8"))
            if class_data.get("classification") != classification:
                errors.append(f"classification_report.json ({class_data.get('classification')}) disagrees with final_verdict.json ({classification})")
            if class_data.get("verdict") != verdict:
                errors.append(f"classification_report.json verdict ({class_data.get('verdict')}) disagrees with final_verdict.json ({verdict})")
            class_commit = class_data.get("git_commit", "")
            if class_commit and class_commit != current_commit:
                errors.append(f"Stale classification_report.json: git_commit {class_commit} != current {current_commit}")
        except (OSError, json.JSONDecodeError):
            errors.append("classification_report.json is invalid JSON")

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_final_verdict",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_BASE / "validate_final_verdict.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE FINAL VERDICT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-final-verdict: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

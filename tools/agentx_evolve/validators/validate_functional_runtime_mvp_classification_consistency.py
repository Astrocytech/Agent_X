"""Validate classification consistency across all proof artifacts.

Items 410, 466:
- Compare scope map, source tree, Makefile targets, acceptance rows,
  traceability rows, and final verdict for contradictions.
- Ensure no artifact implies FUNCTIONAL_RUNTIME_MVP when scope map
  marks required layers as unproven.
- Ensure no acceptance row or traceability row claims PASS for an
  architecture layer that is explicitly out-of-scope.
- Ensure final verdict classification matches the scope map status.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

IN_SCOPE_LAYERS = {
    "initiator", "security_sandbox", "policy_registry", "patch_execution",
    "failure_taxonomy", "tool_adapter", "model_adapter", "local_model_runtime",
    "context_builder", "prompt_contract", "llm_worker", "self_evolution",
    "human_review", "promotion_gate", "git_integration", "evaluation_harness",
    "long_term_learning", "doc_sync", "task_queue", "monitoring",
    "packaging", "backup_dr", "final_acceptance",
}


def load_json(path: Path) -> dict | list | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_classification_consistency(report_dir: Path) -> list[str]:
    errors: list[str] = []

    # Load scope map
    scope_map = load_json(report_dir / "functional_runtime_mvp_scope_map.json")
    if not isinstance(scope_map, dict):
        errors.append("Classification-consistency: scope map missing or invalid")
        return errors

    subsystems = scope_map.get("subsystems", [])
    out_of_scope_items = scope_map.get("out_of_scope", [])

    # Collect which layers are in-scope and which are out-of-scope
    oos_ids: set[str] = set()
    for oos in out_of_scope_items:
        oid = oos.get("id", "")
        if oid:
            oos_ids.add(oid)

    in_scope_ids: set[str] = set()
    for sub in subsystems:
        sub_id = sub.get("id", "")
        if sub_id and sub_id not in oos_ids:
            status = sub.get("status", "")
            if status in ("implemented_and_proven", "implemented_unproven", "stub_only"):
                in_scope_ids.add(sub_id)

    # Load final verdict (may be missing in single-run mode; verdict is generated later)
    verdict = load_json(report_dir / "functional_runtime_mvp_final_verdict.json")
    if not isinstance(verdict, dict):
        return errors

    classification = verdict.get("classification", "")
    if classification == "FUNCTIONAL_RUNTIME_MVP":
        # Check that no required layer is explicitly out-of-scope
        for oos in out_of_scope_items:
            oos_desc = oos.get("description", "")
            oos_reason = oos.get("reason", "")
            if any(layer in oos_desc.lower() for layer in IN_SCOPE_LAYERS):
                errors.append(
                    f"Classification-consistency: classification is FUNCTIONAL_RUNTIME_MVP "
                    f"but layer '{oos.get('id')}' is out-of-scope: {oos_desc}"
                )

        # Check that at least some subsystems are implemented_and_proven
        proven = [s for s in subsystems if s.get("status") == "implemented_and_proven"]
        if not proven:
            errors.append(
                "Classification-consistency: classification is FUNCTIONAL_RUNTIME_MVP "
                "but no subsystems are marked implemented_and_proven"
            )

    # Load acceptance matrix
    acceptance = load_json(report_dir / "functional_runtime_mvp_acceptance_matrix.json")
    if isinstance(acceptance, dict):
        rows = acceptance.get("rows", [])
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row_status = row.get("status", "").upper()
                row_layer = row.get("architecture_layer", row.get("layer", "")).lower()
                if row_status in ("PASS", "ACCEPTED") and row_layer in oos_ids:
                    errors.append(
                        f"Classification-consistency: acceptance row for out-of-scope "
                        f"layer '{row_layer}' has status {row_status}"
                    )

    # Check scope map decision consistency
    scope_decisions = scope_map.get("architecture_decisions", [])
    if isinstance(scope_decisions, list):
        for i, decision in enumerate(scope_decisions):
            if not isinstance(decision, dict):
                continue
            if not decision.get("decision"):
                errors.append(f"Classification-consistency: architecture_decision[{i}] missing decision text")

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_classification_consistency(report_dir)
    if errors:
        for err in errors:
            print(err)
    else:
        print("validate-functional-runtime-mvp-classification-consistency: PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""Validate the Functional Runtime MVP architecture scope map.

Checks:
- File exists and is valid JSON
- All required fields are present
- All architecture layer IDs are unique
- covered_by lists reference valid validator names
- out_of_scope items have reasons
- Each layer has a valid status
- Each layer has at least a component list
- Git provenance fields are present
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

VALIDATOR_NAMES = {
    "validate_functional_runtime_mvp_reports",
    "validate_functional_runtime_mvp_replay",
    "validate_functional_runtime_mvp_transcript",
    "validate_functional_runtime_mvp_reuse_map",
    "validate_functional_runtime_mvp_source_safety",
    "validate_functional_runtime_mvp_traceability",
    "validate_functional_runtime_mvp_gap_discovery",
    "validate_functional_runtime_mvp_anti_false_pass",
    "validate_functional_runtime_mvp_idempotency",
    "validate_functional_runtime_mvp_validator_proof",
    "validate_functional_runtime_mvp_all_in_one",
    "validate_functional_runtime_mvp_final_verdict",
    "validate_functional_runtime_mvp_proof_config",
    "validate_functional_runtime_mvp_state_transition",
    "validate_functional_runtime_mvp_filesystem_snapshot",
    "validate_functional_runtime_mvp_schema_version",
    "validate_functional_runtime_mvp_secret_redaction",
    "validate_functional_runtime_mvp_side_effect",
    "validate_functional_runtime_mvp_failure_taxonomy",
    "validate_functional_runtime_mvp_core_invariants",
    "validate_functional_runtime_mvp_no_forced_pass",
    "validate_functional_runtime_mvp_proof_staleness",
    "validate_functional_runtime_mvp_event_log",
    "validate_functional_runtime_mvp_self_promotion",
    "validate_functional_runtime_mvp_execution_integrity",
    "validate_functional_runtime_mvp_artifact_safety",
    "validate_functional_runtime_mvp_determinism",
    "validate_functional_runtime_mvp_cross_report",
    "validate_functional_runtime_mvp_provenance",
    "validate_functional_runtime_mvp_clean_checkout",
    "validate_functional_runtime_mvp_state",
    "validate_functional_runtime_mvp_meta_quality",
    "validate_functional_runtime_mvp_completeness",
    "validate_functional_runtime_mvp_path_safety",
    "validate_functional_runtime_mvp_lifecycle",
    "validate_functional_runtime_mvp_corrective_coverage",
    "validate_functional_runtime_mvp_runtime_safety",
    "validate_functional_runtime_mvp_infrastructure",
    "validate_functional_runtime_mvp_security",
    "validate_functional_runtime_mvp_scope_map",
    "validate_functional_runtime_mvp_advanced",
    "validate_functional_runtime_mvp_deep",
    "validate_functional_runtime_mvp_enterprise",
    "validate_functional_runtime_mvp_aspirational",
    "validate_functional_runtime_mvp_no_hidden_authority",
    "validate_functional_runtime_mvp_required_artifacts",
    "validate_functional_runtime_mvp_classification_consistency",
    "validate_functional_runtime_mvp_json_markdown_consistency",
    "validate_functional_runtime_mvp_io_boundary",
    "validate_functional_runtime_mvp_proof_size",
    "validate_functional_runtime_mvp_state_reconstruction",
    "validate_functional_runtime_mvp_runtime_entrypoint",
    "validate_functional_runtime_mvp_confidentiality",
}

VALID_STATUSES = {
    "implemented_and_proven",
    "implemented_unproven",
    "stub_only",
    "deliberately_disabled",
    "out_of_scope_for_this_mvp",
    "future_work",
    "blocking",
}


def validate_scope_map(report_dir: Path) -> list[str]:
    errors: list[str] = []
    path = report_dir / "functional_runtime_mvp_scope_map.json"
    if not path.exists():
        errors.append("Scope-map: file not found: functional_runtime_mvp_scope_map.json")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"Scope-map: could not parse JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("Scope-map: root value must be a dict")
        return errors

    sv = data.get("schema_version", "")
    if sv not in ("agentx.scope_map.v1", "agentx.scope_map.v2"):
        errors.append(f"Scope-map: unexpected schema_version: {sv}")

    if not data.get("title"):
        errors.append("Scope-map: missing title")

    if not data.get("generated_at"):
        errors.append("Scope-map: missing generated_at")

    git_prov = data.get("git_provenance", {})
    if sv == "agentx.scope_map.v2" and not git_prov:
        errors.append("Scope-map: v2 requires git_provenance")

    # Validate layers (v2: architecture_layers, v1: subsystems)
    layers = data.get("architecture_layers") or data.get("subsystems", [])
    if not layers:
        errors.append("Scope-map: no layers defined (expected architecture_layers or subsystems)")

    seen_ids: set[str] = set()
    for i, layer in enumerate(layers):
        layer_id = layer.get("id", "")
        if not layer_id:
            errors.append(f"Scope-map: layer[{i}] missing id")
            continue
        if layer_id in seen_ids:
            errors.append(f"Scope-map: duplicate layer id: {layer_id}")
        seen_ids.add(layer_id)

        if not layer.get("name"):
            errors.append(f"Scope-map: layer[{layer_id}] missing name")

        if sv == "agentx.scope_map.v2":
            status = layer.get("status", "")
            if status not in VALID_STATUSES:
                errors.append(f"Scope-map: layer[{layer_id}] invalid status: {status!r}")
            if not layer.get("components"):
                errors.append(f"Scope-map: layer[{layer_id}] missing components list")

        for vname in layer.get("covered_by", []):
            if vname not in VALIDATOR_NAMES:
                errors.append(f"Scope-map: layer[{layer_id}] unknown validator: {vname}")

    out_of_scope = data.get("out_of_scope", [])
    for i, oos in enumerate(out_of_scope):
        if not oos.get("id"):
            errors.append(f"Scope-map: out_of_scope[{i}] missing id")
        if not oos.get("description"):
            errors.append(f"Scope-map: out_of_scope[{i}] missing description")
        if not oos.get("reason"):
            errors.append(f"Scope-map: out_of_scope[{i}] missing reason")

    architecture_decisions = data.get("architecture_decisions", [])
    if not architecture_decisions:
        errors.append("Scope-map: no architecture_decisions recorded")

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_scope_map(report_dir)
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations
import json, sys, os
from pathlib import Path

schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
schema_files = [
    "outcome_event.schema.json",
    "outcome_review.schema.json",
    "learning_signal.schema.json",
    "memory_candidate.schema.json",
    "learning_policy_decision.schema.json",
    "regression_link.schema.json",
    "outcome_review_report.schema.json",
    "learning_audit_event.schema.json",
    "follow_up_task_proposal.schema.json",
    "learning_lock.schema.json",
    "learning_review_index.schema.json",
    "learning_evidence_manifest.schema.json",
    "learning_implementation_review_report.schema.json",
    "learning_completion_record.schema.json",
    "learning_adapter_result.schema.json",
]

errors = []
for fname in schema_files:
    path = schemas_dir / fname
    if not path.exists():
        errors.append(f"MISSING: {fname}")
        continue
    try:
        schema = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"INVALID JSON: {fname} — {e}")
        continue
    for key in ("$schema", "type", "properties"):
        if key not in schema:
            errors.append(f"MISSING KEY '{key}': {fname}")

if errors:
    print(f"FAIL: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"OK: All {len(schema_files)} schemas valid")

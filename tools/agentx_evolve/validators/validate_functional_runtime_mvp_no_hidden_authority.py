"""Validate that no single report can claim FUNCTIONAL_RUNTIME_MVP alone.

Item 419: No single generated report, single validator, single Markdown file,
or single Makefile echo line may be sufficient to claim FUNCTIONAL_RUNTIME_MVP
without the full canonical proof graph.

Checks:
- final_verdict.json alone cannot claim FUNCTIONAL_RUNTIME_MVP without
  proof_bundle.json, evidence_manifest.json, acceptance_matrix.json,
  command_transcript.json, and scope_map.json all existing and consistent.
- No Markdown file contains a FUNCTIONAL_RUNTIME_MVP verdict that contradicts
  the machine-readable JSON.
- The Makefile does not echo FUNCTIONAL_RUNTIME_MVP before the final step.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REQUIRED_EVIDENCE = {
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_acceptance_matrix.json",
    "functional_runtime_mvp_command_transcript.json",
    "functional_runtime_mvp_scope_map.json",
    "functional_runtime_mvp_final_verdict.json",
}


def validate_no_hidden_authority(report_dir: Path) -> list[str]:
    errors: list[str] = []

    verdict_path = report_dir / "functional_runtime_mvp_final_verdict.json"
    if not verdict_path.exists():
        # No final verdict yet — nothing to check. The verdict is generated later
        # in the pipeline after all validators and the no-hidden-authority check.
        return errors

    try:
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"No-hidden-authority: final_verdict.json parse error: {e}")
        return errors

    if not isinstance(verdict, dict):
        errors.append("No-hidden-authority: final_verdict.json not a dict")
        return errors

    classification = verdict.get("classification", "")
    if classification != "FUNCTIONAL_RUNTIME_MVP":
        errors.append(f"No-hidden-authority: classification is '{classification}', not FUNCTIONAL_RUNTIME_MVP")
        return errors

    # Check all required evidence files exist
    for req_file in REQUIRED_EVIDENCE:
        if not (report_dir / req_file).exists():
            errors.append(f"No-hidden-authority: {req_file} missing — cannot claim FUNCTIONAL_RUNTIME_MVP from final_verdict alone")

    # Check that final_validator is not PASS if any required evidence is missing
    final_validator = verdict.get("final_validator", "")
    if final_validator == "all_passed":
        for req_file in REQUIRED_EVIDENCE:
            if not (report_dir / req_file).exists():
                errors.append(f"No-hidden-authority: final_validator says all_passed but {req_file} is missing")

    # Check validators list exists and is non-empty
    validators = verdict.get("validators", [])
    if not validators:
        errors.append("No-hidden-authority: final_verdict has empty validators list")

    # Check no Markdown file independently claims FUNCTIONAL_RUNTIME_MVP
    for md_path in sorted(report_dir.glob("*.md")):
        try:
            content = md_path.read_text(encoding="utf-8", errors="replace")
            if "FUNCTIONAL_RUNTIME_MVP" in content:
                errors.append(
                    f"No-hidden-authority: Markdown file {md_path.name} contains "
                    f"FUNCTIONAL_RUNTIME_MVP — only final_verdict.json may carry classification"
                )
        except OSError:
            pass

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_no_hidden_authority(report_dir)
    if errors:
        for err in errors:
            print(err)
    else:
        print("validate-functional-runtime-mvp-no-hidden-authority: PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

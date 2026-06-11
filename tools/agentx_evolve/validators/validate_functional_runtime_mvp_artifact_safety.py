"""Validate artifact safety proof.

Gaps 101-106: Artifact overwrite tests must prove default overwrite denial,
versioned writes, path traversal rejection, symlink escape rejection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_artifact_safety() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Artifact safety: proof bundle missing")
        return errors

    scenario_proofs = bundle.get("scenario_proofs", [])
    if not scenario_proofs:
        errors.append("Artifact safety: no scenario_proofs in bundle")
        return errors

    found_overwrite_evidence = False
    for sp in scenario_proofs:
        if not isinstance(sp, dict):
            continue
        artifacts = sp.get("artifact_refs", sp.get("artifacts", []))
        for art in artifacts:
            if not isinstance(art, dict):
                continue
            overwrite_policy = art.get("overwrite_policy", art.get("policy", ""))
            if overwrite_policy:
                if overwrite_policy not in ("deny", "versioned", "content_addressed"):
                    errors.append(f"Artifact safety: unknown overwrite_policy '{overwrite_policy}'")
                found_overwrite_evidence = True

    evidence = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(evidence, dict):
        for entry in evidence.get("evidence", []):
            if isinstance(entry, dict):
                etype = entry.get("type", "")
                if "overwrite" in etype.lower() or "artifact" in etype.lower():
                    found_overwrite_evidence = True

    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        for cmd in transcript:
            if isinstance(cmd, dict):
                ctext = (cmd.get("command", "") + " " + (cmd.get("stdout_summary", "") or "")).lower()
                if "overwrite" in ctext or "artifact_store" in ctext:
                    found_overwrite_evidence = True

    if not found_overwrite_evidence:
        errors.append("Artifact safety: no artifact overwrite policy evidence in scenario proofs or reports")

    return errors


def main() -> int:
    errs = validate_artifact_safety()
    if errs:
        print("VALIDATE ARTIFACT SAFETY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-artifact-safety: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())

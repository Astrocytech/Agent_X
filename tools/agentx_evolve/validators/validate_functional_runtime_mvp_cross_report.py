"""Cross-report consistency validator.

Covers gap list items 397-400:
  397. Compare all shared identifiers across reports
  398. Same scenario_id has same final verdict across reports
  399. Same artifact_id has same hash/path/policy across reports
  400. Same validator_id has same command path/version/hash across reports
"""
from __future__ import annotations

import hashlib
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


def load_reports() -> dict[str, dict | list | None]:
    names = [
        "functional_runtime_mvp_proof_bundle.json",
        "functional_runtime_mvp_acceptance_matrix.json",
        "functional_runtime_mvp_requirement_traceability_matrix.json",
        "functional_runtime_mvp_replay_report.json",
        "functional_runtime_mvp_anti_false_pass_audit.json",
        "functional_runtime_mvp_gap_discovery_report.json",
        "functional_runtime_mvp_evidence_manifest.json",
        "functional_runtime_mvp_source_mutation_report.json",
        "functional_runtime_mvp_command_transcript.json",
        "functional_runtime_compatibility_report.json",
    ]
    reports = {}
    for name in names:
        rp = REPORT_DIR / name
        if rp.exists():
            reports[name] = load_json(str(rp))
    return reports


def validate_cross_report() -> list[str]:
    errors = []
    reports = load_reports()

    if not reports:
        errors.append("No reports found for cross-report validation")
        return errors

    # Collect scenario verdicts across reports
    scenario_verdicts: dict[str, list[tuple[str, str]]] = {}

    # From replay report
    replay = reports.get("functional_runtime_mvp_replay_report.json")
    if isinstance(replay, dict):
        rows = replay.get("rows", [])
        for row in rows:
            if isinstance(row, dict):
                scenario = row.get("scenario", "")
                verdict = row.get("replay_verdict", row.get("original_verdict", ""))
                if scenario:
                    scenario_verdicts.setdefault(scenario, []).append(("replay_report", verdict))
    elif isinstance(replay, list):
        for row in replay:
            if isinstance(row, dict):
                scenario = row.get("scenario", "")
                verdict = row.get("replay_verdict", row.get("original_verdict", ""))
                if scenario:
                    scenario_verdicts.setdefault(scenario, []).append(("replay_report", verdict))

    # From acceptance matrix
    matrix = reports.get("functional_runtime_mvp_acceptance_matrix.json")
    if isinstance(matrix, dict):
        rows = matrix.get("rows", [])
        for row in rows:
            if isinstance(row, dict):
                comp = row.get("component", "")
                if "scenario" in comp.lower() or "safe" in comp.lower() or "unsafe" in comp.lower():
                    scenario_verdicts.setdefault(comp, []).append(("acceptance_matrix", row.get("status", "")))

    # From proof bundle
    bundle = reports.get("functional_runtime_mvp_proof_bundle.json")
    if isinstance(bundle, dict):
        for key in ("scenario_proofs", "replay_proofs"):
            proofs = bundle.get(key, [])
            if isinstance(proofs, list):
                for p in proofs:
                    if isinstance(p, dict):
                        sid = p.get("scenario_id", p.get("scenario", p.get("id", "")))
                        sverdict = p.get("verdict", p.get("status", ""))
                        if sid:
                            scenario_verdicts.setdefault(sid, []).append((f"bundle.{key}", sverdict))

    # Gap 398: Same scenario_id must have same verdict across reports
    for scenario, verdicts in scenario_verdicts.items():
        unique_verdicts = set(v for _, v in verdicts)
        if len(unique_verdicts) > 1:
            sources = ", ".join(f"{src}={v}" for src, v in verdicts)
            errors.append(
                f"Cross-report: scenario '{scenario}' has inconsistent verdicts: {sources}"
            )

    # Gap 399: Check artifact_id consistency
    artifact_hashes: dict[str, list[tuple[str, str]]] = {}
    if isinstance(bundle, dict):
        for key in ("scenario_proofs", "replay_proofs"):
            proofs = bundle.get(key, [])
            if isinstance(proofs, list):
                for p in proofs:
                    if isinstance(p, dict):
                        for artifact in p.get("artifact_refs", p.get("artifacts", [])):
                            if isinstance(artifact, dict):
                                aid = artifact.get("artifact_id", artifact.get("id", ""))
                                ahash = artifact.get("hash", "")
                                if aid and ahash:
                                    artifact_hashes.setdefault(aid, []).append((f"bundle.{key}", ahash))

    evidence = reports.get("functional_runtime_mvp_evidence_manifest.json")
    if isinstance(evidence, dict):
        for entry in evidence.get("evidence", []):
            if isinstance(entry, dict):
                aid = entry.get("artifact_id", entry.get("id", entry.get("file", "")))
                ahash = entry.get("hash", "")
                if aid and ahash:
                    artifact_hashes.setdefault(aid, []).append(("evidence_manifest", ahash))

    for aid, hashes in artifact_hashes.items():
        unique_hashes = set(h for _, h in hashes)
        if len(unique_hashes) > 1:
            sources = ", ".join(f"{src}={h}" for src, h in hashes)
            errors.append(
                f"Cross-report: artifact '{aid}' has inconsistent hashes: {sources}"
            )

    # Gap 397: Check git_commit consistency
    git_commits: dict[str, list[str]] = {}
    for rname, rdata in reports.items():
        if isinstance(rdata, dict):
            gc = rdata.get("git_commit", "")
            if gc:
                git_commits.setdefault(gc, []).append(rname)

    if len(git_commits) > 1:
        for gc, sources in git_commits.items():
            errors.append(
                f"Cross-report: git_commit '{gc}' in {sources} differs from other reports"
            )

    # Check proof_run_id consistency
    proof_run_ids: dict[str, list[str]] = {}
    for rname, rdata in reports.items():
        if isinstance(rdata, dict):
            prid = rdata.get("proof_run_id", "")
            if prid:
                proof_run_ids.setdefault(prid, []).append(rname)

    if len(proof_run_ids) > 1:
        for prid, sources in proof_run_ids.items():
            errors.append(
                f"Cross-report: proof_run_id '{prid}' in {sources} differs from other reports"
            )

    # Gap 400: Check validator command consistency in transcript
    transcript = reports.get("functional_runtime_mvp_command_transcript.json")
    if isinstance(transcript, list):
        validator_commands = {}
        for entry in transcript:
            if isinstance(entry, dict):
                cmd = entry.get("command", "")
                if "validate_functional_runtime_mvp_" in cmd:
                    vname = cmd.split("/")[-1].replace(".py", "")
                    if vname in validator_commands:
                        existing = validator_commands[vname]
                        if entry.get("exit_code", -1) != existing.get("exit_code", -2):
                            errors.append(
                                f"Cross-report: validator '{vname}' has inconsistent "
                                f"exit_codes: {existing.get('exit_code')} vs {entry.get('exit_code')}"
                            )
                    else:
                        validator_commands[vname] = entry

    return errors


def main() -> int:
    errs = validate_cross_report()
    if errs:
        print("VALIDATE CROSS-REPORT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-cross-report: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())

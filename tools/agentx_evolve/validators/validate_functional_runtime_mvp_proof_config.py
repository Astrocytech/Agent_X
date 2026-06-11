"""Validate proof configuration manifest, full Git provenance, toolchain integrity.

Gaps 378-394, 404-420: config manifest, full SHA, source-tree manifest, toolchain hashing,
generator fail-closed, final-verifier authority, classification algorithm consistency.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

REQUIRED_PROOF_FILES = [
    "functional_runtime_mvp_command_transcript.json",
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_acceptance_matrix.json",
    "functional_runtime_mvp_final_verdict.json",
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _git_full_sha() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def _git_tree_hash() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD:"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def _git_remote() -> str:
    try:
        r = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def validate_proof_config() -> list[str]:
    errors = []

    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(proof_bundle, dict):
        errors.append("Proof-config: proof bundle missing or invalid")
        return errors

    # Item 378: Canonical proof-configuration manifest
    config_manifest = proof_bundle.get("proof_config", proof_bundle.get("proof_configuration", {}))
    if not config_manifest:
        errors.append("Proof-config: 378 - proof bundle missing proof_config/proof_configuration manifest")
    elif isinstance(config_manifest, dict):
        for req_key in ["proof_version", "required_reports", "required_validators",
                         "required_attacks", "required_scenarios"]:
            if req_key not in config_manifest:
                errors.append(f"Proof-config: 378 - proof_config missing '{req_key}'")

    # Item 379: Hash of proof-configuration manifest in every final artifact
    config_hash = ""
    if isinstance(config_manifest, dict):
        config_hash = hashlib.sha256(json.dumps(config_manifest, sort_keys=True).encode()).hexdigest()
    for fname in REQUIRED_PROOF_FILES:
        fpath = REPORT_DIR / fname
        if not fpath.exists():
            continue
        data = load_json(str(fpath))
        if isinstance(data, dict):
            artifact_config_hash = data.get("proof_config_hash", data.get("config_hash", ""))
            if config_hash and artifact_config_hash and artifact_config_hash != config_hash:
                errors.append(f"Proof-config: 379 - {fname} config_hash mismatch")

    # Item 380: Fail if different proof-config hash from verifier
    if isinstance(config_manifest, dict):
        verifier_hash = proof_bundle.get("verifier_config_hash", "")
        if config_hash and verifier_hash and config_hash != verifier_hash:
            errors.append("Proof-config: 380 - verifier config hash != generator config hash")

    # Items 383-384: Full Git provenance
    full_sha = _git_full_sha()
    tree_hash = _git_tree_hash()
    bundle_commit = proof_bundle.get("git_commit", "")
    if bundle_commit:
        if len(bundle_commit) < 40:
            errors.append(f"Proof-config: 383 - git_commit '{bundle_commit}' is not full 40-char SHA")
        if bundle_commit != full_sha:
            errors.append(f"Proof-config: 383 - git_commit '{bundle_commit}' != current HEAD '{full_sha}'")

    for fname in REQUIRED_PROOF_FILES:
        fpath = REPORT_DIR / fname
        if not fpath.exists():
            continue
        data = load_json(str(fpath))
        if isinstance(data, dict):
            commit = data.get("git_commit", "")
            if commit and len(commit) < 40:
                errors.append(f"Proof-config: 384 - {fname} uses short SHA: '{commit}'")

    # Item 385: Source-tree manifest
    tree_manifest = proof_bundle.get("source_tree", proof_bundle.get("source_tree_manifest", {}))
    if not tree_manifest:
        errors.append("Proof-config: 385 - proof bundle missing source_tree/source_tree_manifest")

    # Items 388-390: Toolchain integrity
    toolchain_hashes = proof_bundle.get("toolchain_hashes", proof_bundle.get("toolchain", {}))
    if not toolchain_hashes:
        errors.append("Proof-config: 388 - proof bundle missing toolchain_hashes/toolchain integrity info")

    # Items 391-393: Generator fail-closed
    generator_proofs = proof_bundle.get("generator_proofs", proof_bundle.get("generator_results", []))
    if not generator_proofs or not isinstance(generator_proofs, list):
        errors.append("Proof-config: 391 - proof bundle missing generator_proofs/generator_results")

    # Items 404-407: Final-verifier authority separation
    verifier_info = proof_bundle.get("final_verifier", proof_bundle.get("verifier", {}))
    if not verifier_info:
        errors.append("Proof-config: 404 - proof bundle missing final_verifier/verifier info")
    elif isinstance(verifier_info, dict):
        verifier_type = verifier_info.get("type", "")
        if "independent" not in verifier_type.lower() and "frozen" not in verifier_type.lower():
            errors.append("Proof-config: 404 - final verifier must be independent/frozen type")

    # Item 405-406: Generator-written final_verdict should be marked candidate or verified
    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    if isinstance(verdict, dict):
        verdict_status = verdict.get("verdict_status", verdict.get("classification_source", "")).lower()
        if "candidate" not in verdict_status and "verified" not in verdict_status:
            errors.append(
                "Proof-config: 405 - final_verdict verdict_status must be 'candidate' or 'verified', "
                f"got '{verdict_status}'"
            )

    # Items 408-409: Single authoritative classification algorithm
    classification = verdict.get("classification", "") if isinstance(verdict, dict) else ""
    if classification == "FUNCTIONAL_RUNTIME_MVP":
        classification_rules = proof_bundle.get("classification_rules", proof_bundle.get("classification", {}))
        if not classification_rules:
            errors.append("Proof-config: 408 - proof bundle missing classification_rules for PASS claims")

    return errors


def main() -> int:
    errs = validate_proof_config()
    if errs:
        print("VALIDATE PROOF CONFIG FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-proof-config: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())

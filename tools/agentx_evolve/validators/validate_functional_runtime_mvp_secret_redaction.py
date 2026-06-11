"""Validate secret redaction and confidentiality in proof artifacts.

Gaps 341-346: secret detection, redaction metadata, anti-false-PASS for redaction.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

SECRET_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)api[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{16,}"),
    re.compile(r"(?i)access[_-]?token\s*[=:]\s*['\"]?[a-zA-Z0-9_\-\.]{16,}"),
    re.compile(r"(?i)secret\s*[=:]\s*['\"]?[a-zA-Z0-9_\-/\+]{16,}"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
    re.compile(r"(?i)private\s*key"),
    re.compile(r"(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"gho_[a-zA-Z0-9]{36}"),
    re.compile(r"sk-[a-zA-Z0-9]{32,}"),
    re.compile(r"(?i)password\s*[=:]\s*['\"]?[^'\"\s]{8,}"),
    re.compile(r"(?i)auth[_-]?token\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{16,}"),
    re.compile(r"(?i)session[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{16,}"),
]

SECRET_ARTIFACT_PATTERNS = [
    "env", "credential", "token", "key", "secret", "password",
    "authorization", "authentication", "bearer", "jwt",
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _scan_text(text: str, source_name: str) -> list[str]:
    errors = []
    for pattern in SECRET_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            errors.append(f"Secret-redaction: 343 - possible secret pattern in {source_name}: {pattern.pattern[:60]}")
    return errors


def validate_secret_redaction() -> list[str]:
    errors = []

    # Item 341: Check transcript for secrets
    transcript_path = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
    if transcript_path.exists():
        transcript = load_json(str(transcript_path))
        if isinstance(transcript, list):
            for cmd_idx, cmd in enumerate(transcript):
                if isinstance(cmd, dict):
                    cmd_text = json.dumps(cmd)
                    errors.extend(_scan_text(cmd_text, f"transcript cmd {cmd_idx}"))
                    stdout_summary = cmd.get("stdout_summary", "")
                    if stdout_summary:
                        errors.extend(_scan_text(stdout_summary, f"transcript cmd {cmd_idx} stdout"))
                    stderr_summary = cmd.get("stderr_summary", "")
                    if stderr_summary:
                        errors.extend(_scan_text(stderr_summary, f"transcript cmd {cmd_idx} stderr"))

    # Item 342: Check evidence manifest for secret-ref erence patterns
    ev_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(ev_manifest, dict):
        ev_text = json.dumps(ev_manifest)
        errors.extend(_scan_text(ev_text, "evidence_manifest"))
        evidence_list = ev_manifest.get("evidence", [])
        for entry in evidence_list:
            if isinstance(entry, dict):
                ev_path = entry.get("file", entry.get("path", ""))
                for pat in SECRET_ARTIFACT_PATTERNS:
                    if pat in ev_path.lower():
                        errors.append(
                            f"Secret-redaction: 342 - evidence manifest contains artifact path "
                            f"with potential secret name: {ev_path}"
                        )

    # Check proof bundle environment for secrets
    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(proof_bundle, dict):
        env = proof_bundle.get("environment", {})
        if isinstance(env, dict):
            env_text = json.dumps(env)
            errors.extend(_scan_text(env_text, "proof_bundle.environment"))
            for key in env:
                if any(pat in key.lower() for pat in ["secret", "token", "key", "password", "credential"]):
                    errors.append(f"Secret-redaction: 342 - environment contains potential secret key: {key}")

        # Item 345: Content-addressed log storage with redaction metadata
        log_proofs = proof_bundle.get("log_proofs", proof_bundle.get("command_proofs", []))
        for lp in log_proofs if isinstance(log_proofs, list) else []:
            if isinstance(lp, dict):
                redacted = lp.get("redacted", lp.get("redaction_applied", False))
                if not redacted:
                    cmd_name = lp.get("command", "?")
                    errors.append(f"Secret-redaction: 345 - command '{cmd_name}' log proof missing redaction metadata")

    # Item 346: Anti-false-PASS for redaction — reject missing redaction metadata
    if isinstance(proof_bundle, dict):
        redaction_proof = proof_bundle.get("redaction_proof", proof_bundle.get("redaction", {}))
        if not redaction_proof:
            errors.append("Secret-redaction: 346 - proof bundle missing redaction_proof section")

    return errors


def main() -> int:
    errs = validate_secret_redaction()
    if errs:
        print("VALIDATE SECRET REDACTION FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-secret-redaction: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())

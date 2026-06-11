from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return None


def sha256_of(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def check_missing_evidence_artifact(manifest: dict, repo_root: str | Path) -> list[str]:
    missing = []
    for art in manifest.get("artifacts", []):
        p = Path(repo_root) / art["path"]
        if not p.exists():
            missing.append(art["path"])
    return missing


def check_invalid_evidence_hash(manifest: dict, repo_root: str | Path) -> list[str]:
    invalid = []
    for art in manifest.get("artifacts", []):
        p = Path(repo_root) / art["path"]
        if p.exists():
            actual = sha256_of(p)
            if actual != art.get("sha256", ""):
                invalid.append(art["path"])
    return invalid


def check_noop_target(target_name: str, transcript: dict) -> bool:
    for cmd in transcript.get("commands", []):
        if cmd.get("command_id") == target_name and cmd.get("tests_run", 0) == 0:
            return True
    return False


def check_skipped_benchmark_cases(results: dict) -> list[str]:
    skipped = []
    for case in results.get("cases", []):
        if case.get("verdict") not in ("PASS", "FAIL"):
            skipped.append(case.get("case_id", "unknown"))
    return skipped


def validate_benchmark_case_schema(case: dict, schema: dict) -> list[str]:
    errors = []
    for req in schema.get("required", []):
        if req not in case:
            errors.append(f"missing required field: {req}")
    if "case_id" in case and not re.match(r"^P[0-9]-B[0-9]{3}$", case["case_id"]):
        errors.append(f"invalid case_id format: {case['case_id']}")
    return errors


def check_provenance(manifest: dict, generated_paths: list[str]) -> list[str]:
    unproven = []
    provenance_paths = {f["path"] for f in manifest.get("files", []) if f.get("origin") == "stage_b_generated"}
    for gp in generated_paths:
        if gp not in provenance_paths:
            unproven.append(gp)
    return unproven


def check_manual_insertion(manifest: dict, generated_paths: list[str]) -> list[str]:
    manual = []
    generated = {f["path"] for f in manifest.get("files", []) if f.get("origin") == "manual"}
    for gp in generated_paths:
        if gp in generated:
            manual.append(gp)
    return manual


def validate_events_append_only(log_path: str | Path, strict: bool = False) -> bool:
    with open(log_path) as f:
        lines = f.readlines()
    ids: list[str] = []
    for line in lines:
        try:
            entry = json.loads(line)
            ids.append(entry.get("event_id", ""))
        except json.JSONDecodeError:
            return False
    if strict and len(ids) >= 2:
        for i in range(1, len(ids)):
            prev = ids[i - 1]
            cur = ids[i]
            if prev and cur and prev.startswith("evt-") and cur.startswith("evt-"):
                try:
                    prev_seq = int(prev.removeprefix("evt-"))
                    cur_seq = int(cur.removeprefix("evt-"))
                    if cur_seq - prev_seq > 1:
                        return False
                except ValueError:
                    pass
    return len(ids) == len(set(ids))


def scan_secrets(paths: list[str | Path]) -> list[tuple[str, str]]:
    secret_patterns = [
        (r"-----BEGIN (RSA |EC )?PRIVATE KEY-----", "private_key"),
        (r"sk-[a-zA-Z0-9]{20,}", "openai_key"),
        (r"ghp_[a-zA-Z0-9]{36}", "github_token"),
        (r"AKIA[0-9A-Z]{16}", "aws_key"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "password"),
    ]
    found = []
    for p in paths:
        try:
            with open(p, 'r', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for pattern, name in secret_patterns:
                        if re.search(pattern, line):
                            found.append((str(p), name))
                            break
        except (IOError, OSError):
            pass
    return found


def check_missing_command_output(transcript: dict, repo_root: str | Path) -> list[str]:
    missing = []
    for cmd in transcript.get("commands", []):
        stdout = cmd.get("stdout_path")
        stderr = cmd.get("stderr_path")
        if stdout and not Path(repo_root, stdout).exists():
            missing.append(f"stdout:{stdout}")
        if stderr and not Path(repo_root, stderr).exists():
            missing.append(f"stderr:{stderr}")
    return missing


def check_changed_file_without_requirement_link(
    source_diff: dict, requirements: list[dict],
) -> list[str]:
    req_files: set[str] = set()
    for r in requirements:
        for f in r.get("covered_by", []):
            req_files.add(f)
    unlinked = []
    for entry in source_diff.get("changes", []):
        fp = entry.get("file", "")
        if fp and fp not in req_files:
            unlinked.append(fp)
    return unlinked


def check_replay_missing_transcript(replay_report: dict, repo_root: str | Path) -> list[str]:
    missing = []
    for cmd in replay_report.get("commands", []):
        tp = cmd.get("transcript_path", "")
        if tp and not Path(repo_root, tp).exists():
            missing.append(tp)
    return missing


def check_dependency_change_without_approval(dep_record: dict) -> list[str]:
    unapproved = []
    for change in dep_record.get("changes", []):
        if not change.get("approved", False):
            unapproved.append(change.get("file", change.get("dependency", "unknown")))
    return unapproved


def check_unsupported_final_claim(claims: list[str], supported: set[str]) -> list[str]:
    unsupported = []
    for claim in claims:
        claim_lower = claim.lower()
        if not any(s in claim_lower for s in supported):
            unsupported.append(claim)
    return unsupported


def check_overwritten_evidence(manifest_history: list[dict], repo_root: str | Path) -> list[str]:
    timestamps: dict[str, float] = {}
    overwritten = []
    for manifest in manifest_history:
        ts = manifest.get("timestamp_utc", 0)
        for art in manifest.get("artifacts", []):
            p = str(Path(repo_root) / art["path"])
            if p in timestamps and ts > timestamps[p]:
                overwritten.append(art["path"])
            timestamps[p] = ts
    return overwritten


def check_missing_failed_run_evidence(evidence_dir: str | Path) -> list[str]:
    missing = []
    ed = Path(evidence_dir)
    if not ed.is_dir():
        return [f"evidence directory not found: {evidence_dir}"]
    for sub in ed.iterdir():
        if sub.is_dir() and sub.name.startswith("run_"):
            verdict_file = sub / "verdict.json"
            if not verdict_file.exists():
                missing.append(str(sub.relative_to(ed.parent)))
            else:
                v = load_json(verdict_file)
                if v and v.get("verdict") == "FAIL":
                    evidence_file = sub / "evidence.json"
                    if not evidence_file.exists():
                        missing.append(f"failed-run missing evidence: {sub.name}")
    return missing


def check_event_log_truncation(log_path: str | Path) -> list[str]:
    issues = []
    if not Path(log_path).exists():
        return [f"log not found: {log_path}"]
    with open(log_path) as f:
        lines = f.readlines()
    ids_seen: set[str] = set()
    for i, line in enumerate(lines, 1):
        try:
            entry = json.loads(line)
            eid = entry.get("event_id", "")
            if eid in ids_seen:
                issues.append(f"duplicate event_id at line {i}: {eid}")
            ids_seen.add(eid)
        except json.JSONDecodeError as e:
            issues.append(f"invalid JSON at line {i}: {e}")
    return issues


def check_reused_run_id(evidence_dir: str | Path) -> list[str]:
    issues = []
    ed = Path(evidence_dir)
    if not ed.is_dir():
        return [f"evidence directory not found: {evidence_dir}"]
    seen: dict[str, str] = {}
    for sub in ed.iterdir():
        if sub.is_dir() and sub.name.startswith("run_"):
            run_id = sub.name
            run_verdict = sub / "verdict.json"
            if run_verdict.exists():
                content_hash = sha256_of(run_verdict)
                if run_id in seen and seen[run_id] != content_hash:
                    issues.append(f"reused run_id with different content: {run_id}")
                seen[run_id] = content_hash
    return issues

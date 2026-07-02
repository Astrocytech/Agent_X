from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def get_repo_root() -> Path:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        ).resolve()
    except Exception:
        return Path(__file__).resolve().parents[3]


# NOTE: Scripts should work from repo root (Makefile guarantees this).
# For scripts that need absolute paths, use get_repo_root().
REPORT_BASE = Path(".agentx-init/reports/functional-agentx")


def get_run_id() -> str:
    seed = os.environ.get("AGENTX_RUN_SEED", "default-seed")
    git_commit = get_git_commit()
    sequence = os.environ.get("AGENTX_RUN_SEQUENCE", "0")
    h = hashlib.sha256(f"{seed}:{git_commit}:{sequence}".encode()).hexdigest()[:12]
    return f"fa-{git_commit[:8]}-{h}"


def ensure_report_dir() -> Path:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    return REPORT_BASE


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_json(path: Path, data: Any) -> str:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)
    return compute_sha256(path)


def load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def get_git_branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"], stderr=subprocess.STDOUT, text=True
        ).strip() or "detached-head"
    except Exception:
        return "UNKNOWN"


def get_canonical_artifact_map() -> dict[str, list[str]]:
    return {
        "functional-agentx": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "final_verdict.json",
            "classification_report.json",
            "no_overclaim_report.json",
            "command_transcript.json",
            "COMMAND_TRANSCRIPT.md",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "gap_discovery_report.json",
            "GAP_DISCOVERY_REPORT.md",
            "ci_evidence_report.json",
            "clean_checkout_report.json",
            "dependency_evidence_report.json",
            "policy_precedence_report.json",
            "budget_enforcement_report.json",
            "side_effect_classification_report.json",
            "observability_trace_report.json",
            "mcp_boundary_validation.json",
            "alias_report.json",
            "environment_report.json",
            "review_evidence_binding_validation.json",
            # terminal_seal.json is intentionally excluded: it is generated after
            # the evidence manifest (Phase 18) and wraps the manifest + final_verdict
            # + classification_report. The seal is validated independently by
            # validate_terminal_seal.py in Phase 19.
        ],
        "agent-evolution-alpha": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "command_transcript.json",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "final_verdict.json",
        ],
        "agent-evolution-beta": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "command_transcript.json",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "final_verdict.json",
        ],
        "governed-self-evolution": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "command_transcript.json",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "final_verdict.json",
        ],
        "repo-memory-mvp": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "command_transcript.json",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "final_verdict.json",
        ],
        "generated-agent-git-promotion": [
            "acceptance_matrix.json",
            "ACCEPTANCE_REVIEW.md",
            "command_transcript.json",
            "evidence_manifest.json",
            "replay_report.json",
            "anti_false_pass_report.json",
            "final_verdict.json",
        ],
    }

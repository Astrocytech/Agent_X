from __future__ import annotations
from pathlib import Path
from typing import Any

from agentx_evolve.security.security_models import SandboxPolicy, new_id
from agentx_evolve.security.sandbox_policy import merge_sandbox_policy

PHASE_UMBRELLA_STAGE_A = "umbrella_stage_a"
PHASE_UMBRELLA_STAGE_B = "umbrella_stage_b"
PHASE_POST_UMBRELLA_STAGE_A = "post_umbrella_stage_a"
PHASE_POST_UMBRELLA_STAGE_B = "post_umbrella_stage_b"
PHASE_INVERSE_SCIENCE_PLANNING = "inverse_science_planning"
PHASE_INVERSE_SCIENCE_GOVERNED = "inverse_science_governed"
PHASE_BENCHCORE_BENCHMARK = "benchcore_benchmark"
PHASE_FINAL_ACCEPTANCE = "final_acceptance"
PHASE_CANARY = "canary"

_PHASE_REGISTRY: dict[str, dict] = {
    PHASE_UMBRELLA_STAGE_A: {
        "source_write_allowed": False,
        "allowlisted_write_paths": [],
    },
    PHASE_UMBRELLA_STAGE_B: {
        "source_write_allowed": True,
        "runtime_write_allowed": True,
        "allowlisted_write_paths": [
            "examples/",
            "tests/quick/umbrella_agent/",
        ],
    },
    PHASE_POST_UMBRELLA_STAGE_A: {
        "source_write_allowed": False,
        "allowlisted_write_paths": [],
        "protected_paths": [".git", ".agentx-init", "tools/agentx_evolve"],
    },
    PHASE_POST_UMBRELLA_STAGE_B: {
        "source_write_allowed": True,
        "runtime_write_allowed": True,
        "allowlisted_write_paths": [
            "examples/",
        ],
        "protected_paths": [".git", ".agentx-init", "tools/agentx_evolve"],
    },
    PHASE_INVERSE_SCIENCE_PLANNING: {
        "source_write_allowed": False,
        "allowlisted_write_paths": [],
    },
    PHASE_INVERSE_SCIENCE_GOVERNED: {
        "source_write_allowed": True,
        "runtime_write_allowed": True,
        "allowlisted_write_paths": [
            "examples/",
            "tests/quick/",
        ],
    },
    PHASE_BENCHCORE_BENCHMARK: {
        "source_write_allowed": False,
        "allowlisted_write_paths": ["benchmarks/benchcore/"],
    },
    PHASE_FINAL_ACCEPTANCE: {
        "source_write_allowed": True,
        "runtime_write_allowed": True,
        "allowlisted_write_paths": ["reports/", ".agentx-init/"],
    },
    PHASE_CANARY: {
        "source_write_allowed": True,
        "runtime_write_allowed": True,
        "allowlisted_write_paths": [".agentx-init/canary/", "reports/umbrella_agent/"],
        "blocked_write_paths": ["L0/"],
    },
}


def register_phase(phase_id: str, overrides: dict) -> None:
    _PHASE_REGISTRY[phase_id] = overrides


def policy_for_phase(
    phase_id: str,
    repo_root: Path,
    overrides: dict[str, Any] | None = None,
) -> SandboxPolicy:
    if phase_id not in _PHASE_REGISTRY:
        raise ValueError(
            f"Unknown phase '{phase_id}'. "
            f"Known phases: {list(_PHASE_REGISTRY.keys())}"
        )

    base = SandboxPolicy(
        policy_id=new_id("policy"),
        repo_root=str(repo_root.resolve()),
        runtime_state_root=".agentx-init",
        protected_paths=["L0/", "agent_x/runtime/", "core/"],
        source_write_allowed=False,
        runtime_write_allowed=True,
        network_allowed=False,
        shell_allowed=False,
        allowlisted_commands=[],
        allowlisted_write_paths=[".agentx-init/"],
        blocked_write_paths=["L0/"],
        max_file_size_bytes=1048576,
        resolve_symlinks=True,
        require_governance_for_source_write=True,
        require_session_for_source_write=True,
        require_rollback_for_source_write=True,
        redact_secret_patterns=[],
        audit_enabled=False,
        audit_log_path="",
        audit_level="metadata",
        warnings=[],
        errors=[],
    )

    phase_overrides = _PHASE_REGISTRY[phase_id]
    merged = merge_sandbox_policy(base, phase_overrides)

    if overrides:
        merged = merge_sandbox_policy(merged, overrides)

    return merged


def list_phases() -> list[str]:
    return list(_PHASE_REGISTRY.keys())

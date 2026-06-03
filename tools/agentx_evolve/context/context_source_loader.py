from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.context.context_models import (
    ContextSource,
    new_id,
    utc_now_iso,
    SOURCE_TRUST_SYSTEM,
    SOURCE_TRUST_AGENTX_CONTRACT,
    SOURCE_TRUST_VALIDATED_ARTIFACT,
    SOURCE_TRUST_USER_INPUT,
    SOURCE_TRUST_TOOL_OUTPUT,
    SOURCE_TRUST_UNTRUSTED_TEXT,
    SOURCE_TRUST_BLOCKED,
)


TRUST_ORDER = {
    SOURCE_TRUST_SYSTEM: 0,
    SOURCE_TRUST_AGENTX_CONTRACT: 1,
    SOURCE_TRUST_VALIDATED_ARTIFACT: 2,
    SOURCE_TRUST_USER_INPUT: 3,
    SOURCE_TRUST_TOOL_OUTPUT: 4,
    SOURCE_TRUST_UNTRUSTED_TEXT: 5,
}

KNOWN_SOURCE_TYPES = {
    "USER_TASK", "ROADMAP_DOCUMENT", "CONTRACT_DOCUMENT",
    "IMPLEMENTATION_SPEC", "REVIEW_DOD_DOCUMENT", "POLICY_RECORD",
    "SECURITY_SANDBOX_RECORD", "TOOL_RESULT", "PATCH_RECORD",
    "MODEL_PROFILE", "RUNTIME_PROFILE", "PROMPT_CONTRACT",
    "TEST_OUTPUT", "REPOSITORY_FILE", "REPOSITORY_SUMMARY",
    "EVIDENCE_ARTIFACT", "HUMAN_REVIEW_NOTE", "SYSTEM_CONSTRAINT",
}


def load_context_sources(
    source_requests: list[dict],
    policy_context: dict | None = None,
    repo_root: Path | None = None,
) -> list[ContextSource]:
    if policy_context is None:
        policy_context = {}

    policy_available = policy_context.get("policy_registry_available", False)
    sources: list[ContextSource] = []

    for req in source_requests:
        source = _build_source(req)

        if not source.allowed_by_policy:
            source.warnings.append("source not allowed by policy")

        if not policy_available:
            if source.source_trust_level in (SOURCE_TRUST_TOOL_OUTPUT, SOURCE_TRUST_UNTRUSTED_TEXT, SOURCE_TRUST_BLOCKED):
                source.errors.append("policy unavailable: high-risk source blocked")
                source.source_trust_level = SOURCE_TRUST_BLOCKED

        if source.source_trust_level == SOURCE_TRUST_BLOCKED:
            source.warnings.append("blocked source excluded")

        if source.source_type not in KNOWN_SOURCE_TYPES:
            source.warnings.append(f"unknown source type: {source.source_type}")

        sources.append(source)

    return sources


def _build_source(req: dict) -> ContextSource:
    trust_str = req.get("source_trust_level", SOURCE_TRUST_UNTRUSTED_TEXT)
    if trust_str not in TRUST_ORDER:
        trust_str = SOURCE_TRUST_UNTRUSTED_TEXT

    allowed = req.get("allowed_by_policy", False)
    if trust_str == SOURCE_TRUST_BLOCKED:
        allowed = False

    return ContextSource(
        source_id=req.get("source_id", new_id("src")),
        source_type=req.get("source_type", "UNKNOWN"),
        source_path=req.get("source_path"),
        source_component=req.get("source_component", ""),
        source_trust_level=trust_str,
        created_at=req.get("created_at"),
        modified_at=req.get("modified_at"),
        loaded_at=utc_now_iso(),
        allowed_by_policy=allowed,
        policy_decision_id=req.get("policy_decision_id"),
        evidence_refs=req.get("evidence_refs", []),
    )


# ---------------------------------------------------------------------------
# File/artifact selection (absorbed from file_selector.py / artifact_selector.py)
# ---------------------------------------------------------------------------


@dataclass
class FileMatch:
    file_path: str = ""
    relevance_score: float = 0.0
    reason: str = ""
    snippet: str = ""
    start_line: int = 0
    end_line: int = 0


@dataclass
class FileSelectionResult:
    allowed: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    matches: list[FileMatch] = field(default_factory=list)
    token_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def select_files(objective: str, task_type: str,
                 candidate_files: list[str] | None = None) -> FileSelectionResult:
    result = FileSelectionResult()
    if candidate_files:
        for f in candidate_files:
            result.allowed.append(f)
            score, reason = _score_file(f, objective, task_type)
            result.matches.append(FileMatch(
                file_path=f, relevance_score=score, reason=reason,
            ))
    return result


def _score_file(file_path: str, objective: str, task_type: str) -> tuple[float, str]:
    path_lower = file_path.lower()
    obj_lower = objective.lower()
    keywords = set(obj_lower.split())
    match_count = sum(1 for kw in keywords if kw in path_lower)
    if match_count > 0:
        return min(1.0, 0.3 + match_count * 0.1), f"Matches {match_count} keyword(s)"
    if task_type in ("WRITE_TEST",):
        if "test" in path_lower:
            return 0.8, "Test file for test-writing task"
        return 0.3, "Source file for test-writing task"
    if task_type == "EXPLAIN_FAILURE":
        return 0.5, "Potential related file for failure analysis"
    return 0.2, "Low relevance"


@dataclass
class ArtifactMatch:
    artifact_id: str = ""
    artifact_type: str = ""
    description: str = ""
    relevance_score: float = 0.0
    reason: str = ""


@dataclass
class ArtifactSelectionResult:
    selected: list[ArtifactMatch] = field(default_factory=list)
    token_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def select_artifacts(task_type: str, objective: str,
                     available: list[dict]) -> ArtifactSelectionResult:
    result = ArtifactSelectionResult()
    obj_lower = objective.lower()
    for item in available:
        artifact_type = item.get("artifact_type", "")
        description = item.get("description", "")
        aid = item.get("artifact_id", "")
        score, reason = _score_artifact(artifact_type, description, obj_lower)
        if score > 0:
            result.selected.append(ArtifactMatch(
                artifact_id=aid, artifact_type=artifact_type,
                description=description, relevance_score=score, reason=reason,
            ))
    return result


def _score_artifact(artifact_type: str, description: str,
                    objective_lower: str) -> tuple[float, str]:
    combined = (artifact_type + " " + description).lower()
    keywords = set(objective_lower.split())
    match_count = sum(1 for kw in keywords if kw in combined)
    if match_count > 0:
        return min(1.0, 0.4 + match_count * 0.1), f"Matches {match_count} keyword(s)"
    return 0.0, "No relevance"

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import to_dict


@dataclass
class FileMatch:
    file_path: str = ""
    relevance_score: float = 0.0
    reason: str = ""
    snippet: str = ""
    start_line: int = 0
    end_line: int = 0

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class FileSelectionResult:
    allowed: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    matches: list[FileMatch] = field(default_factory=list)
    token_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class FileSelector:
    ESTIMATE_TOKENS_PER_CHAR = 0.25

    def __init__(self, repo_path: str = ""):
        self._repo_path = repo_path

    def select(self, objective: str, task_type: str,
               candidate_files: list[str] | None = None) -> FileSelectionResult:
        result = FileSelectionResult()
        if candidate_files:
            for f in candidate_files:
                result.allowed.append(f)
                score, reason = self._score_file(f, objective, task_type)
                result.matches.append(FileMatch(
                    file_path=f, relevance_score=score, reason=reason,
                ))
                result.token_estimate += self._estimate_tokens(f)
        return result

    def _score_file(self, file_path: str, objective: str,
                    task_type: str) -> tuple[float, str]:
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

    def _estimate_tokens(self, file_path: str) -> int:
        return 0

    def with_estimate(self, file_path: str, char_count: int) -> int:
        return int(char_count * self.ESTIMATE_TOKENS_PER_CHAR)

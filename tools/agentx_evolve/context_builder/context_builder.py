"""Context builder with constraints and evidence plan."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TaskContext:
    task_description: str
    constraints: list = field(default_factory=list)
    allowed_files: list = field(default_factory=list)
    forbidden_files: list = field(default_factory=list)
    acceptance_criteria: list = field(default_factory=list)
    evidence_plan: list = field(default_factory=list)
    source: str = "fixture"

def build_context(task: str, profile: Optional[dict] = None) -> TaskContext:
    return TaskContext(
        task_description=task,
        constraints=["Fixture deterministic mode", "No live network", "No L0 mutation"],
        forbidden_files=["L0/", ".git/", ".env", "*.key", "*.pem"],
        acceptance_criteria=["All tests pass", "Evidence written", "No regression"],
        evidence_plan=["Source hashes before", "Test output", "Source diff", "Source hashes after"]
    )

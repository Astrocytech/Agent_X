"""Prompt contract management with versioning."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class PromptContractVersion(str, Enum):
    V1_0 = "1.0"
    V1_1 = "1.1"

@dataclass
class PromptContract:
    version: str = PromptContractVersion.V1_0
    constraints: list = field(default_factory=list)
    allowed_files: list = field(default_factory=list)
    forbidden_files: list = field(default_factory=list)
    acceptance_criteria: list = field(default_factory=list)
    evidence_plan: list = field(default_factory=list)
    
    def to_dict(self):
        return {"version": self.version, "constraints": self.constraints,
                "allowed_files": self.allowed_files, "forbidden_files": self.forbidden_files,
                "acceptance_criteria": self.acceptance_criteria, "evidence_plan": self.evidence_plan}

def create_default_contract():
    return PromptContract(constraints=["No live API", "Fixture deterministic mode"],
                          forbidden_files=["L0/", ".git/", ".env"],
                          acceptance_criteria=["All tests pass", "Evidence recorded"],
                          evidence_plan=["Source hash", "Test output", "Diff review"])

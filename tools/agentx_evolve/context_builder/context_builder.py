"""Canonical context packet construction.

Item 35 (30.1/30.2): Build task packets with bounded context,
token budget, file selection, and schema injection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class ContextPacket:
    task_type: str = ""
    objective: str = ""
    source_requirement: str = ""
    relevant_docs: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=list)
    target_files: list[str] = field(default_factory=list)
    existing_interfaces: list[str] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    model_runtime_profile: str = ""
    output_schema: dict[str, Any] = field(default_factory=dict)
    validation_commands: list[str] = field(default_factory=list)
    evidence_expectations: list[str] = field(default_factory=list)
    rollback_expectations: list[str] = field(default_factory=list)
    review_expectations: list[str] = field(default_factory=list)
    relevant_snippets: list[dict[str, str]] = field(default_factory=list)
    token_budget: int = 4000
    constraints: list[str] = field(default_factory=list)
    evidence_plan: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def estimate_tokens(self) -> int:
        total = 0
        for v in self.to_dict().values():
            if isinstance(v, str):
                total += len(v.split()) * 1.3
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        total += len(item.split()) * 1.3
                    elif isinstance(item, dict):
                        total += len(json.dumps(item).split()) * 1.3
            elif isinstance(v, dict):
                total += len(json.dumps(v).split()) * 1.3
        return int(total)

    def is_within_budget(self, budget: int | None = None) -> bool:
        return self.estimate_tokens() <= (budget or self.token_budget)


class ContextBuilder:
    def __init__(self, docs_root: str | Path | None = None):
        self._docs_root = Path(docs_root) if docs_root else Path("docs")

    def build_packet(self, requirement_id: str = "",
                      objective: str = "",
                      target_files: list[str] | None = None,
                      relevant_docs: list[str] | None = None,
                      allowed_paths: list[str] | None = None,
                      forbidden_paths: list[str] | None = None,
                      output_schema: dict | None = None,
                      token_budget: int = 4000) -> ContextPacket:
        packet = ContextPacket(
            task_type="generate_agent",
            objective=objective,
            source_requirement=requirement_id,
            relevant_docs=relevant_docs or [],
            allowed_paths=allowed_paths or ["examples/", "tests/quick/"],
            forbidden_paths=forbidden_paths or [".agentx-init/", "tools/agentx_evolve/", "L0/"],
            target_files=target_files or [],
            existing_interfaces=self._discover_interfaces(),
            available_tools=["file.read", "file.write", "subprocess.run", "git.status"],
            model_runtime_profile="deterministic-fixture",
            output_schema=output_schema or {"type": "object", "properties": {}},
            validation_commands=["pytest tests/quick/"],
            evidence_expectations=["provenance record", "source diff", "test results"],
            rollback_expectations=["rollback plan included"],
            review_expectations=["human review required"],
            constraints=["no L0 writes", "deterministic only", "fixture mode"],
            evidence_plan=["provenance", "source hash", "test report"],
            token_budget=token_budget,
        )

        if relevant_docs:
            for doc_path in relevant_docs:
                snippet = self._load_snippet(doc_path)
                if snippet:
                    packet.relevant_snippets.append(snippet)

        return packet

    def _discover_interfaces(self) -> list[str]:
        interfaces = []
        base = Path("tools/agentx_evolve/models")
        if base.exists():
            for f in base.rglob("*.py"):
                if f.stem != "__init__":
                    interfaces.append(f"agentx_evolve.models.{f.stem}")
        return interfaces

    def _load_snippet(self, doc_path: str) -> dict[str, str] | None:
        p = Path(doc_path)
        if not p.exists():
            return None
        try:
            text = p.read_text()
            return {"path": doc_path, "content": text[:2000]}  # truncate to 2000 chars
        except Exception:
            return None

    def rank_files(self, files: list[str], objective: str) -> list[str]:
        """Rank files by relevance to the objective using keyword matching."""
        keywords = set(objective.lower().split())
        scored = []
        for f in files:
            p = Path(f)
            if not p.exists():
                continue
            try:
                content = p.read_text().lower()
                score = sum(1 for kw in keywords if kw in content)
                scored.append((score, f))
            except Exception:
                scored.append((0, f))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [f for _, f in scored]


build_context = ContextBuilder().build_packet

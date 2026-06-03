from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import to_dict


@dataclass
class DocDrift:
    location: str = ""
    expected: str = ""
    actual: str = ""
    severity: str = "info"

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class DocSyncResult:
    total_checks: int = 0
    drifts: list[DocDrift] = field(default_factory=list)
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class DocSyncChecker:
    def check(self, checks: list[dict]) -> DocSyncResult:
        result = DocSyncResult()
        for c in checks:
            result.total_checks += 1
            expected = c.get("expected", "")
            actual = c.get("actual", "")
            location = c.get("location", "unknown")
            if expected != actual:
                drift = DocDrift(
                    location=location,
                    expected=expected,
                    actual=actual,
                    severity=c.get("severity", "warn"),
                )
                result.drifts.append(drift)
                result.passed = False
        return result


class SchemaDocChecker:
    def check(self, schema_fields: list[dict], doc_fields: list[str]) -> list[str]:
        mismatches = []
        for field in schema_fields:
            name = field.get("name", "")
            if name and name not in doc_fields:
                mismatches.append(f"Schema field '{name}' missing from docs")
        for doc in doc_fields:
            if not any(f.get("name") == doc for f in schema_fields):
                mismatches.append(f"Doc field '{doc}' missing from schema")
        return mismatches

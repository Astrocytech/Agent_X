from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationErrorEntry:
    test_name: str = ""
    error_message: str = ""
    file: str = ""
    line: int = 0

    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "error_message": self.error_message,
            "file": self.file,
            "line": self.line,
        }


@dataclass
class ValidationErrorSummary:
    total_errors: int = 0
    total_failures: int = 0
    entries: list[ValidationErrorEntry] = field(default_factory=list)
    summary_text: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_errors": self.total_errors,
            "total_failures": self.total_failures,
            "entries": [e.to_dict() for e in self.entries],
            "summary_text": self.summary_text,
        }


class ValidationErrorSummarizer:
    def summarize(self, test_output: str) -> ValidationErrorSummary:
        summary = ValidationErrorSummary()
        if not test_output:
            summary.summary_text = "No test output to analyze."
            return summary
        lines = test_output.split("\n")
        entries: list[ValidationErrorEntry] = []
        for line in lines:
            if "FAILED" in line or "ERROR" in line:
                entries.append(ValidationErrorEntry(
                    error_message=line.strip(),
                ))
        summary.total_errors = sum(1 for e in entries if "ERROR" in e.error_message)
        summary.total_failures = sum(1 for e in entries if "FAILED" in e.error_message)
        summary.entries = entries[:20]
        if len(entries) > 20:
            summary.warnings.append(f"Truncated {len(entries)} errors to 20")
        summary.summary_text = (
            f"{summary.total_failures} failures, {summary.total_errors} errors "
            f"across {len(entries)} entries"
        )
        return summary

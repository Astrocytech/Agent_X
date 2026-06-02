from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Any


@dataclass
class CLICommandRequest:
    schema_version: str = "1.0"
    request_id: str = ""
    timestamp: str = ""
    command: str = ""
    category: str = "UNKNOWN"
    arguments: dict = field(default_factory=dict)
    requested_effect: str = ""
    output_format: str = "text"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CLICommandResponse:
    schema_version: str = "1.0"
    response_id: str = ""
    request_id: str = ""
    timestamp: str = ""
    command: str = ""
    status: str = "SUCCESS"
    exit_code: int = 0
    message: str = ""
    data: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CLIContext:
    repo_root: str = ""
    runtime_root: str = ""
    config: Optional[dict] = None
    path_registry: Optional[Any] = None

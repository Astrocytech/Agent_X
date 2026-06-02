from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


MEMORY_CATEGORIES = [
    "SCAN", "ARCHITECTURE", "GOVERNANCE", "RISK", "PLANNING",
    "PATCH_PROPOSAL", "VALIDATION", "AUDIT", "SYSTEM", "UNKNOWN",
]

MEMORY_STATUSES = ["ACTIVE", "SUPERSEDED", "CORRECTION", "INVALID", "UNKNOWN"]


@dataclass
class MemoryRecord:
    schema_version: str = "1.0"
    memory_id: str = ""
    record_version: str = "1.0"
    timestamp: str = ""
    category: str = "SYSTEM"
    status: str = "ACTIVE"
    source_component: str = ""
    source_artifact: Optional[str] = None
    source_event_id: Optional[str] = None
    payload: dict = field(default_factory=dict)
    references: list = field(default_factory=list)
    content_hash: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryReference:
    schema_version: str = "1.0"
    reference_id: str = ""
    source_memory_id: str = ""
    target_memory_id: str = ""
    target_artifact: str = ""
    reference_type: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryIndex:
    schema_version: str = "1.0"
    index_id: str = ""
    timestamp: str = ""
    by_category: dict = field(default_factory=dict)
    by_source_component: dict = field(default_factory=dict)
    by_source_artifact: dict = field(default_factory=dict)
    by_status: dict = field(default_factory=dict)
    by_memory_id: dict = field(default_factory=dict)
    record_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemorySnapshot:
    schema_version: str = "1.0"
    snapshot_id: str = ""
    timestamp: str = ""
    record_count: int = 0
    index_ref: Optional[str] = None
    records: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryQuery:
    memory_id: Optional[str] = None
    category: Optional[str] = None
    source_component: Optional[str] = None
    source_artifact: Optional[str] = None
    status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryQueryResult:
    schema_version: str = "1.0"
    query_id: str = ""
    timestamp: str = ""
    query: dict = field(default_factory=dict)
    result_count: int = 0
    records: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryManifest:
    schema_version: str = "1.0"
    manifest_id: str = ""
    timestamp: str = ""
    record_count: int = 0
    latest_snapshot: Optional[str] = None
    latest_index: Optional[str] = None
    categories: list = field(default_factory=list)
    schema_versions: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryWriteResult:
    status: str = "SUCCESS"
    memory_id: str = ""
    content_hash: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

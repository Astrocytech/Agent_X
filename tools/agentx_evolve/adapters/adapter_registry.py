from __future__ import annotations

from typing import Any
from dataclasses import dataclass, field

ADAPTER_RECORD_SCHEMA_VERSION = "adapter.record.v1"


@dataclass
class AdapterRecord:
    adapter_id: str = ""
    adapter_type: str = ""
    provider: str = ""
    capabilities: list[str] = field(default_factory=list)
    live_required: bool = False
    allowed_profiles: list[str] = field(default_factory=list)
    schemas: list[str] = field(default_factory=list)
    status: str = "disabled"
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "adapter_type": self.adapter_type,
            "provider": self.provider,
            "capabilities": self.capabilities,
            "live_required": self.live_required,
            "allowed_profiles": self.allowed_profiles,
            "schemas": self.schemas,
            "status": self.status,
            "version": self.version,
        }


class AdapterRegistry:
    def __init__(self) -> None:
        self._records: dict[str, AdapterRecord] = {}

    def register(self, record: AdapterRecord) -> None:
        self._records[record.adapter_id] = record

    def get(self, adapter_id: str) -> AdapterRecord | None:
        return self._records.get(adapter_id)

    def resolve(self, adapter_id: str, profile_id: str = "default") -> AdapterRecord | None:
        record = self._records.get(adapter_id)
        if not record:
            return None
        if record.status != "enabled":
            return None
        if record.live_required and profile_id == "offline":
            return None
        return record

    def list_adapters(self, status: str | None = None) -> list[AdapterRecord]:
        if status:
            return [r for r in self._records.values() if r.status == status]
        return list(self._records.values())

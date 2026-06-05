from __future__ import annotations

from dataclasses import dataclass, field

from agentx_evolve.models.model_models import SPEC_SCHEMA_VERSION, SOURCE_COMPONENT, to_dict


@dataclass
class RuntimeProfile:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_runtime_profile.schema.json"
    profile_id: str = ""
    profile_name: str = ""
    local_only: bool = True
    network_allowed: bool = False
    max_loaded_models: int = 1
    default_context_window: int = 4096
    max_total_context_tokens: int = 8192
    vram_budget_gb: float = 0.0
    endpoint_allowlisted: bool = False
    allowed_endpoints: list[str] = field(default_factory=lambda: ["127.0.0.1", "localhost", "[::1]"])
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalRuntimeProfile(RuntimeProfile):
    profile_id: str = "local_default"
    profile_name: str = "Local Default Runtime"
    local_only: bool = True
    network_allowed: bool = False


@dataclass
class HostedProviderProfile(RuntimeProfile):
    profile_id: str = "hosted_default"
    profile_name: str = "Hosted Provider Runtime"
    local_only: bool = False
    network_allowed: bool = True
    max_loaded_models: int = 3
    endpoint_allowlisted: bool = False
    allowed_endpoints: list[str] = field(default_factory=list)


def make_local_default_runtime() -> LocalRuntimeProfile:
    return LocalRuntimeProfile()


def make_hosted_default_runtime() -> HostedProviderProfile:
    return HostedProviderProfile()

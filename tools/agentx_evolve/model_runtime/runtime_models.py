from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

RUNTIME_MODE_LOCAL_ONLY = "LOCAL_ONLY"
RUNTIME_MODE_LOCAL_PREFERRED = "LOCAL_PREFERRED"
RUNTIME_MODE_DISABLED = "DISABLED"

DEVICE_CPU = "CPU"
DEVICE_GPU = "GPU"
DEVICE_AUTO = "AUTO"

AVAILABILITY_AVAILABLE = "AVAILABLE"
AVAILABILITY_MISSING = "MISSING"
AVAILABILITY_BLOCKED = "BLOCKED"

COMPATIBILITY_COMPATIBLE = "COMPATIBLE"
COMPATIBILITY_INCOMPATIBLE = "INCOMPATIBLE"
COMPATIBILITY_DEGRADED = "DEGRADED"

ELIGIBILITY_ELIGIBLE = "ELIGIBLE"
ELIGIBILITY_INELIGIBLE = "INELIGIBLE"
ELIGIBILITY_BLOCKED = "BLOCKED"
ELIGIBILITY_DEGRADED = "DEGRADED"

QUANT_F32 = "F32"
QUANT_F16 = "F16"
QUANT_Q8 = "Q8"
QUANT_Q6 = "Q6"
QUANT_Q5 = "Q5"
QUANT_Q4 = "Q4"
QUANT_UNKNOWN = "UNKNOWN"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{ts}"


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return dict(obj)


def stable_json_hash(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize_decision_status(value: str) -> str:
    upper = value.upper().strip()
    known = {
        "ALLOW", "BLOCK", "BLOCKED", "UNAVAILABLE", "INCOMPATIBLE",
        "NEEDS_REPACK", "CPU_FALLBACK", "GPU_REQUIRED", "DEGRADED_LOCAL",
        "POLICY_DENIED", "PROFILE_INVALID", "HARDWARE_PROFILE_INVALID",
        "MEMORY_BUDGET_EXCEEDED", "CONTEXT_WINDOW_EXCEEDED",
        "QUANTIZATION_UNSUPPORTED", "BACKEND_UNSUPPORTED",
        "HOSTED_FALLBACK_FORBIDDEN",
    }
    if upper in known:
        return upper
    return "UNKNOWN"


@dataclass
class LocalModelProfile:
    schema_version: str = "1.0"
    schema_id: str = "local_model_profile.schema.json"
    model_id: str = ""
    model_name: str = ""
    model_family: str = ""
    model_format: str = ""
    model_path: str | None = None
    model_size_bytes: int | None = None
    parameter_count: int | None = None
    quantization: str = QUANT_UNKNOWN
    max_context_tokens: int = 0
    supported_task_types: list[str] = field(default_factory=list)
    supported_output_modes: list[str] = field(default_factory=list)
    supported_runtime_ids: list[str] = field(default_factory=list)
    preferred_runtime_ids: list[str] = field(default_factory=list)
    requires_gpu: bool = False
    supports_cpu: bool = True
    supports_gpu: bool = False
    enabled: bool = True
    priority: int = 100
    profile_source_path: str | None = None
    profile_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalRuntimeProfile:
    schema_version: str = "1.0"
    schema_id: str = "local_runtime_profile.schema.json"
    runtime_id: str = ""
    runtime_name: str = ""
    runtime_kind: str = ""
    supported_model_formats: list[str] = field(default_factory=list)
    supported_quantizations: list[str] = field(default_factory=list)
    supported_devices: list[str] = field(default_factory=list)
    max_context_tokens: int = 0
    requires_server: bool = False
    can_start_server: bool = False
    uses_network: bool = False
    supports_cpu_fallback: bool = True
    supports_gpu_fallback: bool = False
    command_probe_allowed: bool = False
    enabled: bool = True
    priority: int = 100
    profile_source_path: str | None = None
    profile_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.max_total_context_tokens = self.max_context_tokens


@dataclass
class LocalHardwareProfile:
    schema_version: str = "1.0"
    schema_id: str = "local_hardware_profile.schema.json"
    hardware_profile_id: str = ""
    probe_mode: str = "STATIC_ONLY"
    cpu_arch: str | None = None
    os_name: str | None = None
    ram_total_bytes: int | None = None
    ram_available_bytes: int | None = None
    gpu_present: bool = False
    gpu_name: str | None = None
    gpu_vram_total_bytes: int | None = None
    gpu_vram_available_bytes: int | None = None
    conservative_ram_limit_bytes: int = 0
    conservative_vram_limit_bytes: int | None = None
    probe_timestamp: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalModelInventory:
    schema_version: str = "1.0"
    schema_id: str = "local_model_inventory.schema.json"
    inventory_id: str = ""
    created_at: str = ""
    approved_model_roots: list[str] = field(default_factory=list)
    models: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalModelAvailabilityDecision:
    schema_version: str = "1.0"
    schema_id: str = "local_model_availability.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    model_id: str = ""
    availability: str = ""
    model_path: str | None = None
    path_allowed: bool = False
    file_present: bool = False
    profile_repository_hash: str = ""
    failure_class: str | None = None
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalRuntimeCompatibilityDecision:
    schema_version: str = "1.0"
    schema_id: str = "local_runtime_compatibility_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    model_id: str = ""
    runtime_id: str = ""
    compatibility: str = ""
    device: str = ""
    format_compatible: bool = False
    quantization_compatible: bool = False
    context_compatible: bool = False
    memory_compatible: bool = False
    policy_allowed: bool = False
    fallback_applied: bool = False
    fallback_reason: str | None = None
    profile_repository_hash: str = ""
    failure_class: str | None = None
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalModelSelectionConstraints:
    schema_version: str = "1.0"
    schema_id: str = "local_model_selection_constraints.schema.json"
    allowed_model_ids: list[str] = field(default_factory=list)
    blocked_model_ids: list[str] = field(default_factory=list)
    allowed_runtime_ids: list[str] = field(default_factory=list)
    blocked_runtime_ids: list[str] = field(default_factory=list)
    allowed_quantizations: list[str] = field(default_factory=list)
    blocked_quantizations: list[str] = field(default_factory=list)
    allowed_devices: list[str] = field(default_factory=list)
    max_model_size_bytes: int = 0
    max_context_tokens: int = 0
    max_estimated_memory_bytes: int = 0
    local_only: bool = True
    network_allowed: bool = False
    allow_model_download: bool = False
    allow_server_start: bool = False
    allow_cpu_fallback: bool = False
    allow_gpu_fallback: bool = False
    allow_hosted_fallback: bool = False
    preferred_runtime_order: list[str] = field(default_factory=list)
    preferred_quantization_order: list[str] = field(default_factory=list)
    preferred_model_order: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalRuntimeRequestLimits:
    schema_version: str = "1.0"
    schema_id: str = "local_runtime_request_limits.schema.json"
    max_prompt_tokens: int = 4096
    max_response_tokens: int = 2048
    max_total_context_tokens: int = 8192
    max_input_bytes: int = 0
    max_output_bytes: int = 0
    max_batch_size: int = 1
    max_concurrent_requests: int = 1
    reserved_response_tokens: int = 512
    safety_margin_tokens: int = 256
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LocalModelEligibilityDecision:
    schema_version: str = "1.0"
    schema_id: str = "local_model_eligibility_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    request_id: str | None = None
    selected_model_id: str | None = None
    selected_runtime_id: str | None = None
    eligibility: str = ""
    requested_task_type: str | None = None
    requested_context_tokens: int = 0
    runtime_mode: str = ""
    device: str = ""
    availability_decision_id: str | None = None
    compatibility_decision_id: str | None = None
    estimated_memory: dict = field(default_factory=dict)
    ranking_score: dict = field(default_factory=dict)
    rejected_candidates: list[dict] = field(default_factory=list)
    fallbacks_applied: list[dict] = field(default_factory=list)
    profile_repository_hash: str = ""
    failure_class: str | None = None
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RuntimeArtifactRecord:
    schema_version: str = "1.0"
    artifact_path: str = ""
    artifact_type: str = ""
    sha256: str = ""
    created_at: str = ""
    size_bytes: int = 0


@dataclass
class LocalRuntimeEvidenceManifest:
    schema_version: str = "1.0"
    schema_id: str = "local_model_runtime_evidence_manifest.schema.json"
    component_id: str = "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
    validated_commit: str = ""
    validated_at: str = ""
    review_environment: dict = field(default_factory=dict)
    commands: list[dict] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    evidence_file_hashes: list[dict] = field(default_factory=list)
    required_artifact_hashes: dict = field(default_factory=dict)
    runtime_artifacts: list[str] = field(default_factory=list)
    known_expected_runtime_artifacts: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    source_mutation_status: str = ""
    no_load_validation_status: str = ""
    deterministic_reproducibility_status: str = ""
    bounded_validation_status: str = ""
    model_profile_validation_status: str = ""
    hardware_profile_validation_status: str = ""
    runtime_compatibility_status: str = ""
    model_locator_safety_status: str = ""
    inventory_drift_status: str = ""
    cache_invalidation_status: str = ""
    capability_taxonomy_status: str = ""
    environment_redaction_status: str = ""
    policy_integration_status: str = ""
    model_adapter_integration_status: str = ""
    context_builder_integration_status: str = ""
    prompt_contract_integration_status: str = ""
    tool_mcp_integration_status: str = ""
    hash_status: str = ""
    final_decision: str = ""


@dataclass
class LocalRuntimeReviewReport:
    schema_version: str = "1.0"
    schema_id: str = "local_model_runtime_review_report.schema.json"
    component_id: str = "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
    review_document_id: str = "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD"
    review_document_version: str = "v4.0"
    reviewed_commit: str = ""
    reviewed_branch: str = ""
    reviewed_at: str = ""
    reviewer: str = ""
    review_environment: dict = field(default_factory=dict)
    working_tree_start_status: str = ""
    working_tree_end_status: str = ""
    commands_run: list[dict] = field(default_factory=list)
    command_output_hashes: list[dict] = field(default_factory=list)
    coverage_statuses: dict = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    high_issues: list[str] = field(default_factory=list)
    non_blocking_followups: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    review_report_path: str = ""
    review_report_sha256: str = ""
    completion_record_path: str = ""
    completion_record_sha256: str = ""
    implementation_rating: float = 10.0
    final_verdict: str = ""


@dataclass
class LocalRuntimeCompletionRecord:
    schema_version: str = "1.0"
    schema_id: str = "local_model_runtime_completion_record.schema.json"
    component_id: str = "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
    component_name: str = "Local Model Runtime Profile Layer"
    status: str = "VALIDATED"
    validated_commit: str = ""
    validated_at: str = ""
    review_environment: dict = field(default_factory=dict)
    canonical_subdirectory: str = "tools/agentx_evolve/model_runtime/"
    canonical_schema_subdirectory: str = "tools/agentx_evolve/schemas/"
    canonical_test_subdirectory: str = "tools/agentx_evolve/tests/"
    runtime_artifact_root: str = ".agentx-init/model_runtime/"
    basis_documents: list[str] = field(default_factory=lambda: [
        "LOCAL_MODEL_RUNTIME_PROFILE_EQC_FIC_SIB_SCHEMA_CONTRACT",
        "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC",
        "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD",
    ])
    commands_run: list[dict] = field(default_factory=list)
    files_created_or_changed: list[str] = field(default_factory=list)
    schemas_created_or_changed: list[str] = field(default_factory=list)
    tests_created_or_changed: list[str] = field(default_factory=list)
    validated_capabilities: list[str] = field(default_factory=list)
    model_profiles_verified: list[str] = field(default_factory=list)
    hardware_profiles_verified: list[str] = field(default_factory=list)
    no_load_validation_verified: list[str] = field(default_factory=list)
    runtime_compatibility_verified: list[str] = field(default_factory=list)
    model_locator_safety_verified: list[str] = field(default_factory=list)
    inventory_drift_verified: list[str] = field(default_factory=list)
    quantization_compatibility_verified: list[str] = field(default_factory=list)
    context_window_compatibility_verified: list[str] = field(default_factory=list)
    memory_budget_verified: list[str] = field(default_factory=list)
    policy_integration_verified: list[str] = field(default_factory=list)
    model_adapter_integration_verified: list[str] = field(default_factory=list)
    context_builder_integration_verified: list[str] = field(default_factory=list)
    prompt_contract_integration_verified: list[str] = field(default_factory=list)
    tool_mcp_adapter_integration_verified: list[str] = field(default_factory=list)
    negative_tests_verified: list[str] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    review_report_path: str = ""
    review_report_sha256: str = ""
    completion_record_sha256: str = ""
    deviation_register: list[dict] = field(default_factory=list)
    unresolved_risks: list[dict] = field(default_factory=list)
    implementation_score: float = 10.0
    final_decision: str = ""


def make_local_default_runtime() -> LocalRuntimeProfile:
    return LocalRuntimeProfile(
        runtime_id="local_default",
        runtime_name="Default Local Runtime",
        runtime_kind="local",
        supported_model_formats=["gguf", "safetensors"],
        supported_quantizations=["Q4", "Q8", "F16"],
        supported_devices=["CPU"],
        max_context_tokens=8192,
        enabled=True,
    )


def make_hosted_default_runtime():
    return LocalRuntimeProfile(
        runtime_id="hosted_default",
        runtime_name="Default Hosted Provider",
        runtime_kind="hosted",
        supported_model_formats=[],
        supported_quantizations=[],
        supported_devices=[],
        max_context_tokens=65536,
        uses_network=True,
        enabled=True,
    )


class RuntimeProfile:
    def __init__(self, profile_id="", max_total_context_tokens=8192, max_loaded_models=1):
        self.profile_id = profile_id
        self.max_total_context_tokens = max_total_context_tokens
        self.max_loaded_models = max_loaded_models


class HostedProviderProfile:
    def __init__(self, profile_id="hosted_default", local_only=False, network_allowed=True,
                 max_total_context_tokens=65536):
        self.profile_id = profile_id
        self.local_only = local_only
        self.network_allowed = network_allowed
        self.max_total_context_tokens = max_total_context_tokens


RuntimeProfileAlias = LocalRuntimeProfile

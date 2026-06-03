from dataclasses import dataclass, field
from typing import Any

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_PARTIAL = "PARTIAL"
STATUS_NOT_CHECKED = "NOT_CHECKED"
STATUS_NOT_RUN = "NOT_RUN"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_DEFERRED_SAFELY = "DEFERRED_SAFELY"
STATUS_STALE = "STALE"

VALIDATED_NOT_ACCEPTED = "VALIDATED_NOT_ACCEPTED"

VERDICT_ACCEPTED = "ACCEPTED"
VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS = "ACCEPTED_WITH_SAFE_DEFERRALS"
VERDICT_NOT_ACCEPTED = "NOT_ACCEPTED"

SEVERITY_BLOCKER = "BLOCKER"
SEVERITY_HIGH = "HIGH"
SEVERITY_NON_BLOCKING = "NON_BLOCKING"

MODE_IMPLEMENTATION_ACCEPTANCE = "IMPLEMENTATION_ACCEPTANCE"
MODE_SOURCE_ONLY_ACCEPTANCE = "SOURCE_ONLY_ACCEPTANCE"
MODE_NON_PRODUCTION_ACCEPTANCE = "NON_PRODUCTION_ACCEPTANCE"
MODE_PRODUCTION_ACCEPTANCE = "PRODUCTION_ACCEPTANCE"
MODE_RELEASE_ACCEPTANCE = "RELEASE_ACCEPTANCE"

ALL_STATUSES = frozenset({
    STATUS_PASS, STATUS_FAIL, STATUS_PARTIAL, STATUS_NOT_CHECKED,
    STATUS_NOT_RUN, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY, STATUS_STALE,
})
ALL_VERDICTS = frozenset({VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED})
ALL_SEVERITIES = frozenset({SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING})
ALL_MODES = frozenset({
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
})


@dataclass
class FinalAcceptanceLayer:
    layer_id: str = ""
    layer_name: str = ""
    roadmap_number: int = 0
    required_for_acceptance: bool = True
    safe_deferral_allowed: bool = False
    expected_package_path: str = ""
    expected_runtime_artifact_root: str = ""
    expected_completion_record_path: str = ""
    expected_review_report_path: str = ""
    expected_evidence_manifest_path: str = ""
    acceptance_modes_required: list[str] = field(default_factory=list)
    deferral_modes_allowed: list[str] = field(default_factory=list)
    expected_evidence_aliases: list[str] = field(default_factory=list)
    stale_after_days: int | None = None
    bootstrap_self_layer: bool = False
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_layer.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceLayerRegistry:
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_layer_registry.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    reviewed_commit: str | None = None
    reviewed_branch: str | None = None
    created_at: str = ""
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE
    bootstrap_self: bool = False
    layers: list[FinalAcceptanceLayer] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceEvidenceItem:
    layer_id: str = ""
    artifact_path: str = ""
    artifact_type: str = ""
    required: bool = True
    exists: bool = False
    readable: bool = False
    sha256: str | None = None
    schema_valid: bool = True
    schema_validation_error: str | None = None
    reviewed_commit_in_artifact: str | None = None
    artifact_timestamp: str | None = None
    stale: bool = False
    alias_used: str | None = None
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_evidence_item.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceEvidenceManifest:
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_evidence_manifest.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    reviewed_commit: str | None = None
    created_at: str = ""
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE
    items: list[FinalAcceptanceEvidenceItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class CrossLayerCheck:
    check_id: str = ""
    source_layer: str = ""
    target_layer: str = ""
    requirement: str = ""
    status: str = STATUS_PASS
    severity: str = SEVERITY_NON_BLOCKING
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_cross_layer_check.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceValidationResult:
    command_name: str = ""
    command_text: str = ""
    exit_code: int | None = None
    status: str = STATUS_NOT_RUN
    summary: str = ""
    output_artifact_path: str | None = None
    output_sha256: str | None = None
    expected_failure: bool = False
    expected_failure_condition: str = ""
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_validation_result.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceDeviation:
    deviation_id: str = ""
    area: str = ""
    layer_id: str = ""
    description: str = ""
    reason: str = ""
    safety_impact: str = "none"
    compensating_control: str = ""
    accepted_status: str = ""
    reviewer_decision: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_deviation.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceArtifactHash:
    artifact_path: str = ""
    sha256: str = ""
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_artifact_hash.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceModePolicy:
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_mode_policy.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE
    mode_rules: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceReport:
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_report.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    reviewed_commit: str | None = None
    reviewed_branch: str | None = None
    created_at: str = ""
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE
    bootstrap_mode_used: bool = False
    final_verdict: str = VERDICT_NOT_ACCEPTED
    implementation_rating: float = 0.0
    layer_statuses: dict[str, str] = field(default_factory=dict)
    evidence_summary: dict[str, Any] = field(default_factory=dict)
    cross_layer_summary: dict[str, Any] = field(default_factory=dict)
    validation_summary: dict[str, Any] = field(default_factory=dict)
    schema_validation_summary: dict[str, Any] = field(default_factory=dict)
    safe_deferrals: list[dict[str, Any]] = field(default_factory=list)
    deviations: list[dict[str, Any]] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    high_issues: list[str] = field(default_factory=list)
    non_blocking_followups: list[str] = field(default_factory=list)
    artifact_hashes: list[dict[str, Any]] = field(default_factory=list)
    artifact_hashes_path: str = ""
    artifact_hashes_content_id: str = ""
    artifact_hashes_sha256: str | None = None
    self_hash_mode: str = "EXCLUDED_FROM_SELF_HASH"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FinalAcceptanceCompletionRecord:
    schema_version: str = "1.0"
    schema_id: str = "final_acceptance_completion_record.schema.json"
    source_component: str = "AGENTX_FINAL_SYSTEM_ACCEPTANCE"
    status: str = "VALIDATED"
    reviewed_commit: str | None = None
    reviewed_branch: str | None = None
    created_at: str = ""
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE
    bootstrap_mode_used: bool = False
    final_verdict: str = VERDICT_NOT_ACCEPTED
    implementation_rating: float = 0.0
    commands_run: list[dict[str, Any]] = field(default_factory=list)
    artifacts_created: list[str] = field(default_factory=list)
    review_environment: dict[str, Any] = field(default_factory=dict)
    artifact_hashes: list[dict[str, Any]] = field(default_factory=list)
    artifact_hashes_path: str = ""
    artifact_hashes_content_id: str = ""
    artifact_hashes_sha256: str | None = None
    self_hash_mode: str = "EXCLUDED_FROM_SELF_HASH"
    accepted_safe_deferrals: list[dict[str, Any]] = field(default_factory=list)
    unresolved_blockers: list[str] = field(default_factory=list)
    unresolved_high_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


LCM_PASS = "PASS"
LCM_FAIL = "FAIL"


@dataclass
class LayerCompletionMatrix:
    layer_id: str = ""
    layer_name: str = ""
    status: str = LCM_PASS
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        return {
            "total": self.total_checks,
            "passed": self.passed_checks,
            "failed": self.failed_checks,
        }

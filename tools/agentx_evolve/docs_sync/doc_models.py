import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DOC_AUTHORITY_MANUAL_GOVERNED = "MANUAL_GOVERNED"
DOC_AUTHORITY_MANUAL_EDITABLE = "MANUAL_EDITABLE"
DOC_AUTHORITY_GENERATED = "GENERATED"
DOC_AUTHORITY_RUNTIME_EVIDENCE = "RUNTIME_EVIDENCE"
DOC_AUTHORITY_EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
DOC_AUTHORITY_UNKNOWN = "UNKNOWN"

DOC_TYPE_CONTRACT = "CONTRACT"
DOC_TYPE_IMPLEMENTATION_SPEC = "IMPLEMENTATION_SPEC"
DOC_TYPE_REVIEW_DOD = "REVIEW_DOD"
DOC_TYPE_README = "README"
DOC_TYPE_INDEX = "INDEX"
DOC_TYPE_SCHEMA = "SCHEMA"
DOC_TYPE_TEST = "TEST"
DOC_TYPE_REPORT = "REPORT"
DOC_TYPE_EVIDENCE = "EVIDENCE"
DOC_TYPE_OTHER = "OTHER"

DOC_OP_SCAN = "SCAN"
DOC_OP_PLAN = "PLAN"
DOC_OP_VALIDATE = "VALIDATE"
DOC_OP_UPDATE_GENERATED = "UPDATE_GENERATED"
DOC_OP_UPDATE_INDEX = "UPDATE_INDEX"
DOC_OP_UPDATE_README_SECTION = "UPDATE_README_SECTION"
DOC_OP_BLOCKED_MANUAL_DOC = "BLOCKED_MANUAL_DOC"
DOC_OP_NOOP = "NOOP"

DOC_STATUS_CURRENT = "CURRENT"
DOC_STATUS_STALE = "STALE"
DOC_STATUS_MISSING = "MISSING"
DOC_STATUS_DRIFTED = "DRIFTED"
DOC_STATUS_BLOCKED = "BLOCKED"
DOC_STATUS_INVALID = "INVALID"
DOC_STATUS_PLANNED = "PLANNED"
DOC_STATUS_APPLIED = "APPLIED"
DOC_STATUS_FAILED = "FAILED"

DOC_SYNC_MODE_SCAN_ONLY = "scan_only"
DOC_SYNC_MODE_VALIDATE_ONLY = "validate_only"
DOC_SYNC_MODE_SCAN_PLAN = "scan_plan"
DOC_SYNC_MODE_DRY_RUN_APPLY = "dry_run_apply"
DOC_SYNC_MODE_APPLY_GENERATED = "apply_generated"
DOC_SYNC_MODE_REVIEW_REPORT = "review_report"
DOC_SYNC_MODE_COMPLETION_RECORD = "completion_record"

LINK_TYPE_LOCAL_FILE = "LOCAL_FILE"
LINK_TYPE_LOCAL_FILE_WITH_ANCHOR = "LOCAL_FILE_WITH_ANCHOR"
LINK_TYPE_LOCAL_ANCHOR = "LOCAL_ANCHOR"
LINK_TYPE_EXTERNAL_HTTP = "EXTERNAL_HTTP"
LINK_TYPE_EXTERNAL_MAILTO = "EXTERNAL_MAILTO"
LINK_TYPE_EXTERNAL_OTHER = "EXTERNAL_OTHER"
LINK_TYPE_UNSUPPORTED = "UNSUPPORTED"
LINK_TYPE_MALFORMED = "MALFORMED"

CENTRAL_STATUS_PASS = "PASS"
CENTRAL_STATUS_PARTIAL = "PARTIAL"
CENTRAL_STATUS_FAIL = "FAIL"
CENTRAL_STATUS_BLOCKED = "BLOCKED"
CENTRAL_STATUS_INVALID = "INVALID"
CENTRAL_STATUS_NOT_CHECKED = "NOT_CHECKED"
CENTRAL_STATUS_NOT_RUN = "NOT_RUN"
CENTRAL_STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
CENTRAL_STATUS_DEFERRED_SAFELY = "DEFERRED_SAFELY"
CENTRAL_STATUS_SCANNED = "SCANNED"
CENTRAL_STATUS_PLAN_CREATED = "PLAN_CREATED"
CENTRAL_STATUS_DRY_RUN_COMPLETE = "DRY_RUN_COMPLETE"
CENTRAL_STATUS_APPLIED = "APPLIED"
CENTRAL_STATUS_CURRENT = "CURRENT"
CENTRAL_STATUS_STALE = "STALE"
CENTRAL_STATUS_DRIFTED = "DRIFTED"
CENTRAL_STATUS_MISSING = "MISSING"

TRACEABILITY_STATUS_PASS = "PASS"
TRACEABILITY_STATUS_PARTIAL = "PARTIAL"
TRACEABILITY_STATUS_FAIL = "FAIL"
TRACEABILITY_STATUS_NOT_CHECKED = "NOT_CHECKED"
TRACEABILITY_STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
TRACEABILITY_STATUS_DEFERRED_SAFELY = "DEFERRED_SAFELY"

DEVIATION_ACCEPTED_STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
DEVIATION_ACCEPTED_STATUS_DEFERRED_SAFELY = "DEFERRED_SAFELY"
DEVIATION_ACCEPTED_STATUS_NON_BLOCKING_FOLLOWUP = "NON_BLOCKING_FOLLOWUP"
DEVIATION_ACCEPTED_STATUS_REJECTED = "REJECTED"

ANCHOR_STATUS_VALID = "ANCHOR_VALID"
ANCHOR_STATUS_MISSING = "ANCHOR_MISSING"
ANCHOR_STATUS_NOT_CHECKED = "ANCHOR_NOT_CHECKED"
ANCHOR_STATUS_DEFERRED_SAFELY = "ANCHOR_DEFERRED_SAFELY"
ANCHOR_STATUS_UNSUPPORTED = "ANCHOR_UNSUPPORTED"

DRIFT_TYPE_MISSING_CONTRACT_SPEC_REVIEW = "MISSING_CONTRACT_SPEC_REVIEW"
DRIFT_TYPE_MISSING_SCHEMA = "MISSING_SCHEMA"
DRIFT_TYPE_MISSING_TEST = "MISSING_TEST"
DRIFT_TYPE_DONE_WITHOUT_EVIDENCE = "DONE_WITHOUT_EVIDENCE"
DRIFT_TYPE_STALE_COMPONENT = "STALE_COMPONENT"
DRIFT_TYPE_STALE_README_STATUS = "STALE_README_STATUS"
DRIFT_TYPE_MISSING_INDEX_ENTRY = "MISSING_INDEX_ENTRY"
DRIFT_TYPE_BROKEN_LINK = "BROKEN_LINK"
DRIFT_TYPE_MISSING_EVIDENCE = "MISSING_EVIDENCE"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_BLOCKER = "BLOCKER"

LOCK_MODE_READ = "read"
LOCK_MODE_WRITE = "write"
LOCK_STATUS_ACTIVE = "ACTIVE"
LOCK_STATUS_STALE = "STALE"
LOCK_STATUS_RELEASED = "RELEASED"
LOCK_STATUS_BLOCKED = "BLOCKED"

APPLY_MODE_DRY_RUN = "dry_run"
APPLY_MODE_APPLY = "apply"

STATUS_VOCABULARY = frozenset({
    "PASS", "PARTIAL", "FAIL", "BLOCKED", "INVALID", "NOT_CHECKED",
    "NOT_RUN", "NOT_APPLICABLE", "DEFERRED_SAFELY", "SCANNED",
    "PLAN_CREATED", "DRY_RUN_COMPLETE", "APPLIED", "CURRENT",
    "STALE", "DRIFTED", "MISSING",
})


class DocumentRecord:
    __slots__ = (
        "schema_version", "schema_id", "document_id", "path", "title",
        "document_type", "authority", "component_id", "layer_id",
        "version", "status", "sha256", "last_modified_utc",
        "contains_generated_markers", "protected", "links_out",
        "links_in", "warnings", "errors",
    )

    def __init__(
        self,
        document_id: str,
        path: str,
        document_type: str = DOC_TYPE_OTHER,
        authority: str = DOC_AUTHORITY_UNKNOWN,
        schema_version: str = "1.0",
        schema_id: str = "documentation_record.schema.json",
        title: str | None = None,
        component_id: str | None = None,
        layer_id: str | None = None,
        version: str | None = None,
        status: str | None = None,
        sha256: str | None = None,
        last_modified_utc: str | None = None,
        contains_generated_markers: bool = False,
        protected: bool = False,
        links_out: list[str] | None = None,
        links_in: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.document_id = document_id
        self.path = path
        self.title = title
        self.document_type = document_type
        self.authority = authority
        self.component_id = component_id
        self.layer_id = layer_id
        self.version = version
        self.status = status
        self.sha256 = sha256
        self.last_modified_utc = last_modified_utc
        self.contains_generated_markers = contains_generated_markers
        self.protected = protected
        self.links_out = links_out or []
        self.links_in = links_in or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentScanReport:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "scan_id",
        "created_at", "repo_root", "scanned_paths", "documents",
        "skipped_paths", "summary", "warnings", "errors",
    )

    def __init__(
        self,
        scan_id: str,
        created_at: str,
        repo_root: str,
        scanned_paths: list[str] | None = None,
        documents: list[DocumentRecord] | None = None,
        skipped_paths: list[str] | None = None,
        summary: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_scan.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.scan_id = scan_id
        self.created_at = created_at
        self.repo_root = repo_root
        self.scanned_paths = scanned_paths or []
        self.documents = documents or []
        self.skipped_paths = skipped_paths or []
        self.summary = summary or {}
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentDriftRecord:
    __slots__ = (
        "schema_version", "schema_id", "drift_id", "created_at",
        "document_id", "path", "drift_type", "status", "expected",
        "actual", "severity", "recommended_operation",
        "blocked_reason", "warnings", "errors",
    )

    def __init__(
        self,
        drift_id: str,
        created_at: str,
        document_id: str,
        path: str,
        drift_type: str,
        status: str,
        expected: dict | None = None,
        actual: dict | None = None,
        severity: str = SEVERITY_MEDIUM,
        recommended_operation: str = DOC_OP_NOOP,
        blocked_reason: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_drift_report.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.drift_id = drift_id
        self.created_at = created_at
        self.document_id = document_id
        self.path = path
        self.drift_type = drift_type
        self.status = status
        self.expected = expected or {}
        self.actual = actual or {}
        self.severity = severity
        self.recommended_operation = recommended_operation
        self.blocked_reason = blocked_reason
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentSyncOperation:
    __slots__ = (
        "schema_version", "schema_id", "operation_id", "operation_type",
        "target_path", "target_authority", "requires_policy_approval",
        "requires_manual_review", "allowed_to_apply", "reason",
        "diff_preview", "evidence_refs", "warnings", "errors",
    )

    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        target_path: str,
        target_authority: str,
        requires_policy_approval: bool = False,
        requires_manual_review: bool = False,
        allowed_to_apply: bool = False,
        reason: str = "",
        diff_preview: str | None = None,
        evidence_refs: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_operation.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.target_path = target_path
        self.target_authority = target_authority
        self.requires_policy_approval = requires_policy_approval
        self.requires_manual_review = requires_manual_review
        self.allowed_to_apply = allowed_to_apply
        self.reason = reason
        self.diff_preview = diff_preview
        self.evidence_refs = evidence_refs or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentSyncPlan:
    __slots__ = (
        "schema_version", "schema_id", "plan_id", "created_at",
        "component_id", "source_scan_id", "operations",
        "blocked_operations", "summary", "warnings", "errors",
    )

    def __init__(
        self,
        plan_id: str,
        created_at: str,
        source_scan_id: str,
        operations: list[DocumentSyncOperation] | None = None,
        blocked_operations: list[DocumentSyncOperation] | None = None,
        summary: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_plan.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.plan_id = plan_id
        self.created_at = created_at
        self.component_id = component_id
        self.source_scan_id = source_scan_id
        self.operations = operations or []
        self.blocked_operations = blocked_operations or []
        self.summary = summary or {}
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentSyncResult:
    __slots__ = (
        "schema_version", "schema_id", "result_id", "created_at",
        "plan_id", "status", "applied_operations", "blocked_operations",
        "changed_files", "evidence_refs", "warnings", "errors",
    )

    def __init__(
        self,
        result_id: str,
        created_at: str,
        plan_id: str,
        status: str = CENTRAL_STATUS_NOT_RUN,
        applied_operations: list[str] | None = None,
        blocked_operations: list[str] | None = None,
        changed_files: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_result.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.result_id = result_id
        self.created_at = created_at
        self.plan_id = plan_id
        self.status = status
        self.applied_operations = applied_operations or []
        self.blocked_operations = blocked_operations or []
        self.changed_files = changed_files or []
        self.evidence_refs = evidence_refs or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentLinkRecord:
    __slots__ = (
        "schema_version", "schema_id", "link_id", "source_path",
        "target", "resolved_path", "link_type", "status", "reason",
        "warnings", "errors",
    )

    def __init__(
        self,
        link_id: str,
        source_path: str,
        target: str,
        link_type: str = LINK_TYPE_UNSUPPORTED,
        status: str = CENTRAL_STATUS_NOT_CHECKED,
        resolved_path: str | None = None,
        reason: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_link_validation.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.link_id = link_id
        self.source_path = source_path
        self.target = target
        self.resolved_path = resolved_path
        self.link_type = link_type
        self.status = status
        self.reason = reason
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentStalenessRecord:
    __slots__ = (
        "schema_version", "schema_id", "staleness_id", "document_id",
        "path", "status", "staleness_reason", "related_code_paths",
        "related_schema_paths", "related_test_paths",
        "related_evidence_paths", "warnings", "errors",
    )

    def __init__(
        self,
        staleness_id: str,
        document_id: str,
        path: str,
        status: str = DOC_STATUS_CURRENT,
        staleness_reason: str = "",
        related_code_paths: list[str] | None = None,
        related_schema_paths: list[str] | None = None,
        related_test_paths: list[str] | None = None,
        related_evidence_paths: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_staleness_record.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.staleness_id = staleness_id
        self.document_id = document_id
        self.path = path
        self.status = status
        self.staleness_reason = staleness_reason
        self.related_code_paths = related_code_paths or []
        self.related_schema_paths = related_schema_paths or []
        self.related_test_paths = related_test_paths or []
        self.related_evidence_paths = related_evidence_paths or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncEvidenceManifest:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "validated_commit",
        "created_at", "scan_report_path", "drift_report_path",
        "sync_plan_path", "sync_result_path", "review_report_path",
        "evidence_file_hashes", "commands_run", "warnings", "errors",
    )

    def __init__(
        self,
        created_at: str,
        scan_report_path: str = "",
        drift_report_path: str = "",
        sync_plan_path: str | None = None,
        sync_result_path: str | None = None,
        review_report_path: str | None = None,
        validated_commit: str | None = None,
        evidence_file_hashes: list[dict] | None = None,
        commands_run: list[dict] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_evidence_manifest.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.validated_commit = validated_commit
        self.created_at = created_at
        self.scan_report_path = scan_report_path
        self.drift_report_path = drift_report_path
        self.sync_plan_path = sync_plan_path
        self.sync_result_path = sync_result_path
        self.review_report_path = review_report_path
        self.evidence_file_hashes = evidence_file_hashes or []
        self.commands_run = commands_run or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncReviewReport:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "reviewed_commit",
        "created_at", "scan_status", "drift_status", "link_status",
        "staleness_status", "manual_doc_protection_status",
        "generated_doc_update_status", "evidence_status", "blockers",
        "high_issues", "non_blocking_followups", "final_verdict",
        "warnings", "errors",
    )

    def __init__(
        self,
        created_at: str,
        scan_status: str = CENTRAL_STATUS_NOT_RUN,
        drift_status: str = CENTRAL_STATUS_NOT_RUN,
        link_status: str = CENTRAL_STATUS_NOT_RUN,
        staleness_status: str = CENTRAL_STATUS_NOT_RUN,
        manual_doc_protection_status: str = CENTRAL_STATUS_NOT_RUN,
        generated_doc_update_status: str = CENTRAL_STATUS_NOT_RUN,
        evidence_status: str = CENTRAL_STATUS_NOT_RUN,
        blockers: list[str] | None = None,
        high_issues: list[str] | None = None,
        non_blocking_followups: list[str] | None = None,
        final_verdict: str = CENTRAL_STATUS_NOT_RUN,
        reviewed_commit: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_review_report.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.reviewed_commit = reviewed_commit
        self.created_at = created_at
        self.scan_status = scan_status
        self.drift_status = drift_status
        self.link_status = link_status
        self.staleness_status = staleness_status
        self.manual_doc_protection_status = manual_doc_protection_status
        self.generated_doc_update_status = generated_doc_update_status
        self.evidence_status = evidence_status
        self.blockers = blockers or []
        self.high_issues = high_issues or []
        self.non_blocking_followups = non_blocking_followups or []
        self.final_verdict = final_verdict
        self.warnings = warnings or []
        self.errors = errors or []


class GeneratedDocumentSection:
    __slots__ = (
        "schema_version", "schema_id", "section_id", "target_path",
        "start_marker", "end_marker", "generator_component",
        "source_scan_id", "source_plan_id", "previous_content_sha256",
        "new_content_sha256", "pre_file_sha256", "post_file_sha256",
        "last_updated_at", "status", "warnings", "errors",
    )

    def __init__(
        self,
        section_id: str,
        target_path: str,
        start_marker: str,
        end_marker: str,
        status: str = CENTRAL_STATUS_CURRENT,
        generator_component: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        source_scan_id: str | None = None,
        source_plan_id: str | None = None,
        previous_content_sha256: str | None = None,
        new_content_sha256: str | None = None,
        pre_file_sha256: str | None = None,
        post_file_sha256: str | None = None,
        last_updated_at: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "generated_document_section.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.section_id = section_id
        self.target_path = target_path
        self.start_marker = start_marker
        self.end_marker = end_marker
        self.generator_component = generator_component
        self.source_scan_id = source_scan_id
        self.source_plan_id = source_plan_id
        self.previous_content_sha256 = previous_content_sha256
        self.new_content_sha256 = new_content_sha256
        self.pre_file_sha256 = pre_file_sha256
        self.post_file_sha256 = post_file_sha256
        self.last_updated_at = last_updated_at
        self.status = status
        self.warnings = warnings or []
        self.errors = errors or []


class GeneratedSectionRegistry:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "registry_id",
        "created_at", "sections", "duplicate_section_ids",
        "warnings", "errors",
    )

    def __init__(
        self,
        registry_id: str,
        created_at: str,
        sections: list[dict] | None = None,
        duplicate_section_ids: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "generated_section_registry.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.registry_id = registry_id
        self.created_at = created_at
        self.sections = sections or []
        self.duplicate_section_ids = duplicate_section_ids or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncCommandResult:
    __slots__ = (
        "schema_version", "schema_id", "command_id", "name", "command",
        "started_at", "ended_at", "exit_code", "status", "summary",
        "output_artifact", "output_sha256", "warnings", "errors",
    )

    def __init__(
        self,
        command_id: str,
        name: str,
        command: str,
        started_at: str,
        ended_at: str,
        exit_code: int,
        status: str = CENTRAL_STATUS_PASS,
        summary: str = "",
        output_artifact: str = "",
        output_sha256: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_command_result.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.command_id = command_id
        self.name = name
        self.command = command
        self.started_at = started_at
        self.ended_at = ended_at
        self.exit_code = exit_code
        self.status = status
        self.summary = summary
        self.output_artifact = output_artifact
        self.output_sha256 = output_sha256
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncLockRecord:
    __slots__ = (
        "schema_version", "schema_id", "lock_id", "created_at",
        "owner_id", "mode", "repo_root", "pid", "status",
        "warnings", "errors",
    )

    def __init__(
        self,
        lock_id: str,
        created_at: str,
        mode: str = LOCK_MODE_READ,
        repo_root: str = "",
        status: str = LOCK_STATUS_ACTIVE,
        owner_id: str | None = None,
        pid: int | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_lock.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.lock_id = lock_id
        self.created_at = created_at
        self.owner_id = owner_id
        self.mode = mode
        self.repo_root = repo_root
        self.pid = pid
        self.status = status
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncTraceabilityMatrix:
    __slots__ = (
        "schema_version", "schema_id", "matrix_id", "created_at",
        "component_id", "entries", "summary", "warnings", "errors",
    )

    def __init__(
        self,
        matrix_id: str,
        created_at: str,
        entries: list[dict] | None = None,
        summary: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_traceability_matrix.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.matrix_id = matrix_id
        self.created_at = created_at
        self.component_id = component_id
        self.entries = entries or []
        self.summary = summary or {}
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncDeviation:
    __slots__ = (
        "schema_version", "schema_id", "deviation_id", "created_at",
        "area", "description", "reason", "safety_impact",
        "compensating_control", "accepted_status", "reviewer_decision",
        "warnings", "errors",
    )

    def __init__(
        self,
        deviation_id: str,
        created_at: str,
        area: str,
        description: str,
        reason: str,
        safety_impact: str = "",
        compensating_control: str = "",
        accepted_status: str = DEVIATION_ACCEPTED_STATUS_NOT_APPLICABLE,
        reviewer_decision: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_deviation.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.deviation_id = deviation_id
        self.created_at = created_at
        self.area = area
        self.description = description
        self.reason = reason
        self.safety_impact = safety_impact
        self.compensating_control = compensating_control
        self.accepted_status = accepted_status
        self.reviewer_decision = reviewer_decision
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncControllerResult:
    __slots__ = (
        "schema_version", "schema_id", "result_id", "created_at",
        "mode", "status", "scan_report_path", "drift_report_path",
        "link_report_path", "staleness_report_path", "sync_plan_path",
        "sync_result_path", "evidence_manifest_path",
        "review_report_path", "changed_files", "blocked_operations",
        "warnings", "errors",
    )

    def __init__(
        self,
        result_id: str,
        created_at: str,
        mode: str = DOC_SYNC_MODE_SCAN_ONLY,
        status: str = CENTRAL_STATUS_NOT_RUN,
        scan_report_path: str | None = None,
        drift_report_path: str | None = None,
        link_report_path: str | None = None,
        staleness_report_path: str | None = None,
        sync_plan_path: str | None = None,
        sync_result_path: str | None = None,
        evidence_manifest_path: str | None = None,
        review_report_path: str | None = None,
        changed_files: list[str] | None = None,
        blocked_operations: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_sync_controller_result.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.result_id = result_id
        self.created_at = created_at
        self.mode = mode
        self.status = status
        self.scan_report_path = scan_report_path
        self.drift_report_path = drift_report_path
        self.link_report_path = link_report_path
        self.staleness_report_path = staleness_report_path
        self.sync_plan_path = sync_plan_path
        self.sync_result_path = sync_result_path
        self.evidence_manifest_path = evidence_manifest_path
        self.review_report_path = review_report_path
        self.changed_files = changed_files or []
        self.blocked_operations = blocked_operations or []
        self.warnings = warnings or []
        self.errors = errors or []


class DocumentationSyncCompletionRecord:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "component_name",
        "status", "validated_commit", "validated_at", "review_environment",
        "commands_run", "evidence_manifest_path", "evidence_manifest_sha256",
        "review_report_path", "review_report_sha256",
        "traceability_matrix_path", "traceability_matrix_sha256",
        "deviation_register_path", "deviation_register_sha256",
        "generated_section_registry_path", "generated_section_registry_sha256",
        "completion_record_sha256", "implementation_score",
        "final_decision", "warnings", "errors",
        "files_created_or_changed", "schemas_created_or_changed",
        "tests_created_or_changed", "validated_capabilities",
        "manual_doc_protection_verified", "generated_doc_updates_verified",
        "readme_index_rules_verified", "broken_link_detection_verified",
        "stale_document_detection_verified", "policy_integration_verified",
        "tool_mcp_adapter_integration_ready",
        "deviations_from_contract", "unresolved_risks",
    )

    def __init__(
        self,
        validated_commit: str,
        validated_at: str,
        status: str = "VALIDATED",
        review_environment: dict | None = None,
        commands_run: list[dict] | None = None,
        evidence_manifest_path: str = "",
        evidence_manifest_sha256: str = "",
        review_report_path: str = "",
        review_report_sha256: str = "",
        traceability_matrix_path: str = "",
        traceability_matrix_sha256: str = "",
        deviation_register_path: str = "",
        deviation_register_sha256: str = "",
        generated_section_registry_path: str = "",
        generated_section_registry_sha256: str = "",
        completion_record_sha256: str = "",
        implementation_score: float = 0.0,
        final_decision: str = "NOT_DONE",
        files_created_or_changed: list[str] | None = None,
        schemas_created_or_changed: list[str] | None = None,
        tests_created_or_changed: list[str] | None = None,
        validated_capabilities: list[str] | None = None,
        manual_doc_protection_verified: bool = False,
        generated_doc_updates_verified: bool = False,
        readme_index_rules_verified: bool = False,
        broken_link_detection_verified: bool = False,
        stale_document_detection_verified: bool = False,
        policy_integration_verified: bool = False,
        tool_mcp_adapter_integration_ready: bool = False,
        deviations_from_contract: list[str] | None = None,
        unresolved_risks: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "documentation_completion_record.schema.json",
        component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        component_name: str = "Documentation Synchronization Layer",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.component_name = component_name
        self.status = status
        self.validated_commit = validated_commit
        self.validated_at = validated_at
        self.review_environment = review_environment or {}
        self.commands_run = commands_run or []
        self.evidence_manifest_path = evidence_manifest_path
        self.evidence_manifest_sha256 = evidence_manifest_sha256
        self.review_report_path = review_report_path
        self.review_report_sha256 = review_report_sha256
        self.traceability_matrix_path = traceability_matrix_path
        self.traceability_matrix_sha256 = traceability_matrix_sha256
        self.deviation_register_path = deviation_register_path
        self.deviation_register_sha256 = deviation_register_sha256
        self.generated_section_registry_path = generated_section_registry_path
        self.generated_section_registry_sha256 = generated_section_registry_sha256
        self.completion_record_sha256 = completion_record_sha256
        self.implementation_score = implementation_score
        self.final_decision = final_decision
        self.files_created_or_changed = files_created_or_changed or []
        self.schemas_created_or_changed = schemas_created_or_changed or []
        self.tests_created_or_changed = tests_created_or_changed or []
        self.validated_capabilities = validated_capabilities or []
        self.manual_doc_protection_verified = manual_doc_protection_verified
        self.generated_doc_updates_verified = generated_doc_updates_verified
        self.readme_index_rules_verified = readme_index_rules_verified
        self.broken_link_detection_verified = broken_link_detection_verified
        self.stale_document_detection_verified = stale_document_detection_verified
        self.policy_integration_verified = policy_integration_verified
        self.tool_mcp_adapter_integration_ready = tool_mcp_adapter_integration_ready
        self.deviations_from_contract = deviations_from_contract or []
        self.unresolved_risks = unresolved_risks or []
        self.warnings = warnings or []
        self.errors = errors or []


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond:06d}Z"


def new_id(prefix: str = "ds") -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_bytes(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def to_dict(obj: Any) -> dict:
    result: dict = {}
    for cls in type(obj).__mro__:
        for slot in getattr(cls, "__slots__", ()):
            if hasattr(obj, slot):
                result[slot] = getattr(obj, slot)
    return result


def is_valid_status(value: str) -> bool:
    return value in STATUS_VOCABULARY

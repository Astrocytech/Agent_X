from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentDriftRecord,
    DocumentSyncOperation,
    DocumentSyncPlan,
    DocumentSyncResult,
    DocumentLinkRecord,
    DocumentStalenessRecord,
    DocumentationSyncEvidenceManifest,
    DocumentationSyncReviewReport,
    GeneratedDocumentSection,
    GeneratedSectionRegistry,
    DocumentationSyncCommandResult,
    DocumentationSyncLockRecord,
    DocumentationSyncTraceabilityMatrix,
    DocumentationSyncDeviation,
    DocumentationSyncControllerResult,
    DocumentationSyncCompletionRecord,
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_MANUAL_EDITABLE,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_AUTHORITY_EXTERNAL_REFERENCE,
    DOC_AUTHORITY_UNKNOWN,
    DOC_TYPE_CONTRACT,
    DOC_TYPE_IMPLEMENTATION_SPEC,
    DOC_TYPE_REVIEW_DOD,
    DOC_TYPE_README,
    DOC_TYPE_INDEX,
    DOC_TYPE_SCHEMA,
    DOC_TYPE_TEST,
    DOC_TYPE_REPORT,
    DOC_TYPE_EVIDENCE,
    DOC_TYPE_OTHER,
    DOC_OP_SCAN,
    DOC_OP_PLAN,
    DOC_OP_VALIDATE,
    DOC_OP_UPDATE_GENERATED,
    DOC_OP_UPDATE_INDEX,
    DOC_OP_UPDATE_README_SECTION,
    LINK_TYPE_LOCAL_FILE,
    LINK_TYPE_LOCAL_FILE_WITH_ANCHOR,
    LINK_TYPE_LOCAL_ANCHOR,
    LINK_TYPE_EXTERNAL_HTTP,
    LINK_TYPE_EXTERNAL_MAILTO,
    LINK_TYPE_EXTERNAL_OTHER,
    LINK_TYPE_UNSUPPORTED,
    LINK_TYPE_MALFORMED,
    utc_now_iso,
    new_id,
    sha256_file,
    to_dict,
)

from .doc_controller import (
    run_documentation_sync,
    run_scan_only,
    run_validate_only,
    run_plan_only,
    run_apply_generated,
)

from .doc_scanner import scan_documentation, scan_document_file

from .sync_planner import (
    generate_documentation_sync_plan,
    plan_readme_updates,
    plan_index_updates,
    block_manual_doc_operation,
)

from .drift_detector import (
    detect_documentation_drift,
    compare_contract_spec_review_set,
    compare_schema_index_to_schema_files,
    compare_tests_to_documented_requirements,
)

from .evidence_writer import (
    write_scan_report,
    write_drift_report,
    write_link_report,
    write_staleness_report,
    write_sync_plan,
    write_sync_result,
    write_evidence_manifest,
    write_command_result,
    write_completion_record,
    write_registry_report,
    write_manual_protection_report,
    write_generated_sync_report,
    append_change_history_line,
)

from .doc_sync_apply import apply_documentation_sync_plan, apply_generated_section_update

from .link_validator import extract_markdown_links

from .doc_deviations import create_docs_sync_deviation, validate_docs_sync_deviation, write_docs_sync_deviation_register

from .doc_lock import (
    acquire_docs_sync_lock,
    release_docs_sync_lock,
    read_docs_sync_lock,
    is_lock_stale,
    recover_stale_docs_sync_lock,
)

from .doc_staleness import detect_stale_documents, is_document_stale_against_related_files

from .doc_index import build_document_index, validate_document_index, render_generated_index_section

from .doc_readme import validate_readme_status, render_generated_readme_section

from .doc_registry import (
    classify_document_type,
    classify_document_authority,
    extract_document_id,
    extract_component_id,
    extract_version,
    has_generated_markers,
    is_protected_document,
)

from .doc_traceability import (
    build_docs_sync_traceability_matrix,
    validate_docs_sync_traceability_matrix,
    write_docs_sync_traceability_matrix,
)

from .generated_doc_sync import (
    find_generated_sections,
    validate_generated_sections,
    build_generated_section_registry,
    replace_generated_section_content,
    write_generated_section_registry,
)

from .manual_doc_protector import (
    check_documentation_sync_permission,
    is_manual_doc_update_allowed,
    is_generated_doc_update_allowed,
)

from .source_of_truth import determine_source_of_truth, resolve_source_of_truth_conflict

from .sync_reporter import build_documentation_sync_review_report

from .validate_docs_sync_schemas import validate_all_docs_sync_schemas

from .cli import main

__all__ = [
    "DocumentRecord", "DocumentScanReport", "DocumentDriftRecord",
    "DocumentSyncOperation", "DocumentSyncPlan", "DocumentSyncResult",
    "DocumentLinkRecord", "DocumentStalenessRecord",
    "DocumentationSyncEvidenceManifest", "DocumentationSyncReviewReport",
    "GeneratedDocumentSection", "GeneratedSectionRegistry",
    "DocumentationSyncCommandResult", "DocumentationSyncLockRecord",
    "DocumentationSyncTraceabilityMatrix", "DocumentationSyncDeviation",
    "DocumentationSyncControllerResult", "DocumentationSyncCompletionRecord",
    "DOC_AUTHORITY_MANUAL_GOVERNED", "DOC_AUTHORITY_MANUAL_EDITABLE",
    "DOC_AUTHORITY_GENERATED", "DOC_AUTHORITY_RUNTIME_EVIDENCE",
    "DOC_AUTHORITY_EXTERNAL_REFERENCE", "DOC_AUTHORITY_UNKNOWN",
    "DOC_TYPE_CONTRACT", "DOC_TYPE_IMPLEMENTATION_SPEC", "DOC_TYPE_REVIEW_DOD",
    "DOC_TYPE_README", "DOC_TYPE_INDEX", "DOC_TYPE_SCHEMA", "DOC_TYPE_TEST",
    "DOC_TYPE_REPORT", "DOC_TYPE_EVIDENCE", "DOC_TYPE_OTHER",
    "DOC_OP_SCAN", "DOC_OP_PLAN", "DOC_OP_VALIDATE", "DOC_OP_UPDATE_GENERATED",
    "DOC_OP_UPDATE_INDEX", "DOC_OP_UPDATE_README_SECTION",
    "LINK_TYPE_LOCAL_FILE", "LINK_TYPE_LOCAL_FILE_WITH_ANCHOR",
    "LINK_TYPE_LOCAL_ANCHOR", "LINK_TYPE_EXTERNAL_HTTP",
    "LINK_TYPE_EXTERNAL_MAILTO", "LINK_TYPE_EXTERNAL_OTHER",
    "LINK_TYPE_UNSUPPORTED", "LINK_TYPE_MALFORMED",
    "utc_now_iso", "new_id", "sha256_file", "to_dict",
    "run_documentation_sync", "run_scan_only", "run_validate_only",
    "run_plan_only", "run_apply_generated",
    "scan_documentation", "scan_document_file",
    "generate_documentation_sync_plan", "plan_readme_updates",
    "plan_index_updates", "block_manual_doc_operation",
    "detect_documentation_drift", "compare_contract_spec_review_set",
    "compare_schema_index_to_schema_files", "compare_tests_to_documented_requirements",
    "write_scan_report", "write_drift_report", "write_link_report",
    "write_staleness_report", "write_sync_plan", "write_sync_result",
    "write_evidence_manifest", "write_command_result", "write_completion_record",
    "write_registry_report", "write_manual_protection_report",
    "write_generated_sync_report", "append_change_history_line",
    "apply_documentation_sync_plan", "apply_generated_section_update",
    "extract_markdown_links",
    "create_docs_sync_deviation", "validate_docs_sync_deviation",
    "write_docs_sync_deviation_register",
    "acquire_docs_sync_lock", "release_docs_sync_lock", "read_docs_sync_lock",
    "is_lock_stale", "recover_stale_docs_sync_lock",
    "detect_stale_documents", "is_document_stale_against_related_files",
    "build_document_index", "validate_document_index", "render_generated_index_section",
    "validate_readme_status", "render_generated_readme_section",
    "classify_document_type", "classify_document_authority",
    "extract_document_id", "extract_component_id",
    "extract_version", "has_generated_markers", "is_protected_document",
    "build_docs_sync_traceability_matrix", "validate_docs_sync_traceability_matrix",
    "write_docs_sync_traceability_matrix",
    "find_generated_sections", "validate_generated_sections",
    "build_generated_section_registry", "replace_generated_section_content",
    "write_generated_section_registry",
    "check_documentation_sync_permission", "is_manual_doc_update_allowed",
    "is_generated_doc_update_allowed",
    "determine_source_of_truth", "resolve_source_of_truth_conflict",
    "build_documentation_sync_review_report",
    "validate_all_docs_sync_schemas",
    "main",
]

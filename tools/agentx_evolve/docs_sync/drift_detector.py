from pathlib import Path

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentDriftRecord,
    DOC_TYPE_CONTRACT,
    DOC_TYPE_IMPLEMENTATION_SPEC,
    DOC_TYPE_REVIEW_DOD,
    DOC_TYPE_SCHEMA,
    DOC_TYPE_TEST,
    DOC_TYPE_REPORT,
    DOC_TYPE_EVIDENCE,
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_STATUS_DRIFTED,
    DOC_STATUS_CURRENT,
    CENTRAL_STATUS_DRIFTED,
    DRIFT_TYPE_MISSING_CONTRACT_SPEC_REVIEW,
    DRIFT_TYPE_MISSING_SCHEMA,
    DRIFT_TYPE_MISSING_TEST,
    DRIFT_TYPE_DONE_WITHOUT_EVIDENCE,
    DRIFT_TYPE_MISSING_EVIDENCE,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    new_id,
    utc_now_iso,
    to_dict,
)


def detect_documentation_drift(
    repo_root: Path,
    scan_report: DocumentScanReport,
) -> list[DocumentDriftRecord]:
    records: list[DocumentDriftRecord] = []
    records.extend(compare_contract_spec_review_set(repo_root, scan_report.documents))
    records.extend(compare_schema_index_to_schema_files(repo_root, scan_report.documents))
    records.extend(compare_tests_to_documented_requirements(repo_root, scan_report.documents))
    return records


def compare_contract_spec_review_set(
    repo_root: Path,
    records: list[DocumentRecord],
) -> list[DocumentDriftRecord]:
    drift_records: list[DocumentDriftRecord] = []
    contracts = [r for r in records if r.document_type == DOC_TYPE_CONTRACT]
    specs = [r for r in records if r.document_type == DOC_TYPE_IMPLEMENTATION_SPEC]
    reviews = [r for r in records if r.document_type == DOC_TYPE_REVIEW_DOD]

    if not contracts:
        drift_records.append(
            _make_drift("no-contracts", "CONTRACT", "no contract documents found",
                        {}, {"found_contracts": 0}, SEVERITY_HIGH)
        )
    if not specs:
        drift_records.append(
            _make_drift("no-specs", "IMPLEMENTATION_SPEC",
                        "no implementation spec documents found",
                        {}, {"found_specs": 0}, SEVERITY_HIGH)
        )
    if not reviews:
        drift_records.append(
            _make_drift("no-reviews", "REVIEW_DOD",
                        "no review/DoD documents found",
                        {}, {"found_reviews": 0}, SEVERITY_HIGH)
        )

    for contract in contracts:
        component_id = contract.component_id
        has_spec = any(
            s.component_id == component_id for s in specs if s.component_id
        )
        has_review = any(
            r.component_id == component_id for r in reviews if r.component_id
        )
        if not has_spec:
            drift_records.append(
                _make_drift(
                    f"contract-{contract.document_id}-no-spec",
                    DRIFT_TYPE_MISSING_CONTRACT_SPEC_REVIEW,
                    f"contract {contract.document_id} has no matching spec",
                    {"component_id": component_id, "spec_count": len(specs)},
                    {"component_id": component_id, "spec_count": 0},
                    SEVERITY_HIGH,
                    contract.document_id, contract.path,
                )
            )
        if not has_review:
            drift_records.append(
                _make_drift(
                    f"contract-{contract.document_id}-no-review",
                    DRIFT_TYPE_MISSING_CONTRACT_SPEC_REVIEW,
                    f"contract {contract.document_id} has no matching review/DoD",
                    {"component_id": component_id, "review_count": len(reviews)},
                    {"component_id": component_id, "review_count": 0},
                    SEVERITY_MEDIUM,
                    contract.document_id, contract.path,
                )
            )

    return drift_records


def compare_schema_index_to_schema_files(
    repo_root: Path,
    records: list[DocumentRecord],
) -> list[DocumentDriftRecord]:
    drift_records: list[DocumentDriftRecord] = []
    schema_docs = [r for r in records if r.document_type == DOC_TYPE_SCHEMA]
    spec_docs = [r for r in records if r.document_type == DOC_TYPE_IMPLEMENTATION_SPEC]

    for spec in spec_docs:
        abs_path = repo_root / spec.path
        text = ""
        if abs_path.exists():
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        expected_ids = []
        for line in text.split("\n"):
            if ".schema.json" in line and "schemas/" in line:
                parts = line.strip().split("/")
                for p in parts:
                    if p.endswith(".schema.json"):
                        expected_ids.append(p.replace("`", "").replace('"', ""))
                        break

        for expected_id in expected_ids:
            found = any(expected_id in s.path for s in schema_docs)
            if not found:
                drift_records.append(
                    _make_drift(
                        f"missing-schema-{expected_id}",
                        DRIFT_TYPE_MISSING_SCHEMA,
                        f"expected schema {expected_id} not found",
                        {"schema_id": expected_id},
                        {"found": False},
                        SEVERITY_HIGH,
                        spec.document_id, spec.path,
                    )
                )

    return drift_records


def compare_tests_to_documented_requirements(
    repo_root: Path,
    records: list[DocumentRecord],
) -> list[DocumentDriftRecord]:
    drift_records: list[DocumentDriftRecord] = []
    test_docs = [r for r in records if r.document_type == DOC_TYPE_TEST]
    spec_docs = [r for r in records if r.document_type == DOC_TYPE_IMPLEMENTATION_SPEC]

    for spec in spec_docs:
        abs_path = repo_root / spec.path
        text = ""
        if abs_path.exists():
            text = abs_path.read_text(encoding="utf-8", errors="replace")

        expected_tests = []
        for line in text.split("\n"):
            if "test_" in line and ".py" in line:
                parts = line.strip().split()
                for p in parts:
                    if p.startswith("test_") and p.endswith(".py"):
                        expected_tests.append(p.replace("`", "").replace('"', ""))
                        break

        for expected in expected_tests:
            found = any(expected in t.path for t in test_docs)
            if not found:
                drift_records.append(
                    _make_drift(
                        f"missing-test-{expected}",
                        DRIFT_TYPE_MISSING_TEST,
                        f"expected test {expected} not found",
                        {"test_file": expected},
                        {"found": False},
                        SEVERITY_HIGH,
                        spec.document_id, spec.path,
                    )
                )

    return drift_records


def _make_drift(
    drift_id_suffix: str,
    drift_type: str,
    message: str,
    expected: dict,
    actual: dict,
    severity: str = SEVERITY_MEDIUM,
    document_id: str = "unknown",
    path: str = "unknown",
) -> DocumentDriftRecord:
    now = utc_now_iso()
    return DocumentDriftRecord(
        drift_id=new_id("drift"),
        created_at=now,
        document_id=document_id,
        path=path,
        drift_type=drift_type,
        status=CENTRAL_STATUS_DRIFTED,
        expected=expected,
        actual=actual,
        severity=severity,
        recommended_operation="REVIEW",
    )

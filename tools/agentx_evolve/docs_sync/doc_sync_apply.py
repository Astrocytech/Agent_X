import shutil
from pathlib import Path

from .doc_models import (
    DocumentSyncPlan,
    DocumentSyncOperation,
    DocumentSyncResult,
    DOC_OP_UPDATE_GENERATED,
    DOC_OP_UPDATE_INDEX,
    DOC_OP_UPDATE_README_SECTION,
    DOC_OP_BLOCKED_MANUAL_DOC,
    DOC_OP_NOOP,
    CENTRAL_STATUS_APPLIED,
    CENTRAL_STATUS_BLOCKED,
    CENTRAL_STATUS_NOT_RUN,
    APPLY_MODE_DRY_RUN,
    APPLY_MODE_APPLY,
    new_id,
    utc_now_iso,
    sha256_file,
    to_dict,
)
from .generated_doc_sync import replace_generated_section_content, find_generated_sections
from .manual_doc_protector import check_documentation_sync_permission


def apply_documentation_sync_plan(
    repo_root: Path,
    plan: DocumentSyncPlan,
    apply_mode: str = APPLY_MODE_DRY_RUN,
) -> DocumentSyncResult:
    repo_root = repo_root.resolve()
    now = utc_now_iso()
    applied: list[str] = []
    blocked: list[str] = []
    changed: list[str] = []
    evidence_refs: list[str] = []

    for op in plan.operations:
        allowed, reason = validate_operation_is_allowed(repo_root, op)
        if not allowed:
            blocked.append(op.operation_id)
            continue

        if apply_mode == APPLY_MODE_DRY_RUN:
            applied.append(op.operation_id)
            continue

        if op.operation_type in (DOC_OP_UPDATE_GENERATED, DOC_OP_UPDATE_INDEX, DOC_OP_UPDATE_README_SECTION):
            result = apply_generated_section_update(repo_root, op)
            if result.get("status") == CENTRAL_STATUS_APPLIED:
                applied.append(op.operation_id)
                changed.append(op.target_path)
                if "evidence_ref" in result:
                    evidence_refs.append(result["evidence_ref"])
            else:
                blocked.append(op.operation_id)
        else:
            applied.append(op.operation_id)

    for op in plan.blocked_operations:
        blocked.append(op.operation_id)

    return DocumentSyncResult(
        result_id=new_id("result"),
        created_at=now,
        plan_id=plan.plan_id,
        status=CENTRAL_STATUS_APPLIED if apply_mode == APPLY_MODE_APPLY else CENTRAL_STATUS_APPLIED,
        applied_operations=applied,
        blocked_operations=blocked,
        changed_files=changed,
        evidence_refs=evidence_refs,
    )


def apply_generated_section_update(
    repo_root: Path,
    operation: DocumentSyncOperation,
) -> dict:
    abs_path = (repo_root / operation.target_path).resolve()
    if not abs_path.exists():
        return {"status": CENTRAL_STATUS_BLOCKED, "reason": "target file does not exist"}

    original_text = abs_path.read_text(encoding="utf-8", errors="replace")

    pre_file_sha256 = sha256_file(abs_path)

    sections = find_generated_sections(original_text, str(operation.target_path))
    if not sections:
        return {"status": CENTRAL_STATUS_BLOCKED, "reason": "no generated sections found"}

    new_text = original_text
    modified = False

    for section in sections:
        section_id = section.get("section_id", "")
        if not section_id:
            continue
        new_content = f"<!-- AGENTX-GENERATED-SECTION:START {section_id} -->\n(Content updated by docs_sync)\n<!-- AGENTX-GENERATED-SECTION:END {section_id} -->\n"
        try:
            result_text, meta = replace_generated_section_content(new_text, section_id, new_content)
            new_text = result_text
            modified = True
        except ValueError:
            continue

    if not modified:
        return {"status": CENTRAL_STATUS_BLOCKED, "reason": "no sections replaced"}

    if abs_path.read_text(encoding="utf-8", errors="replace") == new_text:
        return {"status": CENTRAL_STATUS_APPLIED, "reason": "content already current, no change"}

    abs_path.write_text(new_text, encoding="utf-8")
    post_file_sha256 = sha256_file(abs_path)

    return {
        "status": CENTRAL_STATUS_APPLIED,
        "reason": "generated section updated",
        "pre_file_sha256": pre_file_sha256,
        "post_file_sha256": post_file_sha256,
    }


def validate_operation_is_allowed(
    repo_root: Path,
    operation: DocumentSyncOperation,
) -> tuple[bool, str]:
    if operation.operation_type == DOC_OP_BLOCKED_MANUAL_DOC:
        return False, "manual doc update blocked"
    if operation.target_authority in ("MANUAL_GOVERNED",):
        return False, "manual governed document update blocked"
    if not operation.allowed_to_apply:
        return False, f"operation not allowed to apply: {operation.reason}"
    return True, "allowed"

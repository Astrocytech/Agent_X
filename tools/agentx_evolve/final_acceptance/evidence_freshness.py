import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceEvidenceManifest
from .artifact_writer import write_json_artifact


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _git_merge_base_is_ancestor(repo_root: Path, ancestor: str, commit: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, commit],
            capture_output=True, text=True, cwd=repo_root, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _git_changed_files_since(repo_root: Path, since_commit: str, reviewed_commit: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{since_commit}..{reviewed_commit}"],
            capture_output=True, text=True, cwd=repo_root, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().split("\n")]
        return []
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _evidence_commit_for_layer(
    evidence_manifest: FinalAcceptanceEvidenceManifest, layer_id: str
) -> str | None:
    for item in evidence_manifest.items:
        if item.layer_id == layer_id and item.reviewed_commit_in_artifact:
            return item.reviewed_commit_in_artifact
    reviewed = evidence_manifest.reviewed_commit
    if reviewed:
        return reviewed
    return None


def build_evidence_freshness_report(
    repo_root: Path,
    evidence_manifest: FinalAcceptanceEvidenceManifest,
    reviewed_commit: str | None,
    acceptance_mode: str,
    required_layer_ids: list[str],
) -> dict[str, Any]:
    if not reviewed_commit:
        return {
            "schema_version": "1.0",
            "schema_id": "final_acceptance_evidence_freshness_report.schema.json",
            "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
            "reviewed_commit": None,
            "created_at": _make_timestamp(),
            "report_status": "NOT_CHECKED",
            "layers": [],
            "warnings": [],
            "errors": [],
        }

    layer_reports: list[dict[str, Any]] = []
    seen_layer_ids: set[str] = set()

    for item in evidence_manifest.items:
        lid = item.layer_id
        if lid in seen_layer_ids:
            continue
        seen_layer_ids.add(lid)

        layer_evidence_commit = item.reviewed_commit_in_artifact
        freshness_status = "NOT_CHECKED"
        commit_relation = "unknown"
        changed_files: list[str] = []
        affected = False
        reason = ""

        if layer_evidence_commit == reviewed_commit:
            freshness_status = "FRESH"
            commit_relation = "exact_match"
            reason = f"Layer evidence commit {layer_evidence_commit} matches reviewed commit {reviewed_commit}"
        elif layer_evidence_commit:
            is_ancestor = _git_merge_base_is_ancestor(repo_root, layer_evidence_commit, reviewed_commit)
            if is_ancestor:
                commit_relation = "ancestor"
                changed_files = _git_changed_files_since(repo_root, layer_evidence_commit, reviewed_commit)
                affected = any(
                    f.startswith(lid.lower().replace("_", "/")) or lid.lower().replace("_", "/") in f
                    for f in changed_files
                ) if changed_files else False
                if affected:
                    freshness_status = "STALE_REQUIRES_REVALIDATION"
                    reason = (
                        f"Layer evidence commit {layer_evidence_commit} is ancestor of {reviewed_commit} "
                        f"and {len(changed_files)} file(s) changed that affect this layer"
                    )
                else:
                    freshness_status = "STALE_BUT_UNAFFECTED"
                    reason = (
                        f"Layer evidence commit {layer_evidence_commit} is ancestor of {reviewed_commit} "
                        f"but no changes affect this layer"
                    )
            else:
                freshness_status = "STALE_REQUIRES_REVALIDATION"
                commit_relation = "not_ancestor"
                reason = f"Layer evidence commit {layer_evidence_commit} is not an ancestor of reviewed commit {reviewed_commit}"
        else:
            freshness_status = "STALE_REQUIRES_REVALIDATION"
            reason = "No layer evidence commit found"

        layer_reports.append({
            "layer_id": lid,
            "layer_name": lid,
            "layer_evidence_commit": layer_evidence_commit,
            "reviewed_commit": reviewed_commit,
            "commit_relation": commit_relation,
            "changed_files_since_layer_validation": changed_files,
            "affected_by_changes": affected,
            "freshness_status": freshness_status,
            "reason": reason,
        })

    for lid in required_layer_ids:
        if lid not in seen_layer_ids:
            layer_reports.append({
                "layer_id": lid,
                "layer_name": lid,
                "layer_evidence_commit": None,
                "reviewed_commit": reviewed_commit,
                "commit_relation": "unknown",
                "changed_files_since_layer_validation": [],
                "affected_by_changes": False,
                "freshness_status": "NOT_CHECKED",
                "reason": "No evidence items found for required layer",
            })

    stale_required = [
        r for r in layer_reports
        if r["freshness_status"] == "STALE_REQUIRES_REVALIDATION"
        and lid in required_layer_ids
    ]
    if stale_required:
        report_status = "FAIL"
    elif any(r["freshness_status"] == "STALE_REQUIRES_REVALIDATION" for r in layer_reports):
        report_status = "PARTIAL"
    elif any(r["freshness_status"] in ("NOT_CHECKED",) for r in layer_reports):
        report_status = "PARTIAL"
    else:
        report_status = "PASS"

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_evidence_freshness_report.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "reviewed_commit": reviewed_commit,
        "created_at": _make_timestamp(),
        "acceptance_mode": acceptance_mode,
        "report_status": report_status,
        "layers": layer_reports,
        "warnings": [],
        "errors": [],
    }


def write_evidence_freshness_report(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_evidence_freshness_report.json", data)

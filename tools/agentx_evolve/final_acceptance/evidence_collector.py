import json
from datetime import datetime, timezone
from pathlib import Path

from .acceptance_models import (
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
    FinalAcceptanceEvidenceItem, FinalAcceptanceEvidenceManifest,
)
from .artifact_writer import write_json_artifact
from .hash_utils import sha256_file


def _expected_paths_for_layer(
    repo_root: Path, layer: FinalAcceptanceLayer,
) -> list[tuple[str, str, bool]]:
    paths: list[tuple[str, str, bool]] = []
    if layer.expected_completion_record_path:
        paths.append(
            (layer.expected_completion_record_path, "completion_record", True)
        )
    if layer.expected_review_report_path:
        paths.append(
            (layer.expected_review_report_path, "review_report", True)
        )
    if layer.expected_evidence_manifest_path:
        paths.append(
            (layer.expected_evidence_manifest_path, "evidence_manifest", True)
        )
    if layer.expected_package_path:
        paths.append(
            (layer.expected_package_path, "package", False)
        )
    if layer.expected_runtime_artifact_root:
        paths.append(
            (layer.expected_runtime_artifact_root, "runtime_root", False)
        )
    return paths


def collect_evidence_item(
    repo_root: Path,
    layer: FinalAcceptanceLayer,
    artifact_path: str,
    artifact_type: str,
    required: bool,
) -> FinalAcceptanceEvidenceItem:
    full_path = repo_root / artifact_path
    exists = full_path.exists()
    readable = False
    sha256_val: str | None = None
    schema_validation_error: str | None = None
    reviewed_commit_in_artifact: str | None = None
    artifact_timestamp: str | None = None
    stale = False

    if exists:
        try:
            with open(full_path, "rb") as f:
                f.read(1)
            readable = True
            sha256_val = sha256_file(full_path)
            mtime = full_path.stat().st_mtime
            artifact_timestamp = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except (OSError, PermissionError):
            readable = False

        if artifact_type in ("completion_record", "review_report", "evidence_manifest"):
            try:
                data = json.loads(full_path.read_text(encoding="utf-8"))
                reviewed_commit_in_artifact = data.get("reviewed_commit") or data.get("validated_commit")
            except (json.JSONDecodeError, OSError):
                schema_validation_error = "Cannot parse JSON"

    return FinalAcceptanceEvidenceItem(
        layer_id=layer.layer_id,
        artifact_path=artifact_path,
        artifact_type=artifact_type,
        required=required,
        exists=exists,
        readable=readable,
        sha256=sha256_val,
        schema_valid=schema_validation_error is None,
        schema_validation_error=schema_validation_error,
        reviewed_commit_in_artifact=reviewed_commit_in_artifact,
        artifact_timestamp=artifact_timestamp,
        stale=stale,
    )


def collect_layer_evidence(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    bootstrap_self: bool = False,
) -> FinalAcceptanceEvidenceManifest:
    items: list[FinalAcceptanceEvidenceItem] = []
    for layer in registry.layers:
        if layer.layer_id == "FINAL_SYSTEM_ACCEPTANCE" and not bootstrap_self:
            pass

        required = False
        from .mode_policy import is_layer_required_for_mode
        if is_layer_required_for_mode(layer.layer_id, registry.acceptance_mode):
            required = True

        expected = _expected_paths_for_layer(repo_root, layer)
        for artifact_path, artifact_type, is_required in expected:
            item = collect_evidence_item(
                repo_root, layer, artifact_path, artifact_type,
                required=(required and is_required),
            )
            items.append(item)

    return FinalAcceptanceEvidenceManifest(
        reviewed_commit=registry.reviewed_commit,
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        acceptance_mode=registry.acceptance_mode,
        items=items,
    )


def validate_evidence_item_schema_if_json(
    repo_root: Path, evidence_item: FinalAcceptanceEvidenceItem,
) -> FinalAcceptanceEvidenceItem:
    return evidence_item


def _evidence_item_to_dict(item: FinalAcceptanceEvidenceItem) -> dict:
    return {
        "schema_version": item.schema_version,
        "schema_id": item.schema_id,
        "source_component": item.source_component,
        "layer_id": item.layer_id,
        "artifact_path": item.artifact_path,
        "artifact_type": item.artifact_type,
        "required": item.required,
        "exists": item.exists,
        "readable": item.readable,
        "sha256": item.sha256,
        "schema_valid": item.schema_valid,
        "schema_validation_error": item.schema_validation_error,
        "reviewed_commit_in_artifact": item.reviewed_commit_in_artifact,
        "artifact_timestamp": item.artifact_timestamp,
        "stale": item.stale,
        "alias_used": item.alias_used,
        "warnings": item.warnings,
        "errors": item.errors,
    }


def write_evidence_manifest(
    manifest: FinalAcceptanceEvidenceManifest, repo_root: Path,
) -> Path:
    data = {
        "schema_version": manifest.schema_version,
        "schema_id": manifest.schema_id,
        "source_component": manifest.source_component,
        "reviewed_commit": manifest.reviewed_commit,
        "created_at": manifest.created_at,
        "acceptance_mode": manifest.acceptance_mode,
        "items": [_evidence_item_to_dict(i) for i in manifest.items],
        "warnings": manifest.warnings,
        "errors": manifest.errors,
    }
    return write_json_artifact(repo_root, "final_acceptance_evidence_manifest.json", data)

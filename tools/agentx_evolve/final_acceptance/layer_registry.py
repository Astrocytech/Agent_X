from pathlib import Path

from .acceptance_models import (
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
    MODE_SOURCE_ONLY_ACCEPTANCE,
)
from .artifact_writer import write_json_artifact
from .layer_catalog import build_canonical_layer_catalog
from .mode_policy import is_layer_required_for_mode, is_deferral_allowed_for_mode


def build_final_acceptance_layer_registry(
    repo_root: Path,
    reviewed_commit: str | None = None,
    reviewed_branch: str | None = None,
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE,
    bootstrap_self: bool = False,
) -> FinalAcceptanceLayerRegistry:
    from datetime import datetime, timezone

    catalog = build_canonical_layer_catalog()
    if bootstrap_self:
        pass

    registry = FinalAcceptanceLayerRegistry(
        reviewed_commit=reviewed_commit,
        reviewed_branch=reviewed_branch,
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        acceptance_mode=acceptance_mode,
        bootstrap_self=bootstrap_self,
        layers=catalog,
    )
    return registry


def get_layer_by_id(
    registry: FinalAcceptanceLayerRegistry, layer_id: str
) -> FinalAcceptanceLayer | None:
    for layer in registry.layers:
        if layer.layer_id == layer_id:
            return layer
    return None


def list_required_layers(
    registry: FinalAcceptanceLayerRegistry,
) -> list[FinalAcceptanceLayer]:
    return [
        l for l in registry.layers
        if is_layer_required_for_mode(l.layer_id, registry.acceptance_mode)
    ]


def list_safely_deferred_layers(
    registry: FinalAcceptanceLayerRegistry,
) -> list[FinalAcceptanceLayer]:
    return [
        l for l in registry.layers
        if not is_layer_required_for_mode(l.layer_id, registry.acceptance_mode)
        and is_deferral_allowed_for_mode(l.layer_id, registry.acceptance_mode)
    ]


def _layer_to_dict(layer: FinalAcceptanceLayer) -> dict:
    return {
        "schema_version": layer.schema_version,
        "schema_id": layer.schema_id,
        "source_component": layer.source_component,
        "layer_id": layer.layer_id,
        "layer_name": layer.layer_name,
        "roadmap_number": layer.roadmap_number,
        "required_for_acceptance": layer.required_for_acceptance,
        "safe_deferral_allowed": layer.safe_deferral_allowed,
        "expected_package_path": layer.expected_package_path,
        "expected_runtime_artifact_root": layer.expected_runtime_artifact_root,
        "expected_completion_record_path": layer.expected_completion_record_path,
        "expected_review_report_path": layer.expected_review_report_path,
        "expected_evidence_manifest_path": layer.expected_evidence_manifest_path,
        "acceptance_modes_required": layer.acceptance_modes_required,
        "deferral_modes_allowed": layer.deferral_modes_allowed,
        "expected_evidence_aliases": layer.expected_evidence_aliases,
        "stale_after_days": layer.stale_after_days,
        "bootstrap_self_layer": layer.bootstrap_self_layer,
        "warnings": layer.warnings,
        "errors": layer.errors,
    }


def write_layer_registry(
    registry: FinalAcceptanceLayerRegistry, repo_root: Path
) -> Path:
    data = {
        "schema_version": registry.schema_version,
        "schema_id": registry.schema_id,
        "source_component": registry.source_component,
        "reviewed_commit": registry.reviewed_commit,
        "reviewed_branch": registry.reviewed_branch,
        "created_at": registry.created_at,
        "acceptance_mode": registry.acceptance_mode,
        "bootstrap_self": registry.bootstrap_self,
        "layers": [_layer_to_dict(l) for l in registry.layers],
        "warnings": registry.warnings,
        "errors": registry.errors,
    }
    return write_json_artifact(repo_root, "final_acceptance_layer_registry.json", data)

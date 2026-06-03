from __future__ import annotations
from pathlib import Path
from typing import Any
from .runtime_models import (
    LocalModelInventory, LocalModelAvailabilityDecision,
    AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING, AVAILABILITY_BLOCKED,
    utc_now_iso, new_id,
)


def check_model_availability(
    model_id: str,
    inventory: LocalModelInventory,
    repository: dict,
) -> LocalModelAvailabilityDecision:
    repo_hash = repository.get("repository_hash", "")
    decision = LocalModelAvailabilityDecision(
        decision_id=new_id("avail"),
        timestamp=utc_now_iso(),
        model_id=model_id,
        availability=AVAILABILITY_BLOCKED,
        profile_repository_hash=repo_hash,
        failure_class=None,
        reason="",
    )
    record = _find_inventory_record(inventory, model_id)
    if record is None:
        decision.availability = AVAILABILITY_MISSING
        decision.reason = f"Model {model_id} not found in inventory"
        decision.failure_class = "LOCAL_MODEL_NOT_FOUND"
        return decision

    model_path_str = record.get("model_path", "")
    model_path = Path(model_path_str) if model_path_str else None

    approved_roots = [Path(r) for r in inventory.approved_model_roots]
    if model_path and approved_roots:
        path_allowed = _is_path_allowed(model_path, approved_roots)
        decision.path_allowed = path_allowed
        if not path_allowed:
            decision.availability = AVAILABILITY_BLOCKED
            decision.reason = f"Model path {model_path} outside approved roots"
            decision.failure_class = "LOCAL_MODEL_PATH_OUTSIDE_BOUNDARY"
            decision.model_path = str(model_path)
            return decision

    if model_path:
        decision.model_path = str(model_path)
        decision.file_present = model_path.exists()
        if not decision.file_present:
            decision.availability = AVAILABILITY_MISSING
            decision.reason = f"Model file not found at {model_path}"
            decision.failure_class = "LOCAL_MODEL_PATH_MISSING"
            return decision

    if record.get("enabled") is False:
        decision.availability = AVAILABILITY_BLOCKED
        decision.reason = f"Model {model_id} is disabled in inventory"
        decision.failure_class = "LOCAL_MODEL_DISABLED"
        return decision

    decision.availability = AVAILABILITY_AVAILABLE
    decision.reason = f"Model {model_id} is available"
    return decision


def check_model_path_allowed(path: Path, approved_model_roots: list[Path]) -> dict:
    resolved = path.resolve()
    for root in approved_model_roots:
        try:
            resolved.relative_to(root.resolve())
            return {"allowed": True, "resolved_path": str(resolved)}
        except ValueError:
            continue
    return {"allowed": False, "resolved_path": str(resolved)}


def check_model_file_present(path: Path) -> dict:
    return {"present": path.exists(), "path": str(path), "size_bytes": path.stat().st_size if path.exists() else 0}


def _find_inventory_record(inventory: LocalModelInventory, model_id: str) -> dict | None:
    for m in inventory.models:
        if m.get("model_id") == model_id:
            return m
    return None


def _is_path_allowed(path: Path, approved_roots: list[Path]) -> bool:
    resolved = path.resolve()
    for root in approved_roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False

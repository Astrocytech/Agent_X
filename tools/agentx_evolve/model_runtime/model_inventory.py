from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .runtime_models import LocalModelInventory


def load_model_inventory(path: Path) -> LocalModelInventory:
    with open(path) as f:
        data = json.load(f)
    return LocalModelInventory(
        inventory_id=data.get("inventory_id", ""),
        created_at=data.get("created_at", ""),
        approved_model_roots=data.get("approved_model_roots", []),
        models=data.get("models", []),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def validate_model_inventory(inventory: LocalModelInventory, model_profiles: list) -> dict:
    profile_ids = {p.model_id for p in model_profiles}
    issues: list[str] = []
    for m in inventory.models:
        mid = m.get("model_id", "")
        if mid and mid not in profile_ids:
            issues.append(f"Inventory references unknown model profile: {mid}")
    return {"valid": len(issues) == 0, "issues": issues}


def get_inventory_record(inventory: LocalModelInventory, model_id: str) -> dict | None:
    for m in inventory.models:
        if m.get("model_id") == model_id:
            return m
    return None


def list_inventory_models(inventory: LocalModelInventory) -> list[dict]:
    return list(inventory.models)

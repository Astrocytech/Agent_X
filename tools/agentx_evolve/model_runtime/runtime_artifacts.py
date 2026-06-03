from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from .runtime_models import (
    LocalModelInventory, LocalHardwareProfile,
    LocalModelAvailabilityDecision, LocalRuntimeCompatibilityDecision,
    LocalModelEligibilityDecision,
    utc_now_iso,
)


RUNTIME_ROOT = Path(".agentx-init") / "model_runtime"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: dict) -> None:
    _ensure_dir(path)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.rename(path)


def _append_jsonl(path: Path, data: dict) -> None:
    _ensure_dir(path)
    with open(path, "a") as f:
        f.write(json.dumps(data, default=str) + "\n")


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def write_profile_snapshot(repository: dict, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "model_runtime_profile_snapshot.json"
    _atomic_write(path, repository)
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_inventory_snapshot(inventory: LocalModelInventory, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "model_inventory_snapshot.json"
    _atomic_write(path, inventory.__dict__ if hasattr(inventory, "__dict__") else {})
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_hardware_snapshot(hardware_profile: LocalHardwareProfile, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "hardware_profile_snapshot.json"
    _atomic_write(path, hardware_profile.__dict__ if hasattr(hardware_profile, "__dict__") else {})
    return {"path": str(path), "sha256": calculate_sha256(path)}


def append_runtime_compatibility(decision: LocalRuntimeCompatibilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "runtime_compatibility_history.jsonl"
    _append_jsonl(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path)}


def append_model_availability(decision: LocalModelAvailabilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "model_availability_history.jsonl"
    _append_jsonl(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path)}


def append_model_eligibility(decision: LocalModelEligibilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "model_eligibility_history.jsonl"
    _append_jsonl(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path)}


def write_latest_runtime_compatibility(decision: LocalRuntimeCompatibilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "latest_runtime_compatibility_decision.json"
    _atomic_write(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_latest_model_availability(decision: LocalModelAvailabilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "latest_model_availability_decision.json"
    _atomic_write(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_latest_model_eligibility(decision: LocalModelEligibilityDecision, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "latest_model_eligibility_decision.json"
    _atomic_write(path, decision.__dict__ if hasattr(decision, "__dict__") else {})
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_evidence_manifest(manifest: dict, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "local_model_runtime_evidence_manifest.json"
    _atomic_write(path, manifest)
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_review_report(report: dict, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "local_model_runtime_review_report.json"
    _atomic_write(path, report)
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_runtime_artifact(name: str, data: dict, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / name
    _atomic_write(path, data)
    return {"path": str(path), "sha256": calculate_sha256(path)}


def write_completion_record(record: dict, repo_root: Path) -> dict:
    path = repo_root / RUNTIME_ROOT / "local_model_runtime_completion_record.json"
    _atomic_write(path, record)
    return {"path": str(path), "sha256": calculate_sha256(path)}

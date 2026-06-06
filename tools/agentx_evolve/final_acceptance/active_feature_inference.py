from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceLayer


def _module_exists(repo_root: Path, module_path: str) -> bool:
    full = repo_root / module_path
    if full.suffix == ".py":
        return full.exists()
    return (full / "__init__.py").exists() or full.exists()


def _has_runtime_entrypoints(repo_root: Path, subdirs: list[str]) -> bool:
    for sd in subdirs:
        candidates = [
            repo_root / sd,
            repo_root / "tools" / "agentx_evolve" / sd,
            repo_root / "tools" / sd,
        ]
        for c in candidates:
            if c.exists():
                return True
    return False


_ACTIVITY_CHECKS: dict[str, Any] = {
    "GOVERNED_PATCH_EXECUTION": {
        "module": "tools/agentx_evolve/patch_execution.py",
        "subdirs": ["tools/agentx_evolve/patch"],
    },
    "MODEL_ADAPTER": {
        "module": "tools/agentx_evolve/model_adapter.py",
        "subdirs": ["tools/agentx_evolve/model"],
    },
    "LOCAL_MODEL_RUNTIME_PROFILE": {
        "module": "tools/agentx_evolve/local_model_runtime",
        "subdirs": ["tools/agentx_evolve/local"],
    },
    "CONTEXT_BUILDER_TASK_PACKER": {
        "module": "tools/agentx_evolve/context_builder.py",
        "subdirs": ["tools/agentx_evolve/context"],
    },
    "PROMPT_CONTRACT_VERSIONING": {
        "module": "tools/agentx_evolve/prompt_contract.py",
        "subdirs": ["tools/agentx_evolve/prompts"],
    },
    "LLM_IMPLEMENTATION_WORKER": {
        "module": "tools/agentx_evolve/llm_worker.py",
        "subdirs": ["tools/agentx_evolve/llm"],
    },
    "SELF_EVOLUTION_ORCHESTRATOR": {
        "module": "tools/agentx_evolve/self_evolution_orchestrator",
        "subdirs": ["tools/agentx_evolve/self_evolution"],
    },
    "HUMAN_REVIEW_APPROVAL": {
        "module": "tools/agentx_evolve/human_review.py",
        "subdirs": ["tools/agentx_evolve/human_review"],
    },
    "PROMOTION_RELEASE_GATE": {
        "module": "tools/agentx_evolve/promotion_release.py",
        "subdirs": ["tools/agentx_evolve/promotion"],
    },
    "GIT_INTEGRATION": {
        "module": "tools/agentx_evolve/git_integration.py",
        "subdirs": ["tools/agentx_evolve/git"],
    },
    "LONG_TERM_LEARNING": {
        "module": "tools/agentx_evolve/long_term_learning.py",
        "subdirs": ["tools/agentx_evolve/learning"],
    },
    "DOCUMENTATION_SYNC": {
        "module": "tools/agentx_evolve/documentation_sync.py",
        "subdirs": ["tools/agentx_evolve/docs"],
    },
    "TASK_QUEUE_SESSION_SCHEDULER": {
        "module": "tools/agentx_evolve/task_queue.py",
        "subdirs": ["tools/agentx_evolve/task_queue"],
    },
    "MONITORING_OBSERVABILITY": {
        "module": "tools/agentx_evolve/monitoring.py",
        "subdirs": ["tools/agentx_evolve/monitoring"],
    },
    "PACKAGING_DISTRIBUTION": {
        "module": "tools/agentx_evolve/packaging.py",
        "subdirs": ["tools/agentx_evolve/packaging"],
    },
    "BACKUP_DISASTER_RECOVERY": {
        "module": "tools/agentx_evolve/backup_recovery.py",
        "subdirs": ["tools/agentx_evolve/backup"],
    },
}


def is_feature_active(repo_root: Path, layer_id: str) -> bool:
    check = _ACTIVITY_CHECKS.get(layer_id)
    if not check:
        return True
    module = check.get("module")
    if module and _module_exists(repo_root, module):
        return True
    subdirs = check.get("subdirs", [])
    if subdirs and _has_runtime_entrypoints(repo_root, subdirs):
        return True
    return False


def infer_active_features(
    repo_root: Path,
    layers: list[FinalAcceptanceLayer],
) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for layer in layers:
        if not layer.required_for_acceptance:
            active = is_feature_active(repo_root, layer.layer_id)
            result[layer.layer_id] = active
    return result

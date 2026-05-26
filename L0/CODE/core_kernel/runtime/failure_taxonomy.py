"""Failure taxonomy — categorizes runtime failures for evidence collection and recovery.

Each category defines whether retry is allowed, the fallback phase,
user-facing status, and whether memory lessons and checkpoints are created.
Connected to seed_runtime._handle_failure for evidence generation.
"""

from __future__ import annotations

from typing import Any


FAILURE_CATEGORIES: dict[str, dict[str, Any]] = {
    "input_failure": {
        "retry_allowed": False,
        "fallback_phase": "input",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": False,
    },
    "profile_failure": {
        "retry_allowed": True,
        "fallback_phase": "profile",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "planning_failure": {
        "retry_allowed": True,
        "fallback_phase": "planning",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "governance_denial": {
        "retry_allowed": True,
        "fallback_phase": "governance",
        "user_visible_status": "blocked",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": False,
    },
    "tool_unavailable": {
        "retry_allowed": True,
        "fallback_phase": "planning",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": False,
    },
    "tool_execution_failure": {
        "retry_allowed": True,
        "fallback_phase": "execution",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": False,
    },
    "memory_failure": {
        "retry_allowed": True,
        "fallback_phase": "memory",
        "user_visible_status": "degraded",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "evaluation_failure": {
        "retry_allowed": True,
        "fallback_phase": "evaluation",
        "user_visible_status": "degraded",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "trace_failure": {
        "retry_allowed": False,
        "fallback_phase": "trace",
        "user_visible_status": "failed",
        "memory_lesson_created": False,
        "checkpoint_required": False,
        "promotion_blocker": True,
    },
    "checkpoint_failure": {
        "retry_allowed": False,
        "fallback_phase": "checkpoint",
        "user_visible_status": "failed",
        "memory_lesson_created": False,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "seed_boundary_violation": {
        "retry_allowed": False,
        "fallback_phase": "",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": True,
        "promotion_blocker": True,
    },
    "evolution_candidate_failure": {
        "retry_allowed": True,
        "fallback_phase": "evolution_candidate",
        "user_visible_status": "failed",
        "memory_lesson_created": True,
        "checkpoint_required": False,
        "promotion_blocker": True,
    },
}

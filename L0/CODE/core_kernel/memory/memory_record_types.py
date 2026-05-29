MEMORY_RECORD_TYPES = frozenset({
    "turn_observation",
    "tool_result",
    "governance_denial",
    "approval_pending",
    "evaluation_result",
    "lesson",
})

RECALL_SCOPES = frozenset({
    "session_only",
    "profile_local",
    "seed_global",
    "do_not_recall",
})

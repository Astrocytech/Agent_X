from __future__ import annotations

"""Error types and exception hierarchy for the agent kernel."""

__all__ = [
    "ApprovalRequiredError",
    "CheckpointError",
    "InvalidCodingProviderError",
    "KernelError",
    "MemoryWriteError",
    "PolicyDeniedError",
    "PolicyViolationError",
    "ProfileError",
    "ProfileNotFoundError",
    "ToolCallError",
    "ToolNotFoundError",
    "ValidationError",
]


class KernelError(Exception):
    def __init__(self, message: str, run_id: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.run_id = run_id
        self.details = details or {}

    def __str__(self) -> str:
        if self.run_id:
            return f"[run:{self.run_id}] {self.message}"
        return self.message


class ValidationError(KernelError):
    pass


class PolicyViolationError(KernelError):
    pass


class PolicyDeniedError(KernelError):
    pass


class ApprovalRequiredError(KernelError):
    pass


class CheckpointError(KernelError):
    pass


class InvalidCodingProviderError(KernelError):
    """Raised when an LLM provider does not implement CodingLLMProvider protocol.

    The evolution loop requires providers to implement
    ``generate_patch_candidate()`` — legacy ``LLMProvider`` (``.generate()``
    only) is no longer accepted.
    """

    pass


class ProfileNotFoundError(KernelError):
    pass


class ProfileError(KernelError):
    pass


class ToolNotFoundError(KernelError):
    pass


class ToolCallError(KernelError):
    pass


class MemoryWriteError(KernelError):
    pass


class KernelInvariantViolation(KernelError):
    """Raised when a kernel invariant is violated.

    Used in Phase 1+ to prevent plan-text-as-answer (symbolic
    fallback) and other invariant breaks that degrade seed quality
    below 9.0.
    """

    pass

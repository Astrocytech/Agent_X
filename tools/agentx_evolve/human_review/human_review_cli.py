from __future__ import annotations

import warnings

from agentx_evolve.human_review.review_cli import main

warnings.warn(
    "Import from 'human_review.human_review_cli' is deprecated; use 'human_review.review_cli' instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "main",
]

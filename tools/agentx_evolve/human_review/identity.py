from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ReviewerIdentity",
    "authenticate",
    "authorize",
]


@dataclass
class ReviewerIdentity:
    name: str = ""
    role: str = ""
    certification: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def authenticate(token: str) -> ReviewerIdentity | None:
    if not token:
        return None
    return ReviewerIdentity(name="authenticated-user", role="reviewer", certification="default")


def authorize(identity: ReviewerIdentity, action: str) -> bool:
    if not identity.name:
        return False
    if identity.role == "admin":
        return True
    if identity.role == "reviewer" and action in ("approve", "reject", "defer"):
        return True
    return False

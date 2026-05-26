from __future__ import annotations

"""Irreversible action policy."""


from enum import Enum  # noqa: E402

__all__ = ["IrreversibilityLevel", "IrreversibleActionPolicy"]


class IrreversibilityLevel(Enum):
    REVERSIBLE = "reversible"
    HARD_TO_REVERSE = "hard_to_reverse"
    IRREVERSIBLE = "irreversible"


class IrreversibleActionPolicy:
    IRREVERSIBLE_ACTIONS = {
        "file_delete": IrreversibilityLevel.IRREVERSIBLE,
        "database_drop": IrreversibilityLevel.IRREVERSIBLE,
        "git_force_push": IrreversibilityLevel.IRREVERSIBLE,
        "git_reset_hard": IrreversibilityLevel.HARD_TO_REVERSE,
        "file_write": IrreversibilityLevel.HARD_TO_REVERSE,
        "shell_execute": IrreversibilityLevel.HARD_TO_REVERSE,
    }

    def classify(self, action_type: str) -> IrreversibilityLevel:
        return self.IRREVERSIBLE_ACTIONS.get(action_type, IrreversibilityLevel.REVERSIBLE)

    def requires_approval(self, action_type: str) -> bool:
        return self.classify(action_type) == IrreversibilityLevel.IRREVERSIBLE

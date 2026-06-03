from __future__ import annotations

CBC_PASS = "PASS"
CBC_FAIL = "FAIL"


class ContextBuilderCheck:
    def __init__(self, status: str = CBC_PASS, reason: str = ""):
        self.status = status
        self.reason = reason

    def passed(self) -> bool:
        return self.status == CBC_PASS

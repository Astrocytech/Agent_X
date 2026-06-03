from __future__ import annotations

RP_ALLOW = "ALLOW"
RP_BLOCK = "BLOCK"


class RuntimePolicy:
    def __init__(self, policy_id: str = "", mode: str = RP_ALLOW):
        self.policy_id = policy_id
        self.mode = mode

    def evaluate(self, context: dict) -> str:
        return self.mode


PC_COMPATIBLE = "COMPATIBLE"
PC_INCOMPATIBLE = "INCOMPATIBLE"


class PromptCompatibility:
    def __init__(self, status: str = PC_COMPATIBLE, reason: str = ""):
        self.status = status
        self.reason = reason

    def is_compatible(self) -> bool:
        return self.status == PC_COMPATIBLE


TC_SUPPORTED = "SUPPORTED"
TC_UNSUPPORTED = "UNSUPPORTED"


class ToolCompatibility:
    def __init__(self, status: str = TC_SUPPORTED, reason: str = ""):
        self.status = status
        self.reason = reason

    def is_supported(self) -> bool:
        return self.status == TC_SUPPORTED

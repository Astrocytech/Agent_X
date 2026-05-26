import os
import json
from pathlib import Path
from pydantic import BaseModel
from agentx_initiator.core.path_registry import config_file

DEFAULT_CONFIG = {
    "agentx_init": {
        "version": "1.0.0",
        "state_dir": ".agentx-init",
        "log_level": "info",
        "allowlisted_commands": [
            "python -m compileall -q",
            "python -m pytest --co -q",
            "make prove-seed",
            "make prove-l1",
            "make prove-l2",
        ],
        "protected_paths": [
            "L0/CODE/core_kernel",
            "L0/CODE/governance",
            "L0/CODE/kernel_composition",
        ],
        "blocked_paths": [
            "L0/CODE",
            ".agentx-init",
        ],
        "risk_levels": {
            "R0": "read-only or tool-owned output",
            "R1": "planning, proposals, allowlisted validation",
            "R2": "future docs/tests/schema/profile modifications",
            "R3": "future governance or L1 behavior changes",
            "R4": "L0, promotion, permission behavior, self-modification, governance bypass",
        },
        "max_risk_allowed": "R1",
    }
}


class AgentXInitConfig(BaseModel):
    version: str
    state_dir: str
    log_level: str
    allowlisted_commands: list[str]
    protected_paths: list[str]
    blocked_paths: list[str]
    risk_levels: dict[str, str]
    max_risk_allowed: str


def load_config(config_path: Path | None = None) -> AgentXInitConfig:
    if config_path and config_path.exists():
        raw = json.loads(config_path.read_text())
    elif config_file().exists():
        raw = json.loads(config_file().read_text())
    else:
        raw = DEFAULT_CONFIG
    return AgentXInitConfig(**raw["agentx_init"])

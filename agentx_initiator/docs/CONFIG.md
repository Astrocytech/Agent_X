# Configuration

Configuration file: `.agentx-init/config/config.json`

## Default Configuration

```json
{
  "agentx_init": {
    "version": "1.0.0",
    "state_dir": ".agentx-init",
    "log_level": "info",
    "allowlisted_commands": [
      "python -m compileall -q",
      "make prove-seed",
      "make prove-l1",
      "make prove-l2"
    ],
    "protected_paths": [
      "L0/CODE/core_kernel",
      "L0/CODE/governance",
      "L0/CODE/kernel_composition"
    ],
    "blocked_paths": [
      "L0/CODE",
      ".agentx-init"
    ],
    "risk_levels": {
      "R0": "read-only or tool-owned output",
      "R1": "planning, proposals, allowlisted validation",
      "R2": "future docs/tests/schema/profile modifications",
      "R3": "future governance or L1 behavior changes",
      "R4": "L0, promotion, permission behavior, self-modification, governance bypass"
    },
    "max_risk_allowed": "R1"
  }
}

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `version` | string | Config version |
| `state_dir` | string | State directory path |
| `log_level` | string | Logging verbosity |
| `allowlisted_commands` | list | Commands the validate command may run |
| `protected_paths` | list | Paths that must not be modified |
| `blocked_paths` | list | Paths that are blocked from writes |
| `risk_levels` | dict | Risk level definitions |
| `max_risk_allowed` | string | Maximum risk level for actions |

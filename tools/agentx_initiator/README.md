# agentx-init

Agent_X Initiator / Evolution Assistant — a read-only CLI companion tool for inspecting, explaining, planning, validating, and safely evolving Agent_X.

## Quick Start

```bash
pip install -e .
agentx-init --help
agentx-init scan
agentx-init status
```

## Commands

| Command | Purpose |
| --- | --- |
| `scan` | Scan repository structure and layers |
| `status` | Generate governance status report |
| `explain <path>` | Explain a file, directory, or layer |
| `plan` | Generate ranked evolution recommendations |
| `propose --task "<task>"` | Generate non-mutating patch proposal |
| `validate` | Run allowlisted validation commands |
| `audit` | Read append-only audit history |
| `graph` | Build architecture knowledge graph |

## Governance

- L0 is protected — agentx-init may read L0 but must not modify it.
- L1 remains the governance and implementation-control layer.
- L2 remains the specification, blueprint, and profile layer.
- agentx-init may convert L2 concepts into plans and proposals only.
- All writes go to `.agentx-init/`.
- Risk level R4 (L0 modification, self-modification, governance bypass) is blocked.

## State Directory

`.agentx-init/` stores all tool state:

- `config/config.json` — configuration
- `memory/*.jsonl` — append-only event logs
- `reports/*.md` — generated markdown reports
- `snapshots/*.json` — latest scan/graph snapshots

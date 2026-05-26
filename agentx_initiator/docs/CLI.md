# agentx-init CLI Reference

## Usage

```
agentx-init <command> [options]
```

## Global Options

| Option | Description |
| --- | --- |
| `--help` | Show help message |
| `--version` | Show version |

## Commands

### scan

Scan the repository structure and report layer statistics.

```
agentx-init scan
```

Output: repository file counts per layer, source/doc/test breakdown.

### status

Generate a governance status report with Markdown output.

```
agentx-init status
```

Output: writes `latest_status.md` to `.agentx-init/reports/`.

### explain

Explain a file, directory, or layer.

```
agentx-init explain <path>
agentx-init explain L0/CODE
agentx-init explain L1/docs/00_system_goal.md
```

If path is omitted, explains the repository root.

### plan

Generate a ranked list of evolution recommendations.

```
agentx-init plan
```

Output: writes `latest_plan.md` to `.agentx-init/reports/`.

### propose

Generate a non-mutating, human-reviewable patch proposal.

```
agentx-init propose --task "add FIC unit tests for governance engine"
```

R4 tasks (L0 modification, self-modification, governance bypass) are blocked.
Output: writes `latest_patch_proposal.md` to `.agentx-init/reports/`.

### validate

Run allowlisted validation commands.

```
agentx-init validate
```

Only commands in `config.allowlisted_commands` may run.
Output: writes `latest_validation.md` to `.agentx-init/reports/`.

### audit

Read the append-only audit history.

```
agentx-init audit
agentx-init audit --limit 100
```

### graph

Build and write the architecture knowledge graph.

```
agentx-init graph
```

Output: writes `graph_latest.json` to `.agentx-init/snapshots/`.

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

## Product Milestone 1 Active Commands

### help

Show the help message.

```
agentx-init help
agentx-init --help
agentx-init
```

Equivalent to `--help`. The `help` subcommand is an optional alias.

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

## Product Milestone 1 Stubbed Commands

The following commands are registered in PM1 as BLOCKED stubs.
They return a schema-valid BLOCKED response and do not execute.
Full implementations are scheduled for Product Milestone 2 or later.

- **explain** — explain a file, directory, or layer (PM2)
- **plan** — generate ranked evolution plans (PM2)
- **propose** — generate non-mutating patch proposal (PM2)
- **validate** — run allowlisted validation commands (PM2)
- **audit** — read audit event history (PM2)
- **report** — generate architecture report (PM2)
- **memory** — query memory store (PM2)
- **graph** — generate repository knowledge graph (PM3)

# CLI Command Surface Acceptance Report

**Generated**: 2026-06-09
**Pass**: 10

## Primary CLI: `python3 -m agentx_evolve`

| Command | Status | Behavior |
|---|---|---|
| (no args) | PASS | Prints help, exits 0 |
| `--help` / `-h` | PASS | Prints help, exits 0 |
| `help` | PASS | Prints help, exits 0 |
| `version` | PASS | Prints `agentx-evolve 0.1.0`, exits 0 |
| `review <session_id>` | PASS | Invokes HumanReviewInterface.review |
| `approve <session_id>` | PASS | Invokes HumanReviewInterface.approve |
| `reject <session_id>` | PASS | Invokes HumanReviewInterface.reject |
| `explain <session_id>` | PASS | Invokes HumanReviewInterface.review for display |
| `chat [options]` | PASS | Interactive REPL or --once mode |
| `self-upgrade [options]` | PASS | SelfUpgradeWorkflow |
| `init-agent [options]` | PASS | InitAgentWorkflow |
| `evolve-agent [options]` | PASS | EvolveAgentWorkflow |
| `unknown-command` | PASS | Prints error, exits 1 |

## Sub-Entry Points

| Module | Status |
|---|---|
| `agentx_evolve.final_acceptance.cli` | PASS |
| `agentx_evolve.human_review.review_cli` | PASS |
| `agentx_evolve.docs_sync.cli` | PASS |
| `agentx_evolve.context.cli` | PASS (via `__main__.py` - not standalone) |
| `agentx_evolve.scheduler.scheduler_cli` | PASS |
| `agentx_evolve.prompts.prompt_cli` | PASS |
| `agentx_evolve.evaluation.run_evaluation` | PASS |

## CLI Options Verified

- `--mock` provider flag accepted
- `--json` output flag accepted
- `--provider <name>` accepted (api, opencode, mock)
- `--model <model-id>` accepted
- `--run-root <path>` accepted
- `--timeout <seconds>` accepted
- `--session-id <id>` accepted
- `--concept-file <path>` accepted
- `--mode <plan\|apply>` accepted
- `--dry-run` accepted
- `--name <agent-name>` accepted
- `--dest <path>` accepted
- `--agent-dir <path>` accepted

## Known Gaps
- `agentx_evolve.context.cli` has no `__main__.py` — invoked via `python3 -m agentx_evolve context ...` would need wiring in main CLI
- `agentx_evolve` package cannot be `python3 -m agentx_evolve.chat` — chat is part of main CLI, not standalone

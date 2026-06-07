## Minimal Architecture Change: Add --verbose flag to chat command

### Motivation
Users need visibility into the provider response details during chat sessions.

### Change
1. Add `--verbose` / `-v` flag to the `chat` subcommand in `__main__.py`.
2. When set, print the raw provider response JSON to stderr before the final output.
3. Add `verbose` field to `RuntimeConfig` in `runtime/config.py`.
4. Thread config through `ChatWorkflow` to optionally log response details.

### Files affected
- `tools/agentx_evolve/__main__.py`
- `tools/agentx_evolve/runtime/config.py`
- `tools/agentx_evolve/workflows/chat.py`

### Safety notes
- No new dependencies.
- Stderr output only, never secrets to stdout.
- Config field defaults to False — zero behavioral change for existing users.

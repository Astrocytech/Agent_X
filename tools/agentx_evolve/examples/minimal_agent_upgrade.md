## Minimal Agent Upgrade: Add a README to target agent

### Motivation
Newly initialized agents lack a README explaining their purpose and how to extend them.

### Change
1. Create `README.md` in the target agent root with standard Agent_X boilerplate.
2. Update `agent.cfg` to reference the new README in the documentation field.

### Target
The agent directory at `--agent-dir`.

### Files affected
- `README.md` (new)
- `agent.cfg` (modify)

### Safety notes
- Only touches files inside `--agent-dir`.
- README is a new file — no overwrite risk.
- `agent.cfg` is edited conservatively with a single key addition.

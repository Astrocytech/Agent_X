# Security

## Read-Only by Design

agentx-init version 1 is read-only toward Agent_X source files. The only write location is `.agentx-init/`.

## Path Protection

Protected paths (L0 core kernel, governance, kernel_composition) are enforced at the application level. The `validate` command only runs allowlisted commands.

## Audit Trail

All significant actions are recorded in the append-only audit log at `.agentx-init/memory/audit_events.jsonl`. The audit log cannot be deleted by agentx-init.

## No Network Access

agentx-init does not require network access. No data leaves the local machine.

## No Background Process

agentx-init runs as a foreground CLI command only. No daemon, no scheduler, no background service.

## Risk Controls

Actions are classified by risk level (R0–R4). Version 1 blocks all R4 actions including:
- L0 source modification
- Self-modification
- Governance bypass
- Autonomous promotion

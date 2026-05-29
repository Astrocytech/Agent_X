# Tool Access Policy

## Purpose
Define how L1/L2 extensions can access tools through L0's governed tool gateway.

## Rules
- All tool access goes through L0 ToolGatewayPort
- L1 controllers must authenticate via extension ABI
- L2 profiles define allowed tool sets
- No direct tool bypass allowed

## Enforcement
- L0 governance checks tool access against active profile
- Violations are recorded in evidence ledger

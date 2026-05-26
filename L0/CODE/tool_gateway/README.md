# Tool Gateway — L0 Execution Path

L0 execution path:
1. Runtime builds canonical ToolRequest.
2. Governance approves or blocks.
3. Certification gate checks mode/profile.
4. SeedToolGateway executes canonical seed tool.
5. ToolResult is normalized.
6. ToolCallEvidence is written.

## Seed-only directory
All files in this directory are seed-core L0 execution path files.
Non-L0 files (platform_tool_registry, capability_registry, tool_alias_resolver, tool_cards) have been removed.

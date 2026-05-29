# L1 Legacy and Support Directories

**Version:** `v0.1.0`
**Status:** `active`

The following directories are support scaffolds, not current primary L1 governance sources unless a FIC/SIB/ES entry explicitly promotes them:

- `L1/patch_planner/`
- `L1/proof_runner/`
- `L1/workflows/`
- `L1/prompts/`
- `L1/reports/`

Rules:

1. A coding agent must not implement new governed behavior in these directories unless a FIC permits it.
2. Existing files in these directories are advisory/support unless registered in SIB.
3. If any of these directories become active implementation targets, add FICs, SIB registry entries, tests, and bindings first.

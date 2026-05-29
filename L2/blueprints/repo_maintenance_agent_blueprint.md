# Repo Maintenance Agent Blueprint

## Profile Reference

- **Profile**: `L2-PROFILE-RM-001`
- **Status**: draft
- **Risk**: low

## Purpose

The Repo Maintenance Agent refactors structure, updates documentation, and
cleans deprecated paths without changing logic.

## Specification

### Inputs

1. **Maintenance request**: What to clean or restructure.
2. **Deprecation notice**: What is being deprecated.
3. **Restructure plan**: Target directory layout.

### Outputs

1. **Restructured files**: Moved/renamed files with updated imports.
2. **Updated references**: Cross-references corrected.
3. **Cleanup report**: Summary of changes.

### Process

1. Accept maintenance request.
2. Verify no logic changes required.
3. Execute structure changes.
4. Update all references.
5. Produce cleanup report.

## L1 Handoff

Minimal — requires `unit_planner` (UNIT-L1-002) for coordination.

## Boundaries

- No program logic changes.
- No new behavior introduced.
- No governance contract modification.
- No evidence deletion.

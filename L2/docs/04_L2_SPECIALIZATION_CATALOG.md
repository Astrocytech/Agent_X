# L2 Specialization Catalog

## Specialization Types

| Type | Code | Description | Risk |
|------|------|-------------|------|
| Coding | `coding` | Generate, review, and validate code changes under governance | medium |
| Research | `research` | Explore problem spaces, propose solutions, document findings | low |
| Symbolic Regression | `symbolic-regression` | Plan and validate SR experiments through governed pipelines | medium |
| Repo Maintenance | `repo-maintenance` | Refactor, clean, and maintain codebase structure | low |
| Orchestration | `orchestration` | Coordinate multi-profile workflows | high |

## Coding Agent

- **Purpose**: Generate governed code changes within L1 FIC boundaries.
- **Boundary**: Must not modify L0 without L0 FIC. Must not bypass L1 validation.
- **L1 Dependencies**: goal_classifier, unit_planner, fic_generator, fic_validator,
  handoff_packet_builder.

## Symbolic Regression Controller

- **Purpose**: Define how Agent_X plans, validates, and packages SR work.
- **Boundary**: Must not directly modify PySR_custom, L0, or execute SR backends.
- **L1 Dependencies**: goal_classifier, unit_planner, fic_generator, fic_validator,
  handoff_packet_builder.

## Research Agent

- **Purpose**: Explore problem spaces, produce documentation and proposals.
- **Boundary**: Must not implement code. Must not modify governance artifacts.
- **L1 Dependencies**: (indirect — produces input for goal_classifier)

## Repo Maintenance Agent

- **Purpose**: Refactor structure, update docs, clean deprecated paths.
- **Boundary**: Must not change logic or introduce new behavior.
- **L1 Dependencies**: (minimal — operates on file structure, not logic)

## Orchestration Profile

- **Purpose**: Coordinate multi-agent workflows across profiles.
- **Boundary**: Must not execute tools directly. Routes through L1 governed units.
- **L1 Dependencies**: All L1 units.
- **Risk**: Critical — orchestration errors affect the full system.

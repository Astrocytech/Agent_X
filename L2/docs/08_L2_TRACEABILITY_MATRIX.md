# L2 Traceability Matrix

## L2 Documents → L1 Unit Mapping

| L2 Doc | Description | Related L1 Units |
|--------|-------------|------------------|
| 00_L2_SYSTEM_GOAL.md | System goal | UNIT-L1-001 (goal_classifier) |
| 01_L2_BACKGROUND.md | Background context | UNIT-L1-001 (goal_classifier) |
| 02_L2_ARCHITECTURE_CONTRACT.md | Architecture contract | UNIT-L1-002 (unit_planner) |
| 03_L2_PROFILE_MODEL.md | Profile model | UNIT-L1-003 (fic_generator), UNIT-L1-004 (fic_validator) |
| 04_L2_SPECIALIZATION_CATALOG.md | Specialization catalog | UNIT-L1-002 (unit_planner), UNIT-L1-006 (handoff_packet_builder) |
| 05_L2_INTEGRATION_BOUNDARIES.md | Integration boundaries | UNIT-L1-007, UNIT-L1-008, UNIT-L1-009 |
| 06_L2_EVALUATION_PLAN.md | Evaluation plan | UNIT-L1-012, UNIT-L1-013, UNIT-L1-014 |
| 07_L2_RISK_LEDGER.md | Risk ledger | UNIT-L1-010 (risk_checker) |
| 08_L2_TRACEABILITY_MATRIX.md | This matrix | All units |
| 09_L2_HANDOFF_TO_L1_RULES.md | Handoff rules | UNIT-L1-006 (handoff_packet_builder), UNIT-L1-002 (unit_planner) |

## L2 Profiles → L1 Unit Mapping

| Profile | Required L1 Units |
|---------|-------------------|
| Coding Agent | UNIT-L1-003, UNIT-L1-004, UNIT-L1-005, UNIT-L1-006, UNIT-L1-007 |
| Symbolic Regression Controller | UNIT-L1-003, UNIT-L1-004, UNIT-L1-005, UNIT-L1-006, UNIT-L1-007 |
| Research Agent | UNIT-L1-001 (indirect) |
| Repo Maintenance Agent | UNIT-L1-002 (minimal) |
| Orchestration | All L1 units |

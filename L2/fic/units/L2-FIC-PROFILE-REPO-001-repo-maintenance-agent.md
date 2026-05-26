---
schema: "agent-x-l2-lightweight-eqc-fic/v0.4"
l2_fic_id: "L2-FIC-PROFILE-REPO-001"
global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-REPO-001"
target_artifact_id: "L2-PROFILE-RM-001"
global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-RM-001"
target_path: "L2/profiles/repo_maintenance_agent.yaml"
target_type: "profile"
version: "v0.1.0"
status: "draft"
risk_level: "low"
implementation_allowed: false
may_request_l1_handoff: true
owner: "Agent_X L2"
required_l1_units:
  - "AGENT_X_L1::UNIT-L1-002"
evaluation_refs:
  - "L2/evaluation_specs/repo_maintenance_eval.md"
---

# L2 FIC: Repo Maintenance Agent Profile

## A. Identity

- **FIC ID**: L2-FIC-PROFILE-REPO-001
- **Target**: L2-PROFILE-RM-001 (Repo Maintenance Agent)
- **Layer**: L2
- **Status**: draft

## B. Authority and Source Hierarchy

Governed by L2 system goal and EQC-FIC standard.

## C. Profile Purpose

Refactor structure, update documentation, clean deprecated paths without changing logic.

## D. Non-Goals and Forbidden Runtime Behavior

- No program logic changes.
- No new behavior introduced.
- No governance contract modification.
- No evidence deletion.

## E. L2 Placement and Ownership

Owner: Agent_X L2. Specification only.

## F. Target Artifact Contract

Target: L2/profiles/repo_maintenance_agent.yaml.

## G. Inputs and Allowed Source Material

Maintenance request, deprecation notice, restructure plan.

## H. Expected Outputs

Restructured files, updated references, cleanup report.

## I. Required L1 Handoff Targets

UNIT-L1-002 (minimal).

## J. Boundary and Dependency Rules

No logic changes. No new behavior.

## K. Risk Classification

Low.

## L. Evaluation Contract

See L2/evaluation_specs/repo_maintenance_eval.md.

## M. Readiness Criteria

Profile valid, blueprint complete, evaluation spec exists.

## N. Traceability and Bindings

SIB binding L2-BIND-RM-001.

## O. Change Policy

Version bump required.

## P. LLM Authoring Instructions

Keep implementation_allowed=false.

## Q. Completion Evidence

See L2/evidence/ for future records.

## R. Review Packet Requirements

Verify no logic change scope.

## S. Unknowns and Deferrals

None.

## T. Version Impact

v0.1.0 — initial scaffold.

## U. Source Freshness

Current.

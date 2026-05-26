---
schema: "agent-x-l2-lightweight-eqc-fic/v0.4"
l2_fic_id: "L2-FIC-PROFILE-CODING-001"
global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-CODING-001"
target_artifact_id: "L2-PROFILE-CA-001"
global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-CA-001"
target_path: "L2/profiles/coding_agent.yaml"
target_type: "profile"
version: "v0.1.0"
status: "draft"
risk_level: "medium"
implementation_allowed: false
may_request_l1_handoff: true
owner: "Agent_X L2"
required_l1_units:
  - "AGENT_X_L1::UNIT-L1-003"
  - "AGENT_X_L1::UNIT-L1-004"
  - "AGENT_X_L1::UNIT-L1-005"
  - "AGENT_X_L1::UNIT-L1-006"
  - "AGENT_X_L1::UNIT-L1-007"
evaluation_refs:
  - "L2/evaluation_specs/coding_agent_eval.md"
---

# L2 FIC: Coding Agent Profile

## A. Identity

- **FIC ID**: L2-FIC-PROFILE-CODING-001
- **Target**: L2-PROFILE-CA-001 (Coding Agent)
- **Layer**: L2
- **Status**: draft

## B. Authority and Source Hierarchy

This FIC is governed by:
- L2 system goal (`L2/docs/00_L2_SYSTEM_GOAL.md`)
- L2 architecture contract (`L2/docs/02_L2_ARCHITECTURE_CONTRACT.md`)
- AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4.md

## C. Profile Purpose

Define how Agent_X generates, reviews, and validates code changes within L1 FIC boundaries.

## D. Non-Goals and Forbidden Runtime Behavior

- No direct L0 modification without L0 FIC.
- No bypass of L1 validation.
- No autonomous deployment.
- No ungoverned dependency changes.
- No tool execution from L2.

## E. L2 Placement and Ownership

Owner: Agent_X L2. This profile is a specification only.

## F. Target Artifact Contract

Target: L2/profiles/coding_agent.yaml — must define specialization type, inputs, outputs, forbidden actions, and required L1 units.

## G. Inputs and Allowed Source Material

Implementation request, FIC reference, codebase context, test results.

## H. Expected Outputs

Governed code changes, validation evidence, handoff packets.

## I. Required L1 Handoff Targets

UNIT-L1-003 through UNIT-L1-007.

## J. Boundary and Dependency Rules

Must not modify L0 without L0 FIC. Must not bypass L1 validation.

## K. Risk Classification

Medium — code changes affect system integrity.

## L. Evaluation Contract

See L2/evaluation_specs/coding_agent_eval.md

## M. Readiness Criteria

Profile yaml valid, blueprint complete, evaluation spec exists, L1 units mapped.

## N. Traceability and Bindings

SIB binding L2-BIND-CA-001 references UNIT-L1-003 through UNIT-L1-007.

## O. Change Policy

Changes require version bump. Status changes require review.

## P. LLM Authoring Instructions

Do not add runtime authority. Keep implementation_allowed=false.

## Q. Completion Evidence

See L2/evidence/ for future completion records.

## R. Review Packet Requirements

Review must verify no runtime scope, no false implementation claims.

## S. Unknowns and Deferrals

None.

## T. Version Impact

v0.1.0 — initial scaffold.

## U. Source Freshness

Referenced standards at L2/standards/ are current.

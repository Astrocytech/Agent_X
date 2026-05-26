---
schema: "agent-x-l2-lightweight-eqc-fic/v0.4"
l2_fic_id: "L2-FIC-PROFILE-SR-001"
global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-SR-001"
target_artifact_id: "L2-PROFILE-SR-001"
global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
target_path: "L2/profiles/symbolic_regression_controller.yaml"
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
  - "L2/evaluation_specs/symbolic_regression_eval.md"
---

# L2 FIC: Symbolic Regression Controller Profile

## A. Identity

- **FIC ID**: L2-FIC-PROFILE-SR-001
- **Target**: L2-PROFILE-SR-001 (Symbolic Regression Controller)
- **Layer**: L2
- **Status**: draft

## B. Authority and Source Hierarchy

Governed by L2 system goal, architecture contract, and EQC-FIC standard.

## C. Profile Purpose

Define how Agent_X plans, validates, and packages symbolic-regression work through L1-governed implementation tasks.

## D. Non-Goals and Forbidden Runtime Behavior

- No direct PySR_custom modification.
- No direct L0 modification.
- No runtime autonomous patching.
- No ungoverned tool execution.
- No direct SR experiment execution from L2.

## E. L2 Placement and Ownership

Owner: Agent_X L2. Specification only.

## F. Target Artifact Contract

Target: L2/profiles/symbolic_regression_controller.yaml.

## G. Inputs and Allowed Source Material

Problem statement, dataset description, candidate SR backend, resource budget.

## H. Expected Outputs

Bounded L1 implementation proposal, evaluation plan, risk notes.

## I. Required L1 Handoff Targets

UNIT-L1-003 through UNIT-L1-007.

## J. Boundary and Dependency Rules

Must not import PySR. Must not execute SR experiments.

## K. Risk Classification

Medium — SR experiments could consume significant compute.

## L. Evaluation Contract

See L2/evaluation_specs/symbolic_regression_eval.md.

## M. Readiness Criteria

Profile valid, blueprint complete, evaluation spec exists, L1 units mapped.

## N. Traceability and Bindings

SIB binding L2-BIND-SR-001.

## O. Change Policy

Version bump required. Status changes require review.

## P. LLM Authoring Instructions

Keep implementation_allowed=false. Do not add runtime authority.

## Q. Completion Evidence

See L2/evidence/ for future records.

## R. Review Packet Requirements

Verify no runtime scope, no false implementation claims.

## S. Unknowns and Deferrals

None.

## T. Version Impact

v0.1.0 — initial scaffold.

## U. Source Freshness

Current.

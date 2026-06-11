# Deferred Training Experiments

## Status: Out of Scope for Stage A

This document describes training experiments that are **deferred** to later
stages of the BenchCore project. They are **not** part of the Stage A benchmark
pack and must not be implemented or tested during Stage A.

## Source

These experiments are described in **BENCHCORE-DOC-014** (Training Experiments
specification). Their inclusion here serves as a boundary definition and a
reference for future stages.

## Experiment 1: T5 Fine-Tuning

- **Goal**: Fine-tune a T5 (Text-to-Text Transfer Transformer) model on the
  BenchCore prediction task to improve accuracy on field-value extraction.
- **Stage**: B or later.
- **Requirements**:
  - A labeled training dataset derived from the benchmark fixtures.
  - An evaluation harness that compares T5 predictions against frozen LLM
    baselines.
  - A LoRA or full fine-tuning pipeline that logs all hyperparameters and
    checkpoints.
- **Constraints**:
  - Must not be run during Stage A.
  - Must be evaluated against the same deployment gates defined in
    `evaluation/deployment_gate_contract.json`.
  - Results must be documented and compared with the frozen core LLM baseline.

## Experiment 2: LoRA Adaptation

- **Goal**: Apply low-rank adaptation (LoRA) to the core LLM to specialize it
  for BenchCore prediction tasks while keeping most parameters frozen.
- **Stage**: B or later.
- **Requirements**:
  - A LoRA adapter configuration (rank, alpha, target modules).
  - Training data from BenchCore benchmark fixtures.
  - Evaluation against all deployment gates before and after adaptation.
- **Constraints**:
  - Must pass the anti-retraining policy check: only permitted after Stage A
    is officially closed and the transition to Stage B is approved.
  - Adapter weights must be versioned and auditable.

## Experiment 3: TranX Transfer Learning

- **Goal**: Apply transfer learning from a TranX (transformer-based transfer)
  model pre-trained on a related domain to improve BenchCore prediction accuracy
  with minimal in-domain data.
- **Stage**: C or later.
- **Requirements**:
  - A pre-trained TranX model checkpoint.
  - A domain adaptation dataset (BenchCore-labeled examples).
  - Evaluation metrics comparing TranX against both the frozen LLM and
    T5/LoRA fine-tuned models.
- **Constraints**:
  - TranX is a BenchCore-specific concept and must not be absorbed into the
    Agent_X core ontology.
  - Results are benchmark-only and do not imply production readiness.

## Experiment 4: Multi-Stage Ensemble

- **Goal**: Combine multiple frozen and fine-tuned models (LLM + T5 + TranX)
  via an ensemble voting or stacking mechanism.
- **Stage**: D or later.
- **Requirements**:
  - At least two independently trained models from earlier stages.
  - An ensemble fusion policy (voting, weighted average, learned stacker).
  - Evaluation against deployment gates and comparison to individual models.
- **Constraints**:
  - Ensemble must not introduce hidden state changes in any constituent model.
  - Ensemble policy must pass the same evaluation workflow as individual models.

## Boundary Notes

| Experiment | Stage | Status in Stage A |
|---|---|---|
| T5 Fine-Tuning | B | Forbidden |
| LoRA Adaptation | B | Forbidden |
| TranX Transfer Learning | C | Forbidden |
| Multi-Stage Ensemble | D | Forbidden |

All deferred experiments are **explicitly out of scope** for the Stage A
benchmark pack. Their documentation here serves only to mark the boundary
and to provide a reference for future development.

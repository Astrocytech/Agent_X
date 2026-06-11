# Anti-Retraining Policy

## Status: Stage A (Benchmark Pack Only)

This policy defines what learning mechanisms are **allowed** and **forbidden**
during Stage A of the BenchCore benchmark pack. The core LLM must remain frozen
throughout Stage A. Any modification to the core model's weights constitutes a
violation of this policy.

## Source

This policy derives from **BENCHCORE-DOC-012** (Learning Policy specification).

## Allowed Operations

The following operations are permitted without violating the anti-retraining
policy:

- **Retrieval updates**: Adding, removing, or re-ranking entries in the
  capability registry (`dynamic_retrieval/capability_registry_fixture.json`).
- **Source inventory updates**: Modifying coverage CSVs, source hashes, or
  evidence records.
- **Benchmark fixtures**: Creating or updating evaluation datasets, expected
  metrics, and test fixtures.
- **Lightweight classifiers**: Training or updating lightweight classifiers
  (e.g., logistic regression, decision trees, small embedding-based rankers)
  that operate on top of frozen core LLM representations.
- **Ranking / scoring policies**: Updating reranking weights, score thresholds,
  or fallback strategies in `reranking_policy.json` or `feedback_policy.json`.
- **Calibration**: Adjusting reliability scores, confidence calibration curves,
  or bias correction parameters in the feedback loop.
- **Feedback logs**: Recording, aggregating, and analyzing feedback events
  without modifying core model weights.
- **Supervised evaluation artifacts**: Confusion matrices, bootstrap interval
  reports, regression dashboards — any artifact that evaluates model
  performance without modifying the model.

## Forbidden Operations

The following operations are **strictly forbidden** during Stage A:

| Operation | Rationale |
|---|---|
| **Training the core LLM** | The core model is the frozen foundation. Any gradient update or fine-tuning violates the benchmark isolation principle. |
| **Uncontrolled LoRA updates** | Low-rank adaptation (LoRA) modifies core model behavior via injected weights. Even small LoRA updates can shift predictions in untestable ways. |
| **Online self-modification** | The system must not modify its own core logic or prompt templates based on live feedback without going through the evaluation workflow. |
| **Promotion without evaluation** | No learned policy (ranking, scoring, classification) may be promoted to 'active' status unless it has passed the evaluation workflow and deployment gates. |
| **Hidden model state changes** | Any change to the model's internal state — including cache poisoning, embedding drift, or silent adapter loading — that is not tracked in the evaluation log is prohibited. |

## Consequences of Violation

Any violation of this policy invalidates the Stage A benchmark results. The
system must be reset to a known-good state (baseline checkpoint) and the
violation must be documented in the negative knowledge log.

## Deferred Training Experiments

Training experiments — including T5 fine-tuning, LoRA adaptation, and TranX
transfer learning — are described in `deferred_training_experiments.md` as
later-stage activities. They are explicitly out of scope for Stage A.

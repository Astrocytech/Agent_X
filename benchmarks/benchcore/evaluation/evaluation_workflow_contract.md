# Evaluation Workflow Contract

## Overview

This contract defines the evaluation workflow for the BenchCore benchmark pack.
The workflow loads a dataset, runs prediction on each sample, computes metrics
against ground-truth labels, and optionally checks for regression relative to a
baseline. The workflow is defined by `evaluation_config.schema.json` and
produces output that must satisfy the `deployment_gate_contract.json` conditions
before a candidate system can be considered passing.

## Metric Families

### Exact-Match Accuracy
- **Definition**: Fraction of samples where `predicted_label` exactly equals
  `expected_label`.
- **Output**: `exact_match_accuracy` (float in [0, 1]).
- **Edge case**: Empty dataset raises an error; accuracy is undefined.

### Precision / Recall / F1 (Macro and Micro)
- **Macro**: Precision, recall, and F1 are computed per label, then averaged
  with equal weight per label.
- **Micro**: Global counts of true positives, false positives, and false
  negatives are aggregated across all labels before computing metrics.
- **Output**: `macro_precision`, `macro_recall`, `macro_f1`, `micro_precision`,
  `micro_recall`, `micro_f1`.
- **Edge case**: Labels present in ground truth but never predicted contribute
  zero recall and zero precision to the macro average.

### Top-k Hit Rate
- **Definition**: Fraction of samples where the correct label appears in the
  top-k ranked predictions.
- **Output**: `top_{k}_hit_rate`.
- **Requires**: A `rank` column in the dataset or a ranked list per sample.

### Mean Reciprocal Rank (MRR)
- **Definition**: Mean of the reciprocal rank of the correct label in the
  predicted ranked list.
- **Output**: `mrr`.
- **Edge case**: If the correct label is not in the ranked list, reciprocal rank
  is 0 for that sample.

### Cost-Weighted Macro F1
- **Definition**: Macro F1 where each label's F1 is weighted by a per-label
  cost coefficient (higher cost = more important to get right).
- **Output**: `cost_weighted_macro_f1`.
- **Requires**: A cost map in the evaluation config or dataset metadata.

### Bootstrap Confidence Intervals
- **Method**: Resample dataset with replacement for `bootstrap_iterations`
  rounds, recompute all metrics each round, then report percentile intervals at
  the specified `confidence_level`.
- **Output**: Lower and upper bounds for each metric.

### Regression Check
- **Method**: Compare current metrics against `baseline_path` metrics. A metric
  is flagged as regression if it drops below the baseline by more than a
  configurable tolerance (default: 5% relative decrease).
- **Output**: Boolean `regression_detected` flag and per-metric deltas.

## Dataset Requirements

- Must be a CSV file with at minimum the columns: `id`, `input_text`,
  `expected_label`, `predicted_label`.
- For ranked evaluation, a `rank` column is required.
- The `id` field must be unique per row.
- Rows with missing `expected_label` or `predicted_label` are excluded from
  metric computation and logged as warnings.
- The dataset path must be readable and non-empty.

## Deployment Gates

Deployment gates are defined in `deployment_gate_contract.json`. Each gate
specifies a metric, an operator, and a threshold. The evaluation workflow must:

1. Compute all metrics from the candidate system.
2. Check each gate condition.
3. Compute the fraction of gates that pass.
4. Compare against `pass_threshold`.
5. If `regression_check_required` is true, also verify that no regression is
   detected beyond the allowed tolerance.

## Failure Modes

| Failure Mode | Description | Handling |
|---|---|---|
| Missing keys | Dataset lacks required columns | Evaluation raises an error with a list of missing columns. |
| Bad ranked-list length | Ranked list per sample has length != top_k | Sample is excluded from top-k and MRR metrics; logged as warning. |
| Invalid baseline | `baseline_path` is non-null but file does not exist or is malformed | Evaluation raises an error. |
| Empty dataset | CSV has no data rows | Evaluation raises an error. |
| Non-unique IDs | Duplicate `id` values found | Evaluation raises an error. |

## Benchmark Scope

This evaluation workflow covers the BenchCore Stage A benchmark pack only. It
does not apply to:
- Live production system evaluation.
- Reinforcement learning from human feedback (RLHF) pipelines.
- Continuous online evaluation with streaming data.
- Cross-benchmark metric aggregation.

All metrics and gates are defined relative to the ground-truth labels in the
fixture datasets shipped with this pack.

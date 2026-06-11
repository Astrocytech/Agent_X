# Multi-Line Output Contract

## Purpose

Define the expected output format and validation rules for multi-line prediction benchmarks derived from BenchCore's story/item/split field prediction problem.

## Input

A multi-line input consisting of:
- A story header with metadata (story_id, timestamp, source)
- One or more item blocks, each containing multiple fields
- Split indicators separating item groups

## Output Format

Each prediction must produce a structured output:

```json
{
  "story_id": "STORY-001",
  "items": [
    {
      "item_index": 0,
      "fields": {
        "nrcs": "predicted_value",
        "cam": "predicted_value",
        "mic": "predicted_value",
        "clip": "predicted_value"
      }
    }
  ],
  "predictions": [
    {"field": "nrcs", "value": "predicted", "confidence": 0.95},
    {"field": "cam", "value": "predicted", "confidence": 0.87}
  ]
}
```

## Validation Rules

1. Every item in the input must have a corresponding prediction entry.
2. Field names must match the known taxonomy (NRCS, CAM, MIC, CLIP, VO, SOT, PKG, OTS, FS, DBLBOX).
3. Multi-line splits must preserve item boundary integrity.
4. No hallucinated field names are allowed.
5. Confidence scores must be in [0.0, 1.0].

## Failure Conditions

- Missing item predictions: FAIL
- Extra hallucinated fields: FAIL
- Misaligned split boundaries: FAIL
- Confidence outside [0, 1]: FAIL

## Source

Derived from BENCHCORE-DOC-005 (predicting-rundown-story-item-object-fields-multi-line.pdf).

## Scope

Benchmark contract only. Not a production prediction service.

# Operator: classify_specialization_request

## Purpose

Given an incoming request, determine what specialization type it belongs to.

## Input

`request`: A structured or natural-language request object with fields:
- `description` (string)
- `context` (map, optional)
- `requested_type` (string, optional) — may specify a desired specialization

## Output

`classification`: A map with:
- `specialization_type` (string) — one of: `coding`, `research`, `symbolic-regression`,
  `repo-maintenance`, `orchestration`, or `unknown`
- `confidence` (float, 0.0–1.0)
- `reasoning` (string)

## Logic

1. If `requested_type` is provided and valid, return it with confidence 0.8.
2. Otherwise, match keywords in `description` against known patterns:
   - "equation", "symbolic", "regression", "SR", "PySR" → `symbolic-regression`
   - "refactor", "clean", "restructure", "deprecat" → `repo-maintenance`
   - "research", "explore", "investigate", "feasibility" → `research`
   - "implement", "code", "write", "add feature" → `coding`
   - "coordinate", "orchestrate", "workflow", "multi" → `orchestration`
3. If no match, return `unknown` with confidence 0.0.

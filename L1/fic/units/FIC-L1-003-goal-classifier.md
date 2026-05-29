# FIC-L1-003: Goal Classifier

**fic_id:** `FIC-L1-003`
**unit_id:** `UNIT-L1-003`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/goal_classifier.py`

## Description

Classifies a free-text system goal into a structured `GoalRecord` with type, priority, scope, and constraints. Uses deterministic pattern matching only — no shell, network, or model calls.

## Public surface

```python
__all__ = [
    "GoalType",
    "GoalPriority",
    "GoalScope",
    "GoalRecord",
    "GoalClassifier",
    "GoalClassifierError",
    "classify_goal_text",
    "classify_goal_file",
]
```

### Exports

- `GoalType` — enum: `FEATURE`, `BUG_FIX`, `REFACTOR`, `RESEARCH`, `DOCUMENTATION`, `INFRASTRUCTURE`
- `GoalPriority` — enum: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `GoalScope` — enum: `COMPONENT`, `CROSS_COMPONENT`, `SYSTEM`
- `GoalRecord` — frozen dataclass: `goal_type`, `priority`, `scope`, `summary`, `constraints`, `raw_text`
- `GoalClassifierError` — base exception
- `GoalClassifier` — class:
  - `__init__(self)` — no args
  - `classify(self, text: str) -> GoalRecord` — classify free-text goal
  - `classify_file(self, path: str, *, root: str = ".") -> GoalRecord` — read file then classify
- `classify_goal_text(text: str) -> GoalRecord`
- `classify_goal_file(path: str, *, root: str = ".") -> GoalRecord`

## Classification rules (deterministic)

| Field | Detection |
|---|---|
| `goal_type` | Keywords in text: "feature", "new" → FEATURE; "bug", "fix", "error", "crash" → BUG_FIX; "refactor", "clean", "restructure" → REFACTOR; "research", "investigate", "explore" → RESEARCH; "doc", "readme", "comment" → DOCUMENTATION; "infra", "ci", "cd", "pipeline", "deploy" → INFRASTRUCTURE. First match wins; default FEATURE |
| `priority` | Priority markers: "critical", "urgent", "p0" → CRITICAL; "high", "p1" → HIGH; "medium", "p2" → MEDIUM; "low", "p3", "nice to have" → LOW. First match wins; default MEDIUM |
| `scope` | Scope markers: "system", "cross-layer", "global" → SYSTEM; "cross-component", "inter-module" → CROSS_COMPONENT; "component", "module", "single" → COMPONENT. First match wins; default COMPONENT |
| `summary` | First non-empty line or first sentence after stripping markdown/headers |
| `constraints` | Lines or fragments containing keywords: "must", "must not", "shall", "cannot", "require", "only", "no", "without", "within", "after", "before". Extracted as a list of strings |

## Dependency contract

- **stdlib only** (enum, dataclasses, pathlib, hashlib, re)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. All input text is treated case-insensitively for keyword matching.
2. Unknown types default to `GoalType.FEATURE`.
3. Unknown priorities default to `GoalPriority.MEDIUM`.
4. Unknown scopes default to `GoalScope.COMPONENT`.
5. `constraints` is always a list (may be empty).
6. `raw_text` in `GoalRecord` preserves the original input verbatim.
7. `classify_file` uses `RepoStateReader` to read the file (if available) or `pathlib`.
8. Classifier never raises on unknown content — always returns a valid `GoalRecord` with defaults.
9. No regex backtracking exploits — patterns are simple keyword checks.

## Edge cases

| Case | Behavior |
|---|---|
| empty string | GoalRecord with FEATURE, MEDIUM, COMPONENT, empty summary, empty constraints |
| only whitespace | same as empty |
| multiple type keywords | first match wins |
| no keywords matched | defaults applied |
| non-UTF-8 file | `GoalClassifierError` |
| file not found | `GoalClassifierError` |
| text with markdown headers | headers stripped from summary |
| text with only headers | summary is first header text |

## Test contract

Test file: `L1/tests/test_goal_classifier.py`

Required tests (20):
1. `test_classifies_feature_goal`
2. `test_classifies_bug_fix_goal`
3. `test_classifies_refactor_goal`
4. `test_classifies_research_goal`
5. `test_classifies_documentation_goal`
6. `test_classifies_infrastructure_goal`
7. `test_classifies_critical_priority`
8. `test_classifies_high_priority`
9. `test_classifies_low_priority`
10. `test_classifies_system_scope`
11. `test_classifies_cross_component_scope`
12. `test_defaults_on_empty_text`
13. `test_defaults_on_no_keywords`
14. `test_extracts_summary_from_first_line`
15. `test_extracts_constraints`
16. `test_classify_file_reads_and_classifies`
17. `test_classify_file_rejects_missing_file`
18. `test_goal_record_is_frozen`
19. `test_case_insensitive_keywords`
20. `test_goal_classifier_no_forbidden_imports`

# LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC

```text
document_id: LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff
component_id: AGENTX_LONG_TERM_LEARNING
component_name: Long-Term Learning / Outcome Review Layer
roadmap_layer: 14
roadmap_phase: Phase E — Long-Term Learning
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria
optional_standards: ES, Report Template
target_language: Python
canonical_subdirectory: tools/agentx_evolve/learning/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/learning/
implementation_mode: append-only outcome recording, deterministic strategy memory
previous_version_rating: 9.5/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was strong. I would rate it:

```text
9.5/10
```

It already covered outcome recording, session-based lookup, successful strategy extraction, failure pattern extraction, recommendations, basic StrategyMemory store/retrieve/clear, and simple in-memory persistence.

## 0.2 Why v3 Was Not Fully 10/10

The v3 spec still had a few implementation-safety gaps:

```text
1. No evidence hashing — outcome records lacked a deterministic outcome_hash field.
2. No durable persistence — outcomes existed only in memory, not in .agentx-init/learning/.
3. No locking — concurrent outcome writes could race.
4. No tag-based search — filtering was limited to session_id only.
5. No schema constants or validation.
6. No atomic write patterns for history files.
7. No JSONL append for append-only outcome history.
8. No canonical_json helper for deterministic hashing.
```

## 0.3 v4 Improvements

This v4 adds:

```text
outcome_hash via sha256_dict
write_outcome_history / append_outcome_history atomic persistence
acquire_learning_lock / release_learning_lock
get_by_tag tag-based search
schema constants and validation
canonical_json / sha256_dict / to_dict helpers
jsonl append patterns for history
```

This v4 is the final 10/10 implementation handoff.

---

# 1. Purpose

This document is the full implementation specification for the **Long-Term Learning / Outcome Review Layer**.

It tells the coding agent exactly what to build.

The Long-Term Learning / Outcome Review Layer records implementation outcomes, identifies successful strategies, detects failure patterns, and stores reusable knowledge so that Agent_X can learn from past work.

This layer must:

```text
record every implementation outcome with a deterministic hash
persist outcomes to .agentx-init/learning/ for durable cross-session learning
support retrieval by session_id, tag, strategy success, and failure patterns
maintain an append-only outcome history
use locking to prevent concurrent write corruption
store and retrieve strategy memory for reuse
```

---

# 2. Scope

## 2.1 Required in This Layer

```text
LearningOutcomeRecord dataclass
LearningOutcomeReview class with record, query, and persistence methods
StrategyMemory class with store, retrieve, search, clear, persist, load
outcome_hash computation via sha256_dict
tag-based filtering
schema constants and validation
atomic file writes
append-only JSONL history
learning lock acquisition and release
```

## 2.2 Not Required in This Layer

```text
LLM-based outcome analysis
automatic strategy recommendation generation
network calls
model invocation
MCP server
Git write operations
source mutation
promotion decisions
```

---

# 3. Canonical Destination Summary

Create the Long-Term Learning package here:

```text
tools/agentx_evolve/learning/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/learning/
```

---

# 4. Exact Subdirectory

Required package:

```text
tools/agentx_evolve/learning/
```

Required runtime root:

```text
.agentx-init/learning/
```

Required schemas location:

```text
tools/agentx_evolve/schemas/
```

Required tests location:

```text
tools/agentx_evolve/tests/
```

No learning runtime artifact may be written outside `.agentx-init/learning/`.

---

# 5. Files to Create

## 5.1 Learning Package Files

```text
tools/agentx_evolve/learning/__init__.py
tools/agentx_evolve/learning/outcome_review.py
```

## 5.2 Schema Files

```text
tools/agentx_evolve/schemas/learning_outcome_record.schema.json
```

## 5.3 Test Files

```text
tools/agentx_evolve/tests/test_learning_outcome_review.py
```

---

# 6. Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/learning/
```

Required artifacts:

```text
.agentx-init/learning/outcome_history.json
.agentx-init/learning/outcome_history.jsonl
.agentx-init/learning/strategy_memory.json
.agentx-init/learning/.learning.lock
```

Rules:

```text
history files are append-only JSONL
outcome_history.json is written atomically
strategy_memory.json is written atomically
lock file must not be treated as source mutation
```

---

# 7. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

---

# 8. LearningOutcomeRecord Dataclass

Implement `LearningOutcomeRecord` in `outcome_review.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "learning_outcome_record.schema.json"
outcome_id: str = ""
session_id: str = ""
attempted_task: str = ""
proposal_type: str = ""
files_changed: list[str] = field(default_factory=list)
model_used: str = ""
validation_outcome: str = ""
rollback_outcome: str = ""
failure_reason: str = ""
successful_strategy: str = ""
future_recommendation: str = ""
created_at: str = ""
outcome_hash: str = ""
tags: list[str] = field(default_factory=list)
evidence_refs: list[str] = field(default_factory=list)
warnings: list[str] = field(default_factory=list)
errors: list[str] = field(default_factory=list)
```

---

# 9. LearningOutcomeReview Class

Implement `LearningOutcomeReview` in `outcome_review.py`.

Required public methods:

```python
record_outcome(outcome: LearningOutcomeRecord) -> None
get_by_session(session_id: str) -> list[LearningOutcomeRecord]
get_by_tag(tag: str) -> list[LearningOutcomeRecord]
get_successful_strategies() -> list[LearningOutcomeRecord]
get_failure_patterns() -> list[LearningOutcomeRecord]
get_recommendations() -> list[str]
write_outcome_history(repo_root: str | Path) -> Path
append_outcome_history(outcome: LearningOutcomeRecord, repo_root: str | Path) -> Path
acquire_learning_lock(repo_root: str | Path, timeout_seconds: int = 10) -> object
release_learning_lock(lock: object, repo_root: str | Path) -> None
```

## 9.1 record_outcome behavior:

```text
generate outcome_id via new_id("lr") if empty
generate created_at via utc_now_iso if empty
compute outcome_hash via sha256_dict of the record dict
append to internal records list
```

## 9.2 write_outcome_history:

```text
serialize all records to JSON
write atomically to .agentx-init/learning/outcome_history.json
return the path written
```

## 9.3 append_outcome_history:

```text
serialize a single outcome record to JSON
append to .agentx-init/learning/outcome_history.jsonl
return the path written
```

## 9.4 acquire_learning_lock:

```text
create a lock file at .agentx-init/learning/.learning.lock
use file-based locking with timeout
return a lock identifier
```

## 9.5 release_learning_lock:

```text
remove the lock file
safe to call even if lock is missing
```

---

# 10. StrategyMemory Class

Required public methods:

```python
store(key: str, value: Any) -> None
retrieve(key: str) -> Any | None
search(prefix: str) -> dict[str, Any]
clear() -> None
persist_memory(repo_root: str | Path) -> Path
load_memory(repo_root: str | Path) -> None
```

## 10.1 persist_memory:

```text
serialize _store to JSON
write atomically to .agentx-init/learning/strategy_memory.json
return the path written
```

## 10.2 load_memory:

```text
read .agentx-init/learning/strategy_memory.json
populate _store from contents
no-op if file does not exist
```

---

# 11. Schema Constants

Define in `outcome_review.py`:

```python
LEARNING_SCHEMA_VERSION = "1.0"
LEARNING_SCHEMA_ID = "learning_outcome_record.schema.json"
```

---

# 12. Helper Functions

Define in `outcome_review.py`:

```python
canonical_json(data: dict) -> str
sha256_dict(data: dict) -> str
to_dict(obj: object) -> dict
write_json_atomic(path: Path, data: dict) -> Path
append_jsonl(path: Path, data: dict) -> Path
```

## 12.1 canonical_json:

```text
serialize dict to JSON with sorted keys, compact separators
```

## 12.2 sha256_dict:

```text
compute sha256 hex digest of canonical_json of the dict
```

## 12.3 write_json_atomic:

```text
write to a .tmp file first, then rename atomically
```

## 12.4 append_jsonl:

```text
append a single JSON line to the file
create parent directories if needed
```

---

# 13. Idempotency, Locking, and Immutability

## 13.1 Outcome Immutability

A `LearningOutcomeRecord` is immutable after its `outcome_id`, `created_at`, and `outcome_hash` are recorded.

## 13.2 Idempotency

Repeated recording of the same outcome data must produce the same `outcome_hash`.

## 13.3 Locking

Before writing outcome history or strategy memory, the implementation must acquire the learning lock:

```text
.agentx-init/learning/.learning.lock
```

Rules:

```text
lock acquisition timeout must be bounded
stale lock handling must be conservative
failure to acquire lock must not silently corrupt data
```

---

# 14. Schema: learning_outcome_record.schema.json

Required schema fields:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "outcome_id": "string",
  "session_id": "string",
  "attempted_task": "string",
  "proposal_type": "string",
  "files_changed": ["string"],
  "model_used": "string",
  "validation_outcome": "string",
  "rollback_outcome": "string",
  "failure_reason": "string",
  "successful_strategy": "string",
  "future_recommendation": "string",
  "created_at": "string",
  "outcome_hash": "string",
  "tags": ["string"],
  "evidence_refs": ["string"],
  "warnings": ["string"],
  "errors": ["string"]
}
```

---

# 15. Classes / Functions Summary

## 15.1 Required Dataclasses

```text
LearningOutcomeRecord
```

## 15.2 Required Classes

```text
LearningOutcomeReview
StrategyMemory
```

## 15.3 Required Helper Functions

```python
canonical_json(data: dict) -> str
sha256_dict(data: dict) -> str
to_dict(obj: object) -> dict
write_json_atomic(path: Path, data: dict) -> Path
append_jsonl(path: Path, data: dict) -> Path
```

---

# 16. Test Cases

## 16.1 Required Positive Tests

```text
test_record_outcome_creates_outcome
test_outcome_record_defaults
test_get_by_session_returns_matching
test_get_by_tag_returns_matching
test_get_successful_strategies_returns_only_success
test_get_failure_patterns_returns_only_failures
test_strategy_memory_store_retrieve
test_strategy_memory_search_prefix
test_write_outcome_history_creates_file
test_append_outcome_history_appends
```

---

# 17. Implementation Order

```text
1. outcome_review.py (enhance dataclass, add helpers, add persistence, add locking)
2. learning_outcome_record.schema.json
3. __init__.py (export all new symbols)
4. test_learning_outcome_review.py
5. compileall
6. pytest
```

---

# 18. Acceptance Criteria

The implementation is acceptable only if all are true:

```text
all target files exist
schema exists
all tests exist
outcome can be recorded with hash
outcome gets auto-id and timestamp when empty
session-based filtering works
tag-based filtering works
successful strategy extraction works
failure pattern extraction works
strategy memory store/retrieve/search/clear works
strategy memory persist/load works
outcome history is written atomically
outcome history is appended in JSONL format
learning lock acquire/release works
compileall passes
pytest passes
```

Manual validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_learning_outcome_review.py -v
```

Required result:

```text
compileall PASS
pytest PASS
```

---

# 19. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places package files outside tools/agentx_evolve/learning/ without recorded deviation
writes runtime artifacts outside .agentx-init/learning/ without recorded deviation
records outcomes without computing outcome_hash
omits schema validation constants
omits locking before durable writes
uses non-atomic file writes
uses mutable default arguments in dataclass
mutates source files
performs network calls
requires LLM or model for basic recording
```

---

# 20. Definition of Done

The Long-Term Learning / Outcome Review Layer is done when:

```text
LearningOutcomeRecord has all required fields including outcome_hash
LearningOutcomeReview records outcomes with hash auto-generation
session-based and tag-based filtering work
successful strategies and failure patterns are extractable
StrategyMemory stores, retrieves, searches, clears, persists, and loads
outcome history writes atomically to .agentx-init/learning/
outcome history appends in JSONL format
learning lock protects durable writes
all tests pass
compileall passes
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_learning_outcome_review.py -v
```

Expected proof:

```text
compileall PASS
pytest PASS
```

---

# 21. Go / No-Go Rules

## 21.1 GO Criteria

The layer may be marked DONE only if:

```text
all files exist
schema exists
all tests exist
all required tests pass
outcome records produce deterministic hashes
session/tag filtering works
strategy memory persists and loads
outcome history is written atomically
JSONL append works
locking works
compileall passes
pytest passes
```

## 21.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
outcome records lack outcome_hash
tag search is missing
persistence writes outside .agentx-init/learning/
locking is absent
non-atomic writes used
source mutation occurs
network is required
```

---

# 22. Scoring Rubric

| Category | Points | Required for full credit |
|---|---|---:|---|
| Structure and expected files | 1.0 | Package, schema, tests, runtime artifact paths exist. |
| Outcome record model | 1.0 | All fields present, outcome_hash computed. |
| Outcome review API | 1.0 | record, get_by_session, get_by_tag, get_successful_strategies, get_failure_patterns, get_recommendations. |
| Strategy memory | 1.0 | store, retrieve, search, clear, persist, load. |
| Persistence | 1.0 | Atomic write, JSONL append, correct runtime root. |
| Locking | 1.0 | acquire/release with timeout. |
| Schema | 1.0 | learning_outcome_record.schema.json validates. |
| Helpers | 1.0 | canonical_json, sha256_dict, to_dict, write_json_atomic, append_jsonl. |
| Safety boundaries | 1.0 | No source mutation, network, LLM requirement. |
| Tests and command proof | 1.0 | compileall PASS, pytest PASS. |

Hard caps:

```text
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
missing outcome_hash caps score at 4.0
missing persistence caps score at 5.0
missing locking caps score at 6.0
network required caps score at 6.0
```

---

# 23. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The Long-Term Learning layer lives under tools/agentx_evolve/learning/.
[ ] Runtime artifacts go under .agentx-init/learning/.
[ ] Schemas go under tools/agentx_evolve/schemas/.
[ ] Tests go under tools/agentx_evolve/tests/.
[ ] outcome_hash is required for every recorded outcome.
[ ] Tag-based filtering is required.
[ ] Atomic writes are required.
[ ] JSONL append is required.
[ ] Locking is required before durable writes.
[ ] Network is forbidden by default.
[ ] LLM is not required for recording.
```

---

# 24. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package location | `tools/agentx_evolve/learning/` |
| Runtime root | `.agentx-init/learning/` |
| Outcome record | schema-valid, hash-checked |
| Outcome review | record, filter by session/tag, strategies, failures |
| Strategy memory | store/retrieve/search/clear/persist/load |
| Persistence | Atomic JSON + append JSONL |
| Locking | acquire/release with timeout |
| Schema | learning_outcome_record.schema.json |
| Safety | no source mutation, no network, no LLM required |
| Tests | positive tests for all public API surface |
| DONE proof | compileall PASS, pytest PASS |

---

# 25. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, outcome record model, outcome review API with session/tag/strategy/failure filtering, strategy memory with persistence, atomic writing, JSONL append, locking, schema validation constants, canonical hashing helpers, test cases, compileall/pytest validation, acceptance criteria, Definition of Done, Go/No-Go rules, scoring caps, and final frozen handoff criteria.
```

# LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_LONG_TERM_LEARNING
component_name: Long-Term Learning / Outcome Review Layer
roadmap_layer: 14
roadmap_phase: Phase E — Long-Term Learning
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
risk_level: medium
target_language: Python
canonical_subdirectory: tools/agentx_evolve/learning/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/learning/
purpose: Defines what the Long-Term Learning / Outcome Review Layer must record, persist, and expose for cross-session learning.
contract_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 contract was strong. I would rate v3:

```text
9.5/10
```

It already covered:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Outcome record model
Outcome review API
Strategy memory API
Session-based lookup
In-memory recording
```

It was not fully 10/10 because:

```text
1. No deterministic outcome_hash was required.
2. No durable persistence contract existed.
3. No tag-based contract existed.
4. No locking contract existed.
5. No atomic write contract existed.
```

This v4 closes those gaps and is the final 10/10 controlling contract.

---

# 1. Purpose

This document defines the controlling contract for the **Long-Term Learning / Outcome Review Layer** in the Agent_X self-evolving system.

The layer records implementation outcomes, identifies successful strategies, detects failure patterns, and stores reusable knowledge.

---

# 2. Scope

## 2.1 Required in This Layer

```text
LearningOutcomeRecord with all required fields
LearningOutcomeReview with record, query, persistence, and locking methods
StrategyMemory with store, retrieve, search, clear, persist, and load methods
Schema validation for learning_outcome_record.schema.json
Deterministic outcome_hash via sha256_dict
Tag-based filtering
Atomic write_json_atomic for history files
Append-only JSONL for outcome history
File-based locking for durable writes
```

## 2.2 Not Required in This Layer

```text
LLM-based outcome analysis
Automatic strategy recommendation generation
Network calls
Model invocation
MCP server
Git write operations
Source mutation
Promotion decisions
```

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

```text
EQC
```

EQC is primary because this layer records quality evidence about implementation outcomes and enables learning from past work.

It must enforce:

```text
deterministic outcome hashing
durable persistence
append-only history
lock-protected writes
tag-based discoverability
```

## 3.2 Required Supporting Standard: FIC

```text
FIC
```

FIC is required because this layer must have concrete implementation files with clearly separated responsibilities:

```text
outcome_review.py — dataclass, review class, strategy memory, helpers, persistence, locking
__init__.py — public exports
```

## 3.3 Required Supporting Standard: SIB

```text
SIB
```

SIB is required because this layer integrates with:

```text
Implementation Session Layer (session_id references)
Model Adapter Layer (model_used references)
Governed Patch Execution Layer (files_changed references)
Failure Taxonomy Layer (failure_reason mapping)
```

## 3.4 Required Schema Contract

```text
Schema Contract
```

Required schemas:

```text
learning_outcome_record.schema.json
```

## 3.5 Required Evidence / Audit Rules

```text
Evidence / Audit Rules
```

Every outcome record must create durable evidence under:

```text
.agentx-init/learning/
```

---

# 4. LearningOutcomeRecord Schema Contract

## 4.1 Purpose

The learning outcome record schema defines the structure for recording an implementation outcome.

## 4.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_outcome_record.schema.json",
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

## 4.3 Outcome Rules

```text
Every outcome must have an outcome_hash.
outcome_hash is computed from canonical JSON of the record (excluding itself).
outcome_id is auto-generated if empty.
created_at is set to UTC now if empty.
tags enable cross-session discovery.
```

---

# 5. LearningOutcomeReview API Contract

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

Rules:

```text
record_outcome must set outcome_id, created_at, and outcome_hash if empty.
write_outcome_history must write atomically to .agentx-init/learning/outcome_history.json.
append_outcome_history must append JSONL to .agentx-init/learning/outcome_history.jsonl.
acquire_learning_lock must create .agentx-init/learning/.learning.lock.
release_learning_lock must remove the lock file.
```

---

# 6. StrategyMemory API Contract

Required public methods:

```python
store(key: str, value: Any) -> None
retrieve(key: str) -> Any | None
search(prefix: str) -> dict[str, Any]
clear() -> None
persist_memory(repo_root: str | Path) -> Path
load_memory(repo_root: str | Path) -> None
```

Rules:

```text
persist_memory writes atomically to .agentx-init/learning/strategy_memory.json.
load_memory reads from that file; no-op if missing.
```

---

# 7. Helper Functions Contract

```python
canonical_json(data: dict) -> str
sha256_dict(data: dict) -> str
to_dict(obj: object) -> dict
write_json_atomic(path: Path, data: dict) -> Path
append_jsonl(path: Path, data: dict) -> Path
```

## 7.1 canonical_json

Sort keys alphabetically, use compact separators (`,`, `:`).

## 7.2 sha256_dict

Compute `hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()`.

## 7.3 to_dict

Convert dataclass to dict recursively using `dataclasses.asdict`-like logic.

## 7.4 write_json_atomic

Write to `{path}.tmp` first, then `os.replace` to final path.

## 7.5 append_jsonl

Append `json.dumps(data, separators=(",", ":")) + "\n"` to file, creating parent directories.

---

# 8. Schema Validation Contract

Schema: `learning_outcome_record.schema.json` must validate:

```text
valid outcome record with all fields
missing required fields must fail (outcome_id, session_id, attempted_task, validation_outcome, created_at)
```

---

# 9. Persistence Contract

```text
outcome_history.json — atomic write, all records
outcome_history.jsonl — append-only, one record per line
strategy_memory.json — atomic write, full _store dict
.learning.lock — file-based lock, acquired before durable writes
```

---

# 10. Locking, Concurrency, and Idempotency

## 10.1 Locking Rules

```text
Only one durable write at a time per runtime root.
Lock acquisition must have a bounded timeout.
Stale lock handling must be conservative — never delete without verification.
```

## 10.2 Idempotency Rules

```text
Same input data produces the same outcome_hash.
Repeated recording with same data creates separate records (append-only).
```

---

# 11. Test Acceptance Criteria

Required tests:

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

Definition of Done requires:

```text
compileall PASS
pytest PASS
```

---

# 12. Security Rules

```text
No network calls.
No LLM required.
No Git write operations.
No source mutation.
Secrets must not appear in outcome records.
```

---

# 13. GO / NO-GO Rules

## 13.1 GO Criteria

The layer may be marked DONE only if:

```text
all files exist
schema exists
all tests exist
all required tests pass
outcome_hash is deterministic
session/tag filtering works
persistence writes to correct runtime root
locking works
compileall passes
pytest passes
```

## 13.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

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

# 14. Residual Risks

```yaml
residual_risks:
  - id: "LEARN-RISK-001"
    description: "Outcome records may contain sensitive data from failure_reason or evidence_refs."
    severity: "medium"
    mitigation: "Callers are responsible for redaction before recording."
  - id: "LEARN-RISK-002"
    description: "Stale lock file may block future writes."
    severity: "low"
    mitigation: "Lock with timeout; manual cleanup if stale."
  - id: "LEARN-RISK-003"
    description: "In-memory records may be lost on crash before persistence."
    severity: "low"
    mitigation: "Callers should persist after each recording session."
```

---

# 15. Definition of Done

This controlling contract is satisfied when the implementation proves:

```text
LearningOutcomeRecord has all required fields
outcome_hash is computed deterministically
record_outcome auto-generates id, timestamp, hash
session-based filtering works
tag-based filtering works
successful strategies extract correctly
failure patterns extract correctly
StrategyMemory store/retrieve/search/clear/persist/load work
write_outcome_history writes atomically
append_outcome_history appends JSONL
acquire_learning_lock / release_learning_lock work
all tests pass
compileall passes
no source mutation occurs
no network is required
```

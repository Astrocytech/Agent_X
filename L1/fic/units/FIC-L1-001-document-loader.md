# FIC-L1-001: L1 Document Loader

---
schema: "agent-x-l1-eqc-fic/v0.6"
fic_id: "FIC-L1-001"
unit_id: "UNIT-L1-001"
version: "v0.6.0"
status: "ready-for-code"
target_file: "L1/controller/document_loader.py"
target_language: "python"
artifact_type: "production"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-file"
owner: "Agent_X L1"
permitted_files:
  - "L1/controller/document_loader.py"
  - "L1/tests/test_document_loader.py"
required_checks:
  - "python -m compileall L1"
  - "pytest L1/tests/test_document_loader.py -q"
---

## A. Identity

```yaml
fic_id: "FIC-L1-001"
unit_id: "UNIT-L1-001"
target_file: "L1/controller/document_loader.py"
target_language: "python"
artifact_type: "production"
status: "ready-for-code"
version: "v0.6.0"
owner: "Agent_X L1"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-file"
```

---

## B. Authority and Source Hierarchy

```yaml
authority:
  governing_docs:
    - doc_id: "AGENT-X-L0-CONTRACTS"
      path: "L0/"
      authority_level: "constitutional"
    - doc_id: "AGENT-X-L1-SYSTEM-GOAL"
      path: "L1/docs/00_L1_SYSTEM_GOAL.md"
      authority_level: "architecture"
    - doc_id: "AGENT-X-L1-ARCHITECTURE"
      path: "L1/docs/02_L1_ARCHITECTURE_CONTRACT.md"
      authority_level: "architecture"
    - doc_id: "AGENT-X-L1-UNIT-DAG"
      path: "L1/docs/04_L1_UNIT_DAG.md"
      authority_level: "subsystem"
  conflict_resolution:
    rule: "higher_authority_wins"
    unresolved_conflict_status: "BLOCKED_SOURCE_CONFLICT"
  stale_doc_policy:
    stale_behavior: "BLOCKED_MISSING_CONTEXT"
```

---

## C. File Purpose

`document_loader.py` loads approved L1 control-plane documents from declared paths and returns immutable structured document records for downstream L1 units.

It exists so that later L1 units do not manually read arbitrary files or treat unapproved repository text as authoritative instructions.

---

## D. Non-Goals

This file must not:

- interpret semantic meaning of documents;
- classify goals;
- generate FICs;
- validate FIC readiness;
- modify documents;
- write files;
- execute shell commands;
- call network resources;
- inspect arbitrary repository files outside declared allowed paths;
- import L0 runtime internals;
- import L2 modules;
- use environment variables as hidden inputs;
- cache loaded document content globally;
- silently skip unreadable documents;
- normalize or rewrite document contents beyond UTF-8 decoding.

---

## E. Layer, Ownership, and Placement

```yaml
architecture:
  layer: 1
  architectural_role: "control-plane document loading"
  module_boundary: "L1/controller"
  owns_state: false
  state_owner: "none"
  allowed_callers:
    - "L1 controller/orchestrator"
    - "L1 tests"
  forbidden_callers:
    - "L0 runtime"
    - "L2 profiles"
  allowed_callees:
    - "dataclasses"
    - "hashlib"
    - "pathlib"
    - "typing"
  forbidden_callees:
    - "subprocess"
    - "requests"
    - "urllib"
    - "socket"
    - "http"
    - "L0"
    - "L2"
```

---

## F. Public Surface Contract

```yaml
public_surface:
  module_exports:
    - "DEFAULT_MAX_DOCUMENT_BYTES"
    - "DocumentRecord"
    - "DocumentLoaderError"
    - "DocumentRootError"
    - "DocumentPathError"
    - "DocumentLoadError"
    - "load_document"
    - "load_documents"

  constants:
    - name: "DEFAULT_MAX_DOCUMENT_BYTES"
      value: 1048576
      purpose: "Default maximum size for one loaded document, in bytes."
      stability: "experimental"

  classes:
    - name: "DocumentRecord"
      purpose: "Immutable record describing a loaded control-plane document."
      constructor_signature: "DocumentRecord(path: str, content: str, size_bytes: int, sha256: str, exists: bool = True)"
      fields:
        - "path: str  # normalized POSIX-style relative path from root"
        - "content: str"
        - "size_bytes: int"
        - "sha256: str  # 64-character lowercase hexadecimal SHA-256 digest of raw bytes"
        - "exists: bool"
      dataclass_frozen: true
      equality_semantics: "value equality from frozen dataclass fields"
      stability: "experimental"

    - name: "DocumentLoaderError"
      purpose: "Base exception for document loader failures."
      constructor_signature: "DocumentLoaderError(message: str)"
      stability: "experimental"

    - name: "DocumentRootError"
      purpose: "Raised when the provided root is missing, invalid, or not a directory."
      constructor_signature: "DocumentRootError(message: str)"
      stability: "experimental"

    - name: "DocumentPathError"
      purpose: "Raised when a document path is invalid, absolute, or escapes the declared root."
      constructor_signature: "DocumentPathError(message: str)"
      stability: "experimental"

    - name: "DocumentLoadError"
      purpose: "Raised when a declared document cannot be read as a regular bounded UTF-8 file."
      constructor_signature: "DocumentLoadError(message: str)"
      stability: "experimental"

  functions:
    - name: "load_document"
      signature: "load_document(path: str, *, root: str | pathlib.Path, max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES) -> DocumentRecord"
      purpose: "Load one declared document path under the provided root."
      stability: "experimental"

    - name: "load_documents"
      signature: "load_documents(paths: list[str], *, root: str | pathlib.Path, max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES) -> list[DocumentRecord]"
      purpose: "Load multiple declared document paths under the provided root in deterministic input order."
      stability: "experimental"

  cli_commands: []
  config_keys: []
  events: []
```

No other public functions, classes, constants, CLI commands, config keys, events, or module-level side effects are allowed. The module must define `__all__` matching `module_exports` exactly. Imported implementation helpers must not leak as public symbols; imports should use private aliases where needed, such as `_Path`, `_hashlib`, or `_dataclass`, or must otherwise be hidden from the module public surface.

---

## G. Compatibility and Versioning Contract

```yaml
compatibility:
  backward_compatible: true
  public_surface_change: false
  migration_required: false
  deprecation_required: false
  version_impact: "minor-initial"
  compatibility_tests_required: false
  affected_callers:
    - "future L1 controller/orchestrator"
    - "future L1 repo state reader"
```

Any future public surface change must update this FIC before code changes.

---

## H. Internal Helper Policy

```yaml
internal_helpers:
  allowed: true
  rules:
    - "Helpers must be private/internal by leading underscore."
    - "Helpers must support only declared public functions."
    - "Helpers must not add hidden file-loading modes."
    - "Helpers must not expose additional public symbols through __all__."
  max_helper_count: 5
  max_helper_complexity: "simple path validation, size validation, hash computation, or read helper only"
```

---

## I. Inputs

```yaml
inputs:
  - name: "path"
    type: "str"
    source: "caller"
    required: true
    validation_rule: "must be a relative path that resolves under root"
    trust_level: "untrusted"

  - name: "paths"
    type: "list[str]"
    source: "caller"
    required: true
    validation_rule: "must be a list whose items each pass the same validation as load_document path"
    trust_level: "untrusted"

  - name: "root"
    type: "str | pathlib.Path"
    source: "caller"
    required: true
    validation_rule: "must be non-empty after conversion to a filesystem path, must exist, and must resolve to a directory; root symlink to a directory is allowed after resolution"
    trust_level: "internal"

  - name: "max_bytes"
    type: "int"
    source: "caller or default"
    required: false
    validation_rule: "must be an integer greater than or equal to 0; bool is invalid even though bool subclasses int in Python"
    trust_level: "internal"
```

---

## J. Outputs and Side Effects

```yaml
outputs:
  - name: "DocumentRecord"
    type: "frozen dataclass"
    destination: "return"
    success_shape: "exists=true, content populated as str, size_bytes >= 0, sha256 is lowercase hex digest of raw bytes"
    failure_shape: "raises declared exception"
    ordering_rule: "not applicable for single document"

  - name: "list[DocumentRecord]"
    type: "list"
    destination: "return"
    success_shape: "records returned in the same order as input paths"
    failure_shape: "raises declared exception and returns no partial list"
    ordering_rule: "same order as input paths"

side_effects:
  allowed: true
  declared_effects:
    - "read-only filesystem access to declared paths under root"
```

No file writes are allowed.

---

## K. State Contract

```yaml
state:
  owns_state: false
  state_items: []
```

The module must not use mutable global state, caches, hidden registries, environment variables, or process-wide configuration.

---

## L. Dependency Contract

```yaml
dependencies:
  allowed_imports:
    - "dataclasses"
    - "hashlib"
    - "pathlib"
    - "typing"
  import_style_rules:
    - "Imported helper names must not become public module symbols."
    - "Use private aliases or module imports where needed."
    - "No from-import may create a non-declared public symbol unless it is assigned to a private alias."
  forbidden_imports:
    - "os"
    - "os.system"
    - "subprocess"
    - "requests"
    - "urllib"
    - "socket"
    - "http"
    - "L0"
    - "L2"
  dynamic_imports_allowed: false
```

The implementation must not import L0 or L2 packages. L1 reads L0 only through declared filesystem inspection in later units, not through runtime imports.

---

## M. Existing-Code Inspection Contract

```yaml
existing_code_inspection:
  required: true
  reason: "new-file implementation still must confirm whether target or test file already exists"
  no_change_allowed: true
  must_confirm:
    - "target file does not already exist, or if it exists, whether it already satisfies this FIC"
    - "test file does not already exist, or if it exists, whether it should be updated"
```

If existing code already satisfies the FIC, the correct status is `NO_CHANGE` with evidence.

---

## N. Procedure

### `load_document(path, *, root, max_bytes=DEFAULT_MAX_DOCUMENT_BYTES)`

```text
1. Confirm root is provided and is a string or `pathlib.Path` value.
2. Convert root to a filesystem path and reject empty roots.
3. Resolve root as an absolute path.
4. Confirm root exists and resolves to a directory. A root symlink to a directory is allowed after resolution.
5. Confirm max_bytes is an integer >= 0 and is not bool. `max_bytes=0` allows only empty files.
6. Confirm path is provided and is a string.
7. Reject empty paths.
8. Reject absolute document paths.
9. Resolve root / path.
10. Reject the resolved document path if it escapes root after resolution.
11. Reject the path if it does not exist.
12. Reject the path if it is not a regular file.
13. Read raw bytes from the file only after path validation passes.
14. Reject the file if raw byte length exceeds max_bytes.
15. Decode the raw bytes as UTF-8 text.
16. Compute sha256 as lowercase hex digest from the raw bytes.
17. Compute normalized_relative_path as a POSIX-style path relative to root.
18. Return DocumentRecord(path=normalized_relative_path, content=content, size_bytes=len(raw_bytes), sha256=sha256, exists=true).
```

### `load_documents(paths, *, root, max_bytes=DEFAULT_MAX_DOCUMENT_BYTES)`

```text
1. Confirm paths is a list.
2. Reject non-list paths input.
3. Preserve input order and multiplicity; duplicate paths are allowed and must produce duplicate records.
4. For each path in input order, call load_document(path, root=root, max_bytes=max_bytes).
5. If any path fails, raise the declared exception and return no partial result.
6. Return the list of DocumentRecord values in the same order as the input paths.
```

---

## O. Invariants

```yaml
invariants:
  - id: "FIC-L1-001-INV-001"
    statement: "A document path must never resolve outside the declared root."
    enforcement: "code+test"
    violation_behavior: "raise DocumentPathError"

  - id: "FIC-L1-001-INV-002"
    statement: "The loader must not write files."
    enforcement: "code+test+review"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-003"
    statement: "The loader must not import L0 or L2 modules."
    enforcement: "static review+test"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-004"
    statement: "For the same root and paths, output order must be deterministic."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-005"
    statement: "The loader must not depend on wall-clock time, randomness, network, environment variables, or shell execution."
    enforcement: "static review+test"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-006"
    statement: "DocumentRecord must be immutable after construction."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-007"
    statement: "Loaded content hash must be computed from raw bytes before UTF-8 decoding."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-008"
    statement: "Returned DocumentRecord.path must be normalized, relative to root, and POSIX-style."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-009"
    statement: "Exception messages must not include document content, raw bytes, secrets, or absolute escaped target paths."
    enforcement: "test+review"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-010"
    statement: "Duplicate paths in load_documents must preserve multiplicity and order."
    enforcement: "test"
    violation_behavior: "test failure"
```

---

## P. Error and Failure Behavior

```yaml
errors:
  - condition: "root is missing, empty, wrong type, invalid, or not a directory"
    behavior: "raise"
    error_type: "DocumentRootError"
    recoverable: false

  - condition: "max_bytes is not an integer, is bool, or is negative"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "path is missing, empty, not a string, absolute, or escapes root"
    behavior: "raise"
    error_type: "DocumentPathError"
    recoverable: false

  - condition: "paths is not a list"
    behavior: "raise"
    error_type: "DocumentPathError"
    recoverable: false

  - condition: "path does not exist or is not a regular file"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "file byte length exceeds max_bytes"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "file cannot be decoded as UTF-8"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false
```

No silent fallback behavior is allowed. Exception messages must identify the error category without exposing document content, raw bytes, secrets, or absolute escaped target paths.

---

## Q. Security Contract

```yaml
security:
  handles_sensitive_data: false
  input_validation_required: true
  authorization_required: false
  forbidden_operations:
    - "path traversal"
    - "network access"
    - "shell execution"
    - "unsafe deserialization"
    - "writing files"
    - "environment-variable control"
    - "reading absolute paths supplied by caller"
    - "exposing document contents or raw bytes in exception messages"
```

The loader must treat caller-provided paths as untrusted.

---

## R. Performance and Resource Budget

```yaml
performance:
  expected_complexity: "O(n) in total bytes read"
  max_input_size: "max_bytes per file; default 1048576 bytes"
  memory_budget: "No hidden global copies; only returned content is retained."
  timeout_budget: "No timeout in v0.5.0."
  batching_required: false
  caching_allowed: false
  hot_path: false
  benchmark_required: false
```

---

## S. Determinism and Reproducibility

```yaml
determinism:
  deterministic_required: true
  time_policy: "not-used"
  randomness_policy: "not-used"
  ordering_policy: "preserve input path order"
  floating_point_policy: "not-applicable"
  concurrency_policy: "no shared mutable state"
```

---

## T. Observability and Tracing

```yaml
observability:
  logs_allowed: false
  required_log_events: []
  metrics: []
  traces: []
  forbidden_log_content:
    - "document content"
    - "personal data"
    - "secrets"
```

The loader must not log document contents.

---

## U. Edge Cases

| ID | Case | Input/State | Expected Behavior | Test Required | Waiver Allowed |
|---|---|---|---|---:|---:|
| EC-L1-001-001 | Missing root | `root=""` | raise `DocumentRootError` | yes | no |
| EC-L1-001-002 | Root not directory | root points to file | raise `DocumentRootError` | yes | no |
| EC-L1-001-003 | Negative max bytes | `max_bytes=-1` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-004 | Non-string path | `path=123` | raise `DocumentPathError` | yes | no |
| EC-L1-001-005 | Empty path | `path=""` | raise `DocumentPathError` | yes | no |
| EC-L1-001-006 | Absolute path | `/tmp/x.md` | raise `DocumentPathError` | yes | no |
| EC-L1-001-007 | Path traversal | `../x.md` | raise `DocumentPathError` | yes | no |
| EC-L1-001-008 | Symlink escape | symlink under root points outside root | raise `DocumentPathError` or `DocumentLoadError` before content return | yes | no |
| EC-L1-001-009 | Missing file | valid root, missing path | raise `DocumentLoadError` | yes | no |
| EC-L1-001-010 | Directory path | path points to directory | raise `DocumentLoadError` | yes | no |
| EC-L1-001-011 | Oversized file | file exceeds `max_bytes` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-012 | Non-UTF-8 file | invalid bytes | raise `DocumentLoadError` | yes | no |
| EC-L1-001-013 | Empty file | file exists, zero bytes | return content `""`, size `0`, valid SHA-256 | yes | no |
| EC-L1-001-014 | Multiple paths | list of valid paths | preserve input order | yes | no |
| EC-L1-001-015 | Non-list paths | `paths="abc.md"` | raise `DocumentPathError` | yes | no |
| EC-L1-001-016 | Duplicate paths | same valid path appears twice | return two corresponding records in the same positions | yes | no |
| EC-L1-001-017 | Boolean max bytes | `max_bytes=True` or `False` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-018 | Platform separator | path contains platform separator but resolves under root | returned record path uses POSIX-style relative format | yes | no |
| EC-L1-001-019 | Error message safety | invalid file/path error | message contains no content, raw bytes, secrets, or escaped absolute target | yes | no |
| EC-L1-001-020 | Zero max bytes with empty file | `max_bytes=0`, empty file | return valid empty `DocumentRecord` | yes | no |
| EC-L1-001-021 | Zero max bytes with non-empty file | `max_bytes=0`, non-empty file | raise `DocumentLoadError` | yes | no |
| EC-L1-001-022 | Path-like root | `root` is a `Path` object | accepted if it resolves to a directory | yes | no |
| EC-L1-001-023 | Root symlink to directory | `root` is symlink to valid directory | allowed after resolution; output path remains relative | yes | no |

---

## V. Test Contract

Required test file:

```text
L1/tests/test_document_loader.py
```

Required tests:

```yaml
tests:
  required_unit_tests:
    - id: "TEST-L1-001-001"
      name: "loads a valid UTF-8 document"
    - id: "TEST-L1-001-002"
      name: "loads an empty UTF-8 document"
    - id: "TEST-L1-001-003"
      name: "computes SHA-256 from raw bytes"
    - id: "TEST-L1-001-004"
      name: "DocumentRecord is frozen"
    - id: "TEST-L1-001-005"
      name: "preserves input order for multiple documents"
    - id: "TEST-L1-001-006"
      name: "rejects non-list paths input"
    - id: "TEST-L1-001-007"
      name: "rejects non-string path"
    - id: "TEST-L1-001-008"
      name: "rejects empty path"
    - id: "TEST-L1-001-009"
      name: "rejects absolute path"
    - id: "TEST-L1-001-010"
      name: "rejects path traversal outside root"
    - id: "TEST-L1-001-011"
      name: "rejects symlink escape outside root where platform supports symlink"
    - id: "TEST-L1-001-012"
      name: "rejects missing root"
    - id: "TEST-L1-001-013"
      name: "rejects root that is a file"
    - id: "TEST-L1-001-014"
      name: "rejects missing document"
    - id: "TEST-L1-001-015"
      name: "rejects directory document path"
    - id: "TEST-L1-001-016"
      name: "rejects file larger than max_bytes"
    - id: "TEST-L1-001-017"
      name: "rejects invalid max_bytes"
    - id: "TEST-L1-001-018"
      name: "does not write files"
    - id: "TEST-L1-001-019"
      name: "does not use forbidden imports"
    - id: "TEST-L1-001-020"
      name: "__all__ matches declared module exports"
    - id: "TEST-L1-001-021"
      name: "duplicate paths preserve multiplicity and order"
    - id: "TEST-L1-001-022"
      name: "bool max_bytes is rejected"
    - id: "TEST-L1-001-023"
      name: "returned path is normalized POSIX-style relative path"
    - id: "TEST-L1-001-024"
      name: "error messages do not expose document content or escaped absolute target paths"
    - id: "TEST-L1-001-025"
      name: "non-declared imported helper names do not leak through __all__"
    - id: "TEST-L1-001-026"
      name: "max_bytes zero allows empty file and rejects non-empty file"
    - id: "TEST-L1-001-027"
      name: "path-like root is accepted when it resolves to a directory"
    - id: "TEST-L1-001-028"
      name: "root symlink to directory is allowed while document symlink escape remains blocked"
    - id: "TEST-L1-001-029"
      name: "rejects invalid UTF-8 bytes"
  required_negative_tests:
    - "path traversal"
    - "symlink escape"
    - "missing file"
    - "invalid root"
    - "invalid max_bytes"
    - "non-list paths input"
    - "oversized file"
    - "bool max_bytes"
    - "unsafe error-message leakage"
    - "invalid UTF-8 bytes"
  required_property_tests: []
  required_integration_tests: []
```

Tests must verify behavior, not merely symbol existence.

---

## W. Examples and Test Oracles

```yaml
examples:
  - name: "basic success"
    input:
      root: "/repo"
      path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    expected_output:
      exists: true
      size_bytes: ">= 0"
      sha256: "lowercase hex SHA-256 over raw bytes"
      content_type: "str"

  - name: "path traversal blocked"
    input:
      root: "/repo"
      path: "../secret.txt"
    expected_error: "DocumentPathError"

test_oracles:
  - oracle_type: "exact-error"
    applies_to: "invalid path, invalid root, oversized file, invalid max_bytes, and invalid UTF-8 cases"
    pass_rule: "declared exception type is raised"
  - oracle_type: "exact-output"
    applies_to: "successful load"
    pass_rule: "content, size_bytes, exists, and sha256 match the fixture"
  - oracle_type: "property"
    applies_to: "multiple document loading"
    pass_rule: "output order equals input order"
  - oracle_type: "static"
    applies_to: "forbidden imports and public surface"
    pass_rule: "forbidden import strings are absent, __all__ matches declared exports, and imported helper names do not leak as public API"
  - oracle_type: "exact-output"
    applies_to: "normalized record path"
    pass_rule: "returned DocumentRecord.path is the expected POSIX-style relative path"
  - oracle_type: "negative"
    applies_to: "exception message safety"
    pass_rule: "exception string does not contain fixture content, raw bytes, or escaped absolute target path"
```

---

## X. Document and Code Bindings

```yaml
bindings:
  governs:
    - doc_id: "AGENT-X-L1-SYSTEM-GOAL"
      anchor_id: "L1-document-control-plane"
      binding_strength: "HARD"
  implements:
    - spec_id: "UNIT-L1-001"
      section: "L1 document loading"
  validated_by:
    - test_file: "L1/tests/test_document_loader.py"
  sib_artifact_id: "AGENT_X_L1::ART-DOCUMENT-LOADER"
```

---

## Y. Change Policy

```yaml
change_policy:
  allowed_change_types:
    - "METADATA"
    - "VALIDATION"
    - "FUNCTIONAL"
  requires_fic_update_before_code_change: true
  public_surface_change_requires_version_bump: true
  behavioral_change_requires_tests: true
  refactor_requires_equivalence_evidence: true
```

---

## Z. LLM Implementation Instructions

```text
Before coding:
1. Read this FIC completely.
2. Confirm target file path.
3. Confirm all required existing symbols.
4. Confirm allowed imports.
5. Confirm public surface.
6. Confirm tests to create or update.
7. If existing code already satisfies this FIC, return NO_CHANGE with evidence.
8. If any required information is UNKNOWN, return BLOCKED.
9. Do not invent APIs, files, dependencies, or requirements.
10. Do not edit outside the declared target and test files unless this FIC allows it.
11. Produce the smallest implementation that satisfies this FIC.
12. Produce a completion record.
13. Produce a review packet.
```

---

## AA. Acceptance Criteria

```yaml
acceptance_criteria:
  - id: "AC-L1-001-001"
    text: "DocumentRecord exists as a frozen dataclass with declared fields."
  - id: "AC-L1-001-002"
    text: "Declared error classes exist."
  - id: "AC-L1-001-003"
    text: "DEFAULT_MAX_DOCUMENT_BYTES exists with value 1048576."
  - id: "AC-L1-001-004"
    text: "load_document exists with the declared signature."
  - id: "AC-L1-001-005"
    text: "load_documents exists with the declared signature."
  - id: "AC-L1-001-006"
    text: "__all__ matches the declared public module exports."
  - id: "AC-L1-001-007"
    text: "No public symbols beyond the declared public surface are introduced, except private helpers prefixed with underscore."
  - id: "AC-L1-001-008"
    text: "Absolute paths and path traversal are rejected."
  - id: "AC-L1-001-009"
    text: "File reads are constrained under the declared root."
  - id: "AC-L1-001-010"
    text: "Files larger than max_bytes are rejected."
  - id: "AC-L1-001-011"
    text: "SHA-256 is computed from raw file bytes."
  - id: "AC-L1-001-012"
    text: "No file writes occur."
  - id: "AC-L1-001-013"
    text: "No forbidden imports are present."
  - id: "AC-L1-001-014"
    text: "Required tests exist."
  - id: "AC-L1-001-015"
    text: "Declared tests pass or failures are recorded."
  - id: "AC-L1-001-016"
    text: "Completion record is produced."
  - id: "AC-L1-001-017"
    text: "Review packet is produced."
  - id: "AC-L1-001-018"
    text: "Duplicate paths preserve multiplicity and order."
  - id: "AC-L1-001-019"
    text: "Boolean max_bytes values are rejected."
  - id: "AC-L1-001-020"
    text: "Returned record paths are normalized POSIX-style relative paths."
  - id: "AC-L1-001-021"
    text: "Exception messages do not expose document contents, raw bytes, secrets, or escaped absolute target paths."
  - id: "AC-L1-001-022"
    text: "Invalid UTF-8 files are rejected with DocumentLoadError."
```

---

## AB. Completion Evidence

```yaml
completion_record:
  status: "<BLOCKED|NO_CHANGE|IMPLEMENTED_UNVALIDATED|VALIDATED|IMPLEMENTED_WITH_WAIVERS|REJECTED>"
  fic_id: "FIC-L1-001"
  fic_version: "v0.6.0"
  target_file: "L1/controller/document_loader.py"
  files_inspected: []
  files_changed: []
  public_surface_created_or_preserved: []
  tests_created_or_updated: []
  checks_run:
    - command: "python -m compileall L1"
      result: "<pass|fail|not-run>"
      evidence: ""
    - command: "pytest L1/tests/test_document_loader.py -q"
      result: "<pass|fail|not-run>"
      evidence: ""
  checks_not_run: []
  deviations_from_fic: []
  unresolved_unknowns: []
  residual_risks: []
  requires_fic_update: false
```

---

## AC. Requirement-to-Test Map

Every invariant and acceptance criterion must be mapped before implementation begins.

```yaml
requirement_to_test_map:
  invariants:
    - requirement_id: "FIC-L1-001-INV-001"
      verifies: "document path never resolves outside root"
      tests: ["TEST-L1-001-009", "TEST-L1-001-010", "TEST-L1-001-011"]
    - requirement_id: "FIC-L1-001-INV-002"
      verifies: "loader performs no file writes"
      tests: ["TEST-L1-001-018"]
      review_items: ["forbidden side effects review"]
    - requirement_id: "FIC-L1-001-INV-003"
      verifies: "loader imports neither L0 nor L2"
      tests: ["TEST-L1-001-019"]
    - requirement_id: "FIC-L1-001-INV-004"
      verifies: "output order is deterministic"
      tests: ["TEST-L1-001-005", "TEST-L1-001-021"]
    - requirement_id: "FIC-L1-001-INV-005"
      verifies: "no time, randomness, network, environment variable, or shell dependency"
      tests: ["TEST-L1-001-019"]
      review_items: ["dependency and source review"]
    - requirement_id: "FIC-L1-001-INV-006"
      verifies: "DocumentRecord is immutable"
      tests: ["TEST-L1-001-004"]
    - requirement_id: "FIC-L1-001-INV-007"
      verifies: "hash computed from raw bytes before decoding"
      tests: ["TEST-L1-001-003"]
    - requirement_id: "FIC-L1-001-INV-008"
      verifies: "record path is normalized POSIX-style relative path"
      tests: ["TEST-L1-001-023"]
    - requirement_id: "FIC-L1-001-INV-009"
      verifies: "safe exception messages"
      tests: ["TEST-L1-001-024"]
      review_items: ["error-message review"]
    - requirement_id: "FIC-L1-001-INV-010"
      verifies: "duplicate path multiplicity and order preserved"
      tests: ["TEST-L1-001-021"]

  acceptance_criteria:
    - requirement_id: "AC-L1-001-001"
      tests: ["TEST-L1-001-004"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-002"
      tests: ["TEST-L1-001-007", "TEST-L1-001-012", "TEST-L1-001-014"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-003"
      tests: ["TEST-L1-001-016"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-004"
      tests: ["TEST-L1-001-001"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-005"
      tests: ["TEST-L1-001-005", "TEST-L1-001-021"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-006"
      tests: ["TEST-L1-001-020"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-007"
      tests: ["TEST-L1-001-020", "TEST-L1-001-025"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-008"
      tests: ["TEST-L1-001-009", "TEST-L1-001-010"]
    - requirement_id: "AC-L1-001-009"
      tests: ["TEST-L1-001-010", "TEST-L1-001-011"]
    - requirement_id: "AC-L1-001-010"
      tests: ["TEST-L1-001-016", "TEST-L1-001-026"]
    - requirement_id: "AC-L1-001-011"
      tests: ["TEST-L1-001-003"]
    - requirement_id: "AC-L1-001-012"
      tests: ["TEST-L1-001-018"]
      review_items: ["side-effect review"]
    - requirement_id: "AC-L1-001-013"
      tests: ["TEST-L1-001-019"]
      static_checks: ["forbidden_import_check"]
    - requirement_id: "AC-L1-001-014"
      static_checks: ["test-file-exists review", "requirement_test_map_check"]
    - requirement_id: "AC-L1-001-015"
      checks: ["pytest L1/tests/test_document_loader.py -q"]
    - requirement_id: "AC-L1-001-016"
      static_checks: ["completion_record_check"]
    - requirement_id: "AC-L1-001-017"
      static_checks: ["review_packet_check"]
    - requirement_id: "AC-L1-001-018"
      tests: ["TEST-L1-001-021"]
    - requirement_id: "AC-L1-001-019"
      tests: ["TEST-L1-001-022"]
    - requirement_id: "AC-L1-001-020"
      tests: ["TEST-L1-001-023"]
    - requirement_id: "AC-L1-001-021"
      tests: ["TEST-L1-001-024"]
    - requirement_id: "AC-L1-001-022"
      tests: ["TEST-L1-001-029"]

  edge_cases:
    - edge_case_id: "EC-L1-001-001"
      tests: ["TEST-L1-001-012"]
    - edge_case_id: "EC-L1-001-002"
      tests: ["TEST-L1-001-013"]
    - edge_case_id: "EC-L1-001-003"
      tests: ["TEST-L1-001-017"]
    - edge_case_id: "EC-L1-001-004"
      tests: ["TEST-L1-001-007"]
    - edge_case_id: "EC-L1-001-005"
      tests: ["TEST-L1-001-008"]
    - edge_case_id: "EC-L1-001-006"
      tests: ["TEST-L1-001-009"]
    - edge_case_id: "EC-L1-001-007"
      tests: ["TEST-L1-001-010"]
    - edge_case_id: "EC-L1-001-008"
      tests: ["TEST-L1-001-011"]
    - edge_case_id: "EC-L1-001-009"
      tests: ["TEST-L1-001-014"]
    - edge_case_id: "EC-L1-001-010"
      tests: ["TEST-L1-001-015"]
    - edge_case_id: "EC-L1-001-011"
      tests: ["TEST-L1-001-016"]
    - edge_case_id: "EC-L1-001-012"
      tests: ["TEST-L1-001-029"]
    - edge_case_id: "EC-L1-001-013"
      tests: ["TEST-L1-001-002", "TEST-L1-001-003"]
    - edge_case_id: "EC-L1-001-014"
      tests: ["TEST-L1-001-005"]
    - edge_case_id: "EC-L1-001-015"
      tests: ["TEST-L1-001-006"]
    - edge_case_id: "EC-L1-001-016"
      tests: ["TEST-L1-001-021"]
    - edge_case_id: "EC-L1-001-017"
      tests: ["TEST-L1-001-022"]
    - edge_case_id: "EC-L1-001-018"
      tests: ["TEST-L1-001-023"]
    - edge_case_id: "EC-L1-001-019"
      tests: ["TEST-L1-001-024"]
      review_items: ["error-message review"]
    - edge_case_id: "EC-L1-001-020"
      tests: ["TEST-L1-001-026"]
    - edge_case_id: "EC-L1-001-021"
      tests: ["TEST-L1-001-026"]
    - edge_case_id: "EC-L1-001-022"
      tests: ["TEST-L1-001-027"]
    - edge_case_id: "EC-L1-001-023"
      tests: ["TEST-L1-001-028"]
```

---

## AD. Semantic Diff Expectation

```yaml
semantic_diff_expected:
  behavior_added:
    - "Read-only loading of declared UTF-8 documents under a root path."
    - "Path traversal rejection."
    - "Symlink/root escape rejection after resolution."
    - "Size-bound loading through max_bytes."
    - "Structured immutable document record return value."
    - "SHA-256 digest computation from raw bytes."
    - "Deterministic normalized POSIX-style relative path output."
    - "Duplicate input path preservation."
    - "Safe exception messages that do not leak document contents."
    - "Invalid UTF-8 rejection through DocumentLoadError."
    - "Precise `max_bytes=0` behavior."
    - "Path-like root acceptance."
    - "Resolved-root symlink policy."
  behavior_removed: []
  behavior_changed: []
  behavior_preserved: []
  public_surface_added:
    - "DEFAULT_MAX_DOCUMENT_BYTES"
    - "DocumentRecord"
    - "DocumentLoaderError"
    - "DocumentRootError"
    - "DocumentPathError"
    - "DocumentLoadError"
    - "load_document"
    - "load_documents"
  public_surface_removed: []
  public_surface_changed: []
  state_ownership_changed: []
  dependency_changes:
    - "Adds only declared Python standard library imports."
  compatibility_impact: "new internal L1 module"
```

---

## AE. Residual Risk Ledger

```yaml
residual_risks: []
```

No known residual risk is accepted for `FIC-L1-001` v0.6.0. If implementation cannot satisfy the size, path, import, public surface, or test requirements, the result must be `BLOCKED`, `IMPLEMENTED_UNVALIDATED`, or `REJECTED`, not `VALIDATED`.

---

## AF. Review Packet Requirements

```yaml
review_packet:
  fic_id: "FIC-L1-001"
  fic_version: "v0.6.0"
  implementation_unit: "UNIT-L1-001"
  decision: "ready_for_review|blocked|no_change|rejected"
  changed_files: []
  unchanged_files_inspected: []
  requirement_to_code_map: []
  requirement_to_test_map: []
  acceptance_criteria_coverage: []
  edge_case_coverage: []
  unmapped_requirements: []
  public_surface_diff: []
  semantic_diff: []
  dependency_diff: []
  risk_ledger: []
  validators_run: []
  validators_not_run: []
  waivers: []
  rollback_plan: "revert permitted files changed by this implementation unit"
```

---

# Part III — Minimal First Development Target

The first implementation target is:

```text
FIC-L1-001: L1 Document Loader
```

Only after this unit is implemented and validated should L1 proceed to:

```text
FIC-L1-002: L1 Repo State Reader
```

This keeps L1 grounded in controlled document loading before it starts inspecting repository state or planning changes.

---

# Part IV — Current Rating

This version is rated:

```text
10/10 for L1 scaffolding and first-unit implementation readiness.
```

Scope of the rating:

- It is 10/10 as an **L1 EQC-FIC implementation-control document** for bootstrapping the first controlled L1 unit.
- It is not claiming the entire Agent_X L1 system is complete.
- It is not claiming executable validators already exist.
- It intentionally postpones full EQC-ES/SIB signed checkpoints, digest graph validation, and multi-profile shadow traces until after the basic L1 units exist.
- `FIC-L1-001` now has consistent type contracts, explicit public signatures, complete acceptance mapping, complete edge-case mapping, and no known unresolved specification gaps for implementation of the first L1 unit.

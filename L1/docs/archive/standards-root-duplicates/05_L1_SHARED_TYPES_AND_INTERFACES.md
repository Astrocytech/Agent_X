# L1 Shared Types and Interfaces

**Document ID:** `AX-L1-DOC-IFACE-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

Initial shared types:

```text
DocumentRecord
RepoStateSummary
GoalClassification
ImplementationUnitPlan
FicDraft
FicValidationResult
SemanticLockfile
HandoffPacket
CheckRunResult
EvidenceRecord
CompletionRecord
ReviewPacket
TraceabilityUpdate
FailureLearningEntry
```

## DocumentRecord

```text
DocumentRecord(path: str, content: str, size_bytes: int, sha256: str, exists: bool = True)
```

Rules:

- Immutable value record.
- `path` is normalized POSIX-style relative path.
- `sha256` is a lowercase 64-character hex digest of raw bytes.

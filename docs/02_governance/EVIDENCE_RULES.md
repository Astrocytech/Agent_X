# EQC Spec–Implementation Bridge (EQC-SIB) v1.2.1

**EQC Spec–Implementation Bridge (EQC-SIB)** is the master governance layer for **code and pseudocode artifacts** that are tied to an EQC document portfolio governed by **EQC Ecosystem Specification (EQC-ES)**. It is explicitly **bidirectional** with EQC-ES:

* **Code/Pseudocode → Documents (via EQC-ES):** Any functional change in code or pseudocode produces an impact set of EQC documents that MUST be updated and revalidated under EQC-ES (unless a valid waiver applies).
* **Documents → Code/Pseudocode:** Any change in EQC documents that alters functional meaning produces an impact set of code/pseudocode artifacts that MUST be updated, rebuilt, and revalidated under EQC-SIB (unless a valid waiver applies).

EQC-SIB does **not** replace EQC-ES. EQC-ES remains the governance layer for documents. EQC-SIB governs implementation artifacts and enforces synchronization and determinism across the **document ↔ pseudocode ↔ code** triangle.

---

## 0.0 Identity & Purpose (mandatory)

* **Portfolio Name:** `[e.g., MyMetaheuristicSuite]`
* **Purpose (1 sentence):** Single source of truth that makes every implementation artifact discoverable, deterministically hashed, and provably consistent with the governing EQC documents under bidirectional propagation.
* **Spec Version:** **EQC-SIB-v1.2.1 | 2026-02-19 | [YourName / Team]**
* **Paired Document Governance:** **EQC-ES-v1.9.1** is mandatory and authoritative for document governance.
* **Governance Mode:** `paired-central` (one EQC-SIB paired to one EQC-ES root) or `paired-distributed` (sub-portfolios; see §9.2).

---

## 0.1 Core Principle: Bidirectional Binding Contract (mandatory)

EQC-SIB defines a binding contract:

1. **Every functional implementation artifact MUST bind to one or more EQC documents** that define its semantics, operators, invariants, or trace schema.
2. **Every EQC document that defines functional semantics MUST declare its implementation bindings** (either pseudocode, code, or both).
3. **Impact analysis is symmetric:**

   * If the implementation changes (functional), the governing documents are impacted.
   * If the governing documents change (functional), the implementation is impacted.

“Functional” is determined by **Digest Classes** (§6) and **Equivalence / Drift Rules** (§8), not by filename, formatting, or intent.

---

## 0.2 Normative Definitions (mandatory)

EQC-SIB uses four change classifications:

* **METADATA:** MD changes only (FD and FSD unchanged).
* **STATE:** FSD changes while FD is unchanged OR FD changes that are fully explained by toolchain/canonicalizer/materialization changes and evidence remains within tolerances; revalidation is required.
* **FUNCTIONAL:** FD changes not explained by state-only causes OR required evidence indicates semantic drift beyond tolerances OR public surface/operator contract changes.
* **VALIDATION:** Changes restricted to validation assets or traces (golden/shadow) without changing governed semantics; may still require reruns and drift reporting.

For **HARD** bindings, **evidence** (traces + contracts + surfaces) participates in classification (§5.2). FD is necessary but not sufficient.

---

## 0.3 Deterministic Change Classifier (mandatory)

All tooling MUST classify changes using a single deterministic algorithm.

### 0.3.1 Severity Lattice (mandatory)

Define severity ordering:

`METADATA < VALIDATION < STATE < FUNCTIONAL`

A change event’s **classification** is:

`classification = max_severity(triggers)`

### 0.3.2 Normative Trigger Set (mandatory)

Tooling MUST compute the following triggers (at minimum) and include them in output (§7.2):

#### FUNCTIONAL triggers (highest)

* `TRG_FD_CHANGED_UNEXPLAINED` → FUNCTIONAL
* `TRG_SD_CHANGED` → FUNCTIONAL
* `TRG_OPERATOR_SIGNATURE_CHANGED` → FUNCTIONAL
* `TRG_TRACE_DRIFT_EXCEEDS_TOLERANCE` (HARD) → FUNCTIONAL
* `TRG_OBSERVED_DEPS_VIOLATION` (HARD) → FUNCTIONAL **and** validation FAIL (§3.1)
* `TRG_SANDBOX_POLICY_VIOLATION` (HARD) → FUNCTIONAL **and** validation FAIL (§4.2)
* `TRG_CHECKPOINT_SIGNATURE_INVALID` → FUNCTIONAL **and** validation FAIL (§9.1.3)

#### STATE triggers

* `TRG_PSD_CHANGED` → STATE
* `TRG_TOOLCHAIN_LOCK_CHANGED` → STATE
* `TRG_PROFILE_LOCK_CHANGED` → STATE
* `TRG_GIT_MATERIALIZATION_CHANGED` → STATE
* `TRG_CANONICALIZER_CHANGED` → STATE
* `TRG_CANONICAL_ENCODING_RULES_CHANGED` → STATE
* `TRG_FD_CHANGED_EXPLAINED_BY_STATE_CAUSE_AND_EVIDENCE_WITHIN_TOLERANCE` → STATE

#### VALIDATION triggers

* `TRG_VALIDATION_ASSET_CHANGED` (trace/test-only governed assets) → VALIDATION

#### METADATA default

* Otherwise if only MD changes → METADATA

### 0.3.3 FD Change Root-Cause Rule (mandatory)

If FD differs between two checkpoints, tooling MUST deterministically decide whether it is **explained** by STATE-only causes:

STATE-only explanatory causes include one or more of:

* canonicalizer identity/version/digest change
* canonical encoding rule change (§12)
* git materialization rule/config change (§1.1.3, §12)
* toolchain lock change that impacts parsing/canonicalization (not the artifact’s meaning)

Classification MUST be:

* FUNCTIONAL if evidence drift exceeds tolerances OR surface/operator signature changed OR observed dependency enforcement fails
* otherwise STATE if FD difference is fully explained by STATE-only causes and evidence remains within tolerances
* otherwise FUNCTIONAL

---

# 1. Artifact Registry (mandatory)

Machine-readable inventory stored as `sib-registry.yaml`.

### 1.0 Required Fields (mandatory)

Each registry entry MUST contain:

* **PortfolioID** (global namespace root; required in `paired-distributed`, recommended otherwise)
* **ArtID** (unique short identifier **within PortfolioID**)
* **GlobalArtID** (derived; see §9.2.2)
* **Title**
* **Type:** `pseudocode | reference-impl | production-impl | operator-impl | test-harness | golden-trace-runner | benchmark | schema | generator | derived-artifact | external-dependency | other`
* **Language:** `eqc-procedure | mas-eqc | python | typescript | c++ | go | rust | other`
* **Layer** (integer ≥ 0; see §1.5; external dependencies use §3.2)
* **Repo / Workspace Root** (logical root)
* **File Path / Git Ref** (one or both; see §1.1)
* **Current Version** (`vX.Y.Z` semantic versioning)
* **Status:** `active | deprecated | frozen | experimental | migrating`
* **Owner** (optional)
* **Canonicalization Tier** (see §6.1): `T0|T1|T2|T3`
* **Canonicalizer ID** (`<tool>@<version>`)
* **Canonicalizer Digest** (SHA-256 of the canonicalizer artifact, container image digest, or binary digest)
* **FunctionalDigest SHA-256 (FD)** (local semantics; see §6.2)
* **FunctionalStateDigest SHA-256 (FSD)** (FD + pins + surfaces + contracts; see §6.2)
* **MetadataDigest SHA-256 (MD)**
* **PinSet Digest SHA-256 (PSD)** (digest of declared dependency pin set; see §6.2)
* **Public Surface Digest SHA-256 (SD)** (digest of declared PROVIDES surface; see §6.3)
* **Build Profile Binding** (maps to EQC-ES `environment_profiles`)
* **Spec Bindings** (list of DocID + binding type + anchors; see §2)
* **Trace Bindings** (what traces validate it; see §4)
* **Tooling Manifest reference** (see §7)
* **AllowEmpty** (boolean; default false; see §1.1.4)

---

### 1.1 Strict Path Resolution for Implementation (mandatory)

`eqc-sib validate` MUST resolve each registry entry to a concrete file in a defined workspace:

* If **File Path** is provided: resolve relative to the implementation workspace root; reject symlinks that escape the workspace root.
* If **Git Ref** is provided: materialize `(repo, ref, path)` into a deterministic validation workspace (§1.1.3).
* **Non-empty means:** file length > 0 bytes after canonicalization (§6.1) **unless** `AllowEmpty: true` (§1.1.4).

Validation FAILS if resolution fails.

#### 1.1.1 Symlink and Path Escape Rules (mandatory)

* Resolve `.` and `..` components before access.
* Reject any symlink whose resolved target is outside the workspace root.
* Reject any path that normalizes outside the workspace root.

#### 1.1.2 Line Endings and File Mode (mandatory)

* Canonicalization tiers T1–T3 MAY normalize line endings per language adapter rules.
* T0 MUST hash raw bytes exactly as materialized (including line endings).
* File mode bits (e.g., executable) MUST be captured:

  * either in MD for all tiers, or
  * in FD for T0 if the canonicalizer defines that policy.
    The chosen rule MUST be declared in the Tooling Manifest.

#### 1.1.3 Git Materialization Contract (mandatory)

If `Git Ref` is used, validation MUST materialize deterministically:

* `ref` MUST be a full commit hash (branch names and tags are invalid for validation).
* Submodules MUST be initialized and pinned to the recorded commit hashes.
* Git LFS:

  * forbidden by default, OR
  * explicitly allowed by profile policy and content-addressed with recorded digests.
* `.gitattributes` filters that rewrite content during checkout MUST be either:

  * disabled, OR
  * recorded and included in ToolchainLockDigest.
* Checkout MUST pin and record git normalization controls:

  * `core.autocrlf`, `core.eol`, `core.filemode`
  * sparse checkout disabled unless explicitly recorded
  * filesystem case-sensitivity class (or run in pinned container where class is fixed)
* Materialization MUST record:

  * commit hash
  * submodule commit hashes (if any)
  * LFS object digests (if any)
  * checkout strategy identifier + version (e.g., `git@2.44 sparse=false`)
  * the normalization controls listed above (as a canonical JSON object per §12)

#### 1.1.4 AllowEmpty Exception (mandatory)

Some workflows intentionally include empty sentinel artifacts. To permit this:

* Set `AllowEmpty: true` on the registry entry.
* If `AllowEmpty: true`, a sidecar marker file `<artifact_path>.sibmeta` is **mandatory** (§1.2.2).
* Empty artifacts MUST still satisfy:

  * path resolution
  * version marker or sidecar marker rules (§1.2)
  * digest computation rules (FD/MD/FSD still computed)

---

### 1.2 Version Marker Rule (mandatory)

Each artifact MUST contain a type-appropriate version marker, either **inline** or via a **format-safe sidecar** (§1.2.2).

#### 1.2.1 Inline Marker (preferred)

* **Code files (comment-supporting formats):** a header line containing
  `EQC-SIB ArtID: <GlobalArtID> | Version: <vX.Y.Z>`
* **Pseudocode files:** a header containing
  `Spec Version:` or `Art Version:` with the exact version string.
* **Generated / derived artifacts:** must contain
  `Derived-From: <GlobalArtID>@<SourceVersion>`

Validation FAILS if the required marker is missing and no valid sidecar exists.

#### 1.2.2 Sidecar Marker (mandatory when inline is unsafe)

If the artifact format cannot safely include a marker (e.g., strict JSON, some schema formats, lockfiles, binaries), tooling MUST accept a sidecar file:

* Sidecar filename: `<artifact_path>.sibmeta`
* Sidecar content MUST be YAML and MUST include:

  * `global_art_id`
  * `version`
  * `derived_from` (optional)
  * `anchors` (optional mapping of `art_anchor_id` to stable symbol offsets/paths)
* Sidecar content is included in MD (and in FD only if tier policy declares it).

---

### 1.3 Binary / Non-text Artifacts (mandatory)

Artifacts that cannot be safely canonicalized as UTF-8 text MUST declare:

* `Canonicalization Tier: T0`

FD is computed over raw bytes of the materialized file, without whitespace stripping.

If an artifact is produced by a build step (compiled binary), it MUST be marked `derived-artifact` and MUST have `Derived-From` markers in accompanying metadata (inline or sidecar) binding it to source GlobalArtIDs.

---

### 1.5 Layered Architecture (anti-cycle rule)

Layers define allowed dependency directions within **implementation artifacts**:

* Layer 0: schemas, core runtime contracts, base utilities
* Layer 1: operator implementations, deterministic helpers
* Layer 2: algorithm implementations, pseudocode procedure bindings
* Layer 3: test-harness, golden-trace-runner, benchmarks
* Layer 4+: derived artifacts, generated code, integrations

**Rule:** An artifact may only depend on artifacts of layer ≤ its own layer.

**Metadata exception:** “RECOGNIZES” metadata edges may point upward (never affects FD or FSD; see §3).

---

# 2. Document ↔ Implementation Binding Map (mandatory)

EQC-SIB introduces the binding sidecar: `sib-bindings.yaml`.

This is the **bidirectional bridge** between EQC-ES and implementation artifacts.

## 2.1 Binding Types

Each binding declares one or more of:

* **GOVERNS:** Doc defines functional semantics; implementation must conform.
* **IMPLEMENTS:** Artifact implements a Doc’s procedure/operators.
* **DERIVES-FROM:** Artifact generated from pseudocode/spec.
* **VALIDATES:** Artifact validates the Doc via traces/tests.
* **REFERENCES:** Non-binding citation.

Only **GOVERNS** and **IMPLEMENTS** are bidirectionally binding by default.

## 2.2 Required Binding Structure

```yaml
bindings:
  - doc: "PORT::ALGO-001"
    governs:
      - art: "PORT::IMPL-ALGO-001-PY"
        anchors:
          - doc_anchor_id: "DOC-ALGO-001-BVI-MAIN"
            art_anchor_id: "IMPL-ALGO-001-TRAIN_LOOP"
            binding_strength: "HARD"    # HARD|SOFT
            minimum_equivalence: "E1"   # E0–E3
      - art: "PORT::PSEUDO-ALGO-001"
        anchors:
          - doc_anchor_id: "DOC-ALGO-001-BVI-MAIN"
            art_anchor_id: "PSEUDO-ALGO-001-PROC-MAIN"
            binding_strength: "HARD"
            minimum_equivalence: "E0"
    validates:
      - art: "PORT::TEST-ALGO-001"
        traces:
          - "PORT::GOLDEN-TRACE-ALGO-001"
```

## 2.3 Anchor Semantics (mandatory)

Anchors MUST be stable identifiers that survive refactors.

* **Doc Anchor:** MUST be an explicit `AnchorID:` tag in the doc for HARD bindings.
* **Artifact Anchor:** MUST be an explicit `EQC_ANCHOR` tag or stable symbol ID for HARD bindings.

### 2.3.1 HARD Anchor Requirements (mandatory)

For HARD bindings:

* `doc_anchor_id` MUST reference an explicit `AnchorID:` in the EQC document.
* `art_anchor_id` MUST reference either:

  * an explicit code tag, e.g.
    `# EQC_ANCHOR: IMPL-ALGO-001-TRAIN_LOOP`
    or
  * a tool-defined stable symbol identifier guaranteed stable under refactors.

Anchors are part of **MetadataDigest**. Breaking required anchor resolution is a **blocking validation error**.

---

# 3. Implementation Dependency Graph (mandatory)

Stored in `sib-graph.yaml` with explicit edge types:

* **IMPORTS** (code-level dependency)
* **USES** (operator-level use)
* **PROVIDES** (exported stable API/operator surface)
* **DERIVES** (generated targets)
* **VALIDATES** (test/trace runner validates target)
* **REFERENCES** (non-binding)
* **RECOGNIZES** (metadata-only; excluded from cycle detection and FD/FSD)
* **OBSERVED_IMPORTS** (observed at runtime during validation; see §3.1)
* **OBSERVED_FS_READS** (observed file reads during validation; see §3.1)

## 3.0 Cycle Detection Domain (mandatory)

Cycle detection MUST operate only on **declared functional edges**:

`CYCLE_EDGES = {IMPORTS, USES, DERIVES, VALIDATES}`

Cycle detection MUST exclude:

* `RECOGNIZES`
* `REFERENCES`
* `PROVIDES` (surface is not a dependency edge)
* all `OBSERVED_*` edges

Cycles in `CYCLE_EDGES` are validation FAIL.

---

## 3.1 Declared vs Observed Dependency Enforcement (mandatory)

For each validation run, tooling MUST produce:

* `declared_deps(Art)` from static extraction (imports/manifests/graph)
* `observed_deps(Art)` from runtime observation (imports + file reads)

### 3.1.1 Declared dependency classes (mandatory)

Declared dependencies MUST be partitioned deterministically into:

* `declared_deps_strict` (exact allowlist)
* `declared_deps_optional` (allowed if used)
* `declared_deps_dynamic_patterns` (allowlisted patterns)

Dynamic patterns MUST be canonicalized and MUST use one of these forms:

* `module:<namespace>.*` (e.g., `module:torch.*`)
* `path:<mount>/<glob>` (e.g., `path:inputs/**`)
* `shlib:<name-pattern>` (e.g., `shlib:libc.so.*`)

### 3.1.2 Enforcement rules (mandatory)

Rules:

1. For HARD-governed artifacts:

   `observed_deps ⊆ declared_deps_strict ∪ declared_deps_optional ∪ match(declared_deps_dynamic_patterns)`

   else FAIL (`SIB_OBSERVED_DEP_UNDECLARED`) and trigger `TRG_OBSERVED_DEPS_VIOLATION`.

2. Layer rule (§1.5) MUST be enforced on `declared_deps_strict`, `declared_deps_optional`, and on `observed_deps` after pattern expansion.

3. Any delta MUST be reported in JSON output (§7.2) deterministically sorted (§7.4).

Observed edges MUST NOT participate in cycle detection (§3.0).

---

## 3.2 External Dependencies (mandatory)

Third-party dependencies MUST be representable in the SIB graph and pins.

### 3.2.1 External dependency nodes (mandatory)

External dependencies MUST be represented as nodes with:

* `Type: external-dependency`
* `GlobalArtID: <PortfolioID>::EXT::<namespace>/<name>@<version>`
* `PinSet`: exact version and integrity digest(s) (wheel hash / npm integrity / crate checksum / module sum)
* `Layer`: treated as Layer 0 for layering purposes unless a stricter profile policy overrides

### 3.2.2 External dependency pins (mandatory)

PSD computation MUST include external dependency pins and integrity digests so that dependency substitution is detectable.

---

# 4. Trace & Validation Binding (mandatory)

EQC-SIB requires that implementation artifacts are validated through traces consistent with EQC-ES.

## 4.1 Trace Artifacts

Implementation validation uses one or more of:

* **Golden trace sets** (shared with EQC-ES)
* **Shadow-traces per environment profile** (must match EQC-ES `environment_profiles`)
* **Equivalence diffs** (E0–E3, plus profile drift rules)

---

## 4.2 Clean-Room + Deterministic Sandbox Contract (mandatory)

Shadow-traces MUST run in a clean-room workspace **and** a deterministic sandbox.

### Clean-room requirements

* fresh workspace directory
* only declared inputs mounted read-only (see §4.3)
* outputs written under `./run_artifacts/<run_id>/` only
* cache dirs cleared and cache-disabling env vars applied per profile
* start-state must match the paired portfolio checkpoint (§9)

### Deterministic sandbox requirements

Each environment profile MUST reference a sandbox policy that enforces at minimum:

* **Network:** disabled by default; allowlist only if explicitly declared and content-addressed
* **Time:** `fixed` (recommended) or `recorded` (see §4.2.1)
* **Filesystem:** deny-by-default outside declared mounts
* **Environment:** allowlist env vars; all others cleared
* **Locale/TZ:** pinned
* **Threading:** pinned (OMP/MKL/BLAS/etc.)
* **GPU determinism:** required mode or explicit waiver; nondeterministic kernels must be disallowed unless tolerated by equivalence scope

Validation FAILS for HARD-governed artifacts if any required control is missing (`SIB_SANDBOX_POLICY_MISSING`) or violated (`TRG_SANDBOX_POLICY_VIOLATION`).

#### 4.2.1 Time determinism rule (mandatory)

Sandbox time policy MUST be one of:

* `fixed`: all time sources resolve to a fixed epoch value defined in the profile lock and included in trace inputs
* `recorded`: the run must record an explicit `time_seed`/epoch and include it in trace input digests and in the run record; replay MUST reuse it

---

## 4.3 Content-Addressed Input Contract (mandatory)

Validation runs MUST use content-addressed declared inputs.

### 4.3.1 Required inputs sidecar (mandatory)

Implementation root MUST include:

* `sib-inputs.yaml`

This file MUST declare all allowed read-only inputs for validation, including:

* `input_id`
* `path`
* `digest` (SHA-256, lowercase hex; see §12)
* `size_bytes`
* `mount_point`
* `provenance` (optional but recommended)
* `profiles` allowlist

### 4.3.2 Enforcement (mandatory)

* `OBSERVED_FS_READS` MUST be within declared mounts and match declared input digests where applicable.
* Any read outside declared mounts is validation FAIL for HARD-governed artifacts.

---

# 5. Bidirectional Change Propagation Protocol (mandatory)

EQC-SIB defines a symmetric protocol. A change event is classified, then impact is computed across **both** registries and both graphs:

* implementation side: `sib-registry.yaml` + `sib-graph.yaml`
* document side: EQC-ES `ecosystem-registry.yaml` + `ecosystem-graph.yaml`
* bridge: `sib-bindings.yaml`

## 5.1 Change Types and Required Actions (mandatory)

| Change Source       | Change Type                                                             | Classified As | Affected                                | Required Actions                                                                                       | Version Impact (most severe wins)              |
| ------------------- | ----------------------------------------------------------------------- | ------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| Code / Pseudocode   | formatting / comments / non-functional refactor (FD stable; FSD stable) | METADATA      | bound docs (anchor check) + dependents  | update anchors if needed; rerun validate                                                               | PATCH                                          |
| Code / Pseudocode   | dependency pins / toolchain lock / profile lock change (FSD changes)    | STATE         | validators + dependents + traces        | rerun validations and traces; doc edits only if drift beyond tolerances                                | PATCH/MINOR (if required compat bounds change) |
| Code / Pseudocode   | canonicalizer/materialization change causing FD change with no drift    | STATE         | validators + dependents + traces        | rerun validations; record explanatory triggers; update lock digests                                    | PATCH                                          |
| Code / Pseudocode   | functional behavior change (FUNCTIONAL triggers)                        | FUNCTIONAL    | bound docs + tests + traces + consumers | update docs where semantics changed; update compatibility; rerun golden/shadow traces; EQC-ES validate | MINOR (or MAJOR if breaking surface/contract)  |
| Document            | editorial only (no EQC-ES FD change)                                    | METADATA      | bound artifacts                         | anchor checks only; no functional rebuild required                                                     | PATCH                                          |
| Document            | functional semantic change (EQC-ES FD change)                           | FUNCTIONAL    | bound pseudocode + code artifacts       | update pseudocode/code; rerun traces; update registry digests                                          | MINOR/MAJOR                                    |
| Operator spec (Doc) | operator contract change                                                | FUNCTIONAL    | operator impls + consumers + tests      | update operator code; update dependent algorithms; run targeted traces                                 | MAJOR if breaking                              |
| Test/Trace assets   | golden trace update                                                     | VALIDATION    | validators + governed docs              | rerun validations; update drift report if within tolerance; update waivers if used                     | PATCH unless breaking                          |

Classification MUST follow §0.3 even if the table row suggests a lower class.

---

## 5.2 HARD Binding Classification Triggers (mandatory)

For artifacts governed via **HARD** bindings, a change MUST be classified as FUNCTIONAL if **any** is true:

1. `TRG_FD_CHANGED_UNEXPLAINED`, or
2. Any bound **trace diff** exceeds effective equivalence tolerances (§8.3), or
3. Any declared **PROVIDES surface** changes (§6.3), or
4. Any declared **operator contract signature** changes, or
5. Any observed-deps rule is violated (§3.1), or
6. Sandbox policy is missing/violated (§4.2), or
7. Paired checkpoint signature is invalid/missing (§9.1.3)

---

## 5.3 Impact Closure Rule (mandatory)

`eqc-sib impact` MUST compute a deterministic closure.

### 5.3.1 Impact Graph Traversal Domain (mandatory)

Downstream impacts MUST be computed over declared edges:

`IMPACT_EDGES = {IMPORTS, USES, DERIVES, VALIDATES}`

Bindings traversal MUST include:

* **Implementation → Docs:** follow `GOVERNS/IMPLEMENTS` edges from changed ArtIDs to DocIDs.
* **Docs → Implementation:** follow `GOVERNS/IMPLEMENTS` edges from changed DocIDs to ArtIDs.

`REFERENCES` and `RECOGNIZES` MUST NOT induce required actions (warnings only).

### 5.3.2 Profile-Specific Impacts (mandatory)

If the changed artifact is bound to multiple **Build Profile Bindings**, impact computation MUST include each affected profile as part of required actions (trace reruns, sandbox compliance checks). Tool output MUST list impacted profiles deterministically.

---

# 6. Canonical Hashing & Digest Classes (mandatory)

EQC-SIB mirrors EQC-ES digest separation and adds an explicit **state** layer to prevent false “functional churn” while still capturing dependency/toolchain reality.

## 6.1 Canonicalization Tiers (mandatory)

Each artifact MUST declare one of these tiers:

* **T0 (Byte Canonical):** FD hashes raw bytes of the materialized file (no whitespace stripping).
* **T1 (Token Canonical):** tokenize; normalize whitespace; drop comments/formatting per language adapter rules.
* **T2 (AST Canonical):** parse → canonical AST → stable re-emit used for hashing.
* **T3 (Semantic Canonical):** optional; only permitted if the canonicalizer provides machine-checkable semantic equivalence guarantees.

Tier selection, canonicalizer identity, and canonicalizer digest MUST be recorded in the registry (§1.0) and included in checkpoint hashing (§9).

---

## 6.2 Digest Definitions (mandatory)

* **FunctionalDigest FD(Art):** MUST change whenever the artifact’s **local semantics** change under its declared canonicalization tier, except where a valid waiver applies (§8.1.1). FD MAY change due to canonicalizer/materialization/encoding rule changes; such cases MUST be captured via ToolchainLockDigest / GitMaterializationDigest and classified as STATE unless evidence triggers FUNCTIONAL.

* **PinSet Digest PSD(Art):** digest of the artifact’s declared dependency pins, including external dependency integrity digests (§3.2), and declared dynamic dependency patterns (§3.1.1).

* **Public Surface Digest SD(Art):** digest of the declared **PROVIDES** surface list (§6.3).

* **FunctionalStateDigest FSD(Art):** MUST change whenever the artifact’s effective execution state commitments change. Defined as:

  `FSD(Art) = H( FD(Art) || PSD(Art) || SD(Art) || ToolchainLockDigest(profile) || ProfileLockDigest(profile) || GitMaterializationDigest(profile) || CanonicalEncodingRulesDigest )`

* **MetadataDigest MD(Art):** may change for non-functional edits (comments, formatting not captured by tier rules, anchors, owners, references). MD MUST include anchors and REFERENCES/RECOGNIZES edges.

---

## 6.3 PROVIDES Surface (mandatory)

Any artifact that exposes a stable interface MUST declare a **PROVIDES surface list** that is:

* enumerated (symbols/operators/APIs), not prose
* deterministically ordered
* referenced by `sib-graph.yaml` as PROVIDES edges
* hashed as `SD(Art)`

### 6.3.1 Surface Manifest Rule (mandatory)

The PROVIDES list MUST be machine-verifiable and MUST be authored via one of:

1. **Registry embedded surface** (`provides: [...]` in `sib-registry.yaml` entry), or
2. **Co-located surface manifest** (`<artifact_path>.surface.yaml`), or
3. **Language adapter extraction** from explicit export tags (e.g., `# EQC_EXPORT: symbol_name`), where the adapter spec is pinned in Toolchain Lock.

Tooling MUST fail validation if an artifact has PROVIDES edges but no valid surface manifest is resolvable.

### 6.3.2 Surface diff → version impact (mandatory)

Tooling MUST compute a deterministic surface diff classification:

* **Removed symbol** → breaking → **MAJOR**
* **Changed signature** → breaking → **MAJOR**
* **Added symbol** → additive → **MINOR**
* **Reordered surface list only** (if canonical ordering is enforced) → **PATCH** (and should not change SD)

Signature canonicalization rules MUST be defined per language adapter and pinned in toolchain lock.

---

## 6.4 Toolchain Lock (mandatory)

Each environment profile used for validation MUST have a **Toolchain Lock Digest** that covers, at minimum:

* compiler/interpreter versions + digests (or container image digests)
* build tool versions + digests
* canonicalizer version + digest
* dependency lockfiles (or SBOM digest)
* container image digests (if used)
* Git materialization strategy id/version and normalization controls (§1.1.3)
* OS/runtime determinism state (see Appendix B)

Toolchain lock inputs MUST be stored in a dedicated sidecar (§7).

---

# 7. Tooling (mandatory)

EQC-SIB requires tooling that can compute impact and enforce symmetry.

## 7.0 Required Sidecars at Implementation Root (mandatory)

* `sib-registry.yaml`
* `sib-graph.yaml`
* `sib-bindings.yaml`
* `sib-inputs.yaml`
* `sib-validation-log.md`
* `sib-compatibility-aggregate.yaml`
* `sib-release-notes-template.md`
* `sib-waivers.yaml` (see Appendix A)
* `sib-toolchain-lock.yaml` (see Appendix B)
* `sib-profile-lock.yaml` (profile sandbox + determinism controls; see Appendix B)
* `sib-trust-config.yaml` (see Appendix D)
* `sib-error-codes.yaml` (error code enum; see Appendix C)
* `paired-checkpoint.yaml` (signed paired checkpoint; see §9.1.3)
* `sib-schemas/` (schemas for sidecars; see Appendix E)

---

## 7.1 Mandatory Commands (formal schema)

* `eqc-sib validate`
* `eqc-sib impact --change ARTID@vX.Y.Z`
* `eqc-sib sync --from code|pseudocode|docs`
* `eqc-sib regenerate-sidecars`
* `eqc-sib generate-migration-plan`

### 7.1.1 CLI determinism contract (mandatory)

All commands MUST support:

* `--profile <ENV-PROFILE-ID>` (required when multiple profiles exist)
* `--out <path>` to write canonical JSON output (machine output MUST be written only to the specified path)
* exit codes:

  * `0` → PASS
  * `1` → FAIL (validation errors)
  * `2` → TOOLING ERROR (schema unreadable, internal error, crash)

---

## 7.2 JSON Output Schemas (mandatory)

### 7.2.1 `eqc-sib validate` output (mandatory)

```json
{
  "eqc_sib_version": "v1.2.1",
  "workspace_ref": "<string>",
  "profile": "<ENV-PROFILE-ID>",
  "status": "PASS|FAIL",
  "errors": [{"code":"...", "art":"GLOBAL_ART_ID", "message":"...", "doc_anchor_id":null, "art_anchor_id":null}],
  "warnings": [{"code":"...", "art":"GLOBAL_ART_ID", "message":"...", "doc_anchor_id":null, "art_anchor_id":null}],
  "classification_triggers": [{"art":"GLOBAL_ART_ID","triggers":["TRG_...","..."]}],
  "resolved_sib_graph_hash": "<sha256>",
  "resolved_sib_graph_hash_basis": "DECLARED_ONLY",
  "toolchain_lock_hash": "<sha256>",
  "profile_lock_hash": "<sha256>",
  "git_materialization_hash": "<sha256>",
  "canonical_encoding_rules_hash": "<sha256>",
  "broken_bindings": [{"doc":"GLOBAL_DOC_ID","art":"GLOBAL_ART_ID","doc_anchor_id":"...","art_anchor_id":"..."}],
  "waivers_used": [{"waiver_id":"...", "scope":"...", "expires":"..."}],
  "observed_deps_delta": [{"art":"GLOBAL_ART_ID","missing_declared":["..."],"unexpected_observed":["..."]}],
  "observed_fs_reads_violations": [{"art":"GLOBAL_ART_ID","reads":["..."]}],
  "affected_docs_via_bindings": ["GLOBAL_DOC_ID","..."],
  "checkpoint_signature": {"status":"VALID|INVALID|MISSING","trust_root_id":"...","signers":["..."],"quorum_met":true}
}
```

### 7.2.2 `eqc-sib impact` output (mandatory)

```json
{
  "change": "GLOBAL_ART_ID@vX.Y.Z",
  "classification": "METADATA|STATE|FUNCTIONAL|VALIDATION",
  "classification_triggers": ["TRG_...","..."],
  "impacts": [
    {
      "art": "GLOBAL_ART_ID",
      "required_actions": ["..."],
      "version_impact": "PATCH|MINOR|MAJOR"
    }
  ],
  "affected_docs": [
    {
      "doc": "GLOBAL_DOC_ID",
      "required_actions": ["Update semantics / anchors / compatibility / traces"],
      "eqc_es_version_impact": "PATCH|MINOR|MAJOR"
    }
  ],
  "impacted_profiles": ["ENV-PROFILE-ID","..."]
}
```

---

## 7.3 Error Code Taxonomy (mandatory)

All `errors[].code` and `warnings[].code` MUST come from `sib-error-codes.yaml`. Unknown codes are invalid output.

---

## 7.4 Deterministic Ordering Rules (mandatory)

All tooling output MUST be deterministic:

* lists sorted lexicographically by stable keys:

  * **errors:** `(code, art, doc_anchor_id, art_anchor_id)`
  * **warnings:** `(code, art, doc_anchor_id, art_anchor_id)`
  * **impacts:** `(art, version_impact)`
  * **affected_docs:** `(doc)`
  * **observed deltas:** `(art)`
* YAML parsing MUST be normalized via YAML→canonical JSON conversion (§12)
* JSON emission MUST be canonical (sorted keys, no insignificant whitespace, deterministic numeric encoding; §12)

---

## 7.5 Sidecar Schema Validation (mandatory)

All required sidecars MUST have a formal schema stored under `sib-schemas/`:

* `sib-schemas/sib-registry.schema.json`
* `sib-schemas/sib-graph.schema.json`
* `sib-schemas/sib-bindings.schema.json`
* `sib-schemas/sib-inputs.schema.json`
* `sib-schemas/sib-waivers.schema.json`
* `sib-schemas/sib-toolchain-lock.schema.json`
* `sib-schemas/sib-profile-lock.schema.json`
* `sib-schemas/sib-trust-config.schema.json`
* `sib-schemas/sib-error-codes.schema.json`
* `sib-schemas/paired-checkpoint.schema.json`
* `sib-schemas/canonical-encoding.schema.json`

`eqc-sib validate` MUST validate each sidecar against its schema and FAIL on schema violations.

---

# 8. Equivalence & Round-Trip Consistency Rules (mandatory)

EQC-SIB uses EQC E0–E3 equivalence semantics as the shared language of drift control, and adds a formal waiver system.

## 8.1 Round-Trip Rule (mandatory)

If a binding is **HARD**, then:

* **Doc functional change ⇒ implementation MUST update** such that either:

  * FD changes appropriately, or
  * evidence proves conformance within declared tolerances and a valid waiver exists.
* **Implementation FUNCTIONAL change ⇒ doc MUST update** such that either:

  * EQC-ES FD changes appropriately, or
  * evidence proves equivalence within declared tolerances and a valid waiver exists.

### 8.1.1 Waivers (mandatory)

Waivers are permitted only when:

* the change is proven within declared equivalence tolerances, and
* a matching `waiver_id` exists in both:

  * EQC-ES waiver store / validation log (per EQC-ES rules), and
  * `sib-waivers.yaml` (this spec; Appendix A),
* signatures validate against portfolio trust roots (defined by EQC-ES + SIB trust config),
* waiver is not expired.

Logs may reference waivers, but waivers are the enforceable governance object.

---

## 8.2 Binding Strength

* **HARD:** required bidirectional updates; missing update is a blocking error.
* **SOFT:** impact is reported as warning; used only for prototypes/experimental artifacts.

---

## 8.3 Strictest Tolerance Inheritance (paired rule)

For a governed artifact, effective tolerance is derived from paired documents:

* If the governing doc declares strict tolerance scope for that artifact/provider, that strict value applies.
* Otherwise local scope applies.

---

# 9. Paired Portfolio Checkpoint (mandatory)

EQC-SIB extends the EQC-ES portfolio checkpoint with implementation state.

A paired checkpoint snapshot includes:

* EQC-ES: registry, graph, environment profiles, data registry, document FD/MD, resolved graph hash
* EQC-SIB: registry, graph, bindings map, artifact FD/FSD/MD, resolved SIB graph hash
* tool manifests and validation logs
* waivers + toolchain lock + profile lock
* trust config
* canonical encoding rules
* a combined **Atomic Paired Checkpoint Hash**
* signatures over the paired checkpoint object (§9.1.3)

## 9.1 Atomic Paired Checkpoint Hash (mandatory)

Atomic Paired Checkpoint Hash MUST include:

* hash of EQC-ES files
* hash of EQC-SIB files
* resolved graph hashes for both sides
* bindings map hash
* **toolchain_lock_hash**
* **profile_lock_hash**
* **git_materialization_hash**
* **canonical_encoding_rules_hash**
* **dependency lock hashes / SBOM digests**
* canonicalizer digests / container image digests (if applicable)
* waiver store hash (both sides)
* trust config hash (both sides, if EQC-ES also defines one)

Detached checkpoints are invalid.

### 9.1.3 Signed paired checkpoint (mandatory)

Implementation root MUST include `paired-checkpoint.yaml` containing:

* `portfolio_id`
* `eqc_es_checkpoint_hash`
* `eqc_sib_checkpoint_hash`
* `atomic_paired_checkpoint_hash`
* `toolchain_lock_hash`, `profile_lock_hash`, `git_materialization_hash`, `canonical_encoding_rules_hash`
* `signing_context` (as defined in trust config policy)
* `signatures[]` meeting required quorum from `sib-trust-config.yaml`

Validation MUST fail if:

* signatures are missing, invalid, revoked, expired, or quorum is not met (`TRG_CHECKPOINT_SIGNATURE_INVALID`).

---

## 9.2 Paired-Distributed Mode: Portfolio Federation Contract (mandatory)

In `paired-distributed` mode:

* Each sub-portfolio MUST have its own paired checkpoint (EQC-ES + EQC-SIB) with an atomic paired hash and valid signatures.
* A parent portfolio MUST reference sub-portfolios via **imported checkpoint references**, not raw paths:

```yaml
imports:
  - portfolio_id: "SUBPORT-001"
    paired_checkpoint_hash: "<sha256>"
    compatibility_range: ">=1.2.0 <2.0.0"
```

Rules:

* Cross-portfolio bindings are valid only if the referenced sub-portfolio checkpoint is imported.
* Impact and validation MUST treat imported checkpoints as immutable inputs unless the import reference itself changes.

### 9.2.2 Global ID Namespacing (mandatory)

To prevent collisions across federated portfolios:

* **GlobalArtID** MUST be: `PortfolioID::ArtID`
* **GlobalDocID** MUST be: `PortfolioID::DocID`

All cross-portfolio edges (bindings, graph edges, trace bindings) MUST use Global IDs.

---

## 9.3 Resolved Graph Hash Definition (mandatory)

Tooling MUST compute `resolved_sib_graph_hash` from a canonical representation.

### 9.3.1 Canonical Graph Representation (mandatory)

Define a canonical JSON object:

```json
{
  "portfolio_id": "PORT",
  "nodes": [{"art":"PORT::A1","layer":0,"type":"...","status":"..."}],
  "edges": [{"src":"PORT::A1","type":"IMPORTS","dst":"PORT::A2","payload":{}}]
}
```

Rules:

* `nodes` sorted by `art`
* `edges` sorted by `(src, type, dst)` then canonical payload bytes
* payload keys sorted; absent payload treated as `{}`

### 9.3.2 Hash Algorithm (mandatory)

`resolved_sib_graph_hash = SHA256( canonical_json_bytes )`

`resolved_sib_graph_hash_basis` MUST be `"DECLARED_ONLY"` unless the portfolio explicitly defines a separate run-local observed hash. Observed edges MUST NOT be mixed into the declared resolved hash.

---

# 10. Governance & Lifecycle (mandatory)

Change process (paired):

1. branch → edit (docs or code/pseudocode)
2. run `eqc-sib impact` and `eqc-es impact` using the bindings map
3. apply required updates on both sides
4. run `eqc-sib validate` + `eqc-es validate`
5. run required golden/shadow traces
6. write release notes + migration notes if needed
7. atomic merge with signed paired checkpoint recorded

Deprecation rules align with EQC-ES:

* Deprecated artifacts remain readable for at least one MAJOR portfolio version + documented grace period.
* Frozen artifacts generate warnings only but MUST NOT be depended on by new ACTIVE artifacts via functional edges (IMPORTS/USES/DERIVES/VALIDATES/OBSERVED_*).

---

# 11. Glossary

* **Artifact (ArtID):** any code/pseudocode/test/schema item governed by EQC-SIB.
* **GlobalArtID:** `PortfolioID::ArtID`
* **Bindings Map:** `sib-bindings.yaml`, the bidirectional bridge to EQC-ES.
* **HARD Binding:** bidirectional functional coupling with blocking enforcement.
* **FunctionalDigest (FD):** hash of local semantics under declared canonicalization tier.
* **FunctionalStateDigest (FSD):** hash of FD plus pins, surfaces, toolchain/profile/materialization/encoding locks.
* **MetadataDigest (MD):** hash for non-functional and reference/anchor metadata.
* **PinSet:** declared dependency pins (GlobalArtIDs + version constraints + integrity digests + allowed dynamic patterns).
* **PROVIDES Surface:** enumerated stable API/operator surface.
* **Paired Checkpoint:** atomic snapshot of both document and implementation portfolios plus signatures.
* **Round-Trip Rule:** functional changes must propagate across doc ↔ implementation unless waived with valid evidence.

---

## Appendix A — Waiver Schema (mandatory)

Stored in `sib-waivers.yaml`.

### A.0 Canonical Waiver Objects (mandatory)

To prevent circularity, define:

* **Waiver Core:** the waiver content excluding `waiver_id` and excluding `approvals[]`.
* **Signing Context:** deterministic object that binds signature scope (portfolio, trust root, policy id).
* **Signed Payload Hash:** hash of `Waiver Core + Signing Context`.

Derivations:

* `waiver_id = SHA256(canonical(Waiver Core))`
* `signed_payload_hash = SHA256(canonical(Waiver Core + Signing Context))`
* `signature = Sign(signed_payload_hash, signer_key)`

### A.1 Waiver File Format

```yaml
waivers:
  - waiver_id: "WVR-<sha256_of_waiver_core>"
    scope:
      doc: "PORT::DOCID"              # optional
      art: "PORT::ARTID"              # optional
      doc_anchor_id: "..."            # optional
      art_anchor_id: "..."            # optional
    reason_code: "EQUIV_WITHIN_TOLERANCE"  # ENUM controlled by policy
    equivalence_claim:
      minimum_equivalence: "E2"
      tolerances:
        eps: "1e-8"                   # floats MUST be strings (see §12)
        drift_budget: "..."
    evidence:
      run_ids: ["RUN-..."]
      diff_hashes: ["<sha256>"]
      profile: "ENV-PROFILE-ID"
      resolved_graph_hash: "<sha256>"
      toolchain_lock_hash: "<sha256>"
      profile_lock_hash: "<sha256>"
      git_materialization_hash: "<sha256>"
      canonical_encoding_rules_hash: "<sha256>"
    signing_context:
      portfolio_id: "PORT"
      trust_root_id: "TRUSTROOT-001"
      policy_id: "SIB-WAIVER-POLICY-v1"
    approvals:
      - signer_key_id: "KEY-..."
        signature: "<sig>"
        signed_payload_hash: "<sha256>"
        signed_at: "2026-02-19T00:00:00Z"
    expires: "2026-06-19T00:00:00Z"
```

Rules:

* Waivers MUST be content-addressed (waiver_id derived from canonical Waiver Core).
* Waivers MUST expire.
* Validation MUST fail if a required waiver is missing or expired.

---

## Appendix B — Toolchain Lock + Profile Lock Schema (mandatory)

Stored in `sib-toolchain-lock.yaml` and `sib-profile-lock.yaml`.

### B.1 Toolchain lock (mandatory fields)

```yaml
toolchain_lock:
  profiles:
    - profile: "ENV-PROFILE-ID"
      os_runtime:
        base_image: "ghcr.io/org/image:tag"
        base_image_digest: "sha256:..."
        kernel_version: "..."
        libc_version: "..."
      cpu:
        cpu_class_id: "CPUCLASS-..."      # pinned class or explicit model snapshot
        flags_digest: "<sha256>"          # digest of canonical flags snapshot
      gpu:                                 # optional; required if GPU used
        driver_version: "..."
        cuda_runtime_digest: "<sha256 or image digest>"
        cudnn_digest: "<sha256>"
        determinism_flags:
          - "CUBLAS_WORKSPACE_CONFIG=..."
          - "torch.use_deterministic_algorithms(true)"
      interpreter:
        id: "python"
        version: "3.11.8"
        digest: "<sha256 or container digest>"
      build_tools:
        - id: "uv"
          version: "..."
          digest: "..."
      canonicalizer:
        id: "<tool>@<version>"
        digest: "<sha256 or container digest>"
      yaml_parser:
        id: "<tool>@<version>"
        digest: "<sha256 or container digest>"
      dependency_locks:
        - kind: "pip-lock"
          path: "locks/requirements.lock"
          digest: "<sha256>"
      containers:
        - image: "ghcr.io/org/image:tag"
          digest: "sha256:..."
      sbom:
        path: "sbom/sbom.spdx.json"
        digest: "<sha256>"
      git_materialization:
        strategy_id: "git-checkout-v1"
        git_version: "2.44.0"
        lfs_policy: "forbidden|allowed"
        checkout_normalization:
          core_autocrlf: "false"
          core_eol: "lf"
          core_filemode: "true"
          sparse_checkout: "false"
          fs_case_sensitivity: "case_sensitive|case_insensitive"
```

### B.2 Profile lock (sandbox + determinism) (mandatory)

```yaml
profile_lock:
  profiles:
    - profile: "ENV-PROFILE-ID"
      sandbox:
        network: "disabled"
        filesystem:
          deny_by_default: true
          allowed_mounts:
            - mount_point: "inputs/"
              mode: "ro"
            - mount_point: "run_artifacts/"
              mode: "rw"
        environment:
          allowlist: ["VAR1","VAR2"]
          clear_others: true
        locale_tz:
          locale: "C"
          tz: "UTC"
        threading:
          omp_num_threads: 1
          mkl_num_threads: 1
        time_policy:
          source: "fixed|recorded"
          fixed_epoch: 1700000000           # required if fixed
        gpu_policy:
          require_determinism: true
          allow_nondeterministic_kernels: false
```

---

## Appendix C — Error Code Enum Template (mandatory)

Stored in `sib-error-codes.yaml`.

```yaml
error_codes:
  - code: "SIB_PATH_ESCAPE"
    severity: "ERROR"
    description: "Artifact path resolves outside workspace root."
  - code: "SIB_MISSING_VERSION_MARKER"
    severity: "ERROR"
    description: "Required ArtID/version marker not found in artifact or sidecar."
  - code: "SIB_BROKEN_HARD_BINDING_ANCHOR"
    severity: "ERROR"
    description: "HARD binding anchor could not be resolved."
  - code: "SIB_OBSERVED_DEP_UNDECLARED"
    severity: "ERROR"
    description: "Observed dependency not present in declared dependency set."
  - code: "SIB_LAYER_VIOLATION"
    severity: "ERROR"
    description: "Layer rule violated by declared or observed dependency."
  - code: "SIB_SANDBOX_POLICY_MISSING"
    severity: "ERROR"
    description: "Required deterministic sandbox policy controls not present."
  - code: "SIB_WAIVER_MISSING_OR_EXPIRED"
    severity: "ERROR"
    description: "Required waiver not found or expired."
  - code: "SIB_SCHEMA_INVALID"
    severity: "ERROR"
    description: "A required sidecar file failed schema validation."
  - code: "SIB_GIT_REF_NOT_COMMIT_HASH"
    severity: "ERROR"
    description: "Git Ref is not a full commit hash."
  - code: "SIB_CHECKPOINT_SIGNATURE_INVALID"
    severity: "ERROR"
    description: "Paired checkpoint signature missing/invalid or quorum not met."
  - code: "SIB_INPUT_DIGEST_MISMATCH"
    severity: "ERROR"
    description: "Observed input digest differs from declared content-addressed input."
```

---

## Appendix D — Trust Configuration (mandatory)

Stored in `sib-trust-config.yaml`.

```yaml
trust_config:
  portfolio_id: "PORT"
  trust_roots:
    - trust_root_id: "TRUSTROOT-001"
      keys:
        - key_id: "KEY-001"
          kind: "ed25519"
          public_key: "<base64>"
          status: "active|revoked"
          not_before: "2026-01-01T00:00:00Z"
          not_after: "2028-01-01T00:00:00Z"
  signature_policy:
    allowed_algorithms: ["ed25519"]
    required_quorum:
      waivers: 1
      checkpoints: 1
  time_policy:
    source: "sandbox-recorded|fixed"
    max_clock_skew_seconds: 0
  revocation_policy:
    mode: "deny_revoked"
```

Rules:

* Waiver validation MUST use this trust config (and any paired EQC-ES trust config, if present).
* If EQC-ES provides an authoritative trust config, conflicts MUST be resolved by the paired governance mode policy; in `paired-central` the paired root policy is authoritative.

---

## Appendix E — Sidecar Schemas (mandatory)

All schemas MUST be JSON Schema (draft pinned by Toolchain Lock) and stored under `sib-schemas/`.

Minimum required schemas:

* `sib-registry.schema.json`
* `sib-graph.schema.json`
* `sib-bindings.schema.json`
* `sib-inputs.schema.json`
* `sib-waivers.schema.json`
* `sib-toolchain-lock.schema.json`
* `sib-profile-lock.schema.json`
* `sib-trust-config.schema.json`
* `sib-error-codes.schema.json`
* `paired-checkpoint.schema.json`
* `canonical-encoding.schema.json`

Schema requirements:

* MUST enforce Global ID form when `paired-distributed` is enabled.
* MUST require floats to be encoded as strings where determinism matters (waivers, tolerances, etc.).
* MUST enforce deterministic ordering constraints where representable (or require tooling normalization).
* MUST require `AllowEmpty` only when explicitly set; default false.

---

# 12. Canonical Encoding Rules (mandatory)

To ensure hashes are portable across implementations, **all canonical hashing inputs** MUST follow these rules.

## 12.1 Digest encoding (mandatory)

* SHA-256 values MUST be represented as **lowercase hex** (64 chars), no prefix.
* Container image digests MAY preserve `sha256:` prefix where ecosystem tooling requires it; such strings MUST be treated as opaque values and included verbatim in canonical JSON after normalization.

## 12.2 YAML normalization (mandatory)

Sidecars are authored as YAML, but canonicalization MUST:

1. parse YAML using a pinned YAML parser (declared in toolchain lock),
2. convert to a JSON-compatible object with these constraints:

   * mapping keys MUST be strings,
   * floats MUST be represented as strings in YAML for any field that can affect determinism (schemas MUST enforce where applicable),
3. emit canonical JSON bytes per §12.3.

## 12.3 Canonical JSON bytes (mandatory)

Canonical JSON bytes MUST be:

* UTF-8 encoding
* no insignificant whitespace
* object keys sorted lexicographically (byte order of UTF-8)
* arrays emitted in the deterministic order specified by this spec (e.g., §7.4 ordering rules)
* numbers:

  * NaN/Inf are forbidden
  * integers emitted without leading zeros
  * floats SHOULD be avoided in canonical objects; where unavoidable, they MUST be strings

## 12.4 CanonicalEncodingRulesDigest (mandatory)

Implementation root MUST include a `canonical-encoding.yaml` describing the applied encoding rules and version. Tooling MUST compute:

`CanonicalEncodingRulesDigest = SHA256(canonical_json_bytes(canonical-encoding.yaml))`

Changes to encoding rules MUST trigger `TRG_CANONICAL_ENCODING_RULES_CHANGED` (STATE).

---

 

# AST/Semantic Parsing Benchmark Contract

## Purpose
Define a reproducible benchmark for evaluating AST (Abstract Syntax Tree) generation and semantic parsing from BenchCore production cues, *OD commands, *CG commands, and QuickCode expansions. This benchmark measures the accuracy of parsing structured BenchCore grammar into an intermediary AST representation.

## Source
BENCHCORE-DOC-020

## Input Format
- Input files are plaintext lines, each containing a single BenchCore grammar construct (production cue, *OD command, *CG command, or QuickCode expansion).
- Each line may be prefixed with a type tag in brackets: `[CUE]`, `[OD]`, `[CG]`, or `[QC]`.
- Lines without a type tag are assumed to be cues.

### Examples
```
[CUE] Cue: Report ready | Keywords: summary, final | Delimiter: :
[OD] *OD EXTRACT STORY ID=12345
[CG] *CG GENERATE FIELD type=NRCS
[QC] KEYWORD: [TITLE] -> EXPANSION: {story_title}
```

## Output Format
- Output is a JSON object per input line, one JSON object per line (JSONL).
- Each output JSON object contains:
  - `type`: string — the detected type (cue, od, cg, quickcode)
  - `input`: string — the original input line
  - `ast`: object — the parsed AST structure
  - `valid`: boolean — whether the input passed validation
  - `errors`: array of strings — validation error messages (empty if valid)

### AST Structure Conventions
- **cue**: `{ "cue": string, "keywords": string[], "delimiter": string, "source": string | null }`
- **od**: `{ "command": string, "arguments": object, "transition": string | null }`
- **cg**: `{ "command": string, "arguments": object }`
- **quickcode**: `{ "keyword": string, "expansion": string, "source": string | null }`

## Validation Rules
1. Production cue strings must not exceed 150 characters.
2. Production cues must not contain forbidden keywords: `!halt`, `!emergency`, `!bypass`.
3. Delimiters must be `:` or `=`. `/` and `\` are not allowed.
4. *OD commands must start with `*OD`.
5. *CG commands must start with `*CG`.
6. Comma-separated lists where space-separated is required are rejected.
7. QuickCode keywords must be from the allowed list: TITLE, HEADLINE, SUMMARY, BODY, AUTHOR, DATE, CATEGORY, STATUS, SOURCE, KEYWORDS.
8. QuickCode expansions must be non-empty strings.
9. No additional properties beyond the defined fields are permitted.

## Evaluation Metrics
- **AST accuracy**: percentage of ASTs matching ground truth
- **Validation precision/recall**: correctness of valid/invalid classification
- **Error detection rate**: percentage of actual errors correctly flagged

## Dependencies
- JSON Schema draft-07 validators
- No live network, database, or production system dependencies

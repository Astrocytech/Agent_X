# NLP-to-Code Benchmark Contract

## Purpose
Define a reproducible benchmark for evaluating the translation of natural language (NL) instructions into structured BenchCore commands (cues, *OD, *CG, QuickCode). This benchmark measures an agent's ability to map human-readable requests into valid grammar constructs.

## Source
BENCHCORE-DOC-023

## Input Format (NL Examples)
- Input files are plaintext lines, each containing a natural language instruction describing a desired action.
- Instructions are in English and reflect real-world newsroom or content production scenarios.

### Example Inputs
```
"Generate a summary field for the current story"
"Extract story with ID 12345 from the database"
"Create a production cue for the final report with summary and author keywords"
"Set the QuickCode TITLE to expand to the story title field"
```

## Expected Output Format
- Output is a JSON object per input line, one JSON object per line (JSONL).
- Each output contains:
  - `nl_input`: string — the original NL instruction
  - `expected_command`: object — the expected BenchCore command representation
  - `expected_command_type`: string — one of: cue, od, cg, quickcode
  - `expected_valid`: boolean — whether the command should pass grammar validation
  - `source`: string — source reference

### Example Output
```json
{
  "nl_input": "Extract story with ID 12345 from the database",
  "expected_command": {
    "command": "*OD EXTRACT STORY ID=12345",
    "arguments": { "ID": "12345" },
    "transition": null
  },
  "expected_command_type": "od",
  "expected_valid": true,
  "source": "BENCHCORE-DOC-023"
}
```

## Validation Criteria
1. The generated command must match the expected command type.
2. The generated command must pass the corresponding JSON Schema validation.
3. All arguments required by the NL instruction must be present in the generated command.
4. No extraneous arguments beyond what the NL instruction specifies are permitted.
5. QuickCode keywords must be from the allowed list (TITLE, HEADLINE, SUMMARY, BODY, AUTHOR, DATE, CATEGORY, STATUS, SOURCE, KEYWORDS).
6. Delimiters in production cues must be `:` or `=`; `/` and `\` are not allowed.

## Evaluation Metrics
- **Type accuracy**: percentage of NL inputs mapped to the correct command type
- **Structural accuracy**: percentage of generated commands matching expected structure exactly
- **Grammar compliance**: percentage of generated commands passing schema validation
- **Hallucination rate**: percentage of commands containing fields or arguments not implied by the NL input

## Dependencies
- JSON Schema draft-07 validators
- No live network, database, or production system dependencies

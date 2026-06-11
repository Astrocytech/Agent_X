# Semantic Parser Pipeline Contract

## Purpose
Define the pipeline stages for semantic parsing in the BenchCore benchmark pack: parser → suggestion → rule refinement → renderer. Each stage is a pure transformation with defined interfaces. Mock-only scope.

## Source
BENCHCORE-DOC-023, BENCHCORE-DOC-030

## Pipeline Stages

### Stage 1: Parser
- **Input**: Raw text (production cue, *OD/*CG command, QuickCode expression, or NL instruction)
- **Output**: AST object (per `ast_generation_contract.md`)
- **Responsibility**: Tokenize input, validate against grammar schemas, produce structured AST
- **Interface**: `parse(input: string, schema?: object) -> { ast: object, valid: boolean, errors: string[] }`

### Stage 2: Suggestion
- **Input**: AST object from Parser
- **Output**: Suggestion object (list of suggested transformations or completions)
- **Responsibility**: Analyze AST for missing fields, ambiguous values, or optimization opportunities; produce ranked suggestions
- **Interface**: `suggest(ast: object) -> { suggestions: Suggestion[], confidence: number }`

### Stage 3: Rule Refinement
- **Input**: Suggestion object from Suggestion stage
- **Output**: Refined AST object with applied rules
- **Responsibility**: Apply rule-based refinements (default values, type coercions, format normalizations) to the AST
- **Interface**: `refine(ast: object, suggestions: Suggestion[], rules: Rule[]) -> { refined_ast: object, changes: Change[] }`

### Stage 4: Renderer
- **Input**: Refined AST object from Rule Refinement stage
- **Output**: Formatted output string (text command, XML, JSON, or SQL depending on target format)
- **Responsibility**: Serialize the refined AST back into the target format
- **Interface**: `render(ast: object, target_format: string) -> string`

## Interfaces (Type Definitions)
```
Suggestion {
  field: string
  current_value: any
  suggested_value: any
  reason: string
  confidence: number
}

Change {
  field: string
  old_value: any
  new_value: any
  rule_applied: string
}

Rule {
  name: string
  condition: (ast: object) => boolean
  action: (ast: object) => object
}
```

## Mock-Only Scope
- All pipeline stages operate on in-memory data structures only.
- No database lookups, network calls, or file I/O during pipeline execution.
- The pipeline is deterministic: same input + same rules = same output.
- Pipeline configuration is passed as parameters, not read from environment.
- All schemas are referenced by file path within this benchmark directory.

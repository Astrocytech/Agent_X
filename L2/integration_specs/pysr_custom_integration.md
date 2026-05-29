# PySR Custom Integration Spec

## Purpose
Integration specification for PySR symbolic regression library.

## Interface
- PySR called via governed tool gateway
- Results returned as structured evidence
- Discovery parameters controlled by profile

## Constraints
- PySR runs in sandboxed environment
- No direct filesystem access for PySR
- Results validated before storage

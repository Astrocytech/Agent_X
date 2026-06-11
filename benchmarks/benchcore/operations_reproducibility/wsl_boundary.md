# WSL Boundary

## Status: NOT IMPLEMENTED

This document defines the boundary for Windows Subsystem for Linux (WSL) operations. **This capability is not implemented and is deferred for future consideration.**

## Source
BENCHCORE-DOC-032

## Boundary Rules
1. **No WSL automation**: The BenchCore benchmark pack must not include any WSL detection, WSL command execution, or WSL environment setup logic.
2. **No environment setup**: The benchmark pack must not modify or assume any specific WSL distribution, configuration, or toolchain.
3. **Cross-platform compatibility not required**: The benchmark pack targets Linux environments. WSL-based development workflows are outside scope.

## What Exists
- All benchmarks, schemas, and contracts in this pack are designed to be **platform-independent in theory** but tested on Linux only.
- No scripts or configurations reference WSL paths, mount points, or interoperability features.

## Future Considerations (Deferred)
- If WSL support is implemented in a future phase, it must:
  - Detect WSL environment and adapt paths accordingly (e.g., `/mnt/c/` prefix).
  - Not introduce Windows-specific dependencies that break Linux-only CI pipelines.
  - Be documented with clear setup instructions for WSL 2.

## Rationale
WSL-specific considerations are premature for the current benchmark pack phase. The core validation and architecture benchmarks are environment-agnostic and do not require WSL-specific handling.

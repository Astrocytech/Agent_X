# L1 Validation Plan

**Document ID:** `AX-L1-DOC-VAL-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document defines the initial validation gates for L1 scaffold work.

## Required Checks

- `make seed-boot`
- `make prove-seed`
- `make run`
- source-standard byte-preservation check
- ES cross-check evidence
- SIB cross-check evidence
- EQC cross-check evidence
- bootstrap artifact manifest existence check

## TODO

- Replace bootstrap checks with executable validators after the first L1 validator exists.

# fixtures_invalid

This directory holds **deliberately invalid fixture data** for the BenchCore benchmark pack's data quality evaluation suite.

## Contents

| File | Description | Errors |
|------|-------------|--------|
| `malformed_log_sample.xml` | XML with three deliberate error types: (1) unclosed `<params>` tag in entry m003, (2) mismatched close tag `</incorrectTag>` for entry m004, (3) illegal characters `&` and `>` in element name `<INVALID&ILLEGAL>ACTION>` in entry m005. |
| `unpaired_data.csv` | CSV with misaligned input/output pairs across 10 rows. Row 2 has `output_field` missing, Row 4 output doesn't match the input (invoice vs inventory), Row 5 output mismatches (shipping label vs status update), Rows 6-7 are swapped. Tests orphan output and missing output detection per BENCHCORE-DOC-027. |
| `duplicate_entries.xml` | XML with 7 entries (5 unique IDs, 2 duplicates). Entry `d001` appears twice (different timestamps and targets), entry `d002` appears twice (CREATE then UPDATE). Tests deduplication logic per LogParsePolicy duplicate_handling rule. |

## Usage
Fixtures in this directory are used to test **error detection and handling** in the data quality pipeline. A correctly implemented pipeline must flag, quarantine, or reject these fixtures according to the policies defined in `data_quality/*.json`.

## Constraints
- No live data. All fixtures are synthetic.
- Each invalid fixture includes a companion `.meta.json` file documenting the expected failure reason.

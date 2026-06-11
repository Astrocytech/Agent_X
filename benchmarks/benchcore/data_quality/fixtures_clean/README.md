# fixtures_clean

This directory holds **clean, validated fixture data** for the BenchCore benchmark pack's data quality evaluation suite.

## Contents

| File | Description |
|------|-------------|
| `clean_log_sample.xml` | Cleaned version of `raw_log_sample.xml`. CDATA sections resolved to plain text, XML comments removed from message fields, special characters encoded (`&gt;` for `>`), whitespace normalized to consistent 2-space indentation, and all elements properly balanced. |
| `clean_customer_dump.xml` | Cleaned version of `raw_customer_dump.xml`. Free-text notes scrubbed of embedded XML comments, special characters properly encoded (`&amp;`, `&lt;`, `&uuml;`), whitespace normalized, empty elements preserved as self-closing. |

## Usage
Fixtures in this directory represent the **expected output** of a successful data quality pipeline run. Benchmarks compare pipeline output against these clean fixtures to measure correctness.

## Constraints
- No live data. All fixtures are synthetic.
- Files follow the naming convention: `<source>_<timestamp>.json` for traceability.

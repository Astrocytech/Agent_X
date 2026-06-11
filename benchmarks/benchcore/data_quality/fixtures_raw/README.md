# fixtures_raw

This directory holds **raw, unprocessed fixture data** for the BenchCore benchmark pack's data quality evaluation suite.

## Contents

| File | Description |
|------|-------------|
| `raw_log_sample.xml` | Raw MOS gateway log with 7 entries. Contains nested `<story>/<item>` elements, inconsistent indentation, CDATA sections, HTML-encoded characters (`&amp;`), and XML comments embedded in text content. Source IDs: mos-gateway-01, web-api-02, oracle-db-01. |
| `raw_customer_dump.xml` | Raw customer data dump with 6 records. Contains messy free-text `<notes>` fields with unescaped characters, empty `<state/>` elements, and embedded XML comments. Demonstrates typical pre-cleanup data quality issues. |

## Usage
Fixtures in this directory serve as the **input** to data quality pipeline benchmarks. Processing pipelines read from `fixtures_raw/`, transform/validate the data, and write results to `fixtures_clean/` or `fixtures_invalid/`.

## Constraints
- No live data. All fixtures are synthetic, generated specifically for benchmark reproducibility.
- No credentials, secrets, or customer paths.

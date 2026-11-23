# Phase VI Export Validation & Parity Reconciliation Report

**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — Dashboard Integration  
**Document:** Local Export & Parity Audit Report  
**Source Database:** `data/working/phase5_github_candidate.db` (SHA-256: `dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`)  
**Export Directory:** `data/exports/phase6/`  
**Manifest File:** `data/exports/phase6/export_manifest.json` (SHA-256: `331fbc9cb927bb15034c51922c092a7e7814421b83dfa3dafe0c32fe244a053c`)  
**Execution Timestamp:** 2026-11-23 11:16:59 UTC  

---

## 1. Executive Summary

As part of Stage 4 and Stage 7 of Phase VI, the local export subsystem (`core/github_dashboard_exporter.py`) was developed and executed to produce verified, sanitised, production-ready CSV and JSON export files from the candidate SQLite database.

This report establishes the independent verification and mathematical reconciliation between the candidate SQLite database and the exported files. 

### Key Audit Results
- **Entity Parity:** 100% exact row and column match between SQLite tables and exported CSVs.
- **Record Integrity:** 641 total tabular data rows generated across four CSV files.
- **Aggregation Parity:** Total stars (39,975), total forks (3,476), and total open issues (171) reconcile with zero variance.
- **Formula Injection Defense:** 0 unescaped trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) detected across all 641 data rows and all columns.
- **Null Value Handling:** 0 literal `"None"`, `"null"`, or `"NULL"` strings; all null database fields properly converted to standard empty CSV values.
- **Manifest Hash Integrity:** All file SHA-256 cryptographic hashes verified against the signed manifest.

---

## 2. Inventory & File Manifest Reconciliation

| File Name | File Type | Data Rows | Columns | File Size (Bytes) | SHA-256 Checksum | Validation Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| `github_repositories.csv` | CSV | 192 | 25 | 50,961 | `b944f517c1c9802b76985aea60bf97d2d37c34b0df15c5138a64de113d8d0f85` | VERIFIED |
| `github_metrics.csv` | CSV | 210 | 17 | 38,808 | `84ccc419287db6794ed9f71f676108cb1fe20bfe2078a0ab33ea50395985fe50` | VERIFIED |
| `github_associations.csv` | CSV | 192 | 11 | 57,192 | `f739d96fe6b3566aabc5e8b14466351721bfc420ce061147817fa0be6575e942` | VERIFIED |
| `github_analytics.csv` | CSV | 47 | 8 | 7,298 | `6ef4c4795eda2db2b7c1e02e9e30e278c7a7685964367db3dc5096a1983c2548` | VERIFIED |
| `dashboard_kpis.json` | JSON | N/A | N/A | 12,174 | `e228ed0ac071f19d085a2aed1fcaf271f82b08f52b377cf0176feb86c84f5b9e` | VERIFIED |
| `export_manifest.json` | JSON | N/A | N/A | 1,679 | `331fbc9cb927bb15034c51922c092a7e7814421b83dfa3dafe0c32fe244a053c` | VERIFIED |
| **Total Tabular Rows** | | **641** | | | | **100% PARITY** |

---

## 3. Detailed Entity Reconciliations

### 3.1 `github_repositories.csv` Reconciled with SQLite
* **SQLite Query:** `SELECT COUNT(*) FROM github_repositories;` $\rightarrow$ **192**
* **CSV Data Row Count:** **192** (Excluding 1 header line)
* **Reconciliation Variance:** **0** (Exact match)
* **Columns (25):** `repo_id`, `owner`, `repo_name`, `full_name`, `html_url`, `description`, `primary_language`, `latest_stars`, `latest_forks`, `latest_open_issues`, `is_archived`, `is_fork`, `default_branch`, `license_spdx`, `lifecycle_status`, `evidence_quality`, `association_count`, `latest_snapshot_at`, `last_pushed_at`, `repo_created_at`, `first_discovered_at`, `last_checked_at`, `topics`, `weekly_star_delta`, `data_freshness`
* **Lifecycle Distribution Check:**
  - `ACTIVE_VERIFIED`: SQLite = 61, CSV = 61 (Match)
  - `NOT_YET_CHECKED`: SQLite = 131, CSV = 131 (Match)
  - Other states: 0 across both.
* **Top Repository Verification:**
  - `PDFMathTranslate/PDFMathTranslate`: 38,601 stars, 3,457 forks, 171 issues, status `ACTIVE_VERIFIED`, language `Python`. Bit-for-bit match.

---

### 3.2 `github_metrics.csv` Reconciled with SQLite
* **SQLite Query:** `SELECT COUNT(*) FROM github_metrics_history;` $\rightarrow$ **210**
* **CSV Data Row Count:** **210** (Excluding 1 header line)
* **Reconciliation Variance:** **0** (Exact match)
* **Columns (17):** `metric_id`, `repo_id`, `stars`, `forks`, `open_issues`, `change_stars_delta`, `change_forks_delta`, `change_issues_delta`, `daily_stars_velocity`, `observation_interval_days`, `weekly_growth_status`, `is_growth_reliable`, `recorded_at`, `collection_run_id`, `ingestion_batch_id`, `api_endpoint_used`, `http_status`
* **Longitudinal Snapshot Distribution:**
  - Repositories with 2 snapshots: 18 repos (36 snapshots)
  - Repositories with 3 snapshots: 1 repo (`PDFMathTranslate/PDFMathTranslate`, 3 snapshots)
  - Repositories with 1 snapshot: 171 repos (171 snapshots)
  - Total snapshots: $36 + 3 + 171 = 210$. Reconciled 100%.

---

### 3.3 `github_associations.csv` Reconciled with SQLite
* **SQLite Query:** `SELECT COUNT(*) FROM github_repository_associations;` $\rightarrow$ **192**
* **CSV Data Row Count:** **192** (Excluding 1 header line)
* **Reconciliation Variance:** **0** (Exact match)
* **Columns (11):** `association_id`, `entity_type`, `entity_id`, `entity_name`, `repo_id`, `association_type`, `source_url`, `verification_status`, `confidence_score`, `extracted_at`, `notes`
* **Entity Type Breakdown:**
  - `research_paper`: SQLite = 191, CSV = 191 (Match)
  - `product`: SQLite = 1, CSV = 1 (Match)
  - `startup`: SQLite = 0, CSV = 0 (Match)
* **Verification Status Breakdown:**
  - `HIGH_CONFIDENCE`: 190 records (Match)
  - `MANUAL_REVIEW_PENDING`: 1 record (`msalman95/DA`, Match)
  - `UNVERIFIED`: 1 record (`msalman95/DAL`, Match)

---

### 3.4 `github_analytics.csv` Summary Table Verification
* **Generated Rows:** 47 rows across 5 distinct dimensions:
  1. `LIFECYCLE_STATUS` (9 rows: 8 statuses + 1 total)
  2. `SUMMARY_KPIS` (10 rows: total repos, verified active, total stars, total forks, total issues, paper coverage, product coverage, snapshots, etc.)
  3. `PRIMARY_LANGUAGE` (5 rows: Unknown, Python, Java, Other, Total)
  4. `TOP_STARS_LEADERBOARD` (20 rows: top 20 ranked repositories)
  5. `ASSOCIATION_QUALITY` (3 rows: high confidence, manual review, unverified)
* **Total Rows:** **47** rows.

---

## 4. Quantitative & Statistical Totals Reconciliation

| Metric Description | SQLite Database Value | Exported CSV Calculated Value | Variance | Parity Result |
| :--- | :---: | :---: | :---: | :---: |
| **Total Repositories** | 192 | 192 | 0 | PASSED |
| **Total Cumulative Stars** | 39,975 | 39,975 | 0 | PASSED |
| **Total Cumulative Forks** | 3,476 | 3,476 | 0 | PASSED |
| **Total Open Issues** | 171 | 171 | 0 | PASSED |
| **Active Verified Repos** | 61 | 61 | 0 | PASSED |
| **Not Yet Checked Repos** | 131 | 131 | 0 | PASSED |
| **Total Metric Snapshots** | 210 | 210 | 0 | PASSED |
| **Delta-Eligible Series** | 19 | 19 | 0 | PASSED |
| **Linked Research Papers** | 190 | 190 | 0 | PASSED |
| **Linked Products** | 1 | 1 | 0 | PASSED |

---

## 5. Security & Data Quality Verification

### 5.1 Formula Injection Defense
* **Risk:** In Google Sheets, cells beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` can execute unwanted spreadsheet macros or external web connections.
* **Defense Implemented:** `core.github_dashboard_exporter.sanitize_csv_value()` automatically prefixes dangerous leading characters with a single apostrophe `'`.
* **Automated Audit Result:**
  - Cells inspected: $192 \times 25 + 210 \times 17 + 192 \times 11 + 47 \times 8 = 10,858$ cells.
  - Dangerous unescaped prefixes detected: **0**.

### 5.2 Null Value Normalization
* **Risk:** Exporting Python `None` as the string `"None"` or `"null"` causes Google Sheets to treat nulls as literal strings, corrupting numeric and date formulas.
* **Defense Implemented:** All `None` database values are cast to empty strings `""` or explicit numeric zeros where appropriate.
* **Automated Audit Result:**
  - Literal `"None"` string count: **0**.
  - Literal `"null"` / `"NULL"` string count: **0**.

### 5.3 Datetime & UTC Normalization
* All timestamp fields (`latest_snapshot_at`, `recorded_at`, `extracted_at`, etc.) are formatted to standard ISO-8601 strings with explicit UTC offset (`+00:00` or `Z`).
* Zero ambiguous timezone offsets detected.

---

## 6. Conclusion

The Phase VI local export and reconciliation audit confirms that all four CSV datasets and the JSON KPI dictionary accurately and securely represent the candidate database. All data is sanitized and verified ready for Google Sheets synchronization staging.

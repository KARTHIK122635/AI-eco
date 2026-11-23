# Phase II — Stage 3: Audit 26 Database Hash & Integrity Report

## Executive Summary
This report documents the cryptographic hashes (SHA-256), byte sizes, table schemas, and record counts for all database artifacts evaluated during **Audit 26 — Final Historical Authenticity Correction**.

---

## 1. Primary Database Inventory

| Artifact Logical Name | File Path | File Size (Bytes) | SHA-256 Digest | Status / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Authentic Audit 19 Source Database** | `source/audit19_original_database.db` | 20,770,816 | `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d` | **Authentic Original Source** |
| **Audit 19 Baseline Copy** | `reports/audit19_original_baseline.db` | 20,770,816 | `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d` | Byte-identical baseline copy |
| **Audit 22 Submitted Baseline** | `deliverables_audit22/ai_ecosystem.db` | 21,008,384 | `c944c9349f80d8be2a6feb3a28dbec878ab82665b6c8b9744fc50f2d92cba81d` | Immutable canonical reference (6,745 records) |
| **Active Pipeline Database** | `data/normalized/ai_ecosystem.db` | 20,865,024 | *See dynamic calculation* | Corrected active working database |
| **Audit 26 Corrected Copy** | `reports/audit26_corrected.db` | 20,865,024 | *Matches active pipeline DB* | Corrected review package deliverable |
| **Authentic Recovery Source ZIP** | `reports/audit19_recovery_source_bundle.zip` | 4,004,072 | `8aa58ded2280182268d42096912792d2540b857d2245031a3d0ec5c5e4e52f54` | Official source bundle from reviewer |

---

## 2. Authentic Audit 19 Database Verification (`1958c59f...`)

- **SHA-256 Digest**: `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`
- **File Byte Size**: `20,770,816` bytes
- **SQLite PRAGMA `integrity_check`**: `ok`
- **Table Count**: 6 tables
  - `ai_startups`: 1,307 records
  - `ai_products`: 1,316 records
  - `ai_research_papers`: 1,060 records
  - `ai_news`: 1,132 records
  - `ai_jobs`: 1,930 records
  - `enrichment_audit_log`: 366 records
- **Column Count in `enrichment_audit_log`**: 13 columns (`record_id`, `entity_type`, `field_name`, `original_value`, `enriched_value`, `source_url`, `evidence`, `confidence_score`, `enrichment_method`, `provider`, `model`, `enriched_at`, `validation_status`)
- **Field-Level Null vs Empty String Integrity**:
  - `original_value` NULL count: 0 (354 empty strings, 12 non-empty strings)
  - `enriched_value` NULL count: 0 (50 empty strings, 316 enriched values)
- **Authentic Timestamps**: Authentic ISO 8601 UTC timestamps (e.g., `2026-11-21T20:11:42.334761+00:00`, `2026-11-21T20:11:43.334423+00:00`).

---

## 3. Active & Corrected Database Table Reconciliation

In `data/normalized/ai_ecosystem.db` and `reports/audit26_corrected.db`:

1. **Canonical Tables (Immutable)**:
   - `ai_startups`: 1,307 rows (100% byte & column match to Audit 22)
   - `ai_products`: 1,316 rows (100% byte & column match to Audit 22)
   - `ai_research_papers`: 1,060 rows (100% byte & column match to Audit 22)
   - `ai_news`: 1,132 rows (100% byte & column match to Audit 22)
   - `ai_jobs`: 1,930 rows (100% byte & column match to Audit 22)
   - **Total Canonical Records**: **6,745**

2. **Historical Archive Table**:
   - `audit19_enrichment_audit_log_archive`: **366 rows**, 13 columns.
   - Matches `source/audit19_original_database.db` row-by-row and column-by-column with **0 mismatches**.

3. **Active Stage 3 Results & Review Queue**:
   - `llm_enrichment_results`: 37 rows
   - `llm_review_queue`: 37 rows
   - `llm_provider_usage`: 37 operations (0 tokens, $0.00 cost)
   - `llm_enrichment_logs`: 37 rows

4. **Preserved Backup Tables (All 9 match Audit 22)**:
   - `llm_enrichment_results_backup_20261122_054711`
   - `llm_enrichment_logs_backup_20261122_054711`
   - `llm_provider_usage_backup_20261122_054711`
   - `llm_review_queue_backup_20261122_054711`
   - `enrichment_audit_log_backup_20261122_054906`
   - `llm_enrichment_results_backup_20261122_054906`
   - `llm_enrichment_logs_backup_20261122_054906`
   - `llm_provider_usage_backup_20261122_054906`
   - `llm_review_queue_backup_20261122_054906`

---

## 4. Key Reconciliation Summary

- **Total Original Audit 19 Records**: 366
- **Surviving Audit 19 Keys in Active/Backup Tables**: 42
- **Restored Historical Keys Absent from Active Tables**: 324
- **Post-Audit 19 Key Additions**: 24
- **Total Keys Cataloged in Reconciliation CSV**: **390** (`reports/audit19_to_audit23_reconciliation.csv`)

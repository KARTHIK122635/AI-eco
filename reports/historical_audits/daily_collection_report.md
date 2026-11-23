# Daily AI Ecosystem Ingestion & Metric Refresh Report

**Report Status:** Authoritative Working Database Telemetry (Audit 38A Reconciled)  
**Execution Type:** `ROUTINE_DAILY_INCREMENTAL`  
**Evaluation Reference Time:** `2026-11-22T15:00:00+00:00` (UTC)  
**Dynamic Rolling Window Start:** `2026-05-22T15:00:00+00:00` (UTC)  
**Dynamic Rolling Window End:** `2026-11-22T15:00:00+00:00` (UTC)  
**Rolling Window Duration:** Exactly 6 calendar months (UTC)  
**Canonical Database Preservation:** Verified Byte-Identical (`4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`)  
**Authentic Audit 19 Archive Preservation:** Verified Byte-Identical (`1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`)  
**Working Database SHA-256:** `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`  
**Total Collection Logs Recorded:** `6`  

---

## 1. Daily Ingestion & Modification Summary

| Pipeline Metric | Value | Category / Classification |
|---|:---:|---|
| **Startups Monitored** | **1,307** | Tracked entities (unverified dates strictly held in archive) |
| **Products Monitored** | **1,316** | Developer attribution verified (dates unverified) |
| **Active Research Papers** | **1,060** | arXiv & Hugging Face papers (100% inside 6M window) |
| **Active News Articles** | **311** | 5 legitimate media feeds (827 historical preserved) |
| **Active Job Vacancies** | **1,931** | Greenhouse ATS & Arbeitnow API (32 historical preserved) |
| **GitHub Repository Metric Updates** | **15** | Live stars/forks refreshes in current cycle |
| **Duplicates Identified & Rejected** | **73** | Multi-attribute deduplication gate (0 synthetic leaks) |
| **Daily Ingestion Errors / Failures** | **0** | Clean cycle execution (100% stage success) |
| **Enrichment Proposals Pending Approval** | **20** | Strict Human-in-the-Loop invariant (0 auto-applied) |

---

## 2. Six-Month Rolling Window Freshness Distribution

| Entity Category | Total Records | Inside Window | FRESH_24H | RECENT_7D | HISTORICAL_6M | UNVERIFIED_DATE | OUTSIDE_WINDOW |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **AI Startups** | 1,307 | 0 | 0 | 0 | 0 | 1,307 | 0 |
| **AI Products** | 1,316 | 0 | 0 | 0 | 0 | 1,316 | 0 |
| **Research Papers** | 1,060 | 1,060 | 0 | 1,045 | 15 | 0 | 0 |
| **AI News** | 1,138 | 311 | 5 | 99 | 207 | 0 | 827 |
| **AI Jobs** | 1,963 | 1,931 | 25 | 1116 | 790 | 0 | 32 |

---

## 3. Database Table Record Inventory & Provenance

| Table Name | Live Count | Packaged Count | Reconciliation Status |
| :--- | :---: | :---: | :---: |
| `ai_jobs` | 1,963 | 1,963 | **MATCH (Exact)** |
| `ai_news` | 1,138 | 1,138 | **MATCH (Exact)** |
| `ai_products` | 1,316 | 1,316 | **MATCH (Exact)** |
| `ai_research_papers` | 1,060 | 1,060 | **MATCH (Exact)** |
| `ai_startups` | 1,307 | 1,307 | **MATCH (Exact)** |
| `collection_logs` | 6 | 6 | **MATCH (Exact)** |
| `enrichment_proposals` | 20 | 20 | **MATCH (Exact)** |
| `github_metrics_history` | 205 | 205 | **MATCH (Exact)** |
| `github_repositories` | 190 | 190 | **MATCH (Exact)** |
| `sqlite_sequence` | 1 | 1 | **MATCH (Exact)** |

---

## 4. Collection Execution History (collection_logs)

| Run ID | Execution Type | Status | Start Time (UTC) | End Time (UTC) | Original Run ID |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `recovery_20261122_212554_7ee642` | `STAGE_LEVEL_RECOVERY` | **COMPLETED** | `2026-11-22T21:25:54.962115+00:00` | `N/A` | `interrupted_audit31_025554` |
| `recovery_20261122_212843_ceea58` | `STAGE_LEVEL_RECOVERY` | **COMPLETED** | `2026-11-22T21:28:43.395098+00:00` | `N/A` | `interrupted_audit31_025843` |
| `recovery_20261122_214850_70aadd` | `STAGE_LEVEL_RECOVERY` | **COMPLETED** | `2026-11-22T21:48:50.144532+00:00` | `N/A` | `interrupted_audit31_031850` |
| `recovery_20261122_222028_907f6c` | `STAGE_LEVEL_RECOVERY` | **COMPLETED** | `2026-11-22T22:20:28.409570+00:00` | `N/A` | `interrupted_audit31_035028` |
| `recovery_20261122_231953_3f2e22` | `STAGE_LEVEL_RECOVERY` | **COMPLETED** | `2026-11-22T23:19:53.823421+00:00` | `2026-11-22T23:19:53.818479+00:00` | `interrupted_audit31_044953` |
| `run_20261122_150000_221724` | `ROUTINE_DAILY_INCREMENTAL` | **COMPLETED** | `2026-11-22T15:00:00+00:00` | `2026-11-22T16:01:06.218004+00:00` | `N/A` |

---

## 5. Security & Verification Baseline

- **Working DB Cryptographic SHA-256:** `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`
- **SQLite Internal Integrity:** `ok` (PRAGMA integrity_check = 'ok')
- **Enrichment Proposals Pending Approval:** `20` (100% pending, zero auto-applied)
- **Task Scheduler Status:** NOT REGISTERED (0 tasks active). Unattended daily execution is deferred.
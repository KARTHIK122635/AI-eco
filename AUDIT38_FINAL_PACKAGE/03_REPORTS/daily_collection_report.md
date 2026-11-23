# Daily AI Ecosystem Ingestion & Metric Refresh Report

**Report Status:** Authoritative Working Database Telemetry (Audit 38 Remediated)  
**Execution Type:** `ROUTINE_DAILY_INCREMENTAL`  
**Evaluation Reference Time:** `2026-11-22T15:00:00+00:00` (UTC)  
**Dynamic Rolling Window Start:** `2026-05-22T15:00:00+00:00` (UTC)  
**Dynamic Rolling Window End:** `2026-11-22T15:00:00+00:00` (UTC)  
**Rolling Window Duration:** Exactly 6 calendar months (UTC)  
**Canonical Database Preservation:** Verified Byte-Identical (`4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`)  
**Authentic Audit 19 Archive Preservation:** Verified Byte-Identical (`1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`)  
**Working Database SHA-256:** `7a579df9924861cb1fc0f97bf59ca87cbca449ef0765a93da313da556d228e21`  

---

## 1. Daily Ingestion & Modification Summary

| Pipeline Metric | Value | Category / Classification |
|---|:---:|---|
| **Startups Monitored** | **1,307** | Tracked entities (unverified dates strictly held in archive) |
| **Products Monitored** | **1,316** | Developer attribution verified (dates unverified) |
| **Active Research Papers** | **1,060** | arXiv & Hugging Face papers (100% inside 6M window) |
| **Active News Articles** | **311** | 5 legitimate media feeds (827 historical preserved) |
| **Active Job Vacancies** | **1,931** | Greenhouse ATS & Arbeitnow API (32 historical preserved) |
| **GitHub Repository Metric Updates** | **15** | Live stars/forks snapshots appended (205 total snapshots) |
| **Genuinely Published within 24h** | **30** | 5 News (`FRESH_24H`) + 25 Jobs (`FRESH_24H`) |
| **Duplicate Records Prevented** | **73** | Canonical URL & content hash match |

## 2. Dataset Eligibility Breakdown (Six-Month Rolling Window)

*Generated directly from SQLite tables in `data/working/rolling_ai_ecosystem.db` using explicit date column mappings:*

| Dataset / Table | Schema Date Column | Total Records | Valid Publication Date | Inside 6M Rolling Window | Outside Window (Archived) | Missing / Invalid Date | Future Anomalies |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `ai_startups` | `published_at` | 1,307 | 0 | 0 | 0 | 1,307 | 0 |
| `ai_products` | `published_at` | 1,316 | 0 | 0 | 0 | 1,316 | 0 |
| `ai_research_papers` | `publication_date` | 1,060 | 1,060 | 1,060 | 0 | 0 | 0 |
| `ai_news` | `published_at` | 1,138 | 1,138 | 311 | 827 | 0 | 0 |
| `ai_jobs` | `posted_at` | 1,963 | 1,963 | 1,931 | 32 | 0 | 0 |

### Supplementary GitHub Repositories & Snapshot Metrics

| Metric Entity | Active Records / Snapshots | Operational Status |
|:---|:---:|:---|
| `github_repositories` | 190 | Tracked open-source AI repositories linked to papers |
| `github_metrics_history` | 205 | Longitudinal star and fork delta timeline snapshots (190 baseline + 15 live) |

> [!IMPORTANT]
> **Permanent Historical Archive Preservation:** Zero records have been deleted. Records with missing publication dates (`MISSING_DATE` / `UNVERIFIED_DATE`) and records older than 6 calendar months (`OUTSIDE_WINDOW`) remain permanently stored in the SQLite working archive (`data/working/rolling_ai_ecosystem.db`).

## 3. Phase III Multi-Tier LLM Token & Budget Consumption

| Metric | Status / Value | Operational Notes |
|:---|:---:|:---|
| **Phase III Pilot Status** | **DISABLED** | Routine daily execution (`run_pilot=False`) |
| **LLM Enrichment Requests** | 0 | Skipped in scheduled automation to conserve API budget |
| **Proposals Queue State** | **PENDING_APPROVAL (20)** | 100% of proposals preserved awaiting manual human review |
| **Database Mutability** | **ZERO WRITES** | No unapproved writes or schema changes applied |
| **Manual Execution Path** | `--run-pilot` | Can be triggered on-demand via CLI when required |

## 4. Execution Checkpoint & Scheduler Integrity

- **Scheduler Execution Status:** `COMPLETED`
- **Run ID:** `run_20261122_150000_221724`
- **Completed Pipeline Stages:** `['STAGE_1_NEWS', 'STAGE_2_JOBS', 'STAGE_3_GITHUB_METRICS', 'STAGE_4_VACANCY_LIFECYCLE', 'STAGE_5_EXPORTS', 'STAGE_6_REPORT']`
- **Checkpoint Saved:** Successfully recorded in `collection_logs` with run ID `run_20261122_150000_221724`.
- **Idempotency Guarantee:** Rerunning this pipeline on the same day will produce 0 duplicate records.

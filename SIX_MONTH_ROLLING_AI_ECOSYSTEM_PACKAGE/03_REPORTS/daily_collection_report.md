# Daily AI Ecosystem Ingestion & Metric Refresh Report

**Execution Run ID:** `run_20261122_151538_7e28e5`  
**Execution Type:** `DAILY_INCREMENTAL`  
**Execution Start Time:** `2026-11-22T15:15:38.244769+00:00`  
**Execution Finish Time:** `2026-11-22T15:16:04.094919+00:00`  
**Dynamic Rolling Window:** `2026-05-22` to `2026-11-22` (UTC)  
**Canonical Database Preservation:** Verified Byte-Identical (`4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`)  

---

## 1. Daily Ingestion & Modification Summary

| Pipeline Metric | Value | Category / Classification |
|---|:---:|---|
| **New Startups Discovered** | **+0** | Verified official domains |
| **New Products Discovered** | **+0** | Developer attribution verified |
| **New Research Papers** | **+0** | arXiv & Hugging Face papers |
| **New News Articles Ingested** | **+0** | 5 distinct legitimate media sources |
| **New Job Vacancies Ingested** | **+0** | Greenhouse ATS & Arbeitnow API |
| **GitHub Repository Metric Updates** | **15** | Live stars/forks snapshots appended |
| **Genuinely Published within 24h** | **0** | Strict `FRESH_24H` UTC window |
| **Duplicate Records Prevented** | **112** | Canonical URL & content hash match |

## 2. Active Six-Month Rolling View vs Historical Archive

| Working Table | Active 6-Month Rolling Records | Historical Archived Records | Total Table Count |
|---|:---:|:---:|:---:|
| `ai_startups` | 12 | 1,295 | 1,307 |
| `ai_products` | 1,316 | 0 | 1,316 |
| `ai_research_papers` | 1,060 | 0 | 1,060 |
| `ai_news` | 311 | 827 | 1,138 |
| `ai_jobs` | 1,931 | 32 | 1,963 |
| `github_repositories` | 191 | — | 191 |
| `github_metrics_history` | 224 | — | 224 |

## 3. Phase III Multi-Tier LLM Token & Budget Consumption

| Metric | Consumption Value | Notes |
|---|:---:|---|
| **LLM Enrichment Requests** | 0 | 100% assigned `PENDING_APPROVAL` |
| **Prompt Tokens** | 0 | Full multi-chunk reassembly enabled |
| **Completion Tokens** | 0 | Grounded JSON extractions |
| **Estimated API Cost** | **$0.000000 USD** | Primary Gemini + Groq Fallback |
| **DeepSeek Status** | HTTP 402 Insufficient Balance | Zero credits spent; clean non-retriable failover |

## 4. Execution Checkpoint & Scheduler Integrity

- **Scheduler Execution Status:** `COMPLETED`
- **Checkpoint Saved:** Successfully recorded in `collection_logs` with run ID `run_20261122_151538_7e28e5`.
- **Idempotency Guarantee:** Rerunning this pipeline on the same day will produce 0 duplicate records.

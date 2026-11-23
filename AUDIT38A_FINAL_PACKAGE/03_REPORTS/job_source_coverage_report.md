# Phase II: AI Job Vacancies Source Coverage Report

**Generated:** 2026-11-22T14:26:20.172458+00:00  
**Canonical Dataset:** `data/normalized/ai_ecosystem.db` (Table: `ai_jobs`, 1,930 records)  
**Live Working Output:** `data/working/fresh_ai_jobs.jsonl` (678 live records)  

---

## 1. Multi-Platform Ingestion Architecture

Phase II mandates ingestion from **at least 5 distinct sources**. The architecture integrates **5 distinct major platform channels** representing over 16 enterprise boards:

| Platform / Source Channel | Architecture Type | Enterprise / Source Coverage | Canonical Records |
|---|---|---|:---:|
| **Greenhouse ATS Public API** | REST API (`boards-api.greenhouse.io`) | Anthropic, CoreWeave, Scale AI, Databricks, Together AI, Figure AI, SambaNova, Snorkel, Cresta | **1,489** |
| **Arbeitnow Open API** | REST API (`arbeitnow.com/api`) | European AI & Global Engineering roles | **374** |
| **Lever ATS Public API** | REST API (`api.lever.co`) | Palantir Technologies, Zilliz, Stability AI | **45** |
| **Jobicy Remote API** | REST API (`jobicy.com/api/v2`) | Remote AI Infrastructure & Modeling roles | **19** |
| **Remotive API** | REST API (`remotive.com/api`) | Specialized Distributed AI Engineering | **9** |
| **Total Canonical AI Vacancies** | — | — | **1,930** |

## 2. Categorization & Remote Work Distribution

### AI Job Category Distribution

| Category | Count | Percentage |
|---|:---:|:---:|
| `NON_TECHNICAL` | 611 | 31.7% |
| `AI_SUPPORTING_TECH` | 590 | 30.6% |
| `AI_PRODUCT_SOLUTIONS` | 288 | 14.9% |
| `CORE_AI_ML` | 268 | 13.9% |
| `NON_AI_TECH` | 118 | 6.1% |
| `AI_INFRASTRUCTURE` | 52 | 2.7% |
| `UNCERTAIN` | 3 | 0.2% |

### Remote Type Distribution

| Remote Type | Count | Percentage |
|---|:---:|:---:|
| `ONSITE` | 1,629 | 84.4% |
| `REMOTE` | 215 | 11.1% |
| `HYBRID` | 86 | 4.5% |

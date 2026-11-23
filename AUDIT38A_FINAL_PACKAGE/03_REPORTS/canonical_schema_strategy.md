# Canonical Schema Strategy & Target Field Compatibility Report
**Phase II — Stage 3: LLM Data Enrichment & Canonical Schema Governance**
**Document Reference: AUDIT-28-SCHEMA-STRATEGY**
**Date: 2026-11-22**
**Author: Senior Data Architect & Database Integrity Auditor**

---

## 1. Executive Summary & Audit 28 Revalidation

During independent review of Stage 3 deliverables (Audits 27 & 28), two interconnected architectural requirements were addressed:
1. **Target-Field Schema Governance**: 24 of 37 proposals target fields that do not physically exist in the canonical SQLite database (`data/normalized/ai_ecosystem.db`). Direct SQL updates would have raised `sqlite3.OperationalError: no such column`.
2. **Generated-Label & Duplication Revalidation (Audit 28)**:
   - Application-generated prefixes (e.g. `'AI Focus:'`) are strictly disallowed from serving as source quotations.
   - Proposals 1 and 4 quoted `'AI Focus: Applied AI & Automation'`; both are now classified as **`FAILED`** under Rule 2.
   - Proposals 2, 3, 5, 7 proposed technologies duplicating canonical `ai_evidence`; all are re-classified as **`NEEDS_REVIEW`** under the duplication safeguard.
   - Proposal 6 (Mistral AI, proposed `"Foundation Models & LLMs"`) and Proposals 15 & 16 (arXiv paper methodology and domain) remain semantically `VERIFIED`, but are classified as **`BLOCKED_SCHEMA`** because their target columns do not exist in the database.
   - None of the 13 `SCHEMA_COMPATIBLE` proposals are `VERIFIED` (10 are `NEEDS_REVIEW` news summaries, 3 are `FAILED` job skills).

### Governance Directives
1. **Zero Database Modifications**: In accordance with strict stop boundaries, no DDL statements (`ALTER TABLE`) or schema modifications have been applied to `data/normalized/ai_ecosystem.db`. The canonical database remains byte-identical to Audit 26 (SHA-256: `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`).
2. **Hardened Write Protection**: `src/stage3/apply_approved.py` now enforces:
   - Static schema allowlist checking via `src/stage3/schema_mapping.py`.
   - Runtime `PRAGMA table_info` verification against live SQLite table columns.
   - Rejection of `DUPLICATE_OF_EXISTING_CANONICAL_DATA` and `BLOCKED_SCHEMA`.
   - Dynamic runtime duplication check against the actual SQLite row.
3. **Approval State**: All 37 proposals remain strictly in `PENDING_APPROVAL` status.

---

## 2. Authoritative Canonical Physical Schema (Audit 26 Baseline)

The canonical database `data/normalized/ai_ecosystem.db` contains exactly five entity tables with the following physical columns:

| Canonical Table | Primary Key | Total Records | Physical Columns |
| :--- | :--- | :--- | :--- |
| `ai_startups` | `startup_id` | 337 | `startup_id`, `entity_name`, `ai_focus_area`, `ai_evidence`, `employee_count`, `pricing_model`, `website`, `primary_source_url`, `provenance_sources`, `headquarters`, `batch_or_founded`, `description`, `collected_at` |
| `ai_products` | `product_id` | 443 | `product_id`, `entity_name`, `product_type`, `ai_task_category`, `developer_or_company`, `developer_profile_url`, `official_company_website`, `pricing_model`, `license`, `access_type`, `actual_price`, `original_source_url`, `provenance_source`, `description`, `collected_at` |
| `ai_research_papers` | `paper_id` | 610 | `paper_id`, `title`, `authors`, `publication_date`, `categories`, `paper_url`, `github_url`, `github_stars`, `github_star_source`, `github_star_retrieved_at`, `provenance`, `abstract`, `collected_at` |
| `ai_news` | `news_id` | 741 | `news_id`, `title`, `summary`, `content`, `content_status`, `summary_type`, `content_retrieved_at`, `source_name`, `article_url`, `author`, `published_at`, `category`, `related_companies`, `collected_at`, `provenance` |
| `ai_jobs` | `job_id` | 4,614 | `job_id`, `job_title`, `company_name`, `company_website`, `category`, `classification_reason`, `responsibility_evidence`, `qualification_evidence`, `classification_confidence`, `job_description`, `required_skills`, `preferred_skills`, `experience_level`, `location`, `remote_type`, `salary_min`, `salary_max`, `currency`, `compensation_type`, `compensation_period`, `employment_type`, `job_status`, `vacancy_status`, `application_url`, `posted_at`, `source_name`, `provenance`, `collected_at` |

**Total Canonical Records**: 6,745 (100% preserved).

---

## 3. Schema Strategy for Every Enrichment Target Field

Below is the exhaustive specification for every field targeted across the 37 Stage 3 candidate proposals:

| Entity Type | Proposal Field | Canonical Table | Physical Target Column | Physical Data Type | Serialization Rules | Migration Requirement | Backward Compatibility Impact | Original Value Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **startup** | `ai_specialization` | `ai_startups` | *None* (Missing) | `TEXT` | Scalar string | **Migration Required**: `ALTER TABLE ai_startups ADD COLUMN ai_specialization TEXT;` | Non-breaking; new column defaults to NULL. Existing readers unaffected. | Preserves NULL. If mapped to existing `ai_focus_area`, original value would be overwritten. |
| **startup** | `technologies` | `ai_startups` | *None* (Missing) | `TEXT` | JSON-serialized array (`["tech1", "tech2"]`) | **Migration Required**: `ALTER TABLE ai_startups ADD COLUMN technologies TEXT;` | Non-breaking; defaults to NULL. Requires consumers to parse JSON text. | Preserves NULL. If mapped to `ai_evidence`, would overwrite provenance excerpt. |
| **paper** | `methodology` | `ai_research_papers` | *None* (Missing) | `TEXT` | Scalar string (narrative excerpt/summary) | **Migration Required**: `ALTER TABLE ai_research_papers ADD COLUMN methodology TEXT;` | Non-breaking; defaults to NULL. Existing paper queries unaffected. | Preserves NULL. Original `abstract` remains untouched. |
| **paper** | `key_contributions` | `ai_research_papers` | *None* (Missing) | `TEXT` | JSON-serialized array (`["item1", "item2"]`) | **Migration Required**: `ALTER TABLE ai_research_papers ADD COLUMN key_contributions TEXT;` | Non-breaking; defaults to NULL. JSON parsing required for consumers. | Preserves NULL. Original `abstract` remains untouched. |
| **paper** | `research_domain` | `ai_research_papers` | *None* (Missing) | `TEXT` | Scalar string (domain taxonomy) | **Migration Required**: `ALTER TABLE ai_research_papers ADD COLUMN research_domain TEXT;` | Non-breaking; defaults to NULL. If mapped to `categories`, would overwrite arXiv category codes. | Preserves NULL. Does NOT overwrite arXiv category strings. |
| **news** | `summary` | `ai_news` | `summary` | `TEXT` | Scalar string (clean executive summary) | **None**: Column physically exists in `ai_news`. | 100% compatible. Existing summaries are currently NULL or empty. | Overwrites existing NULL/empty string with verified LLM summary. |
| **job** | `required_skills` | `ai_jobs` | `required_skills` | `TEXT` | JSON-serialized array or semicolon-delimited string | **None**: Column physically exists in `ai_jobs`. | 100% compatible. Existing values are NULL or empty. | Overwrites NULL/empty field with verified structured skills list. |
| **job** | `technologies` | `ai_jobs` | *None* (Missing) | `TEXT` | JSON-serialized array (`["tool1", "tool2"]`) | **Migration Required**: `ALTER TABLE ai_jobs ADD COLUMN technologies TEXT;` | Non-breaking; defaults to NULL. Separate from `required_skills`. | Preserves NULL. Distinct from `required_skills` and `preferred_skills`. |

---

## 4. Revalidated Inventory of All 37 Proposals (Audit 28 Final)

The table below reflects the updated validation outcomes following the implementation of Audit 28 label separation and canonical duplication safeguards:

| # | Proposal ID | Entity | Record ID | Field Name | Validation Status | Schema Status | Physical Target Column | Duplication Analysis | Effective Governance Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| 1 | `f072cf39-...` | startup | `prelim_startup_6631243200679035785` | `ai_specialization` | **FAILED** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** + Label quote prefix (`AI Focus:`) | `BLOCKED_FROM_UPDATE` |
| 2 | `d4d5a715-...` | startup | `prelim_startup_6631243200679035785` | `technologies` | **NEEDS_REVIEW** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** of canonical `ai_evidence` | `BLOCKED_FROM_UPDATE` |
| 3 | `81590dea-...` | startup | `prelim_startup_4138537468450272463` | `technologies` | **NEEDS_REVIEW** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** of canonical `ai_evidence` | `BLOCKED_FROM_UPDATE` |
| 4 | `e3f56a78-...` | startup | `prelim_startup_324069110286089772` | `ai_specialization` | **FAILED** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** + Label quote prefix (`AI Focus:`) | `BLOCKED_FROM_UPDATE` |
| 5 | `5b2ad8e2-...` | startup | `prelim_startup_324069110286089772` | `technologies` | **NEEDS_REVIEW** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** of canonical `ai_evidence` | `BLOCKED_FROM_UPDATE` |
| 6 | `9e9e9770-...` | startup | `prelim_startup_7377128274119126472` | `ai_specialization` | **VERIFIED** | `BLOCKED_SCHEMA` | *None* | Distinct taxonomy ("Foundation Models & LLMs") | `BLOCKED_FROM_UPDATE` |
| 7 | `a9b031c9-...` | startup | `prelim_startup_7377128274119126472` | `technologies` | **NEEDS_REVIEW** | `BLOCKED_SCHEMA` | *None* | **DUPLICATE** of canonical `ai_evidence` | `BLOCKED_FROM_UPDATE` |
| 8 | `d8140ad1-...` | paper | `arxiv_2611_26232` | `methodology` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Novel extraction from abstract | `BLOCKED_FROM_UPDATE` |
| 9 | `324d0a69-...` | paper | `arxiv_2611_26239` | `methodology` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Novel extraction from abstract | `BLOCKED_FROM_UPDATE` |
| 10 | `9dab2ed0-...` | paper | `arxiv_2611_26239` | `key_contributions` | FAILED | `BLOCKED_SCHEMA` | *None* | Extraction failed quality rules | `BLOCKED_FROM_UPDATE` |
| 11 | `1ad16011-...` | paper | `arxiv_2611_25604` | `methodology` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Novel extraction from abstract | `BLOCKED_FROM_UPDATE` |
| 12 | `0bb6f083-...` | paper | `arxiv_2611_15941` | `methodology` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Novel extraction from abstract | `BLOCKED_FROM_UPDATE` |
| 13 | `9f152e24-...` | paper | `arxiv_2611_25200` | `methodology` | FAILED | `BLOCKED_SCHEMA` | *None* | Extraction failed quality rules | `BLOCKED_FROM_UPDATE` |
| 14 | `d1f0414d-...` | paper | `arxiv_2611_26627` | `methodology` | FAILED | `BLOCKED_SCHEMA` | *None* | Extraction failed quality rules | `BLOCKED_FROM_UPDATE` |
| 15 | `3ac0873c-...` | paper | `arxiv_2611_23875` | `methodology` | **VERIFIED** | `BLOCKED_SCHEMA` | *None* | Valid methodology grounded in abstract | `BLOCKED_FROM_UPDATE` |
| 16 | `470dd8df-...` | paper | `arxiv_2611_21885` | `research_domain` | **VERIFIED** | `BLOCKED_SCHEMA` | *None* | Valid domain grounded in abstract | `BLOCKED_FROM_UPDATE` |
| 17 | `e08e6ee7-...` | paper | `arxiv_2611_21885` | `methodology` | FAILED | `BLOCKED_SCHEMA` | *None* | Extraction failed quality rules | `BLOCKED_FROM_UPDATE` |
| 18 | `426b395c-...` | paper | `arxiv_2611_21053` | `methodology` | FAILED | `BLOCKED_SCHEMA` | *None* | Extraction failed quality rules | `BLOCKED_FROM_UPDATE` |
| 19 | `699e2aa3-...` | paper | `arxiv_2611_25567` | `methodology` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Novel extraction from abstract | `BLOCKED_FROM_UPDATE` |
| 20 | `d58c4683-...` | news | `news_824c03b970f1dc58` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 21 | `0ed884e8-...` | news | `news_701a571706ec6c00` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 22 | `af6f9092-...` | news | `news_4dcb26b5e50b7472` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 23 | `42c83120-...` | news | `news_92e2b2f37eb74112` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 24 | `d380b06f-...` | news | `news_aef632472a5e3af7` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 25 | `1f149513-...` | news | `news_ec56b5eff9affb1c` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 26 | `22b674a2-...` | news | `news_5b89a2db7f60ae90` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 27 | `87907ffc-...` | news | `news_8ec21efa2c622734` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 28 | `2d5eab44-...` | news | `news_cdc8eef67bc55a0d` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 29 | `422f64dc-...` | news | `news_96c7f67bef86f831` | `summary` | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `ai_news.summary` | Synthesizes article content | `PENDING_APPROVAL` |
| 30 | `a430e76d-...` | job | `job_e98b00bb44e6a41d` | `technologies` | FAILED | `BLOCKED_SCHEMA` | *None* | Target field missing | `BLOCKED_FROM_UPDATE` |
| 31 | `2b2e23c2-...` | job | `job_66f13e9130efa2e2` | `technologies` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Target field missing | `BLOCKED_FROM_UPDATE` |
| 32 | `abc9431e-...` | job | `job_b9465af7e79040f9` | `required_skills` | FAILED | `SCHEMA_COMPATIBLE` | `ai_jobs.required_skills` | Grounded in JD | `PENDING_APPROVAL` |
| 33 | `b8becf68-...` | job | `job_b9465af7e79040f9` | `technologies` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Target field missing | `BLOCKED_FROM_UPDATE` |
| 34 | `d271cb3d-...` | job | `job_45c1882c91f1b5d5` | `required_skills` | FAILED | `SCHEMA_COMPATIBLE` | `ai_jobs.required_skills` | Grounded in JD | `PENDING_APPROVAL` |
| 35 | `51d61887-...` | job | `job_45c1882c91f1b5d5` | `technologies` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Target field missing | `BLOCKED_FROM_UPDATE` |
| 36 | `a1da2f3a-...` | job | `job_bc685344022df5e7` | `required_skills` | FAILED | `SCHEMA_COMPATIBLE` | `ai_jobs.required_skills` | Grounded in JD | `PENDING_APPROVAL` |
| 37 | `124e74d4-...` | job | `job_bc685344022df5e7` | `technologies` | NEEDS_REVIEW | `BLOCKED_SCHEMA` | *None* | Target field missing | `BLOCKED_FROM_UPDATE` |

---

## 5. Summary Statistics (Audit 28 Revalidated)

- **Total Proposals Evaluated**: 37
- **Validation Status Distribution**:
  - `VERIFIED`: 3 (8.1%) — Proposals 6, 15, 16. All 3 are `BLOCKED_SCHEMA`.
  - `NEEDS_REVIEW`: 23 (62.2%) — 10 news summaries, 4 duplicate startup technologies, 9 others.
  - `FAILED`: 11 (29.7%) — 2 label-prefix startup proposals (Proposals 1 & 4), 9 extraction/quality failures.
  - `INSUFFICIENT_EVIDENCE`: 0 (0.0%).
- **Schema Compatibility Breakdown**:
  - `SCHEMA_COMPATIBLE`: 13 (35.1%) — 10 `ai_news.summary`, 3 `ai_jobs.required_skills`. None are VERIFIED.
  - `BLOCKED_SCHEMA`: 24 (64.9%) — Blocked from database update.
- **Verified Proposals Blocked by Schema**: 3 of 3 (100% of VERIFIED proposals target non-existent physical columns).
- **Startup Data Duplication**: 6 of 7 startup proposals duplicate existing canonical columns (`ai_focus_area` or `ai_evidence`).

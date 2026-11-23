# AI Ecosystem Intelligence Pipeline — Data Dictionary & Schema Specification

This document provides a comprehensive technical reference for all normalized SQLite database tables and corresponding Google Sheets worksheets across the AI Ecosystem Intelligence Pipeline.

---

## 1. Relational Entity Overview

```
  +------------------+         +-------------------------+
  |   ai_startups    |         |       ai_products       |
  |------------------|         |-------------------------|
  | id (PK)          |<---+    | id (PK)                 |
  | name             |    +----| company_id (FK)         |
  +------------------+         +-------------------------+
           |
           | (Mentioned in)
           v
  +------------------+         +-------------------------+
  |     ai_news      |         |         ai_jobs         |
  |------------------|         |-------------------------|
  | id (PK)          |         | id (PK)                 |
  | title            |         | startup_id (FK nullable)|
  +------------------+         +-------------------------+

  +-----------------------+    +-------------------------+
  |  ai_research_papers   |    |   github_repositories   |
  |-----------------------|    |-------------------------|
  | id (PK)               |<---| associated_paper_id(FK) |
  | title, arxiv_id       |    | repo_url (PK / Unique)  |
  +-----------------------+    +-------------------------+
                                            |
                                            v
                               +-------------------------+
                               | github_metric_snapshots |
                               |-------------------------|
                               | snapshot_id (PK)        |
                               | repo_id (FK)            |
                               +-------------------------+
```

---

## 2. Table Specifications & Column Definitions

### 2.1. `ai_startups` (Worksheet: `Startups`)
Stores corporate entities, founding profiles, and venture funding metadata.
- **Row Count**: 1,307 records
- **Primary Key**: `id`

| Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Number | No | Unique sequential primary key identifier. |
| `name` | `TEXT` | Plain Text | No | Normalized legal or operating brand name. |
| `website` | `TEXT` | Hyperlink | Yes | Official company landing domain or corporate URL. |
| `headquarters` | `TEXT` | Plain Text | Yes | Geographic location (`City, State, Country`). |
| `founded_year` | `INTEGER` | Number | Yes | Inception year (`YYYY`). Constrained: $1900 \le \text{year} \le 2026$. |
| `total_funding_usd` | `REAL` | Currency (`$#,##0`) | Yes | Cumulative verified venture funding raised in USD. |
| `funding_stage` | `TEXT` | Plain Text | Yes | Stage indicator (`Seed`, `Series A`, `Series B`, `Growth`, etc.). |
| `employee_count` | `INTEGER` | Number | Yes | Estimated headcount range midpoint or reported staff size. |
| `description` | `TEXT` | Plain Text | Yes | High-level corporate mission and technology focus summary. |
| `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | System extraction timestamp in UTC. |
| `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Last record modification timestamp in UTC. |

---

### 2.2. `ai_products` (Worksheet: `Products`)
Catalogs software tools, models, developer platforms, and commercial AI offerings.
- **Row Count**: 1,316 records
- **Primary Key**: `id`
- **Foreign Key**: `company_id -> ai_startups(id)`

| Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Number | No | Unique product identifier. |
| `name` | `TEXT` | Plain Text | No | Commercial or open-source product name. |
| `company_id` | `INTEGER` | Number | Yes | Parent startup entity reference. |
| `company_name` | `TEXT` | Plain Text | Yes | Denormalized company name for direct reporting. |
| `product_url` | `TEXT` | Hyperlink | Yes | Direct web link to product page or repository. |
| `category` | `TEXT` | Plain Text | Yes | Domain taxonomy (`LLM`, `Vision`, `DevOps`, `Audio`, etc.). |
| `pricing_model` | `TEXT` | Plain Text | Yes | Pricing classification (`Free`, `Freemium`, `Paid`, `Open Source`). |
| `launch_date` | `TEXT` | Date (`YYYY-MM-DD`) | Yes | Public general availability launch date. |
| `description` | `TEXT` | Plain Text | Yes | Brief functional description of capabilities. |
| `monthly_active_users` | `INTEGER` | Number | Yes | Estimated monthly active usage metrics where public. |
| `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Record generation timestamp in UTC. |
| `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Record refresh timestamp in UTC. |

---

### 2.3. `ai_research_papers` (Worksheet: `Research_Papers`)
Tracks academic publications, preprint breakthroughs, and algorithmic literature.
- **Row Count**: 1,060 records
- **Primary Key**: `id`

| Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Number | No | Unique research publication identifier. |
| `title` | `TEXT` | Plain Text | No | Exact title of academic research paper. |
| `authors` | `TEXT` | Plain Text | Yes | Delimited list of primary contributing researchers. |
| `abstract` | `TEXT` | Plain Text | Yes | Full paper abstract summarizing methodology and results. |
| `arxiv_id` | `TEXT` | Plain Text | Yes | Canonical arXiv identifier (e.g., `2310.12345`). |
| `published_date` | `TEXT` | Date (`YYYY-MM-DD`) | Yes | Official publication or preprint release date. |
| `primary_category` | `TEXT` | Plain Text | Yes | Computer Science primary taxonomy (`cs.AI`, `cs.CL`, `cs.CV`). |
| `citation_count` | `INTEGER` | Number | Yes | Total academic citation counter from Semantic Scholar. |
| `pdf_url` | `TEXT` | Hyperlink | Yes | Direct hyperlink to PDF preprint document. |
| `code_url` | `TEXT` | Hyperlink | Yes | Associated code repository referenced in paper. |
| `affiliation` | `TEXT` | Plain Text | Yes | Primary university or corporate research laboratory. |
| `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Paper extraction timestamp in UTC. |
| `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Metadata refresh timestamp in UTC. |

---

### 2.4. `ai_news` (Worksheet: `AI_News`)
Captures 24-hour fresh industry journalism, enterprise releases, and venture news.
- **Row Count**: 1,138 records
- **Primary Key**: `id`

| Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Number | No | Unique news article identifier. |
| `title` | `TEXT` | Plain Text | No | Headline of the news publication. |
| `source` | `TEXT` | Plain Text | No | Publishing entity (`TechCrunch`, `VentureBeat`, `The Verge`). |
| `url` | `TEXT` | Hyperlink | No | Canonical web link to published article. |
| `published_date` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Article publication timestamp. |
| `summary` | `TEXT` | Plain Text | Yes | Neural extraction summary of key events. |
| `primary_topic` | `TEXT` | Plain Text | Yes | Topical classification (`M&A`, `LLM Release`, `Policy`, `Funding`). |
| `sentiment_score` | `REAL` | Number (`0.00`) | Yes | Sentiment polarity score bounded $[-1.0, 1.0]$. |
| `relevance_score` | `REAL` | Number (`0.00`) | Yes | Domain AI relevance threshold score bounded $[0.0, 1.0]$. |
| `author` | `TEXT` | Plain Text | Yes | Journalist or staff author attribution. |
| `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | System ingestion timestamp in UTC. |
| `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Last update timestamp in UTC. |

---

### 2.5. `ai_jobs` (Worksheet: `AI_Jobs`)
Monitors market hiring demand, technical salary distributions, and vacancy lifecycle.
- **Row Count**: 1,963 records
- **Primary Key**: `id`
- **Foreign Key**: `company_id -> ai_startups(id)` (nullable)

| Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Number | No | Unique job posting record identifier. |
| `title` | `TEXT` | Plain Text | No | Official role title (`Research Scientist`, `AI Engineer`). |
| `company_name` | `TEXT` | Plain Text | No | Hiring company or enterprise employer. |
| `company_id` | `INTEGER` | Number | Yes | Foreign key reference to startup directory if matched. |
| `location` | `TEXT` | Plain Text | Yes | Work location (`Remote`, `San Francisco, CA`, `New York, NY`). |
| `employment_type` | `TEXT` | Plain Text | Yes | Employment model (`Full-time`, `Contract`, `Internship`). |
| `salary_min_usd` | `REAL` | Currency (`$#,##0`) | Yes | Minimum reported or parsed base annual compensation. |
| `salary_max_usd` | `REAL` | Currency (`$#,##0`) | Yes | Maximum reported or parsed base annual compensation. |
| `experience_level` | `TEXT` | Plain Text | Yes | Seniority classification (`Entry`, `Mid`, `Senior`, `Executive`). |
| `required_skills` | `TEXT` | Plain Text | Yes | Comma-separated list of technical competencies. |
| `listing_url` | `TEXT` | Hyperlink | Yes | Direct applicant portal URL. |
| `is_active` | `INTEGER` | Boolean (`TRUE`/`FALSE`) | No | Active vacancy status ($1 = \text{Active}, 0 = \text{Closed}$). |
| `posted_date` | `TEXT` | Date (`YYYY-MM-DD`) | Yes | Original job posting timestamp. |
| `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Ingestion timestamp in UTC. |
| `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Last verification timestamp in UTC. |

---

### 2.6. `github_repositories` (Worksheet: `GitHub_Repositories`)
Comprehensive software telemetry for open-source AI projects linked to research papers.
- **Row Count**: 192 records
- **Primary Key**: `id`
- **Unique**: `repo_url`
- **Foreign Key**: `associated_paper_id -> ai_research_papers(id)`

| Col # | Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `id` | `INTEGER` | Number | No | Unique repository tracking identifier. |
| 2 | `associated_paper_id`| `INTEGER` | Number | Yes | Foreign key referencing `ai_research_papers(id)`. |
| 3 | `collection_run_id` | `TEXT` | Plain Text | Yes | Provenance telemetry run identifier. |
| 4 | `repo_url` | `TEXT` | Hyperlink | No | Normalized canonical GitHub web URL (`https://github.com/...`). |
| 5 | `owner` | `TEXT` | Plain Text | No | GitHub organization or username owning repository. |
| 6 | `name` | `TEXT` | Plain Text | No | Repository project name. |
| 7 | `full_name` | `TEXT` | Plain Text | No | Canonical owner/name path (`huggingface/transformers`). |
| 8 | `description` | `TEXT` | Plain Text | Yes | Repository description from GitHub API. |
| 9 | `primary_language` | `TEXT` | Plain Text | Yes | Detected primary programming language (`Python`, `C++`). |
| 10 | `is_archived` | `INTEGER` | Boolean (`TRUE`/`FALSE`) | No | Repository read-only status ($1 = \text{Archived}, 0 = \text{Active}$). |
| 11 | `is_fork` | `INTEGER` | Boolean (`TRUE`/`FALSE`) | No | Fork status ($1 = \text{Fork}, 0 = \text{Root}$). |
| 12 | `license_spdx_id` | `TEXT` | Plain Text | Yes | Standard SPDX license identifier (`Apache-2.0`, `MIT`). |
| 13 | `lifecycle_status` | `TEXT` | Plain Text | No | Verified 8-state FSM status (`ACTIVE_VERIFIED`, etc.). |
| 14 | `evidence_http_code` | `INTEGER` | Number | Yes | Verified HTTP status code returned by API. |
| 15 | `stars_count` | `INTEGER` | Number (`#,##0`) | No | Current stargazer count. |
| 16 | `forks_count` | `INTEGER` | Number (`#,##0`) | No | Current fork count. |
| 17 | `open_issues_count` | `INTEGER` | Number (`#,##0`) | No | Current open issue count. |
| 18 | `watchers_count` | `INTEGER` | Number (`#,##0`) | No | Current subscriber watcher count. |
| 19 | `has_wiki` | `INTEGER` | Boolean (`TRUE`/`FALSE`) | No | Wiki module enabled flag. |
| 20 | `has_pages` | `INTEGER` | Boolean (`TRUE`/`FALSE`) | No | GitHub Pages website enabled flag. |
| 21 | `repo_created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | Yes | GitHub repository creation timestamp in UTC. |
| 22 | `repo_updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | Yes | GitHub repository last push timestamp in UTC. |
| 23 | `last_synced_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | Yes | Last successful API collection timestamp in UTC. |
| 24 | `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Local system row creation timestamp in UTC. |
| 25 | `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Local system row modification timestamp in UTC. |

---

### 2.7. `github_metric_snapshots` (Worksheet: `GitHub_Metrics`)
Time-series longitudinal capture of code momentum, community growth, and deltas.
- **Row Count**: 205 records
- **Primary Key**: `id`
- **Foreign Key**: `repo_id -> github_repositories(id)`

| Col # | Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `id` | `INTEGER` | Number | No | Unique metric snapshot identifier. |
| 2 | `repo_id` | `INTEGER` | Number | No | Foreign key referencing `github_repositories(id)`. |
| 3 | `collection_run_id` | `TEXT` | Plain Text | Yes | Ingestion batch execution identifier. |
| 4 | `snapshot_date` | `TEXT` | Date (`YYYY-MM-DD`) | No | Calendar date of metric recording. |
| 5 | `stars` | `INTEGER` | Number (`#,##0`) | No | Stargazer metric on snapshot date. |
| 6 | `forks` | `INTEGER` | Number (`#,##0`) | No | Fork metric on snapshot date. |
| 7 | `open_issues` | `INTEGER` | Number (`#,##0`) | No | Open issue metric on snapshot date. |
| 8 | `watchers` | `INTEGER` | Number (`#,##0`) | No | Watcher metric on snapshot date. |
| 9 | `stars_delta` | `INTEGER` | Number (`+#,##0;-#,##0;0`) | Yes | Day-over-day star velocity. |
| 10 | `forks_delta` | `INTEGER` | Number (`+#,##0;-#,##0;0`) | Yes | Day-over-day fork velocity. |
| 11 | `issues_delta` | `INTEGER` | Number (`+#,##0;-#,##0;0`) | Yes | Day-over-day open issues change. |
| 12 | `watchers_delta` | `INTEGER` | Number (`+#,##0;-#,##0;0`) | Yes | Day-over-day watchers change. |
| 13 | `commit_count_30d` | `INTEGER` | Number (`#,##0`) | Yes | Rolling 30-day commit volume. |
| 14 | `pull_requests_30d` | `INTEGER` | Number (`#,##0`) | Yes | Rolling 30-day pull request throughput. |
| 15 | `contributors_count`| `INTEGER` | Number (`#,##0`) | Yes | Total distinct contributing authors. |
| 16 | `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Local system row creation timestamp in UTC. |
| 17 | `updated_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Local system row modification timestamp in UTC. |

---

### 2.8. `collection_logs` (Worksheet: `Collection_Logs`)
Execution telemetry auditing pipeline runs, harvesters, error counts, and durations.
- **Row Count**: 6 records
- **Primary Key**: `id`

| Col # | Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `id` | `INTEGER` | Number | No | Unique log execution identifier. |
| 2 | `run_id` | `TEXT` | Plain Text | No | UUIDv4 identifier of collection run. |
| 3 | `source_name` | `TEXT` | Plain Text | No | Source subsystem (`arxiv`, `news`, `github`, `jobs`). |
| 4 | `execution_type` | `TEXT` | Plain Text | No | Mode (`full_scrape`, `delta_sync`, `verification`). |
| 5 | `records_fetched` | `INTEGER` | Number | No | Total raw items acquired during execution. |
| 6 | `records_inserted`| `INTEGER` | Number | No | Net new records written to database. |
| 7 | `records_updated` | `INTEGER` | Number | No | Existing records refreshed in database. |
| 8 | `errors_count` | `INTEGER` | Number | No | Count of caught HTTP or parsing exceptions. |
| 9 | `duration_seconds`| `REAL` | Number (`0.00`) | No | Total run duration in seconds. |
| 10 | `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Execution timestamp in UTC. |

---

### 2.9. `sync_log` (Worksheet: `Sync_Log`)
Google Sheets synchronization audit trail tracking cell updates and API quotas.
- **Row Count**: 1 record per sync run
- **Primary Key**: `id`

| Col # | Column Name | SQLite Type | Google Sheets Format | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `id` | `INTEGER` | Number | No | Unique sync run identifier. |
| 2 | `sync_id` | `TEXT` | Plain Text | No | Synchronizer run identifier. |
| 3 | `target_spreadsheet_id`| `TEXT` | Plain Text | No | Destination Google Sheet ID. |
| 4 | `worksheets_synced` | `INTEGER` | Number | No | Total worksheet tabs updated (11). |
| 5 | `cells_updated` | `INTEGER` | Number | No | Total cell payload written (11,481). |
| 6 | `api_calls_made` | `INTEGER` | Number | No | Total HTTP batch requests executed (3). |
| 7 | `status` | `TEXT` | Plain Text | No | Execution status (`SUCCESS`, `PARTIAL`, `FAILED`). |
| 8 | `error_details` | `TEXT` | Plain Text | Yes | Exception traceback or error summary. |
| 9 | `duration_seconds`| `REAL` | Number (`0.00`) | No | Total round-trip synchronization latency. |
| 10 | `created_at` | `TEXT` | Date (`YYYY-MM-DD HH:MM:SS`) | No | Timestamp of synchronization pass. |

---

### 2.10. `data_dictionary` (Worksheet: `Data_Dictionary`)
Live in-spreadsheet schema metadata defining data types, business rules, and ranges.
- **Row Count**: 31 records

| Col # | Column Name | SQLite Type | Google Sheets Format | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `table_name` | `TEXT` | Plain Text | No | Associated database table. |
| 2 | `column_name` | `TEXT` | Plain Text | No | Name of column attribute. |
| 3 | `data_type` | `TEXT` | Plain Text | No | Storage type (`INTEGER`, `TEXT`, `REAL`, `BOOLEAN`). |
| 4 | `nullable` | `TEXT` | Plain Text | No | Nullability indicator (`YES`, `NO`). |
| 5 | `primary_key` | `TEXT` | Plain Text | No | Primary key indicator (`YES`, `NO`). |
| 6 | `foreign_key` | `TEXT` | Plain Text | Yes | Relational constraint target (`table.column`). |
| 7 | `description` | `TEXT` | Plain Text | No | Functional definition of attribute. |
| 8 | `allowed_values` | `TEXT` | Plain Text | Yes | Domain values or enum states. |
| 9 | `validation_rule`| `TEXT` | Plain Text | Yes | Business logic or range constraint. |
| 10 | `source_pipeline`| `TEXT` | Plain Text | No | Pipeline module responsible for column. |
| 11 | `last_reviewed` | `TEXT` | Date (`YYYY-MM-DD`) | No | Last schema audit verification date. |

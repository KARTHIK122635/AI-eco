# Phase VI Worksheet Schema Proposal — AI Ecosystem Intelligence Dashboard

**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — Dashboard Integration  
**Document:** Google Sheets Worksheet Schema Proposal & Layout Architecture  
**Spreadsheet:** `AI Ecosystem Intelligence Dashboard` (`194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`)  
**Source Database:** `data/working/phase5_github_candidate.db` (SHA-256: `dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`)  
**Generated Date:** 2026-11-23  

---

## 1. Architectural Strategy & Safety Boundaries

The Phase VI dashboard integration connects the accepted Phase V GitHub intelligence into the live Google Spreadsheet created in Phase IV. 

### Safety & Non-Destructive Guarantees
1. **Core Data Immutability:** Worksheets 2 through 6 (`Startups`, `Products`, `Research_Papers`, `AI_News`, `AI_Jobs`) and Worksheet 9 (`Collection_Logs`) remain **100% untouched** in structure and row content.
2. **Worksheet Evolution vs Addition:**
   - Existing Worksheet 7 (`GitHub_Repositories`) evolves from a 12-column placeholder into a 25-column production entity table (expanding from 190 to 192 rows).
   - Existing Worksheet 8 (`GitHub_Metrics`) evolves from a 10-column placeholder into a 17-column longitudinal metrics table (expanding from 205 to 210 rows).
   - A dedicated 12th worksheet (`GitHub_Associations`) is proposed to normalize entity linkages (192 rows, 11 columns).
   - A dedicated 13th worksheet (`GitHub_Analytics`) is proposed to store pre-aggregated summary dimensions and chart feeds (47 rows, 8 columns).
3. **Dashboard Non-Interference:** Existing Phase IV ecosystem KPI cards and tables occupy rows 1–24. The GitHub Ecosystem section is placed starting at row 26, leaving Phase IV layout completely intact.

---

## 2. Worksheet 7: `GitHub_Repositories` (Schema Evolution)

### Context & Justification
In Phase IV, `GitHub_Repositories` contained 190 rows and 12 columns. However, Phase V expanded the repository catalog to 192 unique entities and introduced the 8-state lifecycle classification model, multi-level evidence quality scoring, association indexing, and standardized UTC audit timestamps.

### Proposed Schema (25 Columns)

| Col # | Column Header | Data Type | Nullable | Source Field / Derivation | Example Value | Description |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **A** | `repo_id` | STRING (PK) | NO | `github_repositories.repo_id` | `PDFMathTranslate/PDFMathTranslate` | Canonical repository identifier (`owner/repo_name`). |
| **B** | `owner` | STRING | NO | `github_repositories.owner` | `PDFMathTranslate` | GitHub organization or user account. |
| **C** | `repo_name` | STRING | NO | `github_repositories.repo_name` | `PDFMathTranslate` | Repository repository name. |
| **D** | `full_name` | STRING | NO | `github_repositories.full_name` | `PDFMathTranslate/PDFMathTranslate` | Full repository name. |
| **E** | `html_url` | URL | NO | `github_repositories.html_url` | `https://github.com/PDFMathTranslate/...` | Direct web hyperlink to GitHub repository. |
| **F** | `description` | TEXT | YES | `github_repositories.description` | `PDF scientific paper translation...` | Sanitized repository description. |
| **G** | `primary_language`| STRING | YES | `github_repositories.primary_language` | `Python` | Predominant programming language. |
| **H** | `latest_stars` | INTEGER | NO | `github_repositories.latest_stars` | `38601` | Most recently recorded stargazer count. |
| **I** | `latest_forks` | INTEGER | NO | `github_repositories.latest_forks` | `3457` | Most recently recorded fork count. |
| **J** | `latest_open_issues`| INTEGER | NO | `github_repositories.latest_open_issues` | `171` | Most recently recorded open issue count. |
| **K** | `is_archived` | BOOLEAN | NO | `github_repositories.is_archived` | `FALSE` | GitHub API repository archived flag. |
| **L** | `is_fork` | BOOLEAN | NO | `github_repositories.is_fork` | `FALSE` | Upstream fork indicator. |
| **M** | `default_branch` | STRING | YES | `github_repositories.default_branch` | `main` | Primary git branch name. |
| **N** | `license_spdx` | STRING | YES | `github_repositories.license_spdx` | `GPL-3.0` | Open-source license identifier. |
| **O** | `lifecycle_status`| STRING | NO | `github_repositories.lifecycle_status` | `ACTIVE_VERIFIED` | 8-state verified lifecycle classification. |
| **P** | `evidence_quality`| STRING | NO | `github_repositories.evidence_quality` | `HIGH_CONFIDENCE` | Data provenance score (`HIGH`, `MEDIUM`, `LOW`). |
| **Q** | `association_count`| INTEGER| NO | Computed subquery | `1` | Number of linked papers/products/startups. |
| **R** | `latest_snapshot_at`| TIMESTAMP| YES | `github_repositories.latest_snapshot_at` | `2026-11-23T07:04:10+00:00` | ISO 8601 UTC timestamp of latest metric poll. |
| **S** | `last_pushed_at`| TIMESTAMP| YES | `github_repositories.last_pushed_at` | `2026-11-22T19:40:12+00:00` | Last git commit push timestamp from API. |
| **T** | `repo_created_at`| TIMESTAMP| YES | `github_repositories.repo_created_at` | `2024-03-15T10:00:00+00:00` | Upstream GitHub repo creation timestamp. |
| **U** | `first_discovered_at`| TIMESTAMP| NO | `github_repositories.first_discovered_at` | `2026-11-21T06:00:00+00:00` | Local discovery timestamp into pipeline. |
| **V** | `last_checked_at`| TIMESTAMP| YES | `github_repositories.last_checked_at` | `2026-11-23T07:04:10+00:00` | Ingestion check timestamp. |
| **W** | `topics` | TEXT | YES | `github_repositories.topics` | `pdf, translation, ocr, deep-learning` | Comma-separated GitHub repository topics. |
| **X** | `weekly_star_delta`| INTEGER| YES | Computed from latest metrics | `132` | 7-day stargazer delta (if verified). |
| **Y** | `data_freshness` | STRING | NO | Computed evaluation | `CURRENT_SNAPSHOT` | Evaluation of telemetry timeliness. |

* **Total Row Count:** 193 rows (1 header row + 192 data rows).

---

## 3. Worksheet 8: `GitHub_Metrics` (Schema Evolution)

### Context & Justification
In Phase IV, `GitHub_Metrics` contained 205 rows and 10 columns. Phase V expanded snapshots to 210 records (incorporating the verified reconciliation run `run_gh_manual_20261123_070409`) and introduced velocity tracking, reliability gating, and snapshot collection identifiers.

### Proposed Schema (17 Columns)

| Col # | Column Header | Data Type | Nullable | Source Field / Derivation | Example Value | Description |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **A** | `metric_id` | STRING (PK) | NO | `github_metrics_history.metric_id` | `ghm_001` | Unique surrogate key for the snapshot. |
| **B** | `repo_id` | STRING (FK) | NO | `github_metrics_history.repo_id` | `PDFMathTranslate/PDFMathTranslate` | Target repository identifier. |
| **C** | `stars` | INTEGER | NO | `github_metrics_history.stars` | `38601` | Stargazer count at snapshot time. |
| **D** | `forks` | INTEGER | NO | `github_metrics_history.forks` | `3457` | Fork count at snapshot time. |
| **E** | `open_issues` | INTEGER | NO | `github_metrics_history.open_issues` | `171` | Open issues count at snapshot time. |
| **F** | `change_stars_delta`| INTEGER| YES | `github_metrics_history.change_stars_delta` | `132` | Absolute stargazer change from previous snapshot. |
| **G** | `change_forks_delta`| INTEGER| YES | `github_metrics_history.change_forks_delta` | `19` | Absolute fork change from previous snapshot. |
| **H** | `change_issues_delta`| INTEGER| YES | Computed from history | `0` | Absolute issue count change. |
| **I** | `daily_stars_velocity`| FLOAT | YES | `change_stars_delta / interval_days` | `63.46` | Normalized daily rate of star growth. |
| **J** | `observation_interval_days`| FLOAT| YES | `github_metrics_history.observation_interval_days` | `2.08` | Duration in days between snapshots. |
| **K** | `weekly_growth_status`| STRING| NO | Growth policy check | `INSUFFICIENT_DATA` | `VERIFIED_WEEKLY` if $\ge 5.0\text{d}$, else `INSUFFICIENT_DATA`. |
| **L** | `is_growth_reliable` | BOOLEAN | NO | Gating logic | `FALSE` | Strict boolean flag for reporting. |
| **M** | `recorded_at` | TIMESTAMP| NO | `github_metrics_history.recorded_at` | `2026-11-23T07:04:10+00:00` | Snapshot capture timestamp (UTC). |
| **N** | `collection_run_id`| STRING | NO | `github_metrics_history.collection_run_id` | `run_gh_manual_20261123_070409` | ID of pipeline collection execution. |
| **O** | `ingestion_batch_id`| STRING | YES | `github_metrics_history.ingestion_batch_id` | `batch_manual_rec_01` | Ingestion batch identifier. |
| **P** | `api_endpoint_used` | STRING | YES | Ingestion provenance | `/repos/{owner}/{repo}` | GitHub REST API endpoint queried. |
| **Q** | `http_status` | INTEGER | NO | Pipeline audit log | `200` | HTTP response code returned by GitHub. |

* **Total Row Count:** 211 rows (1 header row + 210 data rows).

---

## 4. Proposed Worksheet 12: `GitHub_Associations` (New Normalized Entity)

### Justification & Entity Integrity
Linking GitHub repositories directly to research papers and commercial products is a core value proposition of the AI Ecosystem Intelligence Pipeline. Without a dedicated association worksheet, repository links would be denormalized or lost.

### Proposed Schema (11 Columns)

| Col # | Column Header | Data Type | Nullable | Source Field / Derivation | Example Value | Description |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **A** | `association_id` | STRING (PK) | NO | `github_repository_associations.association_id` | `gha_001` | Unique surrogate key for the association. |
| **B** | `entity_type` | STRING | NO | `github_repository_associations.entity_type` | `research_paper` | Category of linked entity (`research_paper`, `product`, `startup`). |
| **C** | `entity_id` | STRING (FK) | NO | `github_repository_associations.entity_id` | `paper_0025` | Primary key of linked entity in parent sheet. |
| **D** | `entity_name` | STRING | YES | Linked entity lookup | `PDFMathTranslate Paper Title` | Human-readable title of linked entity. |
| **E** | `repo_id` | STRING (FK) | NO | `github_repository_associations.repo_id` | `PDFMathTranslate/PDFMathTranslate` | Target repository identifier. |
| **F** | `association_type` | STRING | NO | `github_repository_associations.association_type` | `OFFICIAL_IMPLEMENTATION` | Link semantic role (`OFFICIAL`, `COMMUNITY`, `REPLICATION`). |
| **G** | `source_url` | URL | YES | `github_repository_associations.source_url` | `https://arxiv.org/abs/2408.xxxxx` | Web provenance where GitHub link was cited. |
| **H** | `verification_status`| STRING| NO | `github_repository_associations.verification_status`| `HIGH_CONFIDENCE` | Validation state (`HIGH_CONFIDENCE`, `MANUAL_REVIEW`, `UNVERIFIED`). |
| **I** | `confidence_score`| FLOAT | NO | `github_repository_associations.confidence_score` | `1.0` | Algorithmic matching score (0.0 – 1.0). |
| **J** | `extracted_at` | TIMESTAMP| NO | `github_repository_associations.extracted_at` | `2026-11-21T06:00:00+00:00` | Timestamp when linkage was extracted. |
| **K** | `notes` | TEXT | YES | `github_repository_associations.notes` | `Extracted from arXiv abstract` | Curation and verification notes. |

* **Total Row Count:** 193 rows (1 header row + 192 data rows: 191 research papers, 1 product).

---

## 5. Proposed Worksheet 13: `GitHub_Analytics` (Pre-Aggregated Feeds)

### Justification & Performance
To keep the primary `Dashboard` performant and avoid heavy multi-condition array formulas that can cause Google Sheets latency, `GitHub_Analytics` provides structured pre-computed tables for KPI cards, leaderboard lookups, and chart ranges.

### Proposed Schema (8 Columns)

| Col # | Column Header | Data Type | Nullable | Description |
| :---: | :--- | :--- | :---: | :--- |
| **A** | `dimension` | STRING | NO | Categorical dimension (e.g. `LIFECYCLE_STATUS`, `PRIMARY_LANGUAGE`, `SUMMARY_KPIS`, `TOP_STARS_LEADERBOARD`). |
| **B** | `metric_key` | STRING | NO | Unique lookup key (e.g. `ACTIVE_VERIFIED`, `Python`, `TOTAL_STARS`, `RANK_01`). |
| **C** | `metric_label` | STRING | NO | Human-readable display label. |
| **D** | `value_numeric` | FLOAT / INT | YES | Primary quantitative value. |
| **E** | `value_text` | STRING | YES | Primary textual representation. |
| **F** | `percentage` | FLOAT | YES | Calculated share / percentage (0.00 – 100.00). |
| **G** | `secondary_value`| FLOAT / INT | YES | Auxiliary metric (e.g. forks, issue count, total papers). |
| **H** | `notes` | TEXT | YES | Methodological or audit notes. |

* **Total Row Count:** 48 rows (1 header row + 47 data rows).
* **Row Segment Breakdown:**
  - Rows 2–10: 8-State Lifecycle Breakdown (8 data rows + 1 total).
  - Rows 11–20: Core Summary KPI Table (10 data rows).
  - Rows 21–25: Primary Language Breakdown (3 languages + Unknown + Total).
  - Rows 26–45: Top 20 Repositories by Stargazers (20 data rows).
  - Rows 46–48: Association Quality Breakdown (3 status levels).

---

## 6. Dashboard Layout Architecture (Worksheet 1 Expansion)

### Current Spatial Organization (Phase IV)
* **Rows 1–2:** Global Dashboard Title & Synchronization Banner (`AI Ecosystem Intelligence Dashboard`, last synced timestamp).
* **Rows 4–5:** Four Phase IV Ecosystem KPI Cards (`Startups`, `Products`, `Research Papers`, `AI News`, `Job Vacancies`).
* **Rows 7–24:** Core Ecosystem Breakdown Tables (Startup Taxonomy, Job Verification Status) and anchors for Charts 1 to 6.

### Proposed GitHub Expansion (Rows 26–45)
* **Row 26:** Section Banner
  - Merged `A26:L26` with Navy Fill (`#1A365D`), White Bold Text: `"GITHUB OPEN-SOURCE ECOSYSTEM INTELLIGENCE & CODE VELOCITY"`.
* **Rows 27–29: Five GitHub Executive KPI Cards**
  - **Card 1 (`A27:B29`):** **Total Tracked Repositories**  
    Formula: `=COUNTA(GitHub_Repositories!A2:A)` | Value: `192` | Subtitle: `"Discovered across papers & products"`
  - **Card 2 (`C27:D29`):** **Verified Active Repositories**  
    Formula: `=COUNTIF(GitHub_Repositories!O2:O, "ACTIVE_VERIFIED")` | Value: `61` | Subtitle: `"=TEXT(D27/B27, ""0.0%"") & "" verified operational"""`
  - **Card 3 (`E27:F29`):** **Pending Verification Backlog**  
    Formula: `=COUNTIF(GitHub_Repositories!O2:O, "NOT_YET_CHECKED")` | Value: `131` | Subtitle: `"Awaiting rate-limit allocation"`
  - **Card 4 (`G27:H29`):** **Total Community Stargazers**  
    Formula: `=SUM(GitHub_Repositories!H2:H)` | Value: `39,975` | Subtitle: `"=TEXT(SUM(GitHub_Repositories!I2:I), ""#,##0"") & "" total forks"""`
  - **Card 5 (`I27:J29`):** **Research Paper Code Coverage**  
    Formula: `=COUNTIF(GitHub_Associations!B2:B, "research_paper") / COUNTA(Research_Papers!A2:A)` | Value: `17.92%` | Subtitle: `"190 of 1,060 papers linked"`
  - **Card 6 (`K27:L29`):** **Longitudinal Snapshot Count**  
    Formula: `=COUNTA(GitHub_Metrics!A2:A)` | Value: `210` | Subtitle: `"19 delta-eligible series"`
* **Rows 31–38: Top Repositories & Tech Stack Breakdown**
  - Columns `A–G`: Top 5 Open-Source AI Repositories Leaderboard (Columns: Rank, Repository Name, Owner, Language, Stars, Forks, Status).
  - Columns `H–L`: Primary Language Traction Summary (Table feeding Chart 8).
* **Rows 39–45: Repository Lifecycle Status & Velocity Audit**
  - Columns `A–F`: 8-State Lifecycle Distribution Table (Table feeding Chart 7).
  - Columns `G–L`: Growth & Momentum Status Panel (Displaying weekly policy status: `INSUFFICIENT_DATA (<5.0d)` with diagnostic 2-day velocity notes).

---

## 7. Chart Integration Specifications

| Chart ID | Proposed Title | Chart Type | Source Sheet & Range | Target Position | Dimensions |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **Chart 7** | `GitHub Repository Lifecycle Distribution` | Donut Chart (`PIE`) | `GitHub_Analytics!B2:D9` | `Dashboard!A46:F62` | 600px $\times$ 350px |
| **Chart 8** | `Top AI Research Repositories by Stargazers` | Horizontal Bar Chart (`BAR`) | `GitHub_Analytics!C26:D35` | `Dashboard!G46:L62` | 600px $\times$ 350px |

* **Chart 7 Details:** Visualizes verified active (`ACTIVE_VERIFIED`), pending checks (`NOT_YET_CHECKED`), and anomalies (0) to guarantee complete transparency on collection coverage.
* **Chart 8 Details:** Visualizes the top 10 AI research repositories by star volume to highlight dominant community codebases (`PDFMathTranslate`, `ml-depth-pro-2`, etc.).

---

## 8. Updates to `Data_Dictionary` & `Sync_Log`

### `Data_Dictionary` (Worksheet 11) Additions
Rows to be appended to `Data_Dictionary` to document the new and evolved structures:
1. `GitHub_Repositories` (13 new rows): Defining `primary_language`, `latest_open_issues`, `is_fork`, `default_branch`, `license_spdx`, `lifecycle_status`, `evidence_quality`, `association_count`, `latest_snapshot_at`, `weekly_star_delta`, `topics`, `data_freshness`.
2. `GitHub_Metrics` (7 new rows): Defining `change_issues_delta`, `daily_stars_velocity`, `weekly_growth_status`, `is_growth_reliable`, `collection_run_id`, `ingestion_batch_id`, `api_endpoint_used`.
3. `GitHub_Associations` (11 rows): Full dictionary specification for the new table.
4. `GitHub_Analytics` (8 rows): Full dictionary specification for the pre-aggregated summary table.

### `Sync_Log` (Worksheet 10) Entry Preview
When Phase VI is authorized for synchronization, the following audit entry will be appended:
* **Run ID:** `sync_p6_20261123_dashboard`
* **Timestamp:** Current ISO UTC timestamp
* **Worksheets Updated:** `Dashboard`, `GitHub_Repositories`, `GitHub_Metrics`, `Data_Dictionary`, `Sync_Log`
* **Worksheets Added:** `GitHub_Associations`, `GitHub_Analytics`
* **Total Rows Written:** 641 tabular rows + dashboard configuration + metadata.
* **Status:** `SUCCESS`

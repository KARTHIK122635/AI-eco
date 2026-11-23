# Phase VI Architecture Assessment: Google Sheets Dashboard Integration

**Architect:** Senior Data Engineer, Python Backend Architect & Analytics Dashboard Developer  
**Date:** 2026-11-23  
**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — AI Ecosystem Intelligence Dashboard Integration  
**Target Spreadsheet:** `AI Ecosystem Intelligence Dashboard` (`194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`)  
**Status:** ARCHITECTURE ASSESSED & DESIGN VALIDATED  

---

## 1. Executive Summary

This architecture assessment evaluates the integration of Phase V GitHub Ecosystem Intelligence into the operational Phase IV Google Sheets dashboard (`194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`).

The existing spreadsheet was created during Phase IV and successfully hosts 7,185 core ecosystem records across 11 worksheets, supported by 6 executive charts and 10 KPI summary cards. However, the current GitHub worksheets (`GitHub_Repositories` with 190 records and `GitHub_Metrics` with 205 records) reflect only the pre-Phase V schema and do not incorporate the rich metadata, evidence-based lifecycle classifications, multi-source associations, or verified growth velocities developed in Phase V.

This assessment validates the technical strategy to:
1. Extend existing `GitHub_Repositories` and `GitHub_Metrics` worksheets non-destructively.
2. Introduce a dedicated `GitHub_Associations` worksheet to expose the 192 entity-repository links with evidence scoring.
3. Introduce a structured `GitHub_Analytics` worksheet to host pre-aggregated KPI summaries, language distribution, and growth rankings.
4. Upgrade the `Dashboard` worksheet with dedicated GitHub KPI cards, lifecycle distribution visuals, and code coverage metrics.
5. Implement a local, deterministic, and parameterized data exporter (`core/github_dashboard_exporter.py`).

---

## 2. Existing Spreadsheet & Architecture Inspection

### 2.1 Google Sheets OAuth Authentication
- **Client Configuration:** Managed via `core/google_sheets_client.py` using `secrets/google_oauth_client.json` and persistent token file `secrets/google_sheets_token.json`.
- **Scopes Configured:**
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive.file`
- **Connectivity Status:** Verified via read-only API call. The stored OAuth credentials remain valid and active (`AUTHENTICATED_AND_CONNECTED`). No secrets or credentials were exposed.

### 2.2 Live Worksheet Inventory & Header Audit (11 Worksheets)
A live, read-only inspection of spreadsheet `194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI` was conducted using `spreadsheets().get`:

| Sheet ID | Worksheet Title | Current Rows | Current Cols | Charts | Role & Invariant Status |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `716942602` | `Dashboard` | 1,000 | 26 | 6 | Executive KPI cards & charts |
| `706017576` | `Startups` | 1,317 | 24 | 0 | 1,307 startups + 1 header row |
| `740012032` | `Products` | 1,326 | 26 | 0 | 1,316 products + 1 header row |
| `433251445` | `Research_Papers` | 1,070 | 22 | 0 | 1,060 research papers + 1 header row |
| `855816761` | `AI_News` | 1,148 | 20 | 0 | 1,138 AI news records + 1 header row |
| `2028636850` | `AI_Jobs` | 1,973 | 36 | 0 | 1,963 AI job vacancies + 1 header row |
| `483368398` | `GitHub_Repositories` | 1,000 | 26 | 0 | 190 Phase IV repositories + 1 header row |
| `1243210950` | `GitHub_Metrics` | 1,000 | 26 | 0 | 205 Phase IV metric snapshots + 1 header row |
| `1701058697` | `Collection_Logs` | 1,000 | 31 | 0 | 6 collection checkpoints + 1 header row |
| `1081150275` | `Sync_Log` | 1,000 | 26 | 0 | 2 sync execution records + 1 header row |
| `450784151` | `Data_Dictionary` | 1,000 | 26 | 0 | 152 data dictionary definitions + 1 header row |

### 2.3 Existing Dashboard Formulas and Chart Audit
- **Header:** Row 1 (`AI ECOSYSTEM INTELLIGENCE DASHBOARD`) and Row 2 (Subtitle).
- **KPI Summary Cards (Rows 4–5):**
  - Col A: `Total Startups` $\rightarrow$ `=COUNTA(Startups!A2:A)`
  - Col B: `Total Products` $\rightarrow$ `=COUNTA(Products!A2:A)`
  - Col C: `Total Research Papers` $\rightarrow$ `=COUNTA(Research_Papers!A2:A)`
  - Col D: `Total AI News` $\rightarrow$ `=COUNTA(AI_News!A2:A)`
  - Col E: `Total AI Jobs` $\rightarrow$ `=COUNTA(AI_Jobs!A2:A)`
  - Col F: `Six-Month Eligible Content` $\rightarrow$ Sum of `COUNTIF` for eligible flags across dated entities (3,302 content records).
  - Col G: `Fresh Content (24 Hours)` $\rightarrow$ Sum of `COUNTIF` for 24h fresh flags across entities.
  - Col H: `Tracked GitHub Repositories` $\rightarrow$ `=COUNTA(GitHub_Repositories!A2:A)`
  - Col I: `GitHub Metric Snapshots` $\rightarrow$ `=COUNTA(GitHub_Metrics!A2:A)`
  - Col J: `Pipeline Collection Runs` $\rightarrow$ `=COUNTA(Collection_Logs!A2:A)`
- **Existing Visualization Charts (6 Intended Visualizations):**
  1. Chart ID `95220720`: `AI Job Vacancies by Taxonomy Category` (Bar chart)
  2. Chart ID `1823106458`: `AI Startup Domain & Focus Area Distribution` (Pie / Donut)
  3. Chart ID `1057234590`: `Vacancy Verification & Lifecycle Status Distribution` (Column)
  4. Chart ID `329083026`: `Research Paper Domain Category Distribution` (Column)
  5. Chart ID `1272405867`: `Commercial AI Product Categories` (Bar chart)
  6. Chart ID `2083097885`: `AI News Editorial Category Distribution` (Donut / Pie)

---

## 3. Data Source Inspection: Phase V Candidate Database

The source database for Phase VI is `data/working/phase5_github_candidate.db` (SHA-256: `dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`), accessed in strict read-only mode (`file:...db?mode=ro`).

### 3.1 Comparison: Existing Sheet vs. Phase V Database

```
Existing GitHub_Repositories Sheet (12 Columns):
[repo_id, owner, repo_name, html_url, description, associated_paper_id, is_archived, latest_stars, latest_forks, last_checked_at, status, last_synced_at]

Phase V Database github_repositories (22 Columns):
[repo_id, owner, repo_name, html_url, description, associated_paper_id, is_archived, latest_stars, latest_forks, last_checked_at, status, full_name, primary_language, topics, latest_open_issues, created_timestamp, updated_timestamp, pushed_timestamp, default_branch, is_fork, license_spdx_id, collection_run_id]
```

```
Existing GitHub_Metrics Sheet (10 Columns):
[snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count, change_stars_delta, change_forks_delta, retrieval_status, provenance, last_synced_at]

Phase V Database github_metrics_history (13 Columns):
[snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count, change_stars_delta, change_forks_delta, retrieval_status, provenance, open_issues_count, change_open_issues_delta, source_api, collection_run_id]
```

```
Phase V Database github_repository_associations (10 Columns - Currently NOT in Sheets):
[association_id, source_entity_type, source_entity_id, repo_id, evidence_url, evidence_type, confidence, discovery_timestamp, verification_status, notes]
```

---

## 4. Architectural Worksheet Evolution Strategy

### 4.1 Can Existing Worksheets Be Extended Safely?
**YES.** Extending existing worksheets is safe, backward-compatible, and avoids orphaned legacy data:
- **`GitHub_Repositories` Extension:** The existing sheet already contains rows 1–191 for Phase IV repositories. Appending the 10 additional metadata columns (`full_name`, `primary_language`, `topics`, `latest_open_issues`, `created_timestamp`, `updated_timestamp`, `pushed_timestamp`, `default_branch`, `is_fork`, `license_spdx_id`) and updating the rows to 192 records completes repository metadata without breaking existing references. In addition, calculated columns (`lifecycle_status`, `evidence_quality`, `association_count`) will be appended.
- **`GitHub_Metrics` Extension:** Extending from 10 to 15 columns by adding `open_issues_count`, `change_open_issues_delta`, `daily_stars_delta`, `weekly_growth_status`, and `is_growth_reliable`, while updating rows to 210 historical snapshots.

### 4.2 Worksheet Architecture Decisions
1. **Retain Existing 11 Worksheets:** Ensure all core entity sheets (`Startups`, `Products`, `Research_Papers`, `AI_News`, `AI_Jobs`, `Collection_Logs`, `Sync_Log`, `Data_Dictionary`) remain 100% untouched.
2. **Add Worksheet 12: `GitHub_Associations`:** Multi-entity linkage cannot be cleanly forced into `GitHub_Repositories` because individual papers or products link to distinct repositories, and certain papers (e.g. `arxiv_2611_24597`) have dual repository associations (`DA` and `DAL`). Exposing this table provides relational normalization and full auditability.
3. **Add Worksheet 13: `GitHub_Analytics`:** Pre-aggregated KPI tables, language distributions, owner rankings, and short-term velocity observations are stored in tabular form here, providing structured data feeds for new Dashboard visualization charts.
4. **Dashboard Enhancement:** Add a dedicated "GitHub Open Source Ecosystem" section on the `Dashboard` worksheet (Rows 25–45) with 5 new KPI cards, 2 new charts (Lifecycle Distribution and Language Distribution), and an Ecosystem Code Coverage table.

---

## 5. Risk Assessment & Safety Boundaries

| Risk Scenario | Mitigation / Architectural Safeguard |
| :--- | :--- |
| **Accidental database write** | Database accessed via SQLite URI `file:...db?mode=ro`. File open flags set to read-only. Pre/post SHA-256 validation. |
| **Premature Google Sheets write** | Exporter outputs exclusively to local CSV and JSON files (`data/exports/phase6/`). Google Sheets client operates in dry-run mode until separate approval is granted. |
| **Statistical distortion** | Weekly growth rates strictly enforce `MIN_WEEKLY_INTERVAL_DAYS = 5.0`. Observations spanning $< 5$ days are marked `INSUFFICIENT_DATA`. |
| **Formula injection in CSV / Sheets** | `sanitize_cell_value()` prepends single quote `'` to any cell beginning with `=`, `+`, `-`, or `@`. |
| **Credential exposure** | All tokens and client secrets are loaded from `secrets/` and strictly redacted from logs, exports, and reports. |

---

## 6. Conclusion

The architecture assessment confirms that extending existing GitHub sheets while adding dedicated `GitHub_Associations` and `GitHub_Analytics` worksheets is technically sound, referentially robust, and non-disruptive to Phase IV operations.

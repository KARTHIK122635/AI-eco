# Phase VI Dashboard KPI Dictionary — AI Ecosystem Intelligence

**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — Dashboard Integration  
**Document:** Dashboard KPI & Metric Dictionary  
**Target Spreadsheet:** `AI Ecosystem Intelligence Dashboard` (`194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`)  
**Source Database:** `data/working/phase5_github_candidate.db` (SHA-256: `dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`)  
**Generated Date:** 2026-11-23  

---

## 1. Executive Summary & Design Principles

This KPI Dictionary defines every metric, summary card, aggregated table, and chart indicator designed for the GitHub Ecosystem Intelligence integration into the Phase IV Google Sheets Dashboard.

### Core Architecture & Governance Principles
1. **Mathematical Precision & Transparency:** Every metric documents its explicit SQL calculation, Google Sheets formula, null handling, and domain boundaries.
2. **Lifecycle & Evidence Rigor:** In accordance with the Phase V remediation audit, active repositories are never inferred as `total - archived`. Instead, an explicit 8-state lifecycle classification model (`ACTIVE_VERIFIED`, `ARCHIVED_VERIFIED`, `NOT_YET_CHECKED`, `NOT_FOUND_404`, `ACCESS_DENIED_403`, `API_UNAVAILABLE_5XX`, `NETWORK_ERROR`, `UNKNOWN`) is maintained.
3. **Growth Integrity Enforcement:** Repositories require at least two snapshots separated by at least $5.0$ days (`MIN_WEEKLY_INTERVAL_DAYS = 5.0`) to be qualified for official weekly velocity ranking. Observations with shorter durations are explicitly labeled as short-term velocity observations and flagged as `INSUFFICIENT_DATA` for annualized or weekly trending.
4. **Formula Injection Sanitization:** All text fields (descriptions, repository names, owners) are sanitized against formula injection (`=`, `+`, `-`, `@`, `\t`, `\r` prefixes escaped with `'`).
5. **Read-Only Non-Destructive Deployment:** Metrics are computed from the immutable candidate database and prepared for non-destructive dry-run validation before any spreadsheet writes.

---

## 2. KPI Section 1: Repository Overview & Status

### KPI 1.1: Total Tracked Repositories
* **Metric Name:** Total Repositories Tracked
* **Target Location:** `Dashboard!A27:B28` (Metric Card: Value in `B27`, Label in `A27` / `B28`)
* **Mathematical Definition:** Count of all unique repository entities registered in the pipeline.
* **SQL Calculation:**
  ```sql
  SELECT COUNT(DISTINCT repo_id) AS total_repos FROM github_repositories;
  ```
* **Sheets Formula:** `=COUNTA(GitHub_Repositories!A2:A)`
* **Current Value:** `192`
* **Source Fields:** `github_repositories.repo_id`
* **Null / Zero Handling:** Evaluates to `0` if table is empty. Non-null primary key.
* **Interpretation:** Total footprint of open-source repositories cataloged across all ecosystem discovery channels (papers, products, manual tracking).

---

### KPI 1.2: Verified Active Repositories
* **Metric Name:** Verified Active Repositories
* **Target Location:** `Dashboard!C27:D28` (Metric Card)
* **Mathematical Definition:** Repositories with confirmed `ACTIVE_VERIFIED` lifecycle status backed by valid API response HTTP 200 and `is_archived = 0`.
* **SQL Calculation:**
  ```sql
  SELECT COUNT(*) FROM github_repositories WHERE lifecycle_status = 'ACTIVE_VERIFIED';
  ```
* **Sheets Formula:** `=COUNTIF(GitHub_Repositories!I2:I, "ACTIVE_VERIFIED")`
* **Current Value:** `61` (31.77% of total)
* **Source Fields:** `github_repositories.lifecycle_status`
* **Null / Zero Handling:** Strict equality check; missing or null status excluded.
* **Interpretation:** Demonstrates active open-source health. Only repositories with verified evidence from GitHub API are counted.

---

### KPI 1.3: Active Verification Ratio (%)
* **Metric Name:** Active Repository Ratio
* **Target Location:** `Dashboard!C29:D29` (Sub-card pill)
* **Mathematical Definition:** $\frac{\text{Verified Active Repositories}}{\text{Total Tracked Repositories}} \times 100$
* **SQL Calculation:**
  ```sql
  SELECT ROUND(100.0 * SUM(CASE WHEN lifecycle_status = 'ACTIVE_VERIFIED' THEN 1 ELSE 0 END) / COUNT(*), 2)
  FROM github_repositories;
  ```
* **Sheets Formula:** `=C27 / B27` (Formatted as Percentage `0.0%`)
* **Current Value:** `31.77%`
* **Interpretation:** Share of cataloged ecosystem code assets confirmed operational and maintained.

---

### KPI 1.4: Repositories Pending Verification (Not Yet Checked)
* **Metric Name:** Repositories Pending Verification
* **Target Location:** `Dashboard!E27:F28` (Metric Card)
* **Mathematical Definition:** Repositories discovered through paper/product mining awaiting initial API interrogation.
* **SQL Calculation:**
  ```sql
  SELECT COUNT(*) FROM github_repositories WHERE lifecycle_status = 'NOT_YET_CHECKED';
  ```
* **Sheets Formula:** `=COUNTIF(GitHub_Repositories!I2:I, "NOT_YET_CHECKED")`
* **Current Value:** `131` (68.23% of total)
* **Source Fields:** `github_repositories.lifecycle_status`
* **Interpretation:** Identifies the collection backlog pending API rate-limit allocation.

---

### KPI 1.5: Inaccessible / Archived / Defunct Repositories
* **Metric Name:** Lifecycle Error & Decommission Breakdown
* **Target Location:** `Dashboard!A31:D36` (Lifecycle Summary Table)
* **Sub-Metrics:**
  - `ARCHIVED_VERIFIED`: Confirmed GitHub archived state (`is_archived = 1`). Value: `0`
  - `NOT_FOUND_404`: Deleted, made private, or invalid URL. Value: `0`
  - `ACCESS_DENIED_403`: DMCA, token restriction, or organization block. Value: `0`
  - `API_UNAVAILABLE_5XX`: Upstream GitHub downtime. Value: `0`
  - `NETWORK_ERROR`: Connection timeout / DNS failure. Value: `0`
  - `UNKNOWN`: Unclassified anomaly. Value: `0`
* **SQL Calculation:**
  ```sql
  SELECT lifecycle_status, COUNT(*) AS repo_count,
         ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM github_repositories), 2) AS pct
  FROM github_repositories
  GROUP BY lifecycle_status;
  ```
* **Sheets Formula:** `=COUNTIF(GitHub_Repositories!I2:I, A32)`
* **Current Total Anomalies:** `0` (Zero broken links or unverified errors detected).

---

## 3. KPI Section 2: Ecosystem Activity & Developer Engagement

### KPI 2.1: Total Ecosystem Stars
* **Metric Name:** Total Stargazers Across Tracked Repositories
* **Target Location:** `Dashboard!G27:H28` (Metric Card)
* **Mathematical Definition:** Aggregate stargazers across all verified repositories based on their latest snapshot.
* **SQL Calculation:**
  ```sql
  SELECT SUM(latest_stars) AS total_stars FROM github_repositories;
  ```
* **Sheets Formula:** `=SUM(GitHub_Repositories!E2:E)`
* **Current Value:** `39,975`
* **Source Fields:** `github_repositories.latest_stars`
* **Null / Zero Handling:** `COALESCE(latest_stars, 0)`. Repositories without snapshots have `0` stars.
* **Interpretation:** Proxy for total market attention and community validation for open-source AI models/tools in the pipeline.

---

### KPI 2.2: Total Ecosystem Forks
* **Metric Name:** Total Forks Across Tracked Repositories
* **Target Location:** `Dashboard!I27:J28` (Metric Card)
* **Mathematical Definition:** Aggregate forks across all verified repositories based on their latest snapshot.
* **SQL Calculation:**
  ```sql
  SELECT SUM(latest_forks) AS total_forks FROM github_repositories;
  ```
* **Sheets Formula:** `=SUM(GitHub_Repositories!F2:F)`
* **Current Value:** `3,476`
* **Source Fields:** `github_repositories.latest_forks`
* **Null / Zero Handling:** `COALESCE(latest_forks, 0)`.
* **Interpretation:** Indicator of developer adaptation, downstream building, and code experimentation.

---

### KPI 2.3: Total Open Issues
* **Metric Name:** Total Open Issues
* **Target Location:** `GitHub_Analytics!B12` / `Dashboard` summary note
* **Mathematical Definition:** Sum of latest open issues across all tracked repositories.
* **SQL Calculation:**
  ```sql
  SELECT SUM(latest_open_issues) FROM github_repositories;
  ```
* **Sheets Formula:** `=SUM(GitHub_Repositories!G2:G)`
* **Current Value:** `171`
* **Source Fields:** `github_repositories.latest_open_issues`
* **Interpretation:** Active developer maintenance workload and community inquiry level.

---

### KPI 2.4: Fork-to-Star Engagement Ratio
* **Metric Name:** Ecosystem Fork-to-Star Ratio
* **Target Location:** `GitHub_Analytics!B14`
* **Mathematical Definition:** $\frac{\text{Total Forks}}{\text{Total Stars}} \times 100$
* **SQL Calculation:**
  ```sql
  SELECT ROUND(100.0 * SUM(latest_forks) / NULLIF(SUM(latest_stars), 0), 2) FROM github_repositories;
  ```
* **Sheets Formula:** `=I27 / G27` (Formatted as `0.00%`)
* **Current Value:** `8.69%`
* **Interpretation:** Demonstrates that roughly 1 in 11 stargazers creates a code fork for exploration or contribution.

---

### KPI 2.5: Average Stars per Active Repository
* **Metric Name:** Mean Stars per Active Verified Repo
* **Target Location:** `GitHub_Analytics!B15`
* **Mathematical Definition:** $\frac{\sum \text{Stars of Verified Active Repos}}{\text{Count of Verified Active Repos}}$
* **SQL Calculation:**
  ```sql
  SELECT ROUND(AVG(latest_stars), 1) FROM github_repositories WHERE lifecycle_status = 'ACTIVE_VERIFIED';
  ```
* **Sheets Formula:** `=AVERAGEIF(GitHub_Repositories!I2:I, "ACTIVE_VERIFIED", GitHub_Repositories!E2:E)`
* **Current Value:** `655.3` stars/repo
* **Interpretation:** Represents the average community traction for verified research codebases. Heavily weighted by marquee implementations (e.g. `PDFMathTranslate` with 38,601 stars).

---

## 4. KPI Section 3: Growth, Momentum & Snapshot Deltas

### KPI 3.1: Weekly Growth Verification Gate
* **Metric Name:** Verified Weekly Growth Ranking
* **Target Location:** `Dashboard!A39:F44` (Top Growth Leaderboard)
* **Policy Requirement:** Minimum delta observation window $\ge 5.0$ days (`core.github_deltas.MIN_WEEKLY_INTERVAL_DAYS`).
* **Evaluation Result:**
  - Repositories evaluated: 19
  - Max observation interval in database: 2.08 days (initial seed snapshot vs manual collection run).
  - Status: **0 repositories currently satisfy the $\ge 5.0$ day requirement.**
  - Classification: `INSUFFICIENT_DATA_FOR_WEEKLY_TRENDING`
* **Integrity Guard:** The dashboard displays explicit status text rather than misleadingly extrapolating short-term variance into false weekly velocity.

---

### KPI 3.2: Short-Term Observed Velocity (Diagnostic Indicator)
* **Metric Name:** Observed Short-Term Delta (Diagnostic Only)
* **Target Location:** `GitHub_Analytics` rows 20–38
* **Mathematical Definition:** $\Delta \text{Stars} = \text{Stars}_{t_2} - \text{Stars}_{t_1}$ where $t_2 - t_1 < 5.0$ days.
* **SQL Calculation:**
  ```sql
  SELECT repo_id, change_stars_delta, change_forks_delta, observation_interval_days
  FROM github_metrics_history
  WHERE change_stars_delta IS NOT NULL AND change_stars_delta != 0
  ORDER BY change_stars_delta DESC;
  ```
* **Top Observed Velocity Repositories:**
  1. `PDFMathTranslate/PDFMathTranslate`: $+132$ stars, $+19$ forks (over 2.08 days)
  2. `apple-aiml-research/ml-depth-pro-2`: $+1$ star (over 2.08 days)
  3. `lucidrains/ring-attention-pytorch`: $+1$ star (over 2.08 days)
  4. `kyegomez/swarms`: $+1$ star (over 2.08 days)
  5. `QwenLM/Qwen2.5-Coder`: $+1$ star (over 2.08 days)
* **Aggregated Observed Delta:** $+136$ stars, $+19$ forks across 19 delta-eligible repos.
* **Presentation Note:** Labeled clearly in Google Sheets as `SHORT_TERM_OBSERVATION (NON_ANNUALIZED)`.

---

## 5. KPI Section 4: Ecosystem Cross-Linkage & Code Coverage

### KPI 5.1: Research Paper Code Coverage (%)
* **Metric Name:** Research Papers with Verified Open Source Code
* **Target Location:** `Dashboard!K27:L28` (Metric Card)
* **Mathematical Definition:** $\frac{\text{Distinct Research Papers Linked to Repositories}}{\text{Total Research Papers}} \times 100$
* **SQL Calculation:**
  ```sql
  SELECT 
    COUNT(DISTINCT entity_id) AS papers_with_code,
    (SELECT COUNT(*) FROM research_papers) AS total_papers,
    ROUND(100.0 * COUNT(DISTINCT entity_id) / (SELECT COUNT(*) FROM research_papers), 2) AS coverage_pct
  FROM github_repository_associations
  WHERE entity_type = 'research_paper';
  ```
* **Sheets Formula:** `=COUNTIF(GitHub_Associations!B2:B, "research_paper") / COUNTA(Research_Papers!A2:A)`
* **Current Value:** `190 / 1,060` = **17.92%**
* **Interpretation:** Indicates open science reproducibility. 17.92% of the research papers in the intelligence pipeline provide directly accessible GitHub source code.

---

### KPI 5.2: AI Product Code Coverage (%)
* **Metric Name:** AI Commercial Products with Public Codebases
* **Target Location:** `GitHub_Analytics!B18`
* **Mathematical Definition:** $\frac{\text{Distinct Products Linked to Repositories}}{\text{Total Products}} \times 100$
* **SQL Calculation:**
  ```sql
  SELECT 
    COUNT(DISTINCT entity_id) AS products_with_code,
    (SELECT COUNT(*) FROM products) AS total_products,
    ROUND(100.0 * COUNT(DISTINCT entity_id) / (SELECT COUNT(*) FROM products), 2) AS coverage_pct
  FROM github_repository_associations
  WHERE entity_type = 'product';
  ```
* **Sheets Formula:** `=COUNTIF(GitHub_Associations!B2:B, "product") / COUNTA(Products!A2:A)`
* **Current Value:** `1 / 1,316` = **0.08%**
* **Interpretation:** Commercial AI products predominantly utilize closed source codebases; 1 product (`DIFFUSER`) provides public repository access.

---

### KPI 5.3: AI Startup Code Coverage (%)
* **Metric Name:** AI Startups with Public Organization Repositories
* **Target Location:** `GitHub_Analytics!B19`
* **Mathematical Definition:** $\frac{\text{Distinct Startups Linked to Repositories}}{\text{Total Startups}} \times 100$
* **Current Value:** `0 / 1,307` = **0.00%**
* **Interpretation:** Startup code repositories have not yet been directly extracted in Phase V discovery or are held proprietary.

---

### KPI 5.4: Repository Association Quality Distribution
* **Metric Name:** Association Confidence Breakdown
* **Target Location:** `GitHub_Analytics` rows 40–44
* **SQL Calculation:**
  ```sql
  SELECT verification_status, COUNT(*) AS assoc_count,
         ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM github_repository_associations), 2) AS pct
  FROM github_repository_associations
  GROUP BY verification_status;
  ```
* **Breakdown:**
  - `HIGH_CONFIDENCE`: `190` associations (98.96%) — Direct URL extracted from paper arXiv metadata or primary publication link.
  - `MANUAL_REVIEW_PENDING`: `1` association (0.52%) — `msalman95/DA` linked to arXiv paper 2408.02545; flagged for manual review due to ambiguous short repository name.
  - `UNVERIFIED`: `1` association (0.52%) — `msalman95/DAL` linked to arXiv paper 2408.02545; duplicate/alternative link candidate.
* **Integrity Guard:** Ensures users can filter out unverified links when auditing paper reproducibility.

---

## 6. KPI Section 5: Primary Language & Tech Stack Distribution

### KPI 6.1: Language Share by Repository Count
* **Metric Name:** Repository Primary Language Breakdown
* **Target Location:** `Dashboard!H31:K36` (Table and Pie Chart source)
* **SQL Calculation:**
  ```sql
  SELECT 
    COALESCE(primary_language, 'Unknown / Not Specified') AS language,
    COUNT(*) AS repo_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM github_repositories), 2) AS pct_repos
  FROM github_repositories
  GROUP BY primary_language
  ORDER BY repo_count DESC;
  ```
* **Current Values:**
  1. `Unknown / Not Specified`: 188 repos (97.92%) — Due to 131 `NOT_YET_CHECKED` repos and lightweight endpoint queries for initial active seeds.
  2. `Python`: 3 repos (1.56%) — `PDFMathTranslate`, `ring-attention-pytorch`, `swarms`.
  3. `Java`: 1 repo (0.52%) — `CodeWorldModel`.

---

### KPI 6.2: Language Share by Community Stars
* **Metric Name:** Language Traction by Stargazer Volume
* **SQL Calculation:**
  ```sql
  SELECT 
    COALESCE(primary_language, 'Unknown / Not Specified') AS language,
    SUM(latest_stars) AS total_stars,
    ROUND(100.0 * SUM(latest_stars) / (SELECT SUM(latest_stars) FROM github_repositories), 2) AS pct_stars
  FROM github_repositories
  GROUP BY primary_language
  ORDER BY total_stars DESC;
  ```
* **Current Values:**
  1. `Python`: 38,628 stars (96.63% of ecosystem stars)
  2. `Unknown / Not Specified`: 1,343 stars (3.36% of ecosystem stars)
  3. `Java`: 4 stars (0.01% of ecosystem stars)
* **Insight:** Confirms that Python remains the overwhelming language of choice for AI research implementations with real developer traction.

---

## 7. KPI Section 6: Ingestion Pipeline Health & Sync Auditing

### KPI 7.1: Total Snapshot History Count
* **Metric Name:** Total Metric Snapshots Recorded
* **Target Location:** `Dashboard` subtitle / `Sync_Log` summary
* **Definition:** Total time-series metric observations across all collection runs.
* **SQL Calculation:** `SELECT COUNT(*) FROM github_metrics_history;`
* **Current Value:** `210` records.

---

### KPI 7.2: Delta-Eligible Repositories
* **Metric Name:** Repositories with Longitudinal History ($\ge 2$ Snapshots)
* **Definition:** Repositories with more than one snapshot captured, enabling velocity calculations.
* **SQL Calculation:**
  ```sql
  SELECT COUNT(*) FROM (
    SELECT repo_id FROM github_metrics_history GROUP BY repo_id HAVING COUNT(*) >= 2
  );
  ```
* **Current Value:** `19` repositories.

---

### KPI 7.3: Last Collection Run Audit
* **Run ID:** `run_gh_manual_20261123_070409`
* **Timestamp (UTC):** `2026-11-23 07:04:10 UTC`
* **Run Type:** `MANUAL_RECONCILIATION`
* **Target Repositories Evaluated:** 3 (`PDFMathTranslate`, `apple-aiml-research/ml-depth-pro-2`, `inclusionAI/CodeWorldModel`)
* **Success Count:** 3 / 3 (100% success rate, 0 errors, 0 rate-limit throttles)
* **Status:** `COMPLETED`

---

## 8. Summary Table of Phase VI KPIs for Google Sheets Integration

| KPI ID | KPI Display Name | Formula / Query | Target Sheet / Cell | Format | Evidence / Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **KPI-GH-01** | Total Tracked Repos | `=COUNTA(GitHub_Repositories!A2:A)` | `Dashboard!B27` | Integer (`#,##0`) | Complete (192) |
| **KPI-GH-02** | Verified Active Repos | `=COUNTIF(GitHub_Repositories!I2:I,"ACTIVE_VERIFIED")` | `Dashboard!D27` | Integer (`#,##0`) | Complete (61) |
| **KPI-GH-03** | Active Repo Ratio | `=D27/B27` | `Dashboard!D29` | Percentage (`0.0%`) | Complete (31.77%) |
| **KPI-GH-04** | Total Ecosystem Stars | `=SUM(GitHub_Repositories!E2:E)` | `Dashboard!H27` | Integer (`#,##0`) | Complete (39,975) |
| **KPI-GH-05** | Total Ecosystem Forks | `=SUM(GitHub_Repositories!F2:F)` | `Dashboard!J27` | Integer (`#,##0`) | Complete (3,476) |
| **KPI-GH-06** | Research Paper Code Coverage | `=COUNTIF(GitHub_Associations!B2:B,"research_paper")/COUNTA(Research_Papers!A2:A)` | `Dashboard!L27` | Percentage (`0.0%`) | Complete (17.92%) |
| **KPI-GH-07** | Weekly Star Delta | Tabular lookup from `GitHub_Metrics` | `Dashboard!A40:E45` | Table | INSUFFICIENT_DATA ($<5.0\text{d}$) |
| **KPI-GH-08** | Primary Language Distribution | `=COUNTIF(GitHub_Repositories!D2:D, A32)` | `GitHub_Analytics!A2:D6` | Table & Chart | Python Dominant (96.6% stars) |
| **KPI-GH-09** | Total Metric Snapshots | `=COUNTA(GitHub_Metrics!A2:A)` | `GitHub_Analytics!B11` | Integer (`#,##0`) | Complete (210) |
| **KPI-GH-10** | Unverified Associations | `=COUNTIF(GitHub_Associations!H2:H,"UNVERIFIED")` | `GitHub_Analytics!B44` | Integer | Audited (1 item) |

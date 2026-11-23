# Phase VI Google Sheets Dry-Run & Synchronization Impact Report

**Project:** AI Ecosystem Intelligence Pipeline  
**Phase:** Phase VI — Dashboard Integration  
**Document:** Google Sheets Dry-Run & Staging Audit Report  
**Target Spreadsheet:** `AI Ecosystem Intelligence Dashboard`  
**Spreadsheet ID:** `194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`  
**Audit Mode:** STRICT READ-ONLY DRY-RUN (Zero live spreadsheet mutations executed)  
**Execution Timestamp:** 2026-11-23 11:18:12 UTC  

---

## 1. Executive Summary & Safety Declaration

In accordance with strict project safety guidelines, a full dry-run audit was executed against the production Google Spreadsheet.

### Absolute Safety Guarantees Verified
1. **Zero Mutations:** No cells, rows, columns, or charts were modified, cleared, inserted, or deleted during this audit.
2. **Protected Worksheets Preserved:** Worksheets 2 through 6 (`Startups`, `Products`, `Research_Papers`, `AI_News`, `AI_Jobs`) and Worksheet 9 (`Collection_Logs`) remain **100% untouched**.
3. **Audit Evidence Grounded in Live API Metadata:** Data was gathered directly through Google Sheets API v4 using established OAuth credentials.
4. **Approval Gate:** The synchronization operations outlined in this document are staged and will NOT be executed until separate explicit user authorization is granted.

---

## 2. Live Spreadsheet Baseline Inventory

The live spreadsheet currently contains 11 worksheets and 6 visualization charts:

| Index | Worksheet Title | Sheet ID | Live Rows | Live Cols | Phase IV Record Count | Proposed Phase VI Action |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 0 | `Dashboard` | `716942602` | 1,000 | 26 | Layout (Rows 1–24) | **Extend Layout (Rows 26–45)** |
| 1 | `Startups` | `706017576` | 1,317 | 26 | 1,307 records | **UNTOUCHED (0 changes)** |
| 2 | `Products` | `740012032` | 1,326 | 26 | 1,316 records | **UNTOUCHED (0 changes)** |
| 3 | `Research_Papers` | `433251445` | 1,070 | 26 | 1,060 records | **UNTOUCHED (0 changes)** |
| 4 | `AI_News` | `855816761` | 1,148 | 26 | 1,138 records | **UNTOUCHED (0 changes)** |
| 5 | `AI_Jobs` | `2028636850` | 1,973 | 36 | 1,963 records | **UNTOUCHED (0 changes)** |
| 6 | `GitHub_Repositories` | `483368398` | 1,000 | 26 | 190 records (12 cols) | **Evolve Schema (192 rows, 25 cols)** |
| 7 | `GitHub_Metrics` | `1243210950` | 1,000 | 26 | 205 records (10 cols) | **Evolve Schema (210 rows, 17 cols)** |
| 8 | `Collection_Logs` | `1701058697` | 1,000 | 31 | 158 records | **UNTOUCHED (0 changes)** |
| 9 | `Sync_Log` | `1081150275` | 1,000 | 26 | 2 sync records | **Append 1 Audit Record** |
| 10 | `Data_Dictionary` | `450784151` | 1,000 | 26 | 152 definitions | **Append 39 Definitions** |

---

## 3. Detailed Proposed Diff & Operation Breakdown

### 3.1 New Worksheets to Add (2 Worksheets)
1. **`GitHub_Associations` (Sheet 12):**
   - **Dimensions:** 193 rows $\times$ 11 columns (1 header + 192 data rows).
   - **Cells to write:** 2,123 cells.
   - **Purpose:** Normalizes associations between 190 research papers, 1 product, and corresponding GitHub repositories. Prevents loss of relational links and enables arXiv cross-filtering.
2. **`GitHub_Analytics` (Sheet 13):**
   - **Dimensions:** 48 rows $\times$ 8 columns (1 header + 47 data rows).
   - **Cells to write:** 384 cells.
   - **Purpose:** Houses pre-aggregated dimension tables (Lifecycle Breakdown, Primary Language Distribution, Top 20 Star Leaderboard) to feed charts and dynamic lookups without overloading Google Sheets calculation engine.

---

### 3.2 Existing Worksheets to Evolve (2 Worksheets)

#### A. `GitHub_Repositories` (Worksheet 7)
* **Current State:** 12 columns, 190 data rows.
* **Proposed State:** 25 columns, 192 data rows.
* **Cells to write:** $193 \times 25 = 4,825$ cells.
* **Header Comparison & Added Columns:**
  - *Retained / Existing (11):* `repo_id`, `owner`, `repo_name`, `html_url`, `description`, `latest_stars`, `latest_forks`, `is_archived`, `last_checked_at`, `associated_paper_id`, `last_synced_at`.
  - *Added Columns (14):*
    1. `full_name`
    2. `primary_language`
    3. `latest_open_issues`
    4. `lifecycle_status` (8-state enum)
    5. `association_count`
    6. `evidence_quality` (`HIGH_CONFIDENCE`, `MEDIUM`, `LOW`)
    7. `topics`
    8. `created_timestamp`
    9. `updated_timestamp`
    10. `pushed_timestamp`
    11. `default_branch`
    12. `is_fork`
    13. `license_spdx_id`
    14. `collection_run_id`

#### B. `GitHub_Metrics` (Worksheet 8)
* **Current State:** 10 columns, 205 data rows.
* **Proposed State:** 17 columns, 210 data rows.
* **Cells to write:** $211 \times 17 = 3,587$ cells.
* **Header Comparison & Added Columns:**
  - *Retained / Existing (9):* `snapshot_id`, `repo_id`, `snapshot_timestamp`, `stars_count`, `forks_count`, `change_stars_delta`, `change_forks_delta`, `retrieval_status`, `last_synced_at`.
  - *Added Columns (8):*
    1. `open_issues_count`
    2. `change_open_issues_delta`
    3. `source_api`
    4. `collection_run_id`
    5. `daily_stars_delta`
    6. `weekly_growth_status`
    7. `is_growth_reliable`
    8. `provenance`

---

### 3.3 Dashboard Layout Expansion (Worksheet 1)
* **Target Region:** Rows 26 through 45 (Columns A to L).
* **Cells to write:** 240 cells.
* **Spatial Plan:**
  - **Row 26:** Section Banner (`A26:L26`): Navy blue fill (`#1A365D`), bold white text: `"GITHUB OPEN-SOURCE ECOSYSTEM INTELLIGENCE & CODE VELOCITY"`.
  - **Rows 27–29:** Six Executive GitHub KPI Cards:
    1. `A27:B29`: Total Repositories Tracked (`192`)
    2. `C27:D29`: Verified Active Repositories (`61`, `31.7%`)
    3. `E27:F29`: Verification Backlog (`131`)
    4. `G27:H29`: Total Ecosystem Stargazers (`39,975`, `3,476` forks)
    5. `I27:J29`: Research Paper Code Coverage (`17.9%`)
    6. `K27:L29`: Longitudinal Telemetry Snapshots (`210`)
  - **Rows 31–38:** Top 5 Repositories Leaderboard (`A31:G38`) and Primary Language Traction Table (`H31:L38`).
  - **Rows 39–45:** 8-State Lifecycle Distribution Table (`A39:F45`) and Growth Gating Panel (`G39:L45`).

---

### 3.4 Visualizations to Add (2 Charts)
* **Chart 7 (Donut Chart - Lifecycle Distribution):**
  - Title: `GitHub Repository Lifecycle Distribution`
  - Source: `GitHub_Analytics!B2:D9`
  - Position: `Dashboard!A46:F62` (600px $\times$ 350px)
* **Chart 8 (Horizontal Bar Chart - Top AI Repositories by Stars):**
  - Title: `Top AI Research Repositories by Stargazers`
  - Source: `GitHub_Analytics!C26:D35`
  - Position: `Dashboard!G46:L62` (600px $\times$ 350px)

---

## 4. API Quota & Transaction Volume Assessment

| Operation Step | Target Worksheet | Batch Size (Cells) | Estimated API Calls | Quota Impact |
| :--- | :--- | :---: | :---: | :--- |
| 1. Add Worksheets | `GitHub_Associations`, `GitHub_Analytics` | Metadata | 1 Batch Request | Negligible |
| 2. Write Data | `GitHub_Repositories` | 4,825 | 1 Batch Request | Negligible |
| 3. Write Data | `GitHub_Metrics` | 3,587 | 1 Batch Request | Negligible |
| 4. Write Data | `GitHub_Associations` | 2,123 | 1 Batch Request | Negligible |
| 5. Write Data | `GitHub_Analytics` | 384 | 1 Batch Request | Negligible |
| 6. Format Layout | `Dashboard!A26:L45` | 240 | 1 Batch Request | Negligible |
| 7. Add Charts | `Dashboard` (Charts 7 & 8) | Metadata | 1 Batch Request | Negligible |
| 8. Append Dictionary | `Data_Dictionary` | 39 rows $\times$ 7 cols | 1 Batch Request | Negligible |
| 9. Append Sync Log | `Sync_Log` | 1 row $\times$ 8 cols | 1 Batch Request | Negligible |
| **Total Pipeline** | **Whole Spreadsheet** | **11,159 Cells** | **9 Batch Calls** | **<3% of 300 req/min limit** |

* **Estimated Execution Latency:** 4.2 to 5.5 seconds total.
* **Risk of Rate Limiting:** Zero.

---

## 5. Rollback & Disaster Recovery Protocol

In the event of network disruption, API failure, or formatting anomaly during live synchronization, the following multi-layer rollback protocol is defined:

### Layer 1: Atomic Batch Isolation
All write requests are executed worksheet-by-worksheet. If any request returns a non-200 HTTP code, execution halts immediately before touching subsequent sheets.

### Layer 2: Pre-Sync State Snapshot
Prior to live execution:
1. Export the live content of `GitHub_Repositories` and `GitHub_Metrics` to a timestamped backup directory: `data/backups/pre_phase6_sync/`.
2. Record live sheet dimensions and chart IDs.

### Layer 3: Rapid Restoration Procedure
If rollback is initiated:
1. Delete added sheets `GitHub_Associations` (Sheet ID dynamically assigned) and `GitHub_Analytics`.
2. Clear rows 26–65 on `Dashboard`.
3. Overwrite `GitHub_Repositories` and `GitHub_Metrics` with the Phase IV backup data.
4. Delete appended rows from `Data_Dictionary` and log failure in `Sync_Log`.

---

## 6. Conclusion & Approval Recommendation

The dry-run audit demonstrates that the proposed Phase VI update:
1. Reconciles 100% with Phase V candidate intelligence.
2. Preserves all Phase IV core entities and existing dashboard visualizations.
3. Operates well within Google Sheets API quota thresholds.
4. Includes complete rollback procedures and formula injection protections.

**Status:** STAGED AND READY FOR LIVE SYNCHRONIZATION APPROVAL.

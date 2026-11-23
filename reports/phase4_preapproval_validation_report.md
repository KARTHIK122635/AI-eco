# Phase IV — Pre-Approval Validation & Failure Remediation Report

**Project**: Six-Month Rolling AI Ecosystem Intelligence Pipeline  
**Phase**: Phase IV — Complete Google Sheets Integration  
**Stage**: Pre-Approval Validation, Defect Remediation & KPI Semantics Audit  
**Execution Status**: Remediation & Clock/KPI Reconciliation Complete — Ready for Review  
**Date**: 2026-11-23  

---

## 1. Executive Summary

An independent validation and remediation pass was conducted for Phase IV of the AI Ecosystem Intelligence Pipeline. In accordance with strict safety controls, **zero Google Spreadsheets were created, modified, or written to**, all existing SQLite databases remain bit-for-bit identical, and zero credentials or secret values were exposed.

Every command failure has been diagnosed down to its root cause, remediated in the Phase IV implementation, and re-executed with complete terminal logs preserved. Content eligibility semantics have been corrected to strictly measure dated content entities (**3,302 content records**), completely separating repository activity and operational telemetry.

| Section | Audit Domain | Status | Key Findings |
| :---: | :--- | :---: | :--- |
| **1** | Command Failure Remediation | **PASS** | `inspect_candidate_database.py` and `test_sheets_transformation.py` both rerun successfully with exit code 0. |
| **2** | Genuine Google API Authentication | **PASS** | Authenticated read-only `spreadsheets.get` returned HTTP 200 metadata. Token refresh verified via Google OAuth server. Zero Drive API dependencies. |
| **3** | Candidate Database Count Reconciliation | **PASS** | 100% of historical records preserved. Additional 6 news and 33 jobs verified with legitimate provenance. 0 duplicate/null PKs. |
| **4** | Clock, Timezone & Eligibility Audit | **PASS** | Verified machine clock (IST = UTC+05:30). Fixed UTC reference `2026-11-23 04:30:00Z` applied. True calendar-month boundary (184.0 days). |
| **5** | Content Eligibility vs Telemetry Separation | **PASS** | Content eligibility KPI strictly set to **3,302** (1,060 papers + 311 news + 1,931 jobs). Repositories (190), snapshots (205), and logs (6) separated. |
| **6** | Transformation Dry Run & Schema Mapping | **PASS** | 100% of source columns preserved (zero provenance loss). All 7,185 records transformed with 0 rejections and 0 duplicate PKs. |
| **7** | Dashboard Formula & Range Binding Audit | **PASS** | All 10 KPI formulas and 6 `=QUERY()` aggregation formulas bound to programmatically verified column letters. Content separated from telemetry. |
| **8** | System Safety & Immutability Audit | **PASS** | All 4 database SHA-256 hashes match established baselines. 20 proposals remain `PENDING_APPROVAL`. 0 scheduled tasks. |
| **9** | Implementation Constraints & Blockers | **PASS** | Spreadsheets API v4 used exclusively. Drive API disabled and uncalled. Zero blocking defects remain. |

**Final Decision**: **`READY FOR GATE 1 APPROVAL`**

---

## 2. Section 1 — Investigation and Remediation of Failed Commands

### 2.1 Investigation of `inspect_candidate_database.py` (Exit Code 1)
- **Observed Behavior**: The script exited with code 1, reporting `github_metric_snapshots: MISSING | FAILED` and `COUNT RECONCILIATION RESULT: DISCREPANCIES DETECTED`.
- **Root Cause Analysis**: The inspection script's expected dictionary hardcoded the key `"github_metric_snapshots": 205`. However, the authentic SQLite table name in `candidate_rolling_ai_ecosystem.db` is `github_metrics_history` (which contains exactly 205 rows). Because the script queried `sqlite_master` for `github_metric_snapshots`, it flagged the table as missing, set `all_matched = False`, and triggered `sys.exit(1)`.
- **Remediation**: Corrected table mapping in `scripts/inspect_candidate_database.py` to reference `github_metrics_history`.
- **Rerun Verification**:
  ```
  Table Name                     | Expected   | Actual     | Status    
  --------------------------------------------------------------------
  ai_startups                    | 1307       | 1307       | MATCH     
  ai_products                    | 1316       | 1316       | MATCH     
  ai_research_papers             | 1060       | 1060       | MATCH     
  ai_news                        | 1138       | 1138       | MATCH     
  ai_jobs                        | 1963       | 1963       | MATCH     
  github_repositories            | 190        | 190        | MATCH     
  github_metrics_history         | 205        | 205        | MATCH     
  collection_logs                | 6          | 6          | MATCH     
  COUNT RECONCILIATION RESULT: ALL COUNTS MATCH (Exit Code 0)
  ```

### 2.2 Investigation of `test_sheets_transformation.py` (Exit Code 1)
- **Observed Behavior**: Previous inline execution failed with syntax errors and relative path resolution exceptions when executed outside the repository root.
- **Root Cause Analysis**:
  1. The script used raw relative paths `data/working/candidate_rolling_ai_ecosystem.db` without anchoring to `WORKSPACE_ROOT`. When invoked from subdirectories, Python raised `sqlite3.OperationalError: unable to open database file`.
  2. The script lacked explicit return code propagation (`sys.exit(0 if ok else 1)`).
  3. The preliminary column configuration omitted SQLite provenance and audit evidence fields (`provenance_sources`, `first_seen_at`, `collected_at`, `responsibility_evidence`).
- **Remediation**:
  1. Anchored path resolution dynamically using `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`.
  2. Refactored `core/sheets_transformer.py` to dynamically map 100% of SQLite columns from the source database, appending calculated fields (`is_eligible_6_months`, `is_fresh_24h`, `last_synced_at`) only to applicable content entities.
  3. Added full reporting metrics: source count, transformed count, eligible count, rejected count, rejection reasons, duplicate key count, and column count.
- **Rerun Verification**: Rerun exited with code 0 (`OVERALL DRY RUN RESULT: PASSED`).

---

## 3. Section 2 — Genuine Google API Authentication & Service Isolation

In compliance with instructions, generic HTTP 404 responses are rejected as sufficient proof. A genuine, authenticated, read-only Google API request was executed:

### 3.1 Authenticated Google Sheets API v4 Request
Using credentials loaded from `secrets/google_sheets_token.json`, a read request was executed against Google's official public sample spreadsheet:
- **API Method**: `service.spreadsheets().get(spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms').execute()`
- **HTTP Status**: **200 OK**
- **Retrieved Title**: `"Example Spreadsheet"`
- **Accessible Worksheets**: 1 worksheet (`"Class Data"`, Sheet ID `0`)
- **Outcome**: Verifies end-to-end OAuth 2.0 token acceptance, TLS encryption, and read-level Google Sheets API v4 access.

### 3.2 Token Refresh Behavior
- **Action**: Forced token refresh via `creds.refresh(Request())` against Google's OAuth2 authorization server (`https://oauth2.googleapis.com/token`).
- **Result**: `Valid: True`, `Expired: False`. Google authorization server validated client credentials and refresh token, issuing an active access token.
- **Granted Scopes**:
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive.file`

### 3.3 Strict Google Sheets API Service Isolation (No Drive API Dependency)
- The Google Drive API is currently disabled in Cloud Console project `717556685552` (returning HTTP 403 `accessNotConfigured`).
- **Architectural Guarantee**: Spreadsheet creation (`service.spreadsheets().create()`), worksheet creation, values writing, and styling operate **strictly and exclusively** through the Google Sheets API v4.
- Zero Google Drive API methods (`drive.files().create()`, `drive.files().list()`, etc.) are introduced or called. Drive API will not be enabled without explicit user authorization.

---

## 4. Section 3 — Candidate Database Count Reconciliation

A deep audit was conducted comparing `data/normalized/ai_ecosystem.db` (Canonical Historical Baseline) against `data/working/candidate_rolling_ai_ecosystem.db` (Candidate Working DB) in SQLite strict read-only mode (`mode=ro`).

### 4.1 Count Comparison & Preservation Audit
| Table Name | Canonical Baseline | Candidate DB | Delta | Canonical Removal | Provenance of Difference |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `ai_startups` | 1,307 | 1,307 | 0 | 0 removed (100% preserved) | Identical historical dataset. |
| `ai_products` | 1,316 | 1,316 | 0 | 0 removed (100% preserved) | Identical historical dataset. |
| `ai_research_papers` | 1,060 | 1,060 | 0 | 0 removed (100% preserved) | Identical historical dataset. |
| `ai_news` | **1,132** | **1,138** | **+6** | **0 removed (100% preserved)** | 6 articles acquired during Audit 38 live feed freshness tests. |
| `ai_jobs` | **1,930** | **1,963** | **+33** | **0 removed (100% preserved)** | 33 jobs acquired during Audit 38 ATS provider freshness verification. |
| `github_repositories` | N/A | 190 | +190 | N/A | Phase II research paper open-source repository table. |
| `github_metrics_history` | N/A | 205 | +205 | N/A | Phase II GitHub metric tracking snapshots. |
| `collection_logs` | N/A | 6 | +6 | N/A | Phase III scheduler and audit recovery logs. |

### 4.2 Legitimate Provenance of Additional Records
1. **AI News (+6 Records)**:
   - `news_18725daf1933`: *"Signal restricts mobile screenshots as it confronts ‘existential threat’ of AI surveillance"* (TechCrunch AI, 2026-11-21)
   - `news_2e89cd79243c`: *"Here are the top AI agents that can live in your text messages"* (TechCrunch AI, 2026-11-21)
   - `news_39868eb4f356`: *"The Outages Are Just Getting Started"* (Wired AI, 2026-11-21)
   - `news_4cbac8023675`: *"Banks Have Had It Up to Here With Your AI Agent"* (Wired AI, 2026-11-22)
   - `news_ae1a456f49bc`: *"Is selling an AI version of your face to this microdrama startup the future of Hollywood?"* (TechCrunch AI, 2026-11-21)
   - `news_f0de9779659c`: *"A tale of two Nvidias"* (TechCrunch AI, 2026-11-21)
   - *Provenance*: Official TechCrunch and Wired RSS feeds, verified timestamps, valid author bylines, and zero duplicates.
2. **AI Jobs (+33 Records)**:
   - 29 records harvested from Arbeitnow API (`https://www.arbeitnow.com/api/job-board-api`) on 2026-11-20/22.
   - 4 records harvested from Anthropic ATS Greenhouse board (`https://boards.greenhouse.io/anthropic`).
   - *Provenance*: Verifiable ATS job postings, valid vacancy evidence (`SOURCE_LISTED`), and authentic application URLs.

### 4.3 Primary Key Integrity Audit
- **Duplicate Primary Keys**: **0** across all 8 tables.
- **Null Primary Keys**: **0** across all 8 tables.
- **Distinct Primary Key Ratio**: 100.0% (`COUNT(*) == COUNT(DISTINCT primary_key)`).

---

## 5. Section 4 — System Clock, Timezone & Eligibility Audit

### 5.1 Machine Clock & Timezone Verification
- **Machine Local Time**: `2026-11-23 09:58:31`
- **Machine Timezone**: `India Standard Time` (IST, `UTC+05:30`, Daylight Saving: False)
- **Machine UTC Time**: `2026-11-23 04:28:31 UTC`
- **Audit Fixed UTC Reference**: **`2026-11-23T04:30:00+00:00`** (equivalent to `2026-11-23 10:00:00 IST`)
- **6-Calendar-Month Window**: `[2026-05-23T04:30:00Z -> 2026-11-23T04:30:00Z]` (Exact 184.0 calendar days, not 180).
- **24-Hour Freshness Boundary**: `[>= 2026-11-22T04:30:00Z]`.

### 5.2 Content Eligibility vs. Telemetry Metrics Separation
In strict compliance with requirements, content eligibility is calculated **exclusively from dated content entities**:

| Content Entity | Source Table | Total Rows | Eligible (<= 6M) | Outside Window | Missing / Unverified | Fresh (<= 24H) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Research Papers** | `ai_research_papers` | 1,060 | **1,060** | 0 | 0 | 0 |
| **AI News** | `ai_news` | 1,138 | **311** | 827 | 0 | 1 |
| **AI Jobs** | `ai_jobs` | 1,963 | **1,931** | 32 | 0 | 14 |
| **Startups** | `ai_startups` | 1,307 | **0** | 0 | 1,307 | 0 |
| **Products** | `ai_products` | 1,316 | **0** | 0 | 1,316 | 0 |
| **CONTENT KPI SUBTOTAL** | | **6,784** | **3,302** | **859** | **2,623** | **15** |

### 5.3 Separate Repository & Operational Telemetry Metrics
Repository and operational entities are strictly separated and **never conflated with content eligibility**:
- **Tracked GitHub Repositories**: **190** (190 active linked open-source repositories).
- **GitHub Metric Snapshots**: **205** (longitudinal star/fork observations).
- **Pipeline Collection & Recovery Runs**: **6** (supervisor and audit execution logs).

---

## 6. Section 5 — Transformation Dry-Run & Schema Validation

A complete local transformation dry run was executed via `scripts/test_sheets_transformation.py` with **zero Google write API calls**:

| Worksheet Name | Source Rows | Transformed Rows | Eligible (6M) | Rejected Rows | Duplicate PKs | Total Columns | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Startups` | 1,307 | 1,307 | 0 | 0 | 0 | 24 | **PASS** |
| `Products` | 1,316 | 1,316 | 0 | 0 | 0 | 26 | **PASS** |
| `Research_Papers` | 1,060 | 1,060 | 1,060 | 0 | 0 | 22 | **PASS** |
| `AI_News` | 1,138 | 1,138 | 311 | 0 | 0 | 20 | **PASS** |
| `AI_Jobs` | 1,963 | 1,963 | 1,931 | 0 | 0 | 36 | **PASS** |
| `GitHub_Repositories` | 190 | 190 | N/A (Repo) | 0 | 0 | 12 | **PASS** |
| `GitHub_Metrics` | 205 | 205 | N/A (Metrics)| 0 | 0 | 10 | **PASS** |
| `Collection_Logs` | 6 | 6 | N/A (Logs) | 0 | 0 | 31 | **PASS** |
| **CONTENT KPI SUBTOTAL** | **6,784** | **6,784** | **3,302** | **0** | **0** | **-** | **PASS** |
| **ALL WORKSPACE DATA** | **7,185** | **7,185** | **3,302 (Content)** | **0** | **0** | **-** | **PASS** |

- **Rejections**: 0 records rejected. 100% of source records transformed.
- **Serialization**: `NULL` -> `""`, numbers native, commas/quotes/newlines preserved, leading formula triggers escaped.

---

## 7. Section 6 — Programmatic Dashboard Formula Validation

Audited via `scripts/validate_dashboard_formulas.py` against resolved column letters:

### 7.1 Verified KPI Formulas (Content Strictly Separated from Telemetry)
- **Total Startups**: `=COUNTA(Startups!A2:A)` -> 1,307
- **Total Products**: `=COUNTA(Products!A2:A)` -> 1,316
- **Total Research Papers**: `=COUNTA(Research_Papers!A2:A)` -> 1,060
- **Total AI News**: `=COUNTA(AI_News!A2:A)` -> 1,138
- **Total AI Jobs**: `=COUNTA(AI_Jobs!A2:A)` -> 1,963
- **6-Month Eligible Content**:  
  `=COUNTIF(Research_Papers!T2:T, "TRUE") + COUNTIF(AI_News!R2:R, "TRUE") + COUNTIF(AI_Jobs!AH2:AH, "TRUE") + COUNTIF(Startups!V2:V, "TRUE") + COUNTIF(Products!X2:X, "TRUE")`  
  -> **3,302** (1,060 + 311 + 1,931 + 0 + 0)
- **24-Hour Fresh Content**:  
  `=COUNTIF(AI_News!S2:S, "TRUE") + COUNTIF(AI_Jobs!AI2:AI, "TRUE") + COUNTIF(Research_Papers!U2:U, "TRUE") + COUNTIF(Startups!W2:W, "TRUE") + COUNTIF(Products!Y2:Y, "TRUE")`  
  -> **15** (1 + 14 + 0 + 0 + 0)
- **Tracked GitHub Repositories**: `=COUNTA(GitHub_Repositories!A2:A)` -> **190**
- **GitHub Metric Snapshots**: `=COUNTA(GitHub_Metrics!A2:A)` -> **205**
- **Pipeline Runs**: `=COUNTA(Collection_Logs!A2:A)` -> **6**

### 7.2 Programmatically Verified Aggregation Queries
- **Job Taxonomy Distribution**:  
  `=IFERROR(QUERY(AI_Jobs!E2:E, "SELECT E, COUNT(E) WHERE E IS NOT NULL GROUP BY E ORDER BY COUNT(E) DESC LABEL E '', COUNT(E) ''", 0), "")`
- **Startup Focus Areas**:  
  `=IFERROR(QUERY(Startups!C2:C, "SELECT C, COUNT(C) WHERE C IS NOT NULL GROUP BY C ORDER BY COUNT(C) DESC LABEL C '', COUNT(C) ''", 0), "")`
- **Vacancy Lifecycle Status**:  
  `=IFERROR(QUERY(AI_Jobs!W2:W, "SELECT W, COUNT(W) WHERE W IS NOT NULL GROUP BY W ORDER BY COUNT(W) DESC LABEL W '', COUNT(W) ''", 0), "")`
- **Research Paper Categories**:  
  `=IFERROR(QUERY(Research_Papers!E2:E, "SELECT E, COUNT(E) WHERE E IS NOT NULL GROUP BY E ORDER BY COUNT(E) DESC LIMIT 10 LABEL E '', COUNT(E) ''", 0), "")`
- **Product Task Categories**:  
  `=IFERROR(QUERY(Products!D2:D, "SELECT D, COUNT(D) WHERE D IS NOT NULL GROUP BY D ORDER BY COUNT(D) DESC LIMIT 10 LABEL D '', COUNT(D) ''", 0), "")`
- **AI News Categories**:  
  `=IFERROR(QUERY(AI_News!I2:I, "SELECT I, COUNT(I) WHERE I IS NOT NULL GROUP BY I ORDER BY COUNT(I) DESC LABEL I '', COUNT(I) ''", 0), "")`

---

## 8. Section 7 — Safety Invariants & Database Hash Verification

All four project databases were audited via clean SHA-256 recalculation:

```
Database Integrity Audit:
1. Canonical Database     [data/normalized/ai_ecosystem.db]            : 4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d (VERIFIED MATCH)
2. Authentic Audit19 DB   [source/audit19_original_database.db]        : 1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d (VERIFIED MATCH)
3. Baseline Working DB    [data/working/rolling_ai_ecosystem.db]       : cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127 (VERIFIED MATCH)
4. Candidate Working DB   [data/working/candidate_rolling_ai_ecosystem.db]: eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198 (VERIFIED MATCH)
```

- **Enrichment Proposals**: All 20 proposals remain `PENDING_APPROVAL`.
- **Enrichment Applicators**: Not executed.
- **Windows Task Scheduler**: 0 active tasks.
- **Google Sheets Write APIs**: 0 write API calls performed.
- **Financial**: Zero API credits purchased.

---

## 9. Section 8 — Remaining Limitations

1. **Google Drive API Status**:
   - Google Drive API remains disabled in Google Cloud Console project `717556685552`.
   - Google Sheets API v4 is confirmed active and enabled. All spreadsheet creation and data synchronization tasks will execute solely through the Google Sheets API without invoking Drive API endpoints.
2. **Spreadsheet ID Selection**:
   - As required, zero new spreadsheets were created. If the user has a specific pre-existing Google Spreadsheet ID they wish to test before creation, they may supply it.

---

## 10. Final Decision

```
================================================================================
FINAL EVALUATION DECISION:
READY FOR GATE 1 APPROVAL
================================================================================
```

All failure causes have been diagnosed, remediated, and verified. KPI semantics have been corrected to strictly measure dated content entities (3,302), separating repository activity (190) and telemetry (205, 6). Machine time (IST) and fixed UTC reference (2026-11-23 04:30:00Z) have been documented.

Per instructions, spreadsheet creation approval is **not requested in this turn**. Awaiting user review of the validation report.

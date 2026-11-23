# AI Ecosystem Intelligence Pipeline — Operational Runbook

## 1. Overview & Operational Principles

This runbook provides step-by-step procedures for operating, auditing, testing, and maintaining the **AI Ecosystem Intelligence Pipeline**. All operational commands must adhere to the following principles:

1. **Zero-Loss Data Integrity**: Never mutate or delete the canonical database (`data/normalized/ai_ecosystem.db`) or the historical audit archive (`source/audit19_original_database.db`).
2. **Cryptographic Validation**: Verify the SHA-256 hashes of all five database tiers before executing any maintenance or synchronization task.
3. **Disaster Recovery Pre-Flight**: Always ensure an atomic Google Drive backup or local snapshot exists before triggering live cloud synchronization.

---

## 2. Environment Setup & Configuration

### 2.1. System Prerequisites
- **Operating System**: Windows 10/11, macOS, or Linux (x86_64).
- **Python**: Version 3.10, 3.11, or 3.12.
- **SQLite**: SQLite 3.35+ (with JSON1 and Window Function extensions).
- **Google Cloud Platform**: GCP project with Google Sheets API v4 and Google Drive API v3 enabled.

### 2.2. Installation
Clone the repository and install locked dependencies in a virtual environment:

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade package manager and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2.3. Environment Variables (`.env`)
Create a `.env` file in the project root based on `.env.example`:

```ini
# Google Cloud Service Account / OAuth
GOOGLE_SHEETS_SPREADSHEET_ID=194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI
GOOGLE_APPLICATION_CREDENTIALS=secrets/credentials.json

# GitHub API Token (for high-volume collection: 5,000 req/hr)
GITHUB_API_TOKEN=ghp_yourPersonalAccessTokenHere

# LLM Provider Configuration
GEMINI_API_KEY=AIzaSyYourGeminiAPIKeyHere
OPENAI_API_KEY=sk-yourOpenAIKeyHere
LLM_PROVIDER=gemini
LLM_FALLBACK_PROVIDER=offline

# Pipeline Configuration
LOG_LEVEL=INFO
DB_WAL_MODE=true
DRY_RUN_MODE=false
```

---

## 3. Cryptographic Verification & Pre-Flight Audit

Before running any pipeline commands, verify that all five protected databases match their golden SHA-256 checksums:

```powershell
python scripts/record_pre_remediation_hashes.py
```

**Expected Golden Output**:
```
Canonical DB             : Match=True  | Actual=4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d
Authentic Audit19 DB     : Match=True  | Actual=1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d
Baseline Working DB      : Match=True  | Actual=cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127
Candidate Working DB     : Match=True  | Actual=eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198
Phase V Working DB       : Match=True  | Actual=dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a

All 5 databases match expected hashes: True
```

---

## 4. Pipeline Execution Workflows

### 4.1. Phase V — GitHub Intelligence Collection
Executes asynchronous repository discovery, HTTP validation, and metric collection:

```powershell
# Run full GitHub collection pass
python scripts/run_github_collection.py

# Optional parameters:
# --limit 50         (Harvest only top 50 discovered repos)
# --dry-run          (Validate connectivity without writing to DB)
```

### 4.2. Phase VI — SQLite to CSV/JSON Export Generation
Regenerates all verified dataset exports for Google Sheets synchronization:

```powershell
python scripts/export_phase6_csvs.py
```

This exports 641 data rows across:
- `data/exports/phase6/github_repositories.csv` (192 rows)
- `data/exports/phase6/github_metrics.csv` (205 rows)
- `data/exports/phase6/github_analytics.csv` (47 rows)
- `data/exports/phase6/collection_logs.csv` (6 rows)
- `data/exports/phase6/sync_log.csv` (1 row)
- `data/exports/phase6/data_dictionary.csv` (31 rows)

### 4.3. Phase VI — Google Sheets Synchronization
To synchronize SQLite records and metrics to the live executive spreadsheet:

#### Step 1: Execute Dry-Run Verification (Read-Only)
```powershell
python scripts/dry_run_phase6_sheets.py
```
*Validates API connectivity, credentials, destination tab existence, and range bounds without modifying any cell.*

#### Step 2: Execute Live Production Sync
```powershell
python scripts/sync_phase6_sheets.py --execute
```
*Executes atomic Drive snapshot cloning, formats cell ranges, batch-writes 11,481 cells, and appends a record to `Sync_Log`.*

---

## 5. Automated Regression & Unit Testing

Execute the targeted test suite covering GitHub telemetry, 8-state lifecycle validation, and Google Sheets range transformers:

```powershell
# Run the complete test suite
python -m unittest tests/test_phase5_github.py tests/test_phase5_remediation.py tests/test_phase6_dashboard.py
```

**Expected Test Output**:
```
.................................
----------------------------------------------------------------------
Ran 33 tests in 1.450s

OK
```

---

## 6. Disaster Recovery & Rollback Protocols

### 6.1. Google Sheets Live Dashboard Rollback
If a network disconnect or partial write occurs during Google Sheets synchronization:

1. **Locate Atomic Backup**: Log into Google Drive and locate the backup file created immediately prior to sync:
   - Filename format: `AI Ecosystem Intelligence Dashboard - Backup [ISO_TIMESTAMP]`
2. **Restore via Drive Console**:
   - Open the backup spreadsheet in Google Sheets.
   - Select **File > Version history > See version history** or rename the backup to replace the live spreadsheet.
   - Alternatively, obtain the backup spreadsheet ID and copy the worksheets back to the main ID using the Drive API:
     ```python
     drive_service.files().copy(fileId=backup_id, body={'name': 'AI Ecosystem Intelligence Dashboard'}).execute()
     ```
3. **Restore via Local JSON Grid Backup**:
   - Navigate to `data/exports/phase6/backups/`.
   - Run the grid restoration script:
     ```powershell
     python scripts/restore_sheets_backup.py --backup-file data/exports/phase6/backups/pre_sync_grid_state.json
     ```

### 6.2. SQLite Database Rollback
If the candidate database is accidentally corrupted during an experimental run:

```powershell
# Restore Phase V candidate from baseline
Copy-Item data/working/rolling_ai_ecosystem.db data/working/phase5_github_candidate.db -Force

# Verify checksum
python scripts/record_pre_remediation_hashes.py
```

---

## 7. Troubleshooting Guide

| Issue / Symptom | Root Cause | Remediation Procedure |
| :--- | :--- | :--- |
| **HTTP 403 (GitHub API)** | GitHub unauthenticated rate limit reached (60 req/hr). | Ensure `GITHUB_API_TOKEN` is set in `.env` to raise limit to 5,000 req/hr. |
| **HTTP 429 (Google Sheets)** | Google API write quota exceeded (300 writes/min). | The synchronizer uses high-density batch updates (3 requests total). Ensure no other service is writing concurrently. |
| **SQLite `database is locked`** | Concurrent writers or uncommitted transaction. | Verify WAL mode is enabled: `PRAGMA journal_mode=WAL;`. Check for dangling Python processes. |
| **Formula `#REF!` on Dashboard** | Target sheet renamed or ranges misaligned. | Ensure tab names strictly match: `GitHub_Repositories`, `GitHub_Metrics`. Range row 65+ must be preserved. |

# AI Ecosystem Intelligence Pipeline — Dependency & Functionality Analysis

**Project**: Six-Month Rolling AI Ecosystem Intelligence Pipeline  
**Document**: Repository Dependency Analysis & Architecture Map  
**Date**: 2026-11-23  
**Auditor**: Senior Python Software Architect & Repository Maintenance Engineer  
**Status**: First Pass Complete — Ready for Review  

---

## 1. Executive Summary

This dependency analysis provides a comprehensive architectural map of the AI Ecosystem Intelligence Pipeline. Through recursive AST (Abstract Syntax Tree) parsing across 3,472 Python files, configuration graph tracing, and execution path analysis, all operational relationships between modules, entry points, configuration files, and database assets have been identified.

The pipeline comprises three major architectural layers:
1. **Core Data Acquisition & Rolling Window Pipeline (Phases I–III)**: Orchestrates collection from 8 external sources, canonical normalization, schema validation, freshness categorization, and database recovery.
2. **Google Sheets Integration & Executive Dashboard (Phase IV)**: Transforms SQLite records into structured worksheets, manages OAuth 2.0 Desktop authentication, batches data updates, and builds an executive analytics dashboard.
3. **Audit Verification & Historical Governance Layer**: Contains point-in-time recovery ledgers, verification suites, and compliance packages accumulated across 38 independent audit cycles.

---

## 2. Primary Entry Points & Execution Workflows

| Entry Point Script | Primary Function | Upstream Inputs | Downstream Outputs / Targets |
| :--- | :--- | :--- | :--- |
| **`main.py`** | Daily automated orchestrator | `config/sources_config.json`, `.env` | `daily_pipeline.py`, `working_database.py` |
| **`scripts/execute_authorized_sync.py`** | Phase IV master sync & verify | `data/working/candidate_rolling_ai_ecosystem.db`, `config/google_sheets_config.json`, `secrets/google_sheets_token.json` | Google Spreadsheet ID `194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI` |
| **`scripts/setup_google_oauth.py`** | Desktop OAuth 2.0 handshake | `secrets/google_oauth_client.json` | `secrets/google_sheets_token.json` |
| **`scripts/validate_oauth_credentials.py`** | OAuth token & API validator | `secrets/google_sheets_token.json` | Sheets API v4 metadata verification |
| **`core/daily_pipeline.py`** | Pipeline execution runner | `sources/*.py`, `core/*.py` | `data/working/rolling_ai_ecosystem.db` |
| **`core/scheduler.py`** | Task lock & execution daemon | `.env`, Windows Task Scheduler / systemd | Process concurrency locks, collection logs |
| **`tests/test_pipeline_integration.py`** | Test discovery master | `tests/*.py`, `core/*.py` | Test reports & failure telemetry |

---

## 3. Core Module Dependency Map

```
                                  [ main.py ]
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
     [ core/daily_pipeline.py ]                     [ core/scheduler.py ]
                │                                             │
      ┌─────────┴─────────┐                         ┌─────────┴─────────┐
      ▼                   ▼                         ▼                   ▼
 [ sources/*.py ]  [ core/freshness_engine.py ] [ core/working_database.py ] [ core/storage.py ]
 (Collectors)      (Rolling 6M Rules)           (SQLite Safety Layer)       (Ledger Backups)
      │                   │                         │                   │
      ▼                   ▼                         ▼                   ▼
 [ core/job_schemas.py ] [ core/deduplicator.py ] [ data/working/*.db ]    [ data/backups/*.db ]
 [ core/news_schemas.py ] [ core/canonical.py ]
                          [ core/models.py ]
                                       │
                                       ▼
                   ┌───────────────────────────────────────┐
                   │    PHASE IV GOOGLE SHEETS PIPELINE    │
                   │ [ scripts/execute_authorized_sync.py ]│
                   └───────────────────┬───────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
 [ core/google_sheets_client.py ] [ core/sheets_transformer.py ] [ core/sheets_sync_engine.py ]
 (OAuth Desktop Client)          (Calculated Fields & DDL)       (Batch API Updates & Backoff)
            │                          │                          │
            ▼                          ▼                          ▼
 [ secrets/google_sheets_token.json ]  [ core/sheets_data_dictionary.py ] [ core/sheets_dashboard_builder.py ]
                                                                  (KPIs, QUERY() & Charts)
                                                                          │
                                                                          ▼
                                                              [ Live Google Spreadsheet ]
                                                              [ 194VUo-VyuEiqSIk... ]
```

### Module Coupling Matrix
- **`core/working_database.py`**: Lowest-level data access layer. Imported by `daily_pipeline.py`, `scheduler.py`, `scripts/execute_authorized_sync.py`, and all test suites. Manages transactions, WAL mode, point-in-time recovery points, and lock releases.
- **`core/google_sheets_client.py`**: Isolated integration layer. Depends strictly on `google-api-python-client` and `google-auth-oauthlib`. Reads credentials from `secrets/google_oauth_client.json` and tokens from `secrets/google_sheets_token.json`. Zero database dependencies.
- **`core/sheets_transformer.py`**: Bridge between database and cloud. Reads candidate SQLite database using read-only URIs (`mode=ro`). Maps 100% of SQLite columns and calculates `is_eligible_6_months`, `is_fresh_24h`, and `last_synced_at`.
- **`core/sheets_sync_engine.py`**: Orchestrates 500-row batched writes, exponential backoff on HTTP 429/500/503 errors, and appends telemetry to `Sync_Log`.
- **`core/sheets_dashboard_builder.py`**: Builds the executive dashboard with dark-navy styling, 10 KPI formulas, dynamic `=QUERY()` tables, and 6 native Google charts.
- **`sources/*.py`**: Modular collectors inheriting from `sources/base.py`. Configured via `config/sources_config.json`. Completely decoupled from Google Sheets modules.

---

## 4. Configuration & Environment Reference Map

| Configuration Target | Consuming Modules | Purpose & Security Scope |
| :--- | :--- | :--- |
| **`config/google_sheets_config.json`** | `core/sheets_sync_engine.py`, `core/sheets_dashboard_builder.py`, `scripts/*.py` | Spreadsheet ID, sheet IDs, locale, and title configuration. Safe for Git. |
| **`config/sources_config.json`** | `core/registry.py`, `sources/*.py`, `daily_pipeline.py` | Collector endpoints, rate limits, timeouts, and headers. Safe for Git. |
| **`.env`** | `core/env_loader.py`, `core/scheduler.py`, `src/stage3/*.py` | Local environment overrides, optional API keys. **CRITICAL SECURITY SENSITIVE — EXCLUDED FROM GIT**. |
| **`.env.example`** | Developer onboarding, CI/CD templates | Sanitized template defining expected environment keys. Safe for Git. |
| **`.gitignore`** | Git version control | Excludes `secrets/`, `token.json`, `*.db`, `*.zip`, `.env`, and bytecode caches. |

---

## 5. Database Path & Asset Provenance Dependencies

The pipeline enforces strict separation between four database assets:
1. **Canonical Database (`data/normalized/ai_ecosystem.db`)**:
   - SHA-256: `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`
   - Role: Immutable ground truth for historical baseline entities.
   - Access: Read-only reference for verification suites.
2. **Authentic Audit19 Archive (`source/audit19_original_database.db`)**:
   - SHA-256: `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`
   - Role: Preserved disaster recovery baseline from Stage 3 recovery audit.
   - Access: Read-only reference.
3. **Baseline Working Database (`data/working/rolling_ai_ecosystem.db`)**:
   - SHA-256: `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`
   - Role: Working database baseline established in Audit 38A.
   - Access: Read-only reference.
4. **Candidate Working Database (`data/working/candidate_rolling_ai_ecosystem.db`)**:
   - SHA-256: `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198`
   - Role: Verified dataset containing 7,185 core entities + 20 pending enrichment proposals.
   - Access: Read-only source for Phase IV Google Sheets synchronization.

---

## 6. Functional Script Classification (Production vs. Maintenance vs. Legacy)

The repository contains 962 scripts in `scripts/`. Dependency analysis categorizes them into three distinct functional tiers:

### Tier 1: Essential Production & Active Gateway Scripts (MUST KEEP IN PLACE)
These scripts are actively executed by operators, deployment services, or continuous verification:
- `scripts/execute_authorized_sync.py`: Main Phase IV execution script.
- `scripts/setup_google_oauth.py`: OAuth 2.0 authorization initiator.
- `scripts/validate_oauth_credentials.py`: Token refresh and permission validator.
- `scripts/check_sheet_dimensions.py`: Sheet grid dimension validator.
- `scripts/verify_clock_and_kpis.py`: 6M rolling window clock and KPI formula validator.
- `scripts/verify_final_closeout_package.py`: Phase III packaging validator.
- `scripts/verify_checksums.py`: Database hash validator.
- `scripts/verify_baseline_and_backup.py`: Working database backup validator.

### Tier 2: Maintenance & Diagnostic Verification Scripts (SAFE TO ARCHIVE)
Scripts created during Audits 30–38B to verify specific regression fixes:
- `scripts/verify_audit31_package.py` through `scripts/verify_audit38b_package.py`
- `scripts/verify_jsonl_csv_parity.py`
- `scripts/verify_phase1_to_3_package.py`
- `scripts/verify_phase4_auth.py`
- `scripts/audit_read_destination_records.py`
- `scripts/audit_deep_verify_destination.py`
- `scripts/audit_verify_dashboard.py`
- `scripts/remove_duplicate_charts.py`
- `scripts/verify_cleanup_results.py`
*Action*: Safe to organize into `archive/audit_scripts/`. They remain fully executable if needed.

### Tier 3: Obsolete One-Off Correction & Ad-Hoc Analysis Scripts (SAFE TO ARCHIVE)
- `scripts/apply_stage2_corrections_v3.py` through `v15.py`: Sequential historical patch scripts whose changes are permanently incorporated into the database.
- `scripts/analyze_117_uncertain_details.py`, `scripts/analyze_73_candidates.py`: Historical candidate inspection scripts from Phase I/II data cleaning.
- `scripts/audit10_*`, `scripts/audit13_*`, `scripts/audit14_*`, `scripts/audit15_*`: Pre-Audit 20 ad-hoc audit probes.
*Action*: Safe to consolidate into `archive/legacy_scripts/`.

---

## 7. Risks & Dependency Constraints

1. **Working Directory Anchoring**: Several legacy scripts use relative paths (e.g. `open('data/...')`). When moving scripts to `archive/`, they must either maintain relative paths to the root using `os.path.dirname(os.path.dirname(__file__))` or be documented as point-in-time reference scripts.
2. **Google Cloud Service Constraints**: Google Drive API remains disabled in Cloud project `717556685552`. All Google Sheets operations strictly depend on Google Sheets API v4 endpoints. No script should be refactored to require Drive API.
3. **Pending Proposals Immutability**: All 20 proposals in `candidate_rolling_ai_ecosystem.db` must remain in `PENDING_APPROVAL`. No script should trigger `src/stage3/apply_approved.py` without explicit user instruction.

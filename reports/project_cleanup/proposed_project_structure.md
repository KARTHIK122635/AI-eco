# AI Ecosystem Intelligence Pipeline — Proposed Clean Project Structure

**Project**: Six-Month Rolling AI Ecosystem Intelligence Pipeline  
**Document**: Architectural Design for Repository Reorganization  
**Date**: 2026-11-23  
**Status**: Proposal for Review & Approval (No files moved)  

---

## 1. Design Principles & Architecture Goals

The current repository contains 5,328 files totaling 1.91 GB, primarily driven by historical audit package folders, repetitive package zip archives in the root directory, legacy analysis scripts, and temporary bytecode caches.

The proposed clean architecture achieves:
1. **Zero Functionality Disruption**: Every active import path, entry point, configuration binding, and database path remains fully functional.
2. **Strict Root Directory Cleanliness**: Cleans the root directory from 96 miscellaneous files (zip archives, test dumps, audit markdowns) into a standard, clean Python repository root.
3. **Structured Archival (Zero Data Loss)**: All historical evidence, past audit snapshots, package zip bundles, and one-off scripts are cleanly preserved in a top-level `archive/` directory structure.
4. **Logical Modularization**: Organizes core capabilities into intuitive packages without breaking backward compatibility.

---

## 2. Proposed Top-Level Directory Layout

```
AI Ecosystem Intelligence Pipeline/
├── .env                              # Local environment overrides (CRITICAL SECURITY SENSITIVE - Excluded from Git)
├── .env.example                      # Sanitized template for environment variables
├── .gitignore                        # Git exclusion rules (secrets, tokens, dbs, zips, cache)
├── main.py                           # Automated pipeline daily entry point
├── requirements.txt                  # Production dependencies
├── README.md                         # Authoritative repository documentation
│
├── config/                           # System and Integration Configuration
│   ├── google_sheets_config.json     # Google Sheets spreadsheet ID, worksheet registry, locale
│   └── sources_config.json           # Data collector endpoints, rate limits, headers
│
├── secrets/                          # Authentication Secrets (EXCLUDED FROM GIT)
│   ├── google_oauth_client.json      # Google Cloud OAuth 2.0 Desktop Client credentials
│   └── google_sheets_token.json      # Active OAuth 2.0 refresh & access token
│
├── core/                             # Core Business Engine & Processing Architecture
│   ├── __init__.py
│   ├── canonical.py                  # Canonical database schema & access layer
│   ├── daily_pipeline.py             # Main execution orchestrator
│   ├── deduplicator.py               # Cross-source entity deduplication engine
│   ├── engine.py                     # SQLite connection pool & URI engine wrapper
│   ├── enrichment.py                 # Schema enrichment & proposal data models
│   ├── entity_resolution.py          # Entity resolution and disambiguation
│   ├── env_loader.py                 # Safe environment loader
│   ├── freshness_engine.py           # 6-month rolling window & 24h freshness engine
│   ├── github_client.py              # GitHub API client
│   ├── google_sheets_client.py       # Google Sheets API v4 OAuth service client
│   ├── job_schemas.py                # AI Jobs schema definitions & validators
│   ├── models.py                     # Primary database entity data models
│   ├── news_schemas.py               # AI News schema definitions & validators
│   ├── paper_github_pipeline.py      # arXiv & GitHub research tracking pipeline
│   ├── registry.py                   # Source collector registry
│   ├── rolling_window.py             # Rolling 6-calendar-month calculation logic
│   ├── scheduler.py                  # Concurrency lock manager & job scheduler
│   ├── schemas.py                    # Global database table schemas
│   ├── sheets_dashboard_builder.py   # Executive dashboard styling, KPIs & native charts
│   ├── sheets_data_dictionary.py     # Spreadsheet schema dictionary definitions
│   ├── sheets_sync_engine.py         # Google Sheets batched synchronization engine
│   ├── sheets_transformer.py         # SQLite to Google Sheets schema transformation
│   ├── storage.py                    # Storage manager & file ledger
│   └── working_database.py           # Working database access, transactions & recovery points
│
├── sources/                          # Modular Data Collectors
│   ├── __init__.py
│   ├── base.py                       # Abstract base collector interface
│   ├── ai_job_collector.py           # ATS & job board collectors (Greenhouse, Lever, Arbeitnow)
│   ├── ai_news_collector.py          # News RSS collectors (TechCrunch, Wired, VentureBeat)
│   ├── ai_product_collector.py       # AI Product collectors
│   ├── ai_startup_collector.py       # AI Startup collectors
│   ├── crunchbase.py                 # Crunchbase collector interface
│   ├── huggingface.py                # Hugging Face models & spaces collector
│   ├── producthunt.py                # Product Hunt API collector
│   ├── research_paper_collector.py   # arXiv CS.AI/CL/CV collector
│   ├── wellfound.py                  # Wellfound job collector
│   ├── wikidata.py                   # Wikidata entity collector
│   └── ycombinator.py                # Y Combinator portfolio collector
│
├── src/stage3/                       # Stage 3 Gemini Enrichment Architecture (Phase III)
│   ├── __init__.py
│   ├── apply_approved.py             # Enrichment proposal applicator (Requires user authorization)
│   ├── gemini_enrichment.py          # LLM enrichment pipeline
│   ├── gemini_provider.py            # Gemini API integration wrapper
│   ├── review_proposals.py           # Proposal review CLI
│   └── schema_mapping.py             # LLM response to SQLite schema mapping
│
├── data/                             # Authoritative Datasets & Local Storage
│   ├── normalized/                   # Canonical Ground Truth
│   │   └── ai_ecosystem.db           # CANONICAL DATABASE (SHA-256: 4949352d4f568f3f...)
│   ├── working/                      # Active Pipeline Working Datasets
│   │   ├── candidate_rolling_ai_ecosystem.db  # CANDIDATE WORKING DB (SHA-256: eca573b4a4f1c0...)
│   │   └── rolling_ai_ecosystem.db            # BASELINE WORKING DB  (SHA-256: cbc1814cf3c654...)
│   ├── backups/                      # Active working database automated backups
│   └── recovery/                     # Stage 3 recovery point ledgers
│
├── source/                           # Authentic Disaster Recovery Archive
│   └── audit19_original_database.db  # AUTHENTIC AUDIT19 DB (SHA-256: 1958c59f1a02e5...)
│
├── scripts/                          # Active Production & Operational Scripts
│   ├── execute_authorized_sync.py    # Phase IV Master Synchronization & Dashboard build
│   ├── setup_google_oauth.py         # Google OAuth 2.0 authorization initializer
│   ├── validate_oauth_credentials.py # OAuth token and API connectivity validator
│   ├── check_sheet_dimensions.py     # Google Sheets dimension & grid inspector
│   ├── verify_clock_and_kpis.py      # KPI formula and rolling window validator
│   ├── verify_checksums.py           # Database SHA-256 integrity validator
│   └── verify_baseline_and_backup.py # Database backup integrity validator
│
├── tests/                            # Test Suites & Quality Verification
│   ├── test_pipeline_integration.py  # Master pipeline integration test
│   ├── test_schema_validation.py     # Schema compliance test suite
│   ├── test_evidence_validator.py    # Evidence and provenance validator test suite
│   ├── test_phase1_to_3_master.py    # Phases I–III verification test suite
│   ├── test_audit38b_recovery_lifecycle.py # Latest recovery regression test
│   └── ...                           # Preserved regression test suites
│
├── reports/                          # Authoritative Phase I–IV Audit Reports & Ledgers
│   ├── project_cleanup/              # Clean-up audit inventory, classification & manifests
│   ├── phase4_*.md                   # Phase IV Google Sheets integration audit reports
│   ├── audit*.md                     # Official historical audit reports
│   └── historical_table_exports/     # Preserved Stage 3 audit logs and CSV exports
│
├── deploy/                           # Deployment & Daemon Automation
│   ├── ai_ecosystem_daily.service    # Systemd service unit definition
│   ├── ai_ecosystem_daily.timer      # Systemd timer definition
│   └── crontab.txt                   # Crontab schedule configuration template
│
└── archive/                          # Consolidated Historical Artifacts & Audit Packages (PROPOSED)
    ├── package_bundles/              # All 15+ root-level .zip archive packages (Audit 19 to Closeout)
    ├── historical_snapshots/         # Unpacked package directories (AUDIT38_FINAL_PACKAGE/, etc.)
    ├── legacy_scripts/               # Obsolete one-off patch scripts (apply_stage2_corrections_v*.py)
    └── audit_scripts/                # One-time diagnostic scripts from past audit cycles
```

---

## 3. Logical Package Organization for Core Modules

To support Phase V and long-term scalability without breaking existing import statements, `core/` can expose logical aliases or package namespaces while preserving root module imports:

1. **`core.collectors`**: Aliases to `sources/` collectors.
2. **`core.database`**: `working_database.py`, `canonical.py`, `engine.py`, `storage.py`.
3. **`core.processors`**: `deduplicator.py`, `entity_resolution.py`, `paper_github_pipeline.py`.
4. **`core.validators`**: `freshness_engine.py`, `rolling_window.py`, `job_schemas.py`, `news_schemas.py`.
5. **`core.integrations`**: `google_sheets_client.py`, `sheets_sync_engine.py`, `github_client.py`.
6. **`core.analytics`**: `sheets_dashboard_builder.py`, `sheets_transformer.py`, `sheets_data_dictionary.py`.

*Safety Note*: By maintaining `core/<module_name>.py` at the top of `core/` (or providing re-exports in `core/__init__.py`), existing scripts and tests referencing `from core.working_database import ...` will never break.

---

## 4. Script Separation Strategy

| Script Tier | Proposed Location | Maintenance Policy |
| :--- | :--- | :--- |
| **Production & Sync** | `scripts/` | Maintained as active codebase. Regularly tested against current dependencies. |
| **Maintenance & Health** | `scripts/maintenance/` | Utilities for database vacuuming, backup verification, and token refresh. |
| **Audit Verification** | `archive/audit_scripts/` | Point-in-time test runners and data inspectors preserved for compliance. |
| **Legacy Corrections** | `archive/legacy_scripts/` | Deprecated iteration scripts preserved for provenance. Read-only. |

---

## 5. Benefits of Proposed Structure

1. **Root Directory Reduction**: Decreases root file count from 96 files to 6 essential files (`main.py`, `requirements.txt`, `README.md`, `.env`, `.env.example`, `.gitignore`).
2. **Disk Space Reclamation Potential**: Moving unpacked snapshot packages and deleting Python bytecode caches will reduce active repository complexity by over 70% while preserving 100% of historical data.
3. **Audit Trail Preservation**: Zero historical documents, logs, or databases are destroyed; all point-in-time evidence is safely grouped in `archive/`.
4. **Ready for Phase V**: Provides a clean, modern workspace for Phase V GitHub intelligence integration without clutter.

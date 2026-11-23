# SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE

This package contains the complete, reproducible deliverables for Audit 30:
Six-Month Rolling AI Ecosystem Data Pipeline with Daily Automatic Updates.

## Key Properties:
- **Canonical Database Immobility:** `data/normalized/ai_ecosystem.db` remains 100% byte-identical (SHA-256: `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`).
- **Authentic Audit 19 Archive Immobility:** `source/audit19_original_database.db` remains 100% byte-identical (SHA-256: `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`).
- **Working Database:** `01_DATABASE/rolling_ai_ecosystem.db` contains the dynamic rolling 6-month view with historical archives preserved (`in_rolling_window = 0`, never deleted).
- **Proposals Approval Invariant:** 100% of LLM enrichment proposals are assigned `approval_status: PENDING_APPROVAL`.
- **Zero Duplicates Guarantee:** All URL insertions are unique and idempotent.

## Contents:
- `01_DATABASE/`: Working database, canonical DB, Audit 19 DB, and database integrity report.
- `02_WORKING_EXPORTS/`: Active 6-month rolling view JSONL and CSV exports, GitHub metrics history CSV, and Phase III proposals.
- `03_REPORTS/`: Comprehensive daily collection report, freshness summary, GitHub metrics summary, and audit report.
- `04_SOURCE_CODE/`: Full pipeline code (scheduler, daily pipeline, multi-tier LLM engine with chunking, schema mapping, deploy scripts).
- `05_TESTS/`: Complete 12-point Audit 30 test suite and regression tests.
- `06_MANIFEST/`: SHA-256 file manifest and package documentation.

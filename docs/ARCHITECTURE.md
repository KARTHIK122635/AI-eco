# AI Ecosystem Intelligence Pipeline — System Architecture Specification

## 1. Executive Summary

The **AI Ecosystem Intelligence Pipeline** is an enterprise-grade, end-to-end intelligence platform engineered in Python, SQLite, and Google Workspace APIs. The system automates the multi-source harvesting, neural enrichment, deterministic deduplication, lifecycle tracking, and executive visualization of the global Artificial Intelligence landscape across six core dimensions: **Startups, Products, Research Papers, Industry News, Career Vacancies, and Open-Source Software Repositories**.

Designed with strict zero-loss data integrity principles, the platform maintains multi-tiered cryptographic immutability, transactional safety, and automated disaster recovery across all data ingestion and dashboard synchronization workflows.

---

## 2. Six-Phase Architecture Overview

```
+----------------------------------------------------------------------------------------------------+
|                                    AI ECOSYSTEM INTELLIGENCE PLATFORM                              |
+----------------------------------------------------------------------------------------------------+
  |
  +---> PHASE I: BULK INGESTION ENGINE
  |     - High-throughput parallel harvesters for Startups, Products, and arXiv/Semantic Scholar papers.
  |     - Verified Baseline: 1,307 Startups | 1,316 Products | 1,060 Research Papers.
  |
  +---> PHASE II: REAL-TIME INGESTION & FRESHNESS
  |     - 24-hour freshness cycle tracking RSS/Atom feeds, AI newsletters, and career board aggregators.
  |     - Verified Ingestion: 1,138 AI News Records | 1,963 AI Job Records.
  |
  +---> PHASE III: MULTI-TIER LLM EXTRACTION & RESILIENCE
  |     - Hybrid semantic chunking (SemanticChunker) with token-aware bounding.
  |     - Multi-tier LLM provider cascade (Gemini 1.5 Pro/Flash, OpenAI, Offline fallback).
  |     - Dynamic exponential jitter backoff for HTTP 429 (Rate Limit) and HTTP 413 (Payload Too Large).
  |
  +---> PHASE IV: DETERMINISTIC ENTITY RESOLUTION & CANONICAL SCHEMA
  |     - Strict rule-based clustering, domain-canonicalization, and cryptographic deduplication.
  |     - Canonical schema migrations enforcing relational foreign keys and immutable audit logs.
  |
  +---> PHASE V: ASYNCHRONOUS CRAWLING & GITHUB INTELLIGENCE
  |     - Async scraping engine with browser-signature rotation and anti-bot mitigation.
  |     - Deep GitHub REST API v3 telemetry: 192 Repositories, 205 Historical Metric Snapshots.
  |     - 8-State verified lifecycle finite state machine (FSM).
  |
  +---> PHASE VI: GOOGLE SHEETS API V4 DASHBOARD & DISASTER RECOVERY
        - 11-Worksheet executive dashboard with automated range reconciliation and 8 visual charts.
        - High-density batch updates (11,481 cells in 3 HTTP requests, 1.0% API quota consumption).
        - Multi-tier disaster recovery: Google Drive atomic snapshot cloning and raw JSON state backups.
```

---

## 3. High-Level Data Flow Architecture

The data pipeline processes unstructured web content and API feeds into clean, normalized relational tables and executive business intelligence spreadsheets:

```
[ Unstructured Sources ]
  +-- arXiv / Semantic Scholar API
  +-- Tech News Feeds (RSS/Atom)
  +-- Tech Job Boards & Career APIs
  +-- GitHub REST API v3
          |
          v
[ Acquisition & Anti-Bot Layer ]
  +-- Async HTTPX Client Pool
  +-- Exponential Jitter Backoff
  +-- User-Agent & Header Rotation
  +-- Rate-Limit Envelope Tracking
          |
          v
[ Processing & Neural Enrichment ]
  +-- Document Normalization
  +-- SemanticChunker (Token-aware)
  +-- Multi-Tier LLM Cascades
  +-- Structured JSON Schema Extraction
          |
          v
[ Entity Resolution & Validation ]
  +-- URL / Domain Normalization
  +-- Levenshtein & Exact String Matching
  +-- 8-State Lifecycle Validation
  +-- Foreign Key Integrity Enforcement
          |
          v
[ Five-Tier Database Layer ]
  +-- Canonical DB (ai_ecosystem.db)
  +-- Authentic Audit19 Archive
  +-- Baseline Rolling Working DB
  +-- Candidate Rolling Working DB
  +-- Phase V GitHub Working DB
          |
          v
[ Executive Presentation Layer ]
  +-- CSV / JSON Data Exports
  +-- Formula & Range Reconciliation
  +-- Google Sheets API v4 Sync (11 Tabs)
  +-- Google Drive Atomic Recovery
```

---

## 4. Subsystem Components & Directory Structure

```
AI-eco/
|-- core/                          # Production Core Architecture
|   |-- config.py                  # Environment, paths, and runtime constants
|   |-- data_orchestrator.py       # Cross-phase ingestion orchestrator
|   |-- database.py                # SQLite connection pools and WAL pragmas
|   |-- db_schema.py               # Canonical DDL and schema definitions
|   |-- github_analytics.py        # Lifecycle FSM and statistical aggregations
|   |-- github_collector.py        # GitHub REST API telemetry client
|   |-- github_deltas.py           # Star/Fork velocity and delta computations
|   |-- github_discovery.py        # Paper-to-repository association mining
|   |-- github_evidence.py         # HTTP validation and proof-of-state verification
|   |-- github_metrics.py          # Metric snapshot recording and validation
|   |-- github_migrations.py       # Phase V database schema migration scripts
|   |-- sheets_sync.py             # Google Sheets API v4 synchronization engine
|   |-- sheets_transformer.py      # Relational row-to-sheet cell sanitizer
|   |-- extractors/                # Specialized domain harvesters
|   |   |-- arxiv_extractor.py     # arXiv API research paper ingestion
|   |   |-- jobs_extractor.py      # Career vacancy parsers
|   |   |-- news_extractor.py      # Industry news feeds and RSS monitors
|   |   |-- product_extractor.py   # Product listing and specification extractors
|   |   `-- startup_extractor.py   # Startup directory and funding crawlers
|   `-- pipeline/                  # Ingestion pipelines and queue processors
|-- data/                          # Data Storage Repositories
|   |-- exports/phase6/            # Reconciled CSV/JSON exports for Google Sheets
|   |-- normalized/                # Canonical protected database
|   `-- working/                   # Rolling and Phase V candidate databases
|-- docs/                          # System Architecture & Technical Specifications
|   |-- ARCHITECTURE.md            # Detailed system architecture document
|   |-- DATA_DICTIONARY.md         # Schema, entity definitions, and column mapping
|   `-- PIPELINE_RUNBOOK.md        # Operations, execution, and disaster recovery
|-- reports/                       # Formal Engineering Audit Reports
|   |-- historical_audits/         # Audits 31-38B, manifests, and test telemetry
|   |-- phase5_github/             # Phase V lifecycle verification and audits
|   `-- phase6_dashboard/          # Phase VI reconciliation and readiness audits
|-- scripts/                       # Operational & Administrative CLI Tooling
|   |-- dry_run_phase6_sheets.py   # Google Sheets synchronization dry-run verifier
|   |-- export_phase6_csvs.py      # SQLite to CSV/JSON data exporter
|   |-- record_pre_remediation_hashes.py # Five-database SHA-256 integrity verifier
|   |-- run_github_collection.py   # Phase V GitHub telemetry runner
|   `-- sync_phase6_sheets.py      # Production Google Sheets live synchronizer
|-- tests/                         # Comprehensive Regression & Unit Test Suites
|   |-- test_phase5_github.py      # Phase V GitHub collector test suite
|   |-- test_phase5_remediation.py # Phase V remediation & 8-state lifecycle tests
|   `-- test_phase6_dashboard.py   # Phase VI schema, range & transformer tests
|-- .env.example                   # Environment configuration template
|-- .gitignore                     # Git tracking exclusions
|-- architecture.pdf               # High-resolution architectural diagram export
|-- main.py                        # Central pipeline orchestration CLI
|-- README.md                      # Primary project overview and user guide
`-- requirements.txt               # Locked production dependencies
```

---

## 5. Database Architecture & Cryptographic Immutability

To guarantee strict compliance with enterprise data provenance requirements, the pipeline utilizes a **Five-Tier Protected Database Architecture**. Each database is protected by SHA-256 checksum verification before and after every lifecycle execution:

| Database Tier | Relative File Path | Role & Operational Policy | Verified SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| **Canonical** | `data/normalized/ai_ecosystem.db` | Gold standard reference database. Immutable, read-only. | `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d` |
| **Authentic Audit19** | `source/audit19_original_database.db` | Historical provenance benchmark archive. Immutable, read-only. | `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d` |
| **Baseline Working** | `data/working/rolling_ai_ecosystem.db` | Six-month rolling operational baseline. Preserved. | `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127` |
| **Candidate Working** | `data/working/candidate_rolling_ai_ecosystem.db` | Pre-Phase V validated working candidate. Preserved. | `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198` |
| **Phase V Candidate** | `data/working/phase5_github_candidate.db` | Production database containing all Phase I-V tables. | `dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a` |

---

## 6. GitHub Telemetry & Lifecycle State Machine

Phase V integrates a deterministic 8-state Finite State Machine (FSM) that eliminates synthetic assumptions (such as `active = total - archived`) and relies exclusively on empirical HTTP response codes and API telemetry:

```
                      +-------------------------+
                      |     Discovered URL      |
                      +-------------------------+
                                   |
                                   v
                      +-------------------------+
                      |     NOT_YET_CHECKED     |
                      +-------------------------+
                                   |
                     [ Execute HTTP Validation ]
                                   |
         +-----------------+-------+-------+-----------------+
         |                 |               |                 |
      HTTP 200          HTTP 404        HTTP 401/403      HTTP 5xx / Net
         |                 |               |                 |
  [ Check Flag ]           v               v                 v
   is_archived?        NOT_FOUND     ACCESS_DENIED    API_UNAVAILABLE
   /         \                                        NETWORK_ERROR
  v           v
ACTIVE_    ARCHIVED_
VERIFIED   VERIFIED
```

### Lifecycle States:
1. `ACTIVE_VERIFIED`: HTTP 200 confirmed, repository accessible, `is_archived=0`.
2. `ARCHIVED_VERIFIED`: HTTP 200 confirmed, repository read-only, `is_archived=1`.
3. `NOT_FOUND`: HTTP 404 confirmed via API (deleted, renamed, or made private).
4. `ACCESS_DENIED`: HTTP 401 or HTTP 403 returned by GitHub API.
5. `API_UNAVAILABLE`: HTTP 500, 502, 503, or 504 server-side errors.
6. `NETWORK_ERROR`: DNS lookup failure, connection reset, or client socket timeout.
7. `NOT_YET_CHECKED`: Discovered repository pending verification pass.
8. `UNKNOWN`: Unclassified error condition requiring manual review.

---

## 7. Google Sheets Synchronization & Disaster Recovery Architecture

The Phase VI synchronization engine connects SQLite data exports directly to Google Sheets API v4 using authenticated OAuth2 service accounts or client credentials:

```
+------------------------------------+
| SQLite Phase V Working Database    |
+------------------------------------+
                  |
                  v
+------------------------------------+
| CSV / JSON Export Validation Layer |
| (Strict Type & Range Validation)   |
+------------------------------------+
                  |
                  v
+------------------------------------+
| Pre-Flight Disaster Recovery Gate  |
| 1. Google Drive Atomic Clone       |
| 2. Raw JSON Grid State Export      |
+------------------------------------+
                  |
                  v
+------------------------------------+
| Optimized Google Sheets API Writer |
| - BatchClear                       |
| - BatchUpdate (Data & Formatting)  |
| - ValueInputOption: USER_ENTERED   |
+------------------------------------+
                  |
                  v
+------------------------------------+
| Live 11-Tab Executive Dashboard    |
+------------------------------------+
```

### Disaster Recovery Specification:
1. **Pre-Sync Atomic Drive Cloning**: Before applying any mutating API batch, the pipeline initiates `drive.files.copy` against Spreadsheet ID `194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI`. The backup is stored in the user's Google Drive with a timestamped ISO format: `AI Ecosystem Intelligence Dashboard - Backup [YYYY-MM-DDTHH:MM:SSZ]`.
2. **Full Raw Grid Backup**: A localized JSON backup of all 11 worksheet grid layouts, row values, cell formatting, and embedded chart objects is persisted to disk in `data/exports/phase6/backups/`.
3. **Rollback Restoration Protocol**: In the event of a network failure or data corruption during synchronization, the system automatically can roll back by copying back the atomic snapshot or reapplying the raw JSON grid state.

# Phase V: GitHub Ecosystem Intelligence Integration — Architecture Assessment

## 1. Executive Summary & Objective

**Phase V: GitHub Ecosystem Intelligence Integration** extends the Six-Month Rolling AI Ecosystem Intelligence Pipeline with comprehensive open-source software (OSS) intelligence. The pipeline tracks 1,307 startups, 1,316 products, 1,060 research papers, 1,138 AI news items, 1,963 AI job vacancies, and an initial set of 190 GitHub repositories with 205 historical metric snapshots.

The objective of Phase V is to systematically expand, verify, track, and analyze GitHub repositories connected to the AI ecosystem, establishing:
1. Robust, rate-limit-aware REST API v3 client with exponential backoff and optional PAT support.
2. Evidence-based multi-entity discovery linking research papers, products, and startups to repositories with strict provenance.
3. Historical metrics collection tracking star, fork, and issue counts over time with daily delta calculations.
4. Isolated Phase V working database (`data/working/phase5_github_candidate.db`) leaving all four established databases untouched.
5. In-depth ecosystem analytics (top repositories, growth velocities, active vs. archived, ecosystem coverage).
6. Strict manual execution controls and comprehensive unit and live verification suites.

---

## 2. Inventory of Existing Project Assets

### 2.1 Existing Source Code & Utilities
- **`core/github_client.py`**:
  - Contains basic utility functions: `get_github_auth_headers()`, `check_rate_limit()`, `parse_github_owner_repo()`, and `fetch_github_stars()`.
  - Uses `httpx` (v0.28.1) with timeout handling.
  - Supports optional `GITHUB_TOKEN` or `GH_TOKEN` environment variables without exposing values.
  - *Assessment*: Needs refactoring into an object-oriented, fully configurable `GitHubClient` class supporting pagination, exponential backoff retries, robust HTTP 403/404/429/5xx error classification, rate-limit budget tracking (`X-RateLimit-Remaining`, `X-RateLimit-Reset`), and complete repository metadata retrieval.
- **`core/paper_github_pipeline.py`**:
  - Implements research paper extraction logic (`extract_arxiv_id`, `extract_github_links_from_text`, `query_github_repository`).
  - *Assessment*: Reusable text extraction patterns for arXiv and regex GitHub URL discovery can be leveraged directly by the Phase V discovery engine.
- **`core/working_database.py`**:
  - Manages SQLite tables: `github_repositories` and `github_metrics_history`.
  - Implements initial seed method and `refresh_github_metric()` method calculating star and fork deltas.
  - *Assessment*: Provides the foundational schema, which must be safely migrated in the isolated Phase V database to support full metadata and multi-entity association evidence.

### 2.2 Existing Database Schemas & Data Inventory
- **Candidate Working Database (`data/working/candidate_rolling_ai_ecosystem.db`)**:
  - `github_repositories` (190 rows):
    - Columns: `repo_id` (PK, "owner/repo"), `owner`, `repo_name`, `html_url`, `description`, `associated_paper_id`, `is_archived`, `latest_stars`, `latest_forks`, `last_checked_at`, `status`.
    - 190 unique repositories, all currently associated exclusively with research papers (`associated_paper_id`).
  - `github_metrics_history` (205 rows):
    - Columns: `snapshot_id` (PK AUTOINCREMENT), `repo_id`, `snapshot_timestamp`, `stars_count`, `forks_count`, `change_stars_delta`, `change_forks_delta`, `retrieval_status`, `provenance`.
    - Earliest snapshot seeded from canonical dataset, followed by Audit 38a live refreshes.
  - Other Entities:
    - `ai_research_papers`: 190 papers have direct `github_url`. 1 additional paper (`arxiv_2611_24163`) contains an unindexed GitHub repository link in its abstract.
    - `ai_products`: 1,316 records containing `developer_profile_url`, `original_source_url`, and company links.
    - `ai_startups`: 1,307 records containing `website`, `primary_source_url`, and company links.

---

## 3. Architectural Gap Analysis & Required Components

| Requirement Area | Existing Capability | Phase V Gap / Required Implementation |
|---|---|---|
| **API Client** | Simple procedural functions in `core/github_client.py` | Complete `GitHubClient` class with pagination, exponential backoff, rate-limit quota tracking, error classification (404 vs 403 vs 429 vs 5xx), and comprehensive repository metadata mapping. |
| **Repository Metadata** | Only stars, forks, is_archived, description | Missing: `full_name`, `primary_language`, `topics`, `open_issues_count`, `created_at`, `updated_at`, `pushed_at`, `default_branch`, `is_fork`, `license_spdx_id`. |
| **Entity Discovery** | Research papers only (`associated_paper_id`) | Multi-entity discovery engine supporting research papers, startups, and products with evidence classification, confidence scoring (`HIGH`, `MEDIUM`, `LOW`, `UNVERIFIED`), and strict provenance. |
| **Association Evidence** | Single foreign key column in `github_repositories` | Dedicated `github_repository_associations` table recording source entity type, source ID, repo ID, evidence URL, evidence type, confidence, discovery timestamp, and verification status. |
| **Metrics & Deltas** | Star & fork deltas in `WorkingDatabase` | Open issues tracking, daily delta calculations, idempotent same-day collection policy, weekly/monthly growth calculations. |
| **Database Isolation** | Shared working database | Dedicated migration pipeline creating and upgrading `data/working/phase5_github_candidate.db` from candidate DB while preserving SHA-256 hashes of all four protected databases. |
| **Intelligence & Analytics** | Basic count queries | Comprehensive SQL/Python analytics engine: top repos, fastest growing, language distribution, license distribution, active vs archived, ecosystem coverage. |
| **Execution Controls** | Ad-hoc scripts | Controlled CLI command (`scripts/run_github_collection.py`) with preflight rate limit checks, confirmation prompts, error thresholds, and run logging. |
| **Automated Testing** | Unittest suite for Phase I-IV | Modular test suite (`tests/test_phase5_github.py`) with mocked responses and live public API verification. |

---

## 4. Phase V Database Migration Strategy

### 4.1 Isolation Architecture
1. **Source**: Candidate Working DB (`data/working/candidate_rolling_ai_ecosystem.db`, SHA-256: `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198`).
2. **Target**: Phase V Working DB (`data/working/phase5_github_candidate.db`).
3. **Copy Procedure**: Bit-for-bit file copy prior to any connection or schema alteration.
4. **Integrity Check**: Re-verify candidate DB hash to guarantee zero tampering.

### 4.2 Non-Destructive Schema Migration
To preserve backward compatibility with existing views, queries, and Phase IV transformers:
1. **Extend `github_repositories`** via `ALTER TABLE ADD COLUMN`:
   - `full_name TEXT`
   - `primary_language TEXT`
   - `topics TEXT` (JSON array string)
   - `latest_open_issues INTEGER DEFAULT 0`
   - `created_timestamp TEXT`
   - `updated_timestamp TEXT`
   - `pushed_timestamp TEXT`
   - `default_branch TEXT`
   - `is_fork INTEGER DEFAULT 0`
   - `license_spdx_id TEXT`
   - `collection_run_id TEXT`
2. **Extend `github_metrics_history`** via `ALTER TABLE ADD COLUMN`:
   - `open_issues_count INTEGER DEFAULT 0`
   - `change_open_issues_delta INTEGER DEFAULT 0`
   - `source_api TEXT DEFAULT 'github_rest_api_v3'`
   - `collection_run_id TEXT`
3. **Create `github_repository_associations`**:
   - `association_id TEXT PRIMARY KEY`
   - `source_entity_type TEXT NOT NULL` ('research_paper', 'product', 'startup')
   - `source_entity_id TEXT NOT NULL`
   - `repo_id TEXT NOT NULL`
   - `evidence_url TEXT`
   - `evidence_type TEXT NOT NULL` ('CANONICAL_FIELD', 'ABSTRACT_MENTION', 'DEVELOPER_PROFILE', 'HOMEPAGE_LINK')
   - `confidence TEXT NOT NULL` ('HIGH', 'MEDIUM', 'LOW', 'UNVERIFIED')
   - `discovery_timestamp TEXT NOT NULL`
   - `verification_status TEXT NOT NULL` ('VERIFIED', 'UNVERIFIED', 'REJECTED')
   - Foreign key to `github_repositories(repo_id)`
   - Indexes on `source_entity_id`, `repo_id`, and `verification_status`.

---

## 5. Security, Rate Limit, and Boundaries

1. **Authentication Policy**:
   - Default: Public unauthenticated requests (60 requests/hour limit).
   - Optional: Read-only Personal Access Token via `GITHUB_TOKEN` / `GH_TOKEN` environment variables (5,000 requests/hour).
   - Absolute Rule: Never print tokens or `Authorization` headers in logs, outputs, or reports.
2. **Rate Limit Management**:
   - Query `/rate_limit` before initiating collection batches.
   - Stop immediately if remaining quota is below safety threshold (min 5 requests remaining).
   - Automatically pause or back off when receiving HTTP 403 / 429 with `retry-after` or `x-ratelimit-reset`.
3. **System Boundaries**:
   - Read-only on candidate DB, canonical DB, audit19 DB, baseline DB.
   - No Google Sheets write operations.
   - No Windows Task Scheduler activation.
   - No GitHub write operations (stars, forks, issues, PRs, branches).

---

## 6. Implementation Stages & Verification Gates

1. **Stage 1 (Complete)**: Architecture inspection & assessment report (`reports/phase5_github/phase5_architecture_assessment.md`).
2. **Stage 2**: Database setup & schema migration (`core/github_migrations.py` -> `data/working/phase5_github_candidate.db`).
3. **Stage 3**: Enhanced GitHub REST API v3 client (`core/github_client.py`).
4. **Stage 4**: Repository discovery and evidence engine (`core/github_discovery.py`, `core/github_evidence.py`).
5. **Stage 5**: Historical metrics & daily delta engine (`core/github_metrics.py`, `core/github_deltas.py`).
6. **Stage 6**: Intelligence & analytics module (`core/github_analytics.py`).
7. **Stage 7**: Comprehensive test suite & live read-only verification (`tests/test_phase5_github.py`).
8. **Stage 8**: Manual execution CLI with confirmation controls (`scripts/run_github_collection.py`).
9. **Stage 9**: Reporting, hash verification, and stopping point.

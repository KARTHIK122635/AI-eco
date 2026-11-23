# Investigation E: Migration & Database Schema Safety Audit Report

## 1. Executive Summary

This audit evaluated the migration engine (`core/github_migrations.py`), the original candidate database schema (`data/working/candidate_rolling_ai_ecosystem.db`), and the Phase V database schema (`data/working/phase5_github_candidate.db`).

A non-destructive test was conducted using an isolated, disposable database copy in a temporary directory to verify schema safety, repeatability, and idempotency.

---

## 2. Schema Alterations Verification

### 2.1 Table: `github_repositories` (11 Added Columns)
Verified that exactly 11 columns were added via non-destructive `ALTER TABLE` statements:

| Column Name | Data Type | Nullable | Default | Audit Verification |
|---|---|:---:|---|:---:|
| `full_name` | `TEXT` | YES | `None` | **CONFIRMED** |
| `primary_language` | `TEXT` | YES | `None` | **CONFIRMED** |
| `topics` | `TEXT` | YES | `None` | **CONFIRMED** (JSON list string) |
| `latest_open_issues`| `INTEGER`| YES | `0` | **CONFIRMED** |
| `created_timestamp`| `TEXT` | YES | `None` | **CONFIRMED** |
| `updated_timestamp`| `TEXT` | YES | `None` | **CONFIRMED** |
| `pushed_timestamp` | `TEXT` | YES | `None` | **CONFIRMED** |
| `default_branch` | `TEXT` | YES | `None` | **CONFIRMED** |
| `is_fork` | `INTEGER` | YES | `0` | **CONFIRMED** |
| `license_spdx_id` | `TEXT` | YES | `None` | **CONFIRMED** |
| `collection_run_id`| `TEXT` | YES | `None` | **CONFIRMED** |

Total columns after migration: **22 columns** (11 original + 11 added).

### 2.2 Table: `github_metrics_history` (4 Added Columns)
Verified that exactly 4 tracking columns were added:

| Column Name | Data Type | Nullable | Default | Audit Verification |
|---|---|:---:|---|:---:|
| `open_issues_count` | `INTEGER` | YES | `0` | **CONFIRMED** |
| `change_open_issues_delta`| `INTEGER` | YES | `0` | **CONFIRMED** |
| `source_api` | `TEXT` | YES | `'github_rest_api_v3'` | **CONFIRMED** |
| `collection_run_id` | `TEXT` | YES | `None` | **CONFIRMED** |

Total columns after migration: **13 columns** (9 original + 4 added).

### 2.3 New Table: `github_repository_associations` (10 Columns)
Created with the following definition:
- `association_id TEXT PRIMARY KEY`
- `source_entity_type TEXT NOT NULL`
- `source_entity_id TEXT NOT NULL`
- `repo_id TEXT NOT NULL`
- `evidence_url TEXT`
- `evidence_type TEXT NOT NULL`
- `confidence TEXT NOT NULL`
- `discovery_timestamp TEXT NOT NULL`
- `verification_status TEXT NOT NULL`
- `notes TEXT`
- `FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)`

Indexes created:
1. `idx_assoc_repo ON github_repository_associations(repo_id)`
2. `idx_assoc_source ON github_repository_associations(source_entity_id, source_entity_type)`
3. `idx_assoc_status ON github_repository_associations(verification_status)`
4. `idx_assoc_unique UNIQUE ON github_repository_associations(source_entity_type, source_entity_id, repo_id)`

---

## 3. Disposable Database Migration Repeatability Test

A clean-room test was executed on an ephemeral database copy:
1. **Source Replication**: Bit-for-bit clone of `candidate_rolling_ai_ecosystem.db` created in a temporary directory.
2. **Pass 1 Execution**:
   - `apply_phase5_migrations()` applied 16 structural adjustments.
   - Seeded 190 canonical paper associations.
   - Preserved all 190 original `github_repositories` rows.
   - PRAGMA integrity_check: `ok`.
3. **Pass 2 Execution (Idempotency Check)**:
   - `apply_phase5_migrations()` re-executed immediately on the migrated database.
   - Did NOT attempt to re-add existing columns (guarded by `PRAGMA table_info` checks).
   - Did NOT duplicate seeded associations (guarded by `INSERT OR IGNORE`).
   - Succeeded with exit status `MIGRATED`.
   - PRAGMA integrity_check: `ok`.
4. **Cleanup**: Ephemeral database deleted safely without touching workspace assets.

---

## 4. Architectural Observations & Identified Risks

1. **Lack of Migration Version Table**:
   - The project currently relies on inspection of `PRAGMA table_info` rather than a dedicated `schema_migrations` or `alembic_version` table. While safe for non-destructive additions, standard engineering practices recommend tracking migration version numbers and execution timestamps.
2. **SQLite Foreign Key Enforcement**:
   - In SQLite, foreign key enforcement is disabled by default (`PRAGMA foreign_keys = 0`). While the foreign key clause is defined on `github_repository_associations(repo_id)`, child-to-parent integrity is only enforced when connections explicitly execute `PRAGMA foreign_keys = ON;`.
3. **Primary Key Stability**:
   - `repo_id` serves as a natural primary key (`owner/repo`). As demonstrated during Phase V live testing with `PDFMathTranslate`, repository renames on GitHub require updating both `github_repositories.repo_id` and `github_repository_associations.repo_id`. The application handled this correctly in `core/github_metrics.py`.

---

## 5. Audit Status & Severity

- **Audit Status**: **`PASS`** (Migrations are safe, non-destructive, and idempotent).
- **Severity**: **`INFORMATIONAL`** (Foreign key pragma and migration version table recommendations are forward-looking architectural enhancements).

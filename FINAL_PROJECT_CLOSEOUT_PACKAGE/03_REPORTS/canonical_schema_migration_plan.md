# Proposed Canonical Schema Migration Plan
**Status: NOT EXECUTED — PENDING HUMAN AUTHORIZATION**
**Phase II — Stage 3: LLM Data Enrichment & Canonical Schema Governance**
**Document Reference: AUDIT-27-MIGRATION-PLAN**
**Date: 2026-11-22**
**Author: Senior Database Administrator & Systems Architect**

---

> [!CAUTION]
> **STRICT EXECUTION BOUNDARY**: This migration plan is an architectural proposal only.
> In strict compliance with Audit 27 directives, **NO DDL STATEMENTS HAVE BEEN EXECUTED** against `data/normalized/ai_ecosystem.db`.
> The canonical SQLite database remains completely unmodified at SHA-256:
> `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`.

---

## 1. Migration Purpose & Scope

The current canonical SQLite schema was designed during Phase I and Phase II (Audits 1–19) to store normalized data from scraping and API acquisition. Stage 3 enrichment introduced conceptual attributes (`ai_specialization`, `technologies`, `methodology`, `key_contributions`, `research_domain`) that lack physical storage columns in the database.

This migration plan defines the exact DDL commands, storage representations, impact analysis, rollback procedures, and verification scripts required to support these fields whenever human authorization is granted.

---

## 2. Proposed DDL Specification

The following six (6) `ALTER TABLE` statements would add the required columns without altering or rewriting existing table data:

```sql
-- 1. Support startup AI specialization taxonomy
ALTER TABLE ai_startups ADD COLUMN ai_specialization TEXT;

-- 2. Support startup technologies extracted from public profiles
ALTER TABLE ai_startups ADD COLUMN technologies TEXT;

-- 3. Support research paper methodology extraction
ALTER TABLE ai_research_papers ADD COLUMN methodology TEXT;

-- 4. Support research paper key contributions list
ALTER TABLE ai_research_papers ADD COLUMN key_contributions TEXT;

-- 5. Support research paper high-level research domain taxonomy
ALTER TABLE ai_research_papers ADD COLUMN research_domain TEXT;

-- 6. Support AI job technologies and tools list
ALTER TABLE ai_jobs ADD COLUMN technologies TEXT;
```

---

## 3. Storage & Serialization Rules

| Target Table | Target Column | Physical Type | Default Value | Format / Serialization | Validation Constraint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ai_startups` | `ai_specialization` | `TEXT` | `NULL` | Scalar string | Must match `APPROVED_TAXONOMY["startup"]["ai_specialization"]` |
| `ai_startups` | `technologies` | `TEXT` | `NULL` | JSON array of strings (`["PyTorch", "CUDA"]`) | Valid JSON parseable array; no duplicates |
| `ai_research_papers` | `methodology` | `TEXT` | `NULL` | Scalar string | Verbatim-grounded excerpt or summary |
| `ai_research_papers` | `key_contributions` | `TEXT` | `NULL` | JSON array of strings | Valid JSON parseable array |
| `ai_research_papers` | `research_domain` | `TEXT` | `NULL` | Scalar string | Must match `APPROVED_TAXONOMY["paper"]["research_domain"]` |
| `ai_jobs` | `technologies` | `TEXT` | `NULL` | JSON array of strings (`["Python", "BigQuery"]`) | Valid JSON parseable array; no duplicates |

---

## 4. Impact Analysis

### 4.1 Data Integrity & Concurrency Impact
- **Existing Rows**: All 6,745 existing canonical records remain 100% intact. SQLite appends new column definitions to table metadata; existing data rows are not rewritten. The new columns evaluate to `NULL` for all existing records.
- **Query Compatibility**: All existing `SELECT *` and explicit column queries remain compatible. Existing application code reading named columns will experience zero regressions.
- **Physical File Size**: The initial physical size increase is negligible (< 4 KB to update table schema definitions in `sqlite_master`). New records or updated rows will store column values efficiently using SQLite's variable-length header format.

### 4.2 Historical Baseline Preservation
- The authentic Audit 19 database (`source/audit19_original_database.db`, SHA-256 `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`) and historical backup tables (`enrichment_audit_log_backup_*`) will NOT be touched by this migration. They remain independent historical snapshots.

---

## 5. Pre-Migration Checklist & Rollback Plan

When authorization is provided to execute this migration in a future stage:

### Step 1: Immutable Pre-Migration Backup
```bash
python -c "
import shutil, datetime
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copyfile('data/normalized/ai_ecosystem.db', f'data/normalized/ai_ecosystem_pre_migration_{ts}.db')
print(f'Backup created: data/normalized/ai_ecosystem_pre_migration_{ts}.db')
"
```

### Step 2: Atomic Execution within Transaction
```python
import sqlite3

def execute_migration(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    statements = [
        "ALTER TABLE ai_startups ADD COLUMN ai_specialization TEXT;",
        "ALTER TABLE ai_startups ADD COLUMN technologies TEXT;",
        "ALTER TABLE ai_research_papers ADD COLUMN methodology TEXT;",
        "ALTER TABLE ai_research_papers ADD COLUMN key_contributions TEXT;",
        "ALTER TABLE ai_research_papers ADD COLUMN research_domain TEXT;",
        "ALTER TABLE ai_jobs ADD COLUMN technologies TEXT;",
    ]
    try:
        conn.execute("BEGIN IMMEDIATE TRANSACTION;")
        for stmt in statements:
            cursor.execute(stmt)
        conn.commit()
        print("Migration executed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed and rolled back: {e}")
        raise
    finally:
        conn.close()
```

### Step 3: Rollback Procedures
- **Fast Rollback**: Restore from `ai_ecosystem_pre_migration_<timestamp>.db`.
- **SQL Drop Column Rollback** (SQLite >= 3.35.0):
  ```sql
  ALTER TABLE ai_startups DROP COLUMN ai_specialization;
  ALTER TABLE ai_startups DROP COLUMN technologies;
  ALTER TABLE ai_research_papers DROP COLUMN methodology;
  ALTER TABLE ai_research_papers DROP COLUMN key_contributions;
  ALTER TABLE ai_research_papers DROP COLUMN research_domain;
  ALTER TABLE ai_jobs DROP COLUMN technologies;
  ```

---

## 6. Current Audit 27 Status

- **Status**: PENDING AUTHORIZATION
- **Action Taken in Audit 27**: Zero DDL commands executed. Write protection enforced in code.
- **Canonical Database SHA-256**: `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d` (strictly identical to Audit 26 baseline).

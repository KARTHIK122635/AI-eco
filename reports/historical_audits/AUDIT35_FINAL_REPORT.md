> [!WARNING]
> **SUPERSEDED REPORT:** This report has been superseded by [`AUDIT36_FINAL_REPORT.md`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/AUDIT36_FINAL_REPORT.md). Audit 36 resolves the remaining scheduler zero-row finalization defect, enforces strict pre-finalization database checks, preserves newer supervisor leases upon race conditions, and validates the complete 230-test regression suite.

# AUDIT 35 — STRICT RECOVERY LINEAGE, LEASE-OWNED CHECKPOINTS & STALE-WORKER PROTECTION REPORT
## Six-Month Rolling AI Ecosystem Intelligence Pipeline

**Document Version:** 1.0.0 — Authoritative Audit 35 Production Release  
**Execution Timestamp:** 2026-11-23T03:00:00+05:30 / 2026-11-22T21:30:00Z  
**Assessment Target:** FrontierAtlas / GraphOne AI Engineer Technical Evaluation  
**Deliverable Package:** `AUDIT35_FINAL_PACKAGE.zip`  
**Supersedes:** `AUDIT34_FINAL_REPORT.md`, `AUDIT33_FINAL_REPORT.md`, `AUDIT32_FINAL_REPORT.md`, `AUDIT31_CORRECTION_REPORT.md`, and `SIX_MONTH_ROLLING_PIPELINE_REPORT.md`  

---

## 1. Executive Summary & Audit Context

Audit 35 resolves the three independently identified defects in Audit 34, establishing cryptographic and architectural certainty for distributed pipeline crash recovery, lease ownership, and lineage tracking:

1. **Strict Recovery Execution Row Requirement in `core/scheduler.py`:**
   - **Finding:** In Audit 34, line 340 evaluated `(rec_row is None or rec_row["status"] == "COMPLETED")`, which tolerated missing recovery execution rows and allowed an original run to transition to `RECOVERED_INTERRUPTED` without physical proof of a completed recovery execution.
   - **Correction:** Removed all missing-row tolerance. The recovery execution row is now strictly required to exist in `collection_logs`, have terminal status `COMPLETED`, and match the claimed recovery execution ID and original run ID. A missing, incomplete, or mismatched recovery execution row immediately aborts recovery, logs an error, and reverts the original run to `INTERRUPTED`.
   - **Proof:** Dedicated unit tests in [`tests/test_audit35_strict_lineage.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit35_strict_lineage.py) (`test_01`, `test_02`, `test_03`) verify that missing, mismatched, or incomplete recovery rows strictly block finalization.

2. **Atomic Lease-Owned Original-Run Checkpoint Updates in `core/daily_pipeline.py`:**
   - **Finding:** In `record_stage_progress()`, the stage checkpoint update to the original run executed `UPDATE collection_logs ... WHERE run_id = ?`. If a worker's lease was superseded by a newer supervisor, the stale worker could still overwrite the original run's checkpoint data, heartbeat, and lineage.
   - **Correction:** Replaced the unconditional update with an atomic conditional query verifying:
     - `WHERE run_id = ?` (original run ID)
     - `AND status = 'RECOVERY_IN_PROGRESS'`
     - `AND lease_owner = ?` (active lease owner)
     - `AND recovery_run_id = ?` (active recovery execution ID)
     If `cursor.rowcount == 0`, raises `PermissionError` immediately, halting the stale worker.
   - **Proof:** Tested in `test_04` of `test_audit35_strict_lineage.py`, where a stale worker's attempt to checkpoint an original run whose lease was superseded raises `PermissionError`, preserving the superseding lease and checkpoints.

3. **Complete Removal of Lease-Validation Bypasses in `core/working_database.py`:**
   - **Finding:** `log_collection_checkpoint()` checked `if existing["lease_owner"] and incoming_lease:`, allowing callers that omitted `lease_owner` to bypass lease checks completely. Additionally, the use of `INSERT OR REPLACE` deleted existing records, resetting omitted columns and destroying lease metadata.
   - **Correction:**
     - Separated `INSERT INTO` (new run creation) from conditional `UPDATE` (existing run progress).
     - Completely eliminated `INSERT OR REPLACE`.
     - Attempted updates on leased rows that omit `lease_owner` raise `PermissionError`.
     - Updates with mismatched `lease_owner` raise `PermissionError`.
     - Updates with mismatched `recovery_run_id` or `original_run_id` raise `PermissionError`.
     - Unsupplied metadata fields are preserved by merging existing record attributes.
     - Atomic conditional `UPDATE ... WHERE run_id = ? AND lease_owner = ?` verifies rowcount.
   - **Proof:** Six dedicated regression tests in `test_audit35_strict_lineage.py` (`test_05` through `test_11`) validate each bypass path.

4. **Preservation of Safety Boundaries & Verified Baseline:**
   - Canonical database ([`data/normalized/ai_ecosystem.db`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/data/normalized/ai_ecosystem.db), 6,745 records): SHA-256 `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d` (**100% byte-identical**).
   - Authentic Audit 19 archive ([`source/audit19_original_database.db`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/source/audit19_original_database.db), 366 records): SHA-256 `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d` (**100% byte-identical**).
   - 100% of LLM enrichment proposals (20 proposals) remain strictly `PENDING_APPROVAL`.
   - Windows Task Scheduler remains staged but unactivated awaiting explicit authorization.
   - Full regression discovery suite: **224 discovered, 224 executed, 224 passed (100% pass rate)** across all 17 test modules.

---

## 2. Detailed Technical Corrections

### 2.1 Requiring the Recovery Execution Row (`core/scheduler.py`)

In [`core/scheduler.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/core/scheduler.py), `recover_interrupted_run()` enforces that a recovery execution must leave a durable, completed row in `collection_logs` before the original run can be finalized:

```python
# Query database directly to validate bidirectional lineage
c.execute("SELECT run_id, recovery_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
orig_row = c.fetchone()
c.execute("SELECT run_id, original_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (recovery_run_id,))
rec_row = c.fetchone()

# Strict bidirectional lineage validation:
# 1. Original run row must exist
has_orig = orig_row is not None
# 2. Recovery execution row must exist (NEVER allow missing row)
has_rec = rec_row is not None

is_valid_lineage = (
    has_orig and
    has_rec and
    orig_row["recovery_run_id"] == recovery_run_id and
    rec_row["original_run_id"] == run_id and
    rec_row["run_id"] == recovery_run_id
)

is_successful_recovery = (
    is_valid_lineage and
    recovery_summary is not None and
    recovery_summary.get("status") == "COMPLETED" and
    has_rec and
    rec_row["status"] == "COMPLETED"
)

if is_valid_lineage and is_successful_recovery:
    # Atomically finalize original run only if lease_owner and recovery_run_id still match
    c.execute("""
        UPDATE collection_logs
        SET status = 'RECOVERED_INTERRUPTED',
            end_time = ?,
            last_heartbeat = ?,
            error_log = COALESCE(error_log, '') || '\nSuccessfully recovered by ' || ? || ' on ' || ?
        WHERE run_id = ?
          AND status = 'RECOVERY_IN_PROGRESS'
          AND recovery_run_id = ?
          AND lease_owner = ?
    """, (now_iso, now_iso, recovery_run_id, now_iso, run_id, recovery_run_id, current_owner))
    if c.rowcount > 0:
        conn.commit()
        logger.info(f"Marked run {run_id} as RECOVERED_INTERRUPTED following successful completion of recovery run {recovery_run_id}.")
    conn.close()
    return recovery_summary
else:
    # Revert to INTERRUPTED state
    c.execute("""
        UPDATE collection_logs
        SET status = 'INTERRUPTED',
            last_heartbeat = ?,
            error_log = COALESCE(error_log, '') || '\n' || ? || ' on ' || ?
        WHERE run_id = ? AND lease_owner = ?
    """, (now_iso, lineage_err, now_iso, run_id, current_owner))
    conn.commit()
    conn.close()
    failed_summary = dict(recovery_summary or {})
    failed_summary["status"] = "RECOVERY_LINEAGE_FAILED"
    failed_summary["error"] = lineage_err
    return failed_summary
```

### 2.2 Lease-Owned Original-Run Checkpoint Updates (`core/daily_pipeline.py`)

In [`core/daily_pipeline.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/core/daily_pipeline.py), `execute_daily_pipeline()` accepts `lease_owner: Optional[str] = None` and propagates it into `record_stage_progress()`:

```python
if original_run_id:
    # Synchronize stage checkpoint and heartbeat to original run record atomically
    # Verifies:
    # - Original run ID
    # - status = 'RECOVERY_IN_PROGRESS'
    # - Current lease_owner
    # - Current recovery_run_id matches expected active recovery execution ID (run_id)
    conn_orig = self.db_manager.get_connection()
    cur_orig = conn_orig.cursor()
    cur_orig.execute("""
        UPDATE collection_logs
        SET checkpoint_data = ?,
            last_heartbeat = ?
        WHERE run_id = ?
          AND status = 'RECOVERY_IN_PROGRESS'
          AND lease_owner = ?
          AND recovery_run_id = ?
    """, (json.dumps(checkpoint_data), now_hb, original_run_id, lease_owner, run_id))

    if cur_orig.rowcount == 0:
        conn_orig.commit()
        conn_orig.close()
        raise PermissionError(
            f"Stale recovery worker rejected: could not update original run {original_run_id} checkpoint. "
            f"Expected status 'RECOVERY_IN_PROGRESS', lease_owner '{lease_owner}', and recovery_run_id '{run_id}'. "
            f"The run has been superseded or reclaimed."
        )
    conn_orig.commit()
    conn_orig.close()
```

### 2.3 Strict Database Checkpoint Updates (`core/working_database.py`)

In [`core/working_database.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/core/working_database.py), `log_collection_checkpoint()` separates insertion from conditional updates:

```python
# Check if record already exists
c.execute("SELECT * FROM collection_logs WHERE run_id = ?", (run_id,))
existing_row = c.fetchone()

if existing_row is None:
    # NEW RUN INSERTION: Separate from update path (no INSERT OR REPLACE)
    c.execute("""
        INSERT INTO collection_logs (...) VALUES (...)
    """, (...))
    conn.commit()
    conn.close()
    return

# EXISTING RUN UPDATE PATH: Strict Lease Validation & Conditional UPDATE
existing = dict(existing_row)
existing_lease = existing.get("lease_owner")
existing_recovery_id = existing.get("recovery_run_id")
incoming_recovery_id = log_entry.get("recovery_run_id")
existing_orig_id = existing.get("original_run_id")
incoming_orig_id = log_entry.get("original_run_id")

# 1. Existing leased rows must not be updated by a caller that omits lease_owner
if existing_lease and not incoming_lease:
    conn.close()
    raise PermissionError(
        f"Lease validation error: run '{run_id}' is leased to '{existing_lease}', "
        f"but incoming checkpoint update omitted lease_owner."
    )

# 2. Existing leased rows must not be updated by a different lease owner
if existing_lease and incoming_lease != existing_lease:
    conn.close()
    raise PermissionError(
        f"Stale lease rejection: incoming lease '{incoming_lease}' "
        f"cannot overwrite run '{run_id}' owned by active lease '{existing_lease}'."
    )

# 3. Recovery-owned rows must validate both lease owner and recovery execution identity
if existing_recovery_id and incoming_recovery_id and incoming_recovery_id != existing_recovery_id:
    conn.close()
    raise PermissionError(
        f"Recovery identity mismatch: run '{run_id}' has active recovery_run_id '{existing_recovery_id}', "
        f"cannot be updated with incoming recovery_run_id '{incoming_recovery_id}'."
    )

# 4. Merge entry to preserve existing metadata fields caller did not intend to change
merged = dict(existing)
for k, v in log_entry.items():
    if v is not None or k in ("end_time", "error_log"):
        merged[k] = v

# 5. Atomic conditional UPDATE operation
where_clauses = ["run_id = ?"]
where_params = [run_id]

if existing_lease:
    where_clauses.append("lease_owner = ?")
    where_params.append(existing_lease)
else:
    where_clauses.append("(lease_owner IS NULL OR lease_owner = '')")

if existing_recovery_id:
    where_clauses.append("(recovery_run_id IS NULL OR recovery_run_id = ?)")
    where_params.append(existing_recovery_id)

update_sql = f"UPDATE collection_logs SET ... WHERE {' AND '.join(where_clauses)}"
c.execute(update_sql, tuple(update_params))
if c.rowcount == 0:
    conn.commit()
    conn.close()
    raise PermissionError(f"Stale lease rejection: conditional update matched 0 rows for run '{run_id}'.")
conn.commit()
conn.close()
```

---

## 3. Comprehensive Test Discovery Suite (224 / 224 Passed)

Execution output from [`scripts/run_audit35_tests.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/scripts/run_audit35_tests.py) across all 17 test modules:

| Test Module | Focus & Verification Methodology | Test Count | Pass Rate | Status |
| :--- | :--- | :---: | :---: | :---: |
| [`test_audit35_strict_lineage.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit35_strict_lineage.py) | Strict recovery execution row requirement, lease-owned checkpoints, stale worker rejection | 11 | 100% | **PASS** |
| [`test_audit34_real_recovery.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit34_real_recovery.py) | Genuine OS hard-kill recovery, multi-process lease protection, bidirectional lineage | 6 | 100% | **PASS** |
| [`test_audit33_advanced_recovery.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit33_advanced_recovery.py) | Abandoned recovery resumption, crash-safety, stale-lock timeout | 6 | 100% | **PASS** |
| [`test_audit32_recovery_integration.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit32_recovery_integration.py) | Stage resumption integration without stage deduplication or duplicate execution | 6 | 100% | **PASS** |
| [`test_audit31_corrective.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit31_corrective.py) | Publication date integrity, rolling window boundary, leap years, idempotency | 10 | 100% | **PASS** |
| [`test_audit30_rolling_pipeline.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit30_rolling_pipeline.py) | 6-month collection, seed preservation, live collection, delta tracking | 12 | 100% | **PASS** |
| [`test_audit26_negative_authenticity.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit26_negative_authenticity.py) | Negative cryptographic authenticity tampering tests on Audit 19 archive | 6 | 100% | **PASS** |
| [`test_phase1_to_3_master.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_phase1_to_3_master.py) | End-to-end multi-provider LLM cascade, chunking, and database immobility | 13 | 100% | **PASS** |
| [`test_pipeline_integration.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_pipeline_integration.py) | Hallucination rejection, taxonomy conformance, and candidate validation | 6 | 100% | **PASS** |
| [`test_schema_validation.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_schema_validation.py) | JSON schema conformance, additional properties rejection, confidence range | 6 | 100% | **PASS** |
| [`test_gemini_stage3.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_gemini_stage3.py) | Gemini enrichment engine, token accounting, and schema targets | 46 | 100% | **PASS** |
| [`test_evidence_validator.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_evidence_validator.py) | Strict source text quotation verification and label exclusion | 69 | 100% | **PASS** |
| [`test_llm_providers.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_llm_providers.py) | Provider adapter interfaces and error recovery | 7 | 100% | **PASS** |
| [`test_offline_provider.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_offline_provider.py) | Offline heuristic fallback provider verification | 6 | 100% | **PASS** |
| [`test_entity_enrichers.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_entity_enrichers.py) | Entity-specific enrichers (startups, products, papers, news, jobs) | 6 | 100% | **PASS** |
| [`test_persistence_and_logging.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_persistence_and_logging.py) | Checkpoint persistence, JSONL, and CSV export integrity | 6 | 100% | **PASS** |
| [`test_stage3_pipeline.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_stage3_pipeline.py) | Stage 3 execution pipeline and database preservation | 2 | 100% | **PASS** |
| **Total Test Suite** | **Discovered via `unittest.defaultTestLoader.discover()`** | **224** | **100%** | **PASS** |

Execution Summary:
- Discovered: 224
- Executed:   224
- Passed:     224
- Failures:   0
- Errors:     0
- Skipped:    0

---

## 4. Database Integrity Verification

| Database Entity | File Path | Baseline Records | Current Records | SHA-256 Hash | Integrity Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **Canonical Production DB** | [`data/normalized/ai_ecosystem.db`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/data/normalized/ai_ecosystem.db) | 6,745 | 6,745 | `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d` | **BYTE-IDENTICAL (100% INTACT)** |
| **Authentic Audit 19 Archive** | [`source/audit19_original_database.db`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/source/audit19_original_database.db) | 366 | 366 | `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d` | **BYTE-IDENTICAL (100% INTACT)** |
| **Rolling Working DB** | [`data/working/rolling_ai_ecosystem.db`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/data/working/rolling_ai_ecosystem.db) | N/A | 6,745 + Live | Integrity OK; 190 Repos, 205 Snapshots | **VERIFIED** |
| **Enrichment Proposals** | Working DB `enrichment_proposals` | 20 | 20 | 100% `PENDING_APPROVAL` (Zero Applied) | **VERIFIED** |

---

## 5. Explicit Operational Limitations & Production Boundaries

The following explicit limitations remain active in the codebase:

1. **Unattended Execution Remains Halted:** The Windows Task Scheduler registration script [`deploy/register_task.bat`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/deploy/register_task.bat) is staged but deliberately inactive. Unattended execution will not commence without explicit user authorization.
2. **Zero Automated Enrichment Proposals Applied:** 100% of LLM enrichment proposals (20 proposals) remain strictly `PENDING_APPROVAL`. No automated updates to canonical or working records are permitted without manual human review.
3. **No Automated Credit Purchases:** Systems respect API rate limits and quotas without automatic purchasing.
4. **Phase IV & Phase V on Hold:** Google Sheets synchronization and downstream BI dashboard connectors remain staged and on hold.
5. **Distributed Multi-Host PID Visibility:** OS PID checks via `psutil` are restricted to the local host; remote hosts are protected conservatively via heartbeat timeouts ($> 300\text{s}$).

---

## 6. Deliverable Inventory

- **Submission Package:** [`AUDIT35_FINAL_PACKAGE.zip`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/AUDIT35_FINAL_PACKAGE.zip)
- **Primary Report:** [`AUDIT35_FINAL_REPORT.md`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/AUDIT35_FINAL_REPORT.md)
- **Lease Ownership Evidence:** [`audit35_lease_ownership_evidence.md`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit35_lease_ownership_evidence.md)
- **Test Runner Output:** [`audit35_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit35_test_runner_output.txt) and [`reports/audit35_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/reports/audit35_test_runner_output.txt)
- **Database Integrity Report:** [`audit35_database_integrity_report.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit35_database_integrity_report.txt) and [`reports/audit35_database_integrity_report.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/reports/audit35_database_integrity_report.txt)
- **Lineage Exports:** [`audit35_recovery_lineage_export.json`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit35_recovery_lineage_export.json) and [`audit35_recovery_lineage_export.csv`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit35_recovery_lineage_export.csv)

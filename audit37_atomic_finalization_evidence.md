# AUDIT 37 — ATOMIC BIDIRECTIONAL RECOVERY FINALIZATION EVIDENCE

**Document Version:** 1.0.0 — Authoritative Production Release  
**Execution Timestamp:** 2026-11-23T03:50:00+05:30 / 2026-11-22T22:20:00Z  
**Assessment Target:** FrontierAtlas / GraphOne AI Engineer Technical Evaluation  
**Deliverable Package:** `AUDIT37_FINAL_PACKAGE.zip`  
**Companion Artifacts:** [`audit37_database_integrity_report.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit37_database_integrity_report.txt), [`audit37_recovery_lineage_export.json`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit37_recovery_lineage_export.json), [`audit37_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit37_test_runner_output.txt)

---

## 1. Executive Summary & Problem Resolution

Audit 37 closes the remaining concurrency gap identified in Audit 36:

### 1.1 The Vulnerability in Audit 36
In Audit 36, `recover_interrupted_run()` performed preliminary verification by executing `SELECT` queries against `collection_logs` for `orig_row` and `rec_row`, followed by an `UPDATE` on `collection_logs` for `orig_row`.
Although the finalization query verified `orig_row.lease_owner == current_owner` and `orig_row.status == 'RECOVERY_IN_PROGRESS'`, it did not atomically check the state of the recovery execution row at the exact moment of finalization.
If a race occurred between the preliminary `SELECT` and the finalization `UPDATE`—such as the recovery row being deleted, its status modified to `FAILED`, its pointer changed, or its lease reassigned—the original run could theoretically transition while the recovery row was no longer in a valid completed state.

### 1.2 The Audit 37 Atomic Bidirectional Solution
In Audit 37, the finalization update is made **strictly atomic with respect to BOTH original and recovery execution records** using a conditional SQL statement with an `EXISTS` subquery.

```sql
UPDATE collection_logs
SET status = 'RECOVERED_INTERRUPTED',
    end_time = ?,
    last_heartbeat = ?,
    error_log = COALESCE(error_log, '') || '\nSuccessfully recovered by ' || ? || ' on ' || ?
WHERE run_id = ?
  AND status = 'RECOVERY_IN_PROGRESS'
  AND recovery_run_id = ?
  AND lease_owner = ?
  AND EXISTS (
      SELECT 1 FROM collection_logs
      WHERE run_id = ?
        AND original_run_id = ?
        AND status = 'COMPLETED'
        AND lease_owner = ?
  )
```

### 1.3 The 9 Bidirectional Requirements Verified in a Single Statement:
1. Original run exists (`WHERE run_id = ?`).
2. Original run status is `RECOVERY_IN_PROGRESS` (`AND status = 'RECOVERY_IN_PROGRESS'`).
3. Original run `recovery_run_id` equals the claimed recovery execution ID (`AND recovery_run_id = ?`).
4. Original run `lease_owner` equals the current recovery owner (`AND lease_owner = ?`).
5. Recovery execution row exists (`AND EXISTS (SELECT 1 FROM collection_logs WHERE run_id = ? ...)`).
6. Recovery execution row `run_id` equals the claimed recovery execution ID (`WHERE run_id = ?`).
7. Recovery execution row `original_run_id` equals the original run ID (`AND original_run_id = ?`).
8. Recovery execution row status is `COMPLETED` (`AND status = 'COMPLETED'`).
9. Recovery execution row `lease_owner` equals the current recovery owner (`AND lease_owner = ?`).

If **any** of these 9 conditions fail at the exact moment of update, SQLite updates exactly **0 rows** (`c.rowcount == 0`).

---

## 2. Rowcount Verification & Post-Finalization Database Checks

```python
if c.rowcount == 1:
    conn.commit()
    # Audit 37: Verify BOTH persisted original and recovery records after finalization
    c.execute("SELECT status, recovery_run_id, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
    final_orig = c.fetchone()
    c.execute("SELECT status, original_run_id, lease_owner FROM collection_logs WHERE run_id = ?", (recovery_run_id,))
    final_rec = c.fetchone()

    orig_ok = (
        final_orig is not None and
        final_orig["status"] == "RECOVERED_INTERRUPTED" and
        final_orig["recovery_run_id"] == recovery_run_id
    )
    rec_ok = (
        final_rec is not None and
        final_rec["status"] == "COMPLETED" and
        final_rec["original_run_id"] == run_id and
        final_rec["lease_owner"] == current_owner
    )

    if orig_ok and rec_ok:
        logger.info(f"Marked run {run_id} as RECOVERED_INTERRUPTED following successful completion of recovery run {recovery_run_id}.")
        conn.close()
        success_summary = dict(recovery_summary or {})
        success_summary["status"] = "COMPLETED"
        success_summary["run_id"] = recovery_run_id
        success_summary["original_run_id"] = run_id
        return success_summary
```

### Protection of Newer Supervisors on Zero-Row Result:
If `c.rowcount == 0`:
- The scheduler commits the transaction to release locks.
- Queries live SQLite state to diagnose the exact cause.
- Reverts the original run to `INTERRUPTED` **only if** `diag_orig["lease_owner"] == current_owner`.
- If another supervisor took over the lease (`diag_orig["lease_owner"] != current_owner`), the scheduler **never** touches, overwrites, or reverts the newer supervisor's claim.
- Returns explicit `RECOVERY_FINALIZATION_FAILED` with detailed diagnostic logging. It is impossible to return `COMPLETED`.

---

## 3. Concurrency Test Matrix ([`tests/test_audit37_concurrency.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit37_concurrency.py))

| Test Case | Scenario Verified | Injection Technique | Expected Outcome | Verified Result |
|:---|:---|:---|:---|:---:|
| `test_01_recovery_row_status_change_blocks_finalization` | Recovery row changes status after preliminary check | Dynamic SQLite interceptor sets `status='FAILED'` on recovery row right before atomic UPDATE | Atomic UPDATE affects 0 rows; returns `RECOVERY_FINALIZATION_FAILED` | **PASS** |
| `test_02_recovery_row_lease_owner_change_blocks_finalization` | Recovery row lease_owner modified to unauthorized owner | Dynamic interceptor sets `lease_owner='rogue_host:999:unauth'` on recovery row | Atomic UPDATE affects 0 rows; returns `RECOVERY_FINALIZATION_FAILED` | **PASS** |
| `test_03_recovery_row_original_run_id_change_blocks_finalization` | Recovery row `original_run_id` pointer modified | Dynamic interceptor points recovery row to `unrelated_other_run_999` | Atomic UPDATE affects 0 rows; returns `RECOVERY_FINALIZATION_FAILED` | **PASS** |
| `test_04_original_run_lease_superseded_blocks_finalization` | Original run lease claimed by newer supervisor | Dynamic interceptor sets original run lease to `host_sup_z:7777:supervisor_z` | Atomic UPDATE affects 0 rows; newer supervisor lease untouched | **PASS** |
| `test_05_recovery_row_deleted_blocks_finalization` | Recovery execution row deleted from database | Dynamic interceptor deletes recovery row right before atomic UPDATE | `EXISTS` subquery evaluates False; affects 0 rows; returns failure | **PASS** |
| `test_06_both_records_valid_finalization_succeeds_with_post_verification` | Clean recovery run with no concurrency races | Clean execution of recovery pipeline with matching IDs and leases | Affects 1 row; post-verification verifies both records; returns `COMPLETED` | **PASS** |
| `test_07_no_newer_supervisor_state_overwritten` | Race during pipeline execution where newer supervisor claims run | Pipeline mock simulates superseding claim | Scheduler preserves newer supervisor's lease and state intact | **PASS** |
| `test_08_zero_row_finalization_never_returns_completed` | Intentional out-of-band state modification forcing rowcount=0 | Original run set to `CANCELLED` right before finalization | Explicitly confirms status is `RECOVERY_FINALIZATION_FAILED`, never `COMPLETED` | **PASS** |

All 8 tests pass with 100% reliability in under 0.25 seconds.

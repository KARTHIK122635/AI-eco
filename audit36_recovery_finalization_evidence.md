# AUDIT 36 — SCHEDULER FINALIZATION SAFETY & PRE-FINALIZATION EVIDENCE

**Document Version:** 1.0.0 — Authoritative Production Release  
**Execution Timestamp:** 2026-11-23T03:20:00+05:30 / 2026-11-22T21:50:00Z  
**Assessment Target:** FrontierAtlas / GraphOne AI Engineer Technical Evaluation  
**Companion Artifacts:** [`audit36_database_integrity_report.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_database_integrity_report.txt), [`audit36_recovery_lineage_export.json`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_recovery_lineage_export.json), [`audit36_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_test_runner_output.txt)

---

## 1. Executive Summary of Corrections

Audit 36 resolves the remaining scheduler recovery defect identified in Audit 35:

1. **Elimination of False-COMPLETED Recovery Return on Zero-Row Updates:**
   - **Defect in Audit 35:** In `core/scheduler.py` (`recover_interrupted_run()`), when the conditional `UPDATE` on the original run affected zero rows (e.g., due to concurrent lease supersession or state modification), the function still returned `recovery_summary` (which carried `status: COMPLETED`).
   - **Correction in Audit 36:** The return value is strictly gated by SQLite's execution rowcount (`c.rowcount`). If `c.rowcount == 0`, the scheduler returns an explicit `RECOVERY_FINALIZATION_FAILED` result dictionary. It is architecturally impossible to return `COMPLETED` when the original run was not finalized.

2. **Strict Verification of Final Database State:**
   - When `c.rowcount == 1`, the scheduler queries SQLite directly (`SELECT status, recovery_run_id FROM collection_logs WHERE run_id = ?`) to ensure that the row actually reached `RECOVERED_INTERRUPTED` before returning `COMPLETED`.

3. **Protection of Newer Supervisor Leases & State:**
   - When a race condition or concurrent lease supersession is detected (either during pre-finalization checks or during finalization `UPDATE`), the scheduler **never** touches, reverts, or overwrites the newer supervisor's lease or state.
   - If `orig_row["lease_owner"] != current_owner`, the scheduler preserves the row intact and logs a clear, sanitized explanation.

4. **Persisted Pre-Finalization Database Checks:**
   - Before executing the finalization `UPDATE`, the scheduler queries `collection_logs` directly to confirm:
     - The recovery execution row exists in the database.
     - `rec_row.run_id == recovery_run_id`.
     - `rec_row.original_run_id == orig_run_id`.
     - `rec_row.status == "COMPLETED"`.
     - `rec_row.lease_owner == current_owner`.
     - `orig_row` still has `status == "RECOVERY_IN_PROGRESS"`, `recovery_run_id == recovery_run_id`, and `lease_owner == current_owner`.

---

## 2. Technical Implementation in `core/scheduler.py`

### 2.1 Pre-Finalization SQLite Verification & Atomic Finalization

```python
# 5. Pre-Finalization Verification Based on Persisted Database State
conn = self.db_manager.get_connection()
c = conn.cursor()

# Query database directly to validate persisted state
c.execute("SELECT run_id, recovery_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
orig_row = c.fetchone()
c.execute("SELECT run_id, original_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (recovery_run_id,))
rec_row = c.fetchone()

has_orig = orig_row is not None
has_rec = rec_row is not None

rec_matches_claim = (
    has_rec and
    rec_row["run_id"] == recovery_run_id and
    rec_row["original_run_id"] == run_id and
    rec_row["status"] == "COMPLETED" and
    rec_row["lease_owner"] == current_owner
)

orig_still_claimed = (
    has_orig and
    orig_row["recovery_run_id"] == recovery_run_id and
    orig_row["status"] == "RECOVERY_IN_PROGRESS" and
    orig_row["lease_owner"] == current_owner
)

pipeline_summary_completed = (
    recovery_summary is not None and
    recovery_summary.get("status") == "COMPLETED"
)

is_verified = (
    rec_matches_claim and
    orig_still_claimed and
    pipeline_summary_completed
)

if is_verified:
    # Atomically finalize original run only if lease_owner, status, and recovery_run_id still match
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

    if c.rowcount == 1:
        conn.commit()
        # Audit 36: Verify final database state before reporting success
        c.execute("SELECT status, recovery_run_id FROM collection_logs WHERE run_id = ?", (run_id,))
        final_row = c.fetchone()
        conn.close()

        if final_row and final_row["status"] == "RECOVERED_INTERRUPTED":
            logger.info(f"Marked run {run_id} as RECOVERED_INTERRUPTED following successful completion of recovery run {recovery_run_id}.")
            return recovery_summary
        else:
            return {
                "run_id": run_id,
                "recovery_run_id": recovery_run_id,
                "status": "RECOVERY_FINALIZATION_FAILED",
                "error": f"Original run {run_id} status mismatch after update: expected 'RECOVERED_INTERRUPTED'"
            }
    else:
        # Audit 36: Affected 0 rows (concurrent supervisor claimed run or state changed)
        conn.commit()
        conn.close()
        err_msg = (
            f"Original run {run_id} finalization affected 0 rows. The original run's state or lease was "
            f"concurrently modified or superseded. Active lease '{current_owner}' no longer holds the claim."
        )
        logger.warning(err_msg)
        return {
            "run_id": run_id,
            "recovery_run_id": recovery_run_id,
            "status": "RECOVERY_FINALIZATION_FAILED",
            "error": err_msg,
            "sanitized_reason": "Concurrent lease modification or state change prevented finalization"
        }
```

### 2.2 Preservation of Newer Supervisor on Pre-Finalization Failure

```python
else:
    # Pre-finalization check failed: identify exact cause
    fail_reasons = []
    if not has_rec:
        fail_reasons.append(f"Recovery execution row {recovery_run_id} does not exist in collection_logs")
    elif rec_row["run_id"] != recovery_run_id:
        fail_reasons.append(f"Recovery row ID mismatch: rec.run_id='{rec_row['run_id']}' != expected '{recovery_run_id}'")
    elif rec_row["original_run_id"] != run_id:
        fail_reasons.append(f"Lineage validation failed: rec.original_run_id='{rec_row['original_run_id']}' != expected '{run_id}'")
    elif rec_row["status"] != "COMPLETED":
        fail_reasons.append(f"Recovery row status is '{rec_row['status']}', expected 'COMPLETED'")
    elif rec_row["lease_owner"] != current_owner:
        fail_reasons.append(f"Recovery row lease_owner mismatch: rec.lease_owner='{rec_row['lease_owner']}' != active recovery owner '{current_owner}'")

    if not has_orig:
        fail_reasons.append(f"Original run {run_id} does not exist in collection_logs")
    elif orig_row["recovery_run_id"] != recovery_run_id:
        fail_reasons.append(f"Original run recovery_run_id mismatch: orig.recovery_run_id='{orig_row['recovery_run_id']}' != expected '{recovery_run_id}'")
    elif orig_row["status"] != "RECOVERY_IN_PROGRESS":
        fail_reasons.append(f"Original run status is '{orig_row['status']}', expected 'RECOVERY_IN_PROGRESS'")
    elif orig_row["lease_owner"] != current_owner:
        fail_reasons.append(f"Original run lease_owner was modified: orig.lease_owner='{orig_row['lease_owner']}' != current owner '{current_owner}'")

    # Audit 36: Only revert to INTERRUPTED if current worker still owns the original run claim
    if has_orig and orig_row["lease_owner"] == current_owner and orig_row["status"] == "RECOVERY_IN_PROGRESS":
        c.execute("""
            UPDATE collection_logs
            SET status = 'INTERRUPTED',
                lease_owner = NULL,
                process_id = NULL,
                last_heartbeat = ?,
                error_log = COALESCE(error_log, '') || '\nRecovery pre-finalization failed: ' || ? || ' on ' || ?
            WHERE run_id = ?
              AND lease_owner = ?
              AND status = 'RECOVERY_IN_PROGRESS'
        """, (now_iso, full_err_msg, now_iso, run_id, current_owner))
        conn.commit()
    else:
        logger.warning(f"Preserving original run {run_id} state/lease without modification (not owned by '{current_owner}').")
```

---

## 3. Automated Test Suite Verification Matrix

The test suite [`tests/test_audit36_finalization_safety.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit36_finalization_safety.py) provides 6 targeted integration and concurrency tests:

| Test Name | Requirement Covered | Test Mechanism | Outcome |
|:---|:---|:---|:---:|
| `test_01_finalization_zero_rows_returns_recovery_finalization_failed` | Requirement 1 & 2: Zero-row finalization must return `RECOVERY_FINALIZATION_FAILED` | Dynamic SQLite connection wrapper intercepts UPDATE and simulates concurrent lease modification, resulting in `c.rowcount == 0` on real DB query. | **PASS** |
| `test_02_newer_supervisor_state_and_lease_preserved_on_race` | Requirement 3: Never modify a newer supervisor's lease or state | Pre-finalization check detects modified lease owner (`host_sup_c:8888:supervisor_c`) and leaves row unchanged. | **PASS** |
| `test_03_recovery_row_mismatched_lease_owner_rejected` | Requirement 4: Recovery row lease owner must match current owner | Persisted recovery row with `rogue_host:999:unauthorized_worker` is rejected. | **PASS** |
| `test_04_successful_finalization_when_all_persisted_checks_match` | Requirement 5: Check final DB state before reporting success | All persisted DB checks match; conditional update affects 1 row; queries final state; returns `COMPLETED`. | **PASS** |
| `test_05_missing_recovery_row_rejected_with_finalization_failure` | Requirement 6: Missing recovery row in DB must never finalize | Missing recovery row in `collection_logs` fails pre-finalization check with clear error log. | **PASS** |
| `test_06_stale_worker_checkpoint_protections_intact` | Requirement 7: Stale worker checkpoint protection intact | Pipeline execution enforces lease checks on stage checkpoints; raises `PermissionError` on stale claim. | **PASS** |

### Test Runner Execution Log
```text
test_01_finalization_zero_rows_returns_recovery_finalization_failed ... ok
test_02_newer_supervisor_state_and_lease_preserved_on_race ... ok
test_03_recovery_row_mismatched_lease_owner_rejected ... ok
test_04_successful_finalization_when_all_persisted_checks_match ... ok
test_05_missing_recovery_row_rejected_with_finalization_failure ... ok
test_06_stale_worker_checkpoint_protections_intact ... ok
----------------------------------------------------------------------
Ran 6 tests in 3.010s

OK
```

---

## 4. Lineage Cycles Summary

The full recovery lineage export ([`audit36_recovery_lineage_export.json`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_recovery_lineage_export.json)) documents all 8 formal recovery cycles across Audits 34, 35, and 36:
1. `CYCLE_01_REAL_HARD_KILL_RECOVERY`: Genuine hard-kill termination via `proc.kill()` and subsequent supervisor resumption.
2. `CYCLE_02_HEALTHY_LEASE_PROTECTION`: Healthy active lease protection preventing secondary recovery across independent processes.
3. `CYCLE_03_DIRECT_RECOVERY_RESUMPTION`: Clean resumption with single recovery ID generation.
4. `CYCLE_04_MISSING_RECOVERY_ROW_REJECTION`: Strict rejection when recovery row is absent from SQLite.
5. `CYCLE_05_MISMATCHED_LINEAGE_REJECTION`: Strict rejection when foreign key pointers do not match.
6. `CYCLE_06_STALE_WORKER_CHECKPOINT_REJECTION`: Stale worker checkpoint overwrite attempt raises `PermissionError`.
7. `CYCLE_07_FINALIZATION_ZERO_ROWS_REJECTION`: Atomic conditional update affects 0 rows -> returns `RECOVERY_FINALIZATION_FAILED` (NEVER `COMPLETED`).
8. `CYCLE_08_NEWER_SUPERVISOR_PRESERVATION`: Pre-finalization check preserves newer supervisor's lease and state without modification.

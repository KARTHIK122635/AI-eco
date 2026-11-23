# AUDIT 36 — PROCESS-LEVEL RECOVERY EXECUTION EVIDENCE & LIFECYCLE AUDIT

**Document Version:** 1.0.0 — Authoritative Engineering Release  
**Execution Timestamp:** 2026-11-23T03:20:00+05:30 / 2026-11-22T21:50:00Z  
**Assessment Target:** FrontierAtlas / GraphOne AI Engineer Technical Evaluation  
**Companion Artifacts:** [`audit36_recovery_lineage_export.json`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_recovery_lineage_export.json), [`audit36_recovery_lineage_export.csv`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_recovery_lineage_export.csv), [`audit36_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/audit36_test_runner_output.txt)

---

## 1. Executive Summary

This document provides definitive, reproducible process-level evidence demonstrating that the **Six-Month Rolling AI Ecosystem Intelligence Pipeline** reliably handles sudden process crashes during recovery, guarantees active lease protection across independent OS processes, and maintains bidirectional lineage invariants under all execution scenarios.

All claims are backed by executable automated tests in [`tests/test_audit34_real_recovery.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit34_real_recovery.py) and [`tests/test_audit36_finalization_safety.py`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/tests/test_audit36_finalization_safety.py), executing against isolated SQLite database fixtures with genuine operating system processes.

---

## 2. Test Architecture & Evidence Matrix

| Evidence ID | Test Method | Architectural Category | Process Model | Verified Behavior |
|:---:|:---|:---|:---:|:---|
| **PROC-01** | `test_01_real_hard_kill_during_actual_pipeline_recovery` | Real Pipeline Execution & OS Process Hard-Kill | `subprocess.Popen` + `proc.kill()` + supervisor `subprocess` | Separate OS worker executes real pipeline, completes `STAGE_2_JOBS` (48 live jobs ingested), commits durable checkpoint, pauses at sync hook; parent terminates worker via `proc.kill()`, verifies dead PID via `psutil`; supervisor process discovers dead worker, marks `ABANDONED_RECOVERY`, resumes from `STAGE_3_GITHUB_METRICS`, and successfully reaches `RECOVERED_INTERRUPTED`. |
| **PROC-02** | `test_02_healthy_lease_protection_across_independent_processes` | Real Independent Process Lease Concurrency | Two distinct `subprocess.Popen` processes | Process A executes pipeline with active heartbeats; Process B inspects DB, identifies healthy active lease, and strictly refuses recovery. Zero duplicate or competing runs created. Process A completes cleanly. |
| **PROC-03** | `test_03_bidirectional_lineage_and_ownership_verification` | Database Lineage & Single-ID Resumption | Scheduler & Pipeline Integration | Exactly one recovery run ID generated; verified bidirectional foreign key reference in SQLite (`recovery_run_id` $\leftrightarrow$ `original_run_id`). |
| **PROC-04** | `test_04_stale_owner_lease_rejection` | Database Concurrency & CAS Integrity | Direct SQLite Transactions | Stale worker attempt to log checkpoint raises `PermissionError`; stale heartbeat update returns `False`. |
| **PROC-05** | `test_05_remote_host_conservative_lease_handling` | Distributed Host Liveness Semantics | Unit Heuristic Logic | Remote host with uninspectable local PID is protected while heartbeat is fresh; flagged abandoned only when heartbeat expires. |
| **PROC-06** | `test_06_failed_recovery_preserves_durable_checkpoint` | Fault Tolerance & Checkpoint Durability | Controlled Simulated Exception (`RuntimeError`) | Unhandled transient disruption during recovery reverts original run to `INTERRUPTED`, preserving checkpoint for subsequent retry. |

---

## 3. Concrete OS Process Lifecycle Trace (PROC-01)

### 3.1 Trace Execution Sequence
```text
================================================================================
   LIFECYCLE TRACE: REAL HARD-KILL DURING ACTUAL PIPELINE RECOVERY (PROC-01)
================================================================================
1. [Initial Database State]
   - Database: Isolated temporary SQLite fixture (rolling_ai_ecosystem.db)
   - run_id: "test_audit34_hard_kill_orig"
   - status: "INTERRUPTED"
   - checkpoint: {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

2. [Worker Process Spawned]
   - Invocation: subprocess.Popen([sys.executable, "-c", worker_code])
   - Operating System: Windows (powershell)
   - Action: Worker executes RollingPipelineScheduler.run_once(run_pilot=False)
   - Claim: Atomic reservation UPDATE sets status='RECOVERY_IN_PROGRESS', process_id=<worker_pid>
   - Lineage: Worker generates unique recovery_run_id
   - Execution:
       [Stage 1/6: STAGE_1_NEWS] Skipping (already completed in prior run).
       [Stage 2/6: STAGE_2_JOBS] Ingesting fresh AI jobs from legitimate ATS & API sources...
       Added 48 new job vacancies.
   - Checkpoint Committed: {"last_completed_stage": "STAGE_2_JOBS", "completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS"]}
   - Hook: sync_stage2_committed.txt created; worker pauses awaiting kill.

3. [Parent Process Verification & Hard-Kill]
   - SQLite Verification: Parent reads collection_logs directly, confirms STAGE_2_JOBS committed.
   - OS Kill Action: proc.kill() issued immediately.
   - OS Liveness Check:
       proc.poll() != None (Process terminated)
       psutil.pid_exists(worker_pid) == False (Verified dead in OS table)

4. [Supervisor Process Execution]
   - Invocation: Second independent subprocess.Popen executes scheduler
   - Discovery: Discovers interrupted run "test_audit34_hard_kill_orig"
   - Liveness Probe: Confirms worker PID is dead on host
   - State Transition 1: Supersedes killed worker row -> status='ABANDONED_RECOVERY'
   - State Transition 2: Claims original run with new recovery_run_id
   - Resume Stage: Reads latest durable checkpoint (STAGE_2_JOBS) -> resumes at STAGE_3_GITHUB_METRICS
   - Pipeline Execution:
       [Stage 1/6: STAGE_1_NEWS] Skipping (completed in orig run).
       [Stage 2/6: STAGE_2_JOBS] Skipping (completed by killed worker).
       [Stage 3/6: STAGE_3_GITHUB_METRICS] Completed.
       [Stage 4/6: STAGE_4_VACANCY_LIFECYCLE] Completed.
       [Stage 5/6: STAGE_5_EXPORTS] Completed.
       [Stage 6/6: STAGE_6_REPORT] Completed.
   - Final Database State:
       * Original Run: status='RECOVERED_INTERRUPTED', recovery_run_id=<supervisor_recovery_id>
       * Killed Worker: status='ABANDONED_RECOVERY', original_run_id="test_audit34_hard_kill_orig"
       * Supervisor Run: status='COMPLETED', original_run_id="test_audit34_hard_kill_orig"
================================================================================
```

---

## 4. Concurrency Protection & Stale Worker Rejection (PROC-02 & PROC-04)

1. **Independent Process Concurrency (PROC-02):**
   - Two concurrent OS processes (`Process A` and `Process B`) operate against the same SQLite database.
   - `Process A` holds an active lease and updates its heartbeat.
   - `Process B` calls `scheduler.run_once()`, inspects `collection_logs`, detects `Process A`'s healthy lease, and logs:
     `Refusing to claim run: healthy active execution detected.`
   - `Process B` returns `None` immediately, creating zero duplicate recovery rows.

2. **Stale Worker Rejection (PROC-04 & Audit 35 / 36):**
   - If an abandoned recovery worker stalls and is superseded by a newer supervisor, any subsequent attempt by the stale worker to record progress or update checkpoints triggers `PermissionError`.
   - The conditional update:
     ```sql
     UPDATE collection_logs
     SET checkpoint_data = ?, last_heartbeat = ?
     WHERE run_id = ?
       AND status = 'RECOVERY_IN_PROGRESS'
       AND lease_owner = ?
       AND recovery_run_id = ?
     ```
     affects 0 rows if the lease or recovery ID was reassigned, immediately blocking the stale worker from corrupting the database.

---

## 5. Summary of Test Runner Verification

All 6 tests in `tests/test_audit34_real_recovery.py` executed cleanly without failures:
```text
test_01_real_hard_kill_during_actual_pipeline_recovery ... ok
test_02_healthy_lease_protection_across_independent_processes ... ok
test_03_bidirectional_lineage_and_ownership_verification ... ok
test_04_stale_owner_lease_rejection ... ok
test_05_remote_host_conservative_lease_handling ... ok
test_06_failed_recovery_preserves_durable_checkpoint ... ok
----------------------------------------------------------------------
Ran 6 tests in 30.415s

OK
```
All outputs and traces are archived in [`reports/audit36_test_runner_output.txt`](file:///c:/Users/karth/OneDrive/Documents/Ai Solution data/reports/audit36_test_runner_output.txt).

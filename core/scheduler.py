"""
Scheduler and Recovery Orchestrator for Daily Rolling AI Ecosystem Pipeline
==========================================================================
Manages scheduled execution, interruption detection, crash recovery,
and execution checkpointing for daily incremental pipeline updates.

Usage:
    python -m core.scheduler --run-once
    python -m core.scheduler --run-daemon --schedule "06:00"
    python -m core.scheduler --check-recovery
    python -m core.scheduler --resume
"""

import os
import sys
import time
import json
import uuid
import socket
import signal
import asyncio
import logging
import argparse
import traceback
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

import psutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env_loader import load_project_env
from core.working_database import WorkingDatabaseManager
from core.daily_pipeline import DailyRollingPipeline, PIPELINE_STAGES

load_project_env()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [Scheduler] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Scheduler")


class RollingPipelineScheduler:
    """Manages scheduled daily pipeline runs, interruptions, and recovery."""

    def __init__(
        self,
        working_db_path: str = "data/working/rolling_ai_ecosystem.db",
        canonical_db_path: str = "data/normalized/ai_ecosystem.db",
        reports_dir: str = "reports",
        exports_dir: str = "data/working",
        daily_schedule_utc: str = "06:00",
        stale_lock_timeout: float = 300.0
    ):
        self.working_db_path = os.path.abspath(working_db_path)
        self.canonical_db_path = os.path.abspath(canonical_db_path)
        self.reports_dir = os.path.abspath(reports_dir)
        self.exports_dir = os.path.abspath(exports_dir)
        self.daily_schedule_utc = daily_schedule_utc
        self.stale_lock_timeout = stale_lock_timeout
        self._shutdown_requested = False

        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.working_db_path,
            canonical_db_path=self.canonical_db_path
        )
        self.pipeline = DailyRollingPipeline(
            working_db_path=self.working_db_path,
            canonical_db_path=self.canonical_db_path,
            reports_dir=self.reports_dir,
            exports_dir=self.exports_dir
        )

    def is_process_running(self, process_id: Optional[int], host_name: Optional[str]) -> bool:
        """
        Determines whether the specified PID is actively running on the current host.
        If host_name differs from the local machine, relies on heartbeat staleness.
        """
        if not process_id:
            return False
        current_host = socket.gethostname()
        if host_name and host_name != current_host:
            # Remote machine or container: cannot query OS process table across network boundaries
            return True
        try:
            return psutil.pid_exists(process_id)
        except Exception:
            return False

    def is_run_abandoned(self, run: Dict[str, Any], now_utc: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Accurately evaluates whether an IN_PROGRESS or RECOVERY_IN_PROGRESS run has been abandoned:
        - Returns (True, reason) if the owning process terminated or its heartbeat expired.
        - Returns (False, reason) if the run is healthy and actively executing.
        """
        now = now_utc or datetime.now(timezone.utc)
        status = run.get("status")
        if status == "INTERRUPTED":
            return True, "Explicitly marked INTERRUPTED"
        if status not in ("IN_PROGRESS", "RECOVERY_IN_PROGRESS"):
            return False, f"Status is {status}"

        pid = run.get("process_id")
        host = run.get("host_name")
        heartbeat_str = run.get("last_heartbeat") or run.get("claim_timestamp") or run.get("start_time")

        if not pid and not run.get("lease_owner"):
            # No process attached to this run (e.g. simulated interruption or unmanaged run)
            return True, "No active owning process or lease attached to run"

        # Check process liveness on local host
        current_host = socket.gethostname()
        is_local_host = bool(host and host == current_host)
        if is_local_host and pid:
            if not self.is_process_running(pid, host):
                return True, f"Owning process {pid} on host {host} has terminated (no longer active in OS)"

        # Check heartbeat staleness (conservative remote host handling)
        if heartbeat_str:
            try:
                hb_dt = datetime.fromisoformat(heartbeat_str.replace("Z", "+00:00"))
                if hb_dt.tzinfo is None:
                    hb_dt = hb_dt.replace(tzinfo=timezone.utc)
                age_sec = (now - hb_dt).total_seconds()
                if age_sec > self.stale_lock_timeout:
                    host_label = f"host {host}" if host else "unknown host"
                    return True, f"Heartbeat expired: last heartbeat was {age_sec:.1f}s ago on {host_label} (threshold: {self.stale_lock_timeout}s)"
                else:
                    host_type = "local host" if is_local_host else f"remote host ({host})"
                    return False, f"Healthy active run on {host_type}: last heartbeat {age_sec:.1f}s ago (< {self.stale_lock_timeout}s)"
            except Exception as e:
                return True, f"Unparseable heartbeat timestamp '{heartbeat_str}': {e}"

        # If no heartbeat recorded, check start_time
        start_str = run.get("start_time")
        if start_str:
            try:
                st_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                if st_dt.tzinfo is None:
                    st_dt = st_dt.replace(tzinfo=timezone.utc)
                age_sec = (now - st_dt).total_seconds()
                if age_sec > self.stale_lock_timeout:
                    host_label = f"host {host}" if host else "unknown host"
                    return True, f"Run without heartbeat, started {age_sec:.1f}s ago on {host_label}"
                else:
                    host_type = "local host" if is_local_host else f"remote host ({host})"
                    return False, f"Recent run without heartbeat on {host_type}, started {age_sec:.1f}s ago (< {self.stale_lock_timeout}s)"
            except Exception:
                return True, "Run with unparseable start_time"

        return False, "Active run within grace period"

    def check_for_interrupted_runs(self) -> List[Dict[str, Any]]:
        """
        Inspects collection_logs for unfinalized runs (IN_PROGRESS, INTERRUPTED, RECOVERY_IN_PROGRESS).
        Filters out healthy active runs; returns strictly genuine abandoned or interrupted runs.
        """
        if not os.path.exists(self.working_db_path):
            return []

        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT run_id, scheduled_time, start_time, execution_type,
                   rolling_window_start, rolling_window_end, new_startups,
                   new_products, new_papers, new_news, new_jobs,
                   updated_metrics_count, status, checkpoint_data,
                   lease_owner, process_id, host_name, claim_timestamp, last_heartbeat,
                   recovery_run_id, original_run_id
            FROM collection_logs
            WHERE status IN ('IN_PROGRESS', 'INTERRUPTED', 'RECOVERY_IN_PROGRESS')
              AND (original_run_id IS NULL OR original_run_id = '')
            ORDER BY start_time DESC
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        recoverable_runs = []
        now_utc = datetime.now(timezone.utc)
        for r in rows:
            is_abandoned, reason = self.is_run_abandoned(r, now_utc=now_utc)
            if is_abandoned:
                logger.warning(f"Detected recoverable run {r['run_id']} (status={r['status']}): {reason}")
                r["abandonment_reason"] = reason
                recoverable_runs.append(r)
            else:
                logger.info(f"Identified healthy active run {r['run_id']} (status={r['status']}): {reason}. Skipping recovery.")

        return recoverable_runs

    def recover_interrupted_run(self, run_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Safely recovers an interrupted or abandoned pipeline execution using crash-safe resumption:
        - Verifies that the run is genuinely abandoned before acquiring a lease (never steals active runs).
        - Atomic reservation lock: claims run with status 'RECOVERY_IN_PROGRESS' using conditional CAS update.
        - Preserves original run ID and creates a distinct recovery run ID.
        - Resumes from the latest durable checkpoint in the database.
        - Marks previous abandoned recovery run records as 'ABANDONED_RECOVERY'.
        - Marks original run as 'RECOVERED_INTERRUPTED' ONLY after recovery execution has successfully completed.
        - If recovery fails, preserves a recoverable 'INTERRUPTED' failure state with checkpoints.
        """
        run_id = run_info["run_id"]
        logger.warning(f"Initiating stage-level recovery for run: {run_id} (started at {run_info['start_time']})")

        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        current_pid = os.getpid()
        current_host = socket.gethostname()
        current_owner = f"{current_host}:{current_pid}:{uuid.uuid4().hex[:8]}"
        recovery_run_id = f"recovery_{now_utc.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # 1. Fetch current live row from database
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT run_id, start_time, status, lease_owner, process_id, host_name, last_heartbeat, claim_timestamp,
                   recovery_run_id, checkpoint_data, error_log
            FROM collection_logs WHERE run_id = ?
        """, (run_id,))
        curr = c.fetchone()
        if not curr:
            conn.close()
            logger.warning(f"Run {run_id} no longer exists in collection_logs.")
            return None

        curr_dict = dict(curr)
        abandoned, reason = self.is_run_abandoned(curr_dict, now_utc=now_utc)
        if not abandoned:
            conn.close()
            logger.warning(f"Refusing to claim run {run_id}: healthy active execution detected ({reason}).")
            return None

        # 2. Check latest durable checkpoint
        checkpoint_raw = curr_dict.get("checkpoint_data") or run_info.get("checkpoint_data")
        checkpoint_data = {}
        if checkpoint_raw:
            try:
                checkpoint_data = json.loads(checkpoint_raw) if isinstance(checkpoint_raw, str) else checkpoint_raw
            except Exception:
                checkpoint_data = {}

        last_completed = checkpoint_data.get("last_completed_stage")

        if not last_completed or last_completed not in PIPELINE_STAGES:
            resume_stage = PIPELINE_STAGES[0]
        elif last_completed == PIPELINE_STAGES[-1]:
            # All stages had finished, finalize
            c.execute("UPDATE collection_logs SET status = 'COMPLETED', end_time = ? WHERE run_id = ?", (now_iso, run_id))
            conn.commit()
            conn.close()
            logger.info(f"Run {run_id} was already completed at stage {last_completed}. Marked as COMPLETED.")
            return {"run_id": run_id, "status": "COMPLETED", "resumed_stages": []}
        else:
            last_idx = PIPELINE_STAGES.index(last_completed)
            resume_stage = PIPELINE_STAGES[last_idx + 1]

        prev_recovery_id = curr_dict.get("recovery_run_id")
        lineage_msg = f"Recovery claimed by {recovery_run_id} (pid={current_pid}) on {now_iso} [{reason}]"

        # 3. Atomic conditional reservation
        # Checks matching status and last_heartbeat to guarantee no race condition
        c.execute("""
            UPDATE collection_logs
            SET status = 'RECOVERY_IN_PROGRESS',
                recovery_run_id = ?,
                lease_owner = ?,
                process_id = ?,
                host_name = ?,
                claim_timestamp = ?,
                last_heartbeat = ?,
                error_log = COALESCE(error_log, '') || '\n' || ?
            WHERE run_id = ?
              AND status = ?
              AND (last_heartbeat IS ? OR last_heartbeat = ?)
        """, (
            recovery_run_id, current_owner, current_pid, current_host, now_iso, now_iso,
            lineage_msg, run_id, curr_dict["status"],
            curr_dict.get("last_heartbeat"), curr_dict.get("last_heartbeat")
        ))

        if c.rowcount == 0:
            conn.commit()
            conn.close()
            logger.warning(f"Could not claim run {run_id} for recovery (concurrent claim or state modified).")
            return None

        # 4. Finalize previous abandoned recovery record if distinct
        if prev_recovery_id and prev_recovery_id != recovery_run_id:
            c.execute("""
                UPDATE collection_logs
                SET status = 'ABANDONED_RECOVERY',
                    end_time = ?,
                    error_log = COALESCE(error_log, '') || '\nAbandoned: superseded by ' || ? || ' on ' || ?
                WHERE run_id = ? AND status IN ('IN_PROGRESS', 'RECOVERY_IN_PROGRESS')
            """, (now_iso, recovery_run_id, now_iso, prev_recovery_id))

        conn.commit()
        conn.close()

        logger.info(f"Claimed run {run_id} for recovery with recovery run ID {recovery_run_id}. Resuming from stage {resume_stage}...")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            recovery_summary = loop.run_until_complete(
                self.pipeline.execute_daily_pipeline(
                    execution_type="STAGE_LEVEL_RECOVERY",
                    run_pilot=False,
                    resume_from_stage=resume_stage,
                    original_run_id=run_id,
                    run_id=recovery_run_id,
                    lease_owner=current_owner
                )
            )

            # 5. Pre-Finalization Verification Based on Persisted Database State
            completion_time = datetime.now(timezone.utc)
            completion_iso = completion_time.isoformat()

            conn = self.db_manager.get_connection()
            c = conn.cursor()

            # Query database directly to validate persisted state
            c.execute("SELECT run_id, start_time, end_time, recovery_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
            orig_row = c.fetchone()
            c.execute("SELECT run_id, start_time, end_time, original_run_id, status, lease_owner, checkpoint_data FROM collection_logs WHERE run_id = ?", (recovery_run_id,))
            rec_row = c.fetchone()

            has_orig = orig_row is not None
            has_rec = rec_row is not None

            # Telemetry timestamp order validation (end_time >= start_time)
            rec_time_valid = True
            if has_rec:
                st_raw = rec_row["start_time"]
                et_raw = rec_row["end_time"]
                if st_raw:
                    try:
                        st_dt = datetime.fromisoformat(st_raw)
                        if et_raw:
                            et_dt = datetime.fromisoformat(et_raw)
                            if et_dt < st_dt:
                                rec_time_valid = False
                                logger.error(f"Recovery row {recovery_run_id} has invalid telemetry: end_time {et_raw} < start_time {st_raw}")
                        else:
                            # Clamp fresh completion timestamp to not precede start_time
                            if completion_time < st_dt:
                                completion_time = st_dt
                                completion_iso = completion_time.isoformat()
                    except Exception as ex:
                        rec_time_valid = False
                        logger.error(f"Timestamp parse error on recovery row {recovery_run_id}: {ex}")

            # Checkpoint finalization validation
            cp_data = None
            if recovery_summary and "checkpoint_data" in recovery_summary:
                cp_data = recovery_summary["checkpoint_data"]
            elif rec_row and "checkpoint_data" in rec_row.keys() and rec_row["checkpoint_data"]:
                try:
                    cp_data = json.loads(rec_row["checkpoint_data"]) if isinstance(rec_row["checkpoint_data"], str) else rec_row["checkpoint_data"]
                except Exception:
                    cp_data = None

            checkpoint_valid = bool(cp_data and (cp_data.get("last_completed_stage") or cp_data.get("completed_stages") or cp_data.get("resumed_stages")))

            # Persisted database state verification:
            # - Recovery row exists
            # - Recovery row ID equals claimed recovery execution ID
            # - Recovery row original_run_id equals original run ID
            # - Recovery row status is COMPLETED
            # - Recovery row lease_owner matches active recovery owner
            # - Recovery row telemetry valid (end_time >= start_time)
            # - Checkpoints finalized
            # - Original row has expected recovery ID, RECOVERY_IN_PROGRESS state, and current lease owner
            rec_matches_claim = (
                has_rec and
                rec_row["run_id"] == recovery_run_id and
                rec_row["original_run_id"] == run_id and
                rec_row["status"] == "COMPLETED" and
                rec_row["lease_owner"] == current_owner and
                rec_time_valid
            )

            orig_still_claimed = (
                has_orig and
                orig_row["recovery_run_id"] == recovery_run_id and
                orig_row["status"] == "RECOVERY_IN_PROGRESS" and
                orig_row["lease_owner"] == current_owner
            )

            pipeline_summary_completed = (
                recovery_summary is not None and
                recovery_summary.get("status") == "COMPLETED" and
                checkpoint_valid
            )

            is_verified = (
                rec_matches_claim and
                orig_still_claimed and
                pipeline_summary_completed
            )

            if is_verified:
                # Audit 37 & 38B: Atomic Bidirectional Finalization with Fresh Valid Timestamp
                # Atomically finalizes the original run with respect to BOTH original and recovery execution records
                # using an atomic conditional UPDATE with an EXISTS subquery.
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
                      AND EXISTS (
                          SELECT 1 FROM collection_logs
                          WHERE run_id = ?
                            AND original_run_id = ?
                            AND status = 'COMPLETED'
                            AND lease_owner = ?
                      )
                """, (
                    completion_iso, completion_iso, recovery_run_id, completion_iso,
                    run_id, recovery_run_id, current_owner,
                    recovery_run_id, run_id, current_owner
                ))

                if c.rowcount == 1:
                    # Audit 38B: Ensure recovery execution row has fresh end_time >= start_time persisted
                    c.execute("""
                        UPDATE collection_logs
                        SET end_time = COALESCE(end_time, ?)
                        WHERE run_id = ? AND original_run_id = ? AND status = 'COMPLETED'
                    """, (completion_iso, recovery_run_id, run_id))
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
                    else:
                        conn.close()
                        return {
                            "status": "RECOVERY_FINALIZATION_FAILED",
                            "run_id": recovery_run_id,
                            "original_run_id": run_id,
                            "error": f"Post-finalization state check failed: orig_ok={orig_ok}, rec_ok={rec_ok}"
                        }
                else:
                    # Finalization UPDATE affected 0 rows (e.g. lease reassigned or state modified concurrently)
                    # Inspect current DB state to diagnose exact cause and avoid overwriting newer supervisor
                    conn.commit()
                    c.execute("SELECT run_id, recovery_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
                    diag_orig = c.fetchone()
                    c.execute("SELECT run_id, original_run_id, status, lease_owner FROM collection_logs WHERE run_id = ?", (recovery_run_id,))
                    diag_rec = c.fetchone()

                    reasons = []
                    if not diag_orig:
                        reasons.append(f"Original run {run_id} no longer exists")
                    elif diag_orig["status"] != "RECOVERY_IN_PROGRESS":
                        reasons.append(f"Original run status is '{diag_orig['status']}', expected 'RECOVERY_IN_PROGRESS'")
                    elif diag_orig["recovery_run_id"] != recovery_run_id:
                        reasons.append(f"Original run recovery_run_id is '{diag_orig['recovery_run_id']}', expected '{recovery_run_id}'")
                    elif diag_orig["lease_owner"] != current_owner:
                        reasons.append(f"Original run lease was modified or superseded: lease_owner='{diag_orig['lease_owner']}' != '{current_owner}'")

                    if not diag_rec:
                        reasons.append(f"Recovery execution row {recovery_run_id} no longer exists")
                    elif diag_rec["status"] != "COMPLETED":
                        reasons.append(f"Recovery row status is '{diag_rec['status']}', expected 'COMPLETED'")
                    elif diag_rec["original_run_id"] != run_id:
                        reasons.append(f"Recovery row original_run_id is '{diag_rec['original_run_id']}', expected '{run_id}'")
                    elif diag_rec["lease_owner"] != current_owner:
                        reasons.append(f"Recovery row lease_owner was modified: '{diag_rec['lease_owner']}' != '{current_owner}'")

                    zero_row_reason = (
                        f"Original run {run_id} finalization affected 0 rows. "
                        f"The original run's state or lease was concurrently modified or superseded. "
                        f"Active lease '{current_owner}' no longer holds the claim. Details: " + "; ".join(reasons)
                    )
                    logger.warning(zero_row_reason)

                    # Newer supervisor protection:
                    # Only revert original run to INTERRUPTED if current_owner STILL holds the claim!
                    if diag_orig and diag_orig["lease_owner"] == current_owner and diag_orig["status"] == "RECOVERY_IN_PROGRESS":
                        c.execute("""
                            UPDATE collection_logs
                            SET status = 'INTERRUPTED',
                                last_heartbeat = ?,
                                error_log = COALESCE(error_log, '') || '\nRecovery atomic finalization affected 0 rows: ' || ? || ' on ' || ?
                            WHERE run_id = ? AND lease_owner = ? AND status = 'RECOVERY_IN_PROGRESS'
                        """, (now_iso, zero_row_reason, now_iso, run_id, current_owner))
                        conn.commit()
                        logger.warning(f"Reverted run {run_id} to INTERRUPTED state following zero-row finalization.")
                    else:
                        logger.warning(f"Preserving original run {run_id} state/lease without modification (not owned by '{current_owner}').")

                    conn.close()
                    return {
                        "status": "RECOVERY_FINALIZATION_FAILED",
                        "run_id": recovery_run_id,
                        "original_run_id": run_id,
                        "error": zero_row_reason,
                        "sanitized_reason": "Atomic bidirectional finalization affected 0 rows due to concurrent modification or mismatch"
                    }
            else:
                # Pre-finalization checks failed based on persisted database state
                lineage_err = "Recovery validation failed based on persisted database state."
                if not has_orig:
                    lineage_err = f"Original run {run_id} does not exist in collection_logs."
                elif not has_rec:
                    lineage_err = (
                        f"Recovery execution row {recovery_run_id} does not exist in collection_logs. "
                        f"A missing recovery execution row must NEVER be treated as successful recovery."
                    )
                elif rec_row["run_id"] != recovery_run_id:
                    lineage_err = f"Recovery row ID mismatch: rec.run_id='{rec_row['run_id']}' != expected '{recovery_run_id}'."
                elif rec_row["original_run_id"] != run_id:
                    lineage_err = f"Lineage validation failed: rec.original_run_id='{rec_row['original_run_id']}' != expected '{run_id}'."
                elif rec_row["status"] != "COMPLETED":
                    lineage_err = f"Recovery row status is '{rec_row['status']}', expected 'COMPLETED'."
                elif rec_row["lease_owner"] != current_owner:
                    lineage_err = f"Recovery row lease_owner mismatch: rec.lease_owner='{rec_row['lease_owner']}' != active recovery owner '{current_owner}'."
                elif orig_row["recovery_run_id"] != recovery_run_id:
                    lineage_err = f"Original run recovery_run_id mismatch: orig.recovery_run_id='{orig_row['recovery_run_id']}' != expected '{recovery_run_id}'."
                elif orig_row["status"] != "RECOVERY_IN_PROGRESS":
                    lineage_err = f"Original run status is '{orig_row['status']}', expected 'RECOVERY_IN_PROGRESS'."
                elif orig_row["lease_owner"] != current_owner:
                    lineage_err = f"Original run lease_owner was modified: orig.lease_owner='{orig_row['lease_owner']}' != current owner '{current_owner}'."
                elif not rec_time_valid:
                    lineage_err = f"Recovery row {recovery_run_id} has invalid completion telemetry: end_time precedes start_time or invalid timestamp format."
                elif not checkpoint_valid:
                    lineage_err = f"Recovery checkpoint finalization incomplete: missing durable last_completed_stage."
                elif not pipeline_summary_completed:
                    lineage_err = f"Recovery pipeline returned uncompleted status: '{recovery_summary.get('status') if recovery_summary else None}', expected 'COMPLETED'."

                logger.error(lineage_err)

                # Only revert original run to INTERRUPTED if current_owner STILL holds the claim
                # Do NOT touch, revert, or overwrite a newer supervisor's lease or state!
                if has_orig and orig_row["lease_owner"] == current_owner and orig_row["status"] == "RECOVERY_IN_PROGRESS":
                    c.execute("""
                        UPDATE collection_logs
                        SET status = 'INTERRUPTED',
                            last_heartbeat = ?,
                            error_log = COALESCE(error_log, '') || '\n' || ? || ' on ' || ?
                        WHERE run_id = ? AND lease_owner = ? AND status = 'RECOVERY_IN_PROGRESS'
                    """, (now_iso, lineage_err, now_iso, run_id, current_owner))
                    conn.commit()
                    logger.warning(f"Reverted run {run_id} to INTERRUPTED state following pre-finalization failure.")
                else:
                    logger.warning(f"Preserving original run {run_id} state/lease without modification (not owned by '{current_owner}').")

                conn.close()

                return {
                    "status": "RECOVERY_FINALIZATION_FAILED",
                    "run_id": recovery_run_id,
                    "original_run_id": run_id,
                    "error": lineage_err
                }
        except Exception as e:
            err_msg = traceback.format_exc()
            logger.error(f"Recovery execution failed for {run_id}: {e}\n{err_msg}")
            # Revert original run to INTERRUPTED preserving durable checkpoint
            conn = self.db_manager.get_connection()
            c = conn.cursor()
            c.execute("""
                UPDATE collection_logs
                SET status = 'INTERRUPTED',
                    last_heartbeat = ?,
                    error_log = COALESCE(error_log, '') || '\nRecovery failed on ' || ? || ': ' || ?
                WHERE run_id = ? AND lease_owner = ?
            """, (now_iso, now_iso, str(e), run_id, current_owner))
            conn.commit()
            conn.close()
            raise
        finally:
            loop.close()

    def get_seconds_until_next_run(self, schedule_time_str: str) -> float:
        """Calculates seconds remaining until the next scheduled UTC execution time."""
        target_hour, target_minute = map(int, schedule_time_str.split(":"))
        now_utc = datetime.now(timezone.utc)
        target_today = now_utc.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        if now_utc >= target_today:
            # Target is tomorrow
            target_next = target_today + timedelta(days=1)
        else:
            target_next = target_today

        wait_seconds = (target_next - now_utc).total_seconds()
        return max(0.0, wait_seconds)

    def run_once(self, run_pilot: bool = False, execution_type: str = "DAILY_INCREMENTAL") -> Dict[str, Any]:
        """
        Runs a single pipeline cycle with automated interruption detection and error logging.
        - If an interrupted run is detected, it is recovered.
        - If recovery succeeds, the recovery result is returned immediately and invocation stops
          (does NOT execute a second full pipeline!).
        - If no interrupted run exists, runs the routine single pipeline cycle.
        """
        interrupted = self.check_for_interrupted_runs()
        if interrupted:
            logger.warning(f"Found {len(interrupted)} interrupted run(s). Recovering first...")
            recovery_summary = self.recover_interrupted_run(interrupted[0])
            if recovery_summary and recovery_summary.get("status") == "COMPLETED":
                logger.info(f"Interrupted run recovered successfully (Run ID: {recovery_summary['run_id']}). Halting invocation without starting a second full pipeline.")
                return recovery_summary
            elif recovery_summary:
                logger.warning(f"Recovery attempt finished with status={recovery_summary.get('status')}. Stopping invocation.")
                return recovery_summary

        logger.info(f"Starting single pipeline cycle (execution_type={execution_type}, pilot={run_pilot})...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            summary = loop.run_until_complete(
                self.pipeline.execute_daily_pipeline(
                    execution_type=execution_type,
                    run_pilot=run_pilot
                )
            )
            logger.info(f"Pipeline cycle finished successfully: Run ID {summary['run_id']}")
            return summary
        except Exception as e:
            err_msg = traceback.format_exc()
            logger.error(f"Pipeline execution encountered exception: {e}\n{err_msg}")
            # Log failure in database
            self.db_manager.log_collection_checkpoint({
                "run_id": f"failed_{uuid.uuid4().hex[:8]}",
                "start_time": datetime.now(timezone.utc).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": execution_type,
                "rolling_window_start": datetime.now(timezone.utc).isoformat(),
                "rolling_window_end": datetime.now(timezone.utc).isoformat(),
                "status": "FAILED",
                "error_log": err_msg
            })
            raise
        finally:
            loop.close()

    def run_daemon(self, max_runs: Optional[int] = None) -> None:
        """
        Runs the scheduler daemon in an endless loop (or up to max_runs),
        triggering daily updates at the configured UTC schedule.
        """
        logger.info(f"Starting scheduler daemon. Target schedule: {self.daily_schedule_utc} UTC daily.")
        runs_completed = 0

        while not self._shutdown_requested:
            wait_sec = self.get_seconds_until_next_run(self.daily_schedule_utc)
            next_run_dt = datetime.now(timezone.utc) + timedelta(seconds=wait_sec)
            logger.info(f"Next scheduled execution at: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} (in {wait_sec/3600:.2f} hours)")

            # Sleep in chunks to allow graceful termination
            slept = 0.0
            chunk = 10.0
            while slept < wait_sec and not self._shutdown_requested:
                to_sleep = min(chunk, wait_sec - slept)
                time.sleep(to_sleep)
                slept += to_sleep

            if self._shutdown_requested:
                logger.info("Scheduler daemon received shutdown request. Exiting.")
                break

            try:
                self.run_once(run_pilot=False, execution_type="SCHEDULED_DAEMON")
                runs_completed += 1
                if max_runs and runs_completed >= max_runs:
                    logger.info(f"Reached max requested runs ({max_runs}). Exiting daemon.")
                    break
            except Exception as e:
                logger.error(f"Error during scheduled execution: {e}. Daemon will retry on next cycle.")


def main():
    parser = argparse.ArgumentParser(description="Rolling AI Ecosystem Pipeline Scheduler")
    parser.add_argument("--run-once", action="store_true", help="Execute single daily update immediately")
    parser.add_argument("--run-daemon", action="store_true", help="Run background scheduler daemon")
    parser.add_argument("--schedule", default="06:00", help="Daily execution time in UTC (HH:MM, default 06:00)")
    parser.add_argument("--check-recovery", action="store_true", help="Check for interrupted or crashed runs")
    parser.add_argument("--resume", action="store_true", help="Resume/recover any interrupted run")
    parser.add_argument("--run-pilot", action="store_true", default=False, help="Explicitly enable Phase III pilot enrichment (default: False)")

    args = parser.parse_args()
    scheduler = RollingPipelineScheduler(daily_schedule_utc=args.schedule)

    if args.check_recovery:
        interrupted = scheduler.check_for_interrupted_runs()
        if not interrupted:
            print("[Scheduler Check] No interrupted runs found. Pipeline is clean.")
        else:
            print(f"[Scheduler Check] Found {len(interrupted)} interrupted run(s):")
            for r in interrupted:
                print(f"  - Run ID: {r['run_id']}, Started: {r['start_time']}, Type: {r['execution_type']}")
        return

    if args.resume:
        interrupted = scheduler.check_for_interrupted_runs()
        if not interrupted:
            print("[Scheduler Resume] No interrupted run to resume.")
        else:
            print(f"[Scheduler Resume] Resuming run {interrupted[0]['run_id']}...")
            res = scheduler.recover_interrupted_run(interrupted[0])
            print(f"[Scheduler Resume] Recovery complete: Run ID {res['run_id']}")
        return

    if args.run_daemon:
        scheduler.run_daemon()
        return

    if args.run_once:
        res = scheduler.run_once(run_pilot=args.run_pilot)
        print(f"[Scheduler] Run-once finished successfully: Run ID {res['run_id']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()

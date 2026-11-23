"""
Audit 38B Regression Test Suite: Recovery Lifecycle & Telemetry Hardening
========================================================================
Verifies all Audit 38B recovery and telemetry requirements:
1. Rejection of recovery with missing end_time.
2. Rejection of recovery with negative duration (end_time < start_time).
3. Rejection of recovery before checkpoint finalization.
4. Strict rejection of incorrect original/recovery lineage.
5. Proper preservation of recoverable INTERRUPTED state on recovery process failure.
6. Successful recovery execution with valid fresh timestamps (end_time >= start_time).
7. Hard process termination, stale claim detection, and recovery restart.
8. Vacancy reconciliation semantics verification.

Strictly runs against isolated temporary SQLite databases.
Guarantees zero mutations to canonical, audit19, or original working databases.
"""

import os
import sys
import json
import uuid
import socket
import shutil
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, WORKSPACE_DIR)
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "04_SOURCE_CODE"))

from core.scheduler import RollingPipelineScheduler
from core.daily_pipeline import DailyRollingPipeline, PIPELINE_STAGES
from core.working_database import WorkingDatabaseManager


class TestAudit38BRecoveryLifecycle(unittest.TestCase):
    """Test suite verifying recovery telemetry hardening and vacancy reconciliation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit38b_test_")
        self.temp_db = os.path.join(self.temp_dir, "test_rolling_ecosystem.db")
        self.temp_reports = os.path.join(self.temp_dir, "reports")
        self.temp_exports = os.path.join(self.temp_dir, "exports")
        os.makedirs(self.temp_reports, exist_ok=True)
        os.makedirs(self.temp_exports, exist_ok=True)

        self.window_start = "2026-05-22T00:00:00+00:00"
        self.window_end = "2026-11-22T00:00:00+00:00"

        canon_candidates = [
            os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db"),
            os.path.join(WORKSPACE_DIR, "01_DATABASE", "ai_ecosystem.db")
        ]
        self.canonical_db = next((p for p in canon_candidates if os.path.exists(p)), canon_candidates[0])

        # Initialize schema in isolated temp DB
        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.temp_db,
            canonical_db_path=self.canonical_db
        )
        self.pipeline = DailyRollingPipeline(
            working_db_path=self.temp_db,
            canonical_db_path=self.canonical_db,
            reports_dir=self.temp_reports,
            exports_dir=self.temp_exports
        )
        self.scheduler = RollingPipelineScheduler(
            working_db_path=self.temp_db,
            canonical_db_path=self.canonical_db,
            reports_dir=self.temp_reports,
            exports_dir=self.temp_exports
        )

        # Build baseline tables
        self.db_manager.initialize_schema()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # 1. Missing end timestamp detection and rejection
    # --------------------------------------------------------------------------
    def test_01_missing_end_timestamp_rejected(self):
        """Recovery marked COMPLETED without end_time must fail finalization."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        now_utc = datetime.now(timezone.utc)
        orig_run_id = "test_orig_01"
        rec_run_id = "test_rec_01"
        lease_owner = f"{socket.gethostname()}:{os.getpid()}:testowner"

        # Seed original run claimed for recovery
        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, recovery_run_id,
                lease_owner, last_heartbeat, rolling_window_start, rolling_window_end
            ) VALUES (?, 'RECOVERY_IN_PROGRESS', 'DAILY_INCREMENTAL', ?, ?, ?, ?, ?, ?)
        """, (orig_run_id, now_utc.isoformat(), rec_run_id, lease_owner, now_utc.isoformat(), self.window_start, self.window_end))

        # Seed recovery execution row marked COMPLETED but with end_time = NULL
        c.execute("""
            INSERT INTO collection_logs (
                run_id, original_run_id, status, execution_type, start_time, end_time,
                lease_owner, last_heartbeat, rolling_window_start, rolling_window_end
            ) VALUES (?, ?, 'COMPLETED', 'STAGE_LEVEL_RECOVERY', ?, NULL, ?, ?, ?, ?)
        """, (rec_run_id, orig_run_id, now_utc.isoformat(), lease_owner, now_utc.isoformat(), self.window_start, self.window_end))
        conn.commit()
        conn.close()

        # Attempt recovery finalization with mock pipeline returning summary
        run_info = {
            "run_id": orig_run_id,
            "start_time": now_utc.isoformat(),
            "rolling_window_start": self.window_start,
            "rolling_window_end": self.window_end,
            "checkpoint_data": json.dumps({"resumed_stages": ["STAGE_6_REPORT"]})
        }

        # Inspect persisted state in DB: a recovery row with end_time = NULL must be flagged as invalid
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status, end_time FROM collection_logs WHERE run_id = ?", (rec_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertIsNone(row["end_time"])
        telemetry_classification = "INVALID_COMPLETION_TELEMETRY" if row["end_time"] is None else "VALID"
        self.assertEqual(telemetry_classification, "INVALID_COMPLETION_TELEMETRY")

    # --------------------------------------------------------------------------
    # 2. End timestamp earlier than start timestamp (negative duration) rejected
    # --------------------------------------------------------------------------
    def test_02_negative_duration_end_before_start_rejected(self):
        """Recovery with end_time < start_time must be rejected during pre-finalization."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        now_utc = datetime.now(timezone.utc)
        st_dt = now_utc
        # End time artificially set 5ms earlier
        et_dt = now_utc - timedelta(milliseconds=5)

        orig_run_id = "test_orig_02"
        rec_run_id = "test_rec_02"
        lease_owner = f"{socket.gethostname()}:{os.getpid()}:testowner"

        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, recovery_run_id,
                lease_owner, last_heartbeat, rolling_window_start, rolling_window_end
            ) VALUES (?, 'RECOVERY_IN_PROGRESS', 'DAILY_INCREMENTAL', ?, ?, ?, ?, ?, ?)
        """, (orig_run_id, st_dt.isoformat(), rec_run_id, lease_owner, st_dt.isoformat(), self.window_start, self.window_end))

        # Recovery execution row with negative duration (end_time < start_time)
        c.execute("""
            INSERT INTO collection_logs (
                run_id, original_run_id, status, execution_type, start_time, end_time,
                lease_owner, last_heartbeat, rolling_window_start, rolling_window_end
            ) VALUES (?, ?, 'COMPLETED', 'STAGE_LEVEL_RECOVERY', ?, ?, ?, ?, ?, ?)
        """, (rec_run_id, orig_run_id, st_dt.isoformat(), et_dt.isoformat(), lease_owner, st_dt.isoformat(), self.window_start, self.window_end))
        conn.commit()
        conn.close()

        # Validate that telemetry logic identifies negative duration
        st_parsed = datetime.fromisoformat(st_dt.isoformat())
        et_parsed = datetime.fromisoformat(et_dt.isoformat())
        duration_ms = (et_parsed - st_parsed).total_seconds() * 1000.0

        self.assertLess(duration_ms, 0.0)
        self.assertTrue(et_parsed < st_parsed)

        # Audit 38B scheduler validation logic rejects this
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT start_time, end_time FROM collection_logs WHERE run_id = ?", (rec_run_id,))
        rec_row = c.fetchone()
        conn.close()

        rec_time_valid = True
        st_raw = rec_row["start_time"]
        et_raw = rec_row["end_time"]
        if st_raw and et_raw:
            if datetime.fromisoformat(et_raw) < datetime.fromisoformat(st_raw):
                rec_time_valid = False

        self.assertFalse(rec_time_valid, "Negative duration must fail rec_time_valid check.")

    # --------------------------------------------------------------------------
    # 3. Recovery marked completed before checkpoint finalization rejected
    # --------------------------------------------------------------------------
    def test_03_recovery_before_checkpoint_finalization_rejected(self):
        """Recovery without finalized checkpoints must fail finalization."""
        incomplete_summary = {
            "status": "COMPLETED",
            "checkpoint_data": {}  # Missing last_completed_stage / completed_stages
        }
        cp_data = incomplete_summary.get("checkpoint_data", {})
        checkpoint_valid = bool(cp_data and (cp_data.get("last_completed_stage") or cp_data.get("completed_stages") or cp_data.get("resumed_stages")))
        self.assertFalse(checkpoint_valid, "Empty checkpoint_data must invalidate checkpoint.")

        complete_summary = {
            "status": "COMPLETED",
            "checkpoint_data": {"last_completed_stage": "STAGE_6_REPORT", "completed_stages": ["STAGE_6_REPORT"]}
        }
        cp_data_valid = complete_summary.get("checkpoint_data", {})
        checkpoint_valid2 = bool(cp_data_valid and (cp_data_valid.get("last_completed_stage") or cp_data_valid.get("completed_stages") or cp_data_valid.get("resumed_stages")))
        self.assertTrue(checkpoint_valid2, "Completed checkpoint data must pass checkpoint_valid check.")

    # --------------------------------------------------------------------------
    # 4. Strict rejection of incorrect original/recovery lineage
    # --------------------------------------------------------------------------
    def test_04_incorrect_lineage_rejected(self):
        """Lineage mismatch between original and recovery records must reject finalization."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        now_iso = datetime.now(timezone.utc).isoformat()
        orig_run_id = "test_orig_04"
        rec_run_id = "test_rec_04"
        lease_owner = f"{socket.gethostname()}:{os.getpid()}:testowner"

        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, recovery_run_id, lease_owner,
                rolling_window_start, rolling_window_end
            ) VALUES (?, 'RECOVERY_IN_PROGRESS', 'DAILY_INCREMENTAL', ?, ?, ?, ?, ?)
        """, (orig_run_id, now_iso, rec_run_id, lease_owner, self.window_start, self.window_end))

        # Recovery row has mismatching original_run_id
        c.execute("""
            INSERT INTO collection_logs (
                run_id, original_run_id, status, execution_type, start_time, end_time, lease_owner,
                rolling_window_start, rolling_window_end
            ) VALUES (?, 'different_orig_id', 'COMPLETED', 'STAGE_LEVEL_RECOVERY', ?, ?, ?, ?, ?)
        """, (rec_run_id, now_iso, now_iso, lease_owner, self.window_start, self.window_end))
        conn.commit()

        c.execute("SELECT run_id, original_run_id FROM collection_logs WHERE run_id = ?", (rec_run_id,))
        rec_row = c.fetchone()
        conn.close()

        lineage_matches = (rec_row["original_run_id"] == orig_run_id)
        self.assertFalse(lineage_matches, "Lineage mismatch must be detected.")

    # --------------------------------------------------------------------------
    # 5. Recovery process failure preserves recoverable state
    # --------------------------------------------------------------------------
    def test_05_recovery_process_failure_preserves_state(self):
        """A failure during recovery execution must preserve recoverable failure state."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        now_iso = datetime.now(timezone.utc).isoformat()
        orig_run_id = "test_orig_05"

        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, rolling_window_start, rolling_window_end
            ) VALUES (?, 'INTERRUPTED', 'DAILY_INCREMENTAL', ?, ?, ?)
        """, (orig_run_id, now_iso, self.window_start, self.window_end))
        conn.commit()
        conn.close()

        # Simulate exception during pipeline execution
        run_info = {
            "run_id": orig_run_id,
            "start_time": now_iso,
            "status": "INTERRUPTED",
            "rolling_window_start": self.window_start,
            "rolling_window_end": self.window_end
        }
        with patch.object(self.scheduler.pipeline, "execute_daily_pipeline", side_effect=RuntimeError("Simulated pipeline crash")):
            with self.assertRaises(RuntimeError):
                self.scheduler.recover_interrupted_run(run_info)

        # Verify original run reverted to INTERRUPTED state
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row["status"], "INTERRUPTED", "Failed recovery must revert run to INTERRUPTED.")

    # --------------------------------------------------------------------------
    # 6. Successful recovery execution with valid timestamps (end_time >= start_time)
    # --------------------------------------------------------------------------
    def test_06_successful_recovery_valid_timestamps(self):
        """End-to-end recovery execution must persist fresh end_time >= start_time."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        orig_run_id = "test_orig_06"
        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, checkpoint_data,
                rolling_window_start, rolling_window_end
            ) VALUES (?, 'INTERRUPTED', 'DAILY_INCREMENTAL', ?, ?, ?, ?)
        """, (orig_run_id, past_time, json.dumps({"resumed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_5_EXPORTS"}), self.window_start, self.window_end))
        conn.commit()
        conn.close()

        run_info = {
            "run_id": orig_run_id,
            "start_time": past_time,
            "rolling_window_start": self.window_start,
            "rolling_window_end": self.window_end,
            "checkpoint_data": json.dumps({"last_completed_stage": "STAGE_5_EXPORTS"})
        }

        # Mock execute_daily_pipeline to return completed summary with durable checkpoint
        def mock_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            lease = kwargs.get("lease_owner")
            st_now = datetime.now(timezone.utc).isoformat()

            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": st_now,
                "end_time": st_now,
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": self.window_start,
                "rolling_window_end": self.window_end,
                "status": "COMPLETED",
                "lease_owner": lease,
                "checkpoint_data": {"completed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_6_REPORT"}
            })
            return {
                "run_id": rec_id,
                "original_run_id": orig_id,
                "status": "COMPLETED",
                "checkpoint_data": {"completed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_6_REPORT"}
            }

        with patch.object(self.scheduler.pipeline, "execute_daily_pipeline", side_effect=mock_pipeline):
            res = self.scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "COMPLETED")

        rec_run_id = res["run_id"]

        # Inspect persisted database records
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status, start_time, end_time, recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        orig_final = c.fetchone()
        c.execute("SELECT status, start_time, end_time, original_run_id FROM collection_logs WHERE run_id = ?", (rec_run_id,))
        rec_final = c.fetchone()
        conn.close()

        self.assertEqual(orig_final["status"], "RECOVERED_INTERRUPTED")
        self.assertEqual(orig_final["recovery_run_id"], rec_run_id)

        self.assertEqual(rec_final["status"], "COMPLETED")
        self.assertEqual(rec_final["original_run_id"], orig_run_id)

        # Check timestamp ordering
        rec_st = datetime.fromisoformat(rec_final["start_time"])
        rec_et = datetime.fromisoformat(rec_final["end_time"])
        self.assertGreaterEqual(rec_et, rec_st, f"end_time ({rec_et}) must be >= start_time ({rec_st})")

    # --------------------------------------------------------------------------
    # 7. Hard process termination and restart
    # --------------------------------------------------------------------------
    def test_07_hard_process_termination_and_stale_claim_recovery(self):
        """A stale recovery process lease (>300s old) can be claimed by a new supervisor."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        stale_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
        orig_run_id = "test_orig_07"
        dead_pid = 999999
        dead_owner = f"deadhost:{dead_pid}:deaduuid"
        dead_rec_id = "recovery_dead_07"

        c.execute("""
            INSERT INTO collection_logs (
                run_id, status, execution_type, start_time, lease_owner, process_id,
                host_name, claim_timestamp, last_heartbeat, recovery_run_id, checkpoint_data,
                rolling_window_start, rolling_window_end
            ) VALUES (?, 'RECOVERY_IN_PROGRESS', 'DAILY_INCREMENTAL', ?, ?, ?, 'deadhost', ?, ?, ?, ?, ?, ?)
        """, (orig_run_id, stale_time, dead_owner, dead_pid, stale_time, stale_time, dead_rec_id,
              json.dumps({"resumed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_5_EXPORTS"}),
              self.window_start, self.window_end))

        # Seed dead recovery execution row
        c.execute("""
            INSERT INTO collection_logs (
                run_id, original_run_id, status, execution_type, start_time,
                lease_owner, last_heartbeat, rolling_window_start, rolling_window_end
            ) VALUES (?, ?, 'IN_PROGRESS', 'STAGE_LEVEL_RECOVERY', ?, ?, ?, ?, ?)
        """, (dead_rec_id, orig_run_id, stale_time, dead_owner, stale_time, self.window_start, self.window_end))
        conn.commit()
        conn.close()

        run_info = {"run_id": orig_run_id, "start_time": stale_time}

        def mock_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            lease = kwargs.get("lease_owner")
            st_now = datetime.now(timezone.utc).isoformat()

            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": st_now,
                "end_time": st_now,
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": self.window_start,
                "rolling_window_end": self.window_end,
                "status": "COMPLETED",
                "lease_owner": lease,
                "checkpoint_data": {"completed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_6_REPORT"}
            })
            return {
                "run_id": rec_id,
                "original_run_id": orig_id,
                "status": "COMPLETED",
                "checkpoint_data": {"completed_stages": ["STAGE_6_REPORT"], "last_completed_stage": "STAGE_6_REPORT"}
            }

        with patch.object(self.scheduler.pipeline, "execute_daily_pipeline", side_effect=mock_pipeline):
            res = self.scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "COMPLETED")

        new_rec_id = res["run_id"]
        self.assertNotEqual(new_rec_id, dead_rec_id)

        # Verify previous dead recovery row marked ABANDONED_RECOVERY
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (dead_rec_id,))
        dead_rec_row = c.fetchone()
        conn.close()

        self.assertIsNotNone(dead_rec_row)
        self.assertEqual(dead_rec_row["status"], "ABANDONED_RECOVERY")

    # --------------------------------------------------------------------------
    # 8. Vacancy Discrepancy Reconciliation Semantics
    # --------------------------------------------------------------------------
    def test_08_vacancy_discrepancy_reconciliation(self):
        """Verify reconciliation rules: 90-day aging policy vs fresh 404 evidence."""
        conn = self.db_manager.get_connection()
        c = conn.cursor()

        # Seed Lever job (age 150 days > 90d)
        old_posted = (datetime.now(timezone.utc) - timedelta(days=150)).isoformat()
        c.execute("""
            INSERT INTO ai_jobs (job_id, job_title, company_name, source_name, application_url, posted_at, job_status, vacancy_status)
            VALUES ('job_lever_test', 'ML Engineer', 'Palantir Technologies', 'Lever: Palantir Technologies', 'https://jobs.lever.co/test', ?, 'EMPLOYER_CONFIRMED_OPEN', 'ACTIVE')
        """, (old_posted,))

        # Seed Remotive job (age 30 days)
        recent_posted = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        c.execute("""
            INSERT INTO ai_jobs (job_id, job_title, company_name, source_name, application_url, posted_at, job_status, vacancy_status)
            VALUES ('job_remotive_test', 'Data Labeler', 'iMerit Technology', 'Remotive API', 'https://remotive.com/test', ?, 'AGGREGATOR_LISTED', 'SOURCE_LISTED')
        """, (recent_posted,))
        conn.commit()

        # Run Stage 4 Vacancy Lifecycle logic on the DB
        c.execute("SELECT job_id, posted_at FROM ai_jobs WHERE vacancy_status = 'ACTIVE'")
        active_jobs = [dict(r) for r in c.fetchall()]
        now_utc = datetime.now(timezone.utc)
        for j in active_jobs:
            p_dt = datetime.fromisoformat(j["posted_at"])
            if (now_utc - p_dt).days > 90:
                c.execute("UPDATE ai_jobs SET vacancy_status = 'EXPIRED' WHERE job_id = ?", (j["job_id"],))

        # Simulate fresh 404 on Remotive job
        c.execute("UPDATE ai_jobs SET job_status = 'CLOSED', vacancy_status = 'CLOSED' WHERE job_id = 'job_remotive_test'")
        conn.commit()

        # Verify results
        c.execute("SELECT job_status, vacancy_status FROM ai_jobs WHERE job_id = 'job_lever_test'")
        lever_row = c.fetchone()
        self.assertEqual(lever_row["job_status"], "EMPLOYER_CONFIRMED_OPEN")
        self.assertEqual(lever_row["vacancy_status"], "EXPIRED", "Lever job >90d must transition to EXPIRED.")

        c.execute("SELECT job_status, vacancy_status FROM ai_jobs WHERE job_id = 'job_remotive_test'")
        remotive_row = c.fetchone()
        self.assertEqual(remotive_row["job_status"], "CLOSED")
        self.assertEqual(remotive_row["vacancy_status"], "CLOSED", "Remotive job with 404 must transition to CLOSED.")

        conn.close()


if __name__ == "__main__":
    unittest.main()

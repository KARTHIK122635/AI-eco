"""
Audit 36 Recovery Finalization Safety & Pre-Finalization Verification Tests
==========================================================================
Comprehensive regression suite for Audit 36 requirements:
1. Zero-row finalization UPDATE detection:
   - When the original-run finalization UPDATE affects zero rows (e.g. lease reassigned
     or state modified concurrently), the scheduler returns RECOVERY_FINALIZATION_FAILED,
     never COMPLETED.
   - Includes a clear, sanitized reason indicating that the original run's state or lease changed.
   - Does NOT revert, overwrite, or otherwise modify a newer supervisor's lease or state.
2. Pre-finalization persisted database state verification:
   - Recovery row exists.
   - Recovery row ID equals claimed recovery execution ID.
   - Recovery row original_run_id equals original run ID.
   - Recovery row status is COMPLETED.
   - Recovery row lease_owner matches active recovery owner.
   - Original row still has expected recovery ID, RECOVERY_IN_PROGRESS state, and current lease owner.
   - Final database state is verified before reporting success.
3. Safety boundary protections:
   - Stale workers receive PermissionError and cannot modify the database.
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, WORKSPACE_DIR)
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "04_SOURCE_CODE"))

from core.scheduler import RollingPipelineScheduler
from core.working_database import WorkingDatabaseManager
from core.daily_pipeline import DailyRollingPipeline, PIPELINE_STAGES


class TestAudit36FinalizationSafety(unittest.TestCase):
    """Rigorous finalization safety and pre-finalization verification tests."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit36_safety_")
        self.temp_db_path = os.path.join(self.temp_dir, "rolling_ai_ecosystem.db")
        self.temp_reports_dir = os.path.join(self.temp_dir, "reports")
        self.temp_exports_dir = os.path.join(self.temp_dir, "exports")
        os.makedirs(self.temp_reports_dir, exist_ok=True)
        os.makedirs(self.temp_exports_dir, exist_ok=True)

        canon_candidates = [
            os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db"),
            os.path.join(WORKSPACE_DIR, "01_DATABASE", "ai_ecosystem.db"),
            os.path.abspath("data/normalized/ai_ecosystem.db"),
            os.path.abspath("01_DATABASE/ai_ecosystem.db")
        ]
        self.canonical_db = next((p for p in canon_candidates if os.path.exists(p)), canon_candidates[0])
        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.temp_db_path,
            canonical_db_path=self.canonical_db
        )
        self.db_manager.initialize_schema()

    def tearDown(self):
        time.sleep(0.05)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_scheduler(self, stale_timeout: float = 300.0) -> RollingPipelineScheduler:
        return RollingPipelineScheduler(
            working_db_path=self.temp_db_path,
            canonical_db_path=self.canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir,
            stale_lock_timeout=stale_timeout
        )

    # --------------------------------------------------------------------------
    # 1. Zero-Row Finalization Update Tests
    # --------------------------------------------------------------------------
    def test_01_finalization_zero_rows_returns_recovery_finalization_failed(self):
        """
        [CONTROLLED RACE SIMULATION - AUDIT 36 REQUIREMENT 1]
        Scenario:
        1. Original run is claimed by Supervisor A (lease A, recovery ID A).
        2. Recovery pipeline executes, logs completed recovery row with lease A, and returns COMPLETED.
        3. Concurrently, before Supervisor A executes the finalization UPDATE, Supervisor B
           supersedes the lease on the original run (changing lease_owner to lease B).
        4. Supervisor A attempts finalization UPDATE:
           WHERE run_id = ? AND status = 'RECOVERY_IN_PROGRESS' AND recovery_run_id = ? AND lease_owner = ?
           This update affects EXACTLY ZERO ROWS.
        5. Verifies:
           - Scheduler returns status RECOVERY_FINALIZATION_FAILED (NEVER COMPLETED).
           - Includes clear reason that the original run's state or lease was concurrently modified.
           - Supervisor B's lease on the original run remains completely intact.
        """
        scheduler_a = self._create_scheduler()
        orig_run_id = "test_race_orig_run"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": now_iso, "checkpoint_data": json.dumps(checkpoint_data)}

        newer_supervisor_lease = "host_sup_b:9999:supervisor_b_uuid"
        newer_recovery_id = "recovery_supervisor_b_777"

        # Hook get_connection to simulate an exact race between pre-finalization SELECT and finalization UPDATE
        real_get_conn = scheduler_a.db_manager.get_connection

        class InterceptingCursor:
            def __init__(self, real_cursor):
                self._cursor = real_cursor

            def execute(self, sql, params=()):
                if "UPDATE collection_logs" in sql and "status = 'RECOVERED_INTERRUPTED'" in sql:
                    # Concurrent race: another supervisor changes lease_owner right before finalization UPDATE
                    with real_get_conn() as race_conn:
                        race_conn.execute(
                            "UPDATE collection_logs SET lease_owner = ?, recovery_run_id = ? WHERE run_id = ?",
                            (newer_supervisor_lease, newer_recovery_id, orig_run_id)
                        )
                        race_conn.commit()
                return self._cursor.execute(sql, params)

            def __getattr__(self, item):
                return getattr(self._cursor, item)

        class InterceptingConnection:
            def __init__(self, real_conn):
                self._conn = real_conn

            def cursor(self):
                return InterceptingCursor(self._conn.cursor())

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return self._conn.__exit__(exc_type, exc_val, exc_tb)

            def __getattr__(self, item):
                return getattr(self._conn, item)

        def racing_get_conn():
            return InterceptingConnection(real_get_conn())

        scheduler_a.db_manager.get_connection = racing_get_conn

        def race_condition_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            lease = kwargs.get("lease_owner")

            # Supervisor A logs its completed recovery row in SQLite
            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": lease,
                "checkpoint_data": {"completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS", "STAGE_6_REPORT"]}
            })

            return {
                "run_id": rec_id,
                "original_run_id": orig_id,
                "status": "COMPLETED",
                "checkpoint_data": {"resumed_stages": ["STAGE_2_JOBS", "STAGE_6_REPORT"]}
            }

        with patch.object(scheduler_a.pipeline, "execute_daily_pipeline", side_effect=race_condition_pipeline):
            res = scheduler_a.recover_interrupted_run(run_info)

        # 1. Scheduler MUST return RECOVERY_FINALIZATION_FAILED, never COMPLETED
        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED", "Must return RECOVERY_FINALIZATION_FAILED when 0 rows updated")
        self.assertNotEqual(res.get("status"), "COMPLETED", "Must NEVER return COMPLETED when finalization failed")

        # 2. Sanitized error reason explaining zero rows affected
        self.assertIn("affected 0 rows", res.get("error", "").lower())
        self.assertIn("lease was concurrently modified", res.get("error", "").lower())

        # 3. Newer supervisor's lease and state must remain untouched
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT status, lease_owner, recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row["lease_owner"], newer_supervisor_lease, "Newer supervisor's lease must remain intact")
        self.assertEqual(row["recovery_run_id"], newer_recovery_id, "Newer supervisor's recovery ID must remain intact")
        self.assertEqual(row["status"], "RECOVERY_IN_PROGRESS", "Must NOT have been marked RECOVERED_INTERRUPTED")

    def test_02_newer_supervisor_state_and_lease_preserved_on_race(self):
        """
        [CONTROLLED RACE SIMULATION - AUDIT 36 REQUIREMENT 3]
        Confirms that when Supervisor A's finalization fails due to a concurrent lease change,
        Supervisor A does NOT revert the original run to INTERRUPTED, preserving Supervisor B's
        active RECOVERY_IN_PROGRESS state.
        """
        scheduler_a = self._create_scheduler()
        orig_run_id = "test_sup_preserve_orig"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": now_iso, "checkpoint_data": json.dumps(checkpoint_data)}
        newer_lease = "host_sup_c:8888:supervisor_c"

        def race_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            lease = kwargs.get("lease_owner")

            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": lease
            })

            # Reassign to Supervisor C
            conn = self.db_manager.get_connection()
            conn.execute("UPDATE collection_logs SET lease_owner = ? WHERE run_id = ?", (newer_lease, orig_id))
            conn.commit()
            conn.close()
            return {"run_id": rec_id, "status": "COMPLETED"}

        with patch.object(scheduler_a.pipeline, "execute_daily_pipeline", side_effect=race_pipeline):
            res = scheduler_a.recover_interrupted_run(run_info)

        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")

        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status, lease_owner FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        # Crucial check: status is still RECOVERY_IN_PROGRESS for Supervisor C, NOT reverted to INTERRUPTED!
        self.assertEqual(row[0], "RECOVERY_IN_PROGRESS", "Must not revert a newer supervisor's active claim")
        self.assertEqual(row[1], newer_lease)

    # --------------------------------------------------------------------------
    # 2. Pre-Finalization Database State Checks
    # --------------------------------------------------------------------------
    def test_03_recovery_row_mismatched_lease_owner_rejected(self):
        """
        [AUDIT 36 REQUIREMENT 4]
        Validates that if the recovery execution row in collection_logs has a lease_owner
        different from the active recovery owner:
        Pre-finalization check fails, returns RECOVERY_FINALIZATION_FAILED,
        and original run is not marked recovered.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_mismatched_lease_row"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": now_iso, "checkpoint_data": json.dumps(checkpoint_data)}

        def pipeline_with_wrong_lease_owner(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            # Write recovery row with mismatched lease_owner
            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": "rogue_host:999:unauthorized_worker"  # MISMATCH!
            })
            return {"run_id": rec_id, "status": "COMPLETED"}

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=pipeline_with_wrong_lease_owner):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertIn("lease_owner mismatch", res.get("error", ""))

        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertNotEqual(row[0], "RECOVERED_INTERRUPTED")

    def test_04_successful_finalization_when_all_persisted_checks_match(self):
        """
        [AUDIT 36 REQUIREMENT 5]
        Validates that when:
        - Recovery row exists with correct ID, original_run_id, status=COMPLETED, and lease_owner
        - Original row is RECOVERY_IN_PROGRESS with matching recovery_run_id and lease_owner
        - Conditional UPDATE affects exactly 1 row
        - Post-finalization database inspection confirms RECOVERED_INTERRUPTED:
        Scheduler returns status COMPLETED and records success cleanly.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_clean_success_orig"
        checkpoint_data = {"last_completed_stage": "STAGE_2_JOBS", "completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS"]}

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": now_iso, "checkpoint_data": json.dumps(checkpoint_data)}

        def legitimate_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            lease = kwargs.get("lease_owner")

            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": lease,
                "checkpoint_data": {"resumed_stages": ["STAGE_3_GITHUB_METRICS", "STAGE_6_REPORT"]}
            })
            return {"run_id": rec_id, "status": "COMPLETED"}

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=legitimate_pipeline):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertEqual(res.get("status"), "COMPLETED")
        self.assertEqual(res.get("original_run_id"), orig_run_id)

        # Confirm post-finalization DB state
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT status, recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row["status"], "RECOVERED_INTERRUPTED")
        self.assertEqual(row["recovery_run_id"], res.get("run_id"))

    def test_05_missing_recovery_row_rejected_with_finalization_failure(self):
        """
        [AUDIT 36 REQUIREMENT 6]
        Confirms that when the recovery execution row is completely omitted from SQLite,
        recover_interrupted_run returns RECOVERY_FINALIZATION_FAILED.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_missing_row_audit36"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": now_iso, "checkpoint_data": json.dumps(checkpoint_data)}

        # Pipeline returns summary but omits SQLite insert
        with patch.object(scheduler.pipeline, "execute_daily_pipeline", return_value={"run_id": "rec_phantom", "status": "COMPLETED"}):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertIn("does not exist in collection_logs", res.get("error", ""))

        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()
        self.assertEqual(row[0], "INTERRUPTED")

    def test_06_stale_worker_checkpoint_protections_intact(self):
        """
        [AUDIT 36 REQUIREMENT 7]
        Confirms that existing stale worker checkpoint protections in daily_pipeline remain intact.
        """
        pipeline = DailyRollingPipeline(working_db_path=self.temp_db_path, canonical_db_path=self.canonical_db)
        orig_run_id = "test_stale_worker_audit36"
        stale_lease = "host_stale:111:uuid_stale"
        superseding_lease = "host_new:222:uuid_new"
        stale_rec_id = "rec_stale_111"
        superseding_rec_id = "rec_new_222"

        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "RECOVERY_IN_PROGRESS",
            "lease_owner": superseding_lease,
            "recovery_run_id": superseding_rec_id,
            "checkpoint_data": {"last_completed_stage": "STAGE_1_NEWS"}
        })

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with self.assertRaises(PermissionError) as ctx:
                loop.run_until_complete(
                    pipeline.execute_daily_pipeline(
                        execution_type="STAGE_LEVEL_RECOVERY",
                        resume_from_stage="STAGE_2_JOBS",
                        original_run_id=orig_run_id,
                        run_id=stale_rec_id,
                        lease_owner=stale_lease
                    )
                )
            self.assertIn("Stale recovery worker rejected", str(ctx.exception))
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()

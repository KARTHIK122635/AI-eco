"""
Audit 37 Concurrency & Atomic Bidirectional Finalization Tests
==============================================================
Validates the 8 rigorous concurrency requirements for Audit 37:
1. Recovery row changes status after preliminary validation -> zero-row finalization rejected.
2. Recovery row lease_owner changes after preliminary validation -> zero-row finalization rejected.
3. Recovery row original_run_id changes before finalization -> zero-row finalization rejected.
4. Original run lease is superseded before finalization -> zero-row finalization rejected.
5. Recovery row disappears before finalization -> zero-row finalization rejected.
6. Both records remain valid -> atomic conditional update affects 1 row, post-verification succeeds, returns COMPLETED.
7. No newer supervisor state or lease is overwritten on race or failure.
8. Zero-row finalization never returns COMPLETED under any circumstance.
"""

import os
import sys
import json
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


class TestAudit37Concurrency(unittest.TestCase):
    """Rigorous concurrency and atomic finalization test suite for Audit 37."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit37_concurrency_")
        self.temp_db_path = os.path.join(self.temp_dir, "rolling_ai_ecosystem.db")
        self.temp_reports_dir = os.path.join(self.temp_dir, "reports")
        self.temp_exports_dir = os.path.join(self.temp_dir, "exports")
        os.makedirs(self.temp_reports_dir, exist_ok=True)
        os.makedirs(self.temp_exports_dir, exist_ok=True)

        canon_candidates = [
            os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db"),
            os.path.join(WORKSPACE_DIR, "01_DATABASE", "ai_ecosystem.db")
        ]
        self.canonical_db = next((p for p in canon_candidates if os.path.exists(p)), canon_candidates[0])

        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.temp_db_path,
            canonical_db_path=self.canonical_db
        )
        self.db_manager.initialize_schema()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_scheduler(self, stale_timeout: float = 300.0) -> RollingPipelineScheduler:
        return RollingPipelineScheduler(
            working_db_path=self.temp_db_path,
            canonical_db_path=self.canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir,
            stale_lock_timeout=stale_timeout
        )

    def _seed_interrupted_run(self, run_id: str) -> dict:
        start_time_iso = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        run_info = {
            "run_id": run_id,
            "start_time": start_time_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}
        }
        self.db_manager.log_collection_checkpoint(run_info)
        return run_info

    def _setup_intercepting_scheduler(self, on_update_fn):
        """Creates a scheduler whose connection intercepts the finalization UPDATE to execute on_update_fn."""
        scheduler = self._create_scheduler(stale_timeout=300.0)
        real_get_conn = scheduler.db_manager.get_connection

        class InterceptingCursor:
            def __init__(self, real_cur):
                self._cur = real_cur

            def execute(self, sql, params=()):
                if "UPDATE collection_logs" in sql and "status = 'RECOVERED_INTERRUPTED'" in sql:
                    on_update_fn(real_get_conn)
                return self._cur.execute(sql, params)

            def __getattr__(self, name):
                return getattr(self._cur, name)

        class InterceptingConnection:
            def __init__(self, real_c):
                self._conn = real_c

            def cursor(self):
                return InterceptingCursor(self._conn.cursor())

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return self._conn.__exit__(exc_type, exc_val, exc_tb)

            def __getattr__(self, name):
                return getattr(self._conn, name)

        scheduler.db_manager.get_connection = lambda: InterceptingConnection(real_get_conn())
        return scheduler

    def _mock_pipeline_execution(self, scheduler):
        def pipeline_mock(**kwargs):
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
                "checkpoint_data": {"completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS", "STAGE_6_REPORT"]}
            })
            return {
                "run_id": rec_id,
                "original_run_id": orig_id,
                "status": "COMPLETED",
                "checkpoint_data": {"resumed_stages": ["STAGE_2_JOBS", "STAGE_6_REPORT"]}
            }
        return patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=pipeline_mock)

    # --------------------------------------------------------------------------
    # Test 1: Recovery row changes status after preliminary validation
    # --------------------------------------------------------------------------
    def test_01_recovery_row_status_change_blocks_finalization(self):
        orig_run_id = "test_race_rec_status_change"
        run_info = self._seed_interrupted_run(orig_run_id)

        captured_rec_id = []

        def race_status_change(get_conn_fn):
            with get_conn_fn() as conn:
                c = conn.cursor()
                c.execute("SELECT recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
                r = c.fetchone()
                rec_id = r["recovery_run_id"]
                captured_rec_id.append(rec_id)
                # Race: Recovery row changes status to FAILED right before finalization UPDATE
                c.execute("UPDATE collection_logs SET status = 'FAILED' WHERE run_id = ?", (rec_id,))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(race_status_change)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertNotEqual(res.get("status"), "COMPLETED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())

        # Verify DB state: original run not marked RECOVERED_INTERRUPTED
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        self.assertNotEqual(row["status"], "RECOVERED_INTERRUPTED")
        conn.close()

    # --------------------------------------------------------------------------
    # Test 2: Recovery row lease_owner changes after preliminary validation
    # --------------------------------------------------------------------------
    def test_02_recovery_row_lease_owner_change_blocks_finalization(self):
        orig_run_id = "test_race_rec_lease_change"
        run_info = self._seed_interrupted_run(orig_run_id)

        def race_lease_change(get_conn_fn):
            with get_conn_fn() as conn:
                c = conn.cursor()
                c.execute("SELECT recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
                rec_id = c.fetchone()["recovery_run_id"]
                # Race: Recovery row lease_owner modified to unauthorized worker
                c.execute("UPDATE collection_logs SET lease_owner = 'rogue_host:999:unauth' WHERE run_id = ?", (rec_id,))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(race_lease_change)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertNotEqual(res.get("status"), "COMPLETED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())

    # --------------------------------------------------------------------------
    # Test 3: Recovery row original_run_id changes before finalization
    # --------------------------------------------------------------------------
    def test_03_recovery_row_original_run_id_change_blocks_finalization(self):
        orig_run_id = "test_race_orig_pointer_change"
        run_info = self._seed_interrupted_run(orig_run_id)

        def race_pointer_change(get_conn_fn):
            with get_conn_fn() as conn:
                c = conn.cursor()
                c.execute("SELECT recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
                rec_id = c.fetchone()["recovery_run_id"]
                # Race: Recovery row original_run_id changed to point to a different run
                c.execute("UPDATE collection_logs SET original_run_id = 'unrelated_other_run_999' WHERE run_id = ?", (rec_id,))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(race_pointer_change)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertNotEqual(res.get("status"), "COMPLETED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())

    # --------------------------------------------------------------------------
    # Test 4: Original run lease is superseded before finalization
    # --------------------------------------------------------------------------
    def test_04_original_run_lease_superseded_blocks_finalization(self):
        orig_run_id = "test_race_orig_lease_superseded"
        run_info = self._seed_interrupted_run(orig_run_id)
        newer_lease = "host_sup_z:7777:supervisor_z"
        newer_rec_id = "recovery_sup_z_999"

        def race_orig_superseded(get_conn_fn):
            with get_conn_fn() as conn:
                c = conn.cursor()
                # Race: Newer supervisor claims the original run
                c.execute("UPDATE collection_logs SET lease_owner = ?, recovery_run_id = ? WHERE run_id = ?",
                          (newer_lease, newer_rec_id, orig_run_id))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(race_orig_superseded)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertNotEqual(res.get("status"), "COMPLETED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())

        # Verify newer supervisor's lease and recovery ID are preserved untouched
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT lease_owner, recovery_run_id, status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        self.assertEqual(row["lease_owner"], newer_lease)
        self.assertEqual(row["recovery_run_id"], newer_rec_id)
        self.assertEqual(row["status"], "RECOVERY_IN_PROGRESS")
        conn.close()

    # --------------------------------------------------------------------------
    # Test 5: Recovery row disappears before finalization
    # --------------------------------------------------------------------------
    def test_05_recovery_row_deleted_blocks_finalization(self):
        orig_run_id = "test_race_rec_deleted"
        run_info = self._seed_interrupted_run(orig_run_id)

        def race_rec_deleted(get_conn_fn):
            with get_conn_fn() as conn:
                c = conn.cursor()
                c.execute("SELECT recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
                rec_id = c.fetchone()["recovery_run_id"]
                # Race: Recovery row is deleted from collection_logs
                c.execute("DELETE FROM collection_logs WHERE run_id = ?", (rec_id,))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(race_rec_deleted)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertNotEqual(res.get("status"), "COMPLETED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())

    # --------------------------------------------------------------------------
    # Test 6: Both records remain valid and finalization succeeds
    # --------------------------------------------------------------------------
    def test_06_both_records_valid_finalization_succeeds_with_post_verification(self):
        orig_run_id = "test_clean_success_audit37"
        run_info = self._seed_interrupted_run(orig_run_id)

        scheduler = self._create_scheduler(stale_timeout=300.0)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "COMPLETED")
        rec_id = res.get("run_id")
        self.assertIsNotNone(rec_id)

        # Post-finalization database verification
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # 1. Original run must be RECOVERED_INTERRUPTED pointing to recovery run ID
        c.execute("SELECT status, recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row_orig = c.fetchone()
        self.assertIsNotNone(row_orig)
        self.assertEqual(row_orig["status"], "RECOVERED_INTERRUPTED")
        self.assertEqual(row_orig["recovery_run_id"], rec_id)

        # 2. Recovery run must be COMPLETED pointing to original run ID
        c.execute("SELECT status, original_run_id, lease_owner FROM collection_logs WHERE run_id = ?", (rec_id,))
        row_rec = c.fetchone()
        self.assertIsNotNone(row_rec)
        self.assertEqual(row_rec["status"], "COMPLETED")
        self.assertEqual(row_rec["original_run_id"], orig_run_id)
        self.assertIsNotNone(row_rec["lease_owner"])
        self.assertTrue(len(row_rec["lease_owner"]) > 5)
        conn.close()

    # --------------------------------------------------------------------------
    # Test 7: No newer supervisor state is overwritten
    # --------------------------------------------------------------------------
    def test_07_no_newer_supervisor_state_overwritten(self):
        orig_run_id = "test_protect_newer_sup_audit37"
        run_info = self._seed_interrupted_run(orig_run_id)
        newer_lease = "host_sup_omega:1111:supervisor_omega"
        newer_rec_id = "recovery_sup_omega_456"

        scheduler = self._create_scheduler(stale_timeout=300.0)

        # Hook pipeline mock to simulate a concurrent takeover while pipeline runs
        def takeover_pipeline(**kwargs):
            rec_id = kwargs.get("run_id")
            orig_id = kwargs.get("original_run_id")
            # Another supervisor takes over the claim
            conn = sqlite3.connect(self.temp_db_path)
            conn.execute("""
                UPDATE collection_logs
                SET lease_owner = ?, recovery_run_id = ?, status = 'RECOVERY_IN_PROGRESS'
                WHERE run_id = ?
            """, (newer_lease, newer_rec_id, orig_id))
            conn.commit()
            conn.close()

            # First worker writes its row
            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": kwargs.get("lease_owner")
            })
            return {"run_id": rec_id, "original_run_id": orig_id, "status": "COMPLETED"}

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=takeover_pipeline):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")

        # Verify newer supervisor's claim is completely uncorrupted
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT lease_owner, recovery_run_id, status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        self.assertEqual(row["lease_owner"], newer_lease)
        self.assertEqual(row["recovery_run_id"], newer_rec_id)
        self.assertEqual(row["status"], "RECOVERY_IN_PROGRESS")
        conn.close()

    # --------------------------------------------------------------------------
    # Test 8: Zero-row finalization never returns COMPLETED
    # --------------------------------------------------------------------------
    def test_08_zero_row_finalization_never_returns_completed(self):
        orig_run_id = "test_never_completed_audit37"
        run_info = self._seed_interrupted_run(orig_run_id)

        # Force c.rowcount = 0 by intentionally setting original run to INTERRUPTED out of band
        def force_zero_rows(get_conn_fn):
            with get_conn_fn() as conn:
                conn.execute("UPDATE collection_logs SET status = 'CANCELLED' WHERE run_id = ?", (orig_run_id,))
                conn.commit()

        scheduler = self._setup_intercepting_scheduler(force_zero_rows)
        with self._mock_pipeline_execution(scheduler):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIsNotNone(res)
        self.assertNotEqual(res.get("status"), "COMPLETED", "Must NEVER return COMPLETED when zero rows updated")
        self.assertEqual(res.get("status"), "RECOVERY_FINALIZATION_FAILED")
        self.assertIn("affected 0 rows", res.get("error", "").lower())


if __name__ == "__main__":
    unittest.main()

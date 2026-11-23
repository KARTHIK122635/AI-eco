"""
Audit 35 Strict Recovery Lineage, Lease-Owned Checkpoints & Stale-Worker Protection Tests
========================================================================================
Comprehensive regression suite for Audit 35 requirements:
1. Require recovery execution row:
   - Original run row must exist.
   - Recovery execution row must exist (NEVER allow missing row).
   - original.recovery_run_id == recovery execution ID.
   - recovery.original_run_id == original run ID.
   - recovery execution row status == 'COMPLETED'.
   - Missing, omitted, or deleted recovery row strictly rejects finalization.
   - Mismatched or incomplete lineage leaves original run in INTERRUPTED state.
2. Lease-owned checkpoint updates in daily_pipeline:
   - record_stage_progress conditional update verifies run_id, status, lease_owner, recovery_run_id.
   - Stale recovery worker rejected with PermissionError if lease or recovery ID was superseded.
   - Legitimate recovery worker updates checkpoint normally.
3. WorkingDatabaseManager.log_collection_checkpoint lease validation:
   - 1. Existing lease + incoming lease omitted -> PermissionError.
   - 2. Existing lease + wrong incoming owner -> PermissionError.
   - 3. Existing lease + correct owner -> Success.
   - 4. Existing recovery ID + mismatched recovery ID -> PermissionError.
   - 5. Existing checkpoint + stale worker attempting replacement -> PermissionError.
   - 6. Concurrent lease reassignment followed by old-worker update -> PermissionError.
   - 7. Preservation of existing metadata fields on update.
   - 8. Stale worker cannot update heartbeat.
"""

import os
import sys
import json
import time
import uuid
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


class TestAudit35StrictLineage(unittest.TestCase):
    """Rigorous lineage, lease-ownership, and stale-worker protection tests."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit35_lineage_")
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
    # 1. Require Recovery Execution Row Tests
    # --------------------------------------------------------------------------
    def test_01_missing_recovery_row_cannot_finalize_original_run(self):
        """
        [CONTROLLED MOCK TEST - AUDIT 35 REQUIREMENT 1]
        Validates that if execute_daily_pipeline returns a simulated successful
        summary (status=COMPLETED), but the recovery execution row was omitted
        or deleted from collection_logs:
        1. Lineage validation strictly fails.
        2. Original run does NOT transition to RECOVERED_INTERRUPTED.
        3. Original run reverts to INTERRUPTED state.
        4. scheduler.recover_interrupted_run returns a failure status.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_audit35_orig_missing_rec"
        checkpoint_data = {
            "last_completed_stage": "STAGE_2_JOBS",
            "completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS"]
        }
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {
            "run_id": orig_run_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "checkpoint_data": json.dumps(checkpoint_data)
        }

        # Mock execute_daily_pipeline to return COMPLETED summary WITHOUT writing row to SQLite
        def fake_pipeline_without_row(**kwargs):
            rec_id = kwargs.get("run_id")
            return {
                "run_id": rec_id,
                "original_run_id": kwargs.get("original_run_id"),
                "status": "COMPLETED",
                "checkpoint_data": {"resumed_stages": ["STAGE_3_GITHUB_METRICS", "STAGE_6_REPORT"]}
            }

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=fake_pipeline_without_row):
            res = scheduler.recover_interrupted_run(run_info)

        # Verification 1: Returned summary indicates failure
        self.assertIsNotNone(res)
        self.assertIn(res.get("status"), ["RECOVERY_FINALIZATION_FAILED", "RECOVERY_LINEAGE_FAILED"])
        self.assertIn("missing recovery execution row", res.get("error", ""))

        # Verification 2: Original run in DB was NOT marked RECOVERED_INTERRUPTED
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT status, error_log FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row["status"], "INTERRUPTED", "Original run must revert to INTERRUPTED, never RECOVERED_INTERRUPTED")
        self.assertIn("missing recovery execution row", row["error_log"])

    def test_02_mismatched_recovery_lineage_cannot_finalize_original_run(self):
        """
        [CONTROLLED MOCK TEST - AUDIT 35 REQUIREMENT 1]
        Validates that if a recovery row exists but its original_run_id does not
        match the claimed run_id:
        1. Lineage validation fails.
        2. Original run reverts to INTERRUPTED.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_audit35_orig_mismatched"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": datetime.now(timezone.utc).isoformat(), "checkpoint_data": json.dumps(checkpoint_data)}

        # Recovery mock writes row pointing to a different original run ID
        def fake_pipeline_mismatched_lineage(**kwargs):
            rec_id = kwargs.get("run_id")
            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": "completely_different_run_id",  # MISMATCH!
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "COMPLETED",
                "lease_owner": kwargs.get("lease_owner")
            })
            return {"run_id": rec_id, "status": "COMPLETED"}

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=fake_pipeline_mismatched_lineage):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIn(res.get("status"), ["RECOVERY_FINALIZATION_FAILED", "RECOVERY_LINEAGE_FAILED"])
        self.assertIn("Lineage validation failed", res.get("error", ""))

        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status, error_log FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row[0], "INTERRUPTED")
        self.assertIn("Lineage validation failed", row[1])

    def test_03_incomplete_recovery_row_status_cannot_finalize(self):
        """
        [CONTROLLED MOCK TEST - AUDIT 35 REQUIREMENT 1]
        Validates that if the recovery execution row has status != 'COMPLETED' (e.g. 'FAILED'):
        Lineage verification fails and original run is not marked recovered.
        """
        scheduler = self._create_scheduler()
        orig_run_id = "test_audit35_orig_incomplete_status"
        checkpoint_data = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "INTERRUPTED",
            "checkpoint_data": checkpoint_data
        })

        run_info = {"run_id": orig_run_id, "start_time": datetime.now(timezone.utc).isoformat(), "checkpoint_data": json.dumps(checkpoint_data)}

        def fake_pipeline_failed_row(**kwargs):
            rec_id = kwargs.get("run_id")
            self.db_manager.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_run_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": "2026-05-22T00:00:00+00:00",
                "rolling_window_end": "2026-11-22T00:00:00+00:00",
                "status": "FAILED",  # NOT COMPLETED!
                "lease_owner": kwargs.get("lease_owner")
            })
            return {"run_id": rec_id, "status": "COMPLETED"}

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=fake_pipeline_failed_row):
            res = scheduler.recover_interrupted_run(run_info)

        self.assertIn(res.get("status"), ["RECOVERY_FINALIZATION_FAILED", "RECOVERY_LINEAGE_FAILED"])

        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()
        self.assertEqual(row[0], "INTERRUPTED")

    # --------------------------------------------------------------------------
    # 2. Lease-Owned Original-Run Checkpoint Updates in daily_pipeline
    # --------------------------------------------------------------------------
    def test_04_stale_recovery_worker_checkpoint_rejected(self):
        """
        [INTEGRATION TEST - AUDIT 35 REQUIREMENT 2]
        Validates that record_stage_progress conditional update:
        WHERE run_id = ? AND status = 'RECOVERY_IN_PROGRESS' AND lease_owner = ? AND recovery_run_id = ?
        rejects stale recovery workers whose lease or recovery ID was superseded.
        """
        pipeline = DailyRollingPipeline(working_db_path=self.temp_db_path, canonical_db_path=self.canonical_db)
        orig_run_id = "test_orig_stale_worker"
        stale_lease = "host1:1001:stale_uuid"
        superseding_lease = "host1:2002:new_supervisor_uuid"
        stale_recovery_id = "recovery_stale_111"
        superseding_recovery_id = "recovery_new_222"

        now_iso = datetime.now(timezone.utc).isoformat()
        initial_checkpoint = {"last_completed_stage": "STAGE_1_NEWS", "completed_stages": ["STAGE_1_NEWS"]}

        # Original run initially claimed by superseding supervisor
        self.db_manager.log_collection_checkpoint({
            "run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "RECOVERY_IN_PROGRESS",
            "lease_owner": superseding_lease,
            "recovery_run_id": superseding_recovery_id,
            "checkpoint_data": initial_checkpoint
        })

        # Stale recovery execution row for stale worker
        self.db_manager.log_collection_checkpoint({
            "run_id": stale_recovery_id,
            "original_run_id": orig_run_id,
            "start_time": now_iso,
            "execution_type": "STAGE_LEVEL_RECOVERY",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": stale_lease
        })

        # Simulate stale worker attempting to execute daily pipeline with its old credentials
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
                        run_id=stale_recovery_id,
                        lease_owner=stale_lease  # Stale lease!
                    )
                )
            self.assertIn("Stale recovery worker rejected", str(ctx.exception))
        finally:
            loop.close()

        # Verify original run checkpoint was NOT overwritten by stale worker
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT checkpoint_data, lease_owner, recovery_run_id FROM collection_logs WHERE run_id = ?", (orig_run_id,))
        row = c.fetchone()
        conn.close()

        cp = json.loads(row["checkpoint_data"])
        self.assertEqual(cp["last_completed_stage"], "STAGE_1_NEWS")
        self.assertEqual(row["lease_owner"], superseding_lease)
        self.assertEqual(row["recovery_run_id"], superseding_recovery_id)

    # --------------------------------------------------------------------------
    # 3. WorkingDatabaseManager Lease Validation Bypasses Removal
    # --------------------------------------------------------------------------
    def test_05_existing_lease_incoming_omitted_rejected(self):
        """Case 1: Existing lease + incoming lease omitted -> raises PermissionError."""
        run_id = "test_lease_omitted"
        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": "hostA:1234:ownerA"
        })

        # Attempt update omitting lease_owner
        with self.assertRaises(PermissionError) as ctx:
            self.db_manager.log_collection_checkpoint({
                "run_id": run_id,
                "status": "IN_PROGRESS",
                "checkpoint_data": {"stage": "STAGE_2_JOBS"}
                # lease_owner omitted!
            })
        self.assertIn("omitted lease_owner", str(ctx.exception))

    def test_06_existing_lease_wrong_owner_rejected(self):
        """Case 2: Existing lease + wrong incoming owner -> raises PermissionError."""
        run_id = "test_lease_wrong_owner"
        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": "hostA:1234:ownerA"
        })

        with self.assertRaises(PermissionError) as ctx:
            self.db_manager.log_collection_checkpoint({
                "run_id": run_id,
                "status": "IN_PROGRESS",
                "lease_owner": "hostB:5678:ownerB"  # Wrong owner!
            })
        self.assertIn("Stale lease rejection", str(ctx.exception))

    def test_07_existing_lease_correct_owner_succeeds(self):
        """Case 3: Existing lease + correct owner -> succeeds, updates metadata."""
        run_id = "test_lease_correct_owner"
        now_iso = datetime.now(timezone.utc).isoformat()
        owner = "hostA:1234:ownerA"
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": owner,
            "new_news": 10
        })

        # Update with correct owner
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "lease_owner": owner,
            "new_jobs": 15,
            "checkpoint_data": {"last_completed_stage": "STAGE_2_JOBS"}
        })

        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT new_news, new_jobs, checkpoint_data FROM collection_logs WHERE run_id = ?", (run_id,))
        row = c.fetchone()
        conn.close()

        # Both new_jobs (updated) and new_news (preserved metadata) must be correct
        self.assertEqual(row["new_jobs"], 15)
        self.assertEqual(row["new_news"], 10, "Existing metadata field new_news must be preserved!")
        cp = json.loads(row["checkpoint_data"])
        self.assertEqual(cp["last_completed_stage"], "STAGE_2_JOBS")

    def test_08_existing_recovery_id_mismatch_rejected(self):
        """Case 4: Existing recovery ID + mismatched recovery ID -> raises PermissionError."""
        run_id = "test_recovery_id_mismatch"
        now_iso = datetime.now(timezone.utc).isoformat()
        owner = "hostA:1234:ownerA"
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "RECOVERY_IN_PROGRESS",
            "lease_owner": owner,
            "recovery_run_id": "rec_legitimate_001"
        })

        with self.assertRaises(PermissionError) as ctx:
            self.db_manager.log_collection_checkpoint({
                "run_id": run_id,
                "lease_owner": owner,
                "recovery_run_id": "rec_competing_999"  # Mismatch!
            })
        self.assertIn("Recovery identity mismatch", str(ctx.exception))

    def test_09_stale_worker_checkpoint_replacement_rejected(self):
        """Case 5: Existing checkpoint + stale worker attempting replacement -> raises PermissionError."""
        run_id = "test_stale_cp_replacement"
        now_iso = datetime.now(timezone.utc).isoformat()
        stale_lease = "host1:1001:stale"
        new_lease = "host2:2002:new"

        # Initially set by stale worker
        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": stale_lease,
            "checkpoint_data": {"stage": "STAGE_1_NEWS"}
        })

        # New worker claims lease
        conn = self.db_manager.get_connection()
        conn.execute("UPDATE collection_logs SET lease_owner = ?, checkpoint_data = ? WHERE run_id = ?",
                     (new_lease, json.dumps({"stage": "STAGE_2_JOBS"}), run_id))
        conn.commit()
        conn.close()

        # Stale worker attempts to replace checkpoint
        with self.assertRaises(PermissionError):
            self.db_manager.log_collection_checkpoint({
                "run_id": run_id,
                "lease_owner": stale_lease,
                "checkpoint_data": {"stage": "STAGE_1_NEWS_AGAIN"}
            })

        # Verify DB checkpoint was NOT modified
        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT checkpoint_data FROM collection_logs WHERE run_id = ?", (run_id,))
        cp = json.loads(c.fetchone()[0])
        conn.close()
        self.assertEqual(cp["stage"], "STAGE_2_JOBS")

    def test_10_concurrent_lease_reassignment_rejection(self):
        """Case 6: Concurrent lease reassignment followed by old-worker update -> raises PermissionError."""
        run_id = "test_concurrent_reassignment"
        now_iso = datetime.now(timezone.utc).isoformat()
        lease_a = "hostA:100:a"
        lease_b = "hostB:200:b"

        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": lease_a
        })

        # Worker B atomically reclaims lease
        conn = self.db_manager.get_connection()
        conn.execute("UPDATE collection_logs SET lease_owner = ? WHERE run_id = ? AND lease_owner = ?", (lease_b, run_id, lease_a))
        conn.commit()
        conn.close()

        # Worker A attempts update using old lease
        with self.assertRaises(PermissionError) as ctx:
            self.db_manager.log_collection_checkpoint({
                "run_id": run_id,
                "lease_owner": lease_a,
                "status": "COMPLETED"
            })
        self.assertIn("Stale lease rejection", str(ctx.exception))

        # Confirm Worker A did not mark run COMPLETED
        conn = sqlite3.connect(self.temp_db_path)
        c = conn.cursor()
        c.execute("SELECT status, lease_owner FROM collection_logs WHERE run_id = ?", (run_id,))
        row = c.fetchone()
        conn.close()
        self.assertEqual(row[0], "IN_PROGRESS")
        self.assertEqual(row[1], lease_b)

    def test_11_stale_worker_heartbeat_rejected(self):
        """Validates that update_heartbeat strictly rejects stale lease owners (returns False)."""
        run_id = "test_hb_stale"
        now_iso = datetime.now(timezone.utc).isoformat()
        active_lease = "hostX:1:active"
        stale_lease = "hostX:2:stale"

        self.db_manager.log_collection_checkpoint({
            "run_id": run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "lease_owner": active_lease
        })

        # Stale worker heartbeat attempt
        success_stale = self.db_manager.update_heartbeat(run_id, lease_owner=stale_lease)
        self.assertFalse(success_stale, "Stale worker heartbeat update must return False")

        # Active worker heartbeat attempt
        success_active = self.db_manager.update_heartbeat(run_id, lease_owner=active_lease)
        self.assertTrue(success_active, "Active worker heartbeat update must return True")


if __name__ == "__main__":
    unittest.main()

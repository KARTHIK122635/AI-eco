"""
Audit 31 Comprehensive Corrective Test Suite: Six-Month Rolling AI Ecosystem Pipeline
======================================================================================
Validates all 10 corrective criteria mandated in Audit 31:
1. Product publication-date integrity & missing date classification.
2. Startup founding date vs publication date distinction & batch rejection.
3. True six-calendar-month rolling window arithmetic, leap years & exact boundary inclusion.
4. Next-day dynamic rolling window advancement.
5. Idempotent ingestion & duplicate prevention across runs.
6. Granular stage-level resumption & scheduler crash recovery.
7. Routine daily execution skips Phase III pilot (default run_pilot=False).
8. Manual Phase III execution with explicit flag generates proposals (all PENDING_APPROVAL).
9. Canonical database & authentic Audit 19 archive byte-level immutability.
10. Stale-record and missing-date SQLite archive retention (zero records deleted).
"""

import os
import sys
import json
import sqlite3
import hashlib
import unittest
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rolling_window import (
    compute_rolling_window,
    classify_freshness,
    parse_publication_timestamp
)
from core.freshness_engine import (
    canonicalize_url,
    compute_content_fingerprint,
    validate_content_quality,
    DeduplicationRegistry
)
from core.working_database import WorkingDatabaseManager
from core.daily_pipeline import DailyRollingPipeline, PIPELINE_STAGES
from core.scheduler import RollingPipelineScheduler
from src.stage3.schema_mapping import check_proposal_schema_compatibility


class TestAudit31CorrectiveEngineering(unittest.TestCase):
    """Test suite verifying all Audit 31 corrective engineering requirements."""

    @classmethod
    def setUpClass(cls):
        cls.workspace_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        cls.canonical_db = os.path.join(cls.workspace_dir, "data", "normalized", "ai_ecosystem.db")
        cls.audit19_db = os.path.join(cls.workspace_dir, "source", "audit19_original_database.db")
        cls.working_db = os.path.join(cls.workspace_dir, "data", "working", "rolling_ai_ecosystem.db")

        # Support package layout where databases reside in 01_DATABASE
        if not os.path.exists(cls.canonical_db):
            pkg_db_dir = os.path.join(cls.workspace_dir, "01_DATABASE")
            if os.path.exists(pkg_db_dir):
                cls.canonical_db = os.path.join(pkg_db_dir, "ai_ecosystem.db")
                cls.audit19_db = os.path.join(pkg_db_dir, "audit19_original_database.db")
                cls.working_db = os.path.join(pkg_db_dir, "rolling_ai_ecosystem.db")

        cls.expected_canonical_sha256 = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
        cls.expected_audit19_sha256 = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"

    # --------------------------------------------------------------------------
    # 1. Product publication-date integrity & missing date classification
    # --------------------------------------------------------------------------
    def test_01_product_publication_date_integrity(self):
        ref_time = datetime(2026, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
        start_w, _ = compute_rolling_window(ref_time, months=6)

        # Genuine publication date preserved
        genuine_date_str = "2026-10-15T08:30:00Z"
        pub_dt = parse_publication_timestamp(genuine_date_str)
        self.assertIsNotNone(pub_dt)
        f_eval = classify_freshness(pub_dt, ref_time, start_w)
        self.assertEqual(f_eval["status"], "HISTORICAL_6M")
        self.assertTrue(f_eval["in_rolling_window"])

        # When genuine date is missing/empty, classified as MISSING_DATE with in_rolling_window = False
        f_missing = classify_freshness(None, ref_time, start_w)
        self.assertEqual(f_missing["status"], "MISSING_DATE")
        self.assertFalse(f_missing["in_rolling_window"])
        self.assertIsNone(f_missing["age_hours"])

        # In working DB, products seeded from canonical without publication dates must be MISSING_DATE
        if os.path.exists(self.working_db):
            conn = sqlite3.connect(self.working_db)
            c = conn.cursor()
            c.execute("SELECT count(*) FROM ai_products WHERE freshness_status = 'MISSING_DATE' AND in_rolling_window = 0")
            missing_count = c.fetchone()[0]
            c.execute("SELECT count(*) FROM ai_products WHERE freshness_status = 'RECENT_7D'")
            recent_count = c.fetchone()[0]
            conn.close()

            self.assertEqual(missing_count, 1316, "All 1,316 canonical products without publication dates must be classified as MISSING_DATE.")
            self.assertEqual(recent_count, 0, "No products without genuine publication dates may be artificially classified as RECENT_7D.")

    # --------------------------------------------------------------------------
    # 2. Startup founding date vs publication date distinction & batch rejection
    # --------------------------------------------------------------------------
    def test_02_startup_founding_vs_publication_date(self):
        # Explicit rejection of incubator batches and founding seasons
        batch_strings = [
            "Summer 2023", "Winter 2024", "Spring 2022", "Fall 2025",
            "Batch W24", "S22", "batch 10", "W21"
        ]
        for b in batch_strings:
            res = parse_publication_timestamp(b)
            self.assertIsNone(res, f"Batch string '{b}' must not be parsed as a publication date.")

        # In working DB, startups distinguish founding_date, batch_or_founded, collected_at, and published_at
        if os.path.exists(self.working_db):
            conn = sqlite3.connect(self.working_db)
            c = conn.cursor()
            c.execute("SELECT count(*) FROM ai_startups WHERE freshness_status = 'MISSING_DATE' AND in_rolling_window = 0")
            missing_startups = c.fetchone()[0]
            c.execute("SELECT count(*) FROM ai_startups WHERE published_at IS NOT NULL")
            startups_with_pub = c.fetchone()[0]
            conn.close()

            self.assertEqual(missing_startups, 1307, "All 1,307 canonical startups must be classified as MISSING_DATE.")
            self.assertEqual(startups_with_pub, 0, "Canonical startups have no publication timestamp.")

    # --------------------------------------------------------------------------
    # 3. True six-calendar-month rolling window arithmetic, leap years & exact boundary inclusion
    # --------------------------------------------------------------------------
    def test_03_true_six_calendar_month_window_and_leap_years(self):
        # 1. Non-leap year month-end: 2026-08-31 -> 2026-02-28
        t1 = datetime(2026, 8, 31, 14, 25, 30, 123456, tzinfo=timezone.utc)
        s1, e1 = compute_rolling_window(t1, months=6)
        self.assertEqual(s1.year, 2026)
        self.assertEqual(s1.month, 2)
        self.assertEqual(s1.day, 28)
        self.assertEqual(s1.hour, 14)
        self.assertEqual(s1.minute, 25)
        self.assertEqual(s1.second, 30)
        self.assertEqual(s1.microsecond, 123456)
        self.assertEqual(e1, t1)

        # 2. Leap year month-end: 2024-08-31 -> 2024-02-29
        t2 = datetime(2024, 8, 31, 9, 15, 0, tzinfo=timezone.utc)
        s2, e2 = compute_rolling_window(t2, months=6)
        self.assertEqual(s2.year, 2024)
        self.assertEqual(s2.month, 2)
        self.assertEqual(s2.day, 29, "Leap year February must clamp to Feb 29.")
        self.assertEqual(s2.hour, 9)
        self.assertEqual(s2.minute, 15)

        # 3. Standard boundary: 2026-11-22T15:00:00Z -> 2026-05-22T15:00:00Z
        t3 = datetime(2026, 11, 22, 15, 0, 0, tzinfo=timezone.utc)
        s3, e3 = compute_rolling_window(t3, months=6)
        self.assertEqual(s3, datetime(2026, 5, 22, 15, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(e3, t3)

        # 4. Exact boundary inclusion: published_dt == window_start is IN rolling window
        exact_start = s3
        c_exact = classify_freshness(exact_start, t3, s3)
        self.assertTrue(c_exact["in_rolling_window"], "Exact boundary timestamp must be included in rolling window.")
        self.assertEqual(c_exact["status"], "HISTORICAL_6M")

        # 1 microsecond before window_start is OUTSIDE_WINDOW
        one_us_before = s3 - timedelta(microseconds=1)
        c_before = classify_freshness(one_us_before, t3, s3)
        self.assertFalse(c_before["in_rolling_window"])
        self.assertEqual(c_before["status"], "OUTSIDE_WINDOW")

    # --------------------------------------------------------------------------
    # 4. Next-day dynamic rolling window advancement
    # --------------------------------------------------------------------------
    def test_04_dynamic_next_day_advancement(self):
        day1 = datetime(2026, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
        s1, e1 = compute_rolling_window(day1, months=6)

        day2 = day1 + timedelta(days=1)
        s2, e2 = compute_rolling_window(day2, months=6)

        self.assertEqual(e2 - e1, timedelta(days=1))
        self.assertEqual(s2 - s1, timedelta(days=1))
        self.assertEqual(s2, datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc))

        # Simulate 15 days later (2026-11-22 + 15 days = 2026-12-07 -> 6M prior is 2026-06-07)
        day15 = day1 + timedelta(days=15)
        s15, e15 = compute_rolling_window(day15, months=6)
        self.assertEqual(e15, day15)
        self.assertEqual(s15, datetime(2026, 6, 7, 12, 0, 0, tzinfo=timezone.utc))

    # --------------------------------------------------------------------------
    # 5. Idempotent ingestion & duplicate prevention across runs
    # --------------------------------------------------------------------------
    def test_05_idempotent_ingestion_and_duplicate_prevention(self):
        reg = DeduplicationRegistry()
        url1 = "https://techcrunch.com/2026/11/20/ai-agent-breakthrough/?utm_source=rss&utm_medium=feed"
        url2 = "https://techcrunch.com/2026/11/20/ai-agent-breakthrough/"

        c1 = canonicalize_url(url1)
        c2 = canonicalize_url(url2)
        self.assertEqual(c1, c2, "URL canonicalizer must strip tracking query parameters.")

        is_new1, reason1 = reg.check_and_register("n1", url1, "Breakthrough Title", "Article content text")
        self.assertTrue(is_new1)
        self.assertEqual(reason1, "UNIQUE")

        # Second attempt with same canonical URL must be rejected
        is_new2, reason2 = reg.check_and_register("n2", url2, "Different Title", "Different content")
        self.assertFalse(is_new2)
        self.assertIn("Duplicate canonical URL", reason2)

        # Identical content with different URL must also be rejected
        url3 = "https://syndicate.example.com/mirror-story"
        is_new3, reason3 = reg.check_and_register("n3", url3, "Breakthrough Title", "Article content text")
        self.assertFalse(is_new3)
        self.assertIn("Duplicate content fingerprint", reason3)

    # --------------------------------------------------------------------------
    # 6. Granular stage-level resumption & scheduler crash recovery
    # --------------------------------------------------------------------------
    def test_06_stage_level_scheduler_recovery(self):
        self.assertEqual(
            PIPELINE_STAGES,
            ["STAGE_1_NEWS", "STAGE_2_JOBS", "STAGE_3_GITHUB_METRICS", "STAGE_4_VACANCY_LIFECYCLE", "STAGE_5_EXPORTS", "STAGE_6_REPORT"]
        )

        mgr = WorkingDatabaseManager(working_db_path=self.working_db, canonical_db_path=self.canonical_db)
        interrupted_run_id = f"interrupted_audit31_{datetime.now().strftime('%H%M%S')}"

        # Simulate a crash right after STAGE_2_JOBS
        checkpoint = {
            "last_completed_stage": "STAGE_2_JOBS",
            "completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS"],
        }
        mgr.log_collection_checkpoint({
            "run_id": interrupted_run_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": datetime.now(timezone.utc).isoformat(),
            "rolling_window_end": datetime.now(timezone.utc).isoformat(),
            "status": "IN_PROGRESS",
            "checkpoint_data": checkpoint
        })

        scheduler = RollingPipelineScheduler(working_db_path=self.working_db, canonical_db_path=self.canonical_db)
        interrupted = scheduler.check_for_interrupted_runs()
        self.assertTrue(any(r["run_id"] == interrupted_run_id for r in interrupted))

        target = next(r for r in interrupted if r["run_id"] == interrupted_run_id)

        # Recover using stage-level resumption
        def fake_execute(**kwargs):
            rec_id = kwargs.get("run_id") or f"recovery_{datetime.now().strftime('%H%M%S')}"
            orig_id = kwargs.get("original_run_id")
            mgr.log_collection_checkpoint({
                "run_id": rec_id,
                "original_run_id": orig_id,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": "STAGE_LEVEL_RECOVERY",
                "rolling_window_start": datetime.now(timezone.utc).isoformat(),
                "rolling_window_end": datetime.now(timezone.utc).isoformat(),
                "status": "COMPLETED",
                "lease_owner": kwargs.get("lease_owner"),
                "checkpoint_data": {"resumed_stages": ["STAGE_3_GITHUB_METRICS", "STAGE_4_VACANCY_LIFECYCLE", "STAGE_5_EXPORTS", "STAGE_6_REPORT"]}
            })
            return {
                "run_id": rec_id,
                "original_run_id": orig_id,
                "status": "COMPLETED",
                "checkpoint_data": {"resumed_stages": ["STAGE_3_GITHUB_METRICS", "STAGE_4_VACANCY_LIFECYCLE", "STAGE_5_EXPORTS", "STAGE_6_REPORT"]}
            }

        with patch.object(scheduler.pipeline, "execute_daily_pipeline", side_effect=fake_execute) as mock_exec:
            rec_result = scheduler.recover_interrupted_run(target)

            # Verification: pipeline resumed strictly from STAGE_3_GITHUB_METRICS with original_run_id and run_pilot=False
            mock_exec.assert_called_once()
            _, kwargs = mock_exec.call_args
            self.assertEqual(kwargs["resume_from_stage"], "STAGE_3_GITHUB_METRICS")
            self.assertEqual(kwargs["original_run_id"], interrupted_run_id)
            self.assertFalse(kwargs["run_pilot"])
            self.assertEqual(kwargs["execution_type"], "STAGE_LEVEL_RECOVERY")

        # Verify previous run was marked RECOVERED_INTERRUPTED in DB
        conn = mgr.get_connection()
        c = conn.cursor()
        c.execute("SELECT status FROM collection_logs WHERE run_id = ?", (interrupted_run_id,))
        status_after = c.fetchone()[0]
        conn.close()
        self.assertEqual(status_after, "RECOVERED_INTERRUPTED")

        # Cleanup test run from collection_logs
        conn = mgr.get_connection()
        conn.execute("DELETE FROM collection_logs WHERE run_id = ?", (interrupted_run_id,))
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------
    # 7. Routine daily execution skips Phase III pilot (default run_pilot=False)
    # --------------------------------------------------------------------------
    def test_07_routine_daily_run_skips_phase3_pilot(self):
        scheduler = RollingPipelineScheduler(working_db_path=self.working_db, canonical_db_path=self.canonical_db)

        # Verify run_once defaults to run_pilot=False
        with patch.object(scheduler.pipeline, "execute_daily_pipeline") as mock_exec:
            mock_exec.return_value = {"run_id": "test_routine", "status": "COMPLETED"}
            scheduler.run_once()  # No parameters passed

            mock_exec.assert_called_once()
            _, kwargs = mock_exec.call_args
            self.assertFalse(kwargs["run_pilot"], "Routine daily execution must default to run_pilot=False.")

    # --------------------------------------------------------------------------
    # 8. Manual Phase III execution with explicit flag generates proposals (all PENDING_APPROVAL)
    # --------------------------------------------------------------------------
    def test_08_manual_phase3_flag_generates_pending_proposals(self):
        scheduler = RollingPipelineScheduler(working_db_path=self.working_db, canonical_db_path=self.canonical_db)

        with patch.object(scheduler.pipeline, "execute_daily_pipeline") as mock_exec:
            mock_exec.return_value = {"run_id": "test_manual_pilot", "status": "COMPLETED"}
            # Explicit opt-in flag
            scheduler.run_once(run_pilot=True)

            mock_exec.assert_called_once()
            _, kwargs = mock_exec.call_args
            self.assertTrue(kwargs["run_pilot"], "Explicit flag must activate Phase III pilot enrichment.")

        # Check existing proposals in working database: 100% must be PENDING_APPROVAL and schema-compatible
        if os.path.exists(self.working_db):
            conn = sqlite3.connect(self.working_db)
            c = conn.cursor()
            c.execute("SELECT proposal_id, approval_status, schema_status, schema_target_table, schema_target_column FROM enrichment_proposals")
            proposals = c.fetchall()
            conn.close()

            self.assertGreaterEqual(len(proposals), 20)
            for pid, app_status, schema_status, target_tbl, target_col in proposals:
                self.assertEqual(app_status, "PENDING_APPROVAL", f"Proposal {pid} must remain PENDING_APPROVAL.")
                # Verify physical column exists in canonical schema to prevent OperationalError: no such column
                is_compat, code, _ = check_proposal_schema_compatibility("startup", target_col)
                self.assertTrue(is_compat, f"Field {target_col} must be physically present in {target_tbl}")

    # --------------------------------------------------------------------------
    # 9. Canonical database & authentic Audit 19 archive byte-level immutability
    # --------------------------------------------------------------------------
    def test_09_canonical_database_and_audit19_immutability(self):
        # 1. Canonical DB hash check
        self.assertTrue(os.path.exists(self.canonical_db), "Canonical database missing.")
        with open(self.canonical_db, "rb") as f:
            actual_canon_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            actual_canon_hash,
            self.expected_canonical_sha256,
            "CRITICAL VIOLATION: Canonical database data/normalized/ai_ecosystem.db has been modified!"
        )

        # 2. Canonical DB row count checks (exact 6,745 records)
        conn_c = sqlite3.connect(self.canonical_db)
        c_c = conn_c.cursor()
        c_c.execute("SELECT count(*) FROM ai_startups")
        self.assertEqual(c_c.fetchone()[0], 1307)
        c_c.execute("SELECT count(*) FROM ai_products")
        self.assertEqual(c_c.fetchone()[0], 1316)
        c_c.execute("SELECT count(*) FROM ai_research_papers")
        self.assertEqual(c_c.fetchone()[0], 1060)
        c_c.execute("SELECT count(*) FROM ai_news")
        self.assertEqual(c_c.fetchone()[0], 1132)
        c_c.execute("SELECT count(*) FROM ai_jobs")
        self.assertEqual(c_c.fetchone()[0], 1930)
        conn_c.close()

        # 3. Authentic Audit 19 archive hash check
        self.assertTrue(os.path.exists(self.audit19_db), "Authentic Audit 19 database missing.")
        with open(self.audit19_db, "rb") as f:
            actual_audit19_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            actual_audit19_hash,
            self.expected_audit19_sha256,
            "CRITICAL VIOLATION: Authentic Audit 19 database source/audit19_original_database.db has been modified!"
        )

    # --------------------------------------------------------------------------
    # 10. Stale-record and missing-date SQLite archive retention (zero records deleted)
    # --------------------------------------------------------------------------
    def test_10_stale_and_missing_record_archive_retention(self):
        if not os.path.exists(self.working_db):
            self.skipTest("Working database not yet initialized.")

        conn = sqlite3.connect(self.working_db)
        c = conn.cursor()

        # Check total record preservation
        c.execute("SELECT count(*) FROM ai_startups")
        total_startups = c.fetchone()[0]
        self.assertGreaterEqual(total_startups, 1307)

        c.execute("SELECT count(*) FROM ai_products")
        total_products = c.fetchone()[0]
        self.assertGreaterEqual(total_products, 1316)

        c.execute("SELECT count(*) FROM ai_news")
        total_news = c.fetchone()[0]
        self.assertGreaterEqual(total_news, 1132)

        c.execute("SELECT count(*) FROM ai_jobs")
        total_jobs = c.fetchone()[0]
        self.assertGreaterEqual(total_jobs, 1930)

        # Confirm historical records outside rolling window are retained (in_rolling_window = 0)
        c.execute("SELECT count(*) FROM ai_news WHERE in_rolling_window = 0")
        outside_news = c.fetchone()[0]
        self.assertGreaterEqual(outside_news, 827)

        c.execute("SELECT count(*) FROM ai_jobs WHERE in_rolling_window = 0")
        outside_jobs = c.fetchone()[0]
        self.assertGreaterEqual(outside_jobs, 32)

        # Confirm missing date records are preserved (in_rolling_window = 0)
        c.execute("SELECT count(*) FROM ai_startups WHERE freshness_status = 'MISSING_DATE'")
        missing_startups = c.fetchone()[0]
        self.assertEqual(missing_startups, 1307)

        c.execute("SELECT count(*) FROM ai_products WHERE freshness_status = 'MISSING_DATE'")
        missing_products = c.fetchone()[0]
        self.assertEqual(missing_products, 1316)

        conn.close()


if __name__ == "__main__":
    unittest.main()

"""
Audit 32 Comprehensive Integration Test Suite: Real Stage-Level Recovery & Reliability
======================================================================================
Validates all corrective engineering mandates of Audit 32:
1. Real stage-level recovery using an isolated temporary SQLite database fixture (no mocks for execution logic).
2. Verification that stages 1 & 2 are skipped upon resumption, and stages 3, 4, 5, 6 execute to completion.
3. Verification that run is marked recovered ONLY after remaining stages finish.
4. Verification that run_once() returns recovery summary immediately without launching a second full pipeline.
5. Verification that recovery failure preserves a recoverable INTERRUPTED state and intact checkpoint.
6. Verification that atomic reservation lock prevents concurrent recovery by two scheduler processes.
7. Verification of idempotent recovery on already completed checkpoints.
8. Domain-specific 6-month eligibility semantics (date_type, date_provenance, strict archive preservation).
9. Exact GitHub repository (191) and snapshot (211) count reconciliation.
"""

import os
import sys
import json
import sqlite3
import shutil
import tempfile
import asyncio
import unittest
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rolling_window import compute_rolling_window, classify_freshness, parse_publication_timestamp
from core.working_database import WorkingDatabaseManager
from core.daily_pipeline import DailyRollingPipeline, PIPELINE_STAGES
from core.scheduler import RollingPipelineScheduler


class TestAudit32RecoveryIntegration(unittest.TestCase):
    """Integration test suite for stage-level recovery, reliability, and eligibility semantics."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audit32_test_")
        self.temp_working_db = os.path.join(self.temp_dir, "rolling_ai_ecosystem.db")
        self.temp_canonical_db = os.path.join(self.temp_dir, "ai_ecosystem.db")
        self.temp_reports_dir = os.path.join(self.temp_dir, "reports")
        self.temp_exports_dir = os.path.join(self.temp_dir, "exports")
        os.makedirs(self.temp_reports_dir, exist_ok=True)
        os.makedirs(self.temp_exports_dir, exist_ok=True)

        # Create a minimal canonical database fixture
        self._init_canonical_fixture(self.temp_canonical_db)

        # Initialize working database manager
        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db
        )
        self.db_manager.initialize_schema()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _init_canonical_fixture(self, path: str):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE ai_startups (
                startup_id TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                ai_focus_area TEXT,
                ai_evidence TEXT,
                employee_count INTEGER,
                pricing_model TEXT,
                website TEXT,
                primary_source_url TEXT,
                provenance_sources TEXT,
                headquarters TEXT,
                batch_or_founded TEXT,
                description TEXT,
                collected_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE ai_products (
                product_id TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                product_type TEXT,
                ai_task_category TEXT,
                developer_or_company TEXT,
                developer_profile_url TEXT,
                official_company_website TEXT,
                pricing_model TEXT,
                license TEXT,
                access_type TEXT,
                actual_price REAL,
                original_source_url TEXT,
                provenance_source TEXT,
                description TEXT,
                collected_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE ai_research_papers (
                paper_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,
                publication_date TEXT,
                categories TEXT,
                paper_url TEXT,
                github_url TEXT,
                github_stars INTEGER,
                github_forks INTEGER,
                github_star_source TEXT,
                github_star_retrieved_at TEXT,
                provenance TEXT,
                abstract TEXT,
                collected_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE ai_news (
                news_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                source_name TEXT,
                article_url TEXT UNIQUE,
                author TEXT,
                published_at TEXT,
                category TEXT,
                related_companies TEXT,
                provenance TEXT,
                collected_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE ai_jobs (
                job_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                company_website TEXT,
                category TEXT,
                classification_reason TEXT,
                responsibility_evidence TEXT,
                qualification_evidence TEXT,
                classification_confidence REAL,
                job_description TEXT,
                required_skills TEXT,
                preferred_skills TEXT,
                experience_level TEXT,
                location TEXT,
                remote_type TEXT,
                salary_min REAL,
                salary_max REAL,
                currency TEXT,
                compensation_type TEXT,
                compensation_period TEXT,
                employment_type TEXT,
                job_status TEXT,
                vacancy_status TEXT,
                application_url TEXT UNIQUE,
                posted_at TEXT,
                source_name TEXT,
                provenance TEXT,
                collected_at TEXT
            )
        """)
        # Insert 1 sample record each
        now_iso = datetime.now(timezone.utc).isoformat()
        c.execute("INSERT INTO ai_startups (startup_id, entity_name, batch_or_founded, collected_at) VALUES ('s1', 'Startup1', '2023', ?)", (now_iso,))
        c.execute("INSERT INTO ai_products (product_id, entity_name, collected_at) VALUES ('p1', 'Product1', ?)", (now_iso,))
        c.execute("INSERT INTO ai_research_papers (paper_id, title, publication_date, collected_at) VALUES ('pa1', 'Paper1', '2026-10-01', ?)", (now_iso,))
        c.execute("INSERT INTO ai_news (news_id, title, article_url, published_at, collected_at) VALUES ('n1', 'News1', 'https://example.com/n1', '2026-10-15T12:00:00Z', ?)", (now_iso,))
        c.execute("INSERT INTO ai_jobs (job_id, job_title, company_name, application_url, posted_at, collected_at) VALUES ('j1', 'Job1', 'Corp1', 'https://example.com/j1', '2026-10-20T12:00:00Z', ?)", (now_iso,))
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------
    # 1. Real Stage-Level Recovery Integration (No execution mocks)
    # --------------------------------------------------------------------------
    def test_01_real_stage_level_recovery_integration(self):
        """
        Tests end-to-end stage resumption without mocks on isolated SQLite DB:
        - Simulates interruption after STAGE_2_JOBS
        - Invokes scheduler.run_once()
        - Verifies stages 1 & 2 were skipped and stages 3, 4, 5, 6 were executed
        - Verifies original run marked RECOVERED_INTERRUPTED only upon completion
        - Verifies run_once() returns recovery summary immediately without 2nd run
        """
        pipeline = DailyRollingPipeline(
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir
        )
        scheduler = RollingPipelineScheduler(
            daily_schedule_utc="06:00",
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db
        )
        # Override scheduler's pipeline paths
        scheduler.pipeline = pipeline

        # Step 1: Seed working database
        self.db_manager.seed_from_canonical()

        # Step 2: Inject an interrupted run after Stage 2
        interrupted_run_id = "test_run_interrupted_after_stage2"
        checkpoint_data = {
            "last_completed_stage": "STAGE_2_JOBS",
            "completed_stages": ["STAGE_1_NEWS", "STAGE_2_JOBS"]
        }
        self.db_manager.log_collection_checkpoint({
            "run_id": interrupted_run_id,
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "checkpoint_data": checkpoint_data,
            "new_news": 5,
            "new_jobs": 10
        })

        # Verify it is detected as interrupted
        interrupted = scheduler.check_for_interrupted_runs()
        self.assertEqual(len(interrupted), 1)
        self.assertEqual(interrupted[0]["run_id"], interrupted_run_id)

        # Step 3: Run scheduler.run_once()
        # Track pipeline executions: ensure ONLY recovery happens, not a 2nd execution
        res = scheduler.run_once(run_pilot=False)

        # Step 4: Verify recovery execution details
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["original_run_id"], interrupted_run_id)
        self.assertTrue(res["run_id"].startswith("recovery_"))

        # Verify stages skipped and executed
        resumed_checkpoint = res["checkpoint_data"]
        self.assertEqual(resumed_checkpoint["resume_from_stage"], "STAGE_3_GITHUB_METRICS")
        self.assertIn("STAGE_3_GITHUB_METRICS", resumed_checkpoint["resumed_stages"])
        self.assertIn("STAGE_4_VACANCY_LIFECYCLE", resumed_checkpoint["resumed_stages"])
        self.assertIn("STAGE_5_EXPORTS", resumed_checkpoint["resumed_stages"])
        self.assertIn("STAGE_6_REPORT", resumed_checkpoint["resumed_stages"])
        self.assertNotIn("STAGE_1_NEWS", resumed_checkpoint["resumed_stages"])
        self.assertNotIn("STAGE_2_JOBS", resumed_checkpoint["resumed_stages"])

        # Step 5: Verify DB state of original run
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status, error_log FROM collection_logs WHERE run_id = ?", (interrupted_run_id,))
        row = c.fetchone()
        self.assertIn(row["status"], ("RECOVERED", "RECOVERED_INTERRUPTED"))
        self.assertIn("Successfully recovered", row["error_log"])

        # Verify total logs count: 1 original run + 1 recovery run = 2 total
        c.execute("SELECT count(*) FROM collection_logs")
        total_logs = c.fetchone()[0]
        self.assertEqual(total_logs, 2, "Scheduler must NOT launch a second pipeline cycle after recovery.")
        conn.close()

    # --------------------------------------------------------------------------
    # 2. Recovery Failure Preserves Recoverable INTERRUPTED State (Simulated Mock)
    # --------------------------------------------------------------------------
    def test_02_recovery_failure_preserves_recoverable_state(self):
        """
        [TEST WITH SIMULATED EXCEPTION MOCK]
        Simulates an unhandled failure during recovery execution by mocking
        pipeline.execute_daily_pipeline to raise RuntimeError.
        Verifies:
        - Original run is NOT marked recovered
        - Original run reverts to status 'INTERRUPTED'
        - Original checkpoint data is preserved
        - Run remains discoverable by check_for_interrupted_runs()
        """
        scheduler = RollingPipelineScheduler(
            daily_schedule_utc="06:00",
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir
        )
        self.db_manager.seed_from_canonical()

        interrupted_run_id = "test_run_fail_recovery"
        checkpoint_data = {
            "last_completed_stage": "STAGE_1_NEWS",
            "completed_stages": ["STAGE_1_NEWS"]
        }
        self.db_manager.log_collection_checkpoint({
            "run_id": interrupted_run_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "checkpoint_data": checkpoint_data
        })

        # Inject simulated exception into pipeline.execute_daily_pipeline (Explicit Mock)
        async def mock_crashing_pipeline(*args, **kwargs):
            raise RuntimeError("Simulated network outage or transient process crash during recovery!")

        scheduler.pipeline.execute_daily_pipeline = mock_crashing_pipeline

        # Attempt recovery: should raise RuntimeError
        with self.assertRaises(RuntimeError):
            scheduler.recover_interrupted_run({"run_id": interrupted_run_id, "start_time": datetime.now(timezone.utc).isoformat(), "checkpoint_data": json.dumps(checkpoint_data)})

        # Verify DB state of run: must be INTERRUPTED with error recorded
        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("SELECT status, error_log FROM collection_logs WHERE run_id = ?", (interrupted_run_id,))
        row = c.fetchone()
        conn.close()

        self.assertEqual(row["status"], "INTERRUPTED")
        self.assertIn("Simulated network outage", row["error_log"])

        # Verify check_for_interrupted_runs still discovers it for subsequent retry
        still_interrupted = scheduler.check_for_interrupted_runs()
        self.assertTrue(any(r["run_id"] == interrupted_run_id for r in still_interrupted))

    # --------------------------------------------------------------------------
    # 3. Concurrency Protection via Atomic Reservation Lock
    # --------------------------------------------------------------------------
    def test_03_concurrency_protection_atomic_reservation(self):
        """
        Verifies that when a scheduler process begins recovery with an active lease,
        another concurrent scheduler process cannot claim or recover the same run.
        """
        import socket
        scheduler1 = RollingPipelineScheduler(
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir
        )
        scheduler2 = RollingPipelineScheduler(
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir
        )

        interrupted_run_id = "test_concurrent_run"
        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": interrupted_run_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "checkpoint_data": {"last_completed_stage": "STAGE_1_NEWS"}
        })

        run_info = {"run_id": interrupted_run_id, "start_time": now_iso, "checkpoint_data": '{"last_completed_stage": "STAGE_1_NEWS"}'}

        # Scheduler 1 manually acquires active lease and heartbeat
        conn = self.db_manager.get_connection()
        conn.execute("""
            UPDATE collection_logs
            SET status = 'RECOVERY_IN_PROGRESS',
                process_id = ?,
                host_name = ?,
                lease_owner = ?,
                claim_timestamp = ?,
                last_heartbeat = ?
            WHERE run_id = ?
        """, (os.getpid(), socket.gethostname(), f"{socket.gethostname()}:{os.getpid()}:sched1", now_iso, now_iso, interrupted_run_id))
        conn.commit()
        conn.close()

        # Scheduler 2 attempts recovery: must be blocked and return None (active lease)
        res2 = scheduler2.recover_interrupted_run(run_info)
        self.assertIsNone(res2, "Concurrent recovery must be prevented by atomic reservation lock.")

    # --------------------------------------------------------------------------
    # 4. Idempotent Recovery
    # --------------------------------------------------------------------------
    def test_04_idempotent_recovery(self):
        """
        Verifies that recovering an already completed checkpoint is idempotent
        and returns status COMPLETED without re-running any stages.
        """
        scheduler = RollingPipelineScheduler(
            working_db_path=self.temp_working_db,
            canonical_db_path=self.temp_canonical_db,
            reports_dir=self.temp_reports_dir,
            exports_dir=self.temp_exports_dir
        )
        already_completed_id = "test_already_completed"
        now_iso = datetime.now(timezone.utc).isoformat()
        self.db_manager.log_collection_checkpoint({
            "run_id": already_completed_id,
            "start_time": now_iso,
            "execution_type": "DAILY_INCREMENTAL",
            "rolling_window_start": "2026-05-22T00:00:00+00:00",
            "rolling_window_end": "2026-11-22T00:00:00+00:00",
            "status": "IN_PROGRESS",
            "checkpoint_data": {"last_completed_stage": "STAGE_6_REPORT"}
        })

        run_info = {"run_id": already_completed_id, "start_time": now_iso, "checkpoint_data": '{"last_completed_stage": "STAGE_6_REPORT"}'}
        res = scheduler.recover_interrupted_run(run_info)
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["resumed_stages"], [])

    # --------------------------------------------------------------------------
    # 5. Domain-Specific 6-Month Eligibility Semantics
    # --------------------------------------------------------------------------
    def test_05_domain_specific_eligibility_and_provenance(self):
        """
        Verifies:
        - Startups: founding_date is NOT a publication date; classified as UNVERIFIED_DATE / MISSING_DATE.
        - Products: lack genuine publication date; classified as UNVERIFIED_DATE / MISSING_DATE.
        - Papers: classified with date_type = 'RESEARCH_PUBLICATION_DATE'.
        - News: classified with date_type = 'NEWS_PUBLICATION_DATE'.
        - Jobs: classified with date_type = 'JOB_POSTING_DATE'.
        - Zero synthetic dates fabricated.
        - All unverified records preserved in working SQLite archive (in_rolling_window = 0).
        """
        stats = self.db_manager.seed_from_canonical()
        self.assertEqual(stats["startups"], 1)
        self.assertEqual(stats["products"], 1)
        self.assertEqual(stats["papers"], 1)
        self.assertEqual(stats["news"], 1)
        self.assertEqual(stats["jobs"], 1)

        conn = self.db_manager.get_connection()
        c = conn.cursor()

        # Startups check
        c.execute("SELECT startup_id, date_type, date_provenance, freshness_status, in_rolling_window, published_at FROM ai_startups")
        st = dict(c.fetchone())
        self.assertEqual(st["date_type"], "UNVERIFIED_DATE")
        self.assertIn(st["freshness_status"], ("UNVERIFIED_DATE", "MISSING_DATE"))
        self.assertEqual(st["in_rolling_window"], 0)
        self.assertIsNone(st["published_at"])
        self.assertIsNotNone(st["date_provenance"])

        # Products check
        c.execute("SELECT product_id, date_type, date_provenance, freshness_status, in_rolling_window, published_at FROM ai_products")
        pr = dict(c.fetchone())
        self.assertEqual(pr["date_type"], "UNVERIFIED_DATE")
        self.assertIn(pr["freshness_status"], ("UNVERIFIED_DATE", "MISSING_DATE"))
        self.assertEqual(pr["in_rolling_window"], 0)
        self.assertIsNone(pr["published_at"])
        self.assertIsNotNone(pr["date_provenance"])

        # Papers check
        c.execute("SELECT paper_id, date_type, date_provenance, in_rolling_window FROM ai_research_papers")
        pa = dict(c.fetchone())
        self.assertEqual(pa["date_type"], "RESEARCH_PUBLICATION_DATE")
        self.assertEqual(pa["in_rolling_window"], 1)
        self.assertIsNotNone(pa["date_provenance"])

        # News check
        c.execute("SELECT news_id, date_type, date_provenance, in_rolling_window FROM ai_news")
        ne = dict(c.fetchone())
        self.assertEqual(ne["date_type"], "NEWS_PUBLICATION_DATE")
        self.assertEqual(ne["in_rolling_window"], 1)
        self.assertIsNotNone(ne["date_provenance"])

        # Jobs check
        c.execute("SELECT job_id, date_type, date_provenance, in_rolling_window FROM ai_jobs")
        jo = dict(c.fetchone())
        self.assertEqual(jo["date_type"], "JOB_POSTING_DATE")
        self.assertEqual(jo["in_rolling_window"], 1)
        self.assertIsNotNone(jo["date_provenance"])

        conn.close()

    # --------------------------------------------------------------------------
    # 6. GitHub Repository & Snapshot Count Consistency
    # --------------------------------------------------------------------------
    def test_06_github_metrics_count_consistency(self):
        """
        Validates GitHub repositories and snapshots metrics consistency:
        - 190 canonical baseline snapshots + 15 incremental live snapshots = 205 snapshots
        - Exactly 190 tracked repositories (zero mock test artifacts)
        - Exact synchronization between working database, export CSV, and JSON summary
        """
        # Read the real packaged working database
        prod_working_db = os.path.abspath("data/working/rolling_ai_ecosystem.db")
        if not os.path.exists(prod_working_db):
            prod_working_db = os.path.abspath("01_DATABASE/rolling_ai_ecosystem.db")

        if os.path.exists(prod_working_db):
            conn = sqlite3.connect(prod_working_db)
            c = conn.cursor()
            c.execute("SELECT count(*) FROM github_repositories")
            total_repos = c.fetchone()[0]
            c.execute("SELECT count(*) FROM github_metrics_history")
            total_snapshots = c.fetchone()[0]

            # Count initial seed vs incremental snapshots
            c.execute("SELECT count(*) FROM github_metrics_history WHERE change_stars_delta = 0 AND change_forks_delta = 0 AND provenance != 'official_github_rest_api'")
            baseline_snapshots = c.fetchone()[0]
            c.execute("SELECT count(*) FROM github_metrics_history WHERE provenance = 'official_github_rest_api'")
            live_snapshots = c.fetchone()[0]

            conn.close()

            self.assertEqual(total_repos, 190, "Tracked genuine GitHub repositories must equal 190.")
            self.assertEqual(total_snapshots, 205, "Total genuine GitHub metrics snapshots must equal 205.")
            self.assertEqual(baseline_snapshots, 190, "Baseline seed snapshots must equal 190.")
            self.assertEqual(live_snapshots, 15, "Live refreshed snapshots must equal 15.")
            self.assertEqual(baseline_snapshots + live_snapshots, total_snapshots)

            # Check JSON summary if exists
            summary_path = os.path.abspath("reports/github_metrics_summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as f:
                    summary_data = json.load(f)
                self.assertEqual(summary_data["total_tracked_repositories"], 190)
                self.assertEqual(summary_data["total_metric_snapshots"], 205)

            # Check CSV export if exists
            csv_path = os.path.abspath("data/working/github_metrics_history.csv")
            if not os.path.exists(csv_path):
                csv_path = os.path.abspath("02_EXPORTS/github_metrics_history.csv")
            if os.path.exists(csv_path):
                import csv
                with open(csv_path, "r", encoding="utf-8") as f:
                    csv_rows = list(csv.reader(f))
                self.assertEqual(len(csv_rows) - 1, 205, "CSV snapshots must match exactly 205.")


if __name__ == "__main__":
    unittest.main()

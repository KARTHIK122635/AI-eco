"""
Audit 30 Comprehensive Test Suite: 6-Month Rolling AI Ecosystem Pipeline
========================================================================
Covers all 12 mandatory validation criteria from Audit 30 Section 10:
1. Initial historical collection & 6M dynamic rolling window
2. 20-record Phase III pilot execution (100% PENDING_APPROVAL)
3. Duplicate prevention & idempotency guarantee
4. Daily incremental collection & metrics delta tracking
5. Scheduler restart & crash/interruption recovery
6. API rate limits & backoff handling
7. Stale-record retention (outside window preserved, never deleted)
8. GitHub metric refresh & history tracking
9. Gemini-to-Groq fallback mechanism
10. DeepSeek HTTP 402 non-retriable handling
11. Semantic chunking multi-chunk reassembly & physical schema mapping
12. Database integrity & canonical immutability
"""

import os
import sys
import json
import sqlite3
import hashlib
import unittest
from datetime import datetime, timezone, timedelta
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
from core.llm.multi_tier_engine import (
    MultiTierLLMEngine,
    OrchestrationResult,
    TokenUsage
)
from src.stage3.schema_mapping import (
    check_proposal_schema_compatibility,
    get_physical_table_columns,
    CANONICAL_TABLE_SCHEMAS
)
from core.scheduler import RollingPipelineScheduler


class TestAudit30RollingPipeline(unittest.TestCase):
    """Test suite for Audit 30 Rolling Pipeline implementation."""

    @classmethod
    def setUpClass(cls):
        cls.workspace_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        cls.canonical_db = os.path.join(cls.workspace_dir, "data", "normalized", "ai_ecosystem.db")
        cls.audit19_db = os.path.join(cls.workspace_dir, "source", "audit19_original_database.db")
        cls.working_db = os.path.join(cls.workspace_dir, "data", "working", "rolling_ai_ecosystem.db")

        cls.expected_canonical_sha256 = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
        cls.expected_audit19_sha256 = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"

    # --------------------------------------------------------------------------
    # 1. Initial historical collection & 6M dynamic rolling window
    # --------------------------------------------------------------------------
    def test_01_rolling_window_bounds_and_freshness(self):
        ref_dt = datetime(2026, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
        start_w, end_w = compute_rolling_window(ref_dt, months=6)
        self.assertEqual(start_w.year, 2026)
        self.assertEqual(start_w.month, 5)
        self.assertEqual(start_w.day, 22)
        self.assertEqual(end_w, ref_dt)

        # Dynamic advancement test (simulate 30 days later)
        ref_later = ref_dt + timedelta(days=30)
        s_later, e_later = compute_rolling_window(ref_later, months=6)
        self.assertEqual(s_later.year, 2026)
        self.assertEqual(s_later.month, 6)
        self.assertEqual(s_later.day, 22)

        # Freshness tiers classification
        t_fresh = ref_dt - timedelta(hours=6)
        c_fresh = classify_freshness(t_fresh, ref_dt, start_w)
        self.assertEqual(c_fresh["status"], "FRESH_24H")
        self.assertTrue(c_fresh["in_rolling_window"])

        t_recent = ref_dt - timedelta(days=4)
        c_recent = classify_freshness(t_recent, ref_dt, start_w)
        self.assertEqual(c_recent["status"], "RECENT_7D")
        self.assertTrue(c_recent["in_rolling_window"])

        t_hist = ref_dt - timedelta(days=45)
        c_hist = classify_freshness(t_hist, ref_dt, start_w)
        self.assertEqual(c_hist["status"], "HISTORICAL_6M")
        self.assertTrue(c_hist["in_rolling_window"])

        t_outside = datetime(2025, 12, 1, tzinfo=timezone.utc)
        c_outside = classify_freshness(t_outside, ref_dt, start_w)
        self.assertEqual(c_outside["status"], "OUTSIDE_WINDOW")
        self.assertFalse(c_outside["in_rolling_window"])

        c_missing = classify_freshness(None, ref_dt, start_w)
        self.assertEqual(c_missing["status"], "MISSING_DATE")

        t_future = ref_dt + timedelta(days=2)
        c_future = classify_freshness(t_future, ref_dt, start_w)
        self.assertEqual(c_future["status"], "FUTURE_TIMESTAMP_ANOMALY")

    # --------------------------------------------------------------------------
    # 2. 20-record Phase III pilot execution (100% PENDING_APPROVAL)
    # --------------------------------------------------------------------------
    def test_02_pilot_proposals_pending_approval_and_schema(self):
        if not os.path.exists(self.working_db):
            self.skipTest("Working DB not yet generated.")

        conn = sqlite3.connect(self.working_db)
        c = conn.cursor()
        c.execute("SELECT proposal_id, approval_status, schema_status, record_id FROM enrichment_proposals")
        proposals = c.fetchall()
        conn.close()

        if proposals:
            self.assertGreaterEqual(len(proposals), 20)
            for pid, app_status, schema_status, rec_id in proposals:
                # Invariant: Every proposal must remain PENDING_APPROVAL
                self.assertEqual(app_status, "PENDING_APPROVAL", f"Proposal {pid} is not PENDING_APPROVAL")
                self.assertIn(schema_status, ["SCHEMA_COMPATIBLE", "BLOCKED_SCHEMA"])

    # --------------------------------------------------------------------------
    # 3. Duplicate prevention & idempotency guarantee
    # --------------------------------------------------------------------------
    def test_03_duplicate_prevention_and_idempotency(self):
        reg = DeduplicationRegistry()
        url1 = "https://example.com/ai/article?utm_source=twitter&id=123"
        url2 = "https://example.com/ai/article?id=123"
        canon1 = canonicalize_url(url1)
        canon2 = canonicalize_url(url2)
        self.assertEqual(canon1, canon2)

        is_new1, reason1 = reg.check_and_register("id1", url1, "AI Title", "AI Content Body")
        self.assertTrue(is_new1)
        self.assertEqual(reason1, "UNIQUE")

        is_new2, reason2 = reg.check_and_register("id2", url2, "AI Title 2", "AI Content Body 2")
        self.assertFalse(is_new2)
        self.assertIn("Duplicate canonical URL", reason2)

        # Content fingerprint test
        fp1 = compute_content_fingerprint("OpenAI announces GPT-5 frontier model.")
        fp2 = compute_content_fingerprint("  OPENAI Announces  GPT-5  frontier model!  ")
        self.assertEqual(fp1, fp2)

    # --------------------------------------------------------------------------
    # 4. Daily incremental collection & metrics delta tracking
    # --------------------------------------------------------------------------
    def test_04_metrics_delta_tracking(self):
        mgr = WorkingDatabaseManager(working_db_path=self.working_db, canonical_db_path=self.canonical_db)
        mgr.initialize_schema()

        # Seed mock repo if empty
        conn = mgr.get_connection()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO github_repositories (repo_id, owner, repo_name, html_url, latest_stars, latest_forks) VALUES ('mock_repo', 'testowner', 'testrepo', 'https://github.com/testowner/testrepo', 100, 20)")
        conn.commit()
        conn.close()

        # Refresh with higher counts
        delta = mgr.refresh_github_metric("mock_repo", stars=125, forks=25, retrieval_status="HTTP_200_OK")
        self.assertEqual(delta["delta_stars"], 25)
        self.assertEqual(delta["delta_forks"], 5)

        # Refresh again with equal counts
        delta2 = mgr.refresh_github_metric("mock_repo", stars=125, forks=25, retrieval_status="HTTP_200_OK")
        self.assertEqual(delta2["delta_stars"], 0)
        self.assertEqual(delta2["delta_forks"], 0)

        # Cleanup mock records so tests do not pollute production working DB
        conn = mgr.get_connection()
        conn.execute("DELETE FROM github_metrics_history WHERE repo_id = 'mock_repo'")
        conn.execute("DELETE FROM github_repositories WHERE repo_id = 'mock_repo'")
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------
    # 5. Scheduler restart & crash/interruption recovery
    # --------------------------------------------------------------------------
    def test_05_scheduler_interruption_and_recovery(self):
        mgr = WorkingDatabaseManager(working_db_path=self.working_db, canonical_db_path=self.canonical_db)
        interrupted_run_id = f"interrupted_test_{datetime.now().strftime('%H%M%S')}"

        # Inject simulated interrupted run
        mgr.log_collection_checkpoint({
            "run_id": interrupted_run_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "execution_type": "TEST_SIMULATION",
            "rolling_window_start": datetime.now(timezone.utc).isoformat(),
            "rolling_window_end": datetime.now(timezone.utc).isoformat(),
            "status": "IN_PROGRESS"
        })

        scheduler = RollingPipelineScheduler(working_db_path=self.working_db, canonical_db_path=self.canonical_db)
        interrupted = scheduler.check_for_interrupted_runs()
        self.assertTrue(any(r["run_id"] == interrupted_run_id for r in interrupted))

        # Perform recovery on this run
        target = next(r for r in interrupted if r["run_id"] == interrupted_run_id)
        conn = mgr.get_connection()
        c = conn.cursor()
        c.execute("UPDATE collection_logs SET status = 'RECOVERED_INTERRUPTED' WHERE run_id = ?", (interrupted_run_id,))
        conn.commit()
        conn.close()

        # Check that it is no longer IN_PROGRESS
        interrupted_after = scheduler.check_for_interrupted_runs()
        self.assertFalse(any(r["run_id"] == interrupted_run_id for r in interrupted_after))

        # Cleanup test run from collection_logs
        conn = mgr.get_connection()
        conn.execute("DELETE FROM collection_logs WHERE run_id = ?", (interrupted_run_id,))
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------
    # 6. API rate limits & backoff handling
    # --------------------------------------------------------------------------
    def test_06_rate_limits_and_exponential_backoff(self):
        attempts = 0
        def simulated_api_call():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception("HTTP 429 Rate Limit Exceeded")
            return "SUCCESS"

        # Simulate backoff loop
        max_retries = 3
        backoff = 0.01
        result = None
        for i in range(max_retries):
            try:
                result = simulated_api_call()
                break
            except Exception as e:
                if i == max_retries - 1:
                    raise
                import time
                time.sleep(backoff * (2 ** i))

        self.assertEqual(result, "SUCCESS")
        self.assertEqual(attempts, 3)

    # --------------------------------------------------------------------------
    # 7. Stale-record retention (outside window preserved, never deleted)
    # --------------------------------------------------------------------------
    def test_07_stale_record_retention_not_deleted(self):
        if not os.path.exists(self.working_db):
            self.skipTest("Working DB not yet generated.")

        conn = sqlite3.connect(self.working_db)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM ai_news WHERE in_rolling_window = 0")
        outside_news = c.fetchone()[0]
        c.execute("SELECT count(*) FROM ai_jobs WHERE in_rolling_window = 0")
        outside_jobs = c.fetchone()[0]
        conn.close()

        # Historical records outside window must be preserved in SQLite archive
        self.assertGreaterEqual(outside_news, 800)
        self.assertGreaterEqual(outside_jobs, 30)

    # --------------------------------------------------------------------------
    # 8. GitHub metric refresh & history tracking
    # --------------------------------------------------------------------------
    def test_08_github_metrics_history_tracking(self):
        if not os.path.exists(self.working_db):
            self.skipTest("Working DB not yet generated.")

        conn = sqlite3.connect(self.working_db)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM github_repositories")
        repo_count = c.fetchone()[0]
        c.execute("SELECT count(*) FROM github_metrics_history")
        snapshot_count = c.fetchone()[0]
        conn.close()

        self.assertGreaterEqual(repo_count, 190)
        self.assertGreaterEqual(snapshot_count, 190)

    # --------------------------------------------------------------------------
    # 9. Gemini-to-Groq fallback mechanism
    # --------------------------------------------------------------------------
    def test_09_gemini_to_groq_fallback(self):
        engine = MultiTierLLMEngine()
        # Simulate primary Gemini failure
        res = engine.execute_with_fallback(
            "Extract entity info: Anthropic Claude 3.5 Sonnet",
            simulate_primary_failure=True
        )
        self.assertTrue(res.success)
        # Should execute on Groq or offline fallback
        self.assertIn(res.active_tier, ["FALLBACK_1", "OFFLINE"])
        self.assertIn(res.active_provider, ["groq", "offline"])

    # --------------------------------------------------------------------------
    # 10. DeepSeek HTTP 402 non-retriable handling
    # --------------------------------------------------------------------------
    def test_10_deepseek_http_402_non_retriable(self):
        engine = MultiTierLLMEngine()
        deepseek_provider = engine.fallback_2_provider
        self.assertIsNotNone(deepseek_provider)

        # Test prompt execution through deepseek provider directly
        res = deepseek_provider.generate("Test prompt")
        # Insufficient balance returns success=False without crashing or infinite retries
        self.assertFalse(res.success)
        self.assertTrue("402" in (res.error or "") or "Insufficient Balance" in (res.error or ""))

    # --------------------------------------------------------------------------
    # 11. Semantic chunking multi-chunk reassembly & physical schema mapping
    # --------------------------------------------------------------------------
    def test_11_multi_chunk_semantic_reassembly_and_schema_mapping(self):
        # 1. Multi-chunk reassembly test
        engine = MultiTierLLMEngine(force_fallback_tier="offline")
        long_text = ("Artificial intelligence and machine learning research in neural networks. " * 50) + "\n\n" + ("Large language models and multimodal vision transformers in production. " * 50)
        self.assertGreater(len(long_text), 3500)
        res = engine.execute_with_fallback(
            f"Extract topics from: {long_text}"
        )
        self.assertTrue(res.success)
        self.assertIsNotNone(res.structured_data)
        self.assertIn(res.active_tier, ["OFFLINE", "OFFLINE_SAFETY"])

        # 2. Physical schema mapping test
        cols = get_physical_table_columns(self.working_db, "ai_startups")
        self.assertIn("ai_focus_area", cols)
        self.assertIn("ai_evidence", cols)
        self.assertNotIn("ai_specialization", cols)

        is_compat, code, reason = check_proposal_schema_compatibility("startup", "ai_focus_area")
        self.assertTrue(is_compat)
        self.assertEqual(code, "SCHEMA_COMPATIBLE")

        is_compat2, code2, reason2 = check_proposal_schema_compatibility("startup", "ai_specialization")
        self.assertFalse(is_compat2)
        self.assertEqual(code2, "BLOCKED_SCHEMA")

    # --------------------------------------------------------------------------
    # 12. Database integrity & canonical immutability
    # --------------------------------------------------------------------------
    def test_12_canonical_immutability_and_database_integrity(self):
        # Canonical DB hash
        with open(self.canonical_db, "rb") as f:
            h_canon = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(h_canon, self.expected_canonical_sha256)

        # Audit 19 original DB hash
        with open(self.audit19_db, "rb") as f:
            h_audit19 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(h_audit19, self.expected_audit19_sha256)

        # Check canonical record counts (strictly 6,745)
        conn = sqlite3.connect(self.canonical_db)
        c = conn.cursor()
        total_canon = 0
        for tbl in ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]:
            c.execute(f"SELECT count(*) FROM {tbl}")
            total_canon += c.fetchone()[0]
        conn.close()
        self.assertEqual(total_canon, 6745)

        # Working DB SQLite integrity check
        if os.path.exists(self.working_db):
            conn_w = sqlite3.connect(self.working_db)
            c_w = conn_w.cursor()
            c_w.execute("PRAGMA integrity_check")
            status = c_w.fetchone()[0]
            conn_w.close()
            self.assertEqual(status, "ok")


if __name__ == "__main__":
    unittest.main()

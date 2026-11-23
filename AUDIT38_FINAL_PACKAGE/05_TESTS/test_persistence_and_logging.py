"""
Unit tests for multi-table persistence, append-only logging, review routing, and canonical immutability.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Persistence & Review Queue Enforcement
"""

import os
import sqlite3
import tempfile
import unittest
import uuid
import hashlib
from datetime import datetime, timezone

from core.enrichment.engine import EnrichmentEngine, CANONICAL_TABLES
from core.enrichment.schemas import EnrichmentResult, ValidationStatus, compute_source_version
from core.llm.providers.offline_provider import OfflineProvider


class TestPersistenceAndLogging(unittest.TestCase):

    def setUp(self):
        # Create a temporary SQLite database for testing persistence
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

        self.conn = sqlite3.connect(self.temp_db_path)
        self.cur = self.conn.cursor()

        # Create dummy canonical table to test immutability
        self.cur.execute("CREATE TABLE ai_jobs (job_id TEXT PRIMARY KEY, title TEXT, required_skills TEXT)")
        self.cur.execute("INSERT INTO ai_jobs VALUES ('job_001', 'AI Engineer', '[]')")
        self.cur.execute("INSERT INTO ai_jobs VALUES ('job_002', 'Data Scientist', '[]')")
        self.conn.commit()

        self.provider = OfflineProvider()
        self.engine = EnrichmentEngine(provider=self.provider, db_path=self.temp_db_path)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_multi_table_schema_initialization(self):
        """Test that all 4 required tables and legacy audit table are preserved and initialized."""
        self.engine.init_database_tables(self.conn)
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in self.cur.fetchall()]

        self.assertIn("llm_enrichment_results", tables)
        self.assertIn("llm_enrichment_logs", tables)
        self.assertIn("llm_provider_usage", tables)
        self.assertIn("llm_review_queue", tables)
        self.assertIn("enrichment_audit_log", tables)

    def test_append_only_attempt_history_and_retries(self):
        """
        Audit 19 Requirement:
        - Unique attempt_id for each attempt.
        - Maintain an append-only attempt log.
        - Preserve previous attempts.
        - A later retry must not erase the history of an earlier attempt.
        """
        self.engine.init_database_tables(self.conn)
        now_iso = datetime.now(timezone.utc).isoformat()
        src_ver = hashlib.sha256(b"source text v1").hexdigest()

        # Attempt 1: Failed or Needs Review
        attempt_1_id = str(uuid.uuid4())
        res1 = EnrichmentResult(
            attempt_id=attempt_1_id,
            record_id="job_001",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python"],
            source_url="https://example.com/1",
            evidence="Requires Python.",
            source_version=src_ver,
            confidence_score=0.75,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.NEEDS_REVIEW.value,
            validation_rationale="Initial heuristic extraction",
            retry_count=0
        )

        self.engine.enrichment_log = [res1]
        self.engine.persist_multi_table_schema()

        # Check logs: 1 entry
        self.cur.execute("SELECT count(*) FROM llm_enrichment_logs")
        self.assertEqual(self.cur.fetchone()[0], 1)

        # Attempt 2: Explicit retry with new attempt_id
        attempt_2_id = str(uuid.uuid4())
        res2 = EnrichmentResult(
            attempt_id=attempt_2_id,
            record_id="job_001",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python", "PyTorch"],
            source_url="https://example.com/1",
            evidence="Requires Python and PyTorch.",
            source_version=src_ver,
            confidence_score=0.85,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.VERIFIED.value,
            validation_rationale="Verified with exact evidence",
            retry_count=1
        )

        self.engine.enrichment_log = [res2]
        self.engine.persist_multi_table_schema()

        # Append-only check: llm_enrichment_logs now has 2 entries (both attempts preserved!)
        self.cur.execute("SELECT count(*) FROM llm_enrichment_logs WHERE record_id='job_001'")
        self.assertEqual(self.cur.fetchone()[0], 2, "Append-only log must preserve both attempts!")

        # Results table has latest accepted result with retry_count incremented
        self.cur.execute("SELECT attempt_id, retry_count, validation_status FROM llm_enrichment_results WHERE record_id='job_001'")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], attempt_2_id)
        self.assertEqual(row[1], 1)
        self.assertEqual(row[2], "VERIFIED")

    def test_review_queue_routing(self):
        """Test that uncertain or failed records enter llm_review_queue, while VERIFIED records do not."""
        self.engine.init_database_tables(self.conn)
        now_iso = datetime.now(timezone.utc).isoformat()
        src_ver = hashlib.sha256(b"content").hexdigest()

        # 1. NEEDS_REVIEW record
        r_review = EnrichmentResult(
            attempt_id=str(uuid.uuid4()),
            record_id="job_rev_1",
            entity_type="job",
            field_name="role_specialization",
            original_value=None,
            enriched_value="Computer Vision & Multimodal",
            source_url="https://example.com",
            evidence="computer vision",
            source_version=src_ver,
            confidence_score=0.75,
            enrichment_method="heuristic_classification",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.NEEDS_REVIEW.value,
            validation_rationale="Multimodal unestablished in evidence"
        )

        # 2. VERIFIED record
        r_verified = EnrichmentResult(
            attempt_id=str(uuid.uuid4()),
            record_id="job_ver_2",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python"],
            source_url="https://example.com",
            evidence="Python developer",
            source_version=src_ver,
            confidence_score=0.85,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.VERIFIED.value,
            validation_rationale="Fully supported"
        )

        self.engine.enrichment_log = [r_review, r_verified]
        self.engine.persist_multi_table_schema()

        # Review queue must contain r_review, but NOT r_verified
        self.cur.execute("SELECT record_id, validation_status FROM llm_review_queue")
        rows = self.cur.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "job_rev_1")
        self.assertEqual(rows[0][1], "NEEDS_REVIEW")

    def test_canonical_database_immutability(self):
        """Test that canonical tables are 100% immutable and unchanged during enrichment."""
        self.cur.execute("SELECT count(*) FROM ai_jobs")
        count_before = self.cur.fetchone()[0]

        # Execute persistence
        self.engine.enrichment_log = [
            EnrichmentResult(
                attempt_id=str(uuid.uuid4()),
                record_id="job_001",
                entity_type="job",
                field_name="technologies",
                original_value=None,
                enriched_value=["Python"],
                source_url="https://example.com",
                evidence="Python",
                source_version="v1",
                confidence_score=0.80,
                enrichment_method="heuristic_extraction",
                provider="offline",
                model="heuristic-keyword-v1",
                enriched_at=datetime.now(timezone.utc).isoformat(),
                validation_status=ValidationStatus.VERIFIED.value
            )
        ]
        self.engine.persist_multi_table_schema()

        self.cur.execute("SELECT count(*) FROM ai_jobs")
        count_after = self.cur.fetchone()[0]
        self.assertEqual(count_before, count_after, "Canonical table count must not change!")

        self.cur.execute("SELECT * FROM ai_jobs WHERE job_id='job_001'")
        job_row = self.cur.fetchone()
        self.assertEqual(job_row[2], "[]", "Canonical column values must remain completely unmodified!")

    def test_pipeline_run_preserves_history_without_reset(self):
        """
        REGRESSION TEST (Audit 20 Specification):
        Test that running persistence multiple times without resetting tables preserves
        append-only history across runs in llm_enrichment_logs.
        """
        self.engine.init_database_tables(self.conn)
        now_iso = datetime.now(timezone.utc).isoformat()
        src_ver = compute_source_version("Job Title: AI Engineer\nCompany: TechCo\nDescription:\nPython coding")

        # Run 1
        res_run1 = EnrichmentResult(
            attempt_id=str(uuid.uuid4()),
            record_id="job_001",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python"],
            source_url="https://example.com/jobs/1",
            evidence="Python coding",
            source_version=src_ver,
            confidence_score=0.80,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.VERIFIED.value,
            validation_rationale="Grounded in evidence"
        )
        self.engine.enrichment_log = [res_run1]
        self.engine.persist_multi_table_schema()

        self.cur.execute("SELECT count(*) FROM llm_enrichment_logs")
        count_run1 = self.cur.fetchone()[0]
        self.assertEqual(count_run1, 1)

        # Run 2 (without reset): add job_002 and retry job_001 with updated skills
        res_run2 = EnrichmentResult(
            attempt_id=str(uuid.uuid4()),
            record_id="job_002",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["SQL"],
            source_url="https://example.com/jobs/2",
            evidence="SQL database queries",
            source_version=src_ver,
            confidence_score=0.80,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.VERIFIED.value,
            validation_rationale="Grounded in evidence"
        )
        attempt_job1_retry_id = str(uuid.uuid4())
        res_run2_retry = EnrichmentResult(
            attempt_id=attempt_job1_retry_id,
            record_id="job_001",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python", "PyTorch"],
            source_url="https://example.com/jobs/1",
            evidence="Python coding and PyTorch",
            source_version=src_ver,
            confidence_score=0.85,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.VERIFIED.value,
            validation_rationale="Grounded in evidence",
            retry_count=1
        )
        self.engine.enrichment_log = [res_run2, res_run2_retry]
        self.engine.persist_multi_table_schema()

        # Step 4: Confirm that the first execution's attempts remain in llm_enrichment_logs
        self.cur.execute("SELECT count(*) FROM llm_enrichment_logs WHERE record_id='job_001'")
        self.assertEqual(self.cur.fetchone()[0], 2, "First and second execution attempts for job_001 must both remain in llm_enrichment_logs!")

        self.cur.execute("SELECT count(*) FROM llm_enrichment_logs")
        count_run2 = self.cur.fetchone()[0]
        self.assertEqual(count_run2, 3, "Append-only history must be preserved across runs (1 initial + 2 second run)!")

        # Step 5: Confirms that the latest accepted result is represented in llm_enrichment_results
        self.cur.execute("SELECT attempt_id, enriched_value, retry_count FROM llm_enrichment_results WHERE record_id='job_001'")
        latest_res = self.cur.fetchone()
        self.assertIsNotNone(latest_res)
        self.assertEqual(latest_res[0], attempt_job1_retry_id, "Latest accepted attempt_id must match second execution retry!")
        self.assertIn("PyTorch", latest_res[1], "Latest accepted enriched_value must be represented!")
        self.assertEqual(latest_res[2], 1, "Latest retry count must be incremented!")

    def test_legacy_audit_history_preservation_and_recovery(self):
        """
        REGRESSION TEST (Audit 21 Requirement 4):
        - Insert legacy audit history into enrichment_audit_log.
        - Initialize the new schema.
        - Persist results.
        - Prove every original row remains recoverable.
        """
        # Step 1: Create legacy table with pre-existing Audit 19 rows
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS enrichment_audit_log (
            record_id TEXT,
            entity_type TEXT,
            field_name TEXT,
            original_value TEXT,
            enriched_value TEXT,
            source_url TEXT,
            evidence TEXT,
            confidence_score REAL,
            enrichment_method TEXT,
            provider TEXT,
            model TEXT,
            enriched_at TEXT,
            validation_status TEXT,
            PRIMARY KEY (record_id, entity_type, field_name)
        )
        """)
        legacy_rows = [
            ("legacy_job_1", "job", "required_skills", "[]", '["Python"]', "http://test/1", "Python required", 0.85, "heuristic", "offline", "heuristic-v1", "2026-11-20T10:00:00Z", "NEEDS_REVIEW"),
            ("legacy_job_2", "job", "role_specialization", "", "Foundation Models & LLMs", "http://test/2", "LLM work", 0.90, "llm_gemini", "gemini", "gemini-flash", "2026-11-20T10:05:00Z", "VERIFIED"),
            ("legacy_startup_1", "startup", "ai_specialization", "", "Speech & Audio AI", "http://test/3", "Speech AI", 0.88, "llm_gemini", "gemini", "gemini-flash", "2026-11-20T10:10:00Z", "VERIFIED"),
        ]
        self.cur.executemany("INSERT INTO enrichment_audit_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", legacy_rows)
        self.conn.commit()

        # Step 2: Initialize new schema (Audit 21: must NOT drop enrichment_audit_log)
        self.engine.init_database_tables(self.conn)

        # Step 3: Persist new results
        now_iso = datetime.now(timezone.utc).isoformat()
        src_ver = hashlib.sha256(b"canonical source test").hexdigest()
        new_res = EnrichmentResult(
            attempt_id=str(uuid.uuid4()),
            record_id="job_001",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python"],
            source_url="https://example.com/jobs/1",
            evidence="Python coding",
            source_version=src_ver,
            confidence_score=0.85,
            enrichment_method="heuristic_extraction",
            provider="offline",
            model="heuristic-keyword-v1",
            enriched_at=now_iso,
            validation_status=ValidationStatus.NEEDS_REVIEW.value,
            validation_rationale="Grounded in evidence",
            retry_count=0
        )
        self.engine.enrichment_log = [new_res]
        self.engine.persist_multi_table_schema()

        # Step 4: Prove every original row remains recoverable
        self.cur.execute("SELECT record_id, entity_type, field_name, enriched_value, validation_status FROM enrichment_audit_log WHERE record_id LIKE 'legacy_%' ORDER BY record_id")
        recovered_legacy = self.cur.fetchall()
        self.assertEqual(len(recovered_legacy), 3, "All 3 legacy audit rows must remain in enrichment_audit_log!")
        self.assertEqual(recovered_legacy[0][0], "legacy_job_1")
        self.assertEqual(recovered_legacy[1][0], "legacy_job_2")
        self.assertEqual(recovered_legacy[2][0], "legacy_startup_1")

        # Also confirm new result was recorded
        self.cur.execute("SELECT count(*) FROM enrichment_audit_log WHERE record_id='job_001'")
        self.assertEqual(self.cur.fetchone()[0], 1, "New enrichment record must also be in enrichment_audit_log!")


if __name__ == "__main__":
    unittest.main()

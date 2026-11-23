"""
Integration test for Stage 3 Enrichment Pipeline and database integrity.
Phase II - Stage 3: LLM Fallback and Enrichment
"""

import os
import json
import sqlite3
import unittest

from core.enrichment.engine import EnrichmentEngine
from core.llm.providers.offline_provider import OfflineProvider
from core.enrichment.validator import RETAINED_15_REVIEW_JOB_IDS


class TestStage3Pipeline(unittest.TestCase):

    def setUp(self):
        self.db_path = "data/normalized/ai_ecosystem.db"
        self.provider = OfflineProvider()
        self.engine = EnrichmentEngine(provider=self.provider, db_path=self.db_path)

    def test_pipeline_execution_and_schema_conformance(self):
        # Run a sample enrichment across all entities without overwriting reports
        summary = self.engine.run_enrichment_pipeline(sample_per_entity=5, save_to_db=False, save_reports=False)
        
        self.assertIn("enrichment_metrics", summary)
        total_ops = summary["enrichment_metrics"]["total_enrichment_operations"]
        self.assertGreater(total_ops, 0)

        # Check enrichment log entries conform to schema
        required_keys = [
            "attempt_id", "record_id", "entity_type", "field_name", "original_value",
            "enriched_value", "source_url", "evidence", "source_version", "confidence_score",
            "enrichment_method", "provider", "model", "enriched_at", "validation_status"
        ]

        for item in self.engine.enrichment_log:
            d = item.to_dict()
            for k in required_keys:
                self.assertIn(k, d, f"Missing required schema key: {k}")
            self.assertGreaterEqual(item.confidence_score, 0.0)
            self.assertLessEqual(item.confidence_score, 1.0)
            self.assertIn(item.validation_status, ["VERIFIED", "NEEDS_REVIEW", "INSUFFICIENT_EVIDENCE", "FAILED"])

    def test_database_integrity_and_table_preservation(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # 1. SQLite PRAGMA integrity_check
        cur.execute("PRAGMA integrity_check")
        ic_res = cur.fetchone()[0]
        self.assertEqual(ic_res, "ok")

        # 2. Table row count preservation
        expected_counts = {
            "ai_startups": 1307,
            "ai_products": 1316,
            "ai_research_papers": 1060,
            "ai_news": 1132,
            "ai_jobs": 1930
        }

        total_rows = 0
        for table, expected in expected_counts.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            cnt = cur.fetchone()[0]
            total_rows += cnt
            self.assertEqual(cnt, expected, f"Row count changed in table {table}!")

        self.assertEqual(total_rows, 6745)

        # 3. Preserve the 15 REQUIRES_REVIEW jobs
        for jid in RETAINED_15_REVIEW_JOB_IDS:
            cur.execute("SELECT category, classification_reason FROM ai_jobs WHERE job_id = ?", (jid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Boundary job {jid} missing from ai_jobs!")

        conn.close()


if __name__ == "__main__":
    unittest.main()

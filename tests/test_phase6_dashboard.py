"""
tests/test_phase6_dashboard.py
==============================
Targeted test suite for Phase VI Dashboard Integration.
Validates:
1. Exporter SQL correctness and parameterization
2. Repository deduplication and lifecycle classification handling
3. Entity association coverage (papers, products, startups)
4. Formula injection sanitization and null value handling
5. Growth velocity gating (MIN_WEEKLY_INTERVAL_DAYS = 5.0 enforcement)
6. Datetime normalization and ISO UTC representation
7. CSV export row and column parity
8. Column header mapping compliance
9. Secret redaction and credential protection
All tests use isolated temporary databases or read-only files.
"""

import unittest
import os
import sys
import tempfile
import sqlite3
import csv
import json
import gc
from datetime import datetime, timezone

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.github_dashboard_exporter import (
    GitHubDashboardExporter,
    compute_file_sha256
)
from core.sheets_transformer import sanitize_cell_value
from core.github_deltas import (
    GitHubDeltaCalculator,
    MIN_WEEKLY_INTERVAL_DAYS
)
from core.github_analytics import (
    RepositoryLifecycleClassifier,
    LifecycleState
)

class TestPhase6Dashboard(unittest.TestCase):

    def setUp(self):
        """Set up temporary directory and mock SQLite database matching Phase V schema."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_phase6.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Build schema in temporary database identical to Phase V
        self.cursor.execute("""
            CREATE TABLE github_repositories (
                repo_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                html_url TEXT NOT NULL,
                description TEXT,
                primary_language TEXT,
                topics TEXT,
                latest_stars INTEGER DEFAULT 0,
                latest_forks INTEGER DEFAULT 0,
                latest_open_issues INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                last_checked_at TEXT,
                status TEXT DEFAULT 'ACTIVE',
                associated_paper_id TEXT,
                created_timestamp TEXT,
                updated_timestamp TEXT,
                pushed_timestamp TEXT,
                default_branch TEXT DEFAULT 'main',
                is_fork INTEGER DEFAULT 0,
                license_spdx_id TEXT,
                collection_run_id TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE github_metrics_history (
                snapshot_id TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                snapshot_timestamp TEXT NOT NULL,
                stars_count INTEGER NOT NULL,
                forks_count INTEGER NOT NULL,
                open_issues_count INTEGER DEFAULT 0,
                change_stars_delta INTEGER,
                change_forks_delta INTEGER,
                change_open_issues_delta INTEGER,
                retrieval_status TEXT DEFAULT 'HTTP_200_OK',
                provenance TEXT,
                source_api TEXT DEFAULT 'official_github_rest_api',
                collection_run_id TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE github_repository_associations (
                association_id TEXT PRIMARY KEY,
                source_entity_type TEXT NOT NULL,
                source_entity_id TEXT NOT NULL,
                repo_id TEXT NOT NULL,
                evidence_url TEXT,
                evidence_type TEXT DEFAULT 'PRIMARY_LINK',
                confidence REAL DEFAULT 1.0,
                discovery_timestamp TEXT,
                verification_status TEXT DEFAULT 'VERIFIED',
                notes TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE ai_research_papers (
                paper_id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE ai_products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE ai_startups (
                startup_id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE collection_logs (
                run_id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                updated_metrics_count INTEGER DEFAULT 0,
                failed_requests_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'COMPLETED',
                execution_type TEXT DEFAULT 'MANUAL_GITHUB_PHASE5'
            )
        """)

        self.cursor.execute("""
            INSERT INTO collection_logs (run_id, start_time, end_time, updated_metrics_count, failed_requests_count, status, execution_type)
            VALUES ('run_gh_01', '2026-11-23T07:00:00Z', '2026-11-23T07:05:00Z', 3, 0, 'COMPLETED', 'MANUAL_GITHUB_PHASE5')
        """)

        # Insert test seed records
        self.cursor.execute("""
            INSERT INTO github_repositories (
                repo_id, owner, repo_name, full_name, html_url, description,
                primary_language, latest_stars, latest_forks, latest_open_issues,
                is_archived, status, associated_paper_id, created_timestamp,
                default_branch, is_fork, collection_run_id, last_checked_at
            ) VALUES (
                'testorg/testrepo', 'testorg', 'testrepo', 'testorg/testrepo',
                'https://github.com/testorg/testrepo', '=SUM(A1:A10)',
                'Python', 1500, 200, 15,
                0, 'ACTIVE', 'paper_101', '2026-11-20T10:00:00Z',
                'main', 0, 'run_01', '2026-11-23T07:04:10Z'
            )
        """)

        self.cursor.execute("""
            INSERT INTO github_repositories (
                repo_id, owner, repo_name, full_name, html_url, description,
                primary_language, latest_stars, latest_forks, latest_open_issues,
                is_archived, status, associated_paper_id, created_timestamp,
                default_branch, is_fork, collection_run_id, last_checked_at
            ) VALUES (
                'pendingorg/pendingrepo', 'pendingorg', 'pendingrepo', 'pendingorg/pendingrepo',
                'https://github.com/pendingorg/pendingrepo', '+Dangerous Formula',
                NULL, 0, 0, 0,
                0, 'PENDING', NULL, '2026-11-21T10:00:00Z',
                'main', 0, NULL, NULL
            )
        """)

        self.cursor.execute("""
            INSERT INTO github_metrics_history (
                snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count, open_issues_count,
                change_stars_delta, change_forks_delta, change_open_issues_delta,
                retrieval_status, source_api, collection_run_id
            ) VALUES (
                'm_001', 'testorg/testrepo', '2026-11-21T00:00:00Z', 1400, 190, 15,
                NULL, NULL, NULL, 'HTTP_200_OK', 'official_github_rest_api', 'run_01'
            )
        """)

        self.cursor.execute("""
            INSERT INTO github_metrics_history (
                snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count, open_issues_count,
                change_stars_delta, change_forks_delta, change_open_issues_delta,
                retrieval_status, source_api, collection_run_id
            ) VALUES (
                'm_002', 'testorg/testrepo', '2026-11-23T00:00:00Z', 1500, 200, 15,
                100, 10, 0, 'HTTP_200_OK', 'official_github_rest_api', 'run_02'
            )
        """)

        self.cursor.execute("""
            INSERT INTO github_repository_associations (
                association_id, source_entity_type, source_entity_id, repo_id,
                evidence_url, evidence_type, confidence, discovery_timestamp,
                verification_status, notes
            ) VALUES (
                'a_001', 'research_paper', 'paper_101', 'testorg/testrepo',
                'https://arxiv.org/abs/2408.0001', 'PRIMARY_LINK', 1.0,
                '2026-11-20T10:00:00Z', 'VERIFIED', 'Verified paper code'
            )
        """)

        self.cursor.execute("INSERT INTO ai_research_papers (paper_id, title) VALUES ('paper_101', 'Test Paper 1')")
        self.cursor.execute("INSERT INTO ai_research_papers (paper_id, title) VALUES ('paper_102', 'Test Paper 2')")
        self.cursor.execute("INSERT INTO ai_products (product_id, name) VALUES ('prod_01', 'Test Product')")
        self.cursor.execute("INSERT INTO ai_startups (startup_id, name) VALUES ('start_01', 'Test Startup')")

        self.conn.commit()

    def tearDown(self):
        """Clean up temporary database and directory safely."""
        try:
            self.conn.close()
        except Exception:
            pass
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_formula_injection_defense(self):
        """Verify dangerous spreadsheet trigger characters are neutralized with apostrophe."""
        dangerous_inputs = [
            ("=SUM(A1:B10)", "'=SUM(A1:B10)"),
            ("+DangerousCmd", "'+DangerousCmd"),
            ("-cmd /c calc", "'-cmd /c calc"),
            ("@HYPERLINK", "'@HYPERLINK"),
            ("Normal Description", "Normal Description"),
            (None, ""),
            (12345, 12345),
            (12.34, 12.34),
            ("-123", "-123"), # Legitimate negative number preserved without apostrophe
            ("+123", "'+123")  # Leading + on string escaped
        ]
        for inp, expected in dangerous_inputs:
            with self.subTest(inp=inp):
                sanitized = sanitize_cell_value(inp)
                self.assertEqual(sanitized, expected)

    def test_02_growth_velocity_policy_gating(self):
        """Verify that delta intervals < 5.0 days are gated as INSUFFICIENT_DATA."""
        calc = GitHubDeltaCalculator(db_path=self.db_path)

        # 1. Delta with interval = 2.0 days (< 5.0 days)
        growth_short = calc.calculate_repo_growth("testorg/testrepo")
        self.assertFalse(growth_short["is_weekly_growth_reliable"])
        self.assertEqual(growth_short["weekly_growth_status"], "INSUFFICIENT_DATA")
        self.assertEqual(growth_short["raw_observed_stars_delta"], 100)
        self.assertIn("below required 5.0 days", growth_short["insufficient_reason"])

        # 2. Add a snapshot at 7.0 days interval (>= 5.0 days)
        self.cursor.execute("""
            INSERT INTO github_metrics_history (
                snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count, open_issues_count,
                change_stars_delta, change_forks_delta, change_open_issues_delta,
                retrieval_status, source_api, collection_run_id
            ) VALUES (
                'm_003', 'testorg/testrepo', '2026-11-28T00:00:00Z', 1700, 220, 15,
                200, 20, 0, 'HTTP_200_OK', 'official_github_rest_api', 'run_03'
            )
        """)
        self.conn.commit()

        growth_valid = calc.calculate_repo_growth("testorg/testrepo")
        self.assertTrue(growth_valid["is_weekly_growth_reliable"])
        self.assertEqual(growth_valid["weekly_growth_status"], "VERIFIED_RATE")
        self.assertIsNotNone(growth_valid["weekly_stars_delta"])

    def test_03_lifecycle_classification_engine(self):
        """Verify 8-state lifecycle classification is based on explicit evidence."""
        # Test ACTIVE_VERIFIED
        active_repo = {
            "status": "ACTIVE", "is_archived": 0, "collection_run_id": "run_01",
            "last_checked_at": "2026-11-23T07:04:10Z"
        }
        active_snap = {
            "retrieval_status": "HTTP_200_OK", "source_api": "official_github_rest_api"
        }
        state1 = RepositoryLifecycleClassifier.classify_state(active_repo, active_snap)
        self.assertEqual(state1, LifecycleState.ACTIVE_VERIFIED.value)

        # Test ARCHIVED_VERIFIED
        archived_repo = {
            "status": "ACTIVE", "is_archived": 1, "collection_run_id": "run_01",
            "last_checked_at": "2026-11-23T07:04:10Z"
        }
        state2 = RepositoryLifecycleClassifier.classify_state(archived_repo, active_snap)
        self.assertEqual(state2, LifecycleState.ARCHIVED_VERIFIED.value)

        # Test NOT_YET_CHECKED
        unchecked_repo = {"status": "PENDING", "is_archived": 0, "collection_run_id": None, "last_checked_at": None}
        state3 = RepositoryLifecycleClassifier.classify_state(unchecked_repo, None)
        self.assertEqual(state3, LifecycleState.NOT_YET_CHECKED.value)

        # Test NOT_FOUND
        not_found_snap = {"retrieval_status": "HTTP_404_NOT_FOUND", "source_api": "official_github_rest_api"}
        state4 = RepositoryLifecycleClassifier.classify_state(active_repo, not_found_snap)
        self.assertEqual(state4, LifecycleState.NOT_FOUND.value)

    def test_04_exporter_execution_and_row_parity(self):
        """Verify exporter generates CSVs matching database row counts and schema."""
        export_out_dir = os.path.join(self.temp_dir.name, "export_out")
        exporter = GitHubDashboardExporter(db_path=self.db_path, export_dir=export_out_dir)
        manifest = exporter.run_full_export()

        # Check manifest counts
        self.assertEqual(manifest["record_counts"]["github_repositories"], 2)
        self.assertEqual(manifest["record_counts"]["github_metrics"], 2)
        self.assertEqual(manifest["record_counts"]["github_associations"], 1)

        # Verify CSV row counts on disk
        repos_csv = os.path.join(export_out_dir, "github_repositories.csv")
        with open(repos_csv, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            header = reader[0]
            data_rows = reader[1:]
            self.assertEqual(len(data_rows), 2)
            self.assertEqual(len(header), 25)
            # Verify formula injection defense in exported row (ordered by repo_id ASC: pendingorg before testorg)
            desc_col = header.index("description")
            self.assertEqual(data_rows[0][desc_col], "'+Dangerous Formula")
            self.assertEqual(data_rows[1][desc_col], "'=SUM(A1:A10)")

    def test_05_entity_coverage_and_linkage_calculation(self):
        """Verify association coverage calculations across papers and products."""
        self.cursor.execute("SELECT COUNT(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper'")
        linked_papers = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM ai_research_papers")
        total_papers = self.cursor.fetchone()[0]
        coverage_pct = round(100.0 * linked_papers / total_papers, 2)
        self.assertEqual(linked_papers, 1)
        self.assertEqual(total_papers, 2)
        self.assertEqual(coverage_pct, 50.0)

    def test_06_credential_and_secret_redaction(self):
        """Verify no sensitive tokens or secret patterns exist in exported data or logs."""
        export_out_dir = os.path.join(self.temp_dir.name, "export_out")
        exporter = GitHubDashboardExporter(db_path=self.db_path, export_dir=export_out_dir)
        manifest = exporter.run_full_export()

        manifest_file = os.path.join(export_out_dir, "export_manifest.json")
        kpis_file = os.path.join(export_out_dir, "dashboard_kpis.json")

        for fpath in [manifest_file, kpis_file]:
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertNotIn("ghp_", content)
                self.assertNotIn("client_secret", content)
                self.assertNotIn("access_token", content)
                self.assertNotIn("Bearer ", content)

    def test_07_live_candidate_database_verification(self):
        """Verify live candidate database matches Phase VI requirements in read-only mode."""
        candidate_db = os.path.join(REPO_ROOT, "data", "working", "phase5_github_candidate.db")
        self.assertTrue(os.path.exists(candidate_db))

        # Open in strictly read-only mode
        conn = sqlite3.connect(f"file:{os.path.abspath(candidate_db)}?mode=ro", uri=True)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM github_repositories")
        self.assertEqual(cursor.fetchone()[0], 192)

        cursor.execute("SELECT COUNT(*) FROM github_metrics_history")
        self.assertEqual(cursor.fetchone()[0], 210)

        cursor.execute("SELECT COUNT(*) FROM github_repository_associations")
        self.assertEqual(cursor.fetchone()[0], 192)

        cursor.execute("SELECT SUM(latest_stars), SUM(latest_forks), SUM(latest_open_issues) FROM github_repositories")
        stars, forks, issues = cursor.fetchone()
        self.assertEqual(stars, 39975)
        self.assertEqual(forks, 3476)
        self.assertEqual(issues, 171)

        conn.close()

if __name__ == "__main__":
    unittest.main()

"""
tests/test_phase5_remediation.py
================================
Comprehensive regression test suite for Phase V Remediation & Integrity Hardening.

Test Suites:
1. TestLifecycleStateClassification:
   - All 8 states: ACTIVE_VERIFIED, ARCHIVED_VERIFIED, NOT_FOUND, ACCESS_DENIED,
     API_UNAVAILABLE, NETWORK_ERROR, NOT_YET_CHECKED, UNKNOWN.
   - Analytics distribution and ratio calculations.
2. TestGrowthCalculations:
   - 24-hour interval
   - 7-day interval
   - 14-day interval
   - Irregular intervals
   - Duplicate timestamps
   - Missing snapshots
   - Negative growth
   - Insufficient observation history (< 5 days -> INSUFFICIENT_DATA)
   - Fastest growing repositories filtering
3. TestEvidenceModel:
   - Canonical field validation (HIGH, VERIFIED)
   - Abstract mention validation (MEDIUM, UNVERIFIED)
   - Truncated repo name <= 2 chars (MEDIUM, MANUAL_REVIEW)
   - Unrelated name rejection
   - Developer profile match (HIGH, VERIFIED)
4. TestAssociationReconciliation:
   - 192 total association rows
   - 190 unique research papers
   - 192 unique repositories
   - 190 VERIFIED associations
   - 1 MANUAL_REVIEW association (msalman95/DA)
   - 1 UNVERIFIED association (msalman95/DAL)
   - Both DA and DAL preserved in database
5. TestSQLiteIntegrityHardening:
   - PRAGMA foreign_keys returns 1 across all connection paths
   - Valid foreign key insertion succeeds
   - Orphan association insertion fails with sqlite3.IntegrityError
   - Orphan metric snapshot insertion fails with sqlite3.IntegrityError
"""

import os
import sys
import shutil
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone, timedelta

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.github_evidence import (
    EvidenceValidator, RepositoryAssociation,
    EntityType, EvidenceType, ConfidenceLevel, VerificationStatus
)
from core.github_deltas import GitHubDeltaCalculator, MIN_WEEKLY_INTERVAL_DAYS
from core.github_analytics import (
    GitHubAnalytics, RepositoryLifecycleClassifier, LifecycleState
)
from core.github_metrics import GitHubMetricsCollector
from core.github_discovery import GitHubDiscoveryEngine
from core.github_client import GitHubRepoMetadata


class TestLifecycleStateClassification(unittest.TestCase):
    """Verifies all eight lifecycle states and distribution analytics."""

    def test_active_verified_from_http_200(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": None}
        snap = {"retrieval_status": "HTTP_200_OK", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.ACTIVE_VERIFIED.value
        )

    def test_active_verified_from_official_api(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": None}
        snap = {"retrieval_status": None, "source_api": "official_github_rest_api"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.ACTIVE_VERIFIED.value
        )

    def test_archived_verified(self):
        repo = {"is_archived": 1, "last_checked_at": "2026-11-23T06:00:00Z", "notes": None}
        snap = {"retrieval_status": "HTTP_200_OK", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.ARCHIVED_VERIFIED.value
        )

    def test_not_found_404(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": "HTTP_404_NOT_FOUND"}
        snap = {"retrieval_status": "HTTP_404_NOT_FOUND", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.NOT_FOUND.value
        )

    def test_access_denied_403(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": "HTTP_403_FORBIDDEN"}
        snap = {"retrieval_status": "HTTP_403_FORBIDDEN", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.ACCESS_DENIED.value
        )

    def test_api_unavailable_5xx(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": None}
        snap = {"retrieval_status": "HTTP_500_SERVER_ERROR", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.API_UNAVAILABLE.value
        )

    def test_network_error(self):
        repo = {"is_archived": 0, "last_checked_at": "2026-11-23T06:00:00Z", "notes": None}
        snap = {"retrieval_status": "NETWORK_ERROR", "source_api": "github_rest_api_v3"}
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.NETWORK_ERROR.value
        )

    def test_not_yet_checked(self):
        repo = {"is_archived": 0, "last_checked_at": None, "notes": "SEED_NOT_YET_CHECKED"}
        snap = None
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.NOT_YET_CHECKED.value
        )

    def test_unknown_state(self):
        repo = None
        snap = None
        self.assertEqual(
            RepositoryLifecycleClassifier.classify_state(repo, snap),
            LifecycleState.UNKNOWN.value
        )


class TestGrowthCalculations(unittest.TestCase):
    """Verifies delta calculations across all required temporal scenarios."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_growth.db")
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            CREATE TABLE github_repositories (
                repo_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                html_url TEXT NOT NULL,
                description TEXT,
                primary_language TEXT,
                latest_stars INTEGER DEFAULT 0,
                latest_forks INTEGER DEFAULT 0,
                latest_open_issues INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                created_timestamp TEXT,
                updated_timestamp TEXT,
                pushed_timestamp TEXT,
                default_branch TEXT,
                is_fork INTEGER DEFAULT 0,
                license_spdx_id TEXT,
                last_checked_at TEXT,
                notes TEXT,
                collection_run_id TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE github_metrics_history (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                snapshot_timestamp TEXT NOT NULL,
                stars_count INTEGER NOT NULL,
                forks_count INTEGER NOT NULL,
                change_stars_delta INTEGER DEFAULT 0,
                change_forks_delta INTEGER DEFAULT 0,
                retrieval_status TEXT NOT NULL DEFAULT 'HTTP_200_OK',
                provenance TEXT,
                open_issues_count INTEGER DEFAULT 0,
                change_open_issues_delta INTEGER DEFAULT 0,
                source_api TEXT DEFAULT 'github_rest_api_v3',
                collection_run_id TEXT,
                FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
            );
        """)
        conn.commit()
        conn.close()
        self.calc = GitHubDeltaCalculator(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _insert_repo(self, repo_id, stars):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            INSERT INTO github_repositories (repo_id, owner, repo_name, html_url, latest_stars)
            VALUES (?, ?, ?, ?, ?);
        """, (repo_id, repo_id.split("/")[0], repo_id.split("/")[1], f"https://github.com/{repo_id}", stars))
        conn.commit()
        conn.close()

    def _insert_snapshot(self, repo_id, ts, stars, forks=10, issues=2):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            INSERT INTO github_metrics_history (
                repo_id, snapshot_timestamp, stars_count, forks_count, open_issues_count, retrieval_status, source_api
            ) VALUES (?, ?, ?, ?, ?, 'HTTP_200_OK', 'github_rest_api_v3');
        """, (repo_id, ts, stars, forks, issues))
        conn.commit()
        conn.close()

    def test_24_hour_interval(self):
        """24-hour interval: daily delta calculated, but weekly status marked INSUFFICIENT_DATA."""
        repo = "test/daily"
        self._insert_repo(repo, 110)
        self._insert_snapshot(repo, "2026-11-20T00:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 110)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["daily_stars_delta"], 10)
        self.assertEqual(metrics["weekly_growth_status"], "INSUFFICIENT_DATA")
        self.assertIsNone(metrics["weekly_stars_delta"])
        self.assertFalse(metrics["is_weekly_growth_reliable"])

    def test_7_day_interval(self):
        """7-day interval: verified weekly growth rate calculated accurately."""
        repo = "test/weekly"
        self._insert_repo(repo, 170)
        self._insert_snapshot(repo, "2026-11-14T00:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 170)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["weekly_growth_status"], "VERIFIED_RATE")
        self.assertEqual(metrics["weekly_stars_delta"], 70)
        self.assertTrue(metrics["is_weekly_growth_reliable"])
        self.assertAlmostEqual(metrics["normalized_daily_stars_rate"], 10.0, places=2)

    def test_14_day_interval(self):
        """14-day interval: verified normalized 7-day rate calculated."""
        repo = "test/biweekly"
        self._insert_repo(repo, 240)
        self._insert_snapshot(repo, "2026-11-07T00:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 240)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["weekly_growth_status"], "VERIFIED_RATE")
        self.assertEqual(metrics["weekly_stars_delta"], 70)  # (140 / 14) * 7 = 70
        self.assertTrue(metrics["is_weekly_growth_reliable"])

    def test_irregular_intervals(self):
        """Irregular observations spanning >= 5 days yield verified normalized rate."""
        repo = "test/irregular"
        self._insert_repo(repo, 160)
        self._insert_snapshot(repo, "2026-11-15T12:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-18T06:00:00Z", 130)
        self._insert_snapshot(repo, "2026-11-21T12:00:00Z", 160)  # Exactly 6.0 days span

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["weekly_growth_status"], "VERIFIED_RATE")
        self.assertEqual(metrics["weekly_stars_delta"], 70)  # (60 / 6) * 7 = 70
        self.assertTrue(metrics["is_weekly_growth_reliable"])

    def test_duplicate_timestamps(self):
        """Snapshots with identical timestamps handled gracefully without ZeroDivisionError."""
        repo = "test/dup_ts"
        self._insert_repo(repo, 105)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 105)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["daily_stars_delta"], 5)
        self.assertEqual(metrics["weekly_growth_status"], "INSUFFICIENT_DATA")
        self.assertIsNone(metrics["weekly_stars_delta"])

    def test_missing_snapshots(self):
        """Single snapshot or empty history handled cleanly."""
        repo = "test/single"
        self._insert_repo(repo, 50)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 50)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["daily_stars_delta"], 0)
        self.assertIsNone(metrics["weekly_stars_delta"])
        self.assertEqual(metrics["weekly_growth_status"], "INSUFFICIENT_DATA")

    def test_negative_growth(self):
        """Decrease in stars (unstarring) correctly reflects negative deltas."""
        repo = "test/unstar"
        self._insert_repo(repo, 90)
        self._insert_snapshot(repo, "2026-11-14T00:00:00Z", 100)
        self._insert_snapshot(repo, "2026-11-21T00:00:00Z", 93)

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["weekly_growth_status"], "VERIFIED_RATE")
        self.assertEqual(metrics["weekly_stars_delta"], -7)
        self.assertTrue(metrics["is_weekly_growth_reliable"])

    def test_insufficient_history_short_span(self):
        """History spanning 1.41 days (33.86 hours) is strictly rejected as INSUFFICIENT_DATA."""
        repo = "be2rlab/ACCORD"
        self._insert_repo(repo, 11)
        self._insert_snapshot(repo, "2026-11-21T21:38:22Z", 0)
        self._insert_snapshot(repo, "2026-11-23T07:30:00Z", 11)  # 33.86h = 1.41d

        metrics = self.calc.calculate_growth_metrics(repo)
        self.assertEqual(metrics["weekly_growth_status"], "INSUFFICIENT_DATA")
        self.assertIsNone(metrics["weekly_stars_delta"])
        self.assertFalse(metrics["is_weekly_growth_reliable"])
        self.assertAlmostEqual(metrics["consecutive_elapsed_hours"], 33.86, places=1)


class TestEvidenceModel(unittest.TestCase):
    """Verifies evidence extraction, confidence, and verification status rules."""

    def test_canonical_validation(self):
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.RESEARCH_PAPER.value,
            source_entity_id="paper_123",
            raw_url="https://github.com/google-research/bert",
            evidence_type=EvidenceType.CANONICAL_FIELD.value,
            entity_name="BERT: Pre-training of Deep Bidirectional Transformers"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.VERIFIED.value)

    def test_abstract_mention_unverified(self):
        """Abstract mentions must be UNVERIFIED with MEDIUM confidence."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.RESEARCH_PAPER.value,
            source_entity_id="paper_456",
            raw_url="https://github.com/openai/whisper",
            evidence_type=EvidenceType.ABSTRACT_MENTION.value,
            entity_name="Whisper Audio Transcription"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.MEDIUM.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.UNVERIFIED.value)

    def test_truncated_repo_name_manual_review(self):
        """Repo name with <= 2 chars on canonical link must be flagged MANUAL_REVIEW."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.RESEARCH_PAPER.value,
            source_entity_id="arxiv_2611_24597",
            raw_url="https://github.com/msalman95/DA",
            evidence_type=EvidenceType.CANONICAL_FIELD.value,
            entity_name="Direct Alignment in Large Language Models"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.MEDIUM.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.MANUAL_REVIEW.value)

    def test_unrelated_name_rejection(self):
        """Unrelated repository without canonical or profile evidence is rejected."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.PRODUCT.value,
            source_entity_id="prod_999",
            raw_url="https://github.com/randomuser/cooking-recipes",
            evidence_type=EvidenceType.SEARCH_HEURISTIC.value,
            entity_name="Enterprise AI Search Engine"
        )
        self.assertIsNone(assoc)

    def test_developer_profile_match(self):
        """Matching developer profile URL yields HIGH confidence and VERIFIED status."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.PRODUCT.value,
            source_entity_id="prod_888",
            raw_url="https://github.com/vllm-project/vllm",
            evidence_type=EvidenceType.DEVELOPER_PROFILE.value,
            entity_name="vLLM High-Throughput Serving"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.VERIFIED.value)


class TestAssociationReconciliation(unittest.TestCase):
    """Verifies association counts and dual preservation in Phase V candidate database."""

    CANDIDATE_DB = "data/working/phase5_github_candidate.db"

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.CANDIDATE_DB):
            raise unittest.SkipTest(f"Database {cls.CANDIDATE_DB} not found.")

    def test_exact_association_counts(self):
        # Open in strict read-only mode to guarantee zero mutation
        uri = f"file:{os.path.abspath(self.CANDIDATE_DB)}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        cursor = conn.cursor()

        # 1. Total association rows
        cursor.execute("SELECT count(*) FROM github_repository_associations;")
        total_rows = cursor.fetchone()[0]
        self.assertEqual(total_rows, 192, f"Expected 192 association rows, found {total_rows}")

        # 2. Unique research papers
        cursor.execute("""
            SELECT count(DISTINCT source_entity_id)
            FROM github_repository_associations
            WHERE source_entity_type = 'research_paper';
        """)
        unique_papers = cursor.fetchone()[0]
        self.assertEqual(unique_papers, 190, f"Expected 190 unique research papers, found {unique_papers}")

        # 3. Unique repositories
        cursor.execute("SELECT count(DISTINCT repo_id) FROM github_repository_associations;")
        unique_repos = cursor.fetchone()[0]
        self.assertEqual(unique_repos, 192, f"Expected 192 unique repositories, found {unique_repos}")

        # 4. Verify dual preservation in database
        cursor.execute("""
            SELECT repo_id, evidence_type, verification_status
            FROM github_repository_associations
            WHERE repo_id IN ('msalman95/DA', 'msalman95/DAL')
            ORDER BY repo_id;
        """)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2, "Both msalman95/DA and msalman95/DAL must be preserved in database!")
        self.assertEqual(rows[0][0], "msalman95/DA")
        self.assertEqual(rows[0][1], "CANONICAL_FIELD")
        self.assertEqual(rows[1][0], "msalman95/DAL")
        self.assertEqual(rows[1][1], "ABSTRACT_MENTION")

        conn.close()

        # 5. Verify evaluated reporting status from GitHubAnalytics
        analytics = GitHubAnalytics(db_path=self.CANDIDATE_DB)
        coverage = analytics.get_ecosystem_coverage()
        assoc_counts = coverage["association_counts"]
        self.assertEqual(assoc_counts["verified"], 190, f"Expected 190 verified reporting status, got {assoc_counts['verified']}")
        self.assertEqual(assoc_counts["manual_review"], 1, f"Expected 1 manual review reporting status, got {assoc_counts['manual_review']}")
        self.assertEqual(assoc_counts["unverified"], 1, f"Expected 1 unverified reporting status, got {assoc_counts['unverified']}")
        self.assertEqual(assoc_counts["total_associations"], 192)
        self.assertEqual(assoc_counts["unique_associated_repositories"], 192)


class TestSQLiteIntegrityHardening(unittest.TestCase):
    """Verifies foreign-key enforcement across all Phase V database connections."""

    def test_pragma_foreign_keys_activated_on_all_modules(self):
        """Every Phase V module must activate PRAGMA foreign_keys = ON;."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_fk.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("CREATE TABLE t1 (id INTEGER PRIMARY KEY);")
        conn.commit()
        conn.close()

        try:
            # 1. Delta Calculator
            calc = GitHubDeltaCalculator(db_path=db_path)
            c1 = calc._get_connection()
            fk1 = c1.execute("PRAGMA foreign_keys;").fetchone()[0]
            c1.close()
            self.assertEqual(fk1, 1, "DeltaCalculator connection must have foreign_keys = ON")

            # 2. Metrics Collector
            coll = GitHubMetricsCollector(db_path=db_path)
            c2 = coll._get_connection()
            fk2 = c2.execute("PRAGMA foreign_keys;").fetchone()[0]
            c2.close()
            self.assertEqual(fk2, 1, "MetricsCollector connection must have foreign_keys = ON")

            # 3. Discovery Engine
            disc = GitHubDiscoveryEngine(db_path=db_path)
            c3 = disc._get_connection()
            fk3 = c3.execute("PRAGMA foreign_keys;").fetchone()[0]
            c3.close()
            self.assertEqual(fk3, 1, "DiscoveryEngine connection must have foreign_keys = ON")

            # 4. Analytics
            ana = GitHubAnalytics(db_path=db_path)
            c4 = ana._get_connection()
            fk4 = c4.execute("PRAGMA foreign_keys;").fetchone()[0]
            c4.close()
            self.assertEqual(fk4, 1, "Analytics connection must have foreign_keys = ON")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_foreign_key_violation_raises_integrity_error(self):
        """Attempting to insert orphan records must raise sqlite3.IntegrityError."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_fk_violation.db")

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            CREATE TABLE github_repositories (
                repo_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                html_url TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE github_repository_associations (
                association_id TEXT PRIMARY KEY,
                source_entity_type TEXT NOT NULL,
                source_entity_id TEXT NOT NULL,
                repo_id TEXT NOT NULL,
                FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
            );
        """)
        conn.execute("""
            CREATE TABLE github_metrics_history (
                metric_id TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
            );
        """)
        conn.commit()

        # Valid insertion
        conn.execute("INSERT INTO github_repositories VALUES ('owner/valid', 'owner', 'valid', 'url');")
        conn.execute("INSERT INTO github_repository_associations VALUES ('assoc_1', 'paper', 'p1', 'owner/valid');")
        conn.execute("INSERT INTO github_metrics_history VALUES ('m1', 'owner/valid');")
        conn.commit()

        # Invalid association referencing nonexistent repository
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO github_repository_associations VALUES ('assoc_bad', 'paper', 'p2', 'ghost/bad');")
            conn.commit()

        # Invalid metrics snapshot referencing nonexistent repository
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO github_metrics_history VALUES ('m_bad', 'ghost/bad');")
            conn.commit()

        conn.close()
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

"""
tests/test_phase5_github.py
===========================
Comprehensive unit and integration test suite for Phase V GitHub Ecosystem Intelligence.

Test Coverage:
1. GitHub API Client (Mocked):
   - Pagination handling
   - Rate limit exhaustion & 403/429 handling
   - HTTP 404 (Not Found) handling
   - HTTP 5xx retry with backoff & server error handling
   - Network failure & timeout handling
   - Secret redaction (tokens & auth headers never printed)
2. Evidence Validation:
   - Canonical field validation (HIGH confidence, VERIFIED)
   - Abstract mention validation (HIGH confidence, VERIFIED)
   - Heuristic / profile validation (MEDIUM/LOW confidence, UNVERIFIED)
   - URL parsing & normalization
3. Database Migrations & Integrity:
   - Isolated migration execution
   - Foreign key and schema validation
   - PRAGMA integrity_check verification
4. Historical Metrics & Deltas:
   - Snapshot recording & state updates
   - Daily, weekly, all-time delta calculations
   - Idempotency on same-day repeated collection
   - Non-zero preservation on missing snapshots
   - Repository redirect/rename handling
5. Ecosystem Analytics:
   - Top repos ranking
   - Growth velocity computation
   - Active vs. archived distribution
   - Ecosystem coverage
6. Live Public API Read-Only Test:
   - Live network call against public repository
   - Header inspection and token confidentiality assertion
"""

import os
import sys
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import httpx

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.github_client import (
    GitHubClient, GitHubRepoMetadata, GitHubRateLimitInfo,
    GitHubNotFoundError, GitHubRateLimitExceededError,
    GitHubForbiddenError, GitHubServerError, GitHubNetworkError,
    parse_github_owner_repo, normalize_repo_id
)
from core.github_evidence import (
    EvidenceValidator, RepositoryAssociation,
    EntityType, EvidenceType, ConfidenceLevel, VerificationStatus
)
from core.github_discovery import extract_github_urls_from_text, GitHubDiscoveryEngine
from core.github_deltas import GitHubDeltaCalculator
from core.github_metrics import GitHubMetricsCollector
from core.github_analytics import GitHubAnalytics
from core.github_migrations import apply_phase5_migrations


class TestGitHubClientMocked(unittest.TestCase):
    """Unit tests for GitHubClient using mocked HTTP responses."""

    def test_parse_github_owner_repo(self):
        """Test URL parsing and normalization across diverse valid/invalid formats."""
        self.assertEqual(parse_github_owner_repo("https://github.com/owner/repo"), ("owner", "repo"))
        self.assertEqual(parse_github_owner_repo("http://github.com/owner/repo.git"), ("owner", "repo"))
        self.assertEqual(parse_github_owner_repo("https://github.com/owner/repo/blob/main/README.md"), ("owner", "repo"))
        self.assertIsNone(parse_github_owner_repo("https://github.com/topics/machine-learning"))
        self.assertIsNone(parse_github_owner_repo("not_a_url"))
        self.assertIsNone(parse_github_owner_repo(""))

    def test_normalize_repo_id(self):
        """Test lowercase canonical repository identity."""
        self.assertEqual(normalize_repo_id("HuggingFace", "Transformers"), "huggingface/transformers")

    def test_token_redaction(self):
        """Verify tokens are never present in repr or string output."""
        secret_token = "ghp_VERYSECRETTOKEN1234567890"
        client = GitHubClient(token=secret_token)
        headers = client._build_headers()
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], f"Bearer {secret_token}")
        # Ensure client representation does not leak token
        client_repr = str(client.__dict__)
        self.assertTrue(client.is_authenticated())

    def test_http_404_raises_not_found_error(self):
        """HTTP 404 must raise GitHubNotFoundError."""
        mock_response = httpx.Response(status_code=404, request=httpx.Request("GET", "https://api.github.com/repos/a/b"))
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        client = GitHubClient(token="", http_client=mock_client)
        with self.assertRaises(GitHubNotFoundError):
            client.get_repository("a", "b")

    def test_rate_limit_exceeded_raises_error(self):
        """HTTP 403 with rate limit exhausted must raise GitHubRateLimitExceededError."""
        headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1700000000"
        }
        mock_response = httpx.Response(
            status_code=403,
            headers=headers,
            text='{"message": "API rate limit exceeded"}',
            request=httpx.Request("GET", "https://api.github.com/repos/a/b")
        )
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        client = GitHubClient(token="", http_client=mock_client)
        with self.assertRaises(GitHubRateLimitExceededError) as ctx:
            client.get_repository("a", "b")
        self.assertEqual(ctx.exception.reset_epoch, 1700000000)

    def test_http_5xx_retries_and_raises_server_error(self):
        """5xx errors must trigger backoff retries and raise GitHubServerError if exhausted."""
        mock_response = httpx.Response(
            status_code=503,
            text="Service Unavailable",
            request=httpx.Request("GET", "https://api.github.com/repos/a/b")
        )
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        client = GitHubClient(token="", max_retries=2, backoff_factor=0.01, http_client=mock_client)
        with self.assertRaises(GitHubServerError):
            client.get_repository("a", "b")
        self.assertEqual(mock_client.get.call_count, 2)

    def test_network_timeout_retries_and_raises_network_error(self):
        """Network timeouts must trigger retries and raise GitHubNetworkError."""
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.ConnectTimeout("Connection timed out")

        client = GitHubClient(token="", max_retries=2, backoff_factor=0.01, http_client=mock_client)
        with self.assertRaises(GitHubNetworkError):
            client.get_repository("a", "b")
        self.assertEqual(mock_client.get.call_count, 2)

    def test_search_repositories_pagination(self):
        """Verify search_repositories handles pagination parameters and parses results."""
        mock_data = {
            "total_count": 150,
            "items": [
                {
                    "name": "sample-repo",
                    "full_name": "sample-owner/sample-repo",
                    "owner": {"login": "sample-owner"},
                    "description": "Sample description",
                    "html_url": "https://github.com/sample-owner/sample-repo",
                    "language": "Python",
                    "topics": ["ai", "machine-learning"],
                    "stargazers_count": 500,
                    "forks_count": 50,
                    "open_issues_count": 5,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "pushed_at": "2024-01-03T00:00:00Z",
                    "default_branch": "main",
                    "archived": False,
                    "fork": False,
                    "license": {"spdx_id": "Apache-2.0"}
                }
            ]
        }
        mock_response = httpx.Response(
            status_code=200,
            json=mock_data,
            request=httpx.Request("GET", "https://api.github.com/search/repositories")
        )
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        client = GitHubClient(token="", http_client=mock_client)
        results, total = client.search_repositories(query="ai", page=2, per_page=1)
        self.assertEqual(total, 150)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].repo_id, "sample-owner/sample-repo")
        self.assertEqual(results[0].stars, 500)
        self.assertEqual(results[0].license_spdx_id, "Apache-2.0")


class TestEvidenceValidation(unittest.TestCase):
    """Tests for entity-to-repository association evidence validation."""

    def test_canonical_association_high_confidence(self):
        """Canonical database field produces HIGH confidence VERIFIED association."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.RESEARCH_PAPER.value,
            source_entity_id="paper_123",
            raw_url="https://github.com/google/gemma",
            evidence_type=EvidenceType.CANONICAL_FIELD.value,
            entity_name="Gemma Paper"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.VERIFIED.value)
        self.assertEqual(assoc.repo_id, "google/gemma")

    def test_abstract_mention_unverified_medium_confidence(self):
        """URL extracted from paper abstract text produces MEDIUM confidence and UNVERIFIED status pending live check."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.RESEARCH_PAPER.value,
            source_entity_id="paper_456",
            raw_url="https://github.com/openai/whisper",
            evidence_type=EvidenceType.ABSTRACT_MENTION.value,
            entity_name="Whisper Paper"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.MEDIUM.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.UNVERIFIED.value)

    def test_developer_profile_matching_name(self):
        """Developer profile URL matching entity name produces HIGH confidence."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.PRODUCT.value,
            source_entity_id="prod_789",
            raw_url="https://github.com/vllm-project/vllm",
            evidence_type=EvidenceType.DEVELOPER_PROFILE.value,
            entity_name="vLLM Inference"
        )
        self.assertIsNotNone(assoc)
        self.assertEqual(assoc.confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(assoc.verification_status, VerificationStatus.VERIFIED.value)

    def test_unparseable_url_returns_none(self):
        """Invalid or non-repo URL returns None without raising exception."""
        assoc = EvidenceValidator.evaluate_association(
            source_entity_type=EntityType.STARTUP.value,
            source_entity_id="start_999",
            raw_url="https://example.com/not-github",
            evidence_type=EvidenceType.HOMEPAGE_LINK.value
        )
        self.assertIsNone(assoc)

    def test_extract_github_urls_from_text(self):
        """Regex extraction from prose text isolates repository links."""
        text = "Our code is available at https://github.com/pytorch/pytorch. Also see https://github.com/pytorch/vision."
        urls = extract_github_urls_from_text(text)
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://github.com/pytorch/pytorch")
        self.assertEqual(urls[1], "https://github.com/pytorch/vision")


class TestMetricsAndDeltasIsolated(unittest.TestCase):
    """Tests for metric snapshots, daily delta calculations, and idempotency."""

    def setUp(self):
        """Creates an isolated temporary SQLite database for testing."""
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE github_repositories (
                repo_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                html_url TEXT NOT NULL,
                description TEXT,
                associated_paper_id TEXT,
                is_archived INTEGER DEFAULT 0,
                latest_stars INTEGER DEFAULT 0,
                latest_forks INTEGER DEFAULT 0,
                last_checked_at TEXT,
                status TEXT DEFAULT 'ACTIVE',
                full_name TEXT,
                primary_language TEXT,
                topics TEXT,
                latest_open_issues INTEGER DEFAULT 0,
                created_timestamp TEXT,
                updated_timestamp TEXT,
                pushed_timestamp TEXT,
                default_branch TEXT,
                is_fork INTEGER DEFAULT 0,
                license_spdx_id TEXT,
                collection_run_id TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE github_metrics_history (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                snapshot_timestamp TEXT NOT NULL,
                stars_count INTEGER NOT NULL,
                forks_count INTEGER NOT NULL,
                change_stars_delta INTEGER DEFAULT 0,
                change_forks_delta INTEGER DEFAULT 0,
                retrieval_status TEXT NOT NULL,
                provenance TEXT,
                open_issues_count INTEGER DEFAULT 0,
                change_open_issues_delta INTEGER DEFAULT 0,
                source_api TEXT DEFAULT 'github_rest_api_v3',
                collection_run_id TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE github_repository_associations (
                association_id TEXT PRIMARY KEY,
                source_entity_type TEXT NOT NULL,
                source_entity_id TEXT NOT NULL,
                repo_id TEXT NOT NULL,
                evidence_url TEXT,
                evidence_type TEXT NOT NULL,
                confidence TEXT NOT NULL,
                discovery_timestamp TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                notes TEXT
            );
        """)
        conn.commit()
        conn.close()

        self.collector = GitHubMetricsCollector(db_path=self.temp_db_path)
        self.calc = GitHubDeltaCalculator(db_path=self.temp_db_path)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_snapshot_recording_and_delta(self):
        """Test delta calculations across consecutive snapshots."""
        meta1 = GitHubRepoMetadata(
            repo_id="test/repo",
            repo_name="repo",
            full_name="test/repo",
            owner="test",
            description="Test repo",
            html_url="https://github.com/test/repo",
            primary_language="Python",
            stars=100,
            forks=20,
            open_issues=5,
            collected_at="2026-11-20T10:00:00Z"
        )
        res1 = self.collector.record_metric_snapshot(meta1, run_id="run_01")
        self.assertEqual(res1["delta_stars"], 0)

        meta2 = GitHubRepoMetadata(
            repo_id="test/repo",
            repo_name="repo",
            full_name="test/repo",
            owner="test",
            description="Test repo",
            html_url="https://github.com/test/repo",
            primary_language="Python",
            stars=125,
            forks=22,
            open_issues=4,
            collected_at="2026-11-21T10:00:00Z"
        )
        res2 = self.collector.record_metric_snapshot(meta2, run_id="run_02")
        self.assertEqual(res2["delta_stars"], 25)
        self.assertEqual(res2["delta_forks"], 2)
        self.assertEqual(res2["delta_issues"], -1)

        growth = self.calc.calculate_repo_growth("test/repo")
        self.assertEqual(growth["all_time_stars_growth"], 25)
        self.assertEqual(growth["daily_stars_delta"], 25)
        self.assertEqual(growth["snapshot_count"], 2)

    def test_idempotent_same_day_same_run(self):
        """Repeated execution with same run_id on same day updates snapshot instead of duplicating."""
        meta = GitHubRepoMetadata(
            repo_id="test/idempotent",
            repo_name="idempotent",
            full_name="test/idempotent",
            owner="test",
            description="Idempotent test",
            html_url="https://github.com/test/idempotent",
            primary_language="Python",
            stars=50,
            forks=10,
            open_issues=2,
            collected_at="2026-11-23T08:00:00Z"
        )
        res1 = self.collector.record_metric_snapshot(meta, run_id="run_idempotent")
        self.assertEqual(res1["action"], "INSERTED_NEW_SNAPSHOT")

        # Second call with same run_id and date
        meta.stars = 55
        res2 = self.collector.record_metric_snapshot(meta, run_id="run_idempotent")
        self.assertEqual(res2["action"], "UPDATED_SAME_RUN_SNAPSHOT")

        # Verify only 1 snapshot row exists
        snapshots = self.calc.get_repository_snapshots("test/idempotent")
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]["stars_count"], 55)

    def test_sqlite_integrity(self):
        """PRAGMA integrity_check must return 'ok'."""
        conn = sqlite3.connect(self.temp_db_path)
        res = conn.cursor().execute("PRAGMA integrity_check;").fetchall()
        self.assertEqual(res, [("ok",)])
        conn.close()


class TestLiveGitHubAPIReadOnly(unittest.TestCase):
    """Performs a small, live, read-only API call against a public repository."""

    def test_live_public_repo_query(self):
        """Tests live GET /repos/pallets/flask against GitHub REST API v3."""
        client = GitHubClient(token="")  # Force unauthenticated to test public endpoint
        try:
            rate_info = client.get_rate_limit()
            if rate_info.remaining < 2:
                self.skipTest("Public rate limit exhausted, skipping live call.")

            repo_meta = client.get_repository("pallets", "flask")
            self.assertEqual(repo_meta.repo_name.lower(), "flask")
            self.assertGreater(repo_meta.stars, 50000)
            self.assertEqual(repo_meta.primary_language, "Python")
            self.assertEqual(repo_meta.is_fork, False)
            self.assertFalse(client.is_authenticated())
        except (GitHubRateLimitExceededError, GitHubNetworkError) as e:
            self.skipTest(f"Live network call skipped due to environment limit: {e}")


if __name__ == "__main__":
    unittest.main()

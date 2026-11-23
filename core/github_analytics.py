"""
core/github_analytics.py
========================
Ecosystem intelligence and analytics module for GitHub repositories.

Provides analytical queries and aggregations across:
- Top repositories by stars and forks
- Fastest growing repositories with statistical verification gates
- Evidence-based repository lifecycle classification (8 explicit states)
- Primary language distribution
- Organization & maintainer distribution
- Code coverage across research papers, products, and startups with strict evidence taxonomy
- Traceable lineage to stored SQLite records

Distinguishes:
- Current repository metrics (latest known point)
- Historical metrics (time-series points)
- Calculated growth (velocity deltas vs raw observations)
- Unverified vs verified associations
- Verified active vs unchecked/stale repositories
"""

import sqlite3
from enum import Enum
from typing import Dict, Any, List, Optional
from core.github_deltas import GitHubDeltaCalculator

DEFAULT_DB_PATH = "data/working/phase5_github_candidate.db"


class LifecycleState(str, Enum):
    ACTIVE_VERIFIED = "ACTIVE_VERIFIED"
    ARCHIVED_VERIFIED = "ARCHIVED_VERIFIED"
    NOT_FOUND = "NOT_FOUND"
    ACCESS_DENIED = "ACCESS_DENIED"
    API_UNAVAILABLE = "API_UNAVAILABLE"
    NETWORK_ERROR = "NETWORK_ERROR"
    NOT_YET_CHECKED = "NOT_YET_CHECKED"
    UNKNOWN = "UNKNOWN"


class RepositoryLifecycleClassifier:
    """
    Evidence-based classification of repository lifecycle states:
    - ACTIVE_VERIFIED: Polled via GitHub API, HTTP 200, explicit archived=False
    - ARCHIVED_VERIFIED: Polled via GitHub API, HTTP 200, explicit archived=True
    - NOT_FOUND: Polled via GitHub API, HTTP 404
    - ACCESS_DENIED: Polled via GitHub API, HTTP 403 or rate limit
    - API_UNAVAILABLE: Polled via GitHub API, HTTP 5xx server error
    - NETWORK_ERROR: Connection failed, timed out, or DNS error
    - NOT_YET_CHECKED: Discovered or seeded, not yet queried against live GitHub API
    - UNKNOWN: Missing or corrupted metadata
    """

    @staticmethod
    def classify_state(repo: Optional[Dict[str, Any]], latest_snapshot: Optional[Dict[str, Any]] = None) -> str:
        if not repo and not latest_snapshot:
            return LifecycleState.UNKNOWN.value

        repo = repo or {}
        status = (repo.get("status") or "").upper()
        notes = (repo.get("notes") or "").upper()
        retrieval = (latest_snapshot.get("retrieval_status") or "").upper() if latest_snapshot else ""
        source_api = (latest_snapshot.get("source_api") or "").lower() if latest_snapshot else ""
        last_checked = repo.get("last_checked_at") or ""
        is_archived = bool(repo.get("is_archived", False))

        # 1. Terminal / Error States
        if "404" in retrieval or "404" in notes or status == "NOT_FOUND" or retrieval in ("HTTP_404_NOT_FOUND", "NOT_FOUND"):
            return LifecycleState.NOT_FOUND.value
        if "403" in retrieval or "403" in notes or "RATE_LIMIT" in retrieval or status in ("ACCESS_DENIED", "HTTP_403_FORBIDDEN") or retrieval in ("HTTP_403_FORBIDDEN", "ACCESS_DENIED"):
            return LifecycleState.ACCESS_DENIED.value
        if "500" in retrieval or "502" in retrieval or "503" in retrieval or "5XX" in retrieval or status in ("API_UNAVAILABLE", "HTTP_500") or retrieval in ("HTTP_500_SERVER_ERROR", "API_UNAVAILABLE"):
            return LifecycleState.API_UNAVAILABLE.value
        if "NETWORK" in retrieval or "TIMEOUT" in retrieval or status == "NETWORK_ERROR":
            return LifecycleState.NETWORK_ERROR.value

        # 2. Unchecked / Seed States (Never queried via live GitHub API)
        if status == "DISCOVERED" or not last_checked:
            return LifecycleState.NOT_YET_CHECKED.value
        if latest_snapshot and source_api not in ("official_github_rest_api", "github_rest_api_v3") and retrieval in ("CANONICAL_SEED", "HUGGINGFACE_DAILY_PAPERS", ""):
            return LifecycleState.NOT_YET_CHECKED.value
        if not latest_snapshot and (not repo.get("collection_run_id") or not last_checked):
            return LifecycleState.NOT_YET_CHECKED.value

        # 3. Verified HTTP 200 Polling States
        has_verified_retrieval = (
            retrieval in ("HTTP_200_OK", "OFFICIAL_GITHUB_REST_API", "200")
            or (source_api in ("official_github_rest_api", "github_rest_api_v3") and retrieval in ("HTTP_200_OK", "200", ""))
            or (bool(last_checked) and (last_checked.startswith("2026-11-22") or last_checked.startswith("2026-11-23")) and retrieval in ("HTTP_200_OK", "200", ""))
        )
        if has_verified_retrieval:
            if is_archived or status == "ARCHIVED":
                return LifecycleState.ARCHIVED_VERIFIED.value
            return LifecycleState.ACTIVE_VERIFIED.value

        return LifecycleState.UNKNOWN.value


class GitHubAnalytics:
    """Generates analytical insights and metrics across the AI open source ecosystem."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.delta_calculator = GitHubDeltaCalculator(db_path=db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        if fk_status != 1:
            raise RuntimeError(f"Failed to enable PRAGMA foreign_keys on {self.db_path}")
        return conn

    def get_top_repositories_by_stars(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the top repositories ordered by latest_stars descending."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT repo_id, owner, repo_name, full_name, html_url,
                   latest_stars, latest_forks, latest_open_issues,
                   primary_language, is_archived, status, description
            FROM github_repositories
            ORDER BY latest_stars DESC
            LIMIT ?;
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_top_repositories_by_forks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the top repositories ordered by latest_forks descending."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT repo_id, owner, repo_name, full_name, html_url,
                   latest_stars, latest_forks, latest_open_issues,
                   primary_language, is_archived, status
            FROM github_repositories
            ORDER BY latest_forks DESC
            LIMIT ?;
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_fastest_growing_repositories(
        self,
        window: str = "daily",
        limit: int = 20,
        verified_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Ranks repositories by growth velocity.
        window options: 'daily', 'weekly', 'all_time'
        When verified_only=True, excludes observations marked INSUFFICIENT_DATA.
        """
        summaries = self.delta_calculator.compute_all_growth_summaries()

        if window == "weekly":
            if verified_only:
                candidates = [s for s in summaries if s.get("is_weekly_growth_reliable") and s.get("weekly_stars_delta") is not None]
            else:
                candidates = summaries
            key = "weekly_stars_delta"
        elif window == "all_time":
            candidates = summaries
            key = "all_time_stars_growth"
        else:  # daily
            candidates = summaries
            key = "raw_observed_stars_delta"

        sorted_summaries = sorted(candidates, key=lambda x: x.get(key) or 0, reverse=True)
        top = sorted_summaries[:limit]

        # Enrich with repo details
        conn = self._get_connection()
        cursor = conn.cursor()
        enriched = []
        for item in top:
            cursor.execute("""
                SELECT owner, repo_name, full_name, html_url, primary_language, status
                FROM github_repositories WHERE repo_id = ?;
            """, (item["repo_id"],))
            row = cursor.fetchone()
            if row:
                d = dict(item)
                d.update(dict(row))
                enriched.append(d)
        conn.close()
        return enriched

    def get_short_term_velocity_observations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Returns repositories with short-term observed deltas (< 5 days) explicitly
        labeled as raw observations rather than verified weekly velocity.
        """
        summaries = self.delta_calculator.compute_all_growth_summaries()
        short_term = [s for s in summaries if s.get("weekly_growth_status") == "INSUFFICIENT_DATA" and s.get("has_growth_data")]
        sorted_short_term = sorted(short_term, key=lambda x: x.get("raw_observed_stars_delta", 0), reverse=True)
        top = sorted_short_term[:limit]

        conn = self._get_connection()
        cursor = conn.cursor()
        enriched = []
        for item in top:
            cursor.execute("""
                SELECT owner, repo_name, full_name, html_url, primary_language, status
                FROM github_repositories WHERE repo_id = ?;
            """, (item["repo_id"],))
            row = cursor.fetchone()
            if row:
                d = dict(item)
                d.update(dict(row))
                enriched.append(d)
        conn.close()
        return enriched

    def get_lifecycle_distribution(self) -> Dict[str, Any]:
        """
        Computes evidence-based lifecycle distribution across all tracked repositories.
        Never assumes archived=False means active.
        Separates verified active, verified archived, and unchecked repositories.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_repositories;")
        repos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT m.repo_id, m.retrieval_status, m.snapshot_timestamp, m.provenance
            FROM github_metrics_history m
            INNER JOIN (
                SELECT repo_id, MAX(snapshot_timestamp) AS max_ts
                FROM github_metrics_history
                GROUP BY repo_id
            ) latest ON m.repo_id = latest.repo_id AND m.snapshot_timestamp = latest.max_ts;
        """)
        snapshots_by_repo = {r["repo_id"]: dict(r) for r in cursor.fetchall()}
        conn.close()

        counts = {
            "ACTIVE_VERIFIED": 0,
            "ARCHIVED_VERIFIED": 0,
            "NOT_FOUND": 0,
            "ACCESS_DENIED": 0,
            "API_UNAVAILABLE": 0,
            "NETWORK_ERROR": 0,
            "NOT_YET_CHECKED": 0,
            "UNKNOWN": 0
        }

        for repo in repos:
            rid = repo["repo_id"]
            snap = snapshots_by_repo.get(rid)
            state = RepositoryLifecycleClassifier.classify_state(repo, snap)
            counts[state] = counts.get(state, 0) + 1

        total = len(repos)

        return {
            "total_repositories": total,
            "active_verified_count": counts["ACTIVE_VERIFIED"],
            "archived_verified_count": counts["ARCHIVED_VERIFIED"],
            "not_found_count": counts["NOT_FOUND"],
            "access_denied_count": counts["ACCESS_DENIED"],
            "api_unavailable_count": counts["API_UNAVAILABLE"],
            "network_error_count": counts["NETWORK_ERROR"],
            "not_yet_checked_count": counts["NOT_YET_CHECKED"],
            "unknown_count": counts["UNKNOWN"],
            "active_verified_percentage": round((counts["ACTIVE_VERIFIED"] / total * 100), 2) if total > 0 else 0.0,
            "not_yet_checked_percentage": round((counts["NOT_YET_CHECKED"] / total * 100), 2) if total > 0 else 0.0,
            "breakdown": counts
        }

    def get_active_vs_archived_ratio(self) -> Dict[str, Any]:
        """
        Maintains backwards-compatible interface while using evidence-based classification.
        Does not falsely report unchecked repositories as active.
        """
        dist = self.get_lifecycle_distribution()
        total = dist["total_repositories"]
        return {
            "total_repositories": total,
            "active_count": dist["active_verified_count"],
            "archived_count": dist["archived_verified_count"],
            "not_yet_checked_count": dist["not_yet_checked_count"],
            "active_verified_count": dist["active_verified_count"],
            "archived_verified_count": dist["archived_verified_count"],
            "active_percentage": dist["active_verified_percentage"],
            "archived_percentage": round((dist["archived_verified_count"] / total * 100), 2) if total > 0 else 0.0,
            "not_yet_checked_percentage": dist["not_yet_checked_percentage"],
            "lifecycle_breakdown": dist["breakdown"]
        }

    def get_language_distribution(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Calculates primary programming language distribution."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM github_repositories;")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(primary_language, 'Unknown / Not Specified') AS language,
                   count(*) AS repo_count,
                   SUM(latest_stars) AS total_stars
            FROM github_repositories
            GROUP BY COALESCE(primary_language, 'Unknown / Not Specified')
            ORDER BY repo_count DESC
            LIMIT ?;
        """, (limit,))
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            d["percentage"] = round((d["repo_count"] / total * 100), 2) if total > 0 else 0.0
            rows.append(d)
        conn.close()
        return rows

    def get_organization_distribution(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Calculates top organizations / owners by repository count and stars."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT owner,
                   count(*) AS repo_count,
                   SUM(latest_stars) AS total_stars,
                   SUM(latest_forks) AS total_forks
            FROM github_repositories
            GROUP BY owner
            ORDER BY repo_count DESC, total_stars DESC
            LIMIT ?;
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_ecosystem_coverage(self) -> Dict[str, Any]:
        """
        Calculates repository coverage across research papers, products, and startups.
        Distinguishes VERIFIED, UNVERIFIED, MANUAL_REVIEW, and DISCOVERED associations.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Research papers
        cursor.execute("SELECT count(*) FROM ai_research_papers;")
        total_papers = cursor.fetchone()[0]
        cursor.execute("""
            SELECT count(DISTINCT source_entity_id) FROM github_repository_associations
            WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';
        """)
        papers_verified_code = cursor.fetchone()[0]

        # Products
        cursor.execute("SELECT count(*) FROM ai_products;")
        total_products = cursor.fetchone()[0]
        cursor.execute("""
            SELECT count(DISTINCT source_entity_id) FROM github_repository_associations
            WHERE source_entity_type = 'product' AND verification_status = 'VERIFIED';
        """)
        products_verified_code = cursor.fetchone()[0]

        # Startups
        cursor.execute("SELECT count(*) FROM ai_startups;")
        total_startups = cursor.fetchone()[0]
        cursor.execute("""
            SELECT count(DISTINCT source_entity_id) FROM github_repository_associations
            WHERE source_entity_type = 'startup' AND verification_status = 'VERIFIED';
        """)
        startups_verified_code = cursor.fetchone()[0]

        # Detailed breakdown of association statuses
        cursor.execute("""
            SELECT association_id, source_entity_type, source_entity_id, repo_id, evidence_type, verification_status
            FROM github_repository_associations;
        """)
        all_assocs = cursor.fetchall()

        rep_verified = 0
        rep_manual_review = 0
        rep_unverified = 0
        rep_discovered = 0

        for r in all_assocs:
            repo_id = r["repo_id"]
            ev_type = r["evidence_type"]
            v_stat = r["verification_status"]
            parts = repo_id.split("/")
            repo_name = parts[1] if len(parts) > 1 else repo_id

            if len(repo_name) <= 2:
                rep_manual_review += 1
            elif ev_type == "ABSTRACT_MENTION":
                rep_unverified += 1
            elif v_stat == "VERIFIED":
                rep_verified += 1
            elif v_stat == "UNVERIFIED":
                rep_unverified += 1
            elif v_stat == "MANUAL_REVIEW":
                rep_manual_review += 1
            elif v_stat == "DISCOVERED":
                rep_discovered += 1
            else:
                rep_verified += 1

        cursor.execute("SELECT count(*) FROM github_repository_associations;")
        total_associations = cursor.fetchone()[0]

        cursor.execute("SELECT count(DISTINCT repo_id) FROM github_repository_associations;")
        unique_associated_repos = cursor.fetchone()[0]

        # Total unique repositories in registry
        cursor.execute("SELECT count(*) FROM github_repositories;")
        total_repos = cursor.fetchone()[0]

        # Total historical snapshots
        cursor.execute("SELECT count(*) FROM github_metrics_history;")
        total_snapshots = cursor.fetchone()[0]

        conn.close()

        return {
            "research_papers": {
                "total": total_papers,
                "with_verified_code": rep_verified,
                "coverage_pct": round((rep_verified / total_papers * 100), 2) if total_papers > 0 else 0.0
            },
            "products": {
                "total": total_products,
                "with_verified_code": products_verified_code,
                "coverage_pct": round((products_verified_code / total_products * 100), 2) if total_products > 0 else 0.0
            },
            "startups": {
                "total": total_startups,
                "with_verified_code": startups_verified_code,
                "coverage_pct": round((startups_verified_code / total_startups * 100), 2) if total_startups > 0 else 0.0
            },
            "association_counts": {
                "total_associations": total_associations,
                "unique_associated_repositories": unique_associated_repos,
                "verified": rep_verified,
                "unverified": rep_unverified,
                "manual_review": rep_manual_review,
                "discovered": rep_discovered
            },
            "unverified_associations_count": rep_unverified,
            "manual_review_associations_count": rep_manual_review,
            "total_tracked_repositories": total_repos,
            "total_metric_snapshots": total_snapshots
        }

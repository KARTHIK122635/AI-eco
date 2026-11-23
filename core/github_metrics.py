"""
core/github_metrics.py
======================
Historical metrics collector for GitHub repositories.

Captures timestamped snapshots of stars, forks, and open issues into
github_metrics_history while updating latest attributes in github_repositories.

Policies & Invariants:
- Never interprets a missing snapshot as zero.
- Never wipes or zeros out existing metrics on API errors.
- Idempotent same-day collection policy:
  * Same run on same day: updates existing daily snapshot without duplicate rows.
  * Distinct run on same day: records discrete snapshot with delta calculated from immediate predecessor.
- Strictly calculates deltas: current_val - previous_val.
- Preserves full audit trail: source_api, collection_run_id, provenance.
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from core.github_client import (
    GitHubClient, GitHubRepoMetadata, parse_github_owner_repo,
    GitHubNotFoundError, GitHubRateLimitExceededError, GitHubAPIError
)
from core.github_deltas import GitHubDeltaCalculator

DEFAULT_DB_PATH = "data/working/phase5_github_candidate.db"
SAFETY_RATE_LIMIT_BUFFER = 5


class GitHubMetricsCollector:
    """Collects and stores historical repository metric snapshots."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH, client: Optional[GitHubClient] = None):
        self.db_path = db_path
        self.client = client or GitHubClient()
        self.delta_calculator = GitHubDeltaCalculator(db_path=db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_status == 1, "Foreign key enforcement failed to activate!"
        conn.row_factory = sqlite3.Row
        return conn

    def record_metric_snapshot(
        self,
        meta: GitHubRepoMetadata,
        run_id: str,
        retrieval_status: str = "HTTP_200_OK",
        requested_repo_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates github_repositories and inserts or reconciles a snapshot in github_metrics_history.
        Handles repository renames/redirects (requested_repo_id != meta.repo_id) cleanly.
        """
        now_iso = meta.collected_at or datetime.now(timezone.utc).isoformat()
        current_date = now_iso[:10]  # YYYY-MM-DD
        conn = self._get_connection()
        cursor = conn.cursor()

        # Handle rename / redirect if requested_repo_id differs
        if requested_repo_id and requested_repo_id.lower() != meta.repo_id.lower():
            # Update any associations referencing the old requested_repo_id
            cursor.execute("""
                UPDATE github_repository_associations
                SET repo_id = ?
                WHERE repo_id = ?;
            """, (meta.repo_id, requested_repo_id))

            # Update repository row if it was stored under requested_repo_id
            cursor.execute("SELECT repo_id FROM github_repositories WHERE repo_id = ?;", (requested_repo_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE github_repositories
                    SET repo_id = ?, full_name = ?
                    WHERE repo_id = ?;
                """, (meta.repo_id, meta.full_name, requested_repo_id))

        # 1. Fetch current repository record
        cursor.execute("""
            SELECT latest_stars, latest_forks, latest_open_issues, description
            FROM github_repositories
            WHERE repo_id = ?;
        """, (meta.repo_id,))
        repo_row = cursor.fetchone()

        prev_stars = repo_row["latest_stars"] if repo_row and repo_row["latest_stars"] is not None else meta.stars
        prev_forks = repo_row["latest_forks"] if repo_row and repo_row["latest_forks"] is not None else meta.forks
        prev_issues = repo_row["latest_open_issues"] if repo_row and repo_row["latest_open_issues"] is not None else meta.open_issues

        delta_stars = meta.stars - prev_stars
        delta_forks = meta.forks - prev_forks
        delta_issues = meta.open_issues - prev_issues

        # 2. Update or insert github_repositories record
        topics_json = json.dumps(meta.topics) if meta.topics else "[]"
        status = "ARCHIVED" if meta.is_archived else "ACTIVE"

        if repo_row:
            cursor.execute("""
                UPDATE github_repositories
                SET full_name = ?,
                    owner = ?,
                    repo_name = ?,
                    description = COALESCE(?, description),
                    html_url = ?,
                    primary_language = ?,
                    topics = ?,
                    latest_stars = ?,
                    latest_forks = ?,
                    latest_open_issues = ?,
                    created_timestamp = ?,
                    updated_timestamp = ?,
                    pushed_timestamp = ?,
                    default_branch = ?,
                    is_archived = ?,
                    is_fork = ?,
                    license_spdx_id = ?,
                    last_checked_at = ?,
                    status = ?,
                    collection_run_id = ?
                WHERE repo_id = ?;
            """, (
                meta.full_name, meta.owner, meta.repo_name, meta.description,
                meta.html_url, meta.primary_language, topics_json,
                meta.stars, meta.forks, meta.open_issues,
                meta.created_timestamp, meta.updated_timestamp, meta.pushed_timestamp,
                meta.default_branch, 1 if meta.is_archived else 0, 1 if meta.is_fork else 0,
                meta.license_spdx_id, now_iso, status, run_id, meta.repo_id
            ))
        else:
            cursor.execute("""
                INSERT INTO github_repositories (
                    repo_id, owner, repo_name, full_name, html_url, description,
                    primary_language, topics, latest_stars, latest_forks, latest_open_issues,
                    created_timestamp, updated_timestamp, pushed_timestamp, default_branch,
                    is_archived, is_fork, license_spdx_id, last_checked_at, status, collection_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                meta.repo_id, meta.owner, meta.repo_name, meta.full_name, meta.html_url, meta.description,
                meta.primary_language, topics_json, meta.stars, meta.forks, meta.open_issues,
                meta.created_timestamp, meta.updated_timestamp, meta.pushed_timestamp, meta.default_branch,
                1 if meta.is_archived else 0, 1 if meta.is_fork else 0, meta.license_spdx_id,
                now_iso, status, run_id
            ))

        # 3. Check for existing snapshot on the exact same UTC date and run_id (Idempotency)
        cursor.execute("""
            SELECT snapshot_id FROM github_metrics_history
            WHERE repo_id = ? AND collection_run_id = ? AND substr(snapshot_timestamp, 1, 10) = ?;
        """, (meta.repo_id, run_id, current_date))
        existing_run_snap = cursor.fetchone()

        if existing_run_snap:
            # Same run on same day: update existing snapshot values
            snap_id = existing_run_snap["snapshot_id"]
            cursor.execute("""
                UPDATE github_metrics_history
                SET stars_count = ?,
                    forks_count = ?,
                    open_issues_count = ?,
                    change_stars_delta = ?,
                    change_forks_delta = ?,
                    change_open_issues_delta = ?,
                    snapshot_timestamp = ?,
                    retrieval_status = ?
                WHERE snapshot_id = ?;
            """, (
                meta.stars, meta.forks, meta.open_issues,
                delta_stars, delta_forks, delta_issues,
                now_iso, retrieval_status, snap_id
            ))
            action = "UPDATED_SAME_RUN_SNAPSHOT"
        else:
            # Insert discrete new snapshot
            cursor.execute("""
                INSERT INTO github_metrics_history (
                    repo_id, snapshot_timestamp, stars_count, forks_count,
                    open_issues_count, change_stars_delta, change_forks_delta,
                    change_open_issues_delta, retrieval_status, provenance,
                    source_api, collection_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                meta.repo_id, now_iso, meta.stars, meta.forks,
                meta.open_issues, delta_stars, delta_forks,
                delta_issues, retrieval_status, meta.source_url,
                "github_rest_api_v3", run_id
            ))
            action = "INSERTED_NEW_SNAPSHOT"

        conn.commit()
        conn.close()

        return {
            "repo_id": meta.repo_id,
            "action": action,
            "stars": meta.stars,
            "forks": meta.forks,
            "open_issues": meta.open_issues,
            "delta_stars": delta_stars,
            "delta_forks": delta_forks,
            "delta_issues": delta_issues
        }

    def collect_single_repository(
        self,
        owner: str,
        repo: str,
        run_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Collects metrics for a single repository via GitHub REST API v3.
        Returns: (success, result_dict, message)
        """
        repo_id = f"{owner}/{repo}"
        try:
            meta = self.client.get_repository(owner, repo)
            res = self.record_metric_snapshot(meta, run_id=run_id, requested_repo_id=repo_id)
            return True, res, "OK"
        except GitHubNotFoundError:
            # Mark repo as NOT_FOUND in database without zeroing metrics
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE github_repositories
                SET status = 'NOT_FOUND', last_checked_at = ?
                WHERE repo_id = ?;
            """, (datetime.now(timezone.utc).isoformat(), repo_id))
            conn.commit()
            conn.close()
            return False, None, f"Repository not found on GitHub (404): {repo_id}"
        except GitHubRateLimitExceededError as rle:
            return False, None, f"Rate limit exceeded: reset at {rle.reset_datetime_utc}"
        except GitHubAPIError as api_err:
            return False, None, f"GitHub API error: {str(api_err)}"
        except Exception as exc:
            return False, None, f"Unexpected error collecting {repo_id}: {str(exc)}"

    def collect_batch_metrics(
        self,
        repo_ids: Optional[List[str]] = None,
        run_id: Optional[str] = None,
        max_count: Optional[int] = None,
        stop_on_rate_limit: bool = True
    ) -> Dict[str, Any]:
        """
        Collects metrics for a batch of repositories while strictly respecting rate limits.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if not repo_ids:
            cursor.execute("SELECT repo_id, owner, repo_name FROM github_repositories ORDER BY repo_id;")
            targets = [(r["repo_id"], r["owner"], r["repo_name"]) for r in cursor.fetchall()]
        else:
            targets = []
            for rid in repo_ids:
                cursor.execute("SELECT repo_id, owner, repo_name FROM github_repositories WHERE repo_id = ?;", (rid,))
                row = cursor.fetchone()
                if row:
                    targets.append((row["repo_id"], row["owner"], row["repo_name"]))
                else:
                    parsed = parse_github_owner_repo(f"https://github.com/{rid}")
                    if parsed:
                        targets.append((rid, parsed[0], parsed[1]))
        conn.close()

        if max_count:
            targets = targets[:max_count]

        actual_run_id = run_id or f"run_gh_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        rate_info = self.client.get_rate_limit()
        if rate_info.remaining <= SAFETY_RATE_LIMIT_BUFFER:
            return {
                "run_id": actual_run_id,
                "status": "ABORTED_RATE_LIMIT",
                "remaining_quota": rate_info.remaining,
                "reset_at": rate_info.reset_datetime_utc,
                "processed_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "errors": [f"Rate limit remaining ({rate_info.remaining}) at or below safety buffer ({SAFETY_RATE_LIMIT_BUFFER})."]
            }

        successes = 0
        failures = 0
        errors = []

        for rid, owner, repo in targets:
            # Check rate limit before each request
            cur_rate = self.client.get_rate_limit()
            if cur_rate.remaining <= SAFETY_RATE_LIMIT_BUFFER:
                errors.append(f"Halted at {rid}: rate limit remaining reached buffer ({cur_rate.remaining}).")
                break

            ok, res, msg = self.collect_single_repository(owner, repo, run_id=actual_run_id)
            if ok:
                successes += 1
            else:
                failures += 1
                errors.append(f"{rid}: {msg}")
                if "rate limit exceeded" in msg.lower() and stop_on_rate_limit:
                    break

        final_rate = self.client.get_rate_limit()

        return {
            "run_id": actual_run_id,
            "status": "COMPLETED" if failures == 0 else "PARTIAL_COMPLETION",
            "total_targets": len(targets),
            "processed_count": successes + failures,
            "success_count": successes,
            "failure_count": failures,
            "initial_rate_limit_remaining": rate_info.remaining,
            "final_rate_limit_remaining": final_rate.remaining,
            "errors": errors
        }

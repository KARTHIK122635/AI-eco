"""
core/github_deltas.py
=====================
Calculates daily, weekly, and cumulative growth deltas for GitHub repositories
tracked in the AI Ecosystem Intelligence Pipeline.

Rules & Invariants:
- Never interprets a missing snapshot as zero.
- Preserves historical snapshot integrity.
- Calculates actual elapsed time from UTC timestamps.
- Preserves raw observed deltas alongside time-normalized growth rates.
- Never labels an arbitrary short-term raw delta (e.g. 34 hours) as weekly growth.
- Enforces minimum observation and interval requirements:
  * Minimum 5.0 days elapsed interval required for weekly velocity.
  * Observations spanning < 5.0 days are explicitly marked INSUFFICIENT_DATA and excluded from weekly rankings.
- Enforces PRAGMA foreign_keys = ON on all database connections.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta

DEFAULT_DB_PATH = "data/working/phase5_github_candidate.db"

MIN_WEEKLY_INTERVAL_DAYS = 5.0
MIN_WEEKLY_OBSERVATIONS = 2


def parse_utc_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
    """Parses an ISO-8601 UTC timestamp string safely."""
    if not ts_str:
        return None
    try:
        clean_str = ts_str.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


class GitHubDeltaCalculator:
    """Calculates granular deltas and growth velocities from historical snapshots."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        if fk_status != 1:
            raise RuntimeError(f"Failed to enable PRAGMA foreign_keys on {self.db_path}")
        return conn

    def get_repository_snapshots(self, repo_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all historical snapshots for a given repo_id in ascending chronological order.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count,
                   open_issues_count, change_stars_delta, change_forks_delta,
                   change_open_issues_delta, retrieval_status, provenance, source_api, collection_run_id
            FROM github_metrics_history
            WHERE repo_id = ?
            ORDER BY snapshot_timestamp ASC, snapshot_id ASC;
        """, (repo_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def calculate_repo_growth(self, repo_id: str) -> Dict[str, Any]:
        """
        Calculates daily, 7-day, and all-time growth metrics for a repository.
        Does not interpret missing days as zero; calculates rate over available span.
        Enforces statistical reliability thresholding.
        """
        snapshots = self.get_repository_snapshots(repo_id)
        if not snapshots:
            return {
                "repo_id": repo_id,
                "snapshot_count": 0,
                "latest_stars": 0,
                "latest_forks": 0,
                "latest_open_issues": 0,
                "raw_observed_stars_delta": 0,
                "raw_observed_forks_delta": 0,
                "raw_observed_issues_delta": 0,
                "consecutive_elapsed_hours": 0.0,
                "normalized_daily_stars_rate": 0.0,
                "weekly_stars_delta": None,
                "normalized_weekly_stars_rate": None,
                "all_time_stars_growth": 0,
                "all_time_forks_growth": 0,
                "all_time_issues_growth": 0,
                "total_span_days": 0.0,
                "has_growth_data": False,
                "weekly_growth_status": "NO_HISTORICAL_DATA",
                "is_weekly_growth_reliable": False,
                "insufficient_reason": "No snapshots recorded in metrics history."
            }

        latest = snapshots[-1]
        earliest = snapshots[0]

        latest_dt = parse_utc_timestamp(latest["snapshot_timestamp"])
        earliest_dt = parse_utc_timestamp(earliest["snapshot_timestamp"])

        total_span_seconds = (latest_dt - earliest_dt).total_seconds() if (latest_dt and earliest_dt) else 0.0
        total_span_days = max(0.0, total_span_seconds / 86400.0)

        # 1. Consecutive snapshot analysis (latest vs immediately preceding)
        if len(snapshots) >= 2:
            prev = snapshots[-2]
            prev_dt = parse_utc_timestamp(prev["snapshot_timestamp"])

            raw_stars_delta = latest["stars_count"] - prev["stars_count"]
            raw_forks_delta = latest["forks_count"] - prev["forks_count"]
            raw_issues_delta = (latest.get("open_issues_count") or 0) - (prev.get("open_issues_count") or 0)

            consecutive_seconds = (latest_dt - prev_dt).total_seconds() if (latest_dt and prev_dt) else 0.0
            consecutive_hours = max(0.0, consecutive_seconds / 3600.0)
            consecutive_days = max(0.0, consecutive_seconds / 86400.0)

            # Normalized daily velocity (stars/day over consecutive interval)
            if consecutive_days > 0.0001:
                normalized_daily_stars_rate = round(raw_stars_delta / consecutive_days, 4)
            else:
                # Duplicate timestamp or zero-interval
                normalized_daily_stars_rate = 0.0
        else:
            raw_stars_delta = latest.get("change_stars_delta", 0)
            raw_forks_delta = latest.get("change_forks_delta", 0)
            raw_issues_delta = latest.get("change_open_issues_delta", 0)
            consecutive_hours = 0.0
            consecutive_days = 0.0
            normalized_daily_stars_rate = 0.0

        # 2. Weekly velocity calculation with reliability thresholding
        if len(snapshots) < MIN_WEEKLY_OBSERVATIONS:
            weekly_growth_status = "INSUFFICIENT_DATA"
            weekly_stars_delta = None
            normalized_weekly_stars_rate = None
            is_weekly_reliable = False
            insufficient_reason = f"Fewer than {MIN_WEEKLY_OBSERVATIONS} snapshots available."
        elif total_span_days < MIN_WEEKLY_INTERVAL_DAYS:
            # Observation window is too short to compute a reliable weekly velocity
            weekly_growth_status = "INSUFFICIENT_DATA"
            weekly_stars_delta = None
            normalized_weekly_stars_rate = None
            is_weekly_reliable = False
            insufficient_reason = (
                f"Observation span ({total_span_days:.2f} days / {total_span_days * 24:.1f} hours) "
                f"is below required {MIN_WEEKLY_INTERVAL_DAYS} days for weekly rate."
            )
        else:
            # Span is sufficient (>= 5.0 days): find baseline snapshot closest to 7 days ago
            cutoff_7d = latest_dt - timedelta(days=7)
            # Find candidate closest to cutoff_7d
            best_candidate = earliest
            best_diff = abs((parse_utc_timestamp(earliest["snapshot_timestamp"]) - cutoff_7d).total_seconds())

            for s in snapshots:
                s_dt = parse_utc_timestamp(s["snapshot_timestamp"])
                if s_dt:
                    diff = abs((s_dt - cutoff_7d).total_seconds())
                    if diff < best_diff:
                        best_diff = diff
                        best_candidate = s

            base_dt = parse_utc_timestamp(best_candidate["snapshot_timestamp"])
            span_7d_seconds = (latest_dt - base_dt).total_seconds() if (latest_dt and base_dt) else 0.0
            span_7d_days = span_7d_seconds / 86400.0

            raw_7d_delta = latest["stars_count"] - best_candidate["stars_count"]

            if span_7d_days >= 1.0:
                normalized_weekly_stars_rate = round((raw_7d_delta / span_7d_days) * 7.0, 2)
                weekly_stars_delta = round(normalized_weekly_stars_rate)
                weekly_growth_status = "VERIFIED_RATE"
                is_weekly_reliable = True
                insufficient_reason = None
            else:
                weekly_growth_status = "INSUFFICIENT_DATA"
                weekly_stars_delta = None
                normalized_weekly_stars_rate = None
                is_weekly_reliable = False
                insufficient_reason = "Computed weekly baseline interval too small."

        # 3. All-time growth (earliest to latest)
        all_time_stars_growth = latest["stars_count"] - earliest["stars_count"]
        all_time_forks_growth = latest["forks_count"] - earliest["forks_count"]
        all_time_issues_growth = (latest.get("open_issues_count") or 0) - (earliest.get("open_issues_count") or 0)

        return {
            "repo_id": repo_id,
            "snapshot_count": len(snapshots),
            "latest_stars": latest["stars_count"],
            "latest_forks": latest["forks_count"],
            "latest_open_issues": latest.get("open_issues_count", 0),
            "raw_observed_stars_delta": raw_stars_delta,
            "raw_observed_forks_delta": raw_forks_delta,
            "raw_observed_issues_delta": raw_issues_delta,
            "daily_stars_delta": raw_stars_delta,  # Backwards compatibility key
            "daily_forks_delta": raw_forks_delta,
            "daily_issues_delta": raw_issues_delta,
            "consecutive_elapsed_hours": round(consecutive_hours, 2),
            "consecutive_elapsed_days": round(consecutive_days, 4),
            "normalized_daily_stars_rate": normalized_daily_stars_rate,
            "weekly_stars_delta": weekly_stars_delta,
            "normalized_weekly_stars_rate": normalized_weekly_stars_rate,
            "all_time_stars_growth": all_time_stars_growth,
            "all_time_forks_growth": all_time_forks_growth,
            "all_time_issues_growth": all_time_issues_growth,
            "first_snapshot_at": earliest["snapshot_timestamp"],
            "latest_snapshot_at": latest["snapshot_timestamp"],
            "total_span_days": round(total_span_days, 4),
            "has_growth_data": len(snapshots) >= 2,
            "weekly_growth_status": weekly_growth_status,
            "is_weekly_growth_reliable": is_weekly_reliable,
            "insufficient_reason": insufficient_reason
        }

    def compute_all_growth_summaries(self) -> List[Dict[str, Any]]:
        """Computes growth summaries for all repositories in the registry."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT repo_id FROM github_repositories ORDER BY latest_stars DESC;")
        repo_ids = [r["repo_id"] for r in cursor.fetchall()]
        conn.close()

        return [self.calculate_repo_growth(rid) for rid in repo_ids]

    calculate_growth_metrics = calculate_repo_growth

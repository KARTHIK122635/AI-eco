"""
scripts/run_github_collection.py
================================
Manual collection CLI command for Phase V GitHub Ecosystem Intelligence.

Controls & Safeguards:
- Displays proposed collection scope and repository counts.
- Shows authentication configuration status without exposing credentials.
- Checks GitHub API rate limit quota prior to execution.
- Requires explicit user confirmation before writing.
- Writes exclusively to data/working/phase5_github_candidate.db.
- Records execution run in collection_logs.
- Enforces safety rate-limit stopping buffer.
- Never performs automatic or background scheduling.
- Never writes to Google Sheets or protected databases.
"""

import os
import sys
import argparse
import sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.github_client import GitHubClient
from core.github_discovery import GitHubDiscoveryEngine
from core.github_metrics import GitHubMetricsCollector
from core.github_deltas import GitHubDeltaCalculator
from core.github_analytics import GitHubAnalytics
from core.github_migrations import compute_sha256

PROTECTED_DB_PATHS = [
    "data/normalized/ai_ecosystem.db",
    "source/audit19_original_database.db",
    "data/working/rolling_ai_ecosystem.db",
    "data/working/candidate_rolling_ai_ecosystem.db"
]

PHASE5_DEFAULT_DB = "data/working/phase5_github_candidate.db"


def log_manual_collection_run(
    db_path: str,
    run_id: str,
    start_time: str,
    end_time: str,
    updated_metrics_count: int,
    failed_requests_count: int,
    status: str,
    error_log: Optional[str] = None
) -> None:
    """Records the manual Phase V execution run in collection_logs table."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    assert fk_status == 1, "Foreign key enforcement failed to activate!"
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO collection_logs (
            run_id, scheduled_time, start_time, end_time, execution_type,
            rolling_window_start, rolling_window_end, updated_metrics_count,
            failed_requests_count, status, error_log
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        run_id, start_time, start_time, end_time, "MANUAL_GITHUB_PHASE5",
        start_time[:10], end_time[:10], updated_metrics_count,
        failed_requests_count, status, error_log
    ))
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Phase V Manual GitHub Ecosystem Intelligence Collection CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--db-path",
        default=PHASE5_DEFAULT_DB,
        help=f"Target SQLite database path (default: {PHASE5_DEFAULT_DB})"
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=None,
        help="Maximum number of repositories to collect in this run"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run discovery engine to find and register new candidate repositories prior to metrics collection"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect scope and rate limits without making API write calls"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Confirm execution without interactive prompt"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        help="Specific repo IDs to inspect (e.g. owner/repo)"
    )

    args = parser.parse_args()

    # Safety boundary check: Never write to protected databases
    target_norm = os.path.normpath(args.db_path)
    for p in PROTECTED_DB_PATHS:
        if os.path.normpath(p) == target_norm:
            print(f"\n[CRITICAL ERROR] Target path '{args.db_path}' is a PROTECTED database!")
            print("Phase V collection can ONLY write to data/working/phase5_github_candidate.db.")
            sys.exit(1)

    if not os.path.exists(target_norm):
        print(f"\n[ERROR] Target database '{args.db_path}' does not exist.")
        print("Please run core/github_migrations.py first to initialize phase5_github_candidate.db.")
        sys.exit(1)

    print("=" * 78)
    print("   AI ECOSYSTEM INTELLIGENCE PIPELINE — PHASE V GITHUB COLLECTION")
    print("=" * 78)

    # 1. Inspect Client and Authentication Status
    client = GitHubClient()
    is_auth = client.is_authenticated()
    auth_display = "CONFIGURED (Personal Access Token active)" if is_auth else "UNAUTHENTICATED (Public Rate Limits apply)"

    rate_info = client.get_rate_limit()
    print(f"\n[1] GitHub API Status:")
    print(f"    - Authentication:     {auth_display}")
    print(f"    - API Quota Limit:    {rate_info.limit:,} req/hr")
    print(f"    - Remaining Quota:    {rate_info.remaining:,} requests")
    print(f"    - Quota Reset Time:   {rate_info.reset_datetime_utc}")

    if rate_info.remaining <= 5:
        print("\n[ABORT] Rate limit remaining is at or below safety buffer (<= 5).")
        print(f"Please wait until quota resets at {rate_info.reset_datetime_utc}.")
        sys.exit(1)

    # 2. Inspect Target Database Scope
    conn = sqlite3.connect(target_norm)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM github_repositories;")
    total_db_repos = cursor.fetchone()[0]

    if args.repos:
        target_repo_ids = args.repos
        print(f"\n[2] Target Repositories: Specific list ({len(target_repo_ids)} repos specified)")
    else:
        cursor.execute("SELECT repo_id FROM github_repositories ORDER BY repo_id;")
        all_ids = [r[0] for r in cursor.fetchall()]
        if args.max_repos:
            target_repo_ids = all_ids[:args.max_repos]
            print(f"\n[2] Target Repositories: Batch of {len(target_repo_ids)} repos (capped by --max-repos={args.max_repos} out of {total_db_repos} total)")
        else:
            target_repo_ids = all_ids
            print(f"\n[2] Target Repositories: ALL {total_db_repos} repositories in registry")

    conn.close()

    print(f"    - Target Database:    {target_norm}")
    print(f"    - Discovery Step:     {'ENABLED' if args.discover else 'DISABLED'}")
    print(f"    - Execution Mode:     {'DRY RUN (No writes)' if args.dry_run else 'LIVE COLLECTION'}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE] Scope verified. Exiting without modifications.")
        sys.exit(0)

    # 3. Require Explicit Confirmation
    if not args.yes:
        print("\n" + "-" * 78)
        confirm = input("Confirm collection run against phase5_github_candidate.db? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("[CANCELLED] Execution aborted by user.")
            sys.exit(0)

    # 4. Execute Discovery (if requested)
    run_id = f"run_gh_manual_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    start_time = datetime.now(timezone.utc).isoformat()
    print(f"\n[3] Initiating Run {run_id}...")

    if args.discover:
        print("\n--> Running Discovery Engine across papers, products, and startups...")
        discovery_engine = GitHubDiscoveryEngine(db_path=target_norm)
        disc_results = discovery_engine.run_discovery(persist=True)
        print(f"    - Associations Discovered:  {disc_results['total_discovered_associations']}")
        print(f"    - New Repos Registered:     {disc_results['newly_registered_repos']}")

    # 5. Execute Metrics Collection
    print(f"\n--> Collecting metrics for {len(target_repo_ids)} repositories...")
    collector = GitHubMetricsCollector(db_path=target_norm, client=client)
    batch_res = collector.collect_batch_metrics(
        repo_ids=target_repo_ids,
        run_id=run_id,
        stop_on_rate_limit=True
    )

    end_time = datetime.now(timezone.utc).isoformat()

    # 6. Record Collection Log
    error_summary = "; ".join(batch_res["errors"]) if batch_res["errors"] else None
    log_manual_collection_run(
        db_path=target_norm,
        run_id=run_id,
        start_time=start_time,
        end_time=end_time,
        updated_metrics_count=batch_res["success_count"],
        failed_requests_count=batch_res["failure_count"],
        status=batch_res["status"],
        error_log=error_summary
    )

    # 7. Run SQLite Integrity Check
    conn = sqlite3.connect(target_norm)
    conn.execute("PRAGMA foreign_keys = ON;")
    integ = conn.cursor().execute("PRAGMA integrity_check;").fetchall()
    conn.close()
    integ_status = integ[0][0] if integ and len(integ) == 1 else "FAILED"

    # 8. Display Summary
    print("\n" + "=" * 78)
    print("   COLLECTION RUN COMPLETE — SUMMARY REPORT")
    print("=" * 78)
    print(f"Run ID:                      {run_id}")
    print(f"Status:                      {batch_res['status']}")
    print(f"Repositories Processed:      {batch_res['processed_count']}/{batch_res['total_targets']}")
    print(f"Successful Snapshots:        {batch_res['success_count']}")
    print(f"Failed / Rate Limited:       {batch_res['failure_count']}")
    print(f"Initial Rate Limit:          {batch_res['initial_rate_limit_remaining']}")
    print(f"Final Rate Limit:            {batch_res['final_rate_limit_remaining']}")
    print(f"Database Integrity:          {integ_status}")

    if batch_res["errors"]:
        print("\nErrors / Warnings:")
        for err in batch_res["errors"][:5]:
            print(f"  - {err}")
        if len(batch_res["errors"]) > 5:
            print(f"  ... and {len(batch_res['errors']) - 5} more.")

    print("\nTarget DB SHA-256:", compute_sha256(target_norm))
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()

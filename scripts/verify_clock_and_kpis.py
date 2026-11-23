"""
Audit script for Clock, Timezone, and Content Eligibility Semantics.
Uses verified fixed UTC reference timestamp: 2026-11-23 04:30:00 UTC (10:00:00 IST).
Distinguishes content eligibility (3,302) from repository/telemetry counts.
"""

import sqlite3
import os
import sys
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rolling_window import (
    compute_rolling_window,
    parse_publication_timestamp,
    classify_freshness,
)

CANDIDATE_DB = "data/working/candidate_rolling_ai_ecosystem.db"

# Fixed UTC Reference: 2026-11-23 04:30:00 UTC (equivalent to 10:00:00 IST)
AUDIT_REF_UTC = datetime(2026, 11, 23, 4, 30, 0, tzinfo=timezone.utc)

def run_clock_and_kpi_audit():
    print("=" * 85)
    print("PHASE IV — SYSTEM CLOCK, TIMEZONE & KPI SEMANTICS AUDIT")
    print("=" * 85)

    # 1. System Clock Verification
    local_now = datetime.now()
    local_aware = local_now.astimezone()
    utc_now = datetime.now(timezone.utc)
    ist_tz = timezone(timedelta(hours=5, minutes=30), name="IST")
    ist_now = utc_now.astimezone(ist_tz)

    print("System Clock Observations:")
    print(f"  Machine Local Time (naive) : {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Machine Local Aware        : {local_aware.isoformat()}")
    print(f"  Machine UTC Time (live)    : {utc_now.isoformat()}")
    print(f"  India Standard Time (IST)  : {ist_now.isoformat()}")
    print(f"\nAudit Fixed UTC Reference    : {AUDIT_REF_UTC.isoformat()}")
    print(f"Audit IST Reference          : {AUDIT_REF_UTC.astimezone(ist_tz).isoformat()}")

    # 2. Window Calculations
    window_start, window_end = compute_rolling_window(AUDIT_REF_UTC, months=6)
    fresh_24h_boundary = AUDIT_REF_UTC - timedelta(hours=24)

    print("\nWindow Boundaries:")
    print(f"  6-Calendar-Month Window    : [{window_start.isoformat()} -> {window_end.isoformat()}]")
    print(f"  Exact Calendar Month Span  : {(window_end - window_start).total_seconds() / 86400.0} days (184.0 days, not 180)")
    print(f"  24-Hour Freshness Cutoff   : >= {fresh_24h_boundary.isoformat()}")

    # 3. Query Candidate Database for Applicable Content Entities
    conn = sqlite3.connect(f"file:{CANDIDATE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    content_tables = [
        ("ai_research_papers", "Research Papers", ["publication_date"], "date_type"),
        ("ai_news", "AI News", ["published_at"], "date_type"),
        ("ai_jobs", "AI Jobs", ["posted_at"], "date_type"),
        ("ai_startups", "Startups", ["founding_date", "announcement_date", "published_at"], "date_type"),
        ("ai_products", "Products", ["release_date", "launch_date", "published_at"], "date_type"),
    ]

    print("\n" + "=" * 85)
    print("CONTENT ELIGIBILITY KPI AUDIT (DATED CONTENT ENTITIES ONLY)")
    print("=" * 85)
    print(f"{'Content Entity':<20} | {'Total':<6} | {'Eligible (<=6M)':<15} | {'Outside (>6M)':<13} | {'Missing/Unver':<14} | {'Fresh (<=24H)':<12}")
    print("-" * 85)

    content_total = 0
    content_eligible = 0
    content_outside = 0
    content_missing = 0
    content_fresh_24h = 0

    table_results = {}

    for tbl, label, date_cols, date_type_col in content_tables:
        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()
        tot = len(rows)
        content_total += tot

        eligible = 0
        outside = 0
        missing = 0
        fresh = 0

        for r in rows:
            r_dict = dict(r)
            date_type = r_dict.get(date_type_col)

            raw_val = None
            for col in date_cols:
                v = r_dict.get(col)
                if v and str(v).strip():
                    raw_val = v
                    break

            if not raw_val:
                missing += 1
                continue

            dt = parse_publication_timestamp(raw_val)
            if not dt:
                missing += 1
                continue

            c_res = classify_freshness(dt, ref_time=AUDIT_REF_UTC, window_start=window_start, date_type=date_type)
            if c_res["in_rolling_window"]:
                eligible += 1
            elif c_res["status"] == "OUTSIDE_WINDOW":
                outside += 1
            else:
                missing += 1

            if c_res["is_fresh_24h"]:
                fresh += 1

        content_eligible += eligible
        content_outside += outside
        content_missing += missing
        content_fresh_24h += fresh

        table_results[tbl] = {
            "total": tot,
            "eligible": eligible,
            "outside": outside,
            "missing": missing,
            "fresh": fresh
        }

        print(f"{label:<20} | {tot:>6} | {eligible:>15} | {outside:>13} | {missing:>14} | {fresh:>12}")

    print("-" * 85)
    print(f"{'CONTENT KPI TOTALS':<20} | {content_total:>6} | {content_eligible:>15} | {content_outside:>13} | {content_missing:>14} | {content_fresh_24h:>12}")
    print("=" * 85)

    # 4. Separate Repository and Operational Telemetry Metrics
    print("\n" + "=" * 85)
    print("SEPARATE REPOSITORY & OPERATIONAL TELEMETRY METRICS")
    print("=" * 85)
    cursor.execute("SELECT COUNT(*) FROM github_repositories")
    repo_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM github_repositories WHERE status='ACTIVE'")
    active_repo_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM github_metrics_history")
    snapshot_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM collection_logs")
    log_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM collection_logs WHERE status='COMPLETED'")
    completed_log_count = cursor.fetchone()[0]

    print(f"  - Tracked GitHub Repositories   : {repo_count} total ({active_repo_count} active)")
    print(f"  - GitHub Metric Snapshots       : {snapshot_count} snapshots recorded")
    print(f"  - Collection & Recovery Runs    : {log_count} pipeline runs ({completed_log_count} completed)")
    print("  * Confirmed: Zero repository or telemetry records counted toward Content Eligibility.")

    conn.close()

    # 5. Assert Expected Numbers
    assert table_results["ai_research_papers"]["eligible"] == 1060, f"Expected 1060 papers, got {table_results['ai_research_papers']['eligible']}"
    assert table_results["ai_news"]["eligible"] == 311, f"Expected 311 news, got {table_results['ai_news']['eligible']}"
    assert table_results["ai_jobs"]["eligible"] == 1931, f"Expected 1931 jobs, got {table_results['ai_jobs']['eligible']}"
    assert content_eligible == 3302, f"Expected 3302 total content eligible, got {content_eligible}"
    print(f"\n[VERIFIED] Exact Content Eligibility Parity: 1,060 + 311 + 1,931 = 3,302 records.")
    return True

if __name__ == "__main__":
    run_clock_and_kpi_audit()

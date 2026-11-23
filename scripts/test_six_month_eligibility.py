"""
Comprehensive Six-Month Eligibility and Freshness Audit Script.
Validates calendar month calculation, timezone awareness, null/malformed dates,
boundary cases, future timestamps, and candidate database breakdown by entity.
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rolling_window import (
    compute_rolling_window,
    parse_publication_timestamp,
    classify_freshness,
)

CANDIDATE_DB = "data/working/candidate_rolling_ai_ecosystem.db"

def run_unit_validations():
    print("=" * 80)
    print("1. UNIT VALIDATIONS OF ROLLING WINDOW & FRESHNESS LOGIC")
    print("=" * 80)

    # A. 6 Calendar Months vs 180 Days
    ref = datetime(2026, 11, 23, 12, 0, 0, tzinfo=timezone.utc)
    start_6m, end_6m = compute_rolling_window(ref, months=6)
    expected_start = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
    diff_days = (end_6m - start_6m).total_seconds() / 86400.0

    print(f"Reference Time       : {ref.isoformat()}")
    print(f"6-Calendar-Month Start: {start_6m.isoformat()}")
    print(f"Calendar Month Match : {start_6m == expected_start} (Diff: {diff_days:.1f} days, not 180.0 days)")
    assert start_6m == expected_start, "Did not compute exact calendar months!"
    assert diff_days == 184.0, f"Expected 184 days for May-Nov, got {diff_days}"

    # B. Timezone-Aware Handling
    naive_dt = datetime(2026, 11, 20, 10, 0, 0)
    parsed_naive = parse_publication_timestamp(naive_dt)
    print(f"Naive Datetime Parse  : tz={parsed_naive.tzinfo} (UTC converted)")
    assert parsed_naive.tzinfo == timezone.utc

    offset_str = "2026-11-20T15:00:00+05:00"
    parsed_offset = parse_publication_timestamp(offset_str)
    expected_utc = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    print(f"Offset Datetime Parse : {parsed_offset.isoformat()} == {expected_utc.isoformat()} : {parsed_offset == expected_utc}")
    assert parsed_offset == expected_utc

    # C. Null, Empty, and Malformed Strings
    for malformed in [None, "", "   ", "Summer 2023", "Batch W24", "invalid-date-string"]:
        parsed = parse_publication_timestamp(malformed)
        c_res = classify_freshness(parsed, ref_time=ref, window_start=start_6m)
        print(f"Malformed: '{malformed}' -> parsed={parsed}, eligible={c_res['in_rolling_window']}, status={c_res['status']}")
        assert parsed is None
        assert c_res["in_rolling_window"] is False
        assert c_res["is_fresh_24h"] is False

    # D. Exact Boundaries
    exact_start = start_6m
    just_before_start = start_6m - timedelta(seconds=1)
    res_at_boundary = classify_freshness(exact_start, ref_time=ref, window_start=start_6m)
    res_before_boundary = classify_freshness(just_before_start, ref_time=ref, window_start=start_6m)

    print(f"At Boundary (exact start)      : eligible={res_at_boundary['in_rolling_window']} ({res_at_boundary['status']})")
    print(f"Before Boundary (start - 1sec) : eligible={res_before_boundary['in_rolling_window']} ({res_before_boundary['status']})")
    assert res_at_boundary["in_rolling_window"] is True
    assert res_before_boundary["in_rolling_window"] is False
    assert res_before_boundary["status"] == "OUTSIDE_WINDOW"

    # E. Future Timestamps
    future_dt = ref + timedelta(hours=2)
    res_future = classify_freshness(future_dt, ref_time=ref, window_start=start_6m)
    print(f"Future Timestamp (+2h)         : eligible={res_future['in_rolling_window']} ({res_future['status']})")
    assert res_future["in_rolling_window"] is False
    assert res_future["status"] == "FUTURE_TIMESTAMP_ANOMALY"

    # F. 24-Hour Freshness Separation
    fresh_dt = ref - timedelta(hours=12)
    res_fresh = classify_freshness(fresh_dt, ref_time=ref, window_start=start_6m)
    print(f"Fresh Timestamp (-12h)         : eligible={res_fresh['in_rolling_window']}, fresh_24h={res_fresh['is_fresh_24h']} ({res_fresh['status']})")
    assert res_fresh["in_rolling_window"] is True
    assert res_fresh["is_fresh_24h"] is True

    recent_dt = ref - timedelta(days=3)
    res_recent = classify_freshness(recent_dt, ref_time=ref, window_start=start_6m)
    print(f"Recent Timestamp (-3d)         : eligible={res_recent['in_rolling_window']}, fresh_24h={res_recent['is_fresh_24h']} ({res_recent['status']})")
    assert res_recent["in_rolling_window"] is True
    assert res_recent["is_fresh_24h"] is False

    print("\nALL UNIT VALIDATIONS PASSED SUCCESSFULLY.\n")


def audit_candidate_database_eligibility():
    print("=" * 80)
    print("2. CANDIDATE DATABASE ELIGIBILITY & FRESHNESS AUDIT")
    print("=" * 80)

    # Use execution time baseline (Nov 23, 2026)
    ref_time = datetime(2026, 11, 23, 9, 30, 0, tzinfo=timezone.utc)
    window_start, window_end = compute_rolling_window(ref_time, months=6)
    print(f"Reference Time       : {ref_time.isoformat()}")
    print(f"6M Window Start Bound: {window_start.isoformat()}")
    print(f"6M Window End Bound  : {window_end.isoformat()}\n")

    conn = sqlite3.connect(f"file:{CANDIDATE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    configs = [
        ("ai_startups", "Startups", ["founding_date", "announcement_date", "published_at"], "date_type"),
        ("ai_products", "Products", ["release_date", "launch_date", "published_at"], "date_type"),
        ("ai_research_papers", "Research_Papers", ["publication_date"], "date_type"),
        ("ai_news", "AI_News", ["published_at"], "date_type"),
        ("ai_jobs", "AI_Jobs", ["posted_at"], "date_type"),
        ("github_repositories", "GitHub_Repositories", ["last_checked_at"], None),
        ("github_metrics_history", "GitHub_Metrics", ["snapshot_timestamp"], None),
        ("collection_logs", "Collection_Logs", ["start_time"], None),
    ]

    print(f"{'Table Name':<24} | {'Total':<6} | {'Eligible 6M':<12} | {'Outside 6M':<11} | {'Missing/Unver':<14} | {'Fresh 24H':<10}")
    print("-" * 88)

    grand_total = 0
    grand_eligible = 0
    grand_outside = 0
    grand_missing = 0
    grand_fresh = 0

    for tbl, sheet, date_cols, date_type_col in configs:
        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()
        tot = len(rows)
        grand_total += tot

        eligible = 0
        outside = 0
        missing = 0
        fresh = 0

        for r in rows:
            r_dict = dict(r)
            date_type = r_dict.get(date_type_col) if date_type_col else None

            # Pick first non-empty date field
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

            c_res = classify_freshness(dt, ref_time=ref_time, window_start=window_start, date_type=date_type)
            if c_res["in_rolling_window"]:
                eligible += 1
            elif c_res["status"] == "OUTSIDE_WINDOW":
                outside += 1
            else:
                missing += 1

            if c_res["is_fresh_24h"]:
                fresh += 1

        grand_eligible += eligible
        grand_outside += outside
        grand_missing += missing
        grand_fresh += fresh

        print(f"{tbl:<24} | {tot:>6} | {eligible:>12} | {outside:>11} | {missing:>14} | {fresh:>10}")

    print("-" * 88)
    print(f"{'TOTALS':<24} | {grand_total:>6} | {grand_eligible:>12} | {grand_outside:>11} | {grand_missing:>14} | {grand_fresh:>10}")
    print("=" * 88)
    conn.close()

if __name__ == "__main__":
    run_unit_validations()
    audit_candidate_database_eligibility()

"""
scripts/compute_phase6_dashboard_metrics.py
===========================================
Calculates all Phase VI dashboard metrics directly from data/working/phase5_github_candidate.db
in strict read-only mode using parameterized queries and core.github_analytics.
"""

import os
import sys
import json
import sqlite3

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.github_analytics import GitHubAnalytics, RepositoryLifecycleClassifier, LifecycleState
from core.github_deltas import GitHubDeltaCalculator, MIN_WEEKLY_INTERVAL_DAYS

DB_PATH = "data/working/phase5_github_candidate.db"

def main():
    analytics = GitHubAnalytics(db_path=DB_PATH)
    deltas = GitHubDeltaCalculator(db_path=DB_PATH)

    uri = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    print("=" * 80)
    print("PHASE VI METRICS DIRECT RECALCULATION")
    print("=" * 80)

    # 1. Repository Overview
    dist = analytics.get_lifecycle_distribution()
    print("\n[1] REPOSITORY OVERVIEW:")
    print(f"  - Total Unique Repositories:      {dist['total_repositories']}")
    print(f"  - Verified Active Repositories:    {dist['active_verified_count']} ({dist['active_verified_percentage']}%)")
    print(f"  - Verified Archived Repositories:  {dist['archived_verified_count']}")
    print(f"  - Not Yet Checked Repositories:    {dist['not_yet_checked_count']} ({dist['not_yet_checked_percentage']}%)")
    print(f"  - Not Found Repositories (404):    {dist['not_found_count']}")
    print(f"  - Access Denied Repositories (403):{dist['access_denied_count']}")
    print(f"  - API Unavailable Repositories:    {dist['api_unavailable_count']}")
    print(f"  - Network Error Repositories:      {dist['network_error_count']}")
    print(f"  - Unknown Repositories:            {dist['unknown_count']}")

    # 2. Repository Performance
    cursor.execute("""
        SELECT SUM(latest_stars), SUM(latest_forks), SUM(latest_open_issues),
               COUNT(CASE WHEN latest_open_issues IS NOT NULL AND latest_open_issues > 0 THEN 1 END),
               COUNT(CASE WHEN primary_language IS NOT NULL AND primary_language != '' THEN 1 END)
        FROM github_repositories;
    """)
    sum_stars, sum_forks, sum_issues, repos_with_issues, repos_with_lang = cursor.fetchone()
    print("\n[2] REPOSITORY PERFORMANCE:")
    print(f"  - Total Stars across ecosystem:   {sum_stars:,}")
    print(f"  - Total Forks across ecosystem:   {sum_forks:,}")
    print(f"  - Total Open Issues tracked:      {sum_issues:,}")
    print(f"  - Repositories with language set: {repos_with_lang} / {dist['total_repositories']}")

    top_repos = analytics.get_top_repositories_by_stars(limit=5)
    print("\n  Top 5 Repositories by Stars:")
    for idx, r in enumerate(top_repos):
        print(f"    {idx+1}. {r['repo_id']:<35} | {r['latest_stars']:>6,} stars | {r['latest_forks']:>5,} forks | Lang: {r['primary_language'] or 'N/A'}")

    lang_dist = analytics.get_language_distribution(limit=10)
    print("\n  Primary Language Distribution (Top 5):")
    for l in lang_dist[:5]:
        print(f"    - {l['language']:<25}: {l['repo_count']:>3} repos ({l['percentage']:>5.2f}%) | {l['total_stars']:>7,} stars")

    owner_dist = analytics.get_organization_distribution(limit=10)
    print("\n  Top Organizations (Top 5):")
    for o in owner_dist[:5]:
        print(f"    - {o['owner']:<25}: {o['repo_count']:>3} repos | {o['total_stars']:>7,} stars | {o['total_forks']:>5,} forks")

    # 3. Historical Performance & Growth
    summaries = deltas.compute_all_growth_summaries()
    reliable_weekly = [s for s in summaries if s.get("is_weekly_growth_reliable")]
    short_term = [s for s in summaries if s.get("weekly_growth_status") == "INSUFFICIENT_DATA" and s.get("has_growth_data")]
    total_obs_deltas = sum(s.get("raw_observed_stars_delta", 0) for s in summaries)
    total_fork_deltas = sum(s.get("raw_observed_forks_delta", 0) for s in summaries)

    print("\n[3] HISTORICAL PERFORMANCE & GROWTH:")
    print(f"  - Verified Weekly Growth Repositories: {len(reliable_weekly)} (Requires >= {MIN_WEEKLY_INTERVAL_DAYS} days span)")
    print(f"  - Short-Term Observed Repositories:    {len(short_term)} (Span < {MIN_WEEKLY_INTERVAL_DAYS} days)")
    print(f"  - Total Cumulative Stars Delta:        +{total_obs_deltas:,} stars observed across snapshot transitions")
    print(f"  - Total Cumulative Forks Delta:        +{total_fork_deltas:,} forks observed across snapshot transitions")
    
    short_term_obs = analytics.get_short_term_velocity_observations(limit=5)
    print("\n  Top Short-Term Velocity Observations:")
    for idx, r in enumerate(short_term_obs):
        print(f"    {idx+1}. {r['repo_id']:<30} | +{r['raw_observed_stars_delta']} stars in {r['consecutive_elapsed_hours']:.1f}h ({r['total_span_days']:.2f}d) | Rate: {r['normalized_daily_stars_rate']:.2f} stars/d | Status: {r['weekly_growth_status']}")

    # 4. Ecosystem Coverage
    cov = analytics.get_ecosystem_coverage()
    print("\n[4] ECOSYSTEM COVERAGE:")
    print(f"  - Research Papers Total:               {cov['research_papers']['total']}")
    print(f"  - Research Papers with Verified Code:  {cov['research_papers']['with_verified_code']} ({cov['research_papers']['coverage_pct']}%)")
    print(f"  - Commercial Products Total:           {cov['products']['total']}")
    print(f"  - Commercial Products with Code:       {cov['products']['with_verified_code']} ({cov['products']['coverage_pct']}%)")
    print(f"  - AI Startups Total:                   {cov['startups']['total']}")
    print(f"  - AI Startups with Code:               {cov['startups']['with_verified_code']} ({cov['startups']['coverage_pct']}%)")
    print(f"  - Total Association Records:           {cov['association_counts']['total_associations']}")
    print(f"  - Verified Associations:               {cov['association_counts']['verified']}")
    print(f"  - Manual Review Associations:          {cov['association_counts']['manual_review']} (msalman95/DA)")
    print(f"  - Unverified Associations:             {cov['association_counts']['unverified']} (msalman95/DAL)")

    # 5. Collection Monitoring
    cursor.execute("""
        SELECT run_id, scheduled_time, start_time, end_time, execution_type,
               updated_metrics_count, failed_requests_count, status, error_log
        FROM collection_logs
        WHERE execution_type = 'MANUAL_GITHUB_PHASE5'
        ORDER BY start_time DESC;
    """)
    gh_runs = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM collection_logs;")
    total_pipeline_runs = cursor.fetchone()[0]

    print("\n[5] COLLECTION MONITORING:")
    print(f"  - Total Pipeline Collection Runs:      {total_pipeline_runs}")
    print(f"  - Phase V GitHub Collection Runs:      {len(gh_runs)}")
    if gh_runs:
        latest_run = gh_runs[0]
        print(f"  - Latest GitHub Run ID:                {latest_run[0]}")
        print(f"  - Latest GitHub Run Start Time:        {latest_run[2]}")
        print(f"  - Latest GitHub Run End Time:          {latest_run[3]}")
        print(f"  - Latest Run Updated Metrics:          {latest_run[5]}")
        print(f"  - Latest Run Failed Requests:          {latest_run[6]}")
        print(f"  - Latest Run Status:                   {latest_run[7]}")
        print(f"  - Error Log:                           {latest_run[8] or 'None (Clean Run)'}")

    conn.close()

if __name__ == "__main__":
    main()

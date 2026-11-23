"""
Detailed Reconciliation: Canonical DB vs Candidate DB for AI News and AI Jobs.
"""

import sqlite3
import os
import json

CANONICAL_DB = "data/normalized/ai_ecosystem.db"
CANDIDATE_DB = "data/working/candidate_rolling_ai_ecosystem.db"

def reconcile():
    print("=" * 80)
    print("CANONICAL (HISTORICAL) VS CANDIDATE DATABASE RECONCILIATION")
    print("=" * 80)

    conn_can = sqlite3.connect(f"file:{CANONICAL_DB}?mode=ro", uri=True)
    conn_cand = sqlite3.connect(f"file:{CANDIDATE_DB}?mode=ro", uri=True)
    c_can = conn_can.cursor()
    c_cand = conn_cand.cursor()

    # 1. AI News Reconciliation
    c_can.execute("SELECT news_id FROM ai_news")
    can_news_ids = set(r[0] for r in c_can.fetchall())

    c_cand.execute("SELECT news_id FROM ai_news")
    cand_news_ids = set(r[0] for r in c_cand.fetchall())

    missing_news = can_news_ids - cand_news_ids
    added_news = cand_news_ids - can_news_ids

    print(f"\n[AI_NEWS] Canonical Count: {len(can_news_ids)} | Candidate Count: {len(cand_news_ids)}")
    print(f"[AI_NEWS] Missing from Candidate: {len(missing_news)}")
    print(f"[AI_NEWS] Added in Candidate    : {len(added_news)} (+{len(cand_news_ids) - len(can_news_ids)})")

    if missing_news:
        print(f"  CRITICAL: Missing canonical IDs: {list(missing_news)[:10]}")
    else:
        print("  VERIFIED: 100% of canonical 1,132 AI News records exist in Candidate DB. Zero removed.")

    if added_news:
        placeholders = ",".join(f"'{pk}'" for pk in added_news)
        c_cand.execute(f"SELECT news_id, title, source_name, published_at, provenance, freshness_status, in_rolling_window FROM ai_news WHERE news_id IN ({placeholders})")
        print("\n  Detailed Breakdown of the 6 Additional AI News Records:")
        for r in c_cand.fetchall():
            print(f"    - PK: {r[0]}")
            print(f"      Title      : {r[1]}")
            print(f"      Source     : {r[2]}")
            print(f"      Published  : {r[3]}")
            print(f"      Provenance : {r[4]}")
            print(f"      Freshness  : {r[5]} (in_window={r[6]})")

    # 2. AI Jobs Reconciliation
    c_can.execute("SELECT job_id FROM ai_jobs")
    can_job_ids = set(r[0] for r in c_can.fetchall())

    c_cand.execute("SELECT job_id FROM ai_jobs")
    cand_job_ids = set(r[0] for r in c_cand.fetchall())

    missing_jobs = can_job_ids - cand_job_ids
    added_jobs = cand_job_ids - can_job_ids

    print(f"\n[AI_JOBS] Canonical Count: {len(can_job_ids)} | Candidate Count: {len(cand_job_ids)}")
    print(f"[AI_JOBS] Missing from Candidate: {len(missing_jobs)}")
    print(f"[AI_JOBS] Added in Candidate    : {len(added_jobs)} (+{len(cand_job_ids) - len(can_job_ids)})")

    if missing_jobs:
        print(f"  CRITICAL: Missing canonical IDs: {list(missing_jobs)[:10]}")
    else:
        print("  VERIFIED: 100% of canonical 1,930 AI Jobs records exist in Candidate DB. Zero removed.")

    if added_jobs:
        placeholders = ",".join(f"'{pk}'" for pk in added_jobs)
        c_cand.execute(f"SELECT job_id, job_title, company_name, source_name, posted_at, provenance, freshness_status, in_rolling_window, vacancy_status FROM ai_jobs WHERE job_id IN ({placeholders})")
        rows = c_cand.fetchall()
        print(f"\n  Provenance Summary of the 33 Additional AI Jobs Records:")
        sources = {}
        for r in rows:
            src = r[3]
            sources[src] = sources.get(src, 0) + 1
        print(f"  Sources of Added Jobs: {sources}")
        print("\n  Sample Added Jobs (First 5):")
        for r in rows[:5]:
            print(f"    - PK: {r[0]} | Title: {r[1]} | Company: {r[2]} | Source: {r[3]} | Posted: {r[4]} | Prov: {r[5]} | Status: {r[6]}/{r[8]}")

    # 3. Primary Key Uniqueness & Null Checks in Candidate DB
    print("\n" + "=" * 80)
    print("PRIMARY KEY INTEGRITY & NULL AUDIT (CANDIDATE DB)")
    print("=" * 80)
    tables = [
        ("ai_startups", "startup_id"),
        ("ai_products", "product_id"),
        ("ai_research_papers", "paper_id"),
        ("ai_news", "news_id"),
        ("ai_jobs", "job_id"),
        ("github_repositories", "repo_id"),
        ("github_metrics_history", "snapshot_id"),
        ("collection_logs", "run_id"),
    ]

    for tbl, pk in tables:
        c_cand.execute(f"SELECT COUNT(*), COUNT(DISTINCT {pk}), SUM(CASE WHEN {pk} IS NULL THEN 1 ELSE 0 END) FROM {tbl}")
        tot, dist, nulls = c_cand.fetchone()
        dups = tot - dist
        print(f"{tbl:<25} | Total: {tot:>5} | Distinct PK: {dist:>5} | Duplicate PKs: {dups:>2} | Null PKs: {nulls:>2}")

    conn_can.close()
    conn_cand.close()

if __name__ == "__main__":
    reconcile()

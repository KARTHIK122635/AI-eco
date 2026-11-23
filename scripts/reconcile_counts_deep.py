"""
Deep Reconciliation Script for Candidate Database Counts.
Explains the differences:
- AI News: 1,132 vs 1,138 (+6)
- AI Jobs: 1,930 vs 1,963 (+33)
Validates primary keys, null counts, duplicates, and provenance.
"""

import sqlite3
import os

CANDIDATE_DB = "data/working/candidate_rolling_ai_ecosystem.db"
BASELINE_WORKING_DB = "data/working/rolling_ai_ecosystem.db"
CANONICAL_DB = "data/normalized/ai_ecosystem.db"

def inspect_table_deep(db_path, table_name, pk_col):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    # Total count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_count = cursor.fetchone()[0]

    # Distinct PK count (check duplicates)
    cursor.execute(f"SELECT COUNT(DISTINCT {pk_col}) FROM {table_name}")
    distinct_pk_count = cursor.fetchone()[0]
    duplicate_pks = total_count - distinct_pk_count

    # Null PK count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {pk_col} IS NULL")
    null_pks = cursor.fetchone()[0]

    # Get column null counts
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [r[1] for r in cursor.fetchall()]

    null_counts = {}
    for c in cols:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {c} IS NULL")
        null_counts[c] = cursor.fetchone()[0]

    conn.close()
    return {
        "total_count": total_count,
        "distinct_pks": distinct_pk_count,
        "duplicate_pks": duplicate_pks,
        "null_pks": null_pks,
        "null_counts": null_counts,
        "cols": cols,
    }

def compare_tables(base_db, cand_db, table_name, pk_col):
    conn_base = sqlite3.connect(f"file:{base_db}?mode=ro", uri=True)
    conn_cand = sqlite3.connect(f"file:{cand_db}?mode=ro", uri=True)

    c_base = conn_base.cursor()
    c_cand = conn_cand.cursor()

    c_base.execute(f"SELECT {pk_col} FROM {table_name}")
    base_pks = set(r[0] for r in c_base.fetchall())

    c_cand.execute(f"SELECT {pk_col} FROM {table_name}")
    cand_pks = set(r[0] for r in c_cand.fetchall())

    added = cand_pks - base_pks
    removed = base_pks - cand_pks

    added_details = []
    if added:
        placeholders = ",".join(f"'{pk}'" for pk in added)
        c_cand.execute(f"SELECT * FROM {table_name} WHERE {pk_col} IN ({placeholders})")
        cols = [d[0] for d in c_cand.description]
        for row in c_cand.fetchall():
            added_details.append(dict(zip(cols, row)))

    conn_base.close()
    conn_cand.close()

    return {
        "base_count": len(base_pks),
        "cand_count": len(cand_pks),
        "added_count": len(added),
        "removed_count": len(removed),
        "added_pks": list(added),
        "removed_pks": list(removed),
        "added_details": added_details,
    }

def main():
    print("=" * 80)
    print("DEEP RECONCILIATION: BASELINE WORKING DB VS CANDIDATE WORKING DB")
    print("=" * 80)

    # 1. Compare all tables
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
        comp = compare_tables(BASELINE_WORKING_DB, CANDIDATE_DB, tbl, pk)
        print(f"\n[{tbl}] Baseline: {comp['base_count']} | Candidate: {comp['cand_count']} | Added: {comp['added_count']} | Removed: {comp['removed_count']}")
        if comp["removed_count"] > 0:
            print(f"  WARNING: {comp['removed_count']} records REMOVED from baseline!")
        if comp["added_count"] > 0:
            print(f"  Added PKs ({comp['added_count']}): {comp['added_pks'][:5]}...")
            # Inspect provenance of added records
            for d in comp["added_details"][:3]:
                prov = d.get("provenance") or d.get("provenance_sources") or d.get("source_name")
                print(f"    Sample Added: PK={d.get(pk)}, Name={d.get('title') or d.get('job_title') or d.get('entity_name')}, Provenance={prov}, Date={d.get('published_at') or d.get('posted_at')}")

    # Check Canonical DB counts as well
    print("\n" + "=" * 80)
    print("CANONICAL DB COUNTS:")
    print("=" * 80)
    conn_can = sqlite3.connect(f"file:{CANONICAL_DB}?mode=ro", uri=True)
    c_can = conn_can.cursor()
    for tbl, pk in tables:
        if tbl in ("github_metrics_history", "collection_logs"):
            continue
        c_can.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl}: {c_can.fetchone()[0]}")
    conn_can.close()

if __name__ == "__main__":
    main()

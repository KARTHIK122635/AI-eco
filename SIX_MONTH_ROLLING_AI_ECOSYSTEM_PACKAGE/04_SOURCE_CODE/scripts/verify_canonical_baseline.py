import sqlite3
import csv
import os

def verify_canonical():
    db_path = 'data/normalized/ai_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    print(f"PRAGMA integrity_check on active DB: {integrity}")
    assert integrity == "ok"

    counts = {
        "ai_startups": 1307,
        "ai_products": 1316,
        "ai_research_papers": 1060,
        "ai_news": 1132,
        "ai_jobs": 1930
    }

    total = 0
    for tbl, expected in counts.items():
        cur.execute(f"SELECT count(*) FROM {tbl}")
        actual = cur.fetchone()[0]
        print(f"Table {tbl:22s}: actual = {actual:5d}, expected = {expected:5d} -> {'MATCH' if actual == expected else 'MISMATCH'}")
        assert actual == expected, f"Count mismatch for {tbl}: expected {expected}, got {actual}"
        total += actual

    print(f"Total Canonical Records: {total} (expected 6,745) -> MATCH")

    # Verify primary key uniqueness
    pk_map = {
        "ai_startups": "startup_id",
        "ai_products": "product_id",
        "ai_research_papers": "paper_id",
        "ai_news": "news_id",
        "ai_jobs": "job_id"
    }

    for tbl, pk in pk_map.items():
        cur.execute(f"SELECT count(DISTINCT {pk}) FROM {tbl}")
        distinct_pk = cur.fetchone()[0]
        cur.execute(f"SELECT count(*) FROM {tbl}")
        total_rows = cur.fetchone()[0]
        assert distinct_pk == total_rows, f"PK duplication in {tbl}: {distinct_pk} distinct vs {total_rows} rows"
        print(f"PK uniqueness for {tbl} ({pk}): {distinct_pk}/{total_rows} unique -> 100% UNIQUE")

    conn.close()
    print("\nCanonical Dataset Verification PASSED: All 6,745 records completely intact and immutable.")

if __name__ == '__main__':
    verify_canonical()

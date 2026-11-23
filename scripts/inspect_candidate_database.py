"""
Database Inspection Script for Candidate Database (Stage 3).
Connects in strict read-only mode, queries exact table counts and schemas.
"""

import sqlite3
import os
import sys
import json

DB_PATH = os.path.join("data", "working", "candidate_rolling_ai_ecosystem.db")

EXPECTED_COUNTS = {
    "ai_startups": 1307,
    "ai_products": 1316,
    "ai_research_papers": 1060,
    "ai_news": 1138,
    "ai_jobs": 1963,
    "github_repositories": 190,
    "github_metrics_history": 205,
    "collection_logs": 6,
}

def inspect_database():
    print("=" * 70)
    print("STAGE 3 — CANDIDATE DATABASE EXTRACTION & SCHEMA INSPECTION")
    print("=" * 70)
    print(f"Database Path : {DB_PATH}")
    print(f"File Exists   : {os.path.isfile(DB_PATH)}")

    if not os.path.isfile(DB_PATH):
        print("[ERROR] Candidate database file not found!")
        return False

    uri = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"\nAll Database Tables ({len(tables)}): {tables}")

    # Inspect counts
    print("\nTable Row Count Reconciliation:")
    print(f"{'Table Name':<30} | {'Expected':<10} | {'Actual':<10} | {'Status':<10}")
    print("-" * 68)

    all_matched = True
    counts = {}
    for tbl, expected in EXPECTED_COUNTS.items():
        if tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = cursor.fetchone()[0]
            counts[tbl] = cnt
            status = "MATCH" if cnt == expected else "DISCREPANCY"
            if cnt != expected:
                all_matched = False
            print(f"{tbl:<30} | {expected:<10} | {cnt:<10} | {status:<10}")
        else:
            print(f"{tbl:<30} | {expected:<10} | {'MISSING':<10} | FAILED")
            all_matched = False

    # Also check other tables present
    other_tables = [t for t in tables if t not in EXPECTED_COUNTS and not t.startswith("sqlite_")]
    if other_tables:
        print("\nAdditional Tables Present:")
        for tbl in other_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = cursor.fetchone()[0]
            print(f"  - {tbl}: {cnt} rows")

    # Inspect Schemas for target tables
    print("\nDetailed Schema Mapping for Worksheets:")
    schema_info = {}
    for tbl in list(EXPECTED_COUNTS.keys()):
        if tbl in tables:
            cursor.execute(f"PRAGMA table_info({tbl})")
            columns = [(c[1], c[2]) for c in cursor.fetchall()]
            schema_info[tbl] = columns
            print(f"\n[{tbl}] ({len(columns)} columns):")
            col_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
            print(f"  {col_str}")

    conn.close()

    print("\n" + "=" * 70)
    print(f"COUNT RECONCILIATION RESULT: {'ALL COUNTS MATCH' if all_matched else 'DISCREPANCIES DETECTED'}")
    print("=" * 70)
    return all_matched

if __name__ == "__main__":
    ok = inspect_database()
    sys.exit(0 if ok else 1)

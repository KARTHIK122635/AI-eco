"""
scripts/inspect_phase5_schema_details.py
========================================
Inspects tables, columns, constraints, and record counts of data/working/phase5_github_candidate.db
in strict read-only mode.
"""

import os
import sys
import sqlite3

DB_PATH = "data/working/phase5_github_candidate.db"

def main():
    uri = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall()]
    print("=" * 80)
    print("PHASE V DATABASE INSPECTION")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Tables ({len(tables)}): {', '.join(tables)}")

    for t in tables:
        cursor.execute(f"PRAGMA table_info({t});")
        cols = cursor.fetchall()
        cursor.execute(f"SELECT count(*) FROM {t};")
        cnt = cursor.fetchone()[0]
        print(f"\nTable '{t}' ({cnt} rows, {len(cols)} columns):")
        for c in cols:
            pk = " [PK]" if c[5] else ""
            dflt = f" DEFAULT {c[4]}" if c[4] is not None else ""
            notnull = " NOT NULL" if c[3] else ""
            print(f"    {c[1]:<30} {c[2]:<10}{notnull}{dflt}{pk}")

    conn.close()

if __name__ == "__main__":
    main()

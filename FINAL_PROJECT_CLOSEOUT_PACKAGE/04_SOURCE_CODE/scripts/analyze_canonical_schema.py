"""
Canonical Schema Analysis for Stage 3 Candidates
=================================================
Maps each candidate record's target field to the actual canonical SQLite schema.
"""

import json
import sqlite3

def main():
    conn = sqlite3.connect("data/normalized/ai_ecosystem.db")
    cur = conn.cursor()

    tables = ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]
    table_cols = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        table_cols[t] = {r[1]: r[2] for r in cur.fetchall()}

    print("Canonical Table Columns:")
    for t, cols in table_cols.items():
        print(f"  {t}: {list(cols.keys())}")

    # Load 37 candidates
    with open("reports/stage3_enrichment_results.jsonl", "r", encoding="utf-8") as f:
        candidates = [json.loads(line) for line in f if line.strip()]

    print(f"\nAnalyzing {len(candidates)} candidates against canonical schema:")
    print("-" * 100)
    print(f"{'#':<3} {'Entity':<8} {'Record ID':<28} {'Target Field':<20} {'Table':<20} {'Column Exists?':<15} {'Safe Action'}")
    print("-" * 100)

    table_map = {
        "startup": "ai_startups",
        "product": "ai_products",
        "paper": "ai_research_papers",
        "news": "ai_news",
        "job": "ai_jobs",
    }

    exists_count = 0
    missing_count = 0
    for i, c in enumerate(candidates, 1):
        entity = c["entity_type"]
        field = c["field_name"]
        rec_id = c["record_id"]
        table = table_map[entity]
        exists = field in table_cols[table]

        if exists:
            exists_count += 1
            safe_action = "SCHEMA_COMPATIBLE (can update directly if approved)"
        else:
            missing_count += 1
            safe_action = "BLOCKED_SCHEMA (requires migration or schema decision)"

        rec_disp = rec_id if len(rec_id) <= 26 else rec_id[:23] + "..."
        print(f"{i:<3} {entity:<8} {rec_disp:<28} {field:<20} {table:<20} {str(exists):<15} {safe_action}")

    print("-" * 100)
    print(f"Total: {len(candidates)} | Exists in DB: {exists_count} | Missing from DB: {missing_count}")

if __name__ == "__main__":
    main()

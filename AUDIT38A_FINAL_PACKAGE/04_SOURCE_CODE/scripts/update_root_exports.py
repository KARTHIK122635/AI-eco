import json
import csv
import sqlite3
import pandas as pd

print("Updating root data files with unified view...")

with open("data/normalized/ai_startups.jsonl", "r", encoding="utf-8") as f:
    startups = [json.loads(line) for line in f]

with open("data/normalized/ai_products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

unified_records = []

for s in startups:
    unified_records.append({
        "company_name": s["name"],
        "product_name": None,
        "entity_type": "AI Startup",
        "description": s["description"],
        "employee_count": s["employee_count"],
        "pricing_model": s["pricing_model"],
        "company_website": s["website"],
        "original_source_url": s["primary_source_url"],
        "source_directory": "; ".join(s["provenance_sources"]),
        "categories": s["ai_focus_area"],
        "discovered_at": s["discovered_at"]
    })

for p in products:
    unified_records.append({
        "company_name": p["developer_or_company"],
        "product_name": p["name"],
        "entity_type": "AI Product",
        "description": p["description"],
        "employee_count": None,
        "pricing_model": p["pricing_model"],
        "company_website": None,
        "original_source_url": p["original_source_url"],
        "source_directory": p["provenance_source"],
        "categories": p["ai_task_category"],
        "discovered_at": p["discovered_at"]
    })

# Export to root CSV
df = pd.DataFrame(unified_records)
df.to_csv("data/startups_and_products.csv", index=False)

# Export to root JSONL
with open("data/startups_and_products.jsonl", "w", encoding="utf-8") as f:
    for r in unified_records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# Export to root DB
with sqlite3.connect("data/startups_and_products.db") as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS records")
    cursor.execute("""
    CREATE TABLE records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        product_name TEXT,
        entity_type TEXT,
        description TEXT,
        employee_count TEXT,
        pricing_model TEXT,
        company_website TEXT,
        original_source_url TEXT,
        source_directory TEXT,
        categories TEXT,
        discovered_at TEXT
    )
    """)
    for r in unified_records:
        cursor.execute("""
        INSERT INTO records (
            company_name, product_name, entity_type, description,
            employee_count, pricing_model, company_website,
            original_source_url, source_directory, categories, discovered_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["company_name"], r["product_name"], r["entity_type"], r["description"],
            str(r["employee_count"]) if r["employee_count"] is not None else None,
            r["pricing_model"], r["company_website"], r["original_source_url"],
            r["source_directory"], r["categories"], r["discovered_at"]
        ))
    conn.commit()

print(f"Root files updated with {len(unified_records):,} total verified records.")

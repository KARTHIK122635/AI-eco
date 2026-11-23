import sqlite3
import pandas as pd
import json

print("=== VALIDATING CANONICAL NORMALIZED DATASETS ===")

# 1. AI Startups
df_startups = pd.read_csv("data/normalized/ai_startups.csv")
print(f"\n1. AI Startups Count: {len(df_startups):,}")
print("   Columns:", df_startups.columns.tolist())
print("   Non-null counts:")
print(df_startups.notnull().sum())
print("\n   Top AI Focus Areas:")
print(df_startups["ai_focus_area"].value_counts().head(6))
print("\n   Top Provenance Sources:")
print(df_startups["provenance_sources"].value_counts().head(5))

# 2. AI Products
df_products = pd.read_csv("data/normalized/ai_products.csv")
print(f"\n2. AI Products Count: {len(df_products):,}")
print("   Columns:", df_products.columns.tolist())
print("   Non-null counts:")
print(df_products.notnull().sum())
print("\n   Product Types:")
print(df_products["product_type"].value_counts().head(5))
print("\n   Top AI Task Categories:")
print(df_products["ai_task_category"].value_counts().head(6))
print("\n   Pricing Models:")
print(df_products["pricing_model"].value_counts().head(6))

# 3. SQLite Database Check
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
    s_count = c.execute("SELECT COUNT(*) FROM ai_startups").fetchone()[0]
    p_count = c.execute("SELECT COUNT(*) FROM ai_products").fetchone()[0]
    print(f"\n3. SQLite Database Verification:")
    print(f"   ai_startups table rows: {s_count:,}")
    print(f"   ai_products table rows: {p_count:,}")

# 4. Check Archived Non-AI Data
with open("data/raw/preliminary_non_ai_archive.jsonl", "r", encoding="utf-8") as f:
    archived_non_ai = [json.loads(line) for line in f]
print(f"\n4. Non-AI Archived Records Count: {len(archived_non_ai)}")
print("   Sample Non-AI companies:", [r.get("company_name") for r in archived_non_ai[:8]])

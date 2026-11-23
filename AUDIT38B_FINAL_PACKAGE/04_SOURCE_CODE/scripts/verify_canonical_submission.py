import json
import sqlite3
import pandas as pd

print("=" * 70)
print("VERIFYING CANONICAL INTERNSHIP ASSIGNMENT SUBMISSION ASSETS")
print("=" * 70)

# 1. Startups
with open("data/canonical/canonical_startups.jsonl", "r", encoding="utf-8") as f:
    s_records = [json.loads(line) for line in f]
df_s = pd.read_csv("data/canonical/canonical_startups.csv")

print(f"\n1. CANONICAL STARTUPS: {len(s_records):,} records")
print(f"   Schema sample check: recordType='{s_records[0].get('recordType')}', schemaVersion='{s_records[0].get('schemaVersion')}'")
print(f"   Source keys: {list(s_records[0].get('source', {}).keys())}")
print(f"   Content keys: {list(s_records[0].get('content', {}).keys())}")
print(f"   Data keys: {list(s_records[0]['content']['data'].keys())}")
print(f"   CSV Shape: {df_s.shape}, Columns: {df_s.columns.tolist()[:6]}...")
print("   Field coverage in CSV:")
for col in df_s.columns:
    print(f"     - {col}: {df_s[col].notnull().sum()}/{len(df_s)} ({df_s[col].notnull().sum()/len(df_s)*100:.1f}%)")

# 2. Products
with open("data/canonical/canonical_products.jsonl", "r", encoding="utf-8") as f:
    p_records = [json.loads(line) for line in f]
df_p = pd.read_csv("data/canonical/canonical_products.csv")

print(f"\n2. CANONICAL PRODUCTS: {len(p_records):,} records")
print(f"   Distinct product entityNames: {df_p['entity_name'].nunique():,}")
print(f"   Unique product URLs: {df_p['original_source_url'].nunique():,}")
print(f"   Schema sample check: recordType='{p_records[0].get('recordType')}'")
print(f"   Data keys: {list(p_records[0]['content']['data'].keys())}")
print("   Field coverage in CSV:")
for col in df_p.columns:
    print(f"     - {col}: {df_p[col].notnull().sum()}/{len(df_p)} ({df_p[col].notnull().sum()/len(df_p)*100:.1f}%)")

# 3. Research Papers
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    r_records = [json.loads(line) for line in f]
df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")

print(f"\n3. CANONICAL RESEARCH PAPERS: {len(r_records):,} records")
print(f"   Distinct paper titles: {df_r['title'].nunique():,}")
print(f"   Unique paper URLs: {df_r['paper_url'].nunique():,}")
print(f"   Schema sample check: recordType='{r_records[0].get('recordType')}'")
print(f"   Data keys: {list(r_records[0]['content']['data'].keys())}")
print(f"   Papers with correlated GitHub repo: {df_r['github_url'].notnull().sum():,}")
print(f"   Papers with GitHub stars retrieved: {df_r['github_stars'].notnull().sum():,}")
print("   Field coverage in CSV:")
for col in df_r.columns:
    print(f"     - {col}: {df_r[col].notnull().sum()}/{len(df_r)} ({df_r[col].notnull().sum()/len(df_r)*100:.1f}%)")

# 4. SQLite Database
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
    print("\n4. SQLITE DATABASE (data/normalized/ai_ecosystem.db):")
    for tbl in ["ai_startups", "ai_products", "ai_research_papers"]:
        cnt = c.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"   - Table '{tbl}': {cnt:,} rows")

# 5. Check All-in-One submission stream
with open("data/canonical/canonical_submission_all.jsonl", "r", encoding="utf-8") as f:
    total_lines = sum(1 for _ in f)
print(f"\n5. UNIFIED SUBMISSION STREAM (canonical_submission_all.jsonl): {total_lines:,} total records")

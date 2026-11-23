import json
import sqlite3
import pandas as pd

# 1. source_assessments.json
with open('data/source_assessments.json', 'r', encoding='utf-8') as f:
    assessments = json.load(f)
print(f"1. Assessments count: {len(assessments)}")
for a in assessments:
    print(f"   - {a['source_name']}: accessible={a['accessible']}, code={a['status_code']}")

# 2. JSONL count and sample
with open('data/startups_and_products.jsonl', 'r', encoding='utf-8') as f:
    jsonl_records = [json.loads(line) for line in f]
print(f"\n2. JSONL records count: {len(jsonl_records)}")
print(f"   Fields in first record: {list(jsonl_records[0].keys())}")

# 3. CSV count and columns
df = pd.read_csv('data/startups_and_products.csv')
print(f"\n3. CSV records count: {len(df)}")
print(f"   CSV columns: {df.columns.tolist()}")

# 4. SQLite count and tables
with sqlite3.connect('data/startups_and_products.db') as conn:
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n4. SQLite tables: {tables}")
    count = cursor.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    print(f"   SQLite records count: {count}")
    cursor.execute("PRAGMA table_info(records)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"   SQLite columns: {columns}")

import json
import csv
import sqlite3
import hashlib
import sys

print("=" * 80)
print("COMPREHENSIVE VERIFICATION SUITE: PHASE II - STAGE 2: AUDIT 10")
print("=" * 80)

# 1. Load canonical datasets
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jsonl_data = [json.loads(line)['content']['data'] for line in f]

with open('data/canonical/canonical_jobs.csv', 'r', encoding='utf-8') as f:
    csv_data = list(csv.DictReader(f))

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM ai_jobs")
db_rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(ai_jobs)")
db_cols = [c[1] for c in cursor.fetchall()]
conn.close()

assert len(jsonl_data) == 1930
assert len(csv_data) == 1930
assert len(db_rows) == 1930
print("1. Record Count: Exactly 1,930 in JSONL, CSV, and SQLite [PASSED]")

# 2. SQLite PRAGMA integrity check
conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cursor = conn.cursor()
cursor.execute("PRAGMA integrity_check;")
assert cursor.fetchone()[0] == 'ok'
print("2. SQLite PRAGMA integrity_check == ok [PASSED]")

# 3. Historical tables check
tables = ['ai_startups', 'ai_products', 'ai_research_papers', 'ai_news', 'ai_jobs']
expected_counts = {'ai_startups': 1307, 'ai_products': 1316, 'ai_research_papers': 1060, 'ai_news': 1132, 'ai_jobs': 1930}
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    assert cnt == expected_counts[t], f"Table {t} has {cnt} rows, expected {expected_counts[t]}"
conn.close()
print("3. Historical Preservation: All 4 historical tables and 6,745 rows exact match [PASSED]")

# 4. Uniqueness check
jids = [j['jobId'] for j in jsonl_data]
urls = [j['applicationUrl'] for j in jsonl_data]
assert len(set(jids)) == 1930
assert len(set(urls)) == 1930
print("4. Uniqueness: 0 duplicate Job IDs and 0 duplicate application URLs [PASSED]")

# 5. Compensation disclosures
disclosed = [j for j in jsonl_data if j.get('salaryMin') is not None or j.get('salaryMax') is not None]
null_sal = [j for j in jsonl_data if j.get('salaryMin') is None and j.get('salaryMax') is None]
assert len(disclosed) == 1268
assert len(null_sal) == 662
print("5. Compensation Integrity: 1,268 disclosed / 662 null perfectly preserved [PASSED]")

# 6. Quality audit reason equality
with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    q_rows = list(csv.DictReader(f))
assert len(q_rows) == 1930
jsonl_map = {j['jobId']: j for j in jsonl_data}
for q in q_rows:
    jid = q['job_id']
    assert q['classification_reason'] == jsonl_map[jid]['classificationReason']
    assert q['category'] == jsonl_map[jid]['category']
print("6. Quality Audit Parity: Every audit reason and category equals canonical [PASSED]")

# 7. Semantic audit reason equality
with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    s_rows = list(csv.DictReader(f))
assert len(s_rows) == 1930
for s in s_rows:
    jid = s['Job ID']
    assert s['Updated classificationReason'] == jsonl_map[jid]['classificationReason']
print("7. Semantic Audit Parity: All 1,930 records map to canonical and match reasons [PASSED]")

# 8. Category Breakdown
from collections import Counter
cat_counts = Counter(j['category'] for j in jsonl_data)
print(f"8. Taxonomy Breakdown: {dict(cat_counts)} [PASSED]")
assert cat_counts['UNCERTAIN'] == 3

# 9. Test Case Verification
test_cases = [
    ('job_dca7b0b6a47a6b85', 'AI_SUPPORTING_TECH'),
    ('job_93cbaa791c40727a', 'AI_INFRASTRUCTURE'),
    ('job_799b4f210a0fa4ff', 'AI_INFRASTRUCTURE'),
    ('job_e8078287eb87dc0c', 'AI_SUPPORTING_TECH'),
    ('job_f758d5d0dfd3c148', 'AI_SUPPORTING_TECH')
]
for jid, exp_cat in test_cases:
    assert jsonl_map[jid]['category'] == exp_cat, f"{jid} has {jsonl_map[jid]['category']}, expected {exp_cat}"
print("9. Specific Priority Test Cases Verified [PASSED]")

print("=" * 80)
print("ALL AUDIT 10 VERIFICATION SUITES PASSED WITH ZERO ERRORS!")
print("=" * 80)

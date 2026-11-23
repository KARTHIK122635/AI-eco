import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scripts'))
import json
import csv
import sqlite3
from datetime import datetime, timezone

print("=== Starting Phase II – Stage 2: Audit 18 Provenance Pipeline ===")

target_ids = [
    'job_635816dfd21a2298',
    'job_58809b0308baf230',
    'job_4dbed03c7b9d1981',
    'job_675a85266ca800bd'
]

# 1. Load canonical jobs from JSONL
jsonl_path = 'data/canonical/canonical_jobs.jsonl'
with open(jsonl_path, 'r', encoding='utf-8') as f:
    raw_lines = [json.loads(line) for line in f]

jobs = [entry['content']['data'] for entry in raw_lines]
print(f"Loaded {len(jobs)} canonical jobs from JSONL.")
assert len(jobs) == 1930

# Load CSV
csv_path = 'data/canonical/canonical_jobs.csv'
with open(csv_path, 'r', encoding='utf-8') as f:
    csv_rows = list(csv.DictReader(f))
print(f"Loaded {len(csv_rows)} canonical jobs from CSV.")
assert len(csv_rows) == 1930

# 2. Inspect and verify the 4 target records in JSONL and CSV
provenance_inspection_data = []
jobs_by_id = {j['jobId']: j for j in jobs}
csv_by_id = {r['jobId']: r for r in csv_rows}

for jid in target_ids:
    j = jobs_by_id[jid]
    c = csv_by_id[jid]
    
    prov_obj = j['provenance']
    assert isinstance(prov_obj, dict), f"Job {jid} provenance in JSONL is not a dict: {type(prov_obj)}"
    assert 'source' in prov_obj, f"Job {jid} provenance missing 'source'"
    assert 'raw_compensation_disclosure' in prov_obj, f"Job {jid} provenance missing 'raw_compensation_disclosure'"
    
    prov_json_str = json.dumps(prov_obj, ensure_ascii=False)
    assert c['provenance'] == prov_json_str, f"Job {jid} CSV provenance does not match JSONL dump!"
    
    provenance_inspection_data.append({
        'job_id': jid,
        'company_name': j['companyName'],
        'job_title': j['jobTitle'],
        'category': j['category'],
        'source_url': prov_obj['source'],
        'raw_compensation_disclosure': prov_obj['raw_compensation_disclosure'],
        'provenance_object_json': prov_json_str
    })

print(f"Verified {len(provenance_inspection_data)} target provenance objects in JSONL and CSV.")

# 3. Update SQLite Database
db_path = 'data/normalized/ai_ecosystem.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verify integrity before update
cur.execute("PRAGMA integrity_check")
ic_before = cur.fetchone()[0]
assert ic_before == 'ok', f"Integrity check failed before update: {ic_before}"

# Update provenance in SQLite for all 4 target records
for item in provenance_inspection_data:
    jid = item['job_id']
    prov_str = item['provenance_object_json']
    cur.execute("UPDATE ai_jobs SET provenance = ? WHERE job_id = ?", (prov_str, jid))
    print(f"Explicitly updated SQLite ai_jobs provenance for {jid}")

conn.commit()

# Run VACUUM to ensure clean, defragmented storage
cur.execute("VACUUM")
conn.commit()

# Verify integrity after update
cur.execute("PRAGMA integrity_check")
ic_after = cur.fetchone()[0]
assert ic_after == 'ok', f"Integrity check failed after update: {ic_after}"

# Confirm each record in SQLite retains both fields
for item in provenance_inspection_data:
    jid = item['job_id']
    cur.execute("SELECT provenance FROM ai_jobs WHERE job_id = ?", (jid,))
    db_prov = cur.fetchone()[0]
    parsed = json.loads(db_prov)
    assert 'source' in parsed
    assert 'raw_compensation_disclosure' in parsed
    assert parsed['source'] == item['source_url']
    assert parsed['raw_compensation_disclosure'] == item['raw_compensation_disclosure']
    item['sqlite_provenance_verified'] = True
    item['sqlite_value'] = db_prov

print("All 4 SQLite provenance records confirmed to contain both 'source' and 'raw_compensation_disclosure'.")

# Check row counts in SQLite
cur.execute("SELECT COUNT(*) FROM ai_jobs")
ai_jobs_count = cur.fetchone()[0]
assert ai_jobs_count == 1930

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall() if not r[0].startswith('sqlite_')]
expected_historical = {
    'ai_startups': 1307,
    'ai_products': 1316,
    'ai_research_papers': 1060,
    'ai_news': 1132
}
total_db_rows = 0
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    c = cur.fetchone()[0]
    total_db_rows += c
    print(f"  Table {t:20s}: {c:5d} rows")
    if t in expected_historical:
        assert c == expected_historical[t]

assert total_db_rows == 6745
print(f"Total rows across all 5 tables in ai_ecosystem.db: {total_db_rows}")
conn.close()

# 4. Save inspection report
inspection_payload = {
    "audit_version": "Audit 18",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "audit_mandate": "Audit 18 — SQLite Provenance Parity Correction",
    "target_records_count": len(provenance_inspection_data),
    "parity_status": "EXACT_PARITY_VERIFIED",
    "fields_preserved": ["source", "raw_compensation_disclosure"],
    "records": provenance_inspection_data
}

with open('reports/audit18_provenance_inspection.json', 'w', encoding='utf-8') as f:
    json.dump(inspection_payload, f, indent=2, ensure_ascii=False)

print("Saved reports/audit18_provenance_inspection.json.")

# 5. Update stage2_quality_metrics.json audit_version to "Audit 18"
with open('reports/stage2_quality_metrics.json', 'r', encoding='utf-8') as f:
    metrics = json.load(f)

metrics['audit_version'] = 'Audit 18'
metrics['generated_at'] = datetime.now(timezone.utc).isoformat()
metrics['integrity_metrics']['sqlite_provenance_parity'] = "100.0% Exact Parity (All 4 structured provenance objects fully preserved in SQLite)"

with open('reports/stage2_quality_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print("Updated reports/stage2_quality_metrics.json with Audit 18 metadata.")
print("=== Phase II – Stage 2: Audit 18 Pipeline Completed Successfully ===")

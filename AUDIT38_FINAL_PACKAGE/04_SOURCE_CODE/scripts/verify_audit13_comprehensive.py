import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import sqlite3
from collections import Counter
from scripts.test_audit13_evidence_cleanup import is_promotional
from scripts.test_quality_audit_regeneration import REASON_UPDATES, CATEGORY_UPDATES, RETAINED_REVIEWS

print("=" * 80)
print("COMPREHENSIVE VERIFICATION SUITE: PHASE II - STAGE 2: AUDIT 13")
print("=" * 80)

# 1. Canonical Record Counts
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jsonl_data = [json.loads(line)['content']['data'] for line in f]

with open('data/canonical/canonical_jobs.csv', 'r', encoding='utf-8') as f:
    csv_data = list(csv.DictReader(f))

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM ai_jobs")
db_rows = cursor.fetchall()

assert len(jsonl_data) == 1930
assert len(csv_data) == 1930
assert len(db_rows) == 1930
print("1. Record Count: Exactly 1,930 across JSONL, CSV, and SQLite [PASSED]")

# 2. SQLite PRAGMA integrity check
cursor.execute("PRAGMA integrity_check;")
assert cursor.fetchone()[0] == 'ok'
print("2. SQLite PRAGMA integrity_check == ok [PASSED]")

# 3. Historical Preservation
tables = ['ai_startups', 'ai_products', 'ai_research_papers', 'ai_news', 'ai_jobs']
expected_counts = {'ai_startups': 1307, 'ai_products': 1316, 'ai_research_papers': 1060, 'ai_news': 1132, 'ai_jobs': 1930}
total_db_rows = 0
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    total_db_rows += cnt
    assert cnt == expected_counts[t], f"Table {t} has {cnt} rows, expected {expected_counts[t]}"
assert total_db_rows == 6745
print("3. Historical Preservation: All 4 historical tables and 6,745 rows exact match [PASSED]")

# 4. Uniqueness
jids = [j['jobId'] for j in jsonl_data]
urls = [j['applicationUrl'] for j in jsonl_data]
assert len(set(jids)) == 1930
assert len(set(urls)) == 1930
print("4. Uniqueness: 0 duplicate Job IDs and 0 duplicate application URLs [PASSED]")

# 5. Compensation Preservation
disclosed = [j for j in jsonl_data if j.get('salaryMin') is not None or j.get('salaryMax') is not None]
null_sal = [j for j in jsonl_data if j.get('salaryMin') is None and j.get('salaryMax') is None]
assert len(disclosed) == 1268
assert len(null_sal) == 662
print("5. Compensation Integrity: 1,268 disclosed / 662 null preserved [PASSED]")

# 6. Specific Target Checks (Section 1 and Section 2)
print("6. Verifying Mandated Target Records:")
for jid, expected_reason in REASON_UPDATES.items():
    j = [x for x in jsonl_data if x['jobId'] == jid][0]
    assert j['classificationReason'] == expected_reason, f"Reason mismatch on {jid}!"

for jid, expected_cat in CATEGORY_UPDATES.items():
    j = [x for x in jsonl_data if x['jobId'] == jid][0]
    assert j['category'] == expected_cat, f"Category mismatch on {jid}!"

print(f"   All {len(REASON_UPDATES)} target reasons and {len(CATEGORY_UPDATES)} categories verified! [PASSED]")

# 7. Semantic Evidence Quality Across All 1,930 Records
non_verbatim = 0
promo_found = 0
for j in jsonl_data:
    ev = j['responsibilityEvidence']
    if ev not in j['jobDescription']:
        non_verbatim += 1
    if is_promotional(ev):
        promo_found += 1

assert non_verbatim == 0, f"Found {non_verbatim} non-verbatim excerpts!"
assert promo_found == 0, f"Found {promo_found} promotional excerpts!"
print("7. Global Semantic Evidence: 100% verbatim (0 errors), 0 promotional excerpts [PASSED]")

# 8. Cross-Format Cell Parity Check (JSONL vs CSV vs SQLite across all 28 fields)
cursor.execute("PRAGMA table_info(ai_jobs)")
db_cols = [row[1] for row in cursor.fetchall()]

field_to_db = {
    'jobId': 'job_id',
    'jobTitle': 'job_title',
    'companyName': 'company_name',
    'companyWebsite': 'company_website',
    'category': 'category',
    'classificationReason': 'classification_reason',
    'responsibilityEvidence': 'responsibility_evidence',
    'qualificationEvidence': 'qualification_evidence',
    'classificationConfidence': 'classification_confidence',
    'jobDescription': 'job_description',
    'requiredSkills': 'required_skills',
    'preferredSkills': 'preferred_skills',
    'experienceLevel': 'experience_level',
    'location': 'location',
    'remoteType': 'remote_type',
    'salaryMin': 'salary_min',
    'salaryMax': 'salary_max',
    'currency': 'currency',
    'compensationType': 'compensation_type',
    'compensationPeriod': 'compensation_period',
    'employmentType': 'employment_type',
    'jobStatus': 'job_status',
    'vacancyStatus': 'vacancy_status',
    'applicationUrl': 'application_url',
    'postedAt': 'posted_at',
    'sourceName': 'source_name',
    'provenance': 'provenance',
    'collectedAt': 'collected_at'
}

cursor.execute("SELECT * FROM ai_jobs")
db_records_list = cursor.fetchall()
conn.close()

db_map = {row[db_cols.index('job_id')]: dict(zip(db_cols, row)) for row in db_records_list}
csv_map = {r['jobId']: r for r in csv_data}

parity_errors = 0
for j in jsonl_data:
    jid = j['jobId']
    csv_row = csv_map[jid]
    db_row = db_map[jid]
    
    # Check JSONL vs CSV
    for k, v in j.items():
        if k in csv_row:
            csv_val = csv_row[k]
            if v is None:
                expected_csv = ''
            elif isinstance(v, (list, dict)):
                expected_csv = json.dumps(v, ensure_ascii=False)
            elif isinstance(v, bool):
                expected_csv = str(v)
            elif isinstance(v, (int, float)):
                expected_csv = str(v)
            else:
                expected_csv = str(v)
            if csv_val != expected_csv:
                parity_errors += 1
                print(f"Parity error JSONL vs CSV for {jid} on {k}: {expected_csv} vs {csv_val}")

    # Check JSONL vs SQLite
    for k, db_col in field_to_db.items():
        if db_col in db_row:
            db_val = db_row[db_col]
            jsonl_val = j.get(k)
            if isinstance(jsonl_val, (int, float)) and db_val is not None:
                if abs(float(jsonl_val) - float(db_val)) > 1e-6:
                    parity_errors += 1
                    print(f"Numeric mismatch JSONL vs DB for {jid} on {k}: {jsonl_val} vs {db_val}")
            elif isinstance(jsonl_val, (list, dict)):
                db_val_parsed = json.loads(db_val) if db_val else []
                if jsonl_val != db_val_parsed:
                    parity_errors += 1
                    print(f"JSON mismatch JSONL vs DB for {jid} on {k}: {jsonl_val} vs {db_val}")
            elif (jsonl_val is None or jsonl_val == '') and (db_val is None or db_val == ''):
                pass
            elif str(jsonl_val) != str(db_val):
                parity_errors += 1
                print(f"String mismatch JSONL vs DB for {jid} on {k}: {jsonl_val} vs {db_val}")

assert parity_errors == 0, f"Found {parity_errors} cross-format parity errors!"
print("8. Cross-Format Parity: 100.0% exact cell match across JSONL, CSV, and SQLite across all 28 fields [PASSED]")

# 9. Quality Audit CSV Parity & Distribution
with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    q_rows = list(csv.DictReader(f))
assert len(q_rows) == 1930
jsonl_map = {j['jobId']: j for j in jsonl_data}

status_counts = Counter(r['audit_status'] for r in q_rows)
assert status_counts['PASS'] == 1923
assert status_counts['FAIL'] == 0
assert status_counts['REQUIRES_REVIEW'] == 7

for q in q_rows:
    jid = q['job_id']
    assert q['classification_reason'] == jsonl_map[jid]['classificationReason']
    assert q['category'] == jsonl_map[jid]['category']
    if q['audit_status'] == 'REQUIRES_REVIEW':
        assert q['defects_detected'] != 'None' and len(q['defects_detected']) > 5
print("9. Quality Audit Parity: Exact 1,923 PASS, 0 FAIL, 7 REQUIRES_REVIEW (with transparent documentation) [PASSED]")

# 10. Semantic Audit Parity
with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    s_rows = list(csv.DictReader(f))
assert len(s_rows) == 1930
for s in s_rows:
    jid = s['Job ID']
    assert s['Updated classificationReason'] == jsonl_map[jid]['classificationReason']
    assert s['Existing category'] == jsonl_map[jid]['category']
    assert s['Source evidence supporting explanation'] == jsonl_map[jid]['responsibilityEvidence']
    assert s['Source evidence supporting explanation'] in jsonl_map[jid]['jobDescription']
print("10. Semantic Audit Parity: All 1,930 map to canonical with identical reasons and verbatim evidence [PASSED]")

# 11. AI Relevance Audit Parity
with open('reports/stage2_ai_relevance_audit.csv', 'r', encoding='utf-8') as f:
    rel_rows = list(csv.DictReader(f))
assert len(rel_rows) == 1930
for r in rel_rows:
    jid = r['jobId']
    assert r['category'] == jsonl_map[jid]['category']
    assert r['classificationReason'] == jsonl_map[jid]['classificationReason']
print("11. AI Relevance Audit Parity: All 1,930 map to canonical with identical categories and reasons [PASSED]")

print("=" * 80)
print("ALL AUDIT 13 VERIFICATION SUITES PASSED WITH ZERO ERRORS!")
print("=" * 80)

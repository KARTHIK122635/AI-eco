import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import sqlite3
import re
from collections import Counter

print("=================================================================")
print("          PHASE II - STAGE 2: AUDIT 14 VERIFICATION SUITE       ")
print("=================================================================")

# 1. Load canonical jobs from JSONL
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jsonl_jobs = [json.loads(line)['content']['data'] for line in f]

print(f"1. Canonical JSONL Jobs Count: {len(jsonl_jobs)} (Expected: 1930)")
assert len(jsonl_jobs) == 1930, "JSONL count != 1930"

# 2. Load canonical CSV
with open('data/canonical/canonical_jobs.csv', 'r', encoding='utf-8') as f:
    csv_jobs = list(csv.DictReader(f))

print(f"2. Canonical CSV Jobs Count: {len(csv_jobs)} (Expected: 1930)")
assert len(csv_jobs) == 1930, "CSV count != 1930"

# 3. Load SQLite ai_jobs
conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cur = conn.cursor()
cur.execute("PRAGMA integrity_check")
integrity = cur.fetchone()[0]
print(f"3. SQLite Integrity Check: {integrity} (Expected: ok)")
assert integrity == 'ok', "SQLite integrity check failed"

cur.execute("SELECT COUNT(*) FROM ai_jobs")
db_count = cur.fetchone()[0]
print(f"   SQLite ai_jobs Count: {db_count} (Expected: 1930)")
assert db_count == 1930, "SQLite count != 1930"

# Historical table counts
expected_tables = {
    'ai_startups': 1307,
    'ai_products': 1316,
    'ai_research_papers': 1060,
    'ai_news': 1132,
    'ai_jobs': 1930
}
total_db_rows = 0
for table, exp_count in expected_tables.items():
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    cnt = cur.fetchone()[0]
    total_db_rows += cnt
    assert cnt == exp_count, f"Table {table} count mismatch: {cnt} vs {exp_count}"
print(f"   Historical Tables Preservation: Intact across all tables. Total DB rows: {total_db_rows} (Expected: 6745)")
assert total_db_rows == 6745, "Total DB rows != 6745"

# 4. Check uniqueness of job IDs and application URLs
jsonl_jids = [j['jobId'] for j in jsonl_jobs]
jsonl_urls = [j['applicationUrl'] for j in jsonl_jobs]
print(f"4. Unique Job IDs: {len(set(jsonl_jids))} (Expected: 1930)")
print(f"   Unique Application URLs: {len(set(jsonl_urls))} (Expected: 1930)")
assert len(set(jsonl_jids)) == 1930, "Duplicate job IDs found"
assert len(set(jsonl_urls)) == 1930, "Duplicate application URLs found"

# 5. Check Compensation Disclosures
disclosed_count = sum(1 for j in jsonl_jobs if j.get('salaryMin') is not None or j.get('salaryMax') is not None)
null_count = sum(1 for j in jsonl_jobs if j.get('salaryMin') is None and j.get('salaryMax') is None)
print(f"5. Compensation Disclosures: Disclosed: {disclosed_count}, Null: {null_count} (Expected: 1268 / 662)")
assert disclosed_count == 1268, f"Disclosed count mismatch: {disclosed_count}"
assert null_count == 662, f"Null count mismatch: {null_count}"

# 6. Check Cross-Format 28-Column Cell Parity
cur.execute("SELECT * FROM ai_jobs")
db_cols = [desc[0] for desc in cur.description]
db_rows = cur.fetchall()
conn.close()

db_jobs_map = {}
for r in db_rows:
    row_dict = dict(zip(db_cols, r))
    db_jobs_map[row_dict['job_id']] = row_dict

csv_jobs_map = {j['jobId']: j for j in csv_jobs}
jsonl_jobs_map = {j['jobId']: j for j in jsonl_jobs}

col_map_json_to_db = {
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

parity_errors = 0
for jid, j_json in jsonl_jobs_map.items():
    j_csv = csv_jobs_map[jid]
    j_db = db_jobs_map[jid]
    
    # Check JSONL vs CSV
    for k, v in j_json.items():
        csv_val = j_csv[k]
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
            if parity_errors <= 5:
                print(f"Parity error JSONL vs CSV for {jid} on {k}: '{expected_csv}' vs '{csv_val}'")

    # Check JSONL vs SQLite
    for k, db_col in col_map_json_to_db.items():
        db_val = j_db[db_col]
        jsonl_val = j_json.get(k)
        if isinstance(jsonl_val, (int, float)) and db_val is not None:
            if abs(float(jsonl_val) - float(db_val)) > 1e-6:
                parity_errors += 1
                if parity_errors <= 5:
                    print(f"Numeric mismatch JSONL vs DB for {jid} on {k}: {jsonl_val} vs {db_val}")
        elif isinstance(jsonl_val, (list, dict)):
            db_val_parsed = json.loads(db_val) if db_val else []
            if jsonl_val != db_val_parsed:
                parity_errors += 1
                if parity_errors <= 5:
                    print(f"JSON mismatch JSONL vs DB for {jid} on {k}: {jsonl_val} vs {db_val}")
        elif (jsonl_val is None or jsonl_val == '') and (db_val is None or db_val == ''):
            pass
        elif str(jsonl_val) != str(db_val):
            parity_errors += 1
            if parity_errors <= 5:
                print(f"String mismatch JSONL vs DB for {jid} on {k}: '{jsonl_val}' vs '{db_val}'")

print(f"6. Cross-Format Parity: 100.0% exact match across all 28 canonical columns (Errors: {parity_errors})")
assert parity_errors == 0, f"Parity errors found: {parity_errors}"

# 7. Evidence Verbatim Substring Check
verbatim_errors = 0
for j in jsonl_jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    desc = j.get('jobDescription', '') or ''
    if ev not in desc:
        verbatim_errors += 1
        if verbatim_errors <= 5:
            print(f"Non-verbatim error on {j['jobId']}: '{ev[:60]}...'")

print(f"7. Verbatim Evidence Check: {1930 - verbatim_errors} / 1930 verbatim matches (Errors: {verbatim_errors})")
assert verbatim_errors == 0, f"Non-verbatim evidence errors found: {verbatim_errors}"

# 8. Strict Banned Pattern Check across all jobs
BANNED = [
    r'\b(?:product|strategic|company|long-term|our)\s+vision\b|paint the vision|set the vision|shaping the vision|strategic direction, ai vision|towards our vision|from the vision',
    r'\bmission\b',
    r'\bculture\b',
    r'\bour team\b|\bour teams\b',
    r'\bjoin\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b',
    r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b',
    r'\byears experience\b|\byears of experience\b',
    r'\bbachelor\'s degree\b|\bdegree in\b',
    r'\bideal candidate\b',
    r'\bwho you are\b|\bwhat you\'ll need\b',
    r'\bminimum qualifications\b|\bpreferred qualifications\b',
    r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b',
    r'\bexists to ensure\b',
    r'\bsit at the intersection\b',
    r'\bworld-class\b',
    r'\bcollaborative work:\b',
    r'\bplay a key role in\b|\bplays a key role in\b',
    r'^scale’s rapidly growing',
]
flagged_residuals = 0
for j in jsonl_jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    for p in BANNED:
        if re.search(p, ev, re.IGNORECASE):
            flagged_residuals += 1
            break

print(f"8. Residual Promotional/Introductory Check: {flagged_residuals} flagged records (Expected: 0)")
assert flagged_residuals == 0, f"Residual flagged records: {flagged_residuals}"

# 9. Verify Audit Files Parity and Exact Reason Matching
with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    sem_rows = list(csv.DictReader(f))

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    qual_rows = list(csv.DictReader(f))

print(f"9. Audit File Counts: Semantic: {len(sem_rows)}, Quality: {len(qual_rows)} (Expected: 1930 each)")
assert len(sem_rows) == 1930, "Semantic audit row count != 1930"
assert len(qual_rows) == 1930, "Quality audit row count != 1930"

sem_map = {r['Job ID']: r for r in sem_rows}
qual_map = {r['job_id']: r for r in qual_rows}

reason_mismatches = 0
for j in jsonl_jobs:
    jid = j['jobId']
    canonical_reason = j['classificationReason']
    sem_reason = sem_map[jid]['Updated classificationReason']
    qual_reason = qual_map[jid]['classification_reason']
    if canonical_reason != sem_reason or canonical_reason != qual_reason:
        reason_mismatches += 1

print(f"   Reason Exact Match Parity across Canonical, Semantic, and Quality Audits: {1930 - reason_mismatches} / 1930 (Mismatches: {reason_mismatches})")
assert reason_mismatches == 0, f"Reason mismatches found: {reason_mismatches}"

# Status breakdowns
sem_statuses = Counter(r['Semantic alignment result'] for r in sem_rows)
qual_statuses = Counter(r['audit_status'] for r in qual_rows)
print(f"   Semantic Audit Status Breakdown: {dict(sem_statuses)} (Expected: 1915 CONFIRMED_ALIGNED, 15 REQUIRES_REVIEW)")
print(f"   Quality Audit Status Breakdown: {dict(qual_statuses)} (Expected: 1915 PASS, 15 REQUIRES_REVIEW)")
assert sem_statuses['CONFIRMED_ALIGNED'] == 1915, "Semantic CONFIRMED_ALIGNED count != 1915"
assert sem_statuses['REQUIRES_REVIEW'] == 15, "Semantic REQUIRES_REVIEW count != 15"
assert sem_statuses.get('NOT_ALIGNED', 0) == 0, "Semantic NOT_ALIGNED count != 0"
assert qual_statuses['PASS'] == 1915, "Quality PASS count != 1915"
assert qual_statuses['REQUIRES_REVIEW'] == 15, "Quality REQUIRES_REVIEW count != 15"
assert qual_statuses.get('FAIL', 0) == 0, "Quality FAIL count != 0"

print("\n=================================================================")
print("          ALL AUDIT 14 VERIFICATIONS PASSED WITH 100.0% SUCCESS! ")
print("=================================================================")

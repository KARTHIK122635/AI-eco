import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import sqlite3
import pandas as pd
import hashlib

print("==================================================")
print("   COMPREHENSIVE AUDIT 16 VERIFICATION SUITE      ")
print("==================================================")

# 1. Load canonical datasets
jsonl_path = 'data/canonical/canonical_jobs.jsonl'
with open(jsonl_path, 'r', encoding='utf-8') as f:
    jsonl_data = [json.loads(line)['content']['data'] for line in f]

csv_path = 'data/canonical/canonical_jobs.csv'
csv_df = pd.read_csv(csv_path, keep_default_na=False)

db_path = 'data/normalized/ai_ecosystem.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print(f"\n[1] Record Counts:")
print(f"  - Canonical JSONL: {len(jsonl_data)} records")
print(f"  - Canonical CSV:   {len(csv_df)} records")
cur.execute("SELECT COUNT(*) FROM ai_jobs")
db_count = cur.fetchone()[0]
print(f"  - SQLite ai_jobs:  {db_count} records")
assert len(jsonl_data) == 1930
assert len(csv_df) == 1930
assert db_count == 1930
print("  => PASS: Exact 1,930 record count across JSONL, CSV, and SQLite.")

# 2. SQLite Database Integrity & Historical Tables
print(f"\n[2] SQLite Database Integrity & Historical Preservation:")
cur.execute("PRAGMA integrity_check")
integ = cur.fetchone()[0]
print(f"  - PRAGMA integrity_check: {integ}")
assert integ == 'ok'

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
    print(f"  - Table {t:20s}: {c:5d} rows")
    if t in expected_historical:
        assert c == expected_historical[t], f"Mismatch in {t}: expected {expected_historical[t]}, got {c}"

assert total_db_rows == 6745, f"Expected 6745 total rows, got {total_db_rows}"
print(f"  => PASS: All 4 historical tables perfectly preserved (4,815 rows), total DB rows = {total_db_rows}.")

# 3. Cell-by-cell Parity between JSONL and CSV
print(f"\n[3] Cell-by-cell Parity (JSONL vs CSV across 28 fields):")
fieldnames = list(jsonl_data[0].keys())
assert len(fieldnames) == 28
csv_cols = list(csv_df.columns)
assert fieldnames == csv_cols

mismatches = 0
for idx, (j_rec, c_row) in enumerate(zip(jsonl_data, csv_df.to_dict('records'))):
    for col in fieldnames:
        j_val = j_rec.get(col)
        c_val = c_row.get(col)
        
        # Format j_val to string representation as done in export
        if j_val is None:
            norm_j = ''
        elif isinstance(j_val, (list, dict)):
            norm_j = json.dumps(j_val, ensure_ascii=False)
        elif isinstance(j_val, bool):
            norm_j = str(j_val)
        elif isinstance(j_val, (int, float)):
            norm_j = str(j_val)
        else:
            norm_j = str(j_val)
            
        norm_c = str(c_val)
        if norm_j != norm_c:
            mismatches += 1
            if mismatches <= 3:
                print(f"    Mismatch at row {idx}, col {col}: JSONL='{norm_j[:30]}' vs CSV='{norm_c[:30]}'")

print(f"  - Total cell mismatches: {mismatches} / {len(jsonl_data) * 28}")
assert mismatches == 0
print("  => PASS: 100.0% Exact Cell-by-cell Parity between JSONL and CSV.")

# 4. Parity between JSONL and SQLite ai_jobs
print(f"\n[4] Parity between JSONL and SQLite ai_jobs:")
cur.execute("PRAGMA table_info(ai_jobs)")
db_cols = [r[1] for r in cur.fetchall()]
cur.execute("SELECT * FROM ai_jobs")
db_rows = cur.fetchall()

db_jobs_map = {}
for r in db_rows:
    row_dict = dict(zip(db_cols, r))
    db_jobs_map[row_dict['job_id']] = row_dict

jsonl_jobs_map = {j['jobId']: j for j in jsonl_data}

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

sqlite_mismatches = 0
for jid, j_json in jsonl_jobs_map.items():
    j_db = db_jobs_map[jid]
    for k, db_col in col_map_json_to_db.items():
        db_val = j_db[db_col]
        jsonl_val = j_json.get(k)
        if isinstance(jsonl_val, (int, float)) and db_val is not None:
            if abs(float(jsonl_val) - float(db_val)) > 1e-6:
                sqlite_mismatches += 1
        elif isinstance(jsonl_val, (list, dict)):
            db_val_parsed = json.loads(db_val) if db_val else []
            if jsonl_val != db_val_parsed:
                sqlite_mismatches += 1
        elif (jsonl_val is None or jsonl_val == '') and (db_val is None or db_val == ''):
            pass
        elif str(jsonl_val) != str(db_val):
            sqlite_mismatches += 1

print(f"  - Total SQLite cell mismatches: {sqlite_mismatches}")
assert sqlite_mismatches == 0
print("  => PASS: 100.0% Exact Parity between JSONL and SQLite ai_jobs.")

# 5. Uniqueness of Job IDs and Application URLs
print(f"\n[5] Uniqueness Validation:")
job_ids = [j['jobId'] for j in jsonl_data]
app_urls = [j['applicationUrl'] for j in jsonl_data]
assert len(set(job_ids)) == 1930
assert len(set(app_urls)) == 1930
print(f"  - Unique Job IDs:          {len(set(job_ids))} / 1930 (0 duplicates)")
print(f"  - Unique Application URLs: {len(set(app_urls))} / 1930 (0 duplicates)")
print("  => PASS: Zero duplicate IDs or URLs.")

# 6. Evidence Verbatim Substring Validation
print(f"\n[6] Evidence Substring Validation:")
non_verbatim_resp = 0
non_verbatim_qual = 0
for j in jsonl_data:
    jd = j['jobDescription']
    rev = j.get('responsibilityEvidence')
    if not rev or rev not in jd:
        non_verbatim_resp += 1
    qev = j.get('qualificationEvidence')
    if qev and qev not in jd:
        non_verbatim_qual += 1

print(f"  - Responsibility evidence verbatim: {1930 - non_verbatim_resp} / 1930 ({100.0 if non_verbatim_resp == 0 else 0}%)")
print(f"  - Qualification evidence verbatim:  {sum(1 for j in jsonl_data if j.get('qualificationEvidence')) - non_verbatim_qual} / {sum(1 for j in jsonl_data if j.get('qualificationEvidence'))}")
assert non_verbatim_resp == 0
assert non_verbatim_qual == 0
print("  => PASS: 100.0% of evidence excerpts are exact verbatim substrings of source jobDescription.")

# 7. Promotional / Introductory Residual Scan
print(f"\n[7] Promotional / Introductory Language Scan:")
import re
PATTERNS = [
    r'\b(?:at\s+[A-Za-z0-9\s]+,?\s+)?(?:we\s+are|we\'re|is)\s+seeking\b',
    r'\bwe(?:\'re|\s+are)\s+building\b',
    r'\bwho\s+should\s+apply\b',
    r'\babout\s+(?:the\s+role|wpp|scale|anthropic|databricks|coreweave|our|us)\b',
    r'\bforefront\s+of\b',
    r'\bteam\s+is\s+focused\s+on\b',
    r'\bwelcome\s+(?:remote\s+)?applicants\b',
    r'\bfounded\s+by\b',
    r'\bjoin\s+(?:our|the|us)\b',
    r'\bour\s+mission\b',
    r'\btrusted\s+growth\s+partner\b',
    r'\bplay\s+a\s+(?:critical|key|pivotal)\s+role\b',
    r'\bcollaborative\s+work:\s*get\s+invited\b',
    r'\bwe\s+are\s+looking\s+for\b|\bwe\'re\s+looking\s+for\b',
    r'\bthe\s+ideal\s+candidate\b'
]
promo_hits = 0
for j in jsonl_data:
    ev = j.get('responsibilityEvidence', '') or ''
    for p in PATTERNS:
        if re.search(p, ev, re.IGNORECASE):
            promo_hits += 1
            print(f"    Residual hit: {j['jobId']} | {j['jobTitle']} | Pat: {p}")
            break

print(f"  - Total residual promotional / introductory hits: {promo_hits}")
assert promo_hits == 0
print("  => PASS: Zero introductory, promotional, team-overview, or generic phrasing in responsibility evidence.")

# 8. Audit CSV and Quality Metrics Verification
print(f"\n[8] Audit CSV Files and Metrics Parity:")
sem_df = pd.read_csv('reports/stage2_semantic_classification_audit.csv')
qual_df = pd.read_csv('reports/stage2_classification_reason_quality_audit.csv')
with open('reports/stage2_quality_metrics.json', 'r', encoding='utf-8') as f:
    metrics = json.load(f)

print(f"  - Semantic audit rows: {len(sem_df)}")
print(f"  - Quality audit rows:  {len(qual_df)}")
assert len(sem_df) == 1930
assert len(qual_df) == 1930

sem_aligned = (sem_df['Semantic alignment result'] == 'CONFIRMED_ALIGNED').sum()
sem_review = (sem_df['Semantic alignment result'] == 'REQUIRES_REVIEW').sum()
sem_not = (sem_df['Semantic alignment result'] == 'NOT_ALIGNED').sum()
print(f"  - Semantic results:    {sem_aligned} CONFIRMED_ALIGNED, {sem_review} REQUIRES_REVIEW, {sem_not} NOT_ALIGNED")
assert sem_aligned == 1915
assert sem_review == 15
assert sem_not == 0

qual_pass = (qual_df['audit_status'] == 'PASS').sum()
qual_review = (qual_df['audit_status'] == 'REQUIRES_REVIEW').sum()
qual_fail = (qual_df['audit_status'] == 'FAIL').sum()
print(f"  - Quality results:     {qual_pass} PASS, {qual_review} REQUIRES_REVIEW, {qual_fail} FAIL")
assert qual_pass == 1915
assert qual_review == 15
assert qual_fail == 0

# Check metrics json authoritative consistency
cqm = metrics['classification_quality_metrics']
print(f"  - Metrics JSON counts: Pass={cqm['pass_count']}, Review={cqm['requires_review_count']}, Fail={cqm['fail_count']}")
assert cqm['pass_count'] == 1915
assert cqm['requires_review_count'] == 15
assert cqm['fail_count'] == 0
assert 'quality_audit_results' not in cqm, "Stale quality_audit_results block still present in metrics JSON!"
print("  => PASS: Perfect 1:1 metric consistency across semantic audit, quality audit, and quality metrics JSON.")

# 9. Top-Level Compensation Metrics Verification
print(f"\n[9] Top-Level Compensation Metrics Verification:")
comp = metrics['compensation_metrics']
print(f"  - Disclosed count:     {comp['total_with_compensation_disclosed']}")
print(f"  - Null count:          {comp['total_null_compensation']}")
print(f"  - Coverage pct:        {comp['compensation_coverage_pct']}%")
print(f"  - Null pct:            {comp['null_compensation_pct']}%")
print(f"  - Currency only null:  {comp['records_with_currency_disclosed_but_null_values']}")
assert comp['total_with_compensation_disclosed'] == 1268
assert comp['total_null_compensation'] == 662
assert comp['total_with_compensation_disclosed'] + comp['total_null_compensation'] == 1930
assert abs(comp['compensation_coverage_pct'] - 65.7) < 0.05
assert abs(comp['null_compensation_pct'] - 34.3) < 0.05
assert comp['records_with_currency_disclosed_but_null_values'] == 1
print("  => PASS: Top-level compensation metrics 100% reconciled with canonical dataset.")

# 10. Candidate Inspection Records Verification
print(f"\n[10] Candidate Inspection Records Verification:")
with open('reports/audit16_candidates_inspection.json', 'r', encoding='utf-8') as f:
    insp_data = json.load(f)

insp_recs = insp_data['inspection_records']
print(f"  - Inspected candidates: {len(insp_recs)}")
assert len(insp_recs) == 49
required_keys = [
    'job_id', 'job_title', 'company_name', 'category', 'classification_reason',
    'original_responsibility_evidence', 'final_responsibility_evidence',
    'source_description_reference', 'inspection_result', 'correction_made',
    'explanation', 'verbatim_match_verified'
]
for r in insp_recs:
    for k in required_keys:
        assert k in r, f"Missing key {k} in inspection record {r.get('job_id')}"
    assert len(r['original_responsibility_evidence']) > 0
    assert len(r['final_responsibility_evidence']) > 0
    assert r['verbatim_match_verified'] is True

print("  => PASS: Candidate inspection records contain all required fields across all 49 evaluated positions.")

# 11. Ancillary Audit Reports Mapping
print(f"\n[11] Ancillary Audit Reports Mapping:")
url_df = pd.read_csv('reports/stage2_url_validation.csv')
ai_rel_df = pd.read_csv('reports/stage2_ai_relevance_audit.csv')
print(f"  - URL validation rows: {len(url_df)}")
print(f"  - AI relevance rows:   {len(ai_rel_df)}")
assert len(url_df) == 1930
assert len(ai_rel_df) == 1930

url_id_col = 'job_id' if 'job_id' in url_df.columns else url_df.columns[0]
ai_id_col = 'job_id' if 'job_id' in ai_rel_df.columns else ai_rel_df.columns[0]
assert set(url_df[url_id_col]) == set(job_ids)
assert set(ai_rel_df[ai_id_col]) == set(job_ids)
print("  => PASS: Ancillary audits map 100% to canonical jobs.")

print("\n==================================================")
print("   ALL AUDIT 16 VERIFICATION CHECKS PASSED (11/11)")
print("==================================================")
conn.close()

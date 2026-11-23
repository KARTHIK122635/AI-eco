import json
import csv
import sqlite3
import re
import hashlib
import os

print("=" * 100)
print("PHASE II - STAGE 2: AUDIT 5 COMPREHENSIVE VERIFICATION SUITE")
print("=" * 100)

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

# 1. Load Data
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jsonl_records = [json.loads(line)['content']['data'] for line in f]

with open('data/canonical/canonical_jobs.csv', 'r', encoding='utf-8') as f:
    csv_rows = list(csv.DictReader(f))

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM ai_jobs ORDER BY rowid")
sqlite_rows = cur.fetchall()

print(f"Record Counts: JSONL={len(jsonl_records)}, CSV={len(csv_rows)}, SQLite={len(sqlite_rows)}")
assert len(jsonl_records) == len(csv_rows) == len(sqlite_rows) == 1930, "Record counts do not match 1930!"

# 2. SQLite Integrity Check
cur.execute("PRAGMA integrity_check")
ic_res = cur.fetchone()[0]
print(f"SQLite Integrity Check: {ic_res}")
assert ic_res == "ok", "SQLite database corrupted!"

# 3. Historical Table Preservation
cur.execute("SELECT count(*) FROM ai_startups")
n_startups = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM ai_products")
n_products = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM ai_research_papers")
n_papers = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM ai_news")
n_news = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM ai_jobs")
n_jobs = cur.fetchone()[0]
print(f"Preserved Table Counts -> Startups: {n_startups}, Products: {n_products}, Papers: {n_papers}, News: {n_news}, Jobs: {n_jobs}")
assert n_startups == 1307 and n_products == 1316 and n_papers == 1060 and n_news == 1132 and n_jobs == 1930, "Historical table counts modified!"

# 4. Duplicate Detection
job_ids = [r['jobId'] for r in jsonl_records]
app_urls = [r['applicationUrl'] for r in jsonl_records]
print(f"Duplicate Job IDs: {len(job_ids) - len(set(job_ids))}")
print(f"Duplicate Application URLs: {len(app_urls) - len(set(app_urls))}")
assert len(job_ids) == len(set(job_ids)) == 1930
assert len(app_urls) == len(set(app_urls)) == 1930

# 5. Evidence Verbatim Source Matching & Visa Check
missing_resp = 0
missing_qual = 0
visa_in_qual = 0
null_qual_count = 0

for r in jsonl_records:
    desc = norm_ws(r['jobDescription'])
    resp = norm_ws(r['responsibilityEvidence'])
    qual = norm_ws(r['qualificationEvidence'])
    
    if resp:
        if resp not in desc:
            missing_resp += 1
    if qual:
        if qual not in desc:
            missing_qual += 1
        if any(w in qual.lower() for w in ['visa', 'sponsorship', 'work authorization']):
            visa_in_qual += 1
    else:
        null_qual_count += 1

print(f"Responsibility Snippets NOT in Source Description: {missing_resp}")
print(f"Qualification Snippets NOT in Source Description: {missing_qual}")
print(f"Visa/Sponsorship Boilerplate in Qualification Evidence: {visa_in_qual}")
print(f"Truthful Null Qualification Evidence Count: {null_qual_count} / 1930")
assert missing_resp == 0, f"Found {missing_resp} non-verbatim responsibility snippets!"
assert missing_qual == 0, f"Found {missing_qual} non-verbatim qualification snippets!"
assert visa_in_qual == 0, f"Found {visa_in_qual} visa boilerplate snippets in qualification evidence!"

# 6. Salary Extraction Verification of Specific Examples
print("\n--- Verifying Audit 5 Salary Disclosures ---")
by_id = {r['jobId']: r for r in jsonl_records}

user_targets = [
    ('job_16db3f40963e47c5', 'Scale AI', 'AI Safety Residency', 100.0, 100.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_671b00fff11cfc18', 'Together AI', 'Technical Writer Intern', 41.0, 41.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_689c9625b67fc607', 'Snorkel AI', 'Research Fellow', 85.0, 165.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_ac563bb449616a82', 'CoreWeave', 'Recruiter, Data Center Operations', 55.0, 65.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_bfc1bda2dd9fdcc8', 'CoreWeave', 'Recruiting Operations Specialist', 40.0, 50.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_90a3078b4542f9c4', 'Databricks', 'Data Science Intern', 54.0, 60.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_b031e8b7e7239b46', 'Databricks', 'PhD GenAI Research Scientist Intern', 54.0, 60.0, 'USD', 'HOURLY', 'HOURLY'),
    ('job_fece52c6d4b2a2d4', 'Figure AI', 'Team Manager', 77400.0, 77400.0, 'USD', 'ANNUAL_BASE', 'ANNUAL'),
]

for jid, comp, title, exp_min, exp_max, exp_curr, exp_type, exp_per in user_targets:
    r = by_id[jid]
    print(f"Checking {comp} - {title}:")
    print(f"   Extracted: min={r['salaryMin']}, max={r['salaryMax']}, curr={r['currency']}, type={r['compensationType']}, period={r['compensationPeriod']}")
    assert r['salaryMin'] == exp_min
    assert r['salaryMax'] == exp_max
    assert r['currency'] == exp_curr
    assert r['compensationType'] == exp_type
    assert r['compensationPeriod'] == exp_per

# Check malformed values remain null
print("\n--- Verifying Malformed Values Remain Null ---")
malformed_ids = ['job_bac254d74ae1ac78', 'job_fe20ae4ebb1da07b']
for mid in malformed_ids:
    r = by_id[mid]
    print(f"Checking {r['companyName']} - {r['jobTitle']} (ID {mid}): salaryMin={r['salaryMin']}, salaryMax={r['salaryMax']}")
    assert r['salaryMin'] is None and r['salaryMax'] is None, f"Malformed salary was erroneously extracted for {mid}!"

# Check compensation summary
total_with_salary = sum(1 for r in jsonl_records if r['salaryMin'] is not None)
print(f"\nTotal Disclosed Salaries: {total_with_salary} / 1930 ({total_with_salary/1930*100:.2f}%)")
print(f"Total Undisclosed Salaries: {1930 - total_with_salary} / 1930 ({(1930-total_with_salary)/1930*100:.2f}%)")

# 7. Check Review Roles
print("\n--- Verifying Specific Review Roles ---")
r_3p = by_id['job_e98b00bb44e6a41d']
print(f"3P Revenue Accounting -> Cat: {r_3p['category']}, Reason: {r_3p['classificationReason'][:80]}...")
print(f"   Resp: {r_3p['responsibilityEvidence'][:70]}... (In desc: {norm_ws(r_3p['responsibilityEvidence']) in norm_ws(r_3p['jobDescription'])})")
print(f"   Qual: {r_3p['qualificationEvidence'][:70]}... (In desc: {norm_ws(r_3p['qualificationEvidence']) in norm_ws(r_3p['jobDescription'])})")
assert r_3p['category'] == 'NON_TECHNICAL'
assert norm_ws(r_3p['qualificationEvidence']) in norm_ws(r_3p['jobDescription'])

r_infra = by_id['job_3bb94e0bcc526fe4']
print(f"AI Infrastructure Demand Planning -> Cat: {r_infra['category']}, Reason: {r_infra['classificationReason'][:80]}...")
print(f"   Resp: {r_infra['responsibilityEvidence'][:70]}... (In desc: {norm_ws(r_infra['responsibilityEvidence']) in norm_ws(r_infra['jobDescription'])})")
print(f"   Qual: {r_infra['qualificationEvidence'][:70]}... (In desc: {norm_ws(r_infra['qualificationEvidence']) in norm_ws(r_infra['jobDescription'])})")
assert r_infra['category'] == 'AI_INFRASTRUCTURE'
assert norm_ws(r_infra['qualificationEvidence']) in norm_ws(r_infra['jobDescription'])

# 8. Check Vacancy Counts
stat_dist = {}
for r in jsonl_records:
    stat_dist[r['jobStatus']] = stat_dist.get(r['jobStatus'], 0) + 1
print(f"\nVacancy Status Breakdown: {stat_dist}")
assert stat_dist['EMPLOYER_CONFIRMED_OPEN'] == 1527
assert stat_dist['CLOSED'] == 1
assert stat_dist['AGGREGATOR_LISTED'] == 402

conn.close()
print("\nALL VERIFICATION CHECKS PASSED PERFECTLY!")

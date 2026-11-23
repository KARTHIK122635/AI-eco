import json
import csv
import sqlite3
import re
from collections import Counter

print("=" * 100)
print("PHASE II - STAGE 2: AUDIT 8 COMPREHENSIVE VERIFICATION SUITE")
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

print(f"1. Record Counts: JSONL={len(jsonl_records)}, CSV={len(csv_rows)}, SQLite={len(sqlite_rows)}")
assert len(jsonl_records) == len(csv_rows) == len(sqlite_rows) == 1930

# 2. SQLite Integrity Check
cur.execute("PRAGMA integrity_check")
ic_res = cur.fetchone()[0]
print(f"2. SQLite Integrity Check: {ic_res}")
assert ic_res == "ok"

# 3. Duplicate Checks
job_ids = [r['jobId'] for r in jsonl_records]
app_urls = [r['applicationUrl'] for r in jsonl_records]
signatures = [f"{norm_ws(r['companyName']).lower()}|{norm_ws(r['jobTitle']).lower()}|{norm_ws(r['location']).lower()}" for r in jsonl_records]
print(f"3. Duplicate Job IDs: {len(job_ids) - len(set(job_ids))}")
print(f"   Duplicate Application URLs: {len(app_urls) - len(set(app_urls))}")
print(f"   Distinct Signatures: {len(set(signatures))} / 1930")
assert len(job_ids) == len(set(job_ids)) == 1930
assert len(app_urls) == len(set(app_urls)) == 1930

# 4. Evidence Verbatim Source Matching & Visa Check
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

print(f"4. Evidence Matching:")
print(f"   Responsibility Snippets NOT Verbatim: {missing_resp}")
print(f"   Qualification Snippets NOT Verbatim: {missing_qual}")
print(f"   Visa Boilerplate in Qualifications: {visa_in_qual}")
print(f"   Null Qualification Count: {null_qual_count} / 1930")
assert missing_resp == 0
assert missing_qual == 0
assert visa_in_qual == 0

# 5. Compensation Disclosures Verification
print(f"\n5. Compensation Disclosures Verification:")
by_id = {r['jobId']: r for r in jsonl_records}

r_db = by_id['job_58809b0308baf230']
print(f"   Databricks Staff Backline (ID job_58809b0308baf230):")
print(f"      salaryMin={r_db['salaryMin']}, salaryMax={r_db['salaryMax']}, curr={r_db['currency']}, type={r_db['compensationType']}, period={r_db['compensationPeriod']}")
assert r_db['salaryMin'] is None
assert r_db['salaryMax'] is None
assert r_db['currency'] == 'USD'
assert r_db['compensationType'] is None
assert r_db['compensationPeriod'] is None

total_with_comp = sum(1 for r in jsonl_records if r['salaryMin'] is not None or r['salaryMax'] is not None)
total_null_comp = sum(1 for r in jsonl_records if r['salaryMin'] is None and r['salaryMax'] is None)
print(f"   Total with Compensation Disclosed: {total_with_comp} / 1930 ({total_with_comp/1930*100:.2f}%)")
print(f"   Total with Null Compensation: {total_null_comp} / 1930 ({total_null_comp/1930*100:.2f}%)")
assert total_with_comp == 1268
assert total_null_comp == 662

# 6. Audit 8 Quality Verification on Flagged Roles
print(f"\n6. Audit 8 Target Examples Inspection:")
target_checks = [
    ('job_8f652cc76da624e7', 'Data Engineer, Product', 'Builds and maintains data pipelines and data infrastructure supporting internal product and business teams.'),
    ('job_3bb94e0bcc526fe4', 'AI Infrastructure Operations, Demand Planning', 'Plans compute cluster demand, hardware capacity requirements, and operational infrastructure scaling for AI workloads.'),
    ('job_aaed61f362acc050', 'Applied AI Architect', 'Works with enterprise customers to design and deploy AI solutions and guide technical adoption.'),
    ('job_66f13e9130efa2e2', 'Account Executive, AI Native', 'Manages enterprise sales cycles, client negotiations, and commercial contract execution.'),
    ('job_89f4cca3c62134a7', 'Forward Deployed Engineering Intern (AI Agent)', 'Collaborates with engineering teams to deploy, integrate, and test customer-facing AI agent solutions.'),
    ('job_800f8b9de6ea2b31', 'Anthropic Fellows Program, Economics & Policy', 'Conducts empirical economic research and policy analysis on frontier AI impacts and societal governance.'),
    ('job_46ab92d6b3d90f5e', 'Hardware Systems Architect', 'Designs accelerator and compute hardware systems, including interconnects, memory architecture and performance.'),
    ('job_5757352c69c94652', 'Autonomous Systems Security Engineer', 'Develops security controls for autonomous systems, including hardware, firmware and operational environments.'),
    ('job_82529721fad25dda', 'Corporate Accounting', 'Manages revenue recognition, financial reporting, accounting controls and audit readiness.')
]

for jid, title, expected_reason in target_checks:
    r = by_id[jid]
    print(f"   [{r['category']}] {r['companyName']} - {r['jobTitle']}")
    print(f"      Reason: {r['classificationReason']}")
    assert r['classificationReason'] == expected_reason, f"Mismatch for {jid}: {r['classificationReason']} != {expected_reason}"

# 7. Vacancy Verification Preservation
stat_dist = Counter(r['jobStatus'] for r in jsonl_records)
print(f"\n7. Vacancy Status Breakdown: {dict(stat_dist)}")
assert stat_dist['EMPLOYER_CONFIRMED_OPEN'] == 1527
assert stat_dist['CLOSED'] == 1
assert stat_dist['AGGREGATOR_LISTED'] == 402

# 8. Historical Table Preservation
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
print(f"\n8. Preserved Table Counts -> Startups: {n_startups}, Products: {n_products}, Papers: {n_papers}, News: {n_news}, Jobs: {n_jobs}")
assert n_startups == 1307 and n_products == 1316 and n_papers == 1060 and n_news == 1132 and n_jobs == 1930
conn.close()

print("\n" + "=" * 100)
print("ALL AUDIT 8 VERIFICATION CHECKS PASSED PERFECTLY!")
print("=" * 100)

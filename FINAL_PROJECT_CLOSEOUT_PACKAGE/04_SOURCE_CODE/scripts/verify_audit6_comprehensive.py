import json
import csv
import sqlite3
import re
import hashlib
import os
from collections import Counter

print("=" * 100)
print("PHASE II - STAGE 2: AUDIT 6 COMPREHENSIVE VERIFICATION SUITE")
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
print(f"   Distinct Company-Title-Location Signatures: {len(set(signatures))} / 1930")
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
print(f"   Truthful Null Qualification Count: {null_qual_count} / 1930")
assert missing_resp == 0
assert missing_qual == 0
assert visa_in_qual == 0

# 5. Compensation Disclosures Verification
print(f"\n5. Audit 6 Compensation Records Verification:")
by_id = {r['jobId']: r for r in jsonl_records}

# 1. LINKIT B.V.
r_linkit = by_id['job_4dbed03c7b9d1981']
print(f"   LINKIT B.V. (ID job_4dbed03c7b9d1981):")
print(f"      salaryMin={r_linkit['salaryMin']}, salaryMax={r_linkit['salaryMax']}, curr={r_linkit['currency']}, type={r_linkit['compensationType']}, period={r_linkit['compensationPeriod']}")
assert r_linkit['salaryMin'] is None
assert r_linkit['salaryMax'] == 120000.0
assert r_linkit['currency'] == 'EUR'
assert r_linkit['compensationType'] == 'ANNUAL_OTE'
assert r_linkit['compensationPeriod'] == 'ANNUAL'

# 2. Figure AI - Customer Success Associate
r_fig = by_id['job_635816dfd21a2298']
print(f"   Figure AI CSA (ID job_635816dfd21a2298):")
print(f"      salaryMin={r_fig['salaryMin']}, salaryMax={r_fig['salaryMax']}, curr={r_fig['currency']}, type={r_fig['compensationType']}, period={r_fig['compensationPeriod']}")
assert r_fig['salaryMin'] is None
assert r_fig['salaryMax'] == 71000.0
assert r_fig['currency'] == 'USD'
assert r_fig['compensationType'] == 'TOTAL_COMPENSATION'
assert r_fig['compensationPeriod'] == 'ANNUAL'

# 3. Databricks - Staff Backline Engineer
r_db = by_id['job_58809b0308baf230']
print(f"   Databricks Staff Backline (ID job_58809b0308baf230):")
print(f"      salaryMin={r_db['salaryMin']}, salaryMax={r_db['salaryMax']}, curr={r_db['currency']}, type={r_db['compensationType']}, period={r_db['compensationPeriod']}")
print(f"      provenance raw disclosure: {r_db.get('provenance', {}).get('raw_compensation_disclosure')}")
assert r_db['salaryMin'] is None
assert r_db['salaryMax'] is None

# 4. TELUS Digital - Content Reviewer
r_telus = by_id['job_675a85266ca800bd']
print(f"   TELUS Digital (ID job_675a85266ca800bd):")
print(f"      salaryMin={r_telus['salaryMin']}, salaryMax={r_telus['salaryMax']}, curr={r_telus['currency']}, type={r_telus['compensationType']}, period={r_telus['compensationPeriod']}")
assert r_telus['salaryMin'] == 0.2333
assert r_telus['salaryMax'] == 0.2333
assert r_telus['currency'] == 'USD'
assert r_telus['compensationType'] == 'TASK_BASED'
assert r_telus['compensationPeriod'] is None

total_with_comp = sum(1 for r in jsonl_records if r['salaryMin'] is not None or r['salaryMax'] is not None)
print(f"   Total with Compensation Disclosed: {total_with_comp} / 1930 ({total_with_comp/1930*100:.2f}%)")
print(f"   Total with Null Compensation: {1930 - total_with_comp} / 1930 ({(1930-total_with_comp)/1930*100:.2f}%)")

# 6. Recheck the 6 Classification Records
print(f"\n6. Recheck 6 Classification Records:")
reclass_expected = {
    'job_455248a218364d2e': ('Applied AI Architects, Partner', 'AI_PRODUCT_SOLUTIONS'),
    'job_8dc55042eeb084c9': ('Applied AI Architects, Partner', 'AI_PRODUCT_SOLUTIONS'),
    'job_c9050c0a3328518c': ('Manager Applied AI Architecture, Healthcare & Life Sciences', 'AI_PRODUCT_SOLUTIONS'),
    'job_a9ec78f057cc185f': ('Manager of Applied AI Architecture, Commercial', 'AI_PRODUCT_SOLUTIONS'),
    'job_dd881a420fc9e6b6': ('Manager of Applied AI Architecture, Startups', 'AI_PRODUCT_SOLUTIONS'),
    'job_4b765b8c0dd9a693': ('IT Operations Engineer, Asset Management', 'NON_AI_TECH')
}

for jid, (exp_title, exp_cat) in reclass_expected.items():
    r = by_id[jid]
    print(f"   [{jid}] {r['jobTitle']} -> Category: {r['category']} (Expected: {exp_cat})")
    print(f"      Reason: {r['classificationReason'][:90]}...")
    assert r['category'] == exp_cat

# Print taxonomy distribution
cat_counts = Counter(r['category'] for r in jsonl_records)
print(f"\n   Taxonomy Distribution: {dict(cat_counts)}")

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

print("\nALL AUDIT 6 VERIFICATION CHECKS PASSED PERFECTLY!")

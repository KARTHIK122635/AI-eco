import json
import csv
import sqlite3
import re
from collections import Counter

print("=" * 100)
print("PHASE II - STAGE 2: AUDIT 9 COMPREHENSIVE VERIFICATION SUITE")
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

# 6. Audit 9 Target Examples Inspection
print(f"\n6. Audit 9 Explicit Target Roles Inspection:")
audit9_targets = [
    # 282 Backend cluster target roles
    ('job_645ec3c646e82f94', 'Developer Education Lead, Claude Platform', 'Develops technical curriculum, developer documentation, sample projects, and educational workshops for developer platforms.'),
    ('job_db8b6c46c7d0f6c0', 'Field Executive Architect', 'Advises strategic enterprise executive leaders on AI architecture adoption, deployment strategy, and technical governance.'),
    ('job_2800aacada956959', 'Front End Engineer, Marketing', 'Develops user interfaces, web components, and client-facing web applications for corporate digital properties.'),
    ('job_528b4bb095dca31b', 'Incident Response Manager - Product & Engineering', 'Coordinates incident response workflows, operational readiness cadences, and system recovery across product and engineering services.'),
    ('job_095118294141ad91', 'IT Systems Engineer, Client Platform Engineer, ChromeOS', 'Manages corporate ChromeOS endpoint fleets, device provisioning pipelines, and client system policies.'),
    ('job_4d624827f2607a15', 'IT Systems Engineer, Client Platform Engineer, macOS', 'Manages enterprise macOS client platforms, automated device management profiles, and endpoint security standards.'),
    ('job_a5e4210c62f132df', 'Manager, Corporate Network Engineering', 'Architects and maintains internal corporate network infrastructure, enterprise firewalls, and office connectivity systems.'),
    ('job_91f45db292ef7d53', 'Red Team Engineer, Safeguards', 'Executes adversarial red-teaming assessments, vulnerability evaluations, and safeguard testing on AI systems.'),
    ('job_1c4d72ef60363a8f', 'Salesforce Developer', 'Develops custom Salesforce integrations, Apex workflows, and CRM applications supporting business operations.'),
    
    # 155 Business operations cluster target roles
    ('job_286966147c8cad03', 'CMC & Manufacturing Lead, Life Sciences', 'Oversees chemistry, manufacturing, and controls (CMC) compliance, regulatory filings, and biopharma production operations.'),
    ('job_30c503063e81fb5d', 'Customer  Success Manager', 'Guides customer onboarding, relationship management, product adoption, and client retention.'),
    ('job_7e60636a41530dbc', 'Director, IT SOX', 'Leads IT general controls audits, SOX compliance assessments, and financial system security governance.'),
    ('job_8b0aeb86027bf38c', 'Data Center Asset Management, Commercial Associate', 'Manages commercial lease contracts, physical asset tracking, and procurement operations for data center facilities.'),
    ('job_0218c061fb84afce', 'Discovery Technical Operations Specialist', 'Coordinates electronic discovery technical operations, legal hold lifecycles, and litigation data governance.'),
    ('job_7f10f5bf134fcf45', 'Docs Lead, Platform', 'Leads developer documentation strategy, API reference authoring, and platform technical guides.'),

    # Other audited and resolved repeated cluster anomalies
    ('job_ec2913967af6956d', 'Account Manager - Speech & AI Technologies', 'Manages technical client relationships, engineering partner alignment, and account growth across speech and AI machine learning teams.'),
    ('job_0f1a3c2b1fd42054', 'Staff Software Engineer, Internal Products', 'Builds internal developer platforms, core engineering infrastructure, and enterprise tools for engineering teams.'),
    ('job_bec8dd7b8a39dd3e', 'AI Infrastructure System Engineer', 'Designs, deploys, and maintains AI compute cluster infrastructure, GPU host systems, and system hardware interfaces.'),
    ('job_01ed47f989ac45e0', 'Senior Principal Rack System Integration Engineer', 'Leads rack-level hardware system integration, power delivery validation, and thermal packaging for AI acceleration clusters.'),
    ('job_79cb69d5bcd03bd9', 'Business System Engineer', 'Designs, implements, and integrates enterprise business systems, internal application tooling, and corporate data workflows.'),
    ('job_b847c81a2b76a070', 'Data Center OFE - Sourcing Lead, Data Center Power & Cooling', 'Manages strategic equipment sourcing, power and cooling vendor contracts, and supplier execution for data centers.'),
    ('job_b567b0b811517bd2', 'Manager, International Cloud Sourcing', 'Directs global cloud compute capacity procurement, infrastructure provider negotiations, and supply commitments.'),
    ('job_86e95e76d79878c9', 'Strategic Sourcing - OFCI', 'Manages strategic procurement of owner-furnished equipment, vendor supply contracts, and data center hardware deliveries.'),
    ('job_fb3b97caf24d3590', 'Global Specialized Domain Expert Recruiter (Contractor)', 'Manages specialized candidate sourcing, technical interview pipelines, and domain expert recruiting workflows.'),
    ('job_8e7c5ed6ba740523', 'Senior Mechatronics Engineer - Humanoid Head', 'Designs mechatronic actuators, sensor integration, and precision robotic head mechanisms for humanoid robots.'),
    ('job_2db07f22aff840bf', 'GenAI Engineer', 'Designs, builds, and deploys generative AI application pipelines, prompt workflows, and model integrations.')
]

for jid, title, expected_reason in audit9_targets:
    r = by_id[jid]
    print(f"   [{r['category']}] {r['companyName']} - {r['jobTitle']}")
    print(f"      Reason: {r['classificationReason']}")
    assert r['classificationReason'] == expected_reason, f"Mismatch for {jid}: {r['classificationReason']} != {expected_reason}"

# 7. Quality Metrics on Reason Formatting
empty_reasons = sum(1 for r in jsonl_records if not r.get('classificationReason'))
improper_ending = sum(1 for r in jsonl_records if not r.get('classificationReason', '').endswith('.'))
lowercase_start = sum(1 for r in jsonl_records if not (r.get('classificationReason', '') and r['classificationReason'][0].isupper()))
company_intros = sum(1 for r in jsonl_records if any(r.get('classificationReason', '').lower().startswith(p) for p in ['at ', 'about ', 'we are ', 'scale is', 'anthropic is', 'to cresta']))
comp_visa_words = sum(1 for r in jsonl_records if any(w in r.get('classificationReason', '').lower() for w in ['401(k)', 'health insurance', 'visa sponsorship', 'equal opportunity', 'salary range', 'equity', 'usd/year']))

print(f"\n7. Reason Quality Verification:")
print(f"   Empty Reasons: {empty_reasons}")
print(f"   Improper Ending (not period): {improper_ending}")
print(f"   Lowercase Start: {lowercase_start}")
print(f"   Company Intro Boilerplate: {company_intros}")
print(f"   Compensation / Visa / Benefits Words: {comp_visa_words}")
assert empty_reasons == 0
assert improper_ending == 0
assert lowercase_start == 0
assert company_intros == 0
assert comp_visa_words == 0

# 8. Distinct Reasons Metric
counts = Counter(r['classificationReason'] for r in jsonl_records)
print(f"   Distinct Classification Reasons: {len(counts)} (Audit 8 had 143)")
assert len(counts) >= 300

# 9. Vacancy Verification Preservation
stat_dist = Counter(r['jobStatus'] for r in jsonl_records)
print(f"\n8. Vacancy Status Breakdown: {dict(stat_dist)}")
assert stat_dist['EMPLOYER_CONFIRMED_OPEN'] == 1527
assert stat_dist['CLOSED'] == 1
assert stat_dist['AGGREGATOR_LISTED'] == 402

# 10. Historical Table Preservation
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
print(f"\n9. Preserved Table Counts -> Startups: {n_startups}, Products: {n_products}, Papers: {n_papers}, News: {n_news}, Jobs: {n_jobs}")
assert n_startups == 1307 and n_products == 1316 and n_papers == 1060 and n_news == 1132 and n_jobs == 1930
conn.close()

# 11. Deep Parity across All 28 Fields
field_map = {
    "jobId": "job_id",
    "jobTitle": "job_title",
    "companyName": "company_name",
    "companyWebsite": "company_website",
    "category": "category",
    "classificationReason": "classification_reason",
    "responsibilityEvidence": "responsibility_evidence",
    "qualificationEvidence": "qualification_evidence",
    "classificationConfidence": "classification_confidence",
    "jobDescription": "job_description",
    "requiredSkills": "required_skills",
    "preferredSkills": "preferred_skills",
    "experienceLevel": "experience_level",
    "location": "location",
    "remoteType": "remote_type",
    "salaryMin": "salary_min",
    "salaryMax": "salary_max",
    "currency": "currency",
    "compensationType": "compensation_type",
    "compensationPeriod": "compensation_period",
    "employmentType": "employment_type",
    "jobStatus": "job_status",
    "vacancyStatus": "vacancy_status",
    "applicationUrl": "application_url",
    "postedAt": "posted_at",
    "sourceName": "source_name",
    "provenance": "provenance",
    "collectedAt": "collected_at"
}

mismatches = 0
for i in range(1930):
    j_rec = jsonl_records[i]
    c_rec = csv_rows[i]
    s_rec = sqlite_rows[i]

    for j_key, s_key in field_map.items():
        j_val = j_rec.get(j_key)
        c_val = c_rec.get(j_key) if j_key in c_rec else c_rec.get(s_key)
        s_val = s_rec[s_key]

        if isinstance(j_val, (list, dict)):
            c_val_parsed = json.loads(c_val) if c_val else ([] if isinstance(j_val, list) else {})
            s_val_parsed = json.loads(s_val) if s_val else ([] if isinstance(j_val, list) else {})
            if not (j_val == c_val_parsed == s_val_parsed):
                mismatches += 1
            continue

        if isinstance(j_val, float):
            c_float = float(c_val) if (c_val is not None and c_val != "") else None
            s_float = float(s_val) if s_val is not None else None
            if not (j_val == c_float == s_float):
                mismatches += 1
            continue

        if j_val is None:
            if not ((c_val == "" or c_val is None) and s_val is None):
                mismatches += 1
        else:
            if not (str(j_val) == str(c_val) == str(s_val)):
                mismatches += 1

print(f"\n10. Deep Cell-by-Cell Cross-Format Parity: {mismatches} mismatches")
assert mismatches == 0

print("\n" + "=" * 100)
print("ALL AUDIT 9 COMPREHENSIVE VERIFICATION SUITE CHECKS PASSED PERFECTLY!")
print("=" * 100)

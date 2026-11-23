import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

print("=== 1. COMPENSATION RECORDS ===")

# 1. LINKIT B.V. - Account Executive Data & AI
linkit = [r for r in records.values() if 'linkit' in r['companyName'].lower() and 'account executive' in r['jobTitle'].lower()]
for r in linkit:
    print(f"\nID: {r['jobId']} | Company: {r['companyName']} | Title: {r['jobTitle']}")
    print(f"Current Salary: min={r['salaryMin']}, max={r['salaryMax']}, curr={r['currency']}, type={r['compensationType']}, period={r['compensationPeriod']}")
    desc = r['jobDescription']
    for line in desc.split('\n'):
        if any(k in line.lower() for k in ['120', 'ote', 'salaris', 'salary', 'bonus', '€']):
            print("   Line:", line.strip()[:140])

# 2. Figure AI - Customer Success Associate
fig = [r for r in records.values() if 'figure' in r['companyName'].lower() and 'customer success associate' in r['jobTitle'].lower()]
for r in fig:
    print(f"\nID: {r['jobId']} | Company: {r['companyName']} | Title: {r['jobTitle']}")
    print(f"Current Salary: min={r['salaryMin']}, max={r['salaryMax']}, curr={r['currency']}, type={r['compensationType']}, period={r['compensationPeriod']}")
    desc = r['jobDescription']
    for line in desc.split('\n'):
        if any(k in line.lower() for k in ['71,000', 'compensation', 'bonus', 'differential', 'total']):
            print("   Line:", line.strip()[:140])

# 3. Databricks - Staff Backline Engineer – ML/AI
db = [r for r in records.values() if 'databricks' in r['companyName'].lower() and 'staff backline engineer' in r['jobTitle'].lower()]
for r in db:
    print(f"\nID: {r['jobId']} | Company: {r['companyName']} | Title: {r['jobTitle']}")
    print(f"Current Salary: min={r['salaryMin']}, max={r['salaryMax']}, curr={r['currency']}, type={r['compensationType']}, period={r['compensationPeriod']}")
    desc = r['jobDescription']
    idx = desc.find('170.40')
    if idx != -1:
        print("   Snippet around 170.40:", repr(desc[max(0, idx-100):min(len(desc), idx+200)]))

# 4. TELUS Digital - Content Reviewer - United States
telus = [r for r in records.values() if 'telus' in r['companyName'].lower() and 'content reviewer' in r['jobTitle'].lower()]
for r in telus:
    print(f"\nID: {r['jobId']} | Company: {r['companyName']} | Title: {r['jobTitle']}")
    print(f"Current Salary: min={r['salaryMin']}, max={r['salaryMax']}, curr={r['currency']}, type={r['compensationType']}, period={r['compensationPeriod']}")
    desc = r['jobDescription']
    idx = desc.find('0.2333')
    if idx != -1:
        print("   Snippet around 0.2333:", repr(desc[max(0, idx-100):min(len(desc), idx+200)]))

print("\n=== 2. CLASSIFICATION RECORDS ===")
target_class_ids = [
    'job_455248a218364d2e',
    'job_8dc55042eeb084c9',
    'job_c9050c0a3328518c',
    'job_a9ec78f057cc185f',
    'job_dd881a420fc9e6b6',
    'job_4b765b8c0dd9a693'
]

for tid in target_class_ids:
    if tid in records:
        r = records[tid]
        print(f"\nID: {r['jobId']} | Company: {r['companyName']} | Title: {r['jobTitle']}")
        print(f"Current Category: {r['category']} | Confidence: {r['classificationConfidence']}")
        print(f"Current Reason: {r['classificationReason']}")
        print(f"Current Resp: {repr(r['responsibilityEvidence'])}")
        print(f"Current Qual: {repr(r['qualificationEvidence'])}")
        print(f"Job Desc Head: {r['jobDescription'][:300]}...")

import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

# 1. Inspect Databricks FDE records
fde_ids = [
    'job_67f7c6003e024de0',
    'job_a21c829d51c3a7c7',
    'job_807e6632f0af6e22',
    'job_0cb38f99c8da449a',
    'job_22abb2ef0edc96eb'
]

print("=== DATABRICKS FDE RECORDS ===")
for jid in fde_ids:
    j = jobs[jid]
    print(f"{jid} | {j['companyName']} | {j['jobTitle']}")
    print(f"  Classification Reason: {j['classificationReason']}")
    print(f"  Current RespEv: {j.get('responsibilityEvidence')}")
    idx = j['jobDescription'].find('The impact you will have:')
    if idx != -1:
        print(f"  Impact section snippet:\n{j['jobDescription'][idx:idx+600]}")
    print("-" * 50)

# 2. Inspect HFC ML Fellow records
ml_ids = [
    'job_54c421f13430cbf9',
    'job_6235766d8986181c',
    'job_8ee1224407ba5ba6',
    'job_105421a2eaf7d737'
]

print("\n=== HFC ML FELLOW RECORDS ===")
for jid in ml_ids:
    j = jobs[jid]
    print(f"{jid} | {j['companyName']} | {j['jobTitle']}")
    print(f"  Classification Reason: {j['classificationReason']}")
    print(f"  Current RespEv: {j.get('responsibilityEvidence')}")
    idx = j['jobDescription'].find('Participate in AI/ML projects')
    if idx != -1:
        print(f"  AI/ML projects snippet:\n{j['jobDescription'][idx:idx+400]}")
    print("-" * 50)

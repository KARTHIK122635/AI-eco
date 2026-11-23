import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

target_ids = [
    'job_d207b42e585bf8e6',
    'job_80a480dfe5f61806',
    'job_03adf198b79570b7',
    'job_3ab4fad59bd0a42d',
    'job_b30c4117b32b2e1b',
    'job_d2ffb1910190a82b'
]

for jid in target_ids:
    j = jobs[jid]
    print("=" * 80)
    print(f"ID: {jid} | {j['companyName']} - {j['jobTitle']}")
    print(f"Category: {j['category']}")
    print(f"Reason: {j['classificationReason']}")
    print("Full Description:")
    print(j['jobDescription'])
    print("=" * 80)
    print()

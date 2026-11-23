import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

zilliz_jobs = [j for j in jobs if 'zilliz' in j['companyName'].lower()]
for zj in zilliz_jobs:
    print(f"=== {zj['jobId']}: {zj['jobTitle']} ===")
    print("Current Evidence:", zj.get('responsibilityEvidence'))
    print("Reason:", zj.get('classificationReason'))
    print("Desc excerpt (first 600 chars):", repr(zj.get('jobDescription')[:600]))
    print("Desc tail (last 600 chars):", repr(zj.get('jobDescription')[-600:]))
    print()

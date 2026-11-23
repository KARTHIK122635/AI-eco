import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

for title_query in ['Finance Fellow', 'Medical Fellow', 'Principal Software Engineer, GPS']:
    for j in jobs:
        if title_query.lower() in j['jobTitle'].lower():
            print(f"ID: {j['jobId']}")
            print(f"Title: {j['jobTitle']}")
            print(f"Company: {j['companyName']}")
            print(f"Category: {j['category']}")
            print(f"Reason: {j['classificationReason']}")
            print(f"RespEv: {j['responsibilityEvidence']}")
            print(f"QualEv: {j['qualificationEvidence']}")
            print("-" * 50)

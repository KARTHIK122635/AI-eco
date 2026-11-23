import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

jobs_by_id = {j['jobId']: j for j in jobs}

cited_ids = [
    'job_21e78eaefc925d26', # STEM Fellow UK?
    'job_91fd8017f05b1d94', # SWE Fellow Canada
    'job_f3d068e4db415d90', # SWE Fellow UK
    'job_3286c737ec6d7b38', # SWE Fellow US
    'job_cf830bd9939b555e', # Engagement Manager PS
    'job_d28e40a44928956a', # Engagement Manager PS
    'job_f724f26481fd28a7', # Engagement Manager PS
    'job_ac9cb76ba1d920bd', # Engagement Manager PS
    'job_a94a61fdf09a6a38', # Engagement Manager PS
    'job_d937a79251d4723a', # Senior Applied AI Engineer
    'job_fe54132e071496e6', # Senior Applied AI Engineer
    'job_011867a56e3a13b5', # Subcontracts Manager, Public Sector
    'job_a2d39f78a759c157', # SVP, Data Science Lead, CoE – Global Clients
]

print("=== Checking Cited IDs ===")
for cid in cited_ids:
    if cid in jobs_by_id:
        j = jobs_by_id[cid]
        print(f"FOUND: {cid} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']}")
        print(f"   Reason: {j['classificationReason']}")
        print(f"   RespEv: {j.get('responsibilityEvidence')}")
        print()
    else:
        print(f"NOT FOUND: {cid}")

# Also search for titles if not found
print("\n=== Searching for Stem Fellow ===")
for j in jobs:
    if 'stem fellow' in j['jobTitle'].lower():
        print(f"Match: {j['jobId']} | {j['companyName']} | {j['jobTitle']}")
        print(f"   RespEv: {j.get('responsibilityEvidence')}")
